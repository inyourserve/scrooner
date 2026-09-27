"""Effective Tax Rate cross-check (utilization-study ranked idea #5,
built 2026-08-22): compares the company's own reported
effective_tax_rate_reported against the rate ROIC already derives
internally (income_tax_expense / income_before_tax) for the SAME
period. Not a replacement for either figure -- a real, signed gap is the
useful signal (large discrete tax items, e.g. a one-time credit/charge,
that year), same "diagnostic, not a locked ratio" framing as
mapper/reconciliation.py's cash-flow cross-checks.

All three concepts (effective_tax_rate_reported, income_tax_expense,
income_before_tax) are income_statement/duration, so they share the
same period_id for a given company/period -- no instant/duration
matching complexity needed, unlike calculate.py's ROIC handling.
Computed for every period where all three resolve, not FY-restricted --
a tax rate is a pure ratio, no annualization distortion the way ROIC/
"days" metrics have (checked live: EffectiveIncomeTaxRateContinuingOperations
resolves at both FY and quarterly granularity in real data).
"""

import psycopg
import structlog

from scrooner_pipeline.common.errors import log_error

logger = structlog.get_logger()

REQUIRED_CONCEPTS = [
    "effective_tax_rate_reported",
    "income_tax_expense",
    "income_before_tax",
]


def _load_concept_ids(conn: psycopg.Connection) -> dict[str, int]:
    with conn.cursor() as cur:
        cur.execute(
            "select name, id from analytics.canonical_concept where name = any(%s)",
            (REQUIRED_CONCEPTS,),
        )
        return dict(cur.fetchall())


def calculate_tax_reconciliation_for_company(
    conn: psycopg.Connection,
    company_id: int,
    metric_id: int,
    concept_ids: dict[str, int],
) -> dict:
    id_to_name = {v: k for k, v in concept_ids.items()}
    with conn.cursor() as cur:
        cur.execute(
            """
            select cf.canonical_concept_id, cf.period_id, cf.value, p.start_date, p.end_date, p.fiscal_period
            from analytics.canonical_fact cf
            join core.period p on p.id = cf.period_id
            where cf.company_id = %s and cf.canonical_concept_id = any(%s)
            """,
            (company_id, list(concept_ids.values())),
        )
        by_concept_by_period: dict[str, dict[int, tuple]] = {
            name: {} for name in concept_ids
        }
        period_dates: dict[int, tuple] = {}
        for concept_id, period_id, value, start, end, fiscal_period in cur.fetchall():
            by_concept_by_period[id_to_name[concept_id]][period_id] = value
            period_dates[period_id] = (start, end, fiscal_period)

    reported = by_concept_by_period["effective_tax_rate_reported"]
    tax_expense = by_concept_by_period["income_tax_expense"]
    pretax_income = by_concept_by_period["income_before_tax"]

    rows: list[dict] = []
    for period_id, reported_rate in reported.items():
        start, end, fiscal_period = period_dates[period_id]
        if fiscal_period is None:
            continue
        if period_id not in tax_expense:
            rows.append(
                {
                    "company_id": company_id,
                    "metric_definition_id": metric_id,
                    "period_start": start,
                    "period_end": end,
                    "period_label": fiscal_period,
                    "value": None,
                    "is_null_reason": "missing:income_tax_expense",
                    "source_fact_ids": None,
                }
            )
            continue
        if period_id not in pretax_income:
            rows.append(
                {
                    "company_id": company_id,
                    "metric_definition_id": metric_id,
                    "period_start": start,
                    "period_end": end,
                    "period_label": fiscal_period,
                    "value": None,
                    "is_null_reason": "missing:income_before_tax",
                    "source_fact_ids": None,
                }
            )
            continue
        if pretax_income[period_id] == 0:
            rows.append(
                {
                    "company_id": company_id,
                    "metric_definition_id": metric_id,
                    "period_start": start,
                    "period_end": end,
                    "period_label": fiscal_period,
                    "value": None,
                    "is_null_reason": "zero_denominator",
                    "source_fact_ids": None,
                }
            )
            continue
        derived_rate = tax_expense[period_id] / pretax_income[period_id]
        rows.append(
            {
                "company_id": company_id,
                "metric_definition_id": metric_id,
                "period_start": start,
                "period_end": end,
                "period_label": fiscal_period,
                "value": reported_rate - derived_rate,
                "is_null_reason": None,
                "source_fact_ids": None,
            }
        )

    with conn.cursor() as cur:
        cur.execute(
            "delete from analytics.metric_value where company_id = %s and metric_definition_id = %s",
            (company_id, metric_id),
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
    logger.info(
        "tax_reconciliation.company_done",
        company_id=company_id,
        computed=computed,
        null=null,
    )
    return {"computed": computed, "null": null}


def calculate_tax_reconciliation(conn: psycopg.Connection, ciks: set[str]) -> dict:
    concept_ids = _load_concept_ids(conn)
    missing_concepts = [c for c in REQUIRED_CONCEPTS if c not in concept_ids]
    if missing_concepts:
        raise RuntimeError(
            f"tax_reconciliation: canonical concepts not seeded yet: {missing_concepts}"
        )

    with conn.cursor() as cur:
        cur.execute(
            "select id from analytics.metric_definition where metric_name = 'effective_tax_rate_gap'"
        )
        row = cur.fetchone()
    if row is None:
        raise RuntimeError(
            "tax_reconciliation: effective_tax_rate_gap metric_definition row not seeded yet"
        )
    metric_id = row[0]

    with conn.cursor() as cur:
        cur.execute(
            "select cik, id from core.company where cik = any(%s)", (sorted(ciks),)
        )
        company_id_by_cik = dict(cur.fetchall())

    totals = {
        "considered": 0,
        "ok": 0,
        "no_company": 0,
        "errored": 0,
        "computed": 0,
        "null": 0,
    }
    for cik in sorted(ciks):
        totals["considered"] += 1
        company_id = company_id_by_cik.get(cik)
        if company_id is None:
            totals["no_company"] += 1
            continue
        try:
            stats = calculate_tax_reconciliation_for_company(
                conn, company_id, metric_id, concept_ids
            )
        except Exception as exc:
            totals["errored"] += 1
            log_error(conn, "analytics.mapper_error", cik, "tax_reconciliation", exc)
            continue
        totals["ok"] += 1
        totals["computed"] += stats["computed"]
        totals["null"] += stats["null"]
    logger.info("tax_reconciliation.done", **totals)
    return totals
