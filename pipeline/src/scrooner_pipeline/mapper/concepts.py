"""Stage 3a -- Concept mapping (doc 11). Seeds analytics.canonical_concept
(the 17-concept list doc 11 resolved from doc 02's 18-metric formula table)
and analytics.concept_mapping (which core.concept tags count as each one,
priority-ordered or summed per canonical_concept.combination_mode).

Every entry below is curated against real golden-8 tag usage verified live
2026-08-16, not guessed -- including two real bugs caught before they
shipped:

1. `total_debt`'s LongTermDebt tag was found to equal
   LongTermDebtCurrent + LongTermDebtNoncurrent exactly, for 6 of 7
   companies that report all three -- summing all of them (the original
   plan) would have double-counted long-term debt. Fixed: LongTermDebt is
   mapped alone for the long-term component; the split tags are not
   mapped at all.
2. `revenue`'s InterestAndFeeIncomeLoansAndLeases (JPM) was found to be a
   subcomponent of Revenues (e.g. FY2024: $92.4B vs Revenues' $177.6B),
   not an alternative total -- mapping it as a fallback would understate
   JPM's revenue. Excluded entirely; JPM's revenue is null for the years
   (2013-2014, 2016-2020 in the golden set) where no reliable total-revenue
   tag exists at all, per doc 11's "null over guess" rule -- not a bug.

See doc/learnings/mapper-day-01-concepts.md for the full evidence behind
every mapping decision below.
"""

import psycopg
import structlog

logger = structlog.get_logger()

# (name, statement, combination_mode, description)
CANONICAL_CONCEPTS: list[tuple[str, str, str, str]] = [
    ("revenue", "income_statement", "first_match", "Total revenue / net sales"),
    ("gross_profit", "income_statement", "first_match", "Revenue minus cost of revenue"),
    ("operating_income", "income_statement", "first_match", "Income from operations before interest/tax"),
    ("net_income", "income_statement", "first_match", "Bottom-line net income/loss"),
    ("stockholders_equity", "balance_sheet", "first_match", "Total stockholders' equity"),
    ("cash_and_equivalents", "balance_sheet", "first_match", "Cash and cash equivalents"),
    ("total_debt", "balance_sheet", "sum", "Total interest-bearing debt, current + noncurrent"),
    ("current_assets", "balance_sheet", "first_match", "Total current assets"),
    ("current_liabilities", "balance_sheet", "first_match", "Total current liabilities"),
    ("interest_expense", "income_statement", "first_match", "Interest expense on debt"),
    ("income_tax_expense", "income_statement", "first_match", "Income tax expense/benefit"),
    ("income_before_tax", "income_statement", "first_match", "Pretax income from continuing operations"),
    ("cfo", "cash_flow", "first_match", "Net cash from operating activities"),
    ("capex", "cash_flow", "first_match", "Capital expenditures (PP&E purchases)"),
    ("diluted_eps", "income_statement", "first_match", "Diluted earnings per share"),
    ("shares_outstanding", "balance_sheet", "first_match", "Common shares outstanding"),
    ("dividends_per_share", "cash_flow", "first_match", "Dividends declared per common share"),
]

