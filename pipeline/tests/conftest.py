"""Shared deterministic test fixtures.

Default tests never open a database connection or access the network. Future
database integration tests must request ``isolated_database_url``; its guard
refuses URLs that are not explicitly configured and visibly test-only.
"""

from __future__ import annotations

import json
import os
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path
from urllib.parse import urlparse
from uuid import UUID

import pytest


# Production settings are currently instantiated at module-import time. Use
# explicit, unreachable values so importing pure helpers cannot read a local
# .env or accidentally acquire live credentials during the offline suite.
os.environ["DATABASE_URL"] = "postgresql://scrooner_test:unused@127.0.0.1:9/scrooner_test"
os.environ["SUPABASE_URL"] = "https://scrooner-test.invalid"
os.environ["SUPABASE_SERVICE_ROLE_KEY"] = "test-only-not-a-secret"
os.environ["SEC_USER_AGENT"] = "Scrooner test suite test@example.invalid"


FIXTURE_ROOT = Path(__file__).parent / "fixtures"


@pytest.fixture
def company_factory():
    def make(**overrides):
        company = {
            "id": 1,
            "cik": "0000320193",
            "name": "Apple Inc.",
            "ticker": "AAPL",
            "status": "active",
        }
        company.update(overrides)
        return company

    return make


@pytest.fixture
def filing_factory():
    def make(**overrides):
        filing = {
            "id": 10,
            "company_id": 1,
            "accession_number": "0000320193-25-000079",
            "form_type": "10-K",
            "filing_date": date(2025, 10, 31),
            "period_end": date(2025, 9, 27),
        }
        filing.update(overrides)
        return filing

    return make


@pytest.fixture
def period_factory():
    def make(**overrides):
        period = {
            "id": 20,
            "company_id": 1,
            "period_type": "duration",
            "start_date": date(2024, 9, 29),
            "end_date": date(2025, 9, 27),
            "fiscal_year": 2025,
            "fiscal_period": "FY",
        }
        period.update(overrides)
        return period

    return make


@pytest.fixture
def fact_factory():
    def make(**overrides):
        fact = {
            "id": 30,
            "company_id": 1,
            "filing_id": 10,
            "period_id": 20,
            "taxonomy": "us-gaap",
            "concept": "RevenueFromContractWithCustomerExcludingAssessedTax",
            "unit": "usd",
            "value": Decimal("416161000000"),
            "is_authoritative": True,
        }
        fact.update(overrides)
        return fact

    return make


@pytest.fixture
def canonical_fact_factory(fact_factory):
    def make(**overrides):
        canonical_fact = {
            "id": 40,
            "company_id": 1,
            "canonical_concept": "revenue",
            "period_id": 20,
            "value": Decimal("416161000000"),
            "source_fact_ids": [fact_factory()["id"]],
        }
        canonical_fact.update(overrides)
        return canonical_fact

    return make


@pytest.fixture
def metric_factory(canonical_fact_factory):
    def make(**overrides):
        metric = {
            "id": 50,
            "company_id": 1,
            "metric_name": "net_margin",
            "formula_version": 1,
            "period_end": date(2025, 9, 27),
            "value": Decimal("0.26915646386855326424"),
            "source_fact_ids": canonical_fact_factory()["source_fact_ids"],
            "calculated_at": datetime(2026, 8, 18, tzinfo=timezone.utc),
        }
        metric.update(overrides)
        return metric

    return make


@pytest.fixture
def price_factory():
    def make(**overrides):
        price = {
            "security_id": UUID("00000000-0000-0000-0000-000000000001"),
            "ticker": "AAPL",
            "as_of": datetime(2026, 8, 17, 19, 45, tzinfo=timezone.utc),
            "price": Decimal("303.69"),
            "currency": "USD",
            "source": "alpaca_delayed_sip",
        }
        price.update(overrides)
        return price

    return make


@pytest.fixture
def companyfacts_payload() -> dict:
    fixture_path = FIXTURE_ROOT / "sec" / "companyfacts_minimal.json"
    return json.loads(fixture_path.read_text())


@pytest.fixture
def isolated_database_url() -> str:
    """Return an opt-in test DB URL, refusing ambiguous/production targets."""
    url = os.getenv("SCROONER_TEST_DATABASE_URL")
    if not url:
        pytest.skip("SCROONER_TEST_DATABASE_URL is not configured")

    parsed = urlparse(url)
    database_name = parsed.path.removeprefix("/").lower()
    if "test" not in database_name:
        pytest.fail("SCROONER_TEST_DATABASE_URL database name must contain 'test'")

    production_url = os.getenv("DATABASE_URL")
    if production_url and url == production_url:
        pytest.fail("test database URL must not equal DATABASE_URL")
    return url
