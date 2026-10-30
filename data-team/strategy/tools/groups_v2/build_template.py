"""template v1 DRAFT over catalog_version: cell lists per group (PROPOSAL ONLY, not approved).
Rule codes: REQ required | REP replaced by a group definition (accountant; definition_pending until ruled) | COND applies when an
evidenced condition holds (state if false: not_presented / evidenced_zero / undefined_by_math) | NIT not in template.
Base lines = the 133-line catalog (163 data points minus the 30 F-1 removals). Sector rows = catalog extension (data-team/strategy/50 as corrected).
Presence rates (R4, FSDS pre.txt of the filers' own face statements, DATA-INFERRED) drive the leaf defaults: >=95% REQ, 15-94% COND, <15% NIT,
then explicit meaning-based overrides. Metric lines follow their inputs by propagation (AT-4.2l)."""
import csv, json, collections

BASE = "/Users/vikash/wt-sector-groups/data-team/strategy/data/"
CATALOG_VERSION = "cv-2026.10.22-draft1"
TEMPLATE_VERSION = "tv1-draft-2026.10.22"
GROUPS = ["corporate", "utility", "energy", "midstream", "managed_care", "insurance_broker", "exchange", "crypto_digital",
          "bank", "lender_nonbank", "insurer", "reit_equity", "reit_mortgage", "bdc", "asset_manager", "broker_dealer"]
R4FAM = {"corporate": "corporate_other", "utility": "utility_waste", "energy": "energy", "midstream": "MLP_partnership",
         "managed_care": "corporate_other", "insurance_broker": "insurance_agent_broker", "exchange": "corporate_other",
         "crypto_digital": "corporate_other", "bank": "bank_thrift", "lender_nonbank": "nonbank_lender_credit_fintech",
         "insurer": "insurer_underwriter", "reit_equity": "REIT_equity", "reit_mortgage": "REIT_mortgage", "bdc": "BDC_fund",
         "asset_manager": "asset_manager_adviser", "broker_dealer": "broker_dealer_exchange"}
GROUPS_ALL = GROUPS
PRESENT_PROXY = {"managed_care": "corporate_other (no managed-care presence file; proxy)", "crypto_digital": "corporate_other (proxy)",
                 "exchange": "corporate_other (proxy; S2 FILING-CHECKED ICE CME NDAQ CBOE TW classified balance sheets)"}

pres = {r["fam"]: r for r in csv.DictReader(open(BASE + "r4_sector/presence.csv"))}
names = [r["data_point"] for r in csv.DictReader(open(BASE + "empirical_template_candidates.csv"))]
graph = {r["data_point"]: r for r in csv.DictReader(open(BASE + "metric_dependency_graph.csv"))}
F1 = set("basic_eps capex cash_and_equivalents cash_flow_financing cash_flow_investing cfo cost_of_revenue current_assets current_liabilities depreciation_and_amortization diluted_eps dividends_paid dividends_per_share employee_count gross_profit income_before_tax income_tax_expense interest_expense net_income operating_expenses operating_income ppe_net share_buybacks shares_outstanding stockholders_equity total_assets total_debt total_liabilities revenue total_debt_split".split())
CATALOG = [n for n in names if n not in F1]
assert len(CATALOG) == 133

# R4 presence column for each base leaf (the 33 consumed concepts)
PCOL = {"revenue": "revenue", "cost_of_revenue": "cost_of_revenue", "gross_profit": "gross_profit_line", "operating_income": "operating_income",
        "income_before_tax": "income_before_tax", "income_tax_expense": "income_tax_expense", "net_income": "net_income",
        "diluted_eps": "diluted_eps", "basic_eps": "basic_eps", "interest_expense": "interest_expense", "interest_income": "interest_income",
        "sga_expense": "sga_expense", "research_and_development": "research_and_development", "sbc": "sbc",
        "depreciation_and_amortization": "depreciation_and_amortization_resolved", "cfo": "cfo", "capex": "capex",
        "dividends_paid": "dividends_paid", "share_buybacks": "share_buybacks", "dividends_per_share": "dividends_per_share",
        "total_assets": "total_assets", "current_assets": "current_assets", "current_liabilities": "current_liabilities",
        "stockholders_equity": "stockholders_equity", "cash_and_equivalents": "cash_and_equivalents", "inventory": "inventory",
        "accounts_receivable": "accounts_receivable", "accounts_payable": "accounts_payable", "goodwill": "goodwill",
        "total_debt": "total_debt_resolved", "cash_flow_investing": "cash_flow_investing", "cash_flow_financing": "cash_flow_financing"}
# resolved twin / derived concept -> base leaf whose applicability it follows
BASE_OF = {"basic_eps_resolved": "basic_eps", "capex_resolved": "capex", "cash_and_equivalents_resolved": "cash_and_equivalents",
           "cash_flow_financing_resolved": "cash_flow_financing", "cash_flow_investing_resolved": "cash_flow_investing", "cfo_resolved": "cfo",
           "cost_of_revenue_resolved": "cost_of_revenue", "current_assets_resolved": "current_assets", "current_liabilities_resolved": "current_liabilities",
           "depreciation_and_amortization_resolved": "depreciation_and_amortization", "diluted_eps_resolved": "diluted_eps",
           "dividends_paid_resolved": "dividends_paid", "dividends_per_share_resolved": "dividends_per_share", "employee_count_resolved": "employee_count",
           "gross_profit_resolved": "gross_profit", "income_before_tax_resolved": "income_before_tax", "income_tax_expense_resolved": "income_tax_expense",
           "interest_expense_resolved": "interest_expense", "net_income_resolved": "net_income", "operating_expenses_resolved": "operating_expenses",
           "operating_income_resolved": "operating_income", "ppe_net_resolved": "ppe_net", "revenue_sanity_resolved": "revenue",
           "share_buybacks_resolved": "share_buybacks", "shares_outstanding_resolved": "shares_outstanding", "stockholders_equity_resolved": "stockholders_equity",
           "total_assets_resolved": "total_assets", "total_debt_resolved": "total_debt", "total_liabilities_resolved": "total_liabilities"}

