"""The generic slot-record release writer on REAL SQL: every migration applied
(CI's test database; opt-in locally via SCROONER_TEST_DATABASE_URL). The
writer commits for real (one transaction per company); each test gets its own
throwaway copy of the database, so nothing is shared between tests."""

import dataclasses
import hashlib
import json
from datetime import date
from decimal import Decimal

import pytest
from scrooner_pipeline.mapper import canonical_archive as ca
from scrooner_pipeline.mapper import slot_release_writer as w

psycopg = pytest.importorskip("psycopg")

CIK_A, CIK_B = "0000000101", "0000000102"
ACC_A, ACC_B = "0000000101-25-000001", "0000000102-25-000001"
NI = w.SPECS["is_net_income_1"]
TL = w.SPECS["bs_total_liabilities_1"]
ON_NI = {"SCROONER_RULES_ENABLED": NI.rule_id}
ON_TL = {"SCROONER_RULES_ENABLED": TL.rule_id}


def _one(conn, sql, params=()):
    return conn.execute(sql, params).fetchone()[0]


# ------------------------------------------------------------------ files only
def write_package(root, spec, rows, *, meta_sha=None):
    pdir = root / spec.package
    pdir.mkdir(parents=True)
    body = "".join(json.dumps(r, sort_keys=True) + "\n" for r in rows)
    name = "cells.jsonl"
    (pdir / name).write_text(body)
    sha = hashlib.sha256(body.encode()).hexdigest()
    key = "cells_file" if spec is TL else "file"
    meta = {"rule_id": spec.rule_id, "release1": {key: name, "sha256": meta_sha or sha}}
    (pdir / "PACKAGE.json").write_text(json.dumps(meta))
    return sha


def ni_row(cik, acc, start, end, compare, slot, prod=None, cf_id=None):
    return {
        "cik": cik,
        "accession": acc,
        "start": start,
        "end": end,
        "compare": compare,
        "slot_value": slot,
        "prod_value": prod,
        "prod_cf_id": cf_id,
        "slot_tag": "NetIncomeLoss",
        "gate": "G1",
        "family": "net_income",
        "form": "10-K",
    }


def test_digest_must_match_package_json_and_the_reviewed_digest(tmp_path):
    sha = write_package(
        tmp_path,
        NI,
        [ni_row(CIK_A, ACC_A, "2025-01-01", "2025-12-31", "slot_fills_blank", "5")],
    )
    assert len(w.load_package(NI, sha, root=tmp_path).cells) == 1
    with pytest.raises(w.ReleaseRefused, match="reviewed --digest"):
        w.load_package(NI, "0" * 64, root=tmp_path)
    other = tmp_path / "b"
    write_package(
        other,
        NI,
        [ni_row(CIK_A, ACC_A, "2025-01-01", "2025-12-31", "slot_fills_blank", "5")],
        meta_sha="f" * 64,
    )
    with pytest.raises(w.ReleaseRefused, match="PACKAGE.json"):
        w.load_package(NI, sha, root=other)


def test_duplicate_keys_and_non_release_rows_are_refused(tmp_path):
    r = ni_row(CIK_A, ACC_A, "2025-01-01", "2025-12-31", "slot_fills_blank", "5")
    sha = write_package(tmp_path, NI, [r, r])
    with pytest.raises(w.ReleaseRefused, match="duplicate"):
        w.load_package(NI, sha, root=tmp_path)
    other = tmp_path / "b"
    sha = write_package(other, NI, [{**r, "compare": "would_hide"}])
    with pytest.raises(w.ReleaseRefused, match="not a release cell"):
        w.load_package(NI, sha, root=other)


def test_grain():
    def c(s, e):
        return w.Cell(CIK_A, s, e, "insert", Decimal(1), None, ACC_A)

    assert w.grain(c(date(2025, 1, 1), date(2025, 12, 31))) == "FY"
    assert w.grain(c(date(2025, 10, 1), date(2025, 12, 31))) == "Q"
    assert w.grain(c(date(2025, 1, 1), date(2025, 6, 30))) == "TP"
    assert w.grain(c(None, date(2025, 12, 31))) == "I"


