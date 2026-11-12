#!/usr/bin/env python3
"""Document-first reads (founder order 2026-11-12; the format of data-team/companies/reads/ABT-docmap-2026-11-12):
for each company, open its latest 10-K on sec.gov, read every statement R page, and for each data point match the
printed face line -> the filing's own element name (the R page's defref anchor: the tag FSN carries) -> the SEC
companyfacts value for the same accession and period. A data point whose tag changed inside the last 5 fiscal years
in companyfacts gets one more 10-K read: the latest 10-K of the other tag's era.

Evidence: printed values, labels and tags come from the filing's R pages (FILING-CHECKED); the API column is SEC
companyfacts (undimensioned). companyfacts carries no extension (custom) tags, so a custom face line has no API value.

Rules: sec.gov / data.sec.gov only; User-Agent = the declared SEC_USER_AGENT (never typed); at most 0.4 requests per
second (MIN_INTERVAL). No database access. Writes <out>/<TICKER>-docmap-<date>.{md,csv} and appends tag quirks to
<inbox>.

usage: python3 -I docmap_read.py <cohort_v1_1_sic.csv> <seed.md> <out_dir> <inbox.md> <rank_from> <rank_to> [<date>]
"""

from __future__ import annotations

import csv
import html
import json
import os
import re
import sys
import time
import urllib.request
from datetime import date
from pathlib import Path

UA = os.environ["SEC_USER_AGENT"]
MIN_INTERVAL = 2.5  # seconds between requests: 0.4 requests per second
_last = [0.0]


def get(url: str) -> str:
    wait = MIN_INTERVAL - (time.time() - _last[0])
    if wait > 0:
        time.sleep(wait)
    for attempt in range(4):
        _last[0] = time.time()
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": UA, "Accept-Encoding": "identity"}
            )
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise
            time.sleep(MIN_INTERVAL * (2 + attempt * 2))
        except Exception:  # noqa: BLE001  network hiccup: back off and retry
            time.sleep(MIN_INTERVAL * (2 + attempt * 2))
    raise RuntimeError(f"failed after retries: {url}")


