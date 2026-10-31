"""Fetch (through the shared limiter, <=4 req/s) a filing's EDGAR folder index and the named file suffixes. 
usage: fetch_filing_files.py <cik> <adsh> <destdir> <src> <suffix,suffix...>   (e.g. _cal.xml,_htm.xml)"""
import os, sys, tempfile, json
from pathlib import Path
sys.path.insert(0, sys.argv[4])
from scrooner_pipeline.common.rate_limiter import CrossProcessRateLimiter
import httpx
cik, adsh, dest, suffixes = sys.argv[1], sys.argv[2], Path(sys.argv[3]), sys.argv[5].split(",")
lim = CrossProcessRateLimiter(4.0, Path(tempfile.gettempdir()) / "scrooner_sec_rate_limiter.lock")
base = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{adsh.replace('-', '')}/"
n = 0
with httpx.Client(headers={"User-Agent": os.environ["SEC_UA"], "Accept-Encoding": "gzip, deflate"}, timeout=httpx.Timeout(30, read=180)) as c:
    lim.wait(); n += 1
    idx = c.get(base + "index.json"); idx.raise_for_status()
    names = [i["name"] for i in idx.json()["directory"]["item"]]
    for suf in suffixes:
        for nm in names:
            if nm.endswith(suf):
                lim.wait(); n += 1
                with c.stream("GET", base + nm) as r:
                    r.raise_for_status()
                    with open(dest / nm, "wb") as f:
                        for ch in r.iter_bytes(1 << 20): f.write(ch)
                print("got", nm, (dest / nm).stat().st_size)
print("requests", n)
