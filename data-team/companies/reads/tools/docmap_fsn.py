"""Document-first read, FSN-structured (ranks 701-800 lane, 2026-11-12).

Per company: the latest 10-K's face lines come from fsn.line (report = R page, line order = printed order, tag, printed
label, negating flag) with the filing's own XBRL values from fsn.value (undimensioned, FY0/FY1). Each mapped line is
confirmed on the printed R page fetched from sec.gov (same tag, value within rounding). Standard-tag values are compared
with SEC company-API facts in core.fact (same accession, same period; value_source sec_api); extension-tag values come
from the filing XBRL (value_source fsn_xbrl). Eras: the same rules run on every 10-K in fsn from FY2015 to the latest
(each run cites its accession and R page), so every data point is covered FY2015 -> latest or the gap is named.

Output: <TICKER>-docmap-<DATE>.{md,csv} in the format of data-team/companies/reads/ABT-docmap-2026-11-12.* and quirk
rows appended to the lane's feedback inbox.

Read-only. One DB connection (statement_timeout 60s). sec.gov only, at most 0.4 requests per second, disk cache.
Usage: python3 -I docmap_fsn.py <cohort.csv> <first_rank> <last_rank> <out_dir> <cache_dir> <inbox.md>
Env: DATABASE_URL, SEC_UA (User-Agent string).
"""

from __future__ import annotations

import csv
import datetime as dt
import html
import os
import re
import subprocess
import sys
import time
from decimal import Decimal

import json

import psycopg

DATE = "2026-11-12"
MIN_GAP = 2.5  # seconds between SEC requests (0.4 req/s)
_last = [0.0]
FETCHES = [0]
MISSED: list[str] = []


def get(url: str, cache: str) -> str:
    path = os.path.join(cache, re.sub(r"\W", "_", url)[-150:])
    if os.path.exists(path):
        return open(path, encoding="utf8").read()
    if os.environ.get("CACHE_ONLY"):
        MISSED.append(url)
        return ""
    for attempt in range(4):
        wait = MIN_GAP - (time.time() - _last[0])
        if wait > 0:
            time.sleep(wait)
        _last[0] = time.time()
        FETCHES[0] += 1
        res = subprocess.run(["curl", "-sS", "-m", "60", "-A", os.environ["SEC_UA"], "-w", "\n%{http_code}", url],
                             capture_output=True)
        body, _, code = res.stdout.decode("utf8", "ignore").rpartition("\n")
        if code == "200":
            open(path, "w", encoding="utf8").write(body)
            return body
        if code == "404":
            return ""
        time.sleep(10 * (attempt + 1))
    return ""


# ------------------------------------------------------------------ R page (printed values)

