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
    pages = {k: parse_r(get(base + fn, cache)) for k, (_, fn) in reps.items() if k in ("IS", "BS", "CF", "COVER")}
    out: list[dict] = []
    quirks: list[str] = []
    for dp, stmt, tags, rx in DP:
        page = pages.get(stmt)
        rec = {"ticker": tic, "data_point": dp, "status": "", "tags": "", "stmt": stmt,
               "r_page": reps.get(stmt, ("", ""))[1], "label": "", "fy0_printed": "", "fy0_api": "",
               "fy1_printed": "", "fy1_api": "", "match": "", "era_from_note": "", "evidence_class": "", "note": ""}
        if not page or not page["rows"]:
            rec.update(status="statement_not_found", evidence_class="FILING-CHECKED",
                       note="statement page not identified in FilingSummary (auto)")
            out.append(rec)
            continue
        r = None
        if dp == "depreciation_and_amortization":
            r = match_row(page, dp, tags, rx)
            if r is None:
                parts = [x for x in page["rows"] if x["tag"].split(":")[-1] in DA_PARTS]
                if parts:
                    r = {"tag": "+".join(p["tag"] for p in parts), "label": " + ".join(p["label"] for p in parts),
                         "vals": [sum((p["vals"][i] or 0) for p in parts) if any(p["vals"][i] is not None for p in parts if i < len(p["vals"])) else None
                                  for i in range(max(len(p["vals"]) for p in parts))], "parts": parts}
        else:
            r = match_row(page, dp, tags, rx)
        if r is None:
            rec.update(status="not_found_auto", evidence_class="FILING-CHECKED",
                       note=f"{reps[stmt][1]} read; no face row matched the {dp} tag/label rules (check by hand before calling it not_presented)")
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
        status = "component sum" if "parts" in r else ("custom_extension" if not r["tag"].startswith("us-gaap")
                                                       else ("mapped (by label)" if r.get("by_label") else "mapped"))
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
            rec["note"] = f"accn {accn} period ..{vals[0][2].isoformat()}"
        if any(v.startswith("N") for v in verdicts):
            quirks.append(f"| new | {tic} | {dp} | {r['tag']} | printed vs companyfacts mismatch: {'; '.join(v for v in verdicts if v.startswith('N'))} | {accn} {reps[stmt][1]} | FILING-CHECKED |")
        if status == "mapped (by label)":
            quirks.append(f"| new | {tic} | {dp} | {r['tag']} | face line '{r['label'][:80]}' carries a us-gaap tag outside the usual {dp} set | {accn} {reps[stmt][1]} | FILING-CHECKED |")
        if status == "custom_extension":
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
            rec.update(status="not_found_auto", note="no standard debt line on the BS face (auto)")
        out.append(rec)
    # shares outstanding from the cover page
    cov = pages.get("COVER")
    rec = {"ticker": tic, "data_point": "shares_outstanding", "stmt": "COVER", "r_page": reps.get("COVER", ("", ""))[1],
           "evidence_class": "FILING-CHECKED", "era_from_note": ""}
    if cov:
        sh = [x for x in cov["rows"] if x["tag"] == "dei:EntityCommonStockSharesOutstanding"]
        vals = [next((v for v in x["vals"] if v is not None), None) for x in sh]
        vals = [v for v in vals if v is not None]
        if vals:
            rec.update(status="mapped" if len(vals) == 1 else "component sum", tags="dei:EntityCommonStockSharesOutstanding",
                       label="Entity Common Stock, Shares Outstanding (cover)", fy0_printed=fmt(sum(vals)),
                       note="cover page" + ("; classes summed" if len(vals) > 1 else ""))
        else:
            rec.update(status="not_found_auto", note="no cover shares row (auto)")
    out.append(rec)
    # era check: a different tag carried the data point in an earlier fiscal year
    era_lines = []
    era_accns: dict[str, list[str]] = {}
    for rec in out:
        dp = rec["data_point"]
        spec = next((d for d in DP if d[0] == dp), None)
        if not spec or rec.get("status") not in ("mapped", "custom_extension") or not rec["tags"].startswith("us-gaap"):
            continue
        cur = rec["tags"].split(":", 1)[1]
        hist = annual_tag_history(cf, spec[2])
        ends = sorted(hist)[-5:]
        older = [(e, t, a) for e in ends for t, a in hist[e].items() if t != cur and cur not in hist[e]]
        if older:
            e, t, a = older[-1]
            rec["era_from_note"] = f"ERA-CHECK: {t} carried FY ending {e} (accn {a}); {cur} after"
            era_accns.setdefault(a, []).append(dp)
            quirks.append(f"| new | {tic} | {dp} | us-gaap:{t} -> us-gaap:{cur} | tag change across eras: {t} for FY ending {e}, {cur} later | {a} | DATA-INFERRED (companyfacts); era 10-K opened below |")
        else:
            rec["era_from_note"] = "tag covers last 5 FY in companyfacts"
    for a in list(era_accns)[:2]:
        b = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{a.replace('-', '')}/"
        er = find_reports(get(b + "FilingSummary.xml", cache))
        meta["filings"].append((a, "", {k: v[1] for k, v in er.items()}))
        for dp in era_accns[a]:
            spec = next(d for d in DP if d[0] == dp)
            if spec[1] not in er:
                era_lines.append(f"- {dp}: era 10-K {a} statement not identified (auto)")
                continue
            pg = parse_r(get(b + er[spec[1]][1], cache))
            r = match_row(pg, dp, spec[2], spec[3])
            if r:
                c = pick_cols(pg, spec[1])
                v = scaled(r["vals"][c[0]], dp, pg) if c and c[0] < len(r["vals"]) else None
                era_lines.append(f"- {dp}: era 10-K {a} {er[spec[1]][1]} prints '{r['label'][:80]}' on {r['tag']} = {fmt(v)} (FILING-CHECKED)")
            else:
                era_lines.append(f"- {dp}: era 10-K {a} {er[spec[1]][1]} read; no row matched (auto)")
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
         "rows marked (auto) are tool output that a person has not re-read; `not_found_auto` is NOT a not_presented verdict.", "",
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
    L += ["", "## Era checks (tag changes in the last ~5 years)"] + (meta.get("era_lines") or ["none found in companyfacts"])
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
