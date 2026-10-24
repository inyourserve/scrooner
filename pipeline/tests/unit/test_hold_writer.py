"""Shared hold writer (common/hold_writer.py) on REAL SQL in an isolated database.

Migration 0100 and the 0098 archive table are applied verbatim into scratch schemas (analytics -> hw_a, core -> hw_c),
so the CHECKs, uniques and the archive/restore SQL that ship are what is tested; the shared database is never touched.
"""

from __future__ import annotations

import json
import re
from datetime import date
from decimal import Decimal
from pathlib import Path

import psycopg
import pytest

from scrooner_pipeline.common import cell_contract as cc
from scrooner_pipeline.common import hold_writer as hw
from scrooner_pipeline.common import rule_flags

MIG = Path(__file__).resolve().parents[2] / "db" / "migrations"
A, C = "hw_a", "hw_c"
IDENTITY = "balance.identity_equity_basis@1"
DEBT = "debt.total_debt_consistency@1"
D1, D2 = date(2026, 3, 31), date(2026, 6, 30)
ON = {rule_flags.ENV_ENABLED: hw.WRITER_RULE}
DRY = {rule_flags.ENV_DRYRUN: hw.WRITER_RULE}


def _rewrite(sql: str) -> str:
    return sql.replace("analytics.", f"{A}.").replace("core.", f"{C}.")


def _archive_ddl() -> str:
    sql = (MIG / "0098_per_share_gap_cause_and_canonical_fact_retired.sql").read_text()
    ddl = sql[
        sql.index("create table if not exists analytics.canonical_fact_retired") :
    ]
    ddl = ddl[: ddl.index(");") + 2]
    return re.sub(r"references \w+\.\w+ \(id\)", "", ddl)


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
    def __init__(self, conn):
        self._conn = conn

    def cursor(self):
        return _Cur(self._conn.cursor())

    def execute(self, sql, params=None):
        return self.cursor().execute(sql, params)

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()


@pytest.fixture
def store(isolated_database_url):
    with psycopg.connect(isolated_database_url) as c:
        for s in (A, C):
            c.execute(f"drop schema if exists {s} cascade")
            c.execute(f"create schema {s}")
        c.execute(
            f"create table {C}.company (id bigint primary key, cik text not null)"
        )
        c.execute(
            f"insert into {C}.company values (1, '0000000001'), (2, '0000000002')"
        )
        c.execute(
            f"create table {C}.period (id bigint primary key, end_date date not null, period_type text not null)"
        )
        c.execute(
            f"insert into {C}.period values (10, '{D1}', 'instant'), (11, '{D2}', 'instant'), (12, '{D2}', 'duration')"
        )
        c.execute(
            f"create table {A}.canonical_concept (id bigint primary key, name text not null unique)"
        )
        c.execute(
            f"insert into {A}.canonical_concept values (100, 'total_liabilities_resolved'), (101, 'total_debt_resolved')"
        )
        c.execute(
            f"""create table {A}.canonical_fact (
                id bigint generated always as identity primary key, company_id bigint not null,
                canonical_concept_id bigint not null, period_id bigint not null, value numeric not null,
                source_fact_ids bigint[] not null, resolved_at timestamptz not null default now(),
                unique (company_id, canonical_concept_id, period_id))"""
        )
        c.execute(_archive_ddl().replace("analytics.", f"{A}."))
        c.execute(
            _rewrite(
                (MIG / "0100_cell_evidence_reason_registrant_audit.sql").read_text()
            )
        )
        c.commit()
        yield _Conn(c)
        c.rollback()
        for s in (A, C):
            c.execute(f"drop schema if exists {s} cascade")
        c.commit()


def put(store, company, concept, period, value):
    store.execute(
        "insert into analytics.canonical_fact (company_id, canonical_concept_id, period_id, value, source_fact_ids)"
        " values (%s, %s, %s, %s, %s)",
        (company, concept, period, Decimal(str(value)), [1, 2]),
    )


def rows(store, table, cols="*"):
    return store.execute(f"select {cols} from analytics.{table}").fetchall()


def hold(
    company=1,
    end=D1,
    value="500000000",
    reason="identity_not_confirmed_by_face_subtotals",
    rule=IDENTITY,
    dp="total_liabilities_resolved",
    reference="400000000",  # an independent reading 25% below the stored 500M: positive evidence of an error
    **kw,
):
    kw.setdefault("reference_value", None if reference is None else Decimal(reference))
    return hw.Hold(
        company, dp, end, rule, reason, None if value is None else Decimal(value), **kw
    )


