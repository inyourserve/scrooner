"""Hand-check view (Dhairya 2026-11-12): for each ticker, every docmap row with its check class, then the filing's own
R pages printed once (face statements, every page a row cites, the page presenting finance lease liabilities), so a
reader can judge each row against the filing.

Check classes: CHECK = must be hand-checked (every not_presented, combined, component, NOTE row, and mapped rows the
machine itself flags: no API value, extension tag, label match); SAMPLE = the seeded random 10% of the other mapped
rows (the disagreement rate is measured on these only).
usage: handcheck.py <reads_out> <tool_cache> TICKER [...]"""

import csv
import json
import random
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup

FACE = re.compile(r"^R\d+\.htm$")
LEASE = (
    "FinanceLeaseLiabilityCurrent",
    "FinanceLeaseLiabilityNoncurrent",
    "FinanceLeaseLiability",
)


def key(url: str) -> str:
    return re.sub(r"\W", "_", url)[-150:]


def rows_of(page: str) -> list[tuple[str, list[str]]]:
    soup = BeautifulSoup(page, "lxml")
    t = soup.find("table", class_="report") or soup.find("table")
    res = []
    for tr in t.find_all("tr") if t else []:
        a = tr.find("a", onclick=True)
        m = re.search(r"defref_([A-Za-z0-9-]+)_(\w+)'", a["onclick"]) if a else None
        cells = [" ".join(c.get_text(" ").split()) for c in tr.find_all(["td", "th"])]
        res.append(((f"{m.group(1)}:{m.group(2)}" if m else ""), cells))
    return res


def risky(r: dict) -> bool:
    return (
        r["match"] == "API missing"
        or "extension tag" in r["note"]
        or "matched by printed label" in r["note"]
    )


def classes(rows: list[dict], tic: str) -> tuple[set[str], set[str]]:
    must = {
        r["data_point"]
        for r in rows
        if r["status"] != "mapped" or r["stmt"] == "NOTE" or risky(r)
    }
    pool = [r for r in rows if r["data_point"] not in must]
    k = max(1, round(len(pool) * 0.10)) if pool else 0
    pick = (
        {r["data_point"] for r in random.Random(f"301-400:{tic}").sample(pool, k)}
        if k
        else set()
    )
    return must, pick


def face_pages(md: str) -> list[str]:
    m = re.search(r"\(CIK \d{10}, filed [^)]*\): (.*)", md)
    return re.findall(r"\b(?:IS|BS|CF|BSP|CI|EQ) (R\d+\.htm)", m.group(1)) if m else []


def lease_page(ml: Path) -> tuple[str | None, str]:
    if not ml.exists():
        return None, "MetaLinks not cached"
    try:
        inst = next(iter(json.loads(ml.read_text())["instance"].values()))
    except (ValueError, KeyError, StopIteration):
        return None, "MetaLinks unreadable"
    tags = [k for k in inst.get("tag", {}) if "FinanceLease" in k and "Liabilit" in k]
    role2r = {
        v.get("role"): (k, v.get("menuCat", ""), v.get("shortName", ""))
        for k, v in inst.get("report", {}).items()
    }
    for tg in LEASE:
        t = inst.get("tag", {}).get(f"us-gaap_{tg}") or {}
        rs = sorted(
            (role2r[x] for x in t.get("presentation", []) if x in role2r),
            key=lambda x: (x[1] != "Details", int(re.sub(r"\D", "", x[0]) or 0)),
        )
        if rs:
            return (
                f"{rs[0][0]}.htm",
                f"finance-lease tags {tags}; {tg} presented on {[x[0] for x in rs]}",
            )
    return None, f"finance-lease liability tags in filing: {tags or 'none'}"


def main(out: Path, cache: Path, tickers: list[str]) -> None:
    for tic in tickers:
        rows = list(csv.DictReader((out / f"{tic}-docmap-2026-11-12.csv").open()))
        md = (out / f"{tic}-docmap-2026-11-12.md").read_text()
        m = re.search(r"10-K (\d{10}-\d\d-\d{6}) \(CIK (\d{10}), filed", md)
        if not m:
            print(f"=== {tic}: no latest filing in md")
            continue
        accn, cik = m.groups()
        base = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accn.replace('-', '')}/"
        must, pick = classes(rows, tic)
        print(f"=== {tic} cik {cik} accn {accn} | CHECK {len(must)} SAMPLE {len(pick)}")
        for r in rows:
            flag = (
                "CHECK "
                if r["data_point"] in must
                else ("SAMPLE" if r["data_point"] in pick else "      ")
            )
            print(
                f"{flag} {r['data_point']} | {r['status']} | {r['tags'][:160]} | {r['stmt']} {r['r_page']} | "
                f"fy0 {r['fy0_printed']} api {r['fy0_api']} fy1 {r['fy1_printed']} | {r['match'][:30]} | {r['note'][:150]}"
            )
        lp, why = lease_page(cache / key(base + "MetaLinks.json"))
        print(f"## leases: {why}")
        pages = (
            face_pages(md)
            + [p for r in rows for p in r["r_page"].split("+") if FACE.match(p)]
            + ([lp] if lp else [])
        )
        for pg in dict.fromkeys(pages):
            f = cache / key(base + pg)
            if not f.exists():
                print(f"## {pg}: NOT FETCHED")
                continue
            prs = rows_of(f.read_text(encoding="utf8", errors="ignore"))
            print(f"## {pg}: {' / '.join(' | '.join(t) for _, t in prs[:2])[:200]}")
            for e, t in prs[2:]:
                if len(t) > 1 and any(x for x in t[1:]):
                    print(f"   {e} | {' | '.join(t)[:150]}")


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3:])
