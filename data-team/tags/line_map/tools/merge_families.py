"""Merge family resolver outputs into resolver-all110: a family row replaces the base row with the same key
(cik, data_point, period_end, grain). Usage: merge_families.py BASE.csv OUT.csv FAMILY.csv [FAMILY.csv ...]"""
import csv, sys, collections
base, out, fams = sys.argv[1], sys.argv[2], sys.argv[3:]
key = lambda r: (r['cik'], r['data_point'], r['period_end'], r['grain'])
rows = {key(r): r for r in csv.DictReader(open(base))}
fields = list(next(csv.DictReader(open(base))).keys())
n = collections.Counter()
for f in fams:
    for r in csv.DictReader(open(f)):
        k = key(r); n[(f.split('/')[-1], 'replaced' if k in rows else 'added')] += 1
        rows[k] = {c: r.get(c, '') for c in fields}
w = csv.DictWriter(open(out, 'w', newline=''), fieldnames=fields); w.writeheader(); w.writerows(rows.values())
print(len(rows), dict(n))
