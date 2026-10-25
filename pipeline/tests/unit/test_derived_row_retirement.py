"""mapper/derived_row_retirement.py: plan (read-only), apply (flag-gated) and
restore on real SQL in an isolated database (schemas rcore / ranalytics stand
in for core / analytics). The archive DDL below is a copy of migration 0098's
canonical_fact_retired (foreign keys stripped) plus the draft
fact_authority_retired; both live in the test database only."""

from datetime import date
from decimal import Decimal

import psycopg
import pytest

from scrooner_pipeline.common import rule_flags as rf
from scrooner_pipeline.mapper import derived_row_retirement as rr

ON_RATIO = {rf.ENV_ENABLED: rr.RULE_RATIO}
ON_PROXY = {rf.ENV_ENABLED: rr.RULE_PROXY}


# ------------------------------------------------------------------ unit
@pytest.mark.unit
def test_rules_are_registered_and_default_off():
    for rule in (rr.RULE_RATIO, rr.RULE_PROXY):
        assert rule in rf.RULES
        assert rf.rule_mode(rule, {}) == rf.OFF
        assert rf.rule_mode(rule, {rf.ENV_DRYRUN: rule}) == rf.DRY_RUN


@pytest.mark.unit
def test_every_reason_code_has_display_text():
    src = __import__("inspect").getsource(rr)
    for code in (
        "ratio_derived_no_filed_value",
        "ratio_derived_filed_copies_disagree",
        "proxy_only_source",
        "proxy_filed_copies_disagree",
    ):
        assert code in rr.REASON_TEXT and code in src


def _fact(fid, value, *, filed, form="10-K"):
    return rr.FactRow(
        fid,
        1,
        1,
        1,
        "T",
        "usd",
        "FY",
        None,
        None,
        Decimal(value),
        True,
        False,
        form,
        "acc",
        filed,
    )


@pytest.mark.unit
def test_pick_one_rounding_is_one_value_and_real_disagreement_is_none():
    a = _fact(1, "1316000000", filed=date(2025, 2, 1))
    b = _fact(2, "1315605000", filed=date(2025, 3, 1))  # 0.03% apart -> not equal
    assert rr._pick_one([a, b]) is None
    c = _fact(3, "1316000000", filed=date(2025, 3, 1))
    assert rr._pick_one([a, c]).fact_id == 3  # most recently filed witness
    assert rr._pick_one([]) is None


@pytest.mark.unit
@pytest.mark.parametrize(
    ("stored", "filed", "bucket"),
    [
        ("268550", "268550000", "scale_1e3_or_1e6"),  # CHE DEFR14A in thousands
        ("2087", "2087321000", "scale_1e3_or_1e6"),  # ANET DEF 14A in millions
        ("1316000000", "1315605000", "under_0.1pct"),
        ("57000", "57048", "under_0.1pct"),
        ("100", "105", "1_to_10pct"),
        ("100", "150", "10pct_or_more"),
    ],
)
def test_gap_bucket(stored, filed, bucket):
    assert rr._gap_bucket(Decimal(stored), Decimal(filed)) == bucket


class _NoCursor:
    def execute(self, *a, **k):
        raise AssertionError("apply touched the database while the rule is off")


@pytest.mark.unit
def test_apply_refuses_when_rule_is_off_or_dry_run_and_never_touches_db():
    plan = rr.Plan("A_ratio_derived", rr.RULE_RATIO)
    for env in ({}, {rf.ENV_DRYRUN: rr.RULE_RATIO}, ON_PROXY):
        with pytest.raises(rr.RuleNotEnabled):
            rr.apply_plan(
                _NoCursor(),
                plan,
                run_id="r",
                expected_digest=plan.digest(),
                environ=env,
            )


@pytest.mark.unit
def test_apply_refuses_a_plan_that_is_not_the_reviewed_one():
    plan = rr.Plan("A_ratio_derived", rr.RULE_RATIO)
    with pytest.raises(rr.PlanChanged):
        rr.apply_plan(
            _NoCursor(), plan, run_id="r", expected_digest="0" * 64, environ=ON_RATIO
        )


