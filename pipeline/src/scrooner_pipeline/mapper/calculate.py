"""Stage 3d -- Point-in-time metric calculation (doc 11). Computes
analytics.metric_value for the 10 EDGAR-only, non-growth metrics (of the
12 EDGAR-only metrics in doc 02, Revenue Growth and EPS Growth are
TTM/multi-period by nature -- Stage 3e's job, not this one's; the 6
price-dependent metrics stay undefined here entirely, per requires_price).

Reads only analytics.canonical_fact (Stage 3b's output) plus
analytics.metric_definition/metric_definition_input (Stage 3c's output) --
never reads core.fact directly, so a fact's authoritative/superseded
status is already resolved by the time this stage sees it.

Every metric here is one of three formula shapes (see FORMULA_SHAPES):
- ratio: sum(numerator inputs) / sum(denominator inputs)
- sum_diff: sum(add inputs) - sum(subtract inputs)
- sum_diff_ratio: (sum(add) - sum(subtract)) / sum(denominator)   [fcf_margin]
- roic: the one genuinely custom formula, per Stage 3c's pinned definition

ROIC and ROE are restricted to FY periods only -- Stage 3c found live that
naively computing either from a bare quarter produces a badly misleading
number (AAPL: 127.8% vs a sane 31.95% ROIC, from a single strong quarter
naively annualized). Every other metric here is flow/flow or point-in-
time/point-in-time and has no such restriction.

Duration-vs-instant period matching (found live 2026-08-16, fixed before
any wrong metric_value shipped): a metric mixing a duration concept
(net_income, an income-statement flow) with an instant concept
(stockholders_equity, a balance-sheet snapshot) cannot match them by
period_id -- AAPL's FY2024 net_income has period_id 601
(2023-10-01..2024-09-28, duration) while its FY2024 stockholders_equity
has period_id 797 (2024-09-28..2024-09-28, instant) -- genuinely different
period rows even though both represent "AAPL FY2024." A naive period_id
match made ROE/ROIC silently null even when every input actually existed.
Fixed: for a metric with any duration input, anchor on the duration
period(s) present and look up instant inputs by END DATE matching the
duration period's end_date, not by period_id. core.concept has no
explicit period-type-per-concept flag, but canonical_concept.statement
already encodes it losslessly: 'balance_sheet' is always instant,
'income_statement'/'cash_flow' are always duration -- verified true for
all 17 canonical concepts, used directly rather than adding a new column.

A metric gets a metric_value row for every period where AT LEAST ONE of
its required inputs resolves -- not literally every period the company
has any data for. If some but not all required inputs are present for
that period, the row is written with value=null and is_null_reason set to
exactly which concept(s) were missing -- a null is a traceable outcome
(doc 04), never silence.
"""

from decimal import Decimal

import psycopg
import structlog

logger = structlog.get_logger()

# Growth metrics are TTM/multi-period -- Stage 3e's job. Price-dependent
# metrics are excluded via metric_definition.requires_price, not this list.
DEFERRED_TO_STAGE_3E = {"revenue_growth_yoy", "revenue_growth_3y_cagr", "eps_growth_yoy", "eps_growth_3y_cagr"}

FY_ONLY_METRICS = {"roic", "roe"}

FORMULA_SHAPES = {
    "gross_margin": "ratio",
    "operating_margin": "ratio",
    "net_margin": "ratio",
    "roe": "ratio",
    "fcf": "sum_diff",
    "fcf_margin": "sum_diff_ratio",
    "debt_to_equity": "ratio",
    "current_ratio": "ratio",
    "interest_coverage_ratio": "ratio",
    "roic": "roic",
}


def _load_target_metrics(conn: psycopg.Connection) -> list[dict]:
    with conn.cursor() as cur:
        cur.execute("select id, metric_name from analytics.metric_definition where requires_price = false")
        rows = cur.fetchall()
        targets = []
        with conn.cursor() as cur2:
            for metric_id, metric_name in rows:
                if metric_name in DEFERRED_TO_STAGE_3E:
                    continue
                cur2.execute(
                    """
                    select cc.name, cc.id, mdi.role, cc.statement
                    from analytics.metric_definition_input mdi
                    join analytics.canonical_concept cc on cc.id = mdi.canonical_concept_id
                    where mdi.metric_definition_id = %s
                    """,
                    (metric_id,),
                )
                # (concept_name, concept_id, role, is_instant)
                inputs = [(name, cid, role, statement == "balance_sheet") for name, cid, role, statement in cur2.fetchall()]
                targets.append({"id": metric_id, "name": metric_name, "inputs": inputs})
    return targets


