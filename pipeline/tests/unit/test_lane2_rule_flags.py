"""Lane 2's rules in the unified flag module (common/rule_flags.py) and the
in-process decision log (mapper/rule_flags.py)."""

import pytest

from scrooner_pipeline.common import rule_flags as unified
from scrooner_pipeline.mapper import rule_flags


def test_lane2_rules_are_registered_and_default_off():
    for rid in (
        rule_flags.RF01_CONSECUTIVE_WINDOW,
        rule_flags.RF02_AGE_GUARD,
        rule_flags.RF10_BS_DATE_ANCHOR,
        rule_flags.RF_TSY_STALE,
        rule_flags.RF_TSY_UNEVIDENCED_ZERO,
    ):
        assert rid in unified.RULES
        if (
            rid != rule_flags.RF_TSY_UNEVIDENCED_ZERO
        ):  # lane 1's RF-08, applied by lane 2
            assert unified.RULES[rid].lane == "lane2"
        assert rule_flags.rule_mode(rid, {}) == rule_flags.OFF


def test_mapper_module_reexports_the_unified_functions():
    assert rule_flags.rule_mode is unified.rule_mode
    assert rule_flags.ENV_ENABLED == unified.ENV_ENABLED == "SCROONER_RULES_ENABLED"


def test_modes_and_typos():
    env = {
        rule_flags.ENV_ENABLED: " ttm.consecutive_window@1 ",
        rule_flags.ENV_DRYRUN: "ttm.age_guard@2",
    }
    assert (
        rule_flags.rule_mode(rule_flags.RF01_CONSECUTIVE_WINDOW, env) == rule_flags.ON
    )
    assert rule_flags.rule_mode(rule_flags.RF02_AGE_GUARD, env) == rule_flags.DRY_RUN
    assert rule_flags.rule_mode(rule_flags.RF10_BS_DATE_ANCHOR, env) == rule_flags.OFF
    with pytest.raises(ValueError, match="unregistered"):
        rule_flags.rule_mode(
            rule_flags.RF02_AGE_GUARD, {rule_flags.ENV_ENABLED: "ttm.age_guard@3"}
        )
    with pytest.raises(ValueError, match="both"):
        rule_flags.rule_mode(
            rule_flags.RF02_AGE_GUARD,
            {
                rule_flags.ENV_ENABLED: "ttm.age_guard@2",
                rule_flags.ENV_DRYRUN: "ttm.age_guard@2",
            },
        )


def test_unevidenced_zero_is_lane_1s_rf08_rule_and_can_run_in_both_modes():
    uz = rule_flags.RF_TSY_UNEVIDENCED_ZERO
    assert uz == "composite.unknown_not_zero@1" and unified.RULES[uz].rf == "RF-08"
    assert unified.RULES[uz].dry_run  # a real dry-run path (lane 2 applies it to TSY)
    assert rule_flags.rule_mode(uz, {rule_flags.ENV_DRYRUN: uz}) == rule_flags.DRY_RUN
    assert rule_flags.rule_mode(uz, {rule_flags.ENV_ENABLED: uz}) == rule_flags.ON


def test_dispatch_text_can_enable_both_tsy_rules():
    on, dry = unified.parse_dispatch(
        "on:tsy.stale_component@1,composite.unknown_not_zero@1"
    )
    assert on == {"tsy.stale_component@1", "composite.unknown_not_zero@1"} and not dry


def test_decision_log_reports_a_reason_only_for_a_hidden_decision_in_mode_on():
    log = rule_flags.DecisionLog()

    def d(mode, outcome):
        return rule_flags.GuardDecision(
            rule_id="ttm.age_guard@2",
            mode=mode,
            company_id=1,
            data_point="x",
            period_grain="TTM",
            period_start=None,
            period_end=None,
            outcome=outcome,
            reason_code="why",
            old_value=None,
            new_value=None,
        )

    log.add(d(rule_flags.DRY_RUN, "hidden"))
    assert log.reason_for(1, "x") is None  # shadow mode never changes a reason
    log.add(d(rule_flags.ON, "kept"))
    assert log.reason_for(1, "x") is None
    log.add(d(rule_flags.ON, "hidden"))
    assert log.reason_for(1, "x") == "why" and log.reason_for(2, "x") is None
    log.clear_company(1)
    assert log.reason_for(1, "x") is None
