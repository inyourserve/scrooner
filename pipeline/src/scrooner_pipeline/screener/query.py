"""Stage 5d -- Full query execution (doc 14, extended 2026-09-10 by
doc/faster-loading/fast.md / doc/adr/0001-screener-redis-cache-and-
boolean-logic.md). Combines predicates into a fully traceable
ScreenResult: every match cites the exact metric_value row that produced
it, and every exclusion is recorded with a reason -- never silently
dropped.

Reads analytics.company_screening_snapshot (screener/snapshot.py), NOT
analytics.metric_value directly -- the live per-request `resolve()`
window-function query this module used to call was measured (2026-09-10)
to cost 5-7s per metric under real load (a cold Bitmap Heap Scan across
metric_value's 11M scattered rows, not an unindexed query -- see
doc/learnings/2026-09-10-screener-performance.md). The snapshot table
holds the exact same "most recent value" resolution, precomputed once
offline, so a request here never touches metric_value.

Two execution paths, chosen by whether `query.where` is set:

- No `where` (the original, doc-14b-verified shape): metric_predicates/
  categorical_predicates combine with AND only, evaluated in Python --
  same code shape as before the 2026-09-10 rewrite, just reading
  snapshot rows instead of calling resolve_most_recent_values live.
  Preserves full excluded_missing_data/excluded_inactive attribution.
- `where` set (new, doc/adr/0001): an arbitrary AND/OR/NOT tree,
  compiled to a single parameterized SQL statement (EXISTS subqueries
  per metric leaf, direct column comparisons per categorical leaf) and
  run against the snapshot table server-side. Per-predicate exclusion
  attribution has no single well-defined meaning under OR/NOT (a company
  can be excluded by one branch and still match via another), so
  excluded_missing_data is intentionally left empty for this path with
  an explicit `exclusion_detail` note, rather than a false claim of
  precision the tree doesn't support.

Read-only against `core`/`analytics` -- the Screener never writes,
same discipline as every phase before it.
"""

from itertools import count

import psycopg
import structlog

from scrooner_pipeline.screener.evaluate import evaluate_between, evaluate_comparison, rank_top_bottom
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


def _load_candidate_companies(conn: psycopg.Connection, include_inactive: bool) -> dict[int, dict]:
    with conn.cursor() as cur:
        cur.execute(
            """
            select c.id, c.cik, c.company_name, c.sic_code, c.sic_description, c.sector, c.status,
                   (select l.ticker from core.listing l where l.company_id = c.id
                    and l.effective_to is null order by l.id limit 1) as ticker
            from core.company c
            """
        )
        rows = cur.fetchall()
    companies = {}
    for company_id, cik, name, sic_code, sic_description, sector, status, ticker in rows:
        if not include_inactive and status != "active":
            continue
        companies[company_id] = {
            "cik": cik,
            "company_name": name,
            "sic_code": sic_code,
            "sic_description": sic_description,
            "sector": sector,
            "status": status,
            "ticker": ticker,
        }
    return companies


def _apply_categorical_predicates(companies: dict[int, dict], predicates: list) -> dict[int, dict]:
    for pred in predicates:
        companies = {cid: c for cid, c in companies.items() if c.get(pred.field) == pred.value}
    return companies


def _load_snapshot_values(
    conn: psycopg.Connection, metric_definition_ids: list[int], dataset_version: int
) -> dict[tuple[int, int], dict]:
    """(company_id, metric_definition_id) -> {value, period_label,
    period_end, formula_version} from the precomputed snapshot -- the
    same shape resolve_most_recent_values used to return, sourced from a
    simple indexed read instead of a live window-function query."""
    if not metric_definition_ids:
        return {}
    with conn.cursor() as cur:
        cur.execute(
            """
            select company_id, metric_definition_id, value, period_label, period_end, formula_version
            from analytics.company_screening_snapshot
            where metric_definition_id = any(%s) and dataset_version = %s
            """,
            (metric_definition_ids, dataset_version),
        )
        rows = cur.fetchall()
    return {
        (company_id, metric_id): {
            "value": value,
            "period_label": period_label,
            "period_end": period_end,
            "formula_version": formula_version,
        }
        for company_id, metric_id, value, period_label, period_end, formula_version in rows
    }