@pytest.mark.unit
def test_digest_changes_with_any_decision():
    def cell(action):
        return rr.CellPlan(
            "A", rr.RULE_RATIO, 1, 1, 1, "c", 1, None, Decimal("1"), (5,), (5,), action
        )

    p1 = rr.Plan("A", rr.RULE_RATIO, cells=[cell(rr.ACT_REMOVE)])
    p2 = rr.Plan("A", rr.RULE_RATIO, cells=[cell(rr.ACT_REVIEW)])
    assert (
        p1.digest() != p2.digest()
        and p1.digest()
        == rr.Plan("A", rr.RULE_RATIO, cells=[cell(rr.ACT_REMOVE)]).digest()
    )


# ------------------------------------------------------------ real SQL
ARCHIVE_DDL = """
create table ranalytics.canonical_fact_retired (
    id bigint generated always as identity primary key,
    action text not null check (action in ('replaced', 'removed', 'inserted')),
    canonical_fact_id bigint not null, company_id bigint not null,
    canonical_concept_id bigint not null, period_id bigint not null,
    value numeric, source_fact_ids bigint[], resolved_at timestamptz,
    reason_code text not null, run_id text not null, basis_version text,
    retired_at timestamptz not null default now(), restored_at timestamptz);
"""
SCHEMA = """
create schema rcore; create schema ranalytics;
create table rcore.company (id bigint primary key, cik text);
create table rcore.concept (id bigint primary key, tag text);
create table rcore.unit (id bigint primary key, unit_name text);
create table rcore.period (id bigint primary key, company_id bigint, start_date date,
    end_date date, period_type text, fiscal_year int, fiscal_period text);
create table rcore.filing (id bigint primary key, company_id bigint, accession_number text,
    form text, filing_date date);
create table rcore.fact (id bigint primary key, company_id bigint, concept_id bigint,
    unit_id bigint, period_id bigint, filing_id bigint, value numeric,
    is_derived boolean default false, is_authoritative boolean default true);
create table ranalytics.canonical_concept (id bigint primary key, name text);
create table ranalytics.concept_mapping (id bigserial primary key, canonical_concept_id bigint,
    concept_id bigint, priority int, confidence text default 'approved');
create table ranalytics.canonical_fact (id bigint generated always as identity primary key,
    company_id bigint not null, canonical_concept_id bigint not null, period_id bigint not null,
    value numeric not null, source_fact_ids bigint[] not null,
    resolved_at timestamptz not null default now(),
    unique (company_id, canonical_concept_id, period_id));
create table ranalytics.metric_value (id bigserial primary key, company_id bigint,
    source_fact_ids bigint[]);
"""
TAX, NI, OTHER = 303, 11, 12
PURE, USD = 1, 2
CC_TAX, CC_NI, CC_NI_RES = 148, 4, 253


@pytest.fixture
def conn(isolated_database_url):
    with psycopg.connect(isolated_database_url) as c:
        c.execute(
            "drop schema if exists rcore cascade; drop schema if exists ranalytics cascade"
        )
        c.execute(SCHEMA)
        c.execute("insert into rcore.company values (1,'0000000001')")
        c.execute(ARCHIVE_DDL)
        c.execute(
            rr.FACT_AUTHORITY_RETIRED_DDL_DRAFT.replace("analytics.", "ranalytics.")
        )
        c.execute(
            "insert into rcore.concept values (303,'EffectiveIncomeTaxRateContinuingOperations'),"
            "(11,'NetIncomeLoss'),(12,'OtherRate')"
        )
        c.execute("insert into rcore.unit values (1,'pure'),(2,'usd')")
        c.execute(
            "insert into ranalytics.canonical_concept values (148,'effective_tax_rate_reported'),"
            "(4,'net_income'),(253,'net_income_resolved')"
        )
        c.execute(
            "insert into ranalytics.concept_mapping (canonical_concept_id, concept_id, priority)"
            " values (148,303,1),(4,11,1)"
        )
        c.execute(
            "insert into rcore.filing values (1,1,'K1','10-K','2026-02-01'),"
            "(2,1,'P1','DEF 14A','2026-04-01'),(3,1,'Q1','10-Q','2025-11-01'),"
            "(4,1,'E1','8-K','2026-03-01'),(5,1,'K2','10-K','2026-03-01')"
        )
        for i in range(1, 8):
            c.execute(
                "insert into rcore.period values (%s,1,'2025-10-01','2025-12-31','duration',2025,'Q4')",
                (i,),
            )
        yield c
        c.rollback()
        c.execute(
            "drop schema if exists rcore cascade; drop schema if exists ranalytics cascade"
        )
        c.commit()


