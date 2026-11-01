"""Store-path regression gate for the capex / D&A detectors (CAPEX-DA-DEBT-PORT-2026-11-01.md).

On a SCRATCH Postgres built from every migration (refuses any other database): load FSN-store company directories
with fsn_store.load, seed the committed concept_rules, then map + select each company twice, seeds only and
seeds + fsn_store.detectors.DEFAULT, and compare every capex / D&A key with the lane's Verifier-passed family file
(capex_da_cash_debt 6f53c945). Writes <out>/store_gate.json; exits 1 when the detectors publish a key the lane
holds, or publish a value different from the lane's, or leave a conflicting-values defect.
usage: SCRATCH_DATABASE_URL=postgresql://... capex_da_store_gate.py <ref_cells.jsonl.gz> <out_dir> <company_dir>...
"""
import gzip
import json
import os
import sys
from collections import Counter, defaultdict
from decimal import Decimal
from pathlib import Path

import psycopg

from scrooner_pipeline.fsn_store import detectors, load, mapping, rules, select

REPO = Path(__file__).resolve().parents[3]
CONCEPTS = ("capex_resolved", "depreciation_and_amortization_resolved")
STATEMENT = {"BS": "balance_sheet", "IS": "income_statement", "CF": "cash_flow"}

ref_path, out_dir, dirs = sys.argv[1], Path(sys.argv[2]), sys.argv[3:]
out_dir.mkdir(parents=True, exist_ok=True)
conn = psycopg.connect(os.environ["SCRATCH_DATABASE_URL"])
db = conn.execute("select current_database(), inet_server_addr()").fetchone()
if not (db[0].startswith(("scrooner_test", "scratch")) and db[1] in (None, "127.0.0.1", "::1")):
    sys.exit(f"refused: {db} is not a local scratch database")

# canonical concepts the seeds name (production seeds them from the mapper; a migration-only database lacks some)
seeds = sorted(p for p in (REPO / "data-team" / "47-fsn-store" / "concept_rules").glob("*.jsonl") if not p.name.startswith("_"))
need = {}
for p in seeds:
    for line in p.read_text().splitlines():
        if line.strip():
            r = json.loads(line)
            for c in [r["canonical_concept"], *(r.get("components") or []), (r.get("position") or {}).get("anchor_concept")]:
                if c:
                    need.setdefault(c, STATEMENT[r["stmt"]])
have = {r[0] for r in conn.execute("select name from analytics.canonical_concept")}
for name, stmt in sorted(need.items()):
    if name not in have:
        conn.execute("insert into analytics.canonical_concept (name, statement, combination_mode) values (%s, %s, 'first_match')",
                     (name, stmt))
conn.commit()

cids = {}
for d in dirs:
    cik = json.loads((Path(d) / "manifest.json").read_text())["cik"].zfill(10)
    row = conn.execute("select id from core.company where cik = %s", (cik,)).fetchone()
    cid = row[0] if row else conn.execute("insert into core.company (cik, company_name) values (%s, %s) returning id", (cik, f"GATE {cik}")).fetchone()[0]
    conn.commit()
    load.load_company(conn, Path(d), loader_commit="capex_da_store_gate")
    conn.commit()
    cids[cik] = cid
for p in seeds:
    res = rules.seed(conn, p, apply=True)
    assert not res["errors"], (p, res["errors"])
conn.commit()
rule_set = mapping.load_rules(conn)

def month_end(d):
    """FSN num ddate rounding (cf_da_capex_variants.month_end): the nearest month end"""
    from datetime import date, timedelta
    y, m, dd = int(d[:4]), int(d[5:7]), int(d[8:10])
    if dd < 15:
        return (date(y, m, 1) - timedelta(days=1)).isoformat()
    return (date(y + (m == 12), m % 12 + 1, 1) - timedelta(days=1)).isoformat()


