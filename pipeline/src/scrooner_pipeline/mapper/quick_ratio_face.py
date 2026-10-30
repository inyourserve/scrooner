"""What does THIS period's own balance sheet show? (quick_ratio, rule quick_ratio.inventory_evidence@1)

Read from the SEC Financial Statement Data Sets (FSDS, sec.gov/dera/data/financial-statement-data-sets). ``pre.txt``
lists the lines the filer PRESENTS on each statement (stmt 'BS' = the balance-sheet face; parenthetical rows excluded);
``num.txt`` holds their values per date column (ddate, qtrs = 0 for balance-sheet instants). For one accession the result
is per DATE COLUMN, so a line that has a value only in the comparative column does not count for the current date:

  statement_dates   dates for which any presented balance-sheet line has a value (the statement SHOWS this date)
  inventory_dates   dates where a presented inventory line has a NONZERO value (tag or label)
  materials_dates   dates where a presented "materials and supplies" line (not an inventory-named line) has a value
  classified        the face presents BOTH a current-assets and a current-liabilities subtotal (tag or label); an
                    unclassified balance sheet (FTAI 0001590364-24-000003) has no quick ratio

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
_CURRENT_ASSETS_LABEL = re.compile(r"\btotal current assets\b", re.IGNORECASE)
_CURRENT_LIABILITIES_LABEL = re.compile(r"\btotal current liabilities\b", re.IGNORECASE)
csv.field_size_limit(10**8)


@dataclass(frozen=True)
class AccessionFace:
    statement_dates: frozenset[date] = field(default_factory=frozenset)
    inventory_dates: frozenset[date] = field(default_factory=frozenset)
    materials_dates: frozenset[date] = field(default_factory=frozenset)
    # dates where the ONLY inventory value is on InventoryWorkInProcess lines (OMC): excluded for a registrant whose
    # note was read as client billable costs (quick_ratio_evidence.CONTRACT_ASSET_NOTE_READ)
    wip_only_dates: frozenset[date] = field(default_factory=frozenset)
    classified: bool = True


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
    """accession (with dashes) -> AccessionFace for the accessions that have balance-sheet rows in this data set.

    Only lines ABOVE the report's ``AssetsCurrent`` row count as current inventory or supplies lines (the registrant's
    own block: co-registrant blocks carry ``coreg`` on their values and are skipped). A WIP line whose value is also
    tagged as a contract asset in the same filing is not inventory (OMC 2017-2019)."""
    adsh_of = {a.replace("-", ""): a for a in accessions}
    groups: dict[tuple[str, str], list[tuple[int, str, str]]] = {}
    with zipfile.ZipFile(zip_path) as zf:
        for r in _rows(zf, "pre.txt"):
            key = r["adsh"].replace("-", "")
            if (
                key not in adsh_of
                or r.get("stmt") != "BS"
                or r.get("inpth") not in ("0", "", None)
            ):
                continue
            try:
                line = int(r.get("line") or 0)
            except ValueError:
                line = 0
            groups.setdefault((key, r.get("report", "")), []).append(
                (line, r.get("tag", ""), r.get("plabel", ""))
            )
        kinds: dict[
            tuple[str, str], tuple[bool, bool]
        ] = {}  # (adsh, tag) -> (is_inventory, is_materials)
        bs_tags: set[tuple[str, str]] = set()
        classified: set[str] = set()
        for (key, _report), rows in groups.items():
            if any(
                tag == "AssetsCurrent" or _CURRENT_ASSETS_LABEL.search(label)
                for _, tag, label in rows
            ) and any(
                tag == "LiabilitiesCurrent" or _CURRENT_LIABILITIES_LABEL.search(label)
                for _, tag, label in rows
            ):
                classified.add(key)
            ac_line = min(
                (ln for ln, tag, _ in rows if tag == "AssetsCurrent"), default=None
            )
            for ln, tag, label in rows:
                bs_tags.add((key, tag))
                if ac_line is not None and ln >= ac_line:
                    continue  # at or below the current-assets total: not a current line
                tag_materials = "MaterialsSupplies" in tag and "nventor" not in tag
                inv = bool(_INVENTORY_LABEL.search(label)) or (
                    not tag_materials and is_inventory_like(tag)
                )
                mat = (not inv) and (
                    bool(_MATERIALS_LABEL.search(label)) or tag_materials
                )
                old = kinds.get((key, tag), (False, False))
                kinds[(key, tag)] = (old[0] or inv, old[1] or mat)
        statement: dict[str, set[date]] = {}
        inv_values: dict[tuple[str, str], dict[date, Decimal]] = {}
        materials: dict[str, set[date]] = {}
        contract_asset: dict[tuple[str, date], set[Decimal]] = {}
        for r in _rows(zf, "num.txt"):
            key = r["adsh"].replace("-", "")
            tag = r["tag"]
            if key not in adsh_of or r.get("qtrs") != "0" or r.get("coreg"):
                continue
            d = _ddate(r["ddate"])
            if d is None:
                continue
            try:
                value = Decimal(r["value"] or "0")
            except InvalidOperation:
                continue
            if tag.startswith("ContractWithCustomerAsset") and value != 0:
                contract_asset.setdefault((key, d), set()).add(value)
            if (key, tag) in bs_tags:
                statement.setdefault(key, set()).add(d)
            k = kinds.get((key, tag))
            if k is None or value == 0:
                continue
            if k[0]:
                inv_values.setdefault((key, tag), {})[d] = value
            if k[1]:
                materials.setdefault(key, set()).add(d)
    inventory: dict[str, set[date]] = {}
    non_wip: dict[str, set[date]] = {}
    for (key, tag), by_date in inv_values.items():
        for d, value in by_date.items():
            if tag.startswith("InventoryWorkInProcess") and value in contract_asset.get(
                (key, d), ()
            ):
                continue  # the filer's own XBRL also tags this amount as a contract asset
            inventory.setdefault(key, set()).add(d)
            if not tag.startswith("InventoryWorkInProcess"):
                non_wip.setdefault(key, set()).add(d)
    return {
        adsh_of[key]: AccessionFace(
            frozenset(dates),
            frozenset(inventory.get(key, ())),
            frozenset(materials.get(key, ())),
            frozenset(inventory.get(key, set()) - non_wip.get(key, set())),
            key in classified,
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
                        "wip_only_dates": sorted(
                            d.isoformat() for d in face.wip_only_dates
                        ),
                        "classified": face.classified,
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
                    frozenset(
                        date.fromisoformat(d) for d in rec.get("wip_only_dates", [])
                    ),
                    rec.get("classified", True),
                )
    return out
