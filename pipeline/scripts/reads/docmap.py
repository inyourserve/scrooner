"""Document-first read of one company's 10-K face statements (no network, no DB): the R pages fetched by sec_fetch.py
are the authority; SEC companyfacts is only compared against them.

For each data point: find the printed line on its face statement (by the us-gaap element the R page links the line
to, in a fixed candidate order; failing that, a custom element whose printed label matches), read the printed FY0 and
FY1 values times the page scale, and compare with companyfacts for the SAME accession and period. A disagreement is
decided by the filing (the printed value stands; the row says so). Then an era scan: does the chosen tag cover the
last five fiscal years in companyfacts 10-K facts, and if not, which candidate tag carried the earlier years (that
era's 10-K is fetched in a second pass and its face checked with --era).

usage: docmap.py <sec_docs_dir> <cik10> <ticker> <out_dir> [--date 2026-11-12]
       writes <out_dir>/<TICKER>-docmap-<date>.{md,csv} and prints a JSON line (counts, quirks, era requests)
"""

from __future__ import annotations

import csv
import gzip
import io
import json
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

from bs4 import BeautifulSoup

MONTHS = {
    m: i
    for i, m in enumerate(
        (
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec",
        ),
        start=1,
    )
}
DATE_RE = re.compile(r"([A-Z][a-z]{2})[a-z]*\.? (\d{1,2}), (\d{4})")
SCALE_WORDS = {"thousands": 10**3, "millions": 10**6, "billions": 10**9}
YEARLY = re.compile(
    r"(12|11|13) Months Ended|5[23] Weeks Ended|Year Ended", re.IGNORECASE
)

# ------------------------------------------------------------------------------------------------ statement kinds
STMT_RULES = (  # (kind, regex on the report's LongName/ShortName); first match wins
    ("COVER", r"cover|document and entity"),
    ("PAR", r"parenthetical"),
    ("CI", r"comprehensive (income|loss|earnings)"),
    ("CF", r"cash flow"),
    (
        "EQ",
        r"(stockholders|shareholders|shareowners|members|partners)['’]? ?(equity|deficit|investment)|changes in equity|statements? of equity",
    ),
    ("BS", r"balance sheet|financial (condition|position)|statements? of condition"),
    ("IS", r"operations|income|earnings|statements? of (loss|revenue)"),
)


def stmt_kind(name: str) -> str | None:
    if re.search(r"parenthetical", name, re.IGNORECASE):
        base = stmt_kind(re.sub(r"parenthetical", "", name, flags=re.IGNORECASE))
        return f"PAR_{base}" if base and base != "COVER" else "PAR"
    for kind, rx in STMT_RULES:
        if re.search(rx, name, re.IGNORECASE):
            return kind
    return None


# ------------------------------------------------------------------------------------------------ data points
@dataclass(frozen=True)
class DP:
    name: str
    stmts: tuple[str, ...]
    tags: tuple[
        str, ...
    ]  # candidate elements, priority order ("dei:" prefix for dei; else us-gaap)
    label: str = ""  # regex for a custom-element fallback
    kind: str = "money"  # money | pershare | shares
    combined: tuple[str, ...] = ()  # elements that are a combined line for this point


