"""Unified Data Incident dashboard (2026-09-08) -- reads
analytics.data_incident (migration 0055), the live VIEW that normalizes
all 5 checker tables built this session (Data Sanity, yfinance
Financials, SEC Frames, Time-Series Self-Consistency, Freshness) into
one shape. This is the "dashboard" from doc/data-moat/scope/
internal-auto-fixer.md's own example output ("Open incidents 7 /
Critical 0 / Major 2 / ...") -- built as one read-only SQL summary over
a live view, not a separately-synced incident table, since every
checker already writes its own row on every run.

Deliberately NOT the 6-agent Watcher/Triage/Investigator/Impact/
Solver/Verifier system the scope doc sketches -- see doc/data-moat/
learnings/ for the evaluation. What's built here is the "Finding /
Incident" + dashboard layer, expressed as plain deterministic SQL
(doc 05's "determinism before AI magic"), plus (in verifier.py) the
one genuinely new piece: closing the loop by re-running the relevant
checker after a fix and reporting whether the incident actually
cleared."""

from collections import defaultdict

import psycopg
import structlog

logger = structlog.get_logger()

SEVERITY_ORDER = ["critical", "major", "minor", "missing", "ok"]


def summarize(conn: psycopg.Connection) -> dict:
    """One read over the live view -- counts per (source_system,
    severity), plus a top-offenders list (companies with the most
    non-ok findings) and a per-metric/concept breakdown for major+
    findings. Pure read, no writes."""
    with conn.cursor() as cur:
        cur.execute(
            """
            select source_system, severity, count(*)
            from analytics.data_incident
            group by 1, 2
            """
        )
        by_source_severity: dict[str, dict[str, int]] = defaultdict(dict)
        for source, severity, count in cur.fetchall():
            by_source_severity[source][severity] = count

        cur.execute(
            """
            select company_id, company_name, count(*) as n
            from analytics.data_incident
            where severity in ('critical', 'major')
            group by 1, 2
            order by n desc
            limit 15
            """
        )
        top_offenders = [
            {"company_id": r[0], "company_name": r[1], "count": r[2]}
            for r in cur.fetchall()
        ]

        cur.execute(
            """
            select source_system, metric_or_concept, severity, count(*) as n
            from analytics.data_incident
            where severity in ('critical', 'major')
            group by 1, 2, 3
            order by n desc
            limit 20
            """
        )
        worst_metrics = [
            {
                "source_system": r[0],
                "metric_or_concept": r[1],
                "severity": r[2],
                "count": r[3],
            }
            for r in cur.fetchall()
        ]

    totals = {sev: 0 for sev in SEVERITY_ORDER}
    for sev_counts in by_source_severity.values():
        for sev, n in sev_counts.items():
            totals[sev] = totals.get(sev, 0) + n

    return {
        "totals": totals,
        "by_source": dict(by_source_severity),
        "top_offenders": top_offenders,
        "worst_metrics": worst_metrics,
    }


def render_markdown(summary: dict) -> str:
    totals = summary["totals"]
    lines = ["# Unified Data Incident Dashboard", ""]
    lines.append("## Totals")
    lines.append("")
    lines.append("| Severity | Count |")
    lines.append("|---|---|")
    for sev in SEVERITY_ORDER:
        lines.append(f"| {sev} | {totals.get(sev, 0):,} |")
    lines.append("")

    lines.append("## By source system")
    lines.append("")
    lines.append("| Source | " + " | ".join(SEVERITY_ORDER) + " |")
    lines.append("|---|" + "---|" * len(SEVERITY_ORDER))
    for source, sev_counts in sorted(summary["by_source"].items()):
        row = " | ".join(str(sev_counts.get(sev, 0)) for sev in SEVERITY_ORDER)
        lines.append(f"| {source} | {row} |")
    lines.append("")

    lines.append("## Worst metrics/concepts (critical + major)")
    lines.append("")
    if summary["worst_metrics"]:
        lines.append("| Source | Metric/Concept | Severity | Count |")
        lines.append("|---|---|---|---|")
        for row in summary["worst_metrics"]:
            lines.append(
                f"| {row['source_system']} | {row['metric_or_concept']} | {row['severity']} | {row['count']} |"
            )
    else:
        lines.append("_None._")
    lines.append("")

    lines.append("## Top offending companies (critical + major findings)")
    lines.append("")
    if summary["top_offenders"]:
        lines.append("| Company | Findings |")
        lines.append("|---|---|")
        for row in summary["top_offenders"]:
            lines.append(f"| {row['company_name']} | {row['count']} |")
    else:
        lines.append("_None._")
    lines.append("")

    return "\n".join(lines)
