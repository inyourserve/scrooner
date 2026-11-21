"""analytics.display_cell_certificate (0132) and the certificate loader display_cert_load.

Parser tests run on the real signed GILD and JNJ certificates in data-team/strategy/approvals/. DB tests build a minimal
core/analytics schema in an isolated Postgres clone, apply 0130 and 0132 as written, and prove the loader and the
invalidation by join."""

import re
from datetime import date
from decimal import Decimal
from pathlib import Path

import psycopg
import pytest
from scrooner_pipeline.certification import display_cert_load as dl

ROOT = Path(__file__).resolve().parents[3]
DB = ROOT / "pipeline" / "db"
APPR = ROOT / "data-team" / "strategy" / "approvals"
GILD = APPR / "GILD-certificate-2026-11-16-r2.md"
JNJ = APPR / "JNJ-certificate-2026-11-16-r2.md"


def _sql(num):
    f = list(DB.glob(f"pending/{num}_*.sql")) + list(DB.glob(f"migrations/{num}_*.sql"))
    assert len(f) == 1
    return f[0].read_text()


def test_parses_both_signed_certificates():
    for path, ticker in ((GILD, "GILD"), (JNJ, "JNJ")):
        c = dl.parse(path, ROOT)
        assert (c.ticker, c.verdict, len(c.cells)) == (ticker, "PASS", 32)
        assert len({x.company_id for x in c.cells}) == 1
        assert c.certified_on == "2026-11-16" and c.seed.startswith(ticker)
    g = dl.parse(GILD, ROOT)
    assert any(x.data_point == "total_assets" and x.grain == "I" and x.shown_value == Decimal("56977000000") for x in g.cells)


def test_refuses_tampered_coverage_and_wrong_value(tmp_path):
    root = tmp_path
    (root / "data-team/strategy/certification").mkdir(parents=True)
    cert = GILD.read_text()
    cov_rel = re.search(r"Coverage: `([^`]+)`", cert).group(1)
    cov = (ROOT / cov_rel).read_bytes()
    (root / cov_rel).write_bytes(cov.replace(b"56977000000", b"56977000001", 1))
    p = root / "c.md"
    p.write_text(cert)
    with pytest.raises(ValueError, match="hashes to"):
        dl.parse(p, root)
    # a certificate stating a value that differs from its (hash-matching) coverage file
    (root / cov_rel).write_bytes(cov)
    p.write_text(cert.replace("| 56977000000 |", "| 56977000009 |", 1))
    with pytest.raises(ValueError, match="shown 56977000009"):
        dl.parse(p, root)
    p.write_text(cert.replace("PASS", "FAIL", 1))
    with pytest.raises(ValueError, match="only PASS"):
        dl.parse(p, root)


@pytest.fixture
def db(isolated_database_url):
    with psycopg.connect(isolated_database_url) as c:
        c.execute("drop schema if exists analytics cascade; drop schema if exists core cascade")
        c.execute("create schema core; create schema analytics")
        c.execute(
            "create table core.company (id bigint primary key, cik text);"
            "create table core.filing (id bigint generated always as identity primary key, company_id bigint, "
            "accession_number text unique, form text, filing_date date, period_of_report date);"
            "create table analytics.company_certification (company_id bigint primary key);"
        )
        c.execute(re.sub(r"references core\.company \(id\)", "", _sql("0130")))
        c.execute(_sql("0132"))
        c.commit()
        yield c


PV = "res-v1"


def _seed(c, cert):
    cid = cert.cells[0].company_id
    c.execute("insert into core.company values (%s, 'x')", (cid,))
    for cell in cert.cells:
        c.execute(
            "insert into core.filing (company_id, accession_number, form, filing_date, period_of_report) "
            "values (%s, %s, '10-K', '2020-01-01', %s) on conflict do nothing",
            (cid, cell.accession, cell.period_end),
        )
        c.execute(
            "insert into analytics.cell_display_state (company_id, data_point, period_end, grain, display, resolver_version) "
            "values (%s, %s, %s, %s, 'SHOWN_VALUE', %s)",
            (cid, cell.data_point, cell.period_end, cell.grain, PV),
        )
    c.commit()
    return cid


def _statuses(c):
    return {r[0]: r[1] for r in c.execute("select status, count(*) from analytics.display_cell_certificate_status group by 1")}


def test_dry_run_writes_nothing_apply_is_idempotent_and_view_is_valid(db):
    cert = dl.parse(GILD, ROOT)
    _seed(db, cert)
    assert dl.load(db, cert, PV, apply=False) == 32
    assert db.execute("select count(*) from analytics.display_cell_certificate").fetchone()[0] == 0
    assert dl.load(db, cert, PV, apply=True) == 32
    assert dl.load(db, cert, PV, apply=True) == 0  # re-load is a no-op
    assert dl.load(db, cert, PV, apply=False) == 0
    assert _statuses(db) == {"valid": 32}
    st = db.execute("select state, cells, valid_cells from analytics.company_certification_derived").fetchall()
    assert st == [("display_certified", 32, 32)]


def test_invalidation_by_proof_bump_new_filing_and_display_change(db):
    cert = dl.parse(GILD, ROOT)
    cid = _seed(db, cert)
    dl.load(db, cert, PV, apply=True)
    # a proof-version bump on one cell
    db.execute("update analytics.cell_display_state set resolver_version = 'res-v2' where data_point = 'total_assets' and period_end = '2016-12-31'")
    # a cell that stops being shown
    db.execute("update analytics.cell_display_state set display = 'OPEN' where data_point = 'sbc' and period_end = '2020-12-31'")
    # a later annual filing printing a certified period (2022 year end is within 3 years of 2020 and later)
    db.execute(
        "insert into core.filing (company_id, accession_number, form, filing_date, period_of_report) "
        "values (%s, '0000882095-99-000001', '10-K', '2030-01-01', '2021-12-31')",
        (cid,),
    )
    db.commit()
    s = _statuses(db)
    assert s.get("stale_proof") == 1 and s.get("stale_display") == 1 and s.get("stale_filing", 0) >= 1
    assert db.execute("select state from analytics.company_certification_derived").fetchone()[0] == "stale"
    n = db.execute("select analytics.invalidate_display_cell_certificates()").fetchone()[0]
    assert n == sum(v for k, v in s.items() if k != "valid")
    assert db.execute("select analytics.invalidate_display_cell_certificates()").fetchone()[0] == 0
    reasons = {r[0] for r in db.execute("select invalidated_reason from analytics.display_cell_certificate where invalidated_at is not null")}
    assert reasons == {"stale_proof", "stale_display", "stale_filing"}


def test_constraints_and_unknown_accession(db):
    cert = dl.parse(GILD, ROOT)
    db.execute("insert into core.company values (%s, 'x')", (cert.cells[0].company_id,))
    db.commit()
    dl.load(db, cert, PV, apply=True)
    assert _statuses(db) == {"unverifiable_accession": 32}
    with pytest.raises(psycopg.errors.CheckViolation):
        db.execute("update analytics.display_cell_certificate set invalidated_at = now() where id = (select min(id) from analytics.display_cell_certificate)")
    db.rollback()
    assert date(2026, 11, 16)  # certified_at comes from the certificate, not load time
    assert db.execute("select distinct certified_at::date from analytics.display_cell_certificate").fetchall() == [(date(2026, 11, 16),)]
