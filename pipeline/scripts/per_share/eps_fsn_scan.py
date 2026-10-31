"""Find filed 3-month EPS for Family C 'not captured' cells in the FSN num rows (bucket fsn-notes). Read-only.

For each cell: the company's 10-K/10-Q (incl. /A) facts on its concept's tags with qtrs=1 at the cell's end date
rounded to the nearest month end (FSN ddate rule), no dimension, iprx 0, no co-registrant. Outcome per cell:
  replace_with_fsn_value  every filed copy agrees (|diff| <= 0.005); witness = the earliest-filed copy
  fsn_copies_disagree     filed copies differ (restated): hidden, never chosen
  not_in_fsn              no copy in any FSN period
usage: eps_fsn_scan.py <scratch> ; env SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY
"""

import csv
import io
import re
import json
import os
import shutil
import subprocess
import sys
import urllib.request
from calendar import monthrange
from collections import Counter, defaultdict
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

csv.field_size_limit(1 << 24)
S = Path(sys.argv[1])
W = S / "epsfsn2"
W.mkdir(exist_ok=True)
(W / "nc_cells.json").write_text((S / "epsfsn" / "nc_cells.json").read_text())
FORMS = {"10-K", "10-K/A", "10-Q", "10-Q/A", "10-KT", "10-KT/A"}
TAGS = {
    "EarningsPerShareBasic",
    "EarningsPerShareDiluted",
    "EarningsPerShareBasicAndDiluted",
}
# A one-axis context is accepted only for the 10-K "quarterly financial data (unaudited)" presentation axis
# (UNH: Quarterlyfinancialdata=QuarterlyFinancialDataUnaudited); entity, segment, class and restatement axes never.
QUARTERLY_AXIS = re.compile(r"^[^;=]*quarter[^;=]*=[^;]*;?$", re.I)
REJECT_AXIS = re.compile(
    r"consolidat|entit|segment|class|series|restat|scenario|adjust|previously|parent|subsidiar",
    re.I,
)
base = os.environ["SUPABASE_URL"].rstrip("/")
key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]


def month_end(d: date) -> date:
    this = date(d.year, d.month, monthrange(d.year, d.month)[1])
    prev = d.replace(day=1) - timedelta(days=1)
    return this if (this - d) <= (d - prev) else prev


def rows(path: Path):
    p = subprocess.Popen(["zstd", "-dc", str(path)], stdout=subprocess.PIPE)
    yield from csv.DictReader(
        io.TextIOWrapper(p.stdout, encoding="utf-8", errors="replace", newline=""),
        delimiter="\t",
        quoting=csv.QUOTE_NONE,
    )
    p.wait()


def fetch(period: str, table: str, dest: Path) -> None:
    req = urllib.request.Request(
        f"{base}/storage/v1/object/fsn-notes/{period}/{period}_{table}.tsv.zst",
        headers={"Authorization": f"Bearer {key}", "apikey": key},
    )
    with urllib.request.urlopen(req, timeout=600) as r, dest.open("wb") as f:
        shutil.copyfileobj(r, f)


cells = json.load(open(W / "nc_cells.json"))
want = defaultdict(set)  # cik(10) -> {ddate yyyymmdd}
for c in cells:
    want[c["cik"].zfill(10)].add(
        month_end(date.fromisoformat(c["end"])).strftime("%Y%m%d")
    )
periods = [
    f"{y}q{q}" for y in range(2014, 2026) for q in range(1, 5) if (y, q) <= (2025, 3)
]
periods += [f"2025m{m}" for m in (10, 11, 12)] + [f"2026m{m:02d}" for m in range(1, 10)]
copies = defaultdict(list)  # (cik, tag, ddate) -> [(value, adsh, form, filed)]
progress = W / "scan_progress.json"
done = json.loads(progress.read_text())["done"] if progress.exists() else []
if (W / "copies.json").exists():
    for k, v in json.load(open(W / "copies.json")).items():
        copies[tuple(k.split("|"))] = [tuple(x) for x in v]
