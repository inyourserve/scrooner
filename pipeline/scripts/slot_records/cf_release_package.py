"""Cash-flow release package 1 (rule slot.cf_cfo@1 or slot.cf_buybacks@1): the
Verifier-cleared differences and fills of a replay run, packaged for a
flag-gated write.
READ-ONLY here: one connection, 60s timeout. Nothing is applied; the apply and
rollback SQL are WRITTEN as files for the Release Manager (founder's words
needed for the production write).

Every packaged cell is pinned to production rows by id:
  core.fact      the filer's own fact for the cell (same accession, same tag,
                 same value, end within 10 days): exact period_id, start, end,
                 and the source_fact_ids of the new canonical value. A cell
                 whose fact is not in core.fact (custom CFO tag) stays out.
  production     the current cfo_resolved row on that exact period (update),
                 or none (insert). A production row on a NEIGHBOURING period
                 (within 10 days, another period_id) makes the cell ambiguous:
                 it stays out.
Stale cells are refused at apply time, cell by cell: an update runs only where
the row still has the id and value the package saw; an insert only where no
row exists. Skipped cells are returned by the apply script, never forced.
A fill is only a fill when production has no row for the SAME period: any
production row of the same length (+-20 days) ending within 31 days counts as
production having a value (Verifier buybacks run 3: DPZ's 24-week period ends
14 days from its label date and production already holds 97.634M).
usage: DATABASE_URL=... cf_release_package.py <cfo|buybacks> <cohort.csv> <run_dir> <out_dir> [keep_list.json]
"""
import csv
import gzip
import hashlib
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

import psycopg

FAM = sys.argv[1]
RULE_ID, CONCEPT = {"cfo": ("slot.cf_cfo@1", "cfo_resolved"),
                    "buybacks": ("slot.cf_buybacks@1", "share_buybacks_resolved")}[FAM]
cohort_csv, run_dir, out_dir = sys.argv[2], Path(sys.argv[3]), Path(sys.argv[4])
keep = {tuple(k) for k in json.load(open(sys.argv[5]))} if len(sys.argv) > 5 else set()
out_dir.mkdir(parents=True, exist_ok=True)
coh = {r["cik"]: (int(r["company_id"]), r["ticker"]) for r in csv.DictReader(open(cohort_csv))}
diff = {(t, e, m) for t, e, m, *_ in json.load(open(run_dir / f"{FAM}_prod_differs.json"))}
blank = {(t, e, m) for t, e, m, *_ in json.load(open(run_dir / f"{FAM}_prod_blank.json"))}


def source_tag(r):
    """the one face line the value comes from (CFO: the printed total; buybacks:
    the single valued common-repurchase line, multiple lines are held upstream)"""
    if FAM == "cfo":
        return r["detail"]["tag"]
    ms = [m for m in r["detail"]["members"] if m["class"] == "common" and m["value"] not in (None, "0", "0.0000")]
    return ms[0]["tag"] if len(ms) == 1 and not ms[0]["custom"] else None


cands = []
for line in gzip.open(run_dir / f"{FAM}_cells.jsonl.gz", "rt"):
    r = json.loads(line)
    if r["verdict"] != "publishable":
        continue
    cid, ticker = coh[r["cik"]]
    k = (ticker, r["end"], r["months"])
    if k in diff or k in blank:
        r.update(company_id=cid, ticker=ticker, population="differs" if k in diff else "fills_blank", src_tag=source_tag(r))
        cands.append(r)

conn = psycopg.connect(os.environ["DATABASE_URL"], application_name="cf_release_package")
conn.execute("set statement_timeout = '60s'")
conn.execute("set default_transaction_read_only = on")
concept_id = conn.execute("select id from analytics.canonical_concept where name = %s", (CONCEPT,)).fetchone()[0]
by_co = defaultdict(list)
for r in cands:
    by_co[r["company_id"]].append(r)
cells, dropped = [], Counter()
for cid, rs in sorted(by_co.items()):
    tags = sorted({r["src_tag"] for r in rs if r["src_tag"]})
    accs = sorted({r["accession"] for r in rs})
    facts = conn.execute(
        """select f.id, co.tag, fi.accession_number, p.id, p.start_date, p.end_date, f.value
           from core.fact f join core.concept co on co.id = f.concept_id
           join core.filing fi on fi.id = f.filing_id join core.period p on p.id = f.period_id
           where f.company_id = %s and co.taxonomy = 'us-gaap' and co.tag = any(%s)
             and fi.accession_number = any(%s) and p.period_type = 'duration' and f.is_derived = false""",
        (cid, tags, accs),
    ).fetchall()
    prod = conn.execute(
        """select cf.id, cf.period_id, p.start_date, p.end_date, cf.value from analytics.canonical_fact cf
           join core.period p on p.id = cf.period_id
           where cf.company_id = %s and cf.canonical_concept_id = %s and p.start_date is not null""",
        (cid, concept_id),
    ).fetchall()
    for r in rs:
        end, v = date.fromisoformat(r["end"]), Decimal(r["value"])
        days = round(r["months"] / 3 * 91.25 - (r.get("durp") or 0) * 91.25)  # FSN durp = (nominal - actual) / 91.25 (Valaris 5 months: +0.33)
        if not r["src_tag"]:
            dropped["no_single_standard_source_line"] += 1
            continue
        hit = [f for f in facts if f[1] == r["src_tag"] and f[2] == r["accession"] and f[6] == v
               and abs((f[5] - end).days) <= 10 and abs((f[5] - f[4]).days - days) <= 20]
        if len({f[3] for f in hit}) != 1:
            dropped["no_unique_core_fact"] += 1
            continue
        fid, _t, _a, pid, s, e, _v = hit[0]
        if (r["cik"], e.isoformat()) in keep or (r["ticker"], e.isoformat(), r["months"]) in keep:
            dropped["keep_list"] += 1
            continue
        same = [p for p in prod if p[1] == pid]
        near = [p for p in prod if p[1] != pid and abs((p[3] - e).days) <= 31 and abs((p[3] - p[2]).days - (e - s).days) <= 20]
        if near:
            dropped["production_on_neighbour_period"] += 1
            continue
        if same and same[0][4] == v:
            dropped["production_already_equal"] += 1
            continue
        cells.append({
            "rule_id": RULE_ID, "company_id": cid, "cik": r["cik"], "ticker": r["ticker"],
            "canonical_concept_id": concept_id, "period_id": pid, "start": s.isoformat(), "end": e.isoformat(),
            "accession": r["accession"], "source_fact_id": fid, "tag": r["src_tag"], "basis": r["detail"].get("basis", "common_repurchase_line"),
            "slot_value": str(v), "op": "update" if same else "insert",
            "canonical_fact_id": same[0][0] if same else None,
            "expected_before": str(same[0][4]) if same else None,
            "population": r["population"],
        })