DPS: tuple[DP, ...] = (
    DP(
        "revenue",
        ("IS",),
        (
            "Revenues",
            "RevenuesNetOfInterestExpense",
            "RevenueFromContractWithCustomerExcludingAssessedTax",
            "RevenueFromContractWithCustomerIncludingAssessedTax",
            "SalesRevenueNet",
            "RegulatedAndUnregulatedOperatingRevenue",
            "RealEstateRevenueNet",
        ),
        r"^(total )?(net )?(operating )?(revenues?|sales)\b",
    ),
    DP(
        "cost_of_revenue",
        ("IS",),
        (
            "CostOfRevenue",
            "CostOfGoodsAndServicesSold",
            "CostOfGoodsSold",
            "CostOfServices",
            "CostOfGoodsAndServiceExcludingDepreciationDepletionAndAmortization",
        ),
        r"^(total )?cost of (revenues?|sales|goods|products)",
    ),
    DP("gross_profit", ("IS",), ("GrossProfit",), r"^gross (profit|margin)"),
    DP(
        "operating_expenses",
        ("IS",),
        ("OperatingExpenses",),
        r"^total operating expenses",
    ),
    DP(
        "sga_expense",
        ("IS",),
        ("SellingGeneralAndAdministrativeExpense",),
        r"^selling,? general",
    ),
    DP(
        "research_and_development",
        ("IS",),
        (
            "ResearchAndDevelopmentExpense",
            "ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost",
        ),
        r"^research and development",
    ),
    DP(
        "operating_income",
        ("IS",),
        ("OperatingIncomeLoss",),
        r"^(total )?operating (income|profit|earnings|loss)",
    ),
    DP(
        "interest_expense",
        ("IS",),
        (
            "InterestExpense",
            "InterestExpenseNonoperating",
            "InterestExpenseDebt",
            "InterestAndDebtExpense",
            "InterestExpenseOperating",
        ),
        r"^interest expense",
        combined=(
            "InterestIncomeExpenseNonoperatingNet",
            "InterestIncomeExpenseNet",
            "InterestExpenseNet",
        ),
    ),
    DP(
        "interest_income",
        ("IS",),
        (
            "InvestmentIncomeInterest",
            "InterestIncomeOther",
            "InterestIncomeOperating",
            "InterestAndDividendIncomeOperating",
        ),
        r"^interest income",
        combined=("InvestmentIncomeInterestAndDividend", "InterestAndOtherIncome"),
    ),
    DP(
        "other_income_expense_net",
        ("IS",),
        (
            "OtherNonoperatingIncomeExpense",
            "NonoperatingIncomeExpense",
            "OtherNonoperatingIncome",
        ),
        r"^other (income|expense|\(income\)|\(expense\))",
    ),
    DP(
        "income_before_tax",
        ("IS",),
        (
            "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",
            "IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments",
            "IncomeLossFromContinuingOperationsBeforeIncomeTaxesDomestic",
        ),
        r"(income|earnings|loss).* before (income )?tax",
    ),
    DP(
        "income_tax_expense",
        ("IS",),
        ("IncomeTaxExpenseBenefit", "IncomeTaxExpenseBenefitContinuingOperations"),
        r"(provision for|benefit from)? ?income tax",
    ),
    DP(
        "net_income",
        ("IS",),
        (
            "NetIncomeLoss",
            "NetIncomeLossAvailableToCommonStockholdersBasic",
            "ProfitLoss",
        ),
        r"^net (income|earnings|loss)",
    ),
    DP(
        "basic_eps",
        ("IS",),
        ("EarningsPerShareBasic", "EarningsPerShareBasicAndDiluted"),
        r"basic",
        "pershare",
    ),
    DP(
        "diluted_eps",
        ("IS",),
        ("EarningsPerShareDiluted", "EarningsPerShareBasicAndDiluted"),
        r"diluted",
        "pershare",
    ),
    DP(
        "weighted_basic_shares",
        ("IS",),
        (
            "WeightedAverageNumberOfSharesOutstandingBasic",
            "WeightedAverageNumberOfShareOutstandingBasicAndDiluted",
        ),
        r"basic",
        "shares",
    ),
    DP(
        "weighted_diluted_shares",
        ("IS",),
        (
            "WeightedAverageNumberOfDilutedSharesOutstanding",
            "WeightedAverageNumberOfShareOutstandingBasicAndDiluted",
        ),
        r"diluted",
        "shares",
    ),
    DP(
        "dividends_per_share",
        ("IS", "EQ", "PAR_EQ", "PAR_IS", "PAR_CF", "PAR_BS", "PAR", "CF"),
        (
            "CommonStockDividendsPerShareDeclared",
            "CommonStockDividendsPerShareCashPaid",
        ),
        r"dividends? (declared )?per (common )?share",
        "pershare",
    ),
    DP(
        "comprehensive_income",
        ("CI", "IS"),
        (
            "ComprehensiveIncomeNetOfTax",
            "ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest",
        ),
        r"^(total )?comprehensive (income|earnings|loss)",
    ),
    DP(
        "cash_and_equivalents",
        ("BS",),
        (
            "CashAndCashEquivalentsAtCarryingValue",
            "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents",
            "Cash",
            "CashAndDueFromBanks",
        ),
        r"^cash and (cash )?equivalents",
    ),
    DP(
        "accounts_receivable",
        ("BS",),
        (
            "AccountsReceivableNetCurrent",
            "ReceivablesNetCurrent",
            "AccountsNotesAndLoansReceivableNetCurrent",
            "AccountsReceivableNet",
        ),
        r"(accounts|trade) receivables?",
    ),
    DP(
        "inventory",
        ("BS",),
        (
            "InventoryNet",
            "RetailRelatedInventoryMerchandise",
            "InventoryFinishedGoods",
            "InventoryGross",
        ),
        r"^(total )?(net )?inventor(y|ies)",
    ),
    DP("current_assets", ("BS",), ("AssetsCurrent",), r"^total current assets"),
    DP(
        "ppe_net",
        ("BS",),
        (
            "PropertyPlantAndEquipmentNet",
            "PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization",
        ),
        r"property(, plant)? and equipment.*net|net property",
    ),
    DP("goodwill", ("BS",), ("Goodwill",), r"^goodwill"),
    DP("total_assets", ("BS",), ("Assets",), r"^total assets"),
    DP(
        "accounts_payable",
        ("BS",),
        ("AccountsPayableCurrent", "AccountsPayableTradeCurrent"),
        r"^(trade )?accounts payable",
        combined=("AccountsPayableAndAccruedLiabilitiesCurrent",),
    ),
    DP(
        "current_liabilities",
        ("BS",),
        ("LiabilitiesCurrent",),
        r"^total current liabilities",
    ),
    DP("total_liabilities", ("BS",), ("Liabilities",), r"^total liabilities$"),
    DP("total_debt", ("BS",), ()),  # face component sum, below
    DP(
        "stockholders_equity",
        ("BS",),
        (
            "StockholdersEquity",
            "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
        ),
        r"^total .*(stockholders|shareholders|shareowners)['’]? (equity|investment)",
    ),
    DP(
        "shares_outstanding",
        ("BS", "PAR_BS"),
        ("CommonStockSharesOutstanding",),
        "",
        "shares",
    ),
    DP(
        "cfo",
        ("CF",),
        (
            "NetCashProvidedByUsedInOperatingActivities",
            "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations",
        ),
        r"net cash .*operating",
    ),
    DP(
        "cash_flow_investing",
        ("CF",),
        (
            "NetCashProvidedByUsedInInvestingActivities",
            "NetCashProvidedByUsedInInvestingActivitiesContinuingOperations",
        ),
        r"net cash .*investing",
    ),
    DP(
        "cash_flow_financing",
        ("CF",),
        (
            "NetCashProvidedByUsedInFinancingActivities",
            "NetCashProvidedByUsedInFinancingActivitiesContinuingOperations",
        ),
        r"net cash .*financing",
    ),
    DP(
        "capex",
        ("CF",),
        (
            "PaymentsToAcquirePropertyPlantAndEquipment",
            "PaymentsToAcquireProductiveAssets",
            "PaymentsForCapitalImprovements",
            "PaymentsToAcquireOtherPropertyPlantAndEquipment",
        ),
        r"(capital expenditures|purchases? of property|additions to property|acquisitions? of property)",
    ),
    DP(
        "depreciation_and_amortization",
        ("CF",),
        (
            "DepreciationDepletionAndAmortization",
            "DepreciationAmortizationAndAccretionNet",
            "DepreciationAndAmortization",
            "DepreciationAmortizationAndOther",
        ),
        r"^depreciation(,| and) (depletion and )?amortization",
    ),
    DP(
        "amortization_of_intangibles",
        ("CF", "IS"),
        ("AmortizationOfIntangibleAssets",),
        r"^amortization of (acquired )?intangible",
    ),
    DP(
        "sbc",
        ("CF",),
        ("ShareBasedCompensation", "AllocatedShareBasedCompensationExpense"),
        r"(stock|share|equity)[- ]based compensation",
    ),
    DP(
        "dividends_paid",
        ("CF",),
        ("PaymentsOfDividends", "PaymentsOfDividendsCommonStock"),
        r"dividends paid|payments? of dividends|cash dividends",
    ),
    DP(
        "share_buybacks",
        ("CF",),
        ("PaymentsForRepurchaseOfCommonStock", "PaymentsForRepurchaseOfEquity"),
        r"(repurchases?|purchases?) of (common )?(stock|shares)|share repurchases?",
    ),
    DP(
        "cf_ar_change",
        ("CF",),
        ("IncreaseDecreaseInAccountsReceivable", "IncreaseDecreaseInReceivables"),
        r"^(accounts |trade )?receivables?",
        combined=(
            "IncreaseDecreaseInAccountsAndOtherReceivables",
            "IncreaseDecreaseInAccountsReceivableAndOtherOperatingAssets",
        ),
    ),
    DP(
        "cf_inventory_change",
        ("CF",),
        ("IncreaseDecreaseInInventories", "IncreaseDecreaseInRetailRelatedInventories"),
        r"^inventor(y|ies)",
    ),
    DP(
        "cf_ap_change",
        ("CF",),
        ("IncreaseDecreaseInAccountsPayable", "IncreaseDecreaseInAccountsPayableTrade"),
        r"^(trade )?accounts payable$",
        combined=("IncreaseDecreaseInAccountsPayableAndAccruedLiabilities",),
    ),
    DP(
        "cash_paid_for_interest",
        ("CF",),
        ("InterestPaidNet", "InterestPaid"),
        r"interest paid|cash paid for interest",
    ),
    DP(
        "cash_paid_for_income_taxes",
        ("CF",),
        ("IncomeTaxesPaidNet", "IncomeTaxesPaid"),
        r"income taxes paid|cash paid for income taxes",
    ),
)

# face debt lines summed for total_debt (us-gaap); operating leases never
DEBT_TAGS = (
    "ShortTermBorrowings",
    "CommercialPaper",
    "DebtCurrent",
    "LongTermDebtCurrent",
    "LongTermDebtNoncurrent",
    "LongTermDebt",
    "LongTermDebtAndCapitalLeaseObligations",
    "LongTermDebtAndCapitalLeaseObligationsCurrent",
    "LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities",
    "DebtAndCapitalLeaseObligations",
    "FinanceLeaseLiabilityCurrent",
    "FinanceLeaseLiabilityNoncurrent",
    "FinanceLeaseLiability",
    "ConvertibleNotesPayable",
    "ConvertibleNotesPayableCurrent",
    "ConvertibleDebtNoncurrent",
    "ConvertibleDebtCurrent",
    "SeniorNotes",
    "SeniorNotesCurrent",
    "SeniorLongTermNotes",
    "NotesPayable",
    "NotesPayableCurrent",
    "LongTermNotesPayable",
    "LinesOfCreditCurrent",
    "LineOfCredit",
    "LongTermLineOfCredit",
    "OtherLongTermDebtNoncurrent",
    "OtherLongTermDebtCurrent",
    "ShortTermBankLoansAndNotesPayable",
    "SecuredDebt",
    "UnsecuredDebt",
    "LongTermDebtCurrentAndNoncurrent",
    "OtherShortTermBorrowings",
    "BankOverdrafts",
    "FederalHomeLoanBankAdvances",
    "AdvancesFromFederalHomeLoanBanks",
    "LongTermFederalHomeLoanBankAdvancesNoncurrent",
    "OtherBorrowings",
    "SecuritiesSoldUnderAgreementsToRepurchase",
    "FederalFundsPurchasedAndSecuritiesSoldUnderAgreementsToRepurchase",
    "FederalFundsPurchased",
    "DebtInstrumentCarryingAmount",
    "LongTermDebtFairValue",
)
DEBT_LABEL = re.compile(
    r"\b(debt|borrowings?|notes payable|commercial paper|senior notes|credit facility|loans? payable|finance lease)",
    re.IGNORECASE,
)
NOT_DEBT_LABEL = re.compile(
    r"operating lease|deferred|interest payable|accrued|issuance cost", re.IGNORECASE
)
BANK_PERIMETER = {
    "FederalHomeLoanBankAdvances",
    "AdvancesFromFederalHomeLoanBanks",
    "LongTermFederalHomeLoanBankAdvancesNoncurrent",
    "SecuritiesSoldUnderAgreementsToRepurchase",
    "FederalFundsPurchasedAndSecuritiesSoldUnderAgreementsToRepurchase",
    "FederalFundsPurchased",
    "OtherBorrowings",
    "OtherShortTermBorrowings",
}
# DebtInstrumentCarryingAmount / LongTermDebtFairValue are note tags; on a face they are a quirk, never summed blindly
DEBT_NOTE_ONLY = {"DebtInstrumentCarryingAmount", "LongTermDebtFairValue"}
# face elements that mark a bank / lender / insurer template (their presence makes trade-company lines OUT)
FINANCIAL_MARKERS = {
    "InterestAndDividendIncomeOperating",
    "InterestExpenseDeposits",
    "NoninterestIncome",
    "NoninterestExpense",
    "ProvisionForLoanLeaseAndOtherLosses",
    "ProvisionForLoanAndLeaseLosses",
    "ProvisionForCreditLossesNet",
    "Deposits",
    "PremiumsEarnedNet",
    "PolicyholderBenefitsAndClaimsIncurredNet",
    "InterestIncomeExpenseNet",
    "LoansAndLeasesReceivableNetReportedAmount",
    "FinancingReceivableExcludingAccruedInterestAfterAllowanceForCreditLoss",
}
OUT_FINANCIAL = {
    "cost_of_revenue",
    "gross_profit",
    "research_and_development",
    "operating_income",
    "inventory",
    "accounts_receivable",
    "cf_inventory_change",
    "current_assets",
    "current_liabilities",
}
OUT_UNCLASSIFIED = {"current_assets", "current_liabilities"}
DA_PARTS = (
    "Depreciation",
    "DepreciationNonproduction",
    "AmortizationOfIntangibleAssets",
    "DepreciationAndAmortization",
    "AmortizationOfDeferredCharges",
    "FinanceLeaseRightOfUseAssetAmortization",
    "DepreciationDepletionAndAmortization",
)


