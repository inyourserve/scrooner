"""FSDS balance-sheet face reader (mapper/quick_ratio_face.py): per accession, does the presented balance sheet show an
inventory line? No network: a tiny pre.txt zip."""

from __future__ import annotations

import zipfile
from datetime import date

from scrooner_pipeline.mapper import quick_ratio_face as qf

HEADER = "adsh\treport\tline\tstmt\tinpth\trfile\ttag\tversion\tplabel\tnegating\n"


def make_zip(tmp_path, rows):
    p = tmp_path / "2023q4.zip"
    body = HEADER + "".join("\t".join(r) + "\n" for r in rows)
    with zipfile.ZipFile(p, "w") as zf:
        zf.writestr("pre.txt", body)
        zf.writestr("sub.txt", "adsh\tcik\n")
    return p


def row(adsh, stmt, tag, label, inpth="0"):
    return [adsh, "2", "1", stmt, inpth, "H", tag, "v", label, "0"]


def test_shows_inventory_by_label_or_by_tag_on_the_balance_sheet_only(tmp_path):
    z = make_zip(
        tmp_path,
        [
            row("0001-23-000001", "BS", "AssetsCurrent", "Total current assets"),
            row("0001-23-000001", "BS", "InventoryNet", "Inventories"),  # face line
            row(
                "0001-23-000002", "BS", "AssetsCurrent", "Total current assets"
            ),  # no inventory line
            row(
                "0001-23-000002", "BS", "CashAndCashEquivalentsAtCarryingValue", "Cash"
            ),
            row(
                "0001-23-000002", "CF", "IncreaseDecreaseInInventories", "Inventories"
            ),  # a cash-flow row: not the face
            row(
                "0001-23-000003",
                "BS",
                "OtherAssetsCurrent",
                "Merchandise inventory, net",
            ),  # label only
            row(
                "0001-23-000004", "BS", "InventoryNet", "Inventories", inpth="1"
            ),  # parenthetical row: not a line
            row("0001-23-000004", "BS", "AssetsCurrent", "Total current assets"),
            row(
                "0001-23-000009", "BS", "InventoryNet", "Inventories"
            ),  # not a wanted accession
        ],
    )
    got = qf.balance_sheet_inventory_lines(z, {"0001-23-000001", "0001-23-000002", "0001-23-000003", "0001-23-000004", "0001-23-000005"})  # fmt: skip
    assert got == {
        "0001-23-000001": True,
        "0001-23-000002": False,
        "0001-23-000003": True,
        "0001-23-000004": False,
    }
    assert (
        "0001-23-000005" not in got
    )  # no balance-sheet rows at all: the face is unavailable, not False


def test_quarters_and_the_interim_jsonl_round_trip(tmp_path):
    assert qf.quarter_of(date(2023, 11, 3)) == (2023, 4) and qf.quarter_of(
        date(2024, 1, 31)
    ) == (2024, 1)
    f = tmp_path / "face.jsonl"
    qf.write_jsonl(f, {"0001-23-000001": True, "0001-23-000002": False}, "fsds:2023q4")
    assert qf.load_jsonl(f) == {"0001-23-000001": True, "0001-23-000002": False}
    assert qf.load_jsonl(tmp_path / "missing.jsonl") == {}
