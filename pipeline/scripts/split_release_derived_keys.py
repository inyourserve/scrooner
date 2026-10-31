"""Read-only: the derived-only current cells (share_basis.load_derived_only_cells)
for every company with a no_filed_source dividends-per-share or share-count
cell in a cohort dry-run file. The packager uses them so the package lists
exactly the removals the write will make. One connection, statement timeout.
usage: split_release_derived_keys.py <dryrun_cells.csv.gz> [...] -o <keys.csv>
"""

from __future__ import annotations

import csv
import gzip
import sys

import psycopg

from scrooner_pipeline.common.config import settings
from scrooner_pipeline.corporate_actions import share_basis as sb


def main(argv: list[str]) -> int:
    out = argv[argv.index("-o") + 1]
    companies: set[int] = set()
    for src in argv[: argv.index("-o")]:
        with gzip.open(src, "rt") as fh:
            for r in csv.DictReader(fh):
                if (
                    r["status"] == sb.HIDE_NO_FILED_SOURCE
                    and r["concept"] in sb.DERIVED_REMOVAL_CONCEPTS
                    and r["old_value"]
                ):
                    companies.add(int(r["company_id"]))
    n = 0
    with (
        psycopg.connect(
            settings.database_url, application_name="split_release_derived_keys"
        ) as conn,
        open(out, "w", newline="") as fo,
    ):
        conn.execute("set statement_timeout = '60s'")
        conn.execute("set default_transaction_read_only = on")
        w = csv.writer(fo)
        w.writerow(["company_id", "concept", "period_id"])
        for cid in sorted(companies):
            for concept, pid in sorted(sb.load_derived_only_cells(conn, cid)):
                w.writerow([cid, concept, pid])
                n += 1
    print(f"companies {len(companies)}, derived-only cells {n}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
