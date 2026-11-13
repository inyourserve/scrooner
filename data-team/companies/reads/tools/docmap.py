"""Document-first read of a company's latest 10-K (plus one 10-K per tag-change era).

For each printed face line that feeds a data point: printed page (R file) -> tag on that line ->
SEC companyfacts value for the same accession and period. Writes <TICKER>-docmap-<date>.{md,csv}
in the format of data-team/companies/reads/ABT-docmap-2026-11-12.md and returns tag-quirk rows.

Read-only. sec.gov / data.sec.gov only, at most 0.4 requests per second (2.5 s between requests).
The User-Agent contact is read from the file named by SEC_CONTACT_FILE (never hard-coded here).

Usage: python3 -I docmap.py <cohort.csv> <first_rank> <last_rank> <out_dir> <cache_dir> <inbox.md>
"""

from __future__ import annotations

import csv
import datetime as dt
import html
import json
import os
import re
import subprocess
import sys
import time

DATE = "2026-11-12"
MIN_GAP = 2.5  # seconds between SEC requests (0.4 req/s)
_last = [0.0]


def _ua() -> str:
    with open(os.environ["SEC_CONTACT_FILE"]) as fh:
        return "Scrooner research " + fh.read().strip()


def get(url: str, cache: str) -> str:
    path = os.path.join(cache, re.sub(r"\W", "_", url)[-150:])
    if os.path.exists(path):
        return open(path, encoding="utf8").read()
    for attempt in range(4):
        wait = MIN_GAP - (time.time() - _last[0])
        if wait > 0:
            time.sleep(wait)
        _last[0] = time.time()
        res = subprocess.run(
            ["curl", "-sS", "-m", "60", "-A", _ua(), "-w", "\n%{http_code}", url],
            capture_output=True,
        )
        body = res.stdout.decode("utf8", "ignore")
        body, _, code = body.rpartition("\n")
        if code == "200":
            open(path, "w", encoding="utf8").write(body)
            return body
        if code == "404":
            return ""
        time.sleep(10 * (attempt + 1))
    return ""


# ---------------------------------------------------------------- R-page parsing

MONTHS = {m: i for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}


def parse_date(s: str) -> dt.date | None:
    m = re.search(r"([A-Z][a-z]{2})\.?\s+(\d{1,2}),\s+(\d{4})", s)
    if not m or m.group(1).lower()[:3] not in MONTHS:
        return None
    return dt.date(int(m.group(3)), MONTHS[m.group(1).lower()[:3]], int(m.group(2)))


def cell_text(c: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", c))).strip()


def parse_r(page: str) -> dict:
    """Return {'title', 'scale', 'shares_scale', 'cols': [(months, end_date)], 'rows': [...]}."""
    trs = re.findall(r"<tr.*?</tr>", page, re.S)
    if not trs:
        return {"title": "", "scale": 1, "shares_scale": 1, "cols": [], "rows": []}
    title = cell_text(re.findall(r"<t[dh].*?</t[dh]>", trs[0], re.S)[0]) if trs else ""
    low = title.lower()
    scale = 1_000_000 if "$ in millions" in low or "usd ($) $ in millions" in low else (
        1_000 if "$ in thousands" in low else (1_000_000_000 if "$ in billions" in low else 1))
    sh = 1_000_000 if "shares in millions" in low else (1_000 if "shares in thousands" in low else 1)
    # header rows: group row (e.g. "12 Months Ended", colspan) then date row
    cols: list[tuple[int | None, dt.date | None]] = []
    header_rows = [t for t in trs[:3] if "<th" in t]
    groups: list[int | None] = []
    if header_rows:
        first = re.findall(r"<th([^>]*)>(.*?)</th>", header_rows[0], re.S)[1:]
        for attrs, txt in first:
            span = int((re.search(r'colspan="(\d+)"', attrs) or [None, 1])[1])
            t = cell_text(txt)
            m = re.search(r"(\d+)\s+Months Ended", t)
            months = int(m.group(1)) if m else None
            d = parse_date(t)
            groups += [months] * span if d is None else [None]
            if d is not None:
                cols.append((None, d))
        if len(header_rows) > 1:
            dates = [parse_date(cell_text(x)) for x in re.findall(r"<th[^>]*>(.*?)</th>", header_rows[1], re.S)]
            cols = [(groups[i] if i < len(groups) else None, d) for i, d in enumerate(dates)]
    rows = []
    for tr in trs[len(header_rows):]:
        tds = re.findall(r"<td([^>]*)>(.*?)</td>", tr, re.S)
        if not tds:
            continue
        m = re.search(r"defref_([A-Za-z0-9\-]+)_([A-Za-z0-9]+)", tr)
        tag = f"{m.group(1)}:{m.group(2)}" if m else ""
        label = cell_text(tds[0][1])
        vals = []
        for attrs, v in tds[1:]:
            if 'class="th"' in attrs:
                continue  # footnote column next to the label
            t = cell_text(v).replace("$", "").replace(",", "").strip()
            neg = t.startswith("(") and t.endswith(")")
            t = t.strip("()").strip()
            try:
                x = float(t)
                vals.append(-x if neg else x)
            except ValueError:
                vals.append(None)
        rows.append({"tag": tag, "label": label, "vals": vals})
    return {"title": title, "scale": scale, "shares_scale": sh, "cols": cols, "rows": rows}


# ---------------------------------------------------------------- data point rules

DP = [  # (data point, statement, tags in preference order, label regex)
    ("revenue", "IS", ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax",
                       "RevenueFromContractWithCustomerIncludingAssessedTax", "SalesRevenueNet",
                       "RevenuesNetOfInterestExpense", "RegulatedAndUnregulatedOperatingRevenue",
                       "RegulatedOperatingRevenue"], r"^total (net )?(operating )?revenues?$|^(net )?(operating )?revenues?$|^(total )?net sales$|^sales$"),
    ("cost_of_revenue", "IS", ["CostOfRevenue", "CostOfGoodsAndServicesSold", "CostOfGoodsSold", "CostOfServices"],
     r"^(total )?cost of (revenues?|sales|goods|products|services)"),
    ("gross_profit", "IS", ["GrossProfit"], r"^gross (profit|margin)"),
    ("operating_expenses", "IS", ["OperatingExpenses", "CostsAndExpenses"], r"^total (operating )?(costs and )?expenses"),
    ("sga_expense", "IS", ["SellingGeneralAndAdministrativeExpense", "GeneralAndAdministrativeExpense"],
     r"selling, general|general and administrative"),
    ("research_and_development", "IS", ["ResearchAndDevelopmentExpense",
                                        "ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost"], r"research and development"),
    ("operating_income", "IS", ["OperatingIncomeLoss"], r"^(total )?operating (income|profit|earnings)|income from operations"),
    ("interest_expense", "IS", ["InterestExpense", "InterestExpenseNonoperating", "InterestExpenseOperating",
                                "InterestAndDebtExpense", "InterestExpenseDebt", "InterestIncomeExpenseNonoperatingNet"],
     r"^interest (and debt |and other financing )?(expense|costs?)"),
    ("income_before_tax", "IS", ["IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",
                                 "IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments",
                                 "IncomeLossFromContinuingOperationsBeforeIncomeTaxesDomestic"],
     r"(income|earnings|loss).*before (income )?tax"),
    ("income_tax_expense", "IS", ["IncomeTaxExpenseBenefit"], r"(provision for|income tax|taxes on)"),
    ("net_income", "IS", ["NetIncomeLoss", "NetIncomeLossAvailableToCommonStockholdersBasic", "ProfitLoss"],
     r"^net (income|earnings|loss)"),
    ("basic_eps", "IS", ["EarningsPerShareBasic", "EarningsPerShareBasicAndDiluted"], r"basic"),
    ("diluted_eps", "IS", ["EarningsPerShareDiluted", "EarningsPerShareBasicAndDiluted"], r"diluted"),
    ("weighted_basic_shares", "IS", ["WeightedAverageNumberOfSharesOutstandingBasic"], r"^$"),
    ("weighted_diluted_shares", "IS", ["WeightedAverageNumberOfDilutedSharesOutstanding"], r"^$"),
    ("cash_and_equivalents", "BS", ["CashAndCashEquivalentsAtCarryingValue", "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents",
                                    "Cash", "CashAndDueFromBanks"], r"^cash and (cash )?equivalents"),
    ("accounts_receivable", "BS", ["AccountsReceivableNetCurrent", "ReceivablesNetCurrent"], r"receivable"),
    ("inventory", "BS", ["InventoryNet"], r"inventor"),
    ("current_assets", "BS", ["AssetsCurrent"], r"^total current assets"),
    ("ppe_net", "BS", ["PropertyPlantAndEquipmentNet",
                       "PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization",
                       "PublicUtilitiesPropertyPlantAndEquipmentNet"],
     r"property(, plant)? and equipment, net|net property"),
    ("goodwill", "BS", ["Goodwill"], r"^goodwill"),
    ("total_assets", "BS", ["Assets"], r"^total assets"),
    ("accounts_payable", "BS", ["AccountsPayableCurrent", "AccountsPayableTradeCurrent",
                                "AccountsPayableAndAccruedLiabilitiesCurrent"], r"^(trade )?accounts payable"),
    ("current_liabilities", "BS", ["LiabilitiesCurrent"], r"^total current liabilities"),
    ("total_liabilities", "BS", ["Liabilities"], r"^total liabilities$"),
    ("stockholders_equity", "BS", ["StockholdersEquity"], r"total .*(stockholders|shareholders|owners)['’]? (equity|investment)"),
    ("cfo", "CF", ["NetCashProvidedByUsedInOperatingActivities",
                   "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations"], r"operating activities"),
    ("cash_flow_investing", "CF", ["NetCashProvidedByUsedInInvestingActivities",
                                   "NetCashProvidedByUsedInInvestingActivitiesContinuingOperations"], r"investing activities"),
    ("cash_flow_financing", "CF", ["NetCashProvidedByUsedInFinancingActivities",
                                   "NetCashProvidedByUsedInFinancingActivitiesContinuingOperations"], r"financing activities"),
    ("capex", "CF", ["PaymentsToAcquirePropertyPlantAndEquipment", "PaymentsToAcquireProductiveAssets",
                     "PaymentsForCapitalImprovements"], r"(capital expenditures|purchases? of property|additions to property)"),
    ("depreciation_and_amortization", "CF", ["DepreciationDepletionAndAmortization", "DepreciationAmortizationAndAccretionNet",
                                             "DepreciationAndAmortization"], r"^depreciation(,| and)"),
    ("sbc", "CF", ["ShareBasedCompensation", "AllocatedShareBasedCompensationExpense"], r"(stock|share)-based compensation"),
    ("dividends_paid", "CF", ["PaymentsOfDividendsCommonStock", "PaymentsOfDividends", "PaymentsOfOrdinaryDividends",
                              "PaymentsOfCapitalDistribution"],
     r"dividends paid|cash dividends|distributions paid|distributions to (common )?(stockholders|shareholders)"),
    ("share_buybacks", "CF", ["PaymentsForRepurchaseOfCommonStock"], r"repurchase|purchases? of (common|treasury)"),
    # InterestPaidNet = net of capitalized interest (DQC_0065)
    ("cash_paid_for_interest", "CF", ["InterestPaidNet", "InterestPaid"], r"^interest paid|cash paid for interest"),
    ("cash_paid_for_income_taxes", "CF", ["IncomeTaxesPaidNet", "IncomeTaxesPaid"], r"income taxes paid|cash paid for income taxes"),
]
FIN_LEASE_TAGS = ["FinanceLeaseLiability", "FinanceLeaseLiabilityCurrent", "FinanceLeaseLiabilityNoncurrent",
                  "CapitalLeaseObligations", "CapitalLeaseObligationsCurrent", "CapitalLeaseObligationsNoncurrent"]