def band(p):
    return "REQ" if p >= 95 else ("COND" if p >= 15 else "NIT")

# explicit meaning-based overrides on base leaves: (leaf, group) -> (code, why)
OV = {}
def ov(leaf, groups, code, why):
    for g in groups.split():
        OV[(leaf, g)] = (code, why)

ov("revenue", "bank lender_nonbank reit_mortgage bdc broker_dealer", "REP", "revenue is defined by the group (bank: NII + noninterest income; lender/mortgage REIT: interest and fee income; BDC: total investment income; broker-dealer: net revenues); accountant ruling pending; Revenues tag is not safe at banks (tag card revenue.md, data-team/32 s3)")
ov("revenue", "asset_manager", "COND", "R4: revenue caption on the face for 47% of asset managers")
ov("cost_of_revenue", "bank insurer reit_mortgage bdc asset_manager broker_dealer", "NIT", "no cost-of-revenue line on the face (R4 presence <=15%)")
ov("gross_profit", "bank insurer reit_mortgage bdc asset_manager broker_dealer", "NIT", "no gross-profit line (R4 presence <=15%)")
ov("operating_income", "bank insurer reit_mortgage bdc", "NIT", "no operating-income line (R4 <=19%); OperatingIncomeLoss at banks is a mis-tag (tag card operating-income.md; BANR, PEBO)")
ov("interest_expense", "bank lender_nonbank reit_mortgage", "REP", "funding cost is a sector row (total interest expense) at these groups")
ov("interest_income", "bank lender_nonbank reit_mortgage", "REP", "InvestmentIncomeInterest is the securities line at banks (FLG); total interest income is a sector row")
ov("interest_income", "insurer bdc", "NIT", "investment income is a sector row (insurer net investment income / BDC total investment income)")
ov("sga_expense", "bank insurer reit_equity reit_mortgage bdc asset_manager broker_dealer", "NIT", "no SG&A line (R4 <=16%); REIT G&A is a sector row")
ov("research_and_development", "utility energy midstream bank insurer reit_equity reit_mortgage bdc asset_manager broker_dealer insurance_broker exchange", "NIT", "no R&D line (R4 <=6%)")
ov("inventory", "bank insurer reit_equity reit_mortgage bdc asset_manager broker_dealer lender_nonbank insurance_broker", "NIT", "no inventory line (R4 <=6%)")
ov("current_assets", "bank insurer reit_equity reit_mortgage bdc asset_manager broker_dealer", "NIT", "unclassified balance sheet (R4 <=16%)")
ov("current_liabilities", "bank insurer reit_equity reit_mortgage bdc asset_manager broker_dealer", "NIT", "unclassified balance sheet (R4 <=16%)")
ov("capex", "reit_equity", "REP", "capex perimeter (improvements vs acquisitions) needs the accountant (R4 s3; S008 WELL)")
ov("capex", "reit_mortgage bdc", "NIT", "no capex line (R4 <=37%, BDC 1%)")
ov("cash_flow_investing", "bdc", "NIT", "BDC cash-flow statements have no investing section (R4 1%)")
ov("depreciation_and_amortization", "bank insurer reit_mortgage bdc", "COND", "'amortization' at financials is premium/discount/DAC, not D&A (perimeter risk; R4 footnote *)")
ov("total_debt", "bank insurer reit_mortgage", "REP", "borrowings perimeter (deposits are not debt; repos, FHLB advances, notes) needs the accountant (R4 D)")
ov("total_debt", "bdc lender_nonbank broker_dealer asset_manager", "COND", "debt is funding; perimeter per AC card")
ov("goodwill", "reit_mortgage bdc", "NIT", "no goodwill line (R4 <=9%)")
ov("dividends_paid", "reit_equity reit_mortgage bdc", "REQ", "REIT/RIC distribution requirement; R4 presence 82-94%")
ov("dividends_per_share", "reit_equity reit_mortgage bdc", "REQ", "REIT/RIC distribution requirement")
ov("employee_count", "corporate utility energy midstream managed_care insurance_broker exchange crypto_digital bank lender_nonbank insurer reit_equity reit_mortgage bdc asset_manager broker_dealer", "NIT", "D-4 (freeze register): not in template until the 10-K prose source has a staleness rule and a Verifier sample")
ov("shares_outstanding", "corporate utility energy midstream managed_care insurance_broker exchange crypto_digital bank lender_nonbank insurer reit_equity reit_mortgage bdc asset_manager broker_dealer", "REQ", "cover page dei; per-class issuers need class handling (BRK, GOOGL)")
ov("operating_expenses", "bank insurer reit_mortgage bdc", "NIT", "no total operating expense line in the industrial sense")
ov("gross_profit", "lender_nonbank", "NIT", "no gross profit at lenders (R4 19%)")

