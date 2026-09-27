import pytest

from scrooner_pipeline.ai_query.llm_interpreter import (
    DisabledLLMInterpreter,
    InvalidLLMInterpretationError,
    LLMNotConfiguredError,
    LLMSettings,
    MetricCandidate,
    PLACEHOLDER_API_KEY,
    validate_model_interpretation,
)


@pytest.mark.unit
def test_placeholder_key_is_never_considered_configured():
    settings = LLMSettings(
        enabled=True,
        provider="future-provider",
        model="future-model",
        api_key=PLACEHOLDER_API_KEY,
    )
    assert settings.configured is False


@pytest.mark.unit
def test_disabled_adapter_fails_closed_without_affecting_deterministic_parser():
    adapter = DisabledLLMInterpreter(
        LLMSettings(False, "", "", PLACEHOLDER_API_KEY)
    )
    with pytest.raises(LLMNotConfiguredError, match="deterministic interpretation remains available"):
        adapter.interpret("some unresolved request")


def _candidate(metric_name: str, *operators: str) -> MetricCandidate:
    return MetricCandidate(metric_name, frozenset(operators))


@pytest.mark.unit
def test_validated_model_query_preserves_exact_decimal_and_becomes_executable():
    result = validate_model_interpretation(
        {
            "status": "ready",
            "query": {
                "metric_predicates": [
                    {"metric_name": "roe", "operator": ">", "value": "0.2000000000000000001"}
                ]
            },
            "explanation": "ROE above 20%.",
            "unrecognized": [],
            "ambiguous": [],
        },
        candidates=[_candidate("roe", ">", ">=")],
    )

    assert result.is_confident is True
    assert str(result.query.metric_predicates[0].value) == "0.2000000000000000001"


@pytest.mark.unit
def test_model_cannot_invent_metric_inside_boolean_tree():
    with pytest.raises(InvalidLLMInterpretationError, match="candidate allow-list"):
        validate_model_interpretation(
            {
                "status": "ready",
                "query": {
                    "where": {
                        "op": "or",
                        "predicates": [
                            {"metric_name": "roe", "operator": ">", "value": "0.2"},
                            {"metric_name": "secret_alpha", "operator": ">", "value": "1"},
                        ],
                    }
                },
                "explanation": "A boolean screen.",
                "unrecognized": [],
                "ambiguous": [],
            },
            candidates=[_candidate("roe", ">")],
        )


@pytest.mark.unit
def test_model_cannot_use_operator_not_allowed_for_candidate():
    with pytest.raises(InvalidLLMInterpretationError, match="unsupported operator"):
        validate_model_interpretation(
            {
                "status": "ready",
                "query": {
                    "metric_predicates": [
                        {"metric_name": "market_cap", "operator": "top_n", "n": 25}
                    ]
                },
                "explanation": "Top companies.",
                "unrecognized": [],
                "ambiguous": [],
            },
            candidates=[_candidate("market_cap", ">", "<")],
        )


@pytest.mark.unit
def test_unresolved_model_output_can_never_include_executable_query():
    with pytest.raises(InvalidLLMInterpretationError, match="interpretation schema"):
        validate_model_interpretation(
            {
                "status": "needs_clarification",
                "query": {"metric_predicates": []},
                "explanation": "Choose a revenue-growth period.",
                "unrecognized": [],
                "ambiguous": [
                    {
                        "phrase": "revenue growth",
                        "candidates": ["revenue_growth_yoy", "revenue_growth_3y_cagr"],
                    }
                ],
            },
            candidates=[],
        )


@pytest.mark.unit
def test_unknown_model_fields_are_rejected():
    with pytest.raises(InvalidLLMInterpretationError, match="interpretation schema"):
        validate_model_interpretation(
            {
                "status": "unsupported",
                "query": None,
                "explanation": "Unsupported request.",
                "unrecognized": ["predict tomorrow's price"],
                "ambiguous": [],
                "sql": "select * from secrets",
            },
            candidates=[],
        )


@pytest.mark.unit
def test_unknown_fields_nested_inside_screen_query_are_rejected():
    with pytest.raises(InvalidLLMInterpretationError, match="unknown fields at query"):
        validate_model_interpretation(
            {
                "status": "ready",
                "query": {"metric_predicates": [], "sql": "select * from secrets"},
                "explanation": "Empty screen.",
                "unrecognized": [],
                "ambiguous": [],
            },
            candidates=[],
        )


@pytest.mark.unit
def test_empty_ready_query_is_rejected_instead_of_screening_every_company():
    with pytest.raises(InvalidLLMInterpretationError, match="no filtering or ranking criteria"):
        validate_model_interpretation(
            {
                "status": "ready",
                "query": {"metric_predicates": []},
                "explanation": "All companies.",
                "unrecognized": [],
                "ambiguous": [],
            },
            candidates=[],
        )