class _NoDb:
    def __getattr__(self, name):
        raise AssertionError("the database was touched before the guards passed")


def test_flag_and_token_are_checked_before_any_db_access(tmp_path):
    sha = write_package(
        tmp_path,
        NI,
        [ni_row(CIK_A, ACC_A, "2025-01-01", "2025-12-31", "slot_fills_blank", "5")],
    )
    pkg = w.load_package(NI, sha, root=tmp_path)
    with pytest.raises(w.ReleaseRefused, match="not ON"):
        w.apply(_NoDb(), pkg, confirm=NI.confirm, environ={})
    with pytest.raises(w.ReleaseRefused, match="--confirm"):
        w.apply(_NoDb(), pkg, confirm="nope", environ=ON_NI)


def test_every_registered_package_loads_with_its_recorded_digest():
    for spec in w.SPECS.values():
        meta = json.loads((w.RESULTS_DIR / spec.package / "PACKAGE.json").read_text())
        pkg = w.load_package(spec, spec.package_sha(meta))
        assert pkg.cells, spec.name


# ------------------------------------------------------------------ real SQL
@pytest.fixture
def db(isolated_database_url):
    c = psycopg.connect(isolated_database_url)
    if (
        _one(c, "select to_regclass('analytics.slot_protected_cell') is not null")
        is not True
    ):
        c.close()
        pytest.skip("needs the migrated schema (0113)")
    yield c
    c.close()


def seed(conn):
    """Company A: an FY2025 net income row (wrong, 100) with the filing's
    NetIncomeLoss fact (90), and a blank Q4 key. Company B: one wrong row.
    Plus an instant total-liabilities row for A."""
    ids = {}
    for name, cik in (("a", CIK_A), ("b", CIK_B)):
        ids[name] = _one(
            conn,
            "insert into core.company (cik, company_name) values (%s, %s) returning id",
            (cik, name),
        )
    raw = _one(
        conn,
        "insert into raw.sec_companyfacts (cik, source_url, sha256, storage_path, http_status) "
        "values (%s, 'test://cf', repeat('1', 64), 'raw/x', 200) returning id",
        (CIK_A,),
    )
    unit = _one(
        conn,
        "insert into core.unit (unit_name) values ('usd') on conflict (unit_name) "
        "do update set unit_name = excluded.unit_name returning id",
    )
    tag = _one(
        conn,
        "insert into core.concept (taxonomy, tag) values ('us-gaap', 'NetIncomeLoss') "
        "on conflict (taxonomy, tag) do update set tag = excluded.tag returning id",
    )
    for name, cc, stmt in (
        ("ni", NI.concept, "income_statement"),
        ("tl", TL.concept, "balance_sheet"),
    ):
        ids[name] = _one(
            conn,
            "insert into analytics.canonical_concept (name, statement, combination_mode) "
            "values (%s, %s, 'first_match') on conflict (name) do update set name = excluded.name "
            "returning id",
            (cc, stmt),
        )

    def period(co, s, e, kind="duration"):
        return _one(
            conn,
            "insert into core.period (company_id, start_date, end_date, period_type) "
            "values (%s, %s, %s, %s) returning id",
            (co, s, e, kind),
        )

    ids["pa_fy"] = period(ids["a"], "2025-01-01", "2025-12-31")
    ids["pa_q4"] = period(ids["a"], "2025-10-01", "2025-12-31")
    ids["pb_fy"] = period(ids["b"], "2025-01-01", "2025-12-31")
    ids["pa_i"] = period(ids["a"], "2025-12-31", "2025-12-31", "instant")
    filing = _one(
        conn,
        "insert into core.filing (company_id, accession_number, form, filing_date, period_of_report) "
        "values (%s, %s, '10-K', '2026-02-27', '2025-12-31') returning id",
        (ids["a"], ACC_A),
    )
    ids["fact"] = _one(
        conn,
        "insert into core.fact (company_id, concept_id, unit_id, period_id, filing_id, value, raw_object_id) "
        "values (%s, %s, %s, %s, %s, 90, %s) returning id",
        (ids["a"], tag, unit, ids["pa_fy"], filing, raw),
    )

    def cf(co, cc, p, v, src):
        return _one(
            conn,
            "insert into analytics.canonical_fact (company_id, canonical_concept_id, period_id, value, source_fact_ids) "
            "values (%s, %s, %s, %s, %s) returning id",
            (co, cc, p, Decimal(v), src),
        )

    ids["cf_a"] = cf(ids["a"], ids["ni"], ids["pa_fy"], "100", [ids["fact"]])
    ids["cf_b"] = cf(ids["b"], ids["ni"], ids["pb_fy"], "200", [])
    ids["cf_tl"] = cf(ids["a"], ids["tl"], ids["pa_i"], "500", [])
    conn.commit()
    return ids


