"""Stage 5d -- Full query execution (doc 14). Combines predicates with AND
only (doc 02's ~10-operator MVP guardrail, no OR/nested groups), applies
the active-only default, and produces a fully traceable ScreenResult:
every match cites the exact metric_value row that produced it, and every
exclusion is recorded with a reason -- never silently dropped.

Read-only against `core`/`analytics` -- the Screener never writes,
same discipline as every phase before it.
"""

import psycopg
import structlog

from scrooner_pipeline.screener.evaluate import evaluate_between, evaluate_comparison, rank_top_bottom
from scrooner_pipeline.screener.resolve import load_screenable_metric_catalog, resolve_most_recent_values
from scrooner_pipeline.screener.schema import RANKED_OPERATORS, ScreenQuery

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


def run_query(conn: psycopg.Connection, query: ScreenQuery) -> dict:
    catalog = load_screenable_metric_catalog(conn)

    unknown = [p.metric_name for p in query.metric_predicates if p.metric_name not in catalog]
    if query.sort_by and query.sort_by not in catalog:
        unknown.append(query.sort_by)
    if unknown:
        raise ValueError(f"unknown metric_name(s), not in the screenable catalog: {sorted(set(unknown))}")

    companies = _load_candidate_companies(conn, query.include_inactive)
    # Every non-active company in the whole universe, not just ones that would
    # otherwise have matched -- a simplification worth revisiting once a real
    # stale/unknown company exists to check the more precise version against
    # (all 10 golden companies are currently active, so this list is empty
    # either way today).
    excluded_inactive = []
    if not query.include_inactive:
        with conn.cursor() as cur:
            cur.execute("select cik from core.company where status != 'active'")
            excluded_inactive = [r[0] for r in cur.fetchall()]

    companies = _apply_categorical_predicates(companies, query.categorical_predicates)

    non_ranked = [p for p in query.metric_predicates if p.operator not in RANKED_OPERATORS]
    ranked = [p for p in query.metric_predicates if p.operator in RANKED_OPERATORS]

    needed_metric_ids = [catalog[p.metric_name] for p in non_ranked] + [catalog[p.metric_name] for p in ranked]
    if query.sort_by:
        needed_metric_ids.append(catalog[query.sort_by])
    resolved = resolve_most_recent_values(conn, list(set(needed_metric_ids))) if needed_metric_ids else {}

    excluded_missing_data: dict[int, dict] = {}
    surviving = dict(companies)

    for pred in non_ranked:
        metric_id = catalog[pred.metric_name]
        next_surviving = {}
        for company_id, info in surviving.items():
            resolved_row = resolved.get((company_id, metric_id))
            value = resolved_row["value"] if resolved_row else None
            if value is None:
                excluded_missing_data.setdefault(company_id, {"cik": info["cik"], "company_name": info["company_name"], "missing_metrics": []})
                excluded_missing_data[company_id]["missing_metrics"].append(pred.metric_name)
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
                excluded_missing_data.setdefault(company_id, {"cik": info["cik"], "company_name": info["company_name"], "missing_metrics": []})
                excluded_missing_data[company_id]["missing_metrics"].append(pred.metric_name)
                continue
            candidates.append((info["cik"], value))
        ranked_ciks = set(rank_top_bottom(candidates, pred.operator, pred.n))
        surviving = {cid: info for cid, info in surviving.items() if info["cik"] in ranked_ciks}

    matched = []
    for company_id, info in surviving.items():
        # Includes every predicate metric AND sort_by (even when sort_by
        # isn't also a predicate) -- found live 2026-08-17: a result sorted
        # by a metric that wasn't also filtered on had no way to show what
        # value produced that order, an incomplete-lineage gap doc 14's own
        # DoD ("every matched company's result cites the exact metric_value
        # row that produced it") doesn't allow.
        metric_names_to_show = {p.metric_name for p in query.metric_predicates}
        if query.sort_by:
            metric_names_to_show.add(query.sort_by)
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
        # Stable two-pass ordering: CIK ascending breaks equal-value ties;
        # value then determines the requested direction. Nulls remain last.
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
        # SQL without ORDER BY has no stable order. A deterministic default
        # keeps identical queries byte-equivalent even without sort_by.
        matched.sort(key=lambda m: m["cik"])

    if query.limit is not None:
        matched = matched[: query.limit]

    result = {
        "matched": matched,
        "excluded_missing_data": list(excluded_missing_data.values()),
        "excluded_inactive": excluded_inactive,
    }
    logger.info(
        "screener.query.done",
        matched=len(matched),
        excluded_missing_data=len(excluded_missing_data),
        excluded_inactive=len(excluded_inactive),
    )
    return result
