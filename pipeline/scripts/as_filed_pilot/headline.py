"""Headline-cell check: a deliberately tiny presentation-rule mapping (NOT the standardization layer) applied to the
as-filed face lines, compared with stored analytics.canonical_fact. stdlib only.
usage: python3 -I headline.py <workdir> <out.json>"""
import glob, gzip, json, sys, collections
from datetime import date
from decimal import Decimal

W, OUT = sys.argv[1], sys.argv[2]
TICK = {"1045810": "NVDA", "320193": "AAPL", "1652044": "GOOG", "1288776": "GOOG", "789019": "MSFT", "1018724": "AMZN",
        "1326801": "META", "1730168": "AVGO", "1441634": "AVGO", "1318605": "TSLA", "59478": "LLY", "723125": "MU"}
REV = {"Revenues", "SalesRevenueNet", "RevenueFromContractWithCustomerExcludingAssessedTax",
       "RevenueFromContractWithCustomerIncludingAssessedTax", "SalesRevenueGoodsNet", "SalesRevenueServicesNet"}
ym_stored = None
def ym_s(s):
    """FSDS rounds ddate to the NEAREST month-end (verified: AAPL 2015-03-28 -> 2015-03-31); apply the same rounding to
    stored dates so 52/53-week calendars (MU, AVGO: period ends early in a month) match."""
    y, m, d = int(s[:4]), int(s[5:7]), int(s[8:10])
    if d <= 15:
        m -= 1
        if m == 0:
            y, m = y - 1, 12
    return f"{y:04d}-{m:02d}"


def qtrs_of(a, b):
    y0, m0, d0 = map(int, a.split("-")); y1, m1, d1 = map(int, b.split("-"))
    return round((date(y1, m1, d1) - date(y0, m0, d0)).days / 91.3)


rows = collections.defaultdict(list)
for fn in sorted(glob.glob(f"{W}/out/*.jsonl.gz")):
    for l in gzip.open(fn, "rt"):
        r = json.loads(l)
        if r["value"] and r["dims"] == "" and r["coreg"] == "" and r["stmt"] in ("IS", "BS", "CF") and r["inpth"] == "0":
            rows[r["adsh"]].append(r)

# cell extraction: concept -> {(ticker, ym, qtrs): [(filed, adsh, tag, value)]}
cells = {k: collections.defaultdict(list) for k in ("revenue", "diluted_eps", "total_assets", "net_income", "cfo")}
revtag = collections.defaultdict(collections.Counter)  # ticker -> (year, tag) counts for 10-K current
for adsh, rs in rows.items():
    t = TICK[rs[0]["cik"]]; filed = rs[0]["filed"]
    by_cell = collections.defaultdict(list)
    for r in rs:
        by_cell[(r["end"][:7], r["qtrs"])].append(r)
    for (e, q), lst in by_cell.items():
        lst.sort(key=lambda r: (r["report"], r["line"]))
        isr = [r for r in lst if r["stmt"] == "IS"]
        # revenue: presentation total line (label 'total' + revenue tag) else first revenue-tag line
        cand = [r for r in isr if r["tag"] in REV and r["is_total"]] or [r for r in isr if r["tag"] in REV]
        if cand:
            r = cand[0]; cells["revenue"][(t, e, q)].append((filed, adsh, r["tag"], Decimal(r["value"])))
            if r["form"].startswith("10-K") and r["period"][:6].replace("-", "") == e.replace("-", ""):
                revtag[t][(e[:4], r["tag"], r["label"][:40])] += 1
        for r in isr:
            if r["tag"] == "EarningsPerShareDiluted":
                cells["diluted_eps"][(t, e, q)].append((filed, adsh, r["tag"], Decimal(r["value"]))); break
        pick = [r for r in isr if r["tag"] == "NetIncomeLoss"] or [r for r in isr if r["tag"] == "ProfitLoss"]
        if pick:
            r = pick[0]; cells["net_income"][(t, e, q)].append((filed, adsh, r["tag"], Decimal(r["value"])))
        for r in lst:
            if r["stmt"] == "BS" and r["tag"] == "Assets":
                cells["total_assets"][(t, e, 0)].append((filed, adsh, r["tag"], Decimal(r["value"]))); break
        for r in lst:
            if r["stmt"] == "CF" and r["tag"] == "NetCashProvidedByUsedInOperatingActivities":
                cells["cfo"][(t, e, q)].append((filed, adsh, r["tag"], Decimal(r["value"]))); break

res = {"agree": collections.Counter(), "disagree": [], "revenue_tags": {t: sorted((k, v) for k, v in c.items()) for t, c in revtag.items()}}
STORED = {"revenue": ("revenue_resolved", "revenue"), "diluted_eps": ("diluted_eps_resolved", "diluted_eps"), "total_assets": ("total_assets",),
          "net_income": ("net_income",), "cfo": ("cfo",)}
for t in sorted(set(TICK.values())):
    canon = collections.defaultdict(dict)
    for l in gzip.open(f"{W}/stored/canon_{t}.jsonl.gz", "rt"):
        n, s, e, fy, fp, v, src = json.loads(l)
        q = 0 if s == e else qtrs_of(s, e)
        canon[n][(ym_s(e), q)] = Decimal(v)
    for concept, names in STORED.items():
        for key, lst in cells[concept].items():
            if key[0] != t: continue
            sv = None
            for n in names:
                sv = canon.get(n, {}).get((key[1], key[2]))
                if sv is not None: break
            if key[1] < "2015-01": continue
            lst.sort()
            latest, orig = lst[-1][3], lst[0][3]
            if sv is None:
                res["agree"][(concept, "no_stored_cell")] += 1; continue
            if sv == latest and sv == orig: res["agree"][(concept, "agree_all_vintages")] += 1
            elif sv == latest: res["agree"][(concept, "agree_latest_only")] += 1
            elif sv == orig: res["agree"][(concept, "agree_original_only")] += 1
            elif any(sv == x[3] for x in lst): res["agree"][(concept, "agree_middle_vintage")] += 1
            else:
                kind = "DISAGREE"
                if concept == "diluted_eps" and sv != 0:
                    ratio = latest / sv
                    if abs(ratio - round(ratio)) < Decimal("0.02") and round(ratio) > 1:
                        kind = "DISAGREE_stored_is_asfiled_div_%d (split-adjusted stored)" % round(ratio)
                res["agree"][(concept, kind)] += 1
                res["disagree"].append({"t": t, "concept": concept, "end": key[1], "qtrs": key[2], "stored": str(sv), "asfiled": [(x[0], x[1], x[2], str(x[3])) for x in lst]})
res["agree"] = {f"{a}|{b}": v for (a, b), v in sorted(res["agree"].items())}
json.dump(res, open(OUT, "w"), indent=1, default=str)
for k, v in res["agree"].items(): print(k, v)