def cell_text(c: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", c))).strip()


def parse_r(page: str) -> dict:
    trs = re.findall(r"<tr.*?</tr>", page, re.S)
    if not trs:
        return {"scale": 1, "shares_scale": 1, "rows": []}
    title = cell_text(re.findall(r"<t[dh].*?</t[dh]>", trs[0], re.S)[0])
    low = title.lower()
    scale = 1_000_000 if "in millions" in low and "$" in low else (
        1_000 if "in thousands" in low and "$" in low else (1_000_000_000 if "in billions" in low and "$" in low else 1))
    sh = 1_000_000 if "shares in millions" in low else (1_000 if "shares in thousands" in low else 1)
    rows = []
    for tr in trs:
        tds = re.findall(r"<td([^>]*)>(.*?)</td>", tr, re.S)
        m = re.search(r"defref_([A-Za-z0-9\-]+)_([A-Za-z0-9]+)", tr)
        if not tds or not m:
            continue
        vals = []
        for attrs, v in tds[1:]:
            if 'class="th"' in attrs:
                continue
            t = cell_text(v).replace("$", "").replace(",", "").strip()
            neg = t.startswith("(") and t.endswith(")")
            t = t.strip("()").strip()
            try:
                vals.append(-Decimal(t) if neg else Decimal(t))
            except Exception:
                vals.append(None)
        rows.append({"prefix": m.group(1), "tag": m.group(2), "label": cell_text(tds[0][1]), "vals": vals})
    return {"scale": scale, "shares_scale": sh, "rows": rows}


# ------------------------------------------------------------------ data points

DPS = ["revenue", "cost_of_revenue", "gross_profit", "operating_expenses", "sga_expense", "research_and_development",
       "operating_income", "interest_expense", "interest_income", "other_income_expense_net", "income_before_tax",
       "income_tax_expense", "net_income", "basic_eps", "diluted_eps", "weighted_basic_shares",
       "weighted_diluted_shares", "dividends_per_share", "comprehensive_income", "cash_and_equivalents",
       "accounts_receivable", "inventory", "current_assets", "ppe_net", "goodwill", "total_assets", "accounts_payable",
       "current_liabilities", "total_liabilities", "total_debt", "stockholders_equity", "shares_outstanding", "cfo",
       "cash_flow_investing", "cash_flow_financing", "capex", "depreciation_and_amortization",
       "amortization_of_intangibles", "sbc", "dividends_paid", "share_buybacks", "cf_ar_change",
       "cf_inventory_change", "cf_ap_change", "cash_paid_for_interest", "cash_paid_for_income_taxes"]

# data point -> (statements searched, mapped tags in preference order, combined tags (one printed line spanning more))
SPEC: dict[str, tuple[list[str], list[str], list[str]]] = {
    "revenue": (["IS"], ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax",
                         "RevenueFromContractWithCustomerIncludingAssessedTax", "SalesRevenueNet", "SalesRevenueGoodsNet",
                         "SalesRevenueServicesNet", "RevenuesNetOfInterestExpense", "RegulatedAndUnregulatedOperatingRevenue",
                         "ElectricUtilityRevenue", "RegulatedOperatingRevenue", "OperatingLeasesIncomeStatementLeaseRevenue",
                         "RealEstateRevenueNet", "OilAndGasRevenue"], []),
    "cost_of_revenue": (["IS"], ["CostOfRevenue", "CostOfGoodsAndServicesSold", "CostOfGoodsSold",
                                 "CostOfGoodsAndServiceExcludingDepreciationDepletionAndAmortization",
                                 "CostOfGoodsSoldExcludingDepreciationDepletionAndAmortization", "CostOfServices"], []),
    "gross_profit": (["IS"], ["GrossProfit"], []),
    "sga_expense": (["IS"], ["SellingGeneralAndAdministrativeExpense"], []),
    "research_and_development": (["IS"], ["ResearchAndDevelopmentExpense",
                                          "ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost",
                                          "ResearchAndDevelopmentExpenseSoftwareExcludingAcquiredInProcessCost"], []),
    "operating_income": (["IS"], ["OperatingIncomeLoss"], []),
    "interest_expense": (["IS"], ["InterestExpense", "InterestExpenseNonoperating", "InterestExpenseOperating",
                                  "InterestExpenseDebt", "InterestExpenseBorrowings", "InterestExpenseRelatedParty"],
                         ["InterestIncomeExpenseNonoperatingNet", "InterestIncomeExpenseNet", "InterestAndOtherIncomeExpense",
                          "InterestExpenseNetOfInterestIncome"]),
    "interest_income": (["IS"], ["InvestmentIncomeInterest", "InterestIncomeOther", "InterestAndDividendIncomeOperating",
                                 "InvestmentIncomeInterestAndDividend", "InterestIncomeOperating", "InterestIncomeNonoperating"],
                        ["InterestAndOtherIncome", "InvestmentIncomeNonoperating"]),
    "other_income_expense_net": (["IS"], ["OtherNonoperatingIncomeExpense", "OtherNonoperatingIncome",
                                          "OtherNonoperatingExpense"], []),
    "income_before_tax": (["IS"], ["IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",
                                   "IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments",
                                   "IncomeLossFromContinuingOperationsBeforeIncomeTaxesDomestic",
                                   "IncomeLossBeforeIncomeTaxes"], []),
    "income_tax_expense": (["IS"], ["IncomeTaxExpenseBenefit", "IncomeTaxesPaidNet__never"], []),
    "net_income": (["IS"], ["NetIncomeLoss", "NetIncomeLossAvailableToCommonStockholdersBasic"], []),
    "basic_eps": (["IS"], ["EarningsPerShareBasic", "EarningsPerShareBasicAndDiluted",
                           "IncomeLossFromContinuingOperationsPerBasicShare"], []),
    "diluted_eps": (["IS"], ["EarningsPerShareDiluted", "EarningsPerShareBasicAndDiluted",
                             "IncomeLossFromContinuingOperationsPerDilutedShare"], []),
    "weighted_basic_shares": (["IS"], ["WeightedAverageNumberOfSharesOutstandingBasic",
                                       "WeightedAverageNumberOfShareOutstandingBasicAndDiluted"], []),
    "weighted_diluted_shares": (["IS"], ["WeightedAverageNumberOfDilutedSharesOutstanding",
                                         "WeightedAverageNumberOfShareOutstandingBasicAndDiluted"], []),
    "dividends_per_share": (["IS", "EQ", "EQP", "CI", "BSP"], ["CommonStockDividendsPerShareDeclared",
                                                               "CommonStockDividendsPerShareCashPaid"], []),
    "comprehensive_income": (["CI", "IS"], ["ComprehensiveIncomeNetOfTax"], []),
    "cash_and_equivalents": (["BS"], ["CashAndCashEquivalentsAtCarryingValue", "Cash"],
                             ["CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents", "CashCashEquivalentsAndFederalFundsSold",
                              "CashAndCashEquivalentsAtCarryingValueIncludingDiscontinuedOperations"]),
    "accounts_receivable": (["BS"], ["AccountsReceivableNetCurrent", "AccountsReceivableNet", "AccountsReceivableGrossCurrent"], []),
    "inventory": (["BS"], ["InventoryNet", "InventoryGross", "InventoryFinishedGoodsNetOfReserves"], []),
    "current_assets": (["BS"], ["AssetsCurrent"], []),
    "ppe_net": (["BS"], ["PropertyPlantAndEquipmentNet", "PublicUtilitiesPropertyPlantAndEquipmentNet"],
                ["PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization",
                 "PropertyPlantAndEquipmentCollectionsAndOperatingLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization"]),
    "goodwill": (["BS"], ["Goodwill"], ["IntangibleAssetsNetIncludingGoodwill"]),
    "total_assets": (["BS"], ["Assets"], []),
    "accounts_payable": (["BS"], ["AccountsPayableCurrent", "AccountsPayableTradeCurrent"],
                         ["AccountsPayableAndAccruedLiabilitiesCurrent", "AccountsPayableAndOtherAccruedLiabilitiesCurrent",
                          "AccountsPayableAndAccruedLiabilitiesCurrentAndNoncurrent"]),
    "current_liabilities": (["BS"], ["LiabilitiesCurrent"], []),
    "total_liabilities": (["BS"], ["Liabilities"], []),
    "stockholders_equity": (["BS"], ["StockholdersEquity"], []),
    "cfo": (["CF"], ["NetCashProvidedByUsedInOperatingActivities",
                     "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations"], []),
    "cash_flow_investing": (["CF"], ["NetCashProvidedByUsedInInvestingActivities",
                                     "NetCashProvidedByUsedInInvestingActivitiesContinuingOperations"], []),
    "cash_flow_financing": (["CF"], ["NetCashProvidedByUsedInFinancingActivities",
                                     "NetCashProvidedByUsedInFinancingActivitiesContinuingOperations"], []),
    "capex": (["CF"], ["PaymentsToAcquirePropertyPlantAndEquipment", "PaymentsToAcquireProductiveAssets",
                       "PaymentsForCapitalImprovements", "PaymentsToAcquireOilAndGasPropertyAndEquipment",
                       "PaymentsToAcquireOilAndGasProperty", "PaymentsToDevelopRealEstateAssets"], []),
    "depreciation_and_amortization": (["CF"], ["DepreciationDepletionAndAmortization", "DepreciationAndAmortization"],
                                      ["DepreciationAmortizationAndAccretionNet"]),
    "amortization_of_intangibles": (["CF", "IS"], ["AmortizationOfIntangibleAssets"], []),
    "sbc": (["CF"], ["ShareBasedCompensation", "AllocatedShareBasedCompensationExpense"], []),
    "dividends_paid": (["CF"], ["PaymentsOfDividendsCommonStock", "PaymentsOfDividends"], []),
    "share_buybacks": (["CF"], ["PaymentsForRepurchaseOfCommonStock"], ["PaymentsForRepurchaseOfEquity"]),
    "cf_ar_change": (["CF"], ["IncreaseDecreaseInAccountsReceivable"],
                     ["IncreaseDecreaseInAccountsAndOtherReceivables", "IncreaseDecreaseInReceivables",
                      "IncreaseDecreaseInAccountsAndNotesReceivable"]),
    "cf_inventory_change": (["CF"], ["IncreaseDecreaseInInventories", "IncreaseDecreaseInRetailRelatedInventories"], []),
    "cf_ap_change": (["CF"], ["IncreaseDecreaseInAccountsPayable", "IncreaseDecreaseInAccountsPayableTrade"],
                     ["IncreaseDecreaseInAccountsPayableAndAccruedLiabilities",
                      "IncreaseDecreaseInAccountsPayableAndOtherOperatingLiabilities"]),
    "cash_paid_for_interest": (["CF"], ["InterestPaidNet", "InterestPaid", "InterestPaidCapitalized__never"], []),
    "cash_paid_for_income_taxes": (["CF"], ["IncomeTaxesPaidNet", "IncomeTaxesPaid"], []),
}
# extension-tag lines are matched only by these printed-label patterns (a label never promotes a wider us-gaap tag)
CUSTOM_LABEL = {
    "revenue": r"^(total )?(net )?(operating )?(revenues?|sales)(, net)?$|^total (net )?revenues? and other income$",
    "cost_of_revenue": r"^(total )?cost of (revenues?|sales|goods sold|products sold)",
    "gross_profit": r"^gross (profit|margin)$",
    "sga_expense": r"^selling, general and administrative",
    "research_and_development": r"^research and development",
    "operating_income": r"^(total )?operating (income|profit|earnings)|^income from operations",
    "interest_expense": r"^interest expense$",
    "income_before_tax": r"before (provision for )?income tax",
    "net_income": r"^net (income|earnings)( \(loss\))?$",
    "cash_and_equivalents": r"^cash and cash equivalents$",
    "accounts_receivable": r"^(trade )?accounts receivable",
    "inventory": r"^inventor(y|ies)",
    "ppe_net": r"property,? plant,? and equipment,? net|^property and equipment,? net",
    "accounts_payable": r"^(trade )?accounts payable$",
    "depreciation_and_amortization": r"^depreciation(, depletion)? and amortization$",
    "sbc": r"^(stock|share|equity)[- ]based compensation",
    "capex": r"^(capital expenditures|purchases? of property|additions to property|purchases? of property, plant and equipment)",
    "dividends_paid": r"^(cash )?dividends paid( on common stock)?$",
    "share_buybacks": r"^(repurchases?|purchases?) of (common|treasury) (stock|shares)",
}
WIDER_AR = ["ReceivablesNetCurrent", "AccountsNotesAndLoansReceivableNetCurrent", "AccountsAndOtherReceivablesNetCurrent",
            "AccountsReceivableNetCurrentAndNoncurrent", "NotesAndAccountsReceivableNet"]
