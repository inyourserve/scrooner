"""Verifier (2026-09-08) -- the one genuinely new piece of the
Detect->Investigate->...->Verify->Close loop this session's checkers
didn't already have: closing the loop by re-running the relevant
checker after a fix and reporting whether the incident actually
cleared, rather than trusting the fix was correct because it compiled.

Scoped deliberately to the two checks that are safe and cheap to
rerun on demand for a single company, no new external fetch, no rate
limit involved:
  - sanity/tag_investigator.py's investigate_open_findings() -- re-
    resolves company_tag_preference rows against already-fetched
    core.fact data (the real fix mechanism this session built). Now
    takes an optional company_id (added alongside this module) so
    verifying one company doesn't reprocess the whole population's
    open findings.
  - sanity/timeseries_check.py's run_concept() -- pure set-based SQL
    over canonical_fact. Also gained an optional company_id (its
    delete is scoped identically to its load when given, or a single-
    company rerun would silently wipe every other company's rows for
    that concept).

Both were originally whole-population-only; a first live run of this
verifier against one company took 5+ minutes and was killed because
investigate_open_findings() was reprocessing all ~20,000 open
data_sanity_check rows just to verify one company's fix. Fixed at the
source (both functions gained the company_id param above) rather than
working around it here.

Extended 2026-09-08 to ALSO re-fetch+compare yfinance Full Financial
Statements for the one company being verified (opt-out via
include_yfinance=False) -- a single-company yfinance call is cheap and
carries no meaningful rate-limit risk, unlike a full rotation batch.
Still does NOT trigger SEC Frames: Frames has no per-company mode at
all -- fetching one concept's Frame means downloading that whole
quarter's population-wide data regardless of how many companies you
actually want, so there's no cheap single-company path to add here.
Verifying a fix that depends on Frames means waiting for its own
weekly cron, then calling capture_state() again -- this module still
gives the before/after diff, it just doesn't force that one to refetch
on demand."""

from collections import defaultdict

import psycopg
import structlog

from scrooner_pipeline.sanity.tag_investigator import investigate_open_findings
from scrooner_pipeline.sanity.timeseries_check import CONCEPTS_TO_CHECK, run_concept
from scrooner_pipeline.yfinance_financials.fetch import fetch_and_store_statements
from scrooner_pipeline.yfinance_financials.compare import compare_statements

logger = structlog.get_logger()


def capture_state(conn: psycopg.Connection, company_id: int) -> list[dict]:
    """Real snapshot of every current incident row for one company,
    straight from the live view -- no caching, no staleness."""
    with conn.cursor() as cur:
        cur.execute(
            """
            select source_system, metric_or_concept, severity, period_end
            from analytics.data_incident
            where company_id = %s
            order by source_system, metric_or_concept, period_end
            """,
            (company_id,),
        )
        return [
            {"source_system": r[0], "metric_or_concept": r[1], "severity": r[2], "period_end": r[3]}
            for r in cur.fetchall()
        ]


def _key(row: dict) -> tuple:
    return (row["source_system"], row["metric_or_concept"], row["period_end"])


def diff_state(before: list[dict], after: list[dict]) -> dict:
    """Pure classification, no DB access -- unit-testable. Compares two
    capture_state() snapshots for the SAME company and buckets every
    (source_system, metric_or_concept, period_end) key into:
      resolved   -- was non-ok, now ok or gone entirely
      regressed  -- was ok (or absent), now non-ok
      still_open -- non-ok both times
      unchanged_ok -- ok both times (not reported, just counted)
    """
    before_by_key = {_key(r): r["severity"] for r in before}
    after_by_key = {_key(r): r["severity"] for r in after}

    resolved, regressed, still_open = [], [], []
    unchanged_ok = 0

    all_keys = set(before_by_key) | set(after_by_key)
    for k in all_keys:
        b = before_by_key.get(k, "ok")
        a = after_by_key.get(k, "ok")
        was_bad = b not in ("ok",)
        is_bad = a not in ("ok",)
        if was_bad and not is_bad:
            resolved.append({"source_system": k[0], "metric_or_concept": k[1], "period_end": k[2], "before": b, "after": a})
        elif not was_bad and is_bad:
            regressed.append({"source_system": k[0], "metric_or_concept": k[1], "period_end": k[2], "before": b, "after": a})
        elif was_bad and is_bad:
            still_open.append({"source_system": k[0], "metric_or_concept": k[1], "period_end": k[2], "before": b, "after": a})
        else:
            unchanged_ok += 1

    return {
        "resolved": resolved,
        "regressed": regressed,
        "still_open": still_open,
        "unchanged_ok_count": unchanged_ok,
    }


def verify_company(conn: psycopg.Connection, company_id: int, include_yfinance: bool = True) -> dict:
    """The real end-to-end verifier: snapshot -> rerun the checks that
    are safe to rerun on demand for one company -> snapshot again ->
    diff. This is what actually 'closes the loop' after applying a
    company_tag_preference fix (sanity/tag_investigator.py) -- confirms
    the fix cleared the incident rather than trusting the write
    succeeded."""
    before = capture_state(conn, company_id)

    investigate_stats = investigate_open_findings(conn, company_id=company_id)

    timeseries_stats = defaultdict(int)
    for concept_name, min_ratio, max_ratio, floor, never_negative in CONCEPTS_TO_CHECK:
        stats = run_concept(conn, concept_name, min_ratio, max_ratio, floor, never_negative, company_id=company_id)
        for k, v in stats.items():
            timeseries_stats[k] += v

    yfinance_stats = None
    if include_yfinance:
        fetch_and_store_statements(conn, [company_id], paced=True)
        yfinance_stats = compare_statements(conn, [company_id])

    after = capture_state(conn, company_id)
    diff = diff_state(before, after)

    logger.info(
        "verifier.verify_company",
        company_id=company_id,
        resolved=len(diff["resolved"]),
        regressed=len(diff["regressed"]),
        still_open=len(diff["still_open"]),
    )
    return {
        "company_id": company_id,
        "investigate_stats": investigate_stats,
        "timeseries_stats": dict(timeseries_stats),
        "yfinance_stats": yfinance_stats,
        **diff,
    }


def render_markdown(result: dict) -> str:
    lines = [f"# Verification: company_id={result['company_id']}", ""]
    lines.append(f"Resolved: **{len(result['resolved'])}** | Regressed: **{len(result['regressed'])}** | Still open: **{len(result['still_open'])}** | Unchanged ok: {result['unchanged_ok_count']}")
    lines.append("")

    for label, key in [("Resolved", "resolved"), ("Regressed (new/worse)", "regressed"), ("Still open", "still_open")]:
        lines.append(f"## {label}")
        lines.append("")
        rows = result[key]
        if not rows:
            lines.append("_None._")
        else:
            lines.append("| Source | Metric/Concept | Period | Before | After |")
            lines.append("|---|---|---|---|---|")
            for r in rows:
                lines.append(f"| {r['source_system']} | {r['metric_or_concept']} | {r['period_end'] or '-'} | {r['before']} | {r['after']} |")
        lines.append("")
    return "\n".join(lines)
