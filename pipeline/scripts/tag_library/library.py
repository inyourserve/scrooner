"""Library layer over first_pass.py output -> company_tag_map rows (Engineering's column names).

Decisions here are cross-company tag rules (Ritwik, 2026-11-11), applied per company with eras:
  TIERS:     concept -> ordered tags on a statement. The first tag printed in an era is the concept; a later tier whose
             era overlaps an earlier tier's era at that company is 'excluded' (alternate_tag_overlapping); a later tier
             in a non-overlapping era is the concept for its own era (tag switch, e.g. ASC 606).
  COMBINED:  a line that spans two concepts -> decision 'combined' (never the single concept; design §3 rule 3).
  NOT:       tags the old concept_mapping mapped wrongly -> excluded with the reason.
  SGA_PARTS: S&M and G&A printed without an SG&A total in that era -> 'component' of sga_expense (sign +1).
Every other first-pass decision passes through; 'concept' rows of different tags for one concept are de-overlapped by
the same era rule (rule priority, then tier order, then the more filings).
Usage: library.py <first_pass.csv> <rules_dir> <out.csv>
"""
import collections
import csv
import json
import sys
from pathlib import Path

src, rules_dir, out = sys.argv[1], sys.argv[2], sys.argv[3]

TIERS = {
    ("BS", "accounts_receivable"): ["AccountsReceivableNetCurrent", "ReceivablesNetCurrent", "AccountsNotesAndLoansReceivableNetCurrent"],
    ("BS", "accounts_payable"): ["AccountsPayableCurrent", "AccountsPayableTradeCurrent"],
    ("BS", "inventory"): ["InventoryNet"],
    ("BS", "goodwill"): ["Goodwill"],
    ("BS", "ppe_net_resolved"): ["PropertyPlantAndEquipmentNet"],
    ("IS", "sga_expense"): ["SellingGeneralAndAdministrativeExpense"],
    ("IS", "research_and_development"): ["ResearchAndDevelopmentExpense", "ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost"],
    ("IS", "operating_expenses_resolved"): ["OperatingExpenses"],
    ("IS", "interest_income"): ["InvestmentIncomeInterest"],
    ("IS", "other_income_expense_net"): ["NonoperatingIncomeExpense"],
    ("CF", "sbc"): ["ShareBasedCompensation", "AllocatedShareBasedCompensationExpense"],
    ("CF", "depreciation_and_amortization_resolved"): ["DepreciationDepletionAndAmortization", "DepreciationAndAmortization",
                                                        "DepreciationAmortizationAndAccretionNet"],
    ("CF", "amortization_of_intangibles"): ["AmortizationOfIntangibleAssets"],
    ("CF", "cf_ar_change"): ["IncreaseDecreaseInAccountsReceivable", "IncreaseDecreaseInReceivables"],
    ("CF", "cf_inventory_change"): ["IncreaseDecreaseInInventories"],
    ("CF", "cf_ap_change"): ["IncreaseDecreaseInAccountsPayable", "IncreaseDecreaseInAccountsPayableTrade"],
    ("CF", "cash_flow_investing_resolved"): ["NetCashProvidedByUsedInInvestingActivities", "NetCashProvidedByUsedInInvestingActivitiesContinuingOperations"],
    ("CF", "cash_flow_financing_resolved"): ["NetCashProvidedByUsedInFinancingActivities", "NetCashProvidedByUsedInFinancingActivitiesContinuingOperations"],
}
COMBINED = {
    ("BS", "AccountsPayableAndAccruedLiabilitiesCurrent"): ["accounts_payable", "accrued_liabilities"],
    ("BS", "AccountsPayableAndOtherAccruedLiabilitiesCurrent"): ["accounts_payable", "accrued_liabilities"],
    ("BS", "AccountsPayableAndAccruedLiabilitiesCurrentAndNoncurrent"): ["accounts_payable", "accrued_liabilities"],
    ("CF", "IncreaseDecreaseInAccountsPayableAndAccruedLiabilities"): ["cf_ap_change", "accrued_liabilities_change"],
    ("CF", "IncreaseDecreaseInAccountsPayableAndOtherOperatingLiabilities"): ["cf_ap_change", "other_operating_liabilities_change"],
    ("CF", "IncreaseDecreaseInAccountsReceivableAndOtherOperatingAssets"): ["cf_ar_change", "other_operating_assets_change"],
}
NOT = {
    ("IS", "CostsAndExpenses"): ("total_costs_incl_cost_of_revenue", "total costs and expenses includes cost of revenue: not operating_expenses (old concept_mapping was wrong)"),
    ("IS", "GeneralAndAdministrativeExpense"): None,  # decided by SGA_PARTS / tier below, never as sga alone
    ("IS", "InterestIncomeExpenseNet"): ("net_interest", "net interest income/expense (bank NII or net financing cost): not other_income_expense_net, not interest_income"),
    ("IS", "InterestIncomeExpenseNonoperatingNet"): ("net_interest", "net nonoperating interest: not other_income_expense_net"),
}
SGA_PARTS = ["SellingAndMarketingExpense", "GeneralAndAdministrativeExpense"]
# old concept_mapping errors found 2026-11-11 (ranks 1-50): founder "old was not reliable"
NOT.update({
    ("BS", "LiabilitiesAndStockholdersEquity"): ("liabilities_and_equity_total", "L&E total: equals total assets by identity but is not the assets line (old map called it total_assets)"),
    ("BS", "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents"): ("cash_incl_restricted", "includes restricted cash: not cash_and_equivalents"),
    ("BS", "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"): ("equity_incl_nci", "total equity incl. NCI: stockholders_equity is attributable to the parent"),
    ("IS", "NetIncomeLossAvailableToCommonStockholdersBasic"): ("ni_after_preferred", "net income after preferred dividends: not net_income"),
    ("IS", "InterestExpenseDebt"): ("debt_interest_component", "debt-only interest component (interest card); gross only under the sole-line rule"),
    ("IS", "InterestAndDividendIncomeOperating"): ("bank_interest_income", "bank interest and dividend income: not revenue (bank revenue is NII + noninterest income)"),
})
for t in ("NetIncomeLoss", "ProfitLoss", "NetIncomeLossAvailableToCommonStockholdersBasic"):
    NOT[("CI", t)] = ("ci_start_line", "net income as the CI start line; the concept lives on the IS")
