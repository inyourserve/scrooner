"""scripts/build_note_report_lookup.py reads a filing under the COMPANY's CIK, not the accession's agent prefix."""

import csv
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load_script():
    spec = importlib.util.spec_from_file_location(
        "build_note_report_lookup", ROOT / "scripts" / "build_note_report_lookup.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ACC = "0001628280-26-005939"  # PM's FY2025 10-K, filed by agent 1628280


def test_edgar_cik_prefers_the_company_cik_over_the_agent_prefix():
    b = load_script()
    assert b.edgar_cik(ACC, {ACC: "0001413329"}) == 1413329
    assert (
        b.edgar_cik(ACC, {}) == 1628280
    )  # unknown to the store: the prefix is the only guess


def test_main_scans_edgar_with_the_company_cik(tmp_path, monkeypatch):
    b = load_script()
    cov = tmp_path / "cov.csv"
    cov.write_text(
        "locator_source,accession,tag,parts\n"
        f"note_fact_report_not_stored,{ACC},InterestExpenseNonoperating,\n"
    )
    cache = tmp_path / "cache"
    cache.mkdir()
    out = tmp_path / "lookup.csv"
    seen = {}

    def fake_scan(client, cik, adsh, tags):
        seen["cik"] = cik
        return {t: (105, 1) for t in tags}

    monkeypatch.setattr(b.nl, "scan_edgar", fake_scan)
    monkeypatch.setattr(b, "read_ciks", lambda accs: {ACC: "0001413329"})
    monkeypatch.setenv("SEC_USER_AGENT", "test agent test@example.com")
    monkeypatch.setattr(sys, "argv", ["x", str(cov), str(cache), str(out), "--edgar"])
    assert b.main([cov], cache, out, None) == 0
    assert seen["cik"] == 1413329
    rows = list(csv.DictReader(out.open()))
    assert [(r["accession"], r["tag"], r["report"]) for r in rows] == [
        (ACC, "InterestExpenseNonoperating", "105")
    ]


def test_wanted_parts_ask_for_the_base_tag_of_member_and_negative_parts(tmp_path, monkeypatch):
    """scan_edgar matches defref_<prefix>_<Tag>: a 'Tag[Axis=Member]' or '-Tag' pair can never be found, and the
    export's member path looks up the BASE tag (PM sbc AllocatedShareBasedCompensationExpense[AwardType=...])."""
    b = load_script()
    cov = tmp_path / "cov.csv"
    cov.write_text(
        "locator_source,accession,tag,parts\n"
        "component,A-1,X,"
        '"AllocatedShareBasedCompensationExpense[ShareBasedCompensationArrangementByShareBasedPaymentAwardAxis='
        'RestrictedStockUnitsRSUMember]=1@A-1#;-InvestmentIncomeInterest=2@A-1#;Paged=3@A-1#R4"\n'
    )
    monkeypatch.setattr(sys, "argv", ["x", "--parts-only"])
    assert b.wanted_pairs([cov]) == {
        ("A-1", "AllocatedShareBasedCompensationExpense"),
        ("A-1", "InvestmentIncomeInterest"),
    }
