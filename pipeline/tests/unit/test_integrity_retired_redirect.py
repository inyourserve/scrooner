"""Integrity check redirects retired Storage objects to their keeper (migration 0111, Rule S)."""

from scrooner_pipeline.collector import integrity


def test_retired_row_is_checked_at_keeper_path():
    retired = {("raw.sec_companyfacts", 7): "raw/sec/companyfacts/1/keeper.json"}
    row = {"id": 7, "storage_path": "raw/sec/companyfacts/1/old.json"}
    assert integrity.resolve_storage_path("raw.sec_companyfacts", row, retired) == (
        "raw/sec/companyfacts/1/keeper.json",
        True,
    )
    row2 = {"id": 8, "storage_path": "raw/x"}
    assert integrity.resolve_storage_path("raw.sec_companyfacts", row2, retired) == (
        "raw/x",
        False,
    )
    # same id in another table never redirects
    assert (
        integrity.resolve_storage_path("raw.sec_submissions", row, retired)[1] is False
    )
    # filing documents have no integer id
    assert integrity.resolve_storage_path(
        "raw.sec_filing_documents", {"cik": "1", "storage_path": "raw/y"}, retired
    ) == ("raw/y", False)


class _Cur:
    def __init__(self, exists, rows):
        self.exists, self.rows = exists, rows

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def execute(self, sql):
        pass

    def fetchone(self):
        return (self.exists,)

    def fetchall(self):
        return self.rows


class _Conn:
    def __init__(self, exists, rows=()):
        self.cur = _Cur(exists, list(rows))

    def cursor(self):
        return self.cur

    def rollback(self):
        pass


def test_load_retired_map_empty_when_table_missing():
    assert integrity.load_retired_map(_Conn(False)) == {}


def test_load_retired_map_reads_keepers():
    conn = _Conn(True, [("raw.sec_companyfacts", 7, "raw/k.json")])
    assert integrity.load_retired_map(conn) == {
        ("raw.sec_companyfacts", 7): "raw/k.json"
    }