REIT_CAPEX = ["PaymentsToDevelopRealEstateAssets", "PaymentsForCapitalImprovements",
              "PaymentsForLeasingCostsCommissionsAndTenantImprovements", "PaymentsToAcquireAndDevelopRealEstate",
              "PaymentsForConstructionInProcess"]
DEBT_TAGS = ["ShortTermBorrowings", "CommercialPaper", "DebtCurrent", "LongTermDebtCurrent", "LongTermDebtNoncurrent",
             "LongTermDebt", "LongTermDebtAndCapitalLeaseObligations", "LongTermDebtAndCapitalLeaseObligationsCurrent",
             "OtherLongTermDebtNoncurrent", "LinesOfCreditCurrent", "SeniorNotes", "ConvertibleNotesPayable"]
DA_PARTS = ["Depreciation", "AmortizationOfIntangibleAssets", "DepreciationAndAmortization", "AdjustmentForAmortization",
            "DepreciationNonproduction", "DepreciationDepletionAndAmortization"]
STMT_RX = {
    "IS": r"(statements? of (consolidated )?(income|operations|earnings|comprehensive (income|loss))|income statements?|statements? of (net )?(income|earnings|operations))",
    "BS": r"(balance sheets?|statements? of financial (position|condition)|statements? of condition)",
    "CF": r"cash flows?",
    "COVER": r"(cover|document and entity)",
}


def find_reports(fs: str) -> dict[str, tuple[str, str]]:
    reps = re.findall(r"<Report[^>]*>(.*?)</Report>", fs, re.S)
    out: dict[str, tuple[str, str]] = {}
    for r in reps:
        name = html.unescape((re.search(r"<ShortName>(.*?)</ShortName>", r, re.S) or [None, ""])[1])
        fn = (re.search(r"<HtmlFileName>(.*?)</HtmlFileName>", r, re.S) or [None, ""])[1]
        cat = (re.search(r"<MenuCategory>(.*?)</MenuCategory>", r, re.S) or [None, ""])[1]
        n = name.lower()
        if not fn:
            continue
        if "COVER" not in out and (cat == "Cover" or re.search(STMT_RX["COVER"], n)):
            out["COVER"] = (name, fn)
            continue
        if cat and cat != "Statements":
            continue
        if "parenthetical" in n:
            if "BS" in out and "BSP" not in out:
                out["BSP"] = (name, fn)
            continue
        for k in ("CF", "BS", "IS"):
            if k not in out and re.search(STMT_RX[k], n) and not (k == "IS" and "comprehensive" in n and "IS" in out):
                if k == "IS" and re.search(r"^consolidated statements? of comprehensive", n) and "IS" not in out:
                    out.setdefault("CI", (name, fn))
                    continue
                out[k] = (name, fn)
                break
        if re.search(r"comprehensive", n) and "CI" not in out and "IS" in out and out["IS"][1] != fn:
            out["CI"] = (name, fn)
    return out


# ---------------------------------------------------------------- companyfacts lookup

def api_value(cf: dict, tag: str, accn: str, end: dt.date, months: int | None) -> float | None:
    ns, local = tag.split(":", 1) if ":" in tag else ("us-gaap", tag)
    node = cf.get("facts", {}).get(ns, {}).get(local)
    if not node:
        return None
    for unit, facts in node.get("units", {}).items():
        for f in facts:
            if f.get("accn") != accn or f.get("end") != end.isoformat():
                continue
            if months and f.get("start"):
                days = (end - dt.date.fromisoformat(f["start"])).days
                if abs(days - months * 30.4) > 20:
                    continue
            if months and not f.get("start"):
                continue
            return float(f["val"])
    return None


def annual_tag_history(cf: dict, tags: list[str]) -> dict[str, dict[str, str]]:
    """{fy_end: {tag: accn}} for 10-K annual facts of these tags (latest filing per end)."""
    hist: dict[str, dict[str, str]] = {}
    for t in tags:
        node = cf.get("facts", {}).get("us-gaap", {}).get(t)
        if not node:
            continue
        for facts in node.get("units", {}).values():
            for f in facts:
                if f.get("form") != "10-K" or f.get("fp") != "FY":
                    continue
                if f.get("start"):
                    d = (dt.date.fromisoformat(f["end"]) - dt.date.fromisoformat(f["start"])).days
                    if not 350 <= d <= 380:
                        continue
                hist.setdefault(f["end"], {})[t] = f["accn"]
    return hist


# ---------------------------------------------------------------- one company

def scaled(v: float | None, dp: str, page: dict) -> float | None:
    if v is None:
        return None
    if dp in ("basic_eps", "diluted_eps"):
        return v
    if dp in ("weighted_basic_shares", "weighted_diluted_shares"):
        return v * page["shares_scale"]
    return v * page["scale"]


def fmt(x: float | None) -> str:
    if x is None:
        return ""
    return str(int(x)) if abs(x - round(x)) < 1e-9 else f"{x:.4g}"


