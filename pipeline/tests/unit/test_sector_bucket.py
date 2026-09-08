"""Regression tests for company_master/sector_bucket.py's SIC 6770/7389
carve-outs and the SIC 7389 Financials override -- see the module's own
inline comments (found live 2026-09-06) for the evidence behind each."""

from scrooner_pipeline.company_master.sector_bucket import classify_sector


def test_blank_checks_carved_out_of_real_estate():
    assert classify_sector("6770") == ("Other", "sic_range:6770-6770")


def test_surrounding_real_estate_range_unaffected():
    assert classify_sector("6700") == ("Real Estate", "sic_range:6700-6799")
    assert classify_sector("6798") == ("Real Estate", "sic_range:6700-6799")


def test_business_services_nec_carved_out_of_industrials():
    assert classify_sector("7389") == ("Other", "sic_range:7389-7389")


def test_surrounding_industrials_range_unaffected():
    assert classify_sector("7380") == ("Industrials", "sic_range:7380-7799")


def test_sic_7389_financials_override_wins_over_carve_out():
    # Visa -- SIC 7389 on its own resolves to "Other", but the curated
    # per-CIK override (a real, yfinance-informed Credit Services cluster)
    # takes priority.
    assert classify_sector("7389", cik="0001403161") == ("Financials", "sic_7389_financials_override")


def test_override_cik_wins_even_with_a_different_sic_code():
    # The override is keyed on identity (CIK), not on a SIC condition --
    # confirms it isn't accidentally scoped to sic_code == "7389" only.
    assert classify_sector("9999", cik="0001403161") == ("Financials", "sic_7389_financials_override")


def test_unrelated_company_not_swept_into_override():
    assert classify_sector("7389", cik="0000000001") == ("Other", "sic_range:7389-7389")


def test_existing_carve_out_still_correct():
    # Nike -- pre-existing carve-out, must survive unrelated edits to the table.
    assert classify_sector("3021") == ("Consumer Discretionary", "sic_range:3021-3021")
