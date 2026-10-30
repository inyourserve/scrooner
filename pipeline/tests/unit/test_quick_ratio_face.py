"""FSDS balance-sheet face reader (mapper/quick_ratio_face.py): per accession and per DATE COLUMN, does the presented
balance sheet show an inventory line with a value? No network: a tiny pre.txt + num.txt zip."""

from __future__ import annotations

import zipfile
from datetime import date

from scrooner_pipeline.mapper import quick_ratio_face as qf

PRE = "adsh\treport\tline\tstmt\tinpth\trfile\ttag\tversion\tplabel\tnegating\n"
NUM = "adsh\ttag\tversion\tddate\tqtrs\tuom\tcoreg\tvalue\n"
D1, D0 = date(2024, 12, 31), date(2023, 12, 31)


def pre(adsh, stmt, tag, label, inpth="0", line=None):
    # the current-assets total comes after its lines in a balance sheet
    line = line or ("9" if tag == "AssetsCurrent" else "1")
    return [adsh, "2", line, stmt, inpth, "H", tag, "v", label, "0"]


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
    face = qf.AccessionFace(
        frozenset({D1, D0}), frozenset({D0}), frozenset({D1}), frozenset({D0})
    )
    qf.write_jsonl(f, {A1: face}, "fsds:2025q1")
    assert qf.load_jsonl(f) == {A1: face}
    assert qf.load_jsonl(tmp_path / "missing.jsonl") == {}


def test_supplies_labels_count_as_a_materials_line_but_inventory_named_ones_do_not(
    tmp_path,
):
    # FDX 'Spare parts, supplies, and fuel'; ConEd 'Fuel oil, gas in storage, materials and supplies'; UPS prints neither
    z = make_zip(
        tmp_path,
        [
            pre(A1, "BS", "OtherAssetsCurrent", "Spare parts, supplies, and fuel"),
            pre(A2, "BS", "OtherAssetsCurrent", "Fuel oil, gas in storage, materials and supplies"),
            pre(A3, "BS", "InventoryRawMaterialsAndSupplies", "Raw materials and supplies inventory"),
            pre(A4, "BS", "OtherAssetsCurrent", "Prepaid expenses and other"),
        ],
        [num(a, t, "20241231", "5") for a, t in (
            (A1, "OtherAssetsCurrent"), (A2, "OtherAssetsCurrent"), (A3, "InventoryRawMaterialsAndSupplies"), (A4, "OtherAssetsCurrent"))],
    )  # fmt: skip
    got = qf.balance_sheet_faces(z, {A1, A2, A3, A4})
    assert got[A1].materials_dates == {D1} and got[A2].materials_dates == {D1}
    assert got[A3].materials_dates == frozenset() and got[A3].inventory_dates == {
        D1
    }  # an inventory sub-line
    assert (
        got[A4].materials_dates == frozenset()
        and got[A4].inventory_dates == frozenset()
    )


def test_only_lines_above_the_current_assets_total_count(tmp_path):
    z = make_zip(
        tmp_path,
        [
            pre(A1, "BS", "InventoryNet", "Inventories", line="2"),
            pre(A1, "BS", "AssetsCurrent", "Total current assets", line="5"),
            pre(A2, "BS", "AssetsCurrent", "Total current assets", line="5"),
            pre(A2, "BS", "InventoryNet", "Inventories", line="9"),  # a noncurrent block below the total
            pre(A3, "BS", "InventoryNet", "Inventories", line="9"),  # no AssetsCurrent row: unclassified, accepted
        ],
        [num(A1, "InventoryNet", "20241231", "5"), num(A2, "InventoryNet", "20241231", "5"),
         num(A3, "InventoryNet", "20241231", "5"), num(A1, "AssetsCurrent", "20241231", "50"), num(A2, "AssetsCurrent", "20241231", "50")],
    )  # fmt: skip
    got = qf.balance_sheet_faces(z, {A1, A2, A3})
    assert got[A1].inventory_dates == {D1} and got[A2].inventory_dates == frozenset()
    assert got[A3].inventory_dates == {D1}


