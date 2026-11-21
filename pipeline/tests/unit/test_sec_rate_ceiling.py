"""The SEC rate never exceeds the 2 req/s hard rule (root CLAUDE.md; founder 2026-11-17), whatever the configured
value, and every client takes the ONE machine-wide limiter (common/sec_rate.py: one ceiling, one lock file)."""

import pytest

from scrooner_pipeline.common import config, sec_client, sec_rate
from scrooner_pipeline.fsn_store import edgar_fetch


def test_default_sec_rate_is_within_the_rule():
    assert sec_rate.SEC_RATE_CEILING == 2.0
    assert (
        config.Settings.model_fields["sec_max_requests_per_second"].default
        <= sec_rate.SEC_RATE_CEILING
    )


def test_shared_limiter_clamps_to_the_ceiling_and_uses_one_lock(tmp_path):
    lock = tmp_path / "sec.lock"
    assert sec_rate.limiter(9, lock)._min_interval == 0.5
    assert sec_rate.limiter(None, lock)._min_interval == 0.5
    assert (
        sec_rate.limiter(1, lock)._min_interval == 1.0
    )  # lowering is allowed (multi-runner workflows)
    with pytest.raises(ValueError):
        sec_rate.limiter(0, lock)
    assert sec_rate.limiter(9, lock)._lock_path == lock
    assert sec_rate.limiter(9)._lock_path == sec_rate.LOCK_PATH


def test_client_clamps_a_higher_configured_rate(monkeypatch):
    monkeypatch.setattr(sec_client.settings, "sec_max_requests_per_second", 8.0)
    seen = {}

    class Spy:
        def __init__(self, rate, *a, **k):
            seen["rate"] = rate

    monkeypatch.setattr(sec_client, "_RateLimiter", Spy)
    sec_client.SECClient()
    assert seen["rate"] <= sec_client.SEC_RATE_CEILING == 2.0


def test_sec_client_and_edgar_client_share_the_machine_budget(monkeypatch):
    monkeypatch.setattr(sec_client.settings, "sec_max_requests_per_second", 8.0)
    monkeypatch.setattr(
        sec_client.settings, "sec_user_agent", "Scrooner test test@example.com"
    )
    monkeypatch.delenv("SCROONER_EDGAR_MAX_RPS", raising=False)
    a = sec_client.SECClient()
    b = edgar_fetch.EdgarClient("Scrooner test test@example.com")
    try:
        assert a._rate_limiter._min_interval == b._limiter._min_interval == 0.5
        assert a._rate_limiter._lock_path == b._limiter._lock_path == sec_rate.LOCK_PATH
    finally:
        a.close()
        b.close()


def test_module_level_wait_uses_the_shared_limiter(monkeypatch):
    calls = []

    class Fake:
        def wait(self):
            calls.append(1)

    monkeypatch.setattr(sec_rate, "_shared", Fake())
    sec_rate.wait()
    sec_rate.wait()
    assert calls == [1, 1]
