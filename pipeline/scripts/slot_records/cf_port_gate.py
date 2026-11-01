"""Regression gate for the cash-flow port (stdlib, run with -I). Compares two cf_family_replay output
directories family by family as MULTISETS of cells (company mode emits companies in directory order,
cohort mode in batch order; the cells themselves must be identical), and optionally checks each
family's verdict counts against a reference summary (run 7: results/cf_run7/<family>_summary.json).
Exit 1 on any difference; the JSON report names the first differing cells.
usage: cf_port_gate.py <expected_dir> <actual_dir> [--summaries <dir with <family>_summary.json>] [--report <path>]
"""
import gzip
import json
import sys
from collections import Counter
from pathlib import Path

FAMILIES = ("cfo", "buybacks", "dividends_paid")


def cells(d, fam):
    with gzip.open(Path(d) / f"{fam}_cells.jsonl.gz", "rt") as fh:
        return Counter(line.rstrip("\n") for line in fh)


def main(argv):
    exp, act = argv[0], argv[1]
    opts = dict(zip(argv[2::2], argv[3::2]))
    report, ok = {}, True
    for fam in FAMILIES:
        a, b = cells(exp, fam), cells(act, fam)
        only_exp, only_act = a - b, b - a
        r = {"expected_cells": sum(a.values()), "actual_cells": sum(b.values()),
             "only_expected": sum(only_exp.values()), "only_actual": sum(only_act.values()),
             "first_only_expected": [json.loads(x) for x in list(only_exp)[:3]],
             "first_only_actual": [json.loads(x) for x in list(only_act)[:3]]}
        if "--summaries" in opts:
            ref = json.load(open(Path(opts["--summaries"]) / f"{fam}_summary.json"))
            got = Counter(json.loads(x)["verdict"] for x in b.elements())
            r["summary_reference_cells"] = ref["cells"]
            r["summary_verdicts_equal"] = dict(got) == ref["verdicts"] and sum(got.values()) == ref["cells"]
            r["summary_verdict_diff"] = {k: [ref["verdicts"].get(k, 0), got.get(k, 0)]
                                         for k in set(ref["verdicts"]) | set(got) if ref["verdicts"].get(k, 0) != got.get(k, 0)}
            ok &= r["summary_verdicts_equal"]
        r["identical"] = not only_exp and not only_act
        ok &= r["identical"]
        report[fam] = r
        print(fam, "identical" if r["identical"] else "DIFFERS", r["expected_cells"], r["actual_cells"],
              ("verdicts=run7" if r.get("summary_verdicts_equal") else f"verdict diff {r.get('summary_verdict_diff')}") if "--summaries" in opts else "")
    if "--report" in opts:
        Path(opts["--report"]).write_text(json.dumps(report, indent=1) + "\n")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
