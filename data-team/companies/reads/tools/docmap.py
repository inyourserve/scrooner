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
                                "InterestExpenseDebt", "InterestIncomeExpenseNonoperatingNet"], r"^interest expense"),
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
    ("dividends_paid", "CF", ["PaymentsOfDividendsCommonStock", "PaymentsOfDividends"], r"dividends paid|cash dividends"),
    ("share_buybacks", "CF", ["PaymentsForRepurchaseOfCommonStock"], r"repurchase|purchases? of (common|treasury)"),
    ("cash_paid_for_interest", "CF", ["InterestPaidNet", "InterestPaid"], r"^interest paid|cash paid for interest"),
    ("cash_paid_for_income_taxes", "CF", ["IncomeTaxesPaidNet", "IncomeTaxesPaid"], r"income taxes paid|cash paid for income taxes"),
]
DEBT_TAGS = ["ShortTermBorrowings", "CommercialPaper", "DebtCurrent", "LongTermDebtCurrent", "LongTermDebtNoncurrent",
             "LongTermDebt", "LongTermDebtAndCapitalLeaseObligations", "LongTermDebtAndCapitalLeaseObligationsCurrent",
             "OtherLongTermDebtNoncurrent", "LinesOfCreditCurrent", "SeniorNotes", "ConvertibleNotesPayable"]
DA_PARTS = ["Depreciation", "AmortizationOfIntangibleAssets", "DepreciationAndAmortization"]
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


def match_row(page: dict, dp: str, tags: list[str], rx: str) -> dict | None:
    for t in tags:
        for r in page["rows"]:
            if r["tag"] == f"us-gaap:{t}" and any(v is not None for v in r["vals"]):
                return r
    if rx and rx != "^$":
        for r in page["rows"]:
            if r["tag"] and re.search(rx, r["label"], re.I) and any(v is not None for v in r["vals"]):
                return dict(r, by_label=True)  # matched by printed label (custom extension or an unlisted tag)
    return None


def _has(r: dict) -> bool:
    return any(v is not None for v in r["vals"])


def opex_row(page: dict) -> tuple[dict | None, str, str]:
    """Operating expenses never include cost of revenue (Dhairya ruling 2026-11-12).
    1. A printed total opex line that excludes COGS -> mapped.
    2. Else every face line between gross profit and operating income, summed, tied exactly to GP - OI -> component sum.
    3. A total (e.g. CostsAndExpenses) that includes COGS -> combined, never opex."""
    rows = page["rows"]
    loc = lambda tags, rx: next((i for i, r in enumerate(rows) if _has(r) and (
        r["tag"].split(":")[-1] in tags or re.search(rx, r["label"], re.I))), None)
    i_gp = loc(["GrossProfit"], r"^gross (profit|margin)")
    i_oi = loc(["OperatingIncomeLoss"], r"^(total )?operating (income|profit|earnings)|income from operations")
    i_cogs = loc(["CostOfRevenue", "CostOfGoodsAndServicesSold", "CostOfGoodsSold", "CostOfServices"],
                 r"^(total )?cost of (revenues?|sales|goods|products|services)")
    i_tot = next((i for i, r in enumerate(rows) if _has(r) and (r["tag"].split(":")[-1] in ("OperatingExpenses", "CostsAndExpenses")
                  or re.search(r"^total (operating )?(costs and )?expenses", r["label"], re.I))), None)
    v = lambda i: rows[i]["vals"][0] if rows[i]["vals"] else None
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
        rs = [role2r[x] for x in t.get("presentation", []) if x in role2r]
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
            r.update(status="mapped", stmt="NOTE" if rs[0][1] != "statement" else rs[0][1], r_page=f"{rs[0][0]}.htm",
                     tags=f"us-gaap:{t}", label=rs[0][2][:120], fy0_printed="", fy0_api=fmt(av),
                     match="", note=f"not on the face statement; shown in {rs[0][0]}.htm '{rs[0][2][:80]}' (MetaLinks.json presentation); value from companyfacts same accession" + ("" if av is not None else " (no undimensioned companyfacts fact: read the R page)"))
            quirks.append(f"| new | {tic} | {dp} | us-gaap:{t} | not on the face; reported in a note/other page {rs[0][0]}.htm '{rs[0][2][:60]}' | {accn} | FILING-CHECKED (MetaLinks) |")
            continue
        chit = [(t, where(t)) for t in comp if where(t)]
        if chit:
            t, rs = chit[0]
            r.update(status="component_in_note", stmt="NOTE", r_page=f"{rs[0][0]}.htm", tags="+".join(f"us-gaap:{c[0]}" for c in chit),
                     label=rs[0][2][:120], note=f"only component tag(s) {', '.join(c[0] for c in chit)} in the filing ({rs[0][0]}.htm '{rs[0][2][:60]}'); the data point itself is not reported")
            continue
        r.update(status="not_presented", evidence_class="FILING-CHECKED",
                 note=f"whole-filing check: none of {', '.join(full + comp)} in MetaLinks.json ({ntags} tags across all {len(role2r)} R pages, face and notes) of {accn}; no face row matched")


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
        elif dp == "depreciation_and_amortization":
            r = match_row(page, dp, tags, rx)
            if r is None:
                parts = [x for x in page["rows"] if x["tag"].split(":")[-1] in DA_PARTS]
                if parts:
                    r = {"tag": "+".join(p["tag"] for p in parts), "label": " + ".join(p["label"] for p in parts),
                         "vals": [sum((p["vals"][i] or 0) for p in parts) if any(p["vals"][i] is not None for p in parts if i < len(p["vals"])) else None
                                  for i in range(max(len(p["vals"]) for p in parts))], "parts": parts}
        else:
            r = match_row(page, dp, tags, rx)
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
                parts_api = [api_value(cf, p["tag"], accn, end, months) for p in r["parts"]]
                if all(a is not None for a in parts_api):
                    av = sum(parts_api)
            else:
                av = api_value(cf, r["tag"], accn, end, months)
            vals.append((pv, av, end))
        status = r.get("opex_status") or ("component sum" if "parts" in r else "mapped")
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
    # total debt: sum of debt rows printed on the BS
    bs = pages.get("BS")
    if bs and bs["rows"]:
        parts = [x for x in bs["rows"] if x["tag"].split(":")[-1] in DEBT_TAGS and x["tag"].startswith("us-gaap")
                 and any(v is not None for v in x["vals"])]
        cols = pick_cols(bs, "BS")
        rec = {"ticker": tic, "data_point": "total_debt", "stmt": "BS", "r_page": reps["BS"][1],
               "evidence_class": "FILING-CHECKED", "era_from_note": ""}
        if parts and cols:
            pv0 = sum((p["vals"][cols[0]] or 0) for p in parts if cols[0] < len(p["vals"])) * bs["scale"]
            api0 = [api_value(cf, p["tag"], accn, bs["cols"][cols[0]][1], None) for p in parts]
            av0 = sum(api0) if all(a is not None for a in api0) else None
            rec.update(status="component sum", tags="+".join(p["tag"] for p in parts),
                       label=" + ".join(p["label"] for p in parts)[:120], fy0_printed=fmt(pv0), fy0_api=fmt(av0),
                       match="Y" if av0 is not None and abs(pv0 - av0) < 0.5 else ("API missing" if av0 is None else "N"),
                       note="sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check)")
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
        sh = [x for x in pg["rows"] if x["tag"] == "us-gaap:CommonStockSharesOutstanding"
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
    L.append("- companyfacts CIK" + meta["cik"] + ".json (one call).")
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
