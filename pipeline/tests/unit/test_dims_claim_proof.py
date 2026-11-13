"""Member claims in the cell proof (R08/R09/R10/R11): a part written tag[Axis=Member] is read from the dimensional
rows under exactly those members; a plain part never reads a dimensional row. Synthetic FSN quarter through the
real loader (needs the zstd binary the proof job already needs)."""

from __future__ import annotations

import shutil
import subprocess
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest
from scrooner_pipeline.proof import fsn
from scrooner_pipeline.proof.dims import normalize_dims, split_part
from scrooner_pipeline.proof.prove import (
    PROVEN,
    UNCHECKED,
    Claim,
    Shown,
    prove_cell,
)

ADSH = "0000000001-25-000001"
NUM_COLS = ["adsh", "tag", "version", "ddate", "qtrs", "uom", "dimh", "iprx", "value", "footnote", "footlen", "dimn", "coreg", "durp", "datp", "dcml"]
COST = "CostOfGoodsAndServicesSold"
SHARES = "CommonStockSharesOutstanding"


def _zst(path: Path, header: list[str], rows: list[list[str]]) -> None:
    text = "\t".join(header) + "\n" + "".join("\t".join(r) + "\n" for r in rows)
    subprocess.run(
        ["zstd", "-q", "-f", "-o", str(path), "-"], input=text.encode(), check=True
    )


def _num(tag, dimh, value, dimn, qtrs="4", uom="USD"):
    row = dict.fromkeys(NUM_COLS, "")
    row.update(
        adsh=ADSH,
        tag=tag,
        version="us-gaap/2024",
        ddate="20241231",
        qtrs=qtrs,
        uom=uom,
        dimh=dimh,
        iprx="0",
        value=value,
        dimn=dimn,
        dcml="-6" if uom == "USD" else "0",
    )
    return [row[c] for c in NUM_COLS]


@pytest.fixture
def structure(tmp_path: Path) -> fsn.FilingStructure:
    if shutil.which("zstd") is None:
        pytest.skip("zstd binary not installed")
    d = tmp_path / "2025q1"
    d.mkdir()
    _zst(
        d / "2025q1_sub.tsv.zst",
        ["adsh", "cik", "form", "filed", "period", "fy", "fp"],
        [[ADSH, "1", "10-K", "20250201", "20241231", "2024", "FY"]],
    )
    _zst(
        d / "2025q1_pre.tsv.zst",
        [
            "adsh",
            "report",
            "line",
            "stmt",
            "inpth",
            "tag",
            "version",
            "plabel",
            "negating",
        ],
        [],
    )
    _zst(
        d / "2025q1_cal.tsv.zst",
        ["adsh", "grp", "arc", "negative", "ptag", "pversion", "ctag", "cversion"],
        [],
    )
    _zst(
        d / "2025q1_dim.tsv.zst",
        ["dimhash", "segments", "segt"],
        [
            ["0xP", "ProductOrService=Product;", "0"],
            ["0xS", "ProductOrService=Service;", "0"],
            ["0xA", "ClassOfStock=ClassA;", "0"],
            ["0xB", "ClassOfStock=ClassB;", "0"],
        ],
    )
    _zst(
        d / "2025q1_num.tsv.zst",
        NUM_COLS,
        [
            _num(COST, "0xP", "30000000", "1"),
            _num(COST, "0xS", "12000000", "1"),
            _num(COST, "0x00000000", "141000000", "0"),
            _num(SHARES, "0xA", "2000", "1", "0", "shares"),
            _num(SHARES, "0xB", "500", "1", "0", "shares"),
        ],
    )
    return fsn.load_quarter(tmp_path, "2025q1", {ADSH}, with_dims=True)[ADSH]


def _shown(
    name: str, value: str, parts, qtrs_grain="FY", start=date(2024, 1, 1), stmt="IS"
) -> Shown:
    return Shown(
        company_id=1,
        data_point_name=name,
        period_grain=qtrs_grain,
        period_start=start,
        period_end=date(2024, 12, 31),
        value=Decimal(value),
        tags=(),
        accession=ADSH,
        source_fact_ids=(),
        presentation_scale=6,
        claim=Claim("component", stmt, parts=tuple(parts)),
    )


PROD, SERV = "[ProductOrService=Product]", "[ProductOrService=Service]"


def test_member_claim_reads_the_member_value_not_the_total(structure):
    s = _shown(
        "cost_of_revenue_resolved", "42000000", [(1, COST + PROD), (1, COST + SERV)]
    )
    p = prove_cell(s, structure, "2025q1")
    assert p.verdict == PROVEN and p.position_value == Decimal(42000000)


def test_member_claim_equal_to_the_total_is_not_proven(structure):
    s = _shown(
        "cost_of_revenue_resolved", "141000000", [(1, COST + PROD), (1, COST + SERV)]
    )
    assert prove_cell(s, structure, "2025q1").verdict != PROVEN


def test_plain_claim_never_reads_dimensioned_rows(tmp_path, structure):
    # a filing that prints ONLY member rows: the plain tag has no value, so UNCHECKED, never a member stand-in
    structure.num.clear()
    s = _shown("cost_of_revenue_resolved", "42000000", [(1, COST)], stmt="UN")
    p = prove_cell(s, structure, "2025q1")
    assert p.verdict == UNCHECKED and p.position_value is None
    # and with the total present, the plain claim reads the total, not the members
    plain = fsn.load_quarter(tmp_path, "2025q1", {ADSH}, with_dims=True)[ADSH]
    q = prove_cell(
        _shown("cost_of_revenue_resolved", "141000000", [(1, COST)], stmt="UN"),
        plain,
        "2025q1",
    )
    assert q.position_value == Decimal(141000000)


def test_missing_member_is_unchecked_not_a_guess(structure):
    s = _shown(
        "cost_of_revenue_resolved",
        "141000000",
        [(1, COST + PROD), (1, COST + SERV), (1, COST + "[ProductOrService=Other]")],
    )
    p = prove_cell(s, structure, "2025q1")
    assert p.verdict == UNCHECKED and p.position_value is None


def test_without_the_dim_rows_a_member_claim_is_unchecked(tmp_path, structure):
    no_dims = fsn.load_quarter(tmp_path, "2025q1", {ADSH})[ADSH]
    s = _shown(
        "cost_of_revenue_resolved", "42000000", [(1, COST + PROD), (1, COST + SERV)]
    )
    assert prove_cell(s, no_dims, "2025q1").verdict == UNCHECKED


def test_multi_class_shares_are_the_sum_of_the_class_members(structure):
    parts = [
        (1, SHARES + "[ClassOfStock=ClassA]"),
        (1, SHARES + "[ClassOfStock=ClassB]"),
    ]
    s = _shown("shares_outstanding_resolved", "2500", parts, "I")
    p = prove_cell(s, structure, "2025q1")
    assert p.verdict == PROVEN and p.position_value == Decimal(2500)
    one_class = _shown("shares_outstanding_resolved", "2500", parts[:1], "I")
    assert prove_cell(one_class, structure, "2025q1").verdict != PROVEN


def test_member_syntax_is_parsed_and_a_bad_bracket_is_unchecked(structure):
    assert split_part("A") == ("A", "")
    assert split_part("A[us-gaap:ClassOfStockAxis=us-gaap:ClassAMember]") == (
        "A",
        "ClassOfStock=ClassA;",
    )
    assert normalize_dims("B=y,A=x") == "A=x;B=y;"
    bad = _shown("cost_of_revenue_resolved", "42000000", [(1, COST + "[oops")])
    assert prove_cell(bad, structure, "2025q1").verdict == UNCHECKED
