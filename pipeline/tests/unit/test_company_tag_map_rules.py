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