# ---------------------------------------------------------------------------
# Boolean-tree compiler (doc/adr/0001) -- only exercised when query.where is set.
# ---------------------------------------------------------------------------


def _compile_node(node, catalog: dict, dataset_version: int, alias_gen) -> tuple[str, list]:
    if isinstance(node, PredicateGroup):
        if node.op == "not":
            sql, params = _compile_node(node.predicates[0], catalog, dataset_version, alias_gen)
            return f"NOT ({sql})", params
        joiner = " AND " if node.op == "and" else " OR "
        parts, all_params = [], []
        for child in node.predicates:
            sql, params = _compile_node(child, catalog, dataset_version, alias_gen)
            parts.append(f"({sql})")
            all_params.extend(params)
        return joiner.join(parts), all_params

    if isinstance(node, CategoricalPredicate):
        # field is restricted to a fixed Literal set in schema.py -- never
        # a raw user-supplied column name -- safe to interpolate.
        return f"c.{node.field} = %s", [node.value]

    if isinstance(node, MetricPredicate):
        if node.metric_name not in catalog:
            raise ValueError(f"unknown metric_name, not in the screenable catalog: {node.metric_name!r}")
        metric_id = catalog[node.metric_name]
        alias = f"s{next(alias_gen)}"
        params: list = [metric_id, dataset_version]
        clause = (
            f"exists (select 1 from analytics.company_screening_snapshot {alias} "
            f"where {alias}.company_id = c.id and {alias}.metric_definition_id = %s "
            f"and {alias}.dataset_version = %s"
        )
        if node.operator == "between":
            clause += f" and {alias}.value between %s and %s"
            params += [node.value_range[0], node.value_range[1]]
        else:
            if node.operator not in {">", "<", ">=", "<=", "=", "!="}:
                raise ValueError(f"operator not valid inside a boolean tree: {node.operator!r}")
            clause += f" and {alias}.value {node.operator} %s"
            params.append(node.value)
        clause += ")"
        return clause, params

    raise TypeError(f"unknown predicate node: {node!r}")


def _collect_metric_names(node) -> set[str]:
    if isinstance(node, PredicateGroup):
        names: set[str] = set()
        for child in node.predicates:
            names |= _collect_metric_names(child)
        return names
    if isinstance(node, MetricPredicate):
        return {node.metric_name}
    return set()


def _run_boolean_tree_query(
    conn: psycopg.Connection, query: ScreenQuery, catalog: dict, dataset_version: int
) -> dict[int, dict]:
    where_sql, params = _compile_node(query.where, catalog, dataset_version, count())
    status_sql = "" if query.include_inactive else "and c.status = 'active'"
    with conn.cursor() as cur:
        cur.execute(
            f"""
            select c.id, c.cik, c.company_name, c.sic_code, c.sic_description, c.sector, c.status,
                   (select l.ticker from core.listing l where l.company_id = c.id
                    and l.effective_to is null order by l.id limit 1) as ticker
            from core.company c
            where ({where_sql}) {status_sql}
            """,
            params,
        )
        rows = cur.fetchall()
    return {
        company_id: {
            "cik": cik,
            "company_name": name,
            "sic_code": sic_code,
            "sic_description": sic_description,
            "sector": sector,
            "status": status,
            "ticker": ticker,
        }
        for company_id, cik, name, sic_code, sic_description, sector, status, ticker in rows
    }


