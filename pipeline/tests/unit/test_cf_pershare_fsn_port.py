"""Cash-flow and per-share lanes on the FSN store (data-team/strategy/team/CF-PERSHARE-PORT-2026-11-01.md), gate A.

Fixtures: pipeline/tests/fixtures/fsn_company_cf/<cik10>/ (plain .tsv, FORMATS-v1 section 1), rows copied from the
SEC FSN data sets by fsn_sec_fixture.py for filings the Verifier opened. The SAME rows were run through the
UNCHANGED run 7 pipeline (cf_face_rows -> cf_num_rows -> cf_cal_rows -> cf_family_replay @ work/cashflow/v2-emit
2e061bc); its intermediates and cells are committed in results/cf_port_gate_2026-11-01/. Checks:
  1. company mode (cf_family_replay.py --company) = run 7's cells, every family, cell for cell
  2. the refactored cohort mode on run 7's intermediates = run 7's cells, byte for byte
  3. the Verifier's filing-checked values and holds come out of company mode
  4. per-share: filed EPS from the quarterly-data note, Q4 DPS = FY - 9M on one basis, EPS never derived,
     a split between the two DPS inputs blocks the derivation
  5. the per-share selection functions are eps_fsn_scan.py's, moved unchanged (ast)
  6. the concept_rule seeds are valid FORMATS-v1 rows
Scripts run the way the lane runs them: <python> -I <script>.
"""

import ast
import gzip
import json
import shutil
import subprocess
import sys
from collections import Counter
from decimal import Decimal
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
S = ROOT / "pipeline" / "scripts" / "slot_records"
PS = ROOT / "pipeline" / "scripts" / "per_share"
FX = ROOT / "pipeline" / "tests" / "fixtures" / "fsn_company_cf"
GATE = S / "results" / "cf_port_gate_2026-11-01"
SEEDS = ROOT / "data-team" / "47-fsn-store" / "concept_rules"
FAMILIES = ("cfo", "buybacks", "dividends_paid")


def run(script, *args):
    p = subprocess.run([sys.executable, "-I", str(script), *map(str, args)], capture_output=True, text=True)
    assert p.returncode == 0, p.stderr
    return p.stdout


def cells(d, fam):
    with gzip.open(Path(d) / f"{fam}_cells.jsonl.gz", "rt") as fh:
        return [json.loads(x) for x in fh]


@pytest.fixture(scope="module")
def company(tmp_path_factory):
    out = tmp_path_factory.mktemp("cf_company")
    run(S / "cf_family_replay.py", "--company", FX, out)
    return out


@pytest.fixture(scope="module")
def pershare(tmp_path_factory):
    out = tmp_path_factory.mktemp("pershare") / "cells.jsonl"
    run(S / "fsn_company_pershare.py", FX, out)
    return [json.loads(x) for x in out.read_text().splitlines()]


def cell(cs, cik, end, months, accession=None):
    hits = [c for c in cs if c["cik"] == cik and c["end"] == end and c["months"] == months
            and (accession is None or c["accession"] == accession)]
    assert len(hits) == 1, hits
    return hits[0]


# ---------------------------------------------------------------- 1, 2: regression vs run 7
@pytest.mark.parametrize("fam", FAMILIES)
def test_company_mode_equals_run7_cells(company, fam):
    got = Counter(json.dumps(c, sort_keys=True) for c in cells(company, fam))
    want = Counter(json.dumps(c, sort_keys=True) for c in cells(GATE / "run7", fam))
    assert sum(want.values()) > 0
    assert got == want


def test_refactored_cohort_mode_is_byte_identical_to_run7(tmp_path):
    run(S / "cf_family_replay.py", GATE / "face.jsonl.gz", GATE / "num.jsonl.gz", GATE / "cal.jsonl.gz", tmp_path)
    for fam in FAMILIES:
        with gzip.open(tmp_path / f"{fam}_cells.jsonl.gz", "rb") as a, gzip.open(GATE / "run7" / f"{fam}_cells.jsonl.gz", "rb") as b:
            assert a.read() == b.read(), fam


# ---------------------------------------------------------------- 3: Verifier cells (FILING-CHECKED)
def test_buybacks_emr_fy2024_excludes_the_subsidiary_repurchase(company):
    # VERIFY-BUYBACKS-R2-2026-11-04: 435M; "AspenTech purchases of common stock" (208) excluded
    c = cell(cells(company, "buybacks"), "0000032604", "2024-09-30", 12, "0000032604-24-000041")
    assert (c["verdict"], Decimal(c["value"])) == ("publishable", Decimal("435000000"))
    classes = {m["label"]: m["class"] for m in c["detail"]["members"]}
    assert classes["AspenTech purchases of common stock"] == "perimeter_subsidiary_repurchase"


