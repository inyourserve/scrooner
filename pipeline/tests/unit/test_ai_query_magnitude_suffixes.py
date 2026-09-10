"""Magnitude-suffix number parsing (2026-09-10), added alongside widening
the Screener's catalog to price-dependent metrics -- market_cap and
friends are always huge numbers, and no real investor types the full
zero-padded figure."""

from decimal import Decimal

import pytest

from scrooner_pipeline.ai_query.rules import interpret


@pytest.mark.unit
@pytest.mark.parametrize("text,expected_value", [
    ("market cap above 500 billion", Decimal("500000000000")),
    ("market cap above 500billion", Decimal("500000000000")),
    ("market cap above 500B", Decimal("500000000000")),
    ("market cap above 500bn", Decimal("500000000000")),
    ("market cap above $500 billion", Decimal("500000000000")),
    ("market cap above 1 trillion", Decimal("1000000000000")),
    ("market cap above 1T", Decimal("1000000000000")),
    ("market cap above 50 million", Decimal("50000000")),
    ("market cap above 50M", Decimal("50000000")),
    ("market cap above 500 thousand", Decimal("500000")),
    ("market cap above 500K", Decimal("500000")),
    ("market cap above 1.5 billion", Decimal("1500000000")),
    ("market cap above 500,000,000,000", Decimal("500000000000")),
])
def test_magnitude_suffixes_parse_to_the_correct_number(text, expected_value):
    result = interpret(text)

    assert result.is_confident, result.explanation
    predicate = result.query.metric_predicates[0]
    assert predicate.metric_name == "market_cap"
    assert predicate.value == expected_value


@pytest.mark.unit
def test_magnitude_suffix_works_on_both_sides_of_a_between_clause():
    result = interpret("market cap between 100 billion and 500 billion")

    assert result.is_confident, result.explanation
    predicate = result.query.metric_predicates[0]
    assert predicate.operator == "between"
    assert predicate.value_range == (Decimal("100000000000"), Decimal("500000000000"))


@pytest.mark.unit
def test_percentage_metrics_are_unaffected_by_the_new_suffix_grammar():
    result = interpret("roe above 30%")

    assert result.is_confident, result.explanation
    predicate = result.query.metric_predicates[0]
    assert predicate.metric_name == "roe"
    assert predicate.value == Decimal("0.3")
