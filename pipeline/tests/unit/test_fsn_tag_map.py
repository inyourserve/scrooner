"""fsn_store.tag_map: the per-company tag map (analytics.company_tag_map rows) decided by filing structure.

Real FSN company directories (one 10-K each, SEC FSN 2025q1): GE FY2024 and Apple Q1 FY2025. The map is decided in
memory: these tests also check that nothing is written to fsn.line_map."""

from pathlib import Path

import psycopg
import pytest

from scrooner_pipeline.fsn_store import load, rules, tag_map

ROOT = Path(__file__).resolve().parents[3]
FIXTURES = {
    "0000040545": ROOT / "pipeline/tests/fixtures/fsn_is_structure/0000040545",
    "0000320193": ROOT / "pipeline/tests/fixtures/fsn_is_net_income/0000320193",
}
CONCEPTS = (
    "revenue_sanity_resolved", "cost_of_revenue_resolved", "gross_profit_resolved", "operating_income_resolved",
    "net_income_resolved", "income_before_tax_resolved", "income_tax_expense_resolved", "interest_expense_resolved",
    "basic_eps_resolved", "diluted_eps_resolved", "dividends_per_share_resolved", "shares_outstanding_resolved",
    "cfo_resolved", "capex_resolved", "depreciation_and_amortization_resolved", "share_buybacks_resolved",
    "dividends_paid_resolved", "total_assets_resolved", "total_liabilities_resolved", "stockholders_equity_resolved",
    "current_assets_resolved", "current_liabilities_resolved", "cash_and_equivalents_resolved", "total_debt_resolved",
)


def _one(conn, sql, params=()):
    return conn.execute(sql, params).fetchone()[0]


@pytest.fixture
def store(isolated_database_url):
    c = psycopg.connect(isolated_database_url)
    if _one(c, "select count(*) from information_schema.tables where table_schema = 'fsn' and table_name in ('filing', 'line', 'concept_rule')") != 3:
        c.close()
        pytest.skip("needs migration 0118")
    for name in CONCEPTS:
        c.execute(
            "insert into analytics.canonical_concept (name, statement, combination_mode) values (%s, 'income_statement', 'first_match') "
            "on conflict (name) do nothing",
            (name,),
        )
    for cik, d in FIXTURES.items():
        c.execute("insert into core.company (cik, company_name) values (%s, %s)", (cik, cik))
        c.commit()
        load.load_company(c, d, loader_commit="test")
        c.commit()
    for f in sorted((ROOT / "data-team/47-fsn-store/concept_rules").glob("*.jsonl")):
        if f.name.startswith("_"):
            continue
        res = rules.seed(c, f, apply=True)
        assert not res["errors"], (f.name, res["errors"])
    c.commit()
    yield c
    c.close()


def _cid(conn, cik):
    return _one(conn, "select id from core.company where cik = %s", (cik,))


def _by(rows, stmt, tag):
    return [r for r in rows if r["stmt"] == stmt and r["tag"] == tag]


@pytest.mark.integration
def test_ge_tag_map_decides_by_structure_and_writes_nothing(store):
    rows, residue = tag_map.company_tag_map(store, _cid(store, "0000040545"))
    assert _one(store, "select count(*) from fsn.line_map") == 0  # decided in memory only
    assert rows and all(set(tag_map.COLUMNS) <= set(r) | {"disposition"} for r in rows)
    out = [{k: r.get(k) for k in tag_map.COLUMNS} for r in rows]
    assert {r["decision"] for r in out} <= {"concept", "component", "combined", "excluded"}
    # the catalog concept from the rules, on its statement
    ni = _by(out, "IS", "NetIncomeLoss")
    assert ni and ni[0]["decision"] == "concept" and ni[0]["canonical_concept"] == "net_income_resolved"
    assert ni[0]["decided_by"] == "rule" and ni[0]["era_to"] is None  # the latest filing's era is open
    # R1: presentation-only rows
    assert any(r["decision"] == "excluded" and r["reason_class"] == "presentation-only" for r in out)
    # R2: a standard element without a catalog concept is its own concept
    std = [r for r in out if r["decided_by"] == "standard_tag"]
    assert std and all(r["canonical_concept"] == f"{r['taxonomy']}:{r['tag']}" for r in std)
    # one row per (taxonomy, tag, stmt, era) and every row carries filing evidence
    keys = [(r["taxonomy"], r["tag"], r["stmt"], r["era_from"]) for r in out]
    assert len(keys) == len(set(keys))
    assert all(r["evidence_adsh"] and r["evidence_line"] is not None for r in out)
    # every residue row names why and where
    assert all(z["reason"] and z["evidence_adsh"] for z in residue)


