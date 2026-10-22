"""W3 (source.periodic_form_only@1) and WO-23 (dedupe.matching_copies@1) in
Stage 2e, on REAL fixtures from the stored facts (read-only lookups
2026-10-22, DATA-INFERRED; filing locators from data-team/36 item 2 and the
ledger, FILING-CHECKED there):

- JPM FY2025 NetIncomeLoss: 10-K 0001628280-26-008131 fact 29697 = 57,048M and
  DEF 14A 0000019617-26-000096 fact 733850 = 57,000M (R2 pay-versus-performance,
  printed in $ billions to one decimal) disagree, so the legacy stage left both
  non-authoritative.
- JPM Q4 2025 derived: 340478 = 13,025M (10-K) vs 182608846 = 12,977M (DEF 14A).
- WTRG FY2025 operating cash flow: 10-K 0000078128-26-000050 fact 5281880 =
  1,010,459,000 vs 8-K 0001193125-26-124163 fact 5281882 = 2,059,000,000 (the
  8-K furnishes American Water's statements under WTRG's CIK).
"""

import random
from datetime import date
from decimal import Decimal

import pytest

from scrooner_pipeline.common import rule_flags
from scrooner_pipeline.common.periodic_forms import (
    PERIODIC_FORMS_ALL,
    PERIODIC_FORMS_DOMESTIC,
    is_periodic_form,
    is_periodic_source_form,
)
from scrooner_pipeline.normalizer import dedupe
from scrooner_pipeline.normalizer import matching_copies as mc
from scrooner_pipeline.normalizer.dedupe import plan_authority

D = Decimal
K = date(2026, 2, 13)  # 10-K filing date
P = date(2026, 4, 6)  # DEF 14A filing date


def row(fid, value, form, filed, *, concept=1, period=1, auth=False, derived=False, unit=1):
    return (fid, concept, unit, period, D(value), filed, fid + 1000, form, auth, derived)


def final_state(rows, plan):
    state = {r[0]: r[8] for r in rows}
    for f in plan.set_true:
        state[f] = True
    for f in plan.set_false:
        state[f] = False
    return state


# --------------------------------------------------------------------------- JPM
JPM_FY = [
    row(29697, "57048000000", "10-K", K),
    row(733850, "57000000000", "DEF 14A", P),
]
JPM_Q4 = [
    row(340478, "13025000000", "10-K", K, concept=2, period=2, derived=True),
    row(182608846, "12977000000", "DEF 14A", P, concept=2, period=2, derived=True),
    # the priority-3 'available to common' tag, a separate group, authoritative today
    row(340493, "12691000000", "10-K", K, concept=3, period=2, auth=True, derived=True),
]


@pytest.mark.unit
def test_legacy_behaviour_proxy_copy_deauthorizes_the_10k():
    plan = plan_authority(JPM_FY)
    assert final_state(JPM_FY, plan) == {29697: False, 733850: False}
    assert plan.stats["conflict_groups"] == 1


@pytest.mark.unit
def test_w3_jpm_fy_10k_copy_becomes_authoritative_proxy_never():
    plan = plan_authority(JPM_FY, periodic_only=True, collect_changes=True)
    assert final_state(JPM_FY, plan) == {29697: True, 733850: False}
    assert plan.class_counts == {dedupe.CLASS_CONFLICT_CLEARED: 1}
    assert plan.changes[0][6] == ["DEF 14A"]  # the non-periodic form behind the change
    assert plan.stats["shrunk_group_promoted"] == 1


@pytest.mark.unit
def test_w3_jpm_q4_derived_proxy_row_is_ignored_and_10k_row_wins():
    rows = JPM_FY + JPM_Q4
    plan = plan_authority(rows, periodic_only=True)
    st = final_state(rows, plan)
    assert st[340478] is True and st[182608846] is False
    assert st[340493] is True  # untouched singleton in its own group
    # nothing written for the group that did not change
    assert 340493 not in plan.set_true and 340493 not in plan.set_false


