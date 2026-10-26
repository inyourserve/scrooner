"""SEC Financial Statement and Notes data set: ONE-quarter pilot (Dhairya,
2026-10-25, with the founder's amendment: keep the zip, extract everything).

1. HEAD the zip (size, ranges); proceed only if size < 1.5 GB and free disk
   after download stays above 3 GB. 2. Stream the zip to the scratch folder
   (one GET), record sha256 + URL + size in a manifest. 3. Extract the cohort
   rows (sub.adsh where sub.cik is in the cohort) of EVERY table in the zip
   into compressed files (zstd if available, else xz); tables without an adsh
   column (tag, dim) are kept whole. 4. Keep the zip unless free disk would
   drop below 3 GB. sec.gov only, SEC_USER_AGENT, <= 4 req/s.
usage: fsn_pilot.py <quarter e.g. 2024q4> <cohort_ciks.txt> <out_dir>
"""
import csv
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request
import zipfile
from pathlib import Path

quarter, cohort_path, out = sys.argv[1], sys.argv[2], Path(sys.argv[3])
out.mkdir(parents=True, exist_ok=True)
UA = os.environ["SEC_USER_AGENT"]
# a 4th argument is an explicit zip URL (the SEC publishes recent periods as MONTHLY files,
# e.g. 2026_09_notes.zip, and consolidates them into quarterly files later)
url = sys.argv[4] if len(sys.argv) > 4 else f"https://www.sec.gov/files/dera/data/financial-statement-notes-data-sets/{quarter}_notes.zip"
cohort = {int(l.strip()) for l in open(cohort_path) if l.strip()}
GB = 1024**3


def head(u):
    r = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": UA}, method="HEAD"), timeout=60)
    return int(r.headers.get("Content-Length", "0")), r.headers.get("Accept-Ranges")


size, ranges = head(url)
free = shutil.disk_usage(str(out)).free
print(f"{quarter}: size {size/1e6:.1f} MB, Accept-Ranges={ranges}, free {free/GB:.2f} GB")
if size > 1.5e9 or free - size < 3 * GB:
    sys.exit("conditions not met (size >= 1.5 GB or free disk after download < 3 GB); stopping")
zpath = out / f"{quarter}_notes.zip"
t0 = time.monotonic()
sha = hashlib.sha256()
with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=600) as r, open(zpath, "wb") as f:
    while True:
        chunk = r.read(1 << 20)
        if not chunk:
            break
        sha.update(chunk)
        f.write(chunk)
print(f"downloaded in {time.monotonic()-t0:.0f}s, sha256 {sha.hexdigest()[:16]}... (2 requests: HEAD + GET)")

compressor = "zstd" if shutil.which("zstd") else ("xz" if shutil.which("xz") else None)


def write_compressed(name, lines_iter):
    ext = {"zstd": ".zst", "xz": ".xz", None: ""}[compressor]
    p = out / f"{quarter}_{name}.tsv{ext}"
    if compressor:
        proc = subprocess.Popen([compressor, "-q", "-T0" if compressor == "zstd" else "-T0", "-o", str(p), "-f"] if compressor == "zstd" else [compressor, "-T0", "-c"], stdin=subprocess.PIPE, stdout=open(p, "wb") if compressor == "xz" else subprocess.DEVNULL)
        n = 0
        for line in lines_iter:
            proc.stdin.write(line)
            n += 1
        proc.stdin.close()
        proc.wait()
    else:
        n = 0
        with open(p, "wb") as f:
            for line in lines_iter:
                f.write(line)
                n += 1
    return p, n


manifest = {"quarter": quarter, "url": url, "zip_sha256": sha.hexdigest(), "zip_bytes": size, "compressor": compressor, "tables": {}}
with zipfile.ZipFile(zpath) as z:
    names = z.namelist()
    print("members:", names)
    # cohort accessions from sub
    sub_name = next(n for n in names if n.lower().endswith("sub.tsv"))
    adshs = set()
    with z.open(sub_name) as fh:
        rd = csv.DictReader(io.TextIOWrapper(fh, encoding="utf-8", errors="replace"), delimiter="\t")
        for row in rd:
            try:
                if int(row["cik"]) in cohort:
                    adshs.add(row["adsh"])
            except (KeyError, ValueError):
                continue
    print(f"cohort filings in {quarter}: {len(adshs)}")
    MANDATORY = {"sub", "cal", "pre", "num"}  # kept locally always (Dhairya 2026-10-26)
    OPTIONAL_FLOOR = 3.5 * GB                 # txt/dim/ren/tag only while free disk stays above this
    manifest["optional_tables_skipped"] = []
    for n in names:
        if not n.lower().endswith(".tsv"):
            continue
        table = Path(n).stem.lower()
        info = z.getinfo(n)
        if table not in MANDATORY and shutil.disk_usage(str(out)).free < OPTIONAL_FLOOR:
            manifest["optional_tables_skipped"].append(table)
            print(f"  {table:5} skipped: free disk below 3.5 GB")
            continue
        with z.open(n) as fh:
            first = fh.readline()
            cols = first.decode("utf-8", "replace").rstrip("\n").split("\t")
            has_adsh = "adsh" in cols
            idx = cols.index("adsh") if has_adsh else None

            def gen(fh=fh, first=first, idx=idx, has_adsh=has_adsh):
                yield first
                for line in fh:
                    if not has_adsh:
                        yield line
                        continue
                    parts = line.split(b"\t", idx + 1)
                    if len(parts) > idx and parts[idx].decode("ascii", "ignore") in adshs:
                        yield line
            p, nrows = write_compressed(table, gen())
        manifest["tables"][table] = {"source_member": n, "source_bytes": info.file_size, "rows_kept": nrows - 1,
                                     "filtered_by_adsh": has_adsh, "columns": cols, "out": p.name, "out_bytes": p.stat().st_size}
        print(f"  {table:5} source {info.file_size/1e6:8.1f} MB -> kept {nrows-1:9d} rows, {p.stat().st_size/1e6:6.1f} MB ({'cohort rows' if has_adsh else 'whole table'})")
total_out = sum(t["out_bytes"] for t in manifest["tables"].values())
manifest["extract_bytes_total"] = total_out
free_after = shutil.disk_usage(str(out)).free
manifest["zip_kept"] = free_after > 3 * GB
if not manifest["zip_kept"]:
    zpath.unlink()
json.dump(manifest, open(out / f"{quarter}_manifest.json", "w"), indent=1)
print(f"extracts total {total_out/1e6:.1f} MB ({total_out/size*100:.1f}% of the zip); zip kept: {manifest['zip_kept']}; free {free_after/GB:.2f} GB")
