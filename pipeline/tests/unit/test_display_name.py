"""Unit tests for company_master/display_name.py -- cleaning up EDGAR's
raw "/XX/" state-of-incorporation / "/NEW" disambiguation suffixes for
display, e.g. "COSTCO WHOLESALE CORP /NEW", "TUCOWS INC /PA/"."""

from unittest.mock import patch

from scrooner_pipeline.company_master.display_name import resolve_display_name, strip_edgar_suffix


def test_strip_suffix_with_leading_space():
    assert strip_edgar_suffix("CSP INC /MA/") == "CSP INC"


def test_strip_suffix_no_leading_space():
    assert strip_edgar_suffix("ITG, Inc./DE/") == "ITG, Inc."


def test_strip_suffix_new_marker():
    assert strip_edgar_suffix("ONEOK INC /NEW/") == "ONEOK INC"


def test_strip_suffix_no_trailing_slash():
    assert strip_edgar_suffix("SOME CORP /DE") == "SOME CORP"


def test_strip_suffix_leaves_clean_name_untouched():
    assert strip_edgar_suffix("APPLE INC") == "APPLE INC"


def test_strip_suffix_long_legal_name():
    assert (
        strip_edgar_suffix("ZIONS BANCORPORATION, NATIONAL ASSOCIATION /UT/")
        == "ZIONS BANCORPORATION, NATIONAL ASSOCIATION"
    )


def test_resolve_prefers_yfinance_when_available():
    with patch(
        "scrooner_pipeline.company_master.display_name._yfinance_name", return_value="Costco Wholesale Corporation"
    ):
        name, source = resolve_display_name("COST", "COSTCO WHOLESALE CORP /NEW", paced=False)
    assert name == "Costco Wholesale Corporation"
    assert source == "yfinance"


def test_resolve_falls_back_to_openfigi_when_yfinance_has_nothing():
    with patch("scrooner_pipeline.company_master.display_name._yfinance_name", return_value=None), patch(
        "scrooner_pipeline.company_master.display_name._openfigi_name", return_value="TUCOWS INC-CLASS A"
    ):
        name, source = resolve_display_name("TCX", "TUCOWS INC /PA/", paced=False)
    assert name == "TUCOWS INC-CLASS A"
    assert source == "openfigi"


def test_resolve_falls_back_to_suffix_strip_when_both_external_sources_fail():
    with patch("scrooner_pipeline.company_master.display_name._yfinance_name", return_value=None), patch(
        "scrooner_pipeline.company_master.display_name._openfigi_name", return_value=None
    ):
        name, source = resolve_display_name("XXXX", "SOME OBSCURE CO /DE/", paced=False)
    assert name == "SOME OBSCURE CO"
    assert source == "suffix_stripped"


def test_resolve_with_no_ticker_goes_straight_to_suffix_strip():
    name, source = resolve_display_name(None, "SOME CORP /MA/", paced=False)
    assert name == "SOME CORP"
    assert source == "suffix_stripped"
