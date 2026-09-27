"""Module 7 — Raw Storage (doc 06). Thin Supabase Storage client used by
the companyfacts/submissions collectors (and later, filings.py) to upload
raw payloads exactly as fetched. No transformation — bytes in, bytes
stored, a storage_path handed back for the metadata tables to record.

Uses httpx directly against Supabase's Storage REST API rather than the
supabase-py SDK — that would be a new dependency doc 04 hasn't locked, and
the REST surface needed here (upload one object) is tiny.

Day 6 (doc 08): added head() and download() for collector/integrity.py's
reconciliation report — read-only, no transformation, same "never repair,
only observe" boundary as everything else in this module.
"""

import httpx
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

from scrooner_pipeline.collector.retry import HTTP_RETRY
from scrooner_pipeline.common.config import settings

logger = structlog.get_logger()

BUCKET = "raw"


class SupabaseStorageClient:
    def __init__(self) -> None:
        self._client = httpx.Client(
            base_url=settings.supabase_url + "/storage/v1",
            headers={
                "Authorization": f"Bearer {settings.supabase_service_role_key}",
                "apikey": settings.supabase_service_role_key,
            },
            timeout=60.0,
        )

    @retry(
        retry=HTTP_RETRY,
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=1, max=30),
        reraise=True,
    )
    def upload(
        self, object_path: str, content: bytes, content_type: str = "application/json"
    ) -> str:
        """Uploads bytes verbatim to {BUCKET}/{object_path}. Returns the
        full storage_path (bucket-prefixed, e.g. "raw/sec/companyfacts/...")
        for the caller to record in Postgres — matches doc 08's path
        convention, and mirrors what Supabase's own API returns as the
        object's Key. x-upsert lets a rerun overwrite an identical path
        instead of erroring — collision is only realistic if the same
        fetch is literally re-run, since fetched_at is embedded in the path.
        As of Day 4, a resumed run reuses the same fetched_at, so a company
        this pass re-touches (shouldn't happen given the checkpoint skip in
        companyfacts.py/submissions.py, but this is the belt-and-suspenders
        layer) uploads to the identical object_path and just overwrites
        with byte-identical content rather than erroring or duplicating.
        """
        response = self._client.post(
            f"/object/{BUCKET}/{object_path}",
            content=content,
            headers={"Content-Type": content_type, "x-upsert": "true"},
        )
        response.raise_for_status()
        return f"{BUCKET}/{object_path}"

    @retry(
        retry=HTTP_RETRY,
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=1, max=30),
        reraise=True,
    )
    def _head_uncaught(self, object_path: str) -> dict:
        response = self._client.get(
            f"/object/info/authenticated/{BUCKET}/{object_path}"
        )
        response.raise_for_status()
        return response.json()

    def head(self, object_path: str) -> dict | None:
        """Cheap existence + metadata check (Module 11's exhaustive
        existence pass, doc 08 Day 6) via Supabase's object/info endpoint --
        no object bytes transferred, just size/etag/mimetype/last_modified.
        Returns that metadata dict if the object exists, or None if Storage
        genuinely has no object at this path (a real 404). Any OTHER error
        (network, 5xx, auth) propagates rather than being treated as
        "missing" -- an integrity checker that swallows a transient failure
        into a false "missing_object" finding would misreport data loss
        that never happened. See collector/integrity.py.
        """
        try:
            return self._head_uncaught(object_path)
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                return None
            raise

    @retry(
        retry=HTTP_RETRY,
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=1, max=30),
        reraise=True,
    )
    def download(self, object_path: str) -> bytes:
        """Downloads and returns the full object bytes. Used only by
        integrity.py's hash-reverification path -- deliberately NOT used by
        the existence check (head(), above), so confirming a multi-MB
        companyfacts payload still exists never requires transferring it.
        """
        response = self._client.get(f"/object/{BUCKET}/{object_path}")
        response.raise_for_status()
        return response.content

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "SupabaseStorageClient":
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()


def strip_bucket_prefix(storage_path: str) -> str:
    """storage_path as recorded in Postgres is bucket-prefixed (e.g.
    "raw/sec/companyfacts/..."), matching what upload() returns and doc
    08's storage-path convention. Storage's REST API addresses an object by
    bucket and object-path separately (see head()/download() above), so
    this is the one place that prefix convention gets undone -- callers
    (collector/integrity.py) use this instead of each reimplementing
    `.removeprefix(f"{BUCKET}/")` themselves.
    """
    prefix = f"{BUCKET}/"
    if not storage_path.startswith(prefix):
        raise ValueError(
            f"storage_path {storage_path!r} does not start with expected bucket prefix {prefix!r}"
        )
    return storage_path[len(prefix) :]
