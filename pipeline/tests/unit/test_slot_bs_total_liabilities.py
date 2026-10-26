"""Release-1 write path for slot.bs_total_liabilities@1 on REAL SQL (throwaway
database, scratch schemas; production schemas are never touched). Needs
SCROONER_TEST_DATABASE_URL like test_cell_store_sql.py. Guard tests are
mutation-checked (see the report): each guard's test fails when the guard is removed."""

import hashlib
import json
from pathlib import Path

import psycopg
import pytest
from scrooner_pipeline.common import cell_store as cs
from scrooner_pipeline.mapper import slot_bs_total_liabilities as m

MIG = Path(__file__).resolve().parents[2] / "db" / "migrations"
A, C = "sl_a", "sl_c"
ON = {"SCROONER_RULES_ENABLED": m.RULE_ID}
OFF: dict[str, str] = {}


def _rw(sql: str) -> str:
    return sql.replace("analytics.", f"{A}.").replace("core.", f"{C}.")


def _retired_ddl() -> str:
    t = (MIG / "0098_per_share_gap_cause_and_canonical_fact_retired.sql").read_text()
    return "create table" + t.split("create table", 1)[1].split("create index")[0] + ";"


class _Cur:
    def __init__(self, c):
        self._c = c

    def __enter__(self):
        self._c.__enter__()
        return self

    def __exit__(self, *a):
        return self._c.__exit__(*a)

    def execute(self, sql, p=None):
        self._c.execute(_rw(sql), p)
        return self

    def executemany(self, sql, p):
        self._c.executemany(_rw(sql), p)

    def fetchone(self):
        return self._c.fetchone()

    def fetchall(self):
        return self._c.fetchall()

    @property
    def rowcount(self):
        return self._c.rowcount


class _Conn:
    def __init__(self, c):
        self._c = c

    def cursor(self):
        return _Cur(self._c.cursor())

    def execute(self, sql, p=None):
        return self.cursor().execute(sql, p)

    def commit(self):
        self._c.commit()

    def rollback(self):
        self._c.rollback()


@pytest.fixture
def db(isolated_database_url):
    raw = psycopg.connect(isolated_database_url)
    for s in (A, C):
        raw.execute(f"drop schema if exists {s} cascade")
        raw.execute(f"create schema {s}")
    raw.execute(f"create table {C}.company (id bigint primary key, cik text unique)")
    raw.execute(
        f"""create table {C}.period (id bigint primary key, company_id bigint references {C}.company(id),
        start_date date, end_date date, period_type text)"""
    )
    raw.execute(f"create table {A}.canonical_concept (id bigint primary key, name text unique)")
    raw.execute(
        f"""create table {A}.canonical_fact (id bigint generated always as identity primary key,
        company_id bigint not null references {C}.company(id),
        canonical_concept_id bigint not null references {A}.canonical_concept(id),
        period_id bigint not null references {C}.period(id), value numeric not null,
        source_fact_ids bigint[] not null, resolved_at timestamptz not null default now(),
        unique (company_id, canonical_concept_id, period_id))"""
    )
    raw.execute(f"create table {A}.metric_definition (id bigint primary key, metric_name text, status text)")
    raw.execute(f"create table {A}.metric_definition_input (id bigint generated always as identity primary key, metric_definition_id bigint, canonical_concept_id bigint, role text)")
    raw.execute(_rw(_retired_ddl()))
    raw.execute(_rw((MIG / "0100_cell_evidence_reason_registrant_audit.sql").read_text()))
    raw.execute(f"insert into {A}.canonical_concept values (260, 'total_liabilities_resolved')")
    raw.commit()
    yield _Conn(raw), raw
    raw.rollback()
    for s in (A, C):
        raw.execute(f"drop schema if exists {s} cascade")
    raw.commit()
    raw.close()