@pytest.mark.unit
def test_w3_lone_proxy_copy_loses_authority_ma_case():
    # MA: the only NetIncomeLoss copies are the DEF 14A ones (authoritative lone rows)
    rows = [row(900, "14968000000", "DEF 14A", P, auth=True)]
    plan = plan_authority(rows, periodic_only=True, collect_changes=True)
    assert final_state(rows, plan) == {900: False}
    assert plan.class_counts == {dedupe.CLASS_VALUE_TO_NONE: 1}


@pytest.mark.unit
def test_w3_wtrg_8k_furnished_statement_does_not_outrank_the_10k():
    rows = [
        row(5281880, "1010459000", "10-K", date(2026, 2, 26)),
        row(5281882, "2059000000", "8-K", date(2026, 3, 25), auth=True),
    ]
    plan = plan_authority(rows, periodic_only=True, collect_changes=True)
    assert final_state(rows, plan) == {5281880: True, 5281882: False}
    assert plan.class_counts == {dedupe.CLASS_AUTHORITY_VALUE_CHANGED: 1}


@pytest.mark.unit
def test_w3_periodic_disagreement_remains_a_conflict_after_proxy_leaves():
    rows = [
        row(1, "100", "10-K", date(2025, 2, 1)),
        row(2, "130", "10-Q", date(2025, 5, 1)),
        row(3, "100", "DEF 14A", date(2025, 4, 1)),
    ]
    plan = plan_authority(rows, periodic_only=True, collect_changes=True)
    assert final_state(rows, plan) == {1: False, 2: False, 3: False}
    assert plan.class_counts == {dedupe.CLASS_PERIODIC_CONFLICT_REMAINS: 1}


@pytest.mark.unit
def test_w3_agreeing_periodic_copies_keep_earliest_and_demote_proxy():
    rows = [
        row(1, "100", "10-K", date(2025, 2, 1), auth=True),
        row(2, "100", "10-Q", date(2025, 5, 1)),
        row(3, "100", "DEF 14A", date(2025, 4, 1)),
    ]
    plan = plan_authority(rows, periodic_only=True, collect_changes=True)
    assert final_state(rows, plan) == {1: True, 2: False, 3: False}
    assert plan.class_counts == {dedupe.CLASS_NON_PERIODIC_DEMOTED_SAME_VALUE: 1}
    assert plan.set_true == []  # row 1 was already authoritative: no write


@pytest.mark.unit
def test_w3_foreign_periodic_forms_stay_authoritative():
    rows = [row(1, "5", "20-F", date(2025, 2, 1), auth=True), row(2, "7", "40-F/A", date(2025, 3, 1), period=2, auth=True)]
    plan = plan_authority(rows, periodic_only=True)
    assert plan.set_false == [] and plan.set_true == []


@pytest.mark.unit
@pytest.mark.parametrize("form", ["DEF 14A", "8-K", "8-K/A", "S-1", "S-1/A", "424B5", "10-12B", "11-K", "6-K", None])
def test_w3_every_non_periodic_form_is_demoted(form):
    rows = [row(1, "5", form, date(2025, 2, 1), auth=True)]
    plan = plan_authority(rows, periodic_only=True)
    assert final_state(rows, plan) == {1: False}


@pytest.mark.unit
def test_w3_singleton_periodic_group_untouched_even_when_non_authoritative():
    # e.g. a derived row retired by derive_q4: a group that did not shrink is not re-promoted
    rows = [row(1, "5", "10-K", date(2025, 2, 1), auth=False, derived=True)]
    plan = plan_authority(rows, periodic_only=True)
    assert plan.set_true == [] and plan.set_false == []


# ------------------------------------------------------- properties on random groups
def _legacy_reference(rows):
    """Transcription of the pre-W3 algorithm (git show origin/main:.../dedupe.py)."""
    groups = {}
    for fid, c, u, p, v, fd, _fi, _form, _a, _d in rows:
        groups.setdefault((c, u, p), []).append((fid, v))
    auth, non = set(), set()
    for members in groups.values():
        if len(members) == 1:
            continue
        if len({v for _, v in members}) == 1:
            auth.add(members[0][0])
            non.update(f for f, _ in members[1:])
        else:
            non.update(f for f, _ in members)
    return auth, non


