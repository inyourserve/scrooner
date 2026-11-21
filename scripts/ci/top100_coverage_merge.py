"""Merge a per-company coverage export into the committed top-100 coverage files, atomically.

usage: top100_coverage_merge.py --from <export_dir> --into <strategy_dir> [--company-ids 3,4] [--keep-ids 9,666]
                                [--summary-only]

For every company present in <export_dir>'s files (or only --company-ids), its rows REPLACE that company's rows in
<strategy_dir>/top100-coverage-summary.csv and, unless --summary-only, <strategy_dir>/top100-coverage.csv. Every other
company's rows are kept as they are. --keep-ids names companies whose committed rows must stay even if the export has
newer ones: the hourly export passes the companies whose top100-flow job is running, because their database state is
mid-reload (values rewritten, proof not yet rerun) and an export of that moment is a half state, not a measurement
(0.0% and 41% snapshots went to main on 2026-11-16).

Each target file is written to a temp file next to it and renamed into place, so a reader never sees a partial file.
Header columns must match between export and target; a mismatch is an error (exit 2), never a silent reshaping. The one
exception is a header that only APPENDS listed columns (APPENDABLE: badge and sector, 2026-11-22) to the other (an
export written by newer code, or by older code still in flight): the longer header is kept and the rows without those columns carry them
blank; the report names the columns.
Summary rows stay sorted by rank. Exit 0 and a one-line report per file; nothing else is touched.
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
import tempfile
from pathlib import Path

SUMMARY = "top100-coverage-summary.csv"
FULL = "top100-coverage.csv"
# columns a newer export may append (top100_coverage.CSV_COLUMNS, certify_display badge checks of 2026-11-22)
APPENDABLE = ("badge", "sector")


def parse_ids(raw: str | None) -> set[str] | None:
    if raw is None:
        return None
    ids = {x.strip() for x in raw.split(",") if x.strip()}
    for x in ids:
        if not x.isdigit():
            raise SystemExit(f"company ids must be integers, got {x!r}")
    return ids


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="") as fh:
        rd = csv.DictReader(fh)
        return list(rd.fieldnames or []), list(rd)


def write_atomic(path: Path, header: list[str], rows: list[dict[str, str]]) -> None:
    fd, tmp = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=str(path.parent)
    )
    try:
        with os.fdopen(fd, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=header, extrasaction="ignore")
            w.writeheader()
            w.writerows(rows)
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def merge_rows(
    target: list[dict[str, str]],
    source: list[dict[str, str]],
    only: set[str] | None,
    keep: set[str],
) -> tuple[list[dict[str, str]], set[str], set[str]]:
    """Rows after the merge, the ids replaced, the ids kept. Order: target order, replaced in place; new ids appended."""
    incoming: dict[str, list[dict[str, str]]] = {}
    for r in source:
        cid = r["company_id"]
        if only is not None and cid not in only:
            continue
        incoming.setdefault(cid, []).append(r)
    kept = {cid for cid in incoming if cid in keep}
    for cid in kept:
        del incoming[cid]
    replaced = set(incoming)
    out: list[dict[str, str]] = []
    seen: set[str] = set()
    for r in target:
        cid = r["company_id"]
        if cid in incoming:
            if cid not in seen:
                out.extend(incoming[cid])
                seen.add(cid)
            continue
        out.append(r)
    for cid, rows in incoming.items():
        if cid not in seen:
            out.extend(rows)
    return out, replaced, kept


def _rank(r: dict[str, str]) -> tuple[int, int]:
    try:
        return (0, int(r.get("rank") or 0))
    except ValueError:
        return (1, 0)


def merge_file(
    src: Path, dst: Path, only: set[str] | None, keep: set[str], sort_rank: bool
) -> str:
    sh, srows = read_csv(src)
    added: list[str] = []
    if dst.exists():
        dh, drows = read_csv(dst)
        if dh != sh:
            if (
                len(sh) > len(dh)
                and sh[: len(dh)] == dh
                and set(sh[len(dh) :]) <= set(APPENDABLE)
            ):
                added, dh = (
                    sh[len(dh) :],
                    sh,
                )  # the export appends columns: committed rows carry them blank
            elif (
                len(dh) > len(sh)
                and dh[: len(sh)] == sh
                and set(dh[len(sh) :]) <= set(APPENDABLE)
            ):
                added = dh[
                    len(sh) :
                ]  # an older export: its rows carry the committed file's newer columns blank
            else:
                raise SystemExit(
                    f"header mismatch for {dst.name}: export {sh} vs committed {dh}"
                )
    else:
        dh, drows = sh, []
    out, replaced, kept = merge_rows(drows, srows, only, keep)
    if sort_rank:
        out.sort(key=_rank)
    write_atomic(dst, dh, out)
    return (
        f"{dst.name}: replaced {len(replaced)} company(ies) {sorted(replaced, key=int)}, "
        f"kept {len(kept)} in flight {sorted(kept, key=int)}, {len(out)} rows"
        + (f"; appended columns blank where absent: {added}" if added else "")
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument(
        "--from",
        dest="src",
        required=True,
        help="export dir (output of top100_coverage.py)",
    )
    ap.add_argument(
        "--into",
        dest="dst",
        required=True,
        help="committed dir, normally data-team/strategy",
    )
    ap.add_argument("--company-ids", help="merge only these companies from the export")
    ap.add_argument(
        "--keep-ids", help="companies whose committed rows stay (flow job in progress)"
    )
    ap.add_argument(
        "--summary-only", action="store_true", help="leave top100-coverage.csv alone"
    )
    a = ap.parse_args(argv)
    src, dst = Path(a.src), Path(a.dst)
    only = parse_ids(a.company_ids)
    keep = parse_ids(a.keep_ids) or set()
    if not (src / SUMMARY).exists():
        print(f"no {SUMMARY} in {src}: nothing merged")
        return 2
    print(merge_file(src / SUMMARY, dst / SUMMARY, only, keep, sort_rank=True))
    if not a.summary_only:
        if not (src / FULL).exists():
            print(f"no {FULL} in {src}: full file not merged")
            return 2
        print(merge_file(src / FULL, dst / FULL, only, keep, sort_rank=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
