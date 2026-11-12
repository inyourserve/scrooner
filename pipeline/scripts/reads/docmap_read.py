"""Document-first read of one company (stdlib, run with -I): printed statement page -> XBRL tag -> SEC companyfacts.

The method of the ranks 51-100 reads (data-team/companies/reads/ABT-docmap-2026-11-12.md):
  1. the latest 10-K (submissions JSON), its FilingSummary.xml and the statement R pages (IS, CI, BS, BS
     parenthetical, CF, equity and its parenthetical, cover);
  2. every printed face line: label, element (the R page's defref anchor = the XBRL tag), printed values of the
     first two duration (or instant) columns, with the page's scale and the sign as printed;
  3. companyfacts for the same tag, same accession, same period (undimensioned facts only);
  4. per data point: the face line the filer prints for it (standard-tag candidates first, then the label), the
     printed vs API values, and FILING-CHECKED (the page was opened) or a reason;
  5. era check: the data point's candidate tags in companyfacts over the last five fiscal years; when the chosen
     tag does not cover a year that another candidate covers, the 10-K of that era is opened and the same line is
     read from its page.
Every request goes through one throttle (SEC_RATE requests per second, default 0.4) with SEC_USER_AGENT.

usage: docmap_read.py <out_dir> <rank> <ticker> <cik>      (env SEC_USER_AGENT; SEC_RATE optional)
writes <out_dir>/<TICKER>-docmap-<DATE>.md and .csv, and prints one JSON summary line (counts, quirks).
"""

from __future__ import annotations

import csv
import gzip
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

UA = os.environ.get("SEC_USER_AGENT", "")
RATE = float(os.environ.get("SEC_RATE", "0.4"))
DATE = os.environ.get("READ_DATE", "2026-11-12")
_last = [0.0]


def get(url: str) -> bytes:
    if not UA:
        sys.exit("SEC_USER_AGENT is required")
    for attempt in range(5):
        wait = 1.0 / RATE - (time.monotonic() - _last[0])
        if wait > 0:
            time.sleep(wait)
        _last[0] = time.monotonic()
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Encoding": "gzip"})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                body = r.read()
                return gzip.decompress(body) if r.headers.get("Content-Encoding") == "gzip" else body
        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise
            time.sleep(10 * (attempt + 1))
        except (urllib.error.URLError, TimeoutError):
            time.sleep(10 * (attempt + 1))
    raise RuntimeError(f"failed: {url}")


# --- statement pages -----------------------------------------------------------------------------------------

STMT_RX = [
    ("PAR_BS", re.compile(r"(balance sheets?|financial (position|condition)).*parenthetical", re.I)),
    ("PAR_EQ", re.compile(r"(equity|stockholders|shareholders|shareowners|capital).*parenthetical", re.I)),
    ("PAR_IS", re.compile(r"(operations|income|earnings).*parenthetical", re.I)),
    ("CI", re.compile(r"comprehensive (income|loss|earnings)", re.I)),
    ("BS", re.compile(r"balance sheets?|financial (position|condition)|statements? of condition", re.I)),
    ("CF", re.compile(r"cash flows?", re.I)),
    ("EQ", re.compile(r"(changes in|statements? of) .*(equity|stockholders|shareholders|shareowners|capital)|equity", re.I)),
    ("IS", re.compile(r"(statements? of|consolidated) .*(operations|income|earnings)|income statements?|operations", re.I)),
]


def classify_report(short: str) -> str | None:
    for k, rx in STMT_RX:
        if rx.search(short):
            return k
    return None


def filing_reports(cik: int, acc: str) -> tuple[str, list[tuple[str, str, str]]]:
    """(base url, [(kind, short name, R file)]) of the filing's statement reports (first of each kind)."""
    base = f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc.replace('-', '')}/"
    xml = get(base + "FilingSummary.xml").decode("utf-8", "replace")
    out, seen = [], set()
    cover = None
    for m in re.finditer(r"<Report[^>]*>(.*?)</Report>", xml, re.S):
        body = m.group(1)
        f = re.search(r"<HtmlFileName>(.*?)</HtmlFileName>", body)
        s = re.search(r"<ShortName>(.*?)</ShortName>", body)
        cat = re.search(r"<MenuCategory>(.*?)</MenuCategory>", body)
        if not f or not s:
            continue
        short = html.unescape(s.group(1))
        if cover is None and re.search(r"cover|document and entity", short, re.I):
            cover = ("COVER", short, f.group(1))
        if not cat or cat.group(1) != "Statements":
            continue
        kind = classify_report(short)
        if kind and kind not in seen:
            seen.add(kind)
            out.append((kind, short, f.group(1)))
    if cover:
        out.append(cover)
    return base, out


SCALE_RX = re.compile(r"in (thousands|millions|billions)", re.I)


def _num(cell: str) -> Decimal | None:
    t = html.unescape(re.sub(r"<[^>]+>", "", cell)).strip()
    t = t.replace("$", "").replace(",", "").replace("\xa0", " ").strip()
    neg = t.startswith("(") and t.endswith(")")
    t = t.strip("()").strip()
    if not re.fullmatch(r"-?\d+(\.\d+)?", t):
        return None
    try:
        v = Decimal(t)
    except InvalidOperation:
        return None
    return -v if neg else v


