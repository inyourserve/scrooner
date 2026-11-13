"""Proof of a dimensional cell (0125): compared with the filing's value under the SAME segments (proof/dims.py), read
from a synthetic FSN quarter through the real loader (pure; needs the zstd binary the proof job already needs)."""

from __future__ import annotations

import shutil
import subprocess
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from scrooner_pipeline.proof import fsn
from scrooner_pipeline.proof.dims import DISAGREE, PROVEN, UNCHECKED, DimPart, prove_dims_cell

ADSH = "0000000001-25-000001"
NUM_COLS = "adsh tag version ddate qtrs uom dimh iprx value footnote footlen dimn coreg durp datp dcml".split()
COST = "CostOfGoodsAndServicesSold"


def _zst(path: Path, header: list[str], rows: list[list[str]]) -> None:
    text = "\t".join(header) + "\n" + "".join("\t".join(r) + "\n" for r in rows)
    subprocess.run(["zstd", "-q", "-f", "-o", str(path), "-"], input=text.encode(), check=True)


def _num(tag, dimh, value, dimn, qtrs="4"):
    row = dict.fromkeys(NUM_COLS, "")
    row.update(adsh=ADSH, tag=tag, version="us-gaap/2024", ddate="20241231", qtrs=qtrs, uom="USD", dimh=dimh,
               iprx="0", value=value, dimn=dimn, dcml="-6")
    return [row[c] for c in NUM_COLS]


@pytest.fixture
def structure(tmp_path: Path) -> fsn.FilingStructure:
    if shutil.which("zstd") is None:
        pytest.skip("zstd binary not installed")
    d = tmp_path / "2025q1"
    d.mkdir()
    _zst(d / "2025q1_sub.tsv.zst", ["adsh", "cik", "form", "filed", "period", "fy", "fp"],
         [[ADSH, "1", "10-K", "20250201", "20241231", "2024", "FY"]])
    _zst(d / "2025q1_pre.tsv.zst", ["adsh", "report", "line", "stmt", "inpth", "tag", "version", "plabel", "negating"], [])
    _zst(d / "2025q1_cal.tsv.zst", ["adsh", "grp", "arc", "negative", "ptag", "pversion", "ctag", "cversion"], [])
    _zst(d / "2025q1_dim.tsv.zst", ["dimhash", "segments", "segt"],
         [["0xP", "ProductOrService=Product;", "0"], ["0xS", "ProductOrService=Service;", "0"]])
    _zst(d / "2025q1_num.tsv.zst", NUM_COLS, [
        _num(COST, "0xP", "30000000", "1"), _num(COST, "0xS", "12000000", "1"), _num(COST, "0x00000000", "141000000", "0"),
    ])
    return fsn.load_quarter(tmp_path, "2025q1", {ADSH}, with_dims=True)[ADSH]


PARTS = [DimPart(COST, "ProductOrService=Product;"), DimPart(COST, "ProductOrService=Service;")]
END = date(2024, 12, 31)


def test_the_loader_keeps_dimensional_values_under_their_segments_only_when_asked(structure, tmp_path):
    ddate = date(2024, 12, 31)
    assert structure.value_dim(COST, ddate, 4, "ProductOrService=Product;").value == Decimal("30000000")
    assert structure.value_dim(COST, ddate, 4, "ProductOrService=Other;") is None
    assert structure.value(COST, ddate, 4).value == Decimal("141000000")  # the total stays the no-dimension value
    plain = fsn.load_quarter(tmp_path, "2025q1", {ADSH})[ADSH]
    assert plain.dim_num == {} and plain.value(COST, ddate, 4).value == Decimal("141000000")


def test_a_dims_cell_is_proven_against_the_same_segments_sum(structure):
    out = prove_dims_cell(structure, PARTS, Decimal("42000000"), END, 4, Decimal("1500000"))
    assert out["verdict"] == PROVEN and out["position_value"] == Decimal("42000000")


def test_a_dims_cell_that_equals_the_total_or_another_slice_is_a_disagreement(structure):
    out = prove_dims_cell(structure, PARTS, Decimal("141000000"), END, 4, Decimal("1500000"))
    assert out["verdict"] == DISAGREE and out["reason_code"] == "shown_differs_from_printed_segments"


def test_a_part_the_filing_does_not_print_under_those_segments_is_unchecked_never_the_total(structure):
    parts = PARTS + [DimPart(COST, "ProductOrService=Other;")]
    out = prove_dims_cell(structure, parts, Decimal("141000000"), END, 4, Decimal("1500000"))
    assert out["verdict"] == UNCHECKED and out["missing"] == {"tag": COST, "dims": "ProductOrService=Other;"}