def _f(c, fid, concept, unit, period, filing, value, *, derived=False, auth=True):
    c.execute(
        "insert into rcore.fact values (%s,1,%s,%s,%s,%s,%s,%s,%s)",
        (fid, concept, unit, period, filing, Decimal(value), derived, auth),
    )


def _cell(c, ccid, period, value, sources):
    return c.execute(
        "insert into ranalytics.canonical_fact (company_id, canonical_concept_id, period_id, value, source_fact_ids)"
        " values (1,%s,%s,%s,%s) returning id",
        (ccid, period, Decimal(value), sources),
    ).fetchone()[0]


def _state(c):
    cells = c.execute(
        "select company_id, canonical_concept_id, period_id, value, source_fact_ids"
        " from ranalytics.canonical_fact order by 1,2,3"
    ).fetchall()
    facts = c.execute(
        "select id, is_authoritative from rcore.fact order by id"
    ).fetchall()
    return cells, facts


def _plan_a(c):
    with c.cursor() as cur:
        return rr.plan_ratio_chunk(
            cur,
            [1],
            cids=[TAX],
            uids=[PURE],
            mapped_priority={TAX: 1},
            core="rcore",
            analytics="ranalytics",
        )


def _plan_b(c):
    with c.cursor() as cur:
        return rr.plan_proxy_chunk(cur, [1], core="rcore", analytics="ranalytics")


def _seed_a(c):
    # period 1: derived Q4 rate -0.40 (PGR shape), a filed 10-K Q4 rate exists -> replace
    _f(c, 100, TAX, PURE, 1, 3, "-0.404", derived=True)
    _f(c, 101, TAX, PURE, 1, 1, "0.206")
    _cell(c, CC_TAX, 1, "-0.404", [100])
    # period 2: derived, nothing filed -> remove with reason
    _f(c, 110, TAX, PURE, 2, 3, "-0.787", derived=True)
    _cell(c, CC_TAX, 2, "-0.787", [110])
    # period 3: cell with two sources -> review, untouched
    _f(c, 120, TAX, PURE, 3, 3, "0.5", derived=True)
    _f(c, 121, TAX, PURE, 3, 1, "0.2")
    _cell(c, CC_TAX, 3, "0.5", [120, 121])
    # period 4: filed copies disagree (and a derived one) -> remove, disagree
    _f(c, 130, TAX, PURE, 4, 3, "0.9", derived=True)
    _f(c, 131, TAX, PURE, 4, 1, "0.21")
    _f(c, 132, TAX, PURE, 4, 5, "0.25")
    _cell(c, CC_TAX, 4, "0.9", [130])
    # not in scope: derived fact on another tag; a filed (not derived) rate cell
    _f(c, 140, OTHER, PURE, 5, 3, "0.1", derived=True)
    _f(c, 141, TAX, PURE, 6, 1, "0.3")
    _cell(c, CC_TAX, 6, "0.3", [141])


def _seed_b(c):
    # period 1 (net_income_resolved): DEF 14A in thousands vs 10-K in dollars -> replace, scale
    _f(c, 200, NI, USD, 1, 2, "268550")
    _f(c, 201, NI, USD, 1, 1, "268550000")
    _cell(c, CC_NI_RES, 1, "268550", [200])
    # period 2: proxy only -> remove proxy_only_source
    _f(c, 210, NI, USD, 2, 2, "57000000000")
    _cell(c, CC_NI_RES, 2, "57000000000", [210])
    # period 3: only a NON-authoritative 10-K copy -> remove, no authoritative periodic copy
    _f(c, 220, NI, USD, 3, 2, "5000")
    _f(c, 221, NI, USD, 3, 1, "5000000", auth=False)
    _cell(c, CC_NI, 3, "5000", [220])
    # period 4: two disagreeing 10-K copies -> remove, copies disagree
    _f(c, 230, NI, USD, 4, 2, "100")
    _f(c, 231, NI, USD, 4, 1, "101000")
    _f(c, 232, NI, USD, 4, 5, "150000")
    _cell(c, CC_NI, 4, "100", [230])
    # period 5: 8-K source -> out of scope, untouched
    _f(c, 240, NI, USD, 5, 4, "777")
    _cell(c, CC_NI, 5, "777", [240])
    # period 6: authoritative proxy fact that feeds no cell -> counted, not demoted
    _f(c, 250, NI, USD, 6, 2, "42")