# ------------------------------------------------------------------------------------------------ R page parsing
@dataclass
class Row:
    elem: str  # "us-gaap:Revenues", "abc:Foo"
    label: str
    values: list[Decimal | None]
    raw: list[str]
    is_header: bool = False


@dataclass
class Page:
    file: str
    title: str
    kind: str | None
    money_scale: int
    share_scale: int
    cols: list[tuple[str, date | None]]  # (group label, column date)
    rows: list[Row] = field(default_factory=list)


def parse_date(s: str) -> date | None:
    m = DATE_RE.search(s)
    if not m or m.group(1)[:3] not in MONTHS:
        return None
    return date(int(m.group(3)), MONTHS[m.group(1)[:3]], int(m.group(2)))


def parse_num(s: str) -> Decimal | None:
    t = s.replace("$", "").replace(",", "").replace("\xa0", " ").strip()
    t = re.sub(r"\[\d+\]", "", t).strip()
    if not t or t in ("—", "-", "–"):
        return None
    neg = t.startswith("(") and t.endswith(")")
    t = t.strip("()").strip()
    try:
        v = Decimal(t)
    except InvalidOperation:
        return None
    return -v if neg else v


def scales(title: str) -> tuple[int, int]:
    t = title.lower()
    money = share = 1
    m = re.search(r"\$ in (thousands|millions|billions)", t)
    s = re.search(r"shares in (thousands|millions|billions)", t)
    g = re.search(r"\bin (thousands|millions|billions)", t)
    if m:
        money = SCALE_WORDS[m.group(1)]
    elif g and not t.startswith("$"):
        money = SCALE_WORDS[g.group(1)]
    if s:
        share = SCALE_WORDS[s.group(1)]
    elif (
        g
        and "except share" not in t
        and "except per share" not in t.replace(", except per share", "")
        and not m
    ):
        # "In Millions, except Per Share data": shares are in millions too; "except Share data" leaves shares unscaled
        share = SCALE_WORDS[g.group(1)]
    if g and re.search(r"except (share|shares)\b", t) and not s:
        share = 1
    return money, share


def parse_page(path: Path, kind: str | None) -> Page:
    soup = BeautifulSoup(path.read_bytes(), "lxml")
    table = soup.find("table", class_="report") or soup.find("table")
    trs = table.find_all("tr") if table else []
    head = [tr for tr in trs if tr.find("th")]
    title_th = head[0].find("th") if head else None
    title = " ".join(title_th.get_text(" ").split()) if title_th else ""
    money, share = scales(title)
    # header: row 1 = title th (+ group ths with colspan, or date ths), row 2 = date ths under groups
    cols: list[tuple[str, date | None]] = []
    if head:
        r1 = head[0].find_all("th")[1:]
        if len(head) > 1 and any(
            parse_date(th.get_text(" ")) for th in head[1].find_all("th")
        ):
            dates = [parse_date(th.get_text(" ")) for th in head[1].find_all("th")]
            i = 0
            for th in r1:
                span = int(th.get("colspan", 1))
                g = " ".join(th.get_text(" ").split())
                if parse_date(g):  # a date column in row 1 (rowspan 2)
                    cols.append(("", parse_date(g)))
                    continue
                for _ in range(span):
                    cols.append((g, dates[i] if i < len(dates) else None))
                    i += 1
        else:
            cols = [("", parse_date(th.get_text(" "))) for th in r1]
    rows: list[Row] = []
    for tr in trs:
        if tr.find("th"):
            continue
        tds = tr.find_all("td")
        if not tds:
            continue
        a = tds[0].find("a", onclick=True)
        elem = ""
        if a:
            m = re.search(r"defref_([A-Za-z0-9-]+)_([A-Za-z0-9_]+)", a["onclick"])
            if m:
                elem = f"{m.group(1)}:{m.group(2)}"
        label = " ".join(tds[0].get_text(" ").split())
        raw = [" ".join(td.get_text(" ").split()) for td in tds[1:]]
        vals = [parse_num(x) for x in raw]
        rows.append(
            Row(elem, label, vals, raw, is_header=not any(v is not None for v in vals))
        )
    return Page(path.name, title, kind, money, share, cols, rows)


def year_cols(p: Page) -> list[int]:
    """Indexes of the FY0 and FY1 columns: yearly groups (or instant dates), newest first, distinct dates."""
    idx = []
    seen = set()
    for i, (g, d) in enumerate(p.cols):
        if d is None or d in seen:
            continue
        if p.kind in ("BS", "COVER", "PAR_BS") or (
            p.kind and p.kind.startswith("PAR") and not g
        ):
            ok = not g or not re.search(r"Months|Weeks", g) or bool(YEARLY.search(g))
        else:
            ok = bool(YEARLY.search(g)) or (not g and p.kind == "EQ")
        if ok:
            idx.append(i)
            seen.add(d)
    idx.sort(key=lambda i: p.cols[i][1], reverse=True)
    return idx[:2]


# ------------------------------------------------------------------------------------------------ companyfacts
class Facts:
    def __init__(self, path: Path):
        raw = path.read_bytes()
        self.d = json.loads(gzip.decompress(raw) if path.suffix == ".gz" else raw).get(
            "facts", {}
        )

    def units(self, elem: str) -> list[dict]:
        tax, name = elem.split(":", 1)
        node = self.d.get(tax, {}).get(name)
        if not node:
            return []
        out = []
        for unit, lst in node.get("units", {}).items():
            out += [{**x, "unit": unit} for x in lst]
        return out

    def value(self, elem: str, accn: str, end: date, duration: bool) -> Decimal | None:
        cands = []
        for x in self.units(elem):
            if x.get("accn") != accn or x.get("end") != end.isoformat():
                continue
            if duration:
                if "start" not in x:
                    continue
                days = (end - date.fromisoformat(x["start"])).days
                if not 340 <= days <= 380:
                    continue
            elif "start" in x:
                continue
            cands.append(Decimal(str(x["val"])))
        return cands[0] if len(set(cands)) >= 1 else None

    def fy_years(self, elem: str, duration: bool) -> dict[int, str]:
        """{fiscal-year end year: accession of the latest 10-K carrying it} for 10-K annual facts."""
        out: dict[int, tuple[str, str]] = {}
        for x in self.units(elem):
            if x.get("form") not in ("10-K", "10-K/A", "10-KT"):
                continue
            if duration != ("start" in x):
                continue
            if (
                duration
                and not 340
                <= (date.fromisoformat(x["end"]) - date.fromisoformat(x["start"])).days
                <= 380
            ):
                continue
            y = int(x["end"][:4])
            if y not in out or x["filed"] > out[y][1]:
                out[y] = (x["accn"], x["filed"])
        return {y: a for y, (a, _) in out.items()}


