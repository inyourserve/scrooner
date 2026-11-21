"""ONE SEC request budget for every caller on this machine: 2 requests per second in total (founder, 2026-11-17;
root CLAUDE.md hard rule), whatever a setting, an env override or a tool's own pacing says.

Stdlib only (no settings, no httpx), so the standalone data-team tools (instance_evidence.py, text_disclosure.py,
lease_instances.py, the exam fetchers) import it under the system python3 as well. Every SEC caller takes its limiter
from here: common.sec_client.SECClient, fsn_store.edgar_fetch.EdgarClient and the tools through
data-team/tags/line_map/tools/sec_pace.py. The budget is one flock-protected state file (common.rate_limiter), so N
processes share it; it is per machine, which is why a workflow that runs SEC fetchers on several runners at once
must lower each runner's rate so the runners together stay within the ceiling (onboard-company-filings.yml).
"""

from __future__ import annotations

import os
import tempfile
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
