"""Cut fsn_sec_fixture.py output to what the cash-flow and per-share readers read, and rebuild the bucket
layout from the SAME cut rows (stdlib + zstd CLI). Rows are copied, never edited.
Kept: sub; pre rows with stmt CF; cal (all arcs of the filing: the CF group is chosen among them);
num rows whose tag is on that filing's cash-flow face or is a per-share / share-count tag the per-share reader
or share_basis's split signal reads; dim rows those num rows reference. tag/ren are not read, not kept.
usage: fsn_company_fixture_cf.py <fsn_sec_fixture out> <fixture companies dir> <periods out dir>
"""
import csv
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from fsn_company import table  # noqa: E402

PER_SHARE = {"EarningsPerShareBasic", "EarningsPerShareDiluted", "EarningsPerShareBasicAndDiluted",
             "CommonStockDividendsPerShareDeclared", "CommonStockDividendsPerShareCashPaid",
             "CommonStockSharesOutstanding", "EntityCommonStockSharesOutstanding",
             "WeightedAverageNumberOfSharesOutstandingBasic", "WeightedAverageNumberOfDilutedSharesOutstanding"}


def write(path, cols, recs):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, cols, delimiter="\t", quoting=csv.QUOTE_NONE, escapechar="\\", lineterminator="\n")
        w.writeheader()
        w.writerows(recs)


src, out, periods = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
by_period = defaultdict(lambda: defaultdict(list))
cols = {}
for d in sorted((src / "companies").iterdir()):
    t = {name: list(table(d, name)) for name in ("sub", "pre", "num", "cal", "dim")}
    cols |= {name: list(rows[0]) for name, rows in t.items() if rows}
    face = defaultdict(set)
    pre = [r for r in t["pre"] if r["stmt"] == "CF"]
    for r in pre:
        face[r["adsh"]].add(r["tag"])
    num = [r for r in t["num"] if r["tag"] in face[r["adsh"]] or r["tag"] in PER_SHARE]
    dims = {r["dimh"] for r in num}
    dim = [r for r in t["dim"] if r["dimhash"] in dims]
    cut = {"sub": t["sub"], "pre": pre, "num": num, "cal": t["cal"], "dim": dim}
    for name, rows in cut.items():
        if rows:
            write(out / d.name / f"{name}.tsv", cols[name], rows)
    (out / d.name / "manifest.json").write_text((d / "manifest.json").read_text())
    set_of = {r["adsh"]: r["fsn_set"] for r in t["sub"]}
    for name in ("sub", "pre", "num", "cal"):
        for r in cut[name]:
            rr = {k: v for k, v in r.items() if k != "fsn_set"}
            by_period[set_of[r["adsh"]]][name].append(rr)
    print(d.name, {k: len(v) for k, v in cut.items()})
for p, tabs in sorted(by_period.items()):
    for name in ("sub", "pre", "num", "cal"):
        c = [x for x in cols[name] if x != "fsn_set"]
        f = periods / p / f"{p}_{name}.tsv"
        write(f, c, tabs[name])
        subprocess.run(["zstd", "-q", "-f", "--rm", str(f)], check=True)
