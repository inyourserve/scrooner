import pytest

from scrooner_pipeline.ownership.beneficial_ownership import _extract_cusip


@pytest.mark.unit
class TestExtractCusip:
    # The three originally-documented real formats (module docstring) --
    # regression-checked so the new spaced-format fallback below can
    # never silently break these.
    def test_number_before_label(self) -> None:
        assert _extract_cusip("037833100 (CUSIP Number)") == "037833100"

    def test_number_before_label_with_dashed_filler(self) -> None:
        assert _extract_cusip("037833100 -------- (CUSIP Number)") == "037833100"

    def test_number_after_label(self) -> None:
        assert _extract_cusip("CUSIP Number: 037833100") == "037833100"

    # Found live 2026-09-15 investigating why real companies (ADT Inc.,
    # Global Business Travel Group) had a matched 13G filing but no
    # extractable CUSIP: some filer templates typeset the CUSIP's own
    # 6+2+1 character grouping with whitespace between the groups
    # instead of writing it contiguously. Checked against two real,
    # unrelated filings' actual raw text before trusting this as a
    # real, recurring pattern.
    def test_spaced_grouping_real_adt_filing(self) -> None:
        html = '<TD STYLE="width: 100%">CUSIP No.&nbsp;00090Q 10 3</TD>'
        assert _extract_cusip(html) == "00090Q103"

    def test_spaced_grouping_real_gbtg_filing(self) -> None:
        html = '<FONT>CUSIP No.&nbsp;37890B 10 0</FONT>'
        assert _extract_cusip(html) == "37890B100"

    def test_no_cusip_mention_returns_none(self) -> None:
        assert _extract_cusip("no relevant text here at all") is None

    def test_cusip_label_present_but_no_candidate_token_returns_none(self) -> None:
        # "CUSIP" appears, but nothing nearby looks like a real 9-char
        # token (contiguous or spaced) with at least one digit.
        assert _extract_cusip("Schedule 13G CUSIP Number section follows below") is None
