"""Opt-in contract checks against free, official SEC EDGAR endpoints."""

from __future__ import annotations

import os

import httpx
import pytest


@pytest.mark.live
def test_sec_submissions_contract_for_known_filer() -> None:
    user_agent = os.getenv("SCROONER_LIVE_SEC_USER_AGENT")
    if not user_agent:
        pytest.fail(
            "SCROONER_LIVE_SEC_USER_AGENT is required for live SEC checks; "
            "set it to a declared product/contact identity"
        )

    response = httpx.get(
        "https://data.sec.gov/submissions/CIK0000320193.json",
        headers={"User-Agent": user_agent, "Accept-Encoding": "gzip, deflate"},
        timeout=30.0,
    )
    response.raise_for_status()
    payload = response.json()

    assert payload["cik"] == "0000320193"
    assert payload["name"]
    assert payload["filings"]["recent"]["accessionNumber"]
    assert payload["filings"]["recent"]["form"]
