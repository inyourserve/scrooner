"""Reads back analytics.data_sanity_check for a human-readable summary --
the "report it" half of the Data Sanity Layer. Read-only, no fetch, no
pacing concerns; safe to run as often as wanted.

Deliberately does not judge the pipeline's overall health from a single
number -- returns the breakdown by severity AND the worst individual rows,
since a CI job (.github/workflows/pipeline-sanity.yml) wants both: a
GITHUB_STEP_SUMMARY-friendly table, and a decision of whether to fail the
job (any 'critical' row, or more than a small number of 'major' rows)."""

import psycopg

SEVERITY_ORDER = [
    "critical",
    "major",
    "minor",
    "missing_ours",
    "missing_external",
    "ok",
]


def summarize(conn: psycopg.Connection) -> dict:
    with conn.cursor() as cur:
        cur.execute(
            """
            select metric_name, severity, count(*)
            from analytics.data_sanity_check
            group by metric_name, severity
            """
        )
        by_metric_severity: dict[str, dict[str, int]] = {}
        for metric_name, severity, count in cur.fetchall():
            by_metric_severity.setdefault(metric_name, {})[severity] = count

        cur.execute(
            "select count(distinct company_id) from analytics.data_sanity_check"
        )
        (companies_checked,) = cur.fetchone()

        cur.execute(
            "select min(checked_at), max(checked_at) from analytics.data_sanity_check"
        )
        oldest_checked_at, newest_checked_at = cur.fetchone()

        cur.execute(
            """
            select c.company_name, l.ticker, d.metric_name, d.our_value, d.external_value, d.pct_diff, d.note, d.checked_at
            from analytics.data_sanity_check d
            join core.company c on c.id = d.company_id
            left join core.listing l on l.company_id = c.id and l.effective_to is null and l.security_type = 'Common Stock'
            where d.severity in ('critical', 'major')
            order by (d.severity = 'critical') desc, abs(coalesce(d.pct_diff, 999999)) desc
            limit 25
            """
        )
        worst_rows = [
            {
                "company_name": r[0],
                "ticker": r[1],
                "metric_name": r[2],
                "our_value": r[3],
                "external_value": r[4],
                "pct_diff": r[5],
                "note": r[6],
                "checked_at": r[7],
            }
            for r in cur.fetchall()
        ]

        cur.execute(
            "select outcome, count(*) from analytics.data_sanity_investigation group by outcome"
        )
        investigation_counts = dict(cur.fetchall())

        cur.execute(
            """
            select c.company_name, l.ticker, i.concept_name, i.candidate_taxonomy, i.candidate_tag,
                   i.candidate_value, i.external_value, i.pct_diff_vs_external, i.outcome, i.note
            from analytics.data_sanity_investigation i
            join core.company c on c.id = i.company_id
            left join core.listing l on l.company_id = c.id and l.effective_to is null and l.security_type = 'Common Stock'
            where i.outcome in ('auto_fixed', 'needs_review')
            order by (i.outcome = 'auto_fixed') desc, i.investigated_at desc
            limit 25
            """
        )
        investigation_rows = [
            {
                "company_name": r[0],
                "ticker": r[1],
                "concept_name": r[2],
                "candidate_taxonomy": r[3],
                "candidate_tag": r[4],
                "candidate_value": r[5],
                "external_value": r[6],
                "pct_diff": r[7],
                "outcome": r[8],
                "note": r[9],
            }
            for r in cur.fetchall()
        ]

        cur.execute(
            "select severity, count(*) from analytics.data_freshness_check group by severity"
        )
        freshness_counts = dict(cur.fetchall())

        cur.execute(
            """
            select c.company_name, l.ticker, f.our_latest_period_end, f.yfinance_most_recent_quarter, f.days_stale
            from analytics.data_freshness_check f
            join core.company c on c.id = f.company_id
            left join core.listing l on l.company_id = c.id and l.effective_to is null and l.security_type = 'Common Stock'
            where f.severity = 'stale'
            order by f.days_stale desc
            limit 25
            """
        )
        stale_rows = [
            {
                "company_name": r[0],
                "ticker": r[1],
                "our_latest_period_end": r[2],
                "yfinance_most_recent_quarter": r[3],
                "days_stale": r[4],
            }
            for r in cur.fetchall()
        ]

    return {
        "companies_checked": companies_checked,
        "oldest_checked_at": oldest_checked_at,
        "newest_checked_at": newest_checked_at,
        "by_metric_severity": by_metric_severity,
        "worst_rows": worst_rows,
        "investigation_counts": investigation_counts,
        "investigation_rows": investigation_rows,
        "freshness_counts": freshness_counts,
        "stale_rows": stale_rows,
    }