ov("cost_of_revenue", "lender_nonbank", "NIT", "gross-margin family not in lender template (doc 30 s2.2); R4 38% is interest/servicing captions")
ov("cost_of_revenue", "insurance_broker", "NIT", "0 of 7 insurance brokers show a cost-of-revenue line on the face (R-file reader, this run)")
ov("gross_profit", "insurance_broker", "NIT", "0 of 7 insurance brokers show cost of revenue, so no gross profit")
ov("current_assets", "exchange", "COND", "4 of 6 exchanges show total current assets (R-file reader); TW and MKTX-type balance sheets are unclassified")
ov("current_liabilities", "exchange", "COND", "as current assets")
LEAF_SPECIAL = {  # leaves without R4 presence column: group -> code (default COND), with reason
    "amortization_of_intangibles": ("COND", {"bdc": "NIT", "reit_mortgage": "NIT"}, "judgement; no presence file"),
    "collaborative_arrangement_revenue": ("NIT", {"corporate": "COND"}, "biotech/pharma collaboration revenue tag; corporate only, evidence-gated"),
    "comprehensive_income": ("COND", {}, "OCI statement presented by most filers; judgement"),
    "effective_tax_rate_reported": ("COND", {"bdc": "NIT", "reit_equity": "COND"}, "company-disclosed rate; judgement"),
    "other_income_expense_net": ("COND", {"bank": "NIT", "insurer": "NIT", "bdc": "NIT", "reit_mortgage": "NIT", "lender_nonbank": "NIT"}, "judgement; bank NonoperatingIncomeExpense then InterestIncomeExpenseNet ordering is a known defect (data-team/30)"),
    "ppe_net": ("COND", {"corporate": "REQ", "utility": "REQ", "energy": "REQ", "midstream": "REQ", "managed_care": "REQ", "crypto_digital": "REQ", "reit_mortgage": "NIT", "bdc": "NIT"}, "judgement"),
    "public_float": ("REQ", {}, "cover page dei:EntityPublicFloat; scale check DQC_0222; never market cap"),
    "total_liabilities": ("COND", {"bank": "REQ", "insurer": "REQ", "reit_mortgage": "REQ", "bdc": "REQ"}, "total liabilities line often absent at industrials; judgement"),
    "operating_expenses": ("COND", {}, "derived concept"),
    "bdc_total_investment_income": ("NIT", {"bdc": "REQ"}, "registry row that exists only for BDC; gated by group (R4 s3 last para). Collides with insurer net investment income today (24 insurers): never count against other groups"),
    "net_lease_revenue": ("NIT", {"reit_equity": "REQ", "reit_mortgage": "NIT"}, "registry row that exists only for lessors; gated by group"),
    "cf_ar_change": ("FOLLOW:accounts_receivable", {}, ""),
    "cf_ap_change": ("FOLLOW:accounts_payable", {}, ""),
    "cf_inventory_change": ("FOLLOW:inventory", {}, ""),
}
EXTERNAL = {"price": "REQ", "insider_ownership": "REQ", "institutional_ownership": "REQ", "mutual_fund_ownership": "REQ"}

ACTIVITY = {"dividends_paid", "dividends_per_share", "share_buybacks"}
def leaf_rule(leaf, g):
    """returns (code, basis)"""
    c, b = _leaf_rule(leaf, g)
    if leaf in ACTIVITY and c == "NIT":
        return "COND", "activity row: a non-payer is evidenced_zero / no-activity evidence, never not-in-template (" + b[:120] + ")"
    return c, b

def _leaf_rule(leaf, g):
    if (leaf, g) in OV:
        c, why = OV[(leaf, g)]
        return c, "override: " + why
    if leaf in LEAF_SPECIAL:
        dflt, per, why = LEAF_SPECIAL[leaf]
        if dflt.startswith("FOLLOW:"):
            return leaf_rule(dflt.split(":", 1)[1], g)
        return per.get(g, dflt), why
    if leaf in PCOL:
        p = float(pres[R4FAM[g]][PCOL[leaf]])
        c = band(p)
        proxy = " [" + PRESENT_PROXY[g] + "]" if g in PRESENT_PROXY else ""
        return c, f"R4 face presence {p:.0f}% in {R4FAM[g]}{proxy} (DATA-INFERRED)"
    return "COND", "no presence data; judgement"

def base_leaf(dp):
    return BASE_OF.get(dp, dp)

RANK = {"NIT": 0, "REP": 1, "COND": 2, "REQ": 3}
def combine(codes):
    if any(c == "NIT" for c in codes): return "NIT"
    if any(c == "REP" for c in codes): return "REP"
    if any(c == "COND" for c in codes): return "COND"
    return "REQ"

# E-M (line exists, metric meaningless by definition for the group) - accountant ruling pending (freeze register; R4 s6; data-team/32 s5; 30 s2.3)
EM = {}
def em(metrics, groups, why):
    for m in metrics.split():
        for g in groups.split():
            EM[(m, g)] = why
em("fcf fcf_margin fcf_per_share fcf_yield fcf_growth_yoy fcf_growth_3y_cagr fcf_growth_5y_cagr fcf_gt_net_income dividends_pct_fcf share_repurchases_pct_fcf", "bank insurer",
   "cash from operations is deposit/loan/held-for-sale/float flow; FCF meaningless by definition (JPM CFO -147,782M R9; E-M)")
em("debt_to_equity zero_debt net_cash net_cash_per_share ev_sales ev_ebitda net_debt_ebitda debt_to_ebitda", "bank insurer",
   "deposits/float are not debt; EV undefined for deposit-funded entities (E-M)")
em("debt_to_equity net_cash net_cash_per_share ev_sales ev_ebitda net_debt_ebitda debt_to_ebitda zero_debt", "reit_mortgage bdc",
   "debt is the funding model; replaced by group leverage rows (E-M)")
ov("net_interest_income", "bank lender_nonbank reit_mortgage", "NIT", "superseded by sr.fin.net_interest_income (the old metric subtracts total interest expense from the securities-only InvestmentIncomeInterest; id/name collision)")
em("interest_coverage_ratio roic", "bank insurer reit_mortgage bdc", "operating income / invested capital undefined (E-M)")

def metric_rule(dp, g, cache):
    key = (dp, g)
    if key in cache: return cache[key]
    row = graph[dp]
    kind = row["kind"]
    if (dp, g) in OV and kind == "metric":
        cache[key] = (OV[(dp, g)][0], "override: " + OV[(dp, g)][1]); return cache[key]
    if (dp, g) in EM:
        cache[key] = ("NIT", "E-M: " + EM[(dp, g)] + " [accountant-gated, needs_accountant=Y]")
        return cache[key]
    if kind == "external_source" or dp in EXTERNAL:
        cache[key] = (EXTERNAL.get(dp, "REQ"), "external source (price vendor / ownership tables)")
        return cache[key]
    if kind in ("leaf_concept", "resolved_concept", "derived_concept") and dp != "total_debt_resolved":
        c, b = leaf_rule(base_leaf(dp), g)
        cache[key] = (c, b)
        return cache[key]
    if dp == "total_debt_resolved":
        c, b = leaf_rule("total_debt", g); cache[key] = (c, b); return cache[key]
    ins = [x.split(":")[0] for x in row["direct_inputs(node:role)"].split(";") if x]
    ins = [i for i in dict.fromkeys(ins)]
    codes, why = [], []
    for i in ins:
        if i == "price":
            codes.append("REQ"); continue
        if i in graph:
            c, _ = metric_rule(i, g, cache)
        else:
            c, _ = leaf_rule(base_leaf(i), g)
        codes.append(c)
    code = combine(codes) if codes else "COND"
    # market cap needs price and shares only
    cache[key] = (code, "propagated from inputs: " + ",".join(f"{i}={c}" for i, c in zip(ins, codes)))
    return cache[key]

