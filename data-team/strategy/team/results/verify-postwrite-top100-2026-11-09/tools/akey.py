"""Answer key for the post-write sample: values read from the filings' own R pages (Statements), by XBRL tag."""
import sys, re, json, csv
from datetime import date, timedelta
from decimal import Decimal
sys.path.insert(0, sys.path[0])
from sec import reports, page, get, folder
from scrooner_pipeline.verification.filing_kit import parse_number, _reports

TAGS = {
 "revenue": ["Revenues","RevenueFromContractWithCustomerExcludingAssessedTax","SalesRevenueNet","RevenuesNetOfInterestExpense","RevenueFromContractWithCustomerIncludingAssessedTax","SalesRevenueGoodsNet","RevenuesNetOfInterestExpense"],
 "net_income": ["NetIncomeLoss","NetIncomeLossAvailableToCommonStockholdersBasic","ProfitLoss"],
 "operating_income": ["OperatingIncomeLoss"],
 "gross_profit": ["GrossProfit"],
 "cost_of_revenue": ["CostOfRevenue","CostOfGoodsAndServicesSold","CostOfGoodsSold","CostOfServices","CostOfGoodsAndServiceExcludingDepreciationDepletionAndAmortization"],
 "pretax_income": ["IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest","IncomeLossFromContinuingOperationsBeforeIncomeTaxes","IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments","IncomeLossFromContinuingOperationsBeforeIncomeTaxesDomestic"],
 "income_tax": ["IncomeTaxExpenseBenefit","IncomeTaxExpenseBenefitContinuingOperations"],
 "interest_expense": ["InterestExpense","InterestExpenseNonoperating","InterestExpenseDebt","InterestAndDebtExpense","InterestExpenseOperating"],
 "cfo": ["NetCashProvidedByUsedInOperatingActivities","NetCashProvidedByUsedInOperatingActivitiesContinuingOperations"],
 "share_buybacks": ["PaymentsForRepurchaseOfCommonStock","PaymentsForRepurchaseOfEquity"],
 "dividends_paid": ["PaymentsOfDividendsCommonStock","PaymentsOfDividends","PaymentsOfOrdinaryDividendsCommonStockAndDividendEquivalents","PaymentsOfOrdinaryDividends","PaymentsOfCapitalDistribution"],
 "eps_basic": ["EarningsPerShareBasic","IncomeLossFromContinuingOperationsPerBasicShare"],
 "eps_diluted": ["EarningsPerShareDiluted","EarningsPerShareBasicAndDiluted","IncomeLossFromContinuingOperationsPerDilutedShare"],
 "dps": ["CommonStockDividendsPerShareDeclared","CommonStockDividendsPerShareCashPaid"],
 "shares_outstanding": ["EntityCommonStockSharesOutstanding","CommonStockSharesOutstanding"],
}
STMT = {"is": r"income|operations|earnings", "cf": r"cash flow", "eps": r"income|operations|earnings|equity|stockholders|shareholders", "sh": r"cover|document and entity|balance sheet|financial (position|condition)"}

def pages_for(cik, adsh, kind):
    reps, files = reports(cik, adsh)
    out = []
    for n, f, m in reps:
        if kind == "sh" and re.search(r"cover|document and entity", n, re.I):
            out.append((n, f)); continue
        if m != "Statements" and reps and any(mm == "Statements" for _, _, mm in reps): continue
        if re.search(r"parenth", n, re.I) and kind != "sh": continue
        if re.search(STMT[kind], n, re.I) and not (kind == "is" and re.search(r"comprehensive income", n, re.I) and not re.search(r"income and comprehensive|operations and comprehensive|earnings and comprehensive", n, re.I)):
            if kind != "sh" or "arenth" in n or re.search(r"balance", n, re.I):
                out.append((n, f))
    if kind in ("is", "eps") and not out:
        out = [(n, f) for n, f, m in reps if re.search(r"comprehensive income", n, re.I) and not re.search(r"parenth", n, re.I)]
    if kind == "cf" and not out:
        out = [(n, f) for n, f, m in reps if re.search(r"cash flow", n, re.I) and not re.search(r"parenth|supplement", n, re.I)]
    return out[:4]

def share_mult(title):
    m = re.search(r"shares in (thousands|millions|billions)", title, re.I)
    return {"thousands":1000,"millions":1000000,"billions":10**9}[m.group(1).lower()] if m else 1

def read(cik, adsh, dp, kind, end, months, instant=False):
    """[(value Decimal, label, tag, page, colinfo)] for the period column, ordered by tag priority."""
    e = date.fromisoformat(end); hits = []
    for n, f in pages_for(cik, adsh, kind):
        pg, raw = page(cik, adsh, f)
        ncol = len(pg.columns)
        for lab, tags, cells in raw:
            if lab.startswith("- "): continue
            tg = [t.split("_",1)[-1] for t in tags]
            pri = [i for i, t in enumerate(TAGS[dp]) if t in tg]
            if not pri: continue
            cells = cells[-ncol:] if len(cells) >= ncol else [""]*(ncol-len(cells)) + cells
            for i, d in enumerate(pg.columns):
                ok = abs((d - e).days) <= 7 if not (dp == "shares_outstanding" and "cover" in n.lower() or "entity" in n.lower()) else True
                if not ok: continue
                if not instant and months and pg.months[i] not in (months, None): continue
                v = parse_number(re.sub(r"[A-Za-z][\w-]*_\w+.*$", "", cells[i])) if i < len(cells) else None
                if v is None: continue
                mult = 1 if dp in ("eps_basic","eps_diluted","dps") else (share_mult(pg.title) if dp == "shares_outstanding" else pg.multiplier)
                hits.append((min(pri), v * mult, lab[:70], TAGS[dp][min(pri)], f"{f} {n[:50]}", f"{d}/{pg.months[i]}"))
    hits.sort(key=lambda h: h[0])
    return hits

