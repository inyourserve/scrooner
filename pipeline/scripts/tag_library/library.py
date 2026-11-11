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
import re
import sys
from pathlib import Path

src, rules_dir, out = sys.argv[1], sys.argv[2], sys.argv[3]

TIERS = {
    ("BS", "accounts_receivable"): ["AccountsReceivableNetCurrent", "ReceivablesNetCurrent", "AccountsNotesAndLoansReceivableNetCurrent"],
    ("BS", "accounts_payable"): ["AccountsPayableCurrent", "AccountsPayableTradeCurrent"],
    ("BS", "inventory"): ["InventoryNet"],
    ("IS", "revenue_sanity_resolved"): ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax", "RevenueFromContractWithCustomerIncludingAssessedTax",
                                         "RevenuesNetOfInterestExpense", "SalesAndOtherOperatingRevenueIncludingSalesBasedTaxes", "SalesRevenueNet"],
    ("IS", "income_before_tax_resolved"): ["IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",
                                            "IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments",
                                            "IncomeLossFromContinuingOperationsBeforeIncomeTaxes"],
    ("CF", "capex_resolved"): ["PaymentsToAcquirePropertyPlantAndEquipment", "PaymentsToAcquireProductiveAssets"],
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
OVERRIDES = {  # (ticker, stmt, custom tag) -> (concept, evidence)
    ("GE", "BS", "CashAndEquivalentsExcludingAssetsHeldForSale"): ("cash_and_equivalents_resolved", "GE face line 'Cash and equivalents' 2015-2017 (custom tag; held-for-sale cash shown apart)"),
    ("XOM", "IS", "SalesAndOtherOperatingRevenueIncludingSalesBasedTaxes"): ("revenue_sanity_resolved", "XOM face top line 'Sales and other operating revenue' 2015-2018 (custom tag); 'Total revenues and other income' adds other income"),
    ("TSLA", "IS", "RevenueFromContractWithCustomerExcludingAssessedTax"): ("revenue_sanity_resolved", "TSLA face line 'Total revenues' after 2023-06 when Revenues is no longer printed (before: a child of Revenues, leasing added on top)"),
    ("CVX", "BS", "CashAndCashEquivalentsExcludingTimeDeposits"): ("cash_and_equivalents_resolved", "CVX face line 'Cash and cash equivalents' from 2024-09 (custom tag; time deposits shown apart)"),
    ("CVX", "BS", "CashandCashEquivalentsExcludingTimeDepositsatCarryingValue"): ("cash_and_equivalents_resolved", "CVX face line 'Cash and cash equivalents' 2019-12..2022-03 (custom tag)"),
}
NOT_CO = {
    ("CAT", "BS", "CashCashEquivalentsAndShortTermInvestments"): ("cash_incl_short_term_investments", "CAT pre-2021 face line 'Cash and short-term investments': not cash_and_equivalents (blank with reason)"),
}
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
NOT[("IS", "ProfitLoss")] = ("ni_incl_nci", "ProfitLoss includes NCI unless no NCI line exists (fallback below)")
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


def cid_is_bank(rs):
    tags = {r["tag"] for r in rs}
    return bool({"InterestAndDividendIncomeOperating", "NoninterestIncome", "Deposits", "ProvisionForLoanLeaseAndOtherLosses"} & tags) and "NoninterestExpense" in tags


