"""Cash-flow-statement reconciliation gaps (doc 26 follow-on, built
2026-08-21), acting on core-fact-utilization-study.md's #2 recommendation.

Three metrics, one per working-capital line (AR, Inventory, AP), each
comparing two genuinely different sources for "how much did this line
change this year":

1. The balance-sheet-IMPLIED change: this year's instant snapshot minus
   last year's (accounts_receivable[FY] - accounts_receivable[FY-1]).
2. The company's OWN reported cash-flow-statement adjustment for the
   same year (cf_ar_change[FY], IncreaseDecreaseInAccountsReceivable).

gap = (1) - (2). Verified live before choosing this framing (not assumed):
AAPL's balance-sheet-implied FY2025 AR change is $39,777M - $33,410M =
$6,367M; the cash-flow-statement's own reported figure for the same year
is $6,682M -- close but NOT identical. This is EXPECTED, not a bug in
either source: the indirect-method cash-flow adjustment excludes non-cash
and non-operating effects (acquisitions, divestitures, FX translation,
reclassifications) that a bare balance-sheet subtraction can't separate
out. A LARGE gap is the actual signal worth surfacing -- unusual AR/
Inventory/AP movement the cash-flow statement itself doesn't attribute to
ordinary operations -- so this is built as a diagnostic cross-check
(a dollar figure, sign preserved), never a locked ratio with a pass/fail
threshold.

Same reasoning as expanded_metrics.py's cash_conversion_cycle and
quality_flags.py's quality flags for why this can't live in calculate.py's
generic per-period engine: it needs a PRIOR fiscal year's value, not just
the current period's own inputs.
"""

from datetime import date
from decimal import Decimal

import psycopg
import structlog

from scrooner_pipeline.common.errors import log_error

logger = structlog.get_logger()

BALANCE_SHEET_CONCEPTS = {
    "ar_change_reconciliation_gap": "accounts_receivable",
    "inventory_change_reconciliation_gap": "inventory",
    "ap_change_reconciliation_gap": "accounts_payable",
}
CASH_FLOW_CONCEPTS = {
    "ar_change_reconciliation_gap": "cf_ar_change",
    "inventory_change_reconciliation_gap": "cf_inventory_change",
    "ap_change_reconciliation_gap": "cf_ap_change",
}
REQUIRED_CONCEPTS = sorted(set(BALANCE_SHEET_CONCEPTS.values()) | set(CASH_FLOW_CONCEPTS.values()))


def _load_concept_ids(conn: psycopg.Connection) -> dict[str, int]:
    with conn.cursor() as cur:
        cur.execute("select name, id from analytics.canonical_concept where name = any(%s)", (REQUIRED_CONCEPTS,))
        return dict(cur.fetchall())


def _load_fy_facts(conn: psycopg.Connection, company_id: int, concept_ids: dict[str, int]) -> dict[str, dict[int, Decimal]]:
    """concept_name -> {fiscal_year: value}, FY periods only -- same shape
    as quality_flags.py's own loader (balance-sheet concepts are instant,
    cash-flow concepts are duration, but both resolve to one value per FY
    in analytics.canonical_fact regardless)."""
    id_to_name = {v: k for k, v in concept_ids.items()}
    with conn.cursor() as cur:
        cur.execute(
            """
            select cf.canonical_concept_id, p.fiscal_year, cf.value
            from analytics.canonical_fact cf
            join core.period p on p.id = cf.period_id
            where cf.company_id = %s and cf.canonical_concept_id = any(%s) and p.fiscal_period = 'FY'
            """,
            (company_id, list(concept_ids.values())),
        )
        result: dict[str, dict[int, Decimal]] = {name: {} for name in concept_ids}
        for concept_id, fiscal_year, value in cur.fetchall():
            if fiscal_year is not None and value is not None:
                result[id_to_name[concept_id]][fiscal_year] = value
    return result


def _fy_period_dates(conn: psycopg.Connection, company_id: int, anchor_concept_id: int, fiscal_year: int):
    with conn.cursor() as cur:
        cur.execute(
            """
            select p.start_date, p.end_date
            from analytics.canonical_fact cf
            join core.period p on p.id = cf.period_id
            where cf.company_id = %s and cf.canonical_concept_id = %s and p.fiscal_period = 'FY' and p.fiscal_year = %s
            limit 1
            """,
            (company_id, anchor_concept_id, fiscal_year),
        )
        return cur.fetchone()