@pytest.fixture
def seeded(store):
    put(store, 1, 100, 10, "500000000")  # held by the identity rule
    put(store, 1, 100, 11, "700000000")  # not held
    put(store, 2, 100, 10, "900000000")  # another company, not held
    put(
        store, 1, 101, 10, "3000000000"
    )  # same company, other concept, held by the debt rule
    store.commit()
    return store


# ------------------------------------------------------------------ pure
def test_every_mapped_reason_is_a_valid_defect_row_with_a_known_owner():
    for code, spec in hw.REASON_MAP.items():
        cc.validate_defect(
            spec.state, spec.defect_class, spec.owner, spec.root_cause_class
        )
        assert spec.state == "defect" and spec.defect_class == "guard_hidden", code


@pytest.mark.parametrize(
    "text, code",
    [
        ("debt composition undecidable: current debt total is not explained by its filed parts", "debt_current_block_unexplained"),
        ("debt composition undecidable: total would be 0 while a debt tag is nonzero", "debt_zero_with_nonzero_tag"),
        ("debt composition undecidable: total is below a single filed debt instrument tag", "debt_below_instrument_tag"),
        ("debt composition undecidable: total is below the filed lease-inclusive debt total", "debt_below_lease_inclusive_total"),
        ("debt composition undecidable: finance leases are filed but cannot be placed inside or outside the current debt line", "debt_lease_location_unknown"),
        ("debt composition undecidable: several different short-term borrowing amounts are filed and the stated total does not show how they combine", "debt_short_term_overlap"),
        ("debt composition undecidable: borrowings cannot be separated from the lease-inclusive debt lines", "debt_borrowings_not_separable"),
        ("debt composition undecidable: related-party or debt-only current lines sit beside lease-inclusive lines", "debt_related_party_unresolved"),
        ("debt composition undecidable: a debt component is negative", "debt_negative_component"),
        ("debt composition undecidable: only current debt portions are filed (no long-term block)", "debt_partial_component"),
    ],
)  # fmt: skip
def test_every_debt_hold_text_maps_to_a_reason_code(text, code):
    assert hw.debt_reason_code(text) == code and code in hw.REASON_MAP


def test_an_unknown_debt_text_or_reason_code_is_refused_not_guessed():
    with pytest.raises(ValueError):
        hw.debt_reason_code("something new")
    with pytest.raises(ValueError):
        hold(reason="no_such_reason")
    with pytest.raises(ValueError):
        hw.Hold(1, "x", D1, IDENTITY, "mixed_vintage", None, period_grain="FY")
    with pytest.raises(ValueError):
        hold(rule="notarule")


def test_identity_plan_rows_become_holds_and_only_holds():
    plan = [
        {"kind": "hold", "company_id": 1, "concept": "total_liabilities_resolved", "period_end": "2026-03-31",
         "before": "500000000", "basis": "nci_unconfirmed", "filing_id": 7, "equity_tag": "StockholdersEquity", "source_fact_ids": [3, 4]},
        {"kind": "replace", "company_id": 1, "concept": "total_liabilities_resolved", "period_end": "2026-06-30",
         "before": "1", "after": "2", "basis": "x"},
        {"kind": "hold", "company_id": 2, "concept": "total_liabilities_resolved", "period_end": "2026-03-31",
         "before": None, "basis": "mixed_vintage"},
    ]  # fmt: skip
    got = hw.holds_from_plan(plan)
    assert [(h.company_id, h.reason_code, h.stored_value) for h in got] == [
        (1, "nci_unconfirmed", Decimal(500000000)), (2, "mixed_vintage", None)]  # fmt: skip
    assert got[0].evidence == {
        "filing_id": 7,
        "equity_tag": "StockholdersEquity",
    } and got[0].source_fact_ids == (3, 4)
    assert got[0].rule_id == IDENTITY


