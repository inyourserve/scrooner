from django.urls import path

from . import views
from . import worker_api

app_name = "operations"
urlpatterns = [
    path("pipeline/", views.pipeline, name="pipeline"),
    path("quality/", views.quality, name="quality"),
    path("companies/", views.companies, name="companies"),
    path("companies/<int:company_id>/", views.company, name="company"),
    path("mappings/", views.mappings, name="mappings"),
    path("commands/", views.commands, name="commands"),
    path("activity/", views.activity, name="activity"),
    path("work/", views.work_queue, name="work-queue"),
    path("work/<int:item_id>/", views.work_item, name="work-item"),
    path("tickets/", views.tickets, name="tickets"),
    path("tickets/analytics/", views.ticket_analytics_view, name="ticket-analytics"),
    path("worker/v1/claim/", worker_api.claim, name="worker-claim"),
    path("worker/v1/items/<int:item_id>/heartbeat/", worker_api.heartbeat_view, name="worker-heartbeat"),
    path("worker/v1/items/<int:item_id>/evidence/", worker_api.evidence, name="worker-evidence"),
    path("worker/v1/items/<int:item_id>/transition/", worker_api.transition_view, name="worker-transition"),
]
