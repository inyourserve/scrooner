from django.db import connections


def load_coverage_dashboard(days: int = 90, metric_limit: int = 20) -> dict:
    days = max(7, min(days, 365))
    metric_limit = max(1, min(metric_limit, 100))
    with connections["warehouse"].cursor() as cursor:
        cursor.execute(
            """
            select snapshot_date,
                   max(coverage_pct) filter (where item_name = 'avg_metric_coverage_score'),
                   max(coverage_pct) filter (where item_name = 'avg_core_v1_metric_coverage_score'),
                   max(coverage_pct) filter (where item_name = 'avg_concept_coverage_score'),
                   max(total_active_companies)
            from analytics.coverage_snapshot
            where item_type = 'score'
            group by snapshot_date
            order by snapshot_date desc
            limit %s
            """,
            [days],
        )
        history = [
            {"date": row[0], "metric": row[1], "core": row[2], "concept": row[3], "companies": row[4]}
            for row in cursor.fetchall()
        ]
        cursor.execute(
            """
            with latest as (select max(snapshot_date) as snapshot_date from analytics.coverage_snapshot)
            select item_name, companies_covered, total_active_companies, coverage_pct
            from analytics.coverage_snapshot, latest
            where analytics.coverage_snapshot.snapshot_date = latest.snapshot_date
              and item_type = 'metric'
            order by coverage_pct asc, item_name
            limit %s
            """,
            [metric_limit],
        )
        weakest = [
            {"name": row[0], "covered": row[1], "total": row[2], "coverage": row[3]}
            for row in cursor.fetchall()
        ]
    latest = history[0] if history else None
    previous = history[1] if len(history) > 1 else None
    return {"latest": latest, "previous": previous, "history": history, "weakest": weakest}
