"""Migration 0100 + common/cell_store.py on REAL SQL (isolated test database).

The migration text is applied verbatim with `analytics.` / `core.` rewritten to
scratch schemas, so no production table is touched and the exact CHECK,
UNIQUE and trigger behavior shipped in 0100 is what is tested.
"""

import json
import re
from datetime import date
from pathlib import Path

import psycopg
import pytest
from scrooner_pipeline.common import cell_contract as cc
from scrooner_pipeline.common import cell_store as cs

MIGRATION = (
    Path(__file__).resolve().parents[2]
    / "db"
    / "migrations"
    / "0100_cell_evidence_reason_registrant_audit.sql"
)
A, C = "ct_a", "ct_c"


def _rewrite(sql: str) -> str:
    return sql.replace("analytics.", f"{A}.").replace("core.", f"{C}.")


# ---------------------------------------------------------------- pure checks
def _check_lists(sql: str) -> dict[str, set[str]]:
    """column -> set of literals of every `col in ('a', 'b', ...)` CHECK."""
    out: dict[str, set[str]] = {}
    for col, body in re.findall(r"(\w+)\s+in\s*\(([^)]*)\)", sql):
        out.setdefault(col, set()).update(re.findall(r"'([^']+)'", body))
    return out


@pytest.mark.unit
def test_sql_check_lists_equal_python_enums():
    lists = _check_lists(MIGRATION.read_text())
    assert lists["period_grain"] == set(cc.PERIOD_GRAINS)
    assert lists["basis"] == set(cc.BASES)
    assert lists["defect_class"] == set(cc.DEFECT_CLASSES)
    assert lists["owner"] == set(cc.OWNERS)
    assert lists["root_cause_class"] == set(cc.ROOT_CAUSE_CLASSES)
    assert lists["evidence_kind"] == set(cc.EVIDENCE_KINDS)
    assert lists["evidence_level"] == set(cc.EVIDENCE_LEVELS)
    assert lists["role"] == set(cc.REGISTRANT_ROLES)
    assert lists["mode"] == set(cc.RUN_MODES)
    assert lists["flag_state"] == set(cc.FLAG_STATES)
    # state is used twice with different sets: blank reasons vs evidence claims
    sql = MIGRATION.read_text()
    blank = sql.split("create table if not exists analytics.cell_blank_reason")[
        1
    ].split(");")[0]
    assert set(
        re.findall(
            r"'([a-z_]+)'", blank.split("state text")[1].split("defect_class")[0]
        )
    ) == set(cc.BLANK_STATES)
    evid = sql.split("state_claimed text not null check (state_claimed in (")[1].split(
        "))"
    )[0]
    assert set(re.findall(r"'([a-z_]+)'", evid)) == set(cc.STATES)


@pytest.mark.unit
def test_every_default_owner_is_in_the_owner_list_and_classes_are_covered():
    assert set(cc.DEFAULT_OWNER_BY_CLASS.values()) <= cc.OWNERS
    assert set(cc.DEFAULT_OWNER_BY_CLASS) == cc.DEFECT_CLASSES - {
        "guard_hidden",
        "finding_open",
    }


@pytest.mark.unit
@pytest.mark.parametrize(
    "rule_id,ok",
    [
        ("source.periodic_form_only@1", True),
        ("cert.I6.non_periodic_form@1", True),
        ("entity.shared_accession_primary_filer@12", True),
        ("source.periodic_form_only", False),
        ("Source.periodic@1", False),
        ("nodot@1", False),
        ("a.b@", False),
    ],
)
def test_rule_id_format(rule_id, ok):
    if ok:
        cc.parse_rule_id(rule_id)
    else:
        with pytest.raises(ValueError):
            cc.parse_rule_id(rule_id)


@pytest.mark.unit
def test_cell_key_rules():
    k = cc.CellKey(1, "revenue", "I", date(2025, 12, 31), date(2025, 12, 31))
    assert k.basis == "latest"
    with pytest.raises(ValueError):
        cc.CellKey(1, "revenue", "I", date(2025, 12, 30), date(2025, 12, 31))
    with pytest.raises(ValueError):
        cc.CellKey(1, "revenue", "FY", date(2026, 1, 1), date(2025, 12, 31))
    with pytest.raises(ValueError):
        cc.CellKey(1, "revenue", "Y", date(2025, 1, 1), date(2025, 12, 31))
    with pytest.raises(ValueError):
        cc.CellKey(1, "revenue", "FY", date(2025, 1, 1), date(2025, 12, 31), basis="x")