def pick_cols(page: dict, stmt: str) -> list[int]:
    idx = []
    for i, (months, end) in enumerate(page["cols"]):
        if end is None:
            continue
        if stmt == "BS" or months in (12, None):
            idx.append(i)
    return idx[:2]


EXCLUDE = {  # rule-based keying errors to avoid (Dhairya 2026-11-12)
    "share_buybacks": (r"TaxWithholding|SharesPaidForTaxWithholding|ProceedsFromRepurchaseOfEquity",r"withh?old|tax(es)? (paid )?(related to|for|on) (net share|share-based|stock-based|vesting)|net share settlement"),
    "dividends_paid": (r"MinorityInterest|NoncontrollingInterest|PreferredStock|PreferenceStock|Declared",
                       r"noncontrolling|non-controlling|minority|preferred|preference|declared"),
    "accounts_receivable": (r"InterestReceivable|NotesReceivable|FinancingReceivable|LoansAndLeasesReceivable|LoansReceivable", r"interest receivable|notes? receivable|financing receivable|loans? receivable|loans and leases"),
}


def dedupe_coreg(rows: list[dict]) -> list[dict]:
    """Co-registrant blocks print the same tag again on one page (e.g. Prologis, Inc. and Prologis, L.P.):
    only the first (parent, consolidated) occurrence counts (Dhairya / Ritwik 2026-11-12, PLD 70,074 vs 35,037)."""
    seen: dict[str, list] = {}
    out = []
    block = "main"  # main face block, then dimension blocks headed by an Axis/Member row (fix 17)
    for r in rows:
        if is_block_header(r):
            # a legal-entity block (or a multi-dimension header such as 'Electric | Ameren Missouri') is a
            # co-registrant or subsidiary block: dropped whole. Other axes (product / service members) are kept whole.
            block = "entity" if (r["tag"] == "dei:LegalEntityAxis" or " | " in r["label"]) else "member"
            if block == "member":
                out.append(r)
            continue
        if block == "entity":
            continue
        if block == "member":
            r = dict(r, member_block=True)
            out.append(r)
            continue
        key = r["tag"]
        if key and key in seen and any(v == r["vals"] or lab == r["label"] for v, lab in seen[key]):
            continue  # same tag with the same values or the same label: a co-registrant block repeat (AEE, PLD)
        seen.setdefault(key, []).append((r["vals"], r["label"]))
        out.append(r)
    return out


def is_block_header(r: dict) -> bool:
    """A dimension block header row on an R page: an Axis/Member tag carrying no values."""
    return bool(r["tag"]) and bool(re.search(r"(Axis|Member)$", r["tag"])) and not any(v is not None for v in r["vals"])


def main_block(rows: list[dict]) -> int:
    """Index of the first dimension block header (end of the undimensioned face block)."""
    return next((i for i, r in enumerate(rows) if is_block_header(r)), len(rows))


def member_sum(page: dict, r: dict) -> dict:
    """A line printed as several member rows on one tag (e.g. cost of revenue by product / service): a component sum
    of ALL printed member rows, as tag[member: label] (Dhairya 2026-11-12, INTU 4,253, AMT, WMB, REGN, CDNS).
    A row equal to the sum of the others is the printed total and is used alone."""
    same = [x for x in page["rows"] if x["tag"] == r["tag"] and _has(x)]
    face = [x for x in same if not x.get("member_block")]
    if face:
        same = face  # fix 22: rows of the face block decide; member-block rows only when the face block lacks the tag
    if len(same) < 2:
        return same[0] if same else r
    v0 = [x["vals"][0] if x["vals"] else None for x in same]
    if None in v0:
        return r
    for i, x in enumerate(same):
        rest = sum(v for j, v in enumerate(v0) if j != i)
        if abs(v0[i] - rest) <= max(1.0, abs(rest) * 1e-6):
            return x  # the printed total ties to its members
    n = max(len(x["vals"]) for x in same)
    return {"tag": "+".join(f"{x['tag']}[member: {x['label'][:40]}]" for x in same),
            "label": " + ".join(x["label"] for x in same),
            "vals": [sum((x["vals"][k] or 0) for x in same if k < len(x["vals"])) for k in range(n)],
            "parts": same, "opex_status": "component sum",
            "opex_note": "all printed member rows of one tag summed (value_source fsn_xbrl); no printed total on the face"}


def _excluded(dp: str, r: dict) -> bool:
    ex = EXCLUDE.get(dp)
    if dp == "dividends_paid" and re.search(r"common", r["label"], re.I):
        return False  # a common + preferred line is kept and keyed combined, not excluded
    return bool(ex) and (bool(re.search(ex[0], r["tag"])) or bool(re.search(ex[1], r["label"], re.I)))


def match_row(page: dict, dp: str, tags: list[str], rx: str) -> dict | None:
    for t in tags:
        for r in page["rows"]:
            if r["tag"] == f"us-gaap:{t}" and any(v is not None for v in r["vals"]) and not _excluded(dp, r):
                return r
    if rx and rx != "^$":
        for r in page["rows"]:
            if r["tag"] and re.search(rx, r["label"], re.I) and any(v is not None for v in r["vals"]) and not _excluded(dp, r):
                return dict(r, by_label=True)  # matched by printed label (custom extension or an unlisted tag)
    return None


def _has(r: dict) -> bool:
    return any(v is not None for v in r["vals"])


def opex_row(page: dict) -> tuple[dict | None, str, str]:
    """Operating expenses never include cost of revenue (Dhairya ruling 2026-11-12).
    1. A printed total opex line that excludes COGS -> mapped.
    2. Else every face line between gross profit and operating income, summed, tied exactly to GP - OI -> component sum.
    3. A total (e.g. CostsAndExpenses) that includes COGS -> combined, never opex."""
    allrows = page["rows"]
    end_main = main_block(allrows)
    rows = allrows[:end_main]  # locate face lines in the undimensioned block only (fix 18)
    loc = lambda tags, rx: next((i for i, r in enumerate(rows) if _has(r) and (
        r["tag"].split(":")[-1] in tags or re.search(rx, r["label"], re.I))), None)
    i_gp = loc(["GrossProfit"], r"^gross (profit|margin)")
    i_oi = loc(["OperatingIncomeLoss"], r"^(total )?operating (income|profit|earnings)|income from operations")
    i_cogs = loc(["CostOfRevenue", "CostOfGoodsAndServicesSold", "CostOfGoodsSold", "CostOfServices"],
                 r"^(total )?cost of (revenues?|sales|goods|products|services)")
    i_tot = next((i for i, r in enumerate(rows) if _has(r) and (r["tag"].split(":")[-1] in ("OperatingExpenses", "CostsAndExpenses", "OperatingCostsAndExpenses")
                  or re.search(r"^total (operating )?(costs and )?expenses", r["label"], re.I))), None)
    v = lambda i: rows[i]["vals"][0] if rows[i]["vals"] else None
    cogs_tags = ("CostOfRevenue", "CostOfGoodsAndServicesSold", "CostOfGoodsSold", "CostOfServices")
    m_cogs = [r for r in allrows[end_main:] if _has(r) and r["tag"].split(":")[-1] in cogs_tags]
    if i_tot is not None and i_gp is None and i_cogs is None and m_cogs and v(i_tot) is not None:
        # cost of revenue printed only in product/service member blocks (BLCO, CZR, WH): the total includes it.
        # The face lines between revenue and the total are opex when they plus the member COGS rows tie to the
        # total (Dhairya 2026-11-13 adjudication: BLCO 4,988 = 2,938 + 2,050; CZR 9,628 = 3,885 + 5,743).
        tot = rows[i_tot]
        i_rev = max((i for i in range(i_tot) if _has(rows[i]) and (
            rows[i]["tag"].split(":")[-1] in ("Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax",
                                              "RevenueFromContractWithCustomerIncludingAssessedTax", "SalesRevenueNet")
            or re.search(r"^(total |net )?(revenues?|net sales|sales)$", rows[i]["label"], re.I))), default=None)
        parts = [rows[i] for i in range((i_rev if i_rev is not None else -1) + 1, i_tot) if _has(rows[i]) and rows[i]["tag"]]
        mc = sum((r["vals"][0] or 0) for r in m_cogs)
        if parts and i_rev is not None:
            ps = sum((p["vals"][0] or 0) for p in parts)
            if abs(abs(v(i_tot)) - abs(ps + mc)) < 0.5:
                return ({"tag": "+".join(p["tag"] for p in parts), "label": " + ".join(p["label"] for p in parts),
                         "vals": [sum((p["vals"][k] or 0) for p in parts if k < len(p["vals"])) for k in range(max(len(p["vals"]) for p in parts))],
                         "parts": parts}, "component sum",
                        f"face lines between revenue and the printed total {fmt(v(i_tot))}; they plus cost of revenue printed by member "
                        f"({fmt(mc)}) tie to the total, so the total includes COGS and is never opex")
            return tot, "combined", (f"total includes cost of revenue printed by member ({fmt(mc)}); face lines {fmt(ps)} + member COGS "
                                     f"do not tie to the total {fmt(v(i_tot))} (residual {fmt(v(i_tot) - ps - mc)}): combined, never opex")
        return tot, "combined", f"total includes cost of revenue printed by member ({fmt(mc)}): combined, never opex"
    if i_tot is not None:
        tot = rows[i_tot]
        if i_gp is not None and i_oi is not None and None not in (v(i_gp), v(i_oi), v(i_tot)):
            if abs(abs(v(i_tot)) - abs(v(i_gp) - v(i_oi))) < 0.5:
                return tot, "mapped", "printed total opex line excludes cost of revenue (= GP - OI)"
        elif i_gp is None and tot["tag"].endswith(":CostsAndExpenses"):
            return tot, "combined", "CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex"
        elif i_gp is None and (i_cogs is None or i_cogs > i_tot):
            return tot, "mapped", "printed total opex line; no cost-of-revenue line above it"
        if i_cogs is not None and i_cogs < i_tot and (i_gp is None or i_gp > i_tot):
            return tot, "combined", "printed total includes cost of revenue: combined, never opex"
    if i_gp is not None and i_oi is not None and i_gp < i_oi:
        parts = [rows[i] for i in range(i_gp + 1, i_oi) if _has(rows[i]) and rows[i]["tag"]]
        if parts and None not in (v(i_gp), v(i_oi)):
            total = sum((p["vals"][0] or 0) for p in parts)
            if abs(abs(total) - abs(v(i_gp) - v(i_oi))) < 0.5:
                return ({"tag": "+".join(p["tag"] for p in parts), "label": " + ".join(p["label"] for p in parts),
                         "vals": [sum((p["vals"][k] or 0) for p in parts if k < len(p["vals"])) for k in range(max(len(p["vals"]) for p in parts))],
                         "parts": parts}, "component sum", "every face line between gross profit and operating income; ties to GP - OI")
            return None, "", f"face lines between gross profit and operating income sum to {fmt(total)}, not GP - OI {fmt(v(i_gp) - v(i_oi))}"
    if i_tot is not None:
        return None, "", "a total-expense line exists but its COGS perimeter could not be established"
    return None, "", "no total opex line and no gross profit / operating income pair to tie components"