@pytest.mark.integration
def test_same_tag_on_another_statement_is_the_same_concept(store):
    """Apple prints NetIncomeLoss on the income statement and again on the cash-flow and equity statements: the
    seed maps the IS line; the other statements' rows are the same fact (cross_statement)"""
    rows, _ = tag_map.company_tag_map(store, _cid(store, "0000320193"))
    others = [r for r in rows if r["tag"] == "NetIncomeLoss" and r["stmt"] != "IS"]
    assert others
    assert all(r["canonical_concept"] == "net_income_resolved" for r in others)
    assert {r["decided_by"] for r in others} <= {"cross_statement", "rule"}


def test_calc_ancestor_sign_and_ambiguity():
    arcs = {"Ext": [("Mid", -1)], "Mid": [("Total", 1)], "Two": [("A", 1), ("B", 1)]}
    mapped = {("BS", "Total"): "total_liabilities_resolved", ("BS", "A"): "x", ("BS", "B"): "y"}
    assert tag_map.calc_ancestor("Ext", "BS", arcs, mapped) == ("total_liabilities_resolved", -1, ["Ext", "Mid", "Total"])
    assert tag_map.calc_ancestor("Ext", "IS", arcs, mapped) is None  # the ancestor must be on the same statement
    assert tag_map.calc_ancestor("Two", "BS", arcs, mapped) is None  # two different nearest concepts: undecided


def test_contract_fields_vocabulary():
    base = {"rule_id": None, "reason": None, "components": None, "sign": None, "combine_role": None}
    assert tag_map.contract_fields({**base, "disposition": "mapped", "concept": "c", "decided_by": "rule"})["decision"] == "concept"
    comp = tag_map.contract_fields(
        {**base, "disposition": "combined", "combine_role": "component_of", "concept": "p", "sign": -1,
         "decided_by": "calc_ancestor", "reason": "calc path Ext > Mid > Total"}
    )
    assert comp["decision"] == "component" and comp["parent_concept"] == "p" and comp["combine_sign"] == -1
    assert comp["evidence_cal_parent"] == "Mid"
    ex = tag_map.contract_fields(
        {**base, "disposition": "excluded", "concept": None, "decided_by": "structural", "reason": "presentation-only"}
    )
    assert ex["decision"] == "excluded" and ex["reason_class"] == "presentation-only" and ex["reason"]


@pytest.mark.parametrize("tag, out", [("StatementLineItems", True), ("SegmentsAxis", True), ("CommonStockMember", True),
                                      ("ProductOrServiceDomain", True), ("Revenues", False), ("MemberUnitsIssued", False)])
def test_presentation_only_names(tag, out):
    assert bool(tag_map.PRESENTATION_ONLY.search(tag)) is out


LIB = {
    ("IS", "NetIncomeLoss"): {"stmt": "IS", "tag": "NetIncomeLoss", "decision": "component", "concept": "",
                              "parent_concept": "revenue_sanity_resolved", "reason_class": "", "caveat": ""},
    ("CF", "NetCashProvidedByUsedInInvestingActivities"): {
        "stmt": "CF", "tag": "NetCashProvidedByUsedInInvestingActivities", "decision": "excluded", "concept": "",
        "parent_concept": "", "reason_class": "section_total", "caveat": ""},
}


@pytest.mark.integration
def test_library_decides_what_structure_left_open_and_reports_disagreements(store):
    """the library row decides a line the rules left open (Apple's investing total: excluded, section_total); a
    library row that contradicts the company's own structure (a fabricated 'NetIncomeLoss is a component of
    revenue') never overrides the rule and is reported"""
    dis: list = []
    rows, _ = tag_map.company_tag_map(store, _cid(store, "0000320193"), library=LIB, disagreements=dis)
    out = [{**r, **{k: r.get(k) for k in tag_map.COLUMNS}} for r in rows]
    inv = _by(out, "CF", "NetCashProvidedByUsedInInvestingActivities")
    assert inv and all(r["decided_by"] == "library" and r["decision"] == "excluded" for r in inv)
    assert all(r["reason_class"] == "section_total" for r in inv)
    ni = _by(out, "IS", "NetIncomeLoss")
    assert ni and ni[0]["decided_by"] == "rule" and ni[0]["canonical_concept"] == "net_income_resolved"
    assert any(d["tag"] == "NetIncomeLoss" and d["library_decision"] == "component" for d in dis)


