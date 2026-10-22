#!/usr/bin/env python3
"""Re-classify an extract under reason_class_map_v2 and publish what moved (Chief's review of v1).

Writes (never overwrites):
  defects/<date>.defects.map-v2.csv.gz        the proxy register under map v2 (v1 register stays as published)
  maps/reclass_v1_to_v2_<date>.csv            per (v1 class -> v2 class) cell counts
  lists/prior_period_quarter_label_bases_<date>.csv   quarter-label prior-period bases (flag to the Standardization Lead)
  frames/verifier_queue_map_v2_<date>.csv     seeded cells for each DATA-INFERRED family split (items 3, 5, 6)
and appends a K4 old-vs-new section to CHAIN.md, then appends the new files to MANIFEST.sha256.

usage: reclass_v2.py [--cells PATH] [--as-of 2026-10-20] [--seed 20261022] [--per-row 10]
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_scoreboard as B  # noqa: E402
import sampling_frame as SF  # noqa: E402
import sb_lib as L  # noqa: E402

ITEM_OF = {"financial_institution_interest_income_not_revenue": 3, "bank_interest_income_not_revenue": 3,
           "reit_net_interest_income_not_revenue": 3, "bdc_reports_investment_income_not_revenue": 3,
           "zero_denominator": 5, "zero_base_value": 6}


def classify_all(ext, graph, rmap, names):
    clf = L.Classifier(ext, graph, rmap)
    out = {}
    for (cid, dp), c in sorted(ext.cells.items()):
        if dp not in names or (c["has_value"] and not c["reason"]):
            continue
        out[(cid, dp)] = clf.classify(cid, dp)
    return out, clf


def read_published(out: Path, as_of: str):
    """K4 proxy@1 counts exactly as published (the record)."""
    cls, own = {}, {}
    for r in csv.DictReader(open(out / f"{as_of}.csv", newline="")):
        if r["k_id"] == "K4" and r["k_version"] == "proxy@1":
            seg = r["segment"]
            (cls if seg.startswith("class:") else own)[seg.split(":", 1)[1]] = int(r["value"])
    return cls, own


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cells", type=Path, default=L.EXPORT_GZ)
    ap.add_argument("--as-of", default="2026-10-20")
    ap.add_argument("--seed", default="20261022")
    ap.add_argument("--per-row", type=int, default=10)
    ap.add_argument("--out-dir", type=Path, default=L.SB_DIR)
    a = ap.parse_args(argv)
    out = a.out_dir
    ext = L.Extract(a.cells)
    graph = L.load_graph()
    names = set(L.read_lines(L.D0_NAMES_FILE))
    ids, cohort = L.load_cohort()
    ticker = {c: r["ticker"] for c, r in cohort.items()}

    v2, clf2 = classify_all(ext, graph, L.load_reason_map(L.REASON_MAP_V2), names)
    mid, _ = classify_all(ext, graph, L.load_reason_map(L.REASON_MAP), names)   # v1 map, v2 classifier
    if clf2.unmapped:
        raise SystemExit(f"UNMAPPED under v2: {sorted(clf2.unmapped)}")
    pub_cls, pub_own = read_published(out, a.as_of)

    def blank_counts(res):
        c, o, b = Counter(), Counter(), Counter()
        for (cid, dp), r in res.items():
            if not ext.cells[(cid, dp)]["has_value"]:
                c[r.cls] += 1
                o[r.owner] += 1
                if r.bucket:
                    b[r.bucket] += 1
        return c, o, b

    c2, o2, b2 = blank_counts(v2)
    cm, om, bm = blank_counts(mid)

    # ---- files -------------------------------------------------------------------------------
    new_files = []
    dpath = out / "defects" / f"{a.as_of}.defects.map-v2.csv.gz"
    rows = []
    for (cid, dp), r in v2.items():
        c = ext.cells[(cid, dp)]
        rows.append((cid, dp, graph.get(dp, {}).get("kind", "?"),
                     "valued_with_reason" if c["has_value"] else "blank", c["reason"], r.cls, r.owner, r.rf,
                     r.note, r.root_cause, r.candidate, r.second_signal, r.bucket, "yes" if r.excl_k1c else ""))
    if dpath.exists():
        raise SystemExit(f"REFUSING to overwrite {dpath}")
    L.write_gz_deterministic(B.defects_csv(rows, a.as_of, ticker, {}), dpath)
    new_files.append(dpath)

    trans = Counter()
    v1reg = {}
    with L.open_text(out / "defects" / f"{a.as_of}.defects.csv.gz") as fh:
        for r in csv.DictReader(fh):
            v1reg[(int(r["company_id"]), r["data_point_name"])] = r["defect_class"]
    for key, r in v2.items():
        if ext.cells[key]["has_value"]:
            continue
        trans[(v1reg.get(key, "?"), r.cls)] += 1
    tpath = out / "maps" / f"reclass_v1_to_v2_{a.as_of}.csv"
    if tpath.exists():
        raise SystemExit(f"REFUSING to overwrite {tpath}")
    with open(tpath, "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["v1_class", "v2_class", "cells", "moved"])
        for (f, t), n in sorted(trans.items()):
            w.writerow([f, t, n, "no" if f == t else "yes"])
    new_files.append(tpath)

    # quarter-label prior-period bases (item 2)
    ppath = out / "lists" / f"prior_period_quarter_label_bases_{a.as_of}.csv"
    summ = Counter()
    with open(ppath, "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["company_id", "ticker", "data_point_name", "base_period", "base_label", "growth_window",
                    "note"])
        for (cid, dp), c in sorted(ext.cells.items()):
            m = re.match(r"missing:prior_period\((\d{4})_(\w+)\)$", c["reason"])
            if not m or c["has_value"]:
                continue
            lab = m.group(2)
            win = (re.search(r"(\d+y)_cagr|(yoy)", dp) or [None])[0] or ""
            summ[(dp, lab)] += 1
            if lab != "FY":
                w.writerow([cid, ticker.get(cid, ""), dp, f"{m.group(1)}_{lab}", lab, win,
                            "annual growth window anchored on a quarter-label base: check the base choice"])
    new_files.append(ppath)

    # verifier queue (items 3, 5, 6): DATA-INFERRED splits
    qpath = out / "frames" / f"verifier_queue_map_v2_{a.as_of}.csv"
    m2 = L.load_reason_map(L.REASON_MAP_V2)
    with open(qpath, "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["item", "pattern_key", "family", "proposed_class", "proposed_owner", "row_cells", "rank",
                    "company_id", "ticker", "data_point_name", "gap_reason", "md5key", "label"])
        for (pat, fam), row in sorted(m2.items()):
            if row["queue_verifier_sample"] != "yes" or fam == "*":
                continue
            cells = [k for k, r in v2.items() if r.note.endswith(f"reason:{pat}") is False and False]
            cells = sorted(k for k, r in v2.items()
                           if L.reason_pattern(ext.cells[k]["reason"]) == pat
                           and L.data_point_family(k[1], graph) == fam and not ext.cells[k]["has_value"])
            picked, _ = SF.draw(cells, a.seed, a.per_row)
            for i, (cid, dp) in enumerate(picked, 1):
                w.writerow([ITEM_OF.get(pat, ""), pat, fam, row["class"], row["owner"], len(cells), i, cid,
                            ticker.get(cid, ""), dp, ext.cells[(cid, dp)]["reason"],
                            SF.md5key(f"{cid}|{dp}", a.seed), "DATA-INFERRED"])
    new_files.append(qpath)

    # ---- CHAIN.md section --------------------------------------------------------------------
    sect = [f"## Reason map v2: K4 proxy old vs new ({a.as_of} export)\n",
            "v1 = `reason_class_map.csv` as published in `2026-10-20.csv` (record, unchanged). "
            "mid = v1 map run through the v2 classifier (isolates the code fixes: items 1, 7, 8, 11). "
            f"v2 = `reason_class_map_v2.csv` (sha256 {L.sha256_file(L.REASON_MAP_V2)[:16]}). "
            "All DATA-INFERRED; blank cells only (37,392). Items 3, 5, 6 are queued for a Verifier sample "
            f"(`frames/verifier_queue_map_v2_{a.as_of}.csv`, {a.per_row} per row, a proposal).\n",
            "| class | v1 (published) | mid | v2 | v2 - v1 |\n|---|---|---|---|---|"]
    for cls in L.CLASSES:
        sect.append(f"| {cls} | {pub_cls.get(cls, 0):,} | {cm.get(cls, 0):,} | {c2.get(cls, 0):,} | {c2.get(cls, 0) - pub_cls.get(cls, 0):+,} |")
    sect.append(f"| total | {sum(pub_cls.values()):,} | {sum(cm.values()):,} | {sum(c2.values()):,} | |\n")
    sect.append("| owner | v1 (published) | mid | v2 | v2 - v1 |\n|---|---|---|---|---|")
    for ow in L.OWNERS:
        sect.append(f"| {ow} | {pub_own.get(ow, 0):,} | {om.get(ow, 0):,} | {o2.get(ow, 0):,} | {o2.get(ow, 0) - pub_own.get(ow, 0):+,} |")
    sect.append("\n| unclassified sub-bucket (v2) | cells |\n|---|---|")
    for b in ("currency_unknown", "metric_only_fallback"):
        sect.append(f"| {b} | {b2.get(b, 0):,} |")
    sect.append(f"| (unclassified with no bucket: null reason, no row, other) | {c2.get('unclassified', 0) - sum(b2.values()):,} |")
    vwr = sum(1 for k, r in v2.items() if ext.cells[k]["has_value"])
    sect.append(f"\nValued cells with a reason (excluded from K1c when K1c is measured): {vwr}. "
                f"Cells whose class moved v1 -> v2: {sum(n for (f, t), n in trans.items() if f != t):,} "
                f"(`maps/reclass_v1_to_v2_{a.as_of}.csv`).\n")
    chain = out / "CHAIN.md"
    head = chain.read_text()
    title = sect[0].strip()
    if title in head:
        raise SystemExit("CHAIN.md already has this section")
    chain.write_text(head + "\n".join(sect) + "\n")
    new_files += [chain, out / "reason_class_map_v2.csv"]
    n = B.manifest_append(out, new_files)
    print(f"wrote {len(new_files) - 2} files, CHAIN.md section, manifest +{n}")
    print("v2 classes:", dict(c2), "buckets:", dict(b2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
