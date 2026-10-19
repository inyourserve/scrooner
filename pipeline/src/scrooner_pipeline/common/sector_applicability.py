"""Bank applicability: which displayed values are suppressed for a bank, and why.

Decision (Dhairya, delegated by the founder, 2026-10-19), grounded in
data-team/32-VERIFIER-BANK-VALUES-2026-10-19.md (59 wrong values found in 30
banks, filing-checked): for banks and thrifts, STOP SHOWING the metrics below
and show a stated reason instead of a value. Keep ROE, ROA, EPS, book value,
P/B, P/E and the dividend family.

Design (the least invasive mechanism that exists):
  * No schema change, no recompute, no database write. `analytics.metric_value`
    is left exactly as the Mapper wrote it (the stored value stays available to
    the data team and the verifier).
  * The suppression is applied where values are SERVED, at the three choke
    points that read `metric_value`: the Screener's most-recent-value resolver
    (`screener/resolve.py`, which also feeds the screening snapshot), the
    company page (`apps/backend/company_page.py`) and the watchlist endpoint.
    All three import this one module, so the page, screener and API cannot
    drift apart.
  * The "bank" population is defined here once (`BANK_POPULATION_SQL`): SIC
    6020-6036 AND the company's own filed tags show a bank's income statement
    and balance sheet shape (NoninterestExpense and a deposit liability). SIC
    alone is a hypothesis (role spec: never classify by a sector label alone).
    Evidence label: the tag test is DATA-INFERRED (company_sec_tag holds
    authoritative facts only); a rendered-statement check per company would be
    FILING-CHECKED and is not done here.

Reasons are stored in the same field the UI already renders for any null
(`is_null_reason`), in plain words, because the page shows the text after
replacing underscores with spaces.

Nothing here approves accounting. The perimeter of "bank revenue" and the
mapping of net interest income are pending (see the two PENDING reasons), and
the list of suppressed metrics is the delegated product decision, not an
accounting verdict.
"""

from __future__ import annotations

from collections.abc import Iterable

NOT_APPLICABLE_TO_BANKS = "not applicable to banks"
BANK_REVENUE_PENDING = "bank revenue definition pending"
BANK_NII_PENDING = "bank net interest income mapping pending"

# SIC 6020-6036: commercial banks, savings institutions, credit-union-like
# depositories in the SEC's classification. Four-digit text in core.company.
BANK_SIC_MIN = "6020"
BANK_SIC_MAX = "6036"

# A bank's own filed tags. A company in the SIC range that does not file
# NoninterestExpense and a deposit liability is NOT treated as a bank here
# (it keeps its values), and shows up in the "SIC but no evidence" count.
BANK_EVIDENCE_EXPENSE_TAG = "NoninterestExpense"
BANK_EVIDENCE_DEPOSIT_TAGS = (
    "Deposits",
    "InterestBearingDepositLiabilities",
    "NoninterestBearingDepositLiabilities",
    "InterestBearingDepositLiabilitiesDomestic",
)


def is_bank_sic(sic_code: str | None) -> bool:
    """The SIC half of the population test, for callers that already hold the
    SIC and want to skip a database round trip when it cannot be a bank."""
    return (
        sic_code is not None
        and len(sic_code) == 4
        and BANK_SIC_MIN <= sic_code <= BANK_SIC_MAX
    )


def bank_predicate_sql(alias: str = "c") -> str:
    """A boolean SQL expression, true when the row of `core.company` aliased
    `alias` is a bank by the population definition above. Contains no
    parameters, so it can be embedded in any query as a literal fragment."""
    deposit_tags = ", ".join(f"'{tag}'" for tag in BANK_EVIDENCE_DEPOSIT_TAGS)
    return f"""(
        length({alias}.sic_code) = 4
        and {alias}.sic_code between '{BANK_SIC_MIN}' and '{BANK_SIC_MAX}'
        and exists (
            select 1 from analytics.company_sec_tag bt
            join core.concept bk on bk.id = bt.concept_id
            where bt.company_id = {alias}.id
              and bk.taxonomy = 'us-gaap' and bk.tag = '{BANK_EVIDENCE_EXPENSE_TAG}'
        )
        and exists (
            select 1 from analytics.company_sec_tag bt
            join core.concept bk on bk.id = bt.concept_id
            where bt.company_id = {alias}.id
              and bk.taxonomy = 'us-gaap' and bk.tag in ({deposit_tags})
        )
    )"""


# The population as a standalone query (same shape as coverage_matrix.
# POPULATION_QUERIES entries), for the coverage layer to adopt later.
BANK_POPULATION_SQL = f"""
    select c.id from core.company c
    where c.status = 'active' and {bank_predicate_sql("c")}
"""


def _metrics(reason: str, names: Iterable[str]) -> dict[str, str]:
    return {name: reason for name in names}