def shares_filing(a, b):
    fa, fb = a.get("filing_ids"), b.get("filing_ids")
    if not fa or not fb:
        return overlap(a, b)
    return bool(set(fa.split(";")) & set(fb.split(";")))


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
            r.update(decision="combined", canonical_concept="", components=";".join(COMBINED[(st, tag)]),
                     reason_class="line_presented_combined_with_others", reason="one line spans " + " + ".join(COMBINED[(st, tag)]),
                     decided_by="library")
        elif NOT.get((st, tag)):
            rc, why = NOT[(st, tag)]
            r.update(decision="excluded", canonical_concept="", reason_class=rc, reason=why, decided_by="library")
        elif (st, tag) in tier_of:
            r.update(decision="concept", canonical_concept=tier_of[(st, tag)][0], reason_class="", reason="", decided_by="library")
    for r in rs:
        k = (r["ticker"], r["stmt"], r["tag"])
        if k in OVERRIDES:
            r.update(decision="concept", canonical_concept=OVERRIDES[k][0], reason_class="", reason=OVERRIDES[k][1], decided_by="company_override")
        elif k in NOT_CO:
            r.update(decision="excluded", canonical_concept="", reason_class=NOT_CO[k][0], reason=NOT_CO[k][1], decided_by="company_override")
    # sole-source fallbacks (Dhairya 2026-11-11): an exclusion may never leave a template point without a source
    def fids(r):
        ids = set((r.get("filing_ids") or "").split(";")) - {""}
        return ids or {"ALL"}  # no filing list (legacy rows): the tag is printed in every filing

    def fallback(alt_key, primary_tags, blockers, concept, why_ok, rc_no, why_no):
        """per filing: alt is the concept in filings with no primary line and no blocker line"""
        alt = idx.get(alt_key)
        if not alt or alt["taxonomy"] != "us-gaap":
            return
        taken = set().union(*[fids(idx[k]) for k in primary_tags if k in idx and idx[k].get("decision") == "concept"]) if primary_tags else set()
        blocked = set().union(*[fids(idx[k]) for k in blockers if k in idx]) if blockers else set()
        own = fids(alt) - taken - blocked
        if own:
            alt.update(decision="concept", canonical_concept=concept, reason_class="",
                       reason=f"{why_ok} (in {len(own)} of {len(fids(alt))} filings; elsewhere the primary line or a blocker is printed)", decided_by="library")
        elif fids(alt) & blocked - taken and rc_no:
            alt.update(decision="excluded", canonical_concept="", reason_class=rc_no, reason=why_no, decided_by="library")
    fallback(("BS", "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"), [("BS", "StockholdersEquity")],
             [("BS", "MinorityInterest")], "stockholders_equity_resolved",
             "total equity is the only equity line and the company prints no NCI: equals parent equity",
             "parent_equity_not_printed", "parent-only equity not printed; total incl. NCI printed and NCI exists (blank with reason)")
    fallback(("BS", "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents"), [("BS", "CashAndCashEquivalentsAtCarryingValue"), ("BS", "Cash")],
             [], "cash_and_equivalents_resolved", "the face prints cash only together with restricted cash: that line is the cash source", "", "")
    # NI available to common = net income where no NetIncomeLoss is printed and no preferred dividends exist (CAT)
    fallback(("IS", "ProfitLoss"), [("IS", "NetIncomeLoss")], [("IS", t) for t in NCI_TAGS], "net_income_resolved",
             "ProfitLoss as net income: no NetIncomeLoss and no NCI line in these filings",
             "ni_incl_nci", "ProfitLoss includes NCI; net_income is attributable to the parent")
    fallback(("IS", "NetIncomeLossAvailableToCommonStockholdersBasic"), [("IS", "NetIncomeLoss"), ("IS", "ProfitLoss")],
             [("IS", "PreferredStockDividendsIncomeStatementImpact"), ("IS", "DividendsPreferredStock"), ("EQ", "DividendsPreferredStock")],
             "net_income_resolved", "printed as NI available to common with no NetIncomeLoss and no preferred dividends: equals net income",
             "ni_after_preferred", "net income after preferred dividends: not net_income")
    # CostOfRevenue labelled as total costs and expenses (BA, LMT trap): never cost of revenue
    cor = idx.get(("IS", "CostOfRevenue"))
    if cor and "total cost" in (cor.get("evidence_plabel") or "").lower():
        cor.update(decision="excluded", canonical_concept="", reason_class="total_costs_incl_cost_of_revenue",
                   reason="CostOfRevenue tag on a 'total costs and expenses' line: the cost-of-sales line wins", decided_by="library")
    r = idx.get(("BS", "CashAndDueFromBanks"))
    if r and r.get("decision") != "concept":
        plain = set().union(*[fids(idx[("BS", t)]) for t in ("CashAndCashEquivalentsAtCarryingValue", "Cash") if ("BS", t) in idx]) if any(("BS", t) in idx for t in ("CashAndCashEquivalentsAtCarryingValue", "Cash")) else set()
        if fids(r) - plain:
            r.update(decision="excluded", canonical_concept="", reason_class="bank_cash_perimeter",
                     reason="cash and due from banks is the only cash line in these filings: bank/broker cash perimeter pending", decided_by="library")
    if cid_is_bank(rs):
        r = None
        if r and not any(("BS", t) in idx for t in ("CashAndCashEquivalentsAtCarryingValue", "Cash")):
            r.update(decision="excluded", canonical_concept="", reason_class="bank_cash_perimeter",
                     reason="bank cash and due from banks (+ deposits with banks): bank-template cash perimeter pending", decided_by="library")
        for t in ("InterestIncomeExpenseNet", "InterestAndDividendIncomeOperating"):
            r = idx.get(("IS", t))
            if r:
                r.update(decision="excluded", canonical_concept="", reason_class="catalog_gap_bank_nii",
                         reason="bank NII / interest income is a bank-template headline; catalog has no net_interest_income concept yet (Engineering)", decided_by="library")
    # income before tax by calc position (+1 beside the income-tax line under one parent): structure, not label
    ibt_rows = [r for r in rs if r["stmt"] == "IS" and r.get("decision") == "concept" and r["canonical_concept"] == "income_before_tax_resolved"]
    for r in rs:
        if r["stmt"] == "IS" and int(r.get("ibt_by_calc") or 0) > 0 and r.get("decision") != "concept" and r["tag"] != "ProfitLoss":
            if not any(shares_filing(r, k) for k in ibt_rows):
                r.update(decision="concept", canonical_concept="income_before_tax_resolved", reason_class="",
                         reason=f"calc position: +1 beside the income-tax line (-1) in {r['ibt_by_calc']} filing(s); the tag name is the filer's choice",
                         decided_by="calc_position")
                ibt_rows.append(r)
    e = idx.get(("IS", "EarningsPerShareBasicAndDiluted"))
    if e and e.get("decision") != "concept":
        e.update(decision="concept", canonical_concept="basic_eps_resolved", reason_class="",
                 reason="one printed EPS line serves basic AND diluted (mapper: feed diluted_eps from this row too)", decided_by="library")
    # SG&A parts: component of sga_expense in eras with no SG&A total
    sga = idx.get(("IS", "SellingGeneralAndAdministrativeExpense"))
    for t in SGA_PARTS:
        p = idx.get(("IS", t))
        if not p:
            continue
        if sga and shares_filing(p, sga):
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
        g.sort(key=lambda r: 0 if any(r["tag"] in (o.get("evidence_cal_parent") or "").split(";") for o in g if o is not r) else 1)
        kept = []
        for r in g:
            clash = next((k for k in kept if shares_filing(r, k)), None)
            child = clash is not None and clash["tag"] in (r.get("evidence_cal_parent") or "").split(";")
            own = set((r.get("filing_ids") or "").split(";")) - set().union(*[set((k.get("filing_ids") or "").split(";")) for k in kept])
            component_label = re.search(r"(?i)\b(product|service|automotive|leasing|other|segment)\b", r.get("evidence_plabel") or "")
            if clash and own - {""} and (r["decided_by"] == "company_override" or not component_label):
                r.update(reason=f"concept only in filings where {clash['tag']} is not printed ({len(own)} filing(s))")
                kept.append(r)
                continue
            if clash:
                r.update(decision="excluded", canonical_concept="", reason_class="alternate_tag_overlapping",
                         reason=f"same concept {con} printed as {clash['tag']} in the same filing(s); that tag wins", decided_by=r["decided_by"] + "+deoverlap")
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
