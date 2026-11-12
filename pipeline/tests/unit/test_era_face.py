"""Era split by the printed face line of each period's own filing (Dhairya's guard 2026-11-12)."""

import importlib.util
from pathlib import Path

_p = Path(__file__).resolve().parents[2] / "scripts" / "tag_library" / "era_face.py"
_spec = importlib.util.spec_from_file_location("era_face", _p)
era_face = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(era_face)
ORDER = ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax"]


def test_a_period_whose_face_carries_only_the_alternate_is_served_by_the_alternate():
    filings = {1: ("2019-03-31", "2019-05-01"), 2: ("2019-06-30", "2019-08-01"), 3: ("2019-09-30", "2019-11-01")}
    face = {1: {"Revenues"}, 2: {"RevenueFromContractWithCustomerExcludingAssessedTax"}, 3: {"Revenues"}}
    runs, open_p = era_face.face_runs(filings, face, ORDER)
    assert runs == [("Revenues", "2019-03-31", "2019-03-31"),
                    ("RevenueFromContractWithCustomerExcludingAssessedTax", "2019-06-30", "2019-06-30"),
                    ("Revenues", "2019-09-30", "2019-09-30")]
    assert open_p == []


def test_a_period_whose_face_prints_neither_tag_is_open_and_breaks_the_run():
    filings = {1: ("2019-03-31", "a"), 2: ("2019-06-30", "b"), 3: ("2019-09-30", "c")}
    face = {1: {"Revenues"}, 3: {"Revenues"}}
    runs, open_p = era_face.face_runs(filings, face, ORDER)
    assert runs == [("Revenues", "2019-03-31", "2019-03-31"), ("Revenues", "2019-09-30", "2019-09-30")]
    assert open_p == ["2019-06-30"]


def test_both_tags_on_one_face_follow_the_priority():
    runs, _ = era_face.face_runs({1: ("2019-03-31", "a")}, {1: set(ORDER)}, ORDER)
    assert runs == [("Revenues", "2019-03-31", "2019-03-31")]


def test_the_periods_own_latest_filing_decides_even_when_an_older_filing_printed_the_tag():
    filings = {1: ("2019-03-31", "2019-05-01"), 2: ("2019-03-31", "2019-12-01"), 3: ("2019-06-30", "2019-08-01")}
    face = {1: {"Revenues"}, 3: {"Revenues"}}  # filing 2 (the latest copy of 2019-03-31) prints neither
    runs, open_p = era_face.face_runs(filings, face, ORDER)
    assert open_p == ["2019-03-31"]
    assert runs == [("Revenues", "2019-06-30", "2019-06-30")]
