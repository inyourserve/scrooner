"""Rebuild data-team/strategy/top100-coverage.csv and top100-coverage-summary.csv (read-only on the database).

usage (repo root): PYTHONPATH=pipeline/src python3 pipeline/scripts/top100_coverage.py [out_dir] [--write-display-state]
--write-display-state upserts analytics.cell_display_state for the exported companies (dry run without it); the export
read stays read-only and the write uses its own connection, so run that form WITHOUT default_transaction_read_only.
Logic and class definitions: scrooner_pipeline/mapper/top100_coverage.py."""

import sys
from pathlib import Path

from scrooner_pipeline.mapper.top100_coverage import main

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--write-display-state"]
    out = Path(args[0] if args else "data-team/strategy")
    sys.exit(
        main(
            out,
            Path("doc/data-moat/team/top1000/shards.csv"),
            Path("data-team/companies/reads"),
            write_display_state="--write-display-state" in sys.argv,
        )
    )