DEBT_TAGS = {"ShortTermBorrowings", "CommercialPaper", "DebtCurrent", "LongTermDebtCurrent", "LongTermDebtNoncurrent",
             "LongTermDebt", "LongTermDebtAndCapitalLeaseObligations", "LongTermDebtAndCapitalLeaseObligationsCurrent",
             "OtherLongTermDebtNoncurrent", "OtherLongTermDebtCurrent", "LinesOfCreditCurrent", "LongTermLineOfCredit",
             "LineOfCredit", "SeniorNotes", "SeniorNotesCurrent", "SeniorLongTermNotes", "ConvertibleNotesPayable",
             "ConvertibleNotesPayableCurrent", "ConvertibleDebtNoncurrent", "ConvertibleDebtCurrent", "ConvertibleDebt",
             "NotesPayable", "NotesPayableCurrent", "LongTermNotesPayable", "OtherShortTermBorrowings",
             "AdvancesFromFederalHomeLoanBanks", "FederalHomeLoanBankAdvances", "SubordinatedDebt", "OtherBorrowings",
             "SecuredDebt", "UnsecuredDebt", "SecuredDebtOther", "LongTermDebtFairValue__never", "DebtInstrumentCarryingAmount",
             "FinanceLeaseLiabilityCurrent", "FinanceLeaseLiabilityNoncurrent", "FinanceLeaseLiability",
             "CapitalLeaseObligationsCurrent", "CapitalLeaseObligationsNoncurrent", "CapitalLeaseObligations",
             "DebtLongtermAndShorttermCombinedAmount", "LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities",
             "JuniorSubordinatedNotes", "FederalHomeLoanBankAdvancesLongTerm", "FederalHomeLoanBankAdvancesShortTerm", "JuniorSubordinatedDebentureOwedToUnconsolidatedSubsidiaryTrust", "AdvancesFromFederalHomeLoanBanksShortTerm__", "FederalHomeLoanBankBorrowings", "SubordinatedBorrowing", "ShortTermDebtFairValue__never", "OtherLongTermDebt", "NotesPayableRelatedPartiesClassifiedCurrent", "NotesPayableRelatedPartiesNoncurrent", "LongTermDebtNoncurrentExcludingCurrentMaturities__", "SubordinatedLongTermDebt", "LongTermFederalHomeLoanBankAdvancesNoncurrent",
             "ShortTermBankLoansAndNotesPayable", "BankOverdrafts__never", "LoansPayable", "LoansPayableCurrent",
             "MortgageLoansOnRealEstate__never", "SecuredLongTermDebt", "UnsecuredLongTermDebt", "NotesPayableToBank",
             "TermLoan__never", "SeniorSubordinatedNotes", "OtherNotesPayable", "MediumTermNotes",
             "LongTermDebtAndFinanceLeaseLiabilityNoncurrent__never"}
DEBT_LABEL = r"\b(debt|borrowings?|notes payable|senior notes|credit facilit(y|ies)|term loans?|convertible notes|finance lease (liabilit|obligation)|mortgages? payable|mortgage notes|commercial paper|debentures)\b"
DEBT_LABEL_NOT = r"operating lease|deferred|interest payable|accrued|financing obligation"
COS_TYPE_TAGS = r"^(CostOf|CostsOf|FuelCosts|Fuel|.*PurchasedPower|.*CostOfPurchasedPower|ProductionCosts|.*LeaseOperatingExpense|ResultsOfOperationsExpenseOther__|DirectCostsOfLeasedAndRentedPropertyOrEquipment|CostDirect|.*CostOfNaturalGasPurchases|UtilitiesOperatingExpensePurchasedPower|ResultsOfOperationsProductionOrLiftingCosts|OilAndGasProductionExpense|ProductionTaxExpense__)"
COS_TYPE_LABEL = r"\b(cost of|costs of|fuel|purchased power|purchased gas|production (expense|cost|costs)|lease operating|property operating|rental operating|cost of sales|operating costs of)\b"


def norm(t: str) -> str:
    return t.split(":")[-1]


def qn(row: dict) -> str:
    return f"{row['prefix']}:{row['tag']}"


def fmt(x) -> str:
    if x is None:
        return ""
    x = Decimal(x)
    if x == x.to_integral_value():
        return str(int(x))
    return format(x.normalize(), "f")


# ------------------------------------------------------------------ DB

SQL_FILINGS = """select f.id, f.accession, f.period, f.fy, f.filed, f.company_id
from fsn.filing f where f.cik = %s and f.form = '10-K' and not f.amendment
  and exists (select 1 from fsn.line l where l.filing_id = f.id) order by f.period"""
SQL_LINES = """select l.filing_id, l.report, l.line, l.stmt, l.inpth, t.tag, t.custom, t.abstract, l.plabel, l.negating
from fsn.line l join fsn.tag t on t.id = l.tag_id where l.filing_id = any(%s) and l.stmt in ('IS','BS','CF','CI','EQ')
order by l.filing_id, l.report, l.line"""
SQL_VALUES = """select v.filing_id, t.tag, v.ddate, v.qtrs, v.value from fsn.value v join fsn.tag t on t.id = v.tag_id
where v.filing_id = any(%s) and v.dim_id = 0 and v.iprx = 0 and v.coreg = '' and v.qtrs in (0, 4)"""
SQL_REPORTS = """select filing_id, report, rfile, shortname from fsn.report where filing_id = any(%s)"""
SQL_FACTS = """select fi.accession_number, c.taxonomy, c.tag, p.start_date, p.end_date, f.value
from core.fact f join core.filing fi on fi.id = f.filing_id join core.concept c on c.id = f.concept_id
join core.period p on p.id = f.period_id
where f.company_id = %s and fi.accession_number = any(%s) and c.taxonomy in ('us-gaap', 'dei', 'srt')"""


def month_end(d: dt.date) -> dt.date:
    nxt = (d.replace(day=28) + dt.timedelta(days=4))
    return nxt - dt.timedelta(days=nxt.day)


def prior_year(d: dt.date) -> dt.date:
    return month_end(d.replace(year=d.year - 1, day=1))


