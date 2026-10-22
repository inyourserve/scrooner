"""The ONE flag module (common/rule_flags.py), the flag-OFF golden and the
workflow dispatch plumbing."""

import hashlib
import importlib.util
import json
import re
from pathlib import Path

import pytest

from scrooner_pipeline.common import rule_flags as rf
from scrooner_pipeline.normalizer import dedupe

ROOT = Path(__file__).resolve().parents[3]
GOLDEN = Path(__file__).resolve().parents[1] / "fixtures" / "golden"


def _golden_module():
    spec = importlib.util.spec_from_file_location("make_stage2e_golden", GOLDEN / "make_stage2e_golden.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ------------------------------------------------------------------ the module
@pytest.mark.unit
def test_default_is_off_for_every_registered_rule():
    for rule_id in rf.RULES:
        assert rf.rule_mode(rule_id, {}) == rf.OFF
        assert not rf.rule_enabled(rule_id, {}) and not rf.rule_dry_run(rule_id, {})


@pytest.mark.unit
def test_lane2_and_lane3_ids_do_not_crash_lane1_stages():
    env = {rf.ENV_ENABLED: "ttm.age_guard@1, ttm.age_guard@2 mcap.share_basis_guard@1", rf.ENV_DRYRUN: "ttm.consecutive_window@1"}
    # the incident: a dispatch naming another lane's rule used to raise in lane-1 code
    assert rf.rule_enabled(rf.RULE_PERIODIC_FORM_ONLY, env) is False
    assert rf.rule_mode("ttm.age_guard@1", env) == rf.ON
    assert rf.rule_mode("ttm.consecutive_window@1", env) == rf.DRY_RUN


@pytest.mark.unit
def test_every_rule_of_the_three_lanes_named_by_the_chief_is_registered():
    needed = {
        "ttm.consecutive_window@1", "ttm.age_guard@1", "ttm.age_guard@2", "pershare.balance_sheet_date_anchor@1",  # lane 2
        "employee_count.no_yfinance_tier@1", "debt.total_debt_consistency@1", "revenue.total_disagreement@1",  # lane 3
        "oi.derived_not_face@1", "mcap.share_basis_guard@1", "scale.unit_plausibility@1", "currency.non_usd_price_ratio@1",
        "source.periodic_form_only@1", "dedupe.matching_copies@1", "entity.shared_accession_primary_filer@1",  # lane 1
        "identity.cik_name_ticker@1",
    }
    assert needed <= set(rf.RULES)
    assert all(re.match(rf.RULE_ID_PATTERN, r) for r in rf.RULES)


@pytest.mark.unit
def test_typos_and_ambiguity_stop_the_run():
    with pytest.raises(ValueError, match="unregistered"):
        rf.enabled_rules({rf.ENV_ENABLED: "ttm.age_gaurd@1"})
    with pytest.raises(ValueError, match="malformed"):
        rf.enabled_rules({rf.ENV_DRYRUN: "no version"})
    with pytest.raises(ValueError, match="both"):
        rf.rule_mode("ttm.age_guard@1", {rf.ENV_ENABLED: "ttm.age_guard@1", rf.ENV_DRYRUN: "ttm.age_guard@1"})
    with pytest.raises(ValueError):
        rf.rule_mode("made.up@1", {})


@pytest.mark.unit
def test_dry_run_is_off_for_a_rule_without_a_dry_run_path():
    env = {rf.ENV_DRYRUN: "entity.shared_accession_primary_filer@1,source.periodic_form_only@1"}
    assert rf.rule_mode("entity.shared_accession_primary_filer@1", env) == rf.OFF
    assert rf.rule_mode("source.periodic_form_only@1", env) == rf.DRY_RUN


@pytest.mark.unit
def test_dispatch_text_round_trip():
    assert rf.env_lines("") == [] and rf.env_lines(None) == []
    lines = rf.env_lines("on:ttm.age_guard@1,source.periodic_form_only@1 dry_run:dedupe.matching_copies@1")
    assert lines == [
        "SCROONER_RULES_ENABLED=source.periodic_form_only@1,ttm.age_guard@1",
        "SCROONER_RULES_DRYRUN=dedupe.matching_copies@1",
    ]
    for bad in ("ttm.age_guard@1", "yes:ttm.age_guard@1", "on:ttm.age_guard@1 dry_run:ttm.age_guard@1", "on:nope@1"):
        with pytest.raises(ValueError):
            rf.env_lines(bad)
    assert rf.main(["--dispatch", "on:nope@1"]) == 2


# ------------------------------------------------------------------ OFF golden
@pytest.mark.unit
def test_flags_off_is_byte_identical_to_the_pre_w3_stage_2e(monkeypatch):
    for var in (rf.ENV_ENABLED, rf.ENV_DRYRUN):
        monkeypatch.delenv(var, raising=False)
    g = _golden_module()
    stored = json.loads((GOLDEN / "stage2e_flags_off.json").read_text())
    sha = stored.pop("sha256")
    assert hashlib.sha256(json.dumps(stored, sort_keys=True).encode()).hexdigest() == sha  # golden not edited by hand
    assert g.run(dedupe, legacy=False) == stored


@pytest.mark.unit
def test_dry_run_mode_writes_exactly_what_off_writes(monkeypatch):
    g = _golden_module()
    stored = json.loads((GOLDEN / "stage2e_flags_off.json").read_text())
    stored.pop("sha256")
    monkeypatch.setenv(rf.ENV_DRYRUN, "source.periodic_form_only@1,dedupe.matching_copies@1")
    assert g.run(dedupe, legacy=False) == stored


@pytest.mark.unit
def test_flags_on_differs_from_the_golden(monkeypatch):
    g = _golden_module()
    stored = json.loads((GOLDEN / "stage2e_flags_off.json").read_text())
    stored.pop("sha256")
    monkeypatch.setenv(rf.ENV_ENABLED, "source.periodic_form_only@1")
    assert g.run(dedupe, legacy=False) != stored  # the golden would catch a flag that is always off


@pytest.mark.unit
def test_adjust_payload_returns_the_same_object_when_off(monkeypatch):
    from scrooner_pipeline.normalizer import registrant_loader as rl

    monkeypatch.delenv(rf.ENV_ENABLED, raising=False)
    payload = {"facts": {}}
    assert rl.adjust_payload(None, "0000065984", payload, lambda c: None) is payload


# ---------------------------------------------------------------- the workflow
WF = ROOT / ".github" / "workflows" / "pipeline-recompute.yml"


@pytest.mark.unit
def test_recompute_workflow_has_the_rules_input_and_validates_it_in_every_job():
    text = WF.read_text()
    assert re.search(r"^      rules:\n        description: .*\n        default: \"\"", text, re.M)
    # every job that syncs the environment (all five) resolves the flags right after
    assert text.count("- run: uv sync --project pipeline --locked") == text.count("- name: Resolve rule flags") == 5
    assert text.count("python -m scrooner_pipeline.common.rule_flags --dispatch") == 5
    assert text.count('>> "$GITHUB_ENV"') == 5
    # the nightly and the other scheduled workflows never set the flags
    for other in (ROOT / ".github" / "workflows").glob("*.yml"):
        if other.name != "pipeline-recompute.yml":
            assert "SCROONER_RULES" not in other.read_text(), other.name
