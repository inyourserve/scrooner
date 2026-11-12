"""Hand-check helper (Dhairya 2026-11-12): for each ticker, show the filing's own R-page rows behind every row that
must be hand-checked (every not_presented, combined, component, NOTE row, plus a seeded random 10% of mapped rows),
so the reader can judge it against the filing. usage: handcheck.py <reads_out> <tool_cache> TICKER [...]
Prints missing R pages as 'NEED cik accn page' lines (fetch them, then rerun)."""

import csv
import json
import random
import re
import sys
from pathlib import Path

out, cache = Path(sys.argv[1]), Path(sys.argv[2])


def key(url):
    return re.sub(r"\W", "_", url)[-150:]


def rows_of(page):
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(page, "lxml")
    t = soup.find("table", class_="report") or soup.find("table")
    res = []
    for tr in t.find_all("tr") if t else []:
        a = tr.find("a", onclick=True)
        m = re.search(r"defref_([A-Za-z0-9-]+)_(\w+)'", a["onclick"]) if a else None
        cells = [" ".join(c.get_text(" ").split()) for c in tr.find_all(["td", "th"])]
        res.append(((f"{m.group(1)}:{m.group(2)}" if m else ""), cells))
    return res


def sample(rows, tic):
    must = [r for r in rows if r["status"] != "mapped" or r["stmt"] == "NOTE"]
    mapped = [r for r in rows if r["status"] == "mapped" and r["stmt"] != "NOTE"]
    k = max(1, round(len(mapped) * 0.10)) if mapped else 0
    pick = random.Random(f"301-400:{tic}").sample(mapped, k) if k else []
    return must, pick


for tic in sys.argv[3:]:
    p = out / f"{tic}-docmap-2026-11-12.csv"
    rows = list(csv.DictReader(p.open()))
    md = (out / f"{tic}-docmap-2026-11-12.md").read_text()
    m = re.search(r"10-K (\d{10}-\d\d-\d{6}) \(CIK (\d{10}), filed", md)
    if not m:
        print(f"=== {tic}: no latest filing in md")
        continue
    accn, cik = m.group(1), m.group(2)
    base = (
        f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accn.replace('-', '')}/"
    )
    must, pick = sample(rows, tic)
    print(
        f"=== {tic} cik {cik} accn {accn} | must {len(must)} sample {len(pick)} of {sum(r['status'] == 'mapped' for r in rows)} mapped"
    )
    for kind, r in [("MUST", x) for x in must] + [("SAMPLE", x) for x in pick]:
        print(
            f"-- {kind} {r['data_point']} [{r['status']}] tags={r['tags'][:150]} page={r['r_page']} fy0={r['fy0_printed']} api={r['fy0_api']} match={r['match'][:40]}"
        )
        print(f"   note: {r['note'][:300]}")
        pages = [x for x in dict.fromkeys(r["r_page"].split("+")) if x]
        for pg in pages:
            f = cache / key(base + pg)
            if not f.exists():
                print(f"   NEED {cik} {accn} {pg}")
                continue
            prs = rows_of(f.read_text(encoding="utf8", errors="ignore"))
            head = [t for e, t in prs[:2]]
            print(f"   {pg} head: {json.dumps(head)[:200]}")
            tags = set(r["tags"].split("+"))
            words = [w for w in re.split(r"_", r["data_point"]) if len(w) > 3]
            full = r["status"] != "mapped"
            for e, t in prs[2:]:
                if e in tags:
                    print(f"   > {e} | {' | '.join(t)[:200]}")
                elif full and len(t) > 1 and any(x for x in t[1:]):
                    print(f"     {e} | {' | '.join(t)[:110]}")
