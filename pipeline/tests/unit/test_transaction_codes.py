import pytest

from scrooner_pipeline.ownership.transaction_codes import (
    GIFT,
    GRANT,
    OPEN_MARKET_BUY,
    OPEN_MARKET_SALE,
    OPTION_EXERCISE,
    OTHER,
    TAX_RELATED_DISPOSAL,
    TRANSACTION_CODE_LABELS,
    classify_transaction_code,
)


@pytest.mark.unit
@pytest.mark.parametrize(
    "code,expected",
    [
        ("P", OPEN_MARKET_BUY),
        ("S", OPEN_MARKET_SALE),
        ("A", GRANT),
        ("M", OPTION_EXERCISE),
        ("X", OPTION_EXERCISE),
        ("O", OPTION_EXERCISE),
        ("G", GIFT),
        ("F", TAX_RELATED_DISPOSAL),
    ],
)
def test_classify_transaction_code_maps_confident_codes_to_doc_categories(code, expected):
    assert classify_transaction_code(code) == expected


@pytest.mark.unit
@pytest.mark.parametrize("code", ["D", "C", "I", "J", "K", "L", "U", "V", "W", "Z", "E", "H"])
def test_classify_transaction_code_never_force_fits_ambiguous_codes(code):
    """These codes are real (seen live in core.insider_transaction) but
    have no unambiguous match among the doc's 6 categories -- must fall
    to "Other", never guessed into a plausible-looking bucket."""
    assert classify_transaction_code(code) == OTHER


@pytest.mark.unit
def test_classify_transaction_code_handles_missing_or_unknown_code():
    assert classify_transaction_code(None) == OTHER
    assert classify_transaction_code("") == OTHER
    assert classify_transaction_code("Q") == OTHER  # not a real SEC code


@pytest.mark.unit
def test_classify_transaction_code_is_case_and_whitespace_insensitive():
    assert classify_transaction_code(" p ") == OPEN_MARKET_BUY
    assert classify_transaction_code("s") == OPEN_MARKET_SALE


@pytest.mark.unit
def test_every_real_observed_code_has_an_entry():
    """Every code confirmed live 2026-08-29 across the full population's
    core.insider_transaction (513,354 rows) has a deliberate entry --
    catches a code silently missing an entry (which would still resolve
    to "Other" via classify_transaction_code's fallback, but should be an
    explicit, reviewed decision, not an accidental omission)."""
    observed_codes = {"S", "A", "F", "M", "P", "J", "G", "D", "C", "L", "X", "I", "W", "Z", "U", "E", "O"}
    assert observed_codes.issubset(TRANSACTION_CODE_LABELS.keys())
