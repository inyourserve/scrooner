from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.http import Http404
from django.shortcuts import render
from django.db.models import Q

from .models import AuditEvent, CommandRequest, Investigation, WorkItem
from .services import company_detail, mapping_dashboard, pipeline_dashboard, quality_dashboard, search_companies
from .ticket_analytics import OPEN_STATUSES, ticket_analytics


@staff_member_required
def pipeline(request):
    return render(request, "operations/pipeline.html", pipeline_dashboard())


@staff_member_required
def quality(request):
    return render(request, "operations/quality.html", quality_dashboard())


@staff_member_required
def companies(request):
    query = request.GET.get("q", "")
    return render(request, "operations/companies.html", {"query": query, "companies": search_companies(query)})


@staff_member_required
def company(request, company_id):
    context = company_detail(company_id)
    if context is None:
        raise Http404("Company not found")
    return render(request, "operations/company.html", context)


@staff_member_required
def mappings(request):
    return render(request, "operations/mappings.html", {"concepts": mapping_dashboard()})


@staff_member_required
def commands(request):
    return render(request, "operations/commands.html", {
        "commands": CommandRequest.objects.select_related("requested_by", "approved_by")[:100],
        "execution_enabled": settings.OPS_COMMAND_EXECUTION_ENABLED,
    })


@staff_member_required
def activity(request):
    day = request.GET.get("date", "")[:10]
    events = AuditEvent.objects.select_related("actor")
    if day:
        events = events.filter(created_at__date=day)
    return render(request, "operations/activity.html", {
        "events": events[:200],
        "day": day,
        "open_investigations": Investigation.objects.exclude(status__in=["resolved", "wont_fix"]).count(),
    })


@staff_member_required
def work_queue(request):
    status = request.GET.get("status", "")
    items = WorkItem.objects.all()
    if status in WorkItem.Status.values:
        items = items.filter(status=status)
    counts = {value: WorkItem.objects.filter(status=value).count() for value in WorkItem.Status.values}
    return render(request, "operations/work_queue.html", {"items": items[:200], "counts": counts, "selected_status": status, "statuses": WorkItem.Status.choices})


@staff_member_required
def work_item(request, item_id):
    item = WorkItem.objects.prefetch_related("attempts", "evidence").filter(pk=item_id).first()
    if item is None:
        raise Http404("Work item not found")
    return render(request, "operations/work_item.html", {"item": item})


@staff_member_required
def tickets(request):
    state = request.GET.get("state", "open")
    query = request.GET.get("q", "").strip()[:120]
    items = WorkItem.objects.all()
    if state == "open":
        items = items.filter(status__in=OPEN_STATUSES)
    elif state == "closed":
        items = items.filter(status=WorkItem.Status.RESOLVED)
    elif state in WorkItem.Status.values:
        items = items.filter(status=state)
    if query:
        items = items.filter(Q(title__icontains=query) | Q(source_type__icontains=query) | Q(source_id__icontains=query))
    open_count = WorkItem.objects.filter(status__in=OPEN_STATUSES).count()
    closed_count = WorkItem.objects.filter(status=WorkItem.Status.RESOLVED).count()
    total_count = open_count + closed_count
    return render(request, "operations/tickets.html", {
        "items": items[:200], "selected_state": state, "query": query,
        "open_count": open_count,
        "closed_count": closed_count,
        "close_rate": (closed_count / total_count * 100) if total_count else 0,
        "critical_count": WorkItem.objects.filter(status__in=OPEN_STATUSES, severity=WorkItem.Severity.CRITICAL).count(),
    })


@staff_member_required
def ticket_analytics_view(request):
    try:
        days = int(request.GET.get("days", "30"))
    except ValueError:
        days = 30
    return render(request, "operations/ticket_analytics.html", {"analytics": ticket_analytics(days)})
