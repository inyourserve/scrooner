"""pipeline/scripts/fsn_shard_outcome.py, run the way the FSN write workflow runs it (a subprocess on out/)."""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "pipeline" / "scripts" / "fsn_shard_outcome.py"


def run(out: Path, ciks: str):
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(out), ciks],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )


def test_every_company_failed_turns_the_shard_red(tmp_path):
    """Run 42561798991: report.json was [] and failed.json held every company."""
    (tmp_path / "report.json").write_text("[]")
    (tmp_path / "failed.json").write_text(
        json.dumps([{"cik": "0000000001", "error": "QueryCanceled"}])
    )
    (tmp_path / "load.json").write_text(json.dumps({"errors": 0}))
    r = run(tmp_path, "0000000001")
    assert r.returncode == 1
    assert "::error::" in r.stdout and "::warning::1 of 1 companies failed" in r.stdout


def test_no_report_file_at_all_is_red(tmp_path):
    assert run(tmp_path, "0000000001,0000000002").returncode == 1


def test_some_failures_warn_but_pass(tmp_path):
    (tmp_path / "report.json").write_text(json.dumps([{"company_id": 2}]))
    (tmp_path / "failed.json").write_text(json.dumps([{"cik": "0000000001"}]))
    (tmp_path / "load.json").write_text(json.dumps({"errors": 3}))
    r = run(tmp_path, "0000000001,0000000002")
    assert r.returncode == 0
    assert (
        "::warning::1 of 2" in r.stdout
        and "::warning::3 companies failed to load" in r.stdout
    )
    assert "::error::" not in r.stdout


def test_clean_shard_passes_quietly(tmp_path):
    (tmp_path / "report.json").write_text(json.dumps([{"company_id": 1}]))
    (tmp_path / "failed.json").write_text("[]")
    r = run(tmp_path, "0000000001")
    assert r.returncode == 0 and "::" not in r.stdout
