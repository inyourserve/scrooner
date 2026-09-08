"""The "tag db" for yfinance's own statement row labels (2026-09-08,
explicit user request: "same tag mapping stuff") -- mirrors
analytics.concept_mapping's approved/provisional/rejected discipline, just
for yfinance's row labels instead of XBRL tags. Every mapping below was
checked against a REAL fetched value for at least one company before
being added (AAPL for the majority; JPM specifically to check what
survives for a bank) -- never added from the row label's name alone.

Real, generalizable finding baked into this mapping, not glossed over:
banks (and by extension insurers/REITs/other financials) have NO Gross
Profit / Cost Of Revenue / Operating Income / Operating Expense rows at
all in yfinance's own income statement -- confirmed live against JPM.
Their "Total Revenue" is a yfinance-COMPUTED aggregate (net interest
income + non-interest/fee income), which does NOT match our own
bank-specific revenue tag (InterestAndDividendIncomeOperating, gross
interest income alone) -- this generalizes the Commerce Bancshares
critical finding (2026-09-08) to the entire banking sector, not just one
company. `notes` on the income-statement 'revenue'/'interest_expense'
rows flags this explicitly rather than silently mapping and producing a
flood of expected-but-misleading findings for every bank in the batch.

CONCEPT_FOR_COMPARISON: where a *_resolved concept exists (the safe-
widening layer from concept_fallback.py/tag_investigator.py), compare
against THAT, not the raw concept -- it's what the company page actually
displays, so a finding here reflects what a real user would see wrong,
not an intermediate value nobody reads.

SIGN_FLIP_LINE_ITEMS: yfinance reports Capital Expenditure/Cash Dividends
Paid/Repurchase Of Capital Stock as NEGATIVE (a cash outflow) -- verified
live against a real AAPL value (-2,455,000,000 for Capital Expenditure)
-- while our own capex/dividends_paid/share_buybacks concepts are stored
as positive spend amounts (also verified live). Compared as
`our_value == -yfinance_value` for these three, not a naive direct diff."""

import psycopg
import structlog

logger = structlog.get_logger()

# (statement_type, yfinance line_item) -> canonical_concept_name
LINE_ITEM_MAP: dict[tuple[str, str], str] = {
    ("income_statement", "Total Revenue"): "revenue",
    ("income_statement", "Cost Of Revenue"): "cost_of_revenue",
    ("income_statement", "Gross Profit"): "gross_profit",
    ("income_statement", "Operating Expense"): "operating_expenses",
    ("income_statement", "Operating Income"): "operating_income",
    ("income_statement", "Pretax Income"): "income_before_tax",
    ("income_statement", "Tax Provision"): "income_tax_expense",
    ("income_statement", "Net Income"): "net_income",
    ("income_statement", "Diluted EPS"): "diluted_eps",
    ("income_statement", "Research And Development"): "research_and_development",
    ("balance_sheet", "Total Assets"): "total_assets",
    ("balance_sheet", "Current Assets"): "current_assets",
    ("balance_sheet", "Current Liabilities"): "current_liabilities",
    ("balance_sheet", "Total Debt"): "total_debt",
    ("balance_sheet", "Stockholders Equity"): "stockholders_equity",
    ("balance_sheet", "Cash And Cash Equivalents"): "cash_and_equivalents",
    ("balance_sheet", "Total Liabilities Net Minority Interest"): "total_liabilities",
    ("balance_sheet", "Accounts Receivable"): "accounts_receivable",
    ("balance_sheet", "Accounts Payable"): "accounts_payable",
    ("balance_sheet", "Inventory"): "inventory",
    ("balance_sheet", "Net PPE"): "ppe_net",
    ("cash_flow", "Operating Cash Flow"): "cfo",
    ("cash_flow", "Capital Expenditure"): "capex",
    ("cash_flow", "Investing Cash Flow"): "cash_flow_investing",
    ("cash_flow", "Financing Cash Flow"): "cash_flow_financing",
    ("cash_flow", "Cash Dividends Paid"): "dividends_paid",
    ("cash_flow", "Repurchase Of Capital Stock"): "share_buybacks",
    ("cash_flow", "Stock Based Compensation"): "sbc",
    ("cash_flow", "Depreciation And Amortization"): "depreciation_and_amortization",
}

SIGN_FLIP_LINE_ITEMS: frozenset[tuple[str, str]] = frozenset(
    {
        ("cash_flow", "Capital Expenditure"),
        ("cash_flow", "Cash Dividends Paid"),
        ("cash_flow", "Repurchase Of Capital Stock"),
    }
)

# Prefer the *_resolved concept where one exists (concept_fallback.py) --
# what the company page actually shows, not an intermediate raw value.
CONCEPT_FOR_COMPARISON: dict[str, str] = {
    "revenue": "revenue_sanity_resolved",
    "cost_of_revenue": "cost_of_revenue_resolved",
    "gross_profit": "gross_profit_resolved",
    "operating_expenses": "operating_expenses_resolved",
    "total_debt": "total_debt_resolved",
}

# Real, sector-wide finding (checked live against JPM, not guessed): banks
# report no Gross Profit/Cost Of Revenue/Operating Income/Operating
# Expense at all, and their "Total Revenue" is a yfinance-computed
# aggregate that structurally disagrees with our own bank-specific revenue
# tag. Concepts in this set get a note attached to every finding rather
# than silently flooding the report with an already-understood mismatch
# class -- narrowed to SIC codes starting with these prefixes (National/
# State Commercial Banks, Savings Institutions, per core.company.sic_code).
BANK_SIC_PREFIXES: tuple[str, ...] = ("602", "603", "606")
BANK_INCOMPATIBLE_CONCEPTS: frozenset[str] = frozenset({"revenue", "gross_profit", "cost_of_revenue", "operating_expenses", "operating_income"})


def seed_line_item_mapping(conn: psycopg.Connection) -> dict:
    stats = {"considered": len(LINE_ITEM_MAP), "mapped": 0, "unresolved_concept": 0}
    with conn.cursor() as cur:
        for (statement_type, line_item), concept_name in LINE_ITEM_MAP.items():
            cur.execute("select id from analytics.canonical_concept where name = %s", (concept_name,))
            row = cur.fetchone()
            if row is None:
                stats["unresolved_concept"] += 1
                logger.warning("yfinance_financials.concept_not_found", concept=concept_name, line_item=line_item)
                continue
            concept_id = row[0]
            sign_flip = (statement_type, line_item) in SIGN_FLIP_LINE_ITEMS
            cur.execute(
                """
                insert into analytics.yfinance_line_item_mapping (statement_type, line_item, canonical_concept_id, sign_flip, confidence, notes)
                values (%(statement_type)s, %(line_item)s, %(concept_id)s, %(sign_flip)s, 'provisional', %(notes)s)
                on conflict (statement_type, line_item) do update
                    set canonical_concept_id = excluded.canonical_concept_id, sign_flip = excluded.sign_flip, notes = excluded.notes
                """,
                {
                    "statement_type": statement_type, "line_item": line_item, "concept_id": concept_id,
                    "sign_flip": sign_flip,
                    "notes": "Bank-incompatible: yfinance's own income statement has no equivalent row, or its 'Total Revenue' is a computed aggregate that structurally disagrees with our bank-specific revenue tag -- see module docstring."
                    if concept_name in BANK_INCOMPATIBLE_CONCEPTS else None,
                },
            )
            stats["mapped"] += 1
    conn.commit()
    logger.info("yfinance_financials.mapping_seeded", **stats)
    return stats
