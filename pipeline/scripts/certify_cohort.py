"""File a cohort certificate request (certification/cohort_cert.py; Stage 5 Certify, M3). Read-only on the DB.

  # draw only (no DB): the strata and the drawn cells, to check a seed reproduces a request's draw
  python pipeline/scripts/certify_cohort.py --coverage top100-coverage.csv --cohort top100 --draw-only --out-dir OUT

  # live: the per-company judge on every company with its drawn cells; one connection, statement_timeout per query
  python pipeline/scripts/certify_cohort.py --coverage top100-coverage.csv --cohort top100 --live --out-dir OUT \
      --coverage-label "actions run 46167654745 artifact top100-coverage-46167654745/top100-coverage.csv"

  # after the queued cells are read (CSV: ticker, data_point, fiscal_year, verdict, reader, evidence)
  python pipeline/scripts/certify_cohort.py ... --live --reads READS.csv --seed <the request's seed>

Writes OUT/<cohort>-request-<date>.md (the request the approver reads), OUT/<cohort>-draw-<date>.csv (every drawn cell
and its outcome), OUT/<cohort>-reads-<date>.csv (the read queue, blank verdict/reader/evidence) and
OUT/<cohort>-exceptions-<date>.csv (exception_queue rows; load with `exception_queue load --extra-csv`). It never
writes a verdict, a registry row or a certificate: those are the approver's. Exit 0 when the request was written.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from scrooner_pipeline.certification import cohort_cert as cc
from scrooner_pipeline.certification import display_cert as dc

REPO = Path(__file__).resolve().parents[2]


def _code_sha() -> str:
    try:
        return subprocess.run(
            ["git", "-C", str(REPO), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument(
        "--coverage",
        type=Path,
        required=True,
        help="a multi-company export (top100-coverage.csv shape)",
    )
    ap.add_argument(
        "--cohort",
        required=True,
        help="cohort name, e.g. top100 (the id adds the company-set hash)",
    )
    ap.add_argument(
        "--coverage-label",
        help="how the request names the export (repo path or CI artifact)",
    )
    ap.add_argument(
        "--seed", help="default: <cohort id>-<first 12 hex of the export's sha256>"
    )
    ap.add_argument("--n", type=int, default=cc.COHORT_DRAW_SIZE)
    ap.add_argument(
        "--company-ids",
        help="comma-separated company ids: the cohort is only these companies",
    )
    ap.add_argument("--reads", type=Path)
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--live", action="store_true", help="read fsn.* over DATABASE_URL (read-only)"
    )
    mode.add_argument("--draw-only", action="store_true")
    ap.add_argument("--out-dir", type=Path, default=Path("."))
    ap.add_argument("--date", default=date.today().isoformat())
    ap.add_argument(
        "--timeout-ms", type=int, default=60000, help="statement_timeout of every query"
    )
    ap.add_argument(
        "--max-seconds", type=int, default=5400, help="wall-clock cap of the live run"
    )
    ap.add_argument("--preparer", default="cohort-cert preparer (agent)")
    a = ap.parse_args(argv)
    ids = [x.strip() for x in a.company_ids.split(",")] if a.company_ids else None
    a.out_dir.mkdir(parents=True, exist_ok=True)
    label = a.coverage_label or str(a.coverage)

    if a.draw_only:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            companies = cc.load_cohort(a.coverage, Path(tmp), ids)
            sha = dc.sha256(a.coverage)
            cid = cc.cohort_id(a.cohort, companies)
            seed = a.seed or f"{cid}-{sha[:12]}"
            drawn, strata = cc.draw_cohort(companies, seed, a.n)
        out = a.out_dir / f"{a.cohort}-draw-only-{a.date}.csv"
        cc.write_csv(
            out,
            ["ticker", "data_point", "fiscal_year", "stratum"],
            [
                {
                    "ticker": d.ticker,
                    "data_point": d.cell.data_point,
                    "fiscal_year": d.cell.fiscal_year,
                    "stratum": d.stratum,
                }
                for d in drawn
            ],
        )
        print(
            f"cohort {cid} sha {sha} seed {seed}: {len(drawn)} drawn over {len(strata)} strata -> {out}"
        )
        return 0

    from scrooner_pipeline.db.connection import get_connection

    t0 = time.monotonic()
    with get_connection() as conn:
        conn.read_only = True
        source = dc.SqlFactSource(conn, timeout_ms=a.timeout_ms)

        def cik_of(company_id: str) -> str:
            try:
                cik = dc.resolve_cik(conn, int(company_id))
            except ValueError:
                # fsn.filing holds a predecessor's CIK too (GOOGL: Google Inc. 1288776 and Alphabet 1652044): the
                # company's own CIK is core.company's (certify_display._company_cik)
                conn.rollback()
                with conn.cursor() as cur:
                    cur.execute("set statement_timeout = 15000")
                    cur.execute(
                        "select ltrim(cik, '0') from core.company where id = %s",
                        (int(company_id),),
                    )
                    row = cur.fetchone()
                if not row:
                    raise
                cik = str(row[0])
            conn.rollback()
            return cik

        def progress(ticker: str, run: dc.Run) -> None:
            conn.rollback()  # end each company's read transaction
            el = time.monotonic() - t0
            print(f"cohort {ticker}: {len(run.shown)} drawn, {el:.0f}s", flush=True)
            if el > a.max_seconds:
                raise TimeoutError(
                    f"wall-clock cap {a.max_seconds}s reached at {ticker}; no request written"
                )

        co = cc.judge(
            a.cohort,
            a.coverage,
            source,
            cik_of,
            a.seed,
            a.n,
            cc.load_cohort_reads(a.reads),
            ids,
            label,
            on_company=progress,
        )
    stem = f"{a.cohort}-cohort"
    files = {
        "drawn cells": a.out_dir / f"{stem}-draw-{a.date}.csv",
        "read queue": a.out_dir / f"{stem}-reads-{a.date}.csv",
        "exceptions": a.out_dir / f"{stem}-exceptions-{a.date}.csv",
    }
    cc.write_csv(files["drawn cells"], cc.CELL_COLUMNS, cc.cell_rows(co))
    cc.write_read_queue(files["read queue"], co)
    rel = {
        k: str(v.resolve().relative_to(REPO))
        if v.resolve().is_relative_to(REPO)
        else str(v)
        for k, v in files.items()
    }
    cc.write_exceptions(files["exceptions"], cc.exception_rows(co, rel["drawn cells"]))
    req = a.out_dir / f"{stem}-request-{a.date}.md"
    req.write_text(cc.render_request(co, a.date, _code_sha(), rel, a.preparer))
    print(
        f"cohort {co.cohort_id}: n={co.n}, errors={co.errors}, needs read={len(co.pending)}, "
        f"census FAIL={len(co.census_fail)}, status {co.status}, upper95 {co.upper():.4%}; wrote {req}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
