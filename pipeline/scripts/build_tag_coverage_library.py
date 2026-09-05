"""Research tool (doc 40) -- NOT part of the production pipeline (not
imported by any job, no CLI wiring). Surveys every canonical concept's
current XBRL tag coverage against the real 5,024-company active
population, and finds candidate unmapped tags that could safely widen
coverage.

Built after a real, live finding (2026-09-01): `total_debt` (the ONLY
`sum`-mode canonical concept -- confirmed by querying all 44) has a
360-company gap where adding the obvious candidate tags naively would
have double-counted debt for ~2,168 OTHER companies that already report
both forms. This script exists so future coverage decisions are made
from a real, queryable inventory instead of re-deriving it live one
metric at a time, and so the `sum`-mode double-counting risk class is
flagged explicitly wherever it applies (only `total_debt` today, but
the script checks all 44, not just the ones already known).

Per-concept search keywords are curated by hand (not derived
automatically from the concept name) -- an automatic ILIKE match on a
bare word like "income" would return hundreds of irrelevant tags across
statement areas. Deliberately mirrors the manual queries already run
live this session for gross_profit/total_debt/operating_income/
interest_expense/current_assets, so this script's own output can be
checked against those known-correct numbers before trusting it for the
other ~40 concepts (see doc 40's own verification section).

Usage: uv run python scripts/build_tag_coverage_library.py
Output: reference/xbrl_tag_coverage_library.json
"""

import json
import sys
from pathlib import Path

import psycopg

from scrooner_pipeline.db.connection import get_connection

OUTPUT_PATH = Path(__file__).resolve().parents[1] / "reference" / "xbrl_tag_coverage_library.json"

# concept name -> (statement area, list of ILIKE search fragments against
# core.concept.tag). Curated by hand against each concept's own real
# meaning -- a keyword search across the WRONG statement area (e.g.
# "Income" tags showing up for a balance_sheet concept) would be noise,
# so each search is scoped to the concept's own statement.
CONCEPT_SEARCH_KEYWORDS: dict[str, list[str]] = {
    "revenue": ["Revenue", "Sales"],
    "gross_profit": ["GrossProfit"],
    "operating_income": ["OperatingIncome"],
    "net_income": ["NetIncome", "ProfitLoss"],
    "stockholders_equity": ["StockholdersEquity", "PartnersCapital"],
    "cash_and_equivalents": ["Cash"],
    "total_debt": ["Debt", "Borrowing", "NotesPayable", "LoansPayable"],
    "current_assets": ["AssetsCurrent"],
    "current_liabilities": ["LiabilitiesCurrent"],
    "interest_expense": ["InterestExpense"],
    "income_tax_expense": ["IncomeTaxExpense", "IncomeTaxProvision"],
    "income_before_tax": ["BeforeIncomeTax", "IncomeLossFromContinuingOperationsBeforeIncomeTaxes"],
    "cfo": ["NetCashProvidedByUsedInOperatingActivities"],
    "capex": ["PaymentsToAcquireProperty", "PaymentsForCapitalImprovements", "PaymentsToAcquireProductiveAssets"],
    "diluted_eps": ["EarningsPerShareDiluted"],
    "shares_outstanding": ["SharesOutstanding"],
    "dividends_per_share": ["DividendsPerShare"],
    "inventory": ["Inventory"],
    "sbc": ["ShareBasedCompensation", "StockCompensation"],
    "depreciation_and_amortization": ["DepreciationAndAmortization", "DepreciationDepletionAndAmortization"],
    "accounts_receivable": ["AccountsReceivable", "ReceivablesNetCurrent"],
    "accounts_payable": ["AccountsPayable"],
    "goodwill": ["Goodwill"],
    "basic_eps": ["EarningsPerShareBasic"],
    "cf_ar_change": ["IncreaseDecreaseInAccountsReceivable", "IncreaseDecreaseInReceivables"],
    "cf_inventory_change": ["IncreaseDecreaseInInventor"],
    "cf_ap_change": ["IncreaseDecreaseInAccountsPayable"],
    "research_and_development": ["ResearchAndDevelopment"],
    "interest_income": ["InterestIncome", "InvestmentIncomeInterest"],
    "sga_expense": ["SellingGeneralAndAdministrative", "GeneralAndAdministrativeExpense"],
    "comprehensive_income": ["ComprehensiveIncome"],
    "amortization_of_intangibles": ["AmortizationOfIntangible"],
    "effective_tax_rate_reported": ["EffectiveIncomeTaxRate"],
    "employee_count": ["NumberOfEmployees"],
    "cost_of_revenue": ["CostOfGoodsAndServicesSold", "CostOfRevenue", "CostOfGoodsSold", "CostOfSales"],
    "operating_expenses": ["OperatingExpenses", "CostsAndExpenses"],
    "total_assets": ["Assets"],
    "total_liabilities": ["Liabilities"],
    "ppe_net": ["PropertyPlantAndEquipment"],
    "cash_flow_investing": ["NetCashProvidedByUsedInInvestingActivities"],
    "cash_flow_financing": ["NetCashProvidedByUsedInFinancingActivities"],
    "dividends_paid": ["PaymentsOfDividends"],
    "share_buybacks": ["PaymentsForRepurchaseOfCommonStock", "StockRepurchase"],
    "public_float": ["EntityPublicFloat"],
}


def _load_concepts(conn: psycopg.Connection) -> list[dict]:
    with conn.cursor() as cur:
        cur.execute("select id, name, statement, combination_mode from analytics.canonical_concept order by name")
        return [{"id": r[0], "name": r[1], "statement": r[2], "combination_mode": r[3]} for r in cur.fetchall()]