# --------------------------------------------------------------------------- data points
# (data point, statements to look in, candidate tags in priority order)
DP: list[tuple[str, tuple[str, ...], tuple[str, ...]]] = [
    (
        "revenue",
        ("IS",),
        (
            "Revenues",
            "RevenueFromContractWithCustomerExcludingAssessedTax",
            "RevenueFromContractWithCustomerIncludingAssessedTax",
            "SalesRevenueNet",
            "SalesRevenueGoodsNet",
            "RevenuesNetOfInterestExpense",
            "RegulatedAndUnregulatedOperatingRevenue",
        ),
    ),
    (
        "cost_of_revenue",
        ("IS",),
        (
            "CostOfRevenue",
            "CostOfGoodsAndServicesSold",
            "CostOfGoodsSold",
            "CostOfServices",
            "CostOfGoodsAndServiceExcludingDepreciationDepletionAndAmortization",
        ),
    ),
    ("gross_profit", ("IS",), ("GrossProfit",)),
    (
        "operating_expenses",
        ("IS",),
        ("OperatingExpenses", "OperatingCostsAndExpenses", "CostsAndExpenses"),
    ),
    (
        "sga_expense",
        ("IS",),
        ("SellingGeneralAndAdministrativeExpense", "GeneralAndAdministrativeExpense"),
    ),
    (
        "research_and_development",
        ("IS",),
        (
            "ResearchAndDevelopmentExpense",
            "ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost",
        ),
    ),
    ("operating_income", ("IS",), ("OperatingIncomeLoss",)),
    (
        "interest_expense",
        ("IS",),
        (
            "InterestExpense",
            "InterestExpenseNonoperating",
            "InterestExpenseOperating",
            "InterestAndDebtExpense",
            "InterestExpenseDebt",
        ),
    ),
    (
        "interest_income",
        ("IS",),
        (
            "InvestmentIncomeInterest",
            "InterestIncomeOther",
            "InterestAndDividendIncomeOperating",
            "InterestIncomeOperating",
            "InvestmentIncomeInterestAndDividend",
        ),
    ),
    (
        "other_income_expense_net",
        ("IS",),
        ("OtherNonoperatingIncomeExpense", "NonoperatingIncomeExpense"),
    ),
    (
        "income_before_tax",
        ("IS",),
        (
            "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",
            "IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments",
        ),
    ),
    ("income_tax_expense", ("IS",), ("IncomeTaxExpenseBenefit",)),
    (
        "net_income",
        ("IS",),
        (
            "NetIncomeLoss",
            "NetIncomeLossAvailableToCommonStockholdersBasic",
            "ProfitLoss",
        ),
    ),
    (
        "basic_eps",
        ("IS",),
        ("EarningsPerShareBasic", "EarningsPerShareBasicAndDiluted"),
    ),
    (
        "diluted_eps",
        ("IS",),
        ("EarningsPerShareDiluted", "EarningsPerShareBasicAndDiluted"),
    ),
    (
        "weighted_basic_shares",
        ("IS",),
        (
            "WeightedAverageNumberOfSharesOutstandingBasic",
            "WeightedAverageNumberOfShareOutstandingBasicAndDiluted",
        ),
    ),
    (
        "weighted_diluted_shares",
        ("IS",),
        (
            "WeightedAverageNumberOfDilutedSharesOutstanding",
            "WeightedAverageNumberOfShareOutstandingBasicAndDiluted",
        ),
    ),
    (
        "dividends_per_share",
        ("IS", "EQ", "PAR"),
        (
            "CommonStockDividendsPerShareDeclared",
            "CommonStockDividendsPerShareCashPaid",
        ),
    ),
    (
        "comprehensive_income",
        ("CI", "IS"),
        (
            "ComprehensiveIncomeNetOfTax",
            "ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest",
        ),
    ),
    (
        "cash_and_equivalents",
        ("BS",),
        (
            "CashAndCashEquivalentsAtCarryingValue",
            "Cash",
            "CashAndDueFromBanks",
            "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents",
        ),
    ),
    (
        "accounts_receivable",
        ("BS",),
        (
            "AccountsReceivableNetCurrent",
            "ReceivablesNetCurrent",
            "AccountsReceivableNet",
            "AccountsAndOtherReceivablesNetCurrent",
        ),
    ),
    (
        "inventory",
        ("BS",),
        ("InventoryNet", "RetailRelatedInventoryMerchandise", "InventoryGross"),
    ),
    ("current_assets", ("BS",), ("AssetsCurrent",)),
    (
        "ppe_net",
        ("BS",),
        (
            "PropertyPlantAndEquipmentNet",
            "PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization",
            "RealEstateInvestmentPropertyNet",
        ),
    ),
    ("goodwill", ("BS",), ("Goodwill",)),
    ("total_assets", ("BS",), ("Assets",)),
    (
        "accounts_payable",
        ("BS",),
        (
            "AccountsPayableCurrent",
            "AccountsPayableTradeCurrent",
            "AccountsPayableAndAccruedLiabilitiesCurrent",
        ),
    ),
    ("current_liabilities", ("BS",), ("LiabilitiesCurrent",)),
    ("total_liabilities", ("BS",), ("Liabilities",)),
    ("total_debt", ("BS",), ()),  # component sum, see DEBT_TAGS
    (
        "stockholders_equity",
        ("BS",),
        (
            "StockholdersEquity",
            "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
        ),
    ),
    ("shares_outstanding", ("COVER",), ("EntityCommonStockSharesOutstanding",)),
    (
        "cfo",
        ("CF",),
        (
            "NetCashProvidedByUsedInOperatingActivities",
            "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations",
        ),
    ),
    (
        "cash_flow_investing",
        ("CF",),
        (
            "NetCashProvidedByUsedInInvestingActivities",
            "NetCashProvidedByUsedInInvestingActivitiesContinuingOperations",
        ),
    ),
    (
        "cash_flow_financing",
        ("CF",),
        (
            "NetCashProvidedByUsedInFinancingActivities",
            "NetCashProvidedByUsedInFinancingActivitiesContinuingOperations",
        ),
    ),
    (
        "capex",
        ("CF",),
        (
            "PaymentsToAcquirePropertyPlantAndEquipment",
            "PaymentsToAcquireProductiveAssets",
            "PaymentsForCapitalImprovements",
        ),
    ),
    (
        "depreciation_and_amortization",
        ("CF",),
        (
            "DepreciationDepletionAndAmortization",
            "DepreciationAndAmortization",
            "DepreciationAmortizationAndAccretionNet",
        ),
    ),
    ("amortization_of_intangibles", ("CF", "IS"), ("AmortizationOfIntangibleAssets",)),
    (
        "sbc",
        ("CF",),
        ("ShareBasedCompensation", "AllocatedShareBasedCompensationExpense"),
    ),
    (
        "dividends_paid",
        ("CF",),
        ("PaymentsOfDividendsCommonStock", "PaymentsOfDividends"),
    ),
    ("share_buybacks", ("CF",), ("PaymentsForRepurchaseOfCommonStock",)),
    (
        "cf_ar_change",
        ("CF",),
        (
            "IncreaseDecreaseInAccountsReceivable",
            "IncreaseDecreaseInReceivables",
            "IncreaseDecreaseInAccountsAndOtherReceivables",
        ),
    ),
    (
        "cf_inventory_change",
        ("CF",),
        ("IncreaseDecreaseInInventories", "IncreaseDecreaseInRetailRelatedInventories"),
    ),
    (
        "cf_ap_change",
        ("CF",),
        (
            "IncreaseDecreaseInAccountsPayable",
            "IncreaseDecreaseInAccountsPayableTrade",
            "IncreaseDecreaseInAccountsPayableAndAccruedLiabilities",
        ),
    ),
    ("cash_paid_for_interest", ("CF",), ("InterestPaidNet", "InterestPaid")),
    ("cash_paid_for_income_taxes", ("CF",), ("IncomeTaxesPaidNet", "IncomeTaxesPaid")),
]
BANK_DP: list[tuple[str, tuple[str, ...], tuple[str, ...]]] = [
    (
        "net_interest_income",
        ("IS",),
        ("InterestIncomeExpenseNet", "InterestIncomeExpenseAfterProvisionForLoanLoss"),
    ),
    (
        "total_interest_income",
        ("IS",),
        ("InterestAndDividendIncomeOperating", "InterestIncomeOperating"),
    ),
    ("noninterest_income", ("IS",), ("NoninterestIncome",)),
    ("noninterest_expense", ("IS",), ("NoninterestExpense",)),
    (
        "provision_for_credit_losses",
        ("IS",),
        (
            "ProvisionForLoanLeaseAndOtherLosses",
            "ProvisionForCreditLosses",
            "ProvisionForLoanAndLeaseLosses",
        ),
    ),
    ("deposits", ("BS",), ("Deposits",)),
    (
        "loans_net",
        ("BS",),
        (
            "LoansAndLeasesReceivableNetReportedAmount",
            "LoansAndLeasesReceivableNetOfDeferredIncome",
            "FinancingReceivableExcludingAccruedInterestAfterAllowanceForCreditLoss",
        ),
    ),
]
COMBINED = {
    "AccountsPayableAndAccruedLiabilitiesCurrent",
    "IncreaseDecreaseInAccountsPayableAndAccruedLiabilities",
    "AccountsAndOtherReceivablesNetCurrent",
}
NET_INCL_NCI = {
    "ProfitLoss",
    "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
    "ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest",
}
DEBT_TAGS = (
    "ShortTermBorrowings",
    "CommercialPaper",
    "DebtCurrent",
    "LongTermDebtCurrent",
    "LongTermDebtAndCapitalLeaseObligationsCurrent",
    "LongTermDebtNoncurrent",
    "LongTermDebtAndCapitalLeaseObligations",
    "LongTermDebt",
    "SeniorNotes",
    "NotesPayable",
    "FinanceLeaseLiabilityCurrent",
    "FinanceLeaseLiabilityNoncurrent",
)
DA_PARTS = ("Depreciation", "AmortizationOfIntangibleAssets")
# a custom (extension) face line is matched by its label only for these core data points
LABEL_FALLBACK = {
    "revenue": r"^(total\s+)?(net\s+)?(operating\s+)?(revenues?|net sales|sales)\b",
    "cost_of_revenue": r"^(total\s+)?cost\s+of\s+(sales|revenues?|goods sold|products sold)",
    "operating_income": r"^(total\s+)?(operating income|income from operations|operating (profit|earnings))",
    "net_income": r"^net (income|earnings|loss)\b(?!.*(noncontrolling|per share))",
    "capex": r"^(capital expenditures|purchases? of property|additions to property|payments for property)",
}
UNITS = {
    "basic_eps": "USD/shares",
    "diluted_eps": "USD/shares",
    "dividends_per_share": "USD/shares",
    "weighted_basic_shares": "shares",
    "weighted_diluted_shares": "shares",
    "shares_outstanding": "shares",
}