def _random_rows(rng, n_groups=30):
    forms = ["10-K", "10-Q", "10-K/A", "DEF 14A", "8-K", "S-1", "20-F"]
    rows, fid = [], 0
    for g in range(n_groups):
        for _ in range(rng.randint(1, 5)):
            fid += 1
            rows.append(
                (
                    fid,
                    g % 7,
                    1,
                    g,
                    D(rng.choice([100, 100, 101, 5000, 5000000, 5000100])),
                    date(2020 + rng.randint(0, 5), 1 + rng.randint(0, 11), 1 + rng.randint(0, 27)),
                    fid,
                    rng.choice(forms),
                    rng.choice([True, False]),
                    rng.choice([True, False]),
                )
            )
    rows.sort(key=lambda r: (r[1], r[2], r[3], r[5], r[0]))
    return rows


@pytest.mark.unit
def test_flags_off_equals_the_legacy_algorithm_on_random_data():
    rng = random.Random(7)
    for _ in range(200):
        rows = _random_rows(rng)
        plan = plan_authority(rows)
        legacy_true, legacy_false = _legacy_reference(rows)
        cur = {r[0]: r[8] for r in rows}
        # every legacy decision is reproduced (writes that would not change a row are skipped)
        assert set(plan.set_true) == {f for f in legacy_true if not cur[f]}
        assert set(plan.set_false) == {f for f in legacy_false if cur[f]}


@pytest.mark.unit
def test_w3_is_idempotent_and_never_leaves_a_non_periodic_fact_authoritative():
    rng = random.Random(11)
    for _ in range(200):
        rows = _random_rows(rng)
        first = plan_authority(rows, periodic_only=True, matching_copies=True)
        st = final_state(rows, first)
        for r in rows:
            if r[7] not in PERIODIC_FORMS_ALL:
                assert st[r[0]] is False
        again = [r[:8] + (st[r[0]], r[9]) for r in rows]
        second = plan_authority(again, periodic_only=True, matching_copies=True)
        assert second.set_true == [] and second.set_false == []


@pytest.mark.unit
def test_w3_never_changes_a_group_without_non_periodic_copies_except_the_legacy_way():
    rng = random.Random(3)
    for _ in range(100):
        rows = [r for r in _random_rows(rng) if r[7] in PERIODIC_FORMS_ALL]
        assert plan_authority(rows, periodic_only=True).set_true == plan_authority(rows).set_true
        assert plan_authority(rows, periodic_only=True).set_false == plan_authority(rows).set_false


# ---------------------------------------------------------------- WO-23 matching
TTWO = (D("3372772000"), D("3372800000"))  # reported as 3,372,772K and 3,372.8M
ANET = (D("14043921000"), D("14043900000"))


@pytest.mark.unit
@pytest.mark.parametrize("a,b", [TTWO, ANET])
def test_matching_copies_consistent_pairs(a, b):
    assert mc.consistent(a, b) and mc.consistent(b, a)


@pytest.mark.unit
@pytest.mark.parametrize(
    "a,b",
    [
        (D("100000000"), D("120000000")),  # round number must not absorb a 20% restatement
        (D("5000000000"), D("1000000000")),  # company 8 FY2023 copies differ 5-10x
        (D("1000000000"), D("9000000000")),
        (D("100"), D("-100")),
        (D("0"), D("1000")),
        (D("1.92"), D("1.9")),  # per-share values are never merged
        (D("3372772000"), D("3372900000")),  # 128,000 > half of the 100,000 unit
        (D("1000"), D("1400")),  # within half of the 1,000 unit but 28% apart: relative cap
        (D("10000000000"), D("10004000000")),  # tz 10 would allow 5e9; the cap trusts millions at most
    ],
)
def test_matching_copies_inconsistent_pairs(a, b):
    assert not mc.consistent(a, b)


