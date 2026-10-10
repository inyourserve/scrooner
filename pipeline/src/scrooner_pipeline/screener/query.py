"""Stage 5d -- Full query execution (doc 14, extended 2026-09-10 by
doc/faster-loading/fast.md / doc/adr/0001-screener-redis-cache-and-
boolean-logic.md, and 2026-09-20 by migration 0068). Combines predicates
into a fully traceable ScreenResult: every match cites the exact
metric_value row that produced it, and every exclusion is recorded with
a reason -- never silently dropped.

Reads analytics.company_screening_snapshot (screener/snapshot.py), NOT
analytics.metric_value directly -- the live per-request `resolve()`
window-function query this module used to call was measured (2026-09-10)
to cost 5-7s per metric under real load (a cold Bitmap Heap Scan across
metric_value's 11M scattered rows, not an unindexed query -- see
doc/learnings/2026-09-10-screener-performance.md). The snapshot table
holds the exact same "most recent value" resolution, precomputed once
offline, so a request here never touches metric_value.

Rebuilt as a wide (one row per company) shape 2026-09-20 -- see migration
0068's own comment for the measured before/after, including a REJECTED
first attempt (one `metrics jsonb` blob per row) that measured WORSE than
the original EAV table once JSONB/TOAST decompression cost was accounted
for. Each metric instead gets its own native columns (`"<name>"`,
`"<name>__period_label"`, etc.) -- a single-predicate filter dropped from
107ms (JSONB) / a 70ms 3-predicate EAV query to 6.1ms. Company identity
(cik, name, ticker, sic/sector, status) is part of the same row, computed
once per snapshot rebuild instead of once per request via a correlated
`core.listing` subquery.

Two execution paths, chosen by whether `query.where` is set:

- No `where` (the original, doc-14b-verified shape): metric_predicates/
  categorical_predicates combine with AND only, evaluated in Python --
  same code shape as before the 2026-09-10 rewrite, just reading
  snapshot rows instead of calling resolve_most_recent_values live.
  Preserves full excluded_missing_data/excluded_inactive attribution.
- `where` set (new, doc/adr/0001): an arbitrary AND/OR/NOT tree,
  compiled to a single parameterized SQL statement -- now a plain
  boolean expression over the wide snapshot table's own native columns
  (no per-predicate EXISTS subquery or JSONB extraction any more, since
  every predicate reads a plain column off the SAME row). Per-predicate
  exclusion attribution has no single well-defined meaning under OR/NOT
  (a company can be excluded by one branch and still match via another),
  so excluded_missing_data is intentionally left empty for this path with
  an explicit `exclusion_detail` note, rather than a false claim of
  precision the tree doesn't support.

Read-only against `core`/`analytics` -- the Screener never writes,
same discipline as every phase before it.
"""

import psycopg
import structlog
from psycopg import sql

from scrooner_pipeline.screener.evaluate import (
    evaluate_between,
    evaluate_comparison,
    rank_top_bottom,
)
from scrooner_pipeline.screener.resolve import load_screenable_metric_catalog
from scrooner_pipeline.screener.schema import (
    RANKED_OPERATORS,
    CategoricalPredicate,
    MetricPredicate,
    PredicateGroup,
    ScreenQuery,
)
from scrooner_pipeline.screener.snapshot import get_dataset_version

logger = structlog.get_logger()


_IDENTITY_FIELDS = (
    "cik",
    "company_name",
    "sic_code",
    "sic_description",
    "sector",
    "status",
    "ticker",
)