@pytest.mark.integration
def test_family_a_plan_outcomes(conn):
    _seed_a(conn)
    plan = _plan_a(conn)
    by_period = {c.period_id: c for c in plan.cells}
    assert set(by_period) == {1, 2, 3, 4}
    a = by_period[1]
    assert (a.action, a.replacement_fact_id, a.replacement_value) == (
        rr.ACT_REPLACE,
        101,
        Decimal("0.206"),
    )
    assert (by_period[2].action, by_period[2].reason_code) == (
        rr.ACT_REMOVE,
        "ratio_derived_no_filed_value",
    )
    assert by_period[3].action == rr.ACT_REVIEW
    assert (by_period[4].action, by_period[4].reason_code) == (
        rr.ACT_REMOVE,
        "ratio_derived_filed_copies_disagree",
    )
    # demote list: only authoritative derived tax-rate facts, 140 (other tag) and 101 (filed) excluded
    assert sorted(f.fact_id for f in plan.facts) == [100, 110, 120, 130]
    assert plan.info["derived_ratio_facts_total"] == 4
    s = rr.summarize(plan, cohort={1})
    assert s["all_companies"]["cells"] == 4 and s["cohort"]["cells"] == 4
    assert s["all_companies"]["by_action"][rr.ACT_REPLACE] == 1


@pytest.mark.integration
def test_family_b_plan_outcomes(conn):
    _seed_b(conn)
    plan = _plan_b(conn)
    by_period = {c.period_id: c for c in plan.cells}
    assert set(by_period) == {1, 2, 3, 4}
    assert (
        by_period[1].action == rr.ACT_REPLACE
        and by_period[1].replacement_fact_id == 201
    )
    assert by_period[1].note == "scale_1e3_or_1e6"
    assert by_period[2].reason_code == "proxy_only_source"
    assert (
        by_period[3].action == rr.ACT_REPLACE
        and by_period[3].replacement_fact_id == 221
    )
    assert plan.promote_fact_ids == [
        221
    ]  # non-authoritative only because the proxy conflicted
    assert by_period[4].reason_code == "proxy_filed_copies_disagree"
    assert sorted(f.fact_id for f in plan.facts) == [200, 210, 220, 230]
    assert plan.info["proxy_facts_authoritative_not_displayed"] == 1  # fact 250
    assert plan.info["proxy_forms_met"] == {"DEF 14A": 5}


@pytest.mark.integration
def test_plan_is_read_only(conn):
    _seed_a(conn)
    _seed_b(conn)
    before = _state(conn)
    _plan_a(conn)
    _plan_b(conn)
    assert _state(conn) == before


@pytest.mark.integration
@pytest.mark.parametrize("family", ["A", "B"])
def test_apply_then_restore_is_exact_and_replan_is_empty(conn, family):
    _seed_a(conn)
    _seed_b(conn)
    plan_fn, env = (_plan_a, ON_RATIO) if family == "A" else (_plan_b, ON_PROXY)
    before = _state(conn)
    plan = plan_fn(conn)
    with conn.cursor() as cur:
        stats = rr.apply_plan(
            cur,
            plan,
            run_id="run-1",
            expected_digest=plan.digest(),
            environ=env,
            core="rcore",
            analytics="ranalytics",
        )
    after = _state(conn)
    assert after != before
    assert stats["facts_demoted"] == len(plan.facts) == 4
    assert stats["cells_replaced"] == (1 if family == "A" else 2)
    assert stats["cells_removed"] == 2
    assert stats["facts_promoted"] == (0 if family == "A" else 1)
    facts = dict(after[1])
    for f in plan.facts:
        assert facts[f.fact_id] is False
    cells = {(c[1], c[2]): c for c in after[0]}
    if family == "A":
        assert cells[(CC_TAX, 1)][3] == Decimal("0.206") and cells[(CC_TAX, 1)][4] == [
            101
        ]
        assert (CC_TAX, 2) not in cells and (CC_TAX, 4) not in cells
        assert cells[(CC_TAX, 3)][3] == Decimal("0.5")  # review cell untouched
    else:
        assert cells[(CC_NI_RES, 1)][3] == Decimal("268550000")
        assert (CC_NI_RES, 2) not in cells and (CC_NI, 4) not in cells
        assert cells[(CC_NI, 3)][3] == Decimal("5000000")
        assert cells[(CC_NI, 5)][3] == Decimal("777")  # 8-K untouched
    # retired rows keep their before-image and reason
    arch = conn.execute(
        "select action, reason_code from ranalytics.canonical_fact_retired"
        " where run_id='run-1' order by canonical_fact_id"
    ).fetchall()
    assert {a[0] for a in arch} == {"replaced", "removed"}
    assert all(a[1].startswith(plan.rule_id) for a in arch)
    # a second look finds nothing left to retire in the rule's own scope
    again = plan_fn(conn)
    assert [
        c for c in again.cells if c.action != rr.ACT_REVIEW
    ] == [] and again.facts == []
    # rollback restores cells and facts exactly
    with conn.cursor() as cur:
        out = rr.restore(cur, "run-1", core="rcore", analytics="ranalytics")
    assert out["facts_restored"] == (4 if family == "A" else 5)
    restored = _state(conn)
    assert restored[1] == before[1]
    assert sorted(restored[0], key=lambda r: (r[1], r[2])) == sorted(
        before[0], key=lambda r: (r[1], r[2])
    )
    with conn.cursor() as cur:  # twice is a no-op
        assert (
            rr.restore(cur, "run-1", core="rcore", analytics="ranalytics")[
                "facts_restored"
            ]
            == 0
        )


