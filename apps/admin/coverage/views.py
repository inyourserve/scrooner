from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render

from .services import load_coverage_dashboard


@staff_member_required
def dashboard(request):
    try:
        days = int(request.GET.get("days", "90"))
    except ValueError:
        days = 90
    return render(request, "coverage/dashboard.html", {"coverage": load_coverage_dashboard(days=days), "days": max(7, min(days, 365))})
