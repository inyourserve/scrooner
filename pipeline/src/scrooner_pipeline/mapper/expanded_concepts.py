"""Expanded-metric canonical concepts (doc 18 Tier A / doc 26, built
2026-08-18 to raise data-point coverage). Same additive pattern as
statements/classify.py: Mapper's own frozen mapper/concepts.py and
mapper/resolve.py are NOT modified -- new, separate code writing to the
same shared tables, reusing resolve()'s unchanged resolution logic.

depreciation_and_amortization is `first_match`, deliberately NOT `sum`
-- checked live before writing this: AAPL FY2015 reports BOTH
DepreciationAndAmortization and DepreciationDepletionAndAmortization
for the exact same period. Summing them would silently double-count
D&A for that one period; `first_match` (priority order) picks exactly
one, the same discipline already proven for cost_of_revenue's own two
alternates (doc 17).

inventory and sbc (ShareBasedCompensation) are both single-tag,
first_match by convention (room for a real alternate if one turns up,
same as every other concept here) -- not checked for overlap since only
one tag was found for either across the golden-10's concept list.

accounts_receivable/accounts_payable added 2026-08-18 (doc 26's coverage
push, feeding Debtor/Payables Days + Cash Conversion Cycle) -- checked
live first: AccountsReceivableNetCurrent (305 facts/6 companies) and
AccountsPayableCurrent (293 facts/6 companies) are both real, raw,
single-tag, unmapped instant balances across the golden-10.

goodwill and basic_eps added 2026-08-21, acting on
doc/learnings/core-fact-utilization-study.md's #1 and #4 ranked
recommendations. Both single-tag, first_match by convention, no overlap
risk checked (only one tag found for either across the golden-10).

cf_ar_change/cf_inventory_change/cf_ap_change added 2026-08-21, acting on
the study's #2 recommendation -- these are CASH-FLOW-STATEMENT period
CHANGES (IncreaseDecreaseInAccountsReceivable etc.), a genuinely
different concept from the balance-sheet instant snapshots
(accounts_receivable/inventory/accounts_payable) already mapped above.
statement='cash_flow' (duration), not 'balance_sheet'. Feed
mapper/reconciliation.py's cross-check metrics, not calculate.py's
generic engine directly.

total_debt's alternate set was NOT widened, reversing the study's #3
recommendation -- checked live before implementing (not assumed safe
just because the study called it "cheap, already-proven"): company_id=2
has multiple real periods where BOTH LongTermDebt (currently mapped,
priority 1) and LongTermDebtNoncurrent (the proposed alternate) are
tagged SIMULTANEOUS for the SAME period (e.g. $3,478,000,000 vs
$3,472,000,000) -- summing both under total_debt's existing `sum` mode
would nearly double-count debt for any company reporting both
conventions in the same period. mapper/concepts.py's own original
LongTermDebt mapping note already warned of exactly this risk for a
different pair of tags; this confirms the same trap applies here too.
No safe drop-in fix exists at the concept_mapping level -- widening
`sum`-mode alternates is only safe when tags are mutually exclusive
per (company, period), which was checked and failed here. Left as a
named, deferred gap, not implemented unsafely.

research_and_development and interest_income added 2026-08-21, acting on
doc/scoping/28_Scrooner_Trendlyne_Data_Point_Gap_Analysis.md (items #1/#4
-- a real Trendlyne stock page named both as data points this project
doesn't have yet). Checked live before adding: `us-gaap:
ResearchAndDevelopmentExpense` resolves for 5 companies/427 facts;
`us-gaap:InvestmentIncomeInterest` resolves for 7 companies/372 facts
(a cleaner match than two other interest-income tag variants checked,
which covered only 1-2 companies each). Both single-tag, first_match by
convention, no overlap risk checked (only one tag used for either).

employee_count added 2026-08-29, acting on doc/execution-plans/
30_Data_Moat_Full_Population_Strengthening_Plan.md Track 6 #1 (a real
Finviz AAPL page comparison): dei:EntityNumberOfEmployees is a real,
unmapped, already-fetched cover-page tag -- checked live before adding
(not just trusted the doc's earlier count, which predates the
full-population expansion): 1,941 real fact rows across 178 companies
as of 2026-08-29, values sanity-checked plausible (Leidos 50,000,
Cleveland-Cliffs 25,000). statement='balance_sheet' by the same
practical-bucket convention public_float already uses -- neither is
really a balance-sheet line item, but canonical_concept.statement only
has 3 values and this project doesn't yet have a 4th bucket for dei
cover-page facts. A small real data-quality note, not acted on: ~2.5%
of raw fact rows (48/1,941) are tagged with a non-employee-count unit
(usd, shares) -- almost certainly genuine filer tagging errors in a
small number of real filings, not a bug in this mapping. Left
unfiltered, matching this project's existing precedent (no other
single-tag concept unit-filters either) -- the Normalizer's own
dedupe/is_authoritative logic is the layer that already handles a
conflicting value for the same company/period, not the Mapper's
concept_mapping layer.
"""

