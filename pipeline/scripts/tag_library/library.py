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
    ("CF", "cash_paid_for_interest"): ["InterestPaidNet", "InterestPaid"],
    ("CF", "cash_paid_for_income_taxes"): ["IncomeTaxesPaidNet", "IncomeTaxesPaid"],
    ("IS", "weighted_basic_shares"): ["WeightedAverageNumberOfSharesOutstandingBasic", "WeightedAverageNumberOfShareOutstandingBasicAndDiluted"],
    ("IS", "weighted_diluted_shares"): ["WeightedAverageNumberOfDilutedSharesOutstanding"],
    ("IS", "basic_eps_resolved"): ["EarningsPerShareBasic", "IncomeLossFromContinuingOperationsPerBasicShare"],
    ("IS", "diluted_eps_resolved"): ["EarningsPerShareDiluted", "IncomeLossFromContinuingOperationsPerDilutedShare"],
    ("IS", "revenue_sanity_resolved"): ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax", "RevenueFromContractWithCustomerIncludingAssessedTax",
                                         "RevenuesNetOfInterestExpense", "SalesAndOtherOperatingRevenueIncludingSalesBasedTaxes", "SalesRevenueNet"],
    ("IS", "income_before_tax_resolved"): ["IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",
                                            "IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments",
                                            "IncomeLossFromContinuingOperationsBeforeIncomeTaxes",
                                            "IncomeLossIncludingPortionAttributableToNoncontrollingInterest"],  # '...before Tax' (PG, MCK, PSX)
    ("CF", "capex_resolved"): ["PaymentsToAcquirePropertyPlantAndEquipment", "PaymentsToAcquireProductiveAssets"],
    ("BS", "goodwill"): ["Goodwill"],
    ("BS", "ppe_net_resolved"): ["PropertyPlantAndEquipmentNet", "PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization"],
    ("BS", "shares_outstanding_resolved"): ["CommonStockSharesOutstanding"],
    ("IS", "sga_expense"): ["SellingGeneralAndAdministrativeExpense"],
    ("IS", "research_and_development"): ["ResearchAndDevelopmentExpense", "ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost"],
    ("IS", "operating_expenses_resolved"): ["OperatingExpenses"],
    ("IS", "interest_income"): ["InvestmentIncomeInterest", "InvestmentIncomeInterestAndDividend"],
    ("IS", "other_income_expense_net"): ["OtherNonoperatingIncomeExpense", "NonoperatingIncomeExpense"],
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
    ("AVGO", "IS", "CommonStockDividendsDeclaredandPaidperShare"): ("dividends_per_share_resolved", "AVGO IS line 'Cash dividends declared and paid per share' (custom tag)"),
    ("CVX", "BS", "CashAndCashEquivalentsExcludingTimeDeposits"): ("cash_and_equivalents_resolved", "CVX face line 'Cash and cash equivalents' from 2024-09 (custom tag; time deposits shown apart)"),
    ("CVX", "BS", "CashandCashEquivalentsExcludingTimeDepositsatCarryingValue"): ("cash_and_equivalents_resolved", "CVX face line 'Cash and cash equivalents' 2019-12..2022-03 (custom tag)"),
}
COMBINED_CO = {  # (ticker, stmt, custom tag) -> (spanned concepts, evidence)
    ("MSFT", "CF", "DepreciationAmortizationAndOther"): (["depreciation_and_amortization", "other_noncash"], "MSFT CF line 'Depreciation, amortization, and other' (custom tag): D&A plus other non-cash items"),
}
NOT_CO = {
    ("ORCL", "IS", "CostOfServices"): ("component_of_unprinted_total", "ORCL 'Services' is one cost line beside cloud/license, hardware and other costs; no cost-of-revenue total is printed (template-OUT candidate)"),
    ("UNH", "IS", "SellingGeneralAndAdministrativeExpense"): ("not_sga_broad_operating_costs", "UNH 'Operating costs' is broad operating cost, not SG&A (income-statement card)"),
    ("UNH", "IS", "CostOfGoodsSold"): ("cost_of_products_not_total_cor", "UNH 'Cost of products sold' is one cost line beside medical costs, not total cost of revenue"),
    ("UNH", "IS", "CostOfGoodsAndServicesSold"): ("cost_of_products_not_total_cor", "UNH 'Cost of products sold' is one cost line beside medical costs, not total cost of revenue"),
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

RESIDUE = [  # applied last, to rows nothing above decided: (stmt set or None, regex on tag, reason_class, reason)
    (None, r"(?i)percent", "ratio_line", "a percent-of-sales or ratio line, not an amount"),
    ({"CF"}, r"^(InterestPaid|IncomeTaxesPaid|ProceedsFromIncomeTaxRefunds)", "pending_catalog_concept",
     "cash paid for interest / income taxes: catalog concept arrives with 0122, then re-decided as a concept row"),
    ({"IS"}, r"^(NetIncomeLossAvailableToCommonStockholdersDiluted|UndistributedEarnings|DistributedEarnings|ParticipatingSecurities|IncomeLossFromContinuingOperationsPerDilutedShare)",
     "eps_numerator", "EPS numerator or allocation to participating securities; EPS itself is mapped"),
    ({"BS"}, r"^CommitmentsAndContingencies$", "caption_no_value", "commitments and contingencies caption: carries no amount on the face"),
    ({"BS"}, r"(Accumulated|Allowance|Reserve)", "contra_parenthetical", "allowance, reserve or accumulated depreciation/amortization; the net line carries the concept"),
    ({"BS"}, r"(FairValue|Pledged|AmortizedCost|VariableInterestEntit|Collateral)", "fair_value_or_pledged_detail", "fair value, pledged-collateral or VIE detail printed with the BS"),
    ({"BS"}, r"(TemporaryEquity|Redeemable)", "temporary_equity", "temporary/mezzanine equity; not stockholders_equity, no catalog concept"),
    ({"BS"}, r"^InventoryNoncurrent$", "inventory_noncurrent", "inventory classified in other assets; the inventory concept is the current line"),
    ({"BS", "EQ"}, r"Shares?$|SharesHeld|InShares", "share_terms_parenthetical", "share count, not an amount"),
    ({"CF"}, r"(Discontinued|DisposalGroup)", "discontinued_operations", "discontinued-operations cash flow; the totals carry the concepts"),
    ({"CF"}, r"^(LiabilitiesAssumed|DividendsPayable|Noncash|OtherSignificantNoncash|StockIssued|TransferOf|NonCash)", "noncash_supplemental", "non-cash supplemental disclosure; never a cash flow"),
    ({"EQ"}, r"", "equity_statement_line", "equity statement balance or movement; no catalog concept (DPS handled above)"),
    ({"CI"}, r"", "oci_component", "comprehensive income detail; the CI total is mapped"),
]
RESIDUE = [(st, re.compile(rx), rc, why) for st, rx, rc, why in RESIDUE]
ASK_DEFAULT = {  # Tag Expert questions: a decision now, re-decided on the ruling
    "CommonStockSharesIssued": ("share_terms_parenthetical", "BS issued-share count, not outstanding (Tag Expert ruling (a) 2026-11-11)"),
}
FLAG = {  # Tag Expert rulings 2026-11-11 (docs/tag-expert-playbooks 08ab3ed7): visible flags carried in the reason
    ("BS", "ReceivablesNetCurrent"): "plain 'accounts receivable, net' label only (Tag Expert correction (d))",
    ("BS", "PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization"): "flag includes_finance_lease_rou",
    ("BS", "CommonStockSharesOutstanding"): "period-end parenthetical only; never the EQ column or the dei cover count; several classes: per class, NEVER summed (an instant is never derived; Tag Expert correction 2026-11-11)",
}

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


def day_after(d):
    import datetime
    return (datetime.date.fromisoformat(d) + datetime.timedelta(days=1)).isoformat()


def day_before(d):
    import datetime
    return (datetime.date.fromisoformat(d) - datetime.timedelta(days=1)).isoformat()


def era_outside(loser, winners):
    """the part of loser's era outside every winner's era: (from, to) or None. Never a partial-filing row: the mapper
    picks per period across a concept's tags, so two concept tags must never cover the same period."""
    if not winners:
        return loser["era_from"], loser["era_to"]
    lo = min(w["era_from"] for w in winners)
    hi = max(w["era_to"] for w in winners)
    if loser["era_to"] > hi:
        return max(loser["era_from"], day_after(hi)), loser["era_to"]  # never widen an era already narrowed
    if loser["era_from"] < lo:
        return loser["era_from"], min(loser["era_to"], day_before(lo))
    return None


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
            r.update(decision="concept", canonical_concept=tier_of[(st, tag)][0], reason_class="", reason=FLAG.get((st, tag), ""), decided_by="library")
    for r in rs:
        k = (r["ticker"], r["stmt"], r["tag"])
        if k in OVERRIDES:
            r.update(decision="concept", canonical_concept=OVERRIDES[k][0], reason_class="", reason=OVERRIDES[k][1], decided_by="company_override")
        elif k in NOT_CO:
            r.update(decision="excluded", canonical_concept="", reason_class=NOT_CO[k][0], reason=NOT_CO[k][1], decided_by="company_override")
    for r in rs:
        k = (r["ticker"], r["stmt"], r["tag"])
        if k in COMBINED_CO:
            r.update(decision="combined", canonical_concept="", components=";".join(COMBINED_CO[k][0]),
                     reason_class="line_presented_combined_with_others", reason=COMBINED_CO[k][1], decided_by="company_override")
    # sole-source fallbacks (Dhairya 2026-11-11): an exclusion may never leave a template point without a source
    def fids(r):
        ids = set((r.get("filing_ids") or "").split(";")) - {""}
        return ids or {"ALL"}  # no filing list (legacy rows): the tag is printed in every filing

    pending_extra = []

    def fallback(alt_key, primary_tags, blockers, concept, why_ok, rc_no, why_no):
        """alt is the concept only for the era outside every primary concept line and every blocker line"""
        alt = idx.get(alt_key)
        if not alt or alt["taxonomy"] != "us-gaap":
            return
        win = [idx[k] for k in primary_tags if k in idx and idx[k].get("decision") == "concept" and idx[k] is not alt]
        win += [idx[k] for k in blockers if k in idx]
        part = era_outside(alt, win)
        if part and rc_no and (part[0] > alt["era_from"] or part[1] < alt["era_to"]):
            cut = dict(alt)  # the cut-out era keeps its reason, so the gap is explained, never silent
            cut.update(decision="excluded", canonical_concept="", reason_class=rc_no, reason=why_no + " (era cut out of the concept row)",
                       era_from=alt["era_from"] if part[0] > alt["era_from"] else day_after(part[1]),
                       era_to=day_before(part[0]) if part[0] > alt["era_from"] else alt["era_to"], decided_by="library")
            pending_extra.append(cut)
        if part:
            alt.update(decision="concept", canonical_concept=concept, reason_class="", era_from=part[0], era_to=part[1],
                       reason=f"{why_ok} (era {part[0]}..{part[1]}; outside the primary/blocker lines)", decided_by="library")
        elif rc_no:
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
    if cor and re.search(r"(?i)costs? and expenses", cor.get("evidence_plabel") or ""):
        cor.update(decision="excluded", canonical_concept="", reason_class="total_costs_incl_cost_of_revenue",
                   reason="CostOfRevenue tag on a 'total costs and expenses' line: the cost-of-sales line wins", decided_by="library")
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
    non = idx.get(("IS", "NonoperatingIncomeExpense"))
    if non and non.get("decision") == "concept":
        under = [r for r in rs if r["stmt"] == "IS" and "NonoperatingIncomeExpense" in (r.get("evidence_cal_parent") or "").split(";") and re.search(r"Interest", r["tag"])]
        if under:
            non.update(decision="excluded", canonical_concept="", reason_class="nonoperating_total_incl_interest",
                       reason="NonoperatingIncomeExpense has interest lines under it: the total incl. interest, not other_income_expense_net (Tag Expert (f))", decided_by="library")
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
            if clash:
                same = [k for k in kept if shares_filing(r, k)]
                part = era_outside(r, same)
                comp = re.search(r"(?i)\b(product|service|automotive|leasing|other|segment)\b", r.get("evidence_plabel") or "")
                if part and (r["decided_by"] == "company_override" or not comp):
                    r.update(era_from=part[0], era_to=part[1], reason=(r.get("reason") or "") + f" [era limited to {part[0]}..{part[1]}: outside {', '.join(k['tag'] for k in same)}]")
                    kept.append(r)
                    continue
            if clash:
                r.update(decision="excluded", canonical_concept="", reason_class="alternate_tag_overlapping",
                         reason=f"same concept {con} printed as {clash['tag']} in the same filing(s); that tag wins", decided_by=r["decided_by"] + "+deoverlap")
            else:
                kept.append(r)
    for r in rs:
        if r.get("decision"):
            continue
        if r["tag"] in ASK_DEFAULT:
            rc, why = ASK_DEFAULT[r["tag"]]
            r.update(decision="excluded", reason_class=rc, reason=why, decided_by="ask_default")
            continue
        if r["decided_by"] == "ask_expert":
            r.update(decision="excluded", reason_class="pending_catalog_concept", reason=r["reason"], decided_by="ask_default")
            continue
        for sts, rx, rc, why in RESIDUE:
            if (sts is None or r["stmt"] in sts) and rx.search(r["tag"]):
                r.update(decision="excluded", reason_class=rc, reason=why, decided_by="residue_rule")
                break
        else:
            r.update(decision="excluded", reason_class="not_in_any_mapped_calc_path",
                     reason="no calc path into a mapped total in this company's filings, and no catalog match by tag, statement or position",
                     decided_by="residue_rule")
    for r in rs:
        if r["stmt"] == "UN" and r.get("decision") == "excluded" and r.get("reason_class") == "cover_or_parenthetical":
            r.update(reason_class="co_registrant_statement", reason="FSN stmt UN: excluded because the company's own IS/BS/CF cover these points; a co-registrant statement where the column carries a LegalEntityAxis member (D4; Revvity/PLNT are UN and the real entity)")
    # D3: where IS and CF both print D&A in one filing, the CF line wins
    cf_da = [r for r in rs if r["stmt"] == "CF" and r.get("decision") == "concept" and r["canonical_concept"] == "depreciation_and_amortization_resolved"]
    for r in rs:
        if r["stmt"] == "IS" and r.get("decision") == "concept" and r["canonical_concept"] == "depreciation_and_amortization_resolved" and any(shares_filing(r, k) for k in cf_da):
            r.update(decision="excluded", canonical_concept="", reason_class="alternate_tag_overlapping", reason="D&A printed on both IS and CF in these filings: the CF line wins (cash-flow card D3)", decided_by="library")
    # D1/D2: label wording widens the line beyond the concept -> combined (labels only demote)
    for r in rs:
        lab = r.get("evidence_plabel") or ""
        if r.get("decision") == "concept" and r["canonical_concept"] == "share_buybacks_resolved" and re.search(r"(?i)excise|withh?olding", lab):
            r.update(decision="combined", canonical_concept="", components="share_buybacks;excise_tax_or_withholding",
                     reason_class="line_presented_combined_with_others", reason="buyback line includes excise tax or tax-withholding shares (label); founder 2026-11-04 buyback perimeter; cash-flow card D1", decided_by="library")
        if r.get("decision") == "concept" and r["canonical_concept"] == "depreciation_and_amortization_resolved" and re.search(r"(?i)impairment|accretion|nuclear fuel", lab):
            pure = [k for k in cf_da if k is not r and shares_filing(r, k)]
            if not pure:
                r.update(decision="combined", canonical_concept="", components="depreciation_and_amortization;impairment_accretion_or_fuel",
                         reason_class="line_presented_combined_with_others", reason="D&A line includes impairment, accretion or nuclear fuel (label); no pure D&A line printed; cash-flow card D2", decided_by="library")
    for r in rs:
        lab = r.get("evidence_plabel") or ""
        plain_ar = re.fullmatch(r"(?i)\s*(trade )?accounts receivable(s)?(,? net)?(,? less allowance[^|]*|,? net of allowance[^|]*)?\s*", lab or "")
        if r.get("decision") == "concept" and r["canonical_concept"] == "accounts_receivable" and (re.search(r"(?i)\band other\b|notes and", lab)
                or (r["tag"] == "ReceivablesNetCurrent" and not plain_ar)):
            r.update(decision="combined", canonical_concept="", components="accounts_receivable;other_receivables",
                     reason_class="line_presented_combined_with_others", reason="receivables line includes other or notes receivable (label); shown as the company line (BS card)", decided_by="library")
        if r.get("decision") == "concept" and r["canonical_concept"] == "interest_expense_resolved" and re.search(r"(?i)\bnet\b", lab):
            r.update(decision="combined", canonical_concept="", components="interest_expense;interest_income",
                     reason_class="line_presented_combined_with_others", reason="'interest expense, net' is net of interest income (label); shown as the company line (IS card)", decided_by="library")
        if r.get("reason_class") == "nonoperating_total_incl_interest":
            r.update(decision="combined", components="other_income_expense_net;interest_expense;interest_income", reason_class="line_presented_combined_with_others",
                     reason="total non-operating income incl. interest: shown as the company line; never other_income_expense_net (double counts interest)")
    if not any(r.get("decision") == "concept" and r["canonical_concept"] == "inventory" for r in rs):
        for r in rs:
            if (r["stmt"] == "BS" and re.search(r"Inventor", r["tag"]) and "Noncurrent" not in r["tag"] and not re.search(r"(Abstract|Table|LineItems|Axis|Domain|Member|RollForward)$", r["tag"])
                    and "AssetsCurrent" in (r.get("evidence_cal_parent") or "").split(";")):
                r.update(decision="component", canonical_concept="", parent_concept="inventory", combine_sign="1", reason_class="",
                         reason="no inventory total printed: inventory = the printed inventory lines (BS card)", decided_by="library")
    cf_due = ("CF", "CashAndDueFromBanks") in idx
    if cf_due and ("BS", "CashAndDueFromBanks") in idx:
        due = idx[("BS", "CashAndDueFromBanks")]
        dep = idx.get(("BS", "InterestBearingDepositsInBanks"))
        if ("CF", "InterestBearingDepositsInBanks") in idx and dep:
            for x in (due, dep):
                x.update(decision="component", canonical_concept="", parent_concept="cash_and_equivalents_resolved", combine_sign="1", reason_class="",
                         reason="bank/broker cash = the BS lines the CF uses as ending cash (BS card)", decided_by="library")
        else:
            due.update(decision="concept", canonical_concept="cash_and_equivalents_resolved", reason_class="",
                       reason="bank cash: the BS line equals the CF ending cash line (BS card)", decided_by="library")
    # product + service cost lines printed side by side with no cost-of-revenue total: a printed component sum (D3, TMO)
    COR_TOTALS = ("CostOfRevenue", "CostOfGoodsAndServicesSold")
    prod, serv = idx.get(("IS", "CostOfGoodsSold")), idx.get(("IS", "CostOfServices"))
    if prod and serv and shares_filing(prod, serv) and serv.get("decided_by") != "company_override":
        tot = [idx[("IS", t)] for t in COR_TOTALS if ("IS", t) in idx and idx[("IS", t)].get("decision") == "concept"]
        if not any(shares_filing(prod, t) for t in tot):
            for x in (prod, serv):
                x.update(decision="component", canonical_concept="", parent_concept="cost_of_revenue_resolved", combine_sign="1", reason_class="",
                         reason="product and service costs printed side by side with no cost-of-revenue total: a printed component sum (ruling D3)", decided_by="library")
    # ruling (3) 2026-11-11: NI = ProfitLoss - NCI only where both are printed on the IS face, the NCI line is the printed
    # deduction, and no NI-attributable line exists in that era (AVGO 2019-08..2020-10): a duration component sum (D3)
    nci = next((idx[("IS", t)] for t in NCI_TAGS if ("IS", t) in idx), None)
    nil = idx.get(("IS", "NetIncomeLoss"))
    for cut in list(pending_extra):
        if cut["tag"] == "ProfitLoss" and cut["reason_class"] == "ni_incl_nci" and nci and overlap(cut, nci):
            a = max(cut["era_from"], nci["era_from"], day_after(nil["era_to"]) if nil else "0000-00-00")
            b = min(cut["era_to"], nci["era_to"])
            if a > b:
                continue
            if cut["era_from"] < a:  # the part where NetIncomeLoss is printed keeps its reason
                cut["era_to"] = day_before(a)
            else:
                pending_extra.remove(cut)
            for x, sign in ((cut, "1"), (nci, "-1")):
                e = dict(x)
                e.update(decision="component", canonical_concept="", parent_concept="net_income_resolved", combine_sign=sign, era_from=a, era_to=b,
                         reason_class="", reason="NI attributable = ProfitLoss - NCI, both printed on the IS face, no NI-attributable line in this era (ruling 3, 2026-11-11)",
                         decided_by="library")
                pending_extra.append(e)
    extra = list(pending_extra)
    opex_total = [r for r in rs if r["stmt"] == "IS" and r["tag"] == "OperatingExpenses" and r.get("decision") == "concept"]
    gp = [r for r in rs if r["stmt"] == "IS" and r["tag"] == "GrossProfit"]
    if not opex_total and gp:
        for r in rs:
            par = (r.get("evidence_cal_parent") or "").split(";")
            if (r["stmt"] == "IS" and r["taxonomy"] in ("us-gaap", "custom") and "OperatingIncomeLoss" in par and r["tag"] not in ("GrossProfit", "OperatingIncomeLoss")
                    and not re.search(r"(?i)\b(gain|income)\b|^(total )?(net )?(revenues?|sales)$", r.get("evidence_plabel") or "")
                    and not re.search(r"(Revenue|Sales|GrossProfit|CostOf)", r["tag"])):
                e = dict(r)
                e.update(decision="component", canonical_concept="", parent_concept="operating_expenses_resolved", combine_sign="1",
                         reason_class="", reason="no operating-expenses total printed: operating expenses = the expense lines between gross profit and operating income (mapper: GP - sum = OI must tie per filing, else hold)",
                         decided_by="library_opex_parts")
                extra.append(e)
    eb = idx.get(("IS", "EarningsPerShareBasicAndDiluted"))
    if eb and eb.get("decision") == "concept":
        other = "basic_eps_resolved" if eb["canonical_concept"] == "diluted_eps_resolved" else "diluted_eps_resolved"
        e = dict(eb)
        e.update(canonical_concept=other, reason="one printed EPS line serves basic AND diluted (row per concept)")
        extra.append(e)
    wb = idx.get(("IS", "WeightedAverageNumberOfShareOutstandingBasicAndDiluted"))
    if wb and wb.get("decision") == "concept":
        e = dict(wb)
        e.update(canonical_concept="weighted_diluted_shares", reason="one printed weighted-share line serves basic AND diluted (Tag Expert (c))")
        extra.append(e)
    rs.extend(extra)
    # FINAL de-overlap (0122 trigger): no two 'concept' rows for one (company, stmt, concept) may overlap in era, whatever the
    # filings. Winner by rule priority, then tier, then filings; a loser keeps only its era outside the kept rows, and the
    # cut-out era becomes an excluded reason row.
    cut_rows = []
    groups = collections.defaultdict(list)
    for r in rs:
        if r.get("decision") == "concept" and r.get("canonical_concept"):
            groups[(r["stmt"], r["canonical_concept"])].append(r)
    for (st, con), g in groups.items():
        g.sort(key=lambda r: (prio.get((st, r["tag"]), 50), tier_of.get((st, r["tag"]), (con, 9))[1], -int(r.get("filings") or 0), r["era_from"]))
        kept = []
        for r in g:
            hit = [k for k in kept if overlap(r, k)]
            if not hit:
                kept.append(r)
                continue
            lo, hi = min(k["era_from"] for k in hit), max(k["era_to"] for k in hit)
            parts = []
            if r["era_from"] < lo:
                parts.append((r["era_from"], day_before(lo)))
            if r["era_to"] > hi:
                parts.append((day_after(hi), r["era_to"]))
            parts = [p for p in parts if p[0] <= p[1] and not any(overlap({"era_from": p[0], "era_to": p[1]}, k) for k in kept)]
            mid = dict(r)  # the era the winner serves: a reason row
            mid.update(decision="excluded", canonical_concept="", reason_class="alternate_tag_overlapping",
                       reason=f"same concept {con} served by {', '.join(k['tag'] for k in hit)} in this era (no two concept tags per period)",
                       era_from=max(r["era_from"], lo), era_to=min(r["era_to"], hi), decided_by="final_deoverlap")
            cut_rows.append(mid)
            for i, (f, t) in enumerate(parts):
                c = r if i == 0 else dict(r)
                c.update(era_from=f, era_to=t)
                if i:
                    cut_rows.append(c)
                kept.append(c)
            if not parts:
                r.update(decision="excluded", canonical_concept="", reason_class="alternate_tag_overlapping",
                         reason=mid["reason"], decided_by="final_deoverlap")
                cut_rows.remove(mid)
    rs.extend(cut_rows)
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