def _build(tmp_path, db_pair, *, mutate=None):
    """Synthetic package + matching production rows. Companies 1-4 (ciks ...1-4):
    c1: 2 differs; c2: 1 differs + 1 fill; c3: 1 hide; c4: 1 differs."""
    conn, raw = db_pair
    cells, before = [], []
    pid = 100

    def add(cik, cid, end, state, prod, slot, seed_prod=True):
        nonlocal pid
        pid += 1
        raw.execute(f"insert into {C}.company values (%s,%s) on conflict do nothing", (cid, cik))
        raw.execute(f"insert into {C}.period values (%s,%s,%s,%s,'instant')", (pid, cid, end, end))
        fid = None
        if prod is not None and seed_prod:
            fid = raw.execute(
                f"insert into {A}.canonical_fact (company_id,canonical_concept_id,period_id,value,source_fact_ids) "
                "values (%s,260,%s,%s,%s) returning id", (cid, pid, prod, [7, 8])).fetchone()[0]
        cells.append({"accession": f"0000000000-26-00000{cid}", "cik": cik, "end": end,
                      "identity": "identity_ties", "production": None if prod is None else str(prod),
                      "reading": "A_cal_roots", "release": "1", "rule": "face_sum",
                      "slot": None if slot is None else f"{slot}.0", "state": state, "stratum": "x"})
        if prod is not None:
            before.append({"canonical_concept_id": 260, "canonical_fact_id": fid, "cik": cik,
                           "company_id": cid, "end": end, "period_id": pid, "value_before": str(prod)})

    add("0000000001", 1, "2020-03-31", "slot_differs", 1000, 900)
    add("0000000001", 1, "2020-06-30", "slot_differs", 2000, 1900)
    add("0000000002", 2, "2020-03-31", "slot_differs", 3000, 2900)
    add("0000000002", 2, "2020-06-30", "slot_fills_blank", None, 555)
    add("0000000003", 3, "2020-03-31", "slot_holds_prod_has_value", 4000, None)
    add("0000000004", 4, "2020-03-31", "slot_differs", 5000, 4900)
    raw.commit()
    if mutate:
        mutate(cells, before)
    d = tmp_path / "pkg"
    d.mkdir(exist_ok=True)
    body = "".join(json.dumps(c) + "\n" for c in cells)
    (d / "bs_release_release1_cells.jsonl").write_text(body)
    (d / "bs_release_r1_before_image.jsonl").write_text("".join(json.dumps(b) + "\n" for b in before))
    (d / "bs_release_r1_plan.json").write_text(json.dumps({"before_image_rows": len(before)}))
    digest = hashlib.sha256(body.encode()).hexdigest()
    by: dict[str, int] = {}
    for c in cells:
        by[c["state"]] = by.get(c["state"], 0) + 1
    (d / "PACKAGE.json").write_text(json.dumps({"rule_id": m.RULE_ID, "release1": {
        "cells_file": "bs_release_release1_cells.jsonl", "sha256": digest, "cells": len(cells),
        "companies": len({c["cik"] for c in cells}), "by_state": by}}))
    return d, digest


def _values(raw):
    return {r[0]: r[1] for r in raw.execute(
        f"select period_id, value from {A}.canonical_fact order by period_id").fetchall()}


def _apply(conn, pkg, **kw):
    return m.apply(conn, pkg, confirm=kw.pop("confirm", m.CONFIRM_TOKEN),
                   environ=kw.pop("environ", ON), **kw)


# ----------------------------------------------------------------- guards
@pytest.mark.unit
def test_digest_mismatch_with_reviewed_argument_refuses(tmp_path, db):
    d, digest = _build(tmp_path, db)
    with pytest.raises(m.ReleaseRefused, match="reviewed digest"):
        m.load_package(d, "0" * 64)


@pytest.mark.unit
def test_tampered_cells_file_refuses_even_with_its_new_hash(tmp_path, db):
    d, digest = _build(tmp_path, db)
    f = d / "bs_release_release1_cells.jsonl"
    f.write_text(f.read_text().replace('"900.0"', '"901.0"').replace("900.0", "901.0"))
    new = hashlib.sha256(f.read_bytes()).hexdigest()
    with pytest.raises(m.ReleaseRefused, match="PACKAGE.json digest"):
        m.load_package(d, new)


@pytest.mark.unit
def test_rule_off_and_dry_run_flag_refuse_apply_and_write_nothing(tmp_path, db):
    conn, raw = db
    d, digest = _build(tmp_path, db)
    pkg = m.load_package(d, digest)
    before = _values(raw)
    for env in (OFF, {"SCROONER_RULES_DRYRUN": m.RULE_ID}):
        with pytest.raises(m.ReleaseRefused, match="not ON"):
            _apply(conn, pkg, environ=env)
    assert _values(raw) == before
    assert raw.execute(f"select count(*) from {A}.rule_run").fetchone()[0] == 0


