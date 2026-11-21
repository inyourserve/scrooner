"""Gate split + FSN freshness on real SQL (CI: Postgres 16, migrated scratch copy)."""

from datetime import date, datetime, timezone

import psycopg
import pytest

from scrooner_pipeline.operations import (
    evaluate_alerts,
    load_operational_snapshot,
    snapshot_as_dict,
)

pytestmark = pytest.mark.integration
HTTP_503 = "Server error '503 Service Unavailable' for url 'https://www.sec.gov/x/FilingSummary.xml'"


@pytest.fixture
def conn(isolated_database_url):
    with psycopg.connect(isolated_database_url, autocommit=True) as c:
        for t in ("analytics.mapper_error", "core.normalizer_error", "raw.collector_errors"):
            c.execute(f"delete from {t}")
        yield c


def _err(conn, cik, stage, etype, msg, days_ago=0.0, resolved=False):
    conn.execute(
        "insert into analytics.mapper_error (cik, stage, error_type, message, occurred_at, resolved,"
        " resolved_at, resolution_note) "
        "values (%s,%s,%s,%s, now() - make_interval(secs => %s), %s,"
        " case when %s then now() end, case when %s then 'test resolution note for the audit check' end)",
        (cik, stage, etype, msg, days_ago * 86400, resolved, resolved, resolved),
    )


def _snap(conn, **kw):
    return load_operational_snapshot(conn, now=datetime.now(timezone.utc), **kw)


def test_lone_transient_probe_http_error_is_visibility_only(conn):
    _err(conn, "0001487798", "filing_line_evidence", "HTTPStatusError", HTTP_503)
    _err(conn, "0000000001", "filing_line_evidence", "TransientSecError", "transient SEC error after 4 reads")
    snap = _snap(conn)
    assert snap.dead_letters["mapper"] == 0
    assert snap.expected_misses["mapper_transient_sec_http"] == 2
    assert not [a for a in evaluate_alerts(snap) if a.startswith("unresolved_dead_letters")]


@pytest.mark.parametrize(
    "rows",
    [
        # repeated for the same cik within the window
        [("filing_line_evidence", "HTTPStatusError", HTTP_503, 0), ("filing_line_evidence", "HTTPStatusError", HTTP_503, 2)],
        # same cik, another (non-transient) error nearby
        [("filing_line_evidence", "HTTPStatusError", HTTP_503, 0), ("resolve", "ValueError", "boom", 1)],
    ],
)
def test_repeated_transient_errors_still_fail(conn, rows):
    for stage, etype, msg, days in rows:
        _err(conn, "0000000002", stage, etype, msg, days)
    assert _snap(conn).dead_letters["mapper"] == len(rows)


def test_old_repeat_outside_window_does_not_count(conn):
    _err(conn, "0000000003", "filing_line_evidence", "HTTPStatusError", HTTP_503, 0)
    _err(conn, "0000000003", "filing_line_evidence", "HTTPStatusError", HTTP_503, 30, resolved=True)
    assert _snap(conn).dead_letters["mapper"] == 0


@pytest.mark.parametrize(
    "stage,etype,msg",
    [
        ("filing_line_evidence", "HTTPStatusError", "Client error '403 Forbidden' for url 'u'"),
        ("filing_line_evidence", "KeyError", "x"),
        ("resolve", "HTTPStatusError", HTTP_503),  # transient class only excused for the probe
        ("resolve", "ValueError", "systemic"),
    ],
)
def test_non_transient_or_other_stage_errors_fail(conn, stage, etype, msg):
    _err(conn, "0000000004", stage, etype, msg)
    snap = _snap(conn)
    assert snap.dead_letters["mapper"] == 1
    assert "unresolved_dead_letters:mapper:1" in evaluate_alerts(snap)


def test_resolved_rows_never_count(conn):
    _err(conn, "0000000005", "resolve", "ValueError", "x", resolved=True)
    assert _snap(conn).dead_letters["mapper"] == 0


def _fsn_seed(conn):
    def company(cik):
        return conn.execute(
            "insert into core.company (cik, company_name) values (%s,%s) returning id", (cik, cik)
        ).fetchone()[0]

    behind, current = company("9000000001"), company("9000000002")
    for cid, core_d, fsn_d in (
        (behind, date(2026, 11, 10), date(2026, 11, 1)),
        (current, date(2026, 11, 1), date(2026, 11, 1)),
    ):
        conn.execute(
            "insert into core.filing (company_id, accession_number, form, filing_date) values (%s,%s,'10-Q',%s)",
            (cid, f"c-{cid}", core_d),
        )
        conn.execute(
            "insert into fsn.filing (accession, company_id, cik, form, filed, fsn_set) values (%s,%s,%s,'10-Q',%s,'s')",
            (f"f-{cid}", cid, str(cid), fsn_d),
        )


def test_fsn_freshness_reports_lag_and_alerts_only_behind_flag(conn):
    _fsn_seed(conn)
    report = snapshot_as_dict(_snap(conn))
    fsn = report["fsn_freshness"]
    assert (fsn["cohort_companies"], fsn["companies_behind"], fsn["max_lag_days"]) == (2, 1, 9)
    assert "does not yet prove the FSN path" in fsn["note"]
    assert not [a for a in report["alerts"] if a.startswith("fsn_behind")]

    alerts = evaluate_alerts(_snap(conn, fsn_alert_enabled=True))
    assert "fsn_behind_core:1:max_lag_days=9" in alerts
