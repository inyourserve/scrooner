"""Where the structural resolver's output lives and how every reader finds it. ONE place (scale plan 2026-11-17 s.6 #5).

Layout (RESOLVER-OUTPUT-FORMAT.md):
  data-team/tags/line_map/resolver/<TICKER>.csv   one file per company, same columns as before, rows in key order.
  data-team/tags/line_map/resolver-all110-<date>.csv   the OLD single file (29 MB at 110 companies; GitHub refuses
                                                        files over 100 MB, which arrives at about 370 companies).

Rule: the per-company directory is the source whenever it holds a CSV; the single file is read only when the directory
is absent or empty (older checkouts, tests that write one file). When BOTH exist the directory wins and
`conflict()` names the stale single file, so a test keeps main from carrying two sources. `split_all110()` turns a
single file into the directory (the Tag Expert runs tools/split_resolver.py after resolve_all.py).
"""

from __future__ import annotations

import csv
import re
from collections.abc import Iterable, Iterator
from contextlib import contextmanager
from pathlib import Path

LINE_MAP_DIR = Path(__file__).resolve().parents[4] / "data-team" / "tags" / "line_map"
SPLIT_DIRNAME = "resolver"
ALL110_RE = re.compile(r"^resolver-all110-(\d{4}-\d{2}-\d{2})\.csv$")
TICKER_FILE_RE = re.compile(r"^([A-Z0-9][A-Z0-9.\-]{0,11})\.csv$")

csv.field_size_limit(10**8)


def split_dir(line_map_dir: Path = LINE_MAP_DIR) -> Path:
    return line_map_dir / SPLIT_DIRNAME


def split_files(
    line_map_dir: Path = LINE_MAP_DIR, tickers: Iterable[str] | None = None
) -> list[Path]:
    """Per-company files, sorted by ticker; only `tickers` when given (missing tickers are simply absent)."""
    d = split_dir(line_map_dir)
    if not d.is_dir():
        return []
    if tickers is not None:
        return sorted(p for t in set(tickers) if (p := d / f"{t}.csv").is_file())
    return sorted(
        p for p in d.iterdir() if TICKER_FILE_RE.match(p.name) and p.is_file()
    )


def all110_files(line_map_dir: Path = LINE_MAP_DIR) -> list[Path]:
    if not line_map_dir.is_dir():
        return []
    return sorted(
        p for p in line_map_dir.iterdir() if ALL110_RE.match(p.name) and p.is_file()
    )


def resolver_source(line_map_dir: Path = LINE_MAP_DIR) -> Path | None:
    """The directory of per-company files, else the newest single file, else None. Pass it to anything that takes a
    path (structural_loader.read_claims accepts a file or a directory)."""
    if split_files(line_map_dir):
        return split_dir(line_map_dir)
    files = all110_files(line_map_dir)
    return files[-1] if files else None


def resolver_files(
    line_map_dir: Path = LINE_MAP_DIR, tickers: Iterable[str] | None = None
) -> list[Path]:
    """The files a reader should open: the per-company files (optionally only `tickers`), else [newest single file]."""
    files = split_files(line_map_dir, tickers)
    if files or split_files(line_map_dir):
        return files
    single = all110_files(line_map_dir)
    return single[-1:] if single else []


def iter_rows(
    line_map_dir: Path = LINE_MAP_DIR, tickers: Iterable[str] | None = None
) -> Iterator[dict[str, str]]:
    """Every resolver row (optionally only `tickers`), file by file in ticker order."""
    for p in resolver_files(line_map_dir, tickers):
        with p.open(newline="") as fh:
            yield from csv.DictReader(fh)


@contextmanager
def open_rows(
    line_map_dir: Path = LINE_MAP_DIR, tickers: Iterable[str] | None = None
) -> Iterator[Iterator[dict[str, str]]]:
    """`with open_rows(dir) as rows: for r in rows:` -- the same shape as the old `with file.open() as fh: DictReader`."""
    yield iter_rows(line_map_dir, tickers)


def resolver_version(line_map_dir: Path = LINE_MAP_DIR) -> str | None:
    """resolver_version of the first data row of the first file, or None when there is no resolver output."""
    for r in iter_rows(line_map_dir):
        return (r.get("resolver_version") or "").strip() or None
    return None


def conflict(line_map_dir: Path = LINE_MAP_DIR) -> list[Path]:
    """Single files that coexist with a non-empty per-company directory (they are stale copies: the directory wins)."""
    return all110_files(line_map_dir) if split_files(line_map_dir) else []


def split_all110(src: Path, out_dir: Path, prune: bool = True) -> dict[str, int]:
    """Write <out_dir>/<TICKER>.csv from one single-file resolver output. Rows keep the source's column order; within a
    ticker they are sorted by (cik, data_point, period_end, grain) so a re-split of the same rows is byte-identical.
    prune removes ticker files not present in the source. Returns ticker -> row count."""
    out_dir.mkdir(parents=True, exist_ok=True)
    by_ticker: dict[str, list[dict[str, str]]] = {}
    with src.open(newline="") as fh:
        rd = csv.DictReader(fh)
        header = list(rd.fieldnames or [])
        for r in rd:
            t = (r.get("ticker") or "").strip()
            if not TICKER_FILE_RE.match(f"{t}.csv"):
                raise ValueError(
                    f"row with an unusable ticker {t!r}: {dict(list(r.items())[:4])}"
                )
            by_ticker.setdefault(t, []).append(r)
    key = lambda r: (
        r.get("cik", ""),
        r.get("data_point", ""),
        r.get("period_end", ""),
        r.get("grain", ""),
    )  # noqa: E731
    counts: dict[str, int] = {}
    for t, rows in sorted(by_ticker.items()):
        rows.sort(key=key)
        tmp = out_dir / f"{t}.csv.tmp"
        with tmp.open("w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=header, extrasaction="ignore")
            w.writeheader()
            w.writerows(rows)
        tmp.replace(out_dir / f"{t}.csv")
        counts[t] = len(rows)
    if prune:
        for p in (
            split_files(out_dir.parent)
            if out_dir.name == SPLIT_DIRNAME
            else sorted(out_dir.glob("*.csv"))
        ):
            if p.stem not in counts:
                p.unlink()
    return counts