# ---------------------------------------------------------------- whole-filing resolution of face misses

NOTE_FAMILY = {  # data point -> (tags that ARE the data point, tags that are only a component of it)
    "total_debt": (["LongTermDebt", "DebtLongtermAndShorttermCombinedAmount", "DebtInstrumentCarryingAmount",
                    "LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities"],
                   ["LongTermDebtNoncurrent", "LongTermDebtCurrent", "ShortTermBorrowings", "CommercialPaper",
                    "SeniorNotes", "NotesPayable", "LinesOfCreditCurrent"]),
    "depreciation_and_amortization": (["DepreciationDepletionAndAmortization", "DepreciationAndAmortization",
                                       "DepreciationAmortizationAndAccretionNet"],
                                      ["Depreciation", "AmortizationOfIntangibleAssets", "DepreciationNonproduction"]),
    "shares_outstanding": (["CommonStockSharesOutstanding"], []),
    "operating_expenses": (["OperatingExpenses"], []),
}


NOTE_REJECT = (r"variable interest|\bVIEs?\b|subsidiar|merger|acquisition|segment|investee|equity method|"
               r"joint venture|unconsolidated|discontinued|held for sale|guarantor|parent company|condensed financial information|"
               r"affiliated compan|summarized financial")  # fix 20: GATX RRPF affiliate pages

OUT_FOR_FIN = {"cost_of_revenue", "gross_profit", "research_and_development", "inventory", "current_assets",
               "current_liabilities"}
FIN_GROUPS = {"bank", "insurer", "lender_nonbank", "bdc", "broker_dealer", "asset_manager", "reit_mortgage"}
NET_INTEREST_TAGS = {"InterestIncomeExpenseNonoperatingNet", "InterestIncomeExpenseNet", "InterestRevenueExpenseNet",
                     "InterestExpenseNet"}
GROUP_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "strategy", "data", "group_assignment_v2.csv")
_GROUPS: dict[str, str] | None = None


def template_group(tic: str) -> str:
    """The company's template group from data-team/strategy/data/group_assignment_v2.csv ('' when absent)."""
    global _GROUPS
    if _GROUPS is None:
        _GROUPS = {}
        if os.path.exists(GROUP_FILE):
            with open(GROUP_FILE, newline="") as fh:
                _GROUPS = {r["ticker"]: r.get("group") or "" for r in csv.DictReader(fh)}
    return _GROUPS.get(tic, "")

KEYWORDS = {  # label search (any tag, custom included) for the by-hand review of not_presented rows
    "revenue": r"\b(revenues?|net sales|sales)\b", "cost_of_revenue": r"cost of (revenue|sales|goods|products|services)",
    "gross_profit": r"gross (profit|margin)", "operating_expenses": r"operating (costs and )?expenses",
    "sga_expense": r"selling|general and administrative", "research_and_development": r"research",
    "operating_income": r"operating (income|profit|earnings)|income from operations",
    "interest_expense": r"interest expense", "income_before_tax": r"before (income )?tax",
    "income_tax_expense": r"income tax (expense|provision)|provision for income tax", "net_income": r"net (income|earnings|loss)",
    "inventory": r"inventor", "goodwill": r"goodwill", "ppe_net": r"property.*(net|equipment)", "accounts_receivable": r"receivable",
    "accounts_payable": r"accounts payable", "current_assets": r"current assets", "current_liabilities": r"current liabilities",
    "total_liabilities": r"^total liabilities$|^liabilities$", "total_debt": r"\b(debt|borrowings|notes payable)\b",
    "capex": r"capital expenditure|purchases? of property|additions to property",
    "depreciation_and_amortization": r"depreciation", "sbc": r"(stock|share)-based compensation|share based compensation",
    "dividends_paid": r"dividends? paid|payments? of dividends", "share_buybacks": r"repurchase|treasury stock acquired",
    "cash_paid_for_interest": r"interest paid|cash paid for interest", "cash_paid_for_income_taxes": r"income taxes paid|taxes paid",
    "shares_outstanding": r"shares,? outstanding", "basic_eps": r"basic", "diluted_eps": r"diluted",
    "cash_and_equivalents": r"cash and cash equivalents",
}


