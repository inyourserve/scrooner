"""fsn_store.is_structure: income-statement lines mapped by position + label + value tie, not by tag name.

Pre-tax (cohort dry run 41708119011: 39 companies with no pre-tax line in any filing). Real FSN 2025q1 company
directories: ITW prints "Income Before Taxes" under IncomeLossIncludingPortionAttributableToNoncontrollingInterest
(another concept's tag; card net-income-and-shares.md sec. 5); Flowserve under a custom tag EarningsBeforeIncomeTaxes;
Apple under the seed's standard tag (control: the seed's line, untouched)."""

from decimal import Decimal
from pathlib import Path

import psycopg
import pytest

from scrooner_pipeline.fsn_store import detectors, is_structure, load, mapping, rules

ROOT = Path(__file__).resolve().parents[3]
FIXTURES = {
    "ITW": ROOT / "pipeline/tests/fixtures/fsn_is_net_income/0000049826",
    "AAPL": ROOT / "pipeline/tests/fixtures/fsn_is_net_income/0000320193",
    "FLS": ROOT / "pipeline/tests/fixtures/fsn_is_structure/0000030625",
}
PRETAX = is_structure.PRETAX


def _one(conn, sql, params=()):
    return conn.execute(sql, params).fetchone()[0]


@pytest.fixture
def store(isolated_database_url):
    c = psycopg.connect(isolated_database_url)
    if _one(c, "select count(*) from information_schema.tables where table_schema = 'fsn' and table_name in ('filing', 'line', 'concept_rule')") != 3:
        c.close()
        pytest.skip("needs migration 0118")
    for name in (PRETAX, detectors.NI, "income_tax_expense_resolved", "interest_expense_resolved", "revenue_sanity_resolved"):
        c.execute(
            "insert into analytics.canonical_concept (name, statement, combination_mode) values (%s, 'income_statement', 'first_match') "
            "on conflict (name) do nothing",
            (name,),
        )
    for t, d in FIXTURES.items():
        c.execute("insert into core.company (cik, company_name) values (%s, %s)", (d.name, t))
        c.commit()
        load.load_company(c, d, loader_commit="test")
        c.commit()
    for f in ("is.jsonl", "is_pretax_tax_interest.jsonl"):
        res = rules.seed(c, ROOT / "data-team" / "47-fsn-store" / "concept_rules" / f, apply=True)
        assert not res["errors"], res["errors"]
    c.commit()
    yield c
    c.close()


def _fid(conn, t):
    return _one(conn, "select f.id from fsn.filing f join core.company c on c.id = f.company_id where c.cik = %s", (FIXTURES[t].name,))


def _pretax_lines(conn, fid):
    return conn.execute(
        """select t.tag, lm.rule_id from fsn.line_map lm join fsn.line l using (filing_id, report, line)
           join fsn.tag t on t.id = l.tag_id join analytics.canonical_concept c on c.id = lm.canonical_concept_id
           where lm.filing_id = %s and c.name = %s and lm.status = 'mapped'""",
        (fid, PRETAX),
    ).fetchall()


@pytest.mark.integration
def test_pretax_printed_under_another_concepts_tag_or_a_custom_tag_maps_by_position(store):
    rs = mapping.load_rules(store)
    for t, tag in (("ITW", "IncomeLossIncludingPortionAttributableToNoncontrollingInterest"), ("FLS", "EarningsBeforeIncomeTaxes")):
        fid = _fid(store, t)
        mapping.map_filing(store, fid, rs, detectors=detectors.DEFAULT[:2])
        assert _pretax_lines(store, fid) == [], t  # the cohort gap: the seed alone maps nothing
        mapping.map_filing(store, fid, rs, detectors=detectors.DEFAULT)
        assert _pretax_lines(store, fid) == [(tag, is_structure.PRETAX_RULE)], t


@pytest.mark.integration
def test_seed_pretax_line_is_untouched(store):
    rs = mapping.load_rules(store)
    fid = _fid(store, "AAPL")
    mapping.map_filing(store, fid, rs, detectors=detectors.DEFAULT[:2])
    before = _pretax_lines(store, fid)
    mapping.map_filing(store, fid, rs, detectors=detectors.DEFAULT)
    assert before == _pretax_lines(store, fid) and len(before) == 1 and before[0][1] != is_structure.PRETAX_RULE
    decisions = store.execute(
        "select filing_id, report, line, canonical_concept_id, status from fsn.line_map where filing_id = %s", (fid,)
    ).fetchall()
    assert is_structure.pretax_detector(store, fid, decisions) == []