def _load_current_mappings(conn: psycopg.Connection, canonical_concept_id: int) -> list[dict]:
    with conn.cursor() as cur:
        cur.execute(
            """
            select cn.taxonomy, cn.tag, cm.priority, cm.confidence
            from analytics.concept_mapping cm
            join core.concept cn on cn.id = cm.concept_id
            where cm.canonical_concept_id = %s
            order by cm.priority
            """,
            (canonical_concept_id,),
        )
        return [{"taxonomy": r[0], "tag": r[1], "priority": r[2], "confidence": r[3]} for r in cur.fetchall()]


def _load_canonical_concept_coverage(conn: psycopg.Connection) -> dict[int, int]:
    """Same fix as _load_concept_id_coverage below, applied to
    analytics.canonical_fact -- a per-concept `count(distinct
    company_id) where canonical_concept_id = X` loop took 8+ seconds
    PER CALL even with idx_canonical_fact_concept_id in place (still
    real row-scanning work for a broadly-covered concept, index or not)
    -- one grouped pass, done once, avoids 44 separate scans."""
    with conn.cursor() as cur:
        cur.execute("select canonical_concept_id, count(distinct company_id) from analytics.canonical_fact group by canonical_concept_id")
        return dict(cur.fetchall())


def _load_concept_id_coverage(conn: psycopg.Connection) -> dict[int, int]:
    """ONE global aggregation over core.fact (~67M rows, ~96s, done once
    and reused for every concept) instead of N per-keyword/per-tag
    scans. Found live 2026-09-02: even with idx_fact_concept_id in
    place, a per-tag `count(distinct company_id) where concept_id = X`
    loop across ~400+ candidate tags would have taken over an hour and
    repeatedly hit Supabase's 2-minute statement_timeout on the
    broader-keyword concepts (e.g. "Debt" matches many tags). A single
    `group by concept_id` rollup, done once, avoids both problems."""
    with conn.cursor() as cur:
        cur.execute("set statement_timeout = '5min'")
        cur.execute(
            "select concept_id, count(distinct company_id) from core.fact where is_authoritative = true group by concept_id"
        )
        return dict(cur.fetchall())


def _candidate_tags(
    conn: psycopg.Connection, keywords: list[str], already_mapped_tags: set[str], coverage_by_concept_id: dict[int, int]
) -> list[dict]:
    if not keywords:
        return []
    like_clauses = " or ".join(["tag ilike %s"] * len(keywords))
    params = [f"%{kw}%" for kw in keywords]
    with conn.cursor() as cur:
        cur.execute(
            f"select id, tag from core.concept where taxonomy = 'us-gaap' and ({like_clauses})",
            params,
        )
        matches = {r[0]: r[1] for r in cur.fetchall() if r[1] not in already_mapped_tags}
        results = [
            {"tag": tag, "companies": coverage_by_concept_id[cid]}
            for cid, tag in matches.items()
            if cid in coverage_by_concept_id
        ]
        results.sort(key=lambda r: -r["companies"])
        return results[:15]


def _total_active_companies(conn: psycopg.Connection) -> int:
    with conn.cursor() as cur:
        cur.execute("select count(*) from core.company where status = 'active'")
        return cur.fetchone()[0]


def build_library() -> dict:
    library: dict[str, dict] = {}
    with get_connection() as conn:
        total_companies = _total_active_companies(conn)
        concepts = _load_concepts(conn)
        print("loading global concept_id -> company coverage (one-time, ~90s)...", file=sys.stderr)
        coverage_by_concept_id = _load_concept_id_coverage(conn)
        print(f"loaded coverage for {len(coverage_by_concept_id)} distinct concept_ids", file=sys.stderr)
        print("loading canonical_fact coverage per canonical concept (one-time)...", file=sys.stderr)
        canonical_coverage = _load_canonical_concept_coverage(conn)
        print(f"loaded coverage for {len(canonical_coverage)} canonical concepts", file=sys.stderr)
        for concept in concepts:
            name = concept["name"]
            current_mappings = _load_current_mappings(conn, concept["id"])
            coverage = canonical_coverage.get(concept["id"], 0)
            already_mapped_tags = {m["tag"] for m in current_mappings}
            keywords = CONCEPT_SEARCH_KEYWORDS.get(name, [])
            candidates = _candidate_tags(conn, keywords, already_mapped_tags, coverage_by_concept_id)

            if coverage >= 0.85 * total_companies:
                status = "well_covered"
            elif concept["combination_mode"] == "sum" and any(c["companies"] > 50 for c in candidates):
                status = "gap_needs_fallback_resolver"
            elif any(c["companies"] > 100 for c in candidates):
                status = "gap_safe_candidate_found"
            else:
                status = "gap_no_safe_candidate"

            library[name] = {
                "statement": concept["statement"],
                "combination_mode": concept["combination_mode"],
                "current_coverage": coverage,
                "current_coverage_pct": round(100 * coverage / total_companies, 1),
                "current_mappings": current_mappings,
                "candidate_tags": candidates,
                "status": status,
            }
            print(
                f"{name}: {coverage}/{total_companies} ({library[name]['current_coverage_pct']}%) -> {status}",
                file=sys.stderr,
            )
    return {"total_active_companies": total_companies, "concepts": library}


def main() -> None:
    result = build_library()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(result, indent=2))
    print(f"\nWritten to {OUTPUT_PATH}", file=sys.stderr)


if __name__ == "__main__":
    main()
