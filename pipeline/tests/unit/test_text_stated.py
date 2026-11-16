"""Text stated (Dhairya 2026-11-16): a NONZERO value the filing states in its text (MCK R&D, Item 1) is served with no
fact id, the quote and locator in the serve note. Same rejections as stated_zero; a zero belongs under stated_zero."""

from __future__ import annotations

from decimal import Decimal

from scrooner_pipeline.mapper import structural_direct as sd
from scrooner_pipeline.mapper import structural_loader as sl
from scrooner_pipeline.mapper import top100_coverage as tc
from tests.unit.test_stated_zero import ACC, GOOD, _cell, _write

TS = {
    **GOOD,
    "data_point": "research_and_development",
    "flags": "text_stated",
    "value": "74000000",
    "quote": "R&D expenses were $74 million during 2021.",
    "locator": "Item 1 Business, Research and Development, p.13",
}


def test_a_quoted_period_matched_nonzero_is_a_claim(tmp_path):
    claims, rejects, _ = sl.read_claims(_write(tmp_path, TS))
    assert rejects == [] and len(claims) == 1
    c = claims[0]
    assert c.parts == () and c.value == "74000000" and c.quote.startswith("R&D")
    assert sl.is_text_stated(c.decision, c.flags)
    assert not sl.is_stated_zero(c.decision, c.flags)
    assert sd.stated_zero_claim_problem(c) is None


def test_silence_period_mismatch_and_zero_value_are_rejected(tmp_path):
    for bad, word in (
        ({**TS, "quote": ""}, "silence"),
        ({**TS, "locator": ""}, "locator"),
        ({**TS, "quote_period": "2020-12-31"}, "speaks for 2020-12-31"),
        ({**TS, "value": "0"}, "stated_zero"),
        ({**TS, "value": ""}, "no value"),
    ):
        claims, rejects, _ = sl.read_claims(_write(tmp_path, bad))
        assert claims == [] and word in rejects[0]["why"], bad
        assert rejects[0]["why"].startswith("text_stated"), bad


def test_a_stated_zero_still_needs_a_zero(tmp_path):
    claims, rejects, _ = sl.read_claims(_write(tmp_path, {**GOOD, "value": "5"}))
    assert claims == [] and "not 0" in rejects[0]["why"]


def test_coverage_shows_a_text_stated_cell_with_the_same_value_only(tmp_path):
    _write(tmp_path, TS)
    sz = tc.load_stated_zero(tmp_path)
    row = _cell(
        data_point="research_and_development",
        shown_value="74000000",
        _family=tc.TEXT_STATED_FAMILY,
    )
    tc.attach_stated_zero([row], sz)
    tc.apply_display([row])
    assert row["display"] == tc.SHOWN_VALUE and row["text_stated"] == "Y"
    assert row.get("stated_zero", "") != "Y"
    assert row["accession"] == ACC and row["r_page"].startswith("Item 1")
    assert row["evidence"].startswith("R&D expenses")
    # another value, or the stated_zero family on a text_stated row, is never promoted
    for other in (
        _cell(
            data_point="research_and_development",
            shown_value="75000000",
            _family=tc.TEXT_STATED_FAMILY,
        ),
        _cell(
            data_point="research_and_development",
            shown_value="74000000",
            _family=tc.STATED_ZERO_FAMILY,
        ),
    ):
        tc.attach_stated_zero([other], sz)
        assert not other.get("_stated_zero")
    rec = sz[("TST", "research_and_development")]["2022-12-31"]
    assert rec[4] == Decimal("74000000")
