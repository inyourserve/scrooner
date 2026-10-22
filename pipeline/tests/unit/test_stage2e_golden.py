"""Flag-OFF byte-identical golden for Stage 2e: with every rule off (and in dry_run
mode) the current module reproduces the pre-W3 Stage 2e (commit e271b9c) over a
2,697-fact corpus (tests/fixtures/golden/make_stage2e_golden.py regenerates it)."""

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

from scrooner_pipeline.common import rule_flags as rf
from scrooner_pipeline.normalizer import dedupe

GOLDEN = Path(__file__).resolve().parents[1] / "fixtures" / "golden"


def _golden_module():
    spec = importlib.util.spec_from_file_location(
        "make_stage2e_golden", GOLDEN / "make_stage2e_golden.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _stored():
    stored = json.loads((GOLDEN / "stage2e_flags_off.json").read_text())
    return stored, stored.pop("sha256")


@pytest.mark.unit
def test_flags_off_is_byte_identical_to_the_pre_w3_stage_2e(monkeypatch):
    for var in (rf.ENV_ENABLED, rf.ENV_DRYRUN):
        monkeypatch.delenv(var, raising=False)
    stored, sha = _stored()
    assert (
        hashlib.sha256(json.dumps(stored, sort_keys=True).encode()).hexdigest() == sha
    )  # not edited by hand
    assert _golden_module().run(dedupe, legacy=False) == stored


@pytest.mark.unit
def test_dry_run_mode_writes_exactly_what_off_writes(monkeypatch):
    stored, _ = _stored()
    monkeypatch.setenv(
        rf.ENV_DRYRUN, "source.periodic_form_only@1,dedupe.matching_copies@1"
    )
    assert _golden_module().run(dedupe, legacy=False) == stored


@pytest.mark.unit
def test_flags_on_differs_from_the_golden(monkeypatch):
    stored, _ = _stored()
    monkeypatch.setenv(rf.ENV_ENABLED, "source.periodic_form_only@1")
    assert (
        _golden_module().run(dedupe, legacy=False) != stored
    )  # a flag that is always off would fail here