@pytest.mark.unit
def test_wrong_confirm_token_refuses(tmp_path, db):
    conn, raw = db
    d, digest = _build(tmp_path, db)
    with pytest.raises(m.ReleaseRefused, match="--confirm"):
        _apply(conn, m.load_package(d, digest), confirm="yes")
    assert raw.execute(f"select count(*) from {A}.rule_run").fetchone()[0] == 0


@pytest.mark.unit
def test_unknown_company_refuses_whole_run(tmp_path, db):
    conn, raw = db
    d, digest = _build(tmp_path, db)
    raw.execute(f"update {C}.company set cik = '0000000999' where id = 4")
    raw.commit()
    before = _values(raw)
    with pytest.raises(m.ReleaseRefused, match="unknown company cik 0000000004"):
        _apply(conn, m.load_package(d, digest))
    assert _values(raw) == before


@pytest.mark.unit
def test_drift_since_package_refuses_whole_run(tmp_path, db):
    conn, raw = db
    d, digest = _build(tmp_path, db)
    raw.execute(f"update {A}.canonical_fact set value = 123 where company_id = 4")
    raw.commit()
    before = _values(raw)
    with pytest.raises(m.ReleaseRefused, match="neither production nor slot"):
        _apply(conn, m.load_package(d, digest))
    assert _values(raw) == before


# ---------------------------------------------------------------- dry run
@pytest.mark.unit
def test_dry_run_counts_and_writes_nothing(tmp_path, db):
    conn, raw = db
    d, digest = _build(tmp_path, db)
    pkg = m.load_package(d, digest)
    before = _values(raw)
    with conn.cursor() as cur:
        planned, s = m.plan(cur, pkg)
    conn.rollback()
    assert (s["changed"], s["filled"], s["hidden"], s["companies"]) == (4, 1, 1, 4)
    assert s["per_company"]["0000000002"] == {"change": 1, "fill": 1}
    assert _values(raw) == before
    for t in ("rule_run", "canonical_fact_retired", "cell_evidence", "cell_blank_reason"):
        assert raw.execute(f"select count(*) from {A}.{t}").fetchone()[0] == 0


# ------------------------------------------------------- apply and restore
@pytest.mark.unit
def test_apply_then_restore_round_trip_is_exact(tmp_path, db):
    conn, raw = db
    d, digest = _build(tmp_path, db)
    snap = raw.execute(
        f"select company_id, canonical_concept_id, period_id, value, source_fact_ids from {A}.canonical_fact order by period_id"
    ).fetchall()
    res = _apply(conn, m.load_package(d, digest), batch_companies=2)
    assert (res["replaced"], res["inserted"], res["removed"]) == (4, 1, 1)
    assert res["batches_committed"] == 2 and res["touched_ciks"] == [f"000000000{i}" for i in (1, 2, 3, 4)]
    vals = _values(raw)
    assert vals[101] == 900 and vals[102] == 1900 and vals[103] == 2900 and vals[104] == 555
    assert 105 not in vals and vals[106] == 4900
    ev = raw.execute(f"select count(*), count(distinct accession), bool_and(evidence_level='DATA-INFERRED') from {A}.cell_evidence").fetchone()
    assert ev == (6, 4, True)
    br = raw.execute(f"select state, defect_class, owner from {A}.cell_blank_reason").fetchall()
    assert br == [("defect", "guard_hidden", "data_engineer_l1")]
    assert raw.execute(f"select count(*) from {A}.canonical_fact_retired where action in ('replaced','removed')").fetchone()[0] == 5
    # second apply is a no-op (every cell already at the slot value)
    again = _apply(conn, m.load_package(d, digest))
    assert (again["replaced"], again["inserted"], again["removed"]) == (0, 0, 0)
    out = m.restore(conn, res["run_id"], confirm=m.CONFIRM_TOKEN)
    assert out["restored_archive_rows"] == 6
    assert raw.execute(
        f"select company_id, canonical_concept_id, period_id, value, source_fact_ids from {A}.canonical_fact order by period_id"
    ).fetchall() == snap
    assert raw.execute(f"select count(*) from {A}.cell_blank_reason").fetchone()[0] == 0
    assert raw.execute(f"select count(*) from {A}.rule_run where mode='rollback'").fetchone()[0] == 1


