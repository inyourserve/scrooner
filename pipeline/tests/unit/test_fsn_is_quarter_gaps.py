"""Income-statement missing quarters (queue item 2026-11-09): the net-income detector (lane G1b / G2b, imported from
is_detect), the 52/53-week key match and the PNC bottom-line anchor. Shapes are the real filings' face layouts
(FSN pre rows): MA 0001141391-26-000083 R2, ELS 0001628280-26-050244 R4, PNC 0000713676-26-000038 R2 and
0000713676-22-000047 R2, Exelon 0001109357-23-000067 R2."""

from __future__ import annotations

import subprocess
from datetime import date
from decimal import Decimal
from pathlib import Path

import psycopg
import pytest
from scrooner_pipeline.fsn_store import detectors, load, mapping, pilot, rules, shard
from scrooner_pipeline.fsn_store import is_detector as isd
from scrooner_pipeline.fsn_store import select as sel

REPO = Path(__file__).resolve().parents[3]


def _r(line, tag, label, stmt="IS", report=2, custom=False):
    return {"stmt": stmt, "report": report, "line": line, "tag": tag, "label": label, "custom": custom}


MA = [  # one bottom line, "Net Income" tagged ProfitLoss, EPS computed on it; no NCI line on IS/CI
    _r(1, "Revenues", "Net Revenue"),
    _r(15, "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest", "Income before income taxes"),
    _r(16, "IncomeTaxExpenseBenefit", "Income tax expense"),
    _r(17, "ProfitLoss", "Net Income"),
    _r(18, "EarningsPerShareBasic", "Basic Earnings per Share"),
]
ELS = [  # ProfitLoss, OP-unit NCI, the PARENT's preferred dividends, then income available to common
    _r(26, "InterestExpenseDebt", "Interest and related amortization", report=4),
    _r(30, "IncomeTaxExpenseBenefit", "Income tax", report=4),
    _r(31, "ProfitLoss", "Consolidated net income", report=4),
    _r(32, "NoncontrollingInterestInNetIncomeLossOperatingPartnershipsRedeemable", "Income allocated to non-controlling interests", report=4),
    _r(33, "RedeemablePreferredStockDividends", "Redeemable Perpetual Preferred Stock Dividends", report=4),
    _r(34, "NetIncomeLossAvailableToCommonStockholdersBasic", "Net income available for Common Stockholders", report=4),
]
ETR = [  # ProfitLoss bridged to the parent's line through NCI only
    _r(10, "IncomeTaxExpenseBenefit", "Income taxes"),
    _r(11, "ProfitLoss", "Consolidated net income"),
    _r(12, "NetIncomeLossAttributableToNoncontrollingInterest", "Less: noncontrolling interests"),
    _r(13, "NetIncomeLossAvailableToCommonStockholdersBasic", "Net income attributable to Entergy Corporation"),
    _r(14, "EarningsPerShareBasic", "Basic"),
]
EXC = [  # combined filing: NetIncomeLoss is the subsidiaries' member columns only
    _r(44, "IncomeTaxExpenseBenefit", "Income taxes"),
    _r(48, "ProfitLoss", "Net income (loss)"),
    _r(49, "NetIncomeLossAttributableToNoncontrollingInterest", "Net income (loss) attributable to noncontrolling interests"),
    _r(50, "NetIncomeLossAvailableToCommonStockholdersBasic", "Net Income (Loss) Available to Common Stockholders"),
    _r(53, "NetIncomeLoss", "Net income attributable to membership interest"),
    _r(54, "EarningsPerShareBasic", "Basic"),
]


@pytest.mark.unit
def test_ma_profit_loss_is_net_income_when_nothing_below_takes_a_share():
    d = isd.decide(MA, False, lambda t: True)
    assert d is not None and (d["line"], d["tag"], d["rule_id"]) == (17, "ProfitLoss", isd.RULE_G1B)


@pytest.mark.unit
def test_an_nci_line_anywhere_on_the_income_statement_blocks_profit_loss():
    rows = [*MA, _r(40, "NetIncomeLossAttributableToNoncontrollingInterest", "Net income attributable to NCI", stmt="CI", report=3)]
    assert isd.decide(rows, False, lambda t: True) is None


@pytest.mark.unit
def test_els_parent_preferred_between_profit_loss_and_common_line_is_never_net_income():
    # the common line comes after the parent's own preferred dividends: it is not net income, and ProfitLoss is
    # consolidated (OP-unit NCI below it): nothing is mapped, the seed's decision stands (no NetIncomeLoss line)
    assert isd.decide(ELS, False, lambda t: True) is None


@pytest.mark.unit
def test_nci_only_bridge_maps_the_available_to_common_line():
    d = isd.decide(ETR, False, lambda t: True)
    assert d is not None and (d["line"], d["rule_id"]) == (13, isd.RULE_G2B)
    assert d["tie"]["nci"] == ["NetIncomeLossAttributableToNoncontrollingInterest"]


