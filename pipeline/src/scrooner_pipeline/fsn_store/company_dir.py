"""Read one `companies/<cik>/` directory (data-team/47-fsn-store/FORMATS-v1.md §1)."""

from __future__ import annotations

import csv
import io
import json
import subprocess
from pathlib import Path
from typing import Any, Iterator

csv.field_size_limit(1 << 24)

TABLES = ("sub", "pre", "num", "cal", "ren", "tag", "dim")
NO_DIM = "0x00000000"
STATEMENT_STMTS = frozenset({"BS", "IS", "CF", "CI", "EQ", "CP", "UN"})
# Domestic 10-K/10-Q family plus the foreign private issuers' annual reports (20-F, 40-F): a 40-F filer in the
# cohort (SHOP, FY2016-FY2023) has no 10-K for those years, and its own annual statements are its history.
PERIODIC_FORMS = frozenset(
    {"10-K", "10-K/A", "10-KT", "10-KT/A", "10-Q", "10-Q/A", "10-QT", "10-QT/A"}
    | {"20-F", "20-F/A", "40-F", "40-F/A"}
)


def zst_rows(path: Path) -> Iterator[dict[str, str]]:
    """Rows of a (possibly multi-frame) zstd TSV with header."""
    proc = subprocess.Popen(["zstd", "-dc", str(path)], stdout=subprocess.PIPE)
    assert proc.stdout is not None
    fh = io.TextIOWrapper(proc.stdout, encoding="utf-8", errors="replace", newline="")
    yield from csv.DictReader(fh, delimiter="\t", quoting=csv.QUOTE_NONE)
    proc.wait()


def read(path: Path, tables: tuple[str, ...] = TABLES) -> dict[str, Any]:
    """{"manifest": {...}, "sub": [rows], "pre": [rows], ...} for one company directory."""
    out: dict[str, Any] = {"manifest": json.loads((path / "manifest.json").read_text())}
    for t in tables:
        f = path / f"{t}.tsv.zst"
        out[t] = list(zst_rows(f)) if f.exists() else []
    return out
