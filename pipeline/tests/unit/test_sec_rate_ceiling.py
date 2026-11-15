"""The SEC rate never exceeds the 4 req/s hard rule (root CLAUDE.md), whatever the configured value."""

from scrooner_pipeline.common import config, sec_client


def test_default_sec_rate_is_within_the_rule():
    assert config.Settings.model_fields["sec_max_requests_per_second"].default <= 4.0


def test_client_clamps_a_higher_configured_rate(monkeypatch):
    monkeypatch.setattr(sec_client.settings, "sec_max_requests_per_second", 8.0)
    seen = {}

    class Spy:
        def __init__(self, rate, *a, **k):
            seen["rate"] = rate

    monkeypatch.setattr(sec_client, "_RateLimiter", Spy)
    sec_client.SECClient()
    assert seen["rate"] <= sec_client.SEC_RATE_CEILING == 4.0
