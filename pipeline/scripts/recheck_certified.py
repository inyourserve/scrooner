"""Weekly certified re-check: certify_display's mechanical checks (no new draw) on every certified
company's current coverage export (logic: scrooner_pipeline/certification/recheck.py).

  # the company ids to export (latest registry verdict PASS), comma separated; empty when none
  python pipeline/scripts/recheck_certified.py --list-ids

  # re-check against a fresh export (read-only fsn.* queries over DATABASE_URL)
  python pipeline/scripts/recheck_certified.py --coverage OUT/top100-coverage.csv --live

Writes data-team/strategy/approvals/regressions/<TICKER>-<date>.md for each certified company that no
longer passes. Exit 0 all pass, 1 a regression, 2 an error (a re-check that could not run).
"""

from __future__ import annotations

import argparse
import sys
import tempfile
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from scrooner_pipeline.certification import display_cert as dc
from scrooner_pipeline.certification import recheck as rc

REPO = Path(__file__).resolve().parents[2]
APPROVALS = REPO / "data-team/strategy/approvals"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--registry", type=Path, default=APPROVALS / "registry.csv")
    ap.add_argument(
        "--summary",
        type=Path,
        default=REPO / "data-team/strategy/top100-coverage-summary.csv",
    )
    ap.add_argument("--list-ids", action="store_true")
    ap.add_argument("--coverage", type=Path, help="current coverage export (per-cell)")
    ap.add_argument("--live", action="store_true", help="read fsn.* over DATABASE_URL")
    ap.add_argument("--out-dir", type=Path, default=APPROVALS / "regressions")
    ap.add_argument("--date", default=date.today().isoformat())
    a = ap.parse_args(argv)
    if not a.registry.exists():
        print(f"::error::no registry at {a.registry}")
        return 2
    tickers = dc.certified_tickers(a.registry)
    ids = rc.company_ids(a.summary, tickers)
    if a.list_ids:
        print(",".join(str(ids[t]) for t in tickers))
        return 0
    if not (a.coverage and a.live):
        ap.error("give --list-ids, or --coverage and --live")
    if not tickers:
        print(
            "no certified company (no latest PASS in the registry): nothing to re-check"
        )
        return 0
    from scrooner_pipeline.db.connection import get_connection

    with get_connection() as conn, tempfile.TemporaryDirectory() as tmp:
        ciks = {t: dc.resolve_cik(conn, ids[t]) for t in tickers}
        src = dc.SqlFactSource(conn)
        results = rc.recheck(
            a.registry,
            a.coverage,
            ciks,
            lambda _t: src,
            Path(tmp),
            a.out_dir,
            a.date,
        )
    for r in results:
        line = f"{r.ticker} {r.status}: {r.detail}" + (
            f" -> {r.entry}" if r.entry else ""
        )
        print(("::error::" if r.status != "PASS" else "") + line)
    print(
        f"certified re-check: {sum(r.status == 'PASS' for r in results)}/{len(results)} pass"
    )
    return rc.exit_code(results)


if __name__ == "__main__":
    sys.exit(main())
