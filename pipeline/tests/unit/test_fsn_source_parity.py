"""The proof's two FilingStructure sources agree: SEC quarter files (proof/fsn.py) vs schema fsn (proof/fsn_db.py).

One small synthetic filing is written as quarter files AND as a company directory loaded by the real fsn_store
loader into the (throwaway copy of the) test database; both readers must give an identical FilingStructure and the
same verdict for the same cells. Needs the zstd binary and migrations 0118/0119 in the test database."""

from __future__ import annotations

import shutil
import subprocess
from datetime import date
from decimal import Decimal
from pathlib import Path

import psycopg
import pytest
from scrooner_pipeline.fsn_store import load, shard
from scrooner_pipeline.proof import fsn, prove as pv
from scrooner_pipeline.proof.fsn_db import load_filings
from scrooner_pipeline.proof.runner import StructureCache

ADSH = "0000000001-25-000001"
MISSING = "0000000001-25-000002"
CIK = "0000000001"
PERIOD = "2025q1"
STD = "us-gaap/2024"
END = date(2024, 12, 31)

SUB = ["adsh", "cik", "form", "filed", "period", "fy", "fp"]
PRE = ["adsh", "report", "line", "stmt", "inpth", "tag", "version", "prole", "plabel", "negating"]
CAL = ["adsh", "grp", "arc", "negative", "ptag", "pversion", "ctag", "cversion"]
NUM = "adsh tag version ddate qtrs uom dimh iprx value footnote footlen dimn coreg durp datp dcml".split()
DIM = ["dimhash", "segments", "segt"]


def _pre(report, line, stmt, tag, label, inpth="0", version=STD, negating="0"):
    return [ADSH, str(report), str(line), stmt, inpth, tag, version, "terseLabel", label, negating]


def _num(tag, value, qtrs="4", uom="USD", dimh="0x00000000", iprx="0", dimn="0", coreg="", dcml="-6", ddate="20241231", version=STD):
    row = dict.fromkeys(NUM, "")
    row.update(adsh=ADSH, tag=tag, version=version, ddate=ddate, qtrs=qtrs, uom=uom, dimh=dimh, iprx=iprx,
               value=value, dimn=dimn, coreg=coreg, dcml=dcml, footlen="0", durp="1.0", datp="0.0")
    return [row[c] for c in NUM]


PRE_ROWS = [
    _pre(2, 1, "IS", "Revenues", "Revenue"),
    _pre(2, 2, "IS", "CostOfRevenue", "Cost of revenue"),
    _pre(2, 3, "IS", "GrossProfit", "Gross margin"),
    _pre(2, 4, "IS", "CustomRevenue", "Custom revenue", version=ADSH),
    _pre(3, 1, "IS", "Revenues", "Revenue (parenthetical)", inpth="1"),  # parenthetical: never a face line
    _pre(4, 1, "BS", "Assets", "Total assets"),
    _pre(4, 2, "BS", "Liabilities", "Total liabilities"),
    _pre(4, 3, "BS", "StockholdersEquity", "Total equity"),
    _pre(4, 4, "BS", "LiabilitiesAndStockholdersEquity", "Total liabilities and equity"),
    _pre(6, 1, "CF", "NetIncomeLoss", "Net income", negating="1"),
    _pre(9, 1, "UN", "Revenues", "Revenue in a note"),  # an unclassified stmt is not a statement
]
CAL_ROWS = [
    [ADSH, "1", "1", "1", "GrossProfit", STD, "Revenues", STD],
    [ADSH, "1", "2", "-1", "GrossProfit", STD, "CostOfRevenue", STD],
    [ADSH, "2", "1", "1", "GrossProfit", STD, "Revenues", STD],  # the same arc under another role
    [ADSH, "3", "1", "1", "LiabilitiesAndStockholdersEquity", STD, "Liabilities", STD],
    [ADSH, "3", "2", "1", "LiabilitiesAndStockholdersEquity", STD, "StockholdersEquity", STD],
    [ADSH, "4", "1", "1", "CustomTotal", ADSH, "Revenues", STD],  # a filer-extension parent
]
NUM_ROWS = [
    _num("Revenues", "416161000000"),
    _num("Revenues", "380000000000", ddate="20231231"),
    _num("CostOfRevenue", "220000000000"),
    _num("GrossProfit", "196161000000"),
    _num("CustomRevenue", "5000000", version=ADSH),
    _num("NetIncomeLoss", "112010000000"),
    _num("Assets", "359241000000", qtrs="0"),
    _num("Liabilities", "285000000000", qtrs="0"),
    _num("StockholdersEquity", "74241000000", qtrs="0"),
    _num("LiabilitiesAndStockholdersEquity", "359241000000", qtrs="0"),
    _num("EarningsPerShareDiluted", "7.46", uom="USD/shares", dcml="2"),
    _num("EarningsPerShareDiluted", "7.46", uom="USD-per-shares", dcml="INF"),
    _num("SharesOutstanding", "7430000000", uom="shares", dcml=""),
    _num("Revenues", "100000000000", dimh="0xabc", dimn="1"),  # dimensional: .dim_num only
    _num("Revenues", "999", iprx="1"),  # a per-extension row: never read
    _num("Revenues", "888", coreg="0000000002"),  # a co-registrant row: never read
]
DIM_ROWS = [["0xabc", "ProductOrService=Service;", "0"]]