def test_load_library_absent_file_is_empty(tmp_path):
    assert tag_map.load_library(tmp_path / "missing.csv") == {}
    p = tmp_path / "lib.csv"
    p.write_text("stmt,tag,decision,concept,parent_concept,reason_class,caveat\nBS,Assets,map,total_assets_resolved,,,\n")
    assert tag_map.load_library(p)[("BS", "Assets")]["concept"] == "total_assets_resolved"


def test_parenthetical_share_count_is_the_fact_but_other_parentheticals_stay_excluded():
    """Tag Expert 2026-11-11: CommonStockSharesOutstanding in the BS parenthetical (and DPS in the EQ parenthetical)
    is the statement fact; any other parenthetical row, and the cover page, stays excluded"""
    rows = [
        {"stmt": "BS", "report": 3, "line": 40, "plabel": "Common stock, shares outstanding", "tag": "CommonStockSharesOutstanding",
         "version": "us-gaap/2024", "custom": False, "abstract": False, "inpth": True},
        {"stmt": "BS", "report": 3, "line": 41, "plabel": "Allowance for doubtful accounts", "tag": "AllowanceForDoubtfulAccountsReceivableCurrent",
         "version": "us-gaap/2024", "custom": False, "abstract": False, "inpth": True},
        {"stmt": "CP", "report": 1, "line": 9, "plabel": "Shares outstanding", "tag": "CommonStockSharesOutstanding",
         "version": "us-gaap/2024", "custom": False, "abstract": False, "inpth": False},
    ]

    class Conn:  # filing_decisions only reads lines (patched) and calls map_filing (patched)
        pass

    import scrooner_pipeline.fsn_store.tag_map as tm

    orig_lines, orig_map, orig_arcs = tm._lines, tm.mapping.map_filing, tm._arcs
    tm._lines = lambda conn, fid: [dict(r) for r in rows]
    tm.mapping.map_filing = lambda *a, **k: {}
    tm._arcs = lambda conn, fid: {}
    try:
        out = tm.filing_decisions(Conn(), 1, {"positional": []}, [], {})
    finally:
        tm._lines, tm.mapping.map_filing, tm._arcs = orig_lines, orig_map, orig_arcs
    shares, allowance, cover = out
    assert shares["disposition"] == "mapped" and shares["concept"] == "shares_outstanding_resolved"
    assert shares["rule_id"] == tm.PARENTHETICAL_RULE
    assert allowance["disposition"] == "excluded" and allowance["reason"] == "cover_or_parenthetical"
    assert cover["disposition"] == "excluded" and cover["reason"] == "cover_or_parenthetical"


def _rec(stmt, tag, label, disposition="mapped", concept="x"):
    return {"stmt": stmt, "report": 2, "line": 1, "plabel": label, "tag": tag, "version": "us-gaap/2024",
            "custom": False, "abstract": False, "inpth": False, "disposition": disposition, "concept": concept,
            "combine_role": None, "sign": None, "reason": None, "rule_id": "r", "decided_by": "library",
            "components": None}


def test_guards_from_the_tag_expert_rulings():
    """Tag Expert 2026-11-11 (4b7392e0): excise/withholding buybacks, impairment/accretion D&A, restricted cash,
    equity including NCI: the label or the statement decides, whatever the library or a rule said"""
    out = [
        _rec("CF", "PaymentsForRepurchaseOfCommonStock", "Repurchases of common stock, including excise tax", concept="share_buybacks_resolved"),
        _rec("CF", "PaymentsForRepurchaseOfCommonStock", "Repurchases of common stock", concept="share_buybacks_resolved"),
        _rec("CF", "DepreciationDepletionAndAmortization", "Depreciation, depletion, amortization and impairments", concept="d"),
        _rec("BS", "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents", "Cash and due from banks", "excluded", None),
    ]
    tag_map.apply_guards(out)
    assert out[0]["disposition"] == "combined" and out[0]["decided_by"] == "guard"
    assert out[1]["disposition"] == "mapped" and out[1]["concept"] == "share_buybacks_resolved"
    assert out[2]["disposition"] == "combined"
    assert out[3]["disposition"] == "mapped" and out[3]["concept"] == "cash_and_equivalents_resolved"