# ---------------- sector rows (catalog extension; corrected from doc 50; ids are namespaced) -----------------
# (id, label, groups->code dict, formula/face source, group_defining, tag_leads_unverified, needs_accountant, note)
S = []
def sr(id_, label, groups, formula, defining="N", tags="", acct="N", note=""):
    S.append(dict(id=id_, label=label, groups=groups, formula=formula, defining=defining, tags=tags, acct=acct, note=note))

BANKLIKE = {"bank": "REQ", "lender_nonbank": "COND"}
sr("sr.fin.net_interest_income", "Net interest income", {"bank": "REQ", "lender_nonbank": "COND", "reit_mortgage": "REQ"}, "face line", "Y", "InterestIncomeExpenseNet (bank-only reading; also InterestRevenueExpenseNet at ACNB; non-banks use it as net interest EXPENSE)", note="Existing metric 'net_interest_income' = interest_income - interest_expense with interest_income = InvestmentIncomeInterest is wrong for banks: new row needs a new id and a MAJOR definition version, never the old name")
sr("sr.fin.interest_income_total", "Total interest income", {"bank": "REQ", "lender_nonbank": "REQ", "reit_mortgage": "REQ"}, "face line", "Y", "InterestAndDividendIncomeOperating; InterestIncomeOperating (3 of 30 banks); NEVER InvestmentIncomeInterest")
sr("sr.fin.interest_expense_total", "Total interest expense", {"bank": "REQ", "lender_nonbank": "REQ", "reit_mortgage": "REQ"}, "face line", "Y", "InterestExpenseOperating (44 of 44 banks have it or InterestExpense; InterestExpense alone covers only 2 of 44, so doc 50 lead is wrong); mortgage REITs 2/2 InterestExpenseOperating")
sr("sr.bank.noninterest_income", "Noninterest income", {"bank": "REQ", "lender_nonbank": "COND"}, "face line", "Y", "NoninterestIncome (29/30; BANR mis-tags OperatingIncomeLoss: company-scoped exception)")
sr("sr.bank.noninterest_expense", "Noninterest expense", {"bank": "REQ", "lender_nonbank": "COND"}, "face line", "Y", "NoninterestExpense (30/30)")
sr("sr.fin.provision_credit_losses", "Provision for credit losses", {"bank": "REQ", "lender_nonbank": "REQ"}, "face line (total provision caption)", "Y", "NO single safe tag: 7 tags across 30 banks, custom at BAC/FHN/PNC, CECL switch (CCB changed tag between 10-K and 10-Q); perimeter label needed (loans only vs loans + unfunded + securities)", "Y")
sr("sr.bank.revenue_net_of_interest_expense", "Bank revenue (NII + noninterest income)", {"bank": "REP"}, "sr.fin.net_interest_income + sr.bank.noninterest_income", "N", "derived; RevenuesNetOfInterestExpense is presented at JPM, WFC only (cross-check)", "Y", "SFNC FY2025 noninterest income -616M gives a mathematically correct but misleading margin: needs a materiality/NM rule")
sr("sr.bank.efficiency_ratio", "Efficiency ratio (reported basis)", {"bank": "REP"}, "sr.bank.noninterest_expense / sr.bank.revenue_net_of_interest_expense", "N", "derived", "Y", "label 'reported basis, not company-adjusted'")
sr("sr.bank.deposits_total", "Total deposits", {"bank": "REQ", "lender_nonbank": "NIT"}, "face line, else sum of interest-bearing + noninterest-bearing", "Y", "Deposits (27/30); BANR/CARV components only; TFSL no total", note="composition=calculated where only components are filed")
sr("sr.fin.loans_net", "Loans, net of allowance", {"bank": "REQ", "lender_nonbank": "REQ"}, "face line, period-scoped tag set", "Y", "post-CECL FinancingReceivableExcludingAccruedInterestAfterAllowanceForCreditLoss (33 of 44 banks; lenders AFRM/RKT-type use NotesReceivableNet); pre-CECL LoansAndLeasesReceivableNetReportedAmount (1 of 44 on the latest 10-K; doc 50 listed ONLY this tag); NotesReceivableNet company-scoped only")
sr("sr.fin.allowance_credit_losses", "Allowance for credit losses", {"bank": "COND", "lender_nonbank": "COND"}, "face or note", "N", "FinancingReceivableAllowanceForCreditLossExcludingAccruedInterest (20/30); pre-CECL LoansAndLeasesReceivableAllowance; doc 50 name 'AllowanceForLoanAndLeaseLosses...' not verified")
sr("sr.bank.loans_to_deposits", "Loans to deposits", {"bank": "REQ"}, "sr.fin.loans_net / sr.bank.deposits_total", "N", "derived")
sr("sr.bank.equity_to_assets", "Equity to assets", {"bank": "REQ", "insurer": "NIT"}, "stockholders_equity / total_assets (parent common equity basis, preferred disclosed)", "N", "derived from existing concepts")
sr("sr.bank.tangible_book_value_per_share", "Tangible book value per share", {"bank": "REP"}, "(common equity - goodwill - other intangibles) / shares", "N", "goodwill exists; other intangibles and preferred have no concept", "Y")
sr("sr.ins.premiums_earned", "Premiums earned", {"insurer": "REQ", "managed_care": "REQ"}, "face line", "Y", "PremiumsEarnedNet (36 of 40 insurers, 6 of 7 managed-care filers use the same tag, labelled Premiums)", note="one concept for insurer and managed care; doc 50 had separate M1")
sr("sr.ins.net_investment_income", "Net investment income (insurer)", {"insurer": "REQ"}, "face line", "Y", "NetInvestmentIncome (35 of 40 insurers), InvestmentIncomeNet", note="Same tag NetInvestmentIncome is the BDC operating result after expenses (sr.bdc.net_investment_income): one tag, two meanings; the two concepts must not share a mapping (24 insurers already land in the BDC concept today)")
sr("sr.ins.benefits_claims_incurred", "Benefits, losses and claims incurred (medical costs at managed care)", {"insurer": "REQ", "managed_care": "REQ"}, "face line (P&C: losses and LAE; life: policyholder benefits; health: medical costs)", "Y", "PolicyholderBenefitsAndClaimsIncurredNet (33 of 40 insurers; 6 of 7 managed-care filers label it Medical costs); IncurredClaimsPropertyCasualtyAndLiability", "Y", "net vs gross of reinsurance must be labelled; doc 50 had separate M2")
sr("sr.ins.policy_acquisition_cost_amortization", "Amortization of policy acquisition costs", {"insurer": "COND"}, "face line", "N", "DeferredPolicyAcquisitionCostAmortizationExpense (19 of 40 on the face)")
sr("sr.ins.reserves_unpaid_claims", "Reserves for unpaid claims (P&C, health)", {"insurer": "COND"}, "face line", "Y", "LiabilityForClaimsAndClaimsAdjustmentExpense (27 of 40 insurers; also 6 of 7 managed care as Benefits payable)", note="P&C/health only; doc 50 I6 applied it to all insurers")
sr("sr.ins.future_policy_benefits", "Future policy benefits and policyholder account balances (life)", {"insurer": "COND"}, "face lines", "Y", "LiabilityForFuturePolicyBenefits; PolicyholderContractDeposits (21 of 40 insurers show one of them)", "Y", "life-insurer defining row missing in doc 50")
sr("sr.ins.loss_ratio", "Loss ratio (P&C and health only)", {"insurer": "COND", "managed_care": "NIT"}, "sr.ins.benefits_claims_incurred / sr.ins.premiums_earned", "N", "derived", "Y", "reported basis; not for life; combined ratio is MD&A, excluded")
sr("sr.mc.medical_care_ratio", "Medical care ratio (GAAP face basis)", {"managed_care": "COND"}, "sr.ins.benefits_claims_incurred / sr.ins.premiums_earned", "N", "derived", "Y", "not the ACA/regulatory MLR; COND because Cigna/Elevance-type pharmacy revenue dilutes the premium base")
sr("sr.ib.commissions_and_fees", "Commissions and fees revenue (component of revenue)", {"insurance_broker": "COND"}, "face line when separate", "N", "7 of 7 brokers show ONE total-revenue line (RevenueFromContractWithCustomerExcludingAssessedTax or Revenues); AJG/BRO/RYAN split commissions and fees, MRSH/AON/WTW do not; doc 50 had no insurance-broker row")
sr("sr.ib.fiduciary_assets", "Fiduciary assets (and matching liabilities)", {"insurance_broker": "COND"}, "face line", "Y", "fiduciary lines are EXTENSION tags (aon FiduciaryAssets, ajg FiduciaryAssetsCurrent, bro FiduciaryCashCurrent; 0 of 7 us-gaap): capture path = filing instance")
sr("sr.ex.performance_bonds_guaranty_funds", "Clearing assets: performance bonds and guaranty fund contributions", {"exchange": "COND"}, "face line", "Y", "extension tags: CME (MarginDepositsAndGuarantyFundsLiabilitiesCurrent, cme prefix), ICE (ice prefix), CBOE (cboe prefix); 0 of 6 show a us-gaap-prefixed margin-deposit tag: custom facts are absent from companyfacts, capture path = filing instance")
sr("sr.ex.transaction_clearing_revenue", "Transaction and clearing revenue", {"exchange": "COND"}, "face line", "N", "unverified; captions differ (net of transaction-based expenses at ICE/NDAQ/CBOE)")
sr("sr.reit.rental_revenue", "Rental / lease revenue", {"reit_equity": "COND"}, "face line", "Y", "28 of 53 equity REITs show OperatingLeaseLeaseIncome / OperatingLeasesIncomeStatementLeaseRevenue / RealEstateRevenueNet / LeaseAndRentalRevenue; the operating-REIT variant (towers, storage, timber, data centers, hotels) shows plain revenue; REQ for the property_reit variant only", note="doc 50 R1 was REQ for all equity REITs")
sr("sr.reit.property_operating_expenses", "Property operating expenses", {"reit_equity": "COND"}, "face line", "N", "DirectCostsOfLeasedAndRentedPropertyOrEquipment (67/30), RealEstateTaxExpense (56/45): sparse; ESRT face line is custom-labelled")
sr("sr.reit.noi", "Net operating income (face basis)", {"reit_equity": "REP"}, "property revenues (incl. tenant reimbursements) - property operating expenses", "N", "derived", "Y", "doc 50 R3 used rental revenue only, which excludes reimbursements and understates NOI")
sr("sr.reit.real_estate_at_cost", "Real estate investment property, at cost", {"reit_equity": "COND"}, "face or Schedule III note", "Y", "RealEstateInvestmentPropertyAtCost / ...Gross (26 of 53 on the face)")
sr("sr.reit.real_estate_net", "Real estate investment property, net", {"reit_equity": "COND"}, "face line", "Y", "RealEstateInvestmentPropertyNet (36 of 53 on the face)")
sr("sr.reit.accumulated_depreciation", "Accumulated depreciation on real estate", {"reit_equity": "COND"}, "face or note", "N", "RealEstateInvestmentPropertyAccumulatedDepreciation (30 of 53 on the face)")
sr("sr.reit.general_and_administrative", "General and administrative expense", {"reit_equity": "COND"}, "face line", "N", "GeneralAndAdministrativeExpense (47 of 53 equity REITs, 2 of 2 mortgage REITs)")
sr("sr.reit.debt_to_total_assets", "Debt to total assets", {"reit_equity": "REP"}, "total_debt_resolved / total_assets", "N", "derived", "Y", "needs the debt perimeter (secured vs unsecured, leases)")
sr("sr.mreit.repurchase_agreements", "Repurchase agreements (funding)", {"reit_mortgage": "COND"}, "face line", "Y", "SecuritiesSoldUnderAgreementsToRepurchase / AssetsSoldUnderAgreementsToRepurchase (1 of 2 on the face; AGNC and NLY use custom or differently labelled lines)")
sr("sr.mreit.mortgage_assets", "Mortgage-related investments (agency/non-agency securities, loans)", {"reit_mortgage": "REQ"}, "face lines", "Y", "unverified; AFS debt securities, MortgageLoansOnRealEstate, custom captions at NLY/AGNC")
sr("sr.mreit.repo_to_equity", "Repurchase agreements to equity (face basis)", {"reit_mortgage": "COND"}, "sr.mreit.repurchase_agreements / stockholders_equity", "N", "derived", "Y", "must not be labelled 'economic leverage' (TBAs, non-recourse debt excluded)")
sr("sr.bdc.total_investment_income", "Total investment income", {"bdc": "REQ"}, "face line (already catalog row bdc_total_investment_income)", "Y", "GrossInvestmentIncomeOperating (78% of BDCs)", note="not new: existing catalog leaf; keep, gate by group")
sr("sr.bdc.net_investment_income", "Net investment income after tax (BDC)", {"bdc": "REQ"}, "face line (total investment income less expenses and excise/income tax)", "Y", "InvestmentIncomeOperatingAfterExpenseAndTax (2 of 2: ARCC 1,415.0M, BXSL 739,942K); NetInvestmentIncome is the PRE-tax line at both (ARCC 'NET INVESTMENT INCOME BEFORE INCOME TAXES' 1,458.0M); never share the insurer NetInvestmentIncome concept", note="perimeter (pre/post tax) is a Standardization Lead call")
sr("sr.bdc.net_assets", "Net assets", {"bdc": "REQ"}, "face line", "Y", "StockholdersEquity (2 of 2: ARCC 'Total stockholders' equity', BXSL 'Total net assets'); AssetsNet (doc 50 lead) is on the face of 0 of 2")
sr("sr.bdc.nav_per_share", "Net asset value per share", {"bdc": "REQ"}, "face or financial highlights", "Y", "NetAssetValuePerShare (2 of 2 on the balance sheet)")
sr("sr.bdc.investments_fair_value", "Investments at fair value", {"bdc": "REQ"}, "face line", "Y", "InvestmentOwnedAtFairValue (2 of 2)")
sr("sr.bdc.net_increase_net_assets_ops", "Net increase in net assets from operations", {"bdc": "REQ"}, "face line (the BDC earnings line)", "Y", "NetIncomeLoss at ARCC and BXSL (2 of 2); missing from doc 50")
sr("sr.bdc.nii_per_share", "Net investment income per share", {"bdc": "REQ"}, "sr.bdc.net_investment_income / weighted shares", "N", "derived")
sr("sr.bdc.price_to_nav", "Price to NAV", {"bdc": "REQ"}, "price / sr.bdc.nav_per_share", "N", "derived; price from vendor")
sr("sr.bdc.distributions_per_share", "Distributions per share", {"bdc": "REQ"}, "face or note", "N", "DistributionsPerShare... unverified")
sr("sr.am.management_advisory_fees", "Management and advisory fees", {"asset_manager": "COND"}, "face line", "Y", "NO common us-gaap tag on the face: 0 of 14 asset managers show InvestmentAdvisory*/AssetManagementFees*/ManagementFeeRevenue; revenue is one RevenueFromContractWithCustomerExcludingAssessedTax line (14 of 14) or company-specific fee captions: capture path = filing instance, not companyfacts")
sr("sr.am.performance_allocations", "Performance fees / allocations", {"asset_manager": "COND"}, "face line", "N", "unverified; can be negative at alternatives (BX, KKR, APO, CG, TPG, ARES)")
sr("sr.am.compensation_and_benefits", "Compensation and benefits", {"asset_manager": "COND", "broker_dealer": "COND", "insurance_broker": "COND", "exchange": "COND"}, "face line", "N", "LaborAndRelatedExpense (11 of 14 asset managers, caption Compensation and benefits)")
sr("sr.am.compensation_ratio", "Compensation ratio", {"asset_manager": "COND", "broker_dealer": "COND"}, "compensation / revenues (net revenues at broker-dealers)", "N", "derived")
sr("sr.bd.net_revenues", "Net revenues (after interest expense)", {"broker_dealer": "REP"}, "total revenues - interest expense", "Y", "RevenuesNetOfInterestExpense (7 of 11 broker-dealers; Revenues 8 of 11 as total net revenues)", "Y")
sr("sr.bd.commissions_trading", "Commissions, principal transactions and trading revenue", {"broker_dealer": "COND"}, "face lines", "N", "BrokerageCommissionsRevenue (4 of 11)")
sr("sr.bd.receivables_from_brokers_customers", "Receivables from and payables to brokers, dealers and customers", {"broker_dealer": "COND"}, "face lines", "Y", "ReceivablesFromBrokersDealersAndClearingOrganizations (7 of 11); PayablesToBrokerDealersAndClearingOrganizations and PayablesToCustomers (srt prefix, 6 of 11)")
sr("sr.crypto.digital_assets", "Digital assets held", {"crypto_digital": "REQ"}, "face line", "Y", "CryptoAssetFairValue / CryptoAssetFairValueNoncurrent / CryptoAssetFairValueCurrent (6 of 8 crypto-group filers on the face); my earlier lead CryptoAssetNoncurrent was not on any face")
sr("sr.crypto.digital_asset_gains_losses", "Gains/losses on digital assets", {"crypto_digital": "COND"}, "face line", "N", "CryptoAssetRealizedGainLossOperating / CryptoAssetRealizedAndUnrealizedGainLossOperating (5 of 8)")
sr("sr.util.utility_plant_net", "Utility plant, net", {"utility": "COND"}, "face line", "N", "PublicUtilitiesPropertyPlantAndEquipmentNet (12 of 32 utilities on the face; others use PropertyPlantAndEquipmentNet)")
sr("sr.util.regulatory_assets", "Regulatory assets", {"utility": "COND", "midstream": "COND"}, "face line", "Y", "RegulatoryAssetsCurrent / RegulatoryAssetsNoncurrent (22 of 32 utilities); plain RegulatoryAssets (doc 50 lead) is on the face of 0 of 32; also WMB/DTM (FERC-regulated pipelines)")
sr("sr.util.regulatory_liabilities", "Regulatory liabilities", {"utility": "COND", "midstream": "COND"}, "face line", "N", "RegulatoryLiabilityCurrent / RegulatoryLiabilityNoncurrent (22 of 32)")
sr("sr.mlp.partners_capital", "Partners' capital", {"midstream": "COND"}, "face line", "Y", "PartnersCapital / PartnersCapitalIncludingPortionAttributableToNoncontrollingInterest / LimitedPartnersCapitalAccount (6 of 14 midstream filers: the 6 partnerships); legal-form condition (EPD, ET, MPLX, PAA, WES, CQP are partnerships; KMI, WMB, OKE, TRGP, LNG, DTM, AM, VG are corporations). Partnerships print EPS per limited partnership unit (NetIncomeLossPerOutstandingLimitedPartnershipUnit*, 5 of 14): the EPS vocabulary must include it", note="doc 50 L1 marked REQ for the whole midstream group; wrong")
sr("sr.mlp.distributions_per_unit", "Distributions per unit", {"midstream": "COND"}, "note/face", "N", "DistributionMadeToLimitedPartnerDistributionsDeclaredPerUnit (declared) vs ...PaidPerUnit (paid): name the basis")
sr("sr.mlp.distribution_coverage_cfo", "Distributions paid to operating cash flow", {"midstream": "COND"}, "dividends_paid or distributions / cfo", "N", "derived; not DCF/FFO")
sr("sr.energy.oil_gas_properties_net", "Oil and gas properties, net", {"energy": "COND"}, "face line", "N", "OilAndGasPropertyFullCostMethodNet / ...SuccessfulEffortMethodNet; E&P only; none in doc 50")
# overlays: (overlay, id, label, code, note)
OVERLAYS = {
 "pre_revenue": dict(adds=[("sr.pre.cash_and_short_term_investments", "Cash and short-term investments", "REQ", "new concept; components cash + ShortTermInvestments/marketable securities current + non-current marketable securities (composition = calculated; AC)"),
                           ("sr.pre.accumulated_deficit", "Accumulated deficit", "REQ", "RetainedEarningsAccumulatedDeficit; new concept useful to all corporates"),
                           ("sr.pre.operating_cash_burn", "Operating cash burn (TTM)", "REQ", "-cfo_ttm; blank-with-reason when cfo > 0"),
                           ("sr.pre.runway_months", "Cash runway (months), our formula", "COND", "cash and short-term investments / monthly burn; only if burn > 0; formula disclosed as ours (role spec)"),
                           ("sr.pre.equity_proceeds", "Proceeds from issuance of equity", "COND", "ProceedsFromIssuanceOfCommonStock family; new concept")],
                    nit_revenue_denominated=True, trigger="overlay.pre_revenue@1: no revenue line on the latest 10-K statements OR TTM revenue below the $1M floor (floor awaiting Standardization Lead); SIC is a hint only; exits in the first FY with revenue at or above the floor"),
 "captive_finance": dict(adds=[("sr.cap.finance_receivables", "Finance receivables", "COND", "FinancingReceivable... / custom captions (PCAR, CAT Financial Products, DE, F Ford Credit, GM Financial)"),
                               ("sr.cap.financial_services_revenue", "Financial services / finance revenue", "COND", "face line or segment-labelled caption"),
                               ("sr.fin.provision_credit_losses", "Provision for credit losses", "COND", "shared sector row")],
                        trigger="finance-receivable and provision (or finance-revenue) lines on the face of an otherwise industrial filer; accountant: whether captive-finance receivables enter operating debt"),
 "lending_operations": dict(adds=[("sr.cap.finance_receivables", "Loans/finance receivables", "COND", "Block (loans held for investment), CarMax Auto Finance"),
                                  ("sr.fin.provision_credit_losses", "Provision for credit losses", "COND", "shared sector row")],
                           trigger="PROPOSED overlay (not in the plan's list): a non-captive or consumer-finance arm on the face of an otherwise corporate filer"),
 "insurance_operations": dict(adds=[("sr.ins.premiums_earned", "Premiums earned", "COND", ""), ("sr.ins.net_investment_income", "Net investment income (insurer)", "COND", ""),
                                    ("sr.ins.benefits_claims_incurred", "Benefits, losses and claims incurred", "COND", ""), ("sr.ins.future_policy_benefits", "Future policy benefits / reserves", "COND", "")],
                             trigger="premiums + benefits/claims + policy liabilities on the face of a non-insurer group (KKR Global Atlantic, APO Athene, AMP, ALLY insurance, FRHC)"),
 "managed_care_operations": dict(adds=[("sr.ins.premiums_earned", "Premium revenue", "COND", ""), ("sr.ins.benefits_claims_incurred", "Medical costs", "COND", ""), ("sr.mc.medical_care_ratio", "Medical care ratio", "COND", "")],
                                 trigger="premiums + health care costs + health care costs payable on the face of a retailer/PBM (CVS Aetna)"),
 "conglomerate_insurer": dict(adds=[("sr.cap.non_insurance_revenue", "Non-insurance operating revenues (segment-labelled)", "COND", "Markel Ventures, Loews non-CNA, Berkshire non-insurance")],
                              trigger="insurer with large non-insurance operating subsidiaries consolidated line by line (L, MKL, BRK-A candidate)"),
 "deposit_taking_operations": dict(adds=[("sr.bank.deposits_total", "Total deposits", "COND", ""), ("sr.fin.loans_net", "Loans, net", "COND", ""), ("sr.fin.provision_credit_losses", "Provision for credit losses", "COND", ""), ("sr.fin.net_interest_income", "Net interest income", "COND", "")],
                                   trigger="PROPOSED overlay: deposits + loans + provision + NII on the face of a broker-dealer/asset manager (GS, MS, SCHW, RJF, SF)"),
 "crypto_holdings": dict(adds=[("sr.crypto.digital_assets", "Digital assets held", "COND", "")], trigger="digital assets on the balance sheet of a non-crypto-group filer (XYZ Bitcoin investment)"),
 "royalty_land": dict(adds=[], nit=["cost_of_revenue_resolved", "gross_profit_resolved", "inventory", "research_and_development"], trigger="royalty/land revenue (RGLD, TPL, LB, VNOM); SIC 6792/6795 are hints"),
}