def test_buybacks_gpn_fy2022_excludes_share_based_compensation_plans(company):
    # VERIFY-BUYBACKS-R2-2026-11-04: 2,921,307K; "Share-based compensation plans" (38,601) excluded
    c = cell(cells(company, "buybacks"), "0001123360", "2022-12-31", 12, "0001123360-23-000009")
    assert (c["verdict"], Decimal(c["value"])) == ("publishable", Decimal("2921307000"))


def test_buybacks_rost_fy2019_two_repurchase_lines_are_held(company):
    # VERIFY-BUYBACKS-RUN3-2026-11-01: ROST FY2019 perimeter_multiple_repurchase_lines
    c = cell(cells(company, "buybacks"), "0000745732", "2020-01-31", 12, "0000745732-20-000016")
    assert c["verdict"] == "perimeter_multiple_repurchase_lines" and c["value"] is None


def test_buybacks_ldos_fy2020_combined_line_is_held(company):
    # VERIFY-BUYBACKS-RUN3-2026-11-01: LDOS FY2020 "Repurchases of stock and other" -> combined
    c = cell(cells(company, "buybacks"), "0001336920", "2020-12-31", 12, "0001336920-21-000010")
    assert c["verdict"] == "buyback_combined_with_other_items" and c["value"] is None


def test_cfo_so_fy2024_and_gm_q1_2016(company):
    # VERIFY-CFO-BUYBACKS-RUN2-2026-11-01: SO FY2024 9,788M; GM Q1 2016 (164)M
    cs = cells(company, "cfo")
    so = cell(cs, "0000092122", "2024-12-31", 12, "0000092122-25-000018")
    assert (so["verdict"], Decimal(so["value"])) == ("publishable", Decimal("9788000000"))
    gm = cell(cs, "0001467858", "2016-03-31", 3)
    assert (gm["verdict"], Decimal(gm["value"])) == ("publishable", Decimal("-164000000"))


def test_dividends_and_dividend_equivalents_count_as_common(company):
    # founder ruling 2026-11-01: AAPL "Payments for dividends and dividend equivalents" is common dividends paid
    c = cell(cells(company, "dividends_paid"), "0000320193", "2024-09-30", 12, "0000320193-24-000123")
    assert c["verdict"] == "publishable" and Decimal(c["value"]) == Decimal("15234000000")
    assert [m["class"] for m in c["detail"]["members"]] == ["common"]


# ---------------------------------------------------------------- 4: per share
def ps(cs, cik, concept, ddate, qtrs):
    hits = [c for c in cs if c["cik"] == cik and c["concept"] == concept and c["ddate"] == ddate and c["qtrs"] == qtrs]
    assert len(hits) == 1, hits
    return hits[0]


def test_q4_dps_is_fy_minus_9m_on_one_basis(pershare):
    # VERIFY-SPLIT-RELEASE-2-2026-11-04: CFG Q4 2017 0.64 - 0.46 = 0.18; OGE Q4 2018 1.395 - 1.030 = 0.365
    cfg = ps(pershare, "0000759944", "dividends_per_share_resolved", "20171231", 1)
    assert (cfg["verdict"], Decimal(cfg["value"])) == ("derived", Decimal("0.18"))
    assert cfg["inputs"] == ["0000759944-18-000016", "0000759944-17-000073"]
    oge = ps(pershare, "0001021635", "dividends_per_share_resolved", "20181231", 1)
    assert (oge["verdict"], Decimal(oge["value"])) == ("derived", Decimal("0.365"))


def test_eps_q4_comes_from_the_filed_quarterly_note(pershare):
    # VERIFY-EPS-FAMILY-C-V3-2026-11-02: Charter Q4 2015 -1.09 (10-K quarterly data); News Corp Q4 FY2015 -0.65
    chtr = ps(pershare, "0001091667", "basic_eps_resolved", "20151231", 1)
    assert (chtr["verdict"], Decimal(chtr["value"]), chtr["accession"]) == ("filed", Decimal("-1.09"), "0001091667-16-000396")
    nws = ps(pershare, "0001564708", "basic_eps_resolved", "20150630", 1)
    assert (nws["verdict"], Decimal(nws["value"])) == ("filed", Decimal("-0.65"))


def test_eps_is_never_derived(pershare):
    eps = [c for c in pershare if c["concept"] in ("basic_eps_resolved", "diluted_eps_resolved")]
    assert eps and all(c["verdict"] in ("filed", "hidden_fsn_copies_disagree", "hidden_only_rejected_axes") for c in eps)
    # CFG files FY and 9M EPS but no 3-month Q4: no Q4 EPS cell exists (the calendar blanks it)
    for concept in ("basic_eps_resolved", "diluted_eps_resolved"):
        assert ps(pershare, "0000759944", concept, "20171231", 4)["verdict"] == "filed"
        assert not [c for c in pershare if c["cik"] == "0000759944" and c["concept"] == concept and c["ddate"] == "20171231" and c["qtrs"] == 1]
    assert all(c["verdict"] != "derived" for c in pershare if c["concept"] != "dividends_per_share_resolved")