@pytest.mark.unit
def test_matching_copies_flag_off_is_a_conflict_and_on_prefers_the_precise_copy():
    rows = [row(1, TTWO[1], "10-K", date(2024, 5, 1)), row(2, TTWO[0], "10-K", date(2025, 5, 1))]
    off = plan_authority(rows)
    assert final_state(rows, off) == {1: False, 2: False}
    on = plan_authority(rows, matching_copies=True, collect_changes=False)
    assert final_state(rows, on) == {1: False, 2: True}  # 3,372,772,000 is the more precise copy
    assert on.stats["matching_copy_groups"] == 1 and on.stats["conflict_groups"] == 0


@pytest.mark.unit
def test_matching_copies_company8_style_conflict_stays_a_conflict_when_on():
    rows = [row(1, "5000000000", "10-K", date(2024, 5, 1)), row(2, "1000000000", "10-Q", date(2024, 8, 1)),
            row(3, "9000000000", "10-K", date(2025, 5, 1))]
    on = plan_authority(rows, matching_copies=True)
    assert final_state(rows, on) == {1: False, 2: False, 3: False}


@pytest.mark.unit
def test_matching_copies_does_not_pull_a_proxy_copy_in():
    rows = [row(1, TTWO[0], "10-K", date(2024, 5, 1)), row(2, TTWO[1], "DEF 14A", date(2024, 8, 1))]
    on = plan_authority(rows, periodic_only=True, matching_copies=True)
    assert final_state(rows, on) == {1: True, 2: False}


# -------------------------------------------------------------- constants and flags
@pytest.mark.unit
def test_periodic_form_constants():
    assert PERIODIC_FORMS_DOMESTIC < PERIODIC_FORMS_ALL
    assert PERIODIC_FORMS_ALL - PERIODIC_FORMS_DOMESTIC == {"20-F", "20-F/A", "40-F", "40-F/A"}
    assert is_periodic_form("10-K/A") and not is_periodic_form("20-F") and not is_periodic_form("DEF 14A")
    assert is_periodic_source_form("20-F") and not is_periodic_source_form("8-K") and not is_periodic_source_form(None)


@pytest.mark.unit
def test_rule_flag_parsing():
    env = {rule_flags.ENV_VAR: "source.periodic_form_only@1, dedupe.matching_copies@1"}
    assert rule_flags.rule_enabled(rule_flags.RULE_PERIODIC_FORM_ONLY, env)
    assert rule_flags.rule_enabled(rule_flags.RULE_MATCHING_COPIES, env)
    assert not rule_flags.rule_enabled(rule_flags.RULE_PERIODIC_FORM_ONLY, {})
    with pytest.raises(ValueError):
        rule_flags.enabled_rules({rule_flags.ENV_VAR: "source.periodic_form_only@2"})
    with pytest.raises(ValueError):
        rule_flags.enabled_rules({rule_flags.ENV_VAR: "not a rule"})
    with pytest.raises(ValueError):
        rule_flags.rule_enabled("made.up@1", {})


@pytest.mark.unit
def test_default_is_flag_off_in_the_stage_entry_point(monkeypatch):
    monkeypatch.delenv(rule_flags.ENV_VAR, raising=False)
    calls = {}

    class Cur:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def execute(self, sql, params=()):
            if sql.lstrip().startswith("select"):
                self.rows = [tuple(r) for r in JPM_FY]
            else:
                calls.setdefault("writes", []).append((sql, params))

        def fetchall(self):
            return self.rows

    class Conn:
        def cursor(self):
            return Cur()

        def commit(self):
            pass

    stats = dedupe.resolve_authoritative_for_company(Conn(), 1)
    assert stats["conflict_groups"] == 1 and stats["non_periodic_demoted"] == 0  # legacy
    monkeypatch.setenv(rule_flags.ENV_VAR, rule_flags.RULE_PERIODIC_FORM_ONLY)
    stats = dedupe.resolve_authoritative_for_company(Conn(), 1)
    assert stats["conflict_groups"] == 0 and stats["non_periodic_demoted"] == 0
    assert stats["shrunk_group_promoted"] == 1