def ni_rows(ids):
    return [
        ni_row(
            CIK_A,
            ACC_A,
            "2025-01-01",
            "2025-12-31",
            "slot_differs",
            "90",
            "100",
            ids["cf_a"],
        ),
        ni_row(CIK_A, ACC_A, "2025-10-01", "2025-12-31", "slot_fills_blank", "25"),
        ni_row(
            CIK_B,
            ACC_B,
            "2025-01-01",
            "2025-12-31",
            "slot_differs",
            "210",
            "200",
            ids["cf_b"],
        ),
    ]


def ni_pkg(tmp_path, ids, rows=None):
    sha = write_package(tmp_path, NI, rows or ni_rows(ids))
    return w.load_package(NI, sha, root=tmp_path)


def snapshot(conn):
    return conn.execute(
        "select company_id, canonical_concept_id, period_id, value, source_fact_ids, resolved_at "
        "from analytics.canonical_fact order by 1, 2, 3"
    ).fetchall()


def count(conn, table, where="true", params=()):
    return _one(conn, f"select count(*) from {table} where {where}", params)


def test_plan_classifies_and_resolves_lineage_read_only(db, tmp_path):
    ids = seed(db)
    before = snapshot(db)
    with db.cursor() as cur:
        pl = w.plan(cur, ni_pkg(tmp_path, ids))
    db.rollback()
    s = pl.summary
    assert (s["update"], s["insert"], s["hide"], s["already_applied"]) == (2, 1, 0, 0)
    by_cik = {(p.cell.cik, p.cell.start): p for p in pl.cells}
    assert by_cik[(CIK_A, date(2025, 1, 1))].source_fact_ids == (ids["fact"],)
    assert (
        by_cik[(CIK_B, date(2025, 1, 1))].source_fact_ids == ()
    )  # no fact in B's filing
    assert (s["lineage_fact_ids"], s["lineage_evidence_only"]) == (1, 2)
    assert snapshot(db) == before


def test_apply_writes_protects_evidences_and_restore_is_exact(db, tmp_path):
    ids = seed(db)
    before = snapshot(db)
    res = w.apply(db, ni_pkg(tmp_path, ids), confirm=NI.confirm, environ=ON_NI)
    assert (res["replaced"], res["inserted"], res["protected"], res["evidence"]) == (
        2,
        1,
        3,
        3,
    )
    vals = dict(
        db.execute(
            "select period_id, value from analytics.canonical_fact where canonical_concept_id = %s",
            (ids["ni"],),
        ).fetchall()
    )
    assert vals == {
        ids["pa_fy"]: Decimal(90),
        ids["pa_q4"]: Decimal(25),
        ids["pb_fy"]: Decimal(210),
    }
    assert _one(
        db,
        "select source_fact_ids from analytics.canonical_fact where period_id = %s and canonical_concept_id = %s",
        (ids["pa_fy"], ids["ni"]),
    ) == [ids["fact"]]
    assert (
        count(
            db,
            "analytics.slot_protected_cell",
            "run_id = %s and rule_id = %s",
            (res["run_id"], NI.rule_id),
        )
        == 3
    )
    assert (
        count(
            db,
            "analytics.cell_evidence",
            "rule_id = %s and source_hash = %s",
            (NI.rule_id, res["plan"]["digest"]),
        )
        == 3
    )
    assert (
        count(db, "analytics.canonical_fact_retired", "run_id = %s", (res["run_id"],))
        == 3
    )
    out = w.restore(db, res["run_id"], NI, confirm=NI.confirm)
    assert out["protection_removed"] == 3
    after = snapshot(db)
    # same keys, values, sources and resolved_at as before the run
    assert after == before


