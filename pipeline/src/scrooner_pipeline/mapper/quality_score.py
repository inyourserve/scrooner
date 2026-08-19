"""Piotroski F-Score (0-9) -- doc 26 Sec 2 (business-quality boolean
flags / composite scores), built 2026-08-19. Standard 9-binary-test
formulation (Piotroski, 2000), each fiscal year compared against the
PRIOR fiscal year:

Profitability (4):
  1. ROA > 0                          (net_income / total_assets, current year)
  2. CFO > 0                          (current year)
  3. Delta ROA > 0                    (ROA improved vs prior year)
  4. CFO > Net Income                 (accruals/earnings-quality test, current year)

Leverage/Liquidity/Funding (3):
  5. Delta Leverage < 0               (total_debt / total_assets DECREASED vs prior year)
  6. Delta Current Ratio > 0          (current_assets / current_liabilities IMPROVED)
  7. No new shares issued             (shares_outstanding did NOT increase vs prior year)

Operating Efficiency (2):
  8. Delta Gross Margin > 0           (gross_profit / revenue IMPROVED)
  9. Delta Asset Turnover > 0         (revenue / total_assets IMPROVED)

All 9 raw inputs (net_income, cfo, total_assets, current_assets,
current_liabilities, revenue, gross_profit, total_debt,
shares_outstanding) are already-mapped canonical concepts -- zero new
fetches, zero new concept curation, confirmed live before writing this
(doc 26 Sec 2's own finding).

Deliberately requires ALL 9 inputs present for BOTH the current and
prior fiscal year -- no partial/scaled score; a Piotroski score computed
from 6 of 9 tests is a different, less meaningful number, not a fuzzy
approximation of the real one. This means the score is correctly null
for financial institutions (JPM, ARCC): banks/BDCs don't report a
classified current/non-current balance sheet or a gross-profit/COGS
split, since Piotroski's own methodology was designed for and validated
on non-financial companies -- a real, expected null, not a coverage gap
to chase later.

FY-only (mirrors roic/roe/debtor_days's own FY_ONLY_METRICS precedent):
this composite compares year-over-year balance-sheet/income-statement
levels, so a quarter-vs-FY(prior) comparison would mix mismatched
scales for several of the 9 tests.
"""

from decimal import Decimal

import psycopg
import structlog

from scrooner_pipeline.common.errors import log_error

logger = structlog.get_logger()

REQUIRED_CONCEPTS = [
    "net_income", "cfo", "total_assets", "current_assets", "current_liabilities",
    "revenue", "gross_profit", "total_debt", "shares_outstanding",
]


def _load_concept_ids(conn: psycopg.Connection) -> dict[str, int]:
    with conn.cursor() as cur:
        cur.execute("select name, id from analytics.canonical_concept where name = any(%s)", (REQUIRED_CONCEPTS,))
        return dict(cur.fetchall())


def _load_fy_facts(conn: psycopg.Connection, company_id: int, concept_ids: dict[str, int]) -> dict[str, dict[int, Decimal]]:
    """concept_name -> {fiscal_year: value}, FY periods only."""
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


def _score_year(vals_t: dict[str, Decimal], vals_p: dict[str, Decimal]) -> tuple[int | None, str | None]:
    """vals_t = current fiscal year's 9 values, vals_p = prior fiscal
    year's 9 values -- both dicts must already have all 9 keys present
    (checked by the caller) before this is called."""
    net_income_t, cfo_t, assets_t, ca_t, cl_t, rev_t, gp_t, debt_t, shares_t = (
        vals_t["net_income"], vals_t["cfo"], vals_t["total_assets"], vals_t["current_assets"],
        vals_t["current_liabilities"], vals_t["revenue"], vals_t["gross_profit"], vals_t["total_debt"], vals_t["shares_outstanding"],
    )
    net_income_p, cfo_p, assets_p, ca_p, cl_p, rev_p, gp_p, debt_p, shares_p = (
        vals_p["net_income"], vals_p["cfo"], vals_p["total_assets"], vals_p["current_assets"],
        vals_p["current_liabilities"], vals_p["revenue"], vals_p["gross_profit"], vals_p["total_debt"], vals_p["shares_outstanding"],
    )
    if assets_t == 0 or assets_p == 0 or rev_t == 0 or rev_p == 0 or cl_t == 0 or cl_p == 0:
        return None, "zero_denominator"

    roa_t = net_income_t / assets_t
    roa_p = net_income_p / assets_p
    leverage_t = debt_t / assets_t
    leverage_p = debt_p / assets_p
    current_ratio_t = ca_t / cl_t
    current_ratio_p = ca_p / cl_p
    gross_margin_t = gp_t / rev_t
    gross_margin_p = gp_p / rev_p
    turnover_t = rev_t / assets_t
    turnover_p = rev_p / assets_p

    score = 0
    score += 1 if roa_t > 0 else 0
    score += 1 if cfo_t > 0 else 0
    score += 1 if roa_t > roa_p else 0
    score += 1 if cfo_t > net_income_t else 0
    score += 1 if leverage_t < leverage_p else 0
    score += 1 if current_ratio_t > current_ratio_p else 0
    score += 1 if shares_t <= shares_p else 0
    score += 1 if gross_margin_t > gross_margin_p else 0
    score += 1 if turnover_t > turnover_p else 0
    return score, None


