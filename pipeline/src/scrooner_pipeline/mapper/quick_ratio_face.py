"""What does THIS period's own balance sheet show? (quick_ratio, rule quick_ratio.inventory_evidence@1)

Read from the SEC Financial Statement Data Sets (FSDS, sec.gov/dera/data/financial-statement-data-sets). ``pre.txt``
lists the lines the filer PRESENTS on each statement (stmt 'BS' = the balance-sheet face; parenthetical rows excluded);
``num.txt`` holds their values per date column (ddate, qtrs = 0 for balance-sheet instants). For one accession the result
is per DATE COLUMN, so a line that has a value only in the comparative column does not count for the current date:

  statement_dates   dates for which any presented balance-sheet line has a value (the statement SHOWS this date)
  inventory_dates   dates where a presented inventory line has a NONZERO value (tag or label)
  materials_dates   dates where a presented "materials and supplies" line (not an inventory-named line) has a value

A date that is not in ``statement_dates`` is UNAVAILABLE: the accession's statement does not show it (a later filing
showing only newer years; no XBRL pages). The caller then hides the cell with a reason; it never guesses.

Interim storage is a JSONL file, one object per accession; a table needs a migration number claimed in doc 53.
"""

from __future__ import annotations

import csv
import io
import json
import re
import zipfile
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

from scrooner_pipeline.mapper.quick_ratio_evidence import is_inventory_like

FSDS_URL = (
    "https://www.sec.gov/files/dera/data/financial-statement-data-sets/{year}q{q}.zip"
)
_INVENTORY_LABEL = re.compile(r"\binventor(y|ies)\b", re.I)
# a presented supplies line that is not inventory-named: "Materials and supplies", "Spare parts, supplies, and fuel",
# "Fuel oil, gas in storage, materials and supplies"
_MATERIALS_LABEL = re.compile(r"\bsupplies\b|\bspare parts\b", re.I)
csv.field_size_limit(10**8)


@dataclass(frozen=True)
class AccessionFace:
    statement_dates: frozenset[date] = field(default_factory=frozenset)
    inventory_dates: frozenset[date] = field(default_factory=frozenset)
    materials_dates: frozenset[date] = field(default_factory=frozenset)


def quarter_of(filed: date) -> tuple[int, int]:
    return filed.year, (filed.month - 1) // 3 + 1


def _rows(zf: zipfile.ZipFile, name: str) -> Iterable[dict[str, str]]:
    with zf.open(name) as raw:
        reader = csv.DictReader(
            io.TextIOWrapper(raw, encoding="utf-8", errors="replace"), delimiter="\t"
        )
        yield from reader


def _ddate(s: str) -> date | None:
    try:
        return datetime.strptime(s, "%Y%m%d").date()
    except ValueError:
        return None


def balance_sheet_faces(
    zip_path: Path, accessions: set[str]
) -> dict[str, AccessionFace]:
    """accession (with dashes) -> AccessionFace for the accessions that have balance-sheet rows in this data set."""
    adsh_of = {a.replace("-", ""): a for a in accessions}
    kinds: dict[
        tuple[str, str], tuple[bool, bool]
    ] = {}  # (adsh, tag) -> (is_inventory, is_materials)
    with zipfile.ZipFile(zip_path) as zf:
        for r in _rows(zf, "pre.txt"):
            key = r["adsh"].replace("-", "")
            if (
                key not in adsh_of
                or r.get("stmt") != "BS"
                or r.get("inpth") not in ("0", "", None)
            ):
                continue
            label, tag = r.get("plabel", ""), r.get("tag", "")
            tag_materials = "MaterialsSupplies" in tag and "nventor" not in tag
            inv = bool(_INVENTORY_LABEL.search(label)) or (
                not tag_materials and is_inventory_like(tag)
            )
            mat = (not inv) and (bool(_MATERIALS_LABEL.search(label)) or tag_materials)
            old = kinds.get((key, tag), (False, False))
            kinds[(key, tag)] = (old[0] or inv, old[1] or mat)
        statement: dict[str, set[date]] = {}
        inventory: dict[str, set[date]] = {}
        materials: dict[str, set[date]] = {}
        for r in _rows(zf, "num.txt"):
            key = r["adsh"].replace("-", "")
            k = kinds.get((key, r["tag"]))
            if k is None or r.get("qtrs") != "0" or r.get("coreg"):
                continue
            d = _ddate(r["ddate"])
            if d is None:
                continue
            statement.setdefault(key, set()).add(d)
            try:
                nonzero = Decimal(r["value"] or "0") != 0
            except InvalidOperation:
                continue
            if k[0] and nonzero:
                inventory.setdefault(key, set()).add(d)
            if k[1] and nonzero:
                materials.setdefault(key, set()).add(d)
    return {
        adsh_of[key]: AccessionFace(
            frozenset(dates),
            frozenset(inventory.get(key, ())),
            frozenset(materials.get(key, ())),
        )
        for key, dates in statement.items()
    }


def write_jsonl(path: Path, found: dict[str, AccessionFace], source: str) -> None:
    with path.open("a") as f:
        for acc, face in sorted(found.items()):
            f.write(
                json.dumps(
                    {
                        "accession": acc,
                        "statement_dates": sorted(
                            d.isoformat() for d in face.statement_dates
                        ),
                        "inventory_dates": sorted(
                            d.isoformat() for d in face.inventory_dates
                        ),
                        "materials_dates": sorted(
                            d.isoformat() for d in face.materials_dates
                        ),
                        "source": source,
                    }
                )
                + "\n"
            )


def load_jsonl(path: Path) -> dict[str, AccessionFace]:
    out: dict[str, AccessionFace] = {}
    if path.exists():
        for line in path.read_text().splitlines():
            if line.strip():
                rec = json.loads(line)
                out[rec["accession"]] = AccessionFace(
                    frozenset(date.fromisoformat(d) for d in rec["statement_dates"]),
                    frozenset(date.fromisoformat(d) for d in rec["inventory_dates"]),
                    frozenset(date.fromisoformat(d) for d in rec["materials_dates"]),
                )
    return out