NCI_TAGS = {"NetIncomeLossAttributableToNoncontrollingInterest", "MinorityInterestInNetIncomeLossOfConsolidatedEntities"}
CATALOG = set()

prio = {}
for p in Path(rules_dir).glob("*.jsonl"):
    if p.name.startswith("_"):
        continue
    for ln in p.read_text().splitlines():
        r = json.loads(ln)
        if r.get("tag"):
            prio[(r["stmt"], r["tag"].split(":")[-1])] = int(r.get("priority") or 50)
tier_of = {(st, t): (con, i) for (st, con), ts in TIERS.items() for i, t in enumerate(ts)}

CATALOG = {r["name"] for r in csv.DictReader(open(sys.argv[4]))} if len(sys.argv) > 4 else set()


def norm(c):
    return c + "_resolved" if c and not c.endswith("_resolved") and c + "_resolved" in CATALOG else c


rows = list(csv.DictReader(open(src)))
for r in rows:
    r["canonical_concept"] = norm(r["canonical_concept"])
by_co = collections.defaultdict(list)
for r in rows:
    by_co[r["company_id"]].append(r)


def overlap(a, b):
    return not (a["era_to"] < b["era_from"] or b["era_to"] < a["era_from"])


out_rows = []
for cid, rs in by_co.items():
    idx = {(r["stmt"], r["tag"]): r for r in rs}
    for r in rs:
        st, tag = r["stmt"], r["tag"]
        if r["taxonomy"] != "us-gaap":
            continue
        if (st, tag) in COMBINED:
            r.update(decision="combined", canonical_concept=COMBINED[(st, tag)][0], components=";".join(COMBINED[(st, tag)]),
                     reason_class="line_presented_combined_with_others", reason="one line spans " + " + ".join(COMBINED[(st, tag)]),
                     decided_by="library")
        elif NOT.get((st, tag)):
            rc, why = NOT[(st, tag)]
            r.update(decision="excluded", canonical_concept="", reason_class=rc, reason=why, decided_by="library")
        elif (st, tag) in tier_of:
            r.update(decision="concept", canonical_concept=tier_of[(st, tag)][0], reason_class="", reason="", decided_by="library")
    pl, nil = idx.get(("IS", "ProfitLoss")), idx.get(("IS", "NetIncomeLoss"))
    if pl and pl["taxonomy"] == "us-gaap":
        has_nci = any(("IS", t) in idx for t in NCI_TAGS)
        if (nil and overlap(pl, nil)) or has_nci:
            pl.update(decision="excluded", canonical_concept="", reason_class="ni_incl_nci",
                      reason="ProfitLoss includes NCI; net_income is attributable to the parent (NetIncomeLoss printed or an NCI line exists)", decided_by="library")
        else:
            pl.update(decision="concept", canonical_concept="net_income_resolved", reason_class="", reason="ProfitLoss as net income: no NetIncomeLoss in this era and no NCI line", decided_by="library")
    # SG&A parts: component of sga_expense in eras with no SG&A total
    sga = idx.get(("IS", "SellingGeneralAndAdministrativeExpense"))
    for t in SGA_PARTS:
        p = idx.get(("IS", t))
        if not p:
            continue
        if sga and overlap(p, sga):
            p.update(decision="excluded", canonical_concept="", reason_class="detail_of_printed_total",
                     reason="part of the printed SG&A total", decided_by="library")
        else:
            p.update(decision="component", canonical_concept="", parent_concept="sga_expense", combine_sign="1",
                     reason_class="", reason="S&M and G&A printed without an SG&A total: SG&A = their sum", decided_by="library")
    # de-overlap concept rows of one concept (per statement) by era
    groups = collections.defaultdict(list)
    for r in rs:
        if r.get("decision") == "concept" and r["canonical_concept"]:
            groups[(r["stmt"], r["canonical_concept"])].append(r)
    for (st, con), g in groups.items():
        g.sort(key=lambda r: (prio.get((st, r["tag"]), 50), tier_of.get((st, r["tag"]), (con, 9))[1], -int(r["filings"])))
        kept = []
        for r in g:
            clash = next((k for k in kept if overlap(r, k)), None)
            if clash:
                r.update(decision="excluded", canonical_concept="", reason_class="alternate_tag_overlapping",
                         reason=f"same concept {con} printed as {clash['tag']} in an overlapping era; that tag wins", decided_by=r["decided_by"] + "+deoverlap")
            else:
                kept.append(r)
    out_rows.extend(rs)

COLS = ["company_id", "cik", "taxonomy", "tag", "stmt", "decision", "canonical_concept", "parent_concept", "combine_sign",
        "components", "reason_class", "reason", "era_from", "era_to", "evidence_adsh", "evidence_report", "evidence_line",
        "evidence_plabel", "evidence_cal_parent", "decided_by", "rule_id", "rank", "ticker", "lines", "filings"]
with open(out, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=COLS, extrasaction="ignore")
    w.writeheader()
    for r in out_rows:
        if r.get("decision") == "" and r["decided_by"] in ("residue", "ask_expert"):
            r["decision"] = ""
        w.writerow({k: r.get(k, "") for k in COLS})
c = collections.Counter((r.get("decision") or "UNDECIDED") for r in out_rows)
print(dict(c))
print("concept rows by concept:", collections.Counter(r["canonical_concept"] for r in out_rows if r.get("decision") == "concept").most_common(40))
