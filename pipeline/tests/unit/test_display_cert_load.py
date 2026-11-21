"""analytics.display_cell_certificate (0132) and the certificate loader display_cert_load (JSON, display-certificate/1).

Parser tests run on the real signed GILD and JNJ certificates in data-team/strategy/approvals/certificates/. DB tests build
a minimal core/fsn/analytics schema in an isolated Postgres clone, apply 0130 and 0132 as written, and prove the loader
and the read-time invalidation: a restatement marks a cell stale, a same-value later filing does not, a version-only
change does not, a sampled cell is never verified, the latest certificate wins."""

import copy
import json
import re
from decimal import Decimal
from pathlib import Path

import psycopg
import pytest
from scrooner_pipeline.certification import display_cert_load as dl

ROOT = Path(__file__).resolve().parents[3]
DB = ROOT / "pipeline" / "db"
CERTS = ROOT / "data-team" / "strategy" / "approvals" / "certificates"
GILD = CERTS / "GILD-e4ed0b0f7eb9.json"
JNJ = CERTS / "JNJ-674389ae0acd.json"


def _sql(num):
    f = list(DB.glob(f"pending/{num}_*.sql")) + list(DB.glob(f"migrations/{num}_*.sql"))
    assert len(f) == 1
    return f[0].read_text()


def test_loads_both_signed_certificates_every_cell_with_evidence():
    for path, ticker in ((GILD, "GILD"), (JNJ, "JNJ")):
        c = dl.parse(path, ROOT)
        assert (c.ticker, c.verdict, len(c.cells), c.drawn) == (ticker, "PASS", 506, 32)
        assert c.detector_version and c.resolver and c.code_sha and c.sample_hash == c.sample_hash.lower()
    g = dl.parse(GILD, ROOT)
    by = {}
    for x in g.cells:
        by[x.evidence] = by.get(x.evidence, 0) + 1
    assert by == {"drawn": 32, "census": 22, "sampled": 452}
    assert all(x.result == "SAMPLED" for x in g.cells if x.evidence == "sampled")
    assert any(x.display == "HIDDEN_ROW" and x.shown_value is None for x in g.cells)
    ta = [x for x in g.cells if x.data_point == "total_assets" and x.grain == "I" and x.shown_value == Decimal("56977000000")]
    assert ta and isinstance(ta[0].shown_value, Decimal)


def _tamper(tmp_path, mutate):
    root = tmp_path
    doc = json.loads(GILD.read_text())
    (root / "data-team/strategy/certification").mkdir(parents=True, exist_ok=True)
    cov = root / doc["coverage_path"]
    cov.write_bytes((ROOT / doc["coverage_path"]).read_bytes())
    mutate(doc, cov)
    p = root / "c.json"
    p.write_text(json.dumps(doc))
    return p, root


def test_refuses_bad_certificates(tmp_path):
    def run(mutate, match):
        p, root = _tamper(tmp_path, mutate)
        with pytest.raises(ValueError, match=match):
            dl.parse(p, root)

    run(lambda d, cov: d.update(verdict="FAIL"), "only PASS")
    run(lambda d, cov: cov.write_bytes(cov.read_bytes().replace(b"56977000000", b"56977000001", 1)), "hashes to")
    run(lambda d, cov: d.pop("code_sha"), "schema violations")
    run(lambda d, cov: d.update(extra=1), "schema violations")

    def wrong_value(d, cov):
        next(c for c in d["cells"] if c["evidence"] == "drawn")["shown_value"] = "1"

    run(wrong_value, "disagrees with the coverage file")

    def sampled_marked_match(d, cov):
        next(c for c in d["cells"] if c["evidence"] == "sampled")["result"] = "MATCH"

    run(sampled_marked_match, "evidence sampled with result MATCH")

    def bound_n(d, cov):
        d["bound"]["n"] = 33

    run(bound_n, "bound.n")


