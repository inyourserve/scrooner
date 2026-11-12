"""Where each serving row's value comes from (founder decision 2026-11-12, via Dhairya): a standard-taxonomy tag is read
from core.fact (SEC companyfacts, value_source sec_api); a company extension tag, which companyfacts never carries, is read
from the filing's own XBRL in the FSN store (fsn.value: undimensioned, empty coreg, the latest accepted filing whose face
prints the tag for that period; value_source fsn_xbrl). One source per row, and one per component sum, so never two sources within one cell.
Usage: value_source.py <tag_map.csv> <out.csv>"""
import csv
import sys

STD = {"us-gaap", "ifrs-full", "dei", "srt"}
SERVING = ("concept", "component", "combined")


def source(r):
    if r["decision"] not in SERVING:
        return ""
    return "sec_api" if r["taxonomy"] in STD else "fsn_xbrl"


def day(d, n):
    import datetime
    return (datetime.date.fromisoformat(d) + datetime.timedelta(days=n)).isoformat()


def single_source_sums(rows):
    """A component sum is read from one source: where any part of a (company, parent) sum is fsn_xbrl, every part
    overlapping that part's era is read from fsn_xbrl too (the filing's own XBRL carries its us-gaap lines as well);
    a part is split at the window edges so it keeps sec_api outside them."""
    win = {}
    for r in rows:
        if r["decision"] == "component" and source(r) == "fsn_xbrl":
            win.setdefault((r["company_id"], r["parent_concept"]), []).append((r["era_from"], r["era_to"]))
    out = []
    for r in rows:
        w = win.get((r["company_id"], r["parent_concept"])) if r["decision"] == "component" and source(r) == "sec_api" else None
        hits = sorted((max(a, r["era_from"]), min(b, r["era_to"])) for a, b in (w or []) if not (b < r["era_from"] or r["era_to"] < a))
        if not hits:
            out.append({**r, "value_source": source(r)})
            continue
        cur = r["era_from"]
        for a, b in hits:
            if a > cur:
                out.append({**r, "era_from": cur, "era_to": day(a, -1), "value_source": "sec_api"})
            if b >= cur:
                out.append({**r, "era_from": max(a, cur), "era_to": b, "value_source": "fsn_xbrl"})
                cur = day(b, 1)
        if cur <= r["era_to"]:
            out.append({**r, "era_from": cur, "era_to": r["era_to"], "value_source": "sec_api"})
    return out


if __name__ == "__main__":
    src, dst = sys.argv[1:3]
    rows = list(csv.DictReader(open(src)))
    cols = list(rows[0]) + ([] if "value_source" in rows[0] else ["value_source"])
    rows = single_source_sums(rows)
    with open(dst, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    print("rows", len(rows), "| fsn_xbrl", sum(r["value_source"] == "fsn_xbrl" for r in rows), "| sec_api", sum(r["value_source"] == "sec_api" for r in rows))