class Company:
    def __init__(self, conn, row: dict, cache: str):
        self.row, self.cache = row, cache
        self.cik = row["cik"].zfill(10)
        self.tic = row["ticker"]
        cur = conn.cursor()
        cur.execute(SQL_FILINGS, (self.cik,))
        self.filings = [dict(zip(["id", "accn", "period", "fy", "filed", "company_id"], r)) for r in cur.fetchall()]
        if not self.filings:
            return
        latest = self.filings[-1]
        # FY2015 onward (fiscal year focus 2015 or a period ending in/after 2015)
        keep = [f for f in self.filings if (f["fy"] or f["period"].year) >= 2015 or f["period"] >= dt.date(2015, 6, 1)]
        self.era = keep if keep else [latest]
        ids = [f["id"] for f in self.era]
        cur.execute(SQL_LINES, (ids,))
        self.lines: dict[int, list[dict]] = {}
        for r in cur.fetchall():
            d = dict(zip(["fid", "report", "line", "stmt", "inpth", "tag", "custom", "abstract", "plabel", "negating"], r))
            self.lines.setdefault(d["fid"], []).append(d)
        cur.execute(SQL_VALUES, (ids,))
        self.values: dict[tuple, Decimal] = {}
        for fid, tag, ddate, qtrs, value in cur.fetchall():
            if value is not None:
                self.values[(fid, tag, ddate, qtrs)] = value
        cur.execute(SQL_REPORTS, (ids,))
        self.reports = {(r[0], r[1]): (r[2], r[3]) for r in cur.fetchall()}
        cid = int(row["company_id"])
        cur.execute(SQL_FACTS, (cid, [f["accn"] for f in self.era]))
        self.facts: dict[tuple, list] = {}
        for accn, tax, tag, s, e, v in cur.fetchall():
            self.facts.setdefault((accn, tag), []).append((s, e, v))

    # rows of one filing, grouped into statements
    def statements(self, f: dict) -> dict[str, dict]:
        lines = self.lines.get(f["id"], [])
        fy0, fy1 = f["period"], prior_year(f["period"])
        by_rep: dict[int, list[dict]] = {}
        for l in lines:
            by_rep.setdefault(l["report"], []).append(l)
        cand: dict[str, list[tuple[int, int]]] = {}
        for rep, ls in by_rep.items():
            st = ls[0]["stmt"]
            key = st + ("P" if ls[0]["inpth"] else "")
            cand.setdefault(key, []).append((rep, len(ls)))
        out = {}
        for key, reps in cand.items():
            def score(rp):
                tags = {l["tag"] for l in by_rep[rp[0]]}
                bonus = 1000 if key == "IS" and tags & {"NetIncomeLoss", "EarningsPerShareBasic", "ProfitLoss"} else 0
                bonus += 1000 if key == "BS" and "Assets" in tags else 0
                bonus += 1000 if key == "CF" and tags & set(SPEC["cfo"][1]) else 0
                return bonus + rp[1]
            rep = sorted(reps, key=score, reverse=True)[0][0]
            q = 0 if key in ("BS", "BSP") else 4
            rows = []
            for l in by_rep[rep]:
                v0 = self.values.get((f["id"], l["tag"], fy0, q))
                v1 = self.values.get((f["id"], l["tag"], fy1, q))
                if key in ("EQ", "EQP") and v0 is None:
                    v0 = self.values.get((f["id"], l["tag"], fy0, 4)) or self.values.get((f["id"], l["tag"], fy0, 0))
                    v1 = self.values.get((f["id"], l["tag"], fy1, 4)) or self.values.get((f["id"], l["tag"], fy1, 0))
                if key in ("BSP",) and v0 is None:
                    continue
                if v0 is None and v1 is None:
                    continue
                sgn = -1 if l["negating"] else 1
                rows.append(dict(l, v0=v0, v1=v1, p0=None if v0 is None else sgn * v0, p1=None if v1 is None else sgn * v1))
            rf = self.reports.get((f["id"], rep), ("H", ""))
            out[key] = {"report": rep, "r": f"R{rep}.{'xml' if rf[0] == 'X' else 'htm'}", "name": rf[1] or "", "rows": rows}
        if "IS" not in out and "CI" in out:
            out["IS"] = out["CI"]
        return out

    def api(self, accn: str, tag: str, end: dt.date, duration: bool):
        for s, e, v in self.facts.get((accn, tag), []):
            if abs((e - end).days) > 10:
                continue
            if duration and (s == e or not 340 <= (e - s).days <= 390):
                continue
            if not duration and s != e:
                continue
            return v
        return None


# ------------------------------------------------------------------ matching rules

def find(rows, tags, combined=()):
    for t in tags:
        for r in rows:
            if r["tag"] == t and not r["custom"]:
                return r, "mapped"
    for t in combined:
        for r in rows:
            if r["tag"] == t and not r["custom"]:
                return r, "combined"
    return None, ""


def find_custom(rows, dp):
    rx = CUSTOM_LABEL.get(dp)
    if not rx:
        return None
    for r in rows:
        if r["custom"] and re.search(rx, (r["plabel"] or "").strip(), re.I):
            return r
    return None


def template_of(st: dict) -> str:
    tags = {r["tag"] for k in ("IS", "BS") for r in st.get(k, {}).get("rows", [])}
    if "NoninterestExpense" in tags and tags & {"InterestIncomeExpenseNet", "InterestAndDividendIncomeOperating",
                                                 "InterestIncomeExpenseAfterProvisionForLoanLoss"}:
        return "bank"
    if tags & {"PremiumsEarnedNet", "BenefitsLossesAndExpenses", "PolicyholderBenefitsAndClaimsIncurredNet",
               "IncurredClaimsPropertyCasualtyAndLiability", "PremiumsEarnedNetPropertyAndCasualty", "LiabilityForFuturePolicyBenefits",
               "LiabilityForClaimsAndClaimsAdjustmentExpense"}:
        return "insurer"
    return "general"


def opex_rule(rows: list[dict]) -> tuple[list[dict] | None, str, str]:
    """Dhairya ruling 2026-11-12: operating expenses never include cost of revenue."""
    idx = lambda pred: next((i for i, r in enumerate(rows) if pred(r)), None)
    i_rev = idx(lambda r: r["tag"] in SPEC["revenue"][1] and not r["custom"])
    i_gp = idx(lambda r: r["tag"] == "GrossProfit")
    i_oi = idx(lambda r: r["tag"] == "OperatingIncomeLoss")
    i_cogs = idx(lambda r: r["tag"] in SPEC["cost_of_revenue"][1])
    i_tot = idx(lambda r: r["tag"] in ("OperatingExpenses", "CostsAndExpenses", "OperatingCostsAndExpenses", "NoninterestExpense",
                                       "BenefitsLossesAndExpenses"))
    if i_tot is None:
        i_tot = idx(lambda r: re.search(r"^total (operating )?(costs and )?(operating )?expenses?$|^total (costs|expenses)$",
                                        (r["plabel"] or "").strip(), re.I) is not None)
    v = lambda i: rows[i]["p0"]
    if i_tot is not None:
        tot = rows[i_tot]
        if tot["tag"] == "NoninterestExpense":
            return [tot], "mapped", "bank: printed 'total noninterest expense' (no cost of revenue on a bank IS)"
        start = (i_rev + 1) if i_rev is not None and i_rev < i_tot else 0
        inside = [r for r in rows[start:i_tot] if r["p0"] is not None]
        cos_items = [r for r in inside if re.search(COS_TYPE_TAGS, r["tag"]) or re.search(COS_TYPE_LABEL, r["plabel"] or "", re.I)]
        if tot["tag"] == "BenefitsLossesAndExpenses":
            return [tot], "combined", ("insurer: printed total benefits, losses and expenses includes losses and benefits "
                                       "(the insurer's cost of revenue): combined, never opex")
        if i_gp is not None and i_gp < i_tot and i_oi is not None and None not in (v(i_gp), v(i_oi), v(i_tot)):
            if abs(abs(v(i_tot)) - abs(v(i_gp) - v(i_oi))) < 1:
                return [tot], "mapped", "printed total opex line below gross profit; ties to GP - OI (excludes cost of revenue)"
        if i_cogs is not None and i_cogs < i_tot and (i_gp is None or i_gp > i_tot):
            return [tot], "combined", f"printed total '{tot['plabel']}' includes cost of revenue ('{rows[i_cogs]['plabel']}'): combined, never opex"
        if cos_items and (i_gp is None or i_gp > i_tot):
            return [tot], "combined", (f"printed total '{tot['plabel']}' contains cost-of-sales-type line(s) "
                                       f"({'; '.join(repr(r['plabel']) for r in cos_items[:3])}): combined, never opex")
        if i_cogs is not None and i_cogs > i_tot:
            pass
        if i_cogs is None and not cos_items:
            if i_gp is None or i_gp < i_tot:
                return [tot], "mapped", "printed total opex line; no cost-of-revenue or cost-of-sales-type line in it"
    # component sum: every face line between GP (or the cost-of-revenue line) and OI, tied to GP - OI
    anchor = i_gp if i_gp is not None else (i_cogs if i_cogs is not None and i_rev is not None and i_rev < i_cogs else None)
    if anchor is not None and i_oi is not None and anchor < i_oi:
        parts = [r for r in rows[anchor + 1:i_oi] if r["p0"] is not None]
        if i_gp is not None:
            target = v(i_gp) - v(i_oi) if None not in (v(i_gp), v(i_oi)) else None
        else:
            target = (v(i_rev) - abs(v(i_cogs)) - v(i_oi)) if None not in (v(i_rev), v(i_cogs), v(i_oi)) else None
        if parts and target is not None:
            total = sum(abs(r["p0"]) if r is parts[0] else r["p0"] for r in parts) if False else sum(r["p0"] for r in parts)
            if abs(abs(total) - abs(target)) < 1:
                if any(re.search(COS_TYPE_TAGS, r["tag"]) for r in parts):
                    return None, "", "lines between gross profit / cost of revenue and operating income include a cost-of-sales-type line"
                if len(parts) == 1:
                    return parts, "mapped", "single face line between gross profit / cost of revenue and operating income; ties to GP - OI"
                return parts, "component sum", ("every face line between " + ("gross profit" if i_gp is not None else "cost of revenue")
                                                + " and operating income; sum ties exactly to GP - OI")
            return None, "", f"face lines between gross profit / cost of revenue and operating income sum to {fmt(total)}, not GP - OI {fmt(target)}"
    if i_tot is not None:
        return None, "", f"total '{rows[i_tot]['plabel']}' perimeter could not be tied (no gross profit / operating income pair)"
    return None, "", "no total opex line and no gross profit / operating income pair to tie components"


