"""Thin Alpaca Market Data REST client (doc 25). Same shape as
common/sec_client.py -- retried, config-driven auth, one purpose.

feed='delayed_sip' is hard-coded here, not left to Alpaca's own
account-tier default -- confirmed live 2026-08-17 that a free/Basic
account defaults to 'iex' (single exchange, real-time) if `feed` is
omitted, but 'delayed_sip' (full consolidated tape, ~15min delayed) also
works on this same free account and is a deliberately better fit for a
fundamental screener, not a trading terminal. Passing it explicitly
means this choice survives even if Alpaca ever changes its own default,
instead of silently depending on it.
"""

import httpx
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

from scrooner_pipeline.collector.retry import HTTP_RETRY
from scrooner_pipeline.common.config import settings

logger = structlog.get_logger()

FEED = "delayed_sip"


class AlpacaClient:
    def __init__(self) -> None:
        self._client = httpx.Client(
            base_url="https://data.alpaca.markets/v2",
            headers={
                "APCA-API-KEY-ID": settings.alpaca_api_key or "",
                "APCA-API-SECRET-KEY": settings.alpaca_api_secret or "",
            },
            timeout=30.0,
        )

    @retry(
        retry=HTTP_RETRY,
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=1, max=30),
        reraise=True,
    )
    def latest_bars(self, symbols: list[str]) -> dict:
        """One batched call for up to `symbols` -- confirmed live that a
        3-symbol batch returns one bar per symbol in a single request;
        golden-10 scale fits comfortably in one call, well under the
        200 req/min rate limit confirmed live on this account."""
        response = self._client.get(
            "/stocks/bars/latest",
            params={"symbols": ",".join(symbols), "feed": FEED},
        )
        response.raise_for_status()
        return response.json().get("bars", {})

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "AlpacaClient":
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()