# --------------------------------------------------------------------------- R pages
MONTHS = {
    m: i
    for i, m in enumerate(
        [
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
        ],
        1,
    )
}


def _date(text: str) -> date | None:
    m = re.search(r"([A-Z][a-z]{2})\.?\s+(\d{1,2}),\s+(\d{4})", text)
    if not m or m.group(1) not in MONTHS:
        return None
    return date(int(m.group(3)), MONTHS[m.group(1)], int(m.group(2)))


def _num(cell: str) -> float | None:
    t = (
        html.unescape(re.sub(r"<[^>]+>", "", cell))
        .replace("$", "")
        .replace(",", "")
        .replace("\xa0", " ")
        .strip()
    )
    if not t or t in ("-", "—", "–"):
        return None
    neg = t.startswith("(") and t.endswith(")")
    t = t.strip("()").strip()
    try:
        v = float(t)
    except ValueError:
        return None
    return -v if neg else v


def parse_r(page: str) -> dict:
    """Title, scales, columns (dates of the first two duration-12m or instant columns) and rows
    [(label, prefix, tag, [values])]."""
    title_m = re.search(r'<th[^>]*class="tl"[^>]*>(.*?)</th>', page, re.S)
    title = (
        html.unescape(re.sub(r"<[^>]+>", " ", title_m.group(1))).strip()
        if title_m
        else ""
    )
    scale = 1.0
    if re.search(r"\$\s*in\s*Millions", title, re.I):
        scale = 1e6
    elif re.search(r"\$\s*in\s*Thousands", title, re.I):
        scale = 1e3
    elif re.search(r"\$\s*in\s*Billions", title, re.I):
        scale = 1e9
    sh_scale = 1.0
    if re.search(r"shares\s*in\s*Millions", title, re.I):
        sh_scale = 1e6
    elif re.search(r"shares\s*in\s*Thousands", title, re.I):
        sh_scale = 1e3
    # header: the date row (th class="th") in column order; 12 Months Ended groups decide FY columns
    head = page.split("</thead>")[0] if "</thead>" in page else page[:6000]
    groups = re.findall(
        r'<th[^>]*class="th"[^>]*colspan="(\d+)"[^>]*>(.*?)</th>', head, re.S
    )
    dates = [
        _date(html.unescape(re.sub(r"<[^>]+>", "", d)))
        for d in re.findall(
            r'<th[^>]*class="th"(?![^>]*colspan)[^>]*>(.*?)</th>', head, re.S
        )
    ]
    durations: list[str] = []
    for span, text in groups:
        durations += [html.unescape(re.sub(r"<[^>]+>", "", text)).strip()] * int(span)
    rows = []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", page, re.S):
        lab = re.search(r'<td class="pl[^"]*"[^>]*>(.*?)</td>', tr, re.S)
        if not lab:
            continue
        ref = re.search(r"defref_([A-Za-z0-9-]+)_([A-Za-z0-9]+)", lab.group(1))
        label = html.unescape(re.sub(r"<[^>]+>", "", lab.group(1))).strip()
        vals = [
            _num(c)
            for c in re.findall(
                r'<td class="(?:nump|num|text)"[^>]*>(.*?)</td>', tr, re.S
            )
        ]
        rows.append(
            (label, ref.group(1) if ref else "", ref.group(2) if ref else "", vals)
        )
    return {
        "title": title,
        "scale": scale,
        "sh_scale": sh_scale,
        "dates": dates,
        "durations": durations,
        "rows": rows,
    }


