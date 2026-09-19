import pytest

from scrooner_pipeline.ai_query.llm_interpreter import (
    DisabledLLMInterpreter,
    LLMNotConfiguredError,
    LLMSettings,
    PLACEHOLDER_API_KEY,
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

