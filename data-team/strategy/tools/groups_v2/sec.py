"""Tiny SEC fetcher for the Sector Analyst reader. Every request waits on the ONE machine-wide SEC budget
(pipeline/src/scrooner_pipeline/common/sec_rate.py: 2 requests per second in total), declared SEC_USER_AGENT read from the environment or pipeline/.env (never printed).
Responses are cached on local disk outside the repo (CACHE) and count as a request only on a miss."""
import hashlib, os, sys, time, urllib.request, urllib.error, gzip, json
from pathlib import Path

CACHE = Path(os.environ.get("SA_CACHE", "/private/tmp/claude-501/-Users-vikash-scrooner/b256f7de-d50a-4757-b526-8e0954fad6db/scratchpad/w/cache"))
CACHE.mkdir(parents=True, exist_ok=True)
_REPO = Path(__file__).resolve().parents[4]
if str(_REPO / "pipeline" / "src") not in sys.path:
    sys.path.insert(0, str(_REPO / "pipeline" / "src"))
from scrooner_pipeline.common import sec_rate  # noqa: E402
COUNT = {"requests": 0, "cache_hits": 0, "errors": 0}


def _ua() -> str:
    ua = os.environ.get("SEC_USER_AGENT")
    if ua:
        return ua
    for line in open(_REPO / "pipeline" / ".env"):
        if line.startswith("SEC_USER_AGENT="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise RuntimeError("SEC_USER_AGENT not declared")


UA = _ua()


def get(url: str, binary: bool = False):
    key = CACHE / hashlib.sha1(url.encode()).hexdigest()
    if key.exists():
        COUNT["cache_hits"] += 1
        b = key.read_bytes()
    else:
        for attempt in range(4):
            sec_rate.wait()
            COUNT["requests"] += 1
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Encoding": "gzip"})
            try:
                with urllib.request.urlopen(req, timeout=40) as r:
                    b = r.read()
                    if r.headers.get("Content-Encoding") == "gzip":
                        b = gzip.decompress(b)
                break
            except urllib.error.HTTPError as e:
                COUNT["errors"] += 1
                if e.code in (404, 403):
                    return None
                time.sleep(2 * (attempt + 1))
            except Exception:
                COUNT["errors"] += 1
                time.sleep(2 * (attempt + 1))
        else:
            return None
        key.write_bytes(b)
    return b if binary else b.decode("utf-8", "replace")


def get_json(url: str):
    t = get(url)
    return json.loads(t) if t else None
