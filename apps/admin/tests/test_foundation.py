from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.exceptions import ValidationError

from operations.models import AuditEvent, CommandRequest, WorkEvidence, WorkItem
from operations.workflows import review_command, submit_command
from operations.work_queue import fingerprint


@pytest.mark.django_db
def test_health_is_public_and_identifies_the_service(client):
    response = client.get(reverse("health"))
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "scrooner-admin"}
    assert response.headers["X-Request-ID"]


@pytest.mark.django_db
def test_overview_requires_staff_authentication(client):
    response = client.get(reverse("cockpit:overview"))
    assert response.status_code == 302
    assert response.url.startswith("/admin/login/")


@pytest.mark.django_db
def test_staff_can_open_the_overview(client):
    user = get_user_model().objects.create_user("operator", password="safe-test-password", is_staff=True)
    client.force_login(user)
    empty = {"latest": None, "previous": None, "history": [], "weakest": []}
    with patch("cockpit.views.load_coverage_dashboard", return_value=empty):
        response = client.get(reverse("cockpit:overview"))
    assert response.status_code == 200
    assert b"System overview" in response.content
    assert b"Agent work queue" in response.content


@pytest.mark.django_db
def test_operations_pages_require_staff(client):
    for name in ("operations:pipeline", "operations:quality", "operations:companies", "operations:mappings", "operations:commands", "operations:activity", "operations:tickets", "operations:ticket-analytics"):
        response = client.get(reverse(name))
        assert response.status_code == 302


@pytest.mark.django_db
def test_ticket_section_separates_open_and_closed_work(client):
    user = get_user_model().objects.create_user("ticket-operator", password="safe-test-password", is_staff=True)
    client.force_login(user)
    WorkItem.objects.create(fingerprint=fingerprint("finding", "open"), source_type="finding", source_id="open", title="Open issue")
    WorkItem.objects.create(fingerprint=fingerprint("finding", "closed"), source_type="finding", source_id="closed", title="Closed issue", status=WorkItem.Status.RESOLVED)

    response = client.get(reverse("operations:tickets"))
    assert response.status_code == 200
    assert b"Open issue" in response.content
    assert b"Closed issue" not in response.content
    assert b"Closed so far" in response.content


@pytest.mark.django_db
def test_ticket_analytics_reports_flow_and_coverage_impact(client):
    user = get_user_model().objects.create_user("analytics-operator", password="safe-test-password", is_staff=True)
    client.force_login(user)
    WorkItem.objects.create(fingerprint=fingerprint("finding", "1"), source_type="finding", source_id="1", title="Resolved", status=WorkItem.Status.RESOLVED, resolved_at=__import__("django.utils.timezone", fromlist=["now"]).now())
    today = __import__("django.utils.timezone", fromlist=["localdate"]).localdate()
    coverage = {"latest": {"metric": 72.5}, "history": [{"date": today, "metric": 72.5}, {"date": today - __import__("datetime").timedelta(days=1), "metric": 72.0}], "weakest": []}
    with patch("operations.ticket_analytics.load_coverage_dashboard", return_value=coverage):
        response = client.get(reverse("operations:ticket-analytics") + "?days=14")
    assert response.status_code == 200
    assert b"Ticket and coverage impact" in response.content
    assert b"72.5%" in response.content
    assert b"Closed so far" in response.content


@pytest.mark.django_db
def test_command_requires_independent_approval():
    users = get_user_model()
    requester = users.objects.create_user("requester", password="safe-test-password", is_staff=True)
    reviewer = users.objects.create_user("reviewer", password="safe-test-password", is_staff=True)
    permission = __import__("django.contrib.auth.models", fromlist=["Permission"]).Permission.objects.get(codename="approve_commandrequest")
    requester.user_permissions.add(permission)
    reviewer.user_permissions.add(permission)
    command = CommandRequest.objects.create(command_type="coverage_snapshot", parameters={}, reason="Refresh dashboard", requested_by=requester)
    submit_command(command.pk, requester)
    with pytest.raises(ValidationError):
        review_command(command.pk, requester, approve=True)
    approved = review_command(command.pk, reviewer, approve=True)
    assert approved.status == CommandRequest.Status.APPROVED
    assert AuditEvent.objects.filter(target_id=str(command.pk)).count() == 2