import psycopg
import structlog

logger = structlog.get_logger()

NEW_CANONICAL_CONCEPTS: list[tuple[str, str, str, str]] = [
    ("inventory", "balance_sheet", "first_match", "Inventory, net -- needed for Quick Ratio"),
    ("sbc", "income_statement", "first_match", "Stock-based compensation expense"),
    (
        "depreciation_and_amortization",
        "income_statement",
        "first_match",
        "D&A -- confirmed live (AAPL FY2015) that a company can report this under two "
        "different tags for the same period; first_match (not sum) avoids double-counting. "
        "Feeds ebitda.",
    ),
    ("accounts_receivable", "balance_sheet", "first_match", "Accounts receivable, net -- needed for Debtor Days"),
    ("accounts_payable", "balance_sheet", "first_match", "Accounts payable -- needed for Payables Days"),
    ("goodwill", "balance_sheet", "first_match", "Balance-sheet goodwill -- closes doc 26's named Goodwill/Intangibles gap"),
    ("basic_eps", "income_statement", "first_match", "Basic EPS -- standalone from diluted EPS, feeds eps_dilution_spread"),
    ("cf_ar_change", "cash_flow", "first_match",
     "Cash-flow-statement period change in accounts receivable (indirect-method CFO adjustment) -- "
     "a different concept from the balance-sheet instant accounts_receivable above. Feeds the AR "
     "reconciliation-gap cross-check in mapper/reconciliation.py."),
    ("cf_inventory_change", "cash_flow", "first_match",
     "Cash-flow-statement period change in inventory. Feeds mapper/reconciliation.py."),
    ("cf_ap_change", "cash_flow", "first_match",
     "Cash-flow-statement period change in accounts payable. Feeds mapper/reconciliation.py."),
    ("research_and_development", "income_statement", "first_match", "R&D expense -- feeds rnd_intensity"),
    ("interest_income", "income_statement", "first_match", "Interest income -- feeds net_interest_income, "
     "separate from interest_expense (feeds interest_coverage_ratio already)"),
    ("sga_expense", "income_statement", "first_match",
     "SG&A expense -- checked live before choosing the tag: SellingGeneralAndAdministrativeExpense "
     "(60 companies) is far more common than the standalone GeneralAndAdministrativeExpense (31 "
     "companies) across the 174-company pool. first_match (not sum) -- unlike a composite concept, "
     "overlap between these two tags for the same company/period isn't a double-counting risk here "
     "regardless, since first_match only ever takes one value; priority 1/2 just decides which alternate "
     "wins if both happen to resolve."),
    ("comprehensive_income", "income_statement", "first_match",
     "Comprehensive income (net income + other comprehensive income/loss) -- a real, distinct P&L-adjacent "
     "figure, not previously captured. 92 companies/13,574 facts across the 174-pool."),
    ("amortization_of_intangibles", "income_statement", "first_match",
     "Amortization of intangible assets -- a D&A sub-component, distinct from the already-mapped "
     "combined depreciation_and_amortization concept. 78 companies/7,077 facts."),
    ("effective_tax_rate_reported", "income_statement", "first_match",
     "The company's own reported effective tax rate (EffectiveIncomeTaxRateContinuingOperations), a "
     "'pure' decimal-fraction ratio (e.g. 0.156 = 15.6%), same scale as the internally-derived "
     "income_tax_expense/income_before_tax rate ROIC already computes -- feeds "
     "effective_tax_rate_gap as a cross-check, not a replacement. 93 companies/7,113 facts."),
    ("employee_count", "balance_sheet", "first_match",
     "dei:EntityNumberOfEmployees, a cover-page fact -- 178 companies/1,941 facts as of 2026-08-29. "
     "statement bucket follows public_float's own precedent (neither is really a balance-sheet line item)."),
    ("bdc_total_investment_income", "income_statement", "first_match",
     "A Business Development Company / closed-end fund's real top-line figure -- checked live "
     "2026-09-04: 44 real active companies (Ares Capital, Main Street Capital, Prospect Capital, "
     "Goldman Sachs BDC, etc.) surfaced entirely without a `sic_description` (a real classification "
     "gap this project's own data inherited from SEC, not fixed here) and with zero `revenue` "
     "coverage -- because a BDC's income statement genuinely has no revenue line at all, it starts "
     "from 'Total investment income' (interest/dividend/fee income from its portfolio). Deliberately "
     "a SEPARATE concept, never added as a `revenue` fallback tag -- doc 42 Part 4's own reasoning "
     "for banks/insurers/REITs applies identically here: blending a lending business's investment "
     "income into `revenue` would silently corrupt gross_margin/revenue_growth and every other ratio "
     "that assumes a product company's cost structure. 118 real companies use this tag "
     "population-wide (broader than the original 44-BDC sample -- other closed-end funds too), "
     "verified via real values (ARCC $768.0M for the quarter ended 2026-06-30, matching its own "
     "rendered 'Total investment income' statement line exactly). No downstream metric_definition "
     "wired to this concept yet -- this pass only closes the raw-data gap (traceable, screenable via "
     "a future dedicated metric), same 'data layer first' sequencing as segment_revenue.py."),
]