ref, ref_derived = {}, {}
for line in gzip.open(ref_path, "rt"):
    r = json.loads(line)
    cik = str(r["cik"]).zfill(10)
    if cik in cids and r["data_point_name"] in CONCEPTS and r.get("derivation"):
        ref_derived[(cik, r["data_point_name"], str(r["period_grain"]), month_end(r["period_end"]))] = r
    if cik in cids and r["data_point_name"] in CONCEPTS and r["period_grain"] in ("FY", "Q") and not r.get("derivation"):
        # the store keys a cell by the FSN month-end-rounded date (fsn_end); the lane file by the exact date
        ref[(cik, r["data_point_name"], str(r["period_grain"]), month_end(r["period_end"]))] = r


def run(dets):
    rows = {}
    for cik, cid in cids.items():
        mapping.map_company(conn, cid, rule_set, detectors=dets)
        conn.commit()
        for r in select.select_company(conn, cid):
            if r["data_point_name"] in CONCEPTS and r["period_grain"] in ("FY", "Q") and not r.get("derivation"):
                rows[(cik, r["data_point_name"], str(r["period_grain"]), str(r["fsn_end"]))] = r
    return rows


def num(x):
    return None if x in (None, "") else Decimal(str(x))


report = {}
for mode, dets in (("seeds_only", None), ("detectors", detectors.DEFAULT)):
    got = run(dets)
    cls = Counter()
    per = defaultdict(Counter)
    bad = []
    for k in sorted(set(ref) | set(got), key=lambda x: tuple(map(str, x))):
        a, b = ref.get(k), got.get(k)
        av = num(a["value"]) if a and a["state"] == "value" else None
        bv = num(b["value"]) if b and b["state"] == "value" else None
        if b and b["state"] == "defect" and b.get("reason_code") == "conflicting_values_in_filing":
            c = "store_conflicting_values_in_filing"
        elif av is not None and bv is not None:
            c = "same_value" if av == bv else "value_differs"
        elif av is not None:
            c = "lane_value_store_blank"
        elif bv is not None and a and b.get("accession") != a.get("accession"):
            # the store's latest accepted filing (design section 4) is a later vintage than the one the lane held;
            # the line comes from the lane's own single-member decision on that later filing
            c = "later_vintage_publishes_where_lane_held_the_original"
        elif bv is not None:
            if a:
                c = "store_value_lane_held"
            elif k[3] < "2014-01-01":
                c = "store_key_before_lane_window"
            elif k in ref_derived:
                d = ref_derived[k]
                c = ("store_print_equals_lane_derived_quarter" if d["state"] in ("value", "derived") and num(d["value"]) == bv
                     else "store_print_where_lane_derives_differently")
            else:
                c = "store_value_key_not_in_lane"
        else:
            c = "both_blank"
        cls[c] += 1
        per[(k[0], k[1].split("_")[0])][c] += 1
        if c not in ("same_value", "both_blank") and len(bad) < 1000:
            ld = ref_derived.get(k)
            bad.append({"key": k, "class": c, "lane": a and {f: a.get(f) for f in ("state", "value", "reason_code", "accession", "tag")},
                        "lane_derived": ld and {f: ld.get(f) for f in ("state", "value", "reason_code", "derivation")},
                        "store": b and {f: b.get(f) for f in ("state", "value", "reason_code", "accession", "rule_id", "tag")}})
    report[mode] = {"classes": dict(cls), "per_company": {f"{c}:{fam}": dict(v) for (c, fam), v in sorted(per.items())}, "examples": bad}
    print(f"== {mode}: {dict(sorted(cls.items()))}")
json.dump(report, open(out_dir / "store_gate.json", "w"), indent=1, default=str)
d = report["detectors"]["classes"]
fail = d.get("store_value_lane_held", 0) + d.get("value_differs", 0) + d.get("store_conflicting_values_in_filing", 0)
print("verdict:", "FAIL" if fail else "PASS", f"({fail} keys published against the lane or conflicting)")
sys.exit(1 if fail else 0)
