"""Bank canonical concepts (founder "everything approved" 2026-11-14, ruled by Dhairya): six additive
rows so the structural resolver's bank data points load (structural_loader / docmap_loader reject a
data point with "no canonical concept of that name").

Additive and idempotent: `insert ... on conflict (name) do nothing`, so an existing concept row is
never touched. No concept_mapping rows: values reach these concepts through company_tag_map
(structural-load / docmap-load), not through the generic tag resolver. All first_match, served under
their own name (docmap_loader.served_concept: no `<name>_resolved` concept exists, no alias).
Applies to the bank template group only (sector_templates.GROUP_ONLY).
"""

import psycopg

# (name, statement, combination_mode, description); unit USD. IS items are duration, BS items instant.
BANK_CONCEPTS: list[tuple[str, str, str, str]] = [
    (
        "deposits",
        "balance_sheet",
        "first_match",
        "Total deposits (instant, USD) -- bank balance-sheet liability line (us-gaap Deposits)",
    ),
    (
        "loans_net",
        "balance_sheet",
        "first_match",
        "Loans and leases receivable, net of allowance (instant, USD) -- bank balance-sheet asset line",
    ),
    (
        "noninterest_expense",
        "income_statement",
        "first_match",
        "Total noninterest expense (duration, USD) -- a bank's operating expense line (us-gaap NoninterestExpense)",
    ),
    (
        "noninterest_income",
        "income_statement",
        "first_match",
        "Total noninterest income (duration, USD) -- bank fee and other non-spread revenue (us-gaap NoninterestIncome)",
    ),
    (
        "provision_for_credit_losses",
        "income_statement",
        "first_match",
        "Provision for credit losses (duration, USD) -- bank income-statement charge for expected loan losses",
    ),
    (
        "total_interest_income",
        "income_statement",
        "first_match",
        "Total interest and dividend income (duration, USD) -- bank gross interest revenue before interest expense",
    ),
]


def plan(conn: psycopg.Connection) -> tuple[list[tuple], list[str]]:
    """(rows that would be inserted, names already present). Read only."""
    have = {
        r[0]
        for r in conn.execute(
            "select name from analytics.canonical_concept where name = any(%s)",
            ([c[0] for c in BANK_CONCEPTS],),
        )
    }
    return [c for c in BANK_CONCEPTS if c[0] not in have], sorted(have)


def seed(conn: psycopg.Connection) -> dict:
    """Insert the missing rows; never updates an existing one."""
    rows, _ = plan(conn)
    with conn.cursor() as cur:
        cur.executemany(
            "insert into analytics.canonical_concept (name, statement, combination_mode, description) "
            "values (%s, %s, %s, %s) on conflict (name) do nothing",
            rows,
        )
    conn.commit()
    return {"considered": len(BANK_CONCEPTS), "inserted": len(rows)}