def parse_r(page: str) -> dict:
    """Header column labels, scale, and rows [(label, tag, [values per column], is_abstract)] of one R page."""
    title = re.search(r"<th[^>]*class=\"tl\"[^>]*>(.*?)</th>", page, re.S)
    ttl = html.unescape(re.sub(r"<[^>]+>", " ", title.group(1))) if title else ""
    # "$ in Millions" wins; else an "in X" that is not "shares in X" (BALL R2: "shares in Thousands, $ in Millions")
    sm = re.search(r"\$ in (thousands|millions|billions)", ttl, re.I) or next(
        (m for m in SCALE_RX.finditer(ttl) if not re.search(r"shares\s*$", ttl[: m.start()], re.I)), None)
    scale = {"thousands": 10**3, "millions": 10**6, "billions": 10**9}[sm.group(1).lower()] if sm else 1
    per_share_full = re.search(r"except (per share|share)", ttl, re.I) is not None
    shares_scaled = re.search(r"shares in (thousands|millions)", ttl, re.I)
    heads: list[str] = []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", page, re.S):
        if "<th" in tr and "class=\"th\"" in tr:
            heads += [html.unescape(re.sub(r"<[^>]+>", " ", h)).split() for h in re.findall(r"<th[^>]*class=\"th\"[^>]*>(.*?)</th>", tr, re.S)]
    rows = []
    for tr in re.findall(r"<tr[^>]*class=\"(?:r|re|ro|reu|rou|rh)\"[^>]*>(.*?)</tr>", page, re.S):
        lab = re.search(r"<td class=\"pl[^\"]*\"[^>]*>(.*?)</td>", tr, re.S)
        if not lab:
            continue
        tagm = re.search(r"defref_([A-Za-z0-9\-]+)_([A-Za-z0-9]+)", lab.group(1))
        label = html.unescape(re.sub(r"<[^>]+>", "", lab.group(1))).strip()
        cells = re.findall(r"<td class=\"(?:nump|num|text)\"[^>]*>(.*?)</td>", tr, re.S)
        vals = [_num(c) for c in cells]
        tag = f"{tagm.group(1)}:{tagm.group(2)}" if tagm else ""
        rows.append((label, tag, vals))
    return {"title": ttl.strip(), "scale": scale, "per_share_full": per_share_full,
            "shares_scaled": bool(shares_scaled), "shares_scale": (10**3 if shares_scaled and shares_scaled.group(1).lower() == "thousands" else 10**6) if shares_scaled else None,
            "rows": rows}


def scaled(v: Decimal | None, page: dict, unit: str) -> Decimal | None:
    if v is None:
        return None
    if unit == "USD/shares":
        return v.normalize() if v != v.to_integral_value() else v.quantize(Decimal(1))
    if unit == "shares":
        out = v * (page["shares_scale"] or (1 if page["per_share_full"] or page["scale"] == 1 else page["scale"]))
    else:
        out = v * page["scale"]
    return out.quantize(Decimal(1)) if out == out.to_integral_value() else out.normalize()


# --- data points ---------------------------------------------------------------------------------------------

