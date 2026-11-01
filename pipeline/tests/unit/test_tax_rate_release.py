"""Family A release (mapper/tax_rate_release.py): every guard refuses before the first write; a re-built plan with a
different digest is stale; the happy path writes in one transaction; restore is logged."""

from __future__ import annotations

import contextlib
import json
from datetime import date
from decimal import Decimal

import pytest

from scrooner_pipeline.common import rule_flags
from scrooner_pipeline.mapper import derived_row_retirement as rr
from scrooner_pipeline.mapper import tax_rate_release as tr

ON = {rule_flags.ENV_ENABLED: rr.RULE_RATIO}


def _plan(value="-0.404"):
    cell = rr.CellPlan(family="A_ratio_derived", rule_id=rr.RULE_RATIO, canonical_fact_id=1, company_id=7,
                       canonical_concept_id=99, concept="effective_tax_rate_reported", period_id=3,
                       period_end=date(2023, 12, 31), stored_value=Decimal(value), source_fact_ids=(5,),
                       retired_source_ids=(5,), action=rr.ACT_REMOVE, reason_code="ratio_derived_no_filed_value")  # fmt: skip
    return rr.Plan("A_ratio_derived", rr.RULE_RATIO, cells=[cell])


class FakeConn:
    def __init__(self, table=True):
        self.table = table

    def cursor(self):
        return self

    def transaction(self):
        return contextlib.nullcontext()

    def rollback(self):
        pass

    def commit(self):
        pass

    def execute(self, sql, params=None):
        return self

    def fetchone(self):
        return ("analytics.fact_authority_retired" if self.table else None,)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


@pytest.fixture
def pkg(tmp_path, monkeypatch):
    plan = _plan()
    (tmp_path / "company_ids.txt").write_text("7\n")
    (tmp_path / "PACKAGE.json").write_text(
        json.dumps({"digest": plan.digest(), "company_ids_file": "company_ids.txt"})
    )
    calls = {"applied": [], "runs": []}
    monkeypatch.setattr(tr, "build_plan", lambda cur, ids, chunk=50: plan)
    monkeypatch.setattr(
        tr.rr,
        "apply_plan",
        lambda cur, p, **kw: calls["applied"].append(kw) or {"cells_removed": 1},
    )
    monkeypatch.setattr(tr.cs, "start_rule_run", lambda conn, rule, mode, *a, **k: calls["runs"].append(mode) or f"run-{mode}")  # fmt: skip
    monkeypatch.setattr(tr.cs, "finish_rule_run", lambda conn, run, stats: None)
    return tmp_path, plan.digest(), calls


def test_apply_refuses_rule_off_bad_token_wrong_digest_missing_table(pkg):
    d, digest, calls = pkg
    with pytest.raises(tr.ReleaseRefused, match="not ON"):
        tr.apply(FakeConn(), d, digest, tr.CONFIRM_TOKEN, environ={})
    with pytest.raises(tr.ReleaseRefused, match="confirm"):
        tr.apply(FakeConn(), d, digest, "yes", environ=ON)
    with pytest.raises(tr.ReleaseRefused, match="PACKAGE.json"):
        tr.apply(FakeConn(), d, "0" * 64, tr.CONFIRM_TOKEN, environ=ON)
    with pytest.raises(tr.ReleaseRefused, match="0116"):
        tr.apply(FakeConn(table=False), d, digest, tr.CONFIRM_TOKEN, environ=ON)
    assert calls["applied"] == [] and calls["runs"] == []


def test_a_rebuilt_plan_with_another_digest_is_stale(pkg, monkeypatch):
    d, digest, calls = pkg
    monkeypatch.setattr(tr, "build_plan", lambda cur, ids, chunk=50: _plan("-0.405"))
    with pytest.raises(tr.ReleaseRefused, match="stale"):
        tr.apply(FakeConn(), d, digest, tr.CONFIRM_TOKEN, environ=ON)
    assert calls["applied"] == [] and calls["runs"] == []


def test_apply_writes_once_with_the_reviewed_digest(pkg):
    d, digest, calls = pkg
    out = tr.apply(FakeConn(), d, digest, tr.CONFIRM_TOKEN, environ=ON)
    assert out == {"run_id": "run-apply", "cells_removed": 1}
    assert (
        calls["runs"] == ["apply"] and calls["applied"][0]["expected_digest"] == digest
    )


def test_restore_is_logged_and_needs_the_token(monkeypatch):
    runs = []
    monkeypatch.setattr(
        tr.cs,
        "start_rule_run",
        lambda conn, rule, mode, *a, **k: runs.append(mode) or "rb",
    )
    monkeypatch.setattr(tr.cs, "finish_rule_run", lambda conn, run, stats: None)
    monkeypatch.setattr(
        tr.rr,
        "restore",
        lambda cur, run_id: {"cell_archive_rows_restored": 1, "facts_restored": 1},
    )
    assert tr.restore(FakeConn(), "run-apply", tr.CONFIRM_TOKEN)[
        "facts_restored"
    ] == 1 and runs == ["rollback"]
    with pytest.raises(tr.ReleaseRefused):
        tr.restore(FakeConn(), "run-apply", "no")
