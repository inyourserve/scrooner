"""fsn_store.detectors.net_income_detector: net income where the seed (NetIncomeLoss only) maps no line.

Cohort dry run 41708119011: 25 companies had no net-income line mapped in any stored filing (no_mapped_line,
1,353 keys). Fixtures are real company directories built by fsn_store.shard from the SEC FSN 2025q1 set (one filing
each): ITW prints "Net Income" under ProfitLoss with no NCI (lane G1b); CAT bridges ProfitLoss through the NCI line to
NetIncomeLossAvailableToCommonStockholdersBasic (lane G2b); Booking prints "Net income" under the available-to-common
tag directly after the tax line (G2c, bottom line + tie); Boston Scientific prints a preferred-dividend line below
ProfitLoss (held: no line is the parent's figure as printed); Apple prints NetIncomeLoss (the seed's line, untouched).
"""

from decimal import Decimal
from pathlib import Path

import psycopg
import pytest

from scrooner_pipeline.fsn_store import detectors, load, mapping, rules

ROOT = Path(__file__).resolve().parents[3]
FX = ROOT / "pipeline" / "tests" / "fixtures" / "fsn_is_net_income"
NI = detectors.NI
CIKS = {"ITW": "0000049826", "CAT": "0000018230", "BKNG": "0001075531", "BSX": "0000885725", "AAPL": "0000320193"}


def _one(conn, sql, params=()):
    return conn.execute(sql, params).fetchone()[0]


@pytest.fixture
def store(isolated_database_url):
    c = psycopg.connect(isolated_database_url)
    if _one(c, "select count(*) from information_schema.tables where table_schema = 'fsn' and table_name in ('filing', 'line', 'concept_rule')") != 3:
        c.close()
        pytest.skip("needs migration 0118")
    for name in (NI, "income_before_tax_resolved", "income_tax_expense_resolved", "revenue_sanity_resolved"):
        c.execute(
            "insert into analytics.canonical_concept (name, statement, combination_mode) values (%s, 'income_statement', 'first_match') "
            "on conflict (name) do nothing",
            (name,),
        )
    for t in CIKS:
        c.execute("insert into core.company (cik, company_name) values (%s, %s)", (CIKS[t], t))
    c.commit()
    for t in CIKS:
        load.load_company(c, FX / CIKS[t], loader_commit="test")
        c.commit()
    for f in ("is.jsonl", "is_pretax_tax_interest.jsonl"):
        res = rules.seed(c, ROOT / "data-team" / "47-fsn-store" / "concept_rules" / f, apply=True)
        assert not res["errors"], res["errors"]
    c.commit()
    yield c
    c.close()


def _fid(conn, ticker):
    return _one(conn, "select f.id from fsn.filing f join core.company c on c.id = f.company_id where c.cik = %s", (CIKS[ticker],))


def _ni_lines(conn, fid):
    return conn.execute(
        """select t.tag, lm.rule_id from fsn.line_map lm join fsn.line l using (filing_id, report, line)
           join fsn.tag t on t.id = l.tag_id join analytics.canonical_concept c on c.id = lm.canonical_concept_id
           where lm.filing_id = %s and c.name = %s and lm.status = 'mapped'""",
        (fid, NI),
    ).fetchall()


@pytest.mark.integration
def test_seed_alone_maps_no_net_income_line_at_the_three_layouts(store):
    """the cohort gap reproduced: without the detector ITW, CAT and Booking have no net-income line"""
    rs = mapping.load_rules(store)
    for t in ("ITW", "CAT", "BKNG", "BSX"):
        fid = _fid(store, t)
        mapping.map_filing(store, fid, rs, detectors=[detectors.capex_da_detector])
        assert _ni_lines(store, fid) == [], t


@pytest.mark.integration
def test_detector_maps_exactly_one_net_income_line_per_layout(store):
    rs = mapping.load_rules(store)
    want = {
        "ITW": ("ProfitLoss", "is.net_income_profit_loss_no_nci@1"),
        "CAT": ("NetIncomeLossAvailableToCommonStockholdersBasic", "is.net_income_available_to_common_bridge@1"),
        "BKNG": ("NetIncomeLossAvailableToCommonStockholdersBasic", "is.net_income_bottom_line_tie@1"),
    }
    for t, line in want.items():
        fid = _fid(store, t)
        mapping.map_filing(store, fid, rs, detectors=detectors.DEFAULT)
        assert _ni_lines(store, fid) == [line], t


@pytest.mark.integration
def test_preferred_line_below_profit_loss_stays_held(store):
    """BSX FY2024 prints 'Dividends, Preferred Stock' between ProfitLoss and the available-to-common line: neither line
    is the parent's net income as printed, so nothing is mapped (the lane's hold_parent_line_not_standard)"""
    fid = _fid(store, "BSX")
    mapping.map_filing(store, fid, mapping.load_rules(store), detectors=detectors.DEFAULT)
    assert _ni_lines(store, fid) == []


@pytest.mark.integration
def test_seed_line_is_never_touched(store):
    """additive: Apple's NetIncomeLoss stays the seed's line, and the detector proposes nothing for that filing"""
    rs = mapping.load_rules(store)
    fid = _fid(store, "AAPL")
    mapping.map_filing(store, fid, rs, detectors=[detectors.capex_da_detector])
    before = _ni_lines(store, fid)
    mapping.map_filing(store, fid, rs, detectors=detectors.DEFAULT)
    assert before == _ni_lines(store, fid) == [("NetIncomeLoss", "is.net_income_line@1")]
    decisions = store.execute(
        "select filing_id, report, line, canonical_concept_id, status from fsn.line_map where filing_id = %s", (fid,)
    ).fetchall()
    assert detectors.net_income_detector(store, fid, decisions) == []


