"""Only standard-taxonomy tags may serve a value (Engineering 2026-11-12: core.fact holds no extension-taxonomy facts;
SEC companyfacts carries none). A concept/component row on a company extension tag becomes an excluded row
(custom_extension_no_fact, kept for lineage) plus a tagless not_presented row (held_custom_extension_no_fact) over its era,
cut around the concept's other tagless rows and serving rows. A component sum with one extension part loses all its parts
for the overlapping era (a partial sum is never served). Combined lines are left alone (they feed no concept).
Usage: standard_only.py <tag_map.csv> <out.csv>"""
import csv
import datetime
import sys

STD = {"us-gaap", "ifrs-full", "dei", "srt"}
TAGLESS = ("not_presented", "not_in_template")


def day(d, n):
    return (datetime.date.fromisoformat(d) + datetime.timedelta(days=n)).isoformat()


def con_of(r):
    return r["canonical_concept"] if r["decision"] == "concept" else r["parent_concept"] if r["decision"] == "component" else ""


def overlaps(a, b):
    return not (a["era_to"] < b["era_from"] or b["era_to"] < a["era_from"])


def free_pieces(a, b, taken):
    """[a, b] minus the taken (from, to) spans."""
    out = []
    for f, t in sorted(taken):
        if t < a or f > b:
            continue
        if f > a:
            out.append((a, day(f, -1)))
        a = max(a, day(t, 1))
    if a <= b:
        out.append((a, b))
    return out


def apply(rows):
    ext = [r for r in rows if r["decision"] in ("concept", "component") and r["taxonomy"] not in STD]
    # a sum with an extension part is withdrawn only over that part's era (a partial sum is never served)
    windows = {}
    for r in ext:
        if r["decision"] == "component":
            windows.setdefault((r["company_id"], r["parent_concept"]), []).append((r["era_from"], r["era_to"]))
    keep, cut, n = [], [], 0
    for r in rows:
        w = windows.get((r["company_id"], r["parent_concept"])) if r["decision"] == "component" else None
        if r in ext:
            cut.append(r)
            n += 1
        elif w and any(not (b < r["era_from"] or r["era_to"] < a) for a, b in w):
            n += 1
            inside = [(max(a, r["era_from"]), min(b, r["era_to"])) for a, b in w if not (b < r["era_from"] or r["era_to"] < a)]
            for a, b in free_pieces(r["era_from"], r["era_to"], inside):
                keep.append({**r, "era_from": a, "era_to": b})
            for a, b in inside:
                cut.append({**r, "era_from": a, "era_to": b})
        else:
            keep.append(r)
    new, done = [], set()
    for r in cut:
        con = con_of(r)
        new.append({**r, "decision": "excluded", "canonical_concept": "", "parent_concept": "", "combine_sign": "",
                    "reason_class": "custom_extension_no_fact", "decided_by": "standard_only",
                    "reason": f"{r['taxonomy']}:{r['tag']} is a company extension (or a part of a sum with one): no fact in companyfacts / core.fact (was {r['decision']} {con})"})
        if (r["company_id"], r["stmt"], con, r["era_from"], r["era_to"]) in done:
            continue
        done.add((r["company_id"], r["stmt"], con, r["era_from"], r["era_to"]))
        taken = [(x["era_from"], x["era_to"]) for x in keep + new if x["company_id"] == r["company_id"] and x["stmt"] == r["stmt"]
                 and ((x["decision"] in TAGLESS and x["canonical_concept"] == con) or (x["decision"] in ("concept", "component") and con_of(x) == con))]
        for a, b in free_pieces(r["era_from"], r["era_to"], taken):
            e = {k: "" for k in r}
            e.update(company_id=r["company_id"], cik=r["cik"], rank=r["rank"], ticker=r["ticker"], stmt=r["stmt"], decision="not_presented",
                     canonical_concept=con, reason_class="held_custom_extension_no_fact", era_from=a, era_to=b, decided_by="standard_only",
                     rule_id="tagmap.standard_only@1", reason="the printed line (or a part of the printed sum) is a company extension tag: no fact to serve",
                     lines="0", filings="0")
            new.append(e)
    return keep + new, n


if __name__ == "__main__":
    src, dst = sys.argv[1:3]
    rows = list(csv.DictReader(open(src)))
    out, n = apply(rows)
    with open(dst, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(out)
    print("extension rows withdrawn", n, "| tagless rows", sum(1 for r in out if r["decided_by"] == "standard_only" and r["decision"] == "not_presented"))
