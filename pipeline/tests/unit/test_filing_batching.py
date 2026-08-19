from datetime import date

import pytest

from scrooner_pipeline.collector import filings


pytestmark = pytest.mark.unit


class DummySECClient:
    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None


class FakeCursor:
    def __init__(self, known: set[str]) -> None:
        self.known = known
        self.result: list[tuple[str]] = []
        self.batch_sizes: list[int] = []

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None

    def execute(self, query: str, params: tuple) -> None:
        if "from unnest" in query:
            ciks, accessions = params[0], params[1]
            self.batch_sizes.append(len(ciks))
            inserted = []
            for cik, accession in zip(ciks, accessions, strict=True):
                if accession not in self.known:
                    self.known.add(accession)
                    inserted.append((cik,))
            self.result = inserted
        else:
            self.result = []

    def fetchall(self):
        return self.result


class FakeConnection:
    def __init__(self, known: set[str]) -> None:
        self.fake_cursor = FakeCursor(known)
        self.commits = 0
        self.rollbacks = 0

    def cursor(self):
        return self.fake_cursor

    def commit(self) -> None:
        self.commits += 1

    def rollback(self) -> None:
        self.rollbacks += 1


def row(cik: str, accession: str) -> dict:
    return {
        "cik": cik,
        "accession_number": accession,
        "form": "10-Q",
        "filing_date": date(2026, 8, 18),
        "source_url": f"https://www.sec.gov/{accession}",
    }


def test_daily_filings_batches_idempotently_and_filters_scope(monkeypatch) -> None:
    rows = [row("0000000001", "a"), row("0000000001", "b"), row("0000000002", "c")]
    monkeypatch.setattr(filings, "SECClient", DummySECClient)
    monkeypatch.setattr(filings, "fetch_daily_index", lambda _client, _date: rows)
    conn = FakeConnection(known={"a"})

    stats = filings.collect_daily_filings(
        conn,
        for_date=date(2026, 8, 18),
        run_id=12,
        only_ciks={"0000000001"},
    )

    assert stats == {
        "index_rows": 3,
        "considered": 2,
        "new": 1,
        "already_known": 1,
        "errors": 0,
    }
    assert conn.fake_cursor.batch_sizes == [2]
    assert conn.rollbacks == 0
