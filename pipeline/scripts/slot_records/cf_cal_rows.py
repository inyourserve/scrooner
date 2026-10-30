"""Cash-flow calc arcs for each cohort filing from the FSN cal extracts
(stdlib, run with -I; zstd CLI), one period file at a time so memory stays
flat. The cash-flow group is chosen by common.fsn_cal_arcs's element rule
(the group whose parents include the operating-activities total).
usage: cf_cal_rows.py <fsn_root> <cf_face_rows.jsonl.gz> <out.jsonl.gz>
"""
import glob
import gzip
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import common  # noqa: E402

root, face_path, out = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
by_period = {}
with gzip.open(face_path, "rt") as fh:
    for line in fh:
        r = json.loads(line)
        by_period.setdefault(r["fsn"], set()).add(r["adsh"])
n = 0
with gzip.open(out, "wt") as fo:
    for cal in sorted(glob.glob(str(root / "*" / "*_cal.tsv.zst"))):
        period = Path(cal).parent.name
        k = 0
        for adsh in sorted(by_period.get(period, ())):
            arcs = common.fsn_cal_arcs(cal, adsh)
            cf = {p: [[c, w] for c, w, _cu in kids] for (role, p), kids in arcs.items() if role.startswith("CashFlow#")}
            fo.write(json.dumps({"adsh": adsh, "arcs": cf}) + "\n")
            k += bool(cf)
        common._FSN_CAL_CACHE.clear()  # one period in memory at a time
        n += k
        print(f"  {period}: {k} of {len(by_period.get(period, ()))} filings with a cash-flow calc group", flush=True)
print(f"filings with cash-flow arcs: {n}")