def test_protection_holds_against_a_nightly_resolver_write(db, tmp_path):
    ids = seed(db)
    w.apply(db, ni_pkg(tmp_path, ids), confirm=NI.confirm, environ=ON_NI)
    db.execute(
        "update analytics.canonical_fact set value = 1 where id = %s", (ids["cf_a"],)
    )
    db.execute(
        "delete from analytics.canonical_fact where canonical_concept_id = %s and period_id = %s",
        (ids["ni"], ids["pa_q4"]),
    )
    db.commit()
    vals = dict(
        db.execute(
            "select period_id, value from analytics.canonical_fact where canonical_concept_id = %s",
            (ids["ni"],),
        ).fetchall()
    )
    assert vals[ids["pa_fy"]] == Decimal(90) and vals[ids["pa_q4"]] == Decimal(25)
    assert count(db, "analytics.slot_protected_write_skipped") == 2


@pytest.mark.parametrize(
    "drift, match",
    [
        (
            "update analytics.canonical_fact set value = 101 where id = {cf_a}",
            "package expected 100",
        ),
        (
            "delete from analytics.canonical_fact where id = {cf_b}",
            "production row gone",
        ),
        (
            (
                "insert into analytics.canonical_fact (company_id, canonical_concept_id, period_id, value, source_fact_ids) "
                "values ({a}, {ni}, {pa_q4}, 7, '{{}}')"
            ),
            "production now has 7",
        ),
        (
            (
                "insert into analytics.slot_protected_cell (company_id, canonical_concept_id, period_id, rule_id, value, run_id, package_sha256) "
                "values ({b}, {ni}, {pb_fy}, 'slot.other@1', 200, 'r', 'x')"
            ),
            "already protected by slot.other@1",
        ),
    ],
)
def test_stale_refusal_writes_nothing(db, tmp_path, drift, match):
    ids = seed(db)
    pkg = ni_pkg(tmp_path, ids)
    db.execute(drift.format(**ids))
    db.commit()
    before = snapshot(db)
    with pytest.raises(w.ReleaseRefused, match=match):
        w.apply(db, pkg, confirm=NI.confirm, environ=ON_NI)
    assert snapshot(db) == before
    assert (
        count(
            db, "analytics.rule_run", "rule_id = %s and mode = 'apply'", (NI.rule_id,)
        )
        == 0
    )
    assert count(db, "analytics.canonical_fact_retired") == 0


def test_stale_row_id_is_refused(db, tmp_path):
    ids = seed(db)
    rows = ni_rows(ids)
    rows[0]["prod_cf_id"] = ids["cf_a"] + 999
    with pytest.raises(w.ReleaseRefused, match="row id"):
        w.apply(db, ni_pkg(tmp_path, ids, rows), confirm=NI.confirm, environ=ON_NI)


def test_missing_period_is_refused(db, tmp_path):
    ids = seed(db)
    rows = ni_rows(ids) + [
        ni_row(CIK_B, ACC_B, "2025-04-01", "2025-06-30", "slot_fills_blank", "3")
    ]
    with pytest.raises(w.ReleaseRefused, match="0 matching periods"):
        w.apply(db, ni_pkg(tmp_path, ids, rows), confirm=NI.confirm, environ=ON_NI)


