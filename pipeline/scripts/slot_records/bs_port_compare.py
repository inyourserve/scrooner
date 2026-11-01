"""Gates B, C and D of bs_port_gate.sh (stdlib, run with -I). Prints one line per check and writes
<work>/gate_report.json with every difference.
usage: bs_port_compare.py <work_dir> <report_v4.json> <bs_records_v3.jsonl>
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

work, v4_path, v3_path = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
new, comp = work / "new", work / "company"
out = {}


def lines(p):
    return [json.loads(x) for x in open(p) if x.strip()]


def canon(o):
    return json.dumps(o, sort_keys=True)


def same_set(name, a, b):
    sa, sb = Counter(map(canon, a)), Counter(map(canon, b))
    only_a, only_b = sa - sb, sb - sa
    out[name] = {"cohort": sum(sa.values()), "company": sum(sb.values()),
                 "only_cohort": [json.loads(k) for k in only_a], "only_company": [json.loads(k) for k in only_b]}
    ok = not only_a and not only_b
    print(f"  {'identical ' if ok else 'DIFFERENT '} {name}: cohort {sum(sa.values())}, company {sum(sb.values())}"
          + ("" if ok else f", only cohort {sum(only_a.values())}, only company {sum(only_b.values())}"))
    return ok


print("== B: company mode vs cohort mode (ported code, same filings)")
for f in ("bs_eras.json", "debt_eras.json"):
    a, b = json.load(open(new / f)), json.load(open(comp / f))
    same_set(f, [{"cik": k, **e} for k, v in a.items() for e in v], [{"cik": k, **e} for k, v in b.items() for e in v])
for f in ("bs_boundaries.txt", "debt_boundaries.txt"):
    same_set(f, open(new / f).read().split("\n"), open(comp / f).read().split("\n"))
same_set("debt_records.jsonl", lines(new / "debt_records.jsonl"), lines(comp / "debt_records.jsonl"))


def norm_cell(c):
    c = dict(c)
    if c["verdict"] in ("prod_blank", "prod_agrees", "prod_differs"):
        c["verdict"] = "publishable"
    c.pop("prod_value", None)
    return c


ca, cb = json.load(open(new / "debt_replay.json")), json.load(open(comp / "debt_replay.json"))
same_set("debt_replay cells (verdict prod_* = publishable, prod_value dropped)",
         [norm_cell(c) for c in ca["cells"]], [norm_cell(c) for c in cb["cells"]])

print("== C: debt replay, company mode, vs the Verifier-passed report_v4.json")
v4 = {(c["ticker"], c["period_end"]): norm_cell(c) for c in json.load(open(v4_path))["cells"]}
got = {(c["ticker"], c["period_end"]): norm_cell(c) for c in cb["cells"]}
tickers = {t for t, _ in v4}
stat, diffs = Counter(), defaultdict(list)
VALUE = ("slot_lease_inclusive", "slot_borrowings")
for k, ref in sorted(v4.items()):
    g = got.get(k)
    if g is None:
        stat["missing_in_port"] += 1
        diffs["missing_in_port"].append({"key": k, "v4": ref})
        continue
    if ref["verdict"] != g["verdict"]:
        cls = "verdict_differs"
    elif any(ref.get(f) != g.get(f) for f in VALUE):
        cls = "value_differs"
    elif ref.get("accession") != g.get("accession"):
        cls = "accession_differs"
    elif ref.get("members") != g.get("members"):
        cls = "members_differ_same_value"
    elif any(ref.get(f) != g.get(f) for f in ("note_finance_lease_added", "note_current_portion_added", "note_flag")):
        cls = "note_fields_differ_same_value"
    else:
        cls = "identical"
    stat[cls] += 1
    if cls != "identical":
        diffs[cls].append({"key": k, "v4": {f: ref.get(f) for f in ("verdict", *VALUE, "accession", "members", "note_flag", "note_finance_lease_added")},
                           "port": {f: g.get(f) for f in ("verdict", *VALUE, "accession", "members", "note_flag", "note_finance_lease_added")}})
extra = Counter(g["verdict"] for k, g in got.items() if k[0] in tickers and k not in v4)
publishable_v4 = sum(1 for c in v4.values() if c["verdict"] == "publishable")
same_value_publishable = sum(1 for k, c in v4.items() if c["verdict"] == "publishable" and k in got
                             and got[k]["verdict"] == "publishable" and all(got[k].get(f) == c.get(f) for f in VALUE))
print(f"  v4 cells {len(v4)} ({publishable_v4} publishable); port reproduces the publishable value at {same_value_publishable}")
for cls, n in sorted(stat.items()):
    print(f"  {cls}: {n}")
print(f"  port cells outside report_v4's keys (pilot companies): {dict(extra)}")
out["C"] = {"stat": dict(stat), "extra_keys": dict(extra), "diffs": diffs,
            "per_company": {t: dict(Counter(("same" if (k in got and got[k]["verdict"] == c["verdict"] and all(got[k].get(f) == c.get(f) for f in VALUE)) else "diff")
                                            for k, c in v4.items() if k[0] == t)) for t in sorted(tickers)}}
for t, s in out["C"]["per_company"].items():
    print(f"    {t}: {s}")

print("== D: bs_assemble company mode vs the Verifier-passed bs_records_v3.jsonl")
FIELDS = ("filing_from", "filing_to", "period_from", "period_to", "filings_observed", "total_liabilities_rule",
          "requires_identity_tie", "equity_parent_tag", "nci_tag", "equity_component_tags", "mezzanine_dim_tags", "coverage_clean")


def members(r):
    return [(m["tag"], m.get("weight"), m.get("tax_covered"), m.get("custom")) for m in r["total_liabilities_members"]]


v3 = {(r["cik"], r["filing_from"]): r for r in lines(v3_path)}
mine = {(r["cik"], r["filing_from"]): r for r in lines(comp / "bs_records.jsonl")}
v3_ciks = {c for c, _ in v3}
stat, dd = Counter(), defaultdict(list)
for k, ref in sorted(v3.items()):
    g = mine.get(k)
    if g is None:
        stat["record_missing_in_port"] += 1
        dd["record_missing_in_port"].append({"key": k, "company": ref["company"], "period_from": ref["period_from"], "period_to": ref["period_to"]})
        continue
    # a field the reference file does not carry (v3 predates equity_component_tags) is not compared
    bad = [f for f in FIELDS if f in ref and ref.get(f) != g.get(f)]
    if any(f not in ref for f in FIELDS):
        stat["fields_absent_in_reference (not compared)"] += 1
    if members(ref) != members(g):
        bad.append("total_liabilities_members")
    if [m["tag"] for m in ref["mezzanine_face"]] != [m["tag"] for m in g["mezzanine_face"]]:
        bad.append("mezzanine_face")
    if (ref.get("cal_source") or "").split(":")[0] != (g.get("cal_source") or "").split(":")[0]:
        bad.append("cal_source")
    if ref.get("taxonomy_era_from") != g.get("taxonomy_era_from"):
        stat["taxonomy_era_differs (information)"] += 1
    if bad:
        stat["record_differs"] += 1
        dd["record_differs"].append({"key": k, "company": ref["company"], "fields": bad,
                                     "v3": {f: ref.get(f) for f in bad if f in FIELDS} | ({"members": members(ref)} if "total_liabilities_members" in bad else {}) | ({"cal_source": ref.get("cal_source")} if "cal_source" in bad else {}),
                                     "port": {f: g.get(f) for f in bad if f in FIELDS} | ({"members": members(g)} if "total_liabilities_members" in bad else {}) | ({"cal_source": g.get("cal_source")} if "cal_source" in bad else {})})
    else:
        stat["record_identical"] += 1
extra = [k for k in mine if k[0] in v3_ciks and k not in v3]
# explain every difference (BS-PORT-2026-11-01.md, gate D)
eras = json.load(open(comp / "bs_eras.json"))
guard = {(c, e["first"]): {z["tag"] for z in e["zone_lines"] if z.get("equity_block_guard")} for c, el in eras.items() for e in el}
why = Counter()
for x in dd["record_differs"]:
    k, f = tuple(x["key"]), set(x["fields"])
    if "total_liabilities_members" in f:
        v3m, pm = {m[0] for m in x["v3"]["members"]}, {m[0] for m in x["port"]["members"]}
        lost = v3m - pm
        x["why"] = ("equity_block_guard_reclassed_a_v3_member" if lost and lost <= guard.get(k, set()) and not pm - v3m
                    else "member_list_other")
    elif f <= {"filing_to", "period_to", "filings_observed"}:
        x["why"] = "era_span_only"
    else:
        x["why"] = "other:" + ",".join(sorted(f))
    why[(x["why"], x["company"])] += 1
for x in dd["record_missing_in_port"]:
    cov = [r for r in mine.values() if r["cik"] == x["key"][0] and r["period_from"][:7] < x["period_from"][:7] <= r["period_to"][:7]]
    x["why"] = "same_era_starts_earlier_in_fsn" if cov else "no_covering_port_record"
    x["port_record"] = (cov[0]["filing_from"], cov[0]["period_from"], cov[0]["period_to"]) if cov else None
    why[(x["why"], x["company"])] += 1
for (w, co), n in sorted(why.items()):
    print(f"    {n:3} {co:5} {w}")
print(f"  v3 records {len(v3)}; " + ", ".join(f"{k} {v}" for k, v in sorted(stat.items())) + f"; port records not in v3 {len(extra)}")
out["D"] = {"stat": dict(stat), "diffs": dd, "port_only": [mine[k] | {"total_liabilities_members": members(mine[k])} for k in extra]}
json.dump(out, open(work / "gate_report.json", "w"), indent=1, default=str)
print("report:", work / "gate_report.json")
