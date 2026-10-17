from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.shortcuts import render

from coverage.services import load_coverage_dashboard
from operations.models import WorkItem


def health(_request):
    return JsonResponse({"status": "ok", "service": "scrooner-admin"})


@staff_member_required
def overview(request):
    coverage = load_coverage_dashboard(days=14, metric_limit=8)
    work = {
        "ready": WorkItem.objects.filter(status="ready").count(),
        "active": WorkItem.objects.filter(status__in=["claimed", "investigating", "fix_proposed", "verifying"]).count(),
        "approval": WorkItem.objects.filter(status="awaiting_approval").count(),
        "escalated": WorkItem.objects.filter(status="escalated").count(),
    }
    return render(request, "cockpit/overview.html", {"coverage": coverage, "work": work})