# ------------------------------------------------------------------------------------------------ the read
@dataclass
class Hit:
    page: Page
    row: Row
    elem: str


def is_mismatch(m: str) -> bool:
    return m.startswith("N") or "FY0 N" in m or "FY1 N" in m


def fmt(v: Decimal | None) -> str:
    if v is None:
        return ""
    v = v.normalize()
    s = format(v, "f")
    return s


def scaled(p: Page, r: Row, i: int, kind: str) -> Decimal | None:
    if i >= len(r.values) or r.values[i] is None:
        return None
    v = r.values[i]
    if kind == "pershare" or "PerShare" in r.elem:
        return v
    if kind == "shares" or "Shares" in r.elem.split(":")[-1] and "Value" not in r.elem:
        return v * p.share_scale
    return v * p.money_scale


class Reader:
    def __init__(self, base: Path, cik: str, accn: str, facts: Facts | None):
        self.base, self.cik, self.accn, self.facts = base, cik, accn, facts
        d = base / cik / accn
        summ = ET.fromstring((d / "FilingSummary.xml").read_bytes())
        self.pages: list[Page] = []
        for rep in summ.iter("Report"):
            fn = (rep.findtext("HtmlFileName") or "").strip()
            cat = (rep.findtext("MenuCategory") or "").strip()
            name = " ".join(
                (
                    (rep.findtext("LongName") or "")
                    + " "
                    + (rep.findtext("ShortName") or "")
                ).split()
            )
            if not fn or not (d / fn).exists() or cat not in ("Statements", "Cover"):
                continue
            k = (
                "COVER"
                if cat == "Cover"
                else stmt_kind(re.sub(r"^\d+ - \w+ - ", "", name))
            )
            self.pages.append(parse_page(d / fn, k))
        self.by_kind: dict[str, list[Page]] = {}
        for p in self.pages:
            if p.kind:
                self.by_kind.setdefault(p.kind, []).append(p)
        bs = self.by_kind.get("BS", [])
        self.fy0 = self.fy1 = None
        elems = {
            r.elem.split(":", 1)[-1]
            for p in self.pages
            for r in p.rows
            if r.elem.startswith("us-gaap:")
        }
        self.unclassified = bool(self.by_kind.get("BS")) and not elems & {
            "AssetsCurrent",
            "LiabilitiesCurrent",
        }
        self.financial = sorted(elems & FINANCIAL_MARKERS)
        for p in self.by_kind.get("IS", []) + self.by_kind.get("CF", []) + bs:
            yc = year_cols(p)
            if yc:
                self.fy0 = p.cols[yc[0]][1]
                self.fy1 = p.cols[yc[1]][1] if len(yc) > 1 else None
                break

    def find(self, kinds: tuple[str, ...], elems: tuple[str, ...]) -> Hit | None:
        for e in elems:
            q = e if ":" in e else f"us-gaap:{e}"
            for k in kinds:
                for p in self.by_kind.get(k, []):
                    for r in p.rows:
                        if r.elem == q and not r.is_header:
                            return Hit(p, r, q)
        return None

    def find_label(self, kinds: tuple[str, ...], rx: str) -> Hit | None:
        if not rx:
            return None
        for k in kinds:
            for p in self.by_kind.get(k, []):
                for r in p.rows:
                    if r.is_header or r.elem.startswith(("us-gaap:", "dei:", "srt:")):
                        continue
                    if re.search(rx, r.label, re.IGNORECASE):
                        return Hit(p, r, r.elem)
        return None

    def values(
        self, h: Hit, kind: str
    ) -> tuple[Decimal | None, Decimal | None, date | None, date | None]:
        yc = year_cols(h.page)
        p0 = scaled(h.page, h.row, yc[0], kind) if yc else None
        p1 = scaled(h.page, h.row, yc[1], kind) if len(yc) > 1 else None
        d0 = h.page.cols[yc[0]][1] if yc else None
        d1 = h.page.cols[yc[1]][1] if len(yc) > 1 else None
        return p0, p1, d0, d1

    def api(self, elem: str, d: date | None, duration: bool) -> Decimal | None:
        if (
            self.facts is None
            or d is None
            or not elem.startswith(("us-gaap:", "dei:", "srt:"))
        ):
            return None
        if elem == "dei:EntityCommonStockSharesOutstanding":
            for x in self.facts.units(elem):
                if x.get("accn") == self.accn:
                    return Decimal(str(x["val"]))
            return None
        return self.facts.value(elem, self.accn, d, duration)


def match_txt(printed: Decimal | None, api: Decimal | None) -> str:
    if printed is None and api is None:
        return ""
    if api is None:
        return "no API value"
    if printed is None:
        return "N (not printed)"
    if printed == api:
        return "Y"
    if printed == -api:
        return "Y (sign differs: printed in parentheses/negated label)"
    if (
        abs(abs(printed) - abs(api)) <= Decimal("0.005") * max(abs(api), 1)
        and printed.as_tuple().exponent < 0
    ):
        return "Y (rounding)"
    return "N"


def combine_match(m0: str, m1: str) -> str:
    """One match cell for the FY0/FY1 pair: identical texts collapse; an empty or no-API FY1 never hides FY0."""
    if m1 in ("", m0) or (m1 == "no API value" and m0 != ""):
        return m0
    if m0 == "":
        return f"FY1 {m1}"
    return f"FY0 {m0}; FY1 {m1}"


def short(elem: str) -> str:
    return elem.split(":", 1)[1] if elem.startswith(("us-gaap:",)) else elem


