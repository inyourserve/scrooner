#!/usr/bin/env python3
"""Publish reason_class_map v2.1 against v2 (Chief's second review). Writes, never overwriting:
  defects/<date>.defects.map-v2.1.csv.gz, maps/reclass_v2_to_v2_1_<date>.csv,
  frames/verifier_queue_v2_1_<date>.csv (116 partial:missing_debt_or_cash first, then gross-margin, buyback, dividend fallbacks)
and appends a v2 -> v2.1 section (full sha256 of the new map, counts, quarter-label reconciliation) to CHAIN.md and the manifest.

usage: reclass_v2_1.py [--cells PATH] [--as-of 2026-10-20] [--seed 20261022] [--per-row 10]
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

NAMED_CASES = ("PFE", "CMI", "GOOG")


def classify_blank(ext, graph, rmap, names, legacy):
    clf = L.Classifier(ext, graph, rmap, legacy_bucket=legacy)
    out = {}
    for (cid, dp), c in sorted(ext.cells.items()):
        if dp in names and not (c["has_value"] and not c["reason"]):
            out[(cid, dp)] = clf.classify(cid, dp)
    return out, clf


def counts(ext, res):
    cls, buck, flag = Counter(), Counter(), 0
    for k, r in res.items():
        if ext.cells[k]["has_value"]:
            continue
        cls[r.cls] += 1
        if r.bucket:
            buck[r.bucket] += 1
        flag += 1 if r.currency_unknown else 0
    return cls, buck, flag


def prior_period_reconciliation(ext):
    tot = Counter()
    for (cid, dp), c in ext.cells.items():
        m = re.match(r"missing:prior_period\((\d{4})_(\w+)\)$", c["reason"])
        if m and not c["has_value"]:
            tot["all"] += 1
            if m.group(2) == "FY":
                tot["fy_base"] += 1
            else:
                tot["quarter_label_base"] += 1
                tot[f"label_{m.group(2)}"] += 1
                if int(m.group(1)) <= 2014:
                    tot["label_year_le_2014"] += 1
                if dp.endswith("_yoy"):
                    tot["quarter_yoy"] += 1
    return tot


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
    t2id = {v: k for k, v in ticker.items()}

    r2, _ = classify_blank(ext, graph, L.load_reason_map(L.REASON_MAP_V2), names, True)
    r21, clf = classify_blank(ext, graph, L.load_reason_map(L.REASON_MAP_V2_1), names, False)
    if clf.unmapped:
        raise SystemExit(f"UNMAPPED under v2.1: {sorted(clf.unmapped)}")
    c2, b2, f2 = counts(ext, r2)
    c21, b21, f21 = counts(ext, r21)

    new_files = []
    dpath = out / "defects" / f"{a.as_of}.defects.map-v2.1.csv.gz"
    tpath = out / "maps" / f"reclass_v2_to_v2_1_{a.as_of}.csv"
    qpath = out / "frames" / f"verifier_queue_v2_1_{a.as_of}.csv"
    for p in (dpath, tpath, qpath):
        if p.exists():
            raise SystemExit(f"REFUSING to overwrite {p}")
    rows = []
    for (cid, dp), r in r21.items():
        c = ext.cells[(cid, dp)]
        rows.append((cid, dp, graph.get(dp, {}).get("kind", "?"),
                     "valued_with_reason" if c["has_value"] else "blank", c["reason"], r.cls, r.owner, r.rf,
                     r.note, r.root_cause, r.candidate, r.second_signal, r.bucket,
                     "yes" if r.excl_k1c else "", "yes" if r.currency_unknown else ""))
    L.write_gz_deterministic(B.defects_csv(rows, a.as_of, ticker, {}), dpath)
    new_files.append(dpath)

    trans = Counter()
    for k, r in r21.items():
        if not ext.cells[k]["has_value"]:
            o = r2[k]
            trans[(o.cls, r.cls, o.candidate, r.candidate, o.second_signal, r.second_signal)] += 1
    with open(tpath, "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["v2_class", "v2_1_class", "v2_candidate", "v2_1_candidate", "v2_second_signal",
                    "v2_1_second_signal", "cells", "changed"])
        for key, n in sorted(trans.items()):
            w.writerow([*key, n, "no" if key[0::2] == key[1::2] else "yes"])
    new_files.append(tpath)

    # ---- verifier queue: priority 1 = the 116 valued cells that carry a reason -------------------
    def pool(pred):
        return sorted(k for k, r in r21.items() if pred(k, r))

    q = []

    def add(prio, group, keys, n, label):
        picked, size = SF.draw(keys, a.seed, n) if n is not None else (sorted(keys, key=lambda k: (SF.md5key(f"{k[0]}|{k[1]}", a.seed), k)), len(keys))
        named = [k for k in keys if ticker.get(k[0]) in NAMED_CASES and k not in picked]
        for i, k in enumerate([*picked, *named], 1):
            r = r21[k]
            q.append([prio, group, label, i, "named_case" if k in named else "", k[0], ticker.get(k[0], ""), k[1],
                      ext.cells[k]["reason"], len(keys), r.cls, r.owner, r.candidate, r.second_signal, r.note,
                      SF.md5key(f"{k[0]}|{k[1]}", a.seed), "DATA-INFERRED"])

    add(1, "partial:missing_debt_or_cash", pool(lambda k, r: ext.cells[k]["has_value"] and r.excl_k1c), None,
        "EV shown while debt or cash is missing (W13 candidate); all cells")
    fb = lambda pat: pool(lambda k, r: (not ext.cells[k]["has_value"]) and r.note.startswith("walk_no_blank_input")  # noqa: E731
                          and L.reason_pattern(ext.cells[k]["reason"]) == pat)
    add(2, "gross_margin_fallback", fb("missing:fewer_than_3_years_gross_margin"), a.per_row,
        "margin_expanding_3yr, unclassified / metric_only_fallback (v2.1 a)")
    add(3, "share_buybacks_ttm_fallback", fb("missing:share_buybacks_ttm"), a.per_row, "evidenced_zero candidate (v2.1 c)")
    add(4, "dividends_paid_ttm_fallback", fb("missing:dividends_paid_ttm"), a.per_row, "evidenced_zero candidate (v2.1 c)")
    add(5, "dividends_per_share_ttm_fallback", fb("missing:dividends_per_share_ttm"), a.per_row,
        "evidenced_zero candidate (v2.1 c)")
    carried = out / "frames" / f"verifier_queue_map_v2_{a.as_of}.csv"
    n_carried = 0
    if carried.exists():
        for r in csv.DictReader(open(carried, newline="")):
            q.append([6, f"v2_items_3_5_6:{r['pattern_key']}", f"{r['family']} (carried from the v2 queue)", r["rank"], "",
                      r["company_id"], r["ticker"], r["data_point_name"], r["gap_reason"], r["row_cells"],
                      r["proposed_class"], r["proposed_owner"], "", "", "", r["md5key"], "DATA-INFERRED"])
            n_carried += 1
    with open(qpath, "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["priority", "group", "label", "rank", "named_case", "company_id", "ticker", "data_point_name",
                    "gap_reason", "group_cells", "proposed_class", "proposed_owner", "candidate_state", "second_signal",
                    "note", "md5key", "evidence_label"])
        w.writerows(q)
    new_files.append(qpath)
    qprio = Counter(r[0] for r in q)

    # ---- CHAIN.md ----------------------------------------------------------------------------------
    pp = prior_period_reconciliation(ext)
    sha = L.sha256_file(L.REASON_MAP_V2_1)
    sect = ["## Reason map v2.1: K4 proxy v2 vs v2.1 (" + a.as_of + " export)\n",
            "v2 (`reason_class_map_v2.csv`, as published) is kept. v2.1 fixes (a)-(f) of the Chief's second review. "
            "DATA-INFERRED; blank cells only (37,392).\n",
            f"- `reason_class_map_v2_1.csv` sha256 **{sha}**",
            f"- `reason_class_map_v2.csv` sha256 {L.sha256_file(L.REASON_MAP_V2)} (unchanged)\n",
            "| class | v2 | v2.1 | change |\n|---|---|---|---|"]
    for cls in L.CLASSES:
        sect.append(f"| {cls} | {c2.get(cls, 0):,} | {c21.get(cls, 0):,} | {c21.get(cls, 0) - c2.get(cls, 0):+,} |")
    sect.append(f"| total | {sum(c2.values()):,} | {sum(c21.values()):,} | |\n")
    sect.append("| unclassified sub-bucket / flag | v2 | v2.1 |\n|---|---|---|")
    sect.append(f"| metric_only_fallback (bucket) | {b2.get('metric_only_fallback', 0):,} | {b21.get('metric_only_fallback', 0):,} |")
    sect.append(f"| currency_unknown (v2: sub-bucket of unclassified; v2.1: orthogonal flag, any class) | {b2.get('currency_unknown', 0):,} | {f21:,} |")
    sect.append("\nCurrency flag is now independent of the class: it marks every blank cell whose classification rests on a "
                "concept input valued at 'any period' (F2). It includes the period-class walk fallbacks "
                f"({sum(1 for k, r in r21.items() if (not ext.cells[k]['has_value']) and r.currency_unknown and r.cls == 'period' and r.note.startswith('walk_no_blank_input')):,} cells).\n")
    sect.append("Expected effect of (a) was period 6,612 -> 6,444, unclassified 21,554 -> 21,722, metric_only_fallback 0 -> 168: "
                f"measured period {c21.get('period', 0):,}, unclassified {c21.get('unclassified', 0):,}, "
                f"metric_only_fallback {b21.get('metric_only_fallback', 0):,}.\n")
    sect.append("### Quarter-label prior-period family: three counts reconciled\n")
    sect.append("| count | what it is | evidence |\n|---|---|---|")
    sect.append(f"| 1,879 | every blank cell whose reason is `missing:prior_period(...)` (the map's n_cells for the pattern) | MEASURED on the export: {pp['all']:,} |")
    sect.append(f"| {pp['fy_base']} | of those, the base is a fiscal-year label (`YYYY_FY`) | MEASURED |")
    sect.append(f"| 1,798 | of those, the base carries a quarter label (Q1 {pp['label_Q1']:,}, Q2 {pp['label_Q2']:,}, Q3 {pp['label_Q3']:,}, Q4 {pp['label_Q4']:,}); 1,879 = {pp['fy_base']} + {pp['quarter_label_base']:,} exactly | MEASURED: {pp['quarter_label_base']:,} |")
    sect.append("| 1,776 | docs 47/49 figure | NOT REPRODUCED. The text of that figure is in no committed file (searched data-team/ and doc/data-moat/); no cut of the export gives it (non-FY excluding yoy windows = "
                f"{pp['quarter_label_base'] - pp['quarter_yoy']:,}; label year 2015+ = {pp['quarter_label_base'] - pp['label_year_le_2014']:,}). The gap to 1,798 is 22 cells and its cause is unknown (a different build is possible: the table was rebuilt 2026-10-21). The owner of the doc 47/49 figure must supply its query |")
    sect.append(f"\nPre-2015 bases: {pp['label_year_le_2014']} of {pp['quarter_label_base']:,} by FISCAL LABEL (year <= 2014; MEASURED on the export). "
                "By `period_start` DATE the count is NOT_COMPUTABLE offline (the extract has no dates); the query is `sql/Q_prior_period_base_dates.sql` "
                "(NOT RUN), with the 1,798 cells in `lists/prior_period_quarter_label_bases_" + a.as_of + ".csv`. Do not quote 62 as a date count.\n")
    sect.append(f"Verifier queue `frames/verifier_queue_v2_1_{a.as_of}.csv`: priority 1 = all {qprio[1]} `partial:missing_debt_or_cash` cells; "
                f"2 = {qprio[2]} gross-margin fallbacks (of 168); 3-5 = {qprio[3]}, {qprio[4]}, {qprio[5]} buyback / dividend TTM fallbacks "
                f"(plus named cases {', '.join(NAMED_CASES)} where one of their cells is in those pools); 6 = {qprio[6]} cells carried from the v2 queue (items 3, 5, 6). DATA-INFERRED, none filing-checked.\n")
    chain = out / "CHAIN.md"
    head = chain.read_text()
    if sect[0].strip() in head:
        raise SystemExit("CHAIN.md already has this section")
    chain.write_text(head + "\n".join(sect) + "\n")
    new_files += [chain, out / "reason_class_map_v2_1.csv", out / "sql" / "Q_prior_period_base_dates.sql"]
    new_files = [f for f in new_files if f.name != "Q_prior_period_base_dates.sql"]  # sql files are not manifest-pinned
    n = B.manifest_append(out, new_files)
    print(f"wrote CHAIN.md section, manifest +{n}")
    print("v2.1 classes:", dict(c21), "bucket:", dict(b21), "currency flag:", f21, "queue:", dict(qprio))
    return 0


if __name__ == "__main__":
    sys.exit(main())