# (canonical_concept_name, taxonomy, tag, priority, confidence, notes)
CONCEPT_MAPPINGS: list[tuple[str, str, str, int, str, str]] = [
    # revenue -- alternatives, newest taxonomy first. Bank-specific tag kept
    # as a low-confidence last resort only; its known-partial subcomponent
    # (InterestAndFeeIncomeLoansAndLeases) is deliberately NOT mapped.
    ("revenue", "us-gaap", "RevenueFromContractWithCustomerExcludingAssessedTax", 1, "approved",
     "Post-ASC 606 standard tag, most current"),
    ("revenue", "us-gaap", "Revenues", 2, "approved", "Pre-ASC 606 / general-purpose tag, still widely used"),
    ("revenue", "us-gaap", "SalesRevenueNet", 3, "approved", "Legacy pre-2018 tag"),
    ("revenue", "us-gaap", "InterestAndDividendIncomeOperating", 4, "provisional",
     "Bank-specific partial proxy (JPM). Verified live 2026-08-16: does NOT equal Revenues for the same "
     "period in every year (FY2008: 73.0B vs Revenues 67.3B) -- likely a different sub-total, not total "
     "revenue. Last-resort fallback only; expect this to misstate JPM's revenue in years Revenues isn't "
     "separately reported."),

    # gross_profit -- only companies with a COGS-based P&L report this at
    # all; null for the rest is correct, not a coverage gap.
    ("gross_profit", "us-gaap", "GrossProfit", 1, "approved",
     "Only ~half of golden companies report this (financial/services companies have no COGS-based gross "
     "profit concept) -- null for those is correct."),

    ("operating_income", "us-gaap", "OperatingIncomeLoss", 1, "approved", "No drift observed"),

    ("net_income", "us-gaap", "NetIncomeLoss", 1, "approved", None),
    ("net_income", "us-gaap", "ProfitLoss", 2, "approved", "Alternative label used by 2 golden companies"),

    ("stockholders_equity", "us-gaap", "StockholdersEquity", 1, "approved", None),
    ("stockholders_equity", "us-gaap", "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
     2, "approved", "Includes noncontrolling interests -- fallback only, prefer the exclusive figure"),

    ("cash_and_equivalents", "us-gaap", "CashAndCashEquivalentsAtCarryingValue", 1, "approved", None),
    ("cash_and_equivalents", "us-gaap", "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents", 2,
     "approved", "Verified live 2026-08-16: identical to the primary tag for AAPL in every period checked "
     "(negligible restricted cash) -- safe fallback"),

    # total_debt -- SUM mode. LongTermDebt used ALONE for the long-term
    # component (confirmed to equal, never coexist additively with, the
    # split current/noncurrent tags -- see module docstring). The split
    # tags are deliberately absent from this list.
    ("total_debt", "us-gaap", "LongTermDebt", 1, "approved",
     "Verified live 2026-08-16: equals LongTermDebtCurrent+LongTermDebtNoncurrent exactly whenever both "
     "are reported, and is present for every period the split tags are (plus more). Use alone -- summing "
     "alongside the split tags double-counts long-term debt."),
    ("total_debt", "us-gaap", "ShortTermBorrowings", 1, "approved", "Distinct short-term/commercial-paper borrowings, genuinely additive"),
    ("total_debt", "us-gaap", "DebtCurrent", 1, "provisional",
     "Only 1 company (GOOGL) in the golden set -- not yet cross-checked against LongTermDebtCurrent for "
     "overlap the way LongTermDebt was. Flag for review before wider use."),
    ("total_debt", "us-gaap", "SecuredDebtCurrent", 1, "provisional",
     "Only 1 company (Block). Verified live 2026-08-16: consistently a small fraction of LongTermDebt "
     "($120M-$572M against $5-7B) across every period checked -- consistent with a genuinely separate, "
     "additive 'secured debt, current portion' category. No overlap evidence found."),
    ("total_debt", "us-gaap", "OtherLongTermDebtNoncurrent", 1, "rejected",
     "Only 1 company (Block). Verified live 2026-08-16 and REJECTED: tracks 70-100% of LongTermDebt's own "
     "value across periods (exactly equal in the most recent quarter) -- far too large a fraction to be a "
     "separate 'other' category (contrast SecuredDebtCurrent above, a genuinely small fraction). Much more "
     "consistent with the same debt facility being tagged differently across filing vintages than with "
     "additive debt. Summing it alongside LongTermDebt would materially overstate Block's total debt."),

    ("current_assets", "us-gaap", "AssetsCurrent", 1, "approved", None),
    ("current_liabilities", "us-gaap", "LiabilitiesCurrent", 1, "approved", None),

    # interest_expense -- InterestIncomeExpenseNet deliberately excluded:
    # confirmed a NET figure (income minus expense), not pure expense.
    ("interest_expense", "us-gaap", "InterestExpense", 1, "approved", None),
    ("interest_expense", "us-gaap", "InterestExpenseDebt", 2, "approved", "Alternative label, same semantics"),

    ("income_tax_expense", "us-gaap", "IncomeTaxExpenseBenefit", 1, "approved", None),

    ("income_before_tax", "us-gaap",
     "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest", 1, "approved", None),
    ("income_before_tax", "us-gaap",
     "IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments",
     2, "approved", "Alternative label, same semantics, used by different companies/years"),

    ("cfo", "us-gaap", "NetCashProvidedByUsedInOperatingActivities", 1, "approved", None),
    ("cfo", "us-gaap", "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations", 2, "approved", None),

    ("capex", "us-gaap", "PaymentsToAcquirePropertyPlantAndEquipment", 1, "approved", None),

    ("diluted_eps", "us-gaap", "EarningsPerShareDiluted", 1, "approved", "Used consistently by all 8 companies -- no drift observed"),

    ("shares_outstanding", "us-gaap", "CommonStockSharesOutstanding", 1, "approved", None),
    ("shares_outstanding", "dei", "EntityCommonStockSharesOutstanding", 2, "approved", "Cover-page DEI tag, alternative source"),

    ("dividends_per_share", "us-gaap", "CommonStockDividendsPerShareDeclared", 1, "approved", None),
    ("dividends_per_share", "us-gaap", "CommonStockDividendsPerShareCashPaid", 2, "approved",
     "Cash-paid basis rather than declared -- fallback only, prefer declared"),
]


