"""Business-quality boolean/count flags (doc 26 Sec 2.9), built 2026-08-19.
The study's own framing: "cheap to compute... disproportionately
valuable." Four flags, all sourced from already-mapped canonical
concepts -- zero new fetches, zero new concept curation:

- fcf_gt_net_income (0/1, per FY): (CFO - CapEx) > Net Income for that
  year -- an earnings-quality divergence signal (cash generation
  outpacing accounting profit), the same idea as Piotroski's own
  accrual test, exposed here as its own year-by-year flag rather than
  folded into a composite score.
- zero_debt (0/1, per FY): total_debt == 0 for that year. Deliberately
  distinguishes "reported and genuinely zero" (0) from "not reported at
  all" (null, via the standard missing-concept path) -- a company with
  NO total_debt canonical_fact row for a year gets a null flag, never a
  silently-assumed True. Absence is not evidence of debt-free status.
- profitable_streak_years (count, 0+, "as of" the latest FY only, not a
  per-year series): consecutive most-recent FY years with positive net
  income, counted backward from the latest year until a non-positive or
  missing year breaks the streak.
- margin_expanding_3yr (0/1, "as of" the latest FY only): gross margin
  strictly increasing across the 3 most recent consecutive FY years.
  Null if fewer than 3 consecutive years of gross_profit/revenue exist.

All four are FY-only, same FY_ONLY_METRICS-style reasoning as
quality_score.py's Piotroski score and calculate.py's "days" metrics --
quarterly figures at different scales would corrupt a year-over-year or
streak comparison.
"""

from datetime import date
from decimal import Decimal

import psycopg
import structlog

from scrooner_pipeline.common.errors import log_error, safe_rollback

logger = structlog.get_logger()

REQUIRED_CONCEPTS = [
    "net_income",
    "cfo",
    "capex",
    "total_debt_resolved",
    "gross_profit",
    "revenue",
]


def _load_concept_ids(conn: psycopg.Connection) -> dict[str, int]:
    with conn.cursor() as cur:
        cur.execute(
            "select name, id from analytics.canonical_concept where name = any(%s)",
            (REQUIRED_CONCEPTS,),
        )
        return dict(cur.fetchall())


def _load_fy_facts(
    conn: psycopg.Connection, company_id: int, concept_ids: dict[str, int]
) -> dict[str, dict[int, Decimal]]:
    """concept_name -> {fiscal_year: value}, FY periods only -- same
    shape as quality_score.py's own loader, kept separate here rather
    than shared since the two modules' concept sets differ."""
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


def _fy_period_dates(
    conn: psycopg.Connection, company_id: int, anchor_concept_id: int, fiscal_year: int
):
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


def _row(
    company_id: int,
    metric_id: int,
    start,
    end,
    value: Decimal | None,
    reason: str | None,
) -> dict:
    # period_start/period_end are NOT NULL -- when no real FY period was
    # resolvable (a null row with no anchor at all), fall back to today,
    # same "as-of" pattern expanded_metrics.py already established.
    if start is None or end is None:
        start = end = date.today()
    return {
        "company_id": company_id,
        "metric_definition_id": metric_id,
        "period_start": start,
        "period_end": end,
        "period_label": "FY",
        "value": value,
        "is_null_reason": reason,
        "source_fact_ids": None,
    }