def build():
    ids = {s["id"] for s in S}
    for _n, _o in OVERLAYS.items():
        for (_i, *_r) in _o.get("adds", []):
            assert _i in ids or _i.startswith("sr.cap.") or _i.startswith("sr.pre."), _i
    rows = []
    cache = {}
    for dp in CATALOG:
        for g in GROUPS:
            code, basis = metric_rule(dp, g, cache)
            acct = "Y" if ("accountant" in basis or code == "REP") else "N"
            if (dp, g) in EM: acct = "Y"
            rows.append(dict(catalog_version=CATALOG_VERSION, template_version=TEMPLATE_VERSION, scope="group", group_or_overlay=g, row_type="base",
                             data_point=dp, kind=graph[dp]["kind"], rule=code,
                             state_if_condition_false={"COND": "not_presented", "REQ": "defect", "REP": "defect(definition_pending)", "NIT": "not_in_template"}[code],
                             needs_accountant=acct, group_defining="N", definition_status="definition_pending" if code == "REP" else "n/a",
                             basis=basis[:300], tag_leads=""))
    for s in S:
        for g, code in s["groups"].items():
            rows.append(dict(catalog_version=CATALOG_VERSION, template_version=TEMPLATE_VERSION, scope="group", group_or_overlay=g, row_type="sector",
                             data_point=s["id"], kind="sector_row", rule=code,
                             state_if_condition_false={"COND": "not_presented", "REQ": "defect", "REP": "defect(definition_pending)", "NIT": "not_in_template"}[code],
                             needs_accountant=s["acct"], group_defining=s["defining"], definition_status="definition_pending" if (code == "REP" or s["acct"] == "Y") else "n/a",
                             basis=(s["label"] + " | " + s["formula"] + (" | " + s["note"] if s["note"] else ""))[:300], tag_leads=s["tags"][:300]))
    # overlays: only deltas
    base_rules = {(r["data_point"], r["group_or_overlay"]): r["rule"] for r in rows if r["row_type"] == "base"}
    for name, o in OVERLAYS.items():
        for (idd, label, code, note) in o.get("adds", []):
            rows.append(dict(catalog_version=CATALOG_VERSION, template_version=TEMPLATE_VERSION, scope="overlay", group_or_overlay=name, row_type="sector_add",
                             data_point=idd, kind="sector_row", rule=code, state_if_condition_false="not_presented" if code == "COND" else "defect",
                             needs_accountant="Y" if "accountant" in note else "N", group_defining="N", definition_status="n/a", basis=(label + " | " + note)[:300], tag_leads=""))
        if o.get("nit_revenue_denominated"):
            rev_dep = []
            for dp in CATALOG:
                if dp in ("revenue_sanity_resolved",): rev_dep.append(dp)
                elif dp in graph and "revenue" in graph[dp]["ultimate_leaf_inputs"].split(";") and graph[dp]["kind"] == "metric": rev_dep.append(dp)
            rev_dep += ["cost_of_revenue_resolved", "gross_profit_resolved"]
            for dp in sorted(set(rev_dep)):
                rows.append(dict(catalog_version=CATALOG_VERSION, template_version=TEMPLATE_VERSION, scope="overlay", group_or_overlay=name, row_type="base_delta",
                                 data_point=dp, kind=graph[dp]["kind"], rule="COND", state_if_condition_false="undefined_by_math",
                                 needs_accountant="N", group_defining="N", definition_status="n/a",
                                 basis="while overlay.pre_revenue@1 holds the cell is undefined_by_math (state precedence: not_in_template > undefined_by_math via overlay > not_presented ...)", tag_leads=""))
        for dp in o.get("nit", []):
            rows.append(dict(catalog_version=CATALOG_VERSION, template_version=TEMPLATE_VERSION, scope="overlay", group_or_overlay=name, row_type="base_delta",
                             data_point=dp, kind=graph[dp]["kind"], rule="NIT", state_if_condition_false="not_in_template", needs_accountant="N", group_defining="N",
                             definition_status="n/a", basis="royalty/land revenue has no cost of sales or inventory line", tag_leads=""))
        rows.append(dict(catalog_version=CATALOG_VERSION, template_version=TEMPLATE_VERSION, scope="overlay", group_or_overlay=name, row_type="trigger",
                         data_point="(trigger)", kind="rule", rule="n/a", state_if_condition_false="", needs_accountant="N", group_defining="N", definition_status="n/a",
                         basis=o["trigger"][:300], tag_leads=""))
    return rows

if __name__ == "__main__":
    rows = build()
    cols = ["catalog_version", "template_version", "scope", "group_or_overlay", "row_type", "data_point", "kind", "rule", "state_if_condition_false",
            "needs_accountant", "group_defining", "definition_status", "basis", "tag_leads"]
    out = "/Users/vikash/wt-sector-groups/data-team/strategy/data/template_v1_draft.csv"
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
    c = collections.Counter((r["scope"], r["row_type"], r["rule"]) for r in rows)
    for k, v in sorted(c.items()): print(k, v)
    print(len(rows), "rows;", len(S), "sector rows;", len(CATALOG), "base lines")
