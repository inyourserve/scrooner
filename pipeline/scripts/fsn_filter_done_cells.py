"""Keep the cells the write may touch: passed data points of done companies (the same filter as
pipeline-fsn-write.yml's write step; note-sourced operating income is never written).

usage: fsn_filter_done_cells.py SRC.jsonl.gz DST.jsonl.gz DATA_POINTS DONE_COMPANIES.txt
"""

import gzip
import json
import sys

src, dst, allowed, done_path = sys.argv[1], sys.argv[2], set(sys.argv[3].split(",")), sys.argv[4]
done = {int(x) for x in open(done_path).read().split()}
rows = [json.loads(line) for line in gzip.open(src, "rt")]
keep = [
    r
    for r in rows
    if r["data_point_name"] in allowed
    and int(r["company_id"]) in done
    and not (r["data_point_name"] == "operating_income_resolved" and (r.get("input_refs") or {}).get("source") == "note")
]
with gzip.open(dst, "wt") as fh:
    for r in keep:
        fh.write(json.dumps(r) + "\n")
json.dump(
    {
        "family": src.split("/")[-2],
        "rule_id": "fsn.select@1",
        "rows": len(keep),
        "data_points": sorted({r["data_point_name"] for r in keep}),
        "period_floor": "2014-01-01",
    },
    open(dst.rsplit("/", 1)[0] + "/manifest.json", "w"),
)
print(f"{src}: {len(keep)} of {len(rows)} rows (passed data points, {len(done)} done companies)")
