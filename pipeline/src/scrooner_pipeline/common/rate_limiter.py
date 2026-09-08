"""Cross-process min-interval rate limiter via an flock-protected shared
state file.

Extracted 2026-09-06 from common/sec_client.py's own `_RateLimiter` (added
2026-08-29 after a real bug: an in-process `threading.Lock` limiter only
enforces "aggregate rate <= max_per_second" within ONE process -- a
full-population job run as N separate OS processes, each with its own
independent limiter, has a true aggregate rate of up to N x max_per_second.
Confirmed live for the SEC client at the time: 10 processes x 8 req/s = up
to ~80 req/s, 8x over SEC's own ceiling). Made shared/importable rather than
duplicated when `company_master/yfinance_industry.py` needed the exact same
coordination for a second, unrelated external API (Yahoo via yfinance) --
one canonical implementation, not two copies of the same fix.

`flock` (not a Postgres row or Redis) keeps this dependency-free per doc
02's "no Redis/Celery for MVP" lock -- every worker process runs on the same
machine, so a local advisory file lock is sufficient cross-process
coordination, no new infrastructure needed. `time.monotonic()` (via
`CLOCK_MONOTONIC`) is safe to compare across processes on the same machine
(it's a system-wide clock, not per-process) -- the one edge case (a stale
timestamp from before a reboot) only ever fails in the direction of
under-throttling for a single request, never over-throttling or crashing.
"""

import fcntl
import threading
import time
from pathlib import Path


class CrossProcessRateLimiter:
    def __init__(self, max_per_second: float, lock_path: Path):
        self._min_interval = 1.0 / max_per_second
        self._lock_path = lock_path
        self._lock_path.touch(exist_ok=True)
        # A same-process fast path still helps (avoids a syscall-heavy
        # flock round trip for the common single-process case) but is no
        # longer what makes this correct -- the file lock is.
        self._local_lock = threading.Lock()

    def wait(self) -> None:
        with self._local_lock:
            with open(self._lock_path, "r+") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    content = f.read().strip()
                    try:
                        last_request = float(content) if content else 0.0
                    except ValueError:
                        last_request = 0.0
                    now = time.monotonic()
                    elapsed = now - last_request
                    if elapsed < self._min_interval:
                        time.sleep(self._min_interval - elapsed)
                    f.seek(0)
                    f.truncate()
                    f.write(str(time.monotonic()))
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
