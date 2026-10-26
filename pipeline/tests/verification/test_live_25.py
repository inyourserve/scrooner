"""Regression: the Verifier's hand-checked balance-sheet instants.

Skipped by default (needs sec.gov). Run live (~2 requests per filing, 4 req/s):
  cd pipeline && SCROONER_LIVE_SEC=1 SEC_USER_AGENT="..." PYTHONPATH=src \
    .venv/bin/python -m pytest tests/verification/test_live_25.py --noconftest
Must pass all (25 original + 7 layout cases = 32).
"""

import json
import os
import ssl
import time
import urllib.request
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from scrooner_pipeline.verification import filing_kit as fk

CASES = json.loads((Path(__file__).parent / "fixtures" / "live_25.json").read_text())


def test_manifest_is_complete():
    assert len(CASES) == 32
    for c in CASES:
        assert {
            "cik",
            "accession",
            "instant",
            "expected_face_liabilities",
            "page_multiplier",
        } <= set(c)


class _Client:
    def __init__(self):
        self.ua, self.last, self.n = os.environ["SEC_USER_AGENT"], 0.0, 0
        try:
            import certifi

            self.ctx = ssl.create_default_context(cafile=certifi.where())
        except ImportError:
            self.ctx = None

    def get(self, url):
        assert url.startswith("https://www.sec.gov/")
        time.sleep(max(0.0, 0.26 - (time.monotonic() - self.last)))
        self.last, self.n = time.monotonic(), self.n + 1
        req = urllib.request.Request(url, headers={"User-Agent": self.ua})
        return urllib.request.urlopen(req, timeout=60, context=self.ctx).read()


@pytest.mark.skipif(
    not os.environ.get("SCROONER_LIVE_SEC"),
    reason="live sec.gov test; set SCROONER_LIVE_SEC=1",
)
def test_live_25_reproduce():
    client, bad = _Client(), []
    for c in CASES:
        base = f"https://www.sec.gov/Archives/edgar/data/{int(c['cik'])}/{c['accession'].replace('-', '')}/"
        page = fk.fetch_statements(client, base, ("BS",))["BS"]
        r = fk.face_liabilities(page, date.fromisoformat(c["instant"]))
        if (
            r.value is None
            or r.value != Decimal(c["expected_face_liabilities"])
            or page.multiplier != c["page_multiplier"]
        ):
            bad.append(
                (c["ticker"], c["instant"], r.value, c["expected_face_liabilities"])
            )
    assert not bad, bad