def ymd(s): return date.fromisoformat(s)
def run(row):
    tk, cik, dp, kind, grain, end, own, later, prior = row
    cik = cik.lstrip("0") if tk != "XOM" else "34088"
    later = [x.split(":") for x in later.split()] if later else []
    prior = [x.split(":") for x in prior.split()] if prior else []
    res = {"tk": tk, "cik": row[1], "data_point": dp, "grain": grain, "period_end": end}
    try:
        if grain == "FY" or (grain == "Q" and kind != "cf"):
            months = 12 if grain == "FY" else 3
            cands = [(end, own)] + ([x for x in later] if grain == "FY" else [x for x in later if 350 <= (ymd(x[0]) - ymd(end)).days <= 380])
            reads = []
            for por, acc in cands:
                h = read(cik, acc, dp, kind, end, months, instant=(kind == "sh"))
                reads.append((acc, h[0] if h else None, len(h)))
            printed = [r for r in reads if r[1]]
            res["original"] = str(reads[0][1][1]) if reads[0][1] else ""
            res["expected"] = str(printed[-1][1][1]) if printed else ""
            res["expected_from"] = f"{printed[-1][0]} {printed[-1][1][4]} | {printed[-1][1][2]} | {printed[-1][1][3]}" if printed else "no line of the concept on the statements read (blank expected, or a note source)"
            res["route"] = "printed"
            res["copies"] = "; ".join(f"{a}={(h[1] if h else '-')}" for a, h, _ in reads)
        else:
            # derived: Q4 = FY - 9M (QD), or CF quarter = YTD(n) - YTD(n-3)
            if grain == "QD":
                fy = [(end, own)] + later
                ytd_now = []
                for por, acc in fy:
                    h = read(cik, acc, dp, kind, end, 12); ytd_now.append((acc, h[0] if h else None))
                p9 = []
                for por, acc in prior:
                    q3end = (ymd(por) if ymd(por) < ymd(end) else None)
                for por, acc in prior:
                    h = read(cik, acc, dp, kind, None or str([p for p, a in prior if ymd(p) < ymd(end)][0]), 9); p9.append((acc, h[0] if h else None))
                a = [x for x in ytd_now if x[1]]; b = [x for x in p9 if x[1]]
                res["route"] = "derived Q4 = FY - 9M"
            else:
                # CF quarter from a 10-Q: months = YTD length
                cands = [(end, own)] + [x for x in later if 350 <= (ymd(x[0]) - ymd(end)).days <= 380]
                ytd_now = []
                for por, acc in cands:
                    for mo in (3, 6, 9):
                        h = read(cik, acc, dp, kind, end, mo)
                        if h: ytd_now.append((acc, h[0], mo)); break
                mo = ytd_now[-1][2] if ytd_now else None
                if mo == 3:
                    res["route"] = "printed (Q1 = 3M YTD)"; a = [(x[0], x[1]) for x in ytd_now]; b = None
                else:
                    pend = [p for p, acc in prior if ymd(p) < ymd(end)]
                    p9 = []
                    for por, acc in prior:
                        h = read(cik, acc, dp, kind, pend[0], (mo or 6) - 3) if pend else []
                        p9.append((acc, h[0] if h else None))
                    a = [(x[0], x[1]) for x in ytd_now]; b = [x for x in p9 if x[1]]
                    res["route"] = f"derived = {mo}M YTD - {(mo or 6)-3}M YTD"
            if b is None:
                res["expected"] = str(a[-1][1][1]) if a else ""; res["expected_from"] = f"{a[-1][0]} {a[-1][1][4]} | {a[-1][1][2]}" if a else "not printed"
            else:
                if a and b:
                    res["expected"] = str(a[-1][1][1] - b[-1][1][1])
                    res["expected_from"] = f"{a[-1][0]} ({a[-1][1][1]}, {a[-1][1][2]}) - {b[-1][0]} ({b[-1][1][1]})"
                else:
                    res["expected"] = ""; res["expected_from"] = f"inputs missing: ytd={[(x[0], x[1][1]) for x in a]} prior={[(x[0], x[1][1]) for x in b]}"
            res["original"] = ""
            res["copies"] = f"ytd={[(x[0], str(x[1][1])) for x in a]} prior={[(x[0], str(x[1][1])) for x in (b or [])]}"
    except Exception as ex:
        res["expected"] = ""; res["expected_from"] = f"ERR {ex!r}"[:200]; res.setdefault("route", "?")
    return res

if __name__ == "__main__":
    rows = [r.split(",") for r in open(sys.argv[1]).read().strip().split(";")]
    out = csv.DictWriter(open(sys.argv[2], "w"), fieldnames=["tk","cik","data_point","grain","period_end","route","expected","original","expected_from","copies"])
    out.writeheader()
    for r in rows:
        res = run(r); out.writerow(res); print(res["tk"], res["data_point"], res["grain"], res["period_end"], "->", res.get("expected"), "|", res.get("expected_from","")[:110], flush=True)