@pytest.mark.django_db
def test_worker_api_claims_records_evidence_and_resolves(client, settings):
    settings.OPS_WORKER_TOKEN = "test-worker-secret"
    item = WorkItem.objects.create(fingerprint=fingerprint("mapper_error", "42"), source_type="mapper_error", source_id="42", title="Wrong revenue mapping", severity="high", priority=90, payload={"ticker": "AAPL"})
    headers = {"HTTP_AUTHORIZATION": "Bearer test-worker-secret", "content_type": "application/json"}
    response = client.post(reverse("operations:worker-claim"), data='{"worker_id":"solver-1"}', **headers)
    assert response.status_code == 200
    lease = response.json()["work_item"]["lease_token"]
    assert client.post(reverse("operations:worker-claim"), data='{"worker_id":"solver-2"}', **headers).json()["work_item"] is None
    transition_url = reverse("operations:worker-transition", args=[item.pk])
    evidence_url = reverse("operations:worker-evidence", args=[item.pk])
    assert client.post(transition_url, data=f'{{"worker_id":"solver-1","lease_token":"{lease}","status":"investigating"}}', **headers).status_code == 200
    assert client.post(evidence_url, data=f'{{"worker_id":"solver-1","lease_token":"{lease}","kind":"root_cause","summary":"Incorrect tag priority"}}', **headers).status_code == 201
    assert client.post(transition_url, data=f'{{"worker_id":"solver-1","lease_token":"{lease}","status":"verifying"}}', **headers).status_code == 200
    assert client.post(transition_url, data=f'{{"worker_id":"solver-1","lease_token":"{lease}","status":"resolved","summary":"Backfill verified","result":{{"checks_passed":12}}}}', **headers).status_code == 200
    item.refresh_from_db()
    assert item.status == WorkItem.Status.RESOLVED
    assert item.resolution == {"checks_passed": 12}
    assert WorkEvidence.objects.filter(work_item=item, kind="root_cause").exists()


@pytest.mark.django_db
def test_worker_api_rejects_missing_token(client):
    response = client.post(reverse("operations:worker-claim"), data='{"worker_id":"solver-1"}', content_type="application/json")
    assert response.status_code == 401


@pytest.mark.django_db
def test_ingest_stores_a_json_string_payload_as_an_object():
    from operations.work_queue import ingest_work_item

    item, _ = ingest_work_item(
        source_type="company_finding", source_id="1", title="t", severity="high", priority=80,
        payload='{"ticker": "KVHI", "evidence": {"cause": "q4_not_derived"}}',
    )
    item.refresh_from_db()
    assert item.payload["evidence"]["cause"] == "q4_not_derived"


@pytest.mark.django_db
def test_auto_resolve_closes_only_ready_items_whose_source_is_no_longer_open():
    from operations.work_queue import auto_resolve_closed_sources

    def make(source_id, status=WorkItem.Status.READY, source_type="company_finding"):
        return WorkItem.objects.create(
            fingerprint=fingerprint(source_type, source_id), source_type=source_type,
            source_id=source_id, title=source_id, status=status,
        )

    still_open = make("1")
    closed = make("2")
    leased = make("3", status=WorkItem.Status.INVESTIGATING)
    other_type = make("9", source_type="mapper_error")  # no listing for this type: left alone

    resolved = auto_resolve_closed_sources({"company_finding": {"1"}})

    assert resolved == 1
    for item in (still_open, closed, leased, other_type):
        item.refresh_from_db()
    assert closed.status == WorkItem.Status.RESOLVED and closed.resolution["auto_resolved"]
    assert still_open.status == WorkItem.Status.READY
    assert leased.status == WorkItem.Status.INVESTIGATING
    assert other_type.status == WorkItem.Status.READY
    assert AuditEvent.objects.filter(event_type="work.auto_resolved", target_id=str(closed.pk)).exists()
