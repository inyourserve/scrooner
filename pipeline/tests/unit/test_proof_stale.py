"""A proof row at an older rule version is proof_stale, not no_proof_row (2026-11-22: the component_parts v1->v3
bumps turned ~460 PROVEN component cells into UNCHECKED no_proof_row with their values unchanged, and open shown cells
rose 1,485 -> 1,648 between exports). Each test fails without the behaviour it names (mutation-checked)."""

from __future__ import annotations

from collections import Counter
from datetime import date
from decimal import Decimal as D

from scrooner_pipeline.mapper import top100_coverage as t100
from scrooner_pipeline.proof import rules as R
from scrooner_pipeline.proof.prove import DETECTOR_VERSION
from scrooner_pipeline.proof.runner import stale_companies

S, E = date(2020, 1, 1), date(2020, 12, 31)
CUR = {"rules": {"claim": 1, "component_parts": R.RULES["component_parts"].version}}
OLD = {"rules": {"claim": 1, "component_parts": R.RULES["component_parts"].version - 1}}


class FakeConn:
    def __init__(self, rows):
        self.rows = rows
        self.calls = 0

    def execute(self, *_a, **_k):
        self.calls += 1
        return self

    def fetchall(self):
        # one chunk of companies returns the rows once
        return self.rows if self.calls == 1 else []


def _proof_row(cid, name, checks, verdict="PROVEN"):
    return (
        cid,
        name,
        S,
        E,
        verdict,
        None,
        None,
        D(5),
        "T",
        "A-1",
        "fsn",
        "IS",
        3,
        checks,
    )


def test_stale_rules_names_the_moved_rule_and_version():
    v = R.RULES["component_parts"].version
    assert R.stale_rules(CUR) == []
    assert R.stale_rules(OLD) == [f"component_parts:v{v - 1}->v{v}"]
    assert R.stale_rules({"rules": {"gone_rule": 1}}) == ["gone_rule:v1->gone"]
    assert R.stale_rules({}) == ["unrecorded"]


def test_load_current_proofs_reports_stale_rows_apart_from_missing():
    conn = FakeConn([_proof_row(1, "sga", CUR), _proof_row(1, "rnd", OLD)])
    stale: dict = {}
    proofs = t100.load_current_proofs(conn, [1], ["sga", "rnd"], stale)
    assert set(proofs) == {(1, "sga", S, E)}
    assert set(stale) == {(1, "rnd", S, E)}
    assert stale[(1, "rnd", S, E)][0].startswith("component_parts:v")
    # the old call shape keeps working
    assert (
        set(
            t100.load_current_proofs(
                FakeConn([_proof_row(1, "rnd", OLD)]), [1], ["rnd"]
            )
        )
        == set()
    )


def test_classify_stale_is_proof_stale_open_not_proven_not_no_proof_row():
    args = (None, None, None, D(5), None, None, None, "mapped")
    assert t100.classify(*args) == ("UNCHECKED", "no_proof_row")
    assert t100.classify(*args, stale_proof=True) == ("UNCHECKED", t100.PROOF_STALE)
    # a current verdict always wins over the stale flag
    assert t100.classify(
        "PROVEN", None, D(5), D(5), None, None, None, "mapped", stale_proof=True
    ) == (
        "PROVEN",
        None,
    )
    # a stale flag never invents a value for a blank cell
    assert (
        t100.classify(
            None, None, None, None, None, None, None, "mapped", stale_proof=True
        )[0]
        == "BLANK"
    )


def _cell(code):
    return {
        "rank": 1,
        "ticker": "X",
        "company_id": 1,
        "data_point": "sga",
        "fiscal_year": 2020,
        "period_end": E.isoformat(),
        "class": "UNCHECKED",
        "reason_code": code,
        "reason": "",
        "shown_value": "5",
        "display": t100.OPEN,
        "_stale_rules": ["component_parts:v2->v3"]
        if code == t100.PROOF_STALE
        else None,
    }


def test_proof_stale_is_reprove_work_and_counted_per_rule():
    assert t100.work_type(_cell(t100.PROOF_STALE)) == "reprove"
    assert t100.work_type(_cell("no_proof_row")) == "proof"
    assert "reprove" in t100.WORK_TYPES
    rows = [_cell(t100.PROOF_STALE), _cell(t100.PROOF_STALE), _cell("no_proof_row")]
    assert t100.stale_summary(rows) == {"cells": 2, "component_parts:v2->v3": 2}
    assert "component_parts:v2->v3" in t100.stale_reason_text(
        ["component_parts:v2->v3"]
    )


def test_proof_stale_stays_open_never_hidden():
    rows = [{**_cell(t100.PROOF_STALE), "_presented": False}]
    rows[0].pop("display")
    t100.apply_display(rows)
    assert rows[0]["display"] == t100.OPEN


def test_stale_companies_selects_only_companies_with_a_moved_rule():
    conn = FakeConn(
        [(1, CUR["rules"]), (2, OLD["rules"]), (2, CUR["rules"]), (3, None)]
    )
    out = stale_companies(conn, [1, 2, 3])
    assert set(out) == {
        2,
        3,
    }  # 3: a row without a record still needs the scoped run (stamp)
    assert out[2] == Counter({R.stale_rules(OLD)[0]: 1})
    assert out[3] == Counter({"unrecorded": 1})
    assert (
        DETECTOR_VERSION
    )  # the query is pinned to the floor; a floor bump is not a stale rule
