"""As-filed face-statement extractor (PROTOTYPE, read-only, stdlib only).

Reads ONE SEC Financial Statement Data Sets quarter zip (sub/num/pre) and writes the
face balance sheet / income statement / cash flow lines of selected companies' periodic
filings, one JSON object per (presentation line x fact), in presentation order.

usage: python3 -I extract_fsds.py <quarter.zip> <out.jsonl.gz> <cik,cik,...>

Facts (FSDS contract, FILING-CHECKED against 2018q4): num.txt has ddate (end), qtrs
(duration in quarters, 0 = instant), uom, segments (dimension members), value;
it has NO start date, so start is APPROXIMATED (end - qtrs*3 months + 1 day) and
52/53-week years can be off by days; join on (end, qtrs), never on start.
pre.txt must be sorted by (report, line) before use (it is not in statement order).
Totals are NOT in FSDS (no calculation linkbase): `is_total` is a label/tag heuristic.
"""
import calendar, csv, gzip, io, json, re, sys, zipfile
from collections import defaultdict
from datetime import date, timedelta

csv.field_size_limit(1 << 24)
FORMS = {"10-K", "10-K/A", "10-KT", "10-KT/A", "10-Q", "10-Q/A", "10-QT"}
STMTS = {"BS", "IS", "CF"}
TOTAL_RE = re.compile(r"\btotal\b", re.I)
TOTAL_TAGS = {
    "Assets", "AssetsCurrent", "AssetsNoncurrent", "Liabilities", "LiabilitiesCurrent",
    "LiabilitiesNoncurrent", "LiabilitiesAndStockholdersEquity", "StockholdersEquity",
    "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest", "GrossProfit",
    "OperatingIncomeLoss", "OperatingExpenses", "CostsAndExpenses", "NetIncomeLoss",
    "ProfitLoss", "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",
    "IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments",
    "NetCashProvidedByUsedInOperatingActivities", "NetCashProvidedByUsedInInvestingActivities",
    "NetCashProvidedByUsedInFinancingActivities",
    "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseIncludingExchangeRateEffect",
    "CashAndCashEquivalentsPeriodIncreaseDecrease",
}


def d8(s):
    return date(int(s[:4]), int(s[4:6]), int(s[6:8]))


def approx_start(end, qtrs):
    if qtrs == 0:
        return None
    m = end.month - 1 - 3 * qtrs
    y = end.year + m // 12
    m = m % 12 + 1
    day = min(end.day, calendar.monthrange(y, m)[1])
    return date(y, m, day) + timedelta(days=1)


def rows(z, name):
    with z.open(name) as f:
        rd = csv.reader(io.TextIOWrapper(f, encoding="utf-8", errors="replace", newline=""), delimiter="\t", quoting=csv.QUOTE_NONE)
        hdr = next(rd)
        ix = {h: i for i, h in enumerate(hdr)}
        for r in rd:
            if len(r) >= len(hdr) - 1:
                r = r + [""] * (len(hdr) - len(r))
                yield ix, r


def main(zpath, out, ciks):
    ciks = {c.strip() for c in ciks.split(",")}
    z = zipfile.ZipFile(zpath)
    subs = {}
    for ix, r in rows(z, "sub.txt"):
        if r[ix["cik"]] in ciks and r[ix["form"]] in FORMS:
            subs[r[ix["adsh"]]] = {k: r[ix[k]] for k in ("cik", "name", "form", "period", "fy", "fp", "filed", "instance", "prevrpt", "detail")}
    pre = defaultdict(list)
    for ix, r in rows(z, "pre.txt"):
        a = r[ix["adsh"]]
        if a in subs and r[ix["stmt"]] in STMTS:
            pre[a].append((int(r[ix["report"]]), int(r[ix["line"]]), r[ix["stmt"]], r[ix["inpth"]], r[ix["tag"]], r[ix["version"]], r[ix["plabel"]], r[ix["negating"]]))
    for a in pre:
        pre[a].sort()
    nums = defaultdict(list)
    for ix, r in rows(z, "num.txt"):
        a = r[ix["adsh"]]
        if a in subs:
            nums[(a, r[ix["tag"]], r[ix["version"]])].append((r[ix["ddate"]], r[ix["qtrs"]], r[ix["uom"]], r[ix["segments"]], r[ix["coreg"]], r[ix["value"]]))
    n = 0
    with gzip.open(out, "wt", encoding="utf-8") as o:
        for a, s in subs.items():
            for (rep, line, stmt, inpth, tag, ver, label, neg) in pre.get(a, []):
                tot = bool(TOTAL_RE.search(label)) or tag in TOTAL_TAGS
                facts = nums.get((a, tag, ver), [])
                if not facts:
                    o.write(json.dumps({"adsh": a, **{k: s[k] for k in ("cik", "form", "period", "fy", "fp", "filed")}, "stmt": stmt, "report": rep, "line": line, "inpth": inpth, "tag": tag, "version": ver, "custom": ver == a, "label": label, "negating": neg, "is_total": tot, "value": None}) + "\n")
                    continue
                for dd, q, uom, seg, coreg, val in facts:
                    end = d8(dd)
                    st = approx_start(end, int(q))
                    o.write(json.dumps({"adsh": a, **{k: s[k] for k in ("cik", "form", "period", "fy", "fp", "filed")}, "stmt": stmt, "report": rep, "line": line, "inpth": inpth, "tag": tag, "version": ver, "custom": ver == a, "label": label, "negating": neg, "is_total": tot, "end": str(end), "qtrs": int(q), "start_approx": str(st) if st else None, "uom": uom, "dims": seg, "coreg": coreg, "value": val}) + "\n")
                    n += 1
    print(zpath.rsplit("/", 1)[-1], "filings", len(subs), "fact_rows", n)


main(*sys.argv[1:4])