def decide(dp: str, st: dict, tmpl: str) -> dict:
    """One data point on one filing -> {status, parts:[rows], stmt key, note}."""
    stmts, tags, comb = SPEC.get(dp, ([], [], []))
    res = {"status": "not_presented", "parts": [], "key": (stmts or ["IS"])[0], "note": ""}
    OUT_BANK = {"cost_of_revenue", "gross_profit", "operating_income", "current_assets", "current_liabilities", "inventory",
                "accounts_receivable", "research_and_development", "accounts_payable"}
    OUT_INS = {"cost_of_revenue", "gross_profit", "operating_income", "current_assets", "current_liabilities", "inventory",
               "research_and_development"}
    if dp == "operating_expenses":
        rows = st.get("IS", {}).get("rows", [])
        parts, status, note = opex_rule(rows)
        res.update(key="IS", note=note)
        if parts:
            res.update(status=status, parts=parts)
        return res
    if dp == "total_debt":
        rows = st.get("BS", {}).get("rows", [])
        parts = []
        for r in rows:
            lab = r["plabel"] or ""
            if r["v0"] is None:
                continue
            if (not r["custom"] and r["tag"] in DEBT_TAGS) or (r["custom"] and re.search(DEBT_LABEL, lab, re.I)
                                                                and not re.search(DEBT_LABEL_NOT, lab, re.I)
                                                                and not re.search(r"^total", lab, re.I)):
                parts.append(r)
        # drop a total that equals the sum of other picked lines
        if len(parts) > 2:
            for p in list(parts):
                others = [q for q in parts if q is not p]
                if abs(sum(q["v0"] for q in others) - p["v0"]) < 1:
                    parts = [p]
                    break
        res.update(key="BS")
        if parts:
            res.update(status="mapped" if len(parts) == 1 else "component sum", parts=parts,
                       note="BS debt lines: " + " + ".join(repr(p["plabel"]) for p in parts)
                       + "; operating leases excluded; total_debt is the one instant sum allowed")
        else:
            res.update(note="no debt line on the balance-sheet face")
        return res
    if dp == "shares_outstanding":
        for key in ("BS", "BSP"):
            rows = [r for r in st.get(key, {}).get("rows", []) if r["tag"] == "CommonStockSharesOutstanding" and r["v0"] is not None]
            if rows:
                res.update(status="mapped" if len(rows) == 1 else "component sum", parts=rows[:1] if len(rows) == 1 else rows, key=key,
                           note="CommonStockSharesOutstanding at the balance-sheet date" + ("" if len(rows) == 1 else " (class rows summed)"))
                return res
        res.update(key="BS", note="no CommonStockSharesOutstanding count at the balance-sheet date on the BS face or parenthetical; dei cover count not used (ruling 2026-11-12)")
        return res
    for key in stmts:
        rows = st.get(key, {}).get("rows", [])
        if not rows:
            continue
        r, status = find(rows, tags, comb)
        if r is None:
            # special shapes
            if dp == "sga_expense":
                s = [x for x in rows if x["tag"] in ("SellingAndMarketingExpense", "SellingExpense", "MarketingExpense")]
                g = [x for x in rows if x["tag"] == "GeneralAndAdministrativeExpense"]
                if s and g and s[0]["p0"] is not None and g[0]["p0"] is not None:
                    res.update(status="component sum", parts=[s[0], g[0]], key=key,
                               note="no SG&A line; selling/marketing and G&A printed separately")
                    return res
                if g and not s:
                    res.update(status="mapped", parts=[g[0]], key=key, note="lone G&A line (no selling line on the face)")
                    return res
            if dp == "cost_of_revenue":
                c = [x for x in rows if not x["custom"] and re.match(r"^(CostOfGoods|CostOfServices|CostOfProducts|CostOf)", x["tag"])
                     and x["p0"] is not None]
                if len(c) >= 2 and len({x["tag"] for x in c}) == len(c):
                    res.update(status="component sum", parts=c, key=key, note="cost of revenue printed in parts with no total line")
                    return res
            if dp == "depreciation_and_amortization":
                c = [x for x in rows if x["tag"] in ("Depreciation", "AmortizationOfIntangibleAssets", "DepreciationAndAmortization",
                                                      "DepreciationDepletionAndAmortization", "Depletion", "AmortizationOfDeferredCharges__")
                     and x["p0"] is not None]
                if len(c) >= 2:
                    res.update(status="component sum", parts=c, key=key, note="D&A printed as separate CF lines")
                    return res
                if len(c) == 1 and c[0]["tag"] == "Depreciation":
                    res.update(status="mapped", parts=c, key=key, note="CF prints depreciation only (no amortization line)")
                    return res
            if dp == "accounts_receivable":
                recv = [x for x in rows if re.search(r"receivable", x["plabel"] or "", re.I) and x["v0"] is not None
                        and not re.search(r"noncurrent|long-term", x["plabel"] or "", re.I)]
                w = [x for x in recv if x["tag"] in WIDER_AR]
                if w and len(recv) == 1:
                    res.update(status="mapped", parts=w, key=key,
                               note=f"wider tag {w[0]['tag']} is the single receivables line on the BS face: mapped per ruling 2026-11-12")
                    return res
                if w:
                    res.update(status="combined", parts=w[:1], key=key,
                               note=f"wider receivables tag {w[0]['tag']} is not the single receivables line on the face ({len(recv)} lines): never AR")
                    return res
            if dp == "net_income":
                p = [x for x in rows if x["tag"] == "ProfitLoss"]
                nci = [x for x in rows if x["tag"] == "NetIncomeLossAttributableToNoncontrollingInterest"]
                if p and not nci:
                    res.update(status="mapped", parts=p, key=key, note="only ProfitLoss printed; no noncontrolling-interest line on the face")
                    return res
            if dp == "cash_and_equivalents":
                p = [x for x in rows if x["tag"] == "CashAndDueFromBanks"]
                if p:
                    res.update(status="mapped", parts=p, key=key, note="bank: 'cash and due from banks' is the only cash line (no cash-and-equivalents total)")
                    return res
            if dp == "comprehensive_income":
                p = [x for x in rows if x["tag"] == "ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest"]
                nci = [x for x in rows if "NoncontrollingInterest" in x["tag"] and x["tag"] != p[0]["tag"]] if p else []
                if p and not nci:
                    res.update(status="mapped", parts=p, key=key, note="only the comprehensive-income-including-NCI total printed; no NCI line on the face")
                    return res
            if dp == "stockholders_equity":
                p = [x for x in rows if x["tag"] == "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"]
                nci = [x for x in rows if x["tag"] == "MinorityInterest"]
                if p and not nci:
                    res.update(status="mapped", parts=p, key=key, note="only the equity-including-NCI total printed; no NCI line on the face")
                    return res
            if dp == "revenue" and tmpl == "bank":
                pass
            c = find_custom(rows, dp)
            if c is not None and c["v0"] is not None:
                res.update(status="mapped", parts=[c], key=key, note=f"extension tag on the face line '{c['plabel']}'")
                return res
            continue
        if dp == "revenue" and tmpl in ("bank", "insurer") and r["tag"] not in ("Revenues", "RevenuesNetOfInterestExpense"):
            res.update(note=f"{tmpl} IS: '{r['plabel']}' ({r['tag']}) is one revenue component, not total revenue")
            break
        if dp == "interest_income" and tmpl != "bank" and r["tag"] == "InterestAndDividendIncomeOperating":
            pass
        if dp == "other_income_expense_net" and r is not None:
            pass
        res.update(status=status, parts=[r], key=key)
        lab = (r["plabel"] or "").lower()
        if dp == "interest_expense" and status == "mapped" and re.search(r"\bnet\b", lab) and "capitaliz" not in lab:
            res.update(status="combined", note=f"'{r['plabel']}' is a net interest line: interest_expense is the gross charge only (ruling 2026-11-12): combined")
            return res
        if dp == "depreciation_and_amortization" and status == "mapped" and "accretion" in lab:
            res.update(status="combined", note=f"'{r['plabel']}' includes accretion: combined (ruling 2026-11-12)")
            return res
        if dp == "cash_and_equivalents" and status == "combined":
            pass
        if status == "combined" and dp == "interest_expense":
            res["note"] = f"'{r['plabel']}' ({r['tag']}) is a net interest line: interest_expense is the gross charge only (ruling 2026-11-12): combined"
            return res
        if status == "combined" and dp == "depreciation_and_amortization":
            res["note"] = f"'{r['plabel']}' ({r['tag']}) includes accretion: combined (ruling 2026-11-12)"
            return res
        if status == "combined":
            res["note"] = f"'{r['plabel']}' ({r['tag']}) spans more than {dp}: combined, never mapped as one concept"
        return res
    if dp == "other_income_expense_net":
        rows = st.get("IS", {}).get("rows", [])
        w = [x for x in rows if x["tag"] == "NonoperatingIncomeExpense"]
        if w:
            res.update(status="combined", parts=w[:1], key="IS",
                       note=f"'{w[0]['plabel']}' is NonoperatingIncomeExpense (wider than other income): a label never promotes a wider tag")
            return res
    if tmpl == "bank" and dp in OUT_BANK:
        res.update(status="OUT", note="bank template: not a bank statement line")
    elif tmpl == "insurer" and dp in OUT_INS:
        res.update(status="OUT", note="insurer template: not an insurer statement line")
    elif not res["note"]:
        res["note"] = f"no {dp.replace('_', ' ')} line on the face"
    return res


