import pytest

from scrooner_pipeline.ai_query.normalizer import normalize_query_text
from scrooner_pipeline.ai_query.rules import interpret


@pytest.mark.unit
def test_safe_metric_and_operator_typos_are_corrected_and_reported():
    result = interpret("companies with retrun on equitiy higher then 20 percent")

    assert result.is_confident
    predicate = result.query.metric_predicates[0]
    assert predicate.metric_name == "roe"
    assert predicate.operator == ">"
    assert str(predicate.value) == "0.2"
    assert [(item.corrected_text, item.kind) for item in result.corrections] == [
        ("return on equity", "metric_spelling"),
        ("higher than", "operator_spelling"),
        ("%", "unit_form"),
    ]


@pytest.mark.unit
@pytest.mark.parametrize(
    "phrase,expected",
    [
        ("roe no more than 20%", "<="),
        ("roe not greater than 20%", "<="),
        ("roe no less than 20%", ">="),
        ("roe not below 20%", ">="),
        ("roe lower than 20%", "<"),
        ("roe higher than 20%", ">"),
    ],
)
def test_natural_comparison_phrases_map_to_exact_operators(phrase, expected):
    result = interpret(phrase)
    assert result.is_confident
    assert result.query.metric_predicates[0].operator == expected


@pytest.mark.unit
def test_normalization_does_not_resolve_semantic_growth_ambiguity():
    result = interpret("revenue growth higher then 10 percent")
    assert result.query is None
    assert result.ambiguous
    assert result.corrections


@pytest.mark.unit
def test_unicode_comparison_symbols_are_meaning_preserving():
    normalized = normalize_query_text("ROE ≥ 20%")
    assert normalized.text == "ROE >= 20%"

