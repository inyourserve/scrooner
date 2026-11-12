"""Where each serving row's value comes from (founder decision 2026-11-12, via Dhairya): a standard-taxonomy tag is read
from core.fact (SEC companyfacts, value_source sec_api); a company extension tag, which companyfacts never carries, is read
from the filing's own XBRL in the FSN store (fsn.value: undimensioned, empty coreg, the latest accepted filing whose face
prints the tag for that period; value_source fsn_xbrl). One source per row, so never two sources within one cell.
Usage: value_source.py <tag_map.csv> <out.csv>"""
import csv
import sys

STD = {"us-gaap", "ifrs-full", "dei", "srt"}
SERVING = ("concept", "component", "combined")


def source(r):
    if r["decision"] not in SERVING:
        return ""
    return "sec_api" if r["taxonomy"] in STD else "fsn_xbrl"


if __name__ == "__main__":
    src, dst = sys.argv[1:3]
    rows = list(csv.DictReader(open(src)))
    cols = list(rows[0]) + ([] if "value_source" in rows[0] else ["value_source"])
    for r in rows:
        r["value_source"] = source(r)
    with open(dst, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    print("rows", len(rows), "| fsn_xbrl", sum(r["value_source"] == "fsn_xbrl" for r in rows), "| sec_api", sum(r["value_source"] == "sec_api" for r in rows))