def run_query(conn: psycopg.Connection, query: ScreenQuery, dataset_version: int | None = None) -> dict:
    """`dataset_version`: pass a pre-fetched value to avoid a second round
    trip when the caller already needs it for something else (apps/backend's
    cache.py computes a query hash from it before deciding whether to call
    this at all) -- each round trip to this project's Supabase project costs
    ~270ms measured from this dev machine, so skipping a redundant one is a
    real, not cosmetic, saving. Fetched internally when omitted."""
    catalog = load_screenable_metric_catalog(conn)
    if dataset_version is None:
        dataset_version = get_dataset_version(conn)

    unknown = [p.metric_name for p in query.metric_predicates if p.metric_name not in catalog]
    if query.sort_by and query.sort_by not in catalog:
        unknown.append(query.sort_by)
    if query.where is not None:
        unknown += [name for name in _collect_metric_names(query.where) if name not in catalog]
    if unknown:
        raise ValueError(f"unknown metric_name(s), not in the screenable catalog: {sorted(set(unknown))}")

    excluded_inactive: list[str] = []
    if not query.include_inactive:
        with conn.cursor() as cur:
            cur.execute("select cik from core.company where status != 'active'")
            excluded_inactive = [r[0] for r in cur.fetchall()]

    ranked = [p for p in query.metric_predicates if p.operator in RANKED_OPERATORS]
    excluded_missing_data: dict[int, dict] = {}
    exclusion_detail = None

    if query.where is not None:
        surviving = _run_boolean_tree_query(conn, query, catalog, dataset_version)
        metric_names_to_show = _collect_metric_names(query.where)
        exclusion_detail = (
            "per-predicate exclusion attribution is not available for boolean-tree "
            "('where') queries -- a company excluded by one branch may still match via "
            "another, so 'missing data caused this exclusion' has no single meaning here"
        )
    else:
        companies = _load_candidate_companies(conn, query.include_inactive)
        companies = _apply_categorical_predicates(companies, query.categorical_predicates)
        non_ranked = [p for p in query.metric_predicates if p.operator not in RANKED_OPERATORS]

        needed_metric_ids = [catalog[p.metric_name] for p in non_ranked] + [catalog[p.metric_name] for p in ranked]
        if query.sort_by:
            needed_metric_ids.append(catalog[query.sort_by])
        resolved_flat = (
            _load_snapshot_values(conn, list(set(needed_metric_ids)), dataset_version) if needed_metric_ids else {}
        )

        surviving = dict(companies)
        for pred in non_ranked:
            metric_id = catalog[pred.metric_name]
            next_surviving = {}
            for company_id, info in surviving.items():
                resolved_row = resolved_flat.get((company_id, metric_id))
                value = resolved_row["value"] if resolved_row else None
                if value is None:
                    excluded_missing_data.setdefault(
                        company_id, {"cik": info["cik"], "company_name": info["company_name"], "missing_metrics": []}
                    )
                    excluded_missing_data[company_id]["missing_metrics"].append(pred.metric_name)
                    continue
                if pred.operator == "between":
                    ok = evaluate_between(value, pred.value_range)
                else:
                    ok = evaluate_comparison(value, pred.operator, pred.value)
                if ok:
                    next_surviving[company_id] = info
            surviving = next_surviving
        metric_names_to_show = {p.metric_name for p in query.metric_predicates}

    if query.sort_by:
        metric_names_to_show.add(query.sort_by)

    # Fetch citation values for the surviving set + ranked candidates. The
    # flat path already loaded every id it needs (non-ranked + ranked +
    # sort_by, which is exactly what metric_names_to_show covers); the
    # `where` path hasn't loaded anything yet -- the boolean tree itself
    # was evaluated entirely in SQL, without touching per-row values.
    if query.where is None:
        resolved = resolved_flat
    else:
        citation_metric_ids = list(
            {catalog[name] for name in metric_names_to_show} | {catalog[p.metric_name] for p in ranked}
        )
        resolved = _load_snapshot_values(conn, citation_metric_ids, dataset_version) if citation_metric_ids else {}

    if ranked:
        pred = ranked[0]
        metric_id = catalog[pred.metric_name]
        candidates = []
        for company_id, info in surviving.items():
            resolved_row = resolved.get((company_id, metric_id))
            value = resolved_row["value"] if resolved_row else None
            if value is None:
                excluded_missing_data.setdefault(
                    company_id, {"cik": info["cik"], "company_name": info["company_name"], "missing_metrics": []}
                )
                excluded_missing_data[company_id]["missing_metrics"].append(pred.metric_name)
                continue
            candidates.append((info["cik"], value))
        ranked_ciks = set(rank_top_bottom(candidates, pred.operator, pred.n))
        surviving = {cid: info for cid, info in surviving.items() if info["cik"] in ranked_ciks}

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
        present = [m for m in matched if resolved.get((m["company_id"], sort_metric_id), {}).get("value") is not None]
        missing = [m for m in matched if resolved.get((m["company_id"], sort_metric_id), {}).get("value") is None]
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
