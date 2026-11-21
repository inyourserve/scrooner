"""A saved screen run's later pages still explain every exclusion (2026-11-22).

app.screen_result stores only excluded CIKs and metric names; _read_page must
recompute each company's reason and the exclusion summary from the run's own
snapshot version, and a kept-without-value cell on page 2 must carry its reason
too. Runs against the migrated Postgres 16 test database in CI
(SCROONER_TEST_DATABASE_URL); everything is rolled back at the end.
"""

from __future__ import annotations

import os
import uuid
from contextlib import contextmanager
from datetime import date
from decimal import Decimal

import psycopg
import pytest
from psycopg import sql

from routers import screen_runs
from scrooner_pipeline.screener.schema import ScreenQuery

VERSION = 990_002
METRICS = ("revenue_growth_yoy", "roe")


@pytest.fixture
def conn():
    url = os.getenv("SCROONER_TEST_DATABASE_URL")
    if not url:
        pytest.skip("SCROONER_TEST_DATABASE_URL is not configured")
    if "test" not in (url.rsplit("/", 1)[-1]):
        pytest.fail("SCROONER_TEST_DATABASE_URL database name must contain 'test'")
    with psycopg.connect(url) as connection:
        yield connection
        connection.rollback()


def _build(conn) -> dict[str, int]:
    catalog = {
        name: conn.execute(
            "insert into analytics.metric_definition (metric_name, formula_version, formula_description) "
            "values (%s, 1, 'test') returning id",
            (name,),
        ).fetchone()[0]
        for name in METRICS
    }
    parts = []
    for name in METRICS:
        parts += [
            sql.SQL("add column if not exists {} numeric").format(sql.Identifier(name)),
            sql.SQL("add column if not exists {} text").format(
                sql.Identifier(f"{name}__period_label")
            ),
            sql.SQL("add column if not exists {} date").format(
                sql.Identifier(f"{name}__period_end")
            ),
            sql.SQL("add column if not exists {} integer").format(
                sql.Identifier(f"{name}__formula_version")
            ),
        ]
    conn.execute(
        sql.SQL("alter table analytics.company_screening_snapshot {}").format(
            sql.SQL(", ").join(parts)
        )
    )
    end = date(2025, 12, 31)
    spec = [  # key, rgy, rgy label, roe
        ("P", Decimal("0.25"), "FY", Decimal("0.10")),
        ("F", Decimal("0.05"), "FY", Decimal("0.10")),
        ("H", None, "FY", Decimal("0.60")),
        ("T", None, None, None),
        ("G", None, None, None),
    ]
    ids = {}
    for i, (key, rgy, label, roe) in enumerate(spec):
        cik = f"099100{i:04d}"
        cid = conn.execute(
            "insert into core.company (cik, company_name) values (%s, %s) returning id",
            (cik, f"Co {key}"),
        ).fetchone()[0]
        ids[key] = cid
        conn.execute(
            "insert into analytics.company_screening_snapshot (company_id, cik, company_name, sic_code, status, "
            "dataset_version, revenue_growth_yoy, revenue_growth_yoy__period_label, revenue_growth_yoy__period_end, "
            "revenue_growth_yoy__formula_version, roe, roe__period_label, roe__period_end, roe__formula_version) "
            "values (%s, %s, %s, '7372', 'active', %s, %s, %s, %s, 1, %s, %s, %s, 1)",
            (
                cid,
                cik,
                f"Co {key}",
                VERSION,
                rgy,
                label,
                end if label else None,
                roe,
                "FY" if roe is not None else None,
                end if roe is not None else None,
            ),
        )
    conn.execute(
        "insert into analytics.metric_value (company_id, metric_definition_id, period_start, period_end, "
        "period_label, value, is_null_reason) values (%s, %s, '2025-01-01', %s, 'FY', null, "
        "'missing:prior_period(2024_FY)')",
        (ids["H"], catalog["revenue_growth_yoy"], end),
    )
    conn.execute(
        "insert into analytics.company_data_point_template (company_id, data_point, in_template, reason, "
        "effective_from, template, source, template_version) values (%s, 'roe', false, "
        "'not meaningful for this sector', '2020-01-01', 'test', 'company_override', 'v1')",
        (ids["T"],),
    )
    return catalog


@pytest.mark.integration
def test_page_two_of_a_saved_run_still_returns_reasons_and_summary(conn, monkeypatch):
    catalog = _build(conn)
    user_id = str(uuid.uuid4())
    conn.execute("insert into auth.users (id) values (%s)", (user_id,))

    @contextmanager
    def pooled():
        yield conn

    monkeypatch.setattr(screen_runs, "get_pooled_connection", pooled)
    monkeypatch.setattr(screen_runs, "get_cached_dataset_version", lambda _c: VERSION)
    monkeypatch.setattr(screen_runs, "get_cached_metric_catalog", lambda _c: catalog)
    monkeypatch.setattr(screen_runs, "get_cached_run_lookup", lambda *_a: (None, None))
    monkeypatch.setattr(screen_runs, "set_cached_run_write", lambda **_k: None)
    monkeypatch.setattr(screen_runs, "get_cached_run_page", lambda *_a: None)
    monkeypatch.setattr(screen_runs, "set_cached_run_page", lambda *_a: None)
    # Only the two fixture metrics exist here; the product's default columns/sort do not.
    monkeypatch.setattr(screen_runs, "prepare_screen_run_query", lambda q: q)

    query = ScreenQuery.model_validate(
        {
            "metric_predicates": [
                {
                    "metric_name": "revenue_growth_yoy",
                    "operator": ">",
                    "value": "0.10",
                    "include_missing": True,
                },
                {"metric_name": "roe", "operator": ">", "value": "0.05"},
            ]
        }
    )
    first = screen_runs.create_run_from_query("growth", query, user_id, page_size=1)
    second = screen_runs._read_page(
        conn, first["run_id"], user_id, 1, first["next_cursor"]
    )

    # P matches with values; H is kept without a growth value; F fails growth;
    # T (template OUT for roe) and G (no roe row) are excluded for roe.
    assert first["total_count"] == 2
    assert [item["company_name"] for item in first["items"]] == ["Co P"]
    assert [item["company_name"] for item in second["items"]] == ["Co H"]
    cell = second["items"][0]["metrics"]["revenue_growth_yoy"]
    assert cell["value"] is None and cell["missing"]["bucket"] == "history_horizon"

    for page in (first, second):
        reasons = {
            e["company_name"]: e["reasons"]["roe"]["bucket"]
            for e in page["excluded_missing_data"]
        }
        assert reasons == {"Co T": "not_in_template", "Co G": "open_gap"}
        summary = page["exclusion_summary"]
        assert (
            summary["total_candidates"],
            summary["matched"],
            summary["excluded"],
            summary["not_matched"],
        ) == (5, 2, 2, 1)
        assert summary["by_bucket"] == {"not_in_template": 1, "open_gap": 1}
    assert first["exclusion_summary"] == second["exclusion_summary"]