def test_a_wip_line_that_is_also_a_contract_asset_is_not_inventory(tmp_path):
    # OMC 2018-03-31: Work in process 1,378.0 on InventoryWorkInProcess, the same amount tagged ContractWithCustomerAssetGrossCurrent
    z = make_zip(
        tmp_path,
        [pre(A1, "BS", "InventoryWorkInProcess", "Work in process", line="2"), pre(A1, "BS", "AssetsCurrent", "Total current assets", line="5"),
         pre(A2, "BS", "InventoryWorkInProcess", "Work in process", line="2"), pre(A2, "BS", "AssetsCurrent", "Total current assets", line="5"),
         pre(A3, "BS", "InventoryWorkInProcess", "Work in process", line="2"), pre(A3, "BS", "InventoryFinishedGoods", "Finished goods", line="3"),
         pre(A3, "BS", "AssetsCurrent", "Total current assets", line="5")],
        [num(A1, "InventoryWorkInProcess", "20241231", "1378"), num(A1, "ContractWithCustomerAssetGrossCurrent", "20241231", "1378"),
         num(A1, "AssetsCurrent", "20241231", "9000"),
         num(A2, "InventoryWorkInProcess", "20241231", "1378"), num(A2, "AssetsCurrent", "20241231", "9000"),  # no contract-asset tag (pre-606)
         num(A3, "InventoryWorkInProcess", "20241231", "10"), num(A3, "InventoryFinishedGoods", "20241231", "20"), num(A3, "AssetsCurrent", "20241231", "9000")],
    )  # fmt: skip
    got = qf.balance_sheet_faces(z, {A1, A2, A3})
    assert (
        got[A1].inventory_dates == frozenset() and got[A1].wip_only_dates == frozenset()
    )  # guard: equal contract asset
    assert got[A2].inventory_dates == {D1} and got[A2].wip_only_dates == {
        D1
    }  # WIP only: excluded only after a note read
    assert (
        got[A3].inventory_dates == {D1} and got[A3].wip_only_dates == frozenset()
    )  # finished goods beside it


def test_a_face_without_current_subtotals_is_unclassified(tmp_path):
    # FTAI 0001590364-24-000003 presents Total assets / Total liabilities only; a custom-tagged subtotal counts by label
    b1, b2, b3 = "0001-25-000011", "0001-25-000012", "0001-25-000013"
    z = make_zip(
        tmp_path,
        [
            pre(b1, "BS", "Assets", "Total assets"), pre(b1, "BS", "Liabilities", "Total liabilities"),
            pre(b1, "BS", "InventoryNet", "Inventory"),
            pre(b2, "BS", "AssetsCurrent", "Total"), pre(b2, "BS", "LiabilitiesCurrent", "Total"),  # EOG labels
            pre(b3, "BS", "AssetsCurrent", "Total current assets"),
            pre(b3, "BS", "abc_CurrentLiabilitiesTotal", "Total current liabilities"),
        ],
        [num(b, "Assets" if b == b1 else "AssetsCurrent", "20241231", "100") for b in (b1, b2, b3)],
    )  # fmt: skip
    got = qf.balance_sheet_faces(z, {b1, b2, b3})
    assert (got[b1].classified, got[b2].classified, got[b3].classified) == (
        False,
        True,
        True,
    )
    f = tmp_path / "face.jsonl"
    qf.write_jsonl(f, got, "fsds:2024q1")
    back = qf.load_jsonl(f)
    assert back[b1].classified is False and back[b2].classified is True
    old = (
        tmp_path / "old.jsonl"
    )  # records written before the field existed read as classified
    old.write_text(
        '{"accession": "x", "statement_dates": [], "inventory_dates": [], "materials_dates": []}\n'
    )
    assert qf.load_jsonl(old)["x"].classified is True


def test_fsn_num_rows_are_reduced_to_face_facts_before_the_shared_reader():
    # FSN num.tsv carries note and dimensional facts and repeated copies (iprx); FSDS num.txt holds face values only
    rows = [
        {"adsh": A1, "tag": "InventoryNet", "ddate": "20241231", "qtrs": "0", "value": "7", "dimn": "0", "iprx": "0", "coreg": ""},
        {"adsh": A1, "tag": "InventoryNet", "ddate": "20221231", "qtrs": "0", "value": "6", "dimn": "1", "iprx": "0", "coreg": ""},
        {"adsh": A1, "tag": "InventoryNet", "ddate": "20211231", "qtrs": "0", "value": "5", "dimn": "0", "iprx": "1", "coreg": ""},
        {"adsh": A1, "tag": "InventoryNet", "ddate": "20201231", "qtrs": "0", "value": "4", "dimn": "0", "iprx": "0", "coreg": "Sub"},
        {"adsh": A1, "tag": "AssetsCurrent", "ddate": "20241231", "qtrs": "0", "value": "100", "dimn": "0", "iprx": "0", "coreg": ""},
    ]  # fmt: skip
    kept = list(qf.fsn_face_num(rows))
    assert [r["ddate"] for r in kept] == ["20241231", "20241231"]
    hdr = PRE.strip().split("\t")
    pre_rows = [dict(zip(hdr, r)) for r in (
        pre(A1, "BS", "InventoryNet", "Inventories"), pre(A1, "BS", "AssetsCurrent", "Total current assets"),
        pre(A1, "BS", "LiabilitiesCurrent", "Total current liabilities", line="20"),
    )]  # fmt: skip
    got = qf.faces_from_rows(pre_rows, kept, {A1})
    assert (
        got[A1].statement_dates == {D1}
        and got[A1].inventory_dates == {D1}
        and got[A1].classified
    )
