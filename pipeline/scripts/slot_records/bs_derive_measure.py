"""Measure fsn_store.bs_derive on real company directories: the pilot sequence (load, seed rules, map, checks,
pilot.report_company) on a LOCAL scratch database, run without and with bs_derive. Writes, per company and data
point, the gap keys freed (derived value) or reasoned (not_presented), and every derived / reasoned row.
Refuses any database that is not a local scratch database. Zero SEC requests.
usage: SCRATCH_DATABASE_URL=... bs_derive_measure.py <reports.json> <calendar.csv.gz> <out_dir> <company_dir>...
  reports.json: the cohort run's per-company reports (sic code per CIK for the sector template)
"""
import json
import os
import sys
from collections import Counter
from pathlib import Path

import psycopg

from scrooner_pipeline.fsn_store import bs_derive, checks, load, mapping, pilot, rules

REPO = Path(__file__).resolve().parents[3]
POINTS = (bs_derive.TL, bs_derive.CA, bs_derive.CL)
STATEMENT = {"BS": "balance_sheet", "IS": "income_statement", "CF": "cash_flow"}

reports_path, calendar, out_dir, dirs = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3]), sys.argv[4:]
out_dir.mkdir(parents=True, exist_ok=True)
conn = psycopg.connect(os.environ["SCRATCH_DATABASE_URL"])
db = conn.execute("select current_database(), inet_server_addr()").fetchone()
if not (db[0].startswith(("scrooner_test", "scratch")) and db[1] in (None, "127.0.0.1", "::1")):
    sys.exit(f"refused: {db} is not a local scratch database")
reports = json.load(open(reports_path))
profile = {r["cik"].zfill(10): (r.get("profile") or {}) for r in reports}
# the expected-period calendar is keyed by PRODUCTION company_id (pilot.calendar_keys): insert with that id
prod_id = {r["cik"].zfill(10): r["company_id"] for r in reports}

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
        conn.execute("insert into analytics.canonical_concept (name, statement, combination_mode) values (%s, %s, 'first_match')", (name, stmt))
conn.commit()
for p in seeds:
    res = rules.seed(conn, p, apply=True)
    assert not res["errors"], (p, res["errors"])
conn.commit()
rule_set = mapping.load_rules(conn)
rule_concepts = {r[0] for r in conn.execute(
    "select distinct cc.name from fsn.concept_rule r join analytics.canonical_concept cc on cc.id = r.canonical_concept_id")}

real_rows = bs_derive.rows
# resumable: one JSON line per finished company (a container restart loses nothing finished)
progress_path = out_dir / "progress.jsonl"
done = {json.loads(x)["cik"] for x in open(progress_path)} if progress_path.exists() else set()
summary, per_company, examples, misses_total = Counter(), {}, [], Counter()
for d in dirs:
    cik = json.loads((Path(d) / "manifest.json").read_text())["cik"].zfill(10)
    if cik in done:
        continue
    prof = profile.get(cik, {})
    row = conn.execute("select id from core.company where cik = %s", (cik,)).fetchone()
    cid = row[0] if row else conn.execute(
        "insert into core.company (id, cik, company_name, sic_code) overriding system value values (%s, %s, %s, %s) returning id",
        (prod_id[cik], cik, f"MEASURE {cik}", prof.get("sic"))).fetchone()[0]
    conn.commit()
    # predecessor registrants' filings in the directory belong to this company (FSN_PREDECESSORS="pred=succ,...")
    preds = dict(p.split("=", 1) for p in (os.environ.get("FSN_PREDECESSORS") or "").split(",") if "=" in p)
    load.load_company(
        conn, Path(d), loader_commit="bs_derive_measure", predecessors={k.zfill(10): v.zfill(10) for k, v in preds.items()}
    )
    conn.commit()
    mapping.map_company(conn, cid, rule_set)
    checks.check_company(conn, cid)
    conn.commit()
    gaps = {}
    company_misses = Counter()
    for mode in ("before", "after"):
        captured = []

        def hook(c, company_id, have, _mode=mode, _cap=captured):
            if _mode == "before":
                return [], {}
            out, miss = real_rows(c, company_id, have)
            _cap.append((out, miss))
            return out, miss
        bs_derive.rows = hook
        rep = pilot.report_company(conn, cid, calendar, rule_concepts)
        gaps[mode] = {(g["data_point"], g["grain"], g["period_end"]): g["cause"] for g in rep["_gaps"] if g["data_point"] in POINTS}
        if os.environ.get("MEASURE_DEBUG"):
            print(mode, Counter((c["data_point_name"], c["state"]) for c in rep["_cells"] if c["data_point_name"] in POINTS), Counter(k[0] for k in gaps[mode]))
        if mode == "after" and captured:
            out, miss = captured[0]
            misses_total.update(miss)
            company_misses = Counter(miss)
            for r in out:
                if True:
                    examples.append({"cik": cik, "sector": prof.get("sector_template"), **{k: r.get(k) for k in (
                        "data_point_name", "period_grain", "fsn_end", "state", "value", "accession", "rule_id", "reason_code", "derivation")}})
    bs_derive.rows = real_rows
    freed = Counter()
    for k, cause in gaps["before"].items():
        if k not in gaps["after"]:
            freed[(k[0], cause)] += 1
    per_company[cik] = {"sector": prof.get("sector_template"), "before": Counter(k[0] for k in gaps["before"]),
                        "after": Counter(k[0] for k in gaps["after"]), "freed": {f"{a}|{b}": n for (a, b), n in freed.items()}}
    company_rows = [e for e in examples if e["cik"] == cik]
    with open(progress_path, "a") as fo:
        fo.write(json.dumps({"cik": cik, **per_company[cik], "freed_keys": [[a, b, n] for (a, b), n in freed.items()],
                             "misses": dict(company_misses), "rows": company_rows}, default=str) + "\n")
    for (dp, cause), n in freed.items():
        summary[(dp, cause, prof.get("sector_template"))] += n
    conn.execute("delete from fsn.filing where company_id = %s", (cid,))
    conn.commit()
    print(cik, prof.get("sector_template"), dict(freed), flush=True)

json.dump({"freed_by_point_cause_sector": {"|".join(map(str, k)): v for k, v in sorted(summary.items(), key=str)},
           "not_derived_latest_copy_columns": dict(misses_total), "per_company": per_company},
          open(out_dir / "measure.json", "w"), indent=1, default=str)
with open(out_dir / "rows.jsonl", "w") as fo:
    for e in examples:
        fo.write(json.dumps(e, default=str) + "\n")
print(json.dumps({"|".join(map(str, k)): v for k, v in sorted(summary.items(), key=str)}, indent=1))
print("not derived (latest-copy columns):", dict(misses_total))