@pytest.mark.integration
def test_a_filing_whose_seed_maps_pretax_elsewhere_gets_nothing_more(store):
    """additive: ITW's line would map, but a pre-tax decision anywhere in the filing (fabricated on another report)
    means the detector adds nothing, so select never sees two pre-tax lines"""
    fid = _fid(store, "ITW")
    mapping.map_filing(store, fid, mapping.load_rules(store), detectors=detectors.DEFAULT[:2])
    pid = _one(store, "select id from analytics.canonical_concept where name = %s", (PRETAX,))
    decisions = store.execute(
        "select filing_id, report, line, canonical_concept_id, status from fsn.line_map where filing_id = %s", (fid,)
    ).fetchall()
    assert is_structure.pretax_detector(store, fid, decisions)  # control
    assert is_structure.pretax_detector(store, fid, [*decisions, (fid, 99, 1, pid, "mapped")]) == []


@pytest.mark.integration
def test_pretax_that_does_not_tie_holds(store, monkeypatch):
    real = detectors.face_values

    def face_values(conn, filing_id, tags):
        vals = real(conn, filing_id, tags)
        for col in vals.values():
            if "IncomeTaxExpenseBenefit" in col:
                v, dc = col["IncomeTaxExpenseBenefit"]
                col["IncomeTaxExpenseBenefit"] = (v + Decimal(100_000_000), dc)
        return vals

    monkeypatch.setattr(detectors, "face_values", face_values)
    fid = _fid(store, "ITW")
    mapping.map_filing(store, fid, mapping.load_rules(store), detectors=detectors.DEFAULT)
    assert _pretax_lines(store, fid) == []


def _row(line, tag, label, custom=False):
    return {"stmt": "IS", "report": 4, "line": line, "tag": tag, "custom": custom, "label": label, "negating": False}


FACE = [
    _row(1, "Revenues", "Revenues"),
    _row(2, "EarningsBeforeIncomeTaxes", "Income before income taxes", True),
    _row(3, "IncomeTaxExpenseBenefit", "Provision for income taxes"),
    _row(4, "NetIncomeLoss", "Net income"),
    _row(5, "EarningsPerShareBasic", "Basic"),
]
VALS = {"20241231|4": {"EarningsBeforeIncomeTaxes": (Decimal(100), 0), "IncomeTaxExpenseBenefit": (Decimal(20), 0), "NetIncomeLoss": (Decimal(80), 0)}}


def test_pretax_slot_maps_the_line_above_tax_that_ties():
    s = is_structure.pretax_slot(FACE, VALS)
    assert s["status"] == "mapped" and s["line"] == 2


def test_pretax_slot_holds_a_line_above_tax_without_a_before_tax_label():
    """Macerich prints equity in JV losses, Agree Realty interest expense, directly above a tax line"""
    face = [FACE[0], _row(2, "InterestExpenseNonoperating", "Interest expense, net"), *FACE[2:]]
    vals = {"20241231|4": {"InterestExpenseNonoperating": (Decimal(100), 0), **{k: v for k, v in VALS["20241231|4"].items() if k != "EarningsBeforeIncomeTaxes"}}}
    s = is_structure.pretax_slot(face, vals)
    assert s["status"] == "held" and s["gate"] == "hold_pretax_label_not_before_tax"


def test_pretax_slot_holds_a_discontinued_operations_pretax_line():
    face = [FACE[0], _row(2, "DiscontinuedPretax", "Loss from discontinued operations before income taxes", True), *FACE[2:]]
    s = is_structure.pretax_slot(face, VALS)
    assert s["status"] == "held" and s["gate"] == "hold_pretax_label_not_before_tax"


def test_pretax_slot_holds_a_face_without_a_tax_line():
    """most equity REITs print no income-tax line: an absence, not a mapping gap"""
    s = is_structure.pretax_slot([FACE[0], FACE[1], FACE[3]], VALS)
    assert s["status"] == "held" and s["gate"] == "hold_pretax_no_tax_line"