@pytest.fixture
def db(isolated_database_url):
    with psycopg.connect(isolated_database_url) as c:
        c.execute("drop schema if exists analytics cascade; drop schema if exists core cascade; drop schema if exists fsn cascade")
        c.execute("create schema core; create schema analytics; create schema fsn")
        c.execute(
            "create table core.company (id bigint primary key, cik text);"
            "create table core.filing (id bigint generated always as identity primary key, company_id bigint, "
            "accession_number text unique, form text, filing_date date, period_of_report date);"
            "create table analytics.company_certification (company_id bigint primary key);"
        )
        fsn = _sql("0118") if False else (DB / "migrations" / "0118_fsn_store.sql").read_text()
        for name in ("filing", "tag", "dim", "value"):
            c.execute(re.search(rf"create table if not exists fsn\.{name} \(.*?\n\);", fsn, re.S).group(0)
                      .replace("references core.company (id)", ""))
        c.execute("insert into fsn.dim (id, dimh, segments, segt) overriding system value values (0, '0x00000000', '', false)")
        c.execute(re.sub(r"references core\.company \(id\)", "", _sql("0130")))
        c.execute(_sql("0132"))
        c.execute(_sql("0134"))
        c.commit()
        yield c


def _hc(cell):
    """hide_class the live state would hold (the GILD certificate states none for its hidden rows)."""
    return None if cell.display == 'SHOWN_VALUE' else (cell.hide_class or cell.reason_code)


def _seed(c, cert, version="res-v1"):
    """core.filing + display state + fsn.value so every SHOWN cell is valid. The value printed is the certified one."""
    cid = cert.company_id
    c.execute("insert into core.company values (%s, 'x')", (cid,))
    for cell in cert.cells:
        if cell.display == "SHOWN_VALUE":
            c.execute(
                "insert into core.filing (company_id, accession_number, form, filing_date, period_of_report) "
                "values (%s, %s, '10-K', '2020-01-01', %s) on conflict do nothing",
                (cid, cell.accession, cell.period_end),
            )
        c.execute(
            "insert into analytics.cell_display_state (company_id, data_point, period_end, grain, display, hide_class, "
            "evidence_accession, resolver_version) values (%s, %s, %s, %s, %s, %s, %s, %s)",
            (cid, cell.data_point, cell.period_end, cell.grain, cell.display, _hc(cell),
             cell.accession if cell.display == "SHOWN_VALUE" else None, version),
        )
    for acc in {x.accession for x in cert.cells if x.accession}:
        c.execute("insert into fsn.filing (accession, company_id, cik, form, fsn_set, accepted) values (%s, %s, 'x', '10-K', 's', '2020-01-01')", (acc, cid))
    tag_ids = {}
    for cell in cert.cells:
        for t, d in cell.restate_keys:
            if t not in tag_ids:
                tag_ids[t] = c.execute("insert into fsn.tag (tag, version) values (%s, 'v') returning id", (t,)).fetchone()[0]
    c.commit()
    return tag_ids


def _print_value(c, cert, tag_ids, cell, accession, value, accepted="2020-01-01", form="10-K", new_filing=False):
    """One fsn.value row: `accession` prints `value` for the cell's first restate key and period."""
    cid = cert.company_id
    if new_filing:
        c.execute("insert into fsn.filing (accession, company_id, cik, form, fsn_set, accepted) values (%s, %s, 'x', %s, 's', %s)", (accession, cid, form, accepted))
    fid = c.execute("select id from fsn.filing where accession = %s", (accession,)).fetchone()[0]
    c.execute(
        "insert into fsn.value (filing_id, company_id, tag_id, ddate, qtrs, uom, dim_id, value) values (%s, %s, %s, %s, %s, 'USD', 0, %s)",
        (fid, cid, tag_ids[cell.restate_keys[0][0]], cell.period_end, 0 if cell.grain == "I" else 4, value),
    )
    c.commit()


def _statuses(c):
    return {r[0]: r[1] for r in c.execute("select status, count(*) from analytics.display_cell_certificate_status group by 1")}


def _cell(cert, dp, evidence=None):
    return next(x for x in cert.cells if x.data_point == dp and x.display == "SHOWN_VALUE" and (evidence is None or x.evidence == evidence))