@pytest.mark.unit
def test_blank_reason_python_validation():
    key = cc.CellKey(1, "total_debt", "I", date(2025, 12, 31), date(2025, 12, 31))
    with pytest.raises(ValueError):  # a valued state has no reason
        cs.BlankReason(key, "value", "debt.total_debt_consistency@1", "x")
    with pytest.raises(ValueError):  # defect needs class and owner
        cs.BlankReason(key, "defect", "debt.total_debt_consistency@1", "x")
    with pytest.raises(ValueError):  # non-defect must not carry them
        cs.BlankReason(
            key, "not_presented", "a.b@1", "x", defect_class="period", owner="triage"
        )
    with pytest.raises(ValueError):  # guard_hidden is a mechanism, not a root cause
        cs.guard_hidden(key, "a.b@1", "x", "triage", root_cause_class="guard_hidden")
    cs.guard_hidden(
        key,
        "debt.total_debt_consistency@1",
        "r1_containment",
        "data_engineer_l1",
        root_cause_class="composition",
    )


# -------------------------------------------------------------------- real SQL
@pytest.fixture
def conn(isolated_database_url):
    with psycopg.connect(isolated_database_url) as c:
        c.execute(f"drop schema if exists {A} cascade")
        c.execute(f"drop schema if exists {C} cascade")
        c.execute(f"create schema {A}")
        c.execute(f"create schema {C}")
        c.execute(f"create table {C}.company (id bigint primary key)")
        c.execute(f"insert into {C}.company values (1), (2)")
        c.execute(_rewrite(MIGRATION.read_text()))
        c.commit()
        yield c
        c.rollback()
        c.execute(f"drop schema if exists {A} cascade")
        c.execute(f"drop schema if exists {C} cascade")
        c.commit()


class _Cur:
    def __init__(self, cur):
        self._c = cur

    def __enter__(self):
        self._c.__enter__()
        return self

    def __exit__(self, *a):
        return self._c.__exit__(*a)

    def execute(self, sql, params=None):
        self._c.execute(_rewrite(sql), params)
        return self

    def executemany(self, sql, params):
        self._c.executemany(_rewrite(sql), params)

    def fetchone(self):
        return self._c.fetchone()

    def fetchall(self):
        return self._c.fetchall()

    @property
    def rowcount(self):
        return self._c.rowcount


class _Conn:
    """cell_store names the production schemas; this points them at the scratch ones."""

    def __init__(self, conn):
        self._conn = conn

    def cursor(self):
        return _Cur(self._conn.cursor())

    def execute(self, sql, params=None):
        return self.cursor().execute(sql, params)

    def rollback(self):
        self._conn.rollback()

    def commit(self):
        self._conn.commit()


@pytest.fixture
def store(conn):
    return _Conn(conn)


KEY = cc.CellKey(1, "total_debt_resolved", "I", date(2025, 12, 31), date(2025, 12, 31))
RULE = "debt.total_debt_consistency@1"


def _run(conn, rule=RULE, ciks=("0000000001",), mode="dry_run"):
    return cs.start_rule_run(conn, rule, mode, "off", ciks)


@pytest.mark.integration
def test_migration_is_idempotent(conn):
    conn.execute(_rewrite(MIGRATION.read_text()))  # second application: no error


@pytest.mark.integration
def test_rule_run_version_must_match_rule_id(conn):
    with pytest.raises(psycopg.errors.CheckViolation):
        conn.execute(
            f"insert into {A}.rule_run (rule_id, rule_version, mode, flag_name, flag_state) "
            "values ('a.b@1', 2, 'apply', 'a.b@1', 'off')"
        )


@pytest.mark.integration
def test_blank_reason_roundtrip_unique_and_run_scoped_delete(store):
    r1, r2 = _run(store), _run(store)
    reason = cs.guard_hidden(
        KEY,
        RULE,
        "r5_floor",
        "data_engineer_l1",
        root_cause_class="composition",
        source_fact_ids=[5, 6],
        input_refs={"debt": "12"},
    )
    assert cs.write_blank_reasons(store, r1, [reason]) == 1
    assert cs.write_blank_reasons(store, r1, [reason]) == 1  # retried chunk: idempotent
    assert (
        cs.write_blank_reasons(store, r2, [reason]) == 1
    )  # another run keeps its own row
    n = store.execute(f"select count(*) from {A}.cell_blank_reason").fetchone()[0]
    assert n == 2
    row = store.execute(
        f"select state, defect_class, owner, root_cause_class, source_fact_ids, input_refs "
        f"from {A}.cell_blank_reason where run_id = %s::uuid",
        (r1,),
    ).fetchone()
    assert row == (
        "defect",
        "guard_hidden",
        "data_engineer_l1",
        "composition",
        [5, 6],
        {"debt": "12"},
    )
    assert cs.delete_run_blank_reasons(store, r1) == 1
    assert (
        store.execute(f"select count(*) from {A}.cell_blank_reason").fetchone()[0] == 1
    )