def resolve_by_filing(out: list[dict], cf: dict, accn: str, cik: str, cache: str, quirks: list[str], tic: str) -> None:
    """Dhairya ruling 2026-11-12: no AUTO rows. Every face miss is checked against the WHOLE filing (MetaLinks.json:
    every tag in the filing's presentation, face statements and notes, with the R pages that show it):
    a data-point tag in a note -> mapped, stmt NOTE, R page; only a component tag in a note -> component_in_note;
    nothing anywhere -> not_presented, citing the whole-filing check."""
    todo = [r for r in out if r.get("status") == "not_presented" and str(r.get("note", "")).startswith("AUTO")]
    if not todo:
        return
    b = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accn.replace('-', '')}/"
    txt = get(b + "MetaLinks.json", cache)
    try:
        inst = next(iter(json.loads(txt)["instance"].values()))
    except Exception:
        for r in todo:
            r["note"] = "MetaLinks.json not available for this filing: whole-filing check could not run; " + r["note"]
        return
    role2r = {v.get("role"): (k, v.get("groupType", ""), v.get("shortName", "")) for k, v in inst.get("report", {}).items()}
    tags = inst.get("tag", {})
    ntags = len(tags)
    end = None
    for r in out:
        if "period .." in str(r.get("note", "")):
            end = dt.date.fromisoformat(r["note"].split("period ..")[-1][:10])
            break

    def where(local: str) -> list[tuple[str, str, str]]:
        t = tags.get(f"us-gaap_{local}")
        if not t:
            return []
        rs = [role2r[x] for x in t.get("presentation", []) if x in role2r
              and not re.search(NOTE_REJECT, role2r[x][2], re.I)]
        return sorted(rs, key=lambda x: (x[1] == "statement", int(re.sub(r"\D", "", x[0]) or 0)))

    for r in todo:
        dp = r["data_point"]
        spec = next((d for d in DP if d[0] == dp), None)
        full, comp = NOTE_FAMILY.get(dp, ((spec[2] if spec else []), []))
        hit = next(((t, where(t)) for t in full if where(t)), None)
        if hit:
            t, rs = hit
            months = 12 if r.get("stmt") in ("IS", "CF") else None
            av = api_value(cf, f"us-gaap:{t}", accn, end, months) if end else None
            if av is None:
                # note values only from undimensioned consolidated facts: no such fact -> not a hit
                hit = None
        if hit:
            # the value printed on that R page (Dhairya: every mapped row's value must equal its R page)
            pv, plabel = None, ""
            for rr in rs[:3]:
                pg = parse_r(get(b + f"{rr[0]}.htm", cache))
                cand = [x for x in pg["rows"] if x["tag"] == f"us-gaap:{t}" and any(v is not None for v in x["vals"])]
                cand.sort(key=lambda x: (bool(re.search(r"beginning|opening", x["label"], re.I)),
                                         not re.search(r"ending|end of|outstanding|balance", x["label"], re.I)))
                row_ = cand[0] if cand and not re.search(r"beginning|opening", cand[0]["label"], re.I) else None
                if row_:
                    ci = next((i for i, (m, e) in enumerate(pg["cols"]) if e == end and i < len(row_["vals"])
                               and row_["vals"][i] is not None), None)
                    if ci is None:
                        ci = next((i for i, v in enumerate(row_["vals"]) if v is not None), None)
                    if ci is not None:
                        pv = scaled(row_["vals"][ci], dp, pg) if dp != "shares_outstanding" else row_["vals"][ci] * pg["shares_scale"]
                        plabel, rs = row_["label"], [rr] + [x for x in rs if x != rr]
                        break
            if pv is None:
                m = ""
            elif av is None:
                m = "API missing"
            elif abs(pv - av) < 0.5:
                m = "Y"
            elif abs(abs(pv) - abs(av)) < 0.5:
                m = "Y (sign differs: printed in parentheses/negated label)"
            else:
                m = f"N (printed {fmt(pv)} vs API {fmt(av)})"
            r.update(status="mapped", stmt="NOTE" if rs[0][1] != "statement" else rs[0][1], r_page=f"{rs[0][0]}.htm",
                     tags=f"us-gaap:{t}", label=(plabel or rs[0][2])[:120], fy0_printed=fmt(pv), fy0_api=fmt(av),
                     match=m, note=f"not on the face statement; shown in {rs[0][0]}.htm '{rs[0][2][:80]}' (MetaLinks.json presentation)"
                     + ("" if pv is not None else "; HAND REVIEW: no period-end value row found on the R page (only roll-forward or dimensioned rows)"))
            quirks.append(f"| new | {tic} | {dp} | us-gaap:{t} | not on the face; reported in a note/other page {rs[0][0]}.htm '{rs[0][2][:60]}' | {accn} | FILING-CHECKED (MetaLinks) |")
            continue
        chit = [(t, where(t)) for t in comp if where(t)]
        if chit:
            t, rs = chit[0]
            r.update(status="component_in_note", stmt="NOTE", r_page=f"{rs[0][0]}.htm", tags="+".join(f"us-gaap:{c[0]}" for c in chit),
                     label=rs[0][2][:120], note=f"only component tag(s) {', '.join(c[0] for c in chit)} in the filing ({rs[0][0]}.htm '{rs[0][2][:60]}'); the data point itself is not reported")
            continue
        kw = KEYWORDS.get(dp)
        cands = []
        if kw:
            for key, t in tags.items():
                labels = " / ".join(t.get("lang", {}).get("en-us", {}).get("role", {}).values())
                if re.search(kw, labels, re.I) and not re.search(r"(Abstract|Axis|Member|Domain|Policy|TextBlock|Table)$", key):
                    rs = [role2r[x][0] for x in t.get("presentation", []) if x in role2r]
                    cands.append(f"{key.replace('_', ':', 1)} '{labels[:60]}' {','.join(rs[:3])}")
        r.update(status="not_presented", evidence_class="FILING-CHECKED",
                 note=f"whole-filing check: none of {', '.join(full + comp)} in MetaLinks.json ({ntags} tags across all {len(role2r)} R pages, face and notes) of {accn}; "
                 + (f"HAND REVIEW: {len(cands)} label candidate(s) incl. custom tags: " + "; ".join(cands[:8]) if cands
                    else "label search over every tag in the filing (custom included) found no candidate"))