@pytest.mark.unit
def test_exelon_net_income_line_without_a_parent_value_gives_way_to_the_bridge_line():
    d = isd.decide(EXC, True, lambda t: t != "NetIncomeLoss")
    assert d is not None and (d["line"], d["gate"]) == (50, "G2b_alt_no_parent_value")
    assert d["off"]["line"] == 53
    # with an undimensioned parent value the printed NetIncomeLoss line stands
    assert isd.decide(EXC, True, lambda t: True) is None


@pytest.mark.unit
def test_pep_52_53_week_quarter_end_matches_the_month_end_rounded_fsn_date():
    # PepsiCo Q2 2015 ends 2015-06-13; FSN rounds ddate to the nearest month end, 2015-05-31 (13 days)
    rows = [{"period_grain": "Q", "fsn_end": "2015-05-31", "state": "value"}]
    assert pilot._match(rows, "Q", date(2015, 6, 13)) is rows[0]
    # never the neighbouring quarter
    assert pilot._match(rows, "Q", date(2015, 3, 21)) is None


@pytest.mark.unit
def test_default_detectors_run_the_net_income_detector():
    assert detectors._is_net_income_detector in detectors.DEFAULT


# --- on the real schema: load -> seed -> map (DEFAULT detectors) -> select -------------------------------------


def _zst(path: Path, header: list[str], rows: list[list[str]]) -> None:
    body = "\n".join(["\t".join(header), *("\t".join(r) for r in rows)]) + "\n"
    path.write_bytes(subprocess.run(["zstd", "-q", "-c"], input=body.encode(), capture_output=True, check=True).stdout)


V = "us-gaap/2025"
NUM_H = ["adsh", "tag", "version", "ddate", "qtrs", "uom", "dimh", "iprx", "value", "footnote", "footlen", "dimn",
         "coreg", "durp", "datp", "dcml"]


def _company(tmp_path: Path, cik: str, acc: str, face: list[tuple[str, str]], values: dict[str, str]) -> Path:
    """one 10-Q (period 2026-06-30, 3M column) whose report 2 is the income statement `face` [(tag, label)]."""
    d = tmp_path / "companies" / cik
    d.mkdir(parents=True)
    _zst(d / "sub.tsv.zst", ["fsn_set", "adsh", "cik", "form", "period", "fy", "fp", "fye", "filed", "accepted", "prevrpt", "aciks"],
         [["2026m07", acc, cik.lstrip("0"), "10-Q", "20260630", "2026", "Q2", "1231", "20260729", "2026-07-29 16:05:00.0", "0", ""]])
    _zst(d / "pre.tsv.zst", ["adsh", "report", "line", "stmt", "inpth", "tag", "version", "prole", "plabel", "negating"],
         [[acc, "2", str(i + 1), "IS", "0", t, V, "terseLabel", lab, "0"] for i, (t, lab) in enumerate(face)])
    _zst(d / "num.tsv.zst", NUM_H,
         [[acc, t, V, "20260630", "1", "USD", "0x00000000", "0", v, "", "0", "0", "", "1.0", "0.0", "-6"] for t, v in values.items()])
    _zst(d / "cal.tsv.zst", ["adsh", "grp", "arc", "negative", "ptag", "pversion", "ctag", "cversion"], [])
    _zst(d / "ren.tsv.zst", ["adsh", "report", "rfile", "menucat", "shortname", "longname", "roleuri", "parentroleuri", "parentreport", "ultparentrpt"],
         [[acc, "2", "H", "S", "INCOME STATEMENTS", "0000002 - Statement - INCOME STATEMENTS", "http://x/role/IS", "", "", ""]])
    _zst(d / "tag.tsv.zst", ["tag", "version", "custom", "abstract", "datatype", "iord", "crdr", "tlabel", "doc"],
         [[t, V, "0", "0", "monetary", "D", "C", t, ""] for t, _ in face])
    _zst(d / "dim.tsv.zst", ["dimhash", "segments", "segt"], [])
    shard.finalize(tmp_path / "companies", cik, None, ["2026m07"], "test")
    return d


@pytest.fixture
def conn(isolated_database_url):
    c = psycopg.connect(isolated_database_url)
    if c.execute("select count(*) from information_schema.tables where table_schema = 'fsn' and table_name in ('filing', 'value', 'line_map', 'concept_rule')").fetchone()[0] != 4:
        c.close()
        pytest.skip("needs the fsn store migrations")
    for n in ("revenue_sanity_resolved", "income_tax_expense_resolved", "net_income_resolved", "basic_eps_resolved",
              "income_before_tax_resolved", "operating_income_resolved", "gross_profit_resolved", "cost_of_revenue_resolved",
              "interest_expense_resolved", "diluted_eps_resolved"):
        c.execute("insert into analytics.canonical_concept (name, statement, combination_mode) values (%s, 'income_statement', 'first_match') "
                  "on conflict (name) do nothing", (n,))
    c.commit()
    seeds = REPO / "data-team" / "47-fsn-store" / "concept_rules"
    for f in ("is.jsonl",):
        res = rules.seed(c, seeds / f, apply=True)
        assert not res["errors"], res["errors"]
    c.commit()
    yield c
    c.close()