for period in periods:
    if period in done:
        continue
    pdir = W / period
    pdir.mkdir(exist_ok=True)
    try:
        for t in ("sub", "num", "dim"):
            fetch(period, t, pdir / f"{t}.tsv.zst")
    except urllib.error.HTTPError as e:
        print(period, "HTTP", e.code, flush=True)
        continue
    subs = {}
    for r in rows(pdir / "sub.tsv.zst"):
        cik = r["cik"].zfill(10)
        if cik in want and r["form"] in FORMS:
            subs[r["adsh"]] = (cik, r["form"], r["filed"])
    n = 0
    hits = []
    for r in rows(pdir / "num.tsv.zst"):
        s = subs.get(r["adsh"])
        if (
            s is None
            or r["tag"] not in TAGS
            or r["qtrs"] != "1"
            or r.get("dimn", "0") not in ("0", "1")
            or r.get("iprx", "0") != "0"
            or r.get("coreg")
            or r["ddate"] not in want[s[0]]
            or not r["value"]
        ):
            continue
        hits.append((s, r))
    need = {r["dimh"] for _s, r in hits if r.get("dimn") == "1"}
    seg = {}
    if need:
        for d in rows(pdir / "dim.tsv.zst"):
            if d["dimhash"] in need:
                seg[d["dimhash"]] = d["segments"]
    for s, r in hits:
        segment = "" if r.get("dimn") == "0" else seg.get(r["dimh"], "?")
        copies[(s[0], r["tag"], r["ddate"])].append(
            (r["value"], r["adsh"], s[1], s[2], segment)
        )
        n += 1
    shutil.rmtree(pdir)
    done.append(period)
    json.dump(
        {k[0] + "|" + k[1] + "|" + k[2]: v for k, v in copies.items()},
        open(W / "copies.json", "w"),
    )
    progress.write_text(json.dumps({"done": done}))
    print(period, "rows kept", n, flush=True)


def allowed(segment: str) -> bool:
    return segment == "" or (
        bool(QUARTERLY_AXIS.match(segment)) and not REJECT_AXIS.search(segment)
    )


census = Counter()
for v in copies.values():
    for x in v:
        census[x[4] or "(no dimension)"] += 1
json.dump(census.most_common(), open(W / "axis_census.json", "w"), indent=0)
out, stats = [], Counter()
for c in cells:
    dd = month_end(date.fromisoformat(c["end"])).strftime("%Y%m%d")
    cik = c["cik"].zfill(10)
    # the concept's own tag first (basic / diluted), the combined tag only when the own tag has no copy
    found = []
    for tag in c["tags"]:
        found = [x for x in copies.get((cik, tag, dd), []) if allowed(x[4])]
        if found:
            break
    if not found:
        res = {"outcome": "not_in_fsn"}
    else:
        vals = sorted({Decimal(x[0]) for x in found})
        if vals[-1] - vals[0] > Decimal("0.005"):
            res = {"outcome": "fsn_copies_disagree", "values": [str(v) for v in vals]}
        else:
            v, adsh, form, filed, segment = min(found, key=lambda x: (x[3], x[1]))
            res = {
                "outcome": "replace_with_fsn_value",
                "value": str(Decimal(v)),
                "accession": adsh,
                "form": form,
                "filed": filed,
                "tag": tag,
                "copies": len(found),
                "axis": segment,
            }
    stats[res["outcome"]] += 1
    if res["outcome"] == "not_in_fsn" and any(
        copies.get((cik, t, dd)) for t in c["tags"]
    ):
        stats["not_in_fsn_only_rejected_axes"] += 1
        res["rejected_axes"] = sorted(
            {x[4] for t in c["tags"] for x in copies.get((cik, t, dd), [])}
        )
    out.append({**c, **res})
json.dump(out, open(W / "nc_fsn_outcomes.json", "w"), indent=0)
print(json.dumps(stats))