def _select_snapshot_rows(
    conn: psycopg.Connection,
    dataset_version: int,
    metric_names: list[str],
    where_clause: sql.Composable | None = None,
    params: list | None = None,
) -> list[tuple[int, dict, dict[str, dict]]]:
    """One round trip: identity + each requested metric's native columns
    for one snapshot version, optionally filtered. Returns
    [(company_id, identity, {metric_name: {value, period_label,
    period_end, formula_version}})], a metric present only when its value
    is non-null (the same rule every caller relied on before).

    Every snapshot read goes through here, scoped to exactly one
    dataset_version -- since migration 0074 the table holds several
    versions side by side, so an unscoped read would mix generations."""
    columns = [sql.Identifier("company_id")] + [
        sql.Identifier(f) for f in _IDENTITY_FIELDS
    ]
    for name in metric_names:
        columns += [
            sql.Identifier(name),
            sql.Identifier(f"{name}__period_label"),
            sql.Identifier(f"{name}__period_end"),
            sql.Identifier(f"{name}__formula_version"),
        ]
    statement = sql.SQL(
        "select {} from analytics.company_screening_snapshot where dataset_version = %s"
    ).format(sql.SQL(", ").join(columns))
    all_params: list = [dataset_version]
    if where_clause is not None:
        statement = sql.SQL("{} and ({})").format(statement, where_clause)
        all_params += params or []
    # Explicit order: excluded_missing_data/excluded_inactive follow row
    # order, and the same query on the same version must list them the
    # same way every time (release gate: determinism).
    statement = sql.SQL("{} order by company_id").format(statement)
    with conn.cursor() as cur:
        cur.execute(statement, all_params)
        rows = cur.fetchall()

    width = len(_IDENTITY_FIELDS)
    out = []
    for row in rows:
        identity = dict(zip(_IDENTITY_FIELDS, row[1 : 1 + width]))
        metrics = {}
        for i, name in enumerate(metric_names):
            value, period_label, period_end, formula_version = row[
                1 + width + i * 4 : 1 + width + i * 4 + 4
            ]
            if value is not None:
                metrics[name] = {
                    "value": value,
                    "period_label": period_label,
                    "period_end": period_end,
                    "formula_version": formula_version,
                }
        out.append((row[0], identity, metrics))
    return out


def _metric_names_to_show(query: ScreenQuery) -> set[str]:
    """Every metric a matched company cites: predicates (flat or `where`
    tree), the ranked predicate, display_metrics and sort_by. With `where`
    set, metric_predicates can only hold the ranked predicate (schema.py),
    so one formula serves both paths. The ranked name matters: found live
    2026-09-11, "top 5 by roic excluding financials" showed a null roic
    for every match when it was left out."""
    names = {p.metric_name for p in query.metric_predicates} | set(
        query.display_metrics
    )
    if query.where is not None:
        names |= _collect_metric_names(query.where)
    if query.sort_by:
        names.add(query.sort_by)
    return names


def _is_inactive(status: str | None) -> bool:
    # Mirrors SQL `status != 'active'`: a NULL status is neither matched
    # (Python `!= "active"` filtered it out of candidates) nor listed as
    # inactive (SQL `!=` never returned it) -- unchanged from before.
    return status is not None and status != "active"


def _apply_categorical_predicates(
    companies: dict[int, dict], predicates: list
) -> dict[int, dict]:
    for pred in predicates:
        companies = {
            cid: c for cid, c in companies.items() if c.get(pred.field) == pred.value
        }
    return companies


# ---------------------------------------------------------------------------
# Boolean-tree compiler (doc/adr/0001) -- only exercised when query.where is set.
# Compiles directly to a boolean expression over the wide snapshot table's
# own row (no per-predicate join/EXISTS or JSONB extraction any more --
# every predicate reads a plain native column off the SAME row, see
# migration 0068). Returns a psycopg `sql.Composed` fragment (not a plain
# string) since a metric predicate needs a safely-quoted dynamic column
# identifier, not just a bind parameter.
# ---------------------------------------------------------------------------


def _compile_node(node, catalog: dict) -> tuple[sql.Composable, list]:
    if isinstance(node, PredicateGroup):
        if node.op == "not":
            clause, params = _compile_node(node.predicates[0], catalog)
            return sql.SQL("NOT ({})").format(clause), params
        joiner = sql.SQL(" AND ") if node.op == "and" else sql.SQL(" OR ")
        parts, all_params = [], []
        for child in node.predicates:
            clause, params = _compile_node(child, catalog)
            parts.append(sql.SQL("({})").format(clause))
            all_params.extend(params)
        return joiner.join(parts), all_params

    if isinstance(node, CategoricalPredicate):
        # field is restricted to a fixed Literal set in schema.py -- never
        # a raw user-supplied column name -- these are the wide snapshot
        # table's own columns, not core.company's.
        return sql.SQL("{} = %s").format(sql.Identifier(node.field)), [node.value]

    if isinstance(node, MetricPredicate):
        if node.metric_name not in catalog:
            raise ValueError(
                f"unknown metric_name, not in the screenable catalog: {node.metric_name!r}"
            )
        # node.metric_name is checked against the trusted catalog just
        # above (sourced from analytics.metric_definition, never raw user
        # input), so it's safe to use as a column identifier -- still
        # quoted via sql.Identifier rather than string-interpolated, the
        # same defense-in-depth as everywhere else this project builds a
        # dynamic identifier (see snapshot.py's _validate_metric_name).
        # A company with no value at all for this metric correctly fails
        # the comparison (NULL > anything is NULL, i.e. not true) with no
        # separate NULL check needed.
        column = sql.Identifier(node.metric_name)
        params: list = []
        if node.operator == "between":
            clause = sql.SQL("{} between %s and %s").format(column)
            params += [node.value_range[0], node.value_range[1]]
        else:
            if node.operator not in {">", "<", ">=", "<=", "=", "!="}:
                raise ValueError(
                    f"operator not valid inside a boolean tree: {node.operator!r}"
                )
            clause = sql.SQL("{} " + node.operator + " %s").format(column)
            params.append(node.value)
        return clause, params

    raise TypeError(f"unknown predicate node: {node!r}")


