import json
from datetime import date, timedelta

import pytest

from scrooner_pipeline.ownership import beneficial_ownership


class _FakeCursor:
    def __init__(self, storage_paths):
        self._storage_paths = storage_paths

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def execute(self, _sql, _params=()):
        pass

    def fetchall(self):
        return [(p,) for p in self._storage_paths]


class _FakeConnection:
    def __init__(self, storage_paths):
        self._storage_paths = storage_paths

    def cursor(self):
        return _FakeCursor(self._storage_paths)


class _FakeStorage:
    """Always returns the same payload regardless of path -- these tests
    only ever use one storage path, and `strip_bucket_prefix` (called on
    the path before `download()`) makes exact-path dict-keying fragile
    for a fake with no real bucket-prefix logic of its own."""

    def __init__(self, payload):
        self._payload = payload

    def download(self, _path):
        return json.dumps(self._payload).encode()


def _submission_payload(rows):
    return {
        "filings": {
            "recent": {
                "form": [r["form"] for r in rows],
                "accessionNumber": [r["accession_number"] for r in rows],
                "filingDate": [r["filing_date"] for r in rows],
            }
        }
    }


@pytest.mark.unit
class TestBeneficialOwnershipHistoryBound:
    """Real bug found live 2026-08-30: this module had no recency bound at
    all -- 73% of all (company, filer) relationships in the live table had
    their most-recent filing more than 3 years old, almost certainly
    genuinely-closed positions, not stale-but-current ones. These tests
    verify the fix filters BEFORE the expensive per-filing fetch, not
    after -- see MIN_FILING_DATE's own module-level comment for why 3
    years (not 1, like insider.py's Form 4 bound) was chosen: Schedule 13G
    doesn't require an annual refile if nothing changed, unlike Form 4/13F."""

    def test_recent_filing_is_kept(self):
        recent_date = (date.today() - timedelta(days=30)).strftime("%Y-%m-%d")
        rows = [{"form": "SC 13G", "accession_number": "0000000000-26-000001", "filing_date": recent_date}]
        storage = _FakeStorage(_submission_payload(rows))
        conn = _FakeConnection(["raw/sec/submissions/test.json"])
        filings = beneficial_ownership._load_schedule_filings(storage, conn, "0000320193")
        assert len(filings) == 1
        assert filings[0]["filing_date"] == recent_date

    def test_filing_older_than_3_years_is_excluded_before_any_fetch(self):
        old_date = (date.today() - timedelta(days=365 * 4)).strftime("%Y-%m-%d")
        rows = [{"form": "SC 13G", "accession_number": "0000000000-22-000001", "filing_date": old_date}]
        storage = _FakeStorage(_submission_payload(rows))
        conn = _FakeConnection(["raw/sec/submissions/test.json"])
        filings = beneficial_ownership._load_schedule_filings(storage, conn, "0000320193")
        assert filings == []

    def test_filing_just_inside_the_3_year_window_is_kept(self):
        just_inside = (date.today() - timedelta(days=365 * 3 - 10)).strftime("%Y-%m-%d")
        rows = [{"form": "SC 13D/A", "accession_number": "0000000000-24-000001", "filing_date": just_inside}]
        storage = _FakeStorage(_submission_payload(rows))
        conn = _FakeConnection(["raw/sec/submissions/test.json"])
        filings = beneficial_ownership._load_schedule_filings(storage, conn, "0000320193")
        assert len(filings) == 1

    def test_mixed_batch_only_keeps_recent_ones(self):
        recent = (date.today() - timedelta(days=100)).strftime("%Y-%m-%d")
        old = (date.today() - timedelta(days=365 * 10)).strftime("%Y-%m-%d")
        rows = [
            {"form": "SC 13G", "accession_number": "0000000000-26-000001", "filing_date": recent},
            {"form": "SC 13G/A", "accession_number": "0000000000-16-000001", "filing_date": old},
            {"form": "SC 13D", "accession_number": "0000000000-15-000001", "filing_date": old},
        ]
        storage = _FakeStorage(_submission_payload(rows))
        conn = _FakeConnection(["raw/sec/submissions/test.json"])
        filings = beneficial_ownership._load_schedule_filings(storage, conn, "0000320193")
        assert len(filings) == 1
        assert filings[0]["filing_date"] == recent

    def test_form_not_in_scope_is_excluded_even_if_recent(self):
        recent = (date.today() - timedelta(days=10)).strftime("%Y-%m-%d")
        rows = [{"form": "10-K", "accession_number": "0000000000-26-000001", "filing_date": recent}]
        storage = _FakeStorage(_submission_payload(rows))
        conn = _FakeConnection(["raw/sec/submissions/test.json"])
        filings = beneficial_ownership._load_schedule_filings(storage, conn, "0000320193")
        assert filings == []
