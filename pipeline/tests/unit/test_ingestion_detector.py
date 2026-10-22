"""Ingestion detector: pure classification plus a fake connection proving the
detector issues only SELECT/SHOW/SET statement_timeout. Fixtures: REAL KO 10-Q
0001628280-26-050503 (filed 2026-07-29, 0 facts, companyfacts fetched 2026-09-29,
DATA-INFERRED from core.filing / raw.sec_companyfacts on 2026-10-22) and the
DG/HPQ index-vs-core.filing class."""

from datetime import date, datetime, timezone

from scrooner_pipeline.sanity import ingestion_detector as d

TODAY = date(2026, 10, 22)
KO_FETCHED = datetime(2026, 9, 29, 12, 0, tzinfo=timezone.utc)


def test_stage1_causes():
    assert (
        d.classify_stage1(date(2026, 10, 21), KO_FETCHED, TODAY) == d.CAUSE_TOO_RECENT
    )
    assert d.classify_stage1(date(2026, 7, 29), None, TODAY) == d.CAUSE_NO_OBJECT
    assert d.classify_stage1(date(2026, 10, 1), KO_FETCHED, TODAY) == d.CAUSE_OLDER
    assert (
        d.classify_stage1(date(2026, 9, 29), KO_FETCHED, TODAY) == d.CAUSE_OLDER
    )  # same day: fetched before the index caught it
    assert (
        d.classify_stage1(date(2026, 7, 29), KO_FETCHED, TODAY) == d.CAUSE_CHECK
    )  # KO


def test_stage2_distinguishes_sec_lag_from_extraction_defect():
    payload = {
        "facts": {
            "us-gaap": {
                "Revenues": {
                    "units": {"USD": [{"accn": "0001628280-26-028802", "val": 1}]}
                }
            },
            "dei": {
                "EntityCommonStockSharesOutstanding": {
                    "units": {"shares": [{"accn": "0001628280-26-010047"}]}
                }
            },
        }
    }
    got = d.payload_accessions(payload)
    assert got == {"0001628280-26-028802", "0001628280-26-010047"}
    assert (
        d.classify_stage2("0001628280-26-050503", got) == d.CAUSE_LACKS
    )  # KO: SEC payload lacks the 10-Q
    assert d.classify_stage2("0001628280-26-028802", got) == d.CAUSE_NOT_EXTRACTED
    assert d.payload_accessions({}) == set()


class FakeCursor:
    def __init__(self, conn):
        self.conn = conn
        self._rows = []

    def __enter__(self):
        return self

    def __exit__(self, *_a):
        return False

    def execute(self, sql, params=()):
        sql = " ".join(sql.split())
        self.conn.statements.append(sql)
        low = sql.lower()
        if low == "show statement_timeout":
            self._rows = [("2min",)]
        elif "from core.company where status" in low:
            self._rows = [(1, "0000021344", "KO"), (2, "0000029534", "DG")]
        elif "from core.filing f join core.company" in low:
            self._rows = [
                (
                    1,
                    "0000021344",
                    "0001628280-26-050503",
                    "10-Q",
                    date(2026, 7, 29),
                    date(2026, 7, 3),
                    datetime(2026, 8, 20),
                )
            ]
        elif "from raw.sec_companyfacts" in low:
            self._rows = [("0000021344", KO_FETCHED, "raw/sec/companyfacts/x.json")]
        elif "from raw.sec_filing_documents" in low:
            self._rows = [
                (
                    "0000029534",
                    "0000029534-26-000099",
                    "10-Q",
                    date(2026, 8, 27),
                    date(2026, 8, 1),
                )
            ]
        elif "max(f.filing_date)" in low:
            self._rows = [(2, date(2026, 6, 2))]
        else:
            self._rows = []

    def fetchall(self):
        return list(self._rows)

    def fetchone(self):
        return self._rows[0]


class FakeConn:
    def __init__(self):
        self.statements = []

    def cursor(self):
        return FakeCursor(self)


def test_detector_reads_only_and_restores_the_callers_timeout():
    conn = FakeConn()
    zero = d.detect_zero_fact_filings(conn, date(2026, 7, 1), today=TODAY)
    unindexed = d.detect_unindexed_filings(conn, date(2026, 7, 1))
    [z] = zero
    assert (z.ticker, z.accession, z.cause) == (
        "KO",
        "0001628280-26-050503",
        d.CAUSE_CHECK,
    )
    assert z.companyfacts_fetched_at == KO_FETCHED
    [u] = unindexed
    assert (u.ticker, u.accession, u.latest_core_periodic_date) == (
        "DG",
        "0000029534-26-000099",
        date(2026, 6, 2),
    )
    for sql in conn.statements:
        head = sql.split()[0].lower()
        assert head in {"select", "show", "set"}, sql
        if head == "set":
            assert sql.lower().startswith("set statement_timeout")
    assert conn.statements[-1] == "set statement_timeout = '2min'"  # restored


def test_summary_counts():
    z = d.ZeroFactFiling(
        1,
        "c",
        "KO",
        "a",
        "10-Q",
        date(2026, 7, 29),
        None,
        None,
        KO_FETCHED,
        "p",
        d.CAUSE_CHECK,
    )
    u = d.UnindexedFiling("c2", "DG", "b", "10-Q", date(2026, 8, 27), None, None)
    s = d.summarize([z, z], [u])
    assert s["zero_fact_filings"] == 2 and s["zero_fact_companies"] == 1
    assert s["zero_fact_by_cause"] == {d.CAUSE_CHECK: 2} and s["unindexed_filings"] == 1


def test_stage2_download_is_bounded_and_per_company():
    class Storage:
        def __init__(self):
            self.downloads = []

        def download(self, path):
            self.downloads.append(path)
            return (
                b'{"facts": {"us-gaap": {"R": {"units": {"USD": [{"accn": "A-1"}]}}}}}'
            )

        def close(self):
            pass

    def z(accn, cik, cause=d.CAUSE_CHECK):
        return d.ZeroFactFiling(
            1,
            cik,
            "T",
            accn,
            "10-Q",
            date(2026, 7, 29),
            None,
            None,
            KO_FETCHED,
            f"raw/{cik}.json",
            cause,
        )

    storage = Storage()
    out = d.check_payloads(
        [z("A-1", "c1"), z("A-2", "c1"), z("A-3", "c2"), z("A-4", "c3", d.CAUSE_OLDER)],
        limit=1,
        storage=storage,
    )
    assert (
        len(storage.downloads) == 1
    )  # one object for c1 serves both of its filings; budget then spent
    assert [o.cause for o in out] == [
        d.CAUSE_NOT_EXTRACTED,
        d.CAUSE_LACKS,
        d.CAUSE_CHECK,
        d.CAUSE_OLDER,
    ]
