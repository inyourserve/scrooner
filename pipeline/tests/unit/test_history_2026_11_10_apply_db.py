"""The tranche-1 apply script end to end on a migrated scratch database (CI: Postgres 16, every migration replayed)."""

from __future__ import annotations

import csv
import os
import subprocess
import sys
from pathlib import Path

import psycopg
import pytest

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "data-team/42-release-applies-2026-11-10/apply_history_2026_11_10.py"
SOURCES = ROOT / "data-team/47-fsn-store/company_history_sources.csv"
PERIODS = ROOT / "data-team/47-fsn-store/company_history_periods.csv"
INSERT = """insert into core.company_history_source
    (company_id, source_cik, relation, source_name, valid_from, valid_to, reason, evidence)
    values (%s, %s, %s, %s, %s, %s, %s, %s)"""


def _seed(url: str) -> None:
    rows = list(csv.DictReader(open(SOURCES)))
    with psycopg.connect(url) as conn:
        for cid in sorted({int(r["company_id"]) for r in rows}):
            conn.execute(
                "insert into core.company (id, cik, company_name) overriding system value values (%s, %s, %s)",
                (cid, f"9{cid:09d}", f"TEST CO {cid}"),
            )
        for r in rows[:40]:  # the 40 rows live today (the CSV continues with the 26 new ones)
            conn.execute(INSERT, (int(r["company_id"]), r["source_cik"], r["relation"], r["source_name"], r["valid_from"], r["valid_to"], r["reason"], r["evidence"] or None))


def _run(url: str, before: Path, *extra: str) -> subprocess.CompletedProcess:
    env = {**os.environ, "DATABASE_URL": url}
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(SOURCES), str(PERIODS), str(before), *extra],
        env=env, capture_output=True, text=True, timeout=300,
    )


def _count(url: str) -> tuple[int, int]:
    with psycopg.connect(url) as conn:
        n = conn.execute("select count(*) from core.company_history_source").fetchone()[0]
        probe = conn.execute("select count(*) from core.company_history_source where source_cik = '0000000001'").fetchone()[0]
    return n, probe


@pytest.mark.integration
def test_apply_inserts_12_rows_and_the_predecessor_periods(isolated_database_url, tmp_path):
    _seed(isolated_database_url)
    got = _run(isolated_database_url, tmp_path)
    assert got.returncode == 0, got.stdout + got.stderr
    assert _count(isolated_database_url) == (66, 0)
    with psycopg.connect(isolated_database_url) as conn:
        per = dict(conn.execute("select company_id, count(*) from core.period group by 1").fetchall())
    assert per == {3639: 11, 5779: 18}
    ids = (tmp_path / "created_period_ids.txt").read_text().split()
    assert len(ids) == 29
    assert (tmp_path / "core_period_3639.csv").exists() and (tmp_path / "core_period_5779.csv").exists()
    again = _run(isolated_database_url, tmp_path)  # a second run is refused: live count is no longer 40
    assert again.returncode != 0 and _count(isolated_database_url)[0] == 66


@pytest.mark.integration
@pytest.mark.parametrize("break_trigger", [
    "alter table core.company_history_source disable trigger trg_company_history_source_no_overlap",
    "create or replace function core.company_history_source_no_overlap() returns trigger language plpgsql as $$ begin return new; end; $$",
], ids=["trigger_disabled", "trigger_does_not_refuse"])
def test_apply_rolls_back_everything_when_the_overlap_guard_fails(isolated_database_url, tmp_path, break_trigger):
    _seed(isolated_database_url)
    with psycopg.connect(isolated_database_url, autocommit=True) as conn:
        conn.execute(break_trigger)
    got = _run(isolated_database_url, tmp_path)
    assert got.returncode != 0, got.stdout
    assert _count(isolated_database_url) == (40, 0)
    with psycopg.connect(isolated_database_url) as conn:
        assert conn.execute("select count(*) from core.period").fetchone()[0] == 0
