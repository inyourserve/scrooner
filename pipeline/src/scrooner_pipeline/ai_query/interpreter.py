"""Stage 6a -- Interpreter interface (doc 15). The contract every NL
interpreter implements, rule-based (6b) or a real LLM later (6c, not built
here -- the vendor decision is the user's, not assumed). `query` is only
ever populated when nothing was left unrecognized or ambiguous -- a
partial, silently-incomplete ScreenQuery is exactly the "invented field" /
"silent reinterpretation" failure mode doc 03's release gates rule out.
"""

from dataclasses import dataclass, field
from typing import Protocol

from scrooner_pipeline.screener.schema import ScreenQuery


@dataclass
class AmbiguityNote:
    phrase: str
    candidates: list[str]


@dataclass
class InterpretationResult:
    query: ScreenQuery | None
    explanation: str
    unrecognized: list[str] = field(default_factory=list)
    ambiguous: list[AmbiguityNote] = field(default_factory=list)

    @property
    def is_confident(self) -> bool:
        return self.query is not None and not self.unrecognized and not self.ambiguous


class NLInterpreter(Protocol):
    def interpret(self, text: str) -> InterpretationResult: ...
