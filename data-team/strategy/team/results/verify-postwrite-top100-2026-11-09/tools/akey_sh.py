"""Shares outstanding: period-end CommonStockSharesOutstanding (balance-sheet parenthetical, latest copy that prints the date)
and, separately, the period's own filing's cover-page EntityCommonStockSharesOutstanding with its own date."""
import sys, re, csv
from datetime import date
sys.path.insert(0, sys.path[0])
from sec import reports, page
from scrooner_pipeline.verification.filing_kit import parse_number
def mult(title):
    m = re.search(r"shares in (thousands|millions|billions)", title, re.I)
    return {"thousands":1000,"millions":10**6,"billions":10**9}[m.group(1).lower()] if m else 1
def scan(cik, adsh, end, want_cover):
    reps, files = reports(cik, adsh); out = []
    for n, f, m in reps:
        is_cover = re.search(r"cover|document and entity", n, re.I)
        is_bsp = re.search(r"balance sheet|financial (position|condition)", n, re.I) and re.search(r"parenth", n, re.I)
        if not (is_cover and want_cover) and not is_bsp: continue
        pg, raw = page(cik, adsh, f); ncol = len(pg.columns)
        for lab, tags, cells in raw:
            tg = [t.split("_",1)[-1] for t in tags]
            tag = "EntityCommonStockSharesOutstanding" if (is_cover and "EntityCommonStockSharesOutstanding" in tg) else ("CommonStockSharesOutstanding" if (is_bsp and "CommonStockSharesOutstanding" in tg) else None)
            if not tag or lab.startswith("- "): continue
            cells = cells[-ncol:] if len(cells) >= ncol else [""]*(ncol-len(cells)) + cells
            for i, d in enumerate(pg.columns):
                if tag == "CommonStockSharesOutstanding" and abs((d - date.fromisoformat(end)).days) > 7: continue
                v = parse_number(re.sub(r"[A-Za-z][\w-]*_\w+.*$", "", cells[i]))
                if v is not None: out.append((tag, v * mult(pg.title), str(d), f, lab[:50]))
    return out
rows = [r.split(",") for r in open(sys.argv[1]).read().strip().split(";")]
w = csv.writer(open(sys.argv[2], "w")); w.writerow(["tk","grain","period_end","bs_parenthetical_latest","bs_from","own_cover_dei","own_cover_date","copies"])
for tk, cik, dp, kind, grain, end, own, later, prior in rows:
    if dp != "shares_outstanding": continue
    cik = cik.lstrip("0")
    later = [x.split(":") for x in later.split()] if later else []
    cands = [(end, own)] + [x for x in later if (grain == "FY" or 350 <= (date.fromisoformat(x[0]) - date.fromisoformat(end)).days <= 380)]
    bs = []; cover = None
    for i, (por, acc) in enumerate(cands):
        hits = scan(cik, acc, end, want_cover=(i == 0))
        for h in hits:
            if h[0] == "CommonStockSharesOutstanding": bs.append((acc, h))
            elif i == 0 and cover is None: cover = h
    w.writerow([tk, grain, end, str(bs[-1][1][1]) if bs else "", f"{bs[-1][0]} {bs[-1][1][3]} {bs[-1][1][4]}" if bs else "not printed at the date", str(cover[1]) if cover else "", cover[2] if cover else "", "; ".join(f"{a}={h[1]}" for a, h in bs)])
    print(tk, grain, end, "bs", bs[-1][1][1] if bs else None, "cover", cover[1:3] if cover else None, flush=True)
