import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Investigation(models.Model):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        INVESTIGATING = "investigating", "Investigating"
        RESOLVED = "resolved", "Resolved"
        WONT_FIX = "wont_fix", "Won't fix"

    class Severity(models.TextChoices):
        INFO = "info", "Info"
        WARNING = "warning", "Warning"
        CRITICAL = "critical", "Critical"

    title = models.CharField(max_length=240)
    target_type = models.CharField(max_length=80)
    target_id = models.CharField(max_length=160)
    severity = models.CharField(max_length=16, choices=Severity.choices, default=Severity.WARNING)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    conclusion = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=["status", "severity"]), models.Index(fields=["target_type", "target_id"])]
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class InvestigationNote(models.Model):
    investigation = models.ForeignKey(Investigation, related_name="notes", on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]


class AuditEvent(models.Model):
    request_id = models.UUIDField(default=uuid.uuid4, db_index=True)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    event_type = models.CharField(max_length=100, db_index=True)
    target_type = models.CharField(max_length=80)
    target_id = models.CharField(max_length=160, blank=True)
    before = models.JSONField(default=dict, blank=True)
    after = models.JSONField(default=dict, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["target_type", "target_id", "-created_at"])]


class CommandRequest(models.Model):
    class Type(models.TextChoices):
        RETRY_STAGE = "retry_stage", "Retry pipeline stage"
        RECOMPUTE_COMPANY = "recompute_company", "Recompute company"
        COVERAGE_SNAPSHOT = "coverage_snapshot", "Build coverage snapshot"
        INVALIDATE_CACHE = "invalidate_cache", "Invalidate cache"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PENDING = "pending_approval", "Pending approval"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        QUEUED = "queued", "Queued"
        RUNNING = "running", "Running"
        SUCCEEDED = "succeeded", "Succeeded"
        FAILED = "failed", "Failed"
        CANCELLED = "cancelled", "Cancelled"

    command_type = models.CharField(max_length=40, choices=Type.choices)
    parameters = models.JSONField(default=dict, blank=True)
    reason = models.TextField()
    status = models.CharField(max_length=24, choices=Status.choices, default=Status.DRAFT, db_index=True)
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="requested_commands", on_delete=models.PROTECT)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="approved_commands", null=True, blank=True, on_delete=models.PROTECT)
    idempotency_key = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["status", "-created_at"]), models.Index(fields=["command_type", "-created_at"])]
        permissions = [("approve_commandrequest", "Can approve or reject command requests")]

    def clean(self):
        if self.approved_by_id and self.approved_by_id == self.requested_by_id:
            raise ValidationError({"approved_by": "The requester cannot approve their own command."})

    def __str__(self):
        return f"{self.get_command_type_display()} ({self.get_status_display()})"


class CommandAttempt(models.Model):
    command = models.ForeignKey(CommandRequest, related_name="attempts", on_delete=models.PROTECT)
    attempt_number = models.PositiveSmallIntegerField()
    worker_id = models.CharField(max_length=160, blank=True)
    status = models.CharField(max_length=24)
    output = models.JSONField(default=dict, blank=True)
    error = models.TextField(blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["command", "attempt_number"], name="uniq_command_attempt")]
        ordering = ["command_id", "attempt_number"]


class WorkItem(models.Model):
    class Status(models.TextChoices):
        READY = "ready", "Ready"
        CLAIMED = "claimed", "Claimed"
        INVESTIGATING = "investigating", "Investigating"
        FIX_PROPOSED = "fix_proposed", "Fix proposed"
        AWAITING_APPROVAL = "awaiting_approval", "Awaiting approval"
        VERIFYING = "verifying", "Verifying"
        RESOLVED = "resolved", "Resolved"
        ESCALATED = "escalated", "Escalated"
        FAILED = "failed", "Failed"

    class Severity(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    fingerprint = models.CharField(max_length=64, unique=True, editable=False)
    source_type = models.CharField(max_length=80, db_index=True)
    source_id = models.CharField(max_length=160)
    title = models.CharField(max_length=240)
    severity = models.CharField(max_length=16, choices=Severity.choices, default=Severity.MEDIUM, db_index=True)
    status = models.CharField(max_length=24, choices=Status.choices, default=Status.READY, db_index=True)
    priority = models.PositiveSmallIntegerField(default=50)
    payload = models.JSONField(default=dict, blank=True)
    impact = models.JSONField(default=dict, blank=True)
    resolution = models.JSONField(default=dict, blank=True)
    assigned_worker = models.CharField(max_length=160, blank=True)
    lease_token = models.UUIDField(null=True, blank=True, editable=False)
    lease_expires_at = models.DateTimeField(null=True, blank=True)
    last_heartbeat_at = models.DateTimeField(null=True, blank=True)
    first_seen_at = models.DateTimeField(auto_now_add=True)
    last_seen_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-priority", "first_seen_at"]
        indexes = [
            models.Index(fields=["status", "-priority", "first_seen_at"]),
            models.Index(fields=["assigned_worker", "lease_expires_at"]),
            models.Index(fields=["source_type", "source_id"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"


class WorkAttempt(models.Model):
    work_item = models.ForeignKey(WorkItem, related_name="attempts", on_delete=models.PROTECT)
    number = models.PositiveSmallIntegerField()
    worker_id = models.CharField(max_length=160)
    lease_token = models.UUIDField()
    status = models.CharField(max_length=24, default="started")
    summary = models.TextField(blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["work_item", "number"], name="uniq_work_item_attempt")]
        ordering = ["work_item_id", "number"]


class WorkEvidence(models.Model):
    work_item = models.ForeignKey(WorkItem, related_name="evidence", on_delete=models.PROTECT)
    attempt = models.ForeignKey(WorkAttempt, related_name="evidence", null=True, blank=True, on_delete=models.PROTECT)
    kind = models.CharField(max_length=40)
    summary = models.TextField()
    data = models.JSONField(default=dict, blank=True)
    artifact_url = models.URLField(blank=True)
    created_by = models.CharField(max_length=160)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        indexes = [models.Index(fields=["work_item", "created_at"])]
