import hashlib
import json
import uuid
from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import connection, transaction
from django.db.models import Max, Q
from django.utils import timezone

from .models import AuditEvent, WorkAttempt, WorkEvidence, WorkItem


ACTIVE_STATES = {WorkItem.Status.CLAIMED, WorkItem.Status.INVESTIGATING, WorkItem.Status.FIX_PROPOSED, WorkItem.Status.VERIFYING}
WORKER_TRANSITIONS = {
    WorkItem.Status.CLAIMED: {WorkItem.Status.INVESTIGATING, WorkItem.Status.ESCALATED, WorkItem.Status.FAILED},
    WorkItem.Status.INVESTIGATING: {WorkItem.Status.FIX_PROPOSED, WorkItem.Status.VERIFYING, WorkItem.Status.ESCALATED, WorkItem.Status.FAILED},
    WorkItem.Status.FIX_PROPOSED: {WorkItem.Status.AWAITING_APPROVAL, WorkItem.Status.VERIFYING, WorkItem.Status.ESCALATED},
    WorkItem.Status.VERIFYING: {WorkItem.Status.RESOLVED, WorkItem.Status.INVESTIGATING, WorkItem.Status.ESCALATED, WorkItem.Status.FAILED},
}


def fingerprint(source_type, source_id):
    return hashlib.sha256(f"{source_type}:{source_id}".encode()).hexdigest()


def _as_object(payload):
    """The warehouse driver returns jsonb as a JSON string; a worker reads the
    payload as an object (payload["evidence"]), so store it decoded."""
    if isinstance(payload, (str, bytes)):
        try:
            payload = json.loads(payload)
        except json.JSONDecodeError:
            return {"raw": payload.decode() if isinstance(payload, bytes) else payload}
    return payload if isinstance(payload, dict) else {"value": payload}


def ingest_work_item(*, source_type, source_id, title, severity, priority, payload):
    payload = _as_object(payload)
    key = fingerprint(source_type, source_id)
    item, created = WorkItem.objects.get_or_create(
        fingerprint=key,
        defaults={"source_type": source_type, "source_id": str(source_id), "title": title[:240], "severity": severity, "priority": priority, "payload": payload},
    )
    if not created and item.status not in {WorkItem.Status.RESOLVED, WorkItem.Status.ESCALATED}:
        item.title = title[:240]
        item.severity = severity
        item.priority = priority
        item.payload = payload
        item.save(update_fields=["title", "severity", "priority", "payload", "last_seen_at"])
    return item, created


@transaction.atomic
def claim_next(worker_id):
    now = timezone.now()
    eligible = WorkItem.objects.filter(
        Q(status=WorkItem.Status.READY) | Q(status__in=ACTIVE_STATES, lease_expires_at__lt=now)
    ).order_by("-priority", "first_seen_at")
    if connection.features.has_select_for_update_skip_locked:
        eligible = eligible.select_for_update(skip_locked=True)
    else:
        eligible = eligible.select_for_update()
    item = eligible.first()
    if item is None:
        return None, None
    token = uuid.uuid4()
    before = item.status
    item.status = WorkItem.Status.CLAIMED
    item.assigned_worker = worker_id
    item.lease_token = token
    item.last_heartbeat_at = now
    item.lease_expires_at = now + timedelta(seconds=settings.OPS_WORKER_LEASE_SECONDS)
    item.save(update_fields=["status", "assigned_worker", "lease_token", "last_heartbeat_at", "lease_expires_at", "last_seen_at"])
    number = (item.attempts.aggregate(value=Max("number"))["value"] or 0) + 1
    attempt = WorkAttempt.objects.create(work_item=item, number=number, worker_id=worker_id, lease_token=token)
    AuditEvent.objects.create(event_type="work.claimed", target_type="work_item", target_id=str(item.pk), before={"status": before}, after={"status": item.status}, metadata={"worker_id": worker_id, "attempt": number})
    return item, attempt