def test_restricted_cash_total_beside_a_cash_line_is_combined():
    out = [
        _rec("BS", "CashAndCashEquivalentsAtCarryingValue", "Cash and cash equivalents", concept="cash_and_equivalents_resolved"),
        _rec("BS", "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents", "Total cash", "excluded", None),
    ]
    tag_map.apply_guards(out)
    assert out[1]["disposition"] == "combined" and out[0]["concept"] == "cash_and_equivalents_resolved"


@pytest.mark.parametrize(
    "others, want",
    [
        ([], ("mapped", "stockholders_equity_resolved")),  # JNJ / AVGO / V: the only equity line
        (["MinorityInterest"], ("excluded", None)),  # NCI printed, no parent line: not presented
        (["StockholdersEquity"], ("excluded", None)),  # beside a parent line: a different total
    ],
)
def test_equity_including_nci(others, want):
    out = [_rec("BS", "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest", "Total equity", "unmapped", None)]
    out += [_rec("BS", t, t) for t in others]
    tag_map.apply_guards(out)
    assert (out[0]["disposition"], out[0]["concept"]) == want


def test_guards_run_inside_the_filing_pass(monkeypatch):
    """without a rule, R2 would make the excise-tax buyback line its own element; the guard in the filing pass makes
    it combined"""
    import scrooner_pipeline.fsn_store.tag_map as tm

    row = {"stmt": "CF", "report": 6, "line": 12, "plabel": "Repurchase of common stock, including excise tax",
           "tag": "PaymentsForRepurchaseOfCommonStock", "version": "us-gaap/2024", "custom": False, "abstract": False,
           "inpth": False}
    monkeypatch.setattr(tm, "_lines", lambda conn, fid: [dict(row)])
    monkeypatch.setattr(tm.mapping, "map_filing", lambda *a, **k: {})
    monkeypatch.setattr(tm, "_arcs", lambda conn, fid: {})
    (rec,) = tm.filing_decisions(None, 1, {"positional": []}, [], {})
    assert rec["disposition"] == "combined" and rec["decided_by"] == "guard"


def test_sums_rule_instant_components_are_never_summable_except_debt():
    """Dhairya 2026-11-12 (fsn-line-to-concept.md sec. Q): a balance-sheet component row would invite a summed
    total; it is emitted as excluded unless the parent is total_debt (durations keep their components)"""
    liab = _rec("BS", "AccruedLiabilitiesCurrent", "Accrued liabilities", "combined", "total_liabilities_resolved")
    debt = _rec("BS", "CommercialPaper", "Commercial paper", "combined", "total_debt_resolved")
    opex = _rec("IS", "SellingGeneralAndAdministrativeExpense", "SG&A", "combined", "operating_income_resolved")
    for r in (liab, debt, opex):
        r["combine_role"] = "component_of"
        r["sign"] = 1
    tag_map.apply_guards([liab, debt, opex])
    assert liab["disposition"] == "excluded" and "never summed" in liab["reason"]
    assert debt["disposition"] == "combined" and opex["disposition"] == "combined"


def test_bank_cash_split_across_bs_lines_takes_the_cf_ending_cash_line():
    """JPM: cash and due from banks plus deposits with banks, no single cash line on the balance sheet; the
    cash-flow statement's printed ending cash line is the cash fact"""
    out = [
        _rec("BS", "CashAndDueFromBanks", "Cash and due from banks", "mapped", "us-gaap:CashAndDueFromBanks"),
        _rec("BS", "InterestBearingDepositsInBanks", "Deposits with banks", "mapped", "us-gaap:InterestBearingDepositsInBanks"),
        _rec("CF", "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents", "Cash and due from banks and deposits with banks at end", "excluded", None),
    ]
    tag_map.apply_guards(out)
    assert out[2]["disposition"] == "mapped" and out[2]["concept"] == "cash_and_equivalents_resolved"
    # a balance sheet that prints its cash line keeps it; the CF identity line stays excluded
    out2 = [
        _rec("BS", "CashAndCashEquivalentsAtCarryingValue", "Cash", "mapped", "cash_and_equivalents_resolved"),
        _rec("CF", "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents", "Cash at end", "excluded", None),
    ]
    tag_map.apply_guards(out2)
    assert out2[1]["disposition"] == "excluded"
