"""Rebuild data-team/strategy/top100-coverage.csv and top100-coverage-summary.csv (read-only on the database).

usage (repo root): PYTHONPATH=pipeline/src python3 pipeline/scripts/top100_coverage.py [out_dir] [--write-display-state]
                   [--company-ids 3,4,2733 | --company-ids-csv universe.csv] [--ranks 101-200] [--rank-source shards.csv]
--write-display-state upserts analytics.cell_display_state for the exported companies (dry run without it); the export
read stays read-only and the write uses its own connection, so run that form WITHOUT default_transaction_read_only.
--company-ids exports only those companies (the flow exports one company per job); the files then hold only their rows,
and scripts/ci/top100_coverage_merge.py merges them into the committed files. Any rank of the rank source is selectable.
--company-ids-csv reads the ids from a CSV's company_id column (a universe file).
--ranks N-M exports ranks N..M of the rank source (default: ranks 1-100, the hourly behavior). With --company-ids the
ids must fall inside the ranks.
--rank-source is any CSV with rank, ticker, company_id columns (default doc/data-moat/team/top1000/shards.csv).
Logic and class definitions: scrooner_pipeline/mapper/top100_coverage.py."""

import sys
from pathlib import Path

from scrooner_pipeline.mapper.top100_coverage import (
    load_company_ids_csv,
    main,
    parse_ranks,
)

RANK_SOURCE = Path("doc/data-moat/team/top1000/shards.csv")


def parse_ids(raw: str) -> list[int]:
    try:
        ids = sorted({int(x) for x in raw.split(",") if x.strip()})
    except ValueError:
        raise SystemExit(f"--company-ids wants comma-separated integers, got {raw!r}")
    if not ids:
        raise SystemExit("--company-ids given but empty")
    return ids


def parse_args(
    argv: list[str],
) -> tuple[Path, bool, list[int] | None, tuple[int, int] | None, Path]:
    out: Path | None = None
    ids: list[int] | None = None
    ranks: tuple[int, int] | None = None
    source = RANK_SOURCE
    write = False
    it = iter(argv)
    for a in it:
        if a == "--write-display-state":
            write = True
        elif a == "--company-ids":
            ids = parse_ids(next(it, ""))
        elif a == "--company-ids-csv":
            ids = load_company_ids_csv(Path(next(it, "")))
        elif a == "--ranks":
            ranks = parse_ranks(next(it, ""))
        elif a == "--rank-source":
            source = Path(next(it, ""))
        elif a.startswith("--"):
            raise SystemExit(f"unknown option {a}")
        elif out is None:
            out = Path(a)
        else:
            raise SystemExit(f"unexpected argument {a}")
    return out or Path("data-team/strategy"), write, ids, ranks, source


if __name__ == "__main__":
    out, write, ids, ranks, source = parse_args(sys.argv[1:])
    sys.exit(
        main(
            out,
            source,
            Path("data-team/companies/reads"),
            write_display_state=write,
            company_ids=ids,
            ranks=ranks,
        )
    )
