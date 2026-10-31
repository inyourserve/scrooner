"""Reads back analytics.data_sanity_check for a human-readable summary --
the "report it" half of the Data Sanity Layer. Read-only, no fetch, no
pacing concerns; safe to run as often as wanted.

Deliberately does not judge the pipeline's overall health from a single
number -- returns the breakdown by severity AND the worst individual rows,
since a CI job (.github/workflows/pipeline-sanity.yml) wants both: a
GITHUB_STEP_SUMMARY-friendly table, and a decision of whether to fail the
job (when critical/major counts regress against the last passing run's
baseline -- see find_regressions())."""

from datetime import date

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


# Rows are re-checked in rotating batches (`run --limit`), so severity
# counts drift a little between runs even when nothing regressed. Criticals
# get zero tolerance; majors may rise by the larger of these before failing.
MAJOR_TOLERANCE_MIN = 25
MAJOR_TOLERANCE_PCT = 5.0


def _major_tolerance(baseline_count: int) -> int:
    return max(MAJOR_TOLERANCE_MIN, int(baseline_count * MAJOR_TOLERANCE_PCT / 100))


EVALUATED = ("ok", "minor", "major", "critical")  # rows where both sides had a value

# A coverage loss (our value gone: missing_ours rising) fails the gate like a new major, with the same rotation
# tolerance. One-time transition: 3c42fe1 made the newest snapshot decide (a NULL newest is missing_ours, no fallback
# to an older value), which moves these stored evaluated rows to missing_ours as their companies rotate (read-only
# count 2026-10-31 over analytics.data_sanity_check: 5,288 rows, 3,236 of them majors). The allowance covers exactly
# that move and expires after two full rotations (750 of ~5,100 companies a night), so it cannot hide a later loss.
MISSING_OURS_TRANSITION = {
    "current_ratio": 148, "debt_to_equity": 731, "dividend_yield": 3, "ebitda": 701, "ebitda_margin": 453,
    "ev_ebitda": 485, "ev_sales": 100, "gross_margin": 679, "institutional_ownership_pct": 18, "net_margin": 498,
    "operating_margin": 336, "payout_ratio": 458, "peg_ratio": 110, "price_to_book": 1, "price_to_sales": 4,
    "quick_ratio": 150, "revenue_growth_yoy": 330, "roa": 39, "roe": 41, "trailing_pe": 3,
}  # fmt: skip
MISSING_OURS_TRANSITION_UNTIL = date(2026, 11, 14)


def _transition(metric: str | None, today: date) -> int:
    if today > MISSING_OURS_TRANSITION_UNTIL:
        return 0
    if metric is None:
        return sum(MISSING_OURS_TRANSITION.values())
    return MISSING_OURS_TRANSITION.get(metric, 0)


def major_rate(counts: dict[str, int]) -> float | None:
    """Majors among the rows that were actually evaluated (missing_ours / missing_external excluded): the gate counts
    majors against ALL rows, so more coverage (fewer missing_ours) reads as a regression; the rate does not."""
    evaluated = sum(counts.get(k, 0) for k in EVALUATED)
    return None if evaluated == 0 else counts.get("major", 0) / evaluated


def _rate_text(now: dict[str, int], was: dict[str, int]) -> str:
    r_now, r_was = major_rate(now), major_rate(was)
    if r_now is None or r_was is None:
        return ""
    return f" [major rate among evaluated: {r_was:.1%} -> {r_now:.1%}]"


def major_rate_lines(
    summary: dict, baseline: dict[str, dict[str, int]] | None
) -> list[str]:
    """Per metric: evaluated rows and the major rate, now and (when a baseline exists) at the baseline."""
    lines = []
    for metric, counts in sorted(summary["by_metric_severity"].items()):
        rate = major_rate(counts)
        if rate is None:
            continue
        evaluated = sum(counts.get(k, 0) for k in EVALUATED)
        text = f"{metric}: major {counts.get('major', 0)} of {evaluated} evaluated ({rate:.1%})"
        was = (baseline or {}).get(metric)
        if was and major_rate(was) is not None:
            text += f"; baseline {was.get('major', 0)} of {sum(was.get(k, 0) for k in EVALUATED)} ({major_rate(was):.1%})"
        lines.append(text)
    return lines


