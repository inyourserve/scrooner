"""Weekly certified re-check (SYSTEMS.md #14/#15; workflow certified-recheck-weekly.yml).

Every company whose latest registry.csv verdict is PASS is re-run through certify_display's
mechanical checks (display_cert.certify(..., mechanical=True): gate, hide classes and hide proofs,
badges, total_debt census, derived and combined census; no new draw) on its CURRENT coverage export.
A company that no longer passes, or that is missing from the export, gets a regression entry
data-team/strategy/approvals/regressions/<TICKER>-<date>.md. It never writes a verdict: the
approver (Ritwik) decides what the regression means for the certificate.

Pure apart from the injected fact-source factory, so the same code runs live and in tests.
"""

from __future__ import annotations

import csv
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from scrooner_pipeline.certification import display_cert as dc


@dataclass(frozen=True)
class Result:
    ticker: str
    status: str  # PASS | REGRESSION | ERROR
    detail: str
    entry: Path | None = None  # regression file written


def company_ids(summary_csv: Path, tickers: list[str]) -> dict[str, int]:
    """ticker -> core.company id from the committed coverage summary. A certified ticker not in it
    is an error (it cannot be re-checked), never a silent skip."""
    with open(summary_csv, newline="") as fh:
        ids = {r["ticker"]: int(r["company_id"]) for r in csv.DictReader(fh)}
    missing = [t for t in tickers if t not in ids]
    if missing:
        raise ValueError(f"certified tickers not in {summary_csv}: {missing}")
    return {t: ids[t] for t in tickers}


def split_export(
    export_csv: Path, tickers: list[str], out_dir: Path
) -> dict[str, Path]:
    """One per-company coverage file per certified ticker found in the export (same header)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(export_csv, newline="") as fh:
        rd = csv.DictReader(fh)
        fields = rd.fieldnames or []
        rows: dict[str, list[dict]] = {t: [] for t in tickers}
        for r in rd:
            if r.get("ticker") in rows:
                rows[r["ticker"]].append(r)
    paths = {}
    for t, rs in rows.items():
        if not rs:
            continue
        p = out_dir / f"{t}-current-coverage.csv"
        with open(p, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=fields)
            w.writeheader()
            w.writerows(rs)
        paths[t] = p
    return paths


def _entry(
    t: str, today: str, body: str, certified_sha: str, current_sha: str | None
) -> str:
    return "\n".join(
        [
            f"# Certified regression: {t}, {today}",
            "",
            "Opened by the weekly certified re-check (certified-recheck-weekly.yml). The company's latest registry.csv "
            "verdict is PASS, but its current coverage export no longer passes certify_display's mechanical checks "
            "(no new draw). The certificate is in doubt until the approver re-certifies or rules on the findings below.",
            "",
            f"- certified coverage sha256: `{certified_sha}`",
            f"- current coverage sha256: `{current_sha or 'none (company missing from the export)'}`",
            "",
            body,
            "",
        ]
    )


def recheck(
    registry: Path,
    export_csv: Path,
    ciks: dict[str, str],
    source_for: Callable[[str], dc.FactSource],
    work_dir: Path,
    regressions_dir: Path,
    today: str,
) -> list[Result]:
    """Re-check every certified ticker. ciks: ticker -> CIK; source_for(ticker) -> fact source."""
    rows = {r["ticker"]: r for r in dc.latest_rows(dc._read_rows(registry))}
    tickers = dc.certified_tickers(registry)
    files = split_export(export_csv, tickers, work_dir)
    out: list[Result] = []
    for t in tickers:
        sha = rows[t].get("coverage_sha256", "")
        try:
            if t not in files:
                body = "**FAIL**: the certified company has no rows in the current coverage export."
                status, cur, detail = "REGRESSION", None, "missing from the export"
            else:
                run = dc.certify(t, ciks[t], files[t], source_for(t), mechanical=True)
                cur = run.coverage_sha256
                if run.verdict == "PASS":
                    out.append(Result(t, "PASS", "mechanical checks pass"))
                    continue
                status, detail = "REGRESSION", f"mechanical {run.verdict}"
                body = dc.render(run, today, "weekly certified re-check")
        except Exception as exc:  # a broken source or bad input is loud, never a pass
            out.append(Result(t, "ERROR", f"{type(exc).__name__}: {exc}"))
            continue
        regressions_dir.mkdir(parents=True, exist_ok=True)
        p = regressions_dir / f"{t}-{today}.md"
        p.write_text(_entry(t, today, body, sha, cur))
        out.append(Result(t, status, detail, p))
    return out


def exit_code(results: list[Result]) -> int:
    """0 every certified company passes; 1 a regression; 2 an error (a re-check that could not run)."""
    if any(r.status == "ERROR" for r in results):
        return 2
    return 1 if any(r.status == "REGRESSION" for r in results) else 0
