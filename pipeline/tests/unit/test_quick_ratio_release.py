"""Release package 1 of quick_ratio.inventory_evidence@1 (mapper/quick_ratio_release.py): every guard refuses before
the first write, stale cells refuse the whole run, apply and restore are exact. No database: a fake connection."""

from __future__ import annotations

import contextlib
import json
from datetime import date
from decimal import Decimal

import pytest

from scrooner_pipeline.common import rule_flags
from scrooner_pipeline.mapper import quick_ratio_release as qr

ON = {rule_flags.ENV_ENABLED: qr.RULE_ID}
REASON = "incomplete:inventory_value_under_review"


class FakeDB:
    """metric_value rows {id: [company_id, period_end, label, value, reason, sources]}; logs writes and runs."""

    def __init__(self, rows):
        self.rows = {k: list(v) for k, v in rows.items()}
        self.writes = []
        self.runs = []
        self.result = []
        self.rowcount = 0

    # connection API
    def execute(self, sql, params=None):
        self._run(sql, params)
        return self

    def cursor(self):
        return self

    def transaction(self):
        snapshot = {k: list(v) for k, v in self.rows.items()}

        @contextlib.contextmanager
        def tx():
            try:
                yield
            except Exception:
                self.rows = snapshot
                raise

        return tx()

    def commit(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    # cursor API
    def fetchall(self):
        return self.result

    def fetchone(self):
        return self.result[0] if self.result else None

    def _run(self, sql, params):
        s = " ".join(sql.split()).lower()
        self.rowcount = 0
        if s.startswith("set "):
            return
        if "insert into analytics.rule_run" in s:
            self.runs.append(params[2])
            self.result = [(f"run-{len(self.runs)}",)]
            return
        if "update analytics.rule_run" in s:
            self.rowcount = 1
            return
        if s.startswith("select id, company_id, period_end"):
            self.result = [(i, *r) for i, r in self.rows.items() if i in params[0]]
            return
        if "set value = null" in s:
            reason, mid, before = params
            r = self.rows.get(mid)
            if r is not None and r[3] is not None and Decimal(r[3]) == Decimal(before):
                r[3], r[4], r[5] = None, reason, None
                self.rowcount = 1
                self.writes.append(("hide", mid))
            return
        if "set value = %s::numeric" in s:
            value, reason, sources, mid, hidden_reason = params
            r = self.rows.get(mid)
            if r is not None and r[3] is None and r[4] == hidden_reason:
                r[3], r[4], r[5] = Decimal(value), reason, sources
                self.rowcount = 1
                self.writes.append(("restore", mid))
            return
        raise AssertionError(sql)


ROWS = {
    11: [1, date(2026, 6, 30), "Q2", Decimal("2.075"), None, [5, 6]],
    12: [1, date(2026, 3, 31), "Q1", Decimal("1.9"), None, [7]],
    21: [2, date(2025, 12, 31), "FY", Decimal("1.138"), None, [8]],
}


def _package(tmp_path, rows=ROWS):
    plan = [
        {
            "company_id": 1,
            "period_end": "2026-06-30",
            "period_label": "Q2",
            "stored": "2.075",
            "reason": REASON,
        },
        {
            "company_id": 2,
            "period_end": "2025-12-31",
            "period_label": "FY",
            "stored": "1.138",
            "reason": REASON,
        },
        {
            "company_id": 2,
            "period_end": "2024-12-31",
            "period_label": "FY",
            "stored": "1.0",
            "reason": REASON,
        },
    ]

    class BuildConn(FakeDB):
        def _run(self, sql, params):
            if "join core.company c" in " ".join(sql.split()).lower():
                ciks = {1: "0000000001", 2: "0000000002"}
                self.result = [
                    (i, r[0], r[1], r[2], r[3], r[4], r[5], ciks[r[0]])
                    for i, r in rows.items()
                ]
                return
            super()._run(sql, params)

    manifest = qr.build(BuildConn(rows), plan, [1, 2], tmp_path)
    return manifest


def test_build_writes_cells_before_image_keep_list_stale_and_touched_ciks(tmp_path):
    m = _package(tmp_path)
    assert (m["cells"], m["companies"], m["keep_cells"], m["stale_at_build"]) == (
        2,
        2,
        1,
        1,
    )
    assert (tmp_path / "touched_ciks.txt").read_text() == "0000000001\n0000000002\n"
    keep = [
        json.loads(x) for x in (tmp_path / "keep_list.jsonl").read_text().splitlines()
    ]
    assert [k["metric_value_id"] for k in keep] == [
        12
    ]  # evaluated, not in the plan: stays
    before = [
        json.loads(x)
        for x in (tmp_path / "before_image.jsonl").read_text().splitlines()
    ]
    assert before[0] == {
        "metric_value_id": 11,
        "value": "2.075",
        "is_null_reason": None,
        "source_fact_ids": [5, 6],
    }
    assert m["digest"] == qr.file_sha256(tmp_path / "cells.jsonl")


def test_apply_refuses_without_the_rule_the_token_or_the_reviewed_digest(tmp_path):
    m = _package(tmp_path)
    db = FakeDB(ROWS)
    with pytest.raises(qr.ReleaseRefused, match="not ON"):
        qr.apply(db, tmp_path, m["digest"], qr.CONFIRM_TOKEN, environ={})
    with pytest.raises(qr.ReleaseRefused, match="confirm"):
        qr.apply(db, tmp_path, m["digest"], "yes", environ=ON)
    with pytest.raises(qr.ReleaseRefused, match="reviewed digest"):
        qr.apply(db, tmp_path, "0" * 64, qr.CONFIRM_TOKEN, environ=ON)
    (tmp_path / "cells.jsonl").write_text((tmp_path / "cells.jsonl").read_text() + "\n")
    with pytest.raises(qr.ReleaseRefused, match="PACKAGE.json digest"):
        qr.apply(db, tmp_path, m["digest"], qr.CONFIRM_TOKEN, environ=ON)
    assert db.writes == [] and db.runs == []


def test_a_stale_cell_refuses_the_whole_run_before_any_write(tmp_path):
    m = _package(tmp_path)
    for drift in (
        {
            21: [2, date(2025, 12, 31), "FY", Decimal("1.2"), None, [8]]
        },  # recomputed value
        {21: [2, date(2025, 12, 31), "FY", Decimal("1.138"), None, [9]]},
    ):  # same value, new sources
        db = FakeDB({**ROWS, **drift})
        assert (
            qr.dry_run(db, qr.load_package(tmp_path, m["digest"]))["would_apply"]
            is False
        )
        with pytest.raises(qr.ReleaseRefused, match="stale"):
            qr.apply(db, tmp_path, m["digest"], qr.CONFIRM_TOKEN, environ=ON)
        assert db.writes == [] and db.runs == []
    gone = FakeDB({k: v for k, v in ROWS.items() if k != 11})
    with pytest.raises(qr.ReleaseRefused, match="stale"):
        qr.apply(gone, tmp_path, m["digest"], qr.CONFIRM_TOKEN, environ=ON)


def test_apply_hides_exactly_the_package_cells_and_restore_puts_them_back(tmp_path):
    m = _package(tmp_path)
    db = FakeDB(ROWS)
    out = qr.apply(db, tmp_path, m["digest"], qr.CONFIRM_TOKEN, environ=ON)
    assert out["hidden"] == 2 and db.runs == ["apply"]
    assert db.rows[11][3:] == [None, REASON, None] and db.rows[21][3:] == [
        None,
        REASON,
        None,
    ]
    assert db.rows[12] == ROWS[12]  # keep-list cell untouched
    back = qr.restore(db, tmp_path, out["run_id"], qr.CONFIRM_TOKEN)
    assert (
        back["restored"] == 2
        and back["skipped"] == []
        and db.runs == ["apply", "rollback"]
    )
    assert db.rows == {k: list(v) for k, v in ROWS.items()}


def test_restore_skips_a_row_no_longer_in_the_hidden_state(tmp_path):
    m = _package(tmp_path)
    db = FakeDB(ROWS)
    qr.apply(db, tmp_path, m["digest"], qr.CONFIRM_TOKEN, environ=ON)
    db.rows[21][3:] = [
        Decimal("0.5"),
        None,
        [1],
    ]  # the nightly rewrote it after the apply
    back = qr.restore(db, tmp_path, "run-1", qr.CONFIRM_TOKEN)
    assert (
        back["restored"] == 1
        and back["skipped"] == [21]
        and db.rows[21][3] == Decimal("0.5")
    )


def test_a_row_changed_between_the_check_and_the_write_rolls_its_batch_back(tmp_path):
    m = _package(tmp_path)

    class Racing(FakeDB):
        def _run(self, sql, params):
            super()._run(sql, params)
            if (
                " ".join(sql.split())
                .lower()
                .startswith("select id, company_id, period_end")
            ):
                self.rows[21][3] = Decimal(
                    "1.5"
                )  # the nightly rewrites it right after the stale check

    db = Racing(ROWS)
    with pytest.raises(qr.ReleaseRefused, match="changed since the check"):
        qr.apply(db, tmp_path, m["digest"], qr.CONFIRM_TOKEN, environ=ON)
    assert db.rows[11] == ROWS[11]  # same batch: rolled back with it
