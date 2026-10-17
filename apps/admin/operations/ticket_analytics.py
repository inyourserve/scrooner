from datetime import timedelta
from statistics import median

from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from django.utils import timezone

from coverage.services import load_coverage_dashboard

from .models import WorkItem


OPEN_STATUSES = tuple(value for value in WorkItem.Status.values if value != WorkItem.Status.RESOLVED)


def ticket_analytics(days=30):
    days = max(7, min(int(days), 365))
    today = timezone.localdate()
    start = today - timedelta(days=days - 1)

    created = {
        row["day"]: row["count"]
        for row in WorkItem.objects.filter(first_seen_at__date__gte=start)
        .annotate(day=TruncDate("first_seen_at"))
        .values("day").annotate(count=Count("id"))
    }
    resolved = {
        row["day"]: row["count"]
        for row in WorkItem.objects.filter(resolved_at__date__gte=start)
        .annotate(day=TruncDate("resolved_at"))
        .values("day").annotate(count=Count("id"))
    }
    coverage = load_coverage_dashboard(days=days, metric_limit=1)
    coverage_by_date = {row["date"]: row for row in coverage["history"]}

    rows = []
    running_open = WorkItem.objects.filter(first_seen_at__date__lt=start).exclude(
        resolved_at__date__lt=start
    ).count()
    previous_coverage = None
    for offset in range(days):
        day = start + timedelta(days=offset)
        opened = created.get(day, 0)
        closed = resolved.get(day, 0)
        running_open += opened - closed
        snapshot = coverage_by_date.get(day)
        score = snapshot["metric"] if snapshot else None
        delta = None if score is None or previous_coverage is None else score - previous_coverage
        if score is not None:
            previous_coverage = score
        rows.append({
            "date": day,
            "opened": opened,
            "closed": closed,
            "open_end": max(running_open, 0),
            "coverage": score,
            "coverage_delta": delta,
            "coverage_per_close": (delta / closed) if delta is not None and closed else None,
        })

    all_items = WorkItem.objects.all()
    open_items = all_items.filter(status__in=OPEN_STATUSES)
    resolved_items = all_items.filter(status=WorkItem.Status.RESOLVED)
    total = all_items.count()
    closed_total = resolved_items.count()
    open_total = open_items.count()
    active_statuses = (WorkItem.Status.CLAIMED, WorkItem.Status.INVESTIGATING, WorkItem.Status.FIX_PROPOSED, WorkItem.Status.VERIFYING)
    seven_days_ago = today - timedelta(days=6)
    opened_last_7 = all_items.filter(first_seen_at__date__gte=seven_days_ago).count()
    closed_last_7 = resolved_items.filter(resolved_at__date__gte=seven_days_ago).count()
    durations = [
        (resolved_at - first_seen_at).total_seconds() / 3600
        for first_seen_at, resolved_at in resolved_items.exclude(resolved_at=None).values_list("first_seen_at", "resolved_at")
    ]
    oldest = open_items.order_by("first_seen_at").values_list("first_seen_at", flat=True).first()
    evidence_count = resolved_items.filter(evidence__isnull=False).distinct().count()
    resolution_count = resolved_items.exclude(resolution={}).count()
    status_breakdown = [
        {"status": row["status"], "label": WorkItem.Status(row["status"]).label, "count": row["count"], "pct": row["count"] / total * 100 if total else 0}
        for row in all_items.values("status").annotate(count=Count("id")).order_by("-count")
    ]
    severity_breakdown = [
        {"severity": row["severity"], "label": WorkItem.Severity(row["severity"]).label, "count": row["count"], "pct": row["count"] / open_total * 100 if open_total else 0}
        for row in open_items.values("severity").annotate(count=Count("id")).order_by("-count")
    ]
    source_breakdown = []
    for row in all_items.values("source_type").annotate(
        total=Count("id"),
        open=Count("id", filter=Q(status__in=OPEN_STATUSES)),
        closed=Count("id", filter=Q(status=WorkItem.Status.RESOLVED)),
    ).order_by("-open", "source_type"):
        row["close_rate"] = row["closed"] / row["total"] * 100 if row["total"] else 0
        source_breakdown.append(row)
    aging = [
        {"label": "Under 1 day", "count": open_items.filter(first_seen_at__date=today).count()},
        {"label": "1–3 days", "count": open_items.filter(first_seen_at__date__gte=today - timedelta(days=2), first_seen_at__date__lt=today).count()},
        {"label": "3–7 days", "count": open_items.filter(first_seen_at__date__gte=today - timedelta(days=6), first_seen_at__date__lt=today - timedelta(days=2)).count()},
        {"label": "7–30 days", "count": open_items.filter(first_seen_at__date__gte=today - timedelta(days=29), first_seen_at__date__lt=today - timedelta(days=6)).count()},
        {"label": "Over 30 days", "count": open_items.filter(first_seen_at__date__lt=today - timedelta(days=29)).count()},
    ]
    return {
        "days": days,
        "rows": list(reversed(rows)),
        "summary": {
            "total": total,
            "open": open_total,
            "closed": closed_total,
            "close_rate": (closed_total / total * 100) if total else 0,
            "opened_window": sum(created.values()),
            "closed_window": sum(resolved.values()),
            "active": open_items.filter(status__in=active_statuses).count(),
            "unassigned": open_items.filter(assigned_worker="").count(),
            "oldest_open_days": (today - oldest.date()).days if oldest else None,
            "opened_last_7": opened_last_7,
            "closed_last_7": closed_last_7,
            "net_last_7": opened_last_7 - closed_last_7,
            "median_close_hours": median(durations) if durations else None,
            "resolved_with_resolution": resolution_count,
            "resolved_with_evidence": evidence_count,
            "resolution_evidence_pct": evidence_count / closed_total * 100 if closed_total else 0,
            "estimated_clear_days": (open_total / (closed_last_7 / 7)) if closed_last_7 else None,
            "coverage": coverage.get("latest", {}).get("metric") if coverage.get("latest") else None,
            "coverage_change": (
                coverage["latest"]["metric"] - coverage["history"][-1]["metric"]
                if len(coverage["history"]) > 1 and coverage["latest"]["metric"] is not None and coverage["history"][-1]["metric"] is not None
                else None
            ),
        },
        "status_breakdown": status_breakdown,
        "severity_breakdown": severity_breakdown,
        "source_breakdown": source_breakdown,
        "aging": aging,
    }
