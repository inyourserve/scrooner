"""Stage 3e -- TTM and growth windows (doc 11). Two independent jobs:

1. Growth metrics (revenue_growth_yoy/3y_cagr, eps_growth_yoy/3y_cagr) --
   deferred from Stage 3d since they compare two different periods of the
   same company, not a single period's inputs. Matches same fiscal_period
   across fiscal years (Q1 vs year-ago Q1, FY vs year-ago FY, etc.) so
   seasonality never distorts the comparison -- this is exactly why the
   comparison is done on matching fiscal_period, not on unrelated periods.

2. Trailing-twelve-month ROIC/ROE for quarterly periods -- Stage 3d
   deliberately left these FY-only, since naively computing them from a
   bare quarter distorts badly (doc 09's Day 3 finding: 127.8% vs a sane
   31.95% for AAPL). Verified live 2026-08-16 before implementing: summing
   AAPL's four quarterly operating_income facts (Q1-Q4 FY2024) reproduces
   the reported FY2024 figure exactly ($123,216,000,000) -- confirms
   trailing-4-quarter reconstruction via fiscal_year/fiscal_period lookup
   is sound, not just theoretically appealing.

TTM period matching uses (fiscal_year, fiscal_period) arithmetic, not raw
date math -- for a target quarter (Y, Q), the trailing 4 quarters are:
    Q4 -> (Y,Q1),(Y,Q2),(Y,Q3),(Y,Q4)         [equals the FY figure -- used as a cross-check]
    Q3 -> (Y-1,Q4),(Y,Q1),(Y,Q2),(Y,Q3)
    Q2 -> (Y-1,Q3),(Y-1,Q4),(Y,Q1),(Y,Q2)
    Q1 -> (Y-1,Q2),(Y-1,Q3),(Y-1,Q4),(Y,Q1)
All 4 must resolve or the TTM value is null with a reason -- same
completeness discipline as Stage 3d's per-role check, not "sum whatever's
available."
"""

from decimal import Decimal

import psycopg
import structlog

from scrooner_pipeline.common.errors import log_error

logger = structlog.get_logger()

GROWTH_METRICS = {
    "revenue_growth_yoy": ("revenue", 1),
    "revenue_growth_3y_cagr": ("revenue", 3),
    "eps_growth_yoy": ("diluted_eps", 1),
    "eps_growth_3y_cagr": ("diluted_eps", 3),
}

QUARTER_ORDER = ["Q1", "Q2", "Q3", "Q4"]


def _trailing_quarters(fiscal_year: int, fiscal_period: str) -> list[tuple[int, str]]:
    idx = QUARTER_ORDER.index(fiscal_period)
    seq: list[tuple[int, str]] = []
    y, i = fiscal_year, idx
    for _ in range(4):
        seq.append((y, QUARTER_ORDER[i]))
        i -= 1
        if i < 0:
            i = 3
            y -= 1
    return list(reversed(seq))


def _load_metric_ids(conn: psycopg.Connection) -> dict[str, int]:
    with conn.cursor() as cur:
        cur.execute("select metric_name, id from analytics.metric_definition where metric_name = any(%s)", (list(GROWTH_METRICS) + ["roic", "roe"],))
        return dict(cur.fetchall())


def _load_concept_id(conn: psycopg.Connection, name: str) -> int:
    with conn.cursor() as cur:
        cur.execute("select id from analytics.canonical_concept where name = %s", (name,))
        return cur.fetchone()[0]


def _load_company_facts(conn: psycopg.Connection, company_id: int, concept_id: int) -> dict:
    """(fiscal_year, fiscal_period) -> (value, fact_ids, period_start, period_end) for one concept."""
    with conn.cursor() as cur:
        cur.execute(
            """
            select p.fiscal_year, p.fiscal_period, cf.value, cf.source_fact_ids, p.start_date, p.end_date
            from analytics.canonical_fact cf
            join core.period p on p.id = cf.period_id
            where cf.company_id = %s and cf.canonical_concept_id = %s and p.fiscal_period is not null
            """,
            (company_id, concept_id),
        )
        return {(fy, fp): (val, fids, start, end) for fy, fp, val, fids, start, end in cur.fetchall()}