def test_debt_plan_rows_become_holds_only_when_the_value_would_be_blank():
    txt = "debt composition undecidable: a debt component is negative"
    plan = [
        {"company_id": 1, "data_point": "total_debt_resolved", "period_end": "2026-03-31", "before": "100", "after": None,
         "reason": f"r8_carrying_lines:hold={txt}"},
        {"company_id": 1, "data_point": "total_debt_resolved", "period_end": "2026-06-30", "before": "100", "after": "90",
         "reason": "r8_carrying_lines:borrowings_plus_finance_leases"},
        {"company_id": 2, "data_point": "total_debt_resolved", "period_end": "2026-06-30", "before": "100", "after": None,
         "reason": "r1_containment"},
        {"company_id": 2, "data_point": "total_debt_resolved", "period_end": "2026-03-31", "before": "100", "after": "7",
         "reason": f"r8_carrying_lines:hold={txt}"},  # has a value: not a hold whatever the text says
    ]  # fmt: skip
    got = hw.holds_from_debt_plan(plan)
    assert (
        len(got) == 1
        and got[0].reason_code == "debt_negative_component"
        and got[0].rule_id == DEBT
    )
    assert got[0].reason_text == txt


# ------------------------------------------------------------------ dry run
@pytest.mark.integration
def test_dry_run_counts_per_rule_and_per_reason_and_changes_nothing(seeded):
    holds = [
        hold(),  # 500M present, reference 400M: 25% apart -> would blank
        hold(end=D2, value="700000000", reference="699000000"),  # 0.14% apart -> kept
        hold(company=2, value="1"),  # the stored value moved since the plan
        hold(company=2, end=D2, value="1"),  # nothing stored: already blank
        hold(reason="mixed_vintage", end=D2, value="700000000", reference=None, company=1, dp="total_debt_resolved"),  # no such stored row
        hold(rule=DEBT, dp="total_debt_resolved", value="3000000000", reason="debt_below_instrument_tag", reference=None),
    ]  # fmt: skip
    before = rows(seeded, "canonical_fact")
    s = hw.summarize(seeded, holds)
    ident = s[IDENTITY]
    assert (ident["holds"], ident["would_blank"], ident["kept_unverified"]) == (5, 1, 1)
    assert (ident["changed_since_plan"], ident["already_blank"]) == (1, 2)
    r = ident["by_reason"]["identity_not_confirmed_by_face_subtotals"]
    assert (r["would_blank"], r["kept_unverified"]) == (1, 1)
    assert dict(r["magnitude"]) == {"100M-1B": 1}
    assert dict(r["difference_to_reference"]) == {
        "25-100%": 1
    }  # |500M - 400M| / 400M = 25%
    assert s[DEBT]["would_blank"] == 1 and dict(s[DEBT]["magnitude"]) == {"1B-10B": 1}
    text = hw.format_summary(s)
    assert (
        "would_blank=1" in text
        and "kept_unverified=1" in text
        and "identity_not_confirmed" in text
    )
    assert rows(seeded, "canonical_fact") == before and not rows(
        seeded, "cell_blank_reason"
    )
    assert not rows(seeded, "cell_evidence")


# ------------------------------------------------------------------ the blank policy
D = Decimal


def test_decision_blanks_only_with_positive_evidence():
    ref = hold(reference="1000")
    assert ref.decision(D("1005")) == "keep"  # exactly 0.5% apart
    assert ref.decision(D("1005.1")) == "blank"  # just beyond
    assert ref.decision(D("994.9")) == "blank"
    assert (
        hold(reference=None).decision(D("1")) == "keep"
    )  # no independent reading -> never blank
    assert hold(reference="0").decision(D("1")) == "keep"
    # a keep_unverified reason never blanks, even with a reference far from the stored value
    assert hold(reason="mixed_vintage", reference="1").decision(D("1000")) == "keep"
    # the explicit known-wrong reasons blank without a reference
    for code in ("debt_zero_with_nonzero_tag", "debt_below_instrument_tag", "debt_below_lease_inclusive_total", "debt_partial_component"):  # fmt: skip
        assert hold(rule=DEBT, reason=code, reference=None).decision(D("1")) == "blank"


def test_policy_table_is_total_and_the_known_wrong_list_is_explicit():
    assert {c for c, sp in hw.REASON_MAP.items() if sp.policy == hw.POLICY_KNOWN_WRONG} == {
        "debt_zero_with_nonzero_tag", "debt_below_instrument_tag", "debt_below_lease_inclusive_total", "debt_partial_component"}  # fmt: skip
    assert {c for c, sp in hw.REASON_MAP.items() if sp.policy == hw.POLICY_KEEP} >= {"mixed_vintage", "no_source_filing", "debt_short_term_overlap"}  # fmt: skip
    assert all(sp.policy in hw.POLICIES for sp in hw.REASON_MAP.values())
    with pytest.raises(ValueError):
        hw.ReasonSpec("defect", "guard_hidden", "triage", "composition", "sometimes")