def read_company(row: dict, cache: str) -> tuple[list[dict], list[str], dict]:
    cik = row["cik"].zfill(10)
    tic = row["ticker"]
    cf_txt = get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json", cache)
    cf = json.loads(cf_txt) if cf_txt.startswith("{") else {}
    tenks = sorted({(f["filed"], f["accn"]) for n in cf.get("facts", {}).values() for c in n.values()
                    for fs in c.get("units", {}).values() for f in fs if f.get("form") == "10-K"}, reverse=True)
    meta = {"ticker": tic, "cik": cik, "name": row["name"], "accn": "", "filings": [], "quirks": []}
    if not tenks:
        meta["error"] = "no 10-K in companyfacts"
        return [], [], meta
    accn = tenks[0][1]
    meta["accn"], meta["filed"] = accn, tenks[0][0]
    base = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accn.replace('-', '')}/"
    fs = get(base + "FilingSummary.xml", cache)
    reps = find_reports(fs)
    meta["filings"].append((accn, tenks[0][0], {k: v[1] for k, v in reps.items()}))
    pages = {k: parse_r(get(base + fn, cache)) for k, (_, fn) in reps.items() if k in ("IS", "BS", "CF", "BSP")}
    for _pg in pages.values():
        _pg["rows"] = dedupe_coreg(_pg["rows"])
    out: list[dict] = []
    quirks: list[str] = []
    for dp, stmt, tags, rx in DP:
        page = pages.get(stmt)
        rec = {"ticker": tic, "data_point": dp, "status": "", "tags": "", "stmt": stmt,
               "r_page": reps.get(stmt, ("", ""))[1], "label": "", "fy0_printed": "", "fy0_api": "",
               "fy1_printed": "", "fy1_api": "", "match": "", "era_from_note": "", "evidence_class": "", "note": ""}
        if not page or not page["rows"]:
            rec.update(status="not_presented", evidence_class="FILING-CHECKED",
                       note="AUTO: statement page not identified in FilingSummary; not hand-verified")
            out.append(rec)
            continue
        r = None
        if dp == "operating_expenses":
            r, opex_status, opex_note = opex_row(page)
            if r is None:
                rec.update(status="not_presented", evidence_class="FILING-CHECKED",
                           note=f"AUTO: {reps[stmt][1]} read; {opex_note}; not hand-verified")
                out.append(rec)
                continue
            r = dict(r, opex_status=opex_status, opex_note=opex_note)
        elif dp == "sga_expense":
            r = match_row(page, dp, tags, rx)
            if r is not None and not r["tag"].endswith(":SellingGeneralAndAdministrativeExpense"):
                # SG&A is never G&A alone when a selling or marketing line is printed (Dhairya 2026-11-12):
                # component sum of the G&A line and every printed selling / marketing line
                sm = [x for x in page["rows"] if _has(x) and x is not r and (
                    re.search(r"Selling(And)?Marketing|SellingExpense|MarketingExpense|MarketingAndAdvertising", x["tag"])
                    or re.search(r"^(sales|selling)( and | & )marketing|^selling\b|^marketing\b", x["label"], re.I))]
                if sm and re.search(r"GeneralAndAdministrative", r["tag"]) or (sm and re.search(r"general and administrative", r["label"], re.I)):
                    parts = [r] + sm
                    r = {"tag": "+".join(p["tag"] for p in parts), "label": " + ".join(p["label"] for p in parts),
                         "vals": [sum((p["vals"][k] or 0) for p in parts if k < len(p["vals"])) for k in range(max(len(p["vals"]) for p in parts))],
                         "parts": parts, "opex_status": "component sum",
                         "opex_note": "SG&A = G&A + printed selling/marketing line(s); never G&A alone (Dhairya 2026-11-12)"}
        elif dp == "capex":
            r = match_row(page, dp, tags, rx)
            if r is not None and "parts" not in r:
                rows_ = page["rows"]
                i_cfo = next((i for i, x in enumerate(rows_) if x["tag"].split(":")[-1].startswith("NetCashProvidedByUsedInOperatingActivities")), -1)
                i_cfi = next((i for i, x in enumerate(rows_) if x["tag"].split(":")[-1].startswith("NetCashProvidedByUsedInInvestingActivities")), len(rows_))
                ta = [x for x in rows_[i_cfo + 1:i_cfi] if _has(x) and re.search(r"turnaround", x["label"], re.I) and x is not r]
                if ta:
                    parts = [r] + ta
                    r = {"tag": "+".join(p["tag"] for p in parts), "label": " + ".join(p["label"] for p in parts),
                         "vals": [sum((p["vals"][k] or 0) for p in parts if k < len(p["vals"])) for k in range(max(len(p["vals"]) for p in parts))],
                         "parts": parts, "opex_status": "component sum",
                         "opex_note": "capex includes turnaround expenditures printed in investing activities (Dhairya 2026-11-12)"}
            if r is None:
                parts = [x for x in page["rows"] if _has(x) and x["tag"] and (
                    x["tag"].split(":")[-1] in REIT_CAPEX
                    or re.search(r"(property|building|capital) improvements|tenant improvements|leasing (costs|commissions)|^development", x["label"], re.I))
                    and not re.search(r"proceeds|sale|disposition|accrued|non-?cash|not yet paid|incurred but", x["label"], re.I)
                    and not x["tag"].endswith(("CapitalExpendituresIncurredButNotYetPaid", "NoncashOrPartNoncashAcquisitionValueOfAssetsAcquired1"))]
                if parts:
                    r = {"tag": "+".join(p["tag"] for p in parts), "label": " + ".join(p["label"] for p in parts),
                         "vals": [sum((p["vals"][k] or 0) for p in parts if k < len(p["vals"])) for k in range(max(len(p["vals"]) for p in parts))],
                         "parts": parts, "opex_status": "component sum",
                         "opex_note": "REIT capex: development + improvements + TI/leasing commissions lines (Dhairya 2026-11-12, PLD); acquisitions excluded"}
        elif dp == "depreciation_and_amortization":
            r = match_row(page, dp, tags, rx)
            if r is None:
                parts = [x for x in page["rows"] if x["tag"].split(":")[-1] in DA_PARTS]
                if parts:
                    r = {"tag": "+".join(p["tag"] for p in parts), "label": " + ".join(p["label"] for p in parts),
                         "vals": [sum((p["vals"][i] or 0) for p in parts) if any(p["vals"][i] is not None for p in parts if i < len(p["vals"])) else None
                                  for i in range(max(len(p["vals"]) for p in parts))], "parts": parts}
        elif dp not in ("sga_expense", "capex"):
            r = match_row(page, dp, tags, rx)
            if r is not None and "parts" not in r:
                r = member_sum(page, r)
            if dp == "accounts_receivable" and r is not None and r.get("by_label"):
                n_recv = sum(1 for x in page["rows"] if re.search(r"receivable", x["label"], re.I)
                             and any(v is not None for v in x["vals"]))
                if n_recv != 1:
                    r = None  # wider receivables tag only when it is the single receivables line on the face
        if r is None:
            rec.update(status="not_presented", evidence_class="FILING-CHECKED",
                       note=f"AUTO: {reps[stmt][1]} read; no face row matched the {dp} tag/label rules; not hand-verified")
            out.append(rec)
            continue
        cols = pick_cols(page, stmt)
        months = 12 if stmt in ("IS", "CF") else None
        vals = []
        for k, ci in enumerate(cols):
            pv = scaled(r["vals"][ci] if ci < len(r["vals"]) else None, dp, page)
            end = page["cols"][ci][1]
            if "parts" in r:
                av = None
                if len({p["tag"] for p in r["parts"]}) == 1:
                    # member rows of one tag: the undimensioned fact of that tag is the consolidated total
                    av = api_value(cf, r["parts"][0]["tag"], accn, end, months)
                    parts_api = [None]
                else:
                    parts_api = [api_value(cf, p["tag"], accn, end, months) for p in r["parts"]]
                if all(a is not None for a in parts_api):
                    # a part printed with the opposite sign of its fact (e.g. a gain shown negative inside expenses)
                    signed = []
                    for p, a in zip(r["parts"], parts_api):
                        pv_p = p["vals"][ci] if ci < len(p["vals"]) else None
                        signed.append(-a if pv_p is not None and a and (pv_p < 0) != (a < 0) else a)
                    av = sum(signed)
            else:
                av = api_value(cf, r["tag"], accn, end, months)
            vals.append((pv, av, end))
        status = r.get("opex_status") or ("component sum" if "parts" in r else "mapped")
        rule_note = ""
        if dp == "interest_expense" and (re.search(r"\bnet\b|deductions|net of", r["label"], re.I)
                                        or r["tag"].split(":")[-1] in ("InterestIncomeExpenseNonoperatingNet", "InterestIncomeExpenseNet",
                                                                       "InterestRevenueExpenseNet", "InterestExpenseNet")):
            status, rule_note = "combined", "net interest line: interest_expense is the gross charge only, a net line is combined (Dhairya 2026-11-12)"
        if dp == "dividends_paid" and re.search(r"common", r["label"], re.I) and re.search(r"preferred|preference|units|noncontrolling|non-controlling|minority", r["label"], re.I):
            status, rule_note = "combined", "dividend line mixes common with preferred / units / NCI: combined (Dhairya 2026-11-12, PLD)"
        if dp == "depreciation_and_amortization" and (re.search(r"accretion", r["label"], re.I)
                                                      or r["tag"].endswith("DepreciationAmortizationAndAccretionNet")):
            status, rule_note = "combined", "D&A line includes accretion: combined (Dhairya 2026-11-12)"
        how = ("company extension tag, matched by printed label" if not r["tag"].startswith("us-gaap")
               else ("matched by printed label (tag outside the usual set)" if r.get("by_label") else ""))
        rec.update(status=status, tags=r["tag"], label=r["label"][:120], evidence_class="FILING-CHECKED")
        verdicts = []
        for k, (pv, av, end) in enumerate(vals):
            rec[f"fy{k}_printed"], rec[f"fy{k}_api"] = fmt(pv), fmt(av)
            if pv is None:
                verdicts.append("")
            elif av is None:
                verdicts.append("API missing")
            elif abs(pv - av) < 0.5 or abs(pv - av) <= abs(av) * 1e-9:
                verdicts.append("Y")
            elif abs(abs(pv) - abs(av)) < 0.5:
                verdicts.append("Y (sign differs: printed in parentheses/negated label)")
            else:
                verdicts.append(f"N (printed {fmt(pv)} vs API {fmt(av)})")
        rec["match"] = next((v for v in verdicts if v.startswith("N") or v == "API missing"), verdicts[0] if verdicts else "")
        if vals:
            if r.get("opex_note"):
                how = r["opex_note"] + ("; " + how if how else "")
            if rule_note:
                how = rule_note + ("; " + how if how else "")
            rec["note"] = (how + " | " if how else "") + f"accn {accn} {reps[stmt][1]} period ..{vals[0][2].isoformat()}"
        if any(v.startswith("N") for v in verdicts):
            quirks.append(f"| new | {tic} | {dp} | {r['tag']} | printed vs companyfacts mismatch: {'; '.join(v for v in verdicts if v.startswith('N'))} | {accn} {reps[stmt][1]} | FILING-CHECKED |")
        if how and r["tag"].startswith("us-gaap"):
            quirks.append(f"| new | {tic} | {dp} | {r['tag']} | face line '{r['label'][:80]}' carries a us-gaap tag outside the usual {dp} set | {accn} {reps[stmt][1]} | FILING-CHECKED |")
        if how and not r["tag"].startswith("us-gaap"):
            quirks.append(f"| new | {tic} | {dp} | {r['tag']} | face line '{r['label'][:80]}' on a company extension tag, not us-gaap | {accn} {reps[stmt][1]} | FILING-CHECKED |")
        if any(v == "API missing" for v in verdicts):
            quirks.append(f"| new | {tic} | {dp} | {r['tag']} | printed face value has no companyfacts fact for the same accession/period | {accn} {reps[stmt][1]} | FILING-CHECKED |")
        out.append(rec)
    # total debt: printed BS debt lines + finance lease liabilities (current and noncurrent), never operating leases
    # (founder 2026-11-04 item 5, Dhairya 2026-11-12). Leases are not added again when a debt line already carries them
    # (by tag or label); the note total is used only when no face line carries finance leases.
    bs = pages.get("BS")
    if bs and bs["rows"]:
        parts = [x for x in bs["rows"] if not x.get("member_block") and x["tag"].split(":")[-1] in DEBT_TAGS and x["tag"].startswith("us-gaap")
                 and any(v is not None for v in x["vals"])]
        cols = pick_cols(bs, "BS")
        rec = {"ticker": tic, "data_point": "total_debt", "stmt": "BS", "r_page": reps["BS"][1],
               "evidence_class": "FILING-CHECKED", "era_from_note": ""}
        if len(parts) > 2 and cols:
            vv = [(p["vals"][cols[0]] or 0) if cols[0] < len(p["vals"]) else 0 for p in parts]
            for i, p in enumerate(parts):
                if abs(vv[i] - (sum(vv) - vv[i])) <= max(1.0, abs(vv[i]) * 1e-6):
                    parts = [p]  # a printed total that ties to the other debt lines: never add both (PNC)
                    break
        lease_in_debt = any(re.search(r"Lease", p["tag"]) or re.search(r"finance lease|capital lease|lease obligations", p["label"], re.I)
                            for p in parts)
        fl_face = [x for x in bs["rows"] if not x.get("member_block") and _has(x) and x["tag"].split(":")[-1] in FIN_LEASE_TAGS
                   and not re.search(r"operating", x["label"], re.I)]
        lease_note = ""
        if (parts or fl_face) and cols:  # face debt carried only on finance-lease tags (LSTR) is total debt too (fix 21)
            end0 = bs["cols"][cols[0]][1]
            extra = [] if lease_in_debt else fl_face
            allp = parts + extra
            pv0 = sum((p["vals"][cols[0]] or 0) for p in allp if cols[0] < len(p["vals"])) * bs["scale"]
            api0 = [api_value(cf, p["tag"], accn, end0, None) for p in allp]
            av0 = sum(api0) if all(a is not None for a in api0) else None
            if lease_in_debt:
                lease_note = "finance leases already inside a debt line (tag/label): not added again"
            elif extra and not parts:
                lease_note = "the only debt lines on the BS face carry finance lease tags (summed)"
            elif extra:
                lease_note = "finance lease liabilities printed on the BS face added"
            else:
                fl_tot = api_value(cf, "us-gaap:FinanceLeaseLiability", accn, end0, None)
                if fl_tot is None:
                    cur = api_value(cf, "us-gaap:FinanceLeaseLiabilityCurrent", accn, end0, None)
                    non = api_value(cf, "us-gaap:FinanceLeaseLiabilityNoncurrent", accn, end0, None)
                    fl_tot = (cur or 0) + (non or 0) if (cur is not None or non is not None) else None
                if fl_tot:
                    pv0 += fl_tot
                    av0 = av0 + fl_tot if av0 is not None else None
                    allp = allp + [{"tag": "us-gaap:FinanceLeaseLiability(note)", "label": "finance lease liabilities (note)"}]
                    lease_note = f"finance lease liabilities {fmt(fl_tot)} from the lease note (no face line carries them)"
                else:
                    lease_note = "no finance lease liability fact in the filing"
            rec.update(status="component sum", tags="+".join(p["tag"] for p in allp),
                       label=" + ".join(p["label"] for p in allp)[:120], fy0_printed=fmt(pv0), fy0_api=fmt(av0),
                       match="Y" if av0 is not None and abs(pv0 - av0) < 0.5 else ("API missing" if av0 is None else "N"),
                       note="printed BS debt lines; " + lease_note + "; operating leases never included")
        else:
            rec.update(status="not_presented", note="AUTO: no standard debt line on the BS face; not hand-verified")
        out.append(rec)
    # shares outstanding: us-gaap:CommonStockSharesOutstanding (or its class sum) at the balance-sheet date,
    # from the BS face or the BS parenthetical; the dei cover count is never used (Dhairya ruling 2026-11-12)
    rec = {"ticker": tic, "data_point": "shares_outstanding", "evidence_class": "FILING-CHECKED", "era_from_note": ""}
    found = None
    for key in ("BS", "BSP"):
        pg = pages.get(key)
        if not pg:
            continue
        sh = [x for x in pg["rows"] if not x.get("member_block") and x["tag"] == "us-gaap:CommonStockSharesOutstanding"
              and any(v is not None for v in x["vals"])]
        if sh:
            found = (key, pg, sh)
            break
    if found:
        key, pg, sh = found
        cols = pick_cols(pg, "BS") or [0]
        ci = cols[0]
        end = pg["cols"][ci][1] if ci < len(pg["cols"]) else None
        pv = sum((x["vals"][ci] or 0) for x in sh if ci < len(x["vals"])) * pg["shares_scale"]
        av = api_value(cf, "us-gaap:CommonStockSharesOutstanding", accn, end, None) if end and len(sh) == 1 else None
        rec.update(status="mapped" if len(sh) == 1 else "component sum", tags="us-gaap:CommonStockSharesOutstanding",
                   stmt=key, r_page=reps[key][1], label=sh[0]["label"][:120], fy0_printed=fmt(pv), fy0_api=fmt(av),
                   match=("Y" if av is not None and abs(pv - av) < 0.5 else ("" if len(sh) > 1 else "API missing")),
                   note=f"balance-sheet date {end}; " + ("classes summed (printed rows)" if len(sh) > 1 else "single row"))
    else:
        rec.update(status="not_presented", stmt="BS", r_page=reps.get("BS", ("", ""))[1],
                   note="AUTO: no CommonStockSharesOutstanding count at the BS date on the BS face or parenthetical; dei cover count not used")
    out.append(rec)
    resolve_by_filing(out, cf, accn, cik, cache, quirks, tic)
    # fix 19: a net interest line resolved anywhere (face or note) is combined, never gross interest expense
    # (interest card; Dhairya SPGI caption ruling 2026-11-12; DOCS 'Interest income' on InterestIncomeExpenseNonoperatingNet)
    for r in out:
        if r["data_point"] == "interest_expense" and r.get("status") == "mapped" and (
                re.search(r",\s*net\b|\bnet\b|income|net interest|deductions", r.get("label") or "", re.I)
                or (r.get("tags") or "").split(":")[-1] in NET_INTEREST_TAGS):
            r["status"] = "combined"
            r["note"] = "net interest line: interest_expense is the gross charge only, a net line is combined (Dhairya 2026-11-12) | " + (r.get("note") or "")
    # OUT ruling (Dhairya, main @020ebb29): for banks and insurers these data points are outside the template.
    # fix 17 (Dhairya 2026-11-13, SYF CA/CL): the other financial template groups (group_assignment_v2.csv) too,
    # for a row that is not presented on the filing (a presented line is never overruled by the group alone)
    sub = get(f"https://data.sec.gov/submissions/CIK{cik}.json", cache)
    try:
        sic = int(json.loads(sub).get("sic") or 0)
    except Exception:
        sic = 0
    fam = "bank" if (6021 <= sic <= 6036 or sic == 6712) else ("insurer" if 6311 <= sic <= 6411 else "")
    grp = template_group(tic)
    meta["sic"], meta["group"] = sic, grp
    for r in out:
        if r["data_point"] not in OUT_FOR_FIN:
            continue
        was = f"{r.get('status')} {r.get('tags', '')} {r.get('fy0_printed', '')}".strip()
        if fam:
            r.update(status="OUT", note=f"OUT: outside the {fam} template (SIC {sic}; Dhairya OUT ruling main @020ebb29); was: {was[:120]}")
        elif grp in FIN_GROUPS and r.get("status") == "not_presented":
            r.update(status="OUT", note=f"OUT: outside the {grp} template group (group_assignment_v2.csv; Dhairya ruling 2026-11-13, SYF CA/CL); was: {was[:120]}")
    # era coverage FY2015 -> latest (Dhairya 2026-11-12: a docmap is loadable only when every data point's eras
    # cover FY2015 to the latest year). Runs come from companyfacts 10-K annual facts (DATA-INFERRED); the FY2015
    # 10-K is always opened and its printed line recorded (FILING-CHECKED), plus up to 2 more era-change 10-Ks.
    era_lines = []
    era_accns: dict[str, list[str]] = {}
    fy15 = sorted({(f.get("filed", ""), f["accn"]) for n in cf.get("facts", {}).values() for c in n.values()
                   for fs in c.get("units", {}).values() for f in fs
                   if f.get("form") == "10-K" and f.get("fp") == "FY" and f.get("fy") == 2015})
    fy15_accn = fy15[0][1] if fy15 else None
    latest_end = None
    for rec in out:
        if rec.get("note", "").find("period ..") >= 0:
            latest_end = rec["note"].split("period ..")[-1][:10]
            break
    for rec in out:
        dp = rec["data_point"]
        spec = next((d for d in DP if d[0] == dp), None)
        if not spec or rec.get("status") in ("not_presented",) or not rec.get("tags"):
            continue
        fam = list(dict.fromkeys(([rec["tags"].split(":", 1)[1]] if rec["tags"].startswith("us-gaap:") and "+" not in rec["tags"] else []) + spec[2]))
        hist = annual_tag_history(cf, fam)
        ends = [e for e in sorted(hist) if e >= "2015-01-01" and (latest_end is None or e <= latest_end)]
        runs: list[list] = []  # [tag, first_end, last_end]
        for e in ends:
            t = sorted(hist[e])[0] if len(hist[e]) > 1 and fam[0] not in hist[e] else (fam[0] if fam[0] in hist[e] else sorted(hist[e])[0])
            if runs and runs[-1][0] == t:
                runs[-1][2] = e
            else:
                runs.append([t, e, e])
        first_ok = bool(ends) and ends[0] < "2016-06-01"
        covered = first_ok and latest_end is not None and ends and ends[-1] >= latest_end[:4]
        txt = "; ".join(f"{t} FY {a[:7]}..{z[:7]}" for t, a, z in runs) or "no annual 10-K facts for the tag family"
        rec["era_from_note"] = ("ERA COVERED FY2015-latest: " if covered else "ERA GAP (FY2015-latest not covered): ") + txt
        if len(runs) > 1:
            quirks.append(f"| new | {tic} | {dp} | {' -> '.join('us-gaap:' + r[0] for r in runs)} | tag eras from FY2015: {txt} | companyfacts | DATA-INFERRED |")
            for t, a0, z0 in runs[:-1]:
                acc = hist[z0].get(t)
                if acc:
                    era_accns.setdefault(acc, []).append(dp)
        if not covered:
            quirks.append(f"| new | {tic} | {dp} | {rec['tags'][:80]} | era coverage gap: annual facts reach only {ends[0][:7] if ends else 'none'}..{ends[-1][:7] if ends else 'none'} | companyfacts | DATA-INFERRED |")
        if fy15_accn:
            era_accns.setdefault(fy15_accn, [])
            if dp not in era_accns[fy15_accn]:
                era_accns[fy15_accn].append(dp)
    order = ([fy15_accn] if fy15_accn else []) + [a for a in era_accns if a != fy15_accn][:2]
    if not fy15_accn:
        era_lines.append("- FY2015 10-K: none in companyfacts (fy=2015, form 10-K): the FY2015 era cannot be read")
    for a in order:
        b = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{a.replace('-', '')}/"
        er = find_reports(get(b + "FilingSummary.xml", cache))
        meta["filings"].append((a, "FY2015 era" if a == fy15_accn else "", {k: v[1] for k, v in er.items()}))
        if not er:
            era_lines.append(f"- 10-K {a}: no FilingSummary R pages (pre-XBRL viewer or unavailable) (auto)")
            continue
        pgs: dict[str, dict] = {}
        for dp in era_accns[a]:
            spec = next(d for d in DP if d[0] == dp)
            if spec[1] not in er:
                era_lines.append(f"- {dp}: 10-K {a} statement not identified (auto)")
                continue
            if spec[1] not in pgs:
                pgs[spec[1]] = parse_r(get(b + er[spec[1]][1], cache))
            pg = pgs[spec[1]]
            r = opex_row(pg)[0] if dp == "operating_expenses" else match_row(pg, dp, spec[2], spec[3])
            tagname = "FY2015" if a == fy15_accn else "era"
            if r:
                c = pick_cols(pg, spec[1])
                v = scaled(r["vals"][c[0]], dp, pg) if c and c[0] < len(r["vals"]) else None
                era_lines.append(f"- {dp}: {tagname} 10-K {a} {er[spec[1]][1]} prints '{r['label'][:80]}' on {r['tag'][:120]} = {fmt(v)} (FILING-CHECKED)")
            else:
                era_lines.append(f"- {dp}: {tagname} 10-K {a} {er[spec[1]][1]} read; no row matched (auto)")
    meta["era_lines"] = era_lines
    meta["quirks"] = quirks
    return out, quirks, meta


