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
    "PGR": ROOT / "pipeline/tests/fixtures/fsn_is_structure/0000080661",
    "DIS": ROOT / "pipeline/tests/fixtures/fsn_is_structure/0001744489",
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


# ---------------------------------------------------------------- interest expense
INTEREST = is_structure.INTEREST


def _lines(conn, fid, concept):
    return conn.execute(
        """select t.tag, lm.rule_id from fsn.line_map lm join fsn.line l using (filing_id, report, line)
           join fsn.tag t on t.id = l.tag_id join analytics.canonical_concept c on c.id = lm.canonical_concept_id
           where lm.filing_id = %s and c.name = %s and lm.status = 'mapped'""",
        (fid, concept),
    ).fetchall()


@pytest.mark.integration
def test_single_gross_interest_line_under_a_debt_component_tag_maps(store):
    """Progressive FY2024 10-K prints one "Interest expense" line (279M) under InterestExpenseDebt"""
    rs = mapping.load_rules(store)
    fid = _fid(store, "PGR")
    mapping.map_filing(store, fid, rs, detectors=detectors.DEFAULT[:3])
    assert _lines(store, fid, INTEREST) == []
    mapping.map_filing(store, fid, rs, detectors=detectors.DEFAULT)
    assert _lines(store, fid, INTEREST) == [("InterestExpenseDebt", is_structure.INTEREST_RULE)]


@pytest.mark.integration
def test_net_interest_face_maps_no_interest_expense(store):
    """Disney prints only "Interest expense, net" (InterestIncomeExpenseNonoperatingNet): a net line is not gross
    interest expense, so nothing is mapped (its reason belongs to the certification lead)"""
    fid = _fid(store, "DIS")
    mapping.map_filing(store, fid, mapping.load_rules(store), detectors=detectors.DEFAULT)
    assert _lines(store, fid, INTEREST) == []


@pytest.mark.integration
def test_seed_interest_line_untouched(store):
    """ITW prints InterestExpenseNonoperating (the seed's tag); the detector adds nothing"""
    rs = mapping.load_rules(store)
    fid = _fid(store, "ITW")
    mapping.map_filing(store, fid, rs, detectors=detectors.DEFAULT[:3])
    before = _lines(store, fid, INTEREST)
    mapping.map_filing(store, fid, rs, detectors=detectors.DEFAULT)
    assert before == _lines(store, fid, INTEREST) and len(before) == 1 and before[0][0] == "InterestExpenseNonoperating"
    iid = _one(store, "select id from analytics.canonical_concept where name = %s", (INTEREST,))
    pgr = _fid(store, "PGR")
    mapping.map_filing(store, pgr, rs, detectors=detectors.DEFAULT[:3])
    decisions = store.execute(
        "select filing_id, report, line, canonical_concept_id, status from fsn.line_map where filing_id = %s", (pgr,)
    ).fetchall()
    assert is_structure.interest_detector(store, pgr, decisions)  # control
    assert is_structure.interest_detector(store, pgr, [*decisions, (pgr, 99, 1, iid, "mapped")]) == []


IE_FACE = [
    _row(1, "Revenues", "Revenues"),
    _row(2, "InterestExpenseDebt", "Interest expense"),
    _row(3, "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest", "Income before income taxes"),
    _row(4, "IncomeTaxExpenseBenefit", "Income taxes"),
]


def test_interest_slot_maps_the_only_gross_line():
    s = is_structure.interest_slot(IE_FACE)
    assert s["status"] == "mapped" and s["line"] == 2


def test_interest_slot_holds_two_interest_expense_lines():
    """a bank-like split (or debt + other interest) has no single total line"""
    face = [*IE_FACE, _row(5, "InterestExpenseOther", "Interest expense on other borrowings")]
    assert is_structure.interest_slot(face)["status"] == "held"


def test_interest_slot_holds_when_a_net_interest_line_is_printed():
    face = [*IE_FACE, _row(5, "InterestIncomeExpenseNonoperatingNet", "Interest income, net")]
    assert is_structure.interest_slot(face)["gate"] == "hold_interest_net_line_on_face"


def test_interest_slot_holds_a_net_or_other_label():
    """Cigna 'Interest expense and other', GE Vernova 'Interest and other financial charges - net'"""
    face = [IE_FACE[0], _row(2, "InterestExpenseDebt", "Interest expense and other"), *IE_FACE[2:]]
    assert is_structure.interest_slot(face)["status"] == "held"


def test_interest_slot_holds_a_custom_tag():
    """a company extension that reuses a standard local name is still the company's own element"""
    face = [IE_FACE[0], _row(2, "InterestExpenseDebt", "Interest expense", custom=True), *IE_FACE[2:]]
    assert is_structure.interest_slot(face)["status"] == "held"


@pytest.mark.parametrize(
    "label, ok",
    [
        ("Income (loss) before provision for (benefit from) income taxes", True),  # Guidewire, Okta
        ("Income before income taxes and noncontrolling interests", True),  # HEICO, Choice
        ("Income before income taxes, equity in income of affiliates", True),
        ("Pre-tax earnings", True),  # Lowe's, Goldman Sachs
        ("Loss from discontinued operations before income taxes", False),
        ("Net income attributable to noncontrolling interests before taxes", False),
        ("Deferred income tax expense", False),
        ("Income (Loss) from Continuing Operations", False),  # U-Haul: no before-tax wording, held
    ],
)
def test_pretax_label_class(label, ok):
    face = [FACE[0], _row(2, "EarningsBeforeIncomeTaxes", label, True), *FACE[2:]]
    assert (is_structure.pretax_slot(face, VALS)["status"] == "mapped") is ok
