"""Second pass over machine docmaps (shared docmap.py @558f2f15): re-open the cited R page for every not_presented,
combined, component and NOTE row plus a seeded random 10% of mapped rows, and record agree/disagree.

This is a scripted re-check by a different code path (the row is found again on its own R page by element name and
the FY0 column by period end), NOT a human hand check; rows say so.

Usage: python3 -I check_pass.py <shared_dir> <cohort.csv> <m1_dir> <cache> <out_dir> <rank_from> <rank_to>
"""
import csv, json, math, os, random, re, sys
import datetime as dt

shared, cohort, m1, cache, out_dir, lo, hi = sys.argv[1:8]
sys.path.insert(0, shared)
import docmap as D  # noqa: E402

rows = list(csv.DictReader(open(cohort)))
os.makedirs(out_dir, exist_ok=True)
CHECK_STATUSES = {"not_presented", "combined", "component sum", "component_in_note"}


def close(a, b):
    return abs(abs(a) - abs(b)) <= max(0.5, 1e-6 * abs(b))


def page_value(base, rpage, tags, end, stmt, dp):
    """Sum of the FY0 values of the rows carrying these elements on these R pages (one tag per page or all on one)."""
    pages = rpage.split("+")
    total, found = 0.0, 0
    for t in tags:
        hit = None
        for pg in dict.fromkeys(pages):
            p = D.parse_r(D.get(base + pg, cache))
            idx = [i for i, (m, e) in enumerate(p["cols"]) if e == end and (stmt in ("BS", "NOTE") or m in (12, None))]
            for r in p["rows"]:
                if r["tag"] == t:
                    for i in idx:
                        if i < len(r["vals"]) and r["vals"][i] is not None:
                            hit = (D.scaled(r["vals"][i], dp, p), pg)
                            break
                if hit:
                    break
            if hit:
                break
        if hit is None:
            return None, f"{t} not found with a value in the {end} column on {rpage}"
        total += hit[0]
        found += 1
    return total, ""


def metalinks_tags(base):
    txt = D.get(base + "MetaLinks.json", cache)
    try:
        return set(next(iter(json.loads(txt)["instance"].values())).get("tag", {}))
    except Exception:
        return None


