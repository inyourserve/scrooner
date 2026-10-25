"""Fetch the calculation linkbase for boundary filings that lack one (stdlib).

For each 'cik adsh' line whose <out_dir>/<adsh>/ has no *_cal.xml and no
MetaLinks.json: read the filing folder index (one request), download the
*_cal.xml if listed, else MetaLinks.json (one request). sec.gov only; the
User-Agent is SEC_USER_AGENT from pipeline/.env; <= 4 requests/second; one
process; stops when free disk < 4 GB. Prints the request count at the end.
usage: fetch_boundary_cal.py <boundaries.txt> <out_dir> [limit]
"""
import json
import os
import shutil
import sys
import time
import urllib.request
from pathlib import Path

ENV = Path(__file__).resolve().parents[3] / ".env"
UA = None
for line in ENV.read_text().splitlines() if ENV.exists() else []:
    if line.startswith("SEC_USER_AGENT="):
        UA = line.split("=", 1)[1].strip().strip('"').strip("'")
UA = UA or os.environ.get("SEC_USER_AGENT")
if not UA:
    sys.exit("SEC_USER_AGENT missing (pipeline/.env)")

out = Path(sys.argv[2])
limit = int(sys.argv[3]) if len(sys.argv) > 3 else 10**9
requests = 0
last = 0.0


def get(url):
    global requests, last
    if shutil.disk_usage("/private/tmp").free < 4 * 1024**3:
        sys.exit(f"free disk < 4 GB after {requests} requests; stopping")
    wait = 0.26 - (time.monotonic() - last)
    if wait > 0:
        time.sleep(wait)
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Encoding": "gzip, deflate"})
    last = time.monotonic()
    requests += 1
    with urllib.request.urlopen(req, timeout=30) as r:
        data = r.read()
        if r.headers.get("Content-Encoding") == "gzip":
            import gzip
            data = gzip.decompress(data)
        return data


done = fetched = failed = 0
for line in open(sys.argv[1]):
    if done >= limit:
        break
    cik, adsh = line.split()
    d = out / adsh
    if list(d.glob("*_cal.xml")) or (d / "MetaLinks.json").exists():
        continue
    done += 1
    folder = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{adsh.replace('-', '')}/"
    try:
        idx = json.loads(get(folder + "index.json"))
        names = [i["name"] for i in idx["directory"]["item"]]
        target = next((n for n in names if n.endswith("_cal.xml")), None)
        if target is None and "MetaLinks.json" in names:
            target = "MetaLinks.json"
        if target is None:
            d.mkdir(parents=True, exist_ok=True)
            (d / "NO_CAL_IN_FOLDER").write_text("\n".join(names))
            failed += 1
            continue
        data = get(folder + target)
        d.mkdir(parents=True, exist_ok=True)
        (d / target).write_bytes(data)
        fetched += 1
    except Exception as e:  # noqa: BLE001
        failed += 1
        print("FAIL", adsh, type(e).__name__, str(e)[:80], flush=True)
print(f"attempted {done} fetched {fetched} failed {failed} requests {requests}")
