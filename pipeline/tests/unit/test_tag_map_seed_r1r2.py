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


def ap2(fid, stmt, tag, period, plabel, prev="", nxt="", nondim=True):
    return ap(fid, stmt, tag, period, plabel) + (nondim, prev, nxt)


LIB_COR = [("fsn-x.csv", [{"tag": "us-gaap:CostOfRevenue", "home_stmt": "IS", "decision": "map",
                           "concept key": "cost_of_revenue", "evidence": "lib"}])]
OVERLAY_COR = [{"stmt": "IS", "tag": "CostOfRevenue", "decision": "concept", "concept": "cost_of_revenue",
                "condition": "label!~total (costs|operating) and near~cost of (sales|goods|products)",
                "else_reason": "label"}]


def test_shifted_label_is_needs_detail_not_demotion():
    key = ("us-gaap", "CostOfRevenue", "IS")
    # own label says 'total costs' but the row above is 'cost of products': a one-row label shift is possible
    amb = {key: {p: ap2(i, "IS", "CostOfRevenue", p, "Total costs and expenses", prev="Cost of products") for i, p in
                 enumerate(P)}}
    res = expand(LIB_COR, amb, overlay=OVERLAY_COR)[key]
    assert res["rows"] == [] and "ambiguous" in res["needs_detail"][0]["detail_note"]
    clear = {key: {p: ap2(i, "IS", "CostOfRevenue", p, "Total costs and expenses", prev="Revenues", nxt="Operating income")
                   for i, p in enumerate(P)}}
    assert [x[0] for x in spans(expand(LIB_COR, clear, overlay=OVERLAY_COR)[key])] == ["excluded"]
    differs = {key: {p: ap2(i, "IS", "CostOfRevenue", p, "Costs of things") for i, p in enumerate(P)}}
    assert [x[0] for x in spans(expand(LIB_COR, differs, overlay=OVERLAY_COR)[key])] == ["concept"]  # differs != demote


def test_dimensional_only_line_never_becomes_concept():
    key = ("us-gaap", "CostOfRevenue", "IS")
    dim = {key: {p: ap2(i, "IS", "CostOfRevenue", p, "x", nondim=False) for i, p in enumerate(P)}}
    assert expand(LIB_COR, dim)[key]["rows"] == []
    ex = [("fsn-x.csv", [{"tag": "us-gaap:CostOfRevenue", "home_stmt": "IS", "decision": "exclude", "evidence": "e"}])]
    assert [x[0] for x in spans(expand(ex, dim)[key])] == ["excluded"]


CARD = [{"tag": "us-gaap:Assets", "home_stmt": "BS", "decision": "map", "canonical_concept_key": "total_assets",
         "sign_rule": "as filed", "applies_to": "classified balance sheets (828 cos)",
         "exceptions": "HLI label shift (value right), 175 unclassified", "era_from": "2015", "era_to": "",
         "evidence": "card"}]


def test_tag_card_shape_precedence_and_free_text():
    ents = m.parse_source("fsn-balance-sheet-assets.csv", CARD)
    e = ents[0]
    assert e["source"] == "tag-card" and e["concept"] == "total_assets" and e["era"] == (date(2015, 1, 1), None)
    assert e["exceptions"] == [] and e["exceptions_text"] and m.applies(e, 1, set())  # descriptive text applies to all
    lo = m.parse_source("std-tags-rank-1.csv", [{"rank": "1", "tag": "us-gaap:Assets", "statements": "BS",
                                                 "decision": "exclude", "concept": "", "reason": "r"}])
    co_ = m.parse_source("companies-x.csv", [co(1, "BS", "Assets", "map", "assets_x")])
    idx = m.build_index(lo + ents + co_)
    assert [x["source"] for x in idx[("Assets", "BS")]] == ["companies-x.csv", "tag-card", "std-tags-rank-1.csv"]


def un(fid, rep, tag, coreg=False, stmt="UN"):
    return ap(fid, stmt, tag, date(2025, 12, 31)) [:2] + (tag,) + (stmt,) + ap(fid, stmt, tag, date(2025, 12, 31))[4:12] + (rep,) \
        + ap(fid, stmt, tag, date(2025, 12, 31))[13:] + (not coreg, "", "", coreg)


def test_un_statement_effective_role_and_coregistrant_drop():
    rows = [un(1, 4, "NetIncomeLoss"), un(1, 4, "Revenues"),               # real entity IS (Revvity): kept as IS
            un(2, 9, "NetIncomeLoss", coreg=True),                          # subsidiary column: dropped
            un(3, 5, "Assets"), un(3, 2, "NetIncomeLoss", stmt="IS"),       # BS role free; IS already classified
            un(3, 7, "NetIncomeLoss")]                                      # second NI-like UN report: dropped
    out = m.relabel_un(rows)
    assert sorted((r[FID_], r[2], r[3]) for r in out) == [(1, "NetIncomeLoss", "IS"), (1, "Revenues", "IS"),
                                                          (3, "Assets", "BS"), (3, "NetIncomeLoss", "IS")]


