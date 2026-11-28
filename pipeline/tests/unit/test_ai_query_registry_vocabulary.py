"""Registry-generated vocabulary, percent normalization, natural ranking and
period growth in the deterministic interpreter (SYSTEMS.md #18)."""

import pytest
from scrooner_pipeline.ai_query.aliases import (
    ALL_METRIC_ALIASES,
    AMBIGUOUS_METRIC_PHRASES,
    DIAGNOSTIC_METRICS,
    METRIC_ALIASES,
    REGISTRY_LABEL_ALIASES,
    registry_label_aliases,
)
from scrooner_pipeline.ai_query.normalizer import normalize_query_text
from scrooner_pipeline.ai_query.rules import interpret
from scrooner_pipeline.metrics.registry import get_registry


def _only_metric(text):
    result = interpret(text)
    assert result.query is not None, result.explanation
    return result.query


@pytest.mark.unit
def test_every_registry_label_resolves_to_its_own_metric():
    for metric_id, metric in get_registry().items():
        if metric_id in DIAGNOSTIC_METRICS:
            continue
        assert ALL_METRIC_ALIASES.get(metric.label.lower()) == metric_id, metric_id


@pytest.mark.unit
def test_diagnostic_metrics_are_never_reachable_by_label():
    assert not set(REGISTRY_LABEL_ALIASES.values()) & DIAGNOSTIC_METRICS
    assert interpret("receivables reconciliation gap above $5 billion").query is None


@pytest.mark.unit
def test_generated_vocabulary_never_overrides_curated_or_guesses_between_metrics():
    # curated wins, ambiguous bare phrases stay ambiguous
    for phrase, metric in METRIC_ALIASES.items():
        assert ALL_METRIC_ALIASES[phrase] == metric
    assert not set(REGISTRY_LABEL_ALIASES) & set(AMBIGUOUS_METRIC_PHRASES)
    # two metrics claiming one phrase: dropped, not picked
    got = registry_label_aliases({"a": "Same thing (x)", "b": "Same thing (y)"}, {})
    assert "same thing" not in got
    assert got["same thing x"] == "a" and got["same thing y"] == "b"


@pytest.mark.unit
def test_percent_word_after_a_number_is_a_unit_elsewhere_it_is_a_name():
    assert normalize_query_text("roe above 20 percent").text == "roe above 20%"
    assert normalize_query_text("capex percent of revenue at most 15%").text == (
        "capex percent of revenue at most 15%"
    )
    predicate = _only_metric("capex percent of revenue at most 15%").metric_predicates[
        0
    ]
    assert predicate.metric_name == "capex_pct_revenue"


@pytest.mark.unit
def test_metric_name_containing_and_or_an_operator_word_is_not_cut():
    q = _only_metric("research and development intensity at most 15%")
    assert q.metric_predicates[0].metric_name == "rnd_intensity"
    q = _only_metric("fcf greater than net income equals 1")
    assert q.metric_predicates[0].metric_name == "fcf_gt_net_income"


@pytest.mark.unit
def test_natural_ranking():
    q = _only_metric("the 10 largest companies by market cap")
    p = q.metric_predicates[0]
    assert (p.metric_name, p.operator, p.n) == ("market_cap", "top_n", 10)
    q = _only_metric("top 5 tech companies by market cap")
    assert q.categorical_predicates[0].value == "Technology"
    assert q.metric_predicates[0].operator == "top_n"
    assert _only_metric("10 cheapest stocks by pe").metric_predicates[0].operator == (
        "bottom_n"
    )
    # "cheapest" is only a direction for a valuation multiple
    assert interpret("10 cheapest stocks by roe").query is None


@pytest.mark.unit
def test_growth_with_a_period_maps_to_a_horizon_that_exists():
    assert (
        _only_metric("eps growth over 3 years above 15%")
        .metric_predicates[0]
        .metric_name
        == "eps_growth_3y_cagr"
    )
    assert (
        _only_metric("revenue grew more than 10% last year")
        .metric_predicates[0]
        .metric_name
        == "revenue_growth_yoy"
    )
    assert interpret("revenue growth over 7 years above 10%").query is None


@pytest.mark.unit
def test_include_missing_is_set_only_for_a_metric_in_the_query():
    q = _only_metric("roe above 15% including companies with no roe")
    assert q.metric_predicates[0].include_missing is True
    assert (
        interpret("roe above 15%, including companies with no dividend yield").query
        is None
    )
    assert _only_metric("roe above 15%").metric_predicates[0].include_missing is False


@pytest.mark.unit
def test_between_combines_with_other_clauses_and_from_to():
    q = _only_metric("roe between 10% and 20% and debt to equity below 1")
    assert {p.metric_name for p in q.metric_predicates} == {"roe", "debt_to_equity"}
    q = _only_metric("pe from 10 to 20")
    assert q.metric_predicates[0].operator == "between"


@pytest.mark.unit
def test_bare_flag_phrase_means_flag_true_only_for_flag_metrics():
    p = _only_metric("debt free companies").metric_predicates[0]
    assert (p.metric_name, str(p.value)) == ("zero_debt", "1")
    assert interpret("roe companies").query is None


@pytest.mark.unit
def test_period_rewrite_leaves_unknown_horizons_untouched():
    from scrooner_pipeline.ai_query.rules import _rewrite_growth_period

    text = "revenue growth over 7 years above 10%"
    assert _rewrite_growth_period(text) == text
    assert _rewrite_growth_period(
        "revenue growth over the last 5 years above 10% a year"
    ) == ("revenue growth 5y cagr above 10%")