def test_dry_run_writes_nothing_apply_loads_all_cells_and_is_idempotent(db):
    cert = dl.parse(GILD, ROOT)
    _seed(db, cert)
    assert dl.load(db, cert, apply=False) == 506
    assert db.execute("select count(*) from analytics.display_cell_certificate").fetchone()[0] == 0
    assert dl.load(db, cert, apply=True) == 506
    assert dl.load(db, cert, apply=True) == 0
    assert dl.load(db, cert, apply=False) == 0
    assert _statuses(db) == {"valid": 506}
    st = db.execute(
        "select state, cells, valid_cells, drawn_cells, census_cells, sampled_cells from analytics.company_certification_derived"
    ).fetchall()
    assert st == [("display_certified", 506, 506, 32, 22, 452)]
    # versions and identity come from the certificate
    v = db.execute("select distinct detector_version, resolver, code_sha, sample_hash from analytics.display_cell_certificate").fetchall()
    assert v == [(cert.detector_version, cert.resolver, cert.code_sha, cert.sample_hash)]
    # a sampled cell is never stored as verified
    with pytest.raises(psycopg.errors.CheckViolation):
        db.execute("update analytics.display_cell_certificate set result = 'MATCH' where evidence = 'sampled' and id = (select min(id) from analytics.display_cell_certificate where evidence = 'sampled')")
    db.rollback()
    assert db.execute("select count(*) from analytics.display_cell_certificate where evidence = 'sampled' and result <> 'SAMPLED'").fetchone()[0] == 0


def test_restatement_marks_stale_same_value_and_version_bump_do_not(db):
    cert = dl.parse(GILD, ROOT)
    tags = _seed(db, cert)
    cell = _cell(cert, "total_assets", "drawn")
    _print_value(db, cert, tags, cell, cell.accession, cell.shown_value)  # the certified filing's own printed value
    dl.load(db, cert, apply=True)
    assert _statuses(db) == {"valid": 506}

    # a later 10-K re-presents the period as a comparative column with the SAME value: nothing changes
    _print_value(db, cert, tags, cell, "0000000000-27-000001", cell.shown_value, accepted="2027-02-01", new_filing=True)
    assert _statuses(db) == {"valid": 506}

    # a version-only bump (resolver_version differs, nothing else) makes nothing stale
    db.execute("update analytics.cell_display_state set resolver_version = 'res-v2'")
    db.commit()
    assert _statuses(db) == {"valid": 506}

    # a later 10-Q printing a DIFFERENT value for the same tag, period and dimensions: a restatement
    _print_value(db, cert, tags, cell, "0000000000-27-000002", cell.shown_value + 1, accepted="2027-05-01", form="10-Q", new_filing=True)
    s = _statuses(db)
    assert s == {"valid": 505, "stale_restated": 1}
    assert db.execute("select state, valid_cells from analytics.company_certification_derived").fetchone() == ("stale", 505)
    assert db.execute("select analytics.invalidate_display_cell_certificates(%s)", (cert.company_id,)).fetchone()[0] == 1
    assert db.execute("select analytics.invalidate_display_cell_certificates()").fetchone()[0] == 0
    assert db.execute("select invalidated_reason from analytics.display_cell_certificate where invalidated_at is not null").fetchall() == [("restated",)]


def test_display_and_accession_change_are_stale_but_not_made_permanent(db):
    cert = dl.parse(GILD, ROOT)
    _seed(db, cert)
    dl.load(db, cert, apply=True)
    a = _cell(cert, "sbc") if any(x.data_point == "sbc" for x in cert.cells) else _cell(cert, "total_assets", "drawn")
    b = next(x for x in cert.cells if x.display == "HIDDEN_ROW")
    db.execute("update analytics.cell_display_state set display = 'OPEN', hide_class = null where data_point = %s and period_end = %s", (a.data_point, a.period_end))
    db.execute("update analytics.cell_display_state set evidence_accession = '0000000000-99-999999' where data_point = %s and period_end = %s and grain = %s", (cert.cells[0].data_point, cert.cells[0].period_end, cert.cells[0].grain))
    db.execute("update analytics.cell_display_state set hide_class = 'pre_filing' where data_point = %s and period_end = %s", (b.data_point, b.period_end))
    db.commit()
    s = _statuses(db)
    # display change and accession change are stale; a hide_class change is not when the certificate states none (GILD)
    assert s == {"valid": 504, "stale_display": 1, "stale_accession": 1}
    assert db.execute("select state from analytics.company_certification_derived").fetchone()[0] == "stale"
    assert db.execute("select analytics.invalidate_display_cell_certificates()").fetchone()[0] == 0  # drift is not permanent
    # restoring the certified state restores validity
    db.execute("delete from analytics.cell_display_state")
    _seed_state_back(db, cert)
    assert _statuses(db) == {"valid": 506}


