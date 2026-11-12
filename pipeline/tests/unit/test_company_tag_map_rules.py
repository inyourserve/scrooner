"""Calc-tree safety of the tag-map path (pure; Ritwik's three rules, 2026-11-11)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from scrooner_pipeline.mapper.company_tag_map import Fact, MapRow, build_cells

OPEX, ASSETS = 1, 2
INFO = {OPEX: ("opex", "income_statement"), ASSETS: ("assets", "balance_sheet")}
END = date(2020, 12, 31)
ERA = date(2015, 1, 1)


def concept_row(tag, concept=OPEX, stmt="IS"):
    return MapRow("us-gaap", tag, stmt, "concept", concept, None, None, ERA, None)


def comp_row(tag, parent="OperatingExpenses", sign=1, concept=OPEX):
    return MapRow("us-gaap", tag, "IS", "component", None, concept, sign, ERA, None, parent)


def fact(value, fid, filing=10, acc="A-10"):
    return Fact(Decimal(value), fid, END, False, filing, acc)


def run(rows, facts, arcs=None):
    return build_cells(rows, facts, INFO, arcs or {}, {})


def test_rule1_printed_concept_beats_components_of_another_filing():
    rows = [concept_row("OperatingExpenses"), comp_row("OpA"), comp_row("OpB")]
    facts = {
        ("us-gaap", "OperatingExpenses"): {7: fact("30", 1, filing=11, acc="A-11")},
        ("us-gaap", "OpA"): {7: fact("1", 2)},
        ("us-gaap", "OpB"): {7: fact("2", 3)},
    }
    cells, stats = run(rows, facts)
    assert [(c["value"], c["source_fact_ids"]) for c in cells] == [(Decimal("30"), [1])]
    assert stats["held"] == []


def test_rule2_sum_only_direct_children_of_the_calc_parent_in_that_filing():
    rows = [comp_row("OpA"), comp_row("OpB", sign=-1)]
    facts = {("us-gaap", "OpA"): {7: fact("50", 2)}, ("us-gaap", "OpB"): {7: fact("8", 3)}}
    good = {"A-10": {("OperatingExpenses", "OpA"), ("OperatingExpenses", "OpB")}}
    cells, _ = run(rows, facts, good)
    assert [(c["value"], c["source_fact_ids"]) for c in cells] == [(Decimal("42"), [2, 3])]
    deep = {"A-10": {("OperatingExpenses", "OpA"), ("Other", "OpB")}}  # OpB is not a direct child
    cells, stats = run(rows, facts, deep)
    assert cells == [] and stats["held"][0]["reason"] == "component_not_direct_child_of_parent"
    cells, stats = run(rows, facts, {})  # no calc evidence at all: never summed
    assert cells == [] and stats["held"][0]["reason"] == "no_calc_evidence"


def test_rule3_a_component_that_is_an_ancestor_of_another_is_refused():
    rows = [comp_row("OpA"), comp_row("OpB")]
    facts = {("us-gaap", "OpA"): {7: fact("50", 2)}, ("us-gaap", "OpB"): {7: fact("8", 3)}}
    # both are direct children of OperatingExpenses AND OpB sits under OpA (rule 2 alone passes)
    arcs = {"A-10": {("OperatingExpenses", "OpA"), ("OperatingExpenses", "OpB"), ("OpA", "OpB")}}
    cells, stats = run(rows, facts, arcs)
    assert cells == [] and stats["held"][0]["reason"] == "ancestor_in_component_set"


def test_printed_total_must_tie_to_same_filing_components_or_is_held():
    rows = [concept_row("OperatingExpenses"), comp_row("OpA"), comp_row("OpB")]
    arcs = {"A-10": {("OperatingExpenses", "OpA"), ("OperatingExpenses", "OpB")}}

    def facts(b):
        return {
            ("us-gaap", "OperatingExpenses"): {7: fact("100", 1)},
            ("us-gaap", "OpA"): {7: fact("40", 2)},
            ("us-gaap", "OpB"): {7: fact(b, 3)},
        }

    cells, stats = run(rows, facts("60"), arcs)
    assert [c["value"] for c in cells] == [Decimal("100")] and stats["held"] == []
    cells, stats = run(rows, facts("50"), arcs)  # 90 != 100
    assert cells == [] and stats["held"][0]["reason"] == "printed_total_does_not_tie_to_components"


def blank_row(state="not_presented", concept=OPEX, era_to=None):
    return MapRow(None, None, "IS", state, concept, None, None, ERA, era_to, None, "no such line", "tm.not_presented@1")


PERIODS = {
    7: (date(2020, 1, 1), END, "duration"),          # FY
    8: (date(2020, 10, 1), date(2020, 12, 31), "duration"),  # Q
    9: (date(2020, 1, 1), date(2020, 6, 30), "duration"),    # half year: no grain, no blank
    10: (date(2014, 1, 1), date(2014, 12, 31), "duration"),  # before the era
}


def test_tagless_not_presented_row_becomes_reasoned_blanks_per_period_in_era():
    cells, stats = build_cells([blank_row("not_in_template")], {}, INFO, {}, {}, PERIODS)
    assert cells == []
    got = {(b["period_id"], b["grain"], b["state"], b["reason"], b["rule_id"]) for b in stats["blanks"]}
    assert got == {
        (7, "FY", "not_in_template", "no such line", "tm.not_presented@1"),
        (8, "Q", "not_in_template", "no such line", "tm.not_presented@1"),
    }


def test_a_printed_concept_value_beats_the_not_presented_row_and_the_clash_is_reported():
    rows = [blank_row(), concept_row("OperatingExpenses")]
    facts = {("us-gaap", "OperatingExpenses"): {7: fact("30", 1)}}
    cells, stats = build_cells(rows, facts, INFO, {}, {}, PERIODS)
    assert [(c["period_id"], c["value"]) for c in cells] == [(7, Decimal("30"))]
    assert [b["period_id"] for b in stats["blanks"]] == [8]  # only the period with no value is blank
    assert stats["blank_conflicts"] == [{"canonical_concept_id": OPEX, "period_id": 7, "state": "not_presented"}]


def combined_row(canonical=None):
    return MapRow(
        "us-gaap", "AccountsPayableAndAccruedLiabilitiesCurrent", "BS", "combined", canonical, None, None, ERA, None,
        None, "line spans two concepts", "tm.combined@1", ("accounts_payable", "tm_accrued"), "Accounts payable and accrued liabilities",
    )


def test_combined_row_never_feeds_a_concept_only_a_reasoned_blank_per_spanned_concept():
    info = {**INFO, 3: ("accounts_payable", "balance_sheet")}
    periods = {7: (END, END, "instant")}
    facts = {("us-gaap", "AccountsPayableAndAccruedLiabilitiesCurrent"): {7: fact("500", 1)}}
    for canonical in (None, 3):  # even with canonical_concept set the line feeds nothing
        cells, stats = build_cells([combined_row(canonical)], facts, info, {}, {}, periods)
        assert cells == []
        assert [(l["plabel"], l["value"], l["components"], l["source_fact_ids"]) for l in stats["combined_lines"]] == [
            ("Accounts payable and accrued liabilities", Decimal("500"), ["accounts_payable", "tm_accrued"], [1])
        ]
        got = {(b["concept_name"], b["state"], b["reason"], b["rule_id"]) for b in stats["blanks"]}
        assert got == {
            ("accounts_payable", "not_in_template", "shown as the company's combined line 'Accounts payable and accrued liabilities'", "tm.combined@1"),
            ("tm_accrued", "not_in_template", "shown as the company's combined line 'Accounts payable and accrued liabilities'", "tm.combined@1"),
        }


def test_combined_blank_yields_to_a_separately_printed_concept_value():
    info = {**INFO, 3: ("accounts_payable", "balance_sheet")}
    periods = {7: (END, END, "instant")}
    rows = [combined_row(), MapRow("us-gaap", "AccountsPayableCurrent", "BS", "concept", 3, None, None, ERA, None)]
    facts = {
        ("us-gaap", "AccountsPayableAndAccruedLiabilitiesCurrent"): {7: fact("500", 1)},
        ("us-gaap", "AccountsPayableCurrent"): {7: fact("300", 2)},
    }
    cells, stats = build_cells(rows, facts, info, {}, {}, periods)
    assert [(c["canonical_concept_id"], c["value"]) for c in cells] == [(3, Decimal("300"))]
    assert [b["concept_name"] for b in stats["blanks"]] == ["tm_accrued"]


def test_calc_parent_list_of_the_library_files_is_accepted():
    rows = [comp_row("OpA", parent="Foo;OperatingExpenses;Bar"), comp_row("OpB", parent="OperatingExpenses;Baz")]
    facts = {("us-gaap", "OpA"): {7: fact("5", 2)}, ("us-gaap", "OpB"): {7: fact("6", 3)}}
    arcs = {"A-10": {("OperatingExpenses", "OpA"), ("OperatingExpenses", "OpB")}}
    cells, _ = run(rows, facts, arcs)
    assert [c["value"] for c in cells] == [Decimal("11")]


def test_sign_minus_one_on_a_concept_row_and_a_plus_minus_component_pair():
    neg = MapRow("us-gaap", "InterestNet", "IS", "concept", OPEX, None, -1, ERA, None, serve_note="gross shown net")
    cells, _ = run([neg], {("us-gaap", "InterestNet"): {7: fact("40", 1)}})
    assert [(c["value"], c["serve_note"]) for c in cells] == [(Decimal("-40"), "gross shown net")]
    rows = [comp_row("Incurred", parent="InterestExpense", sign=1), comp_row("Capitalized", parent="InterestExpense", sign=-1)]
    facts = {("us-gaap", "Incurred"): {7: fact("50", 2)}, ("us-gaap", "Capitalized"): {7: fact("8", 3)}}
    arcs = {"A-10": {("InterestExpense", "Incurred"), ("InterestExpense", "Capitalized")}}
    cells, _ = run(rows, facts, arcs)
    assert [c["value"] for c in cells] == [Decimal("42")]
    # the printed total (with its sign) must tie to the signed components
    printed = MapRow("us-gaap", "InterestExpense", "IS", "concept", OPEX, None, 1, ERA, None)
    facts[("us-gaap", "InterestExpense")] = {7: fact("42", 4)}
    cells, stats = run(rows + [printed], facts, arcs)
    assert [c["value"] for c in cells] == [Decimal("42")] and stats["held"] == []
    facts[("us-gaap", "InterestExpense")] = {7: fact("58", 4)}  # 50 + 8: the sign was ignored somewhere
    cells, stats = run(rows + [printed], facts, arcs)
    assert cells == [] and stats["held"][0]["reason"] == "printed_total_does_not_tie_to_components"


def test_combined_cash_flow_line_gives_reasoned_blanks_for_duration_periods():
    info = {5: ("share_buybacks", "cash_flow"), 6: ("dividends_paid", "cash_flow")}
    row = MapRow("us-gaap", "PaymentsForDividendsAndRepurchases", "CF", "combined", None, None, 1, ERA, None, None, "one line", "tm.combined@1", ("share_buybacks", "dividends_paid"), "Dividends and repurchases")
    periods = {7: (date(2020, 1, 1), END, "duration")}
    cells, stats = build_cells([row], {("us-gaap", "PaymentsForDividendsAndRepurchases"): {7: fact("9", 1)}}, info, {}, {}, periods)
    assert cells == [] and {(b["concept_name"], b["grain"]) for b in stats["blanks"]} == {("share_buybacks", "FY"), ("dividends_paid", "FY")}


def test_several_concept_rows_latest_filing_wins_never_sum_or_tag_order():
    from datetime import date as d

    q = MapRow("us-gaap", "TagQ", "IS", "concept", OPEX, None, 1, ERA, None)
    k = MapRow("us-gaap", "TagK", "IS", "concept", OPEX, None, 1, ERA, None)

    def f(value, fid, filing, filed):
        return Fact(Decimal(value), fid, END, False, filing, f"A-{filing}", filed)

    facts = {  # the 10-K (later) prints TagK, the earlier 10-Q printed TagQ for the same period
        ("us-gaap", "TagQ"): {7: f("10", 1, 20, d(2021, 2, 1))},
        ("us-gaap", "TagK"): {7: f("12", 2, 21, d(2021, 3, 1))},
    }
    for rows in ([q, k], [k, q]):  # row order must not matter
        cells, stats = run(rows, facts)
        assert [(c["value"], c["source_fact_ids"]) for c in cells] == [(Decimal("12"), [2])] and not stats["held"]
    # both listed tags print different values in the SAME latest filing: a reasoned blank, not a pick
    facts[("us-gaap", "TagQ")] = {7: f("10", 1, 21, d(2021, 3, 1))}
    cells, stats = build_cells([q, k], facts, INFO, {}, {}, {7: (date(2020, 1, 1), END, "duration")})
    assert cells == [] and stats["held"][0]["reason"] == "conflicting_values_in_filing"
    assert [(b["state"], b["reason_code"], b["grain"]) for b in stats["blanks"]] == [("defect", "conflicting_values_in_filing", "FY")]
    facts[("us-gaap", "TagQ")] = {7: f("12", 1, 21, d(2021, 3, 1))}  # same value in the same filing: fine
    cells, _ = run([q, k], facts)
    assert [c["value"] for c in cells] == [Decimal("12")]


def test_one_tag_two_concepts_both_get_the_value_and_eps_is_never_derived():
    info = {**INFO, 8: ("basic_eps_resolved", "income_statement"), 9: ("diluted_eps_resolved", "income_statement")}
    rows = [MapRow("us-gaap", "EarningsPerShareBasicAndDiluted", "IS", "concept", c, None, 1, ERA, None) for c in (8, 9)]
    key = ("us-gaap", "EarningsPerShareBasicAndDiluted")
    cells, _ = build_cells(rows, {key: {7: fact("-1.5", 1)}}, info)
    assert {(c["canonical_concept_id"], c["value"]) for c in cells} == {(8, Decimal("-1.5")), (9, Decimal("-1.5"))}
    derived = Fact(Decimal("-0.4"), 2, END, True, 10, "A-10")
    cells, stats = build_cells(rows, {key: {7: derived}}, info)
    assert cells == [] and stats["derived_eps_skipped"] == 2


STORED = [("Other", "89"), ("LossOnExtinguishment", "-123.9"), ("IssuanceOfStock", "-32.5")]  # AAPL, PODD, TRMB (stored values)


def test_served_value_is_sign_times_the_stored_value_never_the_printed_sign():
    for tag, stored in STORED:
        row = lambda sign: MapRow("us-gaap", tag, "IS", "concept", OPEX, None, sign, ERA, None)
        facts = {("us-gaap", tag): {7: fact(stored, 1)}}
        assert [c["value"] for c in run([row(1)], facts)[0]] == [Decimal(stored)]  # sign +1: exactly as stored
        assert [c["value"] for c in run([row(-1)], facts)[0]] == [-Decimal(stored)]


def test_selection_path_never_takes_an_absolute_value():
    from pathlib import Path

    src = (Path(__file__).resolve().parents[2] / "src/scrooner_pipeline/mapper/company_tag_map.py").read_text()
    code = "\n".join(l for l in src.splitlines() if "abs(total - ref_value)" not in l and "never takes abs()" not in l and 'abs(gp["value"]' not in l and 'abs(eps["value"]' not in l)
    assert "abs(" not in code  # the only abs() is the tie-tolerance difference of two totals
    row = MapRow("us-gaap", "T", "IS", "concept", OPEX, None, 1, ERA, None)
    cells, _ = run([row], {("us-gaap", "T"): {7: fact("-5", 1)}})
    assert [c["value"] for c in cells] == [Decimal("-5")]


def test_unclassified_statement_UN_follows_the_row_and_a_wrong_statement_is_still_refused():
    row = MapRow("us-gaap", "T", "UN", "concept", OPEX, None, 1, ERA, None)  # Revvity-style: the only IS is UN
    cells, stats = run([row], {("us-gaap", "T"): {7: fact("5", 1)}})
    assert [c["value"] for c in cells] == [Decimal("5")] and stats["stmt_mismatch_rows"] == 0
    cf = MapRow("us-gaap", "T", "CF", "concept", OPEX, None, 1, ERA, None)  # an IS concept on the CF stays refused
    cells, stats = run([cf], {("us-gaap", "T"): {7: fact("5", 1)}})
    assert cells == [] and stats["stmt_mismatch_rows"] == 1


def test_d3_no_cross_section_identity_total_minus_other_section_is_refused():
    # liabilities = (liabilities and equity) - (equity): an identity across sections, not a sum of face lines
    rows = [
        comp_row("LiabilitiesAndStockholdersEquity", parent="Root", sign=1),
        comp_row("StockholdersEquity", parent="Root", sign=-1),
    ]
    facts = {
        ("us-gaap", "LiabilitiesAndStockholdersEquity"): {7: fact("1000", 1)},
        ("us-gaap", "StockholdersEquity"): {7: fact("400", 2)},
    }
    arcs = {"A-10": {("LiabilitiesAndStockholdersEquity", "StockholdersEquity")}}
    cells, stats = run(rows, facts, arcs)
    assert cells == [] and stats["held"][0]["reason"] in {"ancestor_in_component_set", "component_not_direct_child_of_parent"}
    # even a total and a line of different sections with no calc relation at all is refused
    cells, stats = run(rows, facts, {"A-10": {("Other", "Thing")}})
    assert cells == [] and stats["held"]


def test_era_is_authoritative_a_row_serves_only_periods_inside_it():
    row = MapRow("us-gaap", "ProfitLoss", "IS", "concept", OPEX, None, 1, date(2021, 1, 1), None)  # AVGO-style: from 2021
    facts = {("us-gaap", "ProfitLoss"): {7: Fact(Decimal("5"), 1, date(2020, 10, 31), False, 10, "A-10"), 8: Fact(Decimal("6"), 2, date(2021, 3, 31), False, 10, "A-10")}}
    cells, _ = run([row], facts)
    assert [(c["period_id"], c["value"]) for c in cells] == [(8, Decimal("6"))]  # the 2020 period is outside the era


OPEX_ID, GP_ID, OI_ID = 11, 12, 13
OPEX_INFO = {OPEX_ID: ("operating_expenses_resolved", "income_statement"), GP_ID: ("gross_profit", "income_statement"), OI_ID: ("operating_income", "income_statement")}


def _opex(gp, a, b, oi):
    rows = [
        MapRow("us-gaap", "GrossProfit", "IS", "concept", GP_ID, None, 1, ERA, None),
        MapRow("us-gaap", "OperatingIncomeLoss", "IS", "concept", OI_ID, None, 1, ERA, None),
        MapRow("us-gaap", "R", "IS", "component", None, OPEX_ID, 1, ERA, None, "OperatingIncomeLoss"),
        MapRow("us-gaap", "G", "IS", "component", None, OPEX_ID, 1, ERA, None, "OperatingIncomeLoss"),
    ]
    facts = {
        ("us-gaap", "GrossProfit"): {7: fact(gp, 1)},
        ("us-gaap", "OperatingIncomeLoss"): {7: fact(oi, 2)},
        ("us-gaap", "R"): {7: fact(a, 3)},
        ("us-gaap", "G"): {7: fact(b, 4)},
    }
    arcs = {"A-10": {("OperatingIncomeLoss", "R"), ("OperatingIncomeLoss", "G")}}
    return build_cells(rows, facts, OPEX_INFO, arcs, {})


def test_opex_components_must_tie_gross_profit_to_operating_income():
    cells, stats = _opex("100", "30", "20", "50")  # 100 - 50 = 50
    assert {c["canonical_concept_id"]: c["value"] for c in cells}[OPEX_ID] == Decimal("50") and stats["held"] == []
    cells, stats = _opex("100", "30", "20", "40")  # 100 - 50 != 40
    assert OPEX_ID not in {c["canonical_concept_id"] for c in cells}
    assert stats["held"][0]["reason"] == "opex_components_do_not_tie_gross_profit_to_operating_income"


def test_seeder_refuses_two_concept_rows_of_one_concept_with_overlapping_eras():
    from scrooner_pipeline.mapper.company_tag_map_seed import check_overlaps

    def row(tag, a, b):
        return {"company_id": 1, "stmt": "IS", "taxonomy": "us-gaap", "tag": tag, "decision": "concept",
                "canonical_concept_id": 5, "parent_concept_id": None, "era_from": date.fromisoformat(a),
                "era_to": date.fromisoformat(b) if b else None}

    assert check_overlaps([row("A", "2015-01-01", "2019-12-31"), row("B", "2020-01-01", None)]) == []  # cut eras
    errs = check_overlaps([row("A", "2015-01-01", "2020-06-30"), row("B", "2020-01-01", None)])
    assert len(errs) == 1 and "two concept rows overlap" in errs[0]


NI = 14
NI_INFO = {NI: ("net_income", "income_statement")}


def _ni_rows(printed: bool):
    rows = [
        MapRow("us-gaap", "ProfitLoss", "IS", "component", None, NI, 1, ERA, None, "IncomeStatementRoot"),
        MapRow("us-gaap", "NetIncomeLossAttributableToNoncontrollingInterest", "IS", "component", None, NI, -1, ERA, None, "IncomeStatementRoot"),
    ]
    if printed:
        rows.append(MapRow("us-gaap", "NetIncomeLoss", "IS", "concept", NI, None, 1, ERA, None))
    return rows


def test_net_income_as_profitloss_minus_nci_only_when_no_attributable_line_is_printed():
    facts = {
        ("us-gaap", "ProfitLoss"): {7: fact("100", 1)},
        ("us-gaap", "NetIncomeLossAttributableToNoncontrollingInterest"): {7: fact("10", 2)},
    }
    arcs = {"A-10": {("IncomeStatementRoot", "ProfitLoss"), ("IncomeStatementRoot", "NetIncomeLossAttributableToNoncontrollingInterest")}}
    cells, _ = build_cells(_ni_rows(False), facts, NI_INFO, arcs, {})
    assert [c["value"] for c in cells] == [Decimal("90")]  # not printed: face components, 100 - 10
    facts[("us-gaap", "NetIncomeLoss")] = {7: fact("90", 3)}
    cells, stats = build_cells(_ni_rows(True), facts, NI_INFO, arcs, {})
    assert [(c["value"], c["source_fact_ids"]) for c in cells] == [(Decimal("90"), [3])] and stats["held"] == []  # printed total wins
    facts[("us-gaap", "NetIncomeLoss")] = {7: fact("85", 3)}  # printed but the components do not tie: held
    cells, stats = build_cells(_ni_rows(True), facts, NI_INFO, arcs, {})
    assert cells == [] and stats["held"][0]["reason"] == "printed_total_does_not_tie_to_components"


def test_winner_tag_gap_is_a_reasoned_blank_never_a_fallback_to_the_alternate():
    win = MapRow("us-gaap", "Revenues", "IS", "concept", OPEX, None, 1, ERA, None)
    alt = MapRow("us-gaap", "RevenueFromContract", "IS", "excluded", None, None, 1, ERA, None,
                 reason="same concept opex served by Revenues in this era", reason_class="alternate_tag_overlapping")
    facts = {("us-gaap", "Revenues"): {7: fact("10", 1)}}
    alts = {("us-gaap", "RevenueFromContract"): {7: fact("11", 2), 8: Fact(Decimal("12"), 3, date(2020, 9, 30), False, 11, "A-11")}}
    periods = {7: (date(2020, 1, 1), END, "duration"), 8: (date(2020, 7, 1), date(2020, 9, 30), "duration")}
    cells, stats = build_cells([win, alt], facts, INFO, {}, {}, periods, alts)
    assert [(c["period_id"], c["value"]) for c in cells] == [(7, Decimal("10"))]  # never the alternate's 11 or 12
    assert [(b["period_id"], b["reason_code"], b["reason"]) for b in stats["blanks"]] == [(8, "no_fact_under_winner_tag", "no fact under Revenues for this period")]


def test_seeder_holds_note_sourced_and_template_out_rows_as_verifier_sample_failed():
    from scrooner_pipeline.mapper.company_tag_map_seed import held_by_verifier

    assert held_by_verifier({"decided_by": "note_sourced"}) and held_by_verifier({"reason_class": "template_out"})
    assert not held_by_verifier({"decided_by": "structure", "reason_class": "detail_of_printed_total"})


def test_two_distinct_values_for_one_tag_and_period_in_the_latest_filing_is_a_blank_not_a_pick():
    row = MapRow("us-gaap", "Revenues", "IS", "concept", OPEX, None, 1, ERA, None)
    amb = Fact(Decimal("10"), 1, END, False, 10, "A-10", None, ambiguous=True)  # PCAR: total row and a segment row
    cells, stats = build_cells([row], {("us-gaap", "Revenues"): {7: amb}}, INFO, {}, {}, {7: (date(2020, 1, 1), END, "duration")})
    assert cells == [] and stats["held"][0]["reason"] == "conflicting_values_in_filing"
    assert [b["reason_code"] for b in stats["blanks"]] == ["conflicting_values_in_filing"]


def test_open_period_rows_load_as_tagless_not_presented_rows(tmp_path):
    from scrooner_pipeline.mapper.company_tag_map_seed import (
        OPEN_PERIOD_REASON, OPEN_PERIOD_RULE_ID, check_overlaps, normalize, read_open_periods,
    )

    f = tmp_path / "open.csv"
    f.write_text('company_id,stmt,concept,period,why\n9,BS,ppe_net_resolved,2020-03-31,"open, not filled"\n')
    (raw,) = read_open_periods(f)
    n = normalize(raw, {}, {"ppe_net_resolved": 77})
    assert (n["decision"], n["tag"], n["taxonomy"], n["canonical_concept_id"], n["stmt"]) == ("not_presented", None, None, 77, "BS")
    assert (n["era_from"], n["era_to"], n["reason"], n["rule_id"]) == (date(2020, 3, 31), date(2020, 3, 31), OPEN_PERIOD_REASON, OPEN_PERIOD_RULE_ID)
    assert check_overlaps([n]) == []


INV, DEBT, CASH = 21, 22, 23
INST_INFO = {INV: ("inventory", "balance_sheet"), DEBT: ("total_debt_resolved", "balance_sheet"), CASH: ("cash_and_equivalents_resolved", "balance_sheet")}


def _bs_comps(parent, a="Raw", b="Wip"):
    rows = [
        MapRow("us-gaap", a, "BS", "component", None, parent, 1, ERA, None, "Root"),
        MapRow("us-gaap", b, "BS", "component", None, parent, 1, ERA, None, "Root"),
    ]
    facts = {("us-gaap", a): {7: fact("5", 1)}, ("us-gaap", b): {7: fact("6", 2)}}
    return rows, facts, {"A-10": {("Root", a), ("Root", b)}}


def test_instant_component_sum_is_refused_except_total_debt():
    rows, facts, arcs = _bs_comps(INV)
    cells, stats = build_cells(rows, facts, INST_INFO, arcs, {})
    assert cells == [] and stats["held"][0]["reason"] == "instant_component_sum_not_allowed"  # inventory pair
    rows, facts, arcs = _bs_comps(DEBT)
    cells, stats = build_cells(rows, facts, INST_INFO, arcs, {})
    assert [c["value"] for c in cells] == [Decimal("11")] and stats["held"] == []  # total debt: founder definition


def test_bank_cash_is_the_cash_flow_ending_line_as_a_concept_row_not_a_balance_sheet_sum():
    row = MapRow("us-gaap", "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents", "CF", "concept", CASH, None, 1, ERA, None, serve_note="cash incl. restricted, as printed")
    cells, stats = build_cells([row], {("us-gaap", row.tag): {7: fact("900", 1)}}, INST_INFO, {}, {})
    assert [(c["value"], c["serve_note"]) for c in cells] == [(Decimal("900"), "cash incl. restricted, as printed")]
    rows, facts, arcs = _bs_comps(CASH, "CashA", "ShortTermInv")  # a BS cash sum is refused
    cells, stats = build_cells(rows, facts, INST_INFO, arcs, {})
    assert cells == [] and stats["held"][0]["reason"] == "instant_component_sum_not_allowed"


SH, EPS, NIID, SO = 31, 32, 33, 34
SCALE_INFO = {
    SH: ("weighted_basic_shares", "income_statement"), EPS: ("basic_eps_resolved", "income_statement"),
    NIID: ("net_income", "income_statement"), SO: ("shares_outstanding_resolved", "balance_sheet"),
}


def _scale_rows():
    return [MapRow("us-gaap", t, "IS", "concept", c, None, 1, ERA, None) for t, c in
            (("WASO", SH), ("Eps", EPS), ("NetIncomeLoss", NIID))]


def _scale(shares, so=None):
    facts = {("us-gaap", "WASO"): {7: fact(shares, 1)}, ("us-gaap", "Eps"): {7: fact("11.5", 2)},
             ("us-gaap", "NetIncomeLoss"): {7: fact("8200000000", 3)}}
    rows = _scale_rows()
    info = dict(SCALE_INFO)
    periods = {7: (date(2020, 1, 1), END, "duration")}
    if so:
        rows.append(MapRow("us-gaap", "SO", "BS", "concept", SO, None, 1, ERA, None))
        facts[("us-gaap", "SO")] = {8: Fact(Decimal(so), 4, END, False, 10, "A-10")}
        periods[8] = (END, END, "instant")
    return build_cells(rows, facts, info, {}, {}, periods)


def test_scale_sanity_blocks_unscaled_weighted_shares_mcd_shape_and_passes_the_scaled_value():
    cells, stats = _scale("713.4")  # MCD: millions tagged unscaled; companyfacts carries the raw value
    assert {c["canonical_concept_id"] for c in cells} == {EPS, NIID}  # EPS and NI stay as served
    (b,) = [b for b in stats["blanks"] if b["reason_code"] == "filer_scale_error"]
    assert b["state"] == "defect" and b["concept_name"] == "weighted_basic_shares" and "713.4" in b["reason"]
    cells, stats = _scale("713400000")  # 11.5 x 713.4M = 8.2B: ties to net income
    assert {c["canonical_concept_id"] for c in cells} == {SH, EPS, NIID} and stats["held"] == []
    cells, stats = _scale("700000000")  # a 2% gap (NCI / preferred / rounding) is not a scale error
    assert SH in {c["canonical_concept_id"] for c in cells}


def test_scale_sanity_blocks_a_share_count_far_below_the_companys_other_share_facts():
    cells, stats = _scale("713400000", so="7134")  # shares outstanding 100000x too small vs the weighted count
    assert SO not in {c["canonical_concept_id"] for c in cells} and SH in {c["canonical_concept_id"] for c in cells}
    assert [b["reason_code"] for b in stats["blanks"]] == ["filer_scale_error"]


def _scaled_rows(scale, decided_by):
    rows = _scale_rows()
    w = rows[0]
    rows[0] = MapRow(w.taxonomy, w.tag, w.stmt, w.decision, w.canonical_concept_id, None, 1, ERA, None, scale=Decimal(scale),
                     decided_by=decided_by, evidence_adsh="0000063908-26-000035", evidence_report=3)
    return rows


def _run_scaled(scale, decided_by, shares="713.4"):
    facts = {("us-gaap", "WASO"): {7: fact(shares, 1)}, ("us-gaap", "Eps"): {7: fact("11.5", 2)},
             ("us-gaap", "NetIncomeLoss"): {7: fact("8200000000", 3)}}
    return build_cells(_scaled_rows(scale, decided_by), facts, dict(SCALE_INFO), {}, {}, {7: (date(2020, 1, 1), END, "duration")})


def test_scale_from_a_company_override_is_applied_in_decimal_with_provenance():
    cells, stats = _run_scaled("1000000", "company_override")  # MCD weighted_basic_shares x1,000,000
    sh = [c for c in cells if c["canonical_concept_id"] == SH][0]
    assert sh["value"] == Decimal("713400000") and isinstance(sh["value"], Decimal)
    assert "scale x1,000,000 from override 0000063908-26-000035 R3" in sh["serve_note"]
    assert stats["held"] == []
    # an explicit override scale is exempt from the sanity block (the override owns the claim)
    cells, stats = _run_scaled("1000", "company_override")
    assert SH in {c["canonical_concept_id"] for c in cells} and stats["held"] == []


def test_scale_from_a_non_override_source_is_ignored_by_the_mapper_and_refused_by_the_seeder():
    from scrooner_pipeline.mapper.company_tag_map_seed import normalize

    cells, stats = _run_scaled("1000000", "library")  # not an override: served unscaled, then the sanity block fires
    assert SH not in {c["canonical_concept_id"] for c in cells}
    assert [b["reason_code"] for b in stats["blanks"]] == ["filer_scale_error"]
    raw = {"company_id": 1, "taxonomy": "us-gaap", "tag": "WASO", "stmt": "IS", "decision": "concept",
           "canonical_concept": "weighted_basic_shares", "era_from": "2015-01-01", "scale": "1000000",
           "decided_by": "library", "rule_id": "tm.r@1", "evidence_adsh": "0000063908-26-000035"}
    import pytest as _pt
    with _pt.raises(ValueError, match="scale .* refused"):
        normalize(raw, {}, {"weighted_basic_shares": 5})
    ok = normalize({**raw, "decided_by": "company_override"}, {}, {"weighted_basic_shares": 5})
    assert ok["scale"] == Decimal("1000000")
    with _pt.raises(ValueError, match="evidence_adsh"):
        normalize({**raw, "decided_by": "company_override", "evidence_adsh": None}, {}, {"weighted_basic_shares": 5})


def test_cash_flow_and_ci_rows_serve_their_catalog_concepts_sbc_da_comprehensive_income():
    info = {41: ("sbc", "income_statement"), 42: ("depreciation_and_amortization_resolved", "income_statement"), 43: ("comprehensive_income", "income_statement")}
    rows = [MapRow("us-gaap", t, st, "concept", c, None, 1, ERA, None) for t, st, c in (("ShareBasedCompensation", "CF", 41), ("DepreciationAndAmortization", "CF", 42), ("ComprehensiveIncomeNetOfTax", "CI", 43))]
    facts = {("us-gaap", r.tag): {7: fact("5", i + 1)} for i, r in enumerate(rows)}
    cells, stats = build_cells(rows, facts, info)
    assert {c["canonical_concept_id"] for c in cells} == {41, 42, 43} and stats["stmt_mismatch_rows"] == 0


def test_eras_in_fsn_month_ends_match_true_52_53_week_period_ends():
    single = MapRow("us-gaap", "T", "IS", "concept", OPEX, None, 1, date(2025, 10, 31), date(2025, 10, 31))  # AMAT-style one-period era
    rng = MapRow("us-gaap", "U", "IS", "concept", 99, None, 1, date(2025, 10, 31), date(2026, 7, 31))
    info = {**INFO, 99: ("other", "income_statement")}
    facts = {("us-gaap", "T"): {7: Fact(Decimal("1"), 1, date(2025, 10, 26), False, 10, "A-10")},
             ("us-gaap", "U"): {8: Fact(Decimal("2"), 2, date(2025, 10, 26), False, 10, "A-10"),
                                9: Fact(Decimal("3"), 3, date(2025, 7, 27), False, 10, "A-10")}}
    cells, _ = build_cells([single, rng], facts, info)
    got = {(c["canonical_concept_id"], c["period_id"]) for c in cells}
    assert (OPEX, 7) in got and (99, 8) in got  # true end 2025-10-26 rounds to the era's 2025-10-31
    assert (99, 9) not in got  # 2025-07-27 rounds to 2025-07-31: before the era


def test_latest_filing_that_has_a_listed_tag_wins_not_a_newer_filing_without_it():
    from datetime import date as d

    a = MapRow("us-gaap", "TagA", "IS", "concept", OPEX, None, 1, ERA, None)
    b = MapRow("us-gaap", "TagB", "IS", "concept", OPEX, None, 1, ERA, None)
    facts = {("us-gaap", "TagA"): {7: Fact(Decimal("5"), 1, END, False, 20, "A-20", d(2021, 2, 1))},
             ("us-gaap", "TagB"): {7: Fact(Decimal("5"), 2, END, False, 21, "A-21", d(2021, 3, 1))}}
    cells, stats = build_cells([a, b], facts, INFO)  # filing 22 (newer) has neither tag: irrelevant
    assert [c["source_fact_ids"] for c in cells] == [[2]] and stats["held"] == []


def test_facts_that_exist_but_none_authoritative_give_a_reasoned_blank_never_a_value():
    row = MapRow("us-gaap", "Assets", "IS", "concept", OPEX, None, 1, ERA, None)
    periods = {7: (date(2020, 1, 1), END, "duration")}
    cells, stats = build_cells([row], {}, INFO, {}, {}, periods, {}, {("us-gaap", "Assets"): {7: 5}})
    assert cells == []
    (b,) = stats["blanks"]
    assert (b["state"], b["reason_code"], b["defect_class"], b["owner"]) == ("defect", "no_authoritative_fact", "ingestion", "data_engineer_l1")
    assert "5 fact(s) under Assets" in b["reason"]


def test_held_status_rows_are_defects_guard_hidden_never_not_presented():
    def st(decision, rc):
        return MapRow(None, None, "IS", decision, OPEX, None, None, ERA, None, None, "status", "tagmap.fy_status@1", reason_class=rc)

    periods = {7: (date(2020, 1, 1), END, "duration")}
    for rc, owner in (("held_c8", "verifier"), ("held_r2", "standardization_lead"), ("held_cover_page", "sector_analyst"), ("held_read_verified_fail_x", "verifier")):
        _, stats = build_cells([st("not_presented", rc)], {}, INFO, {}, {}, periods)
        (b,) = stats["blanks"]
        assert (b["state"], b["defect_class"], b["owner"], b["reason_code"]) == ("defect", "guard_hidden", owner, rc)
    _, stats = build_cells([st("not_in_template", "combined_line")], {}, INFO, {}, {}, periods)
    assert [(b["state"], b["reason_code"]) for b in stats["blanks"]] == [("not_in_template", "combined_line")]


def test_total_debt_components_sum_by_the_founder_definition_without_calc_parents():
    rows = [MapRow("us-gaap", t, "BS", "component", None, DEBT, 1, ERA, None) for t in ("DebtCurrent", "LongTermDebtNoncurrent")]  # no evidence_cal_parent
    facts = {("us-gaap", "DebtCurrent"): {7: fact("999", 1)}, ("us-gaap", "LongTermDebtNoncurrent"): {7: fact("8000", 2)}}
    cells, stats = build_cells(rows, facts, INST_INFO, {}, {})
    assert [c["value"] for c in cells] == [Decimal("8999")] and stats["held"] == []
    # the same set under any other instant concept stays refused
    rows2 = [MapRow("us-gaap", t, "BS", "component", None, INV, 1, ERA, None) for t in ("DebtCurrent", "LongTermDebtNoncurrent")]
    cells, stats = build_cells(rows2, facts, INST_INFO, {}, {})
    assert cells == [] and stats["held"][0]["reason"] == "instant_component_sum_not_allowed"

def test_status_rows_with_a_candidate_marker_still_load():
    # a tagless status row records why the cell is blank; it never serves a value, so it is not held
    from scrooner_pipeline.mapper.company_tag_map_seed import held_by_verifier

    status = {
        "decision": "not_presented",
        "decided_by": "fy_status",
        "rule_id": "tagmap.fy_status@1",
        "reason_class": "held_read_verified_pass_of_note_sourced_candidate",
    }
    candidate = {"decision": "concept", "decided_by": "note_sourced"}
    assert held_by_verifier(status) is False
    assert held_by_verifier(candidate) is True
