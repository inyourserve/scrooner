"""Concept tag-candidate library (2026-09-08) -- DB-native replacement
for pipeline/scripts/build_tag_coverage_library.py's JSON output, per
direct user instruction ("retire json, make everything into db as
source of truth"). Writes analytics.concept_tag_candidate instead of
reference/xbrl_tag_coverage_library.json, and is wired into the daily
cron via `scrooner-map build-tag-candidates` (the JSON version was
manually-triggered only and had gone stale -- last built 2026-09-02,
missing everything since).

Same design as the retired script, ported not reinvented:
- Per-concept search keywords are curated by hand (CONCEPT_SEARCH_
  KEYWORDS below) -- an automatic ILIKE match on a bare word like
  "income" would return hundreds of irrelevant tags across statement
  areas. Add a new concept's keywords here when it's added to
  expanded_concepts.py, same discipline as every other curated table
  in this project.
- One global concept_id -> company-count aggregation over core.fact,
  done once and reused for every concept's candidate search, not one
  scan per candidate tag -- found live 2026-09-02 that the per-tag
  version hit Supabase's 2-minute statement_timeout on broad keywords.
- report_status() classifies each concept from its current coverage +
  stored candidates (well_covered / gap_safe_candidate_found /
  gap_needs_fallback_resolver / gap_no_safe_candidate) -- computed at
  READ time from live data, never stored redundantly next to the
  numbers it's derived from."""

import psycopg
import structlog

logger = structlog.get_logger()

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
    "other_income_expense_net": ["NonoperatingIncomeExpense", "InterestIncomeExpenseNet"],
}

CANDIDATES_PER_CONCEPT = 15


def _load_concepts(conn: psycopg.Connection) -> list[dict]:
    with conn.cursor() as cur:
        cur.execute("select id, name, statement, combination_mode from analytics.canonical_concept order by name")
        return [{"id": r[0], "name": r[1], "statement": r[2], "combination_mode": r[3]} for r in cur.fetchall()]


def _load_current_mapped_tags(conn: psycopg.Connection, canonical_concept_id: int) -> set[str]:
    with conn.cursor() as cur:
        cur.execute(
            "select cn.tag from analytics.concept_mapping cm join core.concept cn on cn.id = cm.concept_id where cm.canonical_concept_id = %s",
            (canonical_concept_id,),
        )
        return {r[0] for r in cur.fetchall()}


def _load_concept_id_coverage(conn: psycopg.Connection) -> dict[int, int]:
    """One global aggregation over core.fact, done once, reused for
    every concept's candidate search -- see module docstring."""
    with conn.cursor() as cur:
        cur.execute("set statement_timeout = '5min'")
        cur.execute(
            "select concept_id, count(distinct company_id) from core.fact where is_authoritative = true group by concept_id"
        )
        return dict(cur.fetchall())


def _candidate_tags(
    conn: psycopg.Connection, keywords: list[str], already_mapped_tags: set[str], coverage_by_concept_id: dict[int, int]
) -> list[tuple[str, str, int]]:
    if not keywords:
        return []
    like_clauses = " or ".join(["tag ilike %s"] * len(keywords))
    params = [f"%{kw}%" for kw in keywords]
    with conn.cursor() as cur:
        cur.execute(
            f"select id, taxonomy, tag from core.concept where taxonomy = 'us-gaap' and ({like_clauses})",
            params,
        )
        matches = {r[0]: (r[1], r[2]) for r in cur.fetchall() if r[2] not in already_mapped_tags}
        results = [
            (taxonomy, tag, coverage_by_concept_id[cid])
            for cid, (taxonomy, tag) in matches.items()
            if cid in coverage_by_concept_id
        ]
        results.sort(key=lambda r: -r[2])
        return results[:CANDIDATES_PER_CONCEPT]


_UPSERT_SQL = """
    insert into analytics.concept_tag_candidate (canonical_concept_id, taxonomy, tag, company_count, checked_at)
    values (%(canonical_concept_id)s, %(taxonomy)s, %(tag)s, %(company_count)s, now())
    on conflict (canonical_concept_id, taxonomy, tag) do update
        set company_count = excluded.company_count, checked_at = now()
"""


def build_tag_candidates(conn: psycopg.Connection) -> dict:
    concepts = _load_concepts(conn)
    coverage_by_concept_id = _load_concept_id_coverage(conn)
    stats = {"considered": len(concepts), "candidates_written": 0}

    for concept in concepts:
        keywords = CONCEPT_SEARCH_KEYWORDS.get(concept["name"], [])
        already_mapped = _load_current_mapped_tags(conn, concept["id"])
        candidates = _candidate_tags(conn, keywords, already_mapped, coverage_by_concept_id)

        with conn.cursor() as cur:
            # Delete-then-reinsert scoped to this concept -- a candidate
            # that's since been mapped (and so no longer a candidate)
            # must disappear, a plain upsert can only ever add/update.
            cur.execute("delete from analytics.concept_tag_candidate where canonical_concept_id = %s", (concept["id"],))
            if candidates:
                cur.executemany(
                    _UPSERT_SQL,
                    [
                        {"canonical_concept_id": concept["id"], "taxonomy": taxonomy, "tag": tag, "company_count": count}
                        for taxonomy, tag, count in candidates
                    ],
                )
        conn.commit()
        stats["candidates_written"] += len(candidates)

    logger.info("tag_candidates.built", **stats)
    return stats


def report_status(conn: psycopg.Connection) -> list[dict]:
    """Classifies every canonical concept from its live coverage +
    stored candidates -- same 4-way status the retired JSON library
    used, computed at read time so it's never stale relative to the
    numbers it's derived from."""
    with conn.cursor() as cur:
        cur.execute("select count(*) from core.company where status = 'active'")
        total_companies = cur.fetchone()[0]

        cur.execute(
            """
            select cc.id, cc.name, cc.combination_mode,
                   coalesce(cf.coverage, 0) as coverage
            from analytics.canonical_concept cc
            left join (
                select canonical_concept_id, count(distinct company_id) as coverage
                from analytics.canonical_fact group by canonical_concept_id
            ) cf on cf.canonical_concept_id = cc.id
            order by cc.name
            """
        )
        concepts = cur.fetchall()

        cur.execute(
            "select canonical_concept_id, tag, company_count from analytics.concept_tag_candidate order by canonical_concept_id, company_count desc"
        )
        candidates_by_concept: dict[int, list[tuple[str, int]]] = {}
        for concept_id, tag, count in cur.fetchall():
            candidates_by_concept.setdefault(concept_id, []).append((tag, count))

    rows = []
    for concept_id, name, combination_mode, coverage in concepts:
        candidates = candidates_by_concept.get(concept_id, [])
        pct = round(100 * coverage / total_companies, 1) if total_companies else 0.0
        if coverage >= 0.85 * total_companies:
            status = "well_covered"
        elif combination_mode == "sum" and any(c > 50 for _, c in candidates):
            status = "gap_needs_fallback_resolver"
        elif any(c > 100 for _, c in candidates):
            status = "gap_safe_candidate_found"
        else:
            status = "gap_no_safe_candidate"
        rows.append(
            {
                "concept": name,
                "coverage": coverage,
                "coverage_pct": pct,
                "status": status,
                "top_candidate": candidates[0] if candidates else None,
            }
        )
    return rows
