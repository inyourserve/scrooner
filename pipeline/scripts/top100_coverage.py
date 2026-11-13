"""Rebuild data-team/strategy/top100-coverage.csv and top100-coverage-summary.csv (read-only on the database).

usage (repo root): PYTHONPATH=pipeline/src python3 pipeline/scripts/top100_coverage.py [out_dir]
Logic and class definitions: scrooner_pipeline/mapper/top100_coverage.py."""

import sys
from pathlib import Path

from scrooner_pipeline.mapper.top100_coverage import main

if __name__ == "__main__":
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "data-team/strategy")
    sys.exit(
        main(
            out,
            Path("doc/data-moat/team/top1000/shards.csv"),
            Path("data-team/companies/reads"),
        )
    )