def read_company(base: Path, cik: str, ticker: str, accn: str, filed: str) -> dict:
    cf = base / cik / "companyfacts.json.gz"
    facts = Facts(cf) if cf.exists() else None
    R = Reader(base, cik, accn, facts)
    rows: list[dict] = []
    quirks: list[dict] = []
    eras: list[dict] = []

    def add(
        dp, status, elems, hits, p0, a0, p1, a1, note="", ev="FILING-CHECKED", period=""
    ):
        m = combine_match(match_txt(p0, a0), match_txt(p1, a1))
        if is_mismatch(m):
            note = (
                note + " | " if note else ""
            ) + "printed vs API disagree: the filing value stands"
            quirks.append(
                {
                    "tag": "+".join(elems),
                    "what": f"{dp.name}: printed {fmt(p0)}/{fmt(p1)} vs companyfacts {fmt(a0)}/{fmt(a1)} (same accession and period)",
                    "where": "+".join(h.page.file for h in hits),
                }
            )
        rows.append(
            {
                "ticker": ticker,
                "data_point": dp.name,
                "status": status,
                "tags": "+".join(e if ":" in e else f"us-gaap:{e}" for e in elems),
                "stmt": "+".join(sorted({h.page.kind or "" for h in hits})),
                "r_page": "+".join(h.page.file for h in hits),
                "label": " + ".join(h.row.label for h in hits),
                "fy0_printed": fmt(p0),
                "fy0_api": fmt(a0),
                "fy1_printed": fmt(p1),
                "fy1_api": fmt(a1),
                "match": m,
                "era_from_note": "",
                "evidence_class": ev,
                "note": " | ".join(
                    x
                    for x in (note, f"accn {accn} period {period}" if hits else "")
                    if x
                ),
            }
        )

    def period(dur: bool, d0: date | None) -> str:
        if d0 is None:
            return ""
        return f"FY ending {d0}" if dur else f"..{d0}"

    found: dict[str, Hit] = {}
    for dp in DPS:
        dur = dp.stmts[0] not in ("BS", "COVER")
        if dp.name == "total_debt":
            read_debt(R, dp, add, quirks)
            continue
        if dp.name == "operating_expenses":
            read_opex(R, dp, add, found, quirks)
            continue
        h = R.find(dp.stmts, dp.tags)
        if h:
            found[dp.name] = h
            p0, p1, d0, d1 = R.values(h, dp.kind)
            a0, a1 = R.api(h.elem, d0, dur), R.api(h.elem, d1, dur)
            note = ""
            period_s = period(dur, d0)
            if dp.name == "shares_outstanding":
                cls = [r for r in h.page.rows if r.elem == h.elem and not r.is_header]
                if (
                    len({tuple(r.values) for r in cls}) > 1
                ):  # one row per share class: the cell is the class sum
                    yc = year_cols(h.page)
                    p0 = (
                        sum(
                            (scaled(h.page, r, yc[0], "shares") or 0 for r in cls),
                            Decimal(0),
                        )
                        if yc
                        else None
                    )
                    p1 = (
                        sum(
                            (scaled(h.page, r, yc[1], "shares") or 0 for r in cls),
                            Decimal(0),
                        )
                        if len(yc) > 1
                        else None
                    )
                    note = f"class sum of {len(cls)} printed rows: " + "; ".join(
                        r.label for r in cls
                    )
                    h = Hit(
                        h.page,
                        Row(h.elem, " + ".join(r.label for r in cls), [], []),
                        h.elem,
                    )
                note = (
                    (note + " | " if note else "")
                    + "balance-sheet-date count (Dhairya 2026-11-12); dei cover never used"
                )
            if h.elem.endswith(
                (
                    "ProfitLoss",
                    "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
                    "ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest",
                )
            ):
                note = (
                    "only the total including noncontrolling interest is printed with a standard tag; the parent line is "
                    + ("custom or absent" if True else "")
                )
            if dp.name == "accounts_receivable" and not h.elem.endswith(
                ("AccountsReceivableNetCurrent", "AccountsReceivableNet")
            ):
                rec = [
                    r
                    for r in h.page.rows
                    if not r.is_header
                    and re.search(r"receivable", r.label, re.IGNORECASE)
                ]
                if len(rec) > 1:
                    found.pop(dp.name, None)
                    add(
                        dp,
                        "not_presented",
                        [],
                        [],
                        None,
                        None,
                        None,
                        None,
                        f"the face prints {len(rec)} receivables lines ("
                        + "; ".join(f"'{r.label}' {r.elem}" for r in rec)
                        + f") on {h.page.file}: the wider tag {short(h.elem)} is not the single receivables line "
                        "(Dhairya 2026-11-12)",
                    )
                    continue
                note = f"wider tag {short(h.elem)} is the single receivables line on {h.page.file} (Dhairya 2026-11-12)"
            if (
                dp.name == "revenue"
                and "Revenue" not in h.elem
                and "Sales" not in h.elem
            ):
                note = "revenue line tag " + short(h.elem)
            if (
                re.search(r"\band\b|, net of|including", h.row.label, re.IGNORECASE)
                and dp.kind == "money"
                and dp.name
                not in (
                    "cash_and_equivalents",
                    "ppe_net",
                    "sga_expense",
                    "research_and_development",
                    "comprehensive_income",
                    "cfo",
                    "cash_flow_investing",
                    "cash_flow_financing",
                    "depreciation_and_amortization",
                    "income_before_tax",
                    "accounts_receivable",
                    "goodwill",
                    "amortization_of_intangibles",
                )
            ):
                note = (
                    note + " | " if note else ""
                ) + f"label '{h.row.label}': check perimeter"
            add(dp, "mapped", [h.elem], [h], p0, a0, p1, a1, note, period=period_s)
            continue
        if dp.combined:
            h = R.find(dp.stmts, dp.combined)
            if h:
                p0, p1, d0, d1 = R.values(h, dp.kind)
                add(
                    dp,
                    "combined",
                    [h.elem],
                    [h],
                    p0,
                    R.api(h.elem, d0, dur),
                    p1,
                    R.api(h.elem, d1, dur),
                    f"'{h.row.label}' = combined line",
                    period=period(dur, d0),
                )
                continue
        if dp.name == "sga_expense":
            parts = [
                R.find(("IS",), (t,))
                for t in (
                    "GeneralAndAdministrativeExpense",
                    "SellingAndMarketingExpense",
                    "SellingExpense",
                    "MarketingAndAdvertisingExpense",
                )
            ]
            parts = [x for x in parts if x]
            if len(parts) >= 2:
                vs = [R.values(x, "money") for x in parts]
                p0 = sum((v[0] or 0 for v in vs), Decimal(0))
                p1 = sum((v[1] or 0 for v in vs), Decimal(0))
                d0, d1 = vs[0][2], vs[0][3]
                a0s = [R.api(x.elem, d0, True) for x in parts]
                a1s = [R.api(x.elem, d1, True) for x in parts]
                a0 = sum(a0s, Decimal(0)) if None not in a0s else None
                a1 = sum(a1s, Decimal(0)) if None not in a1s else None
                add(
                    dp,
                    "component sum",
                    [x.elem for x in parts],
                    parts,
                    p0,
                    a0,
                    p1,
                    a1,
                    "separate selling and G&A lines on the face",
                    period=period(True, d0),
                )
                continue
            if len(parts) == 1:
                p0, p1, d0, d1 = R.values(parts[0], "money")
                add(
                    dp,
                    "not_presented",
                    [],
                    [],
                    None,
                    None,
                    None,
                    None,
                    f"no SG&A line; only '{parts[0].row.label}' ({short(parts[0].elem)}) printed",
                )
                continue
        if dp.name == "depreciation_and_amortization":
            parts = [R.find(("CF",), (t,)) for t in DA_PARTS]
            parts = [x for x in parts if x]
            if parts:
                vs = [R.values(x, "money") for x in parts]
                p0 = sum((v[0] or 0 for v in vs), Decimal(0))
                p1 = sum((v[1] or 0 for v in vs), Decimal(0))
                d0, d1 = vs[0][2], vs[0][3]
                a0s = [R.api(x.elem, d0, True) for x in parts]
                a1s = [R.api(x.elem, d1, True) for x in parts]
                a0 = sum(a0s, Decimal(0)) if None not in a0s else None
                a1 = sum(a1s, Decimal(0)) if None not in a1s else None
                st = "component sum" if len(parts) > 1 else "mapped"
                note = "printed CF lines: " + "; ".join(
                    f"{x.row.label} ({short(x.elem)})" for x in parts
                )
                if len(parts) == 1 and parts[0].elem.endswith("Depreciation"):
                    add(
                        dp,
                        "not_presented",
                        [],
                        [],
                        None,
                        None,
                        None,
                        None,
                        note
                        + ": depreciation only; no D&A or amortization line on the CF face (notes not read)",
                    )
                    continue
                add(
                    dp,
                    st,
                    [x.elem for x in parts],
                    parts,
                    p0,
                    a0,
                    p1,
                    a1,
                    note,
                    period=period(True, d0),
                )
                continue
        h = R.find_label(dp.stmts, dp.label)
        if h and dp.kind == "money":
            p0, p1, d0, d1 = R.values(h, dp.kind)
            add(
                dp,
                "mapped",
                [h.elem],
                [h],
                p0,
                None,
                p1,
                None,
                f"CUSTOM ELEMENT: printed line '{h.row.label}' carries {h.elem} (not in companyfacts); Tag Expert to rule before any mapping",
                period=period(dur, d0),
            )
            quirks.append(
                {
                    "tag": h.elem,
                    "what": f"custom element for {dp.name}: '{h.row.label}' {fmt(p0)}",
                    "where": h.page.file,
                }
            )
            continue
        kinds = "/".join(dp.stmts)
        have = [k for k in dp.stmts if R.by_kind.get(k)]
        where = "+".join(p.file for k in have for p in R.by_kind[k])
        if have and R.financial and dp.name in OUT_FINANCIAL:
            add(
                dp,
                "OUT",
                [],
                [],
                None,
                None,
                None,
                None,
                f"bank/lender/insurer template (face elements {', '.join(R.financial[:3])}): no "
                f"{dp.name.replace('_', ' ')} line on {where}",
            )
            continue
        if have and R.unclassified and dp.name in OUT_UNCLASSIFIED:
            add(
                dp,
                "OUT",
                [],
                [],
                None,
                None,
                None,
                None,
                f"unclassified balance sheet ({where}): no current subtotal",
            )
            continue
        if not have:
            add(
                dp,
                "not_presented",
                [],
                [],
                None,
                None,
                None,
                None,
                f"no {kinds} statement page found in the filing's R pages",
                "DATA-INFERRED",
            )
        else:
            add(
                dp,
                "not_presented",
                [],
                [],
                None,
                None,
                None,
                None,
                f"no {dp.name.replace('_', ' ')} line on "
                + "+".join(p.file for k in have for p in R.by_kind[k]),
            )

    return {
        "reader": R,
        "rows": rows,
        "quirks": quirks,
        "eras": eras,
        "accession": accn,
        "filed": filed,
    }


