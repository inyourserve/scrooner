#!/usr/bin/env python3
"""Live cell extract (E0 / E1) for the scoreboard: Q0 + Q0b + K7 reference dates + K12 + K4b.

AUTHORED, NOT RUN (WO-7, 2026-10-22). Run only when scrooner-4d says so: E0 immediately before the
0096/0097 apply and rebuild; E1 immediately after. Needs the pipeline venv (psycopg):
  /Users/vikash/scrooner/pipeline/.venv/bin/python extract_live.py --authorised-by "<who/when>" --out-dir <dir>

Rules it enforces (it exits non-zero instead of continuing):
  * ONE connection, opened read only (default_transaction_read_only = on), statement_timeout = 60s
    (--statement-timeout-ms; never raised on a timeout: the chunk is halved instead, down to 5 ids).
  * Before EVERY statement batch: select count(*) from pg_stat_activity must be <= --max-connections (14).
  * Reads only the sources in the allowed list of the review (section 1.1). No write statement exists.
  * Never run beside a heavy job: --authorised-by is mandatory and is recorded in the header.
The connection string comes from pipeline/.env (DATABASE_URL) and is never printed.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sb_lib as L  # noqa: E402

SQL = L.SB_DIR / "sql"
MAX_CONN_DEFAULT = 14
CHUNK_BASE = 100
CHUNK_CANON = 25
MIN_CHUNK = 5


class GateError(RuntimeError):
    pass


def chunks(seq, n):
    seq = list(seq)
    for i in range(0, len(seq), n):
        yield seq[i : i + n]


def read_sql(name: str) -> str:
    """Executable statement text of a sql/ file: comment lines dropped, first statement only for
    single-statement files, the Q0 variant A/B handled by the caller."""
    lines = [
        ln
        for ln in (SQL / name).read_text().splitlines()
        if not ln.strip().startswith("--")
    ]
    return "\n".join(lines).strip()


def database_url(env_path: Path) -> str:
    for ln in env_path.read_text().splitlines():
        if ln.startswith("DATABASE_URL="):
            return ln.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("DATABASE_URL not found in " + str(env_path))


class Runner:
    def __init__(self, conn, max_conn: int, log):
        self.conn = conn
        self.max_conn = max_conn
        self.log = log

    def gate(self):
        with self.conn.cursor() as cur:
            cur.execute("select count(*) from pg_stat_activity")
            n = cur.fetchone()[0]
        if n > self.max_conn:
            raise GateError(
                f"pg_stat_activity={n} > {self.max_conn}: stop, do not retry through (CLAUDE.md)"
            )
        return n

    def run_chunked(self, sql: str, ids, base: int):
        """Run `sql` per chunk of ids; on a statement timeout halve the chunk (no timeout raise)."""
        out = []
        queue = list(chunks(ids, base))
        while queue:
            part = queue.pop(0)
            self.gate()
            t0 = time.time()
            try:
                with self.conn.cursor() as cur:
                    cur.execute(sql, {"ids": part})
                    out.extend(cur.fetchall())
                self.conn.rollback()  # read only: end the transaction each chunk
            except Exception as e:  # noqa: BLE001
                self.conn.rollback()
                if "canceling statement" in str(e) and len(part) > MIN_CHUNK:
                    half = max(MIN_CHUNK, len(part) // 2)
                    self.log(f"timeout on {len(part)} ids, halving to {half}")
                    queue = list(chunks(part, half)) + queue
                    continue
                raise
            self.log(f"chunk {len(part)} ids ok in {time.time() - t0:.1f}s")
        return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--authorised-by",
        required=True,
        help="who/when scrooner-4d released the slot (recorded)",
    )
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--label", default=datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    ap.add_argument(
        "--env", type=Path, default=L.REPO.parent / "scrooner/pipeline/.env"
    )
    ap.add_argument("--max-connections", type=int, default=MAX_CONN_DEFAULT)
    ap.add_argument("--statement-timeout-ms", type=int, default=60_000)
    ap.add_argument(
        "--plan-only", action="store_true", help="print the plan, open no connection"
    )
    a = ap.parse_args(argv)

    ids, _ = L.load_cohort()
    names = L.read_lines(L.D0_NAMES_FILE)
    n_batches = (
        len(list(chunks(ids, CHUNK_BASE)))
        + 2 * len(list(chunks(ids, CHUNK_CANON)))
        + 3 * len(list(chunks(ids, CHUNK_BASE)))
    )
    plan = {
        "companies": len(ids),
        "data_points": len(names),
        "approx_statements": n_batches,
        "statement_timeout_ms": a.statement_timeout_ms,
        "max_connections": a.max_connections,
    }
    if a.plan_only:
        print(json.dumps(plan, indent=1))
        return 0

    import psycopg  # only the pipeline venv has it

    a.out_dir.mkdir(parents=True, exist_ok=True)
    logf = open(a.out_dir / f"{a.label}.extract.log", "a")

    def log(m):
        line = f"{datetime.now(timezone.utc).isoformat()} {m}"
        logf.write(line + "\n")
        logf.flush()
        print(line)

    conn = psycopg.connect(database_url(a.env), autocommit=False)
    try:
        with conn.cursor() as cur:
            cur.execute("set default_transaction_read_only = on")
            cur.execute(f"set statement_timeout = {int(a.statement_timeout_ms)}")
        conn.commit()
        r = Runner(conn, a.max_connections, log)
        header = {
            "authorised_by": a.authorised_by,
            "started": datetime.now(timezone.utc).isoformat(),
            "connections_at_start": r.gate(),
        }
        with conn.cursor() as cur:
            cur.execute(
                "select max(checked_at) from analytics.company_data_point_coverage"
            )
            header["coverage_checked_at"] = str(cur.fetchone()[0])
            cur.execute("select max(snapshot_date) from analytics.coverage_snapshot")
            header["snapshot_date"] = str(cur.fetchone()[0])
            cur.execute("select max(checked_at) from analytics.period_gap")
            header["period_gap_checked_at"] = str(cur.fetchone()[0])
            cur.execute(
                "select to_regclass('analytics.company_certification') is not null"
            )
            header["certification_table_exists"] = cur.fetchone()[0]
            cur.execute(
                "select exists (select 1 from information_schema.columns where table_schema='analytics' "
                "and table_name='company_data_point_coverage' and column_name='has_value_any_period')"
            )
            has_any = cur.fetchone()[0]
            header["has_value_any_period_exists"] = has_any
            if header["certification_table_exists"]:
                cur.execute(
                    "select max(checks_run_at) from analytics.company_certification"
                )
                header["certification_checks_run_at"] = str(cur.fetchone()[0])
        conn.rollback()

        q0 = read_sql("Q0_base_cells.sql").split(";")[0] + ";"
        if has_any:
            q0 = q0.replace(
                "cov.has_value, cov.gap_reason, cov.checked_at",
                "cov.has_value, cov.gap_reason, cov.checked_at, cov.has_value_any_period",
            )
        base = r.run_chunked(q0.rstrip(";"), ids, CHUNK_BASE)
        cells = {}
        for row in base:
            cid, dp, typ, hv, reason, _chk = row[:6]
            cells[(cid, dp)] = {
                "type": typ,
                "has_value": bool(hv),
                "reason": reason or "",
                "any": (row[6] if has_any else None),
            }
        latest = {}
        for row in r.run_chunked(
            read_sql("Q0b_concept_latest_period.sql").rstrip(";"), ids, CHUNK_CANON
        ):
            latest[(row[0], row[1])] = (str(row[2]), row[3] or "")
        for row in r.run_chunked(
            read_sql("Q0b_metric_latest_period.sql").rstrip(";"), ids, CHUNK_CANON
        ):
            latest[(row[0], row[1])] = (str(row[2]), row[3] or "")
        ref = r.run_chunked(
            read_sql("K7_reference_end.sql").rstrip(";"), ids, CHUNK_BASE
        )
        k12a = r.run_chunked(
            read_sql("K12a_zero_fact_filings.sql").rstrip(";"), ids, CHUNK_BASE
        )
        k12b = r.run_chunked(
            read_sql("K12b_newest_filing_lag.sql").rstrip(";"), ids, CHUNK_BASE
        )
        k4b = r.run_chunked(
            read_sql("K4b_period_gaps.sql").rstrip(";"), ids, CHUNK_BASE
        )
        k4c = r.run_chunked(read_sql("K4c_findings.sql").split(";")[0], ids, CHUNK_BASE)
        header["finished"] = datetime.now(timezone.utc).isoformat()
    finally:
        conn.close()

    # ---- write files (a company or data point missing from the table is KEPT as absent_from_table)
    buf = [
        "company_id,data_point_name,data_point_type,has_value,has_value_any_period,gap_reason,"
        "latest_period_end,latest_label,absent_from_table"
    ]
    import io

    sio = io.StringIO()
    w = csv.writer(sio, lineterminator="\n")
    w.writerow(buf[0].split(","))
    for cid in ids:
        for dp in names:
            c = cells.get((cid, dp))
            if c is None:
                w.writerow([cid, dp, "", "f", "", "", "", "", "t"])
                continue
            le, ll = latest.get((cid, dp), ("", ""))
            if le == "None":
                le = ""
            w.writerow(
                [
                    cid,
                    dp,
                    c["type"],
                    "t" if c["has_value"] else "f",
                    "" if c["any"] is None else ("t" if c["any"] else "f"),
                    c["reason"],
                    le,
                    ll,
                    "f",
                ]
            )
    L.write_gz_deterministic(sio.getvalue(), a.out_dir / f"{a.label}.cells.csv.gz")
    with open(a.out_dir / f"{a.label}.ref_end.csv", "w", newline="") as fh:
        w2 = csv.writer(fh, lineterminator="\n")
        w2.writerow(["company_id", "ref_end"])
        for cid, ref_end in sorted(ref):
            w2.writerow([cid, ref_end])
    side = {
        "k12a_filings_by_company": {int(c): int(n) for c, n in k12a},
        "k12b_company_ids": sorted(int(c[0]) for c in k12b),
        "k4b": [[r_[0], r_[1], r_[2], int(r_[3])] for r_ in k4b],
        "k4c": [[r_[0], r_[1], int(r_[2])] for r_ in k4c],
    }
    (a.out_dir / f"{a.label}.side.json").write_text(json.dumps(side, sort_keys=True))
    (a.out_dir / f"{a.label}.header.json").write_text(
        json.dumps(header, indent=1, sort_keys=True)
    )
    log("done; nothing was written to the database")
    return 0


if __name__ == "__main__":
    sys.exit(main())
