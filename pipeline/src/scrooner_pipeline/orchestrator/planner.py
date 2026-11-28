"""Planner: turn unplanned events into deduplicated work items (PIPELINE.md section 3).

A work item is (cik, from_stage, versions). Rules:
  * a company with a done, non-dry-run item at the same versions_hash is not planned again (outcome already_done);
  * a company with a queued (pending or retry_wait) item of the same dry_run kind gets the new event merged into it
    (versions unioned, from_stage = the earliest), so duplicate and overlapping events collapse into one item;
  * otherwise a new pending item is created.
A rule_version / template_change event with cik '*' targets only the companies the rule touches, found through a
`RuleUsage` index. If no index answers, the event is marked `unscoped` and NOTHING is queued: it never fans out to
every company (PIPELINE.md: "not everyone"). `cohort` (optional) drops companies outside the cohort being served.

The daily catch-up sweep emits one rule_version event per company whose ops.company_served_version differs from the
current versions and plans them; running it twice with the same current versions collapses to the same events.
"""

from __future__ import annotations

import json
from collections.abc import Collection
from dataclasses import dataclass, field
from typing import Any, Protocol

import psycopg

from .store import (
    DEFAULT_FROM_STAGE,
    STAGE_ORDER,
    emit_event,
    stage_index,
    versions_hash,
)


class RuleUsage(Protocol):
    def companies(self, rule_id: str) -> list[str] | None:
        """CIKs whose served cells a rule touched, or None when the index cannot say (never an empty guess)."""


class DbRuleUsage:
    """Usage from what the DB records today (there is no maintained, indexed rule -> company index yet).

    analytics.cell_proof.checks->'rules' holds {rule_id: version} per proof row (proof/rules.py), and
    analytics.company_tag_map.rule_ids (0128) lists the mapping rules per company. Neither is indexed for this lookup:
    a query scans them, so it is read-only under its own statement_timeout. Shared resolver rules (line_map/rules/*)
    leave no company key anywhere else, so a rule seen in neither place returns None, not [].
    """

    def __init__(self, conn: psycopg.Connection, timeout: str = "120s"):
        self.conn, self.timeout = conn, timeout

    def companies(self, rule_id: str) -> list[str] | None:
        self.conn.execute(f"set statement_timeout = '{self.timeout}'")
        rows = self.conn.execute(
            """select distinct c.cik from analytics.cell_proof p join core.company c on c.id = p.company_id
               where p.checks->'rules' ? %s
               union
               select distinct c.cik from analytics.company_tag_map m join core.company c on c.id = m.company_id
               where m.rule_ids @> array[%s]::text[]""",
            (rule_id, rule_id),
        ).fetchall()
        return sorted(r[0] for r in rows) or None


@dataclass
class PlanReport:
    events: int = 0
    queued: int = 0
    merged: int = 0
    already_done: int = 0
    unscoped: int = 0
    no_companies: int = 0
    blocked_on_ingest: int = 0
    outcomes: dict[int, str] = field(default_factory=dict)


def _has_fsn(conn: psycopg.Connection, cik: str) -> bool:
    """True when fsn.filing holds a row for the company (or the table is absent, as in a bare test database)."""
    if conn.execute("select to_regclass('fsn.filing')").fetchone()[0] is None:
        return True
    return (
        conn.execute(
            "select 1 from fsn.filing where cik = %s limit 1", (cik,)
        ).fetchone()
        is not None
    )


def unblock_ingested(conn: psycopg.Connection) -> int:
    """blocked_on_ingest items whose company now has filings go back to pending."""
    if conn.execute("select to_regclass('fsn.filing')").fetchone()[0] is None:
        return 0
    return conn.execute(
        """update ops.work_item w set status = 'pending', updated_at = now()
           where w.status = 'blocked_on_ingest'
             and exists (select 1 from fsn.filing f where f.cik = w.cik)"""
    ).rowcount