def _compute_growth_for_company(conn: psycopg.Connection, company_id: int, metric_ids: dict[str, int]) -> dict:
        rows: list[dict] = []
        for metric_name, (concept_name, lag_years) in GROWTH_METRICS.items():
            concept_id = _load_concept_id(conn, concept_name)
            by_period = _load_company_facts(conn, company_id, concept_id)
            for (fy, fp), (value_t, fids_t, start_t, end_t) in by_period.items():
                prior_key = (fy - lag_years, fp)
                prior = by_period.get(prior_key)
                if prior is None:
                    rows.append(
                        {
                            "company_id": company_id, "metric_definition_id": metric_ids[metric_name],
                            "period_start": start_t, "period_end": end_t, "period_label": fp,
                            "value": None, "is_null_reason": f"missing:prior_period({prior_key[0]}_{fp})",
                            "source_fact_ids": None,
                        }
                    )
                    continue
                value_prior, fids_prior, _s, _e = prior
                if value_prior == 0:
                    rows.append(
                        {"company_id": company_id, "metric_definition_id": metric_ids[metric_name],
                         "period_start": start_t, "period_end": end_t, "period_label": fp,
                         "value": None, "is_null_reason": "zero_base_value", "source_fact_ids": None}
                    )
                    continue
                if lag_years == 1:
                    growth = (value_t - value_prior) / value_prior
                else:
                    ratio = value_t / value_prior
                    if ratio < 0:
                        rows.append(
                            {"company_id": company_id, "metric_definition_id": metric_ids[metric_name],
                             "period_start": start_t, "period_end": end_t, "period_label": fp,
                             "value": None, "is_null_reason": "negative_ratio_undefined_cagr", "source_fact_ids": None}
                        )
                        continue
                    growth = ratio ** (Decimal(1) / Decimal(lag_years)) - 1
                rows.append(
                    {"company_id": company_id, "metric_definition_id": metric_ids[metric_name],
                     "period_start": start_t, "period_end": end_t, "period_label": fp,
                     "value": growth, "is_null_reason": None, "source_fact_ids": list(fids_t) + list(fids_prior)}
                )

        with conn.cursor() as cur:
            metric_id_list = [metric_ids[m] for m in GROWTH_METRICS]
            cur.execute(
                "delete from analytics.metric_value where company_id = %s and metric_definition_id = any(%s)",
                (company_id, metric_id_list),
            )
            if rows:
                cur.executemany(
                    """
                    insert into analytics.metric_value
                        (company_id, metric_definition_id, period_start, period_end, period_label,
                         value, is_null_reason, source_fact_ids)
                    values
                        (%(company_id)s, %(metric_definition_id)s, %(period_start)s, %(period_end)s, %(period_label)s,
                         %(value)s, %(is_null_reason)s, %(source_fact_ids)s)
                    """,
                    rows,
                )
            conn.commit()
        return {
            "computed": sum(1 for r in rows if r["value"] is not None),
            "null": sum(1 for r in rows if r["value"] is None),
        }


def compute_growth(conn: psycopg.Connection, ciks: set[str]) -> dict:
    metric_ids = _load_metric_ids(conn)
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
            stats = _compute_growth_for_company(conn, company_id, metric_ids)
        except Exception as exc:
            totals["errored"] += 1
            log_error(conn, "analytics.mapper_error", cik, "growth", exc)
            continue
        totals["ok"] += 1
        totals["computed"] += stats["computed"]
        totals["null"] += stats["null"]
        logger.info("ttm.growth_done", cik=cik, computed=stats["computed"], null=stats["null"])

    logger.info("ttm.growth.done", **totals)
    return totals


# --- TTM ROIC/ROE for quarterly periods ---

ROIC_CONCEPTS = {
    "operating_income": "nopat_base",
    "income_tax_expense": "tax_rate_numerator",
    "income_before_tax": "tax_rate_denominator",
}
ROE_CONCEPTS = {"net_income": "numerator"}
INSTANT_CONCEPTS = {"total_debt": "invested_capital_add", "stockholders_equity": ("invested_capital_add", "denominator"), "cash_and_equivalents": "invested_capital_subtract"}


def _ttm_sum(by_period: dict, fiscal_year: int, fiscal_period: str) -> tuple[Decimal | None, list[int]]:
    needed = _trailing_quarters(fiscal_year, fiscal_period)
    total = Decimal(0)
    fact_ids: list[int] = []
    for key in needed:
        hit = by_period.get(key)
        if hit is None:
            return None, []
        value, fids, _s, _e = hit
        total += value
        fact_ids.extend(fids)
    return total, fact_ids


