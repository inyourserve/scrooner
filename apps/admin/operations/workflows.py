from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone

from .models import AuditEvent, CommandRequest


def _audit(command, actor, event_type, before, metadata=None):
    AuditEvent.objects.create(
        actor=actor,
        event_type=event_type,
        target_type="command_request",
        target_id=str(command.pk),
        before={"status": before},
        after={"status": command.status},
        metadata=metadata or {},
    )


@transaction.atomic
def submit_command(command_id, actor):
    command = CommandRequest.objects.select_for_update().get(pk=command_id)
    if command.requested_by_id != actor.pk or command.status != CommandRequest.Status.DRAFT:
        raise ValidationError("Only the requester can submit a draft command.")
    before = command.status
    command.status = CommandRequest.Status.PENDING
    command.save(update_fields=["status", "updated_at"])
    _audit(command, actor, "command.submitted", before)
    return command


@transaction.atomic
def review_command(command_id, actor, *, approve):
    if not actor.has_perm("operations.approve_commandrequest"):
        raise PermissionDenied("Command approval permission is required.")
    command = CommandRequest.objects.select_for_update().get(pk=command_id)
    if command.status != CommandRequest.Status.PENDING:
        raise ValidationError("Only pending commands can be reviewed.")
    if command.requested_by_id == actor.pk:
        raise ValidationError("The requester cannot approve or reject their own command.")
    before = command.status
    command.status = CommandRequest.Status.APPROVED if approve else CommandRequest.Status.REJECTED
    command.approved_by = actor
    command.approved_at = timezone.now()
    command.full_clean()
    command.save(update_fields=["status", "approved_by", "approved_at", "updated_at"])
    _audit(command, actor, "command.approved" if approve else "command.rejected", before)
    return command