def unblock_resolved(conn: psycopg.Connection, ready_ciks) -> int:
    """blocked_on_resolver items whose resolver file now exists go back to pending (the caller names those ciks)."""
    return conn.execute(
        "update ops.work_item set status = 'pending', updated_at = now() where status = 'blocked_on_resolver' and cik = any(%s)",
        (sorted(ready_ciks),),
    ).rowcount


def _event_from_stage(cause: str, versions: dict[str, Any]) -> int:
    stage = int(versions.get("from_stage", DEFAULT_FROM_STAGE[cause]))
    if stage not in STAGE_ORDER:
        raise ValueError(f"bad from_stage {stage!r}")
    return stage


def _merge_versions(
    base: dict[str, Any], cause: str, ev_versions: dict[str, Any]
) -> dict[str, Any]:
    out = {k: list(v) for k, v in base.items()}
    lst = out.setdefault(cause, [])
    if ev_versions not in lst:
        lst.append(ev_versions)
    lst.sort(key=lambda d: json.dumps(d, sort_keys=True))
    return out


def plan_events(
    conn: psycopg.Connection,
    usage: RuleUsage | None = None,
    *,
    cohort: Collection[str] | None = None,
    dry_run: bool = False,
    limit: int = 5000,
) -> PlanReport:
    """Plan every unplanned event in one transaction. Safe to run concurrently (rows are locked skip-locked)."""
    report = PlanReport()
    unblock_ingested(conn)
    with conn.transaction():
        # an event of a company outside the cohort stays unplanned: another rank set's run will take it
        events = conn.execute(
            """select id, cik, cause, versions from ops.pipeline_event
               where planned_at is null and (%s::text[] is null or cik = '*' or cik = any(%s::text[]))
               order by id limit %s for update skip locked""",
            (
                sorted(cohort) if cohort is not None else None,
                sorted(cohort) if cohort is not None else None,
                limit,
            ),
        ).fetchall()
        for ev_id, cik, cause, versions in events:
            report.events += 1
            unscoped = False
            if cik == "*":
                rule_id = versions.get("rule") or versions.get("template")
                ciks = (
                    usage.companies(str(rule_id))
                    if (usage is not None and rule_id)
                    else None
                )
                if ciks is None:
                    unscoped, ciks = True, []
            else:
                ciks = [cik]
            if cohort is not None:
                ciks = [c for c in ciks if c in cohort]
            results = [
                _plan_one(conn, ev_id, c, cause, versions, dry_run)
                for c in sorted(set(ciks))
            ]
            if unscoped:
                outcome = "unscoped"
            elif not results:
                outcome = "no_companies"
            elif "queued" in results or "blocked_on_ingest" in results:
                outcome = "queued" if "queued" in results else "blocked_on_ingest"
            else:
                outcome = "merged" if "merged" in results else "already_done"
            conn.execute(
                "update ops.pipeline_event set planned_at = now(), plan_outcome = %s where id = %s",
                (outcome, ev_id),
            )
            report.outcomes[ev_id] = outcome
            setattr(report, outcome, getattr(report, outcome) + 1)
    return report


