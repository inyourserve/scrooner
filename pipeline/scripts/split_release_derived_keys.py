"""Read-only inputs the packager needs so the package lists exactly the
removals the write will make, computed with the write's own functions:
  derived  share_basis.load_derived_only_cells (every company in the dry run
           with a no_filed_source cell production still holds)
  stale    share_basis.load_held_basis_stale on the dry run's held cells, with
           share_basis.load_split_signal_dates and the dry run's events
One connection, statement timeout.
usage: split_release_derived_keys.py <dryrun_cells.csv.gz> <dryrun_summary.json> -o <out_prefix>
"""

from __future__ import annotations

import csv
import gzip
import json
import sys
from collections import defaultdict
from datetime import date
from types import SimpleNamespace

import psycopg

from scrooner_pipeline.common.config import settings
from scrooner_pipeline.corporate_actions import share_basis as sb


def main(argv: list[str]) -> int:
    cells_path, summary_path = argv[0], argv[1]
    out = argv[argv.index("-o") + 1]
    held: dict[int, list] = defaultdict(list)
    tickers: dict[int, str] = {}
    with gzip.open(cells_path, "rt") as fh:
        for r in csv.DictReader(fh):
            if r["status"] == sb.HIDE_NO_FILED_SOURCE and r["old_value"]:
                cid = int(r["company_id"])
                tickers[cid] = r["ticker"]
                held[cid].append(
                    SimpleNamespace(
                        concept=r["concept"],
                        period_id=int(r["period_id"]),
                        status=r["status"],
                    )
                )
    with open(summary_path) as fh:
        per_company = json.load(fh)["per_company"]
    n_derived = n_stale = 0
    with (
        psycopg.connect(
            settings.database_url, application_name="split_release_keys"
        ) as conn,
        open(out + "_derived.csv", "w", newline="") as fd,
        open(out + "_stale.csv", "w", newline="") as fs,
    ):
        conn.execute("set statement_timeout = '60s'")
        conn.execute("set default_transaction_read_only = on")
        wd, ws = csv.writer(fd), csv.writer(fs)
        wd.writerow(["company_id", "concept", "period_id"])
        ws.writerow(["company_id", "ticker", "concept", "period_id"])
        for cid in sorted(held):
            derived = sb.load_derived_only_cells(conn, cid)
            for concept, pid in sorted(derived):
                wd.writerow([cid, concept, pid])
                n_derived += 1
            events = [
                SimpleNamespace(
                    status=e["status"],
                    hi=date.fromisoformat(e["basis_date"]),
                    disclosures=[],
                )
                for e in per_company.get(tickers[cid], {}).get("events", [])
                if e.get("basis_date")
            ]
            res = SimpleNamespace(cells=held[cid], events=events)
            current = sb.load_current_cells(conn, cid)
            stale = sb.load_held_basis_stale(
                conn, res, current, derived, sb.load_split_signal_dates(conn, cid)
            )
            for concept, pid in sorted(stale):
                ws.writerow([cid, tickers[cid], concept, pid])
                n_stale += 1
            conn.commit()
    print(
        f"companies {len(held)}, derived-only cells {n_derived}, stale held cells {n_stale}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