# metric_name -> reason, exactly the delegated suppress list.
BANK_SUPPRESSED_METRICS: dict[str, str] = {
    # Banks present no gross profit, no operating-income line, no classified
    # balance sheet, and fund themselves with deposits (data-team/32 section 5).
    **_metrics(
        NOT_APPLICABLE_TO_BANKS,
        (
            "gross_margin",
            "operating_margin",
            "roic",
            "interest_coverage_ratio",
            # EBITDA family
            "ebitda",
            "ebitda_margin",
            "ev_ebitda",
            "debt_to_ebitda",
            "net_debt_ebitda",
            # free cash flow family (name starts with fcf)
            "fcf",
            "fcf_yield",
            "fcf_margin",
            "fcf_per_share",
            "fcf_growth_yoy",
            "fcf_growth_3y_cagr",
            "fcf_growth_5y_cagr",
            "fcf_gt_net_income",
            # deposits are the dominant liability; borrowings-only metrics mislead
            "net_cash",
            "net_cash_per_share",
            "debt_to_equity",
            "zero_debt",
            "ev_sales",
            # unclassified balance sheet, no inventory / receivables / payables
            "current_ratio",
            "quick_ratio",
            "working_capital",
            "inventory_days",
            "payables_days",
            "debtor_days",
            "cash_conversion_cycle",
            "piotroski_f_score",
        ),
    ),
    # Revenue perimeter has 6 meanings across 30 banks today (data-team/32 s3).
    **_metrics(
        BANK_REVENUE_PENDING,
        (
            "price_to_sales",
            "net_margin",
            "pretax_margin",
            "revenue_growth_yoy",
            "revenue_growth_3y_cagr",
            "revenue_growth_5y_cagr",
            "revenue_growth_10y_cagr",
        ),
    ),
    # The current formula uses InvestmentIncomeInterest (three different
    # meanings across banks) until InterestIncomeExpenseNet is mapped.
    "net_interest_income": BANK_NII_PENDING,
}

# Statement-table row labels (analytics.statement_line.display_label, plus the
# two metric-backed rows company_page adds) -> reason.
BANK_SUPPRESSED_STATEMENT_LINES: dict[str, str] = {
    "Revenue": BANK_REVENUE_PENDING,
    "Operating Income": NOT_APPLICABLE_TO_BANKS,
    "EBITDA": NOT_APPLICABLE_TO_BANKS,
    "Free Cash Flow": NOT_APPLICABLE_TO_BANKS,
}

# Not suppressed, but a human should decide (see the task report): derived from
# a suppressed quantity, or a related balance-sheet row the delegated list does
# not name. Kept as data so the decision is one edit, never applied implicitly.
PENDING_HUMAN_DECISION: dict[str, str] = {
    "dividends_pct_fcf": "uses fcf in the denominator",
    "share_repurchases_pct_fcf": "uses fcf in the denominator",
    "sbc_pct_revenue": "uses the undefined bank revenue",
    "capex_pct_revenue": "uses the undefined bank revenue",
    "sga_pct_revenue": "uses the undefined bank revenue",
    "rnd_intensity": "uses the undefined bank revenue",
    "ocf_to_net_income": "uses bank cash from operations",
    "Total Debt (statement row)": "wrong at 7 of 30 banks (data-team/32 2a #9-15)",
    "Current Assets / Current Liabilities (statement rows)": "no such line on a bank balance sheet",
}


def metric_suppression_reason(metric_name: str, is_bank: bool) -> str | None:
    """The reason to show instead of a value, or None (not suppressed). A
    non-bank is never suppressed, whatever the metric."""
    if not is_bank:
        return None
    return BANK_SUPPRESSED_METRICS.get(metric_name)


def statement_line_suppression_reason(label: str, is_bank: bool) -> str | None:
    if not is_bank:
        return None
    return BANK_SUPPRESSED_STATEMENT_LINES.get(label)


def load_bank_company_ids(cur, company_ids: list[int] | None = None) -> set[int]:
    """Ids of the companies in the bank population. `cur` is an open psycopg
    cursor. With `company_ids`, only those are tested (index-backed, cheap);
    with None, the whole population (one set-based query). Read-only."""
    if company_ids is not None and not company_ids:
        return set()
    where = "c.id = any(%s::bigint[]) and " if company_ids is not None else ""
    params = (company_ids,) if company_ids is not None else None
    cur.execute(
        f"select c.id from core.company c where {where}{bank_predicate_sql('c')}",
        params,
    )
    return {row[0] for row in cur.fetchall()}


def apply_to_resolved(
    resolved: dict[tuple[int, int], dict],
    bank_company_ids: set[int],
    suppressed_metric_ids: dict[int, str],
) -> int:
    """In place: for every (company, metric) in `resolved` where the company is
    a bank and the metric is suppressed, null the value and set the reason.
    `suppressed_metric_ids` maps metric_definition_id -> reason. Returns how
    many entries were changed (a value or a different reason replaced).

    A bank with no resolved row for a metric is left alone (there is no value
    to hide); the Screener explains the exclusion separately."""
    changed = 0
    for company_id in bank_company_ids:
        for metric_id, reason in suppressed_metric_ids.items():
            entry = resolved.get((company_id, metric_id))
            if entry is None:
                continue
            if entry["value"] is not None or entry["is_null_reason"] != reason:
                entry["value"] = None
                entry["is_null_reason"] = reason
                changed += 1
    return changed
