"""Compare as-filed face facts (extract_fsds output) with stored core.fact / canonical_fact (pulled by pull_*.py).
stdlib only. usage: python3 -I compare.py <ap-workdir> <results.json>
FSDS rounds ddate to month-end, so keys use (tag, uom, year, month, qtrs)."""
import glob, gzip, json, sys, collections
from datetime import date
from decimal import Decimal

W, OUT = sys.argv[1], sys.argv[2]
TICK = {"1045810": "NVDA", "320193": "AAPL", "1652044": "GOOG", "1288776": "GOOG", "789019": "MSFT", "1018724": "AMZN",
        "1326801": "META", "1730168": "AVGO", "1441634": "AVGO", "1318605": "TSLA", "59478": "LLY", "723125": "MU"}


def ym(s):
    """FSDS rounds ddate to the NEAREST month-end (verified: AAPL 2015-03-28 -> 2015-03-31); apply the same rounding to
    stored dates so 52/53-week calendars (MU, AVGO: period ends early in a month) match."""
    y, m, d = int(s[:4]), int(s[5:7]), int(s[8:10])
    if d <= 15:
        m -= 1
        if m == 0:
            y, m = y - 1, 12
    return f"{y:04d}-{m:02d}"


def qtrs_of(a, b):
    y0, m0, d0 = map(int, a.split("-")); y1, m1, d1 = map(int, b.split("-"))
    return round((date(y1, m1, d1) - date(y0, m0, d0)).days / 91.3)


ext = collections.defaultdict(list)   # adsh -> rows
for fn in sorted(glob.glob(f"{W}/out/*.jsonl.gz")):
    for l in gzip.open(fn, "rt"):
        r = json.loads(l); ext[r["adsh"]].append(r)

res = {"per_company": {}, "notes": []}
tot = collections.Counter()
diffs = []
missd = []
for t in sorted(set(TICK.values())):
    st = collections.defaultdict(dict)  # adsh -> key -> list[(value, auth)]
    for l in gzip.open(f"{W}/stored/stored_{t}.jsonl.gz", "rt"):
        acc, form, tx, tag, unit, s, e, v, auth, der, fid = json.loads(l)
        k = (tag, "usd" if unit == "usd/shares" else unit, ym(e), 0 if s == e else qtrs_of(s, e))
        st[acc].setdefault(k, []).append((Decimal(v), auth, tx))
    anyf = collections.defaultdict(set)
    for a_, d_ in st.items():
        for k_, l_ in d_.items():
            for x_ in l_:
                anyf[k_].add(x_[0])
    c = collections.Counter()
    for adsh, rows in ext.items():
        if TICK.get(rows[0]["cik"]) != t:
            continue
        c["filings_parsed"] += 1
        if adsh not in st:
            c["filings_not_in_stored_facts"] += 1
        seen = {}
        face_tags = set()
        for r in rows:
            if not r["value"] or r["dims"] != "" or r["coreg"] != "":
                continue
            if r["end"] < "2014-06-01":
                continue  # stored pull window starts 2014-06-01
            face_tags.add(r["tag"])
            k = (r["tag"], r["uom"].lower(), r["end"][:7], r["qtrs"])
            seen[k] = (Decimal(r["value"]), r)
        for k, (v, r) in seen.items():
            if adsh not in st:
                c["facts_in_filings_with_no_stored_facts"] += 1
                continue
            c["face_nondim_facts"] += 1
            if r["custom"]:
                c["custom_tag_facts"] += 1
            cand = st.get(adsh, {}).get(k)
            if cand is None:
                c["absent_in_stored" + ("_custom" if r["custom"] else "")] += 1
                if not r["custom"]:
                    o_ = anyf.get(k)
                    c["absent_noncustom__" + ("nowhere_in_company_store" if not o_ else "same_value_under_other_filing" if v in o_ else "other_filing_has_different_value")] += 1
                if len(diffs) < 4000:
                    diffs.append({"t": t, "adsh": adsh, "kind": "absent_in_stored", "tag": k[0], "end": k[2], "qtrs": k[3], "value": str(v), "custom": r["custom"], "label": r["label"], "stmt": r["stmt"]})
            elif any(v == x[0] for x in cand):
                c["exact"] += 1
            else:
                c["value_differs"] += 1
                diffs.append({"t": t, "adsh": adsh, "kind": "value_differs", "tag": k[0], "end": k[2], "qtrs": k[3], "fsds": str(v), "stored": [str(x[0]) for x in cand], "label": r["label"]})
        # recall: stored facts of this filing whose tag is on the extractor's face set (same filing) but key missing
        for k, lst in st.get(adsh, {}).items():
            if k[0] in face_tags and lst[0][2] == "us-gaap":
                c["stored_facts_on_face_tags"] += 1
                if k not in seen:
                    c["stored_face_tag_fact_not_in_extractor"] += 1
                    if len(missd) < 3000:
                        missd.append({"t": t, "adsh": adsh, "tag": k[0], "uom": k[1], "end": k[2], "qtrs": k[3], "stored": str(lst[0][0])})
    res["per_company"][t] = dict(c)
    tot.update(c)
res["total"] = dict(tot)
res["diffs"] = diffs
res["missd"] = missd
json.dump(res, open(OUT, "w"), indent=1)
print(json.dumps(res["total"], indent=1))
for t, c in res["per_company"].items():
    print(t, c.get("filings_parsed"), c.get("face_nondim_facts"), c.get("exact"), c.get("value_differs"), c.get("absent_in_stored"), c.get("stored_face_tag_fact_not_in_extractor"))
