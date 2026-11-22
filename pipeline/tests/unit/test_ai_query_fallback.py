"""FallbackInterpreter: the LLM (doc 15 stage 6c) is wired behind the
NLInterpreter contract, deterministic first, fail closed."""

from decimal import Decimal

import pytest
from scrooner_pipeline.ai_query.llm_interpreter import (
    FallbackInterpreter,
    MetricCandidate,
    interpret,
)
from scrooner_pipeline.ai_query.rules import interpret as rules_interpret

CANDIDATES = [MetricCandidate("roe", frozenset({">", "<"}))]


class FakeClient:
    def __init__(self, payload):
        self.payload = payload
        self.calls = 0

    def propose(self, text, *, candidates, current_query=None):
        self.calls += 1
        return self.payload


def _ready(metric="roe", value="0.2"):
    return {
        "status": "ready",
        "query": {
            "metric_predicates": [
                {"metric_name": metric, "operator": ">", "value": value}
            ]
        },
        "explanation": "roe above 20%",
        "unrecognized": [],
        "ambiguous": [],
    }


def _interp(client):
    return FallbackInterpreter(client, candidates=lambda: CANDIDATES)


@pytest.mark.unit
def test_default_entry_point_is_the_deterministic_interpreter():
    for text in (
        "roe above 15%",
        "what stocks should I buy",
        "revenue growth above 5%",
    ):
        assert interpret(text).query == rules_interpret(text).query


@pytest.mark.unit
def test_confident_deterministic_parse_never_calls_the_llm():
    client = FakeClient(_ready(value="0.9"))
    result = _interp(client).interpret("roe above 15%")
    assert client.calls == 0
    assert result.query.metric_predicates[0].value == Decimal("0.15")


@pytest.mark.unit
def test_contradiction_is_not_sent_to_the_llm():
    client = FakeClient(_ready())
    result = _interp(client).interpret("roe below 10% and roe above 20%")
    assert client.calls == 0 and result.query is None and result.contradictions


@pytest.mark.unit
def test_unrecognized_phrase_uses_validated_llm_query():
    client = FakeClient(_ready())
    result = _interp(client).interpret("companies earning a lot on equity, 20%+")
    assert client.calls == 1
    assert result.is_confident
    assert result.query.metric_predicates[0].value == Decimal("0.2")
    assert result.query.metric_predicates[0].include_missing is False


@pytest.mark.unit
def test_llm_metric_outside_allow_list_fails_closed_to_deterministic():
    client = FakeClient(_ready(metric="secret_alpha"))
    result = _interp(client).interpret("what stocks should I buy")
    assert client.calls == 1 and result.query is None


@pytest.mark.unit
def test_llm_refusal_keeps_the_deterministic_refusal():
    payload = {
        "status": "unsupported",
        "query": None,
        "explanation": "stock picks are not a screen",
        "unrecognized": ["what stocks should I buy"],
        "ambiguous": [],
    }
    result = _interp(FakeClient(payload)).interpret("what stocks should I buy")
    assert result.query is None