def render_markdown(summary: dict) -> str:
    lines = ["# Data Sanity Layer report", ""]
    lines.append(
        f"Companies with at least one check: **{summary['companies_checked']}**"
    )
    lines.append(
        f"Oldest check: {summary['oldest_checked_at']} · Newest check: {summary['newest_checked_at']}"
    )
    lines.append("")
    lines.append("| Metric | " + " | ".join(SEVERITY_ORDER) + " |")
    lines.append("|---|" + "---|" * len(SEVERITY_ORDER))
    for metric_name, counts in sorted(summary["by_metric_severity"].items()):
        row = [metric_name] + [str(counts.get(s, 0)) for s in SEVERITY_ORDER]
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")

    if summary["worst_rows"]:
        lines.append("## Worst findings (critical/major, top 25)")
        lines.append("")
        lines.append(
            "| Company | Ticker | Metric | Our value | yfinance value | % diff | Note |"
        )
        lines.append("|---|---|---|---|---|---|---|")
        for row in summary["worst_rows"]:
            pct = f"{row['pct_diff']:.1f}%" if row["pct_diff"] is not None else "—"
            lines.append(
                f"| {row['company_name']} | {row['ticker'] or '—'} | {row['metric_name']} | "
                f"{row['our_value']} | {row['external_value']} | {pct} | {row['note'] or ''} |"
            )
    else:
        lines.append("No critical or major findings.")

    investigation_counts = summary.get("investigation_counts") or {}
    if investigation_counts:
        lines.append("")
        lines.append("## Investigation outcomes (tag-level fix attempts)")
        lines.append("")
        lines.append(
            f"Auto-fixed: **{investigation_counts.get('auto_fixed', 0)}** · "
            f"Needs human review: **{investigation_counts.get('needs_review', 0)}** · "
            f"No reconcilable tag found: **{investigation_counts.get('no_match_found', 0)}**"
        )
        investigation_rows = summary.get("investigation_rows") or []
        if investigation_rows:
            lines.append("")
            lines.append(
                "| Company | Ticker | Concept | Candidate tag | Candidate value | External value | % diff | Outcome |"
            )
            lines.append("|---|---|---|---|---|---|---|---|")
            for row in investigation_rows:
                pct = f"{row['pct_diff']:.1f}%" if row["pct_diff"] is not None else "—"
                tag = (
                    f"{row['candidate_taxonomy']}:{row['candidate_tag']}"
                    if row["candidate_tag"]
                    else "—"
                )
                lines.append(
                    f"| {row['company_name']} | {row['ticker'] or '—'} | {row['concept_name']} | {tag} | "
                    f"{row['candidate_value']} | {row['external_value']} | {pct} | {row['outcome']} |"
                )

    freshness_counts = summary.get("freshness_counts") or {}
    if freshness_counts:
        lines.append("")
        lines.append(
            "## Data freshness (doc 45 P0 -- is our latest data current, independent of whether it's correct)"
        )
        lines.append("")
        lines.append(
            f"Current: **{freshness_counts.get('ok', 0)}** · Stale: **{freshness_counts.get('stale', 0)}** · "
            f"Unknown: **{freshness_counts.get('unknown', 0)}**"
        )
        stale_rows = summary.get("stale_rows") or []
        if stale_rows:
            lines.append("")
            lines.append(
                "| Company | Ticker | Our latest period | yfinance's most recent quarter | Days stale |"
            )
            lines.append("|---|---|---|---|---|")
            for row in stale_rows:
                lines.append(
                    f"| {row['company_name']} | {row['ticker'] or '—'} | {row['our_latest_period_end']} | "
                    f"{row['yfinance_most_recent_quarter']} | {row['days_stale']} |"
                )

    return "\n".join(lines)


def should_fail_ci(summary: dict, max_major: int = 10) -> bool:
    """A single 'critical' row (the revenue-resolves-to-$0 shape, or any
    future check of similar severity) always fails the job -- these are
    named, specific, already-understood failure modes, not noise. 'major'
    rows only fail past a small count, since some real, expected drift
    (Alpaca delayed-SIP price vs. Yahoo's own feed, mid-batch during a
    volatile trading day) will occasionally cross the major threshold for
    a handful of companies without indicating a real pipeline bug."""
    critical_count = sum(
        counts.get("critical", 0) for counts in summary["by_metric_severity"].values()
    )
    major_count = sum(
        counts.get("major", 0) for counts in summary["by_metric_severity"].values()
    )
    return critical_count > 0 or major_count > max_major
