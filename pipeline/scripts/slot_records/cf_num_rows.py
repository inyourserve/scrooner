"""Duration values for every cash-flow FACE tag of each cohort filing, from the
FSN num extracts (stdlib, run with -I; zstd CLI). Zero SEC requests.

Kept: rows of a filing whose tag is on that filing's own cash-flow face
(cf_face_rows.py output), qtrs 1-4, uom USD, consolidated registrant only
(empty coreg, iprx 0), undimensioned. Custom tags are kept too: FSN carries
them, companyfacts does not. Every term of a cell therefore comes from ONE
accession by construction (adsh).
usage: cf_num_rows.py <fsn_root> <cf_face_rows.jsonl.gz> <out.jsonl.gz>
"""
import csv
import glob
import gzip
import io
import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

csv.field_size_limit(sys.maxsize)
NO_DIM = "0x00000000"
root, face_path, out = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
face_tags = defaultdict(set)
with gzip.open(face_path, "rt") as fh:
    for line in fh:
        r = json.loads(line)
        if r["stmt"] == "CF":
            face_tags[r["adsh"]].add(r["tag"])
print(f"filings with a cash-flow face: {len(face_tags)}")
n = 0
with gzip.open(out, "wt") as fo:
    for num in sorted(glob.glob(str(root / "*" / "*_num.tsv.zst"))):
        proc = subprocess.Popen(["zstd", "-dc", num], stdout=subprocess.PIPE)
        rd = csv.DictReader(io.TextIOWrapper(proc.stdout, encoding="utf-8", errors="replace"), delimiter="\t", quoting=csv.QUOTE_NONE)
        k = 0
        for r in rd:
            tags = face_tags.get(r["adsh"])
            if not tags or r["tag"] not in tags or r["qtrs"] not in ("1", "2", "3", "4"):
                continue
            if r["uom"] != "USD" or r["value"] in ("", None) or r.get("dimh", NO_DIM) != NO_DIM:
                continue
            if (r.get("coreg") or "").strip() or (r.get("iprx") or "0") not in ("0", ""):
                continue
            fo.write(json.dumps({"adsh": r["adsh"], "tag": r["tag"], "ddate": r["ddate"], "qtrs": int(r["qtrs"]),
                                 "value": r["value"], "dcml": r.get("dcml"), "durp": r.get("durp")}) + "\n")
            k += 1
        n += k
        print(f"  {Path(num).parent.name}: {k} rows", flush=True)
print(f"cash-flow face values: {n} rows")