@pytest.mark.integration
def test_blank_reason_sql_checks_hold_without_python(store):
    run = _run(store)
    store.commit()
    base = (
        f"insert into {A}.cell_blank_reason (run_id, company_id, data_point_name, period_grain, "
        "period_start, period_end, state, defect_class, owner, rule_id, reason_code) "
        "values (%s::uuid, 1, 'x', %s, %s, %s, %s, %s, %s, 'a.b@1', 'c')"
    )
    d = date(2025, 12, 31)
    bad = [
        (
            run,
            "I",
            date(2025, 12, 30),
            d,
            "not_presented",
            None,
            None,
        ),  # instant with a span
        (
            run,
            "FY",
            d,
            date(2025, 1, 1),
            "not_presented",
            None,
            None,
        ),  # start after end
        (
            run,
            "FY",
            date(2025, 1, 1),
            d,
            "defect",
            None,
            None,
        ),  # defect without class/owner
        (
            run,
            "FY",
            date(2025, 1, 1),
            d,
            "not_presented",
            "period",
            "triage",
        ),  # class on non-defect
        (
            run,
            "FY",
            date(2025, 1, 1),
            d,
            "not_presented",
            None,
            "triage",
        ),  # owner alone on a non-defect
        (
            run,
            "FY",
            date(2025, 1, 1),
            d,
            "value",
            None,
            None,
        ),  # value has no reason row
        (run, "FY", date(2025, 1, 1), d, "defect", "made_up", "triage"),
        (run, "FY", date(2025, 1, 1), d, "defect", "period", "nobody"),
    ]
    for params in bad:
        with pytest.raises(psycopg.errors.CheckViolation):
            store.execute(base, params)
        store.rollback()
    store.execute(
        base, (run, "FY", date(2025, 1, 1), d, "defect", "period", "period_engineer")
    )


@pytest.mark.integration
def test_reason_survives_canonical_fact_delete_then_insert(store):
    """AT-DE-06 shape: the nightly writer deletes and re-inserts valued rows of a
    company; the reason store, keyed by dates in its own table, is untouched."""
    store.execute(
        f"create table {A}.canonical_fact (company_id bigint, concept text, period_end date, value numeric)"
    )
    store.execute(
        f"insert into {A}.canonical_fact values (1, 'total_debt_resolved', '2025-12-31', 5)"
    )
    run = _run(store)
    cs.write_blank_reasons(
        store, run, [cs.guard_hidden(KEY, RULE, "r1", "data_engineer_l1")]
    )
    store.execute(f"delete from {A}.canonical_fact where company_id = 1")  # the hide
    store.execute(
        f"insert into {A}.canonical_fact values (1, 'revenue_sanity_resolved', '2025-12-31', 9)"
    )
    assert (
        store.execute(f"select count(*) from {A}.cell_blank_reason").fetchone()[0] == 1
    )


def _ev(**kw):
    base = {
        "key": KEY,
        "state_claimed": "evidenced_zero",
        "rule_id": "evidence.evidenced_zero@1",
        "evidence_kind": "filing_check",
        "evidence_level": "FILING-CHECKED",
        "recorded_by": "verifier:V-A",
        "accession": "0000065984-26-000174",
        "locator": "R4 row 12",
    }
    base.update(kw)
    return cs.EvidenceRecord(**base)


@pytest.mark.integration
def test_evidence_is_append_only(store):
    e1 = cs.append_evidence(store, _ev())
    e2 = cs.append_evidence(store, _ev(locator="R4 row 13"))
    store.commit()
    for stmt in (
        f"update {A}.cell_evidence set locator = 'x' where evidence_id = {e1}",
        f"update {A}.cell_evidence set recorded_by = 'x', superseded_by = {e2} where evidence_id = {e1}",
        f"delete from {A}.cell_evidence where evidence_id = {e1}",
        f"truncate {A}.cell_evidence",
    ):
        with pytest.raises(psycopg.errors.RaiseException):
            store.execute(stmt)
        store.rollback()
    e3 = cs.append_evidence(store, _ev(locator="R4 row 14"))
    cs.supersede_evidence(store, e1, e3)
    store.commit()
    with pytest.raises(psycopg.errors.RaiseException):  # a row is retired once
        cs.supersede_evidence(store, e1, e2)
    store.rollback()
    assert store.execute(f"select count(*) from {A}.cell_evidence").fetchone()[0] == 3
    assert (
        store.execute(
            f"select superseded_by from {A}.cell_evidence where evidence_id = %s", (e1,)
        ).fetchone()[0]
        == e3
    )


