"""Unit tests for company_master/security_type.py's slash-fallback ticker
classification -- found live 2026-09-06 chasing why Berkshire Hathaway
(BRK-A/BRK-B) never resolved a primary ticker despite both listings existing."""

from unittest.mock import MagicMock, patch

from scrooner_pipeline.company_master.security_type import PRIMARY_SECURITY_TYPES, _classify_ticker


def _mock_response(security_type: str | None, name: str = "SOME CO"):
    data = [{"securityType": security_type, "name": name}] if security_type else None
    resp = MagicMock()
    resp.json.return_value = [{"data": data}]
    return resp


def test_plain_ticker_resolves_without_fallback():
    client = MagicMock()
    client.post.return_value = _mock_response("Common Stock", "APPLE INC")
    result = _classify_ticker(client, "AAPL")
    assert result == ("Common Stock", "APPLE INC")
    assert client.post.call_count == 1


def test_hyphenated_common_share_class_falls_back_to_slash():
    client = MagicMock()
    # First call (hyphen form) -> no match; second call (slash form) -> real hit.
    client.post.side_effect = [_mock_response(None), _mock_response("Common Stock", "BERKSHIRE HATHAWAY INC")]
    with patch("scrooner_pipeline.company_master.security_type.time.sleep"):
        result = _classify_ticker(client, "BRK-A")
    assert result == ("Common Stock", "BERKSHIRE HATHAWAY INC")
    assert client.post.call_count == 2
    second_call_body = client.post.call_args_list[1].kwargs["json"]
    assert second_call_body[0]["idValue"] == "BRK/A"


def test_genuine_preferred_ticker_stays_unresolved_after_fallback():
    # Real evidence: "GNL-PE" and "GNL/PE" both return NO_MATCH -- the
    # fallback must not fabricate a classification for a ticker that's
    # genuinely inconclusive under both forms.
    client = MagicMock()
    client.post.side_effect = [_mock_response(None), _mock_response(None)]
    with patch("scrooner_pipeline.company_master.security_type.time.sleep"):
        result = _classify_ticker(client, "GNL-PE")
    assert result == (None, None)
    assert client.post.call_count == 2


def test_ticker_without_hyphen_never_triggers_fallback():
    client = MagicMock()
    client.post.return_value = _mock_response(None)
    result = _classify_ticker(client, "ZZZZ")
    assert result == (None, None)
    assert client.post.call_count == 1


def test_reit_and_mlp_are_primary_types():
    assert "REIT" in PRIMARY_SECURITY_TYPES
    assert "MLP" in PRIMARY_SECURITY_TYPES


def test_tracking_stock_and_ltd_part_are_primary_types():
    # Liberty Media/Liberty Broadband (tracking stock is their ONLY class of
    # stock) and Empire State Realty OP / Restaurant Brands International LP
    # (real operating partnerships, not passive investment vehicles).
    assert "Tracking Stk" in PRIMARY_SECURITY_TYPES
    assert "Ltd Part" in PRIMARY_SECURITY_TYPES
