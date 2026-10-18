"""Heavy-job gate (proposal 2026-10-18, not yet wired into any command).

Standing rule (root CLAUDE.md, doc 53 rule 5): before a heavy batch job, look at who
else is on the database. The shared pooler allows ~15 client connections in total,
and two concurrent heavy jobs have already taken Postgres unreachable once. A rule
that lives only in prose is skipped under time pressure, so this makes it a check a
command runs first and that refuses by default.

Checks (one cheap read on pg_stat_activity, run with a 20s statement_timeout):
  * total connections to this database above `max_connections` (default 10, leaving
    headroom under the ~15 ceiling for the job's own connections);
  * any OTHER session with a query running longer than `max_query_minutes`
    (default 10) in state 'active' -- that is another heavy job in flight.
Idle sessions and this session itself are ignored.

Wiring (not applied): call `require_heavy_job_gate(conn, job="resolve-facts")` at the
top of each heavy Typer command; `--force-heavy` skips it but logs loudly. GitHub
workflows that are the only intended heavy job set no override, so a manual recompute
overlapping a nightly is refused instead of silently doubling load.
"""

from dataclasses import dataclass, field

import psycopg
import structlog

logger = structlog.get_logger()

DEFAULT_MAX_CONNECTIONS = 10
DEFAULT_MAX_QUERY_MINUTES = 10.0


class HeavyJobGateRefused(RuntimeError):
    """Raised when the database is too busy to start a heavy job."""


@dataclass(frozen=True)
class GateResult:
    allowed: bool
    connections: int
    long_running: list[tuple[int, float, str]] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)


def evaluate_gate(
    connections: int,
    long_running: list[tuple[int, float, str]],
    max_connections: int = DEFAULT_MAX_CONNECTIONS,
    max_query_minutes: float = DEFAULT_MAX_QUERY_MINUTES,
) -> GateResult:
    """Pure decision. `long_running` is (pid, minutes_running, query_head) for other
    sessions' active queries; entries under the threshold are ignored."""
    reasons: list[str] = []
    if connections > max_connections:
        reasons.append(f"{connections} connections open (limit {max_connections})")
    slow = [q for q in long_running if q[1] > max_query_minutes]
    for pid, minutes, head in slow:
        reasons.append(f"pid {pid} running {minutes:.1f} min: {head[:80]!r}")
    return GateResult(not reasons, connections, slow, reasons)


def read_activity(conn: psycopg.Connection) -> tuple[int, list[tuple[int, float, str]]]:
    with conn.cursor() as cur:
        cur.execute("set statement_timeout = '20s'")
        cur.execute(
            "select count(*) from pg_stat_activity where datname = current_database()"
        )
        row = cur.fetchone()
        connections = int(row[0]) if row else 0
        cur.execute(
            """
            select pid, extract(epoch from (now() - query_start)) / 60.0, left(query, 120)
            from pg_stat_activity
            where datname = current_database() and pid <> pg_backend_pid()
              and state = 'active' and query_start is not null
            """
        )
        long_running = [(int(p), float(m), str(q)) for p, m, q in cur.fetchall()]
    return connections, long_running


def require_heavy_job_gate(
    conn: psycopg.Connection,
    job: str,
    max_connections: int = DEFAULT_MAX_CONNECTIONS,
    max_query_minutes: float = DEFAULT_MAX_QUERY_MINUTES,
    force: bool = False,
) -> GateResult:
    connections, long_running = read_activity(conn)
    result = evaluate_gate(
        connections, long_running, max_connections, max_query_minutes
    )
    if result.allowed:
        logger.info("heavy_job_gate.open", job=job, connections=connections)
        return result
    if force:
        logger.warning("heavy_job_gate.forced", job=job, reasons=result.reasons)
        return result
    raise HeavyJobGateRefused(
        f"{job}: refusing to start, database busy -- " + "; ".join(result.reasons)
    )
