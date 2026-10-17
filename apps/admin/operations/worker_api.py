import json
import secrets

from django.conf import settings
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .work_queue import add_evidence, claim_next, heartbeat, transition


def _authorized(request):
    expected = settings.OPS_WORKER_TOKEN
    supplied = request.headers.get("Authorization", "").removeprefix("Bearer ").strip()
    return bool(expected and supplied and secrets.compare_digest(expected, supplied))


def _body(request):
    try:
        return json.loads(request.body or "{}")
    except json.JSONDecodeError as exc:
        raise ValidationError("Request body must be valid JSON.") from exc


def _item(item):
    return {"id": item.pk, "fingerprint": item.fingerprint, "source_type": item.source_type, "source_id": item.source_id, "title": item.title, "severity": item.severity, "priority": item.priority, "status": item.status, "payload": item.payload, "impact": item.impact, "lease_token": str(item.lease_token) if item.lease_token else None, "lease_expires_at": item.lease_expires_at.isoformat() if item.lease_expires_at else None}


def _endpoint(handler):
    @csrf_exempt
    def wrapped(request, *args, **kwargs):
        if not _authorized(request):
            return JsonResponse({"error": "unauthorized"}, status=401)
        if request.method != "POST":
            return JsonResponse({"error": "method_not_allowed"}, status=405)
        try:
            return handler(request, *args, **kwargs)
        except ValidationError as exc:
            return JsonResponse({"error": "invalid_request", "detail": exc.messages}, status=409)
    return wrapped


@_endpoint
def claim(request):
    data = _body(request)
    worker_id = str(data.get("worker_id", "")).strip()[:160]
    if not worker_id:
        raise ValidationError("worker_id is required.")
    item, attempt = claim_next(worker_id)
    return JsonResponse({"work_item": _item(item) if item else None, "attempt": attempt.number if attempt else None})


@_endpoint
def heartbeat_view(request, item_id):
    data = _body(request)
    item = heartbeat(item_id, str(data.get("worker_id", "")), str(data.get("lease_token", "")))
    return JsonResponse({"work_item": _item(item)})


@_endpoint
def evidence(request, item_id):
    data = _body(request)
    row = add_evidence(item_id, str(data.get("worker_id", "")), str(data.get("lease_token", "")), kind=str(data.get("kind", "observation")), summary=str(data.get("summary", "")), data=data.get("data") or {}, artifact_url=str(data.get("artifact_url", "")))
    return JsonResponse({"evidence_id": row.pk}, status=201)


@_endpoint
def transition_view(request, item_id):
    data = _body(request)
    item = transition(item_id, str(data.get("worker_id", "")), str(data.get("lease_token", "")), status=str(data.get("status", "")), summary=str(data.get("summary", "")), result=data.get("result") or {})
    return JsonResponse({"work_item": _item(item)})
