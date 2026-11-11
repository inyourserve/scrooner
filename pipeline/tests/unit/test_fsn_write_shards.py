"""pipeline/scripts/fsn_write_shards.py, run the way pipeline-fsn-write.yml runs it (Ritwik 2026-11-10: the
`ciks` input for reloading the 98 companies lost in run 42561798991's dead shards)."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "pipeline" / "scripts" / "fsn_write_shards.py"
COHORT = (
    ROOT / "data-team" / "strategy" / "data" / "cohort_v1_1_proposal_2026-10-24.csv"
)


def _run(stage: str, shards: str, limit: str, ciks: str):
    res = subprocess.run(
        [sys.executable, str(SCRIPT), str(COHORT), stage, shards, limit, ciks],
        capture_output=True,
        text=True,
    )
    out = dict(line.split("=", 1) for line in res.stdout.splitlines() if "=" in line)
    return res, out


def _cohort():
    with COHORT.open() as fh:
        return list(csv.DictReader(fh))


def _planned(out):
    return [c for s in json.loads(out["shards"]) for c in s["ciks"].split(",")]


@pytest.mark.unit
def test_a_cik_list_overrides_cohort_and_limit_and_is_company_disjoint():
    rows = _cohort()
    picked = [rows[500], rows[3], rows[999]]
    ciks = ",".join(str(int(r["cik"])) for r in picked)  # unpadded, as typed
    res, out = _run("load_map", "4", "100", ciks)
    assert res.returncode == 0, res.stderr
    want = sorted(r["cik"].zfill(10) for r in picked)
    assert sorted(_planned(out)) == want  # limit 100 ignored: rank 1000 is planned
    for s in json.loads(out["shards"]):
        for c in s["ciks"].split(","):
            cid = next(int(r["company_id"]) for r in rows if r["cik"].zfill(10) == c)
            assert cid % 3 == s["i"]  # n = min(shards, companies) = 3
    assert out["ciks_sha256"] == hashlib.sha256(",".join(want).encode()).hexdigest()
    assert f"companies: 3; first {want[0]}, last {want[-1]}" in res.stderr


@pytest.mark.unit
def test_an_empty_list_means_the_cohort_path():
    res, out = _run("select_write", "16", "", "")
    assert res.returncode == 0, res.stderr
    assert len(_planned(out)) == len(_cohort())
    assert out["ciks_sha256"] == ""
    res, out = _run("load_map", "4", "10", "")
    assert sorted(_planned(out)) == sorted(r["cik"].zfill(10) for r in _cohort()[:10])


@pytest.mark.unit
def test_a_cik_outside_the_cohort_or_a_list_with_another_stage_fails():
    inside = _cohort()[0]["cik"]
    res, out = _run("load_map", "4", "", f"{inside},0000000001")
    assert res.returncode == 1 and "outside cohort v1.1: 0000000001" in res.stderr
    assert "shards" not in out
    for stage in ("select_write", "select_plan", "restore"):
        res, out = _run(stage, "4", "", inside)
        assert res.returncode == 1 and "only with stage load_map" in res.stderr
        assert "shards" not in out