@pytest.mark.integration
def test_apply_refuses_stale_cells_and_changes_nothing(conn):
    _seed_a(conn)
    plan = _plan_a(conn)
    conn.execute("update ranalytics.canonical_fact set value = 9 where period_id = 2")
    before = _state(conn)
    with conn.cursor() as cur:
        with pytest.raises(rr.PlanChanged):
            rr.apply_plan(
                cur,
                plan,
                run_id="run-2",
                expected_digest=plan.digest(),
                environ=ON_RATIO,
                core="rcore",
                analytics="ranalytics",
            )
    assert _state(conn) == before


@pytest.mark.integration
def test_apply_with_flag_off_changes_nothing(conn):
    _seed_a(conn)
    plan = _plan_a(conn)
    before = _state(conn)
    with conn.cursor() as cur:
        with pytest.raises(rr.RuleNotEnabled):
            rr.apply_plan(
                cur,
                plan,
                run_id="run-3",
                expected_digest=plan.digest(),
                environ={},
                core="rcore",
                analytics="ranalytics",
            )
    assert _state(conn) == before


PROFIT, CC_PROFIT_PRIO = 13, 2


def _extra_b(c):
    c.execute("insert into rcore.concept values (13,'ProfitLoss')")
    c.execute(
        "insert into ranalytics.concept_mapping (canonical_concept_id, concept_id, priority)"
        " values (4,13,2)"
    )
    # period 6 (MA): proxy NetIncomeLoss rounded; the 10-K carries it on ProfitLoss only
    _f(c, 300, NI, USD, 6, 2, "12900000000")
    _f(c, 301, PROFIT, USD, 6, 1, "12874000000")
    _cell(c, CC_NI, 6, "12900000000", [300])
    # period 7 (SM/ANET): precise 10-K copy vs a later rounded copy -> keep the precise one
    _f(c, 310, NI, USD, 7, 2, "2087")
    _f(c, 311, NI, USD, 7, 1, "2087321000")
    _f(c, 312, NI, USD, 7, 5, "2087000000")
    _cell(c, CC_NI, 7, "2087", [310])
    # Q4 derived on a proxy filing (CMG/NFLX shape): fall back to the 10-K-derived Q4 fact
    _f(c, 320, NI, USD, 8, 2, "999", derived=True)
    _f(c, 321, NI, USD, 8, 1, "1234", derived=True)
    _cell(c, CC_NI, 8, "999", [320])


@pytest.mark.integration
def test_family_b_other_tag_precise_copy_and_derived_q4_fallback(conn):
    conn.execute(
        "insert into rcore.period values (8,1,'2025-10-01','2025-12-31','duration',2025,'Q4')"
    )
    _extra_b(conn)
    plan = _plan_b(conn)
    by_period = {c.period_id: c for c in plan.cells}
    assert (by_period[6].action, by_period[6].replacement_fact_id) == (
        rr.ACT_REPLACE,
        301,
    )
    assert (by_period[7].action, by_period[7].replacement_fact_id) == (
        rr.ACT_REPLACE,
        311,
    )
    assert (by_period[8].action, by_period[8].replacement_fact_id) == (
        rr.ACT_REPLACE,
        321,
    )
    assert plan.promote_fact_ids == []