FID_ = 5


def test_pld_shaped_coregistrant_lines_never_become_parent_rows():
    # PLD prints the operating partnership's statements in the same filing: its own-only tag has coreg values only
    key_parent, key_sub = ("us-gaap", "Revenues", "IS"), ("us-gaap", "LimitedPartnersCapitalAccountUnitsOutstanding", "IS")
    lib = [("fsn-x.csv", [{"tag": "us-gaap:Revenues", "home_stmt": "IS", "decision": "map", "concept key": "revenue",
                           "evidence": "e"}, {"tag": "us-gaap:LimitedPartnersCapitalAccountUnitsOutstanding",
                                               "home_stmt": "IS", "decision": "map", "concept key": "units", "evidence": "e"}])]
    groups = {key_parent: {p: ap2(i, "IS", "Revenues", p, "x") for i, p in enumerate(P)},
              key_sub: {p: ap2(i, "IS", "LimitedPartnersCapitalAccountUnitsOutstanding", p, "x", nondim=False)
                        for i, p in enumerate(P)}}
    out = expand(lib, groups)
    assert len(out[key_parent]["rows"]) == 1 and out[key_sub]["rows"] == []


def test_eras_of_one_key_never_overlap():
    # a tag that leaves and returns, with an open-ended company row and a tag-level row on the same key
    p = [date(2019, 12, 31), date(2020, 12, 31), date(2021, 12, 31), date(2022, 12, 31)]
    groups = {("us-gaap", "Assets", "BS"): {d: ap(i, "BS", "Assets", d) for i, d in enumerate(p) if i != 1}}
    ents = m.parse_source("fsn-x.csv", CARD) + m.parse_source("companies-x.csv", [co(1, "BS", "Assets", "map", "total_assets")])
    rows = m.expand_company(1, set(), groups, p, m.build_index(ents))[("us-gaap", "Assets", "BS")]["rows"]
    spans_ = sorted((a, b or date.max) for _, a, b, _ in rows)
    assert len(spans_) >= 2 and all(y[0] > x[1] for x, y in zip(spans_, spans_[1:]))


# ---- pass 3: presentation pattern, aliases, rulings, free-text applies_to
def test_applies_to_free_text_with_digits_is_all_not_a_company_id():
    e = m.parse_source("fsn-x.csv", [dict(CARD[0], applies_to='bank "Total interest expense" (WTFC 1,503,981)')])[0]
    assert m.applies(e, 1, set()) and m.applies(e, 503, set())
    e2 = m.parse_source("fsn-x.csv", [dict(CARD[0], applies_to="503;sector:bank")])[0]
    assert m.applies(e2, 503, set()) and not m.applies(e2, 1, set()) and m.applies(e2, 1, {"Bank"})


PRES = [{"tag": "presentation elements: StatementTable, StatementLineItems, *Abstract, *Axis, *Domain, *Member",
         "home_stmt": "BS/IS/CF/EQ", "decision": "excluded", "canonical_concept_key": "", "sign_rule": "none",
         "applies_to": "all", "exceptions": "x", "era_from": "", "era_to": "", "evidence": "AAPL R5 AssetsCurrentAbstract"}]


def pres_row(tag, datatype, abstract, stmt="BS"):
    r = ap2(0, stmt, tag, P[0], "x")
    return r[:4] + (abstract,) + r[5:] + (False, datatype)


def test_presentation_pattern_keys_on_suffix_and_datatype():
    assert m.presentation_match("AssetsAbstract", None, True)
    assert m.presentation_match("StatementTable", None, True)
    assert m.presentation_match("FooAxis", "axis", False)  # non-abstract flag but axis datatype: still structure
    assert m.presentation_match("CustomMember", "member", False)
    assert not m.presentation_match("OddAbstract", "monetary", False)  # suffix alone is not enough
    assert not m.presentation_match("FooAxis", "monetary", False)
    ents = m.parse_source("fsn-balance-sheet-assets.csv", PRES)
    assert ents[0]["kind"] == "pattern" and ents[0]["source"] == "tag-card"
    key = ("us-gaap", "AssetsAbstract", "BS")
    r = (ap2(0, "BS", "AssetsAbstract", P[0], "x")[:4] + (True,) + ap2(0, "BS", "AssetsAbstract", P[0], "x")[5:] + (False, None))
    res = m.expand_company(1, set(), {key: {P[0]: r}}, P, m.build_index(ents))[key]
    (e, *_), = res["rows"]
    assert m.library_row(e)["reason_class"] == "presentation_only" and m.library_row(e)["decision"] == "excluded"


def test_alias_resolution_and_unknown_concepts_listed():
    valid = {"depreciation_and_amortization_resolved", "cash_and_equivalents_resolved"}
    ents = m.parse_source("companies-x.csv", [co(1, "CF", "A", "map", "d_and_a"), co(1, "BS", "B", "map", "cash"),
                                              co(1, "BS", "C", "map", "made_up_key")])
    unknown = m.resolve_concepts(ents, valid)
    assert [e["concept"] for e in ents[:2]] == ["depreciation_and_amortization_resolved", "cash_and_equivalents_resolved"]
    assert list(unknown) == ["made_up_key"]


