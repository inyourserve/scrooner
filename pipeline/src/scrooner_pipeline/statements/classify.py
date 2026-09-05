"""Statement classification (doc 17 Sec 4) -- the company page's financial
statement tables. Extends `analytics.canonical_concept`/`concept_mapping`
additively with statement-display-only concepts the 18 locked ratio
metrics never needed (cost_of_revenue, operating_expenses, total_assets,
etc.), then seeds analytics.statement_line to say which concept goes on
which statement, in what order. Mapper's own frozen mapper/concepts.py
and mapper/resolve.py are NOT modified -- this mirrors their exact
upsert pattern as new, separate code writing to the same shared tables,
and reuses resolve()'s already-verified resolution logic unchanged (run
`scrooner-map resolve-facts` after seeding here, same command Mapper
Stage 3b already has).

Every new tag mapping below checked against real golden-8 usage before
being added -- see doc 17 Sec 4 for the live coverage check (8/8, 7/8
companies for the base tags used here) and the CostOfRevenue vs.
CostOfGoodsAndServicesSold alternates-not-summands confirmation (MSFT's
2016/2017 overlap years report identical values under both tags).
"""

import psycopg
import structlog

logger = structlog.get_logger()

# (name, statement, combination_mode, description) -- same shape as
# mapper/concepts.py's CANONICAL_CONCEPTS, new rows only.
NEW_CANONICAL_CONCEPTS: list[tuple[str, str, str, str]] = [
    ("cost_of_revenue", "income_statement", "first_match", "Cost of goods/services sold"),
    ("operating_expenses", "income_statement", "first_match", "Total operating expenses (SG&A + R&D, where reported as one line)"),
    ("total_assets", "balance_sheet", "first_match", "Total assets"),
    ("total_liabilities", "balance_sheet", "first_match", "Total liabilities"),
    ("ppe_net", "balance_sheet", "first_match", "Property, plant and equipment, net"),
    ("cash_flow_investing", "cash_flow", "first_match", "Net cash used in/provided by investing activities"),
    ("cash_flow_financing", "cash_flow", "first_match", "Net cash used in/provided by financing activities"),
    ("dividends_paid", "cash_flow", "first_match", "Total dividends paid (dollar amount, not per-share)"),
    ("share_buybacks", "cash_flow", "first_match", "Cash paid for common stock repurchases"),
    (
        "public_float",
        "balance_sheet",
        "first_match",
        "NOT Market Cap -- aggregate market value of shares held by non-affiliates, "
        "as of the last business day of the filer's 2nd fiscal quarter (10-K cover-page "
        "disclosure, dei:EntityPublicFloat). Annual, excludes insider-held shares, real "
        "lag. See doc 23 Stage B: shown as a distinctly labeled proxy, never substituted "
        "for the still price-vendor-blocked Market Cap metric.",
    ),
]

# (canonical_concept_name, taxonomy, tag, priority, confidence, notes)
NEW_CONCEPT_MAPPINGS: list[tuple[str, str, str, int, str, str]] = [
    ("cost_of_revenue", "us-gaap", "CostOfGoodsAndServicesSold", 1, "approved", "Most current tag across the golden set"),
    ("cost_of_revenue", "us-gaap", "CostOfRevenue", 2, "approved",
     "Confirmed alternate, not summand, via MSFT's 2016/2017 overlap years reporting identical values under both tags"),
    ("operating_expenses", "us-gaap", "OperatingExpenses", 1, "approved", ""),
    ("total_assets", "us-gaap", "Assets", 1, "approved", ""),
    ("total_liabilities", "us-gaap", "Liabilities", 1, "approved", ""),
    ("ppe_net", "us-gaap", "PropertyPlantAndEquipmentNet", 1, "approved", ""),
    ("cash_flow_investing", "us-gaap", "NetCashProvidedByUsedInInvestingActivities", 1, "approved", ""),
    ("cash_flow_financing", "us-gaap", "NetCashProvidedByUsedInFinancingActivities", 1, "approved", ""),
    ("dividends_paid", "us-gaap", "PaymentsOfDividends", 1, "approved", ""),
    ("dividends_paid", "us-gaap", "PaymentsOfDividendsCommonStock", 2, "provisional", "Narrower variant, not yet cross-checked as strictly an alternate"),
    ("share_buybacks", "us-gaap", "PaymentsForRepurchaseOfCommonStock", 1, "approved", ""),
    ("public_float", "dei", "EntityPublicFloat", 1, "approved",
     "Confirmed live 2026-08-17 against real AAPL values ($3.253T as of 2025-03-28) -- see doc 23 Stage B."),
]

