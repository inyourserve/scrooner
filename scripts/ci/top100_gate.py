#!/usr/bin/env python3
"""Per-company certification gate for the top100-flow workflow (founder rule 2026-11-16, doc 02 / 438677db;
method: data-team/strategy/approvals/CERTIFICATION-METHOD-2026-11-16.md).

Reads the coverage export of the flow run, keeps ONE company's rows and decides PASS / FAIL / SKIP.
It does not recompute display rules: the `display` column (SHOWN_VALUE / HIDDEN_ROW / HIDDEN_YEAR / OPEN) is
written by scrooner_pipeline.mapper.top100_coverage. Until that column exists the gate returns SKIP and writes
nothing to send.

PASS needs all of:
  0. at least one SHOWN_VALUE row (display_certified needs shown cells);
  1. zero rows with display == OPEN;
  2. every SHOWN_VALUE row has an accession and an R page, and every part in `parts`
     ("Tag=value@accession#Rpage;...") carries both;
  3. no SHOWN_VALUE row has reason_code no_public_filing_for_period or before_first_10k (a shown cell must be a
     value; those reasons are the evidence of a hidden year, so they are allowed only on HIDDEN_* rows).
On PASS it writes <out>/<TICKER>-coverage-<date>.csv and <out>/<TICKER>-request-<date>.md (hash, counts by display
class, proof DETECTOR_VERSION, run URL). Exit codes: 0 PASS, 1 FAIL, 3 SKIP (no display column), 2 usage/input error.
"""

import argparse
import csv
import datetime as dt
import hashlib
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path

BAD_REASONS = {"no_public_filing_for_period", "before_first_10k"}
ACC = re.compile(r"^\d{10}-\d{2}-\d{6}$")
PART = re.compile(r"@(\d{10}-\d{2}-\d{6})#(R\d+(?:\.htm)?)$")


def detector_version(prove_py: Path) -> str:
    m = re.search(r'^DETECTOR_VERSION\s*=\s*"([^"]+)"', prove_py.read_text(), re.M)
    return m.group(1) if m else "unknown"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--coverage-csv", required=True)
    ap.add_argument("--company-id", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--prove-py", default="pipeline/src/scrooner_pipeline/proof/prove.py")
    ap.add_argument("--resolver", default="")
    a = ap.parse_args()
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    with open(a.coverage_csv, newline="") as fh:
        rd = csv.DictReader(fh)
        fields = rd.fieldnames or []
        rows = [r for r in rd if r.get("company_id") == a.company_id]
    if not rows:
        print(f"gate ERROR: no rows for company_id {a.company_id}")
        (out / "gate.json").write_text(json.dumps({"decision": "ERROR", "reason": "no rows"}))
        return 2
    ticker = rows[0]["ticker"]
    if "display" not in fields:
        print(f"gate SKIP {ticker}: coverage export has no display column yet; nothing sent")
        (out / "gate.json").write_text(json.dumps({"decision": "SKIP", "ticker": ticker, "reason": "no display column"}))
        return 3

    counts = Counter(r["display"] for r in rows)
    fails: list[str] = []
    if not counts.get("SHOWN_VALUE"):
        fails.append("no shown cells (same as display_certified = no)")
    if counts.get("OPEN"):
        fails.append(f"{counts['OPEN']} OPEN cell(s)")
    no_loc = bad_part = bad_reason = 0
    examples: list[str] = []
    for r in rows:
        if r["display"] != "SHOWN_VALUE":
            continue
        key = f"{r['data_point']} FY{r['fiscal_year']}"
        if not ACC.match(r.get("accession", "")) or not r.get("r_page"):
            no_loc += 1
            examples.append(f"no accession/R page: {key}")
        for p in filter(None, (r.get("parts") or "").split(";")):
            if not PART.search(p):
                bad_part += 1
                examples.append(f"part without accession#R page: {key} {p[:60]}")
        if r.get("reason_code") in BAD_REASONS:
            bad_reason += 1
            examples.append(f"shown cell with {r['reason_code']}: {key}")
    if no_loc:
        fails.append(f"{no_loc} shown cell(s) without accession or R page")
    if bad_part:
        fails.append(f"{bad_part} part(s) without accession or R page")
    if bad_reason:
        fails.append(f"{bad_reason} shown cell(s) carrying a no-filing reason")

    decision = "FAIL" if fails else "PASS"
    summary = {
        "decision": decision, "ticker": ticker, "company_id": a.company_id,
        "counts": dict(counts), "fails": fails, "examples": examples[:20],
    }
    (out / "gate.json").write_text(json.dumps(summary, indent=1))
    print(f"gate {decision} {ticker}: {dict(counts)} {'; '.join(fails)}")
    for e in examples[:10]:
        print("  ", e)
    if decision != "PASS":
        return 1

    today = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
    csv_path = out / f"{ticker}-coverage-{today}.csv"
    with open(csv_path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    digest = hashlib.sha256(csv_path.read_bytes()).hexdigest()
    run_url = "{}/{}/actions/runs/{}".format(
        os.environ.get("GITHUB_SERVER_URL", "https://github.com"),
        os.environ.get("GITHUB_REPOSITORY", ""), os.environ.get("GITHUB_RUN_ID", ""))
    lines = [
        f"# Certification request: {ticker} (company {a.company_id}), {today}",
        "",
        "Automatic, from the top100-flow workflow gate. Method: CERTIFICATION-METHOD-2026-11-16.md. "
        "The gate checked only the mechanical conditions below; the seeded shown-cell draw and hide checks are the approver's.",
        "",
        f"- coverage csv: `data-team/strategy/certification/{csv_path.name}`",
        f"- sha256: `{digest}`",
        f"- rows: {len(rows)}",
        "- cells by display class: " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())),
        f"- proof DETECTOR_VERSION: `{detector_version(Path(a.prove_py))}`",
        f"- resolver: `{a.resolver or 'unknown'}`",
        f"- code: `{os.environ.get('GITHUB_SHA', 'unknown')}`",
        f"- run: {run_url}",
        "- gate: 0 OPEN; every shown cell and part has an accession and R page; no no_public_filing_for_period or before_first_10k on a shown cell.",
        "",
    ]
    (out / f"{ticker}-request-{today}.md").write_text("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
