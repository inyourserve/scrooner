"""Company mapping notes generator (pipeline/scripts/tag_library/company_notes.py), run the way the script runs: CSVs in, Markdown out."""

import csv
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
GEN = ROOT / "pipeline" / "scripts" / "tag_library" / "company_notes.py"
FIELDS = ["company_id", "cik", "taxonomy", "tag", "stmt", "decision", "canonical_concept", "parent_concept", "combine_sign",
          "components", "reason_class", "reason", "era_from", "era_to", "evidence_adsh", "evidence_report", "evidence_line",
          "evidence_plabel", "evidence_cal_parent", "decided_by", "rule_id", "rank", "ticker", "lines", "filings"]


def _row(**kw):
    base = {k: "" for k in FIELDS}
    base.update(company_id="9", cik="0000000009", taxonomy="us-gaap", era_from="2015-03-31", era_to="2025-12-31",
                evidence_adsh="0000000009-25-000001", rank="1", ticker="TST", lines="3", filings="3", decided_by="rule")
    base.update(kw)
    return base


def _run(tmp_path, rows, exc=(), std=()):
    tm, ident, out = tmp_path / "tm.csv", tmp_path / "id.csv", tmp_path / "out"
    with open(tm, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    ident.write_text("company_id,cik,name,ticker,sic_code,sector\n9,0000000009,Test Co,TST,3571,Technology\n")
    cmd = [sys.executable, "-I", str(GEN), "--tag-map", str(tm), "--identity", str(ident), "--out", str(out)]
    if exc:
        p = tmp_path / "exc.csv"
        p.write_text("company_id,ticker,stmt,tag,decision,concept,era_from,era_to,n_filings,reason\n" + "\n".join(exc) + "\n")
        cmd += ["--exceptions", str(p)]
    if std:
        p = tmp_path / "std.csv"
        p.write_text("rank,tag,statements,decision,concept,reason\n" + "\n".join(std) + "\n")
        cmd += ["--std-tags", str(p)]
    subprocess.run(cmd, check=True, capture_output=True)
    return (out / "TST.md").read_text()


def _table_row(md, dp):
    return [ln for ln in md.splitlines() if ln.startswith(f"| {dp} |")]


ROWS = [
    _row(tag="Revenues", stmt="IS", decision="concept", canonical_concept="revenue_sanity_resolved", evidence_plabel="Total revenue"),
    _row(tag="NetIncomeLoss", stmt="IS", decision="concept", canonical_concept="net_income_resolved", evidence_plabel="Net income"),
    _row(tag="SellingAndMarketingExpense", stmt="IS", decision="component", parent_concept="sga_expense", combine_sign="1"),
    _row(tag="AccountsPayableAndAccruedLiabilitiesCurrent", stmt="BS", decision="combined", components="accounts_payable;accrued_liabilities"),
    _row(tag="DocumentType", stmt="CP", decision="excluded", reason_class="cover_or_parenthetical", reason="cover"),
    _row(tag="Mystery", stmt="BS", decision="", decided_by="residue", evidence_plabel="Odd line"),
]


def test_note_has_all_sections_and_statuses(tmp_path):
    md = _run(tmp_path, ROWS)
    for h in ("# Test Co (TST)", "CIK 0000000009", "## Data points", "## Company exceptions", "## Excluded lines",
              "## Open items", "## Certification"):
        assert h in md
    assert "us-gaap:Revenues (2015-03-31 to 2025-12-31)" in _table_row(md, "revenue")[0]
    assert "| mapped |" in _table_row(md, "net_income")[0]
    assert "| component sum |" in _table_row(md, "sga_expense")[0]
    assert "| combined |" in _table_row(md, "accounts_payable")[0]
    assert "| undecided |" in _table_row(md, "goodwill")[0]  # no row anywhere: never filled in
    assert "UNDECIDED data point `goodwill`" in md
    assert "UNDECIDED line BS us-gaap:Mystery" in md
    assert "- cover_or_parenthetical: 1" in md
    assert "cell_proof PROVEN share: pending" in md


def test_dropping_a_mapped_row_changes_the_note(tmp_path):
    full = _run(tmp_path, ROWS)
    (tmp_path / "b").mkdir()
    dropped = _run(tmp_path / "b", [r for r in ROWS if r["tag"] != "Revenues"])
    assert "| mapped |" in _table_row(full, "revenue")[0]
    assert "| undecided |" in _table_row(dropped, "revenue")[0]
    assert "UNDECIDED data point `revenue`" in dropped and "UNDECIDED data point `revenue`" not in full


def test_exceptions_and_std_tags_are_applied(tmp_path):
    exc = ["9,TST,IS,,not_presented,gross_profit,,,3,TST prints no gross profit line"]
    std = ["400,us-gaap:Mystery,BS/CF,map,goodwill,odd line is goodwill"]
    md = _run(tmp_path, ROWS, exc, std)
    assert "| not presented |" in _table_row(md, "gross_profit")[0]
    assert "TST prints no gross profit line" in md.split("## Company exceptions")[1].split("## Excluded")[0]
    assert "| mapped |" in _table_row(md, "goodwill")[0] and "std-tags decision rank 400" in _table_row(md, "goodwill")[0]
    assert "UNDECIDED line BS us-gaap:Mystery" not in md


def test_coverage_status_replaces_undecided_and_candidates_become_pending_verifier(tmp_path):
    cov = tmp_path / "cov.csv"
    cov.write_text("company_id,ticker,template,data_point,status\n"
                   "9,TST,general,total_debt,held C8 (debt lane)\n"
                   "9,TST,general,interest_income,note-sourced candidate (Verifier draw)\n")
    tm, ident, out = tmp_path / "tm.csv", tmp_path / "id.csv", tmp_path / "out"
    with open(tm, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(ROWS)
    ident.write_text("company_id,cik,name,ticker,sic_code,sector\n9,0000000009,Test Co,TST,3571,Technology\n")
    subprocess.run([sys.executable, "-I", str(GEN), "--tag-map", str(tm), "--identity", str(ident), "--out", str(out),
                    "--coverage", str(cov)], check=True, capture_output=True)
    md = (out / "TST.md").read_text()
    assert "held C8" in _table_row(md, "total_debt")[0]
    assert "PENDING VERIFIER `interest_income`" in md
    assert "UNDECIDED data point `total_debt`" not in md
    assert "UNDECIDED data point" not in md  # points outside the coverage file are 'not in the approved template'
