"""Decision loader for analytics.company_tag_map: precedence, applies_to, exceptions, off-home statement."""

import importlib.util
from datetime import date
from pathlib import Path

PATH = Path(__file__).resolve().parents[2] / "scripts" / "tag_map_seed_r1r2.py"
spec = importlib.util.spec_from_file_location("tag_map_seed", PATH)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

ERA = [(date(2014, 12, 31), None)]
LIB = [  # fsn library fixture, header spelling deliberately mixed
    {"Tag": "us-gaap:Assets", "Home Stmt": "BS", "Decision": "concept", "Concept Key": "total_assets", "sign": "",
     "applies_to": "all", "exceptions": "", "era": "", "evidence": "BS total"},
    {"Tag": "us-gaap:AssetsAbstract", "Home Stmt": "BS", "Decision": "excluded", "Concept Key": "presentation_only",
     "applies_to": "all", "exceptions": "", "era": "", "evidence": "abstract"},
    {"Tag": "us-gaap:Revenues", "Home Stmt": "IS", "Decision": "concept", "Concept Key": "revenue",
     "applies_to": "sector:bank;77", "exceptions": "", "era": "", "evidence": "bank revenue"},
    {"Tag": "us-gaap:Liabilities", "Home Stmt": "BS", "Decision": "concept", "Concept Key": "total_liabilities",
     "applies_to": "all", "exceptions": "9;5@2020-01-01..2021-12-31", "era": "", "evidence": "x"},
]
STD = [{"rank": "1", "tag": "us-gaap:Goodwill", "statements": "BS/CF", "decision": "component", "concept": "x",
        "reason": "r"},
       {"rank": "2", "tag": "us-gaap:Foo", "statements": "BS", "decision": "review", "concept": "", "reason": "r"}]
COMP = [{"company_id": "5", "ticker": "T", "stmt": "BS", "tag": "us-gaap:Assets", "decision": "exclude", "concept": "",
         "era_from": "2001", "era_to": "", "n_filings": "1", "reason": "co"},
        {"company_id": "5", "ticker": "T", "stmt": "BS", "tag": "us-gaap:Foo", "decision": "map", "concept": "foo",
         "era_from": "", "era_to": "", "n_filings": "1", "reason": "co"},
        {"company_id": "5", "ticker": "T", "stmt": "IS", "tag": "", "decision": "not_presented",
         "concept": "gross_profit", "era_from": "", "era_to": "", "n_filings": "1", "reason": "none"}]


def index():
    ents = (m.parse_source("fsn-test.csv", LIB) + m.parse_source("std-tags-rank-1.csv", STD)
            + m.parse_source("companies-x.csv", COMP))
    return m.build_index(ents), ents


def ap(fid, stmt, tag, period, plabel="x"):
    """An appearance tuple as APPEAR_SQL returns it."""
    return (1, "us-gaap", tag, stmt, False, fid, "adsh%d" % fid, period, "10-K", False, period.year, None, 1, 1,
            plabel, 9)


def run(cid, tax, tag, stmt, templates=(), eras=ERA, extra=None, entries=None):
    """Expand one key over filings starting 2014-03-31 (eras given as the single open era of ERA)."""
    idx = index()[0] if entries is None else m.build_index(entries)
    periods = [date(y, 12, 31) for y in range(2014, 2024)]
    groups = {(tax, tag, stmt): {p: ap(i, stmt, tag, p) for i, p in enumerate(periods)}}
    groups.update(extra or {})
    return m.expand_company(cid, set(templates), groups, periods, idx)[(tax, tag, stmt)]


def test_concept_row_and_decision_normalised():
    r = run(1, "us-gaap", "Assets", "BS")["rows"]
    assert len(r) == 1 and r[0][0]["decision"] == "concept" and m.library_row(r[0][0])["canonical_concept"] == "total_assets"


def test_excluded_presentation_tag_from_library():
    (e, *_), = run(1, "us-gaap", "AssetsAbstract", "BS")["rows"]
    row = m.library_row(e)
    assert row["decision"] == "excluded" and row["reason_class"] == "tag_exclude"


def test_off_home_statement_gives_no_row():
    assert run(1, "us-gaap", "Assets", "CF")["rows"] == []


def test_applies_to_sector_and_company_list():
    assert run(1, "us-gaap", "Revenues", "IS", templates=["Bank"])["rows"]  # sector name, case-insensitive
    assert run(77, "us-gaap", "Revenues", "IS")["rows"]  # company id list
    assert run(1, "us-gaap", "Revenues", "IS", templates=["industrial"])["rows"] == []


def test_exceptions_company_and_era():
    assert run(9, "us-gaap", "Liabilities", "BS")["rows"] == []  # company exception
    rows = run(5, "us-gaap", "Liabilities", "BS")["rows"]  # era exception cuts 2020-2021 out
    assert [(a, b) for _, a, b, _ in rows] == [(date(2014, 12, 31), date(2019, 12, 31)), (date(2022, 1, 1), None)]
    assert len(run(1, "us-gaap", "Liabilities", "BS")["rows"]) == 1


