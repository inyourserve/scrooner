"""Per-group frequency of the tags and labels on the filers' own balance sheet and income statement (R-file rows), from the reader JSON.
Evidence: FILING-CHECKED at the row level for the filings read (Reader 1); counts are over companies, once per company."""
import csv, json, os, sys, collections, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
DATA = "/Users/vikash/wt-sector-groups/data-team/strategy/data/"
SC = os.environ.get("SA_SCRATCH", "/private/tmp/claude-501/-Users-vikash-scrooner/b256f7de-d50a-4757-b526-8e0954fad6db/scratchpad/w")
A = [a for a in csv.DictReader(open(DATA + "group_assignment_v2.csv")) if a["cohort_status"] == "cohort_file_v1" and not a["group"].startswith("excluded") and a["group"] != "OPEN"]
cnt = collections.defaultdict(collections.Counter); lab = collections.defaultdict(lambda: collections.defaultdict(collections.Counter)); N = collections.Counter()
for a in A:
    p = f"{SC}/reads/{a['cik']}.json"
    if not os.path.exists(p): continue
    r = json.load(open(p))
    if "rows" not in r: continue
    N[a["group"]] += 1
    seen = set()
    for st in ("BS", "IS"):
        for tag, label, val in r["rows"].get(st, []):
            if not tag: continue
            k = (st, tag)
            if k in seen: continue
            seen.add(k); cnt[a["group"]][k] += 1; lab[a["group"]][k][label[:50]] += 1
rows = []
for g, c in cnt.items():
    for (st, tag), n in c.items():
        if n >= 2 or N[g] <= 14:
            rows.append(dict(group=g, statement=st, tag=tag, companies=n, group_size_read=N[g], share=round(n / N[g], 3), top_label=lab[g][(st, tag)].most_common(1)[0][0]))
rows.sort(key=lambda x: (x["group"], -x["companies"], x["tag"]))
if __name__ == "__main__":
    with open(DATA + "sector_face_tags_v2.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    print(len(rows), dict(N))
