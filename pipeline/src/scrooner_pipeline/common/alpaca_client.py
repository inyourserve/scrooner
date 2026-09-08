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

import re

import httpx
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

from scrooner_pipeline.collector.retry import HTTP_RETRY
from scrooner_pipeline.common.config import settings

logger = structlog.get_logger()

FEED = "delayed_sip"

# `latest_bars` was only ever verified at golden-10 scale (comment below,
# unchanged from doc 25) -- found live 2026-09-08, wiring this into a
# daily full-population cron for the first time: a single unchunked GET
# with ~5,000 tickers in the query string risks a URL-length rejection
# (most servers/CDNs cap around 8KB) that would fail the exact same
# "unattended job silently red for weeks" way the incremental.py 403 bug
# just did. Chunked defensively -- 300 tickers/request keeps the query
# string under ~2KB, comfortably safe, while still needing <20 requests
# for the full active population, nowhere near Alpaca's documented
# 200 req/min limit.
BATCH_SIZE = 300

# Found live 2026-09-08, first real full-population test (5,175 tickers,
# not the 478-ticker sample tested first -- this is exactly why full-
# scale verification matters, a sample can miss a rare-but-real symbol
# shape): Alpaca rejects the ENTIRE chunk with 400 if even ONE symbol in
# it is malformed for its API, not just that one symbol -- confirmed via
# {"message":"code=400, message=invalid symbol: ANG-PD"}, a hyphenated
# preferred-share ticker this project's own primary-ticker resolution
# can legitimately produce. A pre-filter regex would need to know every
# rejection rule Alpaca enforces in advance; parsing the actual rejected
# symbol out of the real error and retrying without it handles whatever
# Alpaca actually rejects, discovered live rather than guessed.
_INVALID_SYMBOL_RE = re.compile(r'invalid symbol: ([^"]+)')


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
    def _latest_bars_batch(self, symbols: list[str]) -> dict:
        response = self._client.get(
            "/stocks/bars/latest",
            params={"symbols": ",".join(symbols), "feed": FEED},
        )
        response.raise_for_status()
        return response.json().get("bars", {})

    def _fetch_chunk_dropping_invalid(self, symbols: list[str]) -> dict:
        """Retries one chunk, removing whatever symbol Alpaca's own 400
        response names as invalid, until the chunk succeeds or every
        symbol in it has been tried and dropped. See module comment for
        why this is reactive (parse the real rejection) rather than a
        pre-filter regex."""
        remaining = list(symbols)
        dropped: list[str] = []
        while remaining:
            try:
                bars = self._latest_bars_batch(remaining)
                if dropped:
                    logger.warning("alpaca_client.dropped_invalid_symbols", symbols=dropped)
                return bars
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code != 400:
                    raise
                match = _INVALID_SYMBOL_RE.search(exc.response.text)
                if not match or match.group(1) not in remaining:
                    raise
                remaining.remove(match.group(1))
                dropped.append(match.group(1))
        logger.warning("alpaca_client.dropped_invalid_symbols", symbols=dropped)
        return {}

    def latest_bars(self, symbols: list[str]) -> dict:
        """Chunked into BATCH_SIZE-symbol requests (see module comment --
        the original single-request version was only ever verified at
        golden-10 scale). Confirmed live that a 3-symbol batch returns one
        bar per symbol in a single request; each chunk here is well under
        Alpaca's 200 req/min rate limit confirmed live on this account."""
        bars: dict = {}
        for i in range(0, len(symbols), BATCH_SIZE):
            bars.update(self._fetch_chunk_dropping_invalid(symbols[i : i + BATCH_SIZE]))
        return bars

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "AlpacaClient":
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()
