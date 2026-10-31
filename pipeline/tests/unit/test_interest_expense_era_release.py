"""Release package 1 of interest_expense.era_tag_fill@1: guards refuse before the first write, stale cells refuse
the whole run, apply inserts exactly two rows per cell with the filed fact as source, restore undoes the run."""

from __future__ import annotations

import contextlib
from decimal import Decimal

import pytest

from scrooner_pipeline.common import rule_flags
from scrooner_pipeline.mapper import interest_expense_era_release as ie

ON = {rule_flags.ENV_ENABLED: ie.RULE_ID}
PLAN = [
    {"company_id": "1", "cik": "0000000001", "bank": "False", "period_id": "10", "start": "2025-01-01",
     "end": "2025-03-31", "months": "3", "tag": "InterestExpenseNonoperating", "value": "67000000",
     "accession": "0000021665-25-000053", "fact_id": "501", "outcome": "fill", "label_check": "gross_label",
     "label": "Interest expense"},
    {"company_id": "2", "cik": "0000000002", "bank": "True", "period_id": "20", "start": "2025-01-01",
     "end": "2025-12-31", "months": "12", "tag": "InterestExpenseOperating", "value": "261672000",
     "accession": "0001025835-26-000058", "fact_id": "502", "outcome": "fill", "label_check": "gross_label",
     "label": "Total interest expense"},
    {"company_id": "3", "cik": "0000000003", "bank": "False", "period_id": "30", "start": "2025-01-01",
     "end": "2025-03-31", "months": "3", "tag": "InterestExpenseNonoperating", "value": "134612000",
     "accession": "0000917251-26-000013", "fact_id": "503", "outcome": "hold_net_label", "label_check": "net_label",
     "label": "Interest expense, net"},
]  # fmt: skip


class FakeDB:
    def __init__(self, taken=(), facts=None):
        self.taken = set(taken)
        self.facts = facts or {
            501: (Decimal("67000000"), True, False),
            502: (Decimal("261672000"), True, False),
        }
        self.result = []

    def cursor(self):
        return self

    def transaction(self):
        return contextlib.nullcontext()

    def commit(self):
        pass

    def execute(self, sql, params=None):
        s = " ".join(sql.split()).lower()
        if s.startswith("set "):
            return self
        if "from analytics.canonical_concept" in s:
            self.result = [("interest_expense", 7), ("interest_expense_resolved", 8)]
        elif "from analytics.canonical_fact" in s:
            self.result = sorted(self.taken)
        elif "from core.fact" in s:
            self.result = [(i, *v) for i, v in self.facts.items() if i in params[0]]
        else:
            raise AssertionError(sql)
        return self

    def fetchall(self):
        return self.result

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


@pytest.fixture
def pkg(tmp_path, monkeypatch):
    calls = {"rows": [], "evidence": [], "runs": [], "restored": []}

    def replace_rows(cur, rows, **kw):
        calls["rows"].extend(rows)
        return {"unchanged": 0, "replaced": 0, "inserted": len(rows)}

    monkeypatch.setattr(ie.ca, "replace_rows", replace_rows)
    monkeypatch.setattr(
        ie.ca, "restore_run", lambda cur, run_id: calls["restored"].append(run_id) or 4
    )
    monkeypatch.setattr(
        ie.cs,
        "append_evidence",
        lambda conn, rec, import_key=None: calls["evidence"].append(rec),
    )
    monkeypatch.setattr(
        ie.cs,
        "start_rule_run",
        lambda conn, rule, mode, *a, **k: calls["runs"].append(mode) or f"run-{mode}",
    )
    monkeypatch.setattr(ie.cs, "finish_rule_run", lambda conn, run, stats: None)
    m = ie.build(PLAN, tmp_path)
    return tmp_path, m, calls