def _fe_and_ni(store):
    # FE 2018-03-31: stored 31,420M equals the face and the reference reading; NI 2023-12-31: stored 24,674.3M, the
    # reference (assets - NCI-inclusive total) is the face 20,940.9M
    put(store, 1, 100, 10, "31420000000")
    put(store, 2, 100, 10, "24674300000")
    store.commit()
    return [
        hold(company=1, value="31420000000", reference="31420000000", evidence={"filing_id": 1007936}),
        hold(company=2, value="24674300000", reference="20940900000", evidence={"filing_id": 1236891}),
    ]  # fmt: skip


@pytest.mark.integration
def test_fe_is_kept_and_ni_is_blanked(store, tmp_path):
    holds = _fe_and_ni(store)
    s = hw.summarize(store, holds)[IDENTITY]
    assert (s["would_blank"], s["kept_unverified"]) == (1, 1)
    out = hw.apply_holds(store, holds, before_image=tmp_path / "i.jsonl", environ=ON)
    assert (out["blanked"], out["kept_unverified"], out["evidence_written"]) == (
        1,
        1,
        1,
    )
    left = rows(store, "canonical_fact", "company_id, value")
    assert left == [
        (1, Decimal("31420000000"))
    ]  # FE untouched, NI archived and removed
    assert [r[0] for r in rows(store, "canonical_fact_retired", "company_id")] == [2]
    reasons = rows(store, "cell_blank_reason", "company_id, reason_code")
    assert reasons == [
        (2, "identity_not_confirmed_by_face_subtotals")
    ]  # no user-visible reason for FE
    ev = rows(store, "cell_evidence", "company_id, rule_id, evidence_kind, evidence_level, state_claimed, locator, detector_version, recorded_by")  # fmt: skip
    assert ev == [(1, IDENTITY, "detector_audit", "DATA-INFERRED", "value", "unverified_hold:identity_not_confirmed_by_face_subtotals", "identity_not_confirmed_by_face_subtotals", "hold_writer")]  # fmt: skip


@pytest.mark.integration
def test_kept_holds_write_one_evidence_row_however_often_the_writer_runs(
    store, tmp_path
):
    holds = _fe_and_ni(store)
    hw.apply_holds(store, holds, before_image=tmp_path / "a.jsonl", environ=ON)
    again = hw.apply_holds(store, holds, before_image=tmp_path / "b.jsonl", environ=ON)
    assert again["evidence_written"] == 0 and again["blanked"] == 0
    assert (
        len(rows(store, "cell_evidence")) == 1
        and len(rows(store, "cell_blank_reason")) == 1
    )


@pytest.mark.integration
def test_a_keep_unverified_reason_is_never_blanked_even_far_from_its_reference(
    seeded, tmp_path
):
    h = hold(reason="mixed_vintage", reference="1")
    out = hw.apply_holds(seeded, [h], before_image=tmp_path / "i.jsonl", environ=ON)
    assert (
        out["kept_unverified"] == 1
        and out["blanked"] == 0
        and len(rows(seeded, "canonical_fact")) == 4
    )
    assert (
        not rows(seeded, "cell_blank_reason")
        and len(rows(seeded, "cell_evidence")) == 1
    )


@pytest.mark.integration
def test_a_known_wrong_debt_reason_blanks_without_a_reference(seeded, tmp_path):
    h = hold(rule=DEBT, dp="total_debt_resolved", value="3000000000", reason="debt_below_instrument_tag", reference=None)  # fmt: skip
    out = hw.apply_holds(seeded, [h], before_image=tmp_path / "i.jsonl", environ=ON)
    assert out["blanked"] == 1 and not rows(seeded, "cell_evidence")


@pytest.mark.integration
def test_identity_plan_references_reach_the_hold(seeded):
    got = hw.holds_from_plan([
        {"kind": "hold", "company_id": 1, "concept": "total_liabilities_resolved", "period_end": "2026-03-31",
         "before": "500000000", "basis": "nci_unconfirmed", "reference": "400000000"}])  # fmt: skip
    assert (
        got[0].reference_value == Decimal(400000000)
        and got[0].decision(Decimal(500000000)) == "blank"
    )
    none = hw.holds_from_plan([{"kind": "hold", "company_id": 1, "concept": "x", "period_end": "2026-03-31", "before": "5", "basis": "nci_unconfirmed", "reference": None}])  # fmt: skip
    assert none[0].reference_value is None