conn.close()

cells.sort(key=lambda c: (c["company_id"], c["period_id"]))
body = "".join(json.dumps(c, sort_keys=True) + "\n" for c in cells)
(out_dir / f"{FAM}_release1_cells.jsonl").write_text(body)
digest = hashlib.sha256(body.encode()).hexdigest()
(out_dir / f"{FAM}_release1_cells.sha256").write_text(digest + f"  {FAM}_release1_cells.jsonl\n")
with open(out_dir / f"{FAM}_release1_before_image.jsonl", "w") as f:
    for c in cells:
        if c["op"] == "update":
            f.write(json.dumps({"canonical_fact_id": c["canonical_fact_id"], "company_id": c["company_id"],
                                "canonical_concept_id": concept_id, "period_id": c["period_id"],
                                "value_before": c["expected_before"]}, sort_keys=True) + "\n")
(out_dir / f"{FAM}_release1_touched_ciks.txt").write_text("".join(f"{k}\n" for k in sorted({c["cik"] for c in cells})))


def values_sql():
    return ",\n".join(
        f"({c['company_id']}, {c['canonical_concept_id']}, {c['period_id']}, {c['slot_value']}, {c['source_fact_id']}, "
        f"'{c['op']}', {c['canonical_fact_id'] or 'null'}, {c['expected_before'] or 'null'})"
        for c in cells
    )


head = (f"-- {RULE_ID} release 1: {len(cells)} cells, cells sha256 {digest}\n"
        "-- Generated, NOT executed. Release Manager only, behind SCROONER_RULES_ENABLED="
        f"{RULE_ID}, after the founder's typed approval.\n")
pkg = ("create temp table pkg (company_id bigint, concept_id bigint, period_id bigint, slot_value numeric,\n"
       "  source_fact_id bigint, op text, canonical_fact_id bigint, expected_before numeric) on commit drop;\n"
       f"insert into pkg values\n{values_sql()};\n")
(out_dir / f"{FAM}_release1_apply.sql").write_text(head + "begin;\n" + pkg + """-- stale cells are refused one by one: they are listed and left untouched
create temp table refused on commit drop as
select p.*, cf.id as current_id, cf.value as current_value from pkg p
left join analytics.canonical_fact cf
  on cf.company_id = p.company_id and cf.canonical_concept_id = p.concept_id and cf.period_id = p.period_id
where (p.op = 'update' and (cf.id is distinct from p.canonical_fact_id or cf.value is distinct from p.expected_before))
   or (p.op = 'insert' and cf.id is not null);
update analytics.canonical_fact cf set value = p.slot_value, source_fact_ids = array[p.source_fact_id], resolved_at = now()
from pkg p
where p.op = 'update' and cf.id = p.canonical_fact_id and cf.value = p.expected_before;
insert into analytics.canonical_fact (company_id, canonical_concept_id, period_id, value, source_fact_ids)
select p.company_id, p.concept_id, p.period_id, p.slot_value, array[p.source_fact_id] from pkg p
where p.op = 'insert' and not exists (select 1 from analytics.canonical_fact cf
  where cf.company_id = p.company_id and cf.canonical_concept_id = p.concept_id and cf.period_id = p.period_id);
select count(*) as refused_stale_cells from refused;
select * from refused;
commit;
""")
(out_dir / f"{FAM}_release1_rollback.sql").write_text(head.replace("release 1:", "release 1 ROLLBACK:") + "begin;\n" + pkg + """-- only cells still holding the package value are reverted (a later write wins)
update analytics.canonical_fact cf set value = p.expected_before
from pkg p
where p.op = 'update' and cf.id = p.canonical_fact_id and cf.value = p.slot_value;
delete from analytics.canonical_fact cf using pkg p
where p.op = 'insert' and cf.company_id = p.company_id and cf.canonical_concept_id = p.concept_id
  and cf.period_id = p.period_id and cf.value = p.slot_value and cf.source_fact_ids = array[p.source_fact_id];
commit;
""")
plan = {
    "rule_id": RULE_ID, "cells": len(cells), "companies": len({c["company_id"] for c in cells}),
    "by_op": dict(Counter(c["op"] for c in cells)), "by_population": dict(Counter(c["population"] for c in cells)),
    "by_basis": dict(Counter(c["basis"] for c in cells)), "candidates": len(cands), "left_out": dict(dropped),
    "keep_list_cells": len(keep), "cells_sha256": digest,
}
json.dump(plan, open(out_dir / f"{FAM}_release1_plan.json", "w"), indent=1)
print(json.dumps(plan, indent=1))
