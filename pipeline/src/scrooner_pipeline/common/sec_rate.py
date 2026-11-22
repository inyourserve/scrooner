"""ONE SEC request budget for every caller on this machine: 2 requests per second in total (founder, 2026-11-17;
root CLAUDE.md hard rule), whatever a setting, an env override or a tool's own pacing says.

Stdlib only (no settings, no httpx), so the standalone data-team tools (instance_evidence.py, text_disclosure.py,
lease_instances.py, the exam fetchers) import it under the system python3 as well. Every SEC caller takes its limiter
from here: common.sec_client.SECClient, fsn_store.edgar_fetch.EdgarClient and the tools through
data-team/tags/line_map/tools/sec_pace.py. The budget is one flock-protected state file (common.rate_limiter), so N
processes share it; it is per machine, which is why a workflow that runs SEC fetchers on several runners at once
must lower each runner's rate so the runners together stay within the ceiling (onboard-company-filings.yml).

CLI (the agents' one door to sec.gov; replaces the scratchpad `secfetch` helper):
    PYTHONPATH=pipeline/src python3 -m scrooner_pipeline.common.sec_rate fetch URL OUTFILE
    python3 -I data-team/tags/line_map/tools/sec_pace.py fetch URL OUTFILE      (same, under an isolated python3)
sec.gov hosts only; waits on the shared budget; declared User-Agent from SEC_USER_AGENT or pipeline/.env; an OUTFILE
that already exists and is non-empty is never refetched.
"""

from __future__ import annotations

import gzip
import os
import sys
import tempfile
import urllib.request
from pathlib import Path

from scrooner_pipeline.common.rate_limiter import CrossProcessRateLimiter

SEC_RATE_CEILING = (
    2.0  # requests per second, in total, every process and tool on the machine
)

LOCK_PATH = (
    Path(os.environ.get("SCROONER_SEC_LOCK_PATH") or tempfile.gettempdir())
    / "scrooner_sec_rate_limiter.lock"
)


def limiter(
    max_per_second: float | None = None, lock_path: Path | None = None
) -> CrossProcessRateLimiter:
    """The shared limiter at `max_per_second` clamped to SEC_RATE_CEILING (None or anything higher = the ceiling)."""
    rate = SEC_RATE_CEILING if max_per_second is None else float(max_per_second)
    if rate <= 0:
        raise ValueError("SEC rate must be positive")
    return CrossProcessRateLimiter(min(rate, SEC_RATE_CEILING), lock_path or LOCK_PATH)


_shared: CrossProcessRateLimiter | None = None


def wait() -> None:
    """Block until the next request fits the budget. The entry point for callers without a client object."""
    global _shared
    if _shared is None:
        _shared = limiter()
    _shared.wait()


SEC_URL_PREFIXES = (
    "https://www.sec.gov/",
    "https://data.sec.gov/",
    "https://efts.sec.gov/",
)
_ENV_FILE = Path(__file__).resolve().parents[3] / ".env"  # pipeline/.env


def user_agent() -> str:
    """The declared SEC User-Agent (doc 07): SEC_USER_AGENT, else pipeline/.env. Never printed."""
    ua = os.environ.get("SEC_USER_AGENT")
    if ua:
        return ua
    if _ENV_FILE.exists():
        for line in _ENV_FILE.read_text().splitlines():
            if line.startswith("SEC_USER_AGENT="):
                ua = line.split("=", 1)[1].strip().strip('"').strip("'")
                if ua:
                    return ua
    raise SystemExit("SEC_USER_AGENT is not declared (environment or pipeline/.env)")


def fetch(url: str, timeout: float = 60) -> bytes:
    """GET one sec.gov URL through the shared budget, gzip-decoded. The stdlib fetch for tools without a client."""
    if not url.startswith(SEC_URL_PREFIXES):
        raise ValueError(f"sec.gov only: {url}")
    wait()
    req = urllib.request.Request(
        url, headers={"User-Agent": user_agent(), "Accept-Encoding": "gzip"}
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = resp.read()
        if resp.headers.get("Content-Encoding") == "gzip":
            data = gzip.decompress(data)
    return data


def fetch_to(url: str, out: Path) -> bool:
    """Fetch `url` into `out` unless `out` already holds it (never refetch). True when a request was made."""
    out = Path(out)
    if out.exists() and out.stat().st_size > 0:
        return False
    data = fetch(url)
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_name(out.name + ".part")
    tmp.write_bytes(data)
    tmp.replace(out)
    return True


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 3 or args[0] != "fetch":
        print("usage: sec_rate fetch URL OUTFILE", file=sys.stderr)
        return 2
    url, out = args[1], Path(args[2])
    try:
        fetched = fetch_to(url, out)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 2
    print(("fetched" if fetched else "cached"), out, out.stat().st_size)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