# ---------------------------------------------------------------------------
# Flat-AND SQL pre-filter (2026-10-02) -- narrows the snapshot read for the
# non-`where` query path, which previously fetched every company in the
# dataset_version unconditionally (see this module's own historical
# docstring above: "evaluated in Python -- ... Preserves full
# excluded_missing_data/excluded_inactive attribution"). That attribution
# is exactly why this can't just reuse _compile_node's plain `col OP %s`
# compiler the way the `where`-tree path does -- a flat-AND query must
# still be able to tell the user WHICH metric was missing for an excluded
# company, and _compile_node's clauses would silently drop (not just
# fail to match) any row with a NULL value.
#
# This is a PURE speed optimization with a proof of safety, not a new
# filtering rule: it returns a SUPERSET of every row Python's own
# unchanged logic below would ever place in `matched` or
# `excluded_missing_data`, so the final output is byte-for-byte identical
# to fetching the whole population and filtering in Python -- verified by
# tests/unit/test_query_flat_prefilter.py running BOTH paths against the
# same fake rows and asserting identical results, not just "it returns
# something".
#
# Why "superset" and not "exact": Python's existing loop (further below)
# is sequential and SHORT-CIRCUITS -- a company missing metric A is
# removed from `surviving` and tagged in excluded_missing_data citing
# ONLY metric A, and metric B is never even checked for it, regardless of
# whether metric B's value would also have failed. An independent,
# per-predicate `(col IS NULL OR comparison)` AND across all predicates
# would UNDER-fetch this exact case (a company missing A but genuinely
# failing B's comparison) -- so instead this compiles two independent
# sub-conditions, OR'd together:
#   - full_match:   every predicate's value is present AND passes
#   - any_missing:  at least one predicate's value is NULL
# A row Python would show (in either matched or excluded_missing_data)
# always satisfies one of these two. A row Python would drop entirely
# (present value, failed comparison, no missing values anywhere) matches
# neither and SQL correctly excludes it -- that's the whole saving, since
# that's normally the overwhelming majority of the population for a
# selective filter. Categorical predicates get a plain, unrelaxed
# equality clause (NULL = anything is NULL/falsy in SQL, matching
# _apply_categorical_predicates' own Python `==` exactly -- no special
# case needed).
# ---------------------------------------------------------------------------


def _compile_flat_prefilter(
    non_ranked: list[MetricPredicate],
    categorical_predicates: list,
    catalog: dict,
) -> tuple[sql.Composable, list] | tuple[None, None]:
    if not non_ranked and not categorical_predicates:
        return None, None

    clauses: list[sql.Composable] = []
    params: list = []

    for pred in categorical_predicates:
        clauses.append(sql.SQL("{} = %s").format(sql.Identifier(pred.field)))
        params.append(pred.value)

    if non_ranked:
        full_match_parts: list[sql.Composable] = []
        any_missing_parts: list[sql.Composable] = []
        full_match_params: list = []
        for pred in non_ranked:
            if pred.metric_name not in catalog:
                raise ValueError(
                    "unknown metric_name, not in the screenable catalog: "
                    f"{pred.metric_name!r}"
                )
            column = sql.Identifier(pred.metric_name)
            if pred.operator == "between":
                comparison = sql.SQL("{} between %s and %s").format(column)
                full_match_params += [pred.value_range[0], pred.value_range[1]]
            elif pred.operator in {">", "<", ">=", "<=", "=", "!="}:
                comparison = sql.SQL("{} " + pred.operator + " %s").format(column)
                full_match_params.append(pred.value)
            else:
                raise ValueError(
                    f"operator not valid for a flat predicate: {pred.operator!r}"
                )
            full_match_parts.append(
                sql.SQL("({} is not null and {})").format(column, comparison)
            )
            any_missing_parts.append(sql.SQL("{} is null").format(column))

        clauses.append(
            sql.SQL("(({}) or ({}))").format(
                sql.SQL(" and ").join(full_match_parts),
                sql.SQL(" or ").join(any_missing_parts),
            )
        )
        params += full_match_params

    return sql.SQL(" and ").join(clauses), params