def fy_columns(page: dict, kind: str) -> list[int]:
    """Indexes of FY0 and FY1 columns: duration statements take the '12 Months Ended' columns, instants the dates."""
    n = len(page["dates"])
    if kind in ("BS", "COVER", "PAR_BS"):
        return list(range(min(2, n)))
    idx = [
        i
        for i, d in enumerate(page["durations"][:n])
        if re.search(r"12\s*Months|Year|Fiscal", d, re.I)
    ]
    return (idx or list(range(n)))[:2]


# --------------------------------------------------------------------------- one filing
def statements(base: str) -> dict[str, tuple[str, str]]:
    """kind -> (R file, short name) from FilingSummary.xml (Statements menu category; cover = R1)."""
    fs = get(base + "/FilingSummary.xml")
    out: dict[str, tuple[str, str]] = {}
    for rep in re.findall(r"<Report[^>]*>(.*?)</Report>", fs, re.S):
        name = html.unescape(
            (re.search(r"<ShortName>(.*?)</ShortName>", rep, re.S) or [None, ""])[1]
        ).strip()
        cat = (
            re.search(r"<MenuCategory>(.*?)</MenuCategory>", rep, re.S) or [None, ""]
        )[1].strip()
        fn = (
            re.search(r"<HtmlFileName>(.*?)</HtmlFileName>", rep, re.S) or [None, ""]
        )[1].strip()
        if not fn:
            continue
        if cat == "Cover" and "COVER" not in out:
            out["COVER"] = (fn, name)
        if cat != "Statements":
            continue
        low = name.lower()
        par = "parenthetical" in low
        if "cash flow" in low and not par:
            out.setdefault("CF", (fn, name))
        elif re.search(r"balance sheet|financial condition|financial position", low):
            out.setdefault("PAR_BS" if par else "BS", (fn, name))
        elif re.search(
            r"equity|stockholders|shareholders|changes in (net assets|capital)|partners",
            low,
        ):
            out.setdefault("PAR" if par else "EQ", (fn, name))
        elif (
            "comprehensive" in low
            and not re.search(r"operations|earnings|income and", low)
            and not par
        ):
            out.setdefault("CI", (fn, name))
        elif re.search(r"income|operations|earnings", low) and not par:
            out.setdefault("IS", (fn, name))
            if "comprehensive" in low:
                out.setdefault("CI", (fn, name))
    return out


def read_filing(cik: str, acc: str) -> dict:
    base = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc.replace('-', '')}"
    st = statements(base)
    pages = {}
    for kind in ("IS", "CI", "BS", "CF", "PAR", "EQ", "COVER"):
        if kind in st and st[kind][0] not in [p["file"] for p in pages.values()]:
            p = parse_r(get(base + "/" + st[kind][0]))
            p["file"], p["name"] = st[kind]
            pages[kind] = p
        elif kind in st:
            pages[kind] = next(p for p in pages.values() if p["file"] == st[kind][0])
    return pages


# --------------------------------------------------------------------------- companyfacts
def api_value(
    facts: dict, tag: str, unit: str, acc: str, end: date | None, duration: bool
) -> float | None:
    for prefix in ("us-gaap", "dei", "srt"):
        units = facts.get(prefix, {}).get(tag, {}).get("units", {})
        for u, entries in units.items():
            if u != unit and not (unit == "USD" and u == "USD"):
                continue
            for e in entries:
                if (
                    e.get("accn") != acc
                    or end is None
                    or e.get("end") != end.isoformat()
                ):
                    continue
                if duration:
                    if not e.get("start"):
                        continue
                    days = (
                        date.fromisoformat(e["end"]) - date.fromisoformat(e["start"])
                    ).days
                    if not 330 <= days <= 400:
                        continue
                elif e.get("start"):
                    continue
                return float(e["val"])
    return None


def fy_years(facts: dict, tag: str, unit: str, last: int = 5) -> list[str]:
    ends = set()
    for prefix in ("us-gaap",):
        for u, entries in facts.get(prefix, {}).get(tag, {}).get("units", {}).items():
            if u != unit:
                continue
            for e in entries:
                if (
                    e.get("form", "").startswith("10-K")
                    and e.get("fp") == "FY"
                    and e.get("start")
                ):
                    d = (
                        date.fromisoformat(e["end"]) - date.fromisoformat(e["start"])
                    ).days
                    if 330 <= d <= 400:
                        ends.add(e["end"])
                elif (
                    e.get("form", "").startswith("10-K")
                    and e.get("fp") == "FY"
                    and not e.get("start")
                ):
                    ends.add(e["end"])
    return sorted(ends)[-last:]


