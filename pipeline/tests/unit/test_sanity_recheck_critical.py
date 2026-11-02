"""`scrooner-sanity recheck-critical` (2026-11-02): re-check, just before the
gate, every company whose yfinance-check finding is still critical, so a
finding the later fix steps already resolved is not counted stale (FRHC,
run 41343223897)."""

import contextlib

import psycopg
import pytest
from typer.testing import CliRunner

from scrooner_pipeline.jobs import sanity as sanity_job
from scrooner_pipeline.sanity.yfinance_check import critical_finding_company_ids


@pytest.mark.integration
def test_selects_each_company_with_a_critical_yfinance_finding_once(isolated_database_url):
    with psycopg.connect(isolated_database_url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """insert into core.company (cik, company_name)
                   values ('0000000001', 'Critical Co'), ('0000000002', 'Major Co'),
                          ('0000000003', 'Other Source Co'), ('0000000004', 'Two Criticals Co')
                   returning id"""
            )
            critical, major, other_source, two = (r[0] for r in cur.fetchall())
            cur.executemany(
                """insert into analytics.data_sanity_check (company_id, metric_name, severity, external_source)
                   values (%s, %s, %s, %s)""",
                [
                    (critical, "revenue_zero_check", "critical", "yfinance"),
                    (major, "market_cap", "major", "yfinance"),
                    (other_source, "revenue_zero_check", "critical", "sec_frames"),
                    (two, "revenue_zero_check", "critical", "yfinance"),
                    (two, "market_cap", "critical", "yfinance"),
                ],
            )
        assert critical_finding_company_ids(conn) == sorted([critical, two])


@pytest.mark.unit
def test_command_rechecks_exactly_the_critical_companies(monkeypatch):
    calls = []
    monkeypatch.setattr(sanity_job, "get_connection", lambda: contextlib.nullcontext("conn"))
    monkeypatch.setattr(sanity_job, "critical_finding_company_ids", lambda conn: [7, 9])
    monkeypatch.setattr(
        sanity_job, "run_sanity_checks", lambda conn, ids: calls.append((conn, ids)) or {"considered": len(ids)}
    )

    result = CliRunner().invoke(sanity_job.app, ["recheck-critical"])

    assert result.exit_code == 0, result.output
    assert calls == [("conn", [7, 9])]
    assert "considered': 2" in result.output
