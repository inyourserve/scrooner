"""Approver re-cert token for the top100-flow certified-guard (CERT-REGISTRY rulings 2026-11-21, item 15).

The script is invoked as the flow invokes it: `python3 -I scripts/ci/recert_token.py --ticker T`.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
SCRIPT = REPO / "scripts" / "ci" / "recert_token.py"


def _approvals(tmp_path: Path, *, certs=(), tokens=()) -> Path:
    a = tmp_path / "approvals"
    (a / "certificates").mkdir(parents=True)
    (a / "recert").mkdir()
    for name, certified_at, coverage in certs:
        (a / "certificates" / name).write_text(
            json.dumps({"certified_at": certified_at, "coverage_path": coverage})
        )
    for name in tokens:
        (a / "recert" / name).write_text("token")
    return a


def _run(a: Path, ticker="JNJ"):
    r = subprocess.run(
        [sys.executable, "-I", str(SCRIPT), "--approvals", str(a), "--ticker", ticker],
        capture_output=True,
        text=True,
    )
    return r.returncode, r.stdout.strip()


JNJ_CERT = (
    "JNJ-aaa.json",
    "2026-11-21",
    "data-team/strategy/certification/JNJ-coverage-2026-11-16.csv",
)


def test_token_newer_than_certificate_lets_the_company_through(tmp_path):
    # JNJ on main: certificate certified 2026-11-21 from the 11-16 export, token dated the same day
    a = _approvals(tmp_path, certs=[JNJ_CERT], tokens=["JNJ-2026-11-21.md"])
    rc, out = _run(a)
    assert rc == 0 and out.endswith("recert/JNJ-2026-11-21.md")


def test_no_token_is_held_as_before(tmp_path):
    assert _run(_approvals(tmp_path, certs=[JNJ_CERT]))[0] == 1


def test_stale_token_is_held(tmp_path):
    # a certificate issued after the token
    a = _approvals(
        tmp_path,
        certs=[
            (
                "JNJ-b.json",
                "2026-11-23",
                "data-team/strategy/certification/JNJ-coverage-2026-11-16.csv",
            )
        ],
        tokens=["JNJ-2026-11-21.md"],
    )
    assert _run(a)[0] == 1


def test_token_is_consumed_once_a_newer_certificate_exists(tmp_path):
    # the re-certification (export dated on or after the token) is on file: the token is spent
    a = _approvals(
        tmp_path,
        certs=[
            JNJ_CERT,
            (
                "JNJ-c.json",
                "2026-11-21",
                "data-team/strategy/certification/JNJ-coverage-2026-11-21.csv",
            ),
        ],
        tokens=["JNJ-2026-11-21.md"],
    )
    assert _run(a)[0] == 1


def test_another_companys_token_does_not_pass(tmp_path):
    a = _approvals(tmp_path, certs=[JNJ_CERT], tokens=["GILD-2026-11-21.md"])
    assert _run(a)[0] == 1


def test_the_real_jnj_token_on_main_is_spent_by_the_newer_pass():
    """The real state on main: JNJ's re-cert token (recert/JNJ-2026-11-21.md) was consumed by the 2026-11-22 PASS
    (JNJ-certificate-2026-11-22.md, a certificate made from a coverage export dated after the token), so no token is
    pending and the guard applies again. Asserts the files that make it so, then the script's answer."""
    approvals = REPO / "data-team/strategy/approvals"
    assert (approvals / "recert" / "JNJ-2026-11-21.md").exists()
    covs = []
    for p in (approvals / "certificates").glob("JNJ-*.json"):
        d = json.loads(p.read_text())
        covs.append((str(d.get("certified_at", "")), str(d.get("coverage_path", ""))))
    assert max(covs)[0] >= "2026-11-21"  # a certificate at or after the token date exists
    r = subprocess.run(
        [sys.executable, "-I", str(SCRIPT), "--approvals", str(approvals), "--ticker", "JNJ"],
        capture_output=True,
        text=True,
        cwd=REPO,
    )
    assert r.returncode == 1 and r.stdout == ""


def test_flow_wires_the_token_and_the_request_cites_it():
    flow = (REPO / "scripts" / "top100_flow.sh").read_text()
    assert "scripts/ci/recert_token.py" in flow and "RECERT_TOKEN=" in flow
    # the token check sits before the guard call, and the guard is skipped for a token company
    assert flow.index("recert_token.py") < flow.index("jobs.map certified-guard")
    wf = (REPO / ".github" / "workflows" / "top100-flow.yml").read_text()
    assert "--recert-token" in wf
    gate = (REPO / "scripts" / "ci" / "top100_gate.py").read_text()
    assert "re-cert token" in gate and "a.recert_token" in gate