def _zst(path: Path, header: list[str], rows: list[list[str]]) -> None:
    text = "\t".join(header) + "\n" + "".join("\t".join(r) + "\n" for r in rows)
    subprocess.run(["zstd", "-q", "-f", "-o", str(path), "-"], input=text.encode(), check=True)


def _write_quarter(root: Path) -> None:
    d = root / PERIOD
    d.mkdir()
    _zst(d / f"{PERIOD}_sub.tsv.zst", SUB, [[ADSH, "1", "10-K", "20250201", "20241231", "2024", "FY"]])
    _zst(d / f"{PERIOD}_pre.tsv.zst", PRE, PRE_ROWS)
    _zst(d / f"{PERIOD}_cal.tsv.zst", CAL, CAL_ROWS)
    _zst(d / f"{PERIOD}_num.tsv.zst", NUM, NUM_ROWS)
    _zst(d / f"{PERIOD}_dim.tsv.zst", DIM, DIM_ROWS)


def _write_company_dir(root: Path) -> Path:
    d = root / "companies" / CIK
    d.mkdir(parents=True)
    _zst(d / "sub.tsv.zst",
         ["fsn_set", "adsh", "cik", "form", "period", "fy", "fp", "fye", "filed", "accepted", "prevrpt", "aciks"],
         [[PERIOD, ADSH, "1", "10-K", "20241231", "2024", "FY", "1231", "20250201", "2025-02-01 16:05:00.0", "0", ""]])
    _zst(d / "pre.tsv.zst", PRE, PRE_ROWS)
    _zst(d / "cal.tsv.zst", CAL, CAL_ROWS)
    _zst(d / "num.tsv.zst", NUM, NUM_ROWS)
    _zst(d / "dim.tsv.zst", DIM, DIM_ROWS)
    _zst(d / "ren.tsv.zst",
         ["adsh", "report", "rfile", "menucat", "shortname", "longname", "roleuri", "parentroleuri", "parentreport", "ultparentrpt"], [])
    tags = {(r[5], r[6]) for r in PRE_ROWS} | {(r[1], r[2]) for r in NUM_ROWS}
    _zst(d / "tag.tsv.zst", ["tag", "version", "custom", "abstract", "datatype", "iord", "crdr", "tlabel", "doc"],
         [[t, v, "0" if v.startswith("us-gaap") else "1", "0", "monetary", "D", "", t, ""] for t, v in sorted(tags)])
    shard.finalize(root / "companies", CIK, None, [PERIOD], "test")
    return d