def test_a_split_between_the_dps_inputs_blocks_the_derivation(tmp_path):
    # synthetic, in tmp only: a cover share count stepping 2:1 between the 10-Q and the 10-K is a split signal
    d = tmp_path / "0000759944"
    shutil.copytree(FX / "0000759944", d)
    lines = (d / "num.tsv").read_text().splitlines()
    cols = lines[0].split("\t")
    rows = [dict(zip(cols, x.split("\t"))) for x in lines[1:]]
    proto = next(r for r in rows if r["dimh"] == "0x00000000")
    for adsh, v in (("0000759944-17-000073", "500000000"), ("0000759944-18-000016", "1000000000")):
        rows.append({**proto, "adsh": adsh, "tag": "EntityCommonStockSharesOutstanding", "version": "dei/2017", "ddate": "20180101",
                     "qtrs": "0", "uom": "shares", "dimh": "0x00000000", "iprx": "0", "value": v, "coreg": "", "dimn": "0"})
    (d / "num.tsv").write_text("\n".join(["\t".join(cols)] + ["\t".join(r[c] for c in cols) for r in rows]) + "\n")
    out = tmp_path / "cells.jsonl"
    run(S / "fsn_company_pershare.py", d, out)
    got = ps([json.loads(x) for x in out.read_text().splitlines()], "0000759944", "dividends_per_share_resolved", "20171231", 1)
    assert got["verdict"] == "hidden_dps_inputs_not_on_one_basis" and got["value"] is None


# ---------------------------------------------------------------- 5: moved, not changed
def _fn(tree, name):
    return next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == name)


def _body(stmts):
    return [ast.dump(s) for s in stmts if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))]


def test_pershare_rules_are_eps_fsn_scan_unchanged():
    old = ast.parse((PS / "eps_fsn_scan.py").read_text())
    new = ast.parse((PS / "pershare_fsn_rules.py").read_text())
    consts = lambda t: {n.targets[0].id: ast.dump(n.value) for n in t.body if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name)}  # noqa: E731
    co, cn = consts(old), consts(new)
    for k in ("TAGS", "QUARTERLY_AXIS", "REJECT_AXIS", "FORMS"):
        assert co[k] == cn[k], k
    for f in ("month_end", "allowed", "same", "swapped_copies"):
        assert _body(_fn(old, f).body) == _body(_fn(new, f).body), f
    # select() = the scan's per-cell loop body from `found = []` through the outcome if/else
    loop = next(n for n in old.body if isinstance(n, ast.For) and ast.unparse(n.target) == "c" and ast.unparse(n.iter) == "cells"
                and any(ast.unparse(s) == "found = []" for s in n.body))
    start = next(i for i, s in enumerate(loop.body) if ast.unparse(s) == "found = []")
    end = next(i for i, s in enumerate(loop.body) if isinstance(s, ast.If) and "not_in_fsn" in ast.unparse(s.body[0]))
    # the one substitution: the cell's own tag list `c["tags"]` is select()'s parameter `tags`
    old_src = [ast.unparse(x).replace("c['tags']", "tags") for x in loop.body[start:end + 1]]
    assert old_src == [ast.unparse(x) for x in _fn(new, "select").body[1:-1]]


# ---------------------------------------------------------------- 6: seeds
def test_seeds_are_valid_formats_v1_rows():
    from scrooner_pipeline.fsn_store.rules import validate

    for lane, needed in (("cf", {"cfo_resolved", "share_buybacks_resolved", "dividends_paid_resolved"}),
                         ("per_share", {"dividends_per_share_resolved", "shares_outstanding_resolved", "basic_eps_resolved"})):
        rows = [json.loads(x) for x in (SEEDS / f"{lane}.jsonl").read_text().splitlines()]
        assert validate(rows, {r["canonical_concept"]: i for i, r in enumerate(rows)}) == []
        assert needed <= {r["canonical_concept"] for r in rows}
    cf = {(r["canonical_concept"], r["tag"]) for r in (json.loads(x) for x in (SEEDS / "cf.jsonl").read_text().splitlines())}
    assert ("cfo_resolved", "us-gaap:NetCashProvidedByUsedInOperatingActivities") in cf
    assert ("share_buybacks_resolved", "us-gaap:PaymentsForRepurchaseOfCommonStock") in cf
    # exclusions are never a seed row for the concept (tax withholding is not a buyback)
    assert not any(t == "us-gaap:PaymentsRelatedToTaxWithholdingForShareBasedCompensation" for _c, t in cf)
