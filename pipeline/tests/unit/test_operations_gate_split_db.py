"""Gate split + FSN freshness on real SQL (CI: Postgres 16, migrated scratch copy)."""

from datetime import date, datetime, timezone

import psycopg
import pytest

from scrooner_pipeline.operations import (
    FSN_FRESHNESS_SINCE,
    FSN_MISSING_FILINGS_SQL,
    fetch_fsn_missing_filings,
    load_fsn_freshness,
    evaluate_alerts,
    load_operational_snapshot,
    snapshot_as_dict,
)

pytestmark = pytest.mark.integration
HTTP_503 = "Server error '503 Service Unavailable' for url 'https://www.sec.gov/x/FilingSummary.xml'"


@pytest.fixture
def conn(isolated_database_url):
    with psycopg.connect(isolated_database_url, autocommit=True) as c:
        for t in (
            "analytics.mapper_error",
            "core.normalizer_error",
            "raw.collector_errors",
        ):
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
    _err(
        conn,
        "0000000001",
        "filing_line_evidence",
        "TransientSecError",
        "transient SEC error after 4 reads",
    )
    snap = _snap(conn)
    assert snap.dead_letters["mapper"] == 0
    assert snap.expected_misses["mapper_transient_sec_http"] == 2
    assert not [
        a for a in evaluate_alerts(snap) if a.startswith("unresolved_dead_letters")
    ]


@pytest.mark.parametrize(
    "rows",
    [
        # repeated for the same cik within the window
        [
            ("filing_line_evidence", "HTTPStatusError", HTTP_503, 0),
            ("filing_line_evidence", "HTTPStatusError", HTTP_503, 2),
        ],
        # same cik, another (non-transient) error nearby
        [
            ("filing_line_evidence", "HTTPStatusError", HTTP_503, 0),
            ("resolve", "ValueError", "boom", 1),
        ],
    ],
)
def test_repeated_transient_errors_still_fail(conn, rows):
    for stage, etype, msg, days in rows:
        _err(conn, "0000000002", stage, etype, msg, days)
    assert _snap(conn).dead_letters["mapper"] == len(rows)


def test_old_repeat_outside_window_does_not_count(conn):
    _err(conn, "0000000003", "filing_line_evidence", "HTTPStatusError", HTTP_503, 0)
    _err(
        conn,
        "0000000003",
        "filing_line_evidence",
        "HTTPStatusError",
        HTTP_503,
        30,
        resolved=True,
    )
    assert _snap(conn).dead_letters["mapper"] == 0


