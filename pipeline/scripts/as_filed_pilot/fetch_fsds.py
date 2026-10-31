"""Download one FSDS quarter zip through the shared limiter (<=4 req/s). usage: fetch_fsds.py 2018q4 destdir"""
import os, sys, tempfile, time
from pathlib import Path
sys.path.insert(0, sys.argv[3])  # worktree pipeline/src
from scrooner_pipeline.common.rate_limiter import CrossProcessRateLimiter
import httpx
q, dest = sys.argv[1], Path(sys.argv[2])
lim = CrossProcessRateLimiter(4.0, Path(tempfile.gettempdir()) / "scrooner_sec_rate_limiter.lock")
url = f"https://www.sec.gov/files/dera/data/financial-statement-data-sets/{q}.zip"
t = time.time()
with httpx.Client(headers={"User-Agent": os.environ["SEC_UA"], "Accept-Encoding": "gzip, deflate"}, timeout=httpx.Timeout(30, read=180)) as c:
    lim.wait()
    with c.stream("GET", url) as r:
        r.raise_for_status()
        with open(dest / f"{q}.zip", "wb") as f:
            for ch in r.iter_bytes(1 << 20): f.write(ch)
print(q, (dest / f"{q}.zip").stat().st_size, round(time.time() - t, 1), "s")