@pytest.mark.integration
def test_evidence_filing_check_needs_accession_even_through_raw_sql(store):
    with pytest.raises(psycopg.errors.CheckViolation):
        store.execute(
            f"insert into {A}.cell_evidence (company_id, data_point_name, period_grain, "
            "period_start, period_end, state_claimed, rule_id, evidence_kind, evidence_level, recorded_by) "
            "values (1,'x','FY','2025-01-01','2025-12-31','value','a.b@1','filing_check','FILING-CHECKED','me')"
        )
    store.rollback()
    with pytest.raises(
        psycopg.errors.CheckViolation
    ):  # a filing check cannot be DATA-INFERRED
        store.execute(
            f"insert into {A}.cell_evidence (company_id, data_point_name, period_grain, "
            "period_start, period_end, state_claimed, rule_id, evidence_kind, evidence_level, "
            "recorded_by, accession, locator) values "
            "(1,'x','FY','2025-01-01','2025-12-31','value','a.b@1','filing_check','DATA-INFERRED','me','a','b')"
        )


@pytest.mark.unit
def test_evidence_python_rejects_incomplete_filing_check():
    with pytest.raises(ValueError):
        _ev(accession=None)
    with pytest.raises(ValueError):
        _ev(evidence_level="DATA-INFERRED")
    with pytest.raises(ValueError):
        _ev(rule_id="bad")


@pytest.mark.integration
def test_jsonl_roundtrip_is_idempotent_and_validates_before_writing(store, tmp_path):
    f = tmp_path / "cell_evidence.jsonl"
    recs = [
        _ev(locator="R4 row 1"),
        _ev(
            locator="R4 row 2",
            state_claimed="not_presented",
            rule_id="evidence.not_presented@1",
        ),
    ]
    for r in recs:
        cs.append_evidence_jsonl(f, r)
    assert cs.evidence_from_jsonl_line(f.read_text().splitlines()[0]) == recs[0]
    assert cs.load_evidence_jsonl(store, f) == {"lines": 2, "inserted": 2, "skipped": 0}
    assert cs.load_evidence_jsonl(store, f) == {"lines": 2, "inserted": 0, "skipped": 2}
    bad = tmp_path / "bad.jsonl"
    good_line = cs.evidence_to_jsonl_line(_ev(locator="R4 row 99"))
    bad.write_text(good_line + "\n" + json.dumps({"company_id": 1, "oops": 1}) + "\n")
    with pytest.raises((TypeError, KeyError, ValueError)):
        cs.load_evidence_jsonl(store, bad)
    assert (
        store.execute(f"select count(*) from {A}.cell_evidence").fetchone()[0] == 2
    )  # nothing partial


@pytest.mark.integration
def test_registrant_one_primary_or_all_quarantined(store):
    acc = "0000065984-26-000174"
    rows = [
        cs.RegistrantRow("0000065984", "primary", 2),
        cs.RegistrantRow("0000007323", "co_registrant", 1),
    ]
    cs.write_filing_registrants(
        store,
        acc,
        rows,
        dei_default_cik="0000065984",
        header_first_filer_cik="0000065984",
    )
    cs.write_filing_registrants(
        store,
        acc,
        rows,
        dei_default_cik="0000065984",
        header_first_filer_cik="0000065984",
    )  # replay: same rows
    cs.write_filing_registrants(
        store,
        "0000320193-26-000020",
        [cs.RegistrantRow("0000320193", "primary")],
        dei_default_cik="0000320193",
        header_first_filer_cik="0000320193",
    )
    assert (
        store.execute(
            f"select count(*) from {C}.filing_registrant where accession_number=%s",
            (acc,),
        ).fetchone()[0]
        == 2
    )
    # replacing one accession leaves the others alone
    cs.write_filing_registrants(
        store,
        acc,
        [
            cs.RegistrantRow("0000065984", "quarantined"),
            cs.RegistrantRow("0000007323", "quarantined"),
        ],
        dei_default_cik="0000065984",
        header_first_filer_cik="0000007323",
        quarantine_reason="dei CIK and header first filer disagree",
    )
    assert (
        store.execute(f"select count(*) from {C}.filing_registrant").fetchone()[0] == 3
    )
    assert (
        store.execute(
            f"select count(*) from {C}.filing_registrant where role='primary'"
        ).fetchone()[0]
        == 1
    )
    for bad in (
        [
            cs.RegistrantRow("0000000001", "primary"),
            cs.RegistrantRow("0000000002", "primary"),
        ],
        [cs.RegistrantRow("0000000001", "co_registrant")],
        [
            cs.RegistrantRow("0000000001", "primary"),
            cs.RegistrantRow("0000000002", "quarantined"),
        ],
    ):
        with pytest.raises(ValueError):
            cs.write_filing_registrants(
                store,
                "0000000000-26-000001",
                bad,
                dei_default_cik=None,
                header_first_filer_cik=None,
            )


