#!/usr/bin/env python3
"""Seeded sampling frames drawn by Data Triage (WO-7 section 1.5): the role that fixes or proposes a
family never chooses the cells that judge it.

Ordering rule (reproducible in SQL): order by md5(<key> || <seed>) ascending, take the first n, where
<key> = company_id || '|' || data_point_name for cell frames and company_id for company frames.
The seed is mandatory and is written into the output meta so a frame can be re-drawn exactly.

Frames
  cells   a draw of N cells from a filtered frame (--where reasonless | valued_with_reason | pattern=<P> |
          dp=<a,b>), optional --exclude csv (company_id,data_point_name OR ticker,data_point_name)
  groups  group audit frames (doc 49 section 5): every member of every group with a seeded rank; census for
          groups of 30 or fewer, the first 30 seeded rows flagged reread=1 for the named mid groups, 60 for
          corporate, 30 default otherwise (flagged for the Sector Analyst to confirm). Risk-selected and
          negative-control members are NOT chosen here (the analyst picks them); the file says so.

usage: sampling_frame.py cells --seed S --n 40 --where reasonless [--exclude F] [--out F]
       sampling_frame.py groups --seed S [--groups group_assignment_draft.csv] [--out F]
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sb_lib as L  # noqa: E402

MID_GROUPS_READ_ALL_REREAD_30 = ("bank", "insurer", "utility", "energy", "reit")
CORPORATE_RANDOM = 60
DEFAULT_REREAD = 30
CENSUS_MAX = 30


def md5key(key: str, seed: str) -> str:
    return hashlib.md5((key + seed).encode("utf-8")).hexdigest()


def load_exclusions(path: Path, ticker_to_id: dict) -> set:
    out = set()
    for r in csv.DictReader(open(path, newline="", encoding="utf-8")):
        dp = r.get("data_point_name") or r.get("cell")
        if r.get("company_id"):
            cid = int(r["company_id"])
        else:
            cid = ticker_to_id[r["ticker"]]
        out.add((cid, dp))
    return out


def cell_frame(ext: L.Extract, where: str, names: set):
    frame = []
    for (cid, dp), c in ext.cells.items():
        if dp not in names:
            continue
        if where == "reasonless":
            ok = (not c["has_value"]) and not c["reason"]
        elif where == "valued_with_reason":
            ok = c["has_value"] and bool(c["reason"])
        elif where.startswith("pattern="):
            ok = (not c["has_value"]) and L.reason_pattern(c["reason"]) == where[8:]
        elif where.startswith("dp="):
            ok = dp in set(where[3:].split(",")) and not c["has_value"]
        else:
            raise SystemExit(f"unknown --where {where!r}")
        if ok:
            frame.append((cid, dp))
    return sorted(frame)


def draw(frame, seed: str, n: int, exclude=frozenset()):
    pool = [k for k in frame if k not in exclude]
    ranked = sorted(pool, key=lambda k: (md5key(f"{k[0]}|{k[1]}", seed), k))
    return ranked[:n], len(pool)


def group_frames(groups: dict, seed: str):
    """groups: {company_id: group}. -> rows with seeded rank and the re-read flag per doc 49 section 5."""
    by = {}
    for cid, g in groups.items():
        by.setdefault(g, []).append(cid)
    rows = []
    for g in sorted(by):
        members = sorted(by[g], key=lambda c: (md5key(str(c), seed), c))
        size = len(members)
        if size <= CENSUS_MAX:
            policy, k, note = "census", size, "all members read; Verifier re-reads all"
        elif g in MID_GROUPS_READ_ALL_REREAD_30:
            policy, k, note = (
                "read_all_reread_30_plus_10_risk",
                DEFAULT_REREAD,
                "analyst adds 10 risk-selected",
            )
        elif g == "corporate":
            policy, k, note = (
                "random_60_plus_15_risk_plus_15_negative",
                CORPORATE_RANDOM,
                "analyst adds 15 risk and 15 negative controls",
            )
        else:
            policy, k, note = (
                "DEFAULT_30_policy_not_stated",
                DEFAULT_REREAD,
                "doc 49 section 5 names no policy for this group: Sector Analyst to confirm",
            )
        for rank, cid in enumerate(members, 1):
            rows.append(
                {
                    "group": g,
                    "group_size": size,
                    "policy": policy,
                    "company_id": cid,
                    "seed_rank": rank,
                    "md5key": md5key(str(cid), seed),
                    "reread": 1 if rank <= k else 0,
                    "policy_note": note,
                }
            )
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("cells")
    c.add_argument("--cells", type=Path, default=L.EXPORT_GZ)
    c.add_argument("--seed", required=True)
    c.add_argument("--n", type=int, required=True)
    c.add_argument("--where", required=True)
    c.add_argument("--exclude", type=Path)
    c.add_argument("--out", type=Path, required=True)
    g = sub.add_parser("groups")
    g.add_argument("--groups", type=Path, default=L.GROUPS_DRAFT)
    g.add_argument("--seed", required=True)
    g.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)

    ids, cohort = L.load_cohort()
    ticker = {cid: r["ticker"] for cid, r in cohort.items()}
    name = {cid: r["name"] for cid, r in cohort.items()}
    t2id = {v: k for k, v in ticker.items()}
    meta = {
        "seed": a.seed,
        "ordering": "md5(key || seed) ascending",
        "generator": "sampling_frame@1",
        "cohort_ids_hash": L.id_list_hash(ids),
    }
    if a.cmd == "cells":
        ext = L.Extract(a.cells)
        names = set(L.read_lines(L.D0_NAMES_FILE))
        frame = cell_frame(ext, a.where, names)
        excl = load_exclusions(a.exclude, t2id) if a.exclude else set()
        picked, pool = draw(frame, a.seed, a.n, excl)
        gmap = {
            int(r["company_id"]): r["group"]
            for r in csv.DictReader(open(L.GROUPS_DRAFT, newline=""))
        }
        graph = L.load_graph()
        with open(a.out, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(
                [
                    "rank",
                    "company_id",
                    "ticker",
                    "name",
                    "data_point_name",
                    "kind",
                    "gap_reason",
                    "group_draft",
                    "md5key",
                ]
            )
            for i, (cid, dp) in enumerate(picked, 1):
                w.writerow(
                    [
                        i,
                        cid,
                        ticker.get(cid, ""),
                        name.get(cid, ""),
                        dp,
                        graph.get(dp, {}).get("kind", ""),
                        ext.cells[(cid, dp)]["reason"],
                        gmap.get(cid, ""),
                        md5key(f"{cid}|{dp}", a.seed),
                    ]
                )
        meta.update(
            {
                "frame": a.where,
                "extract_sha256": L.sha256_decompressed(a.cells),
                "frame_size": len(frame),
                "excluded": len(excl & set(frame)),
                "pool_after_exclusion": pool,
                "n": len(picked),
            }
        )
    else:
        gmap = {
            int(r["company_id"]): r["group"]
            for r in csv.DictReader(open(a.groups, newline=""))
        }
        gmap = {c_: g_ for c_, g_ in gmap.items() if c_ in cohort}
        rows = group_frames(gmap, a.seed)
        with open(a.out, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(
                [
                    "group",
                    "group_size",
                    "policy",
                    "company_id",
                    "ticker",
                    "name",
                    "sic",
                    "seed_rank",
                    "md5key",
                    "reread",
                    "policy_note",
                ]
            )
            for r in rows:
                cid = r["company_id"]
                w.writerow(
                    [
                        r["group"],
                        r["group_size"],
                        r["policy"],
                        cid,
                        ticker.get(cid, ""),
                        name.get(cid, ""),
                        cohort[cid].get("sic", ""),
                        r["seed_rank"],
                        r["md5key"],
                        r["reread"],
                        r["policy_note"],
                    ]
                )
        meta.update(
            {
                "frame": "group_audit",
                "groups_file": str(Path(a.groups).resolve().relative_to(L.REPO))
                if Path(a.groups).resolve().is_relative_to(L.REPO)
                else str(a.groups),
                "groups_file_sha256": L.sha256_file(a.groups),
                "n_companies": len(gmap),
                "label": "DRAFT groups (v1): superseded when group_assignment_v2.csv exists; redraw then",
            }
        )
    Path(str(a.out) + ".meta.json").write_text(
        json.dumps(meta, indent=1, sort_keys=True)
    )
    print(json.dumps(meta, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
