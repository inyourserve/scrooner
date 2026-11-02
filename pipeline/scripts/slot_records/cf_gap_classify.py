"""Classify FSN-store gap keys of the cash-flow families by what the covering filing actually prints (stdlib, -I).

Inputs: the cohort dry run's gaps.csv (pilot.py causes) and the cash-flow face rows of every FSN set
(fsn_sec_cf_faces.py). For each gap key of dividends_paid_resolved / share_buybacks_resolved, the covering
filing is the earliest original 10-K/10-Q (amendments only when no original exists) whose period of report is
within 15 days of the key's period end (FY keys: 10-K forms only). Its primary cash-flow report
(cf_family_replay.primary_face) is classified line by line with run 7's own classifiers (dividend_class,
buyback_class, imported). One class per key:
  no_filing_in_fsn            no periodic filing for that period in any FSN set
  no_cash_flow_face           the filing has no cash-flow face rows
  no_line_on_face             no line of the family on the face (nothing to map: an absent line)
  only_excluded_lines         only lines run 7 excludes (preferred, NCI, tax withholding, ...): not the concept
  held_lines_only             only lines run 7 holds (combined, net, unresolved, partnership units, ...)
  common_line_seed_tag        a common line whose tag a seed maps: the gap is NOT a mapping gap (look at columns)
  common_line_unseeded_tag    a common line whose tag no seed maps: a mapping coverage gap
usage: cf_gap_classify.py <gaps.csv> <faces_dir> <seeds cf.jsonl> <out_dir>
"""
import csv
import gzip
import json
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from cf_family_replay import buyback_class, dividend_class, primary_face  # noqa: E402

FAM = {"dividends_paid_resolved": dividend_class, "share_buybacks_resolved": buyback_class}
EXCLUDED = {"excluded", "excluded_noncash", "inflow", "perimeter_preferred", "perimeter_nci", "perimeter_dividend_equivalents",
            "perimeter_tax_withholding_shares", "perimeter_excise_tax", "perimeter_sbc_plan_purchase",
            "perimeter_option_exercise", "perimeter_subsidiary_repurchase", "perimeter_share_swap"}


def ymd(s):
    return date(int(s[:4]), int(s[4:6]), int(s[6:8]))


def main(gaps_path, faces_dir, seeds_path, out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    seeded = defaultdict(set)
    for r in map(json.loads, open(seeds_path)):
        if r["match_kind"] == "std_tag":
            seeded[r["canonical_concept"]].add(r["tag"].split(":", 1)[1])
    keys = [r for r in csv.DictReader(open(gaps_path)) if r["data_point"] in FAM]
    ciks = {r["cik"] for r in keys}
    filings, face = {}, defaultdict(list)
    for p in sorted(Path(faces_dir).glob("*.jsonl.gz")):
        for line in gzip.open(p, "rt"):
            r = json.loads(line)
            if r["cik"] not in ciks:
                continue
            filings.setdefault(r["adsh"], {k: r[k] for k in ("cik", "form", "period", "filed", "fsn")})
            if not r.get("filing_only"):
                face[r["adsh"]].append((r["report"], r["line"], r["tag"], r["label"], r["custom"], r["negating"]))
    primary_face(face)
    by_cik = defaultdict(list)
    for a, f in filings.items():
        if f["period"]:
            by_cik[f["cik"]].append((a, f))
    sets_seen = sorted({f["fsn"] for f in filings.values()})
    rows, summary, tags = [], Counter(), defaultdict(Counter)
    for k in keys:
        end = date.fromisoformat(k["period_end"])
        cands = [(a, f) for a, f in by_cik[k["cik"]] if abs((ymd(f["period"]) - end).days) <= 15
                 and (k["grain"] != "FY" or f["form"].startswith("10-K"))]
        orig = [c for c in cands if not c[1]["form"].endswith("/A")] or cands
        orig.sort(key=lambda c: (c[1]["filed"], c[0]))
        detail, tagl = "", ""
        if not orig:
            cls = "no_filing_in_fsn"
        else:
            a, f = orig[0]
            lines = face.get(a, [])
            if not lines:
                cls = "no_cash_flow_face"
            else:
                got = [(fn_cls, t, lab) for _ln, t, lab, _cu, _ng in lines
                       if (fn_cls := FAM[k["data_point"]](t, lab))]
                common = [g for g in got if g[0] == "common"]
                if common:
                    unseeded = [g for g in common if g[1] not in seeded[k["data_point"]]]
                    cls = "common_line_unseeded_tag" if unseeded else "common_line_seed_tag"
                    tagl = "|".join(sorted({g[1] for g in common}))
                    for g in unseeded:
                        tags[k["data_point"]][g[1]] += 1
                elif not got:
                    cls = "no_line_on_face"
                elif all(g[0] in EXCLUDED for g in got):
                    cls = "only_excluded_lines"
                else:
                    cls = "held_lines_only"
                detail = "; ".join(f"{g[0]}:{g[1]}:{g[2][:60]}" for g in got[:4])
            k = {**k, "accession": a, "form": f["form"]}
        summary[(k["data_point"], k["cause"], cls)] += 1
        rows.append({**k, "class": cls, "common_tags": tagl, "lines": detail})
    with open(out / "cf_gap_keys_classified.csv", "w", newline="") as fo:
        w = csv.DictWriter(fo, ["cik", "company_id", "data_point", "grain", "period_end", "cause", "class", "accession", "form", "common_tags", "lines"], extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    res = {"fsn_sets_scanned": len(sets_seen), "keys": len(rows),
           "by_class": [{"data_point": d, "cause": c, "class": cl, "keys": n,
                         "companies": len({r["cik"] for r in rows if (r["data_point"], r["cause"], r["class"]) == (d, c, cl)})}
                        for (d, c, cl), n in sorted(summary.items(), key=lambda kv: -kv[1])],
           "unseeded_common_tags": {d: tc.most_common(40) for d, tc in tags.items()}}
    (out / "cf_gap_summary.json").write_text(json.dumps(res, indent=1) + "\n")
    for b in res["by_class"]:
        print(b)


if __name__ == "__main__":
    main(*sys.argv[1:5])
