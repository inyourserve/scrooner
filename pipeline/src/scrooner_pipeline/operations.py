"""Read-only operational snapshot and alert evaluation for Day 10.

This module consolidates existing durable pipeline evidence: collector run
records, per-layer dead letters, source/stage freshness, duration, and row
statistics. It does not create a parallel source of truth or mutate pipeline
state. The CLI in ``jobs/operations.py`` makes failed/stale state visible
without ad-hoc SQL and can exit non-zero for an external scheduler/alert.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from numbers import Number

import psycopg

from scrooner_pipeline.collector.logs import RunRecord, get_recent_runs


@dataclass(frozen=True)
class FreshnessTarget:
    source: str
    timestamp_sql: str
    row_count_sql: str
    maximum_age: timedelta


FRESHNESS_TARGETS = (
    FreshnessTarget(
        "sec_companyfacts",
        "select max(fetched_at) from raw.sec_companyfacts",
        "select count(*) from raw.sec_companyfacts",
        timedelta(days=7),
    ),
    FreshnessTarget(
        "sec_submissions",
        "select max(fetched_at) from raw.sec_submissions",
        "select count(*) from raw.sec_submissions",
        timedelta(days=7),
    ),
    FreshnessTarget(
        "filing_index",
        "select max(collected_at) from raw.sec_filing_documents",
        "select count(*) from raw.sec_filing_documents",
        timedelta(hours=72),
    ),
    FreshnessTarget(
        "market_prices",
        "select max(bar_timestamp) from core.market_price_alpaca",
        "select count(*) from core.market_price_alpaca",
        timedelta(hours=96),
    ),
    FreshnessTarget(
        "derived_metrics",
        "select max(data_as_of) from analytics.metric_value",
        "select count(*) from analytics.metric_value",
        timedelta(days=7),
    ),
)

DEAD_LETTER_QUERIES = {
    "collector": "select count(*) from raw.collector_errors where not resolved",
    "normalizer": "select count(*) from core.normalizer_error where not resolved",
    "mapper": "select count(*) from analytics.mapper_error where not resolved",
}


@dataclass(frozen=True)
class FreshnessReading:
    source: str
    latest_at: datetime | None
    row_count: int
    maximum_age: timedelta

    def age(self, now: datetime) -> timedelta | None:
        if self.latest_at is None:
            return None
        timestamp = self.latest_at
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        return now - timestamp.astimezone(timezone.utc)

    def state(self, now: datetime) -> str:
        age = self.age(now)
        if age is None or self.row_count == 0:
            return "missing"
        return "stale" if age > self.maximum_age else "fresh"


@dataclass(frozen=True)
class OperationalSnapshot:
    generated_at: datetime
    freshness: tuple[FreshnessReading, ...]
    dead_letters: dict[str, int]
    recent_runs: tuple[RunRecord, ...]


def _scalar(conn: psycopg.Connection, sql: str):
    with conn.cursor() as cur:
        cur.execute(sql)
        row = cur.fetchone()
        return row[0] if row else None


def load_operational_snapshot(
    conn: psycopg.Connection,
    now: datetime | None = None,
    run_limit: int = 50,
) -> OperationalSnapshot:
    generated_at = now or datetime.now(timezone.utc)
    freshness = tuple(
        FreshnessReading(
            source=target.source,
            latest_at=_scalar(conn, target.timestamp_sql),
            row_count=int(_scalar(conn, target.row_count_sql) or 0),
            maximum_age=target.maximum_age,
        )
        for target in FRESHNESS_TARGETS
    )
    dead_letters = {layer: int(_scalar(conn, sql) or 0) for layer, sql in DEAD_LETTER_QUERIES.items()}
    return OperationalSnapshot(
        generated_at=generated_at,
        freshness=freshness,
        dead_letters=dead_letters,
        recent_runs=tuple(get_recent_runs(conn, limit=run_limit)),
    )


def _row_counts(stats: dict) -> dict[str, float]:
    row_words = ("row", "stored", "inserted", "upserted", "company", "filing", "object", "downloaded")
    return {
        key: float(value)
        for key, value in stats.items()
        if isinstance(value, Number) and not isinstance(value, bool) and any(word in key.lower() for word in row_words)
    }


def row_count_anomalies(runs: tuple[RunRecord, ...]) -> list[str]:
    """Compare the latest two successful runs with identical job/scope."""
    grouped: dict[tuple[str | None, str | None], list[RunRecord]] = {}
    for run in runs:
        if run.status == "succeeded":
            grouped.setdefault((run.job, run.params_key), []).append(run)

    alerts: list[str] = []
    for (job, params_key), matching in grouped.items():
        matching.sort(key=lambda run: run.started_at, reverse=True)
        if len(matching) < 2:
            continue
        current, previous = matching[:2]
        current_counts = _row_counts(current.stats)
        previous_counts = _row_counts(previous.stats)
        for key in sorted(current_counts.keys() & previous_counts.keys()):
            before, after = previous_counts[key], current_counts[key]
            if before <= 0:
                continue
            ratio = after / before
            if ratio < 0.5 or ratio > 2:
                alerts.append(
                    f"row_count_anomaly:{job or 'unknown'}:{params_key or 'unknown'}:{key}:{before:g}->{after:g}"
                )
    return alerts


def evaluate_alerts(snapshot: OperationalSnapshot) -> list[str]:
    now = snapshot.generated_at
    alerts = [
        f"freshness_{reading.state(now)}:{reading.source}"
        for reading in snapshot.freshness
        if reading.state(now) != "fresh"
    ]
    alerts.extend(
        f"unresolved_dead_letters:{layer}:{count}"
        for layer, count in sorted(snapshot.dead_letters.items())
        if count
    )

    recent_failure_cutoff = now - timedelta(hours=24)
    stale_heartbeat_cutoff = now - timedelta(hours=2)
    latest_success_by_scope: dict[tuple[str | None, str | None], datetime] = {}
    for run in snapshot.recent_runs:
        if run.status != "succeeded":
            continue
        completed_at = run.finished_at or run.started_at
        completed_at = completed_at if completed_at.tzinfo else completed_at.replace(tzinfo=timezone.utc)
        key = (run.job, run.params_key)
        latest_success_by_scope[key] = max(completed_at, latest_success_by_scope.get(key, completed_at))

    for run in snapshot.recent_runs:
        started_at = run.started_at if run.started_at.tzinfo else run.started_at.replace(tzinfo=timezone.utc)
        failed_at = run.finished_at or run.started_at
        failed_at = failed_at if failed_at.tzinfo else failed_at.replace(tzinfo=timezone.utc)
        heartbeat = run.heartbeat_at or run.started_at
        heartbeat = heartbeat if heartbeat.tzinfo else heartbeat.replace(tzinfo=timezone.utc)
        recovered_at = latest_success_by_scope.get((run.job, run.params_key))
        if (
            run.status == "failed"
            and started_at >= recent_failure_cutoff
            and (recovered_at is None or recovered_at <= failed_at)
        ):
            alerts.append(f"recent_failed_run:{run.id}:{run.job or 'unknown'}")
        if run.status == "running" and heartbeat < stale_heartbeat_cutoff:
            alerts.append(f"stuck_run:{run.id}:{run.job or 'unknown'}")

    alerts.extend(row_count_anomalies(snapshot.recent_runs))
    return alerts


def snapshot_as_dict(snapshot: OperationalSnapshot) -> dict:
    alerts = evaluate_alerts(snapshot)
    return {
        "status": "alert" if alerts else "ok",
        "generated_at": snapshot.generated_at.isoformat(),
        "alerts": alerts,
        "freshness": [
            {
                "source": reading.source,
                "state": reading.state(snapshot.generated_at),
                "latest_at": reading.latest_at.isoformat() if reading.latest_at else None,
                "age_hours": round(reading.age(snapshot.generated_at).total_seconds() / 3600, 2)
                if reading.age(snapshot.generated_at) is not None
                else None,
                "target_hours": reading.maximum_age.total_seconds() / 3600,
                "row_count": reading.row_count,
            }
            for reading in snapshot.freshness
        ],
        "dead_letters": snapshot.dead_letters,
        "recent_runs": [
            {
                "run_id": run.id,
                "job": run.job,
                "scope": run.params_key,
                "status": run.status,
                "started_at": run.started_at.isoformat(),
                "finished_at": run.finished_at.isoformat() if run.finished_at else None,
                "duration_seconds": run.duration_seconds,
                "stats": run.stats,
            }
            for run in snapshot.recent_runs
        ],
    }
