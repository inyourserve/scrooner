"""FSDS balance-sheet face reader (mapper/quick_ratio_face.py): per accession and per DATE COLUMN, does the presented
balance sheet show an inventory line with a value? No network: a tiny pre.txt + num.txt zip."""

from __future__ import annotations

import zipfile
from datetime import date

from scrooner_pipeline.mapper import quick_ratio_face as qf

PRE = "adsh\treport\tline\tstmt\tinpth\trfile\ttag\tversion\tplabel\tnegating\n"
NUM = "adsh\ttag\tversion\tddate\tqtrs\tuom\tcoreg\tvalue\n"
D1, D0 = date(2024, 12, 31), date(2023, 12, 31)


def pre(adsh, stmt, tag, label, inpth="0"):
    return [adsh, "2", "1", stmt, inpth, "H", tag, "v", label, "0"]


def num(adsh, tag, ddate, value, qtrs="0", coreg=""):
    return [adsh, tag, "v", ddate, qtrs, "USD", coreg, value]


def make_zip(tmp_path, pre_rows, num_rows):
    p = tmp_path / "2025q1.zip"
    with zipfile.ZipFile(p, "w") as zf:
        zf.writestr("pre.txt", PRE + "".join("\t".join(r) + "\n" for r in pre_rows))
        zf.writestr("num.txt", NUM + "".join("\t".join(r) + "\n" for r in num_rows))
        zf.writestr("sub.txt", "adsh\tcik\n")
    return p


A1, A2, A3, A4, A5, A6, A7 = (f"0001-25-00000{i}" for i in range(1, 8))


def test_inventory_counts_only_at_the_cell_s_own_date_column(tmp_path):
    z = make_zip(
        tmp_path,
        [
            pre(A1, "BS", "AssetsCurrent", "Total current assets"),
            pre(A1, "BS", "InventoryNet", "Inventories"),
            pre(A2, "BS", "AssetsCurrent", "Total current assets"),
            pre(A2, "BS", "InventoryNet", "Inventories"),
            pre(A3, "BS", "AssetsCurrent", "Total current assets"),
            pre(A3, "BS", "OtherAssetsCurrent", "Merchandise inventory, net"),  # label only
            pre(A4, "BS", "AssetsCurrent", "Total current assets"),
            pre(A4, "CF", "IncreaseDecreaseInInventories", "Inventories"),  # a cash-flow row: not the face
            pre(A5, "BS", "AssetsCurrent", "Total current assets"),
            pre(A5, "BS", "MaterialsSuppliesAndOther", "Materials and supplies"),
            pre(A6, "BS", "InventoryNet", "Inventories", inpth="1"),  # parenthetical: not a line
            pre(A6, "BS", "AssetsCurrent", "Total current assets"),
        ],
        [
            # A1: inventory has a value only in the COMPARATIVE column
            num(A1, "AssetsCurrent", "20241231", "100"), num(A1, "AssetsCurrent", "20231231", "90"),
            num(A1, "InventoryNet", "20231231", "10"),
            # A2: inventory 0 at the cell's date, 10 in the comparative column
            num(A2, "AssetsCurrent", "20241231", "100"), num(A2, "InventoryNet", "20241231", "0"),
            num(A2, "InventoryNet", "20231231", "10"),
            # A3: inventory by label, value at the date
            num(A3, "AssetsCurrent", "20241231", "100"), num(A3, "OtherAssetsCurrent", "20241231", "7"),
            # A4: no inventory row on the balance sheet
            num(A4, "AssetsCurrent", "20241231", "100"),
            # A5: a materials and supplies line
            num(A5, "AssetsCurrent", "20241231", "100"), num(A5, "MaterialsSuppliesAndOther", "20241231", "5"),
            # A6: statement shows only the previous year
            num(A6, "AssetsCurrent", "20231231", "90"),
            num(A6, "InventoryNet", "20241231", "9"),  # only a parenthetical row names it: not a presented line
            # duration facts and consolidating entities never count
            num(A1, "InventoryNet", "20241231", "5", qtrs="4"), num(A1, "InventoryNet", "20241231", "5", coreg="Sub"),
        ],
    )  # fmt: skip
    got = qf.balance_sheet_faces(z, {A1, A2, A3, A4, A5, A6, A7})
    assert got[A1].inventory_dates == {D0} and got[A1].statement_dates == {
        D1,
        D0,
    }  # not D1: comparative column only
    assert (
        got[A2].inventory_dates == {D0} and D1 in got[A2].statement_dates
    )  # a zero value is no line at that date
    assert got[A3].inventory_dates == {D1}
    assert got[A4].inventory_dates == frozenset() and got[A4].statement_dates == {D1}
    assert got[A5].materials_dates == {D1} and got[A5].inventory_dates == frozenset()
    assert (
        got[A6].statement_dates == {D0} and D1 not in got[A6].statement_dates
    )  # the cell's date is not shown
    assert A7 not in got  # no balance-sheet rows at all: unavailable


def test_quarters_and_the_interim_jsonl_round_trip(tmp_path):
    assert qf.quarter_of(date(2023, 11, 3)) == (2023, 4) and qf.quarter_of(
        date(2024, 1, 31)
    ) == (2024, 1)
    f = tmp_path / "face.jsonl"
    face = qf.AccessionFace(frozenset({D1, D0}), frozenset({D0}), frozenset({D1}))
    qf.write_jsonl(f, {A1: face}, "fsds:2025q1")
    assert qf.load_jsonl(f) == {A1: face}
    assert qf.load_jsonl(tmp_path / "missing.jsonl") == {}
