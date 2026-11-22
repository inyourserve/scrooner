"""top100_gate request file: the resolver line names the company's resolver file, its resolver_version and sha256
(the WMT 2026-11-21 request said only `data-team/tags/line_map/resolver`, a directory). The script is invoked as the
top100-flow workflow invokes it: `python3 -I scripts/ci/top100_gate.py ... --resolver DIR`. Mutation: drop the sha256 line and this fails."""

from __future__ import annotations

import csv
import hashlib
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
SCRIPT = REPO / "scripts" / "ci" / "top100_gate.py"


def test_request_names_the_resolver_version_and_hash(tmp_path):
    res = tmp_path / "resolver"
    res.mkdir()
    rf = res / "T.csv"
    rf.write_text(
        "cik,ticker,data_point,period_end,resolver_version\n"
        "1,T,revenue,2024-12-31,resolver-all110-.89\n1,T,net_income,2024-12-31,resolver-all110-.89\n"
    )
    cov = tmp_path / "cov.csv"
    cols = [
        "company_id",
        "ticker",
        "data_point",
        "fiscal_year",
        "display",
        "accession",
        "r_page",
        "parts",
        "reason_code",
    ]
    with open(cov, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerow(
            dict(
                company_id="7",
                ticker="T",
                data_point="revenue",
                fiscal_year="2024",
                display="SHOWN_VALUE",
                accession="0000000001-25-000001",
                r_page="R4.htm",
                parts="",
                reason_code="",
            )
        )
    out = tmp_path / "out"
    p = subprocess.run(
        [
            sys.executable,
            "-I",
            str(SCRIPT),
            "--coverage-csv",
            str(cov),
            "--company-id",
            "7",
            "--out-dir",
            str(out),
            "--resolver",
            str(res),
            "--prove-py",
            str(REPO / "pipeline/src/scrooner_pipeline/proof/prove.py"),
        ],
        capture_output=True,
        text=True,
        cwd=REPO,
    )
    assert p.returncode == 0, p.stdout + p.stderr
    req = next(out.glob("T-request-*.md")).read_text()
    lines = dict(ln.split(": ", 1) for ln in req.splitlines() if ln.startswith("- resolver"))
    assert str(rf) in lines["- resolver file"] and "resolver-all110-.89" in lines["- resolver_version"]
    assert hashlib.sha256(rf.read_bytes()).hexdigest() in lines["- resolver sha256"]