def _seed_state_back(c, cert):
    for cell in cert.cells:
        c.execute(
            "insert into analytics.cell_display_state (company_id, data_point, period_end, grain, display, hide_class, evidence_accession, resolver_version) "
            "values (%s, %s, %s, %s, %s, %s, %s, 'res-v9')",
            (cert.company_id, cell.data_point, cell.period_end, cell.grain, cell.display, _hc(cell),
             cell.accession if cell.display == "SHOWN_VALUE" else None),
        )
    c.commit()


def test_latest_certificate_wins_and_older_is_superseded(db, tmp_path):
    cert = dl.parse(GILD, ROOT)
    _seed(db, cert)
    dl.load(db, cert, apply=True)
    newer = copy.deepcopy(cert)
    object.__setattr__(newer, "sample_hash", "b" * 64)
    object.__setattr__(newer, "certified_at", cert.certified_at.replace(day=cert.certified_at.day + 1))
    assert dl.load(db, newer, apply=True) == 506
    s = _statuses(db)
    assert s == {"valid": 506, "invalidated": 506}
    reasons = {r[0] for r in db.execute("select invalidated_reason from analytics.display_cell_certificate where sample_hash = %s", (cert.sample_hash,))}
    assert reasons == {"superseded"}
    row = db.execute("select sample_hash, state, cells from analytics.company_certification_derived").fetchall()
    assert row == [("b" * 64, "display_certified", 506)]


def test_unknown_accession_is_unverifiable(db):
    cert = dl.parse(GILD, ROOT)
    db.execute("insert into core.company values (%s, 'x')", (cert.company_id,))
    db.commit()
    dl.load(db, cert, apply=True)
    s = _statuses(db)
    assert s.get("unverifiable_accession") == sum(1 for x in cert.cells if x.display == "SHOWN_VALUE")
    with pytest.raises(psycopg.errors.CheckViolation):
        db.execute("update analytics.display_cell_certificate set invalidated_at = now() where id = (select min(id) from analytics.display_cell_certificate)")
    db.rollback()
    assert db.execute("select distinct certified_at::date from analytics.display_cell_certificate").fetchall() == [(cert.certified_at.date(),)]


OPTIONAL_TEXT = ("hide_class", "reason_code", "r_page", "tag", "accession")


def test_blank_optional_text_is_null_in_the_parsed_certificate():
    """The committed JNJ JSON holds "" for hide_class on 462 shown cells; the loader must hand NULL to the database."""
    raw = json.loads(JNJ.read_text())
    assert sum(1 for c in raw["cells"] if c["hide_class"] == "") == 462  # the input really has the blank
    cert = dl.parse(JNJ, ROOT)
    for cell in cert.cells:
        for f in OPTIONAL_TEXT:
            v = getattr(cell, f)
            assert v is None or (v.strip() == v and v != ""), (f, v)
    assert all(r[6] != "" for r in dl.rows(cert))
    assert dl._opt("  ") is None and dl._opt("") is None and dl._opt(" a ") == "a" and dl._opt(None) is None


def test_jnj_shown_cells_are_valid_not_stale_display(db):
    cert = dl.parse(JNJ, ROOT)
    _seed(db, cert)
    dl.load(db, cert, apply=True)
    assert db.execute("select count(*) from analytics.display_cell_certificate where btrim(hide_class) = ''").fetchone()[0] == 0
    assert _statuses(db) == {"valid": 506}


def test_blank_optional_text_is_refused_by_the_table(db):
    cert = dl.parse(GILD, ROOT)
    _seed(db, cert)
    dl.load(db, cert, apply=True)
    for col in ("hide_class", "reason_code", "r_page", "tag", "detector_version", "resolver", "code_sha", "draw_seed"):
        with pytest.raises(psycopg.errors.CheckViolation):
            db.execute(f"update analytics.display_cell_certificate set {col} = ' ' where id = (select min(id) from analytics.display_cell_certificate)")
        db.rollback()


