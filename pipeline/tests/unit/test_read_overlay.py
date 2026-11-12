"""Full 10-K read overlay and the FY0/FY-1 check (pipeline/scripts/tag_library/read_overlay.py, coverage_fy.py), run the
way the scripts run: CSVs in, CSVs out."""

import csv
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
D = ROOT / "pipeline" / "scripts" / "tag_library"
TM = ["company_id", "cik", "taxonomy", "tag", "stmt", "decision", "canonical_concept", "parent_concept", "combine_sign", "components",
      "reason_class", "reason", "era_from", "era_to", "evidence_adsh", "evidence_report", "evidence_line", "evidence_plabel",
      "evidence_cal_parent", "decided_by", "rule_id", "rank", "ticker", "lines", "filings"]
RS = ["ticker", "company_id", "data_point", "verdict", "our_status", "printed_tag", "r_page", "printed_label", "printed_value",
      "not_printed", "evidence_adsh", "reason"]


def _write(path, fields, rows, base=None):
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({**{k: "" for k in fields}, **(base or {}), **r})


def _overlay(tmp_path, tm_rows, reads):
    p = {k: tmp_path / f"{k}.csv" for k in ("tm", "rs", "fy", "cat", "out", "tout", "rev")}
    _write(p["tm"], TM, tm_rows, {"company_id": "1", "ticker": "X", "taxonomy": "us-gaap", "lines": "1", "filings": "1", "decided_by": "library"})
    _write(p["rs"], RS, reads, {"company_id": "1", "ticker": "X", "not_printed": "False", "evidence_adsh": "0000000001-26-000001", "r_page": "R4"})
    _write(p["fy"], ["company_id", "period"], [{"company_id": "1", "period": "2025-12-31"}, {"company_id": "1", "period": "2024-12-31"}])
    p["cat"].write_text("name,statement,combination_mode\ndividends_per_share_resolved,income_statement,x\nshare_buybacks_resolved,cash_flow,x\n")
    subprocess.run([sys.executable, "-I", str(D / "read_overlay.py"), *(str(p[k]) for k in ("tm", "rs", "fy", "cat", "out", "tout", "rev"))],
                   check=True, capture_output=True)
    return list(csv.DictReader(open(p["out"]))), p


def test_a_note_printed_value_named_in_the_read_becomes_a_concept_row_over_fy_and_cuts_the_old_era(tmp_path):
    old = {"tag": "CommonStockDividendsPerShareDeclared", "stmt": "IS", "decision": "concept", "canonical_concept": "dividends_per_share_resolved",
           "era_from": "2015-03-31", "era_to": "2025-03-31"}
    read = {"data_point": "dividends_per_share", "verdict": "NEW-FOUND", "printed_value": "n/a",
            "reason": 'note era ends 2020-12-31; R121 prints "Dividends declared per common share" 1.44 / 1.12 (CommonStockDividendsPerShareCashPaid)'}
    got, _ = _overlay(tmp_path, [old], [read])
    con = sorted((r["tag"], r["era_from"], r["era_to"]) for r in got if r["decision"] == "concept")
    assert con == [("CommonStockDividendsPerShareCashPaid", "2024-12-31", "2025-12-31"), ("CommonStockDividendsPerShareDeclared", "2015-03-31", "2024-12-30")]
    assert any(r["decision"] == "excluded" and r["reason_class"] == "read_override" for r in got)


def test_a_line_the_read_finds_not_printed_gets_a_reason_row_for_fy_never_a_value(tmp_path):
    old = {"tag": "PaymentsForRepurchaseOfCommonStock", "stmt": "CF", "decision": "concept", "canonical_concept": "share_buybacks_resolved",
           "era_from": "2015-03-31", "era_to": "2023-12-31"}
    read = {"data_point": "share_buybacks", "verdict": "FAIL-GAP", "printed_value": "n/a",
            "reason": "era ends 2023-12-31; FY2025 CF prints no repurchase line (no buybacks); no not_presented reason"}
    got, p = _overlay(tmp_path, [old], [read])
    st = [r for r in got if r["decided_by"] == "read_status"]
    assert [(r["decision"], r["reason_class"], r["components"], r["era_from"], r["era_to"]) for r in st] == [
        ("excluded", "not_presented_read_verified", "share_buybacks_resolved", "2024-12-31", "2025-12-31")]
    assert not [r for r in got if r["decision"] == "concept" and r["era_to"] >= "2024-12-31"]
    cov, out = tmp_path / "cov.csv", tmp_path / "fyout.csv"
    _write(cov, ["company_id", "ticker", "template", "data_point", "status"], [{"company_id": "1", "ticker": "X", "data_point": "share_buybacks", "status": "sourced"}])
    _write(tmp_path / "open.csv", ["company_id", "stmt", "concept", "period", "why"], [])
    subprocess.run([sys.executable, "-I", str(D / "coverage_fy.py"), str(p["out"]), str(cov), str(p["fy"]), str(tmp_path / "open.csv"), str(out)],
                   check=True, capture_output=True)
    assert {r["status"] for r in csv.DictReader(open(out))} == {"read: not_presented_read_verified"}


def test_fy_check_flags_a_sourced_cell_with_no_row_and_no_reason(tmp_path):
    p = {k: tmp_path / f"{k}.csv" for k in ("tm", "cov", "fy", "open", "out")}
    _write(p["tm"], TM, [{"company_id": "1", "tag": "PaymentsForRepurchaseOfCommonStock", "stmt": "CF", "decision": "concept",
                          "canonical_concept": "share_buybacks_resolved", "era_from": "2015-03-31", "era_to": "2025-06-30", "decided_by": "library"}])
    _write(p["cov"], ["company_id", "ticker", "template", "data_point", "status"], [{"company_id": "1", "ticker": "X", "data_point": "share_buybacks", "status": "sourced"}])
    _write(p["fy"], ["company_id", "period"], [{"company_id": "1", "period": "2025-12-31"}, {"company_id": "1", "period": "2024-12-31"}])
    _write(p["open"], ["company_id", "stmt", "concept", "period", "why"], [])
    subprocess.run([sys.executable, "-I", str(D / "coverage_fy.py"), *(str(p[k]) for k in ("tm", "cov", "fy", "open", "out"))], check=True, capture_output=True)
    got = {r["fy"]: r["status"] for r in csv.DictReader(open(p["out"]))}
    assert got == {"FY0": "GAP", "FY-1": "served"}