def seed_canonical_concepts(conn: psycopg.Connection) -> dict[str, int]:
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
            CANONICAL_CONCEPTS,
        )
        conn.commit()
        cur.execute("select name, id from analytics.canonical_concept")
        return dict(cur.fetchall())


def seed_concept_mappings(conn: psycopg.Connection, canonical_id_by_name: dict[str, int]) -> dict:
    stats = {"considered": len(CONCEPT_MAPPINGS), "mapped": 0, "unresolved_tag": 0}
    with conn.cursor() as cur:
        for canonical_name, taxonomy, tag, priority, confidence, notes in CONCEPT_MAPPINGS:
            cur.execute("select id from core.concept where taxonomy = %s and tag = %s", (taxonomy, tag))
            row = cur.fetchone()
            if row is None:
                stats["unresolved_tag"] += 1
                logger.warning("concepts.tag_not_in_core", taxonomy=taxonomy, tag=tag, canonical=canonical_name)
                continue
            concept_id = row[0]
            canonical_id = canonical_id_by_name[canonical_name]
            cur.execute(
                """
                insert into analytics.concept_mapping (canonical_concept_id, concept_id, priority, confidence, notes)
                values (%s, %s, %s, %s, %s)
                on conflict (canonical_concept_id, concept_id) do update
                    set priority = excluded.priority,
                        confidence = excluded.confidence,
                        notes = excluded.notes
                """,
                (canonical_id, concept_id, priority, confidence, notes),
            )
            stats["mapped"] += 1
    conn.commit()
    logger.info("concepts.mappings_seeded", **stats)
    return stats


def seed(conn: psycopg.Connection) -> dict:
    canonical_id_by_name = seed_canonical_concepts(conn)
    mapping_stats = seed_concept_mappings(conn, canonical_id_by_name)
    return {"canonical_concepts": len(canonical_id_by_name), **mapping_stats}


def coverage_report(conn: psycopg.Connection, ciks: set[str]) -> list[dict]:
    """For every (company, canonical_concept), does at least one approved/
    provisional mapped tag have authoritative fact data? Stage 3a's actual
    'done when' gate -- one row per company/concept, resolved=false is
    where curation still needs to happen."""
    with conn.cursor() as cur:
        cur.execute(
            """
            select c.cik, cc.name,
                   bool_or(f.id is not null) as resolved,
                   count(distinct f.id) as fact_count
            from core.company c
            cross join analytics.canonical_concept cc
            left join analytics.concept_mapping cm
                on cm.canonical_concept_id = cc.id and cm.confidence != 'rejected'
            left join core.fact f
                on f.concept_id = cm.concept_id and f.company_id = c.id and f.is_authoritative
            where c.cik = any(%s)
            group by c.cik, cc.name
            order by c.cik, cc.name
            """,
            (sorted(ciks),),
        )
        cols = [d.name for d in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]