def _collect_metric_names(node) -> set[str]:
    if isinstance(node, PredicateGroup):
        names: set[str] = set()
        for child in node.predicates:
            names |= _collect_metric_names(child)
        return names
    if isinstance(node, MetricPredicate):
        return {node.metric_name}
    return set()


def run_query(
    conn: psycopg.Connection,
    query: ScreenQuery,
    dataset_version: int | None = None,
    catalog: dict[str, int] | None = None,
) -> dict:
    """`dataset_version` / `catalog`: pass pre-fetched values to skip their
    round trips (~270-300ms each from this dev machine to Supabase) --
    apps/backend already has both cached. Fetched internally when omitted.

    Snapshot reads are ONE round trip on either path (2026-09-26): company
    identity, every needed metric column and the inactive list all come
    off the same version-scoped snapshot rows. Measured before merging, a
    Redis-miss run paid four sequential round trips (catalog 280ms,
    inactive list 419ms, identity 1,721ms, metric values 892ms)."""
    if catalog is None:
        catalog = load_screenable_metric_catalog(conn)
    if dataset_version is None:
        dataset_version = get_dataset_version(conn)

    unknown = [
        p.metric_name for p in query.metric_predicates if p.metric_name not in catalog
    ]
    if query.sort_by and query.sort_by not in catalog:
        unknown.append(query.sort_by)
    unknown += [name for name in query.display_metrics if name not in catalog]
    if query.where is not None:
        unknown += [
            name for name in _collect_metric_names(query.where) if name not in catalog
        ]
    if unknown:
        raise ValueError(
            f"unknown metric_name(s), not in the screenable catalog: {sorted(set(unknown))}"
        )

    ranked = [p for p in query.metric_predicates if p.operator in RANKED_OPERATORS]
    non_ranked = [
        p for p in query.metric_predicates if p.operator not in RANKED_OPERATORS
    ]
    excluded_missing_data: dict[int, dict] = {}
    exclusion_detail = None
    metric_names_to_show = _metric_names_to_show(query)
    needed_names = sorted(metric_names_to_show)

    if query.where is not None:
        where_clause, params = _compile_node(query.where, catalog)
        if not query.include_inactive:
            # Inactive rows ride along in the same round trip so the
            # excluded_inactive list needs no query of its own.
            where_clause = sql.SQL(
                "status != 'active' or (status = 'active' and ({}))"
            ).format(where_clause)
        rows = _select_snapshot_rows(
            conn, dataset_version, needed_names, where_clause, params
        )
        exclusion_detail = (
            "per-predicate exclusion attribution is not available for boolean-tree "
            "('where') queries -- a company excluded by one branch may still match via "
            "another, so 'missing data caused this exclusion' has no single meaning here"
        )
    else:
        # A safe, superset-preserving SQL pre-filter (see
        # _compile_flat_prefilter's own module comment) -- narrows the
        # fetch instead of always reading the whole dataset_version. The
        # rest of this function's logic (below) is completely unchanged
        # and still makes every matched/excluded decision in Python; this
        # only reduces how many rows it has to look at.
        prefilter_clause, prefilter_params = _compile_flat_prefilter(
            non_ranked, query.categorical_predicates, catalog
        )
        if prefilter_clause is not None and not query.include_inactive:
            prefilter_clause = sql.SQL(
                "status != 'active' or (status = 'active' and ({}))"
            ).format(prefilter_clause)
        rows = _select_snapshot_rows(
            conn, dataset_version, needed_names, prefilter_clause, prefilter_params
        )

    excluded_inactive = (
        []
        if query.include_inactive
        else [i["cik"] for _, i, _ in rows if _is_inactive(i["status"])]
    )
    resolved = {
        (company_id, catalog[name]): data
        for company_id, _, metrics in rows
        for name, data in metrics.items()
    }

    if query.where is not None:
        surviving = {
            company_id: identity
            for company_id, identity, _ in rows
            if query.include_inactive or identity["status"] == "active"
        }
    else:
        companies = {
            company_id: identity
            for company_id, identity, _ in rows
            if query.include_inactive or identity["status"] == "active"
        }
        companies = _apply_categorical_predicates(
            companies, query.categorical_predicates
        )

        surviving = dict(companies)
        for pred in non_ranked:
            metric_id = catalog[pred.metric_name]
            next_surviving = {}
            for company_id, info in surviving.items():
                resolved_row = resolved.get((company_id, metric_id))
                value = resolved_row["value"] if resolved_row else None
                if value is None:
                    excluded_missing_data.setdefault(
                        company_id,
                        {
                            "cik": info["cik"],
                            "company_name": info["company_name"],
                            "missing_metrics": [],
                        },
                    )
                    excluded_missing_data[company_id]["missing_metrics"].append(
                        pred.metric_name
                    )
                    continue
                if pred.operator == "between":
                    ok = evaluate_between(value, pred.value_range)
                else:
                    ok = evaluate_comparison(value, pred.operator, pred.value)
                if ok:
                    next_surviving[company_id] = info
            surviving = next_surviving

    if ranked:
        pred = ranked[0]
        metric_id = catalog[pred.metric_name]
        candidates = []
        for company_id, info in surviving.items():
            resolved_row = resolved.get((company_id, metric_id))
            value = resolved_row["value"] if resolved_row else None
            if value is None:
                excluded_missing_data.setdefault(
                    company_id,
                    {
                        "cik": info["cik"],
                        "company_name": info["company_name"],
                        "missing_metrics": [],
                    },
                )
                excluded_missing_data[company_id]["missing_metrics"].append(
                    pred.metric_name
                )
                continue
            candidates.append((info["cik"], value))
        ranked_ciks = set(rank_top_bottom(candidates, pred.operator, pred.n))
        surviving = {
            cid: info for cid, info in surviving.items() if info["cik"] in ranked_ciks
        }

    matched = []
    for company_id, info in surviving.items():
        metrics = {}
        for metric_name in metric_names_to_show:
            metric_id = catalog[metric_name]
            row = resolved.get((company_id, metric_id))
            if row:
                metrics[metric_name] = {
                    "value": row["value"],
                    "period_label": row["period_label"],
                    "period_end": row["period_end"],
                    "formula_version": row["formula_version"],
                }
        matched.append({**info, "company_id": company_id, "metrics": metrics})

    if query.sort_by:
        sort_metric_id = catalog[query.sort_by]
        present = [
            m
            for m in matched
            if resolved.get((m["company_id"], sort_metric_id), {}).get("value")
            is not None
        ]
        missing = [
            m
            for m in matched
            if resolved.get((m["company_id"], sort_metric_id), {}).get("value") is None
        ]
        present.sort(key=lambda m: m["cik"])
        present.sort(
            key=lambda m: resolved[(m["company_id"], sort_metric_id)]["value"],
            reverse=query.sort_desc,
        )
        missing.sort(key=lambda m: m["cik"])
        matched = present + missing
    elif ranked:
        pred = ranked[0]
        metric_id = catalog[pred.metric_name]
        matched.sort(key=lambda m: m["cik"])
        matched.sort(
            key=lambda m: resolved[(m["company_id"], metric_id)]["value"],
            reverse=pred.operator == "top_n",
        )
    else:
        matched.sort(key=lambda m: m["cik"])

    if query.limit is not None:
        matched = matched[: query.limit]

    result = {
        "matched": matched,
        "excluded_missing_data": list(excluded_missing_data.values()),
        "excluded_inactive": excluded_inactive,
        "dataset_version": dataset_version,
    }
    if exclusion_detail:
        result["exclusion_detail"] = exclusion_detail
    logger.info(
        "screener.query.done",
        matched=len(matched),
        excluded_missing_data=len(excluded_missing_data),
        excluded_inactive=len(excluded_inactive),
        boolean_tree=query.where is not None,
    )
    return result


