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


class _Resp:
    def __init__(self, body: bytes, headers: dict | None = None):
        self._body, self.headers = body, headers or {}

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _offline(monkeypatch, body=b"<html/>"):
    """No network: urlopen returns `body`; every wait() is counted; the UA is declared."""
    calls, seen = [], []
    monkeypatch.setattr(sec_rate, "wait", lambda: calls.append(1))
    monkeypatch.setenv("SEC_USER_AGENT", "Scrooner test test@example.com")

    def fake_urlopen(req, timeout=0):
        seen.append(req)
        return _Resp(body)

    monkeypatch.setattr(sec_rate.urllib.request, "urlopen", fake_urlopen)
    return calls, seen


def test_cli_fetch_waits_on_the_budget_and_never_refetches(
    monkeypatch, tmp_path, capsys
):
    calls, seen = _offline(monkeypatch)
    out = tmp_path / "r" / "R2.htm"
    url = "https://www.sec.gov/Archives/edgar/data/320193/x/R2.htm"
    assert sec_rate.main(["fetch", url, str(out)]) == 0
    assert out.read_bytes() == b"<html/>" and calls == [1]
    assert seen[0].get_header("User-agent") == "Scrooner test test@example.com"
    assert sec_rate.main(["fetch", url, str(out)]) == 0  # cached: no second request
    assert calls == [1] and len(seen) == 1
    assert "cached" in capsys.readouterr().out


def test_cli_fetch_refuses_non_sec_hosts_and_bad_usage(monkeypatch, tmp_path):
    calls, seen = _offline(monkeypatch)
    assert sec_rate.main(["fetch", "https://example.com/x", str(tmp_path / "x")]) == 2
    assert sec_rate.main(["get", "https://www.sec.gov/x"]) == 2
    assert calls == [] and seen == []


def test_fetch_decodes_gzip(monkeypatch):
    import gzip

    _offline(monkeypatch)
    monkeypatch.setattr(
        sec_rate.urllib.request,
        "urlopen",
        lambda req, timeout=0: _Resp(
            gzip.compress(b"{}"), {"Content-Encoding": "gzip"}
        ),
    )
    assert (
        sec_rate.fetch("https://data.sec.gov/submissions/CIK0000320193.json") == b"{}"
    )