def latest_10k_with(facts: dict, tag: str, unit: str, fy_end: str) -> str | None:
    accs = []
    for u, entries in facts.get("us-gaap", {}).get(tag, {}).get("units", {}).items():
        if u != unit:
            continue
        accs += [
            (e.get("filed", ""), e["accn"])
            for e in entries
            if e.get("end") == fy_end
            and e.get("form", "").startswith("10-K")
            and e.get("fp") == "FY"
        ]
    return max(accs)[1] if accs else None


# --------------------------------------------------------------------------- mapping
def unit_of(dp: str) -> str:
    return UNITS.get(dp, "USD")


def scaled(page: dict, row: tuple, col: int, dp: str) -> float | None:
    vals = row[3]
    if col >= len(vals) or vals[col] is None:
        return None
    v = vals[col]
    u = unit_of(dp)
    if u == "USD/shares" or "per share" in row[0].lower():
        return v
    if u == "shares" or "(in shares)" in row[0].lower():
        return v * page["sh_scale"]
    return v * page["scale"]


def find_row(pages: dict, kinds, tags) -> tuple[str, tuple] | None:
    for tag in tags:
        for k in kinds:
            p = pages.get(k)
            if not p:
                continue
            for row in p["rows"]:
                if row[2] == tag:
                    return k, row
    return None


def map_company(pages: dict, facts: dict, acc: str, bank: bool) -> list[dict]:
    out = []
    for dp, kinds, tags in DP + (BANK_DP if bank else []):
        rec = {
            "data_point": dp,
            "status": "not_presented",
            "tags": "",
            "stmt": "",
            "r_page": "",
            "label": "",
            "fy0_printed": "",
            "fy0_api": "",
            "fy1_printed": "",
            "fy1_api": "",
            "match": "",
            "note": "",
            "era_from_note": "",
            "fy0_end": "",
            "era_tags": [],
        }
        hits: list[tuple[str, tuple]] = []
        status = "mapped"
        if dp == "total_debt":
            for k in kinds:
                p = pages.get(k)
                if p:
                    hits += [(k, r) for r in p["rows"] if r[2] in DEBT_TAGS]
            status = "component sum"
        elif dp == "depreciation_and_amortization":
            h = find_row(pages, kinds, tags)
            if h:
                hits = [h]
            else:
                parts = [find_row(pages, kinds, (t,)) for t in DA_PARTS]
                if all(parts):
                    hits, status = parts, "component sum"  # type: ignore[assignment]
        else:
            h = find_row(pages, kinds, tags)
            if h:
                hits = [h]
            elif dp in LABEL_FALLBACK:
                for k in kinds:
                    p = pages.get(k)
                    for row in (p or {}).get("rows", []):
                        if (
                            row[1] not in ("us-gaap", "dei", "srt", "")
                            and re.search(LABEL_FALLBACK[dp], row[0], re.I)
                            and any(v is not None for v in row[3])
                        ):
                            hits, status = [(k, row)], "custom (label-matched)"
                            break
                    if hits:
                        break
        if not hits:
            present = [k for k in kinds if k in pages]
            rec["stmt"] = "+".join(present)
            rec["r_page"] = "+".join(pages[k]["file"] for k in present)
            rec["note"] = "no such line on " + (
                ", ".join(f"{k} {pages[k]['file']}" for k in present)
                or "any statement read"
            )
            out.append(rec)
            continue
        k0, row0 = hits[0]
        p0 = pages[k0]
        cols = fy_columns(p0, k0)
        duration = k0 in ("IS", "CI", "CF", "EQ", "PAR") and dp not in (
            "shares_outstanding",
        )
        if (
            dp == "dividends_per_share"
            and k0 == "PAR"
            and len(p0["dates"])
            and not p0["durations"]
        ):
            duration = True
        unit = unit_of(dp)
        tot = [0.0, 0.0]
        api = [0.0, 0.0]
        api_ok = [True, True]
        printed_ok = [False, False]
        for k, row in hits:
            p = pages[k]
            cs = fy_columns(p, k)
            if (
                k == "COVER"
            ):  # the cover prints one value per fact, in its own date column
                cs = [next((i for i, v in enumerate(row[3]) if v is not None), 0)]
            for j in range(2):
                if j < len(cs):
                    v = scaled(p, row, cs[j], dp)
                    if v is not None:
                        tot[j] += v
                        printed_ok[j] = True
                    end = p["dates"][cs[j]] if cs[j] < len(p["dates"]) else None
                    a = (
                        api_value(facts, row[2], unit, acc, end, duration)
                        if row[1] in ("us-gaap", "dei", "srt")
                        else None
                    )
                    if a is None:
                        api_ok[j] = False
                    else:
                        api[j] += a
                else:
                    api_ok[j] = False
        if status == "mapped" and row0[2] in COMBINED:
            status = "combined"
        if status == "mapped" and row0[1] not in ("us-gaap", "dei", "srt"):
            status = "custom"
        rec.update(
            status=status,
            tags="+".join(f"{r[1]}:{r[2]}" for _k, r in hits),
            stmt="+".join(k for k, _r in hits),
            r_page="+".join(pages[k]["file"] for k, _r in hits),
            label=" + ".join(r[0] for _k, r in hits)[:160],
        )
        fy0_end = p0["dates"][cols[0]] if cols and cols[0] < len(p0["dates"]) else None
        rec["fy0_end"] = fy0_end.isoformat() if fy0_end else ""
        for j, key in ((0, "fy0"), (1, "fy1")):
            if printed_ok[j]:
                rec[f"{key}_printed"] = _fmt(tot[j])
            if api_ok[j]:
                rec[f"{key}_api"] = _fmt(api[j])
        rec["match"] = _match(rec)
        notes = []
        if dp == "operating_expenses" and row0[2] == "CostsAndExpenses":
            # the total includes cost of revenue: opex = total less the printed cost-of-revenue line (ABT reference)
            cor = find_row(
                pages, ("IS",), next(t for d, _k, t in DP if d == "cost_of_revenue")
            )
            if cor:
                ck, crow = cor
                cp = pages[ck]
                ccs = fy_columns(cp, ck)
                for j, key in ((0, "fy0"), (1, "fy1")):
                    if j < len(ccs):
                        cv = scaled(cp, crow, ccs[j], "cost_of_revenue")
                        end = cp["dates"][ccs[j]] if ccs[j] < len(cp["dates"]) else None
                        ca = api_value(facts, crow[2], "USD", acc, end, True)
                        if printed_ok[j] and cv is not None:
                            tot[j] -= cv
                        else:
                            printed_ok[j] = False
                        if api_ok[j] and ca is not None:
                            api[j] -= ca
                        else:
                            api_ok[j] = False
                status = "component sum"
                rec.update(
                    status=status,
                    tags=f"{row0[1]}:{row0[2]}-{crow[1]}:{crow[2]}",
                    label=f"{row0[0]} - {crow[0]}"[:160],
                )
                for j, key in ((0, "fy0"), (1, "fy1")):
                    rec[f"{key}_printed"] = _fmt(tot[j]) if printed_ok[j] else ""
                    rec[f"{key}_api"] = _fmt(api[j]) if api_ok[j] else ""
                rec["match"] = _match(rec)
        if row0[2] in NET_INCL_NCI:
            notes.append(f"{row0[2]} includes noncontrolling interest")
        if status == "combined":
            notes.append(f"'{row0[0]}' is a combined line")
        if status.startswith("custom"):
            notes.append("extension tag: companyfacts carries no extension facts")
        if dp == "operating_expenses" and row0[2] == "CostsAndExpenses":
            notes.append(
                "CostsAndExpenses total includes cost of revenue: opex = the total less the cost-of-revenue line"
                if status == "component sum"
                else "CostsAndExpenses total includes cost of revenue (no cost-of-revenue line): perimeter for the Tag Expert"
            )
        if dp == "interest_expense" and re.search(r",\s*net\b", row0[0], re.I):
            notes.append("', net' label: a net perimeter (Tag Expert 2026-11-11)")
        rec["note"] = "; ".join(notes)
        # era check: other candidate tags carrying FY values in the last 5 FY
        if status == "mapped" and tags:
            chosen = fy_years(facts, row0[2], unit)
            others = {t: fy_years(facts, t, unit) for t in tags if t != row0[2]}
            others = {t: [y for y in ys if y not in chosen] for t, ys in others.items()}
            others = {t: ys for t, ys in others.items() if ys}
            if others:
                rec["era_from_note"] = (
                    f"ERA-CHECK: chosen tag {chosen[:1] + chosen[-1:]} ; others in 5y: "
                    + "; ".join(
                        f"{t}: {ys[0]}..{ys[-1]}({len(ys)})" for t, ys in others.items()
                    )
                )
                rec["era_tags"] = [(t, ys[-1]) for t, ys in others.items()]
            else:
                rec["era_from_note"] = (
                    "tag covers last 5 FY in companyfacts"
                    if len(chosen) >= 5
                    else f"tag FY coverage in companyfacts: {len(chosen)}"
                )
        out.append(rec)
    return out