def _plan_one(
    conn, ev_id: int, cik: str, cause: str, ev_versions: dict, dry_run: bool
) -> str:
    from_stage = _event_from_stage(cause, ev_versions)
    cand = _merge_versions({}, cause, ev_versions)
    queued = conn.execute(
        """select id, from_stage, causes, versions, status from ops.work_item
           where cik = %s and dry_run = %s and status in ('pending', 'retry_wait', 'blocked_on_ingest', 'blocked_on_resolver') for update""",
        (cik, dry_run),
    ).fetchone()
    # a stage 3+ item for a company with no fsn.filing row cannot run: it waits (blocked_on_ingest), it is not dead-lettered
    blocked = stage_index(from_stage) > 0 and not _has_fsn(conn, cik)
    if queued is None:
        if (
            not dry_run
            and conn.execute(
                "select 1 from ops.work_item where cik = %s and status = 'done' and not dry_run and versions_hash = %s",
                (cik, versions_hash(cand)),
            ).fetchone()
        ):
            return "already_done"
        wid = conn.execute(
            """insert into ops.work_item (cik, from_stage, causes, versions, versions_hash, dry_run, status)
               values (%s, %s, %s, %s::jsonb, %s, %s, %s) returning id""",
            (
                cik,
                from_stage,
                [cause],
                json.dumps(cand, sort_keys=True),
                versions_hash(cand),
                dry_run,
                "blocked_on_ingest" if blocked else "pending",
            ),
        ).fetchone()[0]
        outcome = "blocked_on_ingest" if blocked else "queued"
    else:
        wid, old_stage, causes, old_versions, old_status = queued
        merged = _merge_versions(old_versions, cause, ev_versions)
        new_stage = min(old_stage, from_stage, key=stage_index)
        if merged != old_versions or new_stage != old_stage:
            conn.execute(
                """update ops.work_item set versions = %s::jsonb, versions_hash = %s, from_stage = %s,
                          causes = %s, updated_at = now() where id = %s""",
                (
                    json.dumps(merged, sort_keys=True),
                    versions_hash(merged),
                    new_stage,
                    sorted(set(causes) | {cause}),
                    wid,
                ),
            )
        if old_status == "blocked_on_ingest" and (
            stage_index(new_stage) == 0 or _has_fsn(conn, cik)
        ):
            conn.execute(
                "update ops.work_item set status = 'pending' where id = %s", (wid,)
            )
        outcome = "merged"
    conn.execute(
        "insert into ops.work_item_event (work_item_id, event_id) values (%s, %s) on conflict do nothing",
        (wid, ev_id),
    )
    return outcome


def sweep(
    conn: psycopg.Connection,
    current_versions: dict[str, dict[str, Any]],
    *,
    dry_run: bool = False,
) -> PlanReport:
    """Daily catch-up: plan every company whose served versions differ from its current versions.

    `current_versions` is cik -> versions (orchestrator/versions.py), covering exactly the cohort being served. A company
    with a queued or running item is left alone (that item will serve it); a company with an unresolved dead letter is
    left to its owner (an auto re-plan would just dead-letter it again); resolving the dead letter re-opens it to the
    sweep. Each planned company gets a `rule_version` event {"catch_up": versions} (idempotent per versions), so the
    audit trail and the dedupe are the same as for any other event. Running it twice plans nothing the second time.
    """
    report = PlanReport()
    served = dict(
        conn.execute(
            "select cik, versions_hash from ops.company_served_version"
        ).fetchall()
    )
    blocked = {
        r[0]
        for r in conn.execute(
            """select cik from ops.work_dead_letter where resolved_at is null
               union select cik from ops.work_item where status in ('pending','retry_wait','running','blocked_on_ingest','blocked_on_resolver') and dry_run = %s""",
            (dry_run,),
        ).fetchall()
    }
    with conn.transaction():
        for cik in sorted(current_versions):
            vs = current_versions[cik]
            if served.get(cik) == versions_hash(vs) or cik in blocked:
                continue
            ev = {"catch_up": vs, "from_stage": 3}
            emit_event(conn, cik=cik, cause="rule_version", versions=ev, source="sweep")
            ev_id = conn.execute(
                "select id from ops.pipeline_event where cik = %s and cause = 'rule_version' and versions_hash = %s",
                (cik, versions_hash(ev)),
            ).fetchone()[0]
            outcome = _plan_one(conn, ev_id, cik, "rule_version", ev, dry_run)
            conn.execute(
                "update ops.pipeline_event set planned_at = coalesce(planned_at, now()), "
                "plan_outcome = coalesce(plan_outcome, %s) where id = %s",
                (outcome, ev_id),
            )
            report.events += 1
            setattr(report, outcome, getattr(report, outcome) + 1)
    return report
