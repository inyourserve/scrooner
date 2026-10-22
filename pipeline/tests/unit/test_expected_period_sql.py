"""expected_period_end on real SQL (opt-in via SCROONER_TEST_DATABASE_URL): the
latest PERIODIC filing's period_of_report, ignoring 8-Ks and far-future dates."""

from datetime import date, timedelta

import psycopg
import pytest

from scrooner_pipeline.mapper import ttm_guards

pytestmark = pytest.mark.integration


@pytest.fixture
def conn(isolated_database_url):
    with psycopg.connect(isolated_database_url, autocommit=True) as c:
        c.execute("drop schema if exists core cascade; create schema core;")
        c.execute(
            "create table core.filing (id bigserial primary key, company_id bigint, form text, period_of_report date)"
        )
        far = date.today() + timedelta(days=400)
        c.cursor().executemany(
            "insert into core.filing (company_id, form, period_of_report) values (%s,%s,%s)",
            [
                (1, "10-K", date(2025, 12, 31)),
                (1, "10-Q", date(2026, 6, 30)),
                (1, "8-K", date(2026, 9, 1)),  # not periodic
                (1, "10-Q", far),  # beyond the future-date grace
                (2, "8-K", date(2026, 6, 30)),  # only a non-periodic filing
            ],
        )
        yield c


def test_expected_period_is_the_latest_periodic_filing(conn):
    assert ttm_guards.expected_period_end(conn, 1) == date(2026, 6, 30)


def test_no_periodic_filing_means_no_reference(conn):
    assert ttm_guards.expected_period_end(conn, 2) is None
    assert ttm_guards.expected_period_end(conn, 3) is None