def _compute_ttm_returns_for_company(conn: psycopg.Connection, company_id: int, metric_ids: dict[str, int], concept_ids: dict[str, int]) -> dict:
        by_concept = {name: _load_company_facts(conn, company_id, cid) for name, cid in concept_ids.items()}
        # Instant facts indexed by end_date for matching against a quarter's own balance-sheet date.
        instant_by_end_date = {}
        for name in ("total_debt", "stockholders_equity", "cash_and_equivalents"):
            instant_by_end_date[name] = {end: (val, fids) for (_fy, _fp), (val, fids, _s, end) in by_concept[name].items()}

        # Every (fiscal_year, Q1-4) this company has ANY operating_income or net_income for.
        quarter_keys = {k for k in by_concept["operating_income"] if k[1] in QUARTER_ORDER} | \
                       {k for k in by_concept["net_income"] if k[1] in QUARTER_ORDER}

        rows: list[dict] = []
        for fy, fp in quarter_keys:
            end_date = (by_concept["operating_income"].get((fy, fp)) or by_concept["net_income"].get((fy, fp)))[3]
            start_date = end_date  # TTM window end; period_start intentionally same as end for a "TTM as of" marker

            # ROIC (TTM)
            ttm_op_income, fids_op = _ttm_sum(by_concept["operating_income"], fy, fp)
            ttm_tax_num, fids_tax_num = _ttm_sum(by_concept["income_tax_expense"], fy, fp)
            ttm_tax_denom, fids_tax_denom = _ttm_sum(by_concept["income_before_tax"], fy, fp)
            debt_hit = instant_by_end_date["total_debt"].get(end_date)
            equity_hit = instant_by_end_date["stockholders_equity"].get(end_date)
            cash_hit = instant_by_end_date["cash_and_equivalents"].get(end_date)

            if None in (ttm_op_income, ttm_tax_num, ttm_tax_denom) or None in (debt_hit, equity_hit, cash_hit):
                missing = []
                if ttm_op_income is None: missing.append("ttm_operating_income")
                if ttm_tax_num is None: missing.append("ttm_income_tax_expense")
                if ttm_tax_denom is None: missing.append("ttm_income_before_tax")
                if debt_hit is None: missing.append("total_debt")
                if equity_hit is None: missing.append("stockholders_equity")
                if cash_hit is None: missing.append("cash_and_equivalents")
                roic_value, roic_reason, roic_fids = None, f"incomplete:{','.join(missing)}", None
            else:
                tax_rate = ttm_tax_num / ttm_tax_denom if ttm_tax_denom != 0 else None
                if tax_rate is None:
                    roic_value, roic_reason, roic_fids = None, "zero_pretax_income", None
                else:
                    nopat = ttm_op_income * (1 - tax_rate)
                    invested_capital = debt_hit[0] + equity_hit[0] - cash_hit[0]
                    if invested_capital == 0:
                        roic_value, roic_reason, roic_fids = None, "zero_invested_capital", None
                    else:
                        roic_value = nopat / invested_capital
                        roic_reason = None
                        roic_fids = fids_op + fids_tax_num + fids_tax_denom + list(debt_hit[1]) + list(equity_hit[1]) + list(cash_hit[1])

            rows.append(
                {"company_id": company_id, "metric_definition_id": metric_ids["roic"],
                 "period_start": start_date, "period_end": end_date, "period_label": "TTM",
                 "value": roic_value, "is_null_reason": roic_reason, "source_fact_ids": roic_fids}
            )

            # ROE (TTM)
            ttm_net_income, fids_ni = _ttm_sum(by_concept["net_income"], fy, fp)
            if ttm_net_income is None or equity_hit is None:
                roe_value = None
                roe_reason = "incomplete:ttm_net_income" if ttm_net_income is None else "incomplete:stockholders_equity"
                roe_fids = None
            elif equity_hit[0] == 0:
                roe_value, roe_reason, roe_fids = None, "zero_denominator", None
            else:
                roe_value = ttm_net_income / equity_hit[0]
                roe_reason = None
                roe_fids = fids_ni + list(equity_hit[1])

            rows.append(
                {"company_id": company_id, "metric_definition_id": metric_ids["roe"],
                 "period_start": start_date, "period_end": end_date, "period_label": "TTM",
                 "value": roe_value, "is_null_reason": roe_reason, "source_fact_ids": roe_fids}
            )

        with conn.cursor() as cur:
            cur.execute(
                """
                delete from analytics.metric_value
                where company_id = %s and metric_definition_id = any(%s) and period_label = 'TTM'
                """,
                (company_id, [metric_ids["roic"], metric_ids["roe"]]),
            )
            if rows:
                cur.executemany(
                    """
                    insert into analytics.metric_value
                        (company_id, metric_definition_id, period_start, period_end, period_label,
                         value, is_null_reason, source_fact_ids)
                    values
                        (%(company_id)s, %(metric_definition_id)s, %(period_start)s, %(period_end)s, %(period_label)s,
                         %(value)s, %(is_null_reason)s, %(source_fact_ids)s)
                    """,
                    rows,
                )
            conn.commit()
        return {
            "computed": sum(1 for r in rows if r["value"] is not None),
            "null": sum(1 for r in rows if r["value"] is None),
        }


def compute_ttm_returns(conn: psycopg.Connection, ciks: set[str]) -> dict:
    metric_ids = _load_metric_ids(conn)
    concept_ids = {
        name: _load_concept_id(conn, name)
        for name in ("operating_income", "income_tax_expense", "income_before_tax", "net_income",
                      "total_debt", "stockholders_equity", "cash_and_equivalents")
    }
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
            stats = _compute_ttm_returns_for_company(conn, company_id, metric_ids, concept_ids)
        except Exception as exc:
            totals["errored"] += 1
            log_error(conn, "analytics.mapper_error", cik, "ttm_returns", exc)
            continue
        totals["ok"] += 1
        totals["computed"] += stats["computed"]
        totals["null"] += stats["null"]
        logger.info("ttm.returns_done", cik=cik, computed=stats["computed"], null=stats["null"])

    logger.info("ttm.returns.done", **totals)
    return totals