def read_opex(R: Reader, dp: DP, add, found: dict, quirks: list) -> None:
    """Dhairya 2026-11-12: operating expenses never include cost of revenue. The printed total when it excludes COGS;
    else the component sum of EVERY face line between gross profit and operating income, tied exactly to GP - OI;
    CostsAndExpenses (or a total) that includes COGS is combined, never opex."""
    ox = R.find(("IS",), ("OperatingExpenses",))
    gp = R.find(("IS",), ("GrossProfit",))
    oi = R.find(("IS",), ("OperatingIncomeLoss",))
    rev, cor = found.get("revenue"), found.get("cost_of_revenue")

    def val(h):
        return R.values(h, "money")

    def gp_less_oi():
        if gp and oi:
            g, o = val(gp), val(oi)
            return (
                g[0] - o[0] if None not in (g[0], o[0]) else None,
                g[1] - o[1] if None not in (g[1], o[1]) else None,
            )
        return None, None

    tie0, tie1 = gp_less_oi()
    if ox:
        p0, p1, d0, d1 = val(ox)
        a0, a1 = R.api(ox.elem, d0, True), R.api(ox.elem, d1, True)
        r0 = val(rev)[0] if rev else None
        o0 = val(oi)[0] if oi else None
        if cor and None not in (r0, o0, p0) and p0 == r0 - o0:
            add(
                dp,
                "combined",
                [ox.elem],
                [ox],
                p0,
                a0,
                p1,
                a1,
                f"'{ox.row.label}' = revenue less operating income: includes cost of revenue, so never opex "
                "(Dhairya 2026-11-12)",
                period=f"FY ending {d0}",
            )
            quirks.append(
                {
                    "tag": ox.elem,
                    "what": f"OperatingExpenses printed as a total that includes cost of revenue ('{ox.row.label}' {fmt(p0)})",
                    "where": ox.page.file,
                }
            )
            return
        note = "printed total excludes cost of revenue"
        if tie0 is not None:
            note += (
                f"; ties GP - OI ({fmt(tie0)})"
                if tie0 == p0
                else f"; GP - OI = {fmt(tie0)} differs (other lines between)"
            )
        add(
            dp,
            "mapped",
            [ox.elem],
            [ox],
            p0,
            a0,
            p1,
            a1,
            note,
            period=f"FY ending {d0}",
        )
        return
    if gp and oi and gp.page is oi.page:
        page = gp.page
        i, j = page.rows.index(gp.row), page.rows.index(oi.row)
        between = [r for r in page.rows[i + 1 : j] if not r.is_header]
        yc = year_cols(page)
        if between and yc:

            def at(r, k):
                return scaled(page, r, yc[k], "money") if len(yc) > k else None

            single = [r for r in between if at(r, 0) == tie0 and len(between) > 1]
            if single:  # an opex subtotal printed with a non-standard element
                r = single[0]
                h = Hit(page, r, r.elem)
                d0 = page.cols[yc[0]][1]
                d1 = page.cols[yc[1]][1] if len(yc) > 1 else None
                add(
                    dp,
                    "mapped",
                    [r.elem],
                    [h],
                    at(r, 0),
                    R.api(r.elem, d0, True),
                    at(r, 1),
                    R.api(r.elem, d1, True),
                    f"opex subtotal '{r.label}' ({r.elem}) ties GP - OI exactly",
                    period=f"FY ending {d0}",
                )
                if not r.elem.startswith("us-gaap:"):
                    quirks.append(
                        {
                            "tag": r.elem,
                            "what": f"custom element for the operating expenses total '{r.label}' {fmt(at(r, 0))}",
                            "where": page.file,
                        }
                    )
                return
            s0 = sum((at(r, 0) or 0 for r in between), Decimal(0))
            s1 = (
                sum((at(r, 1) or 0 for r in between), Decimal(0))
                if len(yc) > 1
                else None
            )
            if s0 == tie0 and (tie1 is None or s1 == tie1):
                hits = [Hit(page, r, r.elem) for r in between]
                d0 = page.cols[yc[0]][1]
                d1 = page.cols[yc[1]][1] if len(yc) > 1 else None
                a0s = [R.api(r.elem, d0, True) for r in between]
                a1s = [R.api(r.elem, d1, True) for r in between]
                add(
                    dp,
                    "component sum",
                    [r.elem for r in between],
                    hits,
                    s0,
                    sum(a0s, Decimal(0)) if None not in a0s else None,
                    s1,
                    sum(a1s, Decimal(0)) if None not in a1s else None,
                    f"every face line between gross profit and operating income ({len(between)}); ties GP - OI exactly "
                    "(Dhairya 2026-11-12)",
                    period=f"FY ending {d0}",
                )
                return
            add(
                dp,
                "not_presented",
                [],
                [],
                None,
                None,
                None,
                None,
                f"the {len(between)} face lines between gross profit and operating income sum to {fmt(s0)}, GP - OI = "
                f"{fmt(tie0)}: no exact tie, so no component sum ({page.file})",
            )
            return
    ce = R.find(("IS",), ("CostsAndExpenses", "BenefitsLossesAndExpenses"))
    if ce:
        p0, p1, d0, d1 = val(ce)
        add(
            dp,
            "combined",
            [ce.elem],
            [ce],
            p0,
            R.api(ce.elem, d0, True),
            p1,
            R.api(ce.elem, d1, True),
            f"'{ce.row.label}' is total costs and expenses"
            + (" including cost of revenue" if cor else "")
            + ": combined, never opex (Dhairya 2026-11-12)",
            period=f"FY ending {d0}",
        )
        return
    pages = "+".join(p.file for p in R.by_kind.get("IS", []))
    add(
        dp,
        "not_presented",
        [],
        [],
        None,
        None,
        None,
        None,
        f"no operating-expenses total and no gross profit + operating income pair on {pages or 'any IS page'}",
        "FILING-CHECKED" if pages else "DATA-INFERRED",
    )


