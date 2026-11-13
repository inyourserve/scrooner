"""A proof run must fail loudly, never degrade to UNCHECKED, when zstd is missing or fails
(incident 2026-11-13: minimal PATH under xargs wrote 172,228 UNCHECKED over cell_proof)."""

from __future__ import annotations

import contextlib
import shutil
from pathlib import Path

import pytest
from typer.testing import CliRunner

from scrooner_pipeline.jobs import proof as job
from scrooner_pipeline.proof import fsn, runner


class _Cur:
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def execute(self, *a, **k):
        pass

    def fetchall(self):
        return [("0000000001", 1)]


class _Conn:
    autocommit = False

    def commit(self):
        pass

    def rollback(self):
        pass

    def execute(self, *_a, **_k):
        pass

    def cursor(self):
        return _Cur()


@contextlib.contextmanager
def _fake_conn():
    yield _Conn()


def _patch_job(monkeypatch, calls):
    monkeypatch.setattr(job, "get_connection", _fake_conn)
    monkeypatch.setattr(runner, "write_proofs", lambda *a, **k: calls.append("upsert"))
    monkeypatch.setattr(runner, "table_exists", lambda c: True)


def test_missing_zstd_exits_nonzero_and_never_upserts(monkeypatch):
    calls: list[str] = []
    _patch_job(monkeypatch, calls)
    monkeypatch.setattr(shutil, "which", lambda *_a, **_k: None)
    res = CliRunner().invoke(job.app, ["run", "--ciks", "1", "--write"])
    assert res.exit_code != 0
    assert calls == []


def test_decompress_failure_aborts_before_upsert(monkeypatch, tmp_path: Path):
    calls: list[str] = []
    _patch_job(monkeypatch, calls)
    monkeypatch.setattr(runner, "require_zstd", lambda: "zstd")

    def fake_prove(conn, company_id, cache, floor):
        # as StructureCache would: zstd exits non-zero while reading a quarter
        monkeypatch.setattr(
            fsn.subprocess,
            "Popen",
            lambda *a, **k: (_ for _ in ()).throw(FileNotFoundError("zstd")),
        )
        runner.StructureCache(tmp_path).get_many({"2020q1": {"a"}})
        return []

    monkeypatch.setattr(runner, "prove_company", fake_prove)
    monkeypatch.setattr(
        runner,
        "load_quarter",
        lambda root, q, acc: list(fsn._zst_rows(tmp_path / "x.zst")),
    )
    with pytest.raises(fsn.DecompressError):
        runner.run(_Conn(), {"0000000001"}, fsn_root=tmp_path, write=True)
    assert calls == []


def test_bucket_absence_stays_distinct(monkeypatch, tmp_path: Path):
    def absent(*_a, **_k):
        raise FileNotFoundError("bucket 404")

    monkeypatch.setattr(runner, "load_quarter", absent)
    cache = runner.StructureCache(tmp_path)
    assert cache.get_many({"2020q1": {"a"}}) == {}
    assert cache.missing_quarters == {"2020q1"}