def test_a_failed_company_rolls_back_alone_and_a_rerun_resumes(
    db, tmp_path, monkeypatch
):
    ids = seed(db)
    pkg = ni_pkg(tmp_path, ids)
    real = ca.replace_rows

    def boom(cur, rows, **kw):
        if rows and rows[0].company_id == ids["b"]:
            raise RuntimeError("connection dropped")
        return real(cur, rows, **kw)

    monkeypatch.setattr(ca, "replace_rows", boom)
    with pytest.raises(RuntimeError):
        w.apply(db, pkg, confirm=NI.confirm, environ=ON_NI)
    assert _one(
        db, "select value from analytics.canonical_fact where id = %s", (ids["cf_b"],)
    ) == Decimal(200)
    assert (
        count(db, "analytics.slot_protected_cell", "company_id = %s", (ids["a"],)) == 2
    )
    assert (
        count(db, "analytics.slot_protected_cell", "company_id = %s", (ids["b"],)) == 0
    )
    monkeypatch.setattr(ca, "replace_rows", real)
    res = w.apply(db, pkg, confirm=NI.confirm, environ=ON_NI)
    assert (
        res["plan"]["already_applied"] == 2
        and res["replaced"] == 1
        and res["touched_ciks"] == [CIK_B]
    )


def test_a_second_apply_is_a_no_op(db, tmp_path):
    ids = seed(db)
    pkg = ni_pkg(tmp_path, ids)
    w.apply(db, pkg, confirm=NI.confirm, environ=ON_NI)
    after = snapshot(db)
    res = w.apply(db, pkg, confirm=NI.confirm, environ=ON_NI)
    assert res["plan"]["already_applied"] == 3 and res["touched_ciks"] == []
    assert snapshot(db) == after


def test_restore_refuses_another_packages_run(db, tmp_path):
    ids = seed(db)
    res = w.apply(db, ni_pkg(tmp_path, ids), confirm=NI.confirm, environ=ON_NI)
    other = dataclasses.replace(NI, name="is_utilities_net_income_1", confirm="X")
    with pytest.raises(w.ReleaseRefused, match="not an apply run"):
        w.restore(db, res["run_id"], other, confirm="X")


def tl_rows():
    return [
        {
            "cik": CIK_A,
            "end": "2025-12-31",
            "state": "slot_holds_prod_has_value",
            "slot": None,
            "production": "500",
            "accession": ACC_A,
            "rule": "face_sum",
            "reading": "B",
            "identity": "gap",
            "release": "1",
            "stratum": "sampled",
        }
    ]


def test_hide_removes_protects_blank_and_writes_a_guard_hidden_reason(db, tmp_path):
    ids = seed(db)
    before = snapshot(db)
    sha = write_package(tmp_path, TL, tl_rows())
    res = w.apply(
        db, w.load_package(TL, sha, root=tmp_path), confirm=TL.confirm, environ=ON_TL
    )
    assert (res["removed"], res["reasons"]) == (1, 1)
    assert count(db, "analytics.canonical_fact", "id = %s", (ids["cf_tl"],)) == 0
    assert (
        _one(
            db,
            "select value is null from analytics.slot_protected_cell where run_id = %s",
            (res["run_id"],),
        )
        is True
    )
    assert (
        _one(
            db,
            "select defect_class from analytics.cell_blank_reason where run_id = %s::uuid",
            (res["run_id"],),
        )
        == "guard_hidden"
    )
    w.restore(db, res["run_id"], TL, confirm=TL.confirm)
    assert snapshot(db) == before
    assert (
        count(db, "analytics.cell_blank_reason", "run_id = %s::uuid", (res["run_id"],))
        == 0
    )


def test_apply_refuses_without_the_protection_table(db, tmp_path):
    ids = seed(db)
    db.execute("drop table analytics.slot_protected_cell cascade")
    db.commit()
    with pytest.raises(w.ReleaseRefused, match="0113"):
        w.apply(db, ni_pkg(tmp_path, ids), confirm=NI.confirm, environ=ON_NI)


def test_export_rollback_sql_restores_the_before_image(db, tmp_path):
    ids = seed(db)
    before = snapshot(db)
    pkg = ni_pkg(tmp_path, ids)
    with db.cursor() as cur:
        pl = w.plan(cur, pkg)
        image = w.before_image(cur, pl)
    db.rollback()
    assert {b["canonical_fact_id"] for b in image} == {ids["cf_a"], ids["cf_b"]}
    w.apply(db, pkg, confirm=NI.confirm, environ=ON_NI)
    db.execute(w.rollback_sql(pkg, pl, image))
    db.commit()
    assert snapshot(db) == before
    assert count(db, "analytics.slot_protected_cell") == 0