def _store(conn, tmp_path, cik, acc, face, values, dets):
    cid = conn.execute("insert into core.company (cik, company_name) values (%s, 'TEST') returning id", (cik,)).fetchone()[0]
    conn.commit()
    load.load_company(conn, _company(tmp_path, cik, acc, face, values), loader_commit="t")
    conn.commit()
    mapping.map_company(conn, cid, mapping.load_rules(conn), detectors=dets)
    conn.commit()
    return cid, sel.load_company(conn, cid)


@pytest.mark.integration
def test_ma_shaped_10q_serves_net_income_from_the_profit_loss_line(conn, tmp_path):
    face = [("Revenues", "Net Revenue"), ("IncomeTaxExpenseBenefit", "Income tax expense"),
            ("ProfitLoss", "Net Income"), ("EarningsPerShareBasic", "Basic Earnings per Share")]
    vals = {"Revenues": "9277000000", "IncomeTaxExpenseBenefit": "1098000000", "ProfitLoss": "4388000000"}
    cid, data = _store(conn, tmp_path, "0001141391", "0001141391-26-000083", face, vals, detectors.DEFAULT)
    cells = sel.select_concept("net_income_resolved", data["prints"]["net_income_resolved"], data["filings"])
    q = [c for c in cells if c.qtrs == 1 and c.state == "value"]
    assert [(c.ddate, c.value, c.tag) for c in q] == [(date(2026, 6, 30), Decimal(4388000000), "ProfitLoss")]
    assert conn.execute(
        "select lm.rule_id from fsn.line_map lm join fsn.line l using (filing_id, report, line) join fsn.tag t on t.id = l.tag_id "
        "join fsn.filing f on f.id = lm.filing_id where f.company_id = %s and t.tag = 'ProfitLoss' and lm.status = 'mapped'", (cid,)
    ).fetchone()[0] == isd.RULE_G1B


@pytest.mark.integration
def test_without_the_detector_the_ma_quarter_has_no_net_income(conn, tmp_path):
    face = [("Revenues", "Net Revenue"), ("ProfitLoss", "Net Income")]
    _, data = _store(conn, tmp_path, "0001141391", "0001141391-26-000083", face,
                     {"Revenues": "9277000000", "ProfitLoss": "4388000000"}, [])
    assert "net_income_resolved" not in data["prints"]


@pytest.mark.integration
def test_pnc_continuing_ops_bottom_line_makes_the_column_a_face_column(conn, tmp_path):
    # PNC 10-Q 2022-03-31: no ProfitLoss / NetIncomeLoss on the face; the bottom line is tagged
    # IncomeLossFromContinuingOperationsIncludingPortionAttributableToNoncontrollingInterest ("Net income")
    face = [("Revenues", "Total revenue"),
            ("IncomeLossFromContinuingOperationsIncludingPortionAttributableToNoncontrollingInterest", "Net income"),
            ("IncomeLossFromContinuingOperationsAttributableToNoncontrollingEntity", "Less: NCI")]
    vals = {"Revenues": "4692000000",
            "IncomeLossFromContinuingOperationsIncludingPortionAttributableToNoncontrollingInterest": "1429000000",
            "IncomeLossFromContinuingOperationsAttributableToNoncontrollingEntity": "21000000"}
    _, data = _store(conn, tmp_path, "0000713676", "0000713676-22-000047", face, vals, detectors.DEFAULT)
    rev = data["prints"]["revenue_sanity_resolved"]
    assert [(p.value, p.face) for p in rev] == [(Decimal(4692000000), True)]


@pytest.mark.unit
def test_a_blank_from_a_9m_input_never_shuts_out_the_fy_route_to_the_quarter():
    # Rhythm 0001649904: FY2018 10-K (face FY, quarterly note Q4 -25,507); the 2019 Q1 10-Q's equity statement
    # prints a 9M ProfitLoss column ending 2018-12-31 (-57,605) with no 6M column before it
    from datetime import datetime

    f = {
        1: sel.Filing(1, "0001558370-19-001698", datetime(2019, 3, 1), "10-K", date(2018, 12, 31), 2018, "FY"),
        2: sel.Filing(2, "0001558370-19-003924", datetime(2019, 5, 1), "10-Q", date(2019, 3, 31), 2019, "Q1"),
    }
    end = date(2018, 12, 31)

    def p(i, fid, q, v, face):
        return sel.Print(i, fid, "ProfitLoss", end, q, "USD", Decimal(v), -3, "IS", face)

    prints = [p(1, 1, 4, -74064000, True), p(2, 1, 1, -25507000, False), p(3, 2, 3, -57605000, True)]
    cells = {(c.ddate, c.qtrs): c for c in sel.select_concept("net_income_resolved", prints, f)}
    q4 = cells[(end, 1)]
    assert (q4.state, q4.value, q4.rule_id) == ("value", Decimal(-25507000), sel.RULE_NOTE_Q)
    # without the FY route the 9M input's blank reason stays
    only = {(c.ddate, c.qtrs): c for c in sel.select_concept("net_income_resolved", [prints[2]], f)}
    assert only[(end, 1)].state == "defect"