# ------------------------------------------------------------------ apply
@pytest.mark.integration
def test_apply_archives_removes_explains_and_writes_the_before_image(seeded, tmp_path):
    img = tmp_path / "img.jsonl"
    stats = hw.apply_holds(
        seeded,
        [hold(evidence={"filing_id": 7}, source_fact_ids=(3,)), hold(rule=DEBT, dp="total_debt_resolved", value="3000000000", reason="debt_below_instrument_tag")],
        before_image=img, environ=ON,
    )  # fmt: skip
    assert (
        stats["blanked"] == 2
        and stats["reasons_written"] == 2
        and stats["companies"] == 1
    )
    left = rows(seeded, "canonical_fact", "company_id, canonical_concept_id, period_id")
    assert sorted(left) == [(1, 100, 11), (2, 100, 10)]  # only the held cells are gone
    arch = rows(
        seeded,
        "canonical_fact_retired",
        "action, company_id, canonical_concept_id, value, reason_code, run_id",
    )
    assert sorted((a[0], a[1], a[2], a[3], a[4]) for a in arch) == [
        ("removed", 1, 100, Decimal(500000000), "hold_writer_blank"),
        ("removed", 1, 101, Decimal(3000000000), "hold_writer_blank")]  # fmt: skip
    run = stats["run_id"]
    assert {a[5] for a in arch} == {run}
    r = seeded.execute(
        "select data_point_name, period_grain, period_start, period_end, state, defect_class, owner, root_cause_class, "
        "rule_id, reason_code, input_refs, source_fact_ids from analytics.cell_blank_reason order by rule_id"
    ).fetchall()
    assert r[1] == ("total_debt_resolved", "I", D1, D1, "defect", "guard_hidden", "data_engineer_l1", "composition", DEBT, "debt_below_instrument_tag", {}, [])  # fmt: skip
    assert r[0] == ("total_liabilities_resolved", "I", D1, D1, "defect", "guard_hidden", "standardization_lead", "composition", IDENTITY, "identity_not_confirmed_by_face_subtotals", {"filing_id": 7}, [3])  # fmt: skip
    manifest = seeded.execute(
        "select rule_id, mode, flag_state, before_image_ref, stats->>'blanked' from analytics.rule_run"
    ).fetchall()
    assert manifest == [(hw.WRITER_RULE, "apply", "on", str(img), "2")]
    lines = [json.loads(x) for x in img.read_text().splitlines()]
    assert {(x["data_point"], x["stored_value"]) for x in lines} == {("total_liabilities_resolved", "500000000"), ("total_debt_resolved", "3000000000")}  # fmt: skip


@pytest.mark.integration
def test_a_second_run_changes_nothing(seeded, tmp_path):
    holds = [
        hold(),
        hold(
            rule=DEBT,
            dp="total_debt_resolved",
            value="3000000000",
            reason="debt_below_instrument_tag",
        ),
    ]
    hw.apply_holds(seeded, holds, before_image=tmp_path / "a.jsonl", environ=ON)
    snap = {
        t: rows(seeded, t)
        for t in ("canonical_fact", "canonical_fact_retired", "cell_blank_reason")
    }
    again = hw.apply_holds(seeded, holds, before_image=tmp_path / "b.jsonl", environ=ON)
    assert (
        again["blanked"] == 0
        and again["reasons_written"] == 0
        and again["skipped_done"] == 2
    )
    assert {t: rows(seeded, t) for t in snap} == snap


@pytest.mark.integration
def test_a_value_that_moved_since_the_plan_is_neither_blanked_nor_explained(
    seeded, tmp_path
):
    s = hw.apply_holds(
        seeded, [hold(value="123")], before_image=tmp_path / "i.jsonl", environ=ON
    )
    assert s["skipped_changed"] == 1 and s["blanked"] == 0
    assert len(rows(seeded, "canonical_fact")) == 4 and not rows(
        seeded, "cell_blank_reason"
    )