NEW_CONCEPT_MAPPINGS: list[tuple[str, str, str, int, str, str]] = [
    ("inventory", "us-gaap", "InventoryNet", 1, "approved", ""),
    ("sbc", "us-gaap", "ShareBasedCompensation", 1, "approved", ""),
    ("depreciation_and_amortization", "us-gaap", "DepreciationAndAmortization", 1, "approved",
     "Priority 1 -- confirmed live this is the tag AAPL's FY2015 filing itself treats as authoritative when both appear."),
    ("depreciation_and_amortization", "us-gaap", "DepreciationDepletionAndAmortization", 2, "approved",
     "Alternate, not summand -- see module docstring's AAPL FY2015 overlap finding."),
    ("accounts_receivable", "us-gaap", "AccountsReceivableNetCurrent", 1, "approved", ""),
    ("accounts_payable", "us-gaap", "AccountsPayableCurrent", 1, "approved", ""),
    ("goodwill", "us-gaap", "Goodwill", 1, "approved", ""),
    ("basic_eps", "us-gaap", "EarningsPerShareBasic", 1, "approved", ""),
    ("cf_ar_change", "us-gaap", "IncreaseDecreaseInAccountsReceivable", 1, "approved", ""),
    ("cf_inventory_change", "us-gaap", "IncreaseDecreaseInInventories", 1, "approved", ""),
    ("cf_ap_change", "us-gaap", "IncreaseDecreaseInAccountsPayable", 1, "approved", ""),
    ("research_and_development", "us-gaap", "ResearchAndDevelopmentExpense", 1, "approved", ""),
    ("interest_income", "us-gaap", "InvestmentIncomeInterest", 1, "approved", ""),
    ("sga_expense", "us-gaap", "SellingGeneralAndAdministrativeExpense", 1, "approved",
     "Priority 1 -- more common than the standalone G&A tag across the 174-pool (60 vs 31 companies)."),
    ("sga_expense", "us-gaap", "GeneralAndAdministrativeExpense", 2, "approved",
     "Alternate for companies that report G&A alone rather than a combined SG&A line."),
    ("comprehensive_income", "us-gaap", "ComprehensiveIncomeNetOfTax", 1, "approved", ""),
    ("amortization_of_intangibles", "us-gaap", "AmortizationOfIntangibleAssets", 1, "approved", ""),
    ("effective_tax_rate_reported", "us-gaap", "EffectiveIncomeTaxRateContinuingOperations", 1, "approved", ""),
    ("employee_count", "dei", "EntityNumberOfEmployees", 1, "approved", ""),
    ("bdc_total_investment_income", "us-gaap", "GrossInvestmentIncomeOperating", 1, "approved",
     "Verified 2026-09-04 against 118 real active companies (35 of the original 44 hand-sampled "
     "BDCs, plus other closed-end funds) -- values sanity-checked plausible and correctly scaled "
     "(ARCC's own rendered statement line 'Total investment income' = $768.0M, exact match). "
     "9 of the original 44 BDCs use no gross tag at all, only NetInvestmentIncome (post-expense) "
     "or per-share/ratio variants -- deliberately NOT added as a fallback here, since substituting "
     "a net figure for a gross concept would be silently wrong, not just incomplete."),
]