def read_debt(R: Reader, dp: DP, add, quirks) -> None:
    hits: list[Hit] = []
    customs: list[Hit] = []
    for p in R.by_kind.get("BS", []):
        for r in p.rows:
            if r.is_header:
                continue
            name = r.elem.split(":", 1)[-1]
            if r.elem.startswith("us-gaap:") and name in DEBT_TAGS:
                hits.append(Hit(p, r, r.elem))
            elif (
                not r.elem.startswith(("us-gaap:", "dei:"))
                and DEBT_LABEL.search(r.label)
                and not NOT_DEBT_LABEL.search(r.label)
            ):
                customs.append(Hit(p, r, r.elem))
        break  # the first balance-sheet page only
    if not hits and not customs:
        add(
            dp,
            "not_presented",
            [],
            [],
            None,
            None,
            None,
            None,
            "no borrowing line on the balance-sheet face",
        )
        return
    # a total that already contains a part on the same page (LongTermDebt beside Current+Noncurrent) is not double added
    names = {h.elem.split(":")[1] for h in hits}
    drop = set()
    if {
        "LongTermDebtCurrent",
        "LongTermDebtNoncurrent",
    } <= names and "LongTermDebt" in names:
        drop.add("LongTermDebt")
    use = [
        h for h in hits if h.elem.split(":")[1] not in drop | DEBT_NOTE_ONLY
    ] + customs
    vs = [R.values(h, "money") for h in use]
    p0 = sum((v[0] or 0 for v in vs), Decimal(0)) if use else None
    p1 = sum((v[1] or 0 for v in vs), Decimal(0)) if use else None
    d0 = vs[0][2] if vs else None
    d1 = vs[0][3] if vs else None
    a0s = [R.api(h.elem, d0, False) for h in use]
    a1s = [R.api(h.elem, d1, False) for h in use]
    a0 = sum(a0s, Decimal(0)) if use and None not in a0s else None
    a1 = sum(a1s, Decimal(0)) if use and None not in a1s else None
    notes = [
        "face borrowing lines summed (finance leases and current maturities in the notes not read)"
    ]
    if any(h.elem.split(":")[1] in BANK_PERIMETER for h in use):
        notes.append(
            "bank-perimeter lines (FHLB/repo/fed funds/other borrowings) included: bank debt perimeter pending (Standardization Lead)"
        )
    if customs:
        notes.append(
            "custom debt-like lines summed (no companyfacts value, so no API total): "
            + "; ".join(
                f"'{h.row.label}' {h.elem} {fmt(R.values(h, 'money')[0])}"
                for h in customs
            )
        )
        for h in customs:
            quirks.append(
                {
                    "tag": h.elem,
                    "what": f"custom debt-like balance-sheet line '{h.row.label}' {fmt(R.values(h, 'money')[0])}",
                    "where": h.page.file,
                }
            )
    if any(h.elem.split(":")[1] in DEBT_NOTE_ONLY for h in hits):
        notes.append("note-only debt tag printed on the face, not summed")
    status = "component sum" if len(use) > 1 else "mapped"
    add(
        dp,
        status,
        [h.elem for h in use],
        use,
        p0,
        a0,
        p1,
        a1,
        " | ".join(notes),
        period=f"..{d0}" if d0 else "",
    )


# ------------------------------------------------------------------------------------------------ output
COLS = (
    "ticker",
    "data_point",
    "status",
    "tags",
    "stmt",
    "r_page",
    "label",
    "fy0_printed",
    "fy0_api",
    "fy1_printed",
    "fy1_api",
    "match",
    "era_from_note",
    "evidence_class",
    "note",
)