def _load_canonical_facts(conn: psycopg.Connection, company_id: int) -> dict:
    """by_period_id: concept_id -> period_id -> (value, fact_ids) -- for duration lookups.
    by_end_date: concept_id -> end_date -> (value, fact_ids) -- for instant lookups, keyed
    by date so they can be matched against a duration period's end_date, not its period_id.
    periods: period_id -> (start, end, fiscal_period)."""
    with conn.cursor() as cur:
        cur.execute(
            """
            select cf.canonical_concept_id, cf.period_id, cf.value, cf.source_fact_ids,
                   p.start_date, p.end_date, p.fiscal_period, p.period_type
            from analytics.canonical_fact cf
            join core.period p on p.id = cf.period_id
            where cf.company_id = %s
            """,
            (company_id,),
        )
        by_period_id: dict[int, dict[int, tuple]] = {}
        by_end_date: dict[int, dict] = {}
        periods: dict[int, tuple] = {}
        for concept_id, period_id, value, fact_ids, start, end, fiscal_period, period_type in cur.fetchall():
            by_period_id.setdefault(concept_id, {})[period_id] = (value, fact_ids)
            if period_type == "instant":
                by_end_date.setdefault(concept_id, {})[end] = (value, fact_ids)
            periods[period_id] = (start, end, fiscal_period)
    return {"by_period_id": by_period_id, "by_end_date": by_end_date, "periods": periods}


def _compute(shape: str, values_by_role: dict[str, list[Decimal]]) -> tuple[Decimal | None, str | None]:
    if shape == "ratio":
        num = values_by_role.get("numerator")
        denom = values_by_role.get("denominator")
        if num is None:
            return None, "missing:numerator"
        if denom is None:
            return None, "missing:denominator"
        denom_sum = sum(denom)
        if denom_sum == 0:
            return None, "zero_denominator"
        return sum(num) / denom_sum, None

    if shape == "sum_diff":
        add = values_by_role.get("add")
        subtract = values_by_role.get("subtract")
        if add is None:
            return None, "missing:add"
        if subtract is None:
            return None, "missing:subtract"
        return sum(add) - sum(subtract), None

    if shape == "sum_diff_ratio":
        add = values_by_role.get("add")
        subtract = values_by_role.get("subtract")
        denom = values_by_role.get("denominator")
        if add is None:
            return None, "missing:add"
        if subtract is None:
            return None, "missing:subtract"
        if denom is None:
            return None, "missing:denominator"
        denom_sum = sum(denom)
        if denom_sum == 0:
            return None, "zero_denominator"
        return (sum(add) - sum(subtract)) / denom_sum, None

    if shape == "roic":
        nopat_base = values_by_role.get("nopat_base")
        tax_num = values_by_role.get("tax_rate_numerator")
        tax_denom = values_by_role.get("tax_rate_denominator")
        ic_add = values_by_role.get("invested_capital_add")
        ic_sub = values_by_role.get("invested_capital_subtract")
        if nopat_base is None:
            return None, "missing:nopat_base"
        if tax_num is None:
            return None, "missing:tax_rate_numerator"
        if tax_denom is None:
            return None, "missing:tax_rate_denominator"
        if ic_add is None:
            return None, "missing:invested_capital_add"
        if ic_sub is None:
            return None, "missing:invested_capital_subtract"
        tax_denom_sum = sum(tax_denom)
        if tax_denom_sum == 0:
            return None, "zero_pretax_income"
        tax_rate = sum(tax_num) / tax_denom_sum
        nopat = sum(nopat_base) * (1 - tax_rate)
        invested_capital = sum(ic_add) - sum(ic_sub)
        if invested_capital == 0:
            return None, "zero_invested_capital"
        return nopat / invested_capital, None

    raise ValueError(f"unknown formula shape: {shape}")