# ------------------------------------------------------------------ whole-filing (notes) check

NOTE_SKIP = {"operating_expenses", "total_debt"}


def note_tags(dp: str, tmpl: str) -> list[str]:
    if dp == "shares_outstanding":
        return ["CommonStockSharesOutstanding"]
    if dp == "revenue" and tmpl in ("bank", "insurer"):
        return ["Revenues", "RevenuesNetOfInterestExpense"]
    return [t for t in SPEC.get(dp, ([], [], []))[1] if not t.endswith("__never")]


def is_instant(dp: str) -> bool:
    return dp in ("cash_and_equivalents", "accounts_receivable", "inventory", "current_assets", "ppe_net", "goodwill",
                  "total_assets", "accounts_payable", "current_liabilities", "total_liabilities", "stockholders_equity",
                  "shares_outstanding", "total_debt")


def xbrl_hit(co, f: dict, dp: str, tmpl: str):
    """First tag of the data point with an undimensioned FY0 fact in the filing's XBRL (fsn.value)."""
    q = 0 if is_instant(dp) else 4
    for t in note_tags(dp, tmpl):
        v0 = co.values.get((f["id"], t, f["period"], q))
        if v0 is not None:
            return t, v0, co.values.get((f["id"], t, prior_year(f["period"]), q))
    return None


def metalinks(co, f: dict) -> dict:
    base = f"https://www.sec.gov/Archives/edgar/data/{int(co.cik)}/{f['accn'].replace('-', '')}/"
    txt = get(base + "MetaLinks.json", co.cache)
    try:
        d = json.loads(txt)
        return list(d["instance"].values())[0]
    except Exception:
        return {}


def note_pages(ml: dict, tag: str) -> list[tuple[str, str]]:
    """R pages (file, short name) whose presentation carries the tag: detail pages first."""
    t = (ml.get("tag") or {}).get(f"us-gaap_{tag}") or {}
    roles = set(t.get("presentation") or [])
    reps = [(k, v) for k, v in (ml.get("report") or {}).items() if v.get("role") in roles]
    reps.sort(key=lambda kv: (0 if "detail" in (kv[1].get("shortName") or "").lower() else 1,
                              0 if kv[1].get("groupType") == "disclosure" else 1,
                              int(kv[0][1:]) if kv[0][1:].isdigit() else 999))
    return [(f"{k}.htm", v.get("shortName") or "") for k, v in reps]


# ------------------------------------------------------------------ one company

def printed_for(page: dict, r: dict, which: int, dp: str):
    """Printed value on the R page for an FSN line: same tag, value equal to the XBRL value within rounding."""
    if not page or not page["rows"]:
        return None
    target = r["v0"] if which == 0 else r["v1"]
    if target is None:
        return None
    if dp in ("basic_eps", "diluted_eps", "dividends_per_share"):
        sc = 1
    elif dp in ("weighted_basic_shares", "weighted_diluted_shares", "shares_outstanding"):
        sc = page["shares_scale"]
    else:
        sc = page["scale"]
    best = None
    for pr in page["rows"]:
        if pr["tag"] != r["tag"]:
            continue
        for x in pr["vals"]:
            if x is None:
                continue
            if abs(abs(x * sc) - abs(target)) <= max(Decimal(sc) / 2, Decimal("0.005")):
                return x * sc
            if best is None:
                best = x * sc
    return None


