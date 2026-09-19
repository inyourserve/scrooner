"""Provider-neutral boundary for the optional LLM interpretation fallback.

The deterministic interpreter remains production behavior until a provider is
selected and this adapter is explicitly enabled. A placeholder key is treated
as not configured; it can never trigger a network call accidentally.
"""

import os
from dataclasses import dataclass
from typing import Protocol

from scrooner_pipeline.ai_query.interpreter import InterpretationResult


PLACEHOLDER_API_KEY = "replace_with_ai_provider_api_key"


class LLMNotConfiguredError(RuntimeError):
    pass


class StructuredLLMClient(Protocol):
    def interpret(self, text: str, *, current_query: dict | None = None) -> InterpretationResult: ...


@dataclass(frozen=True)
class LLMSettings:
    enabled: bool
    provider: str
    model: str
    api_key: str

    @property
    def configured(self) -> bool:
        return bool(
            self.enabled
            and self.provider
            and self.model
            and self.api_key
            and self.api_key != PLACEHOLDER_API_KEY
        )

    @classmethod
    def from_environment(cls) -> "LLMSettings":
        return cls(
            enabled=os.getenv("SCROONER_LLM_ENABLED", "false").lower() == "true",
            provider=os.getenv("SCROONER_LLM_PROVIDER", ""),
            model=os.getenv("SCROONER_LLM_MODEL", ""),
            api_key=os.getenv("SCROONER_LLM_API_KEY", PLACEHOLDER_API_KEY),
        )


class DisabledLLMInterpreter:
    """Explicit safe state until a concrete provider adapter is approved."""

    def __init__(self, settings: LLMSettings | None = None) -> None:
        self.settings = settings or LLMSettings.from_environment()

    def interpret(self, text: str, *, current_query: dict | None = None) -> InterpretationResult:
        del text, current_query
        raise LLMNotConfiguredError(
            "LLM interpretation is disabled; deterministic interpretation remains available"
        )

