"""Custom-tag (and any wanted tag) instant values from the LOCAL FSN num
extracts, in the instance reader's evidence shape, so slot cells held as
needs_instance_reader fill with zero SEC requests.

num.tsv columns: adsh, tag, version, ddate, qtrs, uom, dimh, iprx, value, ...
Kept: qtrs = 0 (instant), uom = USD, undimensioned (dimh of the no-dimension
context) and, for the mezzanine tags, single-axis dimensioned rows too (the
replay groups them per axis). Same accession by construction (adsh).
usage: fsn_num_evidence.py <fsn_root> <records.jsonl ...> -o <out.jsonl>
"""
import csv
import glob
import io
import json
import subprocess
import sys
from pathlib import Path

csv.field_size_limit(sys.maxsize)  # num.tsv footnotes exceed the default 128 KB field limit
args = sys.argv[1:]
out = Path(args[args.index("-o") + 1])
root = Path(args[0])
record_files = [a for a in args[1:args.index("-o")]]
wanted_custom, wanted_mezz = set(), set()
for rf in record_files:
    for line in open(rf):
        r = json.loads(line)
        for m in r.get("total_liabilities_members", []):
            if m.get("custom"):
                wanted_custom.add(m["tag"])
        for m in r.get("mezzanine_face", []):
            wanted_mezz.add(m["tag"])
        wanted_mezz.update(r.get("mezzanine_dim_tags") or [])
wanted = wanted_custom | wanted_mezz
print(f"wanted tags: {len(wanted_custom)} custom members + {len(wanted_mezz)} mezzanine")
NO_DIM = "0x00000000"


def load_dim_segments(quarter, need):
    """dimhash -> segments for the wanted hashes, from the private bucket (SUPABASE_URL +
    SUPABASE_SERVICE_ROLE_KEY from the environment; run with the pipeline venv python for certifi)."""
    import os
    import ssl
    import urllib.request
    try:
        import certifi
        ctx = ssl.create_default_context(cafile=certifi.where())
    except Exception:  # noqa: BLE001
        ctx = None
    key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    req = urllib.request.Request(os.environ["SUPABASE_URL"].rstrip("/") + f"/storage/v1/object/fsn-notes/{quarter}/{quarter}_dim.tsv.zst",
                                 headers={"Authorization": "Bearer " + key, "apikey": key})
    data = urllib.request.urlopen(req, context=ctx, timeout=600).read()
    txt = subprocess.run(["zstd", "-dc"], input=data, capture_output=True).stdout.decode("utf-8", "replace")
    out_ = {}
    for line in txt.split("\n")[1:]:
        parts = line.split("\t")
        if len(parts) >= 2 and parts[0] in need:
            out_[parts[0]] = parts[1]
    return out_
n = 0
with open(out, "w") as fo:
    for num in sorted(glob.glob(str(root / "20*" / "*_num.tsv.zst"))):
        proc = subprocess.Popen(["zstd", "-dc", num], stdout=subprocess.PIPE)
        rd = csv.DictReader(io.TextIOWrapper(proc.stdout, encoding="utf-8", errors="replace"), delimiter="\t")
        k = 0
        rows_q = []
        for r in rd:
            if r["tag"] not in wanted or r["qtrs"] != "0" or r["uom"] != "USD" or r["value"] in ("", None):
                continue
            # consolidated registrant only: a co-registrant (subsidiary) value or a
            # non-primary duplicate (iprx != 0) is not the face value of the filer
            if (r.get("coreg") or "").strip() or (r.get("iprx") or "0") not in ("0", ""):
                continue
            undim = r["dimh"] == NO_DIM
            if not undim and r["tag"] not in wanted_mezz:
                continue
            d = r["ddate"]
            rows_q.append((undim, r, d))
            continue
            fo.write(json.dumps({"cik": None, "adsh": r["adsh"], "tag": r["tag"], "period_type": "instant",
                                 "end": f"{d[:4]}-{d[4:6]}-{d[6:]}", "value": r["value"], "unit": "USD",
                                 "decimals": None, "dims": "" if undim else f"dimh={r['dimh']}",
                                 "source": "fsn_num", "custom": r["version"].split("/")[0] not in ("us-gaap", "srt", "dei")}) + "\n")
            k += 1
        # dimensioned rows: the dimension hash resolves through the quarter's dim extract
        # (bucket fsn-notes, <q>/<q>_dim.tsv.zst, downloaded to memory, nothing kept) to
        # "Axis=Member"; only single-axis rows are kept (the replay groups members per axis)
        need = {r["dimh"] for u, r, _ in rows_q if not u}
        segs = {}
        if need:
            segs = load_dim_segments(Path(num).parent.name, need)
        for undim, r, d in rows_q:
            if undim:
                dims = ""
            else:
                sg = [x for x in segs.get(r["dimh"], "").split(";") if x]
                if len(sg) != 1 or "=" not in sg[0]:
                    continue
                dims = sg[0]
                if dims.startswith("ClassOfStock="):
                    dims = "StatementClassOfStockAxis=" + dims.split("=", 1)[1]  # FSN drops the namespace and 'Axis' suffix
            fo.write(json.dumps({"cik": None, "adsh": r["adsh"], "tag": r["tag"], "period_type": "instant",
                                 "end": f"{d[:4]}-{d[4:6]}-{d[6:]}", "value": r["value"], "unit": "USD",
                                 "decimals": None, "dims": dims,
                                 "source": "fsn_num", "custom": r["version"].split("/")[0] not in ("us-gaap", "srt", "dei")}) + "\n")
            k += 1
        n += k
        print(f"  {Path(num).parent.name}: {k} rows")
print(f"evidence rows {n} -> {out}")