def test_company_row_overrides_tag_row_and_review_blocks():
    res = run(5, "us-gaap", "Assets", "BS")
    assert res["override"]
    decs = [(e["source"], a, b) for e, a, b, _ in res["rows"]]
    assert ("companies-x.csv", date(2020, 1, 1), None) in decs  # era_from 2001 = Jan 2020 (YYMM), open end
    assert any(s == "companies-x.csv" for s, _, _ in decs) and any(s == "fsn-test.csv" for s, _, _ in decs)
    assert [(a, b) for s, a, b in decs if s == "fsn-test.csv"] == [(date(2014, 12, 31), date(2019, 12, 31))]
    r2 = run(1, "us-gaap", "Foo", "BS")  # review loads nothing
    assert r2["rows"] == [] and r2["review"]
    r3 = run(5, "us-gaap", "Foo", "BS")  # company map beats tag-level review
    assert [e["source"] for e, *_ in r3["rows"]] == ["companies-x.csv"]


def test_component_without_sign_is_needs_detail_not_guessed():
    res = run(1, "us-gaap", "Goodwill", "BS")
    assert res["rows"] == [] and res["needs_detail"] and "sign" in m.missing_detail(res["needs_detail"][0])


def test_concept_level_company_row_is_not_a_tag_row():
    _, ents = index()
    assert [e["kind"] for e in ents if e["tag"] == "" ] == ["company_concept"]


def test_eras_split_only_when_tag_leaves_and_returns():
    p = [date(2019, 12, 31), date(2020, 12, 31), date(2021, 12, 31), date(2022, 12, 31)]
    app = {p[0]: "a", p[1]: "b", p[3]: "d"}
    eras = m.build_eras(app, p)
    assert [(a, b) for a, b, _ in eras] == [(p[0], p[1]), (p[3], None)]
    assert [(a, b) for a, b, _ in m.build_eras({p[0]: 1, p[1]: 2}, p)] == [(p[0], None)]
    assert m.build_eras({date(2013, 12, 31): 1}, p) == []


def test_ci_only_filing_counts_as_income_statement():
    f = lambda fid, stmt: (1, "us-gaap", "NetIncomeLoss", stmt, False, fid, "a", date(2015, 3, 31), "10-Q", False, 2015, None, 1, 1, "p", 9)
    out = m.relabel_ci([f(10, "CI"), f(11, "IS"), f(11, "CI")])
    assert [r[3] for r in out] == ["IS", "IS", "CI"]


# ---- per-filing conditions (Ritwik library traps 2026-11-11)
P = [date(y, 12, 31) for y in range(2014, 2020)]


def co(cid, stmt, tag, dec, concept, **kw):
    r = {"company_id": str(cid), "ticker": "T", "stmt": stmt, "tag": "us-gaap:" + tag, "decision": dec,
         "concept": concept, "era_from": "", "era_to": "", "n_filings": "1", "reason": kw.get("reason", "r")}
    return r


def expand(entries_rows, groups, cid=1, overlay=()):
    ents = []
    for src, rows in entries_rows:
        ents += m.parse_source(src, rows)
    m.attach_conditions(ents, list(overlay))
    return m.expand_company(cid, set(), groups, P, m.build_index(ents))


def g(stmt, tag, present, label="x"):
    return {("us-gaap", tag, stmt): {p: ap(i, stmt, tag, p, label) for i, p in enumerate(P) if i in present}}


def spans(res):
    return [(e["decision"], e["reason"], a, b) for e, a, b, _ in res["rows"]]


def test_conditional_exclusion_copresent_splits_eras():  # MCD: restaurant acquisitions beside PP&E capex
    lib = [("fsn-x.csv", [{"tag": "us-gaap:PaymentsToAcquireProductiveAssets", "home_stmt": "CF",
                           "decision": "map", "concept key": "capex", "evidence": "lib"}]),
           ("companies-x.csv", [co(683, "CF", "PaymentsToAcquireProductiveAssets", "exclude", "capex")])]
    overlay = [{"company_id": "683", "stmt": "CF", "tag": "PaymentsToAcquireProductiveAssets", "decision": "excluded",
                "condition": "copresent:PaymentsToAcquirePropertyPlantAndEquipment", "reason": "beside PP&E capex"}]
    groups = g("CF", "PaymentsToAcquireProductiveAssets", range(6))
    groups.update(g("CF", "PaymentsToAcquirePropertyPlantAndEquipment", {1, 2}))  # printed only in 2015, 2016
    res = expand(lib, groups, cid=683, overlay=overlay)[("us-gaap", "PaymentsToAcquireProductiveAssets", "CF")]
    got = sorted(spans(res), key=lambda x: x[2])
    assert got[0][:2] == ("concept", "lib") and got[0][2:] == (P[0], date(2015, 12, 30))  # cut where the exclusion starts
    assert got[1] == ("excluded", "beside PP&E capex", P[1], P[2])
    assert got[2][:2] == ("concept", "lib") and got[2][2] == date(2017, 1, 1)
    # without the overlay the exclusion would cover every filing: the condition is what splits
    res0 = expand(lib, groups, cid=683)[("us-gaap", "PaymentsToAcquireProductiveAssets", "CF")]
    assert [x[0] for x in spans(res0)] == ["excluded"]


