"""Family C release (mapper/per_share_release.py): every guard refuses before the first write; a re-built plan with a
different digest (stale) refuses; the happy path writes in one transaction, protects the FSN-sourced cells and lists
the companies to recompute; restore removes the run's protection."""

from __future__ import annotations

import contextlib
import json
from datetime import date
from decimal import Decimal

import pytest

from scrooner_pipeline.common import rule_flags
from scrooner_pipeline.mapper import derived_row_retirement as rr
from scrooner_pipeline.mapper import per_share_release as ps

BOTH_ON = {rule_flags.ENV_ENABLED: f"{rr.RULE_PER_SHARE},{ps.RULE_PER_SHARE_TTM}"}


def _plan(value="1.10"):
    base = dict(
        family="C_per_share_derived",
        rule_id=rr.RULE_PER_SHARE,
        canonical_concept_id=117,
        concept="basic_eps",
    )
    removed = rr.CellPlan(
        **base,
        canonical_fact_id=1,
        company_id=7,
        period_id=3,
        period_end=date(2025, 12, 31),
        stored_value=Decimal(value),
        source_fact_ids=(5,),
        retired_source_ids=(5,),
        action=rr.ACT_REMOVE,
        reason_code="per_share_not_filed_separately",
    )
    fsn = rr.CellPlan(
        **base,
        canonical_fact_id=2,
        company_id=8,
        period_id=4,
        period_end=date(2019, 12, 31),
        stored_value=Decimal("0.95"),
        source_fact_ids=(6,),
        retired_source_ids=(6,),
        action=rr.ACT_REPLACE_FSN,
        replacement_value=Decimal("0.97"),
        replacement_accession="acc",
        period_start=date(2019, 10, 1),
        note="fsn-notes:2020q1/num",
    )
    return rr.Plan("C_per_share_derived", rr.RULE_PER_SHARE, cells=[removed, fsn])  # fmt: skip


class FakeConn:
    def __init__(self, table=True, guard=True):
        self.table, self.guard = table, guard
        self.result = None
        self.protected = []
        self.statements = []
        self.rowcount = 0

    def cursor(self):
        return self

    def transaction(self):
        return contextlib.nullcontext()

    def rollback(self):
        pass

    def commit(self):
        pass

    def executemany(self, sql, rows):
        self.protected.extend(rows)

    def execute(self, sql, params=None):
        self.statements.append(" ".join(sql.split()).lower())
        name = params[0] if params else ""
        ok = {
            "analytics.fact_authority_retired": self.table,
            "analytics.slot_protected_cell": self.guard,
        }
        self.result = (name if ok.get(name, True) else None,)
        return self

    def fetchone(self):
        return self.result

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


@pytest.fixture
def pkg(tmp_path, monkeypatch):
    plan = _plan()
    (tmp_path / "company_ids.txt").write_text("7\n8\n")
    (tmp_path / "fsn.json").write_text("[]")
    (tmp_path / "PACKAGE.json").write_text(json.dumps({"digest": plan.digest(), "company_ids_file": "company_ids.txt",
                                                       "fsn_outcomes_file": "fsn.json"}))  # fmt: skip
    calls = {"applied": [], "runs": []}
    monkeypatch.setattr(ps, "build_plan", lambda cur, ids, fsn, chunk=50: plan)
    monkeypatch.setattr(
        ps.rr,
        "apply_plan",
        lambda cur, p, **kw: calls["applied"].append(kw) or {"cells_removed": 1},
    )
    monkeypatch.setattr(ps.cs, "start_rule_run", lambda conn, rule, mode, *a, **k: calls["runs"].append(mode) or f"run-{mode}")  # fmt: skip
    monkeypatch.setattr(ps.cs, "finish_rule_run", lambda conn, run, stats: None)
    return tmp_path, plan.digest(), calls


def test_apply_needs_both_rules_on(pkg):
    d, digest, calls = pkg
    only_c = {rule_flags.ENV_ENABLED: rr.RULE_PER_SHARE}
    with pytest.raises(ps.ReleaseRefused, match="pershare.never_derive_ttm"):
        ps.apply(FakeConn(), d, digest, ps.CONFIRM_TOKEN, environ=only_c)
    assert calls["applied"] == [] and calls["runs"] == []


def test_apply_refuses_bad_token_wrong_digest_or_a_missing_table(pkg):
    d, digest, calls = pkg
    with pytest.raises(ps.ReleaseRefused, match="confirm"):
        ps.apply(FakeConn(), d, digest, "yes", environ=BOTH_ON)
    with pytest.raises(ps.ReleaseRefused, match="PACKAGE.json"):
        ps.apply(FakeConn(), d, "0" * 64, ps.CONFIRM_TOKEN, environ=BOTH_ON)
    with pytest.raises(ps.ReleaseRefused, match="fact_authority_retired"):
        ps.apply(FakeConn(table=False), d, digest, ps.CONFIRM_TOKEN, environ=BOTH_ON)
    with pytest.raises(ps.ReleaseRefused, match="slot_protected_cell"):
        ps.apply(FakeConn(guard=False), d, digest, ps.CONFIRM_TOKEN, environ=BOTH_ON)
    assert calls["applied"] == [] and calls["runs"] == []


def test_a_rebuilt_plan_with_another_digest_is_stale_and_refused(pkg, monkeypatch):
    d, digest, calls = pkg
    monkeypatch.setattr(ps, "build_plan", lambda cur, ids, fsn, chunk=50: _plan("1.11"))
    with pytest.raises(ps.ReleaseRefused, match="stale"):
        ps.apply(FakeConn(), d, digest, ps.CONFIRM_TOKEN, environ=BOTH_ON)
    assert calls["applied"] == [] and calls["runs"] == []


def test_apply_writes_once_protects_fsn_cells_and_lists_companies_to_recompute(pkg):
    d, digest, calls = pkg
    conn = FakeConn()
    out = ps.apply(conn, d, digest, ps.CONFIRM_TOKEN, environ=BOTH_ON)
    assert out == {
        "run_id": "run-apply",
        "cells_removed": 1,
        "protected": 1,
        "companies_to_recompute": 2,
    }
    assert (
        calls["runs"] == ["apply"] and calls["applied"][0]["expected_digest"] == digest
    )
    assert conn.protected == [
        (8, 117, 4, rr.RULE_PER_SHARE, Decimal("0.97"), "run-apply", digest)
    ]
    assert "set local scrooner.slot_writer = 'on'" in conn.statements
    assert (d / "touched_company_ids_run-apply.txt").read_text() == "7\n8\n"


def test_restore_removes_the_run_s_protection(monkeypatch):
    monkeypatch.setattr(
        ps.cs, "start_rule_run", lambda conn, rule, mode, *a, **k: f"run-{mode}"
    )
    monkeypatch.setattr(ps.cs, "finish_rule_run", lambda conn, run, stats: None)
    monkeypatch.setattr(
        ps.rr,
        "restore",
        lambda cur, run_id: {"cell_archive_rows_restored": 2, "facts_restored": 1},
    )
    conn = FakeConn()
    out = ps.restore(conn, "run-apply", ps.CONFIRM_TOKEN)
    assert out["cell_archive_rows_restored"] == 2
    assert any(
        s.startswith("delete from analytics.slot_protected_cell")
        for s in conn.statements
    )
    with pytest.raises(ps.ReleaseRefused):
        ps.restore(conn, "run-apply", "no")