@pytest.mark.integration
def test_a_filing_whose_seed_maps_net_income_elsewhere_gets_nothing_more(store):
    """additive: CAT's G2b line would map, but when any line of the filing (here a fabricated seed decision on another
    report) already carries net income, the detector returns nothing, so select never sees two net-income lines"""
    fid = _fid(store, "CAT")
    rs = mapping.load_rules(store)
    mapping.map_filing(store, fid, rs, detectors=[detectors.capex_da_detector])
    ni_id = _one(store, "select id from analytics.canonical_concept where name = %s", (NI,))
    decisions = store.execute(
        "select filing_id, report, line, canonical_concept_id, status from fsn.line_map where filing_id = %s", (fid,)
    ).fetchall()
    assert detectors.net_income_detector(store, fid, decisions)  # control: it maps CAT's line
    seeded = [*decisions, (fid, 99, 1, ni_id, "mapped")]
    assert detectors.net_income_detector(store, fid, seeded) == []


def _perturb(monkeypatch, tag, delta):
    real = detectors.face_values

    def face_values(conn, filing_id, tags):
        vals = real(conn, filing_id, tags)
        for col in vals.values():
            if tag in col:
                v, dc = col[tag]
                col[tag] = (v + Decimal(delta), dc)
        return vals

    monkeypatch.setattr(detectors, "face_values", face_values)


@pytest.mark.integration
def test_bridge_that_does_not_tie_holds(store, monkeypatch):
    """G2b needs ProfitLoss - NCI = available-to-common in every face column; 100 million off (beyond the ±0.5M rounding of each $-million print) holds CAT"""
    _perturb(monkeypatch, "NetIncomeLossAvailableToCommonStockholdersBasic", 100_000_000)
    fid = _fid(store, "CAT")
    mapping.map_filing(store, fid, mapping.load_rules(store), detectors=detectors.DEFAULT)
    assert _ni_lines(store, fid) == []


@pytest.mark.integration
def test_bottom_line_that_does_not_tie_holds(store, monkeypatch):
    """G2c needs pretax - tax (+ lines between) = the bottom line in every face column; a tax print off by 100
    million (beyond rounding) holds Booking"""
    _perturb(monkeypatch, "IncomeTaxExpenseBenefit", 100_000_000)
    fid = _fid(store, "BKNG")
    mapping.map_filing(store, fid, mapping.load_rules(store), detectors=detectors.DEFAULT)
    assert _ni_lines(store, fid) == []


def _row(line, tag, label, stmt="IS", custom=False):
    return {"stmt": stmt, "report": 4, "line": line, "tag": tag, "custom": custom, "label": label, "negating": False}


BOTTOM_FACE = [
    _row(1, "Revenues", "Revenues"),
    _row(2, "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest", "Income before income taxes"),
    _row(3, "IncomeTaxExpenseBenefit", "Income tax expense"),
    _row(4, "NetIncomeLossAvailableToCommonStockholdersBasic", "Net income"),
    _row(5, "EarningsPerShareBasic", "Basic"),
]
BOTTOM_VALUES = {
    "20241231|4": {
        "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest": (Decimal(100), 0),
        "IncomeTaxExpenseBenefit": (Decimal(20), 0),
        "NetIncomeLossAvailableToCommonStockholdersBasic": (Decimal(80), 0),
    }
}


def test_bottom_line_ties_on_a_plain_face():
    d = detectors.decide_net_income(BOTTOM_FACE, False, BOTTOM_VALUES)
    assert d["status"] == "mapped" and d["gate"] == "G2c_bottom_line_tie" and d["line"] == 4


def test_bottom_line_holds_with_a_noncontrolling_label_anywhere_on_the_face():
    """a custom line labelled noncontrolling (in the comprehensive-income statement too) disqualifies the face"""
    rows = BOTTOM_FACE + [_row(9, "NetIncomeAttributableToOpUnits", "Net income attributable to noncontrolling interests", "CI", True)]
    d = detectors.decide_net_income(rows, False, BOTTOM_VALUES)
    assert d["status"] == "held" and d["gate"] == "hold_bottom_line_nci_or_preferred"


def test_bottom_line_skips_a_printed_subtotal_between_tax_and_net_income():
    """Hexcel: 'Income before equity in earnings' (= pretax - tax) then equity earnings, then net income"""
    rows = BOTTOM_FACE[:3] + [
        _row(4, "IncomeLossFromContinuingOperationsBeforeIncomeLossFromEquityMethodInvestments", "Income before equity in earnings"),
        _row(5, "IncomeLossFromEquityMethodInvestments", "Equity in earnings"),
        _row(6, "NetIncomeLossAvailableToCommonStockholdersBasic", "Net income"),
        _row(7, "IncomeLossFromContinuingOperationsPerDilutedShare", "Diluted net income per common share"),
    ]
    vals = {
        "20241231|4": {
            **BOTTOM_VALUES["20241231|4"],
            "IncomeLossFromContinuingOperationsBeforeIncomeLossFromEquityMethodInvestments": (Decimal(80), 0),
            "IncomeLossFromEquityMethodInvestments": (Decimal(5), 0),
            "NetIncomeLossAvailableToCommonStockholdersBasic": (Decimal(85), 0),
        }
    }
    d = detectors.decide_net_income(rows, False, vals)
    assert d["status"] == "mapped" and d["line"] == 6


def test_bottom_line_with_no_column_to_check_holds():
    d = detectors.decide_net_income(BOTTOM_FACE, False, {})
    assert d["status"] == "held" and d["gate"] == "hold_bottom_line_tie_uncheckable"