def calculate_piotroski_for_company(conn: psycopg.Connection, company_id: int, metric_id: int, concept_ids: dict[str, int]) -> dict:
    fy_facts = _load_fy_facts(conn, company_id, concept_ids)
    all_years: set[int] = set()
    for by_year in fy_facts.values():
        all_years.update(by_year.keys())

    rows: list[dict] = []
    for fy in sorted(all_years):
        prior_fy = fy - 1
        vals_t: dict[str, Decimal] = {}
        vals_p: dict[str, Decimal] = {}
        missing: list[str] = []
        for name in REQUIRED_CONCEPTS:
            if fy in fy_facts[name]:
                vals_t[name] = fy_facts[name][fy]
            else:
                missing.append(f"{name}({fy})")
            if prior_fy in fy_facts[name]:
                vals_p[name] = fy_facts[name][prior_fy]
            else:
                missing.append(f"{name}({prior_fy})")

        # metric_value has no period_id column (start/end/label only) --
        # reuse the FY period's own start/end dates, sourced via the
        # net_income concept (arbitrary choice among the 9; all 9 share
        # the same FY period row per doc 09's period-normalization design).
        with conn.cursor() as cur:
            cur.execute(
                """
                select p.start_date, p.end_date
                from analytics.canonical_fact cf
                join core.period p on p.id = cf.period_id
                where cf.company_id = %s and cf.canonical_concept_id = %s and p.fiscal_period = 'FY' and p.fiscal_year = %s
                limit 1
                """,
                (company_id, concept_ids["net_income"], fy),
            )
            period_row = cur.fetchone()
        if period_row is None:
            continue
        start, end = period_row

        if missing:
            reason = "missing:" + ",".join(missing[:3])
            if len(missing) > 3:
                reason += "..."
            rows.append({
                "company_id": company_id, "metric_definition_id": metric_id,
                "period_start": start, "period_end": end, "period_label": "FY",
                "value": None, "is_null_reason": reason,
                "source_fact_ids": None,
            })
            continue

        score, reason = _score_year(vals_t, vals_p)
        rows.append({
            "company_id": company_id, "metric_definition_id": metric_id,
            "period_start": start, "period_end": end, "period_label": "FY",
            "value": Decimal(score) if score is not None else None, "is_null_reason": reason,
            "source_fact_ids": None,
        })

    with conn.cursor() as cur:
        cur.execute(
            "delete from analytics.metric_value where company_id = %s and metric_definition_id = %s and period_label = 'FY'",
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
    logger.info("quality_score.company_done", company_id=company_id, computed=computed, null=null)
    return {"computed": computed, "null": null}


def calculate_piotroski(conn: psycopg.Connection, ciks: set[str]) -> dict:
    concept_ids = _load_concept_ids(conn)
    missing_concepts = [c for c in REQUIRED_CONCEPTS if c not in concept_ids]
    if missing_concepts:
        raise RuntimeError(f"quality_score: canonical concepts not seeded yet: {missing_concepts}")

    with conn.cursor() as cur:
        cur.execute("select id from analytics.metric_definition where metric_name = 'piotroski_f_score'")
        row = cur.fetchone()
        if row is None:
            raise RuntimeError("quality_score: piotroski_f_score metric_definition not seeded yet -- run seed-expanded-definitions first")
        metric_id = row[0]

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
            stats = calculate_piotroski_for_company(conn, company_id, metric_id, concept_ids)
        except Exception as exc:
            totals["errored"] += 1
            log_error(conn, "analytics.mapper_error", cik, "quality_score", exc)
            continue
        totals["ok"] += 1
        totals["computed"] += stats["computed"]
        totals["null"] += stats["null"]

    logger.info("quality_score.done", **totals)
    return totals