def _fmt(v: float) -> str:
    return str(int(round(v))) if abs(v - round(v)) < 1e-6 and abs(v) >= 1 else f"{v:g}"


def _match(rec: dict) -> str:
    res = []
    for key in ("fy0", "fy1"):
        p, a = rec[f"{key}_printed"], rec[f"{key}_api"]
        if p == "" or a == "":
            continue
        pv, av = float(p), float(a)
        tol = max(abs(av) * 1e-6, 0.51 if abs(av) < 1000 else 0.5e3)
        if abs(pv - av) <= tol:
            res.append("Y")
        elif abs(pv + av) <= tol:
            res.append("S")
        else:
            res.append("N")
    if not res:
        return ""
    if "N" in res:
        return "N"
    if "S" in res:
        return "Y (sign differs: printed in parentheses/negated label)"
    return "Y"


# --------------------------------------------------------------------------- templates
def template_of(
    seed_text: str, cohort_file: Path, cik: str, sys_path: str
) -> tuple[str, set[str]]:
    """The company's template and its in-template data points (the seed plan over the whole cohort, built once)."""
    if "plan" not in _TPL:
        sys.path.insert(0, sys_path)
        from scrooner_pipeline.mapper import sector_templates as st  # noqa: PLC0415

        rows = st.build_plan(st.parse_templates(seed_text), st.load_cohort(cohort_file))
        by_cik: dict[str, tuple[str, set[str]]] = {}
        ciks = {c.company_id: c.cik for c in st.load_cohort(cohort_file)}
        for r in rows:
            t, pts = by_cik.setdefault(ciks[r.company_id], (r.template, set()))
            if r.in_template:
                pts.add(r.data_point)
        _TPL["plan"] = by_cik
    return _TPL["plan"].get(cik, ("", set()))


