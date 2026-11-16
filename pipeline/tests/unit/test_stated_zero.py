"""Stated zero (ruling 2026-11-16, Dhairya): a zero the filing STATES for the cell's period is a shown 0 with the exact
quote, the accession and a section locator. Never inferred from silence; the quote must speak for the cell's period.
Pure parts (loader validation, coverage attach and display); each assertion is mutation-checked."""

from __future__ import annotations

import csv
from datetime import date

from scrooner_pipeline.mapper import structural_direct as sd
from scrooner_pipeline.mapper import structural_loader as sl
from scrooner_pipeline.mapper import top100_coverage as tc

ACC = "0000064803-23-000009"
COLS = [
    "cik",
    "ticker",
    "data_point",
    "period_end",
    "grain",
    "decision",
    "nodes",
    "value",
    "accession",
    "column",
    "calc_check",
    "flags",
    "resolver_version",
    "quote",
    "locator",
    "quote_period",
]
GOOD = {
    "cik": "0000000301",
    "ticker": "TST",
    "data_point": "dividends_paid",
    "period_end": "2022-12-31",
    "grain": "FY",
    "decision": "mapped",
    "nodes": "",
    "value": "0",
    "accession": ACC,
    "column": "own",
    "calc_check": "",
    "flags": "stated_zero",
    "resolver_version": "r.1",
    "quote": "We did not pay any dividends during fiscal 2022.",
    "locator": "Item 5, Dividends",
    "quote_period": "2022-12-31",
}


def _write(tmp_path, *rows):
    p = tmp_path / "resolver-all110-2026-11-16.csv"
    with p.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    return p


def test_a_quoted_period_matched_zero_is_a_claim_with_no_tag(tmp_path):
    claims, rejects, _ = sl.read_claims(_write(tmp_path, GOOD))
    assert rejects == [] and len(claims) == 1
    c = claims[0]
    assert c.parts == () and c.quote.startswith("We did not pay")
    assert c.locator == "Item 5, Dividends" and c.quote_period == "2022-12-31"
    assert sd.stated_zero_claim_problem(c) is None


def test_a_zero_inferred_from_silence_is_rejected(tmp_path):
    for bad in (
        {**GOOD, "quote": ""},
        {**GOOD, "quote": "   "},
        {**GOOD, "locator": ""},
        {**GOOD, "quote_period": ""},
    ):
        claims, rejects, _ = sl.read_claims(_write(tmp_path, bad))
        assert claims == [] and "stated_zero" in rejects[0]["why"], bad
    claims, rejects, _ = sl.read_claims(_write(tmp_path, {**GOOD, "quote": ""}))
    assert "silence" in rejects[0]["why"]


def test_a_quote_for_another_period_is_rejected(tmp_path):
    claims, rejects, _ = sl.read_claims(
        _write(tmp_path, {**GOOD, "quote_period": "2021-12-31"})
    )
    assert claims == [] and "speaks for 2021-12-31" in rejects[0]["why"]


def test_a_stated_zero_must_be_the_value_zero(tmp_path):
    claims, rejects, _ = sl.read_claims(_write(tmp_path, {**GOOD, "value": "5"}))
    assert claims == [] and "not 0" in rejects[0]["why"]
    claims, rejects, _ = sl.read_claims(_write(tmp_path, {**GOOD, "value": ""}))
    assert claims == [] and "not 0" in rejects[0]["why"]


def test_only_a_mapped_row_flagged_stated_zero_is_one():
    assert sl.is_stated_zero("mapped", "core;stated_zero")
    assert not sl.is_stated_zero("mapped", "core")
    assert not sl.is_stated_zero("not_presented", "stated_zero")


def _cell(**kw):
    base = {
        "ticker": "TST",
        "data_point": "dividends_paid",
        "company_id": 1,
        "period_end": "2022-12-31",
        "class": "DISAGREE",
        "shown_value": "0",
        "_family": tc.STATED_ZERO_FAMILY,
        "accession": "",
        "r_page": "",
        "evidence": "",
    }
    base.update(kw)
    return base


def test_coverage_loads_only_valid_rows_and_shows_the_cell(tmp_path):
    _write(
        tmp_path,
        GOOD,
        {**GOOD, "data_point": "total_debt", "quote": ""},
        {**GOOD, "data_point": "share_buybacks", "quote_period": "2021-12-31"},
    )
    sz = tc.load_stated_zero(tmp_path)
    assert list(sz) == [("TST", "dividends_paid")]
    row = _cell()
    tc.attach_stated_zero([row], sz)
    tc.apply_display([row])
    assert row["display"] == tc.SHOWN_VALUE and row["stated_zero"] == "Y"
    assert row["accession"] == ACC and row["r_page"] == "Item 5, Dividends"
    assert row["evidence"].startswith("We did not pay")
    # no valid resolver row for the data point, a non-zero value, or another family: never promoted
    for other in (
        _cell(data_point="total_debt"),
        _cell(shown_value="3"),
        _cell(_family="company_tag_map:printed_zero"),
    ):
        tc.attach_stated_zero([other], sz)
        assert other.get("stated_zero", "") != "Y" and not other.get("_stated_zero")
