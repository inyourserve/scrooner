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
            {"stmt": "BS", "tag": "ReceivablesNetCurrent", "filings": "5", "era_from": "2020-01-31", "era_to": "2021-12-31",
             "evidence_plabel": "Accounts receivable, net"}]
    got = _run(tmp_path, rows, catalog=("accounts_receivable",))
    assert got[("BS", "AccountsReceivableNetCurrent")]["decision"] == "concept"
    assert got[("BS", "ReceivablesNetCurrent")]["reason_class"] == "alternate_tag_overlapping"
    rows[1].update(era_from="2026-01-31", era_to="2026-09-30")
    rows[0].update(era_to="2025-12-31")
    got = _run(tmp_path, rows, catalog=("accounts_receivable",))
    assert got[("BS", "ReceivablesNetCurrent")]["decision"] == "concept"  # a tag switch: its own era


def test_profitloss_is_net_income_only_outside_the_netincomeloss_and_nci_eras_and_the_cut_era_keeps_a_reason(tmp_path):
    # AVGO pattern: NetIncomeLoss to 2019-07, an NCI line to 2020-10, ProfitLoss 2016..2026
    rows = [{"stmt": "IS", "tag": "NetIncomeLoss", "era_from": "2015-01-31", "era_to": "2019-07-31", "filing_ids": "1;2",
             "decision": "concept", "canonical_concept": "net_income_resolved", "decided_by": "rule"},
            {"stmt": "IS", "tag": "NetIncomeLossAttributableToNoncontrollingInterest", "era_from": "2016-04-30", "era_to": "2020-10-31", "filing_ids": "2;3"},
            {"stmt": "IS", "tag": "ProfitLoss", "era_from": "2016-04-30", "era_to": "2026-07-31", "filing_ids": "2;3;4"}]
    out = tmp_path / "x"
    out.mkdir()
    _run(out, rows, catalog=("net_income_resolved",))
    pls = [r for r in csv.DictReader(open(out / "out.csv")) if r["tag"] == "ProfitLoss"]
    pl = [r for r in pls if r["decision"] == "concept"]
    assert pl and pl[0]["era_from"] == "2020-11-01" and pl[0]["era_to"] == "2026-07-31"
    cut = [r for r in pls if r["decision"] == "excluded"]
    # ruling (3): 2019-08..2020-10 is ProfitLoss - NCI (a component sum); only the NetIncomeLoss era keeps the reason row
    assert cut and cut[0]["reason_class"] == "ni_incl_nci" and cut[0]["era_to"] == "2019-07-31"


def test_income_before_tax_is_found_by_calc_position_not_by_label(tmp_path):
    rows = [{"stmt": "IS", "tag": "IncomeLossAttributableToParent", "evidence_plabel": "INCOME BEFORE INCOME TAXES", "ibt_by_calc": "8", "filing_ids": "1;2"}]
    got = _run(tmp_path, rows, catalog=("income_before_tax_resolved",))
    assert got[("IS", "IncomeLossAttributableToParent")]["canonical_concept"] == "income_before_tax_resolved"
    rows[0]["ibt_by_calc"] = "0"
    got = _run(tmp_path, rows, catalog=("income_before_tax_resolved",))
    assert got[("IS", "IncomeLossAttributableToParent")]["decision"] != "concept"  # a label alone never promotes


def test_a_losing_tag_keeps_the_concept_only_outside_the_winners_era_and_never_a_component_label(tmp_path):
    rows = [{"stmt": "IS", "tag": "Revenues", "filing_ids": "1;2", "era_from": "2015-03-31", "era_to": "2021-06-30", "evidence_plabel": "Total revenues"},
            {"stmt": "IS", "tag": "RevenueFromContractWithCustomerIncludingAssessedTax", "filing_ids": "2", "era_from": "2018-06-30", "era_to": "2021-06-30", "evidence_plabel": "Product sales"},
            {"stmt": "IS", "tag": "RevenueFromContractWithCustomerExcludingAssessedTax", "filing_ids": "2;4", "era_from": "2020-12-31", "era_to": "2026-06-30", "evidence_plabel": "Total revenues"}]
    got = _run(tmp_path, rows, catalog=("revenue_sanity_resolved",))
    assert got[("IS", "RevenueFromContractWithCustomerIncludingAssessedTax")]["decision"] == "excluded"
    ex = got[("IS", "RevenueFromContractWithCustomerExcludingAssessedTax")]
    assert ex["decision"] == "concept" and ex["era_from"] == "2021-07-01"  # never the shared era: no two concept tags per period


