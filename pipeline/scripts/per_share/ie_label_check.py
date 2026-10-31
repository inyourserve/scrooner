"""Label check for the interest_expense era-rule fill cells: the filer's own label for the tag on its income
statement (FSN pre, bucket fsn-notes; no SEC request). A 'net' perimeter label (Interest expense, net; interest
income/expense) or no income-statement row holds the cell; 'net of capitalized interest' is still gross expense.
usage: ie_label_check.py <scratch> <plan_cells.csv> <out.csv>"""

import csv
import io
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

csv.field_size_limit(1 << 24)
S, IN, OUT = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
NET = re.compile(r"\bnet\b|income", re.I)
GROSS_OK = re.compile(
    r"net of (the )?(amounts?|portion|interest) ?(capitali[sz]ed|capitali)|net of (amounts? )?capitali[sz]ed",
    re.I,
)
base, key = (
    os.environ["SUPABASE_URL"].rstrip("/"),
    os.environ["SUPABASE_SERVICE_ROLE_KEY"],
)


def rows(path: Path):
    p = subprocess.Popen(["zstd", "-dc", str(path)], stdout=subprocess.PIPE)
    yield from csv.DictReader(
        io.TextIOWrapper(p.stdout, encoding="utf-8", errors="replace", newline=""),
        delimiter="\t",
        quoting=csv.QUOTE_NONE,
    )
    p.wait()


cells = list(csv.DictReader(open(IN)))
fills = [c for c in cells if c["outcome"] == "fill"]
need = defaultdict(set)  # period -> accessions
acc_filed = {}
conn_rows = None
sys.path.insert(0, str(Path(__file__).parent))
from _ro import conn  # noqa: E402

c = conn()
accs = sorted({x["accession"] for x in fills})
for acc, filed in c.execute(
    "select accession_number, filing_date from core.filing where accession_number = any(%s)",
    (accs,),
):
    acc_filed[acc] = filed
for acc, filed in acc_filed.items():
    period = (
        f"{filed.year}q{(filed.month - 1) // 3 + 1}"
        if filed < date(2025, 10, 1)
        else f"{filed.year}m{filed.month:02d}"
    )
    need[period].add(acc.replace("-", ""))
labels = defaultdict(list)  # (adsh, tag) -> [(stmt, plabel)]
tags = {x["tag"] for x in fills}
for period in sorted(need):
    d = S / "ielab" / period
    d.mkdir(parents=True, exist_ok=True)
    f = d / "pre.tsv.zst"
    try:
        req = urllib.request.Request(
            f"{base}/storage/v1/object/fsn-notes/{period}/{period}_pre.tsv.zst",
            headers={"Authorization": f"Bearer {key}", "apikey": key},
        )
        with urllib.request.urlopen(req, timeout=600) as r, f.open("wb") as o:
            shutil.copyfileobj(r, o)
    except urllib.error.HTTPError as e:
        print(period, "HTTP", e.code, flush=True)
        continue
    for r in rows(f):
        a = r["adsh"].replace("-", "")
        if a in need[period] and r["tag"] in tags and r.get("inpth", "0") == "0":
            labels[(a, r["tag"])].append((r["stmt"], r["plabel"]))
    shutil.rmtree(d)
    print(period, len(need[period]), flush=True)
stats = Counter()
for x in fills:
    got = labels.get((x["accession"].replace("-", ""), x["tag"]), [])
    face = [lab for stmt, lab in got if stmt in ("IS", "CI")]
    if not got:
        x["label_check"], x["label"] = "no_pre_rows", ""
    elif not face:
        x["label_check"], x["label"] = "not_on_income_statement", got[0][1]
    elif any(NET.search(lab) and not GROSS_OK.search(lab) for lab in face):
        x["label_check"], x["label"] = "net_label", face[0]
    else:
        x["label_check"], x["label"] = "gross_label", face[0]
    stats[x["label_check"]] += 1
for x in cells:
    x.setdefault("label_check", "")
    x.setdefault("label", "")
    if x["outcome"] == "fill" and x["label_check"] == "net_label":
        x["outcome"] = "hold_net_label"
    elif x["outcome"] == "fill" and x["label_check"] in (
        "not_on_income_statement",
        "no_pre_rows",
    ):
        x["outcome"] = (
            "hold_label_unread"
            if x["label_check"] == "no_pre_rows"
            else "hold_not_on_face"
        )
with open(OUT, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(cells[0]))
    w.writeheader()
    w.writerows(cells)
print(
    json.dumps(
        {
            "label_check": dict(stats),
            "outcomes": dict(Counter(x["outcome"] for x in cells)),
            "fill_companies": len(
                {x["company_id"] for x in cells if x["outcome"] == "fill"}
            ),
        },
        indent=1,
    )
)