COLS = ["ticker", "data_point", "status", "tags", "stmt", "r_page", "label", "fy0_printed", "fy0_api", "fy1_printed",
        "fy1_api", "match", "era_from_note", "evidence_class", "note"]


def write_company(out: list[dict], meta: dict, out_dir: str) -> None:
    tic = meta["ticker"]
    for r in out:
        if "check:" not in str(r.get("note", "")):
            r["note"] = "check: machine-full-filing | " + str(r.get("note", ""))
    with open(os.path.join(out_dir, f"{tic}-docmap-{DATE}.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS, extrasaction="ignore")
        w.writeheader()
        for r in out:
            w.writerow({k: r.get(k, "") for k in COLS})
    L = [f"# {tic} document-first map {DATE} (read-only, bottom-up)", "",
         "Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element "
         "references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: "
         "status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss "
         "is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): "
         "stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.", "",
         "## Filings opened"]
    if meta.get("error"):
        L.append(f"- none: {meta['error']} (CIK {meta['cik']}, {meta['name']})")
    for a, filed, reps in meta["filings"]:
        L.append(f"- 10-K {a} (CIK {meta['cik']}{', filed ' + filed if filed else ', era filing'}): "
                 + ", ".join(f"{k} {v}" for k, v in reps.items()))
    L.append("- companyfacts CIK" + meta["cik"] + ".json (one call); submissions CIK" + meta["cik"] + f".json (SIC {meta.get('sic', '')}).")
    L += ["", "## Data points", "| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in out:
        L.append("| " + " | ".join(str(r.get(k, "")).replace("|", "/") for k in
                                    ["data_point", "status", "tags", "r_page", "label", "fy0_printed", "fy0_api",
                                     "fy1_printed", "fy1_api", "match", "evidence_class", "note"]) + " |")
    L += ["", "## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)"] + (meta.get("era_lines") or ["none found in companyfacts"])
    mism = [r for r in out if str(r.get("match", "")).startswith("N") or r.get("match") == "API missing"]
    L += ["", "## Mismatches (printed vs API)"] + ([f"- {r['data_point']}: {r['match']} ({r.get('tags', '')})" for r in mism]
                                                   or ["none beyond sign differences"])
    open(os.path.join(out_dir, f"{tic}-docmap-{DATE}.md"), "w").write("\n".join(L) + "\n")


def main() -> None:
    cohort, first, last, out_dir, cache, inbox = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], sys.argv[5], sys.argv[6]
    os.makedirs(cache, exist_ok=True)
    rows = list(csv.DictReader(open(cohort)))
    for rank in range(first, last + 1):
        row = rows[rank - 1]
        if os.path.exists(os.path.join(out_dir, f"{row['ticker']}-docmap-{DATE}.md")):
            continue
        try:
            out, quirks, meta = read_company(row, cache)
        except Exception as exc:  # one company must not stop the range
            out, quirks, meta = [], [], {"ticker": row["ticker"], "cik": row["cik"].zfill(10), "name": row["name"],
                                         "filings": [], "error": f"tool error {exc!r}"[:200]}
        write_company(out, meta, out_dir)
        with open(inbox, "a") as fh:
            for q in quirks:
                fh.write(q + "\n")
        n = len(out)
        ok = sum(1 for r in out if str(r.get("match", "")).startswith("Y"))
        print(f"rank {rank} {row['ticker']}: rows {n}, matched {ok}, quirks {len(quirks)}"
              + (f", ERROR {meta.get('error')}" if meta.get("error") else ""), flush=True)


if __name__ == "__main__":
    main()