@pytest.mark.parametrize(
    "stage,etype,msg",
    [
        (
            "filing_line_evidence",
            "HTTPStatusError",
            "Client error '403 Forbidden' for url 'u'",
        ),
        ("filing_line_evidence", "KeyError", "x"),
        (
            "resolve",
            "HTTPStatusError",
            HTTP_503,
        ),  # transient class only excused for the probe
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


TODAY = date(2026, 11, 12)


def _fsn_seed(conn):
    """Two cohort companies plus a third outside the cohort. Returns (cohort ids, outsider id).
    A: core 10-Qs A1 (matched in fsn), A2 age 2, A3 age 72, A4 age 600+, A5 age 1; B: fully matched, plus rows that must
    never count (pre-2015, a 10-K/A, a filing inside an 'exclude' window); C (outside the cohort) has a missing filing."""

    def company(cik):
        return conn.execute(
            "insert into core.company (cik, company_name) values (%s,%s) returning id",
            (cik, cik),
        ).fetchone()[0]

    def core(cid, acc, filed, form="10-Q", period=None):
        conn.execute(
            "insert into core.filing (company_id, accession_number, form, filing_date, period_of_report)"
            " values (%s,%s,%s,%s,%s)",
            (cid, acc, form, filed, period),
        )

    def fsn(cid, acc, filed):
        conn.execute(
            "insert into fsn.filing (accession, company_id, cik, form, filed, fsn_set) values (%s,%s,%s,'10-Q',%s,'s')",
            (acc, cid, str(cid), filed),
        )

    a, b, c = company("9000000001"), company("9000000002"), company("9000000003")
    core(a, "A1", date(2026, 11, 1))
    fsn(a, "A1", date(2026, 11, 1))
    core(a, "A2", date(2026, 11, 10))
    core(a, "A3", date(2026, 9, 1))
    core(a, "A4", date(2025, 1, 15))
    core(a, "A5", date(2026, 11, 11))
    core(b, "B1", date(2026, 11, 1))
    fsn(b, "B1", date(2026, 11, 1))
    core(b, "B-old", date(2014, 6, 1))  # before 2015-01-01
    core(b, "B-amend", date(2026, 10, 1), form="10-K/A")  # not a 10-K/10-Q
    core(b, "B-excl", date(2020, 3, 1), period=date(2020, 1, 31))
    conn.execute(
        "insert into core.company_history_source (company_id, source_cik, relation, source_name, valid_from, valid_to, reason)"
        " values (%s,'0000000009','exclude','x','2020-01-01','2020-02-28','another entity')",
        (b,),
    )
    core(c, "C1", date(2026, 10, 1))
    fsn(c, "C0", date(2019, 2, 11))
    return [a, b], c


def test_fsn_freshness_counts_missing_filings_by_age_over_the_cohort_only(conn):
    cohort, _outsider = _fsn_seed(conn)
    fsn = load_fsn_freshness(conn, cohort, today=TODAY)
    assert (fsn["cohort_companies"], fsn["companies_behind"], fsn["max_lag_days"]) == (
        2,
        1,
        10,
    )
    assert fsn["missing_filings"] == 4 and fsn["companies_with_missing"] == 1
    assert fsn["missing_filings_by_age"] == {
        "le_1d": 1,
        "d2_30": 1,
        "d31_90": 1,
        "gt_90": 1,
    }
    rows = fetch_fsn_missing_filings(conn, cohort, today=TODAY)
    assert [r[1] for r in rows] == [
        "A4",
        "A3",
        "A2",
        "A5",
    ]  # the list the CLI emits, oldest first
    assert "does not yet prove the FSN path" in fsn["note"]


def test_fsn_freshness_alert_only_behind_flag(conn):
    cohort, _ = _fsn_seed(conn)
    report = snapshot_as_dict(_snap(conn, fsn_cohort_ids=cohort))
    assert (
        report["fsn_freshness"]["missing_filings"] == 4
    )  # today-relative ages; counts do not depend on them
    assert not [a for a in report["alerts"] if a.startswith("fsn_behind")]
    alerts = evaluate_alerts(_snap(conn, fsn_alert_enabled=True, fsn_cohort_ids=cohort))
    assert "fsn_behind_core:1:max_lag_days=10" in alerts


def test_fsn_missing_query_uses_the_company_index(conn):
    cohort, _ = _fsn_seed(conn)
    conn.execute("set enable_seqscan = off")
    plan = "\n".join(
        r[0]
        for r in conn.execute(
            "explain " + FSN_MISSING_FILINGS_SQL,
            {"ids": cohort, "since": FSN_FRESHNESS_SINCE, "today": TODAY},
        ).fetchall()
    )
    assert "idx_filing_company_id" in plan


def test_null_cik_transient_error_is_never_hidden(conn):
    """A NULL cik can never be shown isolated (o.cik = NULL matches nothing, which used to hide it). The column is NOT NULL
    today, so the condition is evaluated on a literal row; the same row with a cik is transient (control)."""
    from scrooner_pipeline.operations import MAPPER_TRANSIENT_CONDITION

    def transient(cik):
        return conn.execute(
            "with e as (select -1::bigint as id, %s::text as cik, 'filing_line_evidence'::text as stage, "
            "'TransientSecError'::text as error_type, 'x'::text as message, now() as occurred_at) "
            f"select count(*) from e where {MAPPER_TRANSIENT_CONDITION}",
            (cik,),
        ).fetchone()[0]

    assert transient("0000000009") == 1
    assert transient(None) == 0
