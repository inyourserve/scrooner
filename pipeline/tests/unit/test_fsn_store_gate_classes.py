"""The capex / D&A store gate must FAIL a store value the Verifier-passed lane file does not back
(scripts/slot_records/capex_da_store_gate.py; fsn_store.gate_classes). Before, a later vintage, a quarter the lane
derives differently and a key the lane file lacks all passed (the gate failed open on store-only values)."""

import pytest

from scrooner_pipeline.fsn_store import gate_classes as g

K = ("0000019617", "capex_resolved", "Q", "2015-03-31")


def val(v, acc="A1", state="value"):
    return {"state": state, "value": v, "accession": acc, "reason_code": None}


def row(key, lane, store, derived=None):
    return {"key": key, "class": g.classify(key, lane, store, derived)}


def test_later_vintage_where_the_lane_held_the_original_fails():
    """JPM Q1 2014, AAPL capex FY2016 / FY2017 / Q 2017-12, PLD FY2014: the lane held another filing's blank"""
    r = row(K, val(None, "A1", "held"), val("5", "A2"))
    assert r["class"] == "later_vintage_publishes_where_lane_held_the_original"
    assert g.verdict([r])[0] == "FAIL"


def test_store_print_where_the_lane_derives_differently_fails():
    """PLD Q ending 2014-09-30: no lane printed row, the lane's derived quarter differs from the store's print"""
    r = row(K, None, val("5"), val("7", state="derived"))
    assert r["class"] == "store_print_where_lane_derives_differently"
    assert g.verdict([r])[0] == "FAIL"


def test_store_value_for_a_key_the_lane_file_does_not_have_fails():
    r = row(K, None, val("5"))
    assert r["class"] == "store_value_key_not_in_lane"
    assert g.verdict([r])[0] == "FAIL"


def test_every_failing_class_is_in_the_failing_set():
    for c in (
        "later_vintage_publishes_where_lane_held_the_original",
        "store_print_where_lane_derives_differently",
        "store_value_key_not_in_lane",
        "store_value_lane_held",
        "value_differs",
        "store_conflicting_values_in_filing",
    ):
        assert g.verdict([{"key": K, "class": c}])[0] == "FAIL", c


def test_keys_the_lane_explains_pass():
    rows = [
        row(K, val("5"), val("5")),  # same value
        row(K, val("5"), None),  # lane value, store blank: not a store-only value (reported, separate class)
        row(K, None, val("5"), val("5", state="derived")),  # equals the lane's own derived quarter
        row(("0000019617", "capex_resolved", "FY", "2012-12-31"), None, val("5")),  # before the lane window
        row(K, None, None),
    ]
    assert [r["class"] for r in rows] == [
        "same_value", "lane_value_store_blank", "store_print_equals_lane_derived_quarter",
        "store_key_before_lane_window", "both_blank",
    ]
    assert g.verdict(rows) == ("PASS", {})


def test_a_verifier_cleared_key_passes_and_an_uncleared_one_still_fails():
    a, b = row(K, None, val("5")), row(("0000019617", "capex_resolved", "Q", "2015-06-30"), None, val("6"))
    assert g.verdict([a, b], {K}) == ("FAIL", {"store_value_key_not_in_lane": 1})
    assert g.verdict([a], {K}) == ("PASS", {})


@pytest.mark.parametrize("cls", sorted(g.FAIL_CLASSES))
def test_each_failing_class_names_why_it_is_not_evidence(cls):
    assert g.FAIL_CLASSES[cls]
