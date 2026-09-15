"""AND/OR/NOT support in the rule-based NL parser (2026-09-11), added
once the Screener itself gained `ScreenQuery.where` support
(doc/adr/0001-screener-redis-cache-and-boolean-logic.md)."""

from decimal import Decimal

import pytest

from scrooner_pipeline.ai_query.rules import interpret


@pytest.mark.unit
def test_or_of_two_metric_predicates():
    result = interpret("roe above 30% or debt to equity below 0.5")

    assert result.is_confident, result.explanation
    where = result.query.where
    assert where.op == "or"
    assert {p.metric_name for p in where.predicates} == {"roe", "debt_to_equity"}
    assert result.query.metric_predicates == []


@pytest.mark.unit
def test_or_of_two_categorical_predicates():
    result = interpret("software companies or healthcare companies")

    assert result.is_confident, result.explanation
    where = result.query.where
    assert where.op == "or"
    assert {p.value for p in where.predicates} == {"7372", "Healthcare"}


@pytest.mark.unit
def test_mixing_and_and_or_is_rejected_not_guessed():
    result = interpret("roe above 30% and debt to equity below 0.5 or market cap above 1 billion")

    assert result.query is None
    assert "ambiguous" in result.explanation.lower()


@pytest.mark.unit
def test_top_n_cannot_combine_with_or():
    result = interpret("top 5 by roic or roe above 30%")

    assert result.query is None
    assert "top n" in result.explanation.lower() or "ranking" in result.explanation.lower()


@pytest.mark.unit
def test_trailing_exclusion_wraps_the_rest_in_and_not():
    result = interpret("roe above 20% excluding financials")

    assert result.is_confident, result.explanation
    where = result.query.where
    assert where.op == "and"
    kinds = {getattr(p, "op", None) for p in where.predicates}
    assert "not" in kinds
    not_node = next(p for p in where.predicates if getattr(p, "op", None) == "not")
    assert not_node.predicates[0].value == "Financials"
    metric_node = next(p for p in where.predicates if getattr(p, "op", None) != "not")
    assert metric_node.metric_name == "roe"
    assert metric_node.value == Decimal("0.2")


@pytest.mark.unit
def test_ranked_query_with_exclusion_keeps_ranking_outside_the_tree():
    result = interpret("top 5 by roic excluding financials")

    assert result.is_confident, result.explanation
    assert len(result.query.metric_predicates) == 1
    ranked = result.query.metric_predicates[0]
    assert (ranked.metric_name, ranked.operator, ranked.n) == ("roic", "top_n", 5)
    where = result.query.where
    assert where is not None
    # Exactly one child (the NOT node) since there's no other non-ranked
    # clause to AND it with here.
    assert where.predicates[0].op == "not"


@pytest.mark.unit
def test_exclusion_phrase_that_is_not_a_known_sector_falls_through_to_unrecognized():
    # "penny stocks" isn't a sector this project maps -- must not be
    # silently swallowed as if it were a real, understood exclusion.
    result = interpret("software companies excluding penny stocks")

    assert result.query is None
    assert result.unrecognized


@pytest.mark.unit
def test_plain_and_query_is_unaffected_by_the_new_grammar():
    result = interpret("market cap above 10 billion and roe above 15%")

    assert result.is_confident, result.explanation
    assert result.query.where is None
    assert {p.metric_name for p in result.query.metric_predicates} == {"market_cap", "roe"}
