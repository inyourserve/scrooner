import csv
import io
import zipfile

import pytest

from scrooner_pipeline.ownership.institutional import (
    _load_company_name_lookup,
    _load_submission_lookup,
    _load_filer_name_lookup,
    _match_infotable,
    normalize_issuer_name,
)


def _make_13f_zip(submission_rows: list[dict], coverpage_rows: list[dict], infotable_rows: list[dict]) -> zipfile.ZipFile:
    """Real SEC Form 13F bulk-data column names (SUBMISSION/COVERPAGE/
    INFOTABLE), mirroring the fixture pattern test_mutual_fund_ownership.py
    already established for N-PORT."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for name, rows, fieldnames in [
            ("SUBMISSION.tsv", submission_rows, ["ACCESSION_NUMBER", "CIK", "PERIODOFREPORT", "FILING_DATE", "SUBMISSIONTYPE"]),
            ("COVERPAGE.tsv", coverpage_rows, ["ACCESSION_NUMBER", "FILINGMANAGER_NAME"]),
            (
                "INFOTABLE.tsv",
                infotable_rows,
                ["ACCESSION_NUMBER", "INFOTABLE_SK", "NAMEOFISSUER", "CUSIP", "VALUE", "SSHPRNAMT", "SSHPRNAMTTYPE", "PUTCALL"],
            ),
        ]:
            out = io.StringIO()
            writer = csv.DictWriter(out, fieldnames=fieldnames, delimiter="\t")
            writer.writeheader()
            for row in rows:
                writer.writerow({f: row.get(f, "") for f in fieldnames})
            zf.writestr(name, out.getvalue())
    buf.seek(0)
    return zipfile.ZipFile(buf)


SUBMISSION_BASE = {"ACCESSION_NUMBER": "0000123456-26-000001", "CIK": "0000999999", "PERIODOFREPORT": "31-MAR-2026", "FILING_DATE": "15-MAY-2026", "SUBMISSIONTYPE": "13F-HR"}
COVERPAGE_BASE = {"ACCESSION_NUMBER": "0000123456-26-000001", "FILINGMANAGER_NAME": "Big Capital Management LLC"}


@pytest.mark.unit
def test_normalize_issuer_name_strips_suffixes_and_punctuation():
    assert normalize_issuer_name("EVOMMUNE INC") == "EVOMMUNE"
    assert normalize_issuer_name("Apple Inc.") == "APPLE"
    assert normalize_issuer_name("Berkshire Hathaway Inc Class B") == "BERKSHIRE HATHAWAY"
    assert normalize_issuer_name("AT&T Inc") == "AT T"


@pytest.mark.unit
def test_match_infotable_falls_back_to_name_when_cusip_unmatched():
    """The exact real-world case this fallback exists for: a company
    with no Schedule 13D/13G on file has no entry in cusip_to_company at
    all, so the only way in is a normalized NAMEOFISSUER match."""
    infotable_rows = [
        {**SUBMISSION_BASE, "NAMEOFISSUER": "EVOMMUNE INC", "CUSIP": "UNKNOWNCUSIP1", "INFOTABLE_SK": "1", "VALUE": "5000000", "SSHPRNAMT": "10000", "SSHPRNAMTTYPE": "SH", "PUTCALL": ""},
    ]
    zf = _make_13f_zip([SUBMISSION_BASE], [COVERPAGE_BASE], infotable_rows)
    submission_lookup = _load_submission_lookup(zf)
    filer_name_lookup = _load_filer_name_lookup(zf)

    cusip_to_company: dict[str, int] = {}  # this company has NO cusip on file
    name_to_company = {"EVOMMUNE": 4513}

    matched, total = _match_infotable(zf, cusip_to_company, submission_lookup, filer_name_lookup, name_to_company)
    assert total == 1
    assert len(matched) == 1
    assert matched[0]["company_id"] == 4513
    assert matched[0]["match_method"] == "name"


@pytest.mark.unit
def test_match_infotable_prefers_cusip_over_name_when_both_available():
    """CUSIP is the hard identifier; name matching only fills a gap, it
    never overrides or competes with a real CUSIP hit."""
    infotable_rows = [
        {**SUBMISSION_BASE, "NAMEOFISSUER": "APPLE INC", "CUSIP": "037833100", "INFOTABLE_SK": "1", "VALUE": "5000000", "SSHPRNAMT": "10000", "SSHPRNAMTTYPE": "SH", "PUTCALL": ""},
    ]
    zf = _make_13f_zip([SUBMISSION_BASE], [COVERPAGE_BASE], infotable_rows)
    submission_lookup = _load_submission_lookup(zf)
    filer_name_lookup = _load_filer_name_lookup(zf)

    cusip_to_company = {"037833100": 3}
    # A deliberately WRONG name mapping -- if this got used instead of the
    # cusip, the test would catch it immediately.
    name_to_company = {"APPLE": 99999}

    matched, _total = _match_infotable(zf, cusip_to_company, submission_lookup, filer_name_lookup, name_to_company)
    assert matched[0]["company_id"] == 3
    assert matched[0]["match_method"] == "cusip"


@pytest.mark.unit
def test_match_infotable_skips_row_when_neither_cusip_nor_name_match():
    infotable_rows = [
        {**SUBMISSION_BASE, "NAMEOFISSUER": "SOME UNTRACKED COMPANY", "CUSIP": "000000000", "INFOTABLE_SK": "1", "VALUE": "1", "SSHPRNAMT": "1", "SSHPRNAMTTYPE": "SH", "PUTCALL": ""},
    ]
    zf = _make_13f_zip([SUBMISSION_BASE], [COVERPAGE_BASE], infotable_rows)
    submission_lookup = _load_submission_lookup(zf)
    filer_name_lookup = _load_filer_name_lookup(zf)

    matched, total = _match_infotable(zf, {}, submission_lookup, filer_name_lookup, {"EVOMMUNE": 4513})
    assert total == 1
    assert matched == []


class _FakeCursor:
    def __init__(self, rows):
        self._rows = rows

    def execute(self, _sql, _params=None):
        pass

    def fetchall(self):
        return self._rows

    def __enter__(self):
        return self

    def __exit__(self, *_exc):
        return False


class _FakeConnection:
    def __init__(self, rows):
        self._rows = rows

    def cursor(self):
        return _FakeCursor(self._rows)


@pytest.mark.unit
def test_load_company_name_lookup_excludes_covered_and_collisions():
    rows = [
        (1, "Apple Inc"),  # already covered by cusip -- must be excluded
        (2, "Evommune Inc"),  # uncovered, unique -- should be included
        (3, "Ambiguous Co"),
        (4, "Ambiguous Co"),  # collides with company 3 -- both excluded
    ]
    conn = _FakeConnection(rows)
    lookup = _load_company_name_lookup(conn, covered_company_ids={1})
    assert lookup == {"EVOMMUNE": 2}