def calculate_for_company(conn: psycopg.Connection, company_id: int, targets: list[dict]) -> dict:
    facts = _load_canonical_facts(conn, company_id)
    by_period_id, by_end_date, periods = facts["by_period_id"], facts["by_end_date"], facts["periods"]

    stats = {"computed": 0, "null": 0}
    rows: list[dict] = []

    for target in targets:
        metric_id, metric_name, inputs = target["id"], target["name"], target["inputs"]
        shape = FORMULA_SHAPES[metric_name]
        fy_only = metric_name in FY_ONLY_METRICS

        duration_inputs = [i for i in inputs if not i[3]]
        instant_inputs = [i for i in inputs if i[3]]

        # Anchor on duration periods when any exist (the "reporting period" a
        # mixed metric conceptually belongs to); pure-instant metrics
        # (current_ratio, debt_to_equity) anchor on their own instant periods
        # instead, matched by period_id as before -- both concepts in those
        # metrics are always dated as of the same balance-sheet date.
        anchor_inputs = duration_inputs or instant_inputs
        anchor_concept_ids = {cid for _name, cid, _role, _is_instant in anchor_inputs}
        anchor_period_ids: set[int] = set()
        for concept_id in anchor_concept_ids:
            anchor_period_ids.update(by_period_id.get(concept_id, {}).keys())

        # A role can have MORE THAN ONE expected concept (roic's
        # invested_capital_add covers both total_debt and
        # stockholders_equity). Found live 2026-08-16: checking only
        # "did this role get at least one value" silently drops a missing
        # summand instead of nulling the whole metric -- for AAPL FY2024,
        # total_debt was genuinely unresolved (a real Stage 2e conflict) but
        # stockholders_equity wasn't, so ROIC silently computed using equity
        # alone as "invested capital," reporting 346% instead of null. A
        # role is only usable if EVERY concept mapped to it resolved.
        expected_concepts_by_role: dict[str, set[int]] = {}
        for _name, concept_id, role, _is_instant in inputs:
            expected_concepts_by_role.setdefault(role, set()).add(concept_id)

        for period_id in anchor_period_ids:
            start, end, fiscal_period = periods[period_id]
            if fiscal_period is None:
                # Non-standard duration Stage 2b deliberately left unclassified
                # (e.g. a 6-month YTD span) -- doesn't fit the FY/Q1-4/TTM
                # period_label model this table requires, so it gets no
                # point-in-time metric row at all. Not a bug: doc 09's own
                # Normalizer design already chose not to force a label here.
                continue
            if fy_only and fiscal_period != "FY":
                continue

            values_by_role: dict[str, list[Decimal]] = {}
            found_concepts_by_role: dict[str, set[int]] = {}
            source_fact_ids: list[int] = []

            for _concept_name, concept_id, role, is_instant in duration_inputs:
                hit = by_period_id.get(concept_id, {}).get(period_id)
                if hit is not None:
                    value, fact_ids = hit
                    values_by_role.setdefault(role, []).append(value)
                    found_concepts_by_role.setdefault(role, set()).add(concept_id)
                    source_fact_ids.extend(fact_ids)

            for _concept_name, concept_id, role, is_instant in instant_inputs:
                # Matched by END DATE against the anchor period's end, not
                # period_id -- see module docstring.
                hit = by_end_date.get(concept_id, {}).get(end)
                if hit is not None:
                    value, fact_ids = hit
                    values_by_role.setdefault(role, []).append(value)
                    found_concepts_by_role.setdefault(role, set()).add(concept_id)
                    source_fact_ids.extend(fact_ids)

            # Drop any role where not every expected concept resolved --
            # a partial summand list must null the whole metric, never
            # silently compute from whichever subset happened to resolve.
            incomplete_role = None
            for role, expected in expected_concepts_by_role.items():
                if found_concepts_by_role.get(role, set()) != expected:
                    incomplete_role = role
                    values_by_role.pop(role, None)
                    break

            if incomplete_role is not None:
                value, null_reason = None, f"incomplete:{incomplete_role}"
            else:
                value, null_reason = _compute(shape, values_by_role)
            rows.append(
                {
                    "company_id": company_id,
                    "metric_definition_id": metric_id,
                    "period_start": start,
                    "period_end": end,
                    "period_label": fiscal_period,
                    "value": value,
                    "is_null_reason": null_reason,
                    "source_fact_ids": source_fact_ids or None,
                }
            )
            stats["computed" if value is not None else "null"] += 1

    target_ids = [t["id"] for t in targets]
    with conn.cursor() as cur:
        # Scoped to only the metric_definition_ids this stage owns AND
        # excluding period_label='TTM' -- an unscoped delete here (found
        # live 2026-08-16) wiped out Stage 3e's growth/TTM rows for the
        # company too, since metric_value is a shared table across stages.
        # Scoping by metric_definition_id alone still wasn't enough: roic
        # and roe share the same metric_definition_id between this stage's
        # FY rows and Stage 3e's TTM rows (compute_ttm_returns in ttm.py),
        # distinguished only by period_label. This stage never writes
        # period_label='TTM' (fiscal_period is always FY/Q1-4), so
        # excluding it here mirrors ttm.py's own TTM-scoped delete and
        # keeps the two stages' writes fully partitioned. See mapper-day-06
        # learnings.
        cur.execute(
            "delete from analytics.metric_value where company_id = %s and metric_definition_id = any(%s) and period_label != 'TTM'",
            (company_id, target_ids),
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
    logger.info("calculate.company_done", company_id=company_id, **stats)
    return stats


def calculate(conn: psycopg.Connection, ciks: set[str]) -> dict:
    targets = _load_target_metrics(conn)
    with conn.cursor() as cur:
        cur.execute("select cik, id from core.company where cik = any(%s)", (sorted(ciks),))
        company_id_by_cik = dict(cur.fetchall())

    totals = {"considered": 0, "ok": 0, "no_company": 0, "computed": 0, "null": 0}
    for cik in sorted(ciks):
        totals["considered"] += 1
        company_id = company_id_by_cik.get(cik)
        if company_id is None:
            totals["no_company"] += 1
            continue
        stats = calculate_for_company(conn, company_id, targets)
        totals["ok"] += 1
        totals["computed"] += stats["computed"]
        totals["null"] += stats["null"]

    logger.info("calculate.done", **totals)
    return totals