@pytest.mark.integration
def test_registrant_sql_enforces_single_primary(store):
    ins = (
        f"insert into {C}.filing_registrant (accession_number, registrant_cik, role, filer_count) "
        "values ('0000000000-26-000001', %s, 'primary', 2)"
    )
    store.execute(ins, ("0000000001",))
    with pytest.raises(psycopg.errors.UniqueViolation):
        store.execute(ins, ("0000000002",))


@pytest.mark.integration
def test_identity_audit_records_reverses_once_and_cannot_be_deleted(store):
    a = cs.record_identity_audit(
        store,
        company_id=1,
        field_name="display_name",
        old_value="AvalonBay Communities, Inc.",
        new_value="VIVMARK RESIDENTIAL",
        rule_id="identity.cik_name_ticker@1",
        evidence_level="FILING-CHECKED",
        accession="0001140361-26-033377",
        locator="Item 5.03",
    )
    store.commit()
    with pytest.raises(ValueError):
        cs.record_identity_audit(
            store,
            company_id=1,
            field_name="x",
            old_value="a",
            new_value="a",
            rule_id="identity.cik_name_ticker@1",
            evidence_level="DATA-INFERRED",
        )
    with pytest.raises(ValueError):
        cs.record_identity_audit(
            store,
            company_id=1,
            field_name="x",
            old_value="a",
            new_value="b",
            rule_id="identity.cik_name_ticker@1",
            evidence_level="FILING-CHECKED",
        )
    for stmt in (
        f"delete from {C}.company_identity_audit where id = {a}",
        f"update {C}.company_identity_audit set new_value = 'z' where id = {a}",
    ):
        with pytest.raises(psycopg.errors.RaiseException):
            store.execute(stmt)
        store.rollback()
    a = cs.record_identity_audit(
        store,
        company_id=1,
        field_name="display_name",
        old_value="o",
        new_value="n",
        rule_id="identity.cik_name_ticker@1",
        evidence_level="DATA-INFERRED",
    )
    cs.mark_identity_audit_reversed(store, a)
    with pytest.raises(psycopg.errors.RaiseException):
        cs.mark_identity_audit_reversed(store, a)


@pytest.mark.integration
def test_replace_rule_reasons_deletes_only_its_own_rule_company_and_run(store):
    r1, r2 = _run(store), _run(store)
    other_rule = "oi.derived_not_face@1"
    k2 = cc.CellKey(
        2, "total_debt_resolved", "I", date(2025, 12, 31), date(2025, 12, 31)
    )
    mk = lambda key, rule: cs.guard_hidden(key, rule, "r1", "data_engineer_l1")  # noqa: E731
    cs.write_blank_reasons(
        store, r1, [mk(KEY, RULE), mk(KEY, other_rule), mk(k2, RULE)]
    )
    cs.write_blank_reasons(store, r2, [mk(KEY, RULE)])
    store.commit()
    key_b = cc.CellKey(
        1, "total_debt_resolved", "I", date(2024, 12, 31), date(2024, 12, 31)
    )
    assert cs.replace_rule_reasons(store, r1, 1, RULE, [mk(key_b, RULE)]) == 1
    rows = store.execute(
        f"select run_id::text, company_id, rule_id, period_end from {A}.cell_blank_reason order by 1, 2, 3, 4"
    ).fetchall()
    assert (r1, 1, RULE, date(2025, 12, 31)) not in rows  # replaced
    assert (r1, 1, RULE, date(2024, 12, 31)) in rows  # new
    assert (r1, 1, other_rule, date(2025, 12, 31)) in rows  # other rule untouched
    assert (r1, 2, RULE, date(2025, 12, 31)) in rows  # other company untouched
    assert (r2, 1, RULE, date(2025, 12, 31)) in rows  # other run untouched
    with pytest.raises(ValueError):
        cs.replace_rule_reasons(
            store, r1, 1, RULE, [mk(k2, RULE)]
        )  # company outside scope
    with pytest.raises(ValueError):
        cs.replace_rule_reasons(
            store, r1, 1, RULE, [mk(KEY, other_rule)]
        )  # rule outside scope