def calculate_quality_flags_for_company(
    conn: psycopg.Connection,
    company_id: int,
    metric_ids: dict[str, int],
    concept_ids: dict[str, int],
) -> dict:
    facts = _load_fy_facts(conn, company_id, concept_ids)
    all_years = sorted(set().union(*(facts[name].keys() for name in facts)))

    rows: list[dict] = []

    # --- fcf_gt_net_income + zero_debt: one row per FY year ---
    for fy in all_years:
        period = (
            _fy_period_dates(conn, company_id, concept_ids["net_income"], fy)
            if fy in facts["net_income"]
            else None
        )
        if period is None:
            # No net_income period anchor for this year -- try total_debt's
            # own anchor instead, since zero_debt doesn't need net_income.
            period = _fy_period_dates(
                conn, company_id, concept_ids["total_debt_resolved"], fy
            )
        if period is None:
            continue
        start, end = period

        if "fcf_gt_net_income" in metric_ids:
            if (
                fy not in facts["cfo"]
                or fy not in facts["capex"]
                or fy not in facts["net_income"]
            ):
                missing = [
                    n for n in ("cfo", "capex", "net_income") if fy not in facts[n]
                ]
                rows.append(
                    _row(
                        company_id,
                        metric_ids["fcf_gt_net_income"],
                        start,
                        end,
                        None,
                        f"missing:{','.join(missing)}({fy})",
                    )
                )
            else:
                fcf = facts["cfo"][fy] - facts["capex"][fy]
                rows.append(
                    _row(
                        company_id,
                        metric_ids["fcf_gt_net_income"],
                        start,
                        end,
                        Decimal(1) if fcf > facts["net_income"][fy] else Decimal(0),
                        None,
                    )
                )

        if "zero_debt" in metric_ids:
            if fy not in facts["total_debt_resolved"]:
                rows.append(
                    _row(
                        company_id,
                        metric_ids["zero_debt"],
                        start,
                        end,
                        None,
                        f"missing:total_debt({fy})",
                    )
                )
            else:
                rows.append(
                    _row(
                        company_id,
                        metric_ids["zero_debt"],
                        start,
                        end,
                        Decimal(1)
                        if facts["total_debt_resolved"][fy] == 0
                        else Decimal(0),
                        None,
                    )
                )

    # --- profitable_streak_years: single "as of latest FY" value ---
    if "profitable_streak_years" in metric_ids and all_years:
        latest_fy = max(all_years)
        period = _fy_period_dates(
            conn, company_id, concept_ids["net_income"], latest_fy
        )
        if period is None or latest_fy not in facts["net_income"]:
            rows.append(
                _row(
                    company_id,
                    metric_ids["profitable_streak_years"],
                    None,
                    None,
                    None,
                    f"missing:net_income({latest_fy})",
                )
            )
        else:
            start, end = period
            streak = 0
            fy = latest_fy
            while fy in facts["net_income"] and facts["net_income"][fy] > 0:
                streak += 1
                fy -= 1
            rows.append(
                _row(
                    company_id,
                    metric_ids["profitable_streak_years"],
                    start,
                    end,
                    Decimal(streak),
                    None,
                )
            )

    # --- margin_expanding_3yr: single "as of latest FY" value ---
    if "margin_expanding_3yr" in metric_ids and all_years:
        margin_years = sorted(
            y
            for y in all_years
            if y in facts["gross_profit"]
            and y in facts["revenue"]
            and facts["revenue"][y] != 0
        )
        if len(margin_years) < 3:
            rows.append(
                _row(
                    company_id,
                    metric_ids["margin_expanding_3yr"],
                    None,
                    None,
                    None,
                    "missing:fewer_than_3_years_gross_margin",
                )
            )
        else:
            latest_three = margin_years[-3:]
            if latest_three[-1] - latest_three[0] != 2:
                # Not 3 CONSECUTIVE fiscal years (a gap in the data) --
                # a margin trend across non-adjacent years isn't the
                # "3yr running" signal doc 26 actually asked for.
                rows.append(
                    _row(
                        company_id,
                        metric_ids["margin_expanding_3yr"],
                        None,
                        None,
                        None,
                        "missing:non_consecutive_years",
                    )
                )
            else:
                margins = [
                    facts["gross_profit"][y] / facts["revenue"][y] for y in latest_three
                ]
                expanding = margins[0] < margins[1] < margins[2]
                period = _fy_period_dates(
                    conn, company_id, concept_ids["revenue"], latest_three[-1]
                )
                start, end = period if period else (None, None)
                rows.append(
                    _row(
                        company_id,
                        metric_ids["margin_expanding_3yr"],
                        start,
                        end,
                        Decimal(1) if expanding else Decimal(0),
                        None,
                    )
                )

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
    logger.info(
        "quality_flags.company_done",
        company_id=company_id,
        computed=computed,
        null=null,
    )
    return {"computed": computed, "null": null}


def calculate_quality_flags(conn: psycopg.Connection, ciks: set[str]) -> dict:
    concept_ids = _load_concept_ids(conn)
    missing_concepts = [c for c in REQUIRED_CONCEPTS if c not in concept_ids]
    if missing_concepts:
        raise RuntimeError(
            f"quality_flags: canonical concepts not seeded yet: {missing_concepts}"
        )

    metric_names = [
        "fcf_gt_net_income",
        "zero_debt",
        "profitable_streak_years",
        "margin_expanding_3yr",
    ]
    with conn.cursor() as cur:
        cur.execute(
            "select metric_name, id from analytics.metric_definition where metric_name = any(%s)",
            (metric_names,),
        )
        metric_ids = dict(cur.fetchall())
    missing_metrics = [m for m in metric_names if m not in metric_ids]
    if missing_metrics:
        raise RuntimeError(
            f"quality_flags: metric_definitions not seeded yet: {missing_metrics} -- run seed-expanded-definitions first"
        )

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
            stats = calculate_quality_flags_for_company(
                conn, company_id, metric_ids, concept_ids
            )
        except Exception as exc:
            totals["errored"] += 1
            log_error(conn, "analytics.mapper_error", cik, "quality_flags", exc)
            conn = safe_rollback(conn, stage="quality_flags", cik=cik)
            continue
        totals["ok"] += 1
        totals["computed"] += stats["computed"]
        totals["null"] += stats["null"]

    logger.info("quality_flags.done", **totals)
    return totals