def test_label_condition_with_else_excluded():  # BA/LMT: cost_of_revenue only on the cost-of-sales line
    lib = [("fsn-x.csv", [{"tag": "us-gaap:CostOfRevenue", "home_stmt": "IS", "decision": "map",
                           "concept key": "cost_of_revenue", "evidence": "lib"}])]
    overlay = [{"stmt": "IS", "tag": "CostOfRevenue", "decision": "concept", "concept": "cost_of_revenue",
                "condition": "label!~total (costs|operating)", "else_reason": "label: total costs line"}]
    key = ("us-gaap", "CostOfRevenue", "IS")
    sales = expand(lib, g("IS", "CostOfRevenue", range(6), "Total cost of sales"), overlay=overlay)[key]
    assert [x[0] for x in spans(sales)] == ["concept"]
    tot = expand(lib, g("IS", "CostOfRevenue", range(6), "Total costs and expenses"), overlay=overlay)[key]
    assert [(x[0], x[1]) for x in spans(tot)] == [("excluded", "label: total costs line")]


def test_printed_total_beats_components():  # VZ/TMUS: components only where no total prints
    comp = {"company_id": "1", "ticker": "V", "stmt": "IS", "tag": "us-gaap:CostOfServices + us-gaap:CostOfGoodsSold",
            "decision": "component", "concept": "cost_of_revenue", "era_from": "", "era_to": "", "n_filings": "3",
            "reason": "sum of the two"}
    lib = [("fsn-x.csv", [{"tag": "us-gaap:CostOfRevenue", "home_stmt": "IS", "decision": "map",
                           "concept key": "cost_of_revenue", "evidence": "total"}]),
           ("companies-x.csv", [comp])]
    groups = {}
    groups.update(g("IS", "CostOfServices", range(6)))
    groups.update(g("IS", "CostOfGoodsSold", range(6)))
    groups.update(g("IS", "CostOfRevenue", {2, 3}))  # a total prints in 2016, 2017 only
    out = expand(lib, groups)
    for t in ("CostOfServices", "CostOfGoodsSold"):
        rows = out[("us-gaap", t, "IS")]["rows"]
        assert [(e["decision"], e["combine_sign"] if "combine_sign" in e else e["sign"], a, b) for e, a, b, _ in rows] == [
            ("component", "+1", P[0], P[1]), ("component", "+1", P[4], None)]
        assert m.library_row(rows[0][0])["parent_concept"] == "cost_of_revenue"
    assert len(out[("us-gaap", "CostOfRevenue", "IS")]["rows"]) == 1


def test_component_sign_ruling_only_for_sums_else_needs_detail():
    nee = [{"company_id": "1", "ticker": "N", "stmt": "CF", "tag": "c:X", "decision": "component", "concept": "capex",
            "era_from": "", "era_to": "", "n_filings": "1", "reason": "capex = A + B"},
           {"company_id": "1", "ticker": "N", "stmt": "CF", "tag": "c:Y", "decision": "component", "concept": "capex",
            "era_from": "", "era_to": "", "n_filings": "1", "reason": "other"}]
    ents = m.parse_source("companies-x.csv", nee)
    assert [e["sign"] for e in ents] == ["+1", ""] and m.missing_detail(ents[1]) == "sign"


def test_ranks_file_rows_are_company_specific_and_blank_means_undecided():
    base = {"company_id": "1", "cik": "c", "taxonomy": "us-gaap", "stmt": "BS", "evidence_adsh": "a",
            "canonical_concept": "", "parent_concept": "", "combine_sign": "", "components": "", "reason_class": "",
            "reason": "", "era_from": "2015-03-31", "era_to": "2026-09-30", "decided_by": "library"}
    rows = [dict(base, tag="Assets", decision="concept", canonical_concept="total_assets"),
            dict(base, tag="Foo", decision=""),
            dict(base, tag="Bar", decision="component", parent_concept="sga_expense", combine_sign="1"),
            dict(base, tag="Baz", decision="combined", components="a;b")]
    ents = m.parse_source("ranks_1_50.csv", rows)
    assert [e["decision"] for e in ents] == ["concept", "review", "component", "combined"]
    assert ents[0]["source"] == "ranks_1_50.csv:library" and ents[0]["rule_id"] == m.RULE_COMPANY
    assert m.missing_detail(ents[2]) is None and m.missing_detail(ents[3]) == "member tags / concept"