def seed_new_canonical_concepts(conn: psycopg.Connection) -> dict[str, int]:
    with conn.cursor() as cur:
        cur.executemany(
            """
            insert into analytics.canonical_concept (name, statement, combination_mode, description)
            values (%s, %s, %s, %s)
            on conflict (name) do update
                set statement = excluded.statement,
                    combination_mode = excluded.combination_mode,
                    description = excluded.description
            """,
            NEW_CANONICAL_CONCEPTS,
        )
        conn.commit()
        cur.execute("select name, id from analytics.canonical_concept")
        return dict(cur.fetchall())


def seed_new_concept_mappings(conn: psycopg.Connection, canonical_id_by_name: dict[str, int]) -> dict:
    stats = {"considered": len(NEW_CONCEPT_MAPPINGS), "mapped": 0, "unresolved_tag": 0}
    with conn.cursor() as cur:
        for canonical_name, taxonomy, tag, priority, confidence, notes in NEW_CONCEPT_MAPPINGS:
            cur.execute("select id from core.concept where taxonomy = %s and tag = %s", (taxonomy, tag))
            row = cur.fetchone()
            if row is None:
                stats["unresolved_tag"] += 1
                logger.warning("expanded_concepts.tag_not_in_core", taxonomy=taxonomy, tag=tag, canonical=canonical_name)
                continue
            concept_id = row[0]
            canonical_id = canonical_id_by_name[canonical_name]
            cur.execute(
                """
                insert into analytics.concept_mapping (canonical_concept_id, concept_id, priority, confidence, notes)
                values (%s, %s, %s, %s, %s)
                on conflict (canonical_concept_id, concept_id) do update
                    set priority = excluded.priority, confidence = excluded.confidence, notes = excluded.notes
                """,
                (canonical_id, concept_id, priority, confidence, notes),
            )
            stats["mapped"] += 1
    conn.commit()
    logger.info("expanded_concepts.mappings_seeded", **stats)
    return stats


def seed(conn: psycopg.Connection) -> dict:
    canonical_id_by_name = seed_new_canonical_concepts(conn)
    mapping_stats = seed_new_concept_mappings(conn, canonical_id_by_name)
    return {"new_canonical_concepts": len(NEW_CANONICAL_CONCEPTS), **mapping_stats}
