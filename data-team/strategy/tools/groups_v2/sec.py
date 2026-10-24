"""Tiny SEC fetcher for the Sector Analyst reader. One process, shared flock limiter (same lock file as common/sec_client.py),
4 requests per second (cap agreed: 5 combined), declared SEC_USER_AGENT read from the environment or pipeline/.env (never printed).
Responses are cached on local disk outside the repo (CACHE) and count as a request only on a miss."""
import hashlib, importlib.util, os, tempfile, time, urllib.request, urllib.error, gzip, json
from pathlib import Path

CACHE = Path(os.environ.get("SA_CACHE", "/private/tmp/claude-501/-Users-vikash-scrooner/b256f7de-d50a-4757-b526-8e0954fad6db/scratchpad/w/cache"))
CACHE.mkdir(parents=True, exist_ok=True)
_spec = importlib.util.spec_from_file_location("rl", "/Users/vikash/scrooner/pipeline/src/scrooner_pipeline/common/rate_limiter.py")
_rl = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_rl)
LIM = _rl.CrossProcessRateLimiter(4.0, Path(tempfile.gettempdir()) / "scrooner_sec_rate_limiter.lock")
COUNT = {"requests": 0, "cache_hits": 0, "errors": 0}


def _ua() -> str:
    ua = os.environ.get("SEC_USER_AGENT")
    if ua:
        return ua
    for line in open("/Users/vikash/scrooner/pipeline/.env"):
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
            LIM.wait()
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
