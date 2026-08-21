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