_TPL: dict = {}


# --------------------------------------------------------------------------- output
COLS = [
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
]


def write(
    out_dir: Path,
    day: str,
    ticker: str,
    meta: dict,
    recs: list[dict],
    era_reads: list[dict],
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    with (out_dir / f"{ticker}-docmap-{day}.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, COLS, extrasaction="ignore")
        w.writeheader()
        for r in recs:
            note = r["note"] + (
                f" | accn {meta['acc']} FY end {r['fy0_end']}"
                if r["status"] != "not_presented"
                else ""
            )
            w.writerow(
                {
                    **r,
                    "ticker": ticker,
                    "tags": r["tags"],
                    "evidence_class": "FILING-CHECKED",
                    "note": note,
                }
            )
    lines = [
        f"# {ticker} document-first map {day} (read-only, bottom-up)",
        "",
        "Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing, tags from the R-page "
        "element references; API = SEC companyfacts, undimensioned, same accession, same period). Read by "
        "data-team/strategy/tools/docmap_read.py (certification lead session), sec.gov at <= 0.4 req/s with the "
        "declared SEC_USER_AGENT.",
        "",
        "## Filings opened",
        f"- Latest 10-K {meta['acc']} (CIK {meta['cik']}, filed {meta['filed']}, FY ended {meta['fy0_end']}). "
        + ", ".join(f"{k} {p['file']} ({p['name']})" for k, p in meta["pages"].items())
        + ".",
        f"- companyfacts CIK{meta['cik']}.json (one call).",
    ]
    for e in era_reads:
        lines.append(f"- Era 10-K {e['acc']} (FY {e['fy']}): {e['summary']}")
    lines += [
        "",
        f"Sector template: **{meta['template'] or 'not in the seed cohort'}**. "
        + (
            f"Template lines this filing does not print: {', '.join(meta['tpl_missing'])}."
            if meta["tpl_missing"]
            else "Every template line read here is printed or derived from printed lines."
        ),
        "",
        "## Data points",
        "| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in recs:
        tags = r["tags"].replace("us-gaap:", "")
        lines.append(
            f"| {r['data_point']} | {r['status']} | {tags} | {r['stmt']} {r['r_page']} | {r['label'][:60]} | "
            f"{r['fy0_printed']} | {r['fy0_api']} | {r['fy1_printed']} | {r['fy1_api']} | {r['match']} | "
            f"FILING-CHECKED | {r['note']}{(' ' + r['era_from_note']) if r['era_from_note'].startswith('ERA') else ''} |"
        )
    (out_dir / f"{ticker}-docmap-{day}.md").write_text("\n".join(lines) + "\n")


def quirks(
    ticker: str, meta: dict, recs: list[dict], era_reads: list[dict], day: str
) -> list[str]:
    out = []
    ev = f"{ticker} {meta['acc']}"
    for r in recs:
        tag = r["tags"].split("+")[0] if r["tags"] else ""
        loc = f"{ev} {r['r_page'].split('+')[0]}"
        if r["match"] == "N":
            out.append(
                (
                    tag,
                    f"{ticker} {r['data_point']}: printed {r['fy0_printed']} vs companyfacts {r['fy0_api']} "
                    f"(FY1 {r['fy1_printed']} vs {r['fy1_api']}) for the same accession and period",
                    loc,
                )
            )
        if r["status"].startswith("custom"):
            out.append(
                (
                    tag,
                    f"{ticker} {r['data_point']} printed on an extension tag ('{r['label'][:60]}'); "
                    "companyfacts has no value for it",
                    loc,
                )
            )
        if r["status"] == "combined":
            out.append(
                (
                    tag,
                    f"{ticker} {r['data_point']}: combined line '{r['label'][:60]}'",
                    loc,
                )
            )
        if r["note"] and "noncontrolling" in r["note"]:
            out.append(
                (tag, f"{ticker} {r['data_point']} printed only incl. NCI ({tag})", loc)
            )
        if r["note"] and "', net' label" in r["note"]:
            out.append(
                (
                    tag,
                    f"{ticker} interest expense printed as '{r['label'][:60]}' (net perimeter)",
                    loc,
                )
            )
    for e in era_reads:
        out.append(
            (
                e["tag"],
                f"{ticker} {e['data_point']}: tag changed across eras; era 10-K FY {e['fy']} prints "
                f"'{e['label'][:60]}' on {e['tag']} (latest 10-K: {e['latest_tag']})",
                f"{ticker} {e['acc']} {e['page']}",
            )
        )
    return [
        f"| {day} | certification lead (docmap 601-700) | {t or '-'} | {w} | {l} | FILING-CHECKED | new |"
        for t, w, l in out
    ]


def read_company(
    r: dict, seed_text: str, cohort_file: Path, sys_path: str, out_dir: Path, day: str
) -> dict:
    cik, ticker = r["cik"], r["ticker"]
    # SEC requests are spent carefully (Dhairya 2026-11-12): the latest 10-K comes from companyfacts itself (the 10-K
    # accession with the latest filing date among its facts), so no submissions call; then only FilingSummary + R pages
    facts = json.loads(
        get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json")
    ).get("facts", {})
    tenk = sorted(
        {
            (e.get("filed", ""), e["accn"])
            for ns in facts.values()
            for t in ns.values()
            for es in t.get("units", {}).values()
            for e in es
            if e.get("form") in ("10-K", "10-KT") and e.get("fp") == "FY"
        }
    )
    if not tenk:
        raise RuntimeError("no 10-K facts in companyfacts")
    filed, acc = tenk[-1]
    sic = int(r.get("sic") or 0)
    pages = read_filing(cik, acc)
    template, tpl_in = template_of(seed_text, cohort_file, cik, sys_path)
    bank = template in ("bank", "lender") or 6020 <= sic <= 6036
    recs = map_company(pages, facts, acc, bank)
    fy0 = next((x["fy0_end"] for x in recs if x["fy0_end"]), "")
    # era reads: one 10-K per distinct other-tag era (latest FY of the other tag), at most 2
    era_targets: dict[str, list[tuple[dict, str]]] = {}
    for x in recs:
        for t, fy in x["era_tags"]:
            a = latest_10k_with(facts, t, unit_of(x["data_point"]), fy)
            if a and a != acc:
                era_targets.setdefault(a, []).append((x, t))
    era_reads = []
    for a, items in sorted(era_targets.items(), reverse=True)[:2]:
        try:
            ep = read_filing(cik, a)
        except Exception as exc:  # noqa: BLE001
            era_reads.append(
                {
                    "acc": a,
                    "fy": "",
                    "summary": f"read failed: {exc!r}"[:120],
                    "data_point": "",
                    "tag": "",
                    "label": "",
                    "page": "",
                    "latest_tag": "",
                }
            )
            continue
        for x, t in items:
            dp_kinds = next(k for d, k, _ in DP + BANK_DP if d == x["data_point"])
            h = find_row(ep, dp_kinds, (t,))
            if h:
                k, row = h
                era_reads.append(
                    {
                        "acc": a,
                        "fy": ep[k]["dates"][0].isoformat() if ep[k]["dates"] else "",
                        "summary": f"{x['data_point']} printed as '{row[0][:50]}' on {t} ({ep[k]['file']})",
                        "data_point": x["data_point"],
                        "tag": t,
                        "label": row[0],
                        "page": ep[k]["file"],
                        "latest_tag": x["tags"],
                    }
                )
                x["note"] = (
                    x["note"] + "; " if x["note"] else ""
                ) + f"era 10-K {a} prints it on {t} ({ep[k]['file']})"
    tpl_missing = []
    names = {x["data_point"] for x in recs if x["status"] == "not_presented"}
    for dp in sorted(names):
        if dp in tpl_in or f"{dp}_resolved" in tpl_in:
            tpl_missing.append(dp)
    meta = {
        "acc": acc,
        "cik": cik,
        "filed": filed,
        "fy0_end": fy0,
        "pages": pages,
        "template": template,
        "tpl_missing": tpl_missing,
    }
    write(out_dir, day, ticker, meta, recs, era_reads)
    return {
        "meta": meta,
        "recs": recs,
        "era": era_reads,
        "quirks": quirks(ticker, meta, recs, era_reads, day),
    }


def main() -> None:
    cohort_file, seed, out_dir, inbox, lo, hi = sys.argv[1:7]
    day = sys.argv[7] if len(sys.argv) > 7 else date.today().isoformat()
    sys_path = str(Path(__file__).resolve().parents[3] / "pipeline" / "src")
    seed_text = Path(seed).read_text()
    v11 = (
        Path(__file__).resolve().parents[1]
        / "data"
        / "cohort_v1_1_proposal_2026-10-24.csv"
    )
    order = [r["company_id"] for r in csv.DictReader(v11.open())]
    by_id = {r["company_id"]: r for r in csv.DictReader(Path(cohort_file).open())}
    stats_path = Path(out_dir) / f"_progress-{lo}-{hi}.jsonl"
    done = set()
    if stats_path.exists():
        done = {
            json.loads(line)["ticker"]
            for line in stats_path.read_text().splitlines()
            if line.strip()
        }
    for rank in range(int(lo), int(hi) + 1):
        r = by_id[order[rank - 1]]
        if r["ticker"] in done:
            continue
        try:
            res = read_company(
                r, seed_text, Path(cohort_file), sys_path, Path(out_dir), day
            )
            stat = {
                "rank": rank,
                "ticker": r["ticker"],
                "ok": True,
                "status": {
                    s: sum(1 for x in res["recs"] if x["status"] == s)
                    for s in {x["status"] for x in res["recs"]}
                },
                "match": {
                    m or "none": sum(1 for x in res["recs"] if x["match"] == m)
                    for m in {x["match"] for x in res["recs"]}
                },
                "era_reads": len(res["era"]),
                "quirks": len(res["quirks"]),
                "template": res["meta"]["template"],
                "template_missing": len(res["meta"]["tpl_missing"]),
            }
            with open(inbox, "a") as fh:
                for q in res["quirks"]:
                    fh.write(q + "\n")
        except Exception as exc:  # noqa: BLE001  one company must not stop the range
            stat = {
                "rank": rank,
                "ticker": r["ticker"],
                "ok": False,
                "error": repr(exc)[:200],
            }
        with stats_path.open("a") as fh:
            fh.write(json.dumps(stat) + "\n")
        print(json.dumps(stat), flush=True)


if __name__ == "__main__":
    main()