def test_ruling_ambiguity_goes_to_needs_detail():
    rul = [{"tag": "us-gaap:PaymentsOfDividends", "home_stmt": "CF", "decision": "map", "concept": "dividends_paid_resolved",
            "condition": "amb_label~preferred|noncontrolling", "reason_class": "", "reason": "r"}]
    ents = m.parse_source("rulings_2026-11-12.csv", rul)
    assert ents[0]["source"] == "ruling:dhairya-2026-11-12" and ents[0]["rule_id"] == m.RULE_RULING
    key = ("us-gaap", "PaymentsOfDividends", "CF")
    plain = {key: {P[0]: ap2(0, "CF", "PaymentsOfDividends", P[0], "Dividends paid")}}
    pref = {key: {P[0]: ap2(0, "CF", "PaymentsOfDividends", P[0], "Dividends paid to preferred stockholders")}}
    assert len(m.expand_company(1, set(), plain, P, m.build_index(ents))[key]["rows"]) == 1
    res = m.expand_company(1, set(), pref, P, m.build_index(ents))[key]
    assert res["rows"] == [] and res["needs_detail"]


def test_company_row_with_several_concepts_or_tags():
    rows = [dict(co(1, "IS", "A", "map", "basic_eps;diluted_eps"), tag="us-gaap:A|us-gaap:B"),
            dict(co(1, "IS", "C", "map", "revenue"), tag="us-gaap:X|us-gaap:Y")]
    ents = m.parse_source("companies-x.csv", rows)
    assert [(e["tag"], e["decision"]) for e in ents] == [("A", "needs_detail"), ("B", "needs_detail"), ("X", "concept"), ("Y", "concept")]
    assert "several concepts" in ents[0]["detail_note"]


def test_needs_detail_answers_replace_the_entry_and_combined_members_are_display_only():
    card = [{"tag": "us-gaap:NonoperatingIncomeExpense", "home_stmt": "IS", "decision": "combined",
             "canonical_concept_key": "other_income_expense_net", "applies_to": "all", "evidence": "e"},
            {"tag": "us-gaap:OtherNonoperatingExpense", "home_stmt": "IS", "decision": "component",
             "canonical_concept_key": "other_income_expense_net", "applies_to": "all", "evidence": "e"}]
    ents = m.parse_source("fsn-income-statement.csv", card)
    ents[0]["source"] = ents[1]["source"] = "tag-card"
    ans = [{"source": "tag-card", "tag": "NonoperatingIncomeExpense", "stmt": "IS", "decision": "combined",
            "concept": "other_income_expense_net", "final_decision": "combined", "members": "interest_income:+1 ; x:-1",
            "sign": "", "label_condition": "members only from this filing's own calc", "rule": "", "status": "closed"},
           {"source": "tag-card", "tag": "OtherNonoperatingExpense", "stmt": "IS", "decision": "component",
            "concept": "other_income_expense_net", "final_decision": "component", "members": "", "sign": "-1",
            "label_condition": "", "rule": "debit: subtract", "status": "closed"}]
    assert m.missing_detail(ents[0]) and m.missing_detail(ents[1])
    assert m.apply_answers(ents, ans) == 2
    assert m.missing_detail(ents[0]) is None and m.missing_detail(ents[1]) is None
    row = m.library_row(ents[0])
    assert row["canonical_concept"] == "other_income_expense_net" and row["components"] == "{interest_income:+1,x:-1}"
    assert "own calc" in row["reason"] and m.library_row(ents[1])["combine_sign"] == "-1"


def test_company_overrides_only_filing_checked_and_latest_scope():
    rows = [{"company": "RTX", "cik": "0000101829", "tag": "ReceivablesNetCurrent", "stmt": "BS",
             "concept": "accounts_receivable", "scope": "latest 10-K read era", "status": "FILING-CHECKED",
             "evidence": "read", "note": "n"},
            {"company": "X", "cik": "0000000001", "tag": "Foo", "stmt": "BS", "concept": "goodwill", "scope": "",
             "status": "PENDING", "evidence": "", "note": ""}]
    ents = m.parse_source("company-overrides.csv", rows, {"0000101829": 7, "0000000001": 8})
    assert len(ents) == 1 and ents[0]["company"] == 7 and ents[0]["scope_latest"] and ents[0]["prio"] == 0.3
    key = ("us-gaap", "ReceivablesNetCurrent", "BS")
    p = [date(2018, 12, 31), date(2019, 12, 31), date(2020, 12, 31), date(2021, 12, 31)]
    groups = {key: {d: ap(i, "BS", "ReceivablesNetCurrent", d) for i, d in enumerate(p) if i != 1}}  # gap: two eras
    res = m.expand_company(7, set(), groups, p, m.build_index(ents))[key]
    assert [(a, b) for _, a, b, _ in res["rows"]] == [(p[2], None)]  # latest era only