@pytest.mark.unit
def test_restore_needs_confirm_and_an_apply_run(tmp_path, db):
    conn, raw = db
    d, digest = _build(tmp_path, db)
    res = _apply(conn, m.load_package(d, digest))
    with pytest.raises(m.ReleaseRefused):
        m.restore(conn, res["run_id"], confirm="")
    with pytest.raises(m.ReleaseRefused):
        m.restore(conn, "00000000-0000-0000-0000-000000000000", confirm=m.CONFIRM_TOKEN)


@pytest.mark.unit
def test_partial_failure_rolls_back_the_failing_batch_and_run_is_resumable(tmp_path, db, monkeypatch):
    conn, raw = db
    d, digest = _build(tmp_path, db)
    pkg = m.load_package(d, digest)
    real = cs.write_blank_reasons
    calls = {"n": 0}

    def boom(c, run_id, reasons):
        calls["n"] += 1
        if calls["n"] == 2:  # second batch, AFTER its replace/archive/evidence ran
            raise RuntimeError("injected")
        return real(c, run_id, reasons)

    monkeypatch.setattr(cs, "write_blank_reasons", boom)
    with pytest.raises(RuntimeError, match="injected"):
        _apply(conn, pkg, batch_companies=2)
    vals = _values(raw)
    # batch 1 (companies 1,2) committed; batch 2 (3,4) left NO trace
    assert vals[101] == 900 and vals[104] == 555
    assert vals[105] == 4000 and vals[106] == 5000
    run_id = raw.execute(f"select run_id::text from {A}.rule_run").fetchone()[0]
    assert raw.execute(f"select count(*) from {A}.cell_evidence").fetchone()[0] == 4
    assert raw.execute(f"select count(*) from {A}.canonical_fact_retired where company_id in (3,4)").fetchone()[0] == 0
    # resume finishes only the remainder
    monkeypatch.setattr(cs, "write_blank_reasons", real)
    res = _apply(conn, pkg, batch_companies=2, resume_run_id=run_id)
    assert (res["replaced"], res["removed"]) == (1, 1)
    # a restore of the run undoes batch 1 and the resumed batch together
    m.restore(conn, run_id, confirm=m.CONFIRM_TOKEN)
    assert _values(raw)[101] == 1000 and _values(raw)[105] == 4000 and 104 not in _values(raw)


@pytest.mark.unit
def test_missing_period_for_a_fill_refuses(tmp_path, db):
    conn, raw = db
    d, digest = _build(tmp_path, db)
    raw.execute(f"delete from {C}.period where id = 104")
    raw.commit()
    with pytest.raises(m.ReleaseRefused, match="0 instant periods"):
        _apply(conn, m.load_package(d, digest))


@pytest.mark.unit
def test_downstream_consumers_read_from_definition_tables(tmp_path, db):
    conn, raw = db
    raw.execute(f"insert into {A}.metric_definition values (1,'x_ratio','active'),(2,'old','deprecated')")
    raw.execute(f"insert into {A}.metric_definition_input (metric_definition_id,canonical_concept_id,role) values (1,260,'n'),(2,260,'n')")
    raw.commit()
    with conn.cursor() as cur:
        assert m.downstream_consumers(cur, 260) == ["x_ratio"]
    conn.rollback()


@pytest.mark.unit
def test_rule_is_registered_default_off():
    from scrooner_pipeline.common import rule_flags as rf

    assert m.RULE_ID in rf.RULES and rf.RULES[m.RULE_ID].dry_run
    assert rf.rule_mode(m.RULE_ID, {}) == "off"


@pytest.mark.unit
def test_real_package_digest_and_counts():
    meta = json.loads((m.PACKAGE_DIR / "PACKAGE.json").read_text())
    pkg = m.load_package(m.PACKAGE_DIR, meta["release1"]["sha256"])
    assert len(pkg.cells) == 3533 and len(pkg.before_image) == 3443
    with pytest.raises(m.ReleaseRefused):
        m.load_package(m.PACKAGE_DIR, "f" * 64)