def write(
    res: dict, cik: str, ticker: str, out: Path, day: str, era_results: list[dict]
) -> None:
    R: Reader = res["reader"]
    rows = res["rows"]
    out.mkdir(parents=True, exist_ok=True)
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=COLS, lineterminator="\n")
    w.writeheader()
    for r in rows:
        w.writerow(r)
    (out / f"{ticker}-docmap-{day}.csv").write_text(buf.getvalue())
    pages = "; ".join(f"{p.file} {p.kind or '-'} '{p.title[:70]}'" for p in R.pages)
    md = [
        f"# {ticker} document-first map {day} (read-only, bottom-up)",
        "",
        (
            "Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing, tags from the R-page "
            "element references = MetaLinks equivalent; API = SEC companyfacts, undimensioned, same accession, same "
            "period). DATA-INFERRED rows say so. Read by pipeline/scripts/reads/docmap.py from the raw pages fetched "
            "by the sec-reads-fetch workflow (repo SEC_USER_AGENT, 0.4 req/s)."
        ),
        "",
        "## Filings opened",
        f"- Latest 10-K {res['accession']} (CIK {cik}, filed {res['filed']}, FY ended {R.fy0}, comparative {R.fy1}). Pages: {pages}.",
        f"- companyfacts CIK{cik}.json (one call).",
    ]
    for e in era_results:
        md.append(
            f"- Era 10-K {e['accession']} (FY{e['fy']}, FY0 {e['fy0']}, filed {e['filed']}): full face read."
        )
    md += [
        "",
        (
            "FY0 = the latest fiscal year end; FY1 = prior year. Values in full USD (printed value x the R-page "
            "scale); EPS and dividends per share in USD per share; shares in shares."
        ),
        "",
        "## Data points",
        "| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        tags = r["tags"].replace("us-gaap:", "")
        cell = lambda s: s.replace("|", "/").replace("\n", " ")
        md.append(
            "| "
            + " | ".join(
                cell(x)
                for x in (
                    r["data_point"],
                    r["status"],
                    tags,
                    f"{r['stmt']} {r['r_page']}".strip(),
                    r["label"][:60],
                    r["fy0_printed"],
                    r["fy0_api"],
                    r["fy1_printed"],
                    r["fy1_api"],
                    r["match"],
                    r["evidence_class"],
                    r["note"],
                )
            )
            + " |"
        )
    md += era_md(res.get("era_plan"))
    md += [
        "",
        "## Disagreements with cloud Ritwik",
        "No ranks 301-400 exceptions file from cloud Ritwik on main at read time; nothing to compare.",
        "",
        "## Mismatches (printed vs API)",
    ]
    mm = [r for r in rows if is_mismatch(r["match"])]
    noapi = [
        r["data_point"]
        for r in rows
        if r["match"] == "no API value" and "CUSTOM ELEMENT" not in r["note"]
    ]
    sign = [r["data_point"] for r in rows if "sign differs" in r["match"]]
    if mm:
        for r in mm:
            md.append(
                f"- {r['data_point']}: {r['match']} (printed FY0 {r['fy0_printed']} vs API {r['fy0_api']}; FY1 {r['fy1_printed']} vs {r['fy1_api']}); the filing value stands."
            )
    else:
        md.append(
            "none" + (f" beyond sign differences ({', '.join(sign)})." if sign else ".")
        )
    if noapi:
        md.append(
            f"No companyfacts value for the same accession and period (printed value stands, nothing to compare): {', '.join(noapi)}."
        )
    (out / f"{ticker}-docmap-{day}.md").write_text("\n".join(md) + "\n")


# ------------------------------------------------------------------------------------------------ eras FY2015 -> latest
# Dhairya 2026-11-12: a docmap loads only when every data point's eras cover FY2015 to the latest year. An era is a
# run of fiscal years with the same companyfacts tag signature (the tag the 10-K for that year files for the line;
# for summed points the set of component tags); each era needs one opened 10-K whose face shows it. The FY2015 10-K
# is always opened.
START_FY = 2015
ERA_SETS: dict[str, tuple[str, ...]] = {
    "total_debt": tuple(t for t in DEBT_TAGS if t not in DEBT_NOTE_ONLY),
    "depreciation_and_amortization": DA_PARTS
    + ("DepreciationAmortizationAndAccretionNet", "DepreciationAmortizationAndOther"),
    "operating_expenses": (
        "OperatingExpenses",
        "CostsAndExpenses",
        "GrossProfit",
        "OperatingIncomeLoss",
    ),
    "sga_expense": (
        "SellingGeneralAndAdministrativeExpense",
        "GeneralAndAdministrativeExpense",
        "SellingAndMarketingExpense",
    ),
}


def tenks(facts: Facts) -> dict[int, tuple[str, date, str]]:
    """{fiscal year (companyfacts fy): (accession, FY0 end, filed)} for original 10-K / 10-KT filings."""
    by_acc: dict[str, list] = {}
    for node in facts.d.get("us-gaap", {}).values():
        for lst in node.get("units", {}).values():
            for x in lst:
                # annual duration facts only: an instant can postdate the year end (subsequent events)
                if (
                    x.get("form") not in ("10-K", "10-KT")
                    or not x.get("fy")
                    or "start" not in x
                ):
                    continue
                e = date.fromisoformat(x["end"])
                if not 340 <= (e - date.fromisoformat(x["start"])).days <= 380:
                    continue
                cur = by_acc.setdefault(x["accn"], [x["fy"], e, x["filed"]])
                cur[1] = max(cur[1], e)
    out: dict[int, tuple[str, date, str]] = {}
    for acc, (fy, end, filed) in by_acc.items():
        if fy not in out or filed < out[fy][2]:
            out[fy] = (acc, end, filed)
    return out


def _has(facts: Facts, elem: str, end: date, dur: bool, accn: str) -> bool:
    for x in facts.units(elem):
        if (
            x.get("accn") != accn
            or x.get("end") != end.isoformat()
            or dur != ("start" in x)
        ):
            continue
        if dur and not 340 <= (end - date.fromisoformat(x["start"])).days <= 380:
            continue
        return True
    return False


def year_sig(facts: Facts, dp: DP, end: date, accn: str, first: str = "") -> str:
    dur = dp.stmts[0] not in ("BS", "COVER", "PAR_BS")
    if dp.name in ERA_SETS:
        present = [
            t for t in ERA_SETS[dp.name] if _has(facts, f"us-gaap:{t}", end, dur, accn)
        ]
        return "+".join(sorted(present)) or "-"
    order = ([first] if first else []) + [
        t for t in dp.tags + dp.combined if t != first
    ]
    for t in order:
        q = t if ":" in t else f"us-gaap:{t}"
        if _has(facts, q, end, dur, accn):
            return short(q)
    return "-"


def plan_eras(facts: Facts | None, latest: dict) -> dict:
    if facts is None:
        return {"error": "no companyfacts"}
    tk = tenks(facts)
    lat_fy = next(
        (fy for fy, v in tk.items() if v[0] == latest["accession"]),
        max(tk) if tk else None,
    )
    if lat_fy is None:
        return {"error": "no 10-K in companyfacts"}
    years = [y for y in sorted(tk) if START_FY <= y <= lat_fy]
    if not years:
        years = [lat_fy]
    gaps = [y for y in range(years[0], lat_fy + 1) if y not in tk]
    rows = {r["data_point"]: r for r in latest["rows"]}
    eras: dict[str, list[dict]] = {}
    need: dict[int, str] = {lat_fy: tk[lat_fy][0], years[0]: tk[years[0]][0]}
    for dp in DPS:
        first = (
            rows[dp.name]["tags"].split(":", 1)[-1]
            if "+" not in rows[dp.name]["tags"]
            else ""
        )
        runs: list[dict] = []
        for y in years:
            sig = year_sig(facts, dp, tk[y][1], tk[y][0], first)
            if runs and runs[-1]["sig"] == sig:
                runs[-1]["to"] = y
            else:
                runs.append({"sig": sig, "from": y, "to": y})
        for r in runs:
            if not any(r["from"] <= y <= r["to"] for y in need):
                need[r["to"]] = tk[r["to"]][0]
        eras[dp.name] = runs
    return {
        "latest_fy": lat_fy,
        "first_fy": years[0],
        "reaches_2015": years[0] == START_FY,
        "gaps": gaps,
        "eras": eras,
        "need": {
            y: {"accession": a, "fy0": str(tk[y][1]), "filed": tk[y][2]}
            for y, a in sorted(need.items())
        },
    }


def era_md(plan: dict | None) -> list[str]:
    out = [
        "",
        f"## Eras FY{START_FY} to latest (Dhairya 2026-11-12: every data point must cover FY{START_FY}-latest)",
    ]
    if not plan or plan.get("error"):
        return out + [f"Era plan not possible: {(plan or {}).get('error', 'not run')}."]
    v = plan["verdict"]
    out.append(
        f"Coverage verdict: {'COVERED' if v['covered'] else 'NOT COVERED'} FY{plan['first_fy']}-FY{plan['latest_fy']}"
        + (
            ""
            if plan["reaches_2015"]
            else f"; no FY{START_FY} 10-K in companyfacts (first 10-K FY{plan['first_fy']})"
        )
        + (
            f"; fiscal years with no 10-K in companyfacts: {plan['gaps']}"
            if plan["gaps"]
            else ""
        )
        + (
            f"; data points with an era not yet opened: {', '.join(v['uncovered'])}"
            if v["uncovered"]
            else ""
        )
        + "."
    )
    out += [
        "",
        "| data point | era | companyfacts tag(s) | opened 10-K face (FILING-CHECKED) | covered |",
        "|---|---|---|---|---|",
    ]
    for dp, runs in plan["eras"].items():
        for r in runs:
            ev = "; ".join(r.get("evidence", [])) or "not opened"
            out.append(
                f"| {dp} | FY{r['from']}-{r['to']} | {r['sig']} | {ev.replace('|', '/')} | {'Y' if r.get('evidence') else 'N'} |"
            )
    return out


def era_evidence(plan: dict, reads: dict[int, dict]) -> None:
    """Attach each opened 10-K's face read to the eras it falls in; set the coverage verdict."""
    unc = []
    for dp, runs in plan["eras"].items():
        for r in runs:
            r["evidence"] = []
            for fy, rd in sorted(reads.items()):
                if not r["from"] <= fy <= r["to"]:
                    continue
                row = next(x for x in rd["rows"] if x["data_point"] == dp)
                face = row["tags"].replace("us-gaap:", "") or "-"
                agree = (
                    ""
                    if face == r["sig"]
                    or row["status"] in ("not_presented", "OUT")
                    and r["sig"] == "-"
                    else " (face differs from companyfacts: the face stands)"
                )
                r["evidence"].append(
                    f"FY{fy} {rd['accession']} {row['r_page'] or '-'}: {row['status']} {face} FY0 {row['fy0_printed'] or '-'} [{row['match'] or '-'}]{agree}"
                )
            if not r["evidence"]:
                unc.append(dp)
    plan["verdict"] = {
        "covered": not unc and plan["reaches_2015"] and not plan["gaps"],
        "uncovered": sorted(set(unc)),
    }


def main(argv: list[str]) -> None:
    base, cik, ticker, out = Path(argv[1]), argv[2].zfill(10), argv[3], Path(argv[4])
    day = argv[argv.index("--date") + 1] if "--date" in argv else "2026-11-12"
    summ = json.loads((base / "fetch_summary.json").read_text())
    rec = next(
        r for r in summ if r["cik"] == cik and not r.get("error") and r.get("filed")
    )
    res = read_company(base, cik, ticker, rec["accession"], rec["filed"])
    facts = res["reader"].facts
    plan = plan_eras(facts, res)
    res["era_plan"] = plan
    reads: dict[int, dict] = {}
    era_results: list[dict] = []
    missing: list[dict] = []
    if not plan.get("error"):
        for fy, n in plan["need"].items():
            if n["accession"] == rec["accession"]:
                reads[fy] = res
                continue
            if not (base / cik / n["accession"] / "FilingSummary.xml").exists():
                missing.append(
                    {
                        "cik": cik,
                        "ticker": ticker,
                        "accession": n["accession"],
                        "fy": fy,
                    }
                )
                continue
            reads[fy] = read_company(base, cik, ticker, n["accession"], n["filed"])
            era_results.append(
                {
                    "accession": n["accession"],
                    "fy": fy,
                    "fy0": n["fy0"],
                    "filed": n["filed"],
                }
            )
            res["quirks"] += [
                {**q, "where": f"{n['accession']} {q['where']}"}
                for q in reads[fy]["quirks"]
            ]
        era_evidence(plan, reads)
        for row in res["rows"]:
            runs = plan["eras"][row["data_point"]]
            row["era_from_note"] = "; ".join(
                f"FY{r['from']}-{r['to']} {r['sig']}{'' if r['evidence'] else ' [not opened]'}"
                for r in runs
            )
    if "--plan" in argv:
        print(json.dumps({"ticker": ticker, "missing": missing}))
        return
    write(res, cik, ticker, out, day, era_results)
    counts: dict[str, int] = {}
    for r in res["rows"]:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    print(
        json.dumps(
            {
                "ticker": ticker,
                "cik": cik,
                "accession": rec["accession"],
                "fy0": str(res["reader"].fy0),
                "status": counts,
                "mismatch_rows": sum(1 for r in res["rows"] if is_mismatch(r["match"])),
                "quirks": res["quirks"],
                "era": {
                    k: plan.get(k)
                    for k in (
                        "first_fy",
                        "latest_fy",
                        "reaches_2015",
                        "gaps",
                        "verdict",
                        "error",
                    )
                },
                "era_filings": [e["accession"] for e in era_results],
                "missing": missing,
                "eras_changed": {
                    k: [f"FY{r['from']}-{r['to']} {r['sig']}" for r in v]
                    for k, v in plan.get("eras", {}).items()
                    if len(v) > 1
                },
            },
            default=str,
        )
    )


if __name__ == "__main__":
    main(sys.argv)
