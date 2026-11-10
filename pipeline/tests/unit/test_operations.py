from datetime import datetime, timedelta, timezone

import pytest

from scrooner_pipeline.collector.logs import RunRecord
from scrooner_pipeline.operations import (
    DEAD_LETTER_QUERIES,
    EXPECTED_MISS_QUERIES,
    FreshnessReading,
    OperationalSnapshot,
    evaluate_alerts,
    row_count_anomalies,
    snapshot_as_dict,
)


pytestmark = pytest.mark.unit
NOW = datetime(2026, 8, 19, 12, tzinfo=timezone.utc)


def run(
    run_id: int,
    *,
    status: str = "succeeded",
    started_at: datetime = NOW - timedelta(hours=1),
    finished_at: datetime | None = None,
    heartbeat_at: datetime | None = NOW - timedelta(minutes=5),
    stats: dict | None = None,
    job: str = "incremental",
    params_key: str = "ciks=ALL|limit=None",
) -> RunRecord:
    return RunRecord(
        id=run_id,
        run_type="incremental",
        job=job,
        params_key=params_key,
        status=status,
        started_at=started_at,
        finished_at=(finished_at or NOW) if status != "running" else None,
        heartbeat_at=heartbeat_at,
        stats=stats or {},
    )


def healthy_snapshot() -> OperationalSnapshot:
    return OperationalSnapshot(
        generated_at=NOW,
        freshness=(
            FreshnessReading("filing_index", NOW - timedelta(hours=1), 100, timedelta(hours=72)),
            FreshnessReading("market_prices", NOW - timedelta(hours=12), 10, timedelta(hours=96)),
        ),
        dead_letters={"collector": 0, "normalizer": 0, "mapper": 0},
        recent_runs=(run(1),),
    )


def test_healthy_snapshot_has_no_alerts_and_serializes_duration_and_rows() -> None:
    report = snapshot_as_dict(healthy_snapshot())

    assert report["status"] == "ok"
    assert report["alerts"] == []
    assert report["freshness"][0]["age_hours"] == 1
    assert report["recent_runs"][0]["duration_seconds"] == 3600


def test_missing_stale_dead_letter_failed_and_stuck_states_are_visible() -> None:
    snapshot = OperationalSnapshot(
        generated_at=NOW,
        freshness=(
            FreshnessReading("missing_source", None, 0, timedelta(hours=1)),
            FreshnessReading("stale_source", NOW - timedelta(hours=2), 10, timedelta(hours=1)),
        ),
        dead_letters={"collector": 0, "normalizer": 2, "mapper": 3},
        recent_runs=(
            run(2, status="failed"),
            run(3, status="running", started_at=NOW - timedelta(hours=4), heartbeat_at=NOW - timedelta(hours=3)),
        ),
    )

    assert evaluate_alerts(snapshot) == [
        "freshness_missing:missing_source",
        "freshness_stale:stale_source",
        "unresolved_dead_letters:mapper:3",
        "unresolved_dead_letters:normalizer:2",
        "recent_failed_run:2:incremental",
        "stuck_run:3:incremental",
    ]


def test_collector_dead_letter_query_excludes_not_in_bulk_archive() -> None:
    # Found live 2026-09-10: NotInBulkArchive is the ONLY error_type
    # raw.collector_errors has ever recorded (97/97 historical rows) -- a
    # benign, expected condition, not a pipeline bug -- but the old
    # unfiltered query treated it as zero-tolerance, alert-failing the
    # daily "Enforce freshness and dead-letter health" gate for 8+
    # consecutive days on pure noise. Any OTHER collector error_type must
    # still alert with zero tolerance.
    query = DEAD_LETTER_QUERIES["collector"]
    assert "error_type != 'NotInBulkArchive'" in query
    assert "not resolved" in query


def test_expected_misses_never_reach_evaluate_alerts() -> None:
    # expected_misses is visibility-only -- a healthy snapshot with real
    # NotInBulkArchive counts in expected_misses must still report zero
    # alerts and status "ok".
    snapshot = OperationalSnapshot(
        generated_at=NOW,
        freshness=(FreshnessReading("filing_index", NOW - timedelta(hours=1), 100, timedelta(hours=72)),),
        dead_letters={"collector": 0, "normalizer": 0, "mapper": 0},
        recent_runs=(run(1),),
        expected_misses={"collector_not_in_bulk_archive": 15},
    )

    report = snapshot_as_dict(snapshot)

    assert report["status"] == "ok"
    assert report["alerts"] == []
    assert report["expected_misses"] == {"collector_not_in_bulk_archive": 15}


def test_expected_miss_queries_target_the_same_table_with_the_opposite_filter() -> None:
    query = EXPECTED_MISS_QUERIES["collector_not_in_bulk_archive"]
    assert "raw.collector_errors" in query
    assert "error_type = 'NotInBulkArchive'" in query
    assert "not resolved" in query


def test_row_count_anomaly_compares_only_same_successful_job_and_scope() -> None:
    runs = (
        run(4, started_at=NOW - timedelta(minutes=5), stats={"filings_inserted": 20}),
        run(3, started_at=NOW - timedelta(hours=1), stats={"filings_inserted": 100}),
        run(2, started_at=NOW - timedelta(hours=2), stats={"filings_inserted": 100}, params_key="other"),
        run(1, status="failed", started_at=NOW - timedelta(hours=3), stats={"filings_inserted": 1}),
    )

    assert row_count_anomalies(runs) == [
        "row_count_anomaly:incremental:ciks=ALL|limit=None:filings_inserted:100->20"
    ]


