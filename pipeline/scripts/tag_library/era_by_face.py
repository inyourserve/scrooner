"""Split contested concept eras by the PRINTED FACE LINE of each period's own filing (read-only on the FSN store).

Dhairya's guard 2026-11-12: in each period the chosen tag must be the tag on the face line of that period's own filing
(latest accepted filing for the period), not merely a tag that has a companyfacts fact. If both competing tags are on that
face, the library priority decides; if neither is, the period stays OPEN (no concept row covers it), never filled.
Runs of consecutive periods with one tag become non-overlapping concept rows with exact bounds; the rest are excluded
reason rows. Usage: era_by_face.py <tag_map.csv> <out.csv> [<open_periods.csv>]
"""
import collections
import csv
import os
import sys

import psycopg

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

src, out = sys.argv[1], sys.argv[2]
open_out = sys.argv[3] if len(sys.argv) > 3 else None
rows = list(csv.DictReader(open(src)))
cols = list(rows[0])
groups = collections.defaultdict(list)
for i, r in enumerate(rows):
    if r["decision"] == "concept" and r["canonical_concept"]:
        groups[(r["company_id"], r["stmt"], r["canonical_concept"])].append(i)
alt = collections.defaultdict(list)
for i, r in enumerate(rows):
    if r["decision"] == "excluded" and r["reason_class"] == "alternate_tag_overlapping":
        for (c, st, con) in groups:
            if c == r["company_id"] and st == r["stmt"] and f"concept {con} " in r["reason"]:
                alt[(c, st, con)].append(i)
contested = {k: v for k, v in groups.items() if k in alt}

from era_face import face_runs  # noqa: E402

new_rows, drop, opens = [], set(), []
with psycopg.connect(os.environ["DATABASE_URL"], connect_timeout=20) as conn:
    conn.execute("set statement_timeout = '60s'")
    for (c, st, con), kept in contested.items():
        kept_rows = sorted([rows[i] for i in kept], key=lambda r: r["era_from"])
        alt_rows = sorted([rows[i] for i in alt[(c, st, con)]], key=lambda r: -int(r["filings"] or 0))
        order = []
        for r in kept_rows + alt_rows:  # priority: the library's kept tags first, then alternates
            if r["tag"] not in order:
                order.append(r["tag"])
        q = """select f.id, f.period, f.accepted, t.tag from fsn.line l join fsn.filing f on f.id = l.filing_id join fsn.tag t on t.id = l.tag_id
               where f.company_id = %s and l.stmt = %s and f.period >= '2015-01-01'"""
        filings, face = {}, collections.defaultdict(set)
        for fid, period, accepted, tag in conn.execute(q, (int(c), st)).fetchall():
            filings[fid] = (str(period), accepted)
            if tag in order:
                face[fid].add(tag)
        runs, open_p = face_runs(filings, face, order)
        if not runs:
            continue
        for p in open_p:
            opens.append({"company_id": c, "stmt": st, "concept": con, "period": p, "why": "the period's own latest filing prints none of the competing tags: open, not filled"})
        drop.update(kept + alt[(c, st, con)])
        tmpl = {r["tag"]: r for r in kept_rows + alt_rows}
        used = set()
        for t, a, b in runs:
            e = dict(tmpl[t])
            e.update(decision="concept", canonical_concept=con, era_from=a, era_to=b, reason_class="",
                     reason=(tmpl[t].get("reason") or "").split(" [")[0] + " [era by face line: the tag printed on each period's own filing]",
                     decided_by=(tmpl[t]["decided_by"] or "").split("+")[0] + "+era_by_face")
            new_rows.append(e)
            used.add(t)
        for t in order:
            if t not in used:
                e = dict(tmpl[t])
                e.update(decision="excluded", canonical_concept="", reason_class="alternate_tag_overlapping",
                         reason=f"same concept {con}: wherever {t} is printed, a higher-priority tag is printed on the same face", decided_by="era_by_face")
                new_rows.append(e)

with open(out, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=cols)
    w.writeheader()
    w.writerows([r for i, r in enumerate(rows) if i not in drop] + new_rows)
if open_out:
    with open(open_out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["company_id", "stmt", "concept", "period", "why"])
        w.writeheader()
        w.writerows(opens)
print("contested", len(contested), "| rows replaced", len(drop), "-> new", len(new_rows), "| open periods", len(opens))
