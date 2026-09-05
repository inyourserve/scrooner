"""Unit tests for identity.py's 8-K `items` parsing (doc 21/24 Phase 1,
doc 31 section 2 Task 1) -- SEC's own structured event-classification
codes (e.g. "5.02", "2.02,9.01") sitting in raw.sec_submissions'
filings.recent block, parsed into core.filing.items with zero new
fetches. `_parse_filings_block` is pure (no DB), so these test it
directly with real-shaped payload fragments -- no fake cursor needed."""

import pytest

from scrooner_pipeline.normalizer.identity import FORM_ALLOWLIST, _parse_filings_block


@pytest.mark.unit
def test_8k_items_parsed_as_comma_separated_string_verbatim():
    """Real shape confirmed live against AAPL/MSFT submissions.json: `items`
    is a flat array parallel to `form`/`accessionNumber`, holding SEC's own
    comma-separated item codes for 8-K rows (e.g. "5.02" = departure/
    appointment of directors/officers, "2.02" = results of operations)."""
    block = {
        "accessionNumber": ["0000320193-24-000050", "0000320193-24-000051"],
        "form": ["8-K", "8-K"],
        "filingDate": ["2024-05-02", "2024-08-01"],
        "reportDate": ["2024-05-02", "2024-08-01"],
        "items": ["2.02,9.01", "5.02"],
    }

    rows = _parse_filings_block(block)

    assert rows[0]["items"] == "2.02,9.01"
    assert rows[1]["items"] == "5.02"


@pytest.mark.unit
def test_non_8k_forms_with_no_items_key_get_null_not_crash():
    """Most of filings.recent has no `items` field at all (only 8-K
    populates it) -- a 10-K/10-Q block must parse cleanly to items=None,
    never KeyError."""
    block = {
        "accessionNumber": ["0000320193-24-000010"],
        "form": ["10-K"],
        "filingDate": ["2024-11-01"],
        "reportDate": ["2024-09-28"],
        # no "items" key present at all, matching real non-8-K shape
    }

    rows = _parse_filings_block(block)

    assert len(rows) == 1
    assert rows[0]["items"] is None


@pytest.mark.unit
def test_empty_string_item_value_normalized_to_none():
    """An 8-K where EDGAR itself didn't populate items (empty string in the
    array) must come out as None, not an empty string -- so a later `is
    null` check in core.filing behaves as "no items", not "items = ''"."""
    block = {
        "accessionNumber": ["0000320193-24-000099"],
        "form": ["8-K"],
        "filingDate": ["2024-06-01"],
        "reportDate": ["2024-06-01"],
        "items": [""],
    }

    rows = _parse_filings_block(block)

    assert rows[0]["items"] is None


@pytest.mark.unit
def test_items_array_shorter_than_accession_array_falls_back_to_none():
    """A real EDGAR quirk this codebase already guards against for other
    parallel arrays (filingDate/reportDate): `items` can be shorter than
    `accessionNumber` for an older filing. Missing index must fall back to
    None, not IndexError."""
    block = {
        "accessionNumber": ["acc-1", "acc-2"],
        "form": ["8-K", "8-K"],
        "filingDate": ["2024-01-01", "2024-02-01"],
        "reportDate": ["2024-01-01", "2024-02-01"],
        "items": ["1.01"],  # only one entry for two filings
    }

    rows = _parse_filings_block(block)

    assert rows[0]["items"] == "1.01"
    assert rows[1]["items"] is None


@pytest.mark.unit
def test_non_allowlisted_form_dropped_regardless_of_items_value():
    """FORM_ALLOWLIST filtering happens before items are even inspected --
    a form outside the allowlist must never produce a row, whether or not
    it happens to carry an items value."""
    block = {
        "accessionNumber": ["acc-1"],
        "form": ["S-1"],
        "filingDate": ["2024-01-01"],
        "reportDate": ["2024-01-01"],
        "items": ["2.02"],
    }

    rows = _parse_filings_block(block)

    assert rows == []


@pytest.mark.unit
def test_144_424b5_fwp_added_2026_08_29_are_allowlisted():
    """Zero-new-fetch coverage pass: 144 (restricted-stock resale notices),
    424B5 (prospectus supplements), and FWP (free-writing prospectuses)
    confirmed live across the full golden-10 before being added here (942 /
    182 / 23,042 real filings respectively) -- same purely-additive
    widening pattern as every prior FORM_ALLOWLIST addition."""
    assert {"144", "424B5", "FWP"} <= FORM_ALLOWLIST

    block = {
        "accessionNumber": ["acc-1", "acc-2", "acc-3"],
        "form": ["144", "424B5", "FWP"],
        "filingDate": ["2024-01-01", "2024-02-01", "2024-03-01"],
        "reportDate": [None, None, None],
    }

    rows = _parse_filings_block(block)

    assert [r["form"] for r in rows] == ["144", "424B5", "FWP"]