@pytest.mark.unit
def test_rounded_copy_rule():
    D = Decimal
    assert rr._rounded_copy_of(D("770000000"), D("770293000"))  # SM
    assert rr._rounded_copy_of(D("29000000"), D("29373000"))  # WDAY
    assert rr._rounded_copy_of(D("230000000"), D("230141000"))  # NOW
    assert rr._rounded_copy_of(D("-3900000000"), D("-3909000000"))  # ST
    assert rr._rounded_copy_of(D("100000000"), D("100293000"))
    assert not rr._rounded_copy_of(D("1000000"), D("1100000"))  # restatement
    assert not rr._rounded_copy_of(D("770000000"), D("780000000"))


@pytest.mark.integration
def test_family_b_never_replaces_with_nci_inclusive_income(conn):
    conn.execute(
        "insert into rcore.concept values (13,'ProfitLoss'),(14,'NetIncomeLossAttributableToNoncontrollingInterest')"
    )
    conn.execute(
        "insert into ranalytics.concept_mapping (canonical_concept_id, concept_id, priority) values (4,13,0)"
    )  # ProfitLoss ranked FIRST, as in the real mapping
    # FCX shape: ProfitLoss 5,365 > attributable 4,306; attributable wins
    _f(conn, 500, NI, USD, 1, 2, "5000")
    _f(conn, 501, PROFIT, USD, 1, 1, "5365000000")
    _f(conn, 502, NI, USD, 1, 1, "4306000000")
    _cell(conn, CC_NI, 1, "5000", [500])
    # ProfitLoss only and a nonzero NCI fact: hidden, not replaced
    _f(conn, 510, NI, USD, 2, 2, "100")
    _f(conn, 511, PROFIT, USD, 2, 1, "313675000")
    _f(conn, 512, 14, USD, 2, 1, "8800000")
    _cell(conn, CC_NI, 2, "100", [510])
    # ProfitLoss only, no NCI fact: usable (MA shape)
    _f(conn, 520, NI, USD, 3, 2, "12900000000")
    _f(conn, 521, PROFIT, USD, 3, 1, "12874000000")
    _cell(conn, CC_NI, 3, "12900000000", [520])
    by = {c.period_id: c for c in _plan_b(conn).cells}
    assert (by[1].action, by[1].replacement_fact_id) == (rr.ACT_REPLACE, 502)
    assert (by[2].action, by[2].reason_code) == (
        rr.ACT_REMOVE,
        "proxy_nci_inclusive_only",
    )
    assert (by[3].action, by[3].replacement_fact_id) == (rr.ACT_REPLACE, 521)


@pytest.mark.integration
def test_family_b_vintage_disagreement_hides_the_cell(conn):
    # RGA/MET shape: original and restated 10-K values differ materially -> hide
    _f(conn, 400, NI, USD, 1, 2, "100")
    _f(conn, 401, NI, USD, 1, 1, "1000000", auth=False)
    _f(conn, 402, NI, USD, 1, 5, "1100000", auth=False)
    _cell(conn, CC_NI, 1, "100", [400])
    plan = _plan_b(conn)
    assert plan.cells[0].action == rr.ACT_REMOVE
    assert plan.cells[0].reason_code == "proxy_filed_copies_disagree"
    assert plan.promote_fact_ids == []


@pytest.mark.unit
def test_pick_precise_resolves_sm_wday_now_rounding_but_not_restatements():
    precise = _fact(1, "770293000", filed=date(2025, 2, 1))
    rounded = _fact(2, "770000000", filed=date(2026, 2, 1))  # later, rounded
    assert rr._pick_precise([rounded, precise]).fact_id == 1
    restated = _fact(3, "1100000", filed=date(2026, 2, 1))
    assert (
        rr._pick_precise([_fact(4, "1000000", filed=date(2025, 2, 1)), restated])
        is None
    )


