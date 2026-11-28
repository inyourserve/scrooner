"""Egress fix: FSN row sets are read once, then served from the local cache while fsn.filing.src_sha256 is unchanged.
Outputs must be identical to the uncached path."""

from datetime import date, datetime

import pytest

from scrooner_pipeline.common.authority import load_face_indexes
from scrooner_pipeline.mapper.top100_coverage import _locator_index


class FakeConn:
    def __init__(self, sha="s1"):
        self.sha = sha
        self.big = []  # the heavy queries seen

    def execute(self, sql, params=()):
        conn = self

        class C:
            def fetchone(self):
                return ("fsn.line",)

            def fetchall(self):
                if "select accession, src_sha256" in sql:
                    return [("A", conn.sha), ("B", conn.sha)]
                if "select company_id, accession, src_sha256" in sql:
                    return [(7, "A", conn.sha)]
                if "from fsn.report" in sql:
                    return [("A", 3, "Balance Sheets")]
                if "from fsn.line l join fsn.filing" in sql:
                    rows = [
                        ("A", 4, 9, "BS", "Assets", "Total assets"),
                        ("A", 4, 10, "BS", "Cash", "Cash"),
                        ("B", 1, 1, "IS", "Revenues", "Revenue"),
                    ]
                    return [r for r in rows if r[0] in params[0]]
                if "from fsn.filing f" in sql:
                    return [
                        (
                            7,
                            "A",
                            "10-K",
                            date(2024, 12, 31),
                            date(2025, 2, 1),
                            datetime(2025, 2, 1, 9, 0),
                            "Assets",
                            "BS",
                            date(2024, 12, 31),
                            0,
                        ),
                    ]
                return []

        light = (
            "select accession, src_sha256",
            "select company_id, accession, src_sha256",
            "to_regclass",
            "analytics.company_tag_map",
        )
        if not any(k in sql for k in light):
            self.big.append(sql)
        return C()


@pytest.fixture
def cache(tmp_path, monkeypatch):
    monkeypatch.setenv("SCROONER_FSN_CACHE_DIR", str(tmp_path))
    monkeypatch.setenv("SCROONER_FSN_CACHE", "1")


def _snap(idx):
    return (idx.pos, idx.line, dict(idx.tag), idx.plabel, dict(idx.stmt_n), idx.titles)


def test_locator_second_run_makes_no_heavy_query_and_is_identical(cache, monkeypatch):
    c1, c2 = FakeConn(), FakeConn()
    first = _locator_index(c1, {"A", "B"}, {"Assets"})
    second = _locator_index(c2, {"A", "B"}, {"Assets"})
    assert len(c1.big) == 2  # one lines query + one reports query for BOTH accessions
    assert c2.big == []
    assert _snap(first) == _snap(second)
    monkeypatch.setenv("SCROONER_FSN_CACHE", "0")
    off = _locator_index(FakeConn(), {"A", "B"}, {"Assets"})
    assert _snap(off) == _snap(first)


def test_locator_refetches_when_source_hash_changes(cache):
    _locator_index(FakeConn("s1"), {"A"}, set())
    c = FakeConn("s2")
    _locator_index(c, {"A"}, set())
    assert len(c.big) == 2


def test_face_second_run_makes_no_heavy_query_and_is_identical(cache, monkeypatch):
    c1, c2 = FakeConn(), FakeConn()
    a = load_face_indexes(c1, [7])[7]
    b = load_face_indexes(c2, [7])[7]
    assert len(c1.big) == 1 and c2.big == []
    assert (a.filings, a.prints) == (b.filings, b.prints)
    monkeypatch.setenv("SCROONER_FSN_CACHE", "0")
    off = load_face_indexes(FakeConn(), [7])[7]
    assert (off.filings, off.prints) == (a.filings, a.prints)


def test_face_refetches_when_source_hash_changes(cache):
    load_face_indexes(FakeConn("s1"), [7])
    c = FakeConn("s2")
    load_face_indexes(c, [7])
    assert len(c.big) == 1