def test_committed_ranks_1_50_map_covers_the_full_sector_template():
    cov = ROOT / "pipeline" / "scripts" / "tag_library" / "coverage_full.py"
    d = ROOT / "data-team" / "47-fsn-store" / "company_tag_map"
    with __import__("tempfile").TemporaryDirectory() as t:
        out = subprocess.run([sys.executable, "-I", str(cov), str(d / "ranks_1_50.csv"), str(d / "template_points_ranks_1_50.csv"),
                              str(d / "concepts_catalog.csv"), str(d / "note_sourced_candidates_ranks_1_50.csv"),
                              str(d / "template_out_candidates_ranks_1_50.csv"), t + "/cov.csv"], check=True, capture_output=True, text=True).stdout
    assert out.strip().splitlines()[-1] == "gaps 0", out


def test_committed_ranks_1_50_map_leaves_no_core_point_without_source_or_reason():
    cov = ROOT / "pipeline" / "scripts" / "tag_library" / "coverage.py"
    csv_path = ROOT / "data-team" / "47-fsn-store" / "company_tag_map" / "ranks_1_50.csv"
    out = subprocess.run([sys.executable, "-I", str(cov), str(csv_path)], check=True, capture_output=True, text=True).stdout
    assert out.strip().splitlines()[-1] == "gaps 0", out


def test_committed_ranks_1_50_map_has_a_decision_and_a_reason_for_every_row():
    csv_path = ROOT / "data-team" / "47-fsn-store" / "company_tag_map" / "ranks_1_50.csv"
    rows = list(csv.DictReader(open(csv_path)))
    assert rows
    assert not [r for r in rows if r["decision"] not in ("concept", "component", "combined", "excluded")]
    assert not [r for r in rows if r["decision"] == "excluded" and not (r["reason_class"] and r["reason"])]
    assert not [r for r in rows if r["decision"] == "combined" and r["canonical_concept"]]


def test_ni_is_profitloss_minus_nci_only_after_netincomeloss_stops_and_while_the_nci_line_is_printed(tmp_path):
    # ruling (3) 2026-11-11, AVGO pattern
    rows = [{"stmt": "IS", "tag": "NetIncomeLoss", "era_from": "2015-01-31", "era_to": "2019-07-31", "filing_ids": "1;2",
             "decision": "concept", "canonical_concept": "net_income_resolved", "decided_by": "rule"},
            {"stmt": "IS", "tag": "NetIncomeLossAttributableToNoncontrollingInterest", "era_from": "2016-04-30", "era_to": "2020-10-31", "filing_ids": "2;3"},
            {"stmt": "IS", "tag": "ProfitLoss", "era_from": "2016-04-30", "era_to": "2026-07-31", "filing_ids": "2;3;4"}]
    out = tmp_path / "y"
    out.mkdir()
    _run(out, rows, catalog=("net_income_resolved",))
    comp = sorted((r["tag"], r["combine_sign"], r["era_from"], r["era_to"]) for r in csv.DictReader(open(out / "out.csv"))
                  if r["parent_concept"] == "net_income_resolved")
    assert comp == [("NetIncomeLossAttributableToNoncontrollingInterest", "-1", "2019-08-01", "2020-10-31"),
                    ("ProfitLoss", "1", "2019-08-01", "2020-10-31")]


def test_receivables_net_current_under_a_non_plain_label_is_combined(tmp_path):
    got = _run(tmp_path, [{"stmt": "BS", "tag": "ReceivablesNetCurrent", "evidence_plabel": "Notes and accounts receivable, net"}],
               catalog=("accounts_receivable",))
    assert got[("BS", "ReceivablesNetCurrent")]["decision"] == "combined"


def test_committed_map_has_no_two_concept_rows_overlapping_for_one_company_statement_and_concept():
    # the 0122 trigger's rule, checked on the committed seed: one tag per (company, stmt, concept) per period
    import collections
    rows = [r for r in csv.DictReader(open(ROOT / "data-team" / "47-fsn-store" / "company_tag_map" / "ranks_1_50.csv"))
            if r["decision"] == "concept"]
    g = collections.defaultdict(list)
    for r in rows:
        g[(r["company_id"], r["stmt"], r["canonical_concept"])].append((r["era_from"], r["era_to"], r["tag"]))
    clashes = [(k, a, b) for k, v in g.items() for a, b in zip(sorted(v), sorted(v)[1:]) if b[0] <= a[1]]
    assert not clashes, clashes[:5]