def test_later_success_for_identical_job_and_scope_closes_failure_alert() -> None:
    snapshot = OperationalSnapshot(
        generated_at=NOW,
        freshness=healthy_snapshot().freshness,
        dead_letters={"collector": 0, "normalizer": 0, "mapper": 0},
        recent_runs=(
            run(13, started_at=NOW - timedelta(minutes=5), finished_at=NOW - timedelta(minutes=4)),
            run(
                12,
                status="failed",
                started_at=NOW - timedelta(minutes=20),
                finished_at=NOW - timedelta(minutes=15),
            ),
        ),
    )

    assert evaluate_alerts(snapshot) == []


def test_success_for_different_scope_does_not_hide_failure() -> None:
    snapshot = OperationalSnapshot(
        generated_at=NOW,
        freshness=healthy_snapshot().freshness,
        dead_letters={"collector": 0, "normalizer": 0, "mapper": 0},
        recent_runs=(
            run(
                13,
                started_at=NOW - timedelta(minutes=5),
                finished_at=NOW - timedelta(minutes=4),
                params_key="different",
            ),
            run(
                12,
                status="failed",
                started_at=NOW - timedelta(minutes=20),
                finished_at=NOW - timedelta(minutes=15),
            ),
        ),
    )

    assert evaluate_alerts(snapshot) == ["recent_failed_run:12:incremental"]


# 2026-11-06: the nightly refresh failed 11-02 to 11-05 on
# row_count_anomaly:companyfacts:...:stored:214->0. Run 311 re-collected the
# same companies as run 308 (the same SEC day indexed twice) and every one was
# byte-identical, so storing 0 was correct; the old pair then re-alerted every
# night because nothing newer shared its scope.
COMPANYFACTS = {"job": "companyfacts", "params_key": "ciks=0000002098,0000002230|limit=None"}


def test_a_drop_fully_explained_by_unchanged_skips_is_not_an_anomaly() -> None:
    runs = (
        run(311, started_at=NOW - timedelta(hours=1), **COMPANYFACTS,
            stats={"considered": 1051, "stored": 0, "unchanged_skipped": 1051, "errors": 0, "not_in_archive": 18}),
        run(308, started_at=NOW - timedelta(days=2), **COMPANYFACTS,
            stats={"considered": 1051, "stored": 214, "unchanged_skipped": 837, "errors": 0, "not_in_archive": 18}),
    )

    assert row_count_anomalies(runs, now=NOW) == []


def test_a_drop_with_errors_or_unaccounted_items_still_alerts() -> None:
    previous = run(308, started_at=NOW - timedelta(days=2), **COMPANYFACTS,
                   stats={"considered": 1051, "stored": 214, "unchanged_skipped": 837, "errors": 0})
    broken = run(311, started_at=NOW - timedelta(hours=1), **COMPANYFACTS,
                 stats={"considered": 1051, "stored": 0, "unchanged_skipped": 900, "errors": 151})
    vanished = run(312, started_at=NOW - timedelta(hours=1), **COMPANYFACTS,
                   stats={"considered": 1051, "stored": 0, "unchanged_skipped": 0, "errors": 0})

    # Every item accounted for as unchanged, but the run also had errors: the
    # errors == 0 guard must keep this alerting.
    accounted_but_errored = run(313, started_at=NOW - timedelta(hours=1), **COMPANYFACTS,
                                stats={"considered": 1051, "stored": 0, "unchanged_skipped": 1051, "errors": 5})

    expected = [f"row_count_anomaly:companyfacts:{COMPANYFACTS['params_key']}:stored:214->0"]
    assert row_count_anomalies((broken, previous), now=NOW) == expected
    assert row_count_anomalies((vanished, previous), now=NOW) == expected
    assert row_count_anomalies((accounted_but_errored, previous), now=NOW) == expected


def test_a_pair_whose_newer_run_is_over_a_day_old_does_not_re_alert() -> None:
    runs = (
        run(4, started_at=NOW - timedelta(days=3), stats={"filings_inserted": 20}),
        run(3, started_at=NOW - timedelta(days=4), stats={"filings_inserted": 100}),
    )

    assert row_count_anomalies(runs, now=NOW) == []
    # The same pair is still reported when it is fresh.
    assert row_count_anomalies(runs, now=NOW - timedelta(days=3)) == [
        "row_count_anomaly:incremental:ciks=ALL|limit=None:filings_inserted:100->20"
    ]


def test_normalizer_backlog_measures_ingest_time_not_the_filing_date() -> None:
    # 2026-11-10: max(filing_date) read as midnight made a normal weekend look like a 4-day
    # backlog once the gate ran after midnight UTC (run 42712874321).
    from scrooner_pipeline.operations import FRESHNESS_TARGETS

    target = next(t for t in FRESHNESS_TARGETS if t.source == "normalizer_backlog")
    assert target.timestamp_sql == "select max(created_at) from core.filing"
    assert target.maximum_age == timedelta(days=5)
    # Friday's filings ingested Saturday 18:03 UTC, gate on Tuesday 00:53 UTC: fresh.
    reading = FreshnessReading(
        source="normalizer_backlog",
        latest_at=datetime(2026, 11, 7, 18, 3, tzinfo=timezone.utc),
        row_count=1,
        maximum_age=target.maximum_age,
    )
    assert reading.state(datetime(2026, 11, 10, 0, 53, tzinfo=timezone.utc)) == "fresh"
    # A normalizer that has ingested nothing for 6 days is stale.
    assert reading.state(datetime(2026, 11, 13, 19, 0, tzinfo=timezone.utc)) != "fresh"