@pytest.mark.integration
def test_a_cell_that_is_already_blank_without_a_reason_only_gets_the_reason(
    seeded, tmp_path
):
    s = hw.apply_holds(
        seeded,
        [hold(company=2, end=D2, value=None)],
        before_image=tmp_path / "i.jsonl",
        environ=ON,
    )
    assert s["blanked"] == 0 and s["reasons_written"] == 1
    assert (
        not rows(seeded, "canonical_fact_retired")
        and len(rows(seeded, "canonical_fact")) == 4
    )


@pytest.mark.integration
def test_scope_is_company_rule_run_and_never_wider(seeded, tmp_path):
    first = hw.apply_holds(
        seeded, [hold()], before_image=tmp_path / "a.jsonl", environ=ON
    )
    second = hw.apply_holds(
        seeded,
        [hold(company=2, value="900000000")],
        before_image=tmp_path / "b.jsonl",
        environ=ON,
    )
    assert first["run_id"] != second["run_id"]
    runs = {
        r[0]
        for r in seeded.execute(
            "select run_id::text from analytics.cell_blank_reason"
        ).fetchall()
    }
    assert runs == {
        first["run_id"],
        second["run_id"],
    }  # the first run's reason row survived the second run
    # the instant D2 row, the other period type and the non-held concept stay
    assert sorted(
        rows(seeded, "canonical_fact", "company_id, canonical_concept_id, period_id")
    ) == [(1, 100, 11), (1, 101, 10)]


@pytest.mark.integration
def test_rollback_restores_the_values_and_discards_the_reasons(seeded, tmp_path):
    before = sorted(
        rows(
            seeded,
            "canonical_fact",
            "company_id, canonical_concept_id, period_id, value, source_fact_ids",
        )
    )
    s = hw.apply_holds(seeded, [hold(), hold(rule=DEBT, dp="total_debt_resolved", value="3000000000", reason="debt_below_instrument_tag")], before_image=tmp_path / "i.jsonl", environ=ON)  # fmt: skip
    assert hw.rollback_run(seeded, s["run_id"]) == {
        "restored": 2,
        "reasons_discarded": 2,
    }
    assert sorted(rows(seeded, "canonical_fact", "company_id, canonical_concept_id, period_id, value, source_fact_ids")) == before  # fmt: skip
    assert not rows(seeded, "cell_blank_reason")
    assert hw.rollback_run(seeded, s["run_id"]) == {
        "restored": 0,
        "reasons_discarded": 0,
    }


@pytest.mark.integration
def test_periods_of_another_type_are_not_matched(seeded, tmp_path):
    put(seeded, 1, 100, 12, "42")  # a duration period ending on D2
    seeded.commit()
    s = hw.apply_holds(
        seeded,
        [hold(end=D2, value="700000000")],
        before_image=tmp_path / "i.jsonl",
        environ=ON,
    )
    left = rows(seeded, "canonical_fact", "company_id, canonical_concept_id, period_id")
    assert s["blanked"] == 1 and (1, 100, 12) in left and (1, 100, 11) not in left


# ------------------------------------------------------------------ flag
@pytest.mark.integration
@pytest.mark.parametrize("env", [{}, DRY])
def test_apply_refuses_unless_the_writer_rule_is_on(seeded, tmp_path, env):
    with pytest.raises(PermissionError):
        hw.apply_holds(seeded, [hold()], before_image=tmp_path / "i.jsonl", environ=env)
    assert len(rows(seeded, "canonical_fact")) == 4 and not rows(seeded, "rule_run")


@pytest.mark.integration
def test_sink_is_off_by_default_prints_a_summary_in_dry_run_and_writes_only_when_on(
    seeded, tmp_path, capsys
):
    assert hw.sink(seeded, [hold()], environ={}) is None
    assert (
        not rows(seeded, "cell_blank_reason")
        and len(rows(seeded, "canonical_fact")) == 4
    )
    out = hw.sink(seeded, [hold()], environ=DRY)
    assert (
        out["summary"][IDENTITY]["would_blank"] == 1
        and "would_blank=1" in capsys.readouterr().out
    )
    assert len(rows(seeded, "canonical_fact")) == 4
    done = hw.sink(seeded, [hold()], before_image=tmp_path / "i.jsonl", environ=ON)
    assert done["blanked"] == 1 and len(rows(seeded, "canonical_fact")) == 3


def test_the_writer_rule_is_registered_default_off_with_a_dry_run():
    assert rule_flags.RULES[hw.WRITER_RULE].dry_run is True
    assert rule_flags.rule_mode(hw.WRITER_RULE, {}) == rule_flags.OFF