def read_company(conn, row: dict, cache: str):
    co = Company(conn, row, cache)
    meta = {"ticker": co.tic, "cik": co.cik, "name": row["name"], "quirks": [], "fetches": 0}
    if not co.filings:
        meta["error"] = "no 10-K in fsn.filing"
        return [], meta
    latest = co.filings[-1]
    meta.update(accn=latest["accn"], filed=str(latest["filed"]), period=latest["period"])
    st = co.statements(latest)
    tmpl = template_of(st)
    meta["template"] = tmpl
    base = f"https://www.sec.gov/Archives/edgar/data/{int(co.cik)}/{latest['accn'].replace('-', '')}/"
    pages: dict[str, dict] = {}
    out = []
    decisions = {dp: decide(dp, st, tmpl) for dp in DPS}
    ml = metalinks(co, latest)
    meta["metalinks"] = bool(ml)
    for dp in DPS:
        d = decisions[dp]
        if dp in NOTE_SKIP or d["status"] == "OUT":
            continue
        if not (d["status"] == "not_presented" or (dp == "interest_expense" and d["status"] == "combined")):
            continue
        hit = xbrl_hit(co, latest, dp, tmpl)
        faces = ", ".join(sorted({v["r"] for k, v in st.items() if k in ("IS", "BS", "CF", "CI", "EQ", "BSP", "EQP")}))
        tags_checked = ", ".join(note_tags(dp, tmpl))
        if hit is None:
            in_ml = [t for t in note_tags(dp, tmpl) if f"us-gaap_{t}" in (ml.get("tag") or {})]
            if d["status"] == "not_presented":
                d["note"] = ((d["note"] + "; ") if d["note"] else "") + (
                    f"whole-filing check: no undimensioned FY0 fact for {tags_checked} in the filing XBRL (fsn.value of this accession); "
                    + (f"MetaLinks lists {', '.join(in_ml)} only dimensioned or for other periods" if in_ml else
                       "MetaLinks.json lists none of these tags on any R page") + f"; faces read {faces}")
            continue
        tag, v0, v1 = hit
        pages_ = note_pages(ml, tag)
        chosen = None
        for rf, nm in pages_[:3]:
            pg = parse_r(get(f"https://www.sec.gov/Archives/edgar/data/{int(co.cik)}/{latest['accn'].replace('-', '')}/{rf}", cache))
            if printed_for(pg, {"tag": tag, "v0": v0, "v1": v1}, 0, dp) is not None:
                chosen = (rf, nm, pg)
                break
        prev = d["note"]
        key = f"NOTE:{chosen[0] if chosen else (pages_[0][0] if pages_ else '')}"
        row_ = {"tag": tag, "custom": False, "plabel": "", "v0": v0, "v1": v1, "negating": False, "p0": v0, "p1": v1}
        if chosen:
            row_["plabel"] = next((pr["label"] for pr in chosen[2]["rows"] if pr["tag"] == tag), "")
            pages[key] = chosen[2]
            st[key] = {"r": chosen[0], "name": chosen[1], "rows": [row_]}
        else:
            st[key] = {"r": pages_[0][0] if pages_ else "", "name": pages_[0][1] if pages_ else "", "rows": [row_]}
        decisions[dp] = {"status": "mapped", "parts": [row_], "key": key,
                         "note": (f"not on the face ({prev or 'no face line'}); found only in a note: {tag} on {st[key]['r']} '{st[key]['name']}'"
                                  + ("" if chosen else " (R page value not paired)"))}
    need = {d["key"] for d in decisions.values() if d["parts"] and not d["key"].startswith("NOTE:")}
    for key in sorted(need):
        if key in st:
            pages[key] = parse_r(get(base + st[key]["r"], cache))
    meta["pages"] = {k: (v["r"], v["name"]) for k, v in st.items()}
    quirks = []
    fy0_end = latest["period"]
    for dp in DPS:
        d = decisions[dp]
        rec = {"ticker": co.tic, "data_point": dp, "status": d["status"], "tags": "", "stmt": "NOTE" if d["key"].startswith("NOTE:") else d["key"].replace("BSP", "PAR").replace("EQP", "PAR"),
               "r_page": st.get(d["key"], {}).get("r", ""), "label": "", "fy0_printed": "", "fy0_api": "", "fy1_printed": "",
               "fy1_api": "", "match": "", "era_from_note": "", "evidence_class": "FILING-CHECKED", "note": d["note"]}
        parts = d["parts"]
        if parts:
            page = pages.get(d["key"])
            duration = not is_instant(dp) if d["key"].startswith("NOTE:") else d["key"] not in ("BS", "BSP")
            custom = any(p["custom"] for p in parts)
            prefix = lambda p: (next((pr["prefix"] for pr in (page or {}).get("rows", []) if pr["tag"] == p["tag"]), None)
                                or (co.tic.lower().replace("-", "") if p["custom"] else "us-gaap"))
            rec["tags"] = "+".join(f"{prefix(p)}:{p['tag']}" for p in parts)
            rec["label"] = " + ".join((p["plabel"] or "") for p in parts)[:120]
            src = "fsn_xbrl" if custom else "sec_api"
            verdicts = []
            for k, end in ((0, fy0_end), (1, prior_year(fy0_end))):
                pv_parts = [printed_for(page, p, k, dp) for p in parts]
                xv = [p["v0"] if k == 0 else p["v1"] for p in parts]
                if all(x is None for x in xv):
                    continue
                pv = sum(pv_parts) if all(x is not None for x in pv_parts) else None
                if custom:
                    av_parts = [(p["v0"] if k == 0 else p["v1"]) if p["custom"] else co.api(latest["accn"], p["tag"], end, duration)
                                for p in parts]
                else:
                    av_parts = [co.api(latest["accn"], p["tag"], end, duration) for p in parts]
                if d["key"] == "BS" and dp == "shares_outstanding":
                    pass
                av = sum(av_parts) if all(x is not None for x in av_parts) else None
                if pv is None:
                    # printed sign follows the face; fall back to the XBRL value with the negating flag when the R row
                    # could not be paired (recorded as such)
                    verdicts.append("R page value not paired")
                rec[f"fy{k}_printed"] = fmt(pv)
                rec[f"fy{k}_api"] = fmt(av)
                if pv is None:
                    continue
                if av is None:
                    verdicts.append("API missing")
                elif abs(pv - av) < Decimal("0.5") or (dp.endswith("eps") or dp == "dividends_per_share") and abs(pv - av) < Decimal("0.005"):
                    verdicts.append("Y")
                elif abs(abs(pv) - abs(av)) < Decimal("0.5"):
                    verdicts.append("Y (sign differs: printed in parentheses/negated label)")
                else:
                    verdicts.append(f"N (printed {fmt(pv)} vs API {fmt(av)})")
            bad = [v for v in verdicts if v.startswith("N") or v in ("API missing", "R page value not paired")]
            rec["match"] = bad[0] if bad else (verdicts[0] if verdicts else "")
            per = f"period {fy0_end.isoformat()[:4]}..{fy0_end.isoformat()}" if duration else f"period ..{fy0_end.isoformat()}"
            rec["note"] = ((d["note"] + " | ") if d["note"] else "") + f"accn {latest['accn']} {rec['r_page']} {per} | value_source={src}"
            for p in parts:
                if p["custom"]:
                    quirks.append(f"| {DATE} | Reader (reads 701-800) | {prefix(p)}:{p['tag']} | {co.tic} {dp}: face line '{(p['plabel'] or '')[:70]}' is on a company extension tag (value from filing XBRL, fsn_xbrl) | {co.tic} {latest['accn']} {rec['r_page']} | FILING-CHECKED | new |")
            if any(v.startswith("N") for v in verdicts):
                quirks.append(f"| {DATE} | Reader (reads 701-800) | {rec['tags'][:90]} | {co.tic} {dp}: printed value differs from the SEC API value ({'; '.join(v for v in verdicts if v.startswith('N'))}) | {co.tic} {latest['accn']} {rec['r_page']} | FILING-CHECKED | new |")
            if d["status"] == "combined":
                quirks.append(f"| {DATE} | Reader (reads 701-800) | {rec['tags'][:90]} | {co.tic} {dp}: {d['note'][:160]} | {co.tic} {latest['accn']} {rec['r_page']} | FILING-CHECKED | new |")
        else:
            rec["note"] = (d["note"] + " | " if d["note"] else "") + f"accn {latest['accn']} {rec['r_page']} read"
        out.append(rec)
    # eras: same rules on every 10-K FY2015 -> latest (FSN = the filing's own XBRL; each run cites accession and R page)
    era_lines = []
    per_filing = []
    for f in co.era:
        s = co.statements(f) if f is not latest else st
        per_filing.append((f, s, template_of(s) if f is not latest else tmpl))
    first = co.era[0]
    for rec in out:
        dp = rec["data_point"]
        runs: list[list] = []  # [sig, first_period, last_period, accn, r, label, value]
        for f, s, t in per_filing:
            d = decide(dp, s, t) if f is not latest else decisions[dp]
            if f is not latest and dp not in NOTE_SKIP and (d["status"] == "not_presented" or (dp == "interest_expense" and d["status"] == "combined")):
                h = xbrl_hit(co, f, dp, t)
                if h:
                    d = {"status": "mapped", "parts": [{"tag": h[0], "plabel": "(note)", "v0": h[1], "custom": False}], "key": "NOTE", "note": ""}
            sig = (d["status"], "+".join(p["tag"] for p in d["parts"]))
            rr = s.get(d["key"], {}).get("r", "") if d["key"] != "NOTE" else "note (filing XBRL)"
            lab = " + ".join((p["plabel"] or "") for p in d["parts"])[:70]
            val = sum(p["v0"] for p in d["parts"]) if d["parts"] and all(p["v0"] is not None for p in d["parts"]) else None
            if runs and runs[-1][0] == sig:
                runs[-1][2] = f["period"]
                runs[-1][7].append(f["accn"])
            else:
                runs.append([sig, f["period"], f["period"], f["accn"], rr, lab, val, [f["accn"]]])
        txt = " -> ".join(
            f"FY{a.isoformat()[:7]}..FY{z.isoformat()[:7]} {sg[0]}{(' ' + sg[1]) if sg[1] else ''} ({acc} {rr})"
            for sg, a, z, acc, rr, lab, val, _ in runs)
        cur = runs[-1]
        fy15 = first["period"] <= dt.date(2016, 1, 31)
        cov = "ERA COVERED FY2015-latest" if fy15 else f"ERA FROM FIRST 10-K FY{first['period'].isoformat()[:7]} (no earlier 10-K in fsn)"
        rec["era_from_note"] = f"{cov}: same_tag@{cur[1].isoformat()}; runs: {txt}" if rec["status"] not in ("not_presented", "OUT", "combined") \
            else f"{cov}: runs: {txt}"
        if len(runs) > 1:
            era_lines.append(f"- {dp}: " + " -> ".join(
                f"FY{a.isoformat()[:7]}..FY{z.isoformat()[:7]} {sg[0]} {sg[1] or '-'} (first 10-K of run {acc} {rr}"
                + (f" '{lab}' = {fmt(val)}" if lab else "") + ")" for sg, a, z, acc, rr, lab, val, _ in runs))
            tags_seq = [r[0][1] for r in runs if r[0][1]]
            if len(set(tags_seq)) > 1:
                quirks.append(f"| {DATE} | Reader (reads 701-800) | {' -> '.join(dict.fromkeys(tags_seq))[:120]} | {co.tic} {dp}: tag eras FY2015->latest: "
                              + "; ".join(f"{r[0][0]} {r[0][1] or '-'} FY{r[1].isoformat()[:4]}-FY{r[2].isoformat()[:4]}" for r in runs)[:300]
                              + f" | {co.tic} " + "; ".join(f"{r[3]} {r[4]}" for r in runs)[:200] + " | FILING-CHECKED (fsn.line) | new |")
    meta["era_lines"] = era_lines
    meta["era_filings"] = [(f["accn"], f["period"]) for f in co.era]
    meta["quirks"] = quirks
    # era value check against SEC API (each era 10-K's own FY0 value, standard tags)
    em = []
    for f, s, t in per_filing:
        if f is latest:
            continue
        for dp in DPS:
            d = decide(dp, s, t)
            if not d["parts"] or any(p["custom"] for p in d["parts"]) or d["status"] == "OUT":
                continue
            dur = d["key"] not in ("BS", "BSP")
            for p in d["parts"]:
                if p["v0"] is None:
                    continue
                a = co.api(f["accn"], p["tag"], f["period"], dur)
                if a is not None and abs(a - p["v0"]) >= Decimal("0.5") and not (dp.endswith("eps") and abs(a - p["v0"]) < Decimal("0.005")):
                    em.append(f"{dp} {p['tag']} {f['accn']} filing XBRL {fmt(p['v0'])} vs API {fmt(a)}")
    meta["era_mismatch"] = em
    return out, meta


