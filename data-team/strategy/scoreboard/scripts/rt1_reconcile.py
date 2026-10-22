#!/usr/bin/env python3
"""RT-1: exact-equality reconciliation of the committed 2026-10-20 export against the
doc 44 numbers (WO-7, Data Triage review section 3).

No new scoreboard number is published before this passes. Exits 1 and prints every failing
equality if anything differs. stdlib only, no database.

usage: rt1_reconcile.py [--cells PATH] [--json]
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sb_lib as L  # noqa: E402

# doc 44 ten largest reason patterns (reason text as stored, '' = no reason). Exact counts.
TOP10_REASONS = [
    ("", 13349), ("incomplete:numerator", 3522), ("line_not_presented_in_filing", 2314),
    ("incomplete:add", 1802), ("missing:ebitda_ttm", 1641), ("negative_ratio_undefined_cagr", 968),
    ("incomplete:denominator", 890), ("incomplete:subtract", 847),
    ("line_in_filing_not_extracted", 654), ("missing:fcf_ttm", 602),
]
EXPECT = {
    "D0 cells": 160_718, "D0 companies": 986, "D0 data points": 163,
    "valued": 123_326, "valued pct": "76.73", "blank": 37_392, "reasonless": 13_349,
    "D0e cells": 131_138, "D0e valued": 98_332, "D0e valued pct": "74.98", "D0e blank": 32_806,
    "reasonless in the 30 removed rows": 3_165,
    "valued with reason": 116, "valued with reason ev_sales": 70, "valued with reason ev_ebitda": 46,
    # NOTE: the review/doc 49 say "309 distinct reason strings". Measured: 309 INCLUDING the empty
    # (no-reason) string, so 308 non-empty strings; the 132 patterns are non-empty only.
    "distinct blank reason strings (incl. none)": 309,
    "distinct non-empty reason strings": 308,
    "distinct non-empty reason patterns": 132,
    # kind split of blanks (graph kinds), doc 44 / review RT-1
    "blank metric": 22_740, "blank leaf_concept": 11_320, "blank resolved_concept": 1_564,
    "blank derived_concept": 897, "blank price_metric": 809, "blank external_source": 62,
    # concept-type vs metric-type split (F2)
    "concept-type cells": 79_866, "concept-type valued": 66_023,
    "metric-type cells": 80_852, "metric-type valued": 57_303,
    # reasonless by kind (review K2@1 note)
    "reasonless leaf_concept": 7_887, "reasonless metric": 3_723,
    "reasonless resolved_concept": 1_557, "reasonless derived_concept": 120,
    "reasonless external_source": 62,
}


def run(cells_path: Path = L.EXPORT_GZ, shards: Path = L.SHARDS, graph_path: Path = L.GRAPH):
    """-> list of dict(check, expected, observed, passed)."""
    res = []

    def chk(name, expected, observed):
        res.append({"check": name, "expected": expected, "observed": observed,
                    "passed": expected == observed})

    chk("export sha256 (decompressed)", L.EXPORT_SHA256, L.sha256_decompressed(cells_path))
    chk("dependency graph sha256", L.GRAPH_SHA256, L.sha256_file(graph_path))
    chk("shards.csv sha256", L.SHARDS_SHA256, L.sha256_file(shards))
    ext = L.Extract(cells_path)
    graph = L.load_graph(graph_path)
    ids, _ = L.load_cohort(shards)

    chk("D0 cells", EXPECT["D0 cells"], len(ext))
    chk("duplicate (company, data point) keys", 0, ext.dups)
    chk("D0 companies", EXPECT["D0 companies"], len(ext.company_ids))
    chk("D0 data points", EXPECT["D0 data points"], len(ext.names))
    chk("rows == companies x data points", len(ext.company_ids) * len(ext.names), len(ext))
    chk("company ids hash", L.IDS_HASH, L.id_list_hash(ext.company_ids))
    chk("data point names hash", L.NAMES_HASH, L.name_list_hash(ext.names))
    chk("extract company ids == non-excluded shards.csv ids", ids, ext.company_ids)
    chk("d0_datapoints.txt == extract names", L.read_lines(L.D0_NAMES_FILE), ext.names)
    chk("every data point has a graph kind", [], sorted(n for n in ext.names if n not in graph))

    t = L.tally(ext, graph)
    chk("valued", EXPECT["valued"], t["valued"])
    chk("valued pct", EXPECT["valued pct"], L.pct(t["valued"], t["cells"]))
    chk("blank", EXPECT["blank"], t["blank"])
    chk("valued + blank == D0", EXPECT["D0 cells"], t["valued"] + t["blank"])
    chk("reasonless", EXPECT["reasonless"], t["reasonless"])
    chk("valued with reason", EXPECT["valued with reason"], t["valued_with_reason"])
    vwr = Counter(dp for (c, dp), v in ext.cells.items() if v["has_value"] and v["reason"])
    chk("valued with reason ev_sales", EXPECT["valued with reason ev_sales"], vwr.get("ev_sales", 0))
    chk("valued with reason ev_ebitda", EXPECT["valued with reason ev_ebitda"], vwr.get("ev_ebitda", 0))
    chk("valued-with-reason reasons", {"partial:missing_debt_or_cash": 116},
        dict(Counter(v["reason"] for v in ext.cells.values() if v["has_value"] and v["reason"])))

    for reason, n in TOP10_REASONS:
        chk(f"reason count [{reason or '(none)'}]", n, t["reasons"].get(reason, 0)
            if reason else t["reasonless"])
    chk("ten largest reason strings (exact text, none first)", [r for r, _ in TOP10_REASONS],
        _top_strings(t["reasons"]))

    nonempty = [r for r in t["reasons"] if r]
    chk("distinct non-empty reason strings", EXPECT["distinct non-empty reason strings"], len(nonempty))
    chk("distinct blank reason strings (incl. none)", EXPECT["distinct blank reason strings (incl. none)"],
        len(t["reasons"]))
    chk("distinct non-empty reason patterns", EXPECT["distinct non-empty reason patterns"],
        len({L.reason_pattern(r) for r in nonempty}))

    removed = L.read_lines(L.D0E_REMOVED_FILE)
    chk("D0e removal list size", 30, len(removed))
    keep = set(ext.names) - set(removed)
    te = L.tally(ext, graph, names=keep)
    chk("D0e cells", EXPECT["D0e cells"], te["cells"])
    chk("D0e cells == 986 x 133", 986 * 133, te["cells"])
    chk("D0e valued", EXPECT["D0e valued"], te["valued"])
    chk("D0e valued pct", EXPECT["D0e valued pct"], L.pct(te["valued"], te["cells"]))
    chk("D0e blank", EXPECT["D0e blank"], te["blank"])
    chk("reasonless in the 30 removed rows", EXPECT["reasonless in the 30 removed rows"],
        t["reasonless"] - te["reasonless"])

    for k in L.KIND_ORDER:
        chk(f"blank {k}", EXPECT[f"blank {k}"], t["by_kind"][k]["blank"])
    for k in ("leaf_concept", "metric", "resolved_concept", "derived_concept", "external_source"):
        chk(f"reasonless {k}", EXPECT[f"reasonless {k}"], t["by_kind"][k]["reasonless"])
    cc = sum(t["by_kind"][k]["cells"] for k in L.CONCEPT_KINDS)
    cv = sum(t["by_kind"][k]["valued"] for k in L.CONCEPT_KINDS)
    mc = sum(t["by_kind"][k]["cells"] for k in L.METRIC_KINDS)
    mv = sum(t["by_kind"][k]["valued"] for k in L.METRIC_KINDS)
    chk("concept-type cells", EXPECT["concept-type cells"], cc)
    chk("concept-type valued", EXPECT["concept-type valued"], cv)
    chk("metric-type cells", EXPECT["metric-type cells"], mc)
    chk("metric-type valued", EXPECT["metric-type valued"], mv)
    chk("concept + metric valued == valued", EXPECT["valued"], cv + mv)
    return res


def _top_strings(reasons: Counter):
    """The ten largest blank-reason strings, exact text ('' = no reason), count desc then text."""
    return [r for r, _ in sorted(reasons.items(), key=lambda kv: (-kv[1], kv[0]))[:10]]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cells", type=Path, default=L.EXPORT_GZ)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    res = run(a.cells)
    failed = [r for r in res if not r["passed"]]
    if a.json:
        print(json.dumps({"passed": not failed, "n_checks": len(res), "failures": failed}, indent=1,
                         default=str))
    else:
        for r in res:
            print(("PASS " if r["passed"] else "FAIL ") + f"{r['check']}: expected={_s(r['expected'])} observed={_s(r['observed'])}")
        print(f"\nRT-1 {'PASSED' if not failed else 'FAILED'}: {len(res) - len(failed)}/{len(res)} equalities hold")
    if failed:
        print(f"RT-1 FAILED: {len(failed)} equality(ies) differ. No scoreboard may be published.",
              file=sys.stderr)
        return 1
    return 0


def _s(v):
    s = str(v)
    return s if len(s) <= 90 else s[:87] + "..."


if __name__ == "__main__":
    sys.exit(main())