def _leased_item(item_id, worker_id, lease_token, *, lock=False):
    query = WorkItem.objects
    if lock:
        query = query.select_for_update()
    item = query.get(pk=item_id)
    if item.assigned_worker != worker_id or str(item.lease_token) != str(lease_token):
        raise ValidationError("This worker does not hold the active lease.")
    if not item.lease_expires_at or item.lease_expires_at <= timezone.now():
        raise ValidationError("The work lease has expired; claim the item again.")
    return item


@transaction.atomic
def heartbeat(item_id, worker_id, lease_token):
    item = _leased_item(item_id, worker_id, lease_token, lock=True)
    now = timezone.now()
    item.last_heartbeat_at = now
    item.lease_expires_at = now + timedelta(seconds=settings.OPS_WORKER_LEASE_SECONDS)
    item.save(update_fields=["last_heartbeat_at", "lease_expires_at", "last_seen_at"])
    return item


@transaction.atomic
def add_evidence(item_id, worker_id, lease_token, *, kind, summary, data=None, artifact_url=""):
    item = _leased_item(item_id, worker_id, lease_token, lock=True)
    attempt = item.attempts.filter(lease_token=lease_token).order_by("-number").first()
    return WorkEvidence.objects.create(work_item=item, attempt=attempt, kind=kind[:40], summary=summary, data=data or {}, artifact_url=artifact_url, created_by=worker_id)


@transaction.atomic
def transition(item_id, worker_id, lease_token, *, status, summary="", result=None):
    item = _leased_item(item_id, worker_id, lease_token, lock=True)
    if status not in WORKER_TRANSITIONS.get(item.status, set()):
        raise ValidationError(f"Transition from {item.status} to {status} is not allowed.")
    before = item.status
    item.status = status
    if result:
        if status == WorkItem.Status.RESOLVED:
            item.resolution = result
        else:
            item.impact = {**item.impact, **result}
    if status in {WorkItem.Status.RESOLVED, WorkItem.Status.ESCALATED, WorkItem.Status.FAILED, WorkItem.Status.AWAITING_APPROVAL}:
        item.lease_expires_at = None
        item.lease_token = None
        item.assigned_worker = ""
    if status == WorkItem.Status.RESOLVED:
        item.resolved_at = timezone.now()
    item.save()
    attempt = item.attempts.filter(lease_token=lease_token).order_by("-number").first()
    if attempt and status in {WorkItem.Status.RESOLVED, WorkItem.Status.ESCALATED, WorkItem.Status.FAILED, WorkItem.Status.AWAITING_APPROVAL}:
        attempt.status = status
        attempt.summary = summary
        attempt.finished_at = timezone.now()
        attempt.save(update_fields=["status", "summary", "finished_at"])
    AuditEvent.objects.create(event_type=f"work.{status}", target_type="work_item", target_id=str(item.pk), before={"status": before}, after={"status": status}, metadata={"worker_id": worker_id, "summary": summary})
    return item


@transaction.atomic
def auto_resolve_closed_sources(open_ids_by_type):
    """Resolve READY items whose source row has since closed in the warehouse.

    `open_ids_by_type` maps source_type -> set of source ids that are still
    open there. Only unclaimed READY items are touched: a leased item is a
    worker's to finish, and a source type we got no listing for is left alone
    rather than treated as "everything closed"."""
    resolved = 0
    now = timezone.now()
    for source_type, open_ids in open_ids_by_type.items():
        stale = WorkItem.objects.select_for_update().filter(
            source_type=source_type, status=WorkItem.Status.READY
        ).exclude(source_id__in=open_ids)
        for item in stale:
            item.status = WorkItem.Status.RESOLVED
            item.resolved_at = now
            item.resolution = {"auto_resolved": "source finding is no longer open in the warehouse"}
            item.save(update_fields=["status", "resolved_at", "resolution", "last_seen_at"])
            AuditEvent.objects.create(
                event_type="work.auto_resolved",
                target_type="work_item",
                target_id=str(item.pk),
                before={"status": WorkItem.Status.READY},
                after={"status": WorkItem.Status.RESOLVED},
                metadata={"reason": "source_closed", "source_type": source_type},
            )
            resolved += 1
    return resolved
