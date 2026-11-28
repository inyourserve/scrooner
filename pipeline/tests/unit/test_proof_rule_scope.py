"""ONE-PATH step 1: rule-scoped proof versions (proof/rules.py, proof/runner.scope_proofs).
Each test fails without the behaviour it names (mutation-checked, see the commit message)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from scrooner_pipeline.proof import rules as R
from scrooner_pipeline.proof.prove import (
    DETECTOR_VERSION,
    PROVEN,
    Claim,
    Proof,
    Shown,
)
from scrooner_pipeline.proof.runner import scope_proofs

FLOOR = DETECTOR_VERSION
S, E = date(2019, 1, 1), date(2019, 12, 31)


def shown(name="total_debt_resolved", claim=None, split=()):
    return Shown(
        1,
        name,
        "FY",
        S,
        E,
        Decimal(5),
        (),
        "A-1",
        (1,),
        claim=claim,
        combined_splits=split,
    )


COMP = Claim("component", "BS", parts=((1, "A"), (1, "B")))
SPLIT = (("X", ("a", "b")),)


def proof(sh, **checks):
    return Proof(sh, PROVEN, checks={"claim": {"status": "pass"}, **checks})


def test_record_is_built_from_what_ran_and_stored_in_row_checks():
    p = proof(shown(claim=COMP, split=SPLIT), period_length={"status": "pass"})
    row = p.row()
    assert row["checks"]["rules"] == R.rules_used(p.shown, p.checks)
    assert row["checks"]["rules"]["component_sum_authority"] == 3  # v3: 8ce6807f3
    assert row["checks"]["rules"]["split_parts"] == 2
    assert (
        "rules" not in p.checks
    )  # in-memory checks stay check-only (_finish iterates them)
    plain = proof(shown()).row()["checks"]["rules"]
    assert "split_parts" not in plain and "component_sum_authority" not in plain


def test_currency_rule_version_and_floor():
    ok = {"rules": {"claim": 1, "split_parts": 2}}
    assert R.row_is_current(FLOOR, ok, FLOOR)
    assert not R.row_is_current("cell_proof_v1_old", ok, FLOOR)  # floor bump = history
    assert not R.row_is_current(FLOOR, {"rules": {"claim": 1, "split_parts": 0}}, FLOOR)
    assert not R.row_is_current(FLOOR, {"rules": {"gone_rule": 1}}, FLOOR)
    assert not R.row_is_current(FLOOR, {}, FLOOR)  # unstamped legacy row
    assert R.row_holds_disagree(FLOOR, {}, FLOOR)  # ... but it still holds a DISAGREE
    assert not R.row_holds_disagree(FLOOR, {"rules": {"split_parts": 0}}, FLOOR)


def test_a_rule_change_selects_only_cells_that_used_the_rule():
    plain, comp, split = shown(), shown(claim=COMP), shown(split=SPLIT)
    chk = {"claim": {}}
    # legacy rows (no record): v22 moved component_sum_authority (1 -> 2) and added split_parts (0 -> 1)
    assert R.reproof_rules(None, plain, chk) == []
    assert R.reproof_rules(None, comp, chk) == ["component_sum_authority"]
    # a combined-spanned cell is also re-proved by resolver_beats_combined (0 -> 1, ONE-PATH 2026-11-16)
    assert R.reproof_rules(None, split, chk) == [
        "resolver_beats_combined",
        "split_parts",
    ]
    cur = R.rules_used(comp, chk)
    assert R.reproof_rules(cur, comp, chk) == []
    assert R.reproof_rules({**cur, "component_sum_authority": 1}, comp, chk) == [
        "component_sum_authority"
    ]


class FakeConn:
    def __init__(self, rows):
        self.rows = rows

    def execute(self, *_a, **_k):
        return self

    def fetchall(self):
        return self.rows


def _stored(i, sh, dv=FLOOR, rec="legacy"):
    checks = {"claim": {"status": "pass"}}
    if rec != "legacy":
        checks["rules"] = rec
    return (
        i,
        sh.data_point_name,
        sh.period_grain,
        sh.period_start,
        sh.period_end,
        dv,
        checks,
    )


def test_scope_proofs_writes_selected_stamps_unselected_legacy_keeps_current():
    comp = proof(shown("total_debt_resolved", claim=COMP))
    plain = proof(shown("revenue_sanity_resolved"))
    done = proof(shown("net_income_resolved"))
    new = proof(shown("operating_income_resolved"))
    old_floor = proof(shown("gross_profit_resolved"))
    conn = FakeConn(
        [
            _stored(1, comp.shown),  # legacy, used component_sum_authority -> re-proved
            _stored(2, plain.shown),  # legacy, nothing moved -> stamped
            _stored(
                3, done.shown, rec=R.rules_used(done.shown, done.checks)
            ),  # current -> kept
            _stored(
                5, old_floor.shown, dv="cell_proof_v19_x"
            ),  # other floor -> re-proved
        ]
    )
    to_write, stamps, kept, why = scope_proofs(
        conn, 1, [comp, plain, done, new, old_floor]
    )
    assert {p.shown.data_point_name for p in to_write} == {
        "total_debt_resolved",
        "operating_income_resolved",
        "gross_profit_resolved",
    }
    assert [i for i, _ in stamps] == [2]
    assert kept == 1
    assert why["component_sum_authority"] == 1


def test_registry_is_consistent():
    for r in R.RULES.values():
        assert r.version >= r.legacy_version >= 0