def test_0134_text_has_the_fixes():
    sql = _sql("0134")
    assert sql.rstrip().endswith(";")
    assert "idx_fsn_value_series" in sql and "later.dim_id = 0" in sql
    assert "lf.company_id = c.company_id" in sql
    assert "btrim(hide_class) = ''" in sql


def _dimensioned_cell_setup(db):
    """GILD, with the total_assets drawn cell keyed to a dimensioned member; the base filing prints V under dim D."""
    import dataclasses

    cert = dl.parse(GILD, ROOT)
    cell = _cell(cert, "total_assets", "drawn")
    tag = cell.restate_keys[0][0]
    new = dataclasses.replace(cell, restate_keys=((tag, "Seg=Mem;"),))
    cert = dataclasses.replace(cert, cells=tuple(new if x is cell else x for x in cert.cells))
    tags = _seed(db, cert)
    did = db.execute("insert into fsn.dim (dimh, segments, segt) values ('0x01', 'Seg=Mem;', true) returning id").fetchone()[0]
    return cert, new, tags, did


def _print_dim(db, cert, tags, cell, accession, value, did, accepted="2020-01-01", form="10-K", new_filing=False):
    cid = cert.company_id
    if new_filing:
        db.execute("insert into fsn.filing (accession, company_id, cik, form, fsn_set, accepted) values (%s, %s, 'x', %s, 's', %s)", (accession, cid, form, accepted))
    fid = db.execute("select id from fsn.filing where accession = %s", (accession,)).fetchone()[0]
    db.execute(
        "insert into fsn.value (filing_id, company_id, tag_id, ddate, qtrs, uom, dim_id, value) values (%s, %s, %s, %s, %s, 'USD', %s, %s)",
        (fid, cid, tags[cell.restate_keys[0][0]], cell.period_end, 0 if cell.grain == "I" else 4, did, value),
    )
    db.commit()


def test_restatement_detected_on_the_dimensioned_branch(db):
    cert, cell, tags, did = _dimensioned_cell_setup(db)
    _print_dim(db, cert, tags, cell, cell.accession, cell.shown_value, did)
    dl.load(db, cert, apply=True)
    assert _statuses(db) == {"valid": 506}
    _print_dim(db, cert, tags, cell, "0000000000-27-000005", cell.shown_value, did, accepted="2027-02-01", new_filing=True)
    assert _statuses(db) == {"valid": 506}  # same value on a later filing: no restatement
    _print_dim(db, cert, tags, cell, "0000000000-27-000006", cell.shown_value + 1, did, accepted="2027-05-01", form="10-Q", new_filing=True)
    assert _statuses(db) == {"valid": 505, "stale_restated": 1}
    assert db.execute("select analytics.invalidate_display_cell_certificates(%s)", (cert.company_id,)).fetchone()[0] == 1


def test_later_filing_of_another_company_is_not_a_restatement(db):
    cert = dl.parse(GILD, ROOT)
    tags = _seed(db, cert)
    cell = _cell(cert, "total_assets", "drawn")
    _print_value(db, cert, tags, cell, cell.accession, cell.shown_value)
    dl.load(db, cert, apply=True)
    db.execute("insert into core.company values (999, 'y')")
    db.execute("insert into fsn.filing (accession, company_id, cik, form, fsn_set, accepted) values ('0000000000-27-000099', 999, 'y', '10-K', 's', '2027-02-01')")
    fid = db.execute("select id from fsn.filing where accession = '0000000000-27-000099'").fetchone()[0]
    db.execute(
        "insert into fsn.value (filing_id, company_id, tag_id, ddate, qtrs, uom, dim_id, value) values (%s, 999, %s, %s, %s, 'USD', 0, %s)",
        (fid, tags[cell.restate_keys[0][0]], cell.period_end, 0 if cell.grain == "I" else 4, cell.shown_value + 1),
    )
    db.commit()
    assert _statuses(db) == {"valid": 506}
