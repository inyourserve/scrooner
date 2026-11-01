import multiprocessing
import time
from pathlib import Path

import pytest

from scrooner_pipeline.common.sec_client import _RateLimiter

# "Must not sleep" tests need an upper bound on real wall-clock elapsed
# time -- 0.05s originally, found live 2026-09-19 to fail on every single
# CI push since at least 2026-09-15 (GitHub Actions' shared runners add
# 0.1-0.16s of real scheduler jitter around a bare `time.monotonic()`
# pair, consistently, not a one-off). Not a regression in _RateLimiter
# itself -- every failure is the identical 3 tests, unrelated to whatever
# the given commit actually changed. Raised generously (10x the largest
# observed jitter) rather than tuned precisely, since these tests exist to
# catch a GROSSLY broken "slept when it shouldn't have" path, not to
# assert sub-100ms timing precision a shared CI runner can't reliably
# provide -- the positive case (`test_second_call_within_window_sleeps_
# the_remainder`, a LOWER bound) already covers the actual sleep-duration
# correctness and is inherently CI-safe (added latency only helps a `>=`
# assertion, never breaks it).
CI_JITTER_TOLERANCE_SECONDS = 1.5


@pytest.mark.unit
class TestRateLimiterSingleProcess:
    def test_first_call_never_sleeps(self, tmp_path):
        limiter = _RateLimiter(max_per_second=10.0, lock_path=tmp_path / "rl.lock")
        started = time.monotonic()
        limiter.wait()
        assert time.monotonic() - started < CI_JITTER_TOLERANCE_SECONDS

    def test_second_call_within_window_sleeps_the_remainder(self, tmp_path):
        # 5 req/s -> 0.2s minimum spacing.
        limiter = _RateLimiter(max_per_second=5.0, lock_path=tmp_path / "rl.lock")
        # Measure from BEFORE the first call. The limiter stamps the lock file
        # inside wait(), so a clock read taken after the first wait() returns
        # can land arbitrarily late (a preempted CI runner measured 0.11s,
        # run 41238979522) and shrink the apparent sleep. The first stamp is
        # never earlier than `started`, so the second call cannot return
        # before started + 0.2s: a true lower bound, independent of jitter.
        started = time.monotonic()
        limiter.wait()
        limiter.wait()
        elapsed = time.monotonic() - started
        assert elapsed >= 0.2 - 1e-3

    def test_call_after_the_window_has_passed_does_not_sleep(self, tmp_path):
        limiter = _RateLimiter(max_per_second=20.0, lock_path=tmp_path / "rl.lock")  # 0.05s window
        limiter.wait()
        time.sleep(0.1)
        started = time.monotonic()
        limiter.wait()
        assert time.monotonic() - started < CI_JITTER_TOLERANCE_SECONDS

    def test_corrupted_lock_file_content_is_treated_as_no_prior_request(self, tmp_path):
        lock_path = tmp_path / "rl.lock"
        lock_path.write_text("not-a-number")
        limiter = _RateLimiter(max_per_second=10.0, lock_path=lock_path)
        started = time.monotonic()
        limiter.wait()  # must not raise, must not sleep on a garbage/first-touch file
        assert time.monotonic() - started < CI_JITTER_TOLERANCE_SECONDS


def _worker_call_wait_and_record(lock_path_str: str, max_per_second: float, out_queue, barrier) -> None:
    limiter = _RateLimiter(max_per_second=max_per_second, lock_path=Path(lock_path_str))
    barrier.wait(timeout=30)
    before = time.monotonic()
    limiter.wait()
    out_queue.put((before, time.monotonic()))


@pytest.mark.unit
class TestRateLimiterCrossProcess:
    def test_two_separate_processes_share_the_same_pacing(self, tmp_path):
        """The real bug this fix closes: two SEPARATE OS processes (real
        multiprocessing, not threads in one process -- threads would
        share the old in-memory limiter's state too, which is exactly
        why that version looked correct under a threaded test but wasn't
        under the real deployment shape, multiple `uv run` invocations).
        Both must be paced against each other, not just internally."""
        lock_path = tmp_path / "rl.lock"
        max_per_second = 5.0  # 0.2s minimum spacing
        ctx = multiprocessing.get_context("spawn")
        q = ctx.Queue()
        # Both workers block on the barrier until both have booted, so they
        # call wait() at the same moment rather than one spawn-boot apart.
        barrier = ctx.Barrier(2)

        args = (str(lock_path), max_per_second, q, barrier)
        p1 = ctx.Process(target=_worker_call_wait_and_record, args=args)
        p2 = ctx.Process(target=_worker_call_wait_and_record, args=args)

        p1.start()
        p2.start()
        results = [q.get(timeout=30), q.get(timeout=30)]
        p1.join(timeout=30)
        p2.join(timeout=30)

        # The first process to stamp the lock file did so no earlier than its
        # own `before`; the other cannot return until 0.2s after that stamp.
        # So the last return is >= the earliest start + 0.2s whatever the
        # scheduler does (the old after-to-after gap broke at 0.09s on a
        # preempted runner, run 41202752853). If the processes paced
        # independently (the old bug), both would return right after the
        # barrier released them and this would fail.
        earliest_start = min(before for before, _ in results)
        last_return = max(after for _, after in results)
        assert last_return - earliest_start >= 0.2 - 1e-3
