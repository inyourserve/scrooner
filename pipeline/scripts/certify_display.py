"""Certify one company's display coverage export (CERTIFICATION-METHOD-2026-11-16.md).

No SEC downloads: every check reads SEC's Financial Statement and Notes data already held in fsn.*.

  # live (CI, or anywhere DATABASE_URL is set)
  python pipeline/scripts/certify_display.py --ticker BA --cik 12927 --coverage BA.csv --live --out-dir OUT

  # where only a SQL console reaches the database: emit the one read-only query, run it, save the JSON
  python pipeline/scripts/certify_display.py --ticker BA --cik 12927 --coverage BA.csv --emit-sql > ba.sql
  python pipeline/scripts/certify_display.py --ticker BA --cik 12927 --coverage BA.csv --bundle ba.json --out-dir OUT

Writes OUT/<TICKER>-display-cert-<date>.md (verdict), OUT/<TICKER>-display-cert-<date>-evidence.csv,
and appends one row to --registry (default data-team/strategy/approvals/registry.csv), printing the
pooled bound over every company whose latest row is PASS. Exit code 0 PASS, 1 FAIL, 2 REVIEW.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from scrooner_pipeline.certification import display_cert as dc

REPO = Path(__file__).resolve().parents[2]
DEFAULT_REGISTRY = REPO / "data-team/strategy/approvals/registry.csv"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument(
        "--request",
        type=Path,
        help="a requests/<T>-request-<date>.md file; sets ticker and coverage and checks the sha256",
    )
    ap.add_argument("--ticker")
    ap.add_argument(
        "--cik",
        help="needed without --live; with --live it is read from fsn.filing by company id",
    )
    ap.add_argument("--coverage", type=Path)
    ap.add_argument(
        "--seed", help="default: <TICKER>-<first 12 hex of the coverage file's sha256>"
    )
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--live", action="store_true", help="read fsn.* over DATABASE_URL")
    src.add_argument(
        "--bundle", type=Path, help="evidence bundle JSON from the --emit-sql query"
    )
    src.add_argument(
        "--emit-sql", action="store_true", help="print the bundle query and exit"
    )
    ap.add_argument("--out-dir", type=Path, default=Path("."))
    ap.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    ap.add_argument("--no-registry", action="store_true")
    ap.add_argument("--date", default=date.today().isoformat())
    a = ap.parse_args(argv)
    company_id = None
    if a.request:
        req = dc.read_request(a.request)
        a.ticker, company_id = req.ticker, req.company_id
        a.coverage = a.coverage or REPO / req.coverage
        if dc.sha256(a.coverage) != req.sha256:
            ap.error(
                f"{a.coverage}: sha256 differs from the request; the file changed after the gate ran"
            )
    if not (a.ticker and a.coverage):
        ap.error("give --request, or --ticker and --coverage")
    if not a.cik and not (a.live and company_id is not None):
        ap.error("--cik is required unless --live with --request")
    t = a.ticker.upper()

    if a.emit_sql:
        print(dc.bundle_sql(a.cik, dc.plan(t, a.coverage, a.seed)))
        return 0
    if a.live:
        from scrooner_pipeline.db.connection import get_connection

        with get_connection() as conn:
            assert a.cik or company_id is not None  # argparse checks above
            cik = a.cik or dc.resolve_cik(conn, company_id or 0)
            run = dc.certify(t, cik, a.coverage, dc.SqlFactSource(conn), a.seed)
    else:
        raw = json.loads(a.bundle.read_text())
        bundle = raw[0]["bundle"] if isinstance(raw, list) else raw.get("bundle", raw)
        run = dc.certify(t, a.cik, a.coverage, dc.BundleFactSource(bundle), a.seed)

    a.out_dir.mkdir(parents=True, exist_ok=True)
    md = a.out_dir / f"{t}-display-cert-{a.date}.md"
    md.write_text(dc.render(run, a.date))
    with open(
        a.out_dir / f"{t}-display-cert-{a.date}-evidence.csv", "w", newline=""
    ) as fh:
        csv.writer(fh).writerows(dc.evidence_rows(run))
    if not a.no_registry:
        new = not a.registry.exists()
        with open(a.registry, "a", newline="") as fh:
            w = csv.writer(fh)
            if new:
                w.writerow(dc.REGISTRY_HEADER)
            n, k = len(run.shown), run.errors
            w.writerow(
                [
                    t,
                    a.date,
                    run.verdict,
                    run.coverage_sha256,
                    run.seed,
                    n,
                    k,
                    f"{dc.clopper_pearson_upper(k, n):.6f}",
                    "approver",
                ]
            )
        pn, pk, pub = dc.pooled_bound(a.registry)
        print(f"pooled over PASS companies: {pk}/{pn} wrong, 95% upper bound {pub:.4%}")
    print(dc.to_json(run))
    print(f"wrote {md}")
    return {"PASS": 0, "FAIL": 1}.get(run.verdict, 2)


if __name__ == "__main__":
    sys.exit(main())
