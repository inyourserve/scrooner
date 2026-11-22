"""Optional live-LLM run of the AI query eval set. Never runs in CI.

Opt in with both:
  SCROONER_LLM_EVAL=1
  SCROONER_LLM_CLIENT=module.path:factory   (returns a StructuredLLMClient)
and run: uv run --project pipeline pytest -m live pipeline/tests/unit/test_ai_query_eval_llm_live.py -s

No provider ships in the repo (doc 15: the vendor is the founder's call), so
the client factory is supplied by whoever runs this. Every payload goes through
validate_model_interpretation, the same gate production uses.
Optional SCROONER_LLM_EVAL_MIN_RATE (e.g. 0.95) turns the report into a gate.
"""

import importlib
import os

import pytest
from scrooner_pipeline.ai_query.evaluation import score
from scrooner_pipeline.ai_query.llm_interpreter import FallbackInterpreter


def _client():
    spec = os.getenv("SCROONER_LLM_CLIENT", "")
    module_name, _, attr = spec.partition(":")
    if not module_name or not attr:
        pytest.skip("SCROONER_LLM_CLIENT=module:factory not set")
    return getattr(importlib.import_module(module_name), attr)()


@pytest.mark.live
@pytest.mark.skipif(
    os.getenv("SCROONER_LLM_EVAL") != "1", reason="set SCROONER_LLM_EVAL=1 to run"
)
def test_llm_fallback_eval_set_hit_rate():
    client = _client()
    llm_only = FallbackInterpreter(client, deterministic=lambda text: _unresolved(text))
    with_fallback = FallbackInterpreter(client)
    for name, interpreter in (("llm_only", llm_only), ("fallback", with_fallback)):
        report = score(interpreter.interpret)
        print(f"\n[{name}] " + report.summary())
        for case, cls, got in report.failures:
            print(f"  {case.id} | {case.ask} | {cls} | {got[:120]}")
    leaked = [c.id for c, cls, _ in report.failures if cls.endswith("none_expected")]
    assert not leaked, f"LLM produced a query where none is correct: {leaked}"
    floor = os.getenv("SCROONER_LLM_EVAL_MIN_RATE")
    if floor:
        assert report.hit_rate >= float(floor), report.summary()


def _unresolved(text):
    from scrooner_pipeline.ai_query.interpreter import InterpretationResult

    return InterpretationResult(query=None, explanation="", unrecognized=[text])
