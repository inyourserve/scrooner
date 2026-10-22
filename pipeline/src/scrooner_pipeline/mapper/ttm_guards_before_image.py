"""Before-image and restore check for RF-01 / RF-02 (read-only).

Design (WO-REVIEW-release-manager.md section 2, procedure steps 5-7):

  1. BEFORE a flag-on run for a set of CIKs, `export` saves the latest stored TTM
     row of every consumer metric of the two rules (value, reason, source fact
     ids) to a CSV and writes a manifest next to it (row count, sha256, DB
     watermark, git sha, the CIK list). Files above 5 MB are attached to the run
     as an artifact with the sha256 committed in the manifest, not committed.
  2. The flag-on run happens through the manual dispatch of pipeline-recompute.yml
     (rules_enabled input), never from here.
  3. ROLLBACK is a re-run of the same stages for the same CIKs with the flag OFF.
     The TTM rows are recomputed deterministically from stored inputs and
     upserted, so the legacy values come back without hand-written SQL.
  4. `compare` proves the rollback: it reads the current latest TTM rows for the
     CIKs and diffs them with the saved before-image on (company, metric, value,
     reason). Zero differences = restored. The comparison ignores period_end
     because these rows are stamped with the calculation date.

The rehearsal required by doc 49 section 2 condition 3 is: export, run the flag-on
stage for 10 CIKs on a scratch copy or the 10-company scope, run it again with the
flag off, `compare` must report 0 differences.

Nothing here writes to the database (read-only session, explicit statement_timeout).
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any

CONSUMER_METRICS = (
    "ebitda",
    "net_debt_ebitda",
    "ebitda_margin",
    "debt_to_ebitda",
    "ev_ebitda",
    "fcf_per_share",
    "share_repurchases_pct_fcf",
    "dividends_pct_fcf",
    "buyback_yield",
    "total_shareholder_yield",
)
FIELDS = [
    "company_id",
    "cik",
    "ticker",
    "metric_name",
    "period_label",
    "period_start",
    "period_end",
    "value",
    "is_null_reason",
    "source_fact_ids",
]
COMPARE_FIELDS = ("company_id", "metric_name", "value", "is_null_reason")


def _read_only_connection(
    statement_timeout_ms: int,
) -> Any:  # pragma: no cover - database
    import psycopg

    from scrooner_pipeline.common.config import settings

    return psycopg.connect(
        settings.database_url,
        options=f"-c statement_timeout={statement_timeout_ms} -c default_transaction_read_only=on",
        autocommit=True,
    )


def fetch_latest_ttm(
    conn: Any, ciks: list[str]
) -> list[dict[str, Any]]:  # pragma: no cover - database
    with conn.cursor() as cur:
        cur.execute(
            """
            select distinct on (mv.company_id, md.metric_name)
                   mv.company_id, c.cik, c.primary_ticker, md.metric_name, mv.period_label,
                   mv.period_start, mv.period_end, mv.value, mv.is_null_reason, mv.source_fact_ids
            from core.company c
            join analytics.metric_value mv on mv.company_id = c.id
            join analytics.metric_definition md on md.id = mv.metric_definition_id
            where c.cik = any(%s) and mv.period_label = 'TTM' and md.metric_name = any(%s)
            order by mv.company_id, md.metric_name, mv.period_end desc
            """,
            (ciks, list(CONSUMER_METRICS)),
        )
        return [dict(zip(FIELDS, row)) for row in cur.fetchall()]


def write_before_image(
    rows: list[dict[str, Any]], out: Path, meta: dict[str, Any]
) -> dict[str, Any]:
    with out.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        for r in sorted(rows, key=lambda x: (x["company_id"], x["metric_name"])):
            w.writerow({k: ("" if r[k] is None else r[k]) for k in FIELDS})
    digest = hashlib.sha256(out.read_bytes()).hexdigest()
    manifest = {
        **meta,
        "file": out.name,
        "rows": len(rows),
        "sha256": digest,
        "bytes": out.stat().st_size,
        "attach_as_artifact": out.stat().st_size > 5_000_000,
    }
    out.with_suffix(".manifest.json").write_text(
        json.dumps(manifest, indent=2, default=str)
    )
    return manifest


def _norm(value: Any) -> str:
    if value is None or value == "":
        return ""
    try:
        return str(Decimal(str(value)).normalize())
    except Exception:
        return str(value)


def diff_images(
    before: list[dict[str, Any]], after: list[dict[str, Any]]
) -> list[dict[str, str]]:
    """Differences on (company_id, metric_name) between two images, ignoring dates."""

    def keyed(rows: list[dict[str, Any]]) -> dict[tuple[str, str], dict[str, str]]:
        return {
            (str(r["company_id"]), r["metric_name"]): {
                "value": _norm(r.get("value")),
                "is_null_reason": ""
                if r.get("is_null_reason") in (None, "")
                else str(r["is_null_reason"]),
            }
            for r in rows
        }

    b, a = keyed(before), keyed(after)
    out = []
    for key in sorted(set(b) | set(a)):
        if b.get(key) != a.get(key):
            out.append(
                {
                    "company_id": key[0],
                    "metric_name": key[1],
                    "before": json.dumps(b.get(key)),
                    "after": json.dumps(a.get(key)),
                }
            )
    return out


def read_image(path: Path) -> list[dict[str, Any]]:
    with path.open(newline="") as fh:
        return list(csv.DictReader(fh))


def main(argv: list[str] | None = None) -> int:  # pragma: no cover - database
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("export", "compare"):
        p = sub.add_parser(name)
        p.add_argument(
            "--ciks",
            required=True,
            help="comma separated CIKs (10-digit, as in core.company.cik)",
        )
        p.add_argument("--image", required=True, type=Path)
        p.add_argument("--statement-timeout-ms", type=int, default=20000)
    sub.choices["compare"].add_argument("--diff-out", type=Path)
    args = ap.parse_args(argv)
    ciks = [c.strip() for c in args.ciks.split(",") if c.strip()]
    if len(ciks) > 100:
        print("at most 100 CIKs per image (chunk bigger scopes)", file=sys.stderr)
        return 2
    conn = _read_only_connection(args.statement_timeout_ms)
    rows = fetch_latest_ttm(conn, ciks)
    if args.cmd == "export":
        with conn.cursor() as cur:
            cur.execute("select now()")
            watermark = cur.fetchone()[0]
        sha = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=False,
            cwd=Path(__file__).resolve().parent,
        ).stdout.strip()
        manifest = write_before_image(
            rows,
            args.image,
            {
                "ciks": ciks,
                "db_watermark": str(watermark),
                "git_sha": sha,
                "taken_on": str(date.today()),
            },
        )
        print(json.dumps(manifest, indent=2, default=str))
        return 0
    diffs = diff_images(read_image(args.image), rows)
    if args.diff_out:
        with args.diff_out.open("w", newline="") as fh:
            w = csv.DictWriter(
                fh, fieldnames=["company_id", "metric_name", "before", "after"]
            )
            w.writeheader()
            w.writerows(diffs)
    print(f"differences: {len(diffs)}")
    return 0 if not diffs else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
