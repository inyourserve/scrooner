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
from scrooner_pipeline.ai_query.normalizer import QueryCorrection


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
    # Recognized clauses may be shown to a user while unresolved clauses are
    # repaired. This field is never executable by itself; `query` remains the
    # sole confidence gate and stays None for partial interpretations.
    recognized_query: ScreenQuery | None = None
    corrections: list[QueryCorrection] = field(default_factory=list)
    # Human-readable descriptions of AND-combined clauses on the same metric
    # whose intervals don't overlap (e.g. "P/E below 10 AND P/E above 20") --
    # doc/scoping/46's CONTRADICTORY_FILTERS case. Always empty unless a real
    # contradiction was found; `query` stays None whenever this is non-empty.
    contradictions: list[str] = field(default_factory=list)

    @property
    def is_confident(self) -> bool:
        return self.query is not None and not self.unrecognized and not self.ambiguous


class NLInterpreter(Protocol):
    def interpret(self, text: str) -> InterpretationResult: ...