@pytest.fixture
def seeded(isolated_database_url, tmp_path):
    if shutil.which("zstd") is None:
        pytest.skip("zstd binary not installed")
    conn = psycopg.connect(isolated_database_url)
    have = conn.execute(
        "select count(*) from information_schema.tables where table_schema = 'fsn' and table_name in ('filing', 'value', 'company_load')"
    ).fetchone()[0]
    if have != 3:
        conn.close()
        pytest.skip("needs migrations 0118/0119")
    conn.execute("insert into core.company (cik, company_name) values (%s, 'PARITY TEST')", (CIK,))
    conn.commit()
    root = tmp_path / "files"
    root.mkdir()
    _write_quarter(root)
    load.load_company(conn, _write_company_dir(tmp_path), loader_commit="parity")
    conn.commit()
    yield conn, root
    conn.close()


def _shown(name, value, grain="FY", tags=("x",)):
    start = END if grain == "I" else date(2024, 1, 1)
    return pv.Shown(3, name, grain, start, END, Decimal(value), tuple(tags), ADSH, (1,), False, 6)


CELLS = [
    _shown("total_assets_resolved", "359241000000", "I"),
    _shown("gross_profit_resolved", "196161000000"),
    _shown("cost_of_revenue_resolved", "220000000000"),
    _shown("net_income_resolved", "112010000000"),
    _shown("net_income_resolved", "99000000000", tags=("ProfitLoss",)),  # a wrong value: DISAGREE on both
    _shown("gross_profit_resolved", "1"),
]


def _verdicts(structure):
    out = []
    for c in CELLS:
        p = pv.prove_cell(c, structure, PERIOD)
        r = p.row()
        out.append((p.verdict, p.reason_code, r["position_value"], r["position_tag"], r["fsn_stmt"], r["fsn_line"], r["checks"]))
    return out


@pytest.mark.integration
def test_the_db_source_gives_the_identical_structure_and_verdicts(seeded):
    conn, root = seeded
    files = fsn.load_quarter(root, PERIOD, {ADSH}, with_dims=True)[ADSH]
    db = load_filings(conn, {ADSH}, with_dims=True)[ADSH]
    # field by field first, so a failure names the field
    for f in ("adsh", "cik", "form", "filed", "period", "fy", "fp", "pre", "calc_children", "calc_parents",
              "custom_parents", "calc_groups", "num", "dim_num"):
        assert getattr(db, f) == getattr(files, f), f
    assert db == files
    assert [v[0] for v in _verdicts(files)].count(pv.PROVEN) >= 3  # not a vacuous comparison
    assert any(v[0] == pv.DISAGREE for v in _verdicts(files))
    assert _verdicts(db) == _verdicts(files)
    # the filters the files reader applies are applied here too
    assert all(p.stmt != "UN" for p in db.pre) and len(db.pre) == 9
    assert db.value("Revenues", END, 4).value == Decimal("416161000000")
    assert db.value_dim("Revenues", END, 4, "ProductOrService=Service;").value == Decimal("100000000000")
    assert {v.dcml for v in db.num[("EarningsPerShareDiluted", END, 4)]} == {2, None}
    assert db.custom_parents["Revenues"] == {"CustomTotal"}


@pytest.mark.integration
def test_without_dims_the_db_source_keeps_only_plain_values(seeded):
    conn, root = seeded
    db = load_filings(conn, {ADSH}, with_dims=False)[ADSH]
    assert db == fsn.load_quarter(root, PERIOD, {ADSH})[ADSH]
    assert not db.dim_num


@pytest.mark.integration
def test_a_filing_the_store_lacks_falls_back_to_the_files_and_is_counted(seeded, tmp_path):
    conn, root = seeded
    assert set(load_filings(conn, {ADSH, MISSING})) == {ADSH}
    cache = StructureCache(root, conn, "db")
    cache.company = CIK
    got = cache.get_many({PERIOD: {ADSH, MISSING}})
    assert set(got) == {ADSH}  # MISSING is in neither source: absent, not invented
    assert cache.fallbacks == [(CIK, MISSING, PERIOD)]
    # a filing held by the store is never a fallback
    cache2 = StructureCache(root, conn, "db")
    assert set(cache2.get_many({PERIOD: {ADSH}})) == {ADSH} and cache2.fallbacks == []
