from django.core.management.base import BaseCommand

from operations.services import open_source_ids, work_queue_sources
from operations.work_queue import auto_resolve_closed_sources, ingest_work_item


class Command(BaseCommand):
    help = "Synchronize unresolved warehouse findings into the cockpit work queue."

    def handle(self, *args, **options):
        created = 0
        refreshed = 0
        for source in work_queue_sources():
            _, was_created = ingest_work_item(**source)
            created += int(was_created)
            refreshed += int(not was_created)
        closed = auto_resolve_closed_sources(open_source_ids())
        self.stdout.write(self.style.SUCCESS(
            f"Work queue synchronized: {created} created, {refreshed} refreshed, {closed} auto-resolved (source closed)."
        ))