def _quarter_world(c, *, fy_value, fy_filing, extra_fy=()):
    c.execute(
        "insert into rcore.filing values (6,1,'K24','10-K','2024-02-01'),(7,1,'Q21','10-Q','2021-11-01'),(8,1,'K22','10-K','2022-02-01')"
    )
    c.execute(
        "insert into rcore.period values (20,1,'2021-01-01','2021-12-31','duration',2021,'FY'),"
        "(21,1,'2021-01-01','2021-09-30','duration',2021,null),(22,1,'2021-10-01','2021-12-31','duration',2021,'Q4')"
    )
    _f(c, 600, NI, USD, 22, 2, "999")  # the proxy-sourced value on the Q4 cell
    _cell(c, CC_NI, 22, "999", [600])
    _f(c, 610, NI, USD, 20, fy_filing, fy_value)
    for i, (fid, filing, value) in enumerate(extra_fy):
        _f(c, fid, NI, USD, 20, filing, value)
    _f(c, 611, NI, USD, 21, 7, "-693000000")


@pytest.mark.integration
def test_derived_replacement_mixing_vintages_is_removed_and_same_vintage_kept(conn):
    # EQH Q4 2021: restated year (filed 2024) minus original nine months (filed 2021)
    _quarter_world(conn, fy_value="1755000000", fy_filing=6)
    _f(conn, 601, NI, USD, 22, 8, "2448000000", derived=True)
    cell = _plan_b(conn).cells[0]
    assert (cell.action, cell.reason_code) == (rr.ACT_REMOVE, "derived_mixed_vintage")


@pytest.mark.integration
def test_derived_replacement_from_one_vintage_is_kept(conn):
    _quarter_world(conn, fy_value="-439000000", fy_filing=8)
    _f(conn, 601, NI, USD, 22, 8, "254000000", derived=True)
    cell = _plan_b(conn).cells[0]
    assert (cell.action, cell.replacement_fact_id) == (rr.ACT_REPLACE, 601)


@pytest.mark.integration
def test_derived_replacement_from_a_rounded_year_is_removed(conn):
    # ST Q4 2023: year used -3,900M although the precise -3,909M is filed
    _quarter_world(
        conn, fy_value="-3900000000", fy_filing=8, extra_fy=[(612, 6, "-3909000000")]
    )
    _f(conn, 601, NI, USD, 22, 8, "-3207000000", derived=True)  # -3,900 - (-693)
    cell = _plan_b(conn).cells[0]
    assert (cell.action, cell.reason_code) == (
        rr.ACT_REMOVE,
        "derived_from_rounded_input",
    )


@pytest.mark.integration
def test_blank_quarter_gets_its_attributable_year_and_ytd_repromoted(conn):
    # LNG: nothing periodic for the quarter itself, the 10-K year and the 10-Q nine months
    # are non-authoritative: re-promote them so the next Normalizer run can derive Q4
    _quarter_world(conn, fy_value="-1000000000", fy_filing=8)
    conn.execute(
        "update rcore.fact set is_authoritative = false where id in (610, 611)"
    )
    plan = _plan_b(conn)
    assert plan.cells[0].action == rr.ACT_REMOVE
    assert plan.promote_fact_ids == [610, 611]


def _blocked_nci(conn):
    conn.execute(
        "insert into rcore.concept values (13,'ProfitLoss'),(14,'NetIncomeLossAttributableToNoncontrollingInterest')"
    )
    conn.execute(
        "insert into ranalytics.concept_mapping (canonical_concept_id, concept_id, priority) values (4,13,0)"
    )
    _f(conn, 700, NI, USD, 1, 2, "100")
    _f(conn, 701, PROFIT, USD, 1, 1, "12874000000")
    _f(conn, 702, 14, USD, 1, 5, "16000000")  # an NCI fact exists, but not on the face
    _cell(conn, CC_NI, 1, "100", [700])
    return _plan_b(conn)


@pytest.mark.integration
@pytest.mark.parametrize(
    ("labels", "released"),
    [
        (["Revenues", "Net Income"], True),  # MA: one bottom line
        (
            [
                "Net income",
                "Net income attributable to noncontrolling interests",
                "Net income attributable to X",
            ],
            False,
        ),
        (None, False),  # statement not located: no evidence, stays hidden
    ],
)
def test_nci_block_is_released_only_by_a_face_without_nci_line(conn, labels, released):
    plan = _blocked_nci(conn)
    assert plan.cells[0].reason_code == "proxy_nci_inclusive_only"
    with conn.cursor() as cur:
        rr.resolve_nci_face(cur, plan, lambda cik, acc: labels, core="rcore")
    assert (plan.cells[0].action == rr.ACT_REPLACE) is released
    if released:
        assert plan.cells[0].replacement_fact_id == 701