COLS = ["ticker", "data_point", "status", "tags", "stmt", "r_page", "label", "fy0_printed", "fy0_api", "fy1_printed",
        "fy1_api", "match", "era_from_note", "evidence_class", "note"]


def write_company(out: list[dict], meta: dict, out_dir: str) -> None:
    tic = meta["ticker"]
    with open(os.path.join(out_dir, f"{tic}-docmap-{DATE}.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS, extrasaction="ignore")
        w.writeheader()
        for r in out:
            w.writerow({k: r.get(k, "") for k in COLS})
    L = [f"# {tic} document-first map {DATE} (read-only, bottom-up)", "",
         "Evidence label: FILING-CHECKED unless a row says otherwise. Structure (statement, R page, line order, tag, printed "
         "label) from fsn.line of the 10-K = the filing's own presentation; printed values from the R pages fetched from sec.gov "
         "(paired to the FSN line by tag and value); API = SEC company API facts in core.fact, same accession and period "
         "(value_source sec_api); extension-tag values from the filing XBRL via fsn.value (value_source fsn_xbrl). Built with "
         "data-team/companies/reads/tools/docmap_fsn.py under Dhairya's rulings of 2026-11-12 (status vocabulary mapped / combined / "
         "component sum / component_in_note / not_presented / OUT; opex never includes cost of revenue; shares = "
         "CommonStockSharesOutstanding at the BS date, never the dei cover count; a label never promotes a wider tag; instants "
         "never summed except total_debt).", "", "## Filings opened"]
    if meta.get("error"):
        L.append(f"- none: {meta['error']} (CIK {meta['cik']}, {meta['name']})")
    else:
        L.append(f"- Latest 10-K {meta['accn']} (CIK {meta['cik']}, {meta['name']}, filed {meta['filed']}, FY ended "
                 f"{meta['period']}; template {meta['template']}). Statement pages: "
                 + ", ".join(f"{k} {r} '{n}'" for k, (r, n) in meta["pages"].items()))
        L.append("- R pages fetched from sec.gov for the statements used; core.fact (SEC company API) for the API values.")
        L.append("- Era 10-Ks read from fsn.line/fsn.value (one per fiscal year, FY2015 to latest): "
                 + ", ".join(f"{a} (FY {p})" for a, p in meta["era_filings"]))
        L.append("")
        L.append(f"FY0 = {meta['period']}; FY1 = prior year. Values in full USD (printed value x the R-page scale); EPS per share; shares in shares.")
    L += ["", "## Data points", "| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in out:
        L.append("| " + " | ".join(str(r.get(k, "")).replace("|", "/") for k in
                                    ["data_point", "status", "tags", "r_page", "label", "fy0_printed", "fy0_api",
                                     "fy1_printed", "fy1_api", "match", "evidence_class", "note"]) + " |")
    L += ["", "## Era coverage FY2015 to latest (every 10-K in fsn; runs with a change listed, each citing its first 10-K and R page)"]
    L += meta.get("era_lines") or ["- no tag or status change across the 10-Ks read: every data point keeps its latest decision FY2015 (or first 10-K) to latest"]
    L += ["", "## Era values vs SEC API (each era 10-K's own FY value, standard tags)"]
    L += [f"- {x}" for x in meta.get("era_mismatch", [])[:40]] or ["- none"]
    mism = [r for r in out if str(r.get("match", "")).startswith("N") or r.get("match") in ("API missing", "R page value not paired")]
    L += ["", "## Mismatches (printed vs API)"] + ([f"- {r['data_point']}: {r['match']} ({r.get('tags', '')})" for r in mism]
                                                   or ["none beyond sign differences"])
    open(os.path.join(out_dir, f"{tic}-docmap-{DATE}.md"), "w").write("\n".join(L) + "\n")


def main() -> None:
    cohort, first, last, out_dir, cache, inbox = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], sys.argv[5], sys.argv[6]
    os.makedirs(cache, exist_ok=True)
    rows = list(csv.DictReader(open(cohort)))
    conn = psycopg.connect(os.environ["DATABASE_URL"], autocommit=True)
    conn.execute("set statement_timeout = '60s'")
    for rank in range(first, last + 1):
        row = rows[rank - 1]
        n0 = FETCHES[0]
        try:
            out, meta = read_company(conn, row, cache)
        except Exception as exc:  # one company must not stop the range
            out, meta = [], {"ticker": row["ticker"], "cik": row["cik"].zfill(10), "name": row["name"],
                             "error": f"tool error {exc!r}"[:300]}
        write_company(out, meta, out_dir)
        with open(inbox, "a") as fh:
            for q in dict.fromkeys(meta.get("quirks", [])):
                fh.write(q + "\n")
        mm = sum(1 for r in out if str(r.get("match", "")).startswith("N"))
        print(f"rank {rank} {row['ticker']}: rows {len(out)}, mapped {sum(1 for r in out if r['status'] not in ('not_presented', 'OUT'))}, "
              f"N {mm}, unpaired {sum(1 for r in out if r.get('match') == 'R page value not paired')}, api-missing "
              f"{sum(1 for r in out if r.get('match') == 'API missing')}, era-mismatch {len(meta.get('era_mismatch', []))}, "
              f"quirks {len(meta.get('quirks', []))}, fetches {FETCHES[0] - n0}"
              + (f", ERROR {meta.get('error')}" if meta.get("error") else ""), flush=True)
    conn.close()


if __name__ == "__main__":
    main()