def test_build_takes_only_fill_cells_and_lists_the_rest(pkg):
    d, m, _ = pkg
    assert (m["cells"], m["companies"], m["rows_to_insert"], m["keep_cells"]) == (
        2,
        2,
        4,
        1,
    )
    assert m["keep_by_outcome"] == {"hold_net_label": 1}
    assert (d / "touched_ciks.txt").read_text() == "0000000001\n0000000002\n"


def test_apply_refuses_without_rule_token_or_reviewed_digest(pkg):
    d, m, calls = pkg
    with pytest.raises(ie.ReleaseRefused, match="not ON"):
        ie.apply(FakeDB(), d, m["digest"], ie.CONFIRM_TOKEN, environ={})
    with pytest.raises(ie.ReleaseRefused, match="confirm"):
        ie.apply(FakeDB(), d, m["digest"], "yes", environ=ON)
    with pytest.raises(ie.ReleaseRefused, match="reviewed digest"):
        ie.apply(FakeDB(), d, "0" * 64, ie.CONFIRM_TOKEN, environ=ON)
    assert calls["rows"] == [] and calls["runs"] == []


@pytest.mark.parametrize(
    "db",
    [
        FakeDB(taken={(2, 20)}),  # the nightly has since filled the key
        FakeDB(
            facts={
                501: (Decimal("67000000"), False, False),
                502: (Decimal("261672000"), True, False),
            }
        ),  # demoted
        FakeDB(
            facts={
                501: (Decimal("68000000"), True, False),
                502: (Decimal("261672000"), True, False),
            }
        ),  # changed
        FakeDB(facts={502: (Decimal("261672000"), True, False)}),  # gone
    ],
)
def test_a_stale_cell_refuses_the_whole_run_before_any_write(pkg, db):
    d, m, calls = pkg
    assert ie.dry_run(db, ie.load_package(d, m["digest"]))["would_apply"] is False
    with pytest.raises(ie.ReleaseRefused, match="stale"):
        ie.apply(db, d, m["digest"], ie.CONFIRM_TOKEN, environ=ON)
    assert calls["rows"] == [] and calls["runs"] == []


def test_apply_inserts_both_concepts_with_the_filed_fact_and_writes_evidence(pkg):
    d, m, calls = pkg
    out = ie.apply(FakeDB(), d, m["digest"], ie.CONFIRM_TOKEN, environ=ON)
    assert out == {"run_id": "run-apply", "inserted": 4, "cells": 2}
    assert {(r.company_id, r.canonical_concept_id, r.period_id, r.value, r.source_fact_ids) for r in calls["rows"]} == {
        (1, 7, 10, Decimal("67000000"), (501,)), (1, 8, 10, Decimal("67000000"), (501,)),
        (2, 7, 20, Decimal("261672000"), (502,)), (2, 8, 20, Decimal("261672000"), (502,)),
    }  # fmt: skip
    grains = sorted(
        (e.key.company_id, e.key.period_grain, e.accession) for e in calls["evidence"]
    )
    assert grains == [
        (1, "Q", "0000021665-25-000053"),
        (2, "FY", "0001025835-26-000058"),
    ]


def test_apply_refuses_a_batch_that_would_replace_a_stored_row(pkg, monkeypatch):
    d, m, calls = pkg
    monkeypatch.setattr(
        ie.ca,
        "replace_rows",
        lambda cur, rows, **kw: {
            "unchanged": 0,
            "replaced": 1,
            "inserted": len(rows) - 1,
        },
    )
    with pytest.raises(ie.ReleaseRefused, match="replace stored rows"):
        ie.apply(FakeDB(), d, m["digest"], ie.CONFIRM_TOKEN, environ=ON)


def test_restore_undoes_the_run(pkg):
    _d, _m, calls = pkg
    assert (
        ie.restore(FakeDB(), "run-apply", ie.CONFIRM_TOKEN)["restored_archive_rows"]
        == 4
    )
    assert calls["restored"] == ["run-apply"] and calls["runs"] == ["rollback"]
    with pytest.raises(ie.ReleaseRefused):
        ie.restore(FakeDB(), "run-apply", "no")