def _row(company_id: int, metric_id: int, start, end, value: Decimal | None, reason: str | None) -> dict:
    if start is None or end is None:
        start = end = date.today()
    return {
        "company_id": company_id, "metric_definition_id": metric_id,
        "period_start": start, "period_end": end, "period_label": "FY",
        "value": value, "is_null_reason": reason, "source_fact_ids": None,
    }


def calculate_reconciliation_for_company(
    conn: psycopg.Connection, company_id: int, metric_ids: dict[str, int], concept_ids: dict[str, int]
) -> dict:
    facts = _load_fy_facts(conn, company_id, concept_ids)
    rows: list[dict] = []

    for metric_name, bs_concept in BALANCE_SHEET_CONCEPTS.items():
        if metric_name not in metric_ids:
            continue
        cf_concept = CASH_FLOW_CONCEPTS[metric_name]
        cf_concept_id = concept_ids[cf_concept]
        bs_years = facts[bs_concept]
        cf_years = facts[cf_concept]

        for fy in sorted(cf_years.keys()):
            period = _fy_period_dates(conn, company_id, cf_concept_id, fy)
            start, end = period if period else (None, None)

            if fy not in bs_years:
                rows.append(_row(company_id, metric_ids[metric_name], start, end, None, f"missing:{bs_concept}({fy})"))
                continue
            if (fy - 1) not in bs_years:
                rows.append(_row(company_id, metric_ids[metric_name], start, end, None, f"missing:{bs_concept}({fy - 1})"))
                continue

            bs_implied_change = bs_years[fy] - bs_years[fy - 1]
            gap = bs_implied_change - cf_years[fy]
            rows.append(_row(company_id, metric_ids[metric_name], start, end, gap, None))

    with conn.cursor() as cur:
        target_ids = list(metric_ids.values())
        cur.execute(
            "delete from analytics.metric_value where company_id = %s and metric_definition_id = any(%s) and period_label = 'FY'",
            (company_id, target_ids),
        )
        if rows:
            cur.executemany(
                """
                insert into analytics.metric_value
                    (company_id, metric_definition_id, period_start, period_end, period_label,
                     value, is_null_reason, source_fact_ids)
                values
                    (%(company_id)s, %(metric_definition_id)s, %(period_start)s, %(period_end)s,
                     %(period_label)s, %(value)s, %(is_null_reason)s, %(source_fact_ids)s)
                """,
                rows,
            )
        conn.commit()

    computed = sum(1 for r in rows if r["value"] is not None)
    null = sum(1 for r in rows if r["value"] is None)
    logger.info("reconciliation.company_done", company_id=company_id, computed=computed, null=null)
    return {"computed": computed, "null": null}


def calculate_reconciliation(conn: psycopg.Connection, ciks: set[str]) -> dict:
    concept_ids = _load_concept_ids(conn)
    missing_concepts = [c for c in REQUIRED_CONCEPTS if c not in concept_ids]
    if missing_concepts:
        raise RuntimeError(f"reconciliation: canonical concepts not seeded yet: {missing_concepts}")

    metric_names = list(BALANCE_SHEET_CONCEPTS.keys())
    with conn.cursor() as cur:
        cur.execute("select metric_name, id from analytics.metric_definition where metric_name = any(%s)", (metric_names,))
        metric_ids = dict(cur.fetchall())
    missing_metrics = [m for m in metric_names if m not in metric_ids]
    if missing_metrics:
        raise RuntimeError(f"reconciliation: metric_definition rows not seeded yet: {missing_metrics}")

    with conn.cursor() as cur:
        cur.execute("select cik, id from core.company where cik = any(%s)", (sorted(ciks),))
        company_id_by_cik = dict(cur.fetchall())

    totals = {"considered": 0, "ok": 0, "no_company": 0, "errored": 0, "computed": 0, "null": 0}
    for cik in sorted(ciks):
        totals["considered"] += 1
        company_id = company_id_by_cik.get(cik)
        if company_id is None:
            totals["no_company"] += 1
            continue
        try:
            stats = calculate_reconciliation_for_company(conn, company_id, metric_ids, concept_ids)
        except Exception as exc:
            totals["errored"] += 1
            log_error(conn, "analytics.mapper_error", cik, "reconciliation", exc)
            continue
        totals["ok"] += 1
        totals["computed"] += stats["computed"]
        totals["null"] += stats["null"]
    logger.info("reconciliation.done", **totals)
    return totals
