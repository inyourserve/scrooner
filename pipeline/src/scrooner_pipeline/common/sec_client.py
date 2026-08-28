import time
import threading
from datetime import date
from pathlib import Path

import httpx
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

from scrooner_pipeline.collector.retry import HTTP_RETRY
from scrooner_pipeline.common.config import settings

logger = structlog.get_logger()


class _RateLimiter:
    """Simple min-interval limiter. A solo sequential Collector doesn't need
    a real token bucket — doc 07 just requires not exceeding a request rate,
    and spacing requests evenly is the simplest thing that guarantees that."""

    def __init__(self, max_per_second: float):
        self._min_interval = 1.0 / max_per_second
        self._lock = threading.Lock()
        self._last_request = 0.0

    def wait(self) -> None:
        with self._lock:
            now = time.monotonic()
            elapsed = now - self._last_request
            if elapsed < self._min_interval:
                time.sleep(self._min_interval - elapsed)
            self._last_request = time.monotonic()


class SECClient:
    """Fetches from www.sec.gov / data.sec.gov per doc 07's access rules:
    declared User-Agent on every request, aggregate rate capped at
    settings.sec_max_requests_per_second (doc 02's buffer under SEC's 10/s
    ceiling), retry-with-backoff on 429/5xx rather than failing immediately.
    The retry predicate itself (`HTTP_RETRY`) lives in collector/retry.py --
    doc 06 module 9 -- so this client and storage.py share one definition of
    "transient" instead of each keeping their own copy.
    """

    def __init__(self) -> None:
        self._rate_limiter = _RateLimiter(settings.sec_max_requests_per_second)
        self._client = httpx.Client(
            headers={
                "User-Agent": settings.sec_user_agent,
                "Accept-Encoding": "gzip, deflate",
            },
            timeout=30.0,
        )

    @retry(
        retry=HTTP_RETRY,
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=1, max=30),
        reraise=True,
    )
    def get(self, url: str) -> httpx.Response:
        self._rate_limiter.wait()
        response = self._client.get(url)
        response.raise_for_status()
        return response

    def get_json(self, url: str) -> dict:
        return self.get(url).json()

    @retry(
        retry=HTTP_RETRY,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=2, max=30),
        reraise=True,
        before_sleep=lambda retry_state: logger.warning(
            "bulk_zip.download_retry",
            attempt=retry_state.attempt_number,
            exception=repr(retry_state.outcome.exception()) if retry_state.outcome else None,
            note="partial download discarded, retrying from byte 0 -- see download_to_file docstring",
        ),
    )
    def download_to_file(self, url: str, dest_path: Path) -> None:
        """Streams a response straight to disk in chunks, never buffering
        the whole body in memory — needed for doc 07 §5's bulk archives
        (companyfacts.zip / submissions.zip are ~1.4-1.5GB each as of
        2026-08-14). This is one request against the rate limiter, not one
        per chunk. A failed/partial download is discarded and retried from
        scratch on the next attempt within this same process (capped at 3
        attempts rather than the usual 5, since retrying a multi-GB
        transfer is expensive) -- byte-range resumption of a partial
        download is deliberately out of scope (see
        doc/learnings/day-04-retry-and-resume.md): Day 4's checkpoint/resume
        requirement is about not double-storing a company already
        successfully recorded in Postgres/Storage across a kill-and-rerun,
        not about resuming a half-downloaded zip byte-for-byte. Re-fetching
        the whole zip on a killed-mid-download rerun is bandwidth cost, not
        a duplicate-row/duplicate-object correctness problem.
        """
        self._rate_limiter.wait()
        with self._client.stream(
            "GET", url, timeout=httpx.Timeout(30.0, read=120.0)
        ) as response:
            response.raise_for_status()
            with open(dest_path, "wb") as f:
                for chunk in response.iter_bytes(chunk_size=1024 * 1024):
                    f.write(chunk)

    def get_cached_bulk_zip(self, url: str, cache_name: str) -> Path:
        """Like download_to_file, but reuses a local copy from earlier today
        instead of always re-downloading. SEC recompiles companyfacts.zip/
        submissions.zip nightly (doc 07 §5), so "today's" copy is exactly as
        fresh as a brand-new download within the same day. This is what
        makes a kill-and-resume test (and repeated small-scope test runs)
        cheap instead of re-paying the full ~1.4GB transfer every time --
        see doc/learnings/day-04-retry-and-resume.md.

        Deliberately date-keyed, not run-keyed or content-hash-keyed: doc 08
        already ties a *checkpoint* resume to (job, params_key), which reuses
        the same fetched_at regardless of this cache. This cache is purely a
        bandwidth optimization underneath that -- correctness never depends
        on a cache hit vs. miss, only speed does.
        """
        cache_dir = settings.bulk_zip_cache_dir
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_path = cache_dir / f"{cache_name}-{date.today().isoformat()}.zip"

        if cache_path.exists():
            logger.info("bulk_zip.cache_hit", path=str(cache_path), size_bytes=cache_path.stat().st_size)
            return cache_path

        tmp_path = cache_path.with_suffix(".zip.tmp")
        logger.info("bulk_zip.cache_miss", url=url, cache_path=str(cache_path))
        self.download_to_file(url, tmp_path)
        tmp_path.rename(cache_path)  # atomic on the same filesystem -- no torn/partial cache entries
        self._prune_stale_cache(cache_dir, cache_name, keep=cache_path)
        return cache_path

    def _prune_stale_cache(self, cache_dir: Path, cache_name: str, keep: Path) -> None:
        """Delete previous days' copies of this same bulk file. Each one is
        1-1.5GB and otherwise accumulates forever (found live 2026-08-23: a
        multi-day session filled a 228GB disk down to 206MB free, taking
        every shard of a running job down with `OSError: No space left on
        device`). Safe to delete unconditionally -- these are pure bandwidth
        cache, re-fetchable from SEC any time, never a source of truth."""
        for stale in cache_dir.glob(f"{cache_name}-*.zip"):
            if stale != keep:
                stale.unlink()
                logger.info("bulk_zip.pruned_stale", path=str(stale))

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "SECClient":
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()
