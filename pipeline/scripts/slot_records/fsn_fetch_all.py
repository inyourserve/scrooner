"""Full SEC Financial Statement and Notes download, quarter by quarter, READY
BUT NOT TO BE RUN until Dhairya relays the founder's decision on THE-PLAN 7.3.

Per quarter (from results/fsn_quarter_links.txt): HEAD (size, ranges) ->
proceed only if free disk after download stays above the floor -> GET,
sha256 -> extract cohort rows of every table with fsn_pilot's logic -> keep
the zip only while free disk stays above the floor, else delete it (the
manifest records URL + sha256 so a refetch is one request) -> append to
results/fsn_manifest_all.jsonl. sec.gov only, SEC_USER_AGENT, <= 4 req/s;
stops at the request budget given on the command line and asks.
usage: fsn_fetch_all.py <quarter_links.txt> <cohort_ciks.txt> <out_root> <max_requests> [first_quarter] [last_quarter]
"""
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).parent
links_path, cohort, out_root, max_requests = sys.argv[1], sys.argv[2], Path(sys.argv[3]), int(sys.argv[4])
first = sys.argv[5] if len(sys.argv) > 5 else "0000q0"
last = sys.argv[6] if len(sys.argv) > 6 else "9999q9"
out_root.mkdir(parents=True, exist_ok=True)
manifest_all = out_root / "fsn_manifest_all.jsonl"
done = set()
if manifest_all.exists():
    for line in open(manifest_all):
        done.add(json.loads(line)["quarter"])
quarters = [l.split()[0] for l in open(links_path) if l.strip()]
requests_used = 0
t0 = time.monotonic()
for q in quarters:
    if q in done or not (first <= q <= last):
        continue
    if requests_used + 2 > max_requests:
        print(f"request budget {max_requests} reached before {q}; stopping and asking")
        break
    qdir = out_root / q
    r = subprocess.run([sys.executable, "-I", str(HERE / "fsn_pilot.py"), q, cohort, str(qdir)], capture_output=True, text=True)
    requests_used += 2  # HEAD + GET
    tail = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr.strip()[-300:]
    man = qdir / f"{q}_manifest.json"
    if r.returncode != 0 or not man.exists():
        print(f"{q}: FAILED ({tail})")
        with open(manifest_all, "a") as f:
            f.write(json.dumps({"quarter": q, "status": "failed", "detail": tail}) + "\n")
        if "conditions not met" in tail:
            print("disk or size condition failed; stopping")
            break
        continue
    # store in Supabase (founder 2026-10-26): extracts + zip to the private bucket, local zip removed
    up = subprocess.run([sys.executable, "-I", str(HERE / "fsn_upload.py"), str(qdir)], capture_output=True, text=True)
    if up.returncode != 0:
        print(f"{q}: extracted but UPLOAD FAILED ({(up.stdout + up.stderr).strip()[-300:]}); stopping and asking")
        break
    m = json.load(open(man))
    m["status"] = "ok"
    with open(manifest_all, "a") as f:
        f.write(json.dumps(m) + "\n")
    print(f"{q}: ok, zip {m['zip_bytes']/1e6:.0f} MB, extracts {m['extract_bytes_total']/1e6:.0f} MB, zip kept={m['zip_kept']}, optional skipped={m.get('optional_tables_skipped')}  [{requests_used} requests, {time.monotonic()-t0:.0f}s]")
    if m.get("optional_tables_skipped"):
        print("free disk below 3.5 GB: optional tables skipped; stopping after this quarter's manifest (Dhairya rule) and asking")
        break
print(f"done; requests used {requests_used}")
