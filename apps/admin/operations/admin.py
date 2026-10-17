from django.contrib import admin

from .models import AuditEvent, CommandAttempt, CommandRequest, Investigation, InvestigationNote, WorkAttempt, WorkEvidence, WorkItem
from .workflows import review_command, submit_command


class InvestigationNoteInline(admin.TabularInline):
    model = InvestigationNote
    extra = 1
    fields = ("body", "author", "created_at")
    readonly_fields = ("created_at",)


@admin.register(Investigation)
class InvestigationAdmin(admin.ModelAdmin):
    list_display = ("title", "severity", "status", "target_type", "target_id", "owner", "updated_at")
    list_filter = ("severity", "status", "target_type")
    search_fields = ("title", "target_id", "conclusion")
    inlines = [InvestigationNoteInline]


@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display = ("created_at", "event_type", "target_type", "target_id", "actor", "request_id")
    list_filter = ("event_type", "target_type")
    search_fields = ("target_id", "request_id")
    readonly_fields = tuple(field.name for field in AuditEvent._meta.fields)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class CommandAttemptInline(admin.TabularInline):
    model = CommandAttempt
    extra = 0
    readonly_fields = tuple(field.name for field in CommandAttempt._meta.fields)
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(CommandRequest)
class CommandRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "command_type", "status", "requested_by", "approved_by", "created_at")
    list_filter = ("command_type", "status")
    search_fields = ("reason", "idempotency_key")
    readonly_fields = ("idempotency_key", "created_at", "updated_at", "approved_at")
    inlines = [CommandAttemptInline]
    actions = ("submit_selected", "approve_selected", "reject_selected")

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.requested_by = request.user
        obj.full_clean()
        super().save_model(request, obj, form, change)

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.action(description="Submit selected drafts for approval")
    def submit_selected(self, request, queryset):
        for command in queryset:
            submit_command(command.pk, request.user)

    @admin.action(description="Approve selected pending commands", permissions=["approve"])
    def approve_selected(self, request, queryset):
        for command in queryset:
            review_command(command.pk, request.user, approve=True)

    @admin.action(description="Reject selected pending commands", permissions=["approve"])
    def reject_selected(self, request, queryset):
        for command in queryset:
            review_command(command.pk, request.user, approve=False)

    def has_approve_permission(self, request):
        return request.user.has_perm("operations.approve_commandrequest")


class WorkAttemptInline(admin.TabularInline):
    model = WorkAttempt
    extra = 0
    readonly_fields = tuple(field.name for field in WorkAttempt._meta.fields)
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


class WorkEvidenceInline(admin.TabularInline):
    model = WorkEvidence
    extra = 0
    readonly_fields = tuple(field.name for field in WorkEvidence._meta.fields)
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(WorkItem)
class WorkItemAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "severity", "status", "priority", "assigned_worker", "last_seen_at")
    list_filter = ("status", "severity", "source_type")
    search_fields = ("title", "source_id", "fingerprint", "assigned_worker")
    readonly_fields = tuple(field.name for field in WorkItem._meta.fields)
    inlines = [WorkAttemptInline, WorkEvidenceInline]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