def check_company(rank):
    row = rows[rank - 1]
    tic, cik = row["ticker"], row["cik"]
    src = os.path.join(m1, f"{tic}-docmap-{D.DATE}.csv")
    md = os.path.join(m1, f"{tic}-docmap-{D.DATE}.md")
    if not os.path.exists(src):
        return {"rank": rank, "ticker": tic, "ok": False, "error": "no machine docmap"}
    recs = list(csv.DictReader(open(src)))
    mdt = open(md).read()
    m = re.search(r"- 10-K (\d{10}-\d{2}-\d{6}) \(CIK \d+, filed", mdt)
    accn = m[1] if m else ""
    end = next((r["note"].split("period ..")[-1][:10] for r in recs if "period .." in r["note"]), "")
    st = {"rank": rank, "ticker": tic, "ok": bool(recs and accn and end), "rows": len(recs), "checked": 0,
          "by_class": {}, "mapped_sample": 0, "mapped_disagree": 0, "other_disagree": 0}
    if not st["ok"]:
        for r in recs:
            r["check"] = "check: machine-full-filing"
        write(tic, recs, mdt, [], st)
        return st
    end_d = dt.date.fromisoformat(end)
    base = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accn.replace('-', '')}/"
    mapped = [r for r in recs if r["status"] == "mapped" and r["stmt"] != "NOTE"]
    sample = set(id(r) for r in random.Random(tic).sample(mapped, math.ceil(len(mapped) * 0.1))) if mapped else set()
    log = []
    for r in recs:
        r["check"] = "check: machine-full-filing"
        cls = ("NOTE" if r["stmt"] == "NOTE" else r["status"]) if (r["status"] in CHECK_STATUSES or r["stmt"] == "NOTE") \
            else ("mapped-sample" if id(r) in sample else None)
        if cls is None:
            continue
        st["checked"] += 1
        st["by_class"][cls] = st["by_class"].get(cls, 0) + 1
        if cls == "mapped-sample":
            st["mapped_sample"] += 1
        tags = [t for t in r["tags"].split("+") if t]
        if r["status"] == "not_presented":
            have = metalinks_tags(base)
            spec = next((d for d in D.DP if d[0] == r["data_point"]), None)
            full, comp = D.NOTE_FAMILY.get(r["data_point"], ((spec[2] if spec else []), []))
            if have is None:
                ok, why = None, "MetaLinks.json not available: absence not re-checked"
            else:
                present = [t for t in list(full) + list(comp) if f"us-gaap_{t}" in have]
                ok = not present
                why = ("none of the candidate elements in MetaLinks.json" if ok
                       else "element(s) present in the filing: " + ", ".join(present))
        elif r["status"] == "component_in_note":
            p = D.parse_r(D.get(base + r["r_page"].split("+")[0], cache))
            ok = any(x["tag"] in tags for x in p["rows"])
            why = f"component element on {r['r_page']}" if ok else f"element not on {r['r_page']}"
        elif not r["r_page"] or not tags:
            ok, why = None, "no R page or tag to re-open"
        else:
            v, why = page_value(base, r["r_page"], tags, end_d, r["stmt"], r["data_point"])
            ref = r["fy0_printed"] or r["fy0_api"]
            if v is None:
                ok = False
            elif not ref:
                ok, why = True, f"value {D.fmt(v)} read off its own R page (no companyfacts fact to compare)"
            elif "e" in ref.lower() and float(f"{v:.4g}") == float(ref):
                # the shared tool wrote a non-integer sum with %.4g (precision lost): restore the page value
                ok = True
                why = f"page value {round(v)} = printed {ref} at 4 significant digits; fy0_printed restored to the page value"
                if r["fy0_printed"] == ref:
                    r["fy0_printed"] = str(round(v))
                    st["format_fixes"] = st.get("format_fixes", 0) + 1
            else:
                ok = close(v, float(ref))
                why = f"page value {D.fmt(v)} vs {'printed' if r['fy0_printed'] else 'API'} {ref}"
            if v is not None and r["stmt"] == "NOTE" and not r["fy0_printed"]:
                r["fy0_printed"] = D.fmt(v)  # NOTE value read off its own R page
                if r["fy0_api"]:
                    r["match"] = "Y" if close(v, float(r["fy0_api"])) else "N"
        verdict = "agree" if ok else ("not re-checkable" if ok is None else "DISAGREE")
        if ok is False:
            st["mapped_disagree" if cls == "mapped-sample" else "other_disagree"] += 1
        r["check"] += f"; recheck (script, not hand) {r['r_page'] or 'MetaLinks.json'}: {verdict}: {why}"
        log.append((r["data_point"], cls, verdict, why))
    write(tic, recs, mdt, log, st)
    return st


def write(tic, recs, mdt, log, st):
    cols = list(D.COLS) + ["check"]
    with open(os.path.join(out_dir, f"{tic}-docmap-{D.DATE}.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in recs:
            w.writerow({k: r.get(k, "") for k in cols})
    L = ["", "## Check pass",
         "Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens "
         "the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, "
         f"plus a seeded random 10% of mapped rows ({st['mapped_sample']}). This is a scripted re-check, not a human hand check.",
         "", "| data point | class | verdict | detail |", "|---|---|---|---|"]
    L += [f"| {a} | {b} | {c} | {d.replace('|', '/')} |" for a, b, c, d in log]
    open(os.path.join(out_dir, f"{tic}-docmap-{D.DATE}.md"), "w").write(mdt.rstrip("\n") + "\n" + "\n".join(L) + "\n")


for rank in range(int(lo), int(hi) + 1):
    try:
        st = check_company(rank)
    except Exception as exc:  # noqa: BLE001
        st = {"rank": rank, "ticker": rows[rank - 1]["ticker"], "ok": False, "error": repr(exc)[:200]}
    with open(os.path.join(out_dir, f"_check-{lo}-{hi}.jsonl"), "a") as fh:
        fh.write(json.dumps(st) + "\n")
    print(json.dumps(st), flush=True)
