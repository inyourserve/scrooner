"""Classify pilot gap keys (no_mapped_line_cond, no_face_print_for_period) against the filings themselves, read from
FSN-store company directories (FORMATS-v1: pre = the filing's rendered statement rows, num = its values). Read-only;
zero SEC requests, zero database reads.

For each key (cik, data point, grain, period_end) every filing that prints that column (FSN month-end date, 4 quarters
for FY flows, 0 for instants) on the data point's statement is opened, and its face lines are searched for the data
point by element and by printed label. One class per key:
  printed_rule_misses      a face line of the concept is valued in that column (tag, label, accession, report)
  not_presented            filings print the column, none prints a line of the concept (their face labels listed)
  dimensional_or_valueless the concept's line is on the face but its undimensioned value for the column is missing
  no_filing_prints_period  no stored filing prints that column on that statement
usage: pilot_gap_classify.py <gaps.csv> <library.csv> <out.jsonl> <companies_dir>... [--alias new=old,...]
"""
import csv
import json
import re
import sys
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from fsn_company import table  # noqa: E402

CAUSES = ("no_mapped_line_cond", "no_face_print_for_period")
INSTANT = {"total_assets_resolved", "total_liabilities_resolved", "stockholders_equity_resolved", "current_assets_resolved",
           "current_liabilities_resolved", "total_debt_resolved", "cash_and_equivalents_resolved"}
# data point -> (statement, element regex, label regex): a SEARCH net for evidence, never a mapping rule
CONCEPT = {
    "cost_of_revenue_resolved": ("IS", r"^CostOf(Revenue|GoodsAndServicesSold|GoodsSold|Services)", r"^\s*(total )?cost(s)? of (revenue|sales|goods|products|services)"),
    "gross_profit_resolved": ("IS", r"^GrossProfit$", r"gross (profit|margin)"),
    "operating_income_resolved": ("IS", r"^OperatingIncomeLoss$", r"^\s*(total )?operating (income|profit)|income from operations"),
    "revenue_sanity_resolved": ("IS", r"^(Revenues|RevenueFromContractWithCustomer\w*|RevenuesNetOfInterestExpense|SalesRevenueNet|SalesAndOtherOperatingRevenue\w*|RealEstateRevenueNet)$",
                                r"^\s*total (net )?revenues?|^\s*(net )?revenues?,? net|^\s*total net revenue"),
    "stockholders_equity_resolved": ("BS", r"^StockholdersEquity", r"^\s*total (share|stock)holders.? equity\s*$"),
    "total_liabilities_resolved": ("BS", r"^Liabilities$", r"^\s*total liabilities\s*$"),
    "total_assets_resolved": ("BS", r"^Assets$", r"^\s*total assets\s*$"),
    "current_assets_resolved": ("BS", r"^AssetsCurrent$", r"total current assets"),
    "current_liabilities_resolved": ("BS", r"^LiabilitiesCurrent$", r"total current liabilities"),
    "total_debt_resolved": ("BS", r"Debt|Borrowing", r"debt|borrowing"),
    "share_buybacks_resolved": ("CF", r"PaymentsForRepurchaseOf(Common|Equity)|TreasuryStockValueAcquired",
                                r"(repurchase|buy.?back|purchase)s? of (common|company|own|treasury)? ?(stock|shares)|treasury stock"),
    "depreciation_and_amortization_resolved": ("CF", r"^Depreciation|AmortizationOfIntangible", r"depreciation"),
}


# the statement's own anchor total (fsn_store.select.ANCHOR_TAGS, plus the L&E / OCF variants): a column is on the face
# only where it is valued
ANCHOR = {"IS": {"NetIncomeLoss", "ProfitLoss", "NetIncomeLossAvailableToCommonStockholdersBasic", "IncomeLossFromContinuingOperations"},
          "BS": {"Assets", "LiabilitiesAndStockholdersEquity", "LiabilitiesAndPartnersCapital"},
          "CF": {"NetCashProvidedByUsedInOperatingActivities", "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations"}}
# the last FSN set in the store is 2026m09: a Q3 2026 report (period 2026-09-30, filed Oct/Nov) is not in it yet
LAST_FSN_PERIOD_END = "2026-09-01"


def month_end(d):
    y, m, dd = int(d[:4]), int(d[5:7]), int(d[8:10])
    if dd < 15:
        return (date(y, m, 1) - timedelta(days=1))
    return date(y + (m == 12), m % 12 + 1, 1) - timedelta(days=1)