# (statement, display_order, display_label, canonical_concept_name) --
# reuses Mapper's existing 17 concepts where they already cover a
# statement line (revenue, gross_profit, operating_income, etc.) rather
# than re-mapping them.
STATEMENT_LINES: list[tuple[str, int, str, str]] = [
    ("income_statement", 1, "Revenue", "revenue"),
    ("income_statement", 2, "Cost of Revenue", "cost_of_revenue"),
    ("income_statement", 3, "Gross Profit", "gross_profit"),
    ("income_statement", 4, "Operating Expenses", "operating_expenses"),
    ("income_statement", 5, "Operating Income", "operating_income"),
    ("income_statement", 6, "Interest Expense", "interest_expense"),
    ("income_statement", 7, "Income Before Tax", "income_before_tax"),
    ("income_statement", 8, "Income Tax Expense", "income_tax_expense"),
    ("income_statement", 9, "Net Income", "net_income"),
    ("income_statement", 10, "Diluted EPS", "diluted_eps"),
    ("balance_sheet", 1, "Cash and Equivalents", "cash_and_equivalents"),
    ("balance_sheet", 2, "Current Assets", "current_assets"),
    ("balance_sheet", 3, "Property, Plant & Equipment", "ppe_net"),
    ("balance_sheet", 4, "Total Assets", "total_assets"),
    ("balance_sheet", 5, "Current Liabilities", "current_liabilities"),
    ("balance_sheet", 6, "Total Debt", "total_debt_resolved"),  # doc 40, 2026-09-02 -- prefers combined tag, falls back to split-tag sum
    ("balance_sheet", 7, "Total Liabilities", "total_liabilities"),
    ("balance_sheet", 8, "Stockholders' Equity", "stockholders_equity"),
    ("cash_flow", 1, "Cash from Operations", "cfo"),
    ("cash_flow", 2, "Capital Expenditures", "capex"),
    ("cash_flow", 3, "Cash from Investing", "cash_flow_investing"),
    ("cash_flow", 4, "Cash from Financing", "cash_flow_financing"),
    ("cash_flow", 5, "Dividends Paid", "dividends_paid"),
    ("cash_flow", 6, "Share Buybacks", "share_buybacks"),
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
                logger.warning("statements.tag_not_in_core", taxonomy=taxonomy, tag=tag, canonical=canonical_name)
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
    logger.info("statements.mappings_seeded", **stats)
    return stats


def seed_statement_lines(conn: psycopg.Connection, canonical_id_by_name: dict[str, int]) -> int:
    rows = [
        {"statement": s, "display_order": o, "display_label": label, "canonical_concept_id": canonical_id_by_name[concept_name]}
        for s, o, label, concept_name in STATEMENT_LINES
    ]
    with conn.cursor() as cur:
        cur.executemany(
            """
            insert into analytics.statement_line (statement, display_order, display_label, canonical_concept_id)
            values (%(statement)s, %(display_order)s, %(display_label)s, %(canonical_concept_id)s)
            on conflict (statement, display_order) do update
                set display_label = excluded.display_label, canonical_concept_id = excluded.canonical_concept_id
            """,
            rows,
        )
    conn.commit()
    return len(rows)


def seed(conn: psycopg.Connection) -> dict:
    canonical_id_by_name = seed_new_canonical_concepts(conn)
    mapping_stats = seed_new_concept_mappings(conn, canonical_id_by_name)
    line_count = seed_statement_lines(conn, canonical_id_by_name)
    return {"new_canonical_concepts": len(NEW_CANONICAL_CONCEPTS), "statement_lines": line_count, **mapping_stats}


def get_statement(conn: psycopg.Connection, company_id: int, statement: str) -> dict:
    """Full statement, all periods, in display order. Reuses
    analytics.canonical_fact directly -- already resolved, already
    taxonomy-drift-safe, no new resolution logic.

    Excludes periods with fiscal_period is null -- found live 2026-08-17:
    a non-standard YTD duration span (e.g. AAPL's 2025-09-28..2026-06-27,
    9 months) that the Normalizer deliberately leaves unclassified
    (doc 09's own design) otherwise shows up as an extra, confusing
    near-duplicate column next to the real Q3 quarter ending the same
    date. Mapper's own calculate.py already skips these for the same
    reason -- this reuses that established pattern, not a new rule."""
    with conn.cursor() as cur:
        cur.execute(
            """
            select sl.display_order, sl.display_label, p.fiscal_year, p.fiscal_period, p.end_date, cf.value
            from analytics.statement_line sl
            left join analytics.canonical_fact cf
                on cf.canonical_concept_id = sl.canonical_concept_id and cf.company_id = %s
            left join core.period p on p.id = cf.period_id
            where sl.statement = %s and (p.fiscal_period is not null or p.id is null)
            order by sl.display_order, p.end_date
            """,
            (company_id, statement),
        )
        rows = cur.fetchall()

    lines: dict[int, dict] = {}
    periods: set[tuple] = set()
    for display_order, label, fiscal_year, fiscal_period, period_end, value in rows:
        lines.setdefault(display_order, {"label": label, "values": {}})
        if period_end is not None:
            key = (fiscal_year, fiscal_period, period_end)
            periods.add(key)
            lines[display_order]["values"][key] = value

    sorted_periods = sorted(periods, key=lambda k: k[2])
    return {
        "periods": [{"fiscal_year": fy, "fiscal_period": fp, "period_end": str(pe)} for fy, fp, pe in sorted_periods],
        "lines": [
            {"label": lines[o]["label"], "values": [lines[o]["values"].get(p) for p in sorted_periods]}
            for o in sorted(lines)
        ],
    }