def load_screen_result_page(
    conn: psycopg.Connection,
    query: ScreenQuery,
    dataset_version: int,
    company_ids: list[int],
) -> list[dict] | None:
    """Rebuild one page of a stored screen run from its own snapshot
    version (migration 0074: runs store matched company IDs, not a copy of
    each company's values). `company_ids` is the page's slice, in result
    order. Returns matched entries in exactly run_query's shape, or None
    when that snapshot version has been pruned (snapshot.py keeps the
    latest few plus any version a saved screen still points at).

    Only the page's own companies are read: exclusion lists are resolved
    server-side by the caller's run lookup, since downloading full rows for
    thousands of excluded companies cost seconds per page on a slow link
    (measured 2026-09-26)."""
    if not company_ids:
        return []
    names = sorted(_metric_names_to_show(query))
    rows = _select_snapshot_rows(
        conn, dataset_version, names, sql.SQL("company_id = any(%s)"), [company_ids]
    )
    if not rows:
        # Every version holds the full company universe, so asking for
        # companies and getting none back means the version is gone.
        return None
    by_id = {company_id: (identity, metrics) for company_id, identity, metrics in rows}
    return [
        {
            **by_id[company_id][0],
            "company_id": company_id,
            "metrics": by_id[company_id][1],
        }
        for company_id in company_ids
    ]