def load_company(dirs):
    subs, pre, vals, dims = {}, defaultdict(list), {}, defaultdict(int)
    for d in dirs:
        for r in table(d, "sub"):
            subs.setdefault(r["adsh"], r)
        for r in table(d, "pre"):
            if r["adsh"] in subs:
                pre[r["adsh"]].append(r)
        for r in table(d, "num"):
            if r["adsh"] in subs and r["dimh"] == "0x00000000" and not (r.get("coreg") or "").strip() and r["value"] not in ("", None):
                vals[(r["adsh"], r["tag"], r["ddate"], r["qtrs"])] = r["value"]
        for r in table(d, "num"):
            if r["adsh"] in subs and r["dimh"] != "0x00000000":
                dims[(r["adsh"], r["tag"], r["ddate"], r["qtrs"])] += 1
    return subs, pre, vals, dims


def classify(dp, grain, end, subs, pre, vals, dims):
    stmt, tag_rx, lab_rx = CONCEPT[dp]
    dd = month_end(end).strftime("%Y%m%d")
    q = "0" if dp in INSTANT else ("4" if grain == "FY" else "1")
    printing = []  # filings whose statement face prints the column: the statement's own anchor total is valued there
    for adsh, rows in pre.items():
        face = [r for r in rows if r["stmt"] == stmt and r["inpth"] == "0"]
        valued = [r for r in face if (adsh, r["tag"], dd, q) in vals]
        # a face column: the anchor total is valued AND at least half of the face's valued lines print there (a later
        # filing's note can carry an older date's total, which is not a face column)
        lines_with_values = [r for r in face if not r["tag"].endswith("Abstract")]
        if any(r["tag"] in ANCHOR[stmt] for r in valued) and len(valued) * 2 >= len(lines_with_values):
            printing.append((subs[adsh].get("accepted", ""), adsh, face))
    printing.sort(reverse=True)
    if not printing:
        if end >= LAST_FSN_PERIOD_END:
            return {"class": "filing_newer_than_fsn_set", "column": [dd, q]}
        if q == "1" and any(subs[a]["form"].startswith("10-K") and subs[a]["period"] == dd for a in pre):
            return {"class": "q4_no_three_month_column", "column": [dd, q]}
        return {"class": "no_filing_prints_period", "column": [dd, q]}
    hits, valueless = [], []
    for _acc, adsh, face in printing:
        for r in face:
            if re.search(tag_rx, r["tag"]) or re.search(lab_rx, r["plabel"] or "", re.I):
                v = vals.get((adsh, r["tag"], dd, q))
                rec = {"accession": adsh, "form": subs[adsh]["form"], "report": r["report"], "line": r["line"], "tag": r["tag"],
                       "custom": not r["version"].startswith(("us-gaap", "srt", "dei", "ifrs")), "plabel": r["plabel"], "value": v}
                if v is not None:
                    hits.append(rec)
                else:
                    valueless.append(dict(rec, dimensional_rows=dims.get((adsh, r["tag"], dd, q), 0)))
    if hits:
        return {"class": "printed_rule_misses", "column": [dd, q], "lines": hits[:6]}
    if valueless:
        return {"class": "dimensional_or_valueless", "column": [dd, q], "lines": valueless[:6]}
    _acc, adsh, face = printing[0]
    return {"class": "not_presented", "column": [dd, q], "latest_printing_filing": adsh, "form": subs[adsh]["form"],
            "filings_printing_column": len(printing),
            "face_labels": [f"{r['report']}/{r['line']} {r['tag']}: {r['plabel']}" for r in face][:60]}


def main(argv):
    gaps_path, lib_path, out_path = argv[1:4]
    rest = [a for a in argv[4:] if not a.startswith("--")]
    alias = {}
    if "--alias" in argv:
        for pair in argv[argv.index("--alias") + 1].split(","):
            new, old = pair.split("=")
            alias[new.zfill(10)] = old.zfill(10)
        rest = [a for a in rest if "=" not in a]
    dirs = {Path(p).name: Path(p) for p in rest}
    lib = defaultdict(list)
    for r in csv.DictReader(open(lib_path)):
        lib[(r["cik"], r["data_point"])].append({k: r[k] for k in ("status", "stmt", "tag", "plabel", "rule_id", "filings")})
    gaps = [r for r in csv.DictReader(open(gaps_path)) if r["cause"] in CAUSES]
    by_cik = defaultdict(list)
    for g in gaps:
        by_cik[g["cik"]].append(g)
    with open(out_path, "w") as fo:
        for cik, rows in sorted(by_cik.items()):
            cdirs = [dirs[c] for c in (cik, alias.get(cik)) if c and c in dirs]
            if not cdirs:
                for g in rows:
                    fo.write(json.dumps({**g, "class": "company_not_in_store"}) + "\n")
                continue
            data = load_company(cdirs)
            for g in rows:
                res = classify(g["data_point"], g["grain"], g["period_end"], *data)
                fo.write(json.dumps({**g, **res, "library": lib.get((cik, g["data_point"]), [])[:4]}) + "\n")


if __name__ == "__main__":
    main(sys.argv)