def find_regressions(
    summary: dict,
    baseline: dict[str, dict[str, int]] | None,
    today: date | None = None,
) -> list[str]:
    """Compares current severity counts against the last passing run's
    baseline (analytics.data_sanity_gate_baseline) and returns one line per
    regression; an empty list means the gate passes. No baseline yet means
    nothing to regress from -- the first run just establishes one.

    Replaced a fixed "any critical or >10 major" threshold (2026-09-27): the
    existing backlog (~18,000 major rows) meant that gate could never pass,
    so it carried no signal. Fails on: any increase in total criticals, a
    critical in a metric that had none, or majors or missing_ours (a coverage
    loss) rising past the rotation tolerance -- in total or for any single
    metric. missing_ours also gets the one-time 3c42fe1 transition allowance."""
    if baseline is None:
        return []
    today = today or date.today()

    def total(counts: dict[str, dict[str, int]], severity: str) -> int:
        return sum(c.get(severity, 0) for c in counts.values())

    current = summary["by_metric_severity"]
    regressions: list[str] = []

    now_critical, was_critical = total(current, "critical"), total(baseline, "critical")
    if now_critical > was_critical:
        regressions.append(f"critical: {was_critical} -> {now_critical}")
    for metric, counts in sorted(current.items()):
        if (
            counts.get("critical", 0) > 0
            and baseline.get(metric, {}).get("critical", 0) == 0
        ):
            regressions.append(
                f"{metric}: new critical findings ({counts['critical']})"
            )

    now_major, was_major = total(current, "major"), total(baseline, "major")
    if now_major - was_major > _major_tolerance(was_major):
        regressions.append(
            f"major (all metrics): {was_major} -> {now_major}"
            + _rate_text(
                {k: total(current, k) for k in EVALUATED},
                {k: total(baseline, k) for k in EVALUATED},
            )
        )
    for metric, counts in sorted(current.items()):
        was = baseline.get(metric, {}).get("major", 0)
        now = counts.get("major", 0)
        if now - was > _major_tolerance(was):
            regressions.append(
                f"{metric} major: {was} -> {now}"
                + _rate_text(counts, baseline.get(metric, {}))
            )

    now_missing, was_missing = (
        total(current, "missing_ours"),
        total(baseline, "missing_ours"),
    )
    if now_missing - was_missing > _major_tolerance(was_missing) + _transition(
        None, today
    ):
        regressions.append(
            f"missing_ours (all metrics, coverage loss): {was_missing} -> {now_missing}"
        )
    for metric, counts in sorted(current.items()):
        was = baseline.get(metric, {}).get("missing_ours", 0)
        now = counts.get("missing_ours", 0)
        if now - was > _major_tolerance(was) + _transition(metric, today):
            regressions.append(f"{metric} missing_ours (coverage loss): {was} -> {now}")

    return regressions


def load_baseline(conn: psycopg.Connection) -> dict[str, dict[str, int]] | None:
    with conn.cursor() as cur:
        cur.execute(
            """
            select metric_name, severity, count
            from analytics.data_sanity_gate_baseline
            where recorded_at = (select max(recorded_at) from analytics.data_sanity_gate_baseline)
            """
        )
        rows = cur.fetchall()
    if not rows:
        return None
    baseline: dict[str, dict[str, int]] = {}
    for metric_name, severity, count in rows:
        baseline.setdefault(metric_name, {})[severity] = count
    return baseline


def record_baseline(conn: psycopg.Connection, summary: dict) -> None:
    """One batched insert, all rows sharing a single recorded_at."""
    rows = [
        (metric_name, severity, count)
        for metric_name, counts in summary["by_metric_severity"].items()
        for severity, count in counts.items()
    ]
    with conn.cursor() as cur:
        cur.execute("select now()")
        (recorded_at,) = cur.fetchone()
        cur.executemany(
            """
            insert into analytics.data_sanity_gate_baseline
                (recorded_at, metric_name, severity, count)
            values (%s, %s, %s, %s)
            """,
            [(recorded_at, *row) for row in rows],
        )
    conn.commit()
