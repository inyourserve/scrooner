"""Tag library rules (pipeline/scripts/tag_library/library.py), run the way the script runs: a CSV in, a CSV out."""

import csv
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LIB = ROOT / "pipeline" / "scripts" / "tag_library" / "library.py"
FIELDS = ["rank", "company_id", "cik", "ticker", "taxonomy", "stmt", "tag", "lines", "filings", "evidence_plabel",
          "evidence_adsh", "evidence_cal_parent", "era_from", "era_to", "decision", "canonical_concept", "reason_class",
          "reason", "decided_by", "filing_ids", "ibt_by_calc"]


def _run(tmp_path, rows, catalog=("net_income", "net_income_resolved", "sga_expense", "accounts_payable")):
    src, out, cat, rules = tmp_path / "in.csv", tmp_path / "out.csv", tmp_path / "cat.csv", tmp_path / "rules"
    rules.mkdir(exist_ok=True)
    with open(src, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow({**{k: "" for k in FIELDS}, "company_id": "1", "taxonomy": "us-gaap", "lines": "1", "filings": "1",
                        "era_from": "2015-01-31", "era_to": "2025-12-31", "decided_by": "residue", **r})
    with open(cat, "w", newline="") as fh:
        fh.write("name,statement,combination_mode\n" + "".join(f"{c},x,x\n" for c in catalog))
    subprocess.run([sys.executable, "-I", str(LIB), str(src), str(rules), str(out), str(cat)], check=True, capture_output=True)
    return {(r["stmt"], r["tag"]): r for r in csv.DictReader(open(out))}


def test_profitloss_is_net_income_only_without_netincomeloss_and_without_nci(tmp_path):
    got = _run(tmp_path, [{"stmt": "IS", "tag": "ProfitLoss"}])
    assert got[("IS", "ProfitLoss")]["decision"] == "concept"
    assert got[("IS", "ProfitLoss")]["canonical_concept"] == "net_income_resolved"
    got = _run(tmp_path, [{"stmt": "IS", "tag": "ProfitLoss"}, {"stmt": "IS", "tag": "NetIncomeLossAttributableToNoncontrollingInterest"}])
    assert got[("IS", "ProfitLoss")]["decision"] == "excluded"
    assert got[("IS", "ProfitLoss")]["reason_class"] == "ni_incl_nci"


def test_ap_and_accrued_is_combined_never_accounts_payable(tmp_path):
    got = _run(tmp_path, [{"stmt": "BS", "tag": "AccountsPayableAndAccruedLiabilitiesCurrent"}])
    r = got[("BS", "AccountsPayableAndAccruedLiabilitiesCurrent")]
    assert r["decision"] == "combined"
    assert r["reason_class"] == "line_presented_combined_with_others"
    assert r["canonical_concept"] == ""  # a combined line never feeds a single concept (design §3 rule 3)


def test_sga_parts_are_components_only_without_a_printed_sga_total(tmp_path):
    got = _run(tmp_path, [{"stmt": "IS", "tag": "SellingAndMarketingExpense"}, {"stmt": "IS", "tag": "GeneralAndAdministrativeExpense"}])
    assert {got[("IS", t)]["decision"] for t in ("SellingAndMarketingExpense", "GeneralAndAdministrativeExpense")} == {"component"}
    assert got[("IS", "GeneralAndAdministrativeExpense")]["parent_concept"] == "sga_expense"
    got = _run(tmp_path, [{"stmt": "IS", "tag": "SellingGeneralAndAdministrativeExpense"}, {"stmt": "IS", "tag": "GeneralAndAdministrativeExpense"}])
    assert got[("IS", "GeneralAndAdministrativeExpense")]["decision"] == "excluded"
    assert got[("IS", "SellingGeneralAndAdministrativeExpense")]["decision"] == "concept"


def test_old_map_errors_are_excluded(tmp_path):
    rows = [{"stmt": "BS", "tag": "LiabilitiesAndStockholdersEquity", "decision": "concept", "canonical_concept": "total_assets", "decided_by": "oldmap"},
            {"stmt": "IS", "tag": "CostsAndExpenses", "decision": "concept", "canonical_concept": "operating_expenses", "decided_by": "oldmap"}]
    got = _run(tmp_path, rows)
    assert got[("BS", "LiabilitiesAndStockholdersEquity")]["decision"] == "excluded"
    assert got[("IS", "CostsAndExpenses")]["decision"] == "excluded"


def test_alternate_tags_for_one_concept_never_overlap_in_era(tmp_path):
    rows = [{"stmt": "BS", "tag": "AccountsReceivableNetCurrent", "filings": "40"},
            {"stmt": "BS", "tag": "ReceivablesNetCurrent", "filings": "5", "era_from": "2020-01-31", "era_to": "2021-12-31"}]
    got = _run(tmp_path, rows, catalog=("accounts_receivable",))
    assert got[("BS", "AccountsReceivableNetCurrent")]["decision"] == "concept"
    assert got[("BS", "ReceivablesNetCurrent")]["reason_class"] == "alternate_tag_overlapping"
    rows[1].update(era_from="2026-01-31", era_to="2026-09-30")
    rows[0].update(era_to="2025-12-31")
    got = _run(tmp_path, rows, catalog=("accounts_receivable",))
    assert got[("BS", "ReceivablesNetCurrent")]["decision"] == "concept"  # a tag switch: its own era


def test_profitloss_is_decided_per_filing_not_per_company(tmp_path):
    # AVGO pattern: NetIncomeLoss and an NCI line until filing 3; from filing 4 only ProfitLoss is printed
    rows = [{"stmt": "IS", "tag": "NetIncomeLoss", "filing_ids": "1;2;3"},
            {"stmt": "IS", "tag": "NetIncomeLossAttributableToNoncontrollingInterest", "filing_ids": "2;3"},
            {"stmt": "IS", "tag": "ProfitLoss", "filing_ids": "2;3;4;5"}]
    got = _run(tmp_path, rows, catalog=("net_income_resolved",))
    assert got[("IS", "ProfitLoss")]["decision"] == "concept"
    assert "2 of 4 filings" in got[("IS", "ProfitLoss")]["reason"]


def test_income_before_tax_is_found_by_calc_position_not_by_label(tmp_path):
    rows = [{"stmt": "IS", "tag": "IncomeLossAttributableToParent", "evidence_plabel": "INCOME BEFORE INCOME TAXES", "ibt_by_calc": "8", "filing_ids": "1;2"}]
    got = _run(tmp_path, rows, catalog=("income_before_tax_resolved",))
    assert got[("IS", "IncomeLossAttributableToParent")]["canonical_concept"] == "income_before_tax_resolved"
    rows[0]["ibt_by_calc"] = "0"
    got = _run(tmp_path, rows, catalog=("income_before_tax_resolved",))
    assert got[("IS", "IncomeLossAttributableToParent")]["decision"] != "concept"  # a label alone never promotes


def test_a_component_label_is_never_promoted_in_its_own_filings(tmp_path):
    rows = [{"stmt": "IS", "tag": "Revenues", "filing_ids": "1;2", "evidence_plabel": "Total revenues"},
            {"stmt": "IS", "tag": "RevenueFromContractWithCustomerIncludingAssessedTax", "filing_ids": "2;3", "evidence_plabel": "Product sales"},
            {"stmt": "IS", "tag": "RevenueFromContractWithCustomerExcludingAssessedTax", "filing_ids": "2;4", "evidence_plabel": "Total revenues"}]
    got = _run(tmp_path, rows, catalog=("revenue_sanity_resolved",))
    assert got[("IS", "RevenueFromContractWithCustomerIncludingAssessedTax")]["decision"] == "excluded"
    assert got[("IS", "RevenueFromContractWithCustomerExcludingAssessedTax")]["decision"] == "concept"


def test_committed_ranks_1_50_map_leaves_no_core_point_without_source_or_reason():
    cov = ROOT / "pipeline" / "scripts" / "tag_library" / "coverage.py"
    csv_path = ROOT / "data-team" / "47-fsn-store" / "company_tag_map" / "ranks_1_50.csv"
    out = subprocess.run([sys.executable, "-I", str(cov), str(csv_path)], check=True, capture_output=True, text=True).stdout
    assert out.strip().splitlines()[-1] == "gaps 0", out
