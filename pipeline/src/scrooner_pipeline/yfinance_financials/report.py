"""Reads back analytics.statement_comparison_finding for a human-readable
summary -- read-only, safe to run any time."""

import psycopg

SEVERITY_ORDER = ["major", "minor", "missing_ours", "ok"]


def summarize(conn: psycopg.Connection) -> dict:
    with conn.cursor() as cur:
        cur.execute(
            """
            select cc.name, f.severity, count(*)
            from analytics.statement_comparison_finding f
            join analytics.canonical_concept cc on cc.id = f.canonical_concept_id
            group by cc.name, f.severity
            """
        )
        by_concept_severity: dict[str, dict[str, int]] = {}
        for concept_name, severity, count in cur.fetchall():
            by_concept_severity.setdefault(concept_name, {})[severity] = count

        cur.execute(
            "select count(distinct company_id) from analytics.statement_comparison_finding"
        )
        (companies_checked,) = cur.fetchone()

        cur.execute(
            """
            select c.company_name, l.ticker, cc.name, f.period_end, f.our_value, f.yfinance_value,
                   f.yfinance_line_item, f.pct_diff, f.note
            from analytics.statement_comparison_finding f
            join core.company c on c.id = f.company_id
            join analytics.canonical_concept cc on cc.id = f.canonical_concept_id
            left join core.listing l on l.company_id = c.id and l.effective_to is null and l.security_type = 'Common Stock'
            where f.severity = 'major'
            order by abs(coalesce(f.pct_diff, 999999)) desc
            limit 40
            """
        )
        worst_rows = [
            {
                "company_name": r[0],
                "ticker": r[1],
                "concept_name": r[2],
                "period_end": r[3],
                "our_value": r[4],
                "yfinance_value": r[5],
                "yfinance_line_item": r[6],
                "pct_diff": r[7],
                "note": r[8],
            }
            for r in cur.fetchall()
        ]

    return {
        "companies_checked": companies_checked,
        "by_concept_severity": by_concept_severity,
        "worst_rows": worst_rows,
    }


def render_markdown(summary: dict) -> str:
    lines = ["# yfinance Financial Statements comparison report", ""]
    lines.append(f"Companies checked: **{summary['companies_checked']}**")
    lines.append("")
    lines.append("| Concept | " + " | ".join(SEVERITY_ORDER) + " |")
    lines.append("|---|" + "---|" * len(SEVERITY_ORDER))
    for concept_name, counts in sorted(summary["by_concept_severity"].items()):
        row = [concept_name] + [str(counts.get(s, 0)) for s in SEVERITY_ORDER]
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")

    if summary["worst_rows"]:
        lines.append(
            "## Major findings (unexplained, i.e. no bank-incompatibility note), worst first"
        )
        lines.append("")
        lines.append(
            "| Company | Ticker | Concept | Period | Our value | yfinance value (line item) | % diff | Note |"
        )
        lines.append("|---|---|---|---|---|---|---|---|")
        for row in summary["worst_rows"]:
            pct = f"{row['pct_diff']:.1f}%" if row["pct_diff"] is not None else "—"
            lines.append(
                f"| {row['company_name']} | {row['ticker'] or '—'} | {row['concept_name']} | {row['period_end']} | "
                f"{row['our_value']} | {row['yfinance_value']} ({row['yfinance_line_item']}) | {pct} | {row['note'] or ''} |"
            )
    else:
        lines.append("No major findings.")

    return "\n".join(lines)