# (data point, statements, unit, candidate standard tags in order, label regex fallback)
DP = [
    ("revenue", ("IS",), "USD", ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax", "RevenueFromContractWithCustomerIncludingAssessedTax", "SalesRevenueNet", "SalesRevenueGoodsNet", "RegulatedAndUnregulatedOperatingRevenue", "RevenuesNetOfInterestExpense"], r"^(total )?(net )?(revenues?|sales)\b"),
    ("cost_of_revenue", ("IS",), "USD", ["CostOfRevenue", "CostOfGoodsAndServicesSold", "CostOfGoodsSold", "CostOfServices"], r"^(total )?costs? of (net )?(revenues?|sales|goods|products)"),
    ("gross_profit", ("IS",), "USD", ["GrossProfit"], r"^gross (profit|margin)"),
    ("operating_income", ("IS",), "USD", ["OperatingIncomeLoss"], r"^(total )?(operating (income|profit|loss)|income from operations)"),
    ("interest_expense", ("IS",), "USD", ["InterestExpense", "InterestExpenseNonoperating", "InterestExpenseDebt", "InterestAndDebtExpense", "InterestExpenseOperating"], r"^interest expense"),
    ("income_before_tax", ("IS",), "USD", ["IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest", "IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments", "IncomeLossFromContinuingOperationsBeforeIncomeTaxesDomestic"], r"before (income )?tax"),
    ("income_tax_expense", ("IS",), "USD", ["IncomeTaxExpenseBenefit"], r"income tax"),
    ("net_income", ("IS",), "USD", ["NetIncomeLoss", "NetIncomeLossAvailableToCommonStockholdersBasic", "ProfitLoss"], r"^net (income|earnings|loss)"),
    ("basic_eps", ("IS",), "USD/shares", ["EarningsPerShareBasic", "EarningsPerShareBasicAndDiluted", "IncomeLossFromContinuingOperationsPerBasicShare"], r"\bbasic\b"),
    ("diluted_eps", ("IS",), "USD/shares", ["EarningsPerShareDiluted", "EarningsPerShareBasicAndDiluted", "IncomeLossFromContinuingOperationsPerDilutedShare"], r"\bdiluted\b"),
    ("weighted_basic_shares", ("IS",), "shares", ["WeightedAverageNumberOfSharesOutstandingBasic", "WeightedAverageNumberOfShareOutstandingBasicAndDiluted"], r"basic"),
    ("weighted_diluted_shares", ("IS",), "shares", ["WeightedAverageNumberOfDilutedSharesOutstanding", "WeightedAverageNumberOfShareOutstandingBasicAndDiluted"], r"diluted"),
    ("dividends_per_share", ("IS", "PAR_EQ", "EQ", "PAR_IS"), "USD/shares", ["CommonStockDividendsPerShareDeclared", "CommonStockDividendsPerShareCashPaid"], r"dividends?.*per (common )?share"),
    ("comprehensive_income", ("CI", "IS"), "USD", ["ComprehensiveIncomeNetOfTax", "ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest"], r"comprehensive (income|loss)"),
    ("cash_and_equivalents", ("BS",), "USD", ["CashAndCashEquivalentsAtCarryingValue", "Cash", "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents"], r"^cash"),
    ("accounts_receivable", ("BS",), "USD", ["AccountsReceivableNetCurrent"], r"receivable"),
    ("inventory", ("BS",), "USD", ["InventoryNet", "InventoryFinishedGoodsNetOfReserves"], r"^(total )?inventor"),
    ("current_assets", ("BS",), "USD", ["AssetsCurrent"], r"^total current assets"),
    ("ppe_net", ("BS",), "USD", ["PropertyPlantAndEquipmentNet", "PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization"], r"property.*(net|equipment)"),
    ("goodwill", ("BS",), "USD", ["Goodwill"], r"^goodwill"),
    ("total_assets", ("BS",), "USD", ["Assets"], r"^total assets"),
    ("accounts_payable", ("BS",), "USD", ["AccountsPayableCurrent", "AccountsPayableTradeCurrent", "AccountsPayableAndAccruedLiabilitiesCurrent"], r"accounts payable"),
    ("current_liabilities", ("BS",), "USD", ["LiabilitiesCurrent"], r"^total current liabilities"),
    ("total_liabilities", ("BS",), "USD", ["Liabilities"], r"^total liabilities$"),
    ("stockholders_equity", ("BS",), "USD", ["StockholdersEquity", "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"], r"total .*(stockholders|shareholders|shareowners).* equity"),
    ("operating_expenses", ("IS",), "USD", ["OperatingExpenses", "CostsAndExpenses"], r"^total (operating )?(costs and )?expenses"),
    ("sga_expense", ("IS",), "USD", ["SellingGeneralAndAdministrativeExpense", "GeneralAndAdministrativeExpense"], r"selling, general|general and administrative"),
    ("research_and_development", ("IS",), "USD", ["ResearchAndDevelopmentExpense", "ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost"], r"research and development"),
    ("interest_income", ("IS",), "USD", ["InvestmentIncomeInterest", "InterestIncomeOther", "InvestmentIncomeInterestAndDividend", "InterestAndOtherIncome"], r"^interest (and other )?income"),
    ("other_income_expense_net", ("IS",), "USD", ["OtherNonoperatingIncomeExpense", "NonoperatingIncomeExpense"], r"^other (income|expense)"),
    ("amortization_of_intangibles", ("CF", "IS"), "USD", ["AmortizationOfIntangibleAssets"], r"^amortization of (acquired )?intangible"),
    ("cf_ar_change", ("CF",), "USD", ["IncreaseDecreaseInAccountsReceivable", "IncreaseDecreaseInReceivables", "IncreaseDecreaseInAccountsAndOtherReceivables"], r"receivable"),
    ("cf_inventory_change", ("CF",), "USD", ["IncreaseDecreaseInInventories"], r"^inventor"),
    ("cf_ap_change", ("CF",), "USD", ["IncreaseDecreaseInAccountsPayable", "IncreaseDecreaseInAccountsPayableTrade", "IncreaseDecreaseInAccountsPayableAndAccruedLiabilities"], r"accounts payable"),
    ("cash_paid_for_interest", ("CF",), "USD", ["InterestPaidNet", "InterestPaid"], r"interest paid|cash paid.*interest"),
    ("cash_paid_for_income_taxes", ("CF",), "USD", ["IncomeTaxesPaidNet", "IncomeTaxesPaid"], r"(income )?taxes paid|cash paid.*taxes"),
    ("deposits", ("BS",), "USD", ["Deposits"], r"^total deposits"),
    ("loans_net", ("BS",), "USD", ["LoansAndLeasesReceivableNetReportedAmount", "LoansAndLeasesReceivableNetOfDeferredIncome"], r"loans.*net"),
    ("total_interest_income", ("IS",), "USD", ["InterestAndDividendIncomeOperating", "InterestIncomeOperating"], r"^total interest (and dividend )?income"),
    ("net_interest_income", ("IS",), "USD", ["InterestIncomeExpenseNet", "InterestIncomeExpenseAfterProvisionForLoanLoss"], r"^net interest income"),
    ("provision_for_credit_losses", ("IS",), "USD", ["ProvisionForLoanLeaseAndOtherLosses", "ProvisionForLoanAndLeaseLosses", "CreditLossExpenseReversal"], r"provision for (credit|loan)"),
    ("noninterest_income", ("IS",), "USD", ["NoninterestIncome"], r"^total non-?interest income"),
    ("noninterest_expense", ("IS",), "USD", ["NoninterestExpense"], r"^total non-?interest expense"),
    ("cfo", ("CF",), "USD", ["NetCashProvidedByUsedInOperatingActivities", "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations"], r"operating activities"),
    ("cash_flow_investing", ("CF",), "USD", ["NetCashProvidedByUsedInInvestingActivities", "NetCashProvidedByUsedInInvestingActivitiesContinuingOperations"], r"investing activities"),
    ("cash_flow_financing", ("CF",), "USD", ["NetCashProvidedByUsedInFinancingActivities", "NetCashProvidedByUsedInFinancingActivitiesContinuingOperations"], r"financing activities"),
    ("capex", ("CF",), "USD", ["PaymentsToAcquirePropertyPlantAndEquipment", "PaymentsToAcquireProductiveAssets", "PaymentsForCapitalImprovements", "PaymentsToAcquireOtherPropertyPlantAndEquipment"], r"(capital expenditures|purchases? of property|additions to property)"),
    ("depreciation_and_amortization", ("CF",), "USD", ["DepreciationDepletionAndAmortization", "DepreciationAmortizationAndAccretionNet", "DepreciationAndAmortization", "Depreciation"], r"^depreciation"),
    ("sbc", ("CF",), "USD", ["ShareBasedCompensation", "AllocatedShareBasedCompensationExpense"], r"(stock|share)-based compensation"),
    ("dividends_paid", ("CF",), "USD", ["PaymentsOfDividendsCommonStock", "PaymentsOfDividends", "PaymentsOfOrdinaryDividends"], r"dividends? paid|cash dividends"),
    ("share_buybacks", ("CF",), "USD", ["PaymentsForRepurchaseOfCommonStock", "PaymentsForRepurchaseOfEquity"], r"(repurchase|purchase)s? of (common |treasury )?(stock|shares)"),
]
DPMAP = {d[0]: d for d in DP}
BANK_DP = {"deposits", "loans_net", "total_interest_income", "net_interest_income", "provision_for_credit_losses", "noninterest_income", "noninterest_expense"}
DEBT_TAGS = ["LongTermDebtCurrent", "LongTermDebtNoncurrent", "LongTermDebt", "ShortTermBorrowings", "CommercialPaper", "DebtCurrent",
             "LongTermDebtAndCapitalLeaseObligations", "LongTermDebtAndCapitalLeaseObligationsCurrent", "OtherLongTermDebtNoncurrent",
             "LinesOfCreditCurrent", "ShortTermDebtAndCurrentPortionOfLongTermDebt", "SeniorNotes", "ConvertibleNotesPayable",
             "LongTermDebtCurrentAndNoncurrent", "NotesPayable", "DebtLongtermAndShorttermCombinedAmount"]


def pick(stmts: dict, dp: tuple) -> tuple[str, str, tuple] | None:
    """(status, stmt, row) the face prints for the data point: a candidate standard tag first, else a label match."""
    name, kinds, unit, tags, rx = dp
    for k in kinds:
        page = stmts.get(k)
        if not page:
            continue
        for t in tags:
            for row in page["rows"]:
                if row[1] == f"us-gaap:{t}" and any(v is not None for v in row[2]):
                    return "mapped", k, row
    lrx = re.compile(rx, re.I)
    for k in kinds:
        page = stmts.get(k)
        if not page:
            continue
        for row in page["rows"]:
            if row[1] and lrx.search(row[0]) and any(v is not None for v in row[2]):
                if name in ("weighted_basic_shares", "weighted_diluted_shares") and "share" not in row[0].lower():
                    continue
                if name in ("basic_eps", "diluted_eps") and unit == "USD/shares" and "share" not in (row[0] + row[1]).lower():
                    continue
                std = row[1].startswith("us-gaap:")
                return ("mapped_other" if std else "mapped_custom"), k, row
    return None


def api_value(facts: dict, tag: str, acc: str, end: str | None, duration: bool, unit: str):
    tx, _, nm = tag.partition(":")
    tx = {"us-gaap": "us-gaap", "dei": "dei", "ifrs-full": "ifrs-full", "srt": "srt"}.get(tx)
    if not tx:
        return None
    units = facts.get("facts", {}).get(tx, {}).get(nm, {}).get("units", {})
    best = None
    for u, rows in units.items():
        if unit == "USD/shares" and "/shares" not in u:
            continue
        if unit == "shares" and u != "shares":
            continue
        if unit == "USD" and u != "USD":
            continue
        for r in rows:
            if r.get("accn") != acc:
                continue
            if end and r.get("end") != end:
                continue
            if duration:
                if not r.get("start"):
                    continue
                days = (date.fromisoformat(r["end"]) - date.fromisoformat(r["start"])).days
                if not 330 <= days <= 400:
                    continue
            elif r.get("start"):
                continue
            best = Decimal(str(r["val"]))
    return best


def fy_ends(facts: dict, acc: str) -> list[str]:
    """The fiscal-year ends (FY0, FY1) the 10-K's own facts report, from dei/us-gaap duration facts of ~1 year."""
    ends = {}
    for tx in ("us-gaap",):
        for nm in ("Assets", "NetIncomeLoss", "Revenues", "NetCashProvidedByUsedInOperatingActivities", "ProfitLoss", "StockholdersEquity"):
            for rows in facts.get("facts", {}).get(tx, {}).get(nm, {}).get("units", {}).values():
                for r in rows:
                    if r.get("accn") == acc:
                        ends[r["end"]] = ends.get(r["end"], 0) + 1
    return sorted(ends, reverse=True)[:2]


def fiscal_label(end: str) -> int:
    """The fiscal year a period end belongs to: a year ending January-March is the prior fiscal year (retail FYE)."""
    d = date.fromisoformat(end)
    return d.year if d.month >= 4 else d.year - 1


def era_tags(facts: dict, cands: list[str], unit: str, first: int = 2015) -> dict[str, list[int]]:
    """{tag: [fiscal years it is filed for in a 10-K]} for the candidate tags, FY`first` to the latest year."""
    out: dict[str, set[int]] = {}
    for t in cands:
        units = facts.get("facts", {}).get("us-gaap", {}).get(t, {}).get("units", {})
        for u, rows in units.items():
            if (unit == "USD" and u != "USD") or (unit == "USD/shares" and "/shares" not in u) or (unit == "shares" and u != "shares"):
                continue
            for r in rows:
                if r.get("form", "").startswith("10-K") and r.get("fp") == "FY":
                    if r.get("start"):
                        days = (date.fromisoformat(r["end"]) - date.fromisoformat(r["start"])).days
                        if not 330 <= days <= 400:
                            continue
                    y = fiscal_label(r["end"])
                    if y >= first:
                        out.setdefault(t, set()).add(y)
    return {t: sorted(s) for t, s in out.items()}


def fy2015_accession(facts: dict) -> str | None:
    """The original 10-K of fiscal year 2015: the earliest-filed 10-K whose own facts end in fiscal year 2015."""
    best = None
    for nm in ("Assets", "NetIncomeLoss", "StockholdersEquity", "ProfitLoss", "NetCashProvidedByUsedInOperatingActivities"):
        for rows in facts.get("facts", {}).get("us-gaap", {}).get(nm, {}).get("units", {}).values():
            for r in rows:
                if r.get("form") in ("10-K", "10-KT") and r.get("fy") in (2015,) and fiscal_label(r["end"]) == 2015:
                    if best is None or r.get("filed", "") < best[0]:
                        best = (r.get("filed", ""), r["accn"])
    return best[1] if best else None


def era_accession(facts: dict, tag: str, unit: str) -> str | None:
    """The latest 10-K accession that files the tag for its own fiscal year."""
    units = facts.get("facts", {}).get("us-gaap", {}).get(tag, {}).get("units", {})
    best = None
    for rows in units.values():
        for r in rows:
            if r.get("form", "").startswith("10-K") and r.get("fp") == "FY" and r.get("fy") and r["end"][:4] == str(r["fy"]):
                if best is None or r["end"] > best[0]:
                    best = (r["end"], r["accn"])
    return best[1] if best else None


def read_statements(cik: int, acc: str, kinds: tuple[str, ...] | None = None) -> dict:
    """The filing's statement pages; only `kinds` when given (an era 10-K needs one page, not all)."""
    base, reps = filing_reports(cik, acc)
    stmts = {}
    for kind, short, rfile in reps:
        if kinds is not None and kind not in kinds:
            continue
        page = parse_r(get(base + rfile).decode("utf-8", "replace"))
        page["short"], page["rfile"] = short, rfile
        stmts[kind] = page
    return stmts


def _first(page: dict, row: tuple, i: int = 0, unit: str = "USD"):
    nn = [v for v in row[2] if v is not None]
    return scaled(nn[i], page, unit) if len(nn) > i else None


def opex_rule(stmts: dict, facts: dict, acc: str, fy0: str, fy1: str | None, row) -> bool:
    """Dhairya ruling 2026-11-12: operating_expenses never includes cost of revenue. A printed total opex line that
    excludes COGS is mapped; a total that includes COGS (CostsAndExpenses) is combined, never opex; otherwise the
    component sum of EVERY face line between gross profit and operating income, tied exactly to GP - OI.
    Returns True when it wrote the row."""
    page = stmts.get("IS")
    if not page:
        return False
    rows_ = page["rows"]
    def idx(pred):
        return next((k for k, x in enumerate(rows_) if pred(x) and any(v is not None for v in x[2])), None)
    i_rev = idx(lambda x: x[1].split(":")[-1] in DP[0][3])
    i_cor = idx(lambda x: x[1].split(":")[-1] in DP[1][3] or x[1].endswith("CostOfGoodsAndServiceExcludingDepreciationDepletionAndAmortization"))
    i_gp = idx(lambda x: x[1] == "us-gaap:GrossProfit")
    i_oi = idx(lambda x: x[1] == "us-gaap:OperatingIncomeLoss")
    i_tot = idx(lambda x: x[1].split(":")[-1] in ("OperatingExpenses", "CostsAndExpenses", "OperatingCostsAndExpenses")
                or re.search(r"^total (operating )?(costs and )?expenses", x[0], re.I))
    v = lambda k, c=0: _first(page, rows_[k], c) if k is not None else None  # noqa: E731
    acc_tail = f"accn {acc} FY0 {fy0}" + (f" FY1 {fy1}" if fy1 else "")
    if i_tot is not None:
        t = rows_[i_tot]
        tv, rev, oi, gp = v(i_tot), v(i_rev), v(i_oi), v(i_gp)
        includes = (rev is not None and oi is not None and tv is not None and abs(tv) == abs(rev - oi)) or (
            i_cor is not None and i_cor < i_tot and (i_gp is None or i_gp > i_tot))
        excludes = gp is not None and oi is not None and tv is not None and abs(tv) == abs(gp - oi)
        a0 = api_value(facts, t[1], acc, fy0, True, "USD")
        a1 = api_value(facts, t[1], acc, fy1, True, "USD") if fy1 else None
        if includes and not excludes:
            row("operating_expenses", "combined", "IS", t, tv, a0, v(i_tot, 1), a1,
                f"'{t[0][:60]}' ({t[1]}) includes cost of revenue: combined, never opex (Dhairya ruling 2026-11-12)")
            return True
        row("operating_expenses", "mapped", "IS", t, tv, a0, v(i_tot, 1), a1,
            "printed total opex, excludes cost of revenue" + (" (ties GP - OI)" if excludes else ""))
        return True
    if i_gp is not None and i_oi is not None and i_gp < i_oi:
        comp = [x for x in rows_[i_gp + 1:i_oi] if x[1] and any(y is not None for y in x[2])]
        if not comp:
            return False
        s0 = sum((_first(page, x) or Decimal(0) for x in comp), Decimal(0))
        gp, oi = v(i_gp), v(i_oi)
        tie = gp is not None and oi is not None and abs(s0) == abs(gp - oi)
        if not tie:
            row("operating_expenses", "not_presented", "IS", None, None, None, None, None,
                f"no total opex line; the {len(comp)} lines between gross profit and operating income sum to {s0}, GP - OI = "
                f"{gp - oi if gp is not None and oi is not None else ''}: no exact tie, not served")
            return True
        aps = [api_value(facts, x[1], acc, fy0, True, "USD") for x in comp]
        a_sum = sum(aps, Decimal(0)) if all(a is not None for a in aps) else None
        s1 = [_first(page, x, 1) for x in comp]
        row("operating_expenses", "component sum", "IS", (" + ".join(x[0][:30] for x in comp), ";".join(x[1] for x in comp), []),
            s0, a_sum, sum(s1, Decimal(0)) if all(y is not None for y in s1) else None, None,
            f"every face line between gross profit and operating income ({len(comp)}), ties GP - OI = {gp - oi}", tags=";".join(x[1] for x in comp))
        return True
    return False



def main(out_dir: str, rank: str, ticker: str, cik_s: str) -> None:
    cik = int(cik_s)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    sub = json.loads(get(f"https://data.sec.gov/submissions/CIK{cik:010d}.json"))
    rec = sub["filings"]["recent"]
    tenks = [(rec["filingDate"][i], rec["accessionNumber"][i], rec["form"][i], rec["reportDate"][i])
             for i in range(len(rec["form"])) if rec["form"][i] in ("10-K", "10-KT")]
    if not tenks:
        print(json.dumps({"rank": rank, "ticker": ticker, "status": "no_10k_in_submissions"}))
        return
    filed, acc, form, period = max(tenks)
    stmts = read_statements(cik, acc)
    facts = json.loads(get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json"))
    ends = fy_ends(facts, acc)
    acc15 = fy2015_accession(facts)
    stmts15, ends15 = {}, []
    if acc15 and acc15 != acc:
        try:
            stmts15 = read_statements(cik, acc15, ("IS", "CI", "BS", "PAR_BS", "CF", "EQ", "PAR_EQ", "PAR_IS"))
            ends15 = fy_ends(facts, acc15)
        except Exception as e:  # noqa: BLE001
            stmts15 = {"_error": type(e).__name__}
    fy0 = ends[0] if ends else period
    fy1 = ends[1] if len(ends) > 1 else None
    rows, quirks = [], []

    def read15(dp_name: str) -> dict:
        """The FY2015 10-K's own face line for the data point: tag, printed, API, match (the FY2015 era read)."""
        if not acc15:
            return {"fy2015_note": "no FY2015 10-K for this CIK in companyfacts (first 10-K later): era starts at the first 10-K"}
        if acc15 == acc:
            return {"fy2015_accession": acc15, "fy2015_note": "the latest 10-K is the FY2015 10-K"}
        if "_error" in stmts15:
            return {"fy2015_accession": acc15, "fy2015_note": f"FY2015 10-K not readable ({stmts15['_error']})"}
        e0 = ends15[0] if ends15 else None
        if dp_name in DPMAP:
            dp = DPMAP[dp_name]
            hit = pick(stmts15, dp)
            if hit is None:
                return {"fy2015_accession": acc15, "fy2015_status": "not_presented", "fy2015_note": "no face line in the FY2015 10-K"}
            k, rr = hit[1], hit[2]
            unit = dp[2]
            pv = [scaled(v, stmts15[k], unit) for v in rr[2] if v is not None]
            av = api_value(facts, rr[1], acc15, e0, k not in ("BS", "PAR_BS"), unit)
        elif dp_name == "shares_outstanding":
            k = next((kk for kk in ("BS", "PAR_BS") if any(x[1] == "us-gaap:CommonStockSharesOutstanding" for x in stmts15.get(kk, {}).get("rows", []))), None)
            if not k:
                return {"fy2015_accession": acc15, "fy2015_status": "not_presented", "fy2015_note": "no BS-date share count in the FY2015 10-K"}
            rr = next(x for x in stmts15[k]["rows"] if x[1] == "us-gaap:CommonStockSharesOutstanding")
            pv = [scaled(v, stmts15[k], "shares") for v in rr[2] if v is not None]
            av = api_value(facts, rr[1], acc15, e0, False, "shares")
        elif dp_name == "total_debt":
            k = "BS"
            lines = [x for x in stmts15.get("BS", {}).get("rows", []) if x[1].split(":")[-1] in DEBT_TAGS and any(v is not None for v in x[2])]
            if not lines:
                return {"fy2015_accession": acc15, "fy2015_status": "not_presented", "fy2015_note": "no standard debt line in the FY2015 10-K"}
            rr = ("", ";".join(x[1] for x in lines), [])
            pv = [sum((scaled(next(v for v in x[2] if v is not None), stmts15["BS"], "USD") for x in lines), Decimal(0))]
            aa = [api_value(facts, x[1], acc15, e0, False, "USD") for x in lines]
            av = sum(aa, Decimal(0)) if all(a is not None for a in aa) else None
        else:
            return {"fy2015_accession": acc15}
        m = "" if not pv or av is None else ("Y" if abs(pv[0]) == abs(av) else "N")
        return {"fy2015_accession": acc15, "fy2015_status": "face_line", "fy2015_tag": rr[1], "fy2015_r_page": stmts15.get(k, {}).get("rfile", ""),
                "fy2015_printed": pv[0] if pv else "", "fy2015_api": av if av is not None else "", "fy2015_match": m}

    def row(dp_name, status, kind, r, fy0p, fy0a, fy1p, fy1a, note, era="", tags=""):
        page = stmts.get(kind, {}) if kind else {}
        if fy0p is not None and fy0a is not None:
            if fy0p == fy0a:
                match = "Y"
            elif fy0p == -fy0a:
                match = "Y (sign differs: printed in parentheses/negated label)"
            else:
                match = "N"
        else:
            match = ""
        rows.append({"ticker": ticker, "data_point": dp_name, "status": status, "tags": tags or (r[1] if r else ""),
                     "stmt": kind or "", "r_page": page.get("rfile", ""), "label": r[0] if r else "",
                     "fy0_printed": fy0p if fy0p is not None else "", "fy0_api": fy0a if fy0a is not None else "",
                     "fy1_printed": fy1p if fy1p is not None else "", "fy1_api": fy1a if fy1a is not None else "",
                     "match": match, "era_from_note": era, "evidence_class": "FILING-CHECKED" if kind else "FILING-CHECKED (absence on the opened statement pages)",
                     "note": (note + " | " if note else "") + f"accn {acc} FY0 {fy0}" + (f" FY1 {fy1}" if fy1 else ""),
                     **read15(dp_name)})
        r15 = rows[-1]
        # era coverage FY2015 .. latest (Dhairya 2026-11-12: a docmap loads only when every data point's eras cover it)
        if status not in ("not_presented", "OUT") and dp_name in DPMAP and fy0:
            dpd = DPMAP[dp_name]
            tagset_ = {t.split(":")[-1] for t in (tags or (r[1] if r else "")).split(";") if t}
            cands_ = list(dict.fromkeys([*dpd[3], *tagset_, (r15.get("fy2015_tag") or "").split(":")[-1]]))
            et_ = era_tags(facts, [c for c in cands_ if c], dpd[2])
            if len(tagset_) > 1:  # a component sum: a year counts when every component is filed
                yrs = set.intersection(*(set(et_.get(t, [])) for t in tagset_))
            else:
                yrs = {y for ys in et_.values() for y in ys}
            latest = fiscal_label(fy0)
            unc = [y for y in range(2015, latest + 1) if y not in yrs]
            r15["era_coverage"] = "FY2015-FY%d covered" % latest if not unc else "uncovered FY: " + ",".join(map(str, unc))
        if r15.get("fy2015_match") == "N":
            quirks.append((dp_name, r15.get("fy2015_tag", ""), f"FY2015 10-K {acc15}: printed {r15.get('fy2015_printed')} vs companyfacts {r15.get('fy2015_api')}", ""))
        if r15.get("fy2015_tag") and r and r15["fy2015_tag"] != r[1] and status not in ("not_presented", "OUT"):
            quirks.append((dp_name, r15["fy2015_tag"], f"FY2015 10-K {acc15} prints the line under {r15['fy2015_tag']}; the latest 10-K uses {r[1]}", ""))
        if match == "N":
            quirks.append((dp_name, r[1] if r else "", f"printed {fy0p} vs companyfacts {fy0a} (same accession, FY0): the filing decides, the printed value stands", kind))

    is_tags = {r[1].split(":")[-1] for r in stmts.get("IS", {}).get("rows", [])}
    bank = bool(is_tags & {"InterestIncomeExpenseNet", "NoninterestExpense", "NoninterestIncome", "InterestIncomeExpenseAfterProvisionForLoanLoss"})
    for dp in DP:
        name, kinds, unit, cands, _ = dp
        if name == "accounts_receivable" and stmts.get("BS") and (pick(stmts, dp) or ("",))[0] != "mapped":
            bsp = stmts["BS"]
            recv = [x for x in bsp["rows"] if re.search(r"receivable", x[0], re.I) and x[1] and any(v is not None for v in x[2])
                    and not re.search(r"noncurrent|long-term|non-current", x[0], re.I)]
            if len(recv) == 1 and recv[0][1].split(":")[-1] in ("ReceivablesNetCurrent", "AccountsReceivableNet", "AccountsNotesAndLoansReceivableNetCurrent", "AccountsAndOtherReceivablesNetCurrent"):
                x = recv[0]
                v = [scaled(y, bsp, unit) for y in x[2] if y is not None]
                row(name, "mapped", "BS", x, v[0] if v else None, api_value(facts, x[1], acc, fy0, False, unit),
                    v[1] if len(v) > 1 else None, api_value(facts, x[1], acc, fy1, False, unit) if fy1 else None,
                    f"wider receivables tag {x[1]}: the single receivables line on the BS face ({bsp['rfile']}), Dhairya ruling 2026-11-12")
                continue
            if recv and not any(x[1].endswith(":AccountsReceivableNetCurrent") for x in recv):
                row(name, "not_presented", None, None, None, None, None, None,
                    f"no AccountsReceivableNetCurrent line; {len(recv)} receivables line(s) on {bsp['rfile']} ({'; '.join(x[1] + ' ' + repr(x[0][:40]) for x in recv[:3])}): a wider tag maps only when it is the single receivables line")
                continue
        if name == "operating_expenses":
            done = opex_rule(stmts, facts, acc, fy0, fy1, row)
            if done:
                continue
        if name in BANK_DP and not bank:
            row(name, "OUT", None, None, None, None, None, None, "not a bank (no net interest / noninterest lines on the income statement)")
            continue
        hit = pick(stmts, dp)
        if hit is None:
            note = f"no {name} line on {'/'.join(k for k in kinds if k in stmts) or 'the statements found'}"
            for t in cands:
                if api_value(facts, f"us-gaap:{t}", acc, fy0, kinds[0] not in ("BS",), unit) is not None:
                    note += f"; companyfacts carries {t} for this accession (a note fact, not a face line)"
                    break
            row(name, "not_presented", None, None, None, None, None, None, note)
            continue
        status, kind, r = hit
        page = stmts[kind]
        dur = kind not in ("BS", "PAR_BS")
        vals = [scaled(v, page, unit) for v in r[2] if v is not None]
        p0 = vals[0] if vals else None
        p1 = vals[1] if len(vals) > 1 else None
        a0 = api_value(facts, r[1], acc, fy0, dur, unit)
        a1 = api_value(facts, r[1], acc, fy1, dur, unit) if fy1 else None
        note = ""
        if status == "mapped_custom":
            note = f"custom tag {r[1]}: no companyfacts series"
            quirks.append((name, r[1], f"the face line '{r[0][:70]}' uses a custom tag", kind))
        elif status == "mapped_other":
            note = f"standard tag outside the candidate list: {r[1]}"
            quirks.append((name, r[1], f"the face line '{r[0][:70]}' carries a tag outside the data point's candidates", kind))
        if a0 is None and status != "mapped_custom":
            note += ("; " if note else "") + "no companyfacts fact for this accession/period"
        era = ""
        if status == "mapped":
            et = era_tags(facts, cands, unit)
            chosen = r[1].split(":")[1]
            mine = set(et.get(chosen, []))
            others = {t: ys for t, ys in et.items() if t != chosen and set(ys) - mine}
            if others:
                era = f"ERA-CHECK: chosen tag {sorted(mine)}; others since FY2015: " + "; ".join(f"{t} {ys}" for t, ys in others.items())
                for t, ys in others.items():
                    eacc = era_accession(facts, t, unit)
                    if not eacc or eacc == acc:
                        continue
                    try:
                        est = read_statements(cik, eacc, kinds)
                    except Exception as e:  # noqa: BLE001
                        era += f" | era 10-K {eacc} not readable ({type(e).__name__})"
                        continue
                    ehit = None
                    for k in kinds:
                        for rr in est.get(k, {}).get("rows", []):
                            if rr[1] == f"us-gaap:{t}" and any(v is not None for v in rr[2]):
                                ehit = (k, rr)
                                break
                        if ehit:
                            break
                    if ehit:
                        ev = [scaled(v, est[ehit[0]], unit) for v in ehit[1][2] if v is not None]
                        eends = fy_ends(facts, eacc)
                        ea = api_value(facts, ehit[1][1], eacc, eends[0] if eends else None, dur, unit)
                        same = ev and ea is not None and abs(ev[0]) == abs(ea)
                        era += f" | era 10-K {eacc} {est[ehit[0]]['rfile']} '{ehit[1][0][:50]}' {t} printed {ev[0] if ev else ''} api {ea} {'Y' if same else 'N'} FILING-CHECKED"
                        quirks.append((name, f"us-gaap:{t}", f"era change: {t} in 10-K {eacc} -> {chosen} in {acc}", ehit[0]))
                    else:
                        era += f" | era 10-K {eacc}: {t} not on its face pages (note-only fact)"
        if name == "cf_ap_change" and (r[1].endswith("AndAccruedLiabilities") or re.search(r"\band\b|accrued|other", r[0], re.I)):
            row(name, "combined", kind, r, p0, a0, p1, a1, f"'{r[0][:70]}' = combined", era)
            continue
        if name == "depreciation_and_amortization" and r[1].split(":")[-1] == "Depreciation":
            amort = [x for x in page["rows"] if re.search(r"^us-gaap:Amortization(OfIntangibleAssets|OfDeferredCharges)?$|^us-gaap:AmortizationOfIntangibleAssets", x[1]) and any(v is not None for v in x[2])]
            if amort:
                am = amort[0]
                av = [scaled(v, page, unit) for v in am[2] if v is not None]
                aa0 = api_value(facts, am[1], acc, fy0, dur, unit)
                aa1 = api_value(facts, am[1], acc, fy1, dur, unit) if fy1 else None
                add = lambda x, y: (x + y) if x is not None and y is not None else None  # noqa: E731
                row(name, "component sum", kind, (f"{r[0][:40]} + {am[0][:40]}", f"{r[1]};{am[1]}", []),
                    add(p0, av[0] if av else None), add(a0, aa0), add(p1, av[1] if len(av) > 1 else None), add(a1, aa1),
                    f"two printed CF lines: {r[0][:40]} {p0} + {am[0][:40]} {av[0] if av else ''}", era, tags=f"{r[1]};{am[1]}")
                continue
        row(name, "mapped" if status.startswith("mapped") else status, kind, r, p0, a0, p1, a1, note, era)

    # total debt: the printed debt lines of the balance sheet, summed (instants never derived beyond the printed lines)
    bs = stmts.get("BS")
    if bs:
        lines = [r for r in bs["rows"] if r[1].split(":")[-1] in DEBT_TAGS and any(v is not None for v in r[2])]
        if lines:
            p0 = sum((scaled(next(v for v in r[2] if v is not None), bs, "USD") for r in lines), Decimal(0))
            a0s = [api_value(facts, r[1], acc, fy0, False, "USD") for r in lines]
            a0 = sum(a0s, Decimal(0)) if all(a is not None for a in a0s) else None
            row("total_debt", "component sum" if len(lines) > 1 else "mapped", "BS", (" + ".join(r[0][:40] for r in lines), ";".join(r[1] for r in lines), []),
                p0, a0, None, None, f"{len(lines)} printed debt line(s)", tags=";".join(r[1] for r in lines))
        else:
            row("total_debt", "not_presented", "BS", None, None, None, None, None, "no debt line under a standard debt tag on the balance sheet (custom or lease-only lines are not summed)")
    # shares outstanding (Dhairya ruling 2026-11-12): us-gaap:CommonStockSharesOutstanding at the balance-sheet
    # date (BS face or its parenthetical; a class sum when the page prints one line per class); never the dei cover count
    so = []
    for k in ("BS", "PAR_BS"):
        pg = stmts.get(k)
        if pg:
            so = [(k, x) for x in pg["rows"] if x[1] == "us-gaap:CommonStockSharesOutstanding" and any(v is not None for v in x[2])]
            if so:
                break
    if so:
        k, x = so[0]
        pg = stmts[k]
        vals = [scaled(v, pg, "shares") for v in x[2] if v is not None]
        a0 = api_value(facts, x[1], acc, fy0, False, "shares")
        if len(so) > 1:  # one line per class: the class sum at the first (latest) column
            tot = sum((scaled(next(v for v in xx[2] if v is not None), pg, "shares") for _, xx in so), Decimal(0))
            row("shares_outstanding", "component sum", k, (" + ".join(xx[0][:30] for _, xx in so), x[1], []), tot, a0, None, None,
                f"{len(so)} class lines on {pg['rfile']}", tags=x[1])
        else:
            note = "" if a0 is not None else "no undimensioned companyfacts fact (class-dimensioned only?): printed first column"
            row("shares_outstanding", "mapped", k, x, vals[0] if vals else None, a0, vals[1] if len(vals) > 1 else None,
                api_value(facts, x[1], acc, fy1, False, "shares") if fy1 else None, note)
    else:
        row("shares_outstanding", "not_presented", None, None, None, None, None, None,
            "no CommonStockSharesOutstanding at the balance-sheet date on the BS or its parenthetical (the dei cover count is never used)")
    write(out, ticker, rank, cik, acc, filed, fy0, fy1, stmts, rows)
    n = len(rows)
    summ = {"rank": rank, "ticker": ticker, "cik": f"{cik:010d}", "accession": acc, "rows": n,
            "mapped": sum(r["status"] == "mapped" for r in rows), "not_presented": sum(r["status"] == "not_presented" for r in rows),
            "combined": sum(r["status"] == "combined" for r in rows), "out": sum(r["status"] == "OUT" for r in rows),
            "component sum": sum(r["status"] == "component sum" for r in rows),
            "match_y": sum(r["match"].startswith("Y") for r in rows), "match_n": sum(r["match"] == "N" for r in rows),
            "era_checks": sum(1 for r in rows if "ERA-CHECK" in r["era_from_note"]),
            "fy2015_accession": acc15 or "", "fy2015_match_y": sum(r.get("fy2015_match") == "Y" for r in rows),
            "fy2015_match_n": sum(r.get("fy2015_match") == "N" for r in rows),
            "points_covered_2015_latest": sum(str(r.get("era_coverage", "")).endswith("covered") for r in rows),
            "points_uncovered": sum(str(r.get("era_coverage", "")).startswith("uncovered") for r in rows),
            "quirks": [{"data_point": q[0], "tag": q[1], "quirk": q[2], "stmt": q[3]} for q in quirks]}
    print(json.dumps(summ, default=str))


FIELDS = ["ticker", "data_point", "status", "tags", "stmt", "r_page", "label", "fy0_printed", "fy0_api", "fy1_printed", "fy1_api",
          "match", "era_from_note", "evidence_class", "note", "fy2015_accession", "fy2015_status", "fy2015_tag", "fy2015_r_page",
          "fy2015_printed", "fy2015_api", "fy2015_match", "fy2015_note", "era_coverage"]


def write(out: Path, ticker, rank, cik, acc, filed, fy0, fy1, stmts, rows) -> None:
    with open(out / f"{ticker}-docmap-{DATE}.csv", "w", newline="") as f:
        w = csv.DictWriter(f, FIELDS)
        w.writeheader()
        w.writerows(rows)
    pages = "; ".join(f"{k} {p['rfile']} ({p['short'][:60]})" for k, p in stmts.items())
    lines = [f"# {ticker} document-first map {DATE} (read-only, bottom-up; rank {rank})", "",
             "Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing, tags from the R-page element "
             "references; API = SEC companyfacts, undimensioned, same accession, same period). Printed values are the page's "
             "value x the page's scale, sign as printed. Where printed and API differ, the filing decides.", "",
             "## Filings opened",
             f"- Latest 10-K {acc} (CIK {cik:010d}, filed {filed}, FY0 = {fy0}" + (f", FY1 = {fy1}" if fy1 else "") + f"). Pages: {pages}.",
             "- companyfacts CIK%010d.json (one call); era 10-Ks are named in the era column." % cik, "",
             "## Data points",
             "| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        lines.append("| " + " | ".join(str(r[k]).replace("|", "/")[:120] for k in ("data_point", "status", "tags", "stmt", "label", "fy0_printed", "fy0_api", "fy1_printed", "fy1_api", "match", "evidence_class", "note")) + " |")
    lines += ["", "## FY2015 era read (the FY2015 10-K opened; Dhairya 2026-11-12)",
              "| data point | FY2015 10-K | tag | R | printed | API | match | coverage FY2015-latest | note |", "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        lines.append("| " + " | ".join(str(r.get(k, "")).replace("|", "/")[:100] for k in ("data_point", "fy2015_accession", "fy2015_tag", "fy2015_r_page", "fy2015_printed", "fy2015_api", "fy2015_match", "era_coverage", "fy2015_note")) + " |")
    eras = [r for r in rows if r["era_from_note"]]
    lines += ["", "## Era checks (tag changes in the last five fiscal years)"]
    lines += [f"- {r['data_point']}: {r['era_from_note']}" for r in eras] or ["- none"]
    mism = [r for r in rows if r["match"] == "N"]
    lines += ["", "## Mismatches (printed vs API; the printed page decides)"]
    lines += [f"- {r['data_point']} {r['tags']}: printed {r['fy0_printed']} vs API {r['fy0_api']}" for r in mism] or ["- none beyond sign differences"]
    (out / f"{ticker}-docmap-{DATE}.md").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main(*sys.argv[1:5])
