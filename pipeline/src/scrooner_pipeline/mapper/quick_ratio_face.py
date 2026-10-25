"""Does THIS period's own balance sheet show an inventory line? (quick_ratio, rule quick_ratio.inventory_evidence@1)

Read from the SEC Financial Statement Data Sets (FSDS, sec.gov/dera/data/financial-statement-data-sets): ``sub.txt``
maps an accession (adsh) to its filing, ``pre.txt`` lists the lines the filer PRESENTS on each statement (stmt 'BS' =
the balance sheet face). The answer is per accession, never inherited from the latest statements:

  True   a presented, non-parenthetical balance-sheet row is an inventory line (tag or label)
  False  the accession's balance sheet is in the data set and none of its rows is an inventory line
  absent the accession has no balance-sheet rows in the data set: the face is UNAVAILABLE (the caller keeps the
         stored value and flags it; it never NULLs on a guess)

Interim storage is a JSONL file ({"accession": ..., "inventory_line": true/false, "source": "fsds:2023q4"}); a table
needs a migration number claimed in doc 53 (next free 0110) and is a follow-up.
"""

from __future__ import annotations

import csv
import io
import json
import re
import zipfile
from collections.abc import Iterable
from datetime import date
from pathlib import Path

from scrooner_pipeline.mapper.quick_ratio_evidence import is_inventory_like

FSDS_URL = (
    "https://www.sec.gov/files/dera/data/financial-statement-data-sets/{year}q{q}.zip"
)
_LABEL = re.compile(r"\binventor(y|ies)\b", re.I)
csv.field_size_limit(10**8)


def quarter_of(filed: date) -> tuple[int, int]:
    return filed.year, (filed.month - 1) // 3 + 1


def _rows(zf: zipfile.ZipFile, name: str) -> Iterable[dict[str, str]]:
    with zf.open(name) as raw:
        reader = csv.DictReader(
            io.TextIOWrapper(raw, encoding="utf-8", errors="replace"), delimiter="\t"
        )
        yield from reader


def balance_sheet_inventory_lines(
    zip_path: Path, accessions: set[str]
) -> dict[str, bool]:
    """accession (with dashes) -> True/False for the accessions that have balance-sheet rows in this data set."""
    wanted = {a.replace("-", "") for a in accessions}
    out: dict[str, bool] = {}
    with zipfile.ZipFile(zip_path) as zf:
        adsh_of = {a.replace("-", ""): a for a in accessions}
        for r in _rows(zf, "pre.txt"):
            key = r["adsh"].replace("-", "")
            if (
                key not in wanted
                or r.get("stmt") != "BS"
                or r.get("inpth") not in ("0", "", None)
            ):
                continue  # not a wanted accession, not the balance sheet, or a parenthetical row
            acc = adsh_of[key]
            shown = bool(_LABEL.search(r.get("plabel", ""))) or is_inventory_like(
                r.get("tag", "")
            )
            out[acc] = out.get(acc, False) or shown
    return out


def write_jsonl(path: Path, found: dict[str, bool], source: str) -> None:
    with path.open("a") as f:
        for acc, shown in sorted(found.items()):
            f.write(
                json.dumps(
                    {"accession": acc, "inventory_line": shown, "source": source}
                )
                + "\n"
            )


def load_jsonl(path: Path) -> dict[str, bool]:
    out: dict[str, bool] = {}
    if path.exists():
        for line in path.read_text().splitlines():
            if line.strip():
                rec = json.loads(line)
                out[rec["accession"]] = bool(rec["inventory_line"])
    return out
