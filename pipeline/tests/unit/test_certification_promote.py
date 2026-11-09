"""FSN-era certification ladder above checks_clean (certification/promote.py, migration 0122).
Unit tests decide on in-memory evidence; the integration test runs every SQL statement and the
--apply path on REAL Postgres (SCROONER_TEST_DATABASE_URL)."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal as D

import pytest

from scrooner_pipeline.certification import promote as pr

NOW = datetime(2026, 11, 9, 12, tzinfo=timezone.utc)
FY, Q = date(2025, 12, 31), date(2026, 9, 30)


def full_evidence(state="checks_clean") -> pr.Evidence:
    """A company that satisfies every rung."""
    ev = pr.Evidence(1, state)
    ev.template_rows = [("revenue", True), ("ebitda", True)]
    ev.template_cells = ev.template_accounted = 2
    for c in pr.HEADLINE_PROVED:
        ev.served[c] = (40, 40)
        for grain in pr._grains(c):
            end = Q if grain in ("Q", "I") else FY
            ev.latest[(c, grain)] = (end, D("100"))
            ev.checks.append((c, grain, end, "right", D("100"), NOW - timedelta(days=3)))
    ev.checks.append((pr.MARKET_CAP, "I", Q, "right", D("5"), NOW - timedelta(days=3)))
    return ev


def decide(ev):
    return pr.decide(ev, NOW)


@pytest.mark.unit
class TestLadder:
    def test_full_evidence_is_certified(self):
        d = decide(full_evidence())
        assert (d.new_state, d.blockers) == ("certified", ())

    def test_uncertified_is_never_promoted(self):
        d = decide(full_evidence("uncertified"))
        assert d.new_state == "uncertified"

    def test_an_unproven_or_stale_served_cell_stops_at_checks_clean(self):
        ev = full_evidence()
        ev.served["net_income_resolved"] = (40, 39)
        d = decide(ev)
        assert d.new_state == "checks_clean"
        assert d.blockers == ("reconciled:unproven:net_income_resolved:1_of_40",)

    def test_one_disagree_anywhere_blocks_reconciled(self):
        ev = full_evidence()
        ev.disagree["capex_resolved"] = 1
        assert decide(ev).new_state == "checks_clean"

    def test_a_headline_with_no_served_cell_blocks_unless_out_of_template(self):
        ev = full_evidence()
        del ev.served["operating_income_resolved"]
        assert decide(ev).blockers == ("reconciled:no_served_cell:operating_income_resolved",)
        ev.template_rows.append(("operating_income", False))  # bank: OI not in its template
        ev.latest = {k: v for k, v in ev.latest.items() if k[0] != "operating_income_resolved"}
        assert decide(ev).new_state == "certified"

    def test_verified_needs_a_right_check_on_the_current_value_of_each_latest_cell(self):
        ev = full_evidence()
        ev.latest[("revenue_sanity_resolved", "Q")] = (Q, D("101"))  # value changed since the check
        d = decide(ev)
        assert d.new_state == "reconciled"
        assert d.blockers == (f"verified:no_right_check:revenue_sanity_resolved:Q:{Q}",)

    def test_verified_needs_both_fy_and_q_for_flows(self):
        ev = full_evidence()
        ev.checks = [c for c in ev.checks if not (c[0] == "cfo_resolved" and c[1] == "FY")]
        assert decide(ev).blockers == (f"verified:no_right_check:cfo_resolved:FY:{FY}",)

    def test_open_wrong_verdict_blocks_verified(self):
        ev = full_evidence()
        ev.open_wrong = 1
        assert decide(ev).new_state == "reconciled"

    def test_market_cap_check_must_be_recent(self):
        ev = full_evidence()
        ev.checks = [c for c in ev.checks if c[0] != pr.MARKET_CAP]
        ev.checks.append((pr.MARKET_CAP, "I", Q, "right", D("5"), NOW - timedelta(days=40)))
        assert decide(ev).blockers == ("verified:no_recent_right_check:market_cap",)

    def test_certified_needs_a_template_and_every_template_cell_accounted(self):
        ev = full_evidence()
        ev.template_accounted = 1
        d = decide(ev)
        assert (d.new_state, d.blockers) == ("verified", ("certified:template_cells_unaccounted:1_of_2",))
        ev = full_evidence()
        ev.template_rows, ev.template_cells, ev.template_accounted = [], 0, 0
        assert decide(ev).blockers == ("certified:no_sector_template",)

    def test_template_out_needs_every_variant_out(self):
        assert pr.template_out([("revenue", True), ("revenue_sanity_resolved", False)]) == set()
        assert pr.template_out([("capex", False), ("capex_resolved", False)]) == {"capex"}


# --------------------------------------------------------------------------- real SQL


@pytest.fixture
def db(isolated_database_url):
    psycopg = pytest.importorskip("psycopg")
    conn = psycopg.connect(isolated_database_url)
    if not conn.execute("select to_regclass('analytics.verifier_check') is not null").fetchone()[0]:
        conn.close()
        pytest.skip("needs the migrated schema with migration 0122")
    yield conn
    conn.close()


def _seed(conn):
    """One company with every headline concept served on one FY and one Q (or one instant),
    each proven, verified and template-accounted."""
    one = lambda sql, p=(): conn.execute(sql, p).fetchone()[0]  # noqa: E731
    cid = one("insert into core.company (cik, company_name) values ('0000000555', 'PROMO') returning id")
    run = one("insert into analytics.rule_run (rule_id, rule_version, mode, flag_name, flag_state)"
              " values ('fsn.select@1', 1, 'apply', 'f', 'on') returning run_id")  # fmt: skip
    periods = {
        "FY": one("insert into core.period (company_id, start_date, end_date, period_type)"
                  " values (%s, '2025-01-01', '2025-12-31', 'duration') returning id", (cid,)),  # fmt: skip
        "Q": one("insert into core.period (company_id, start_date, end_date, period_type)"
                 " values (%s, '2026-07-01', '2026-09-30', 'duration') returning id", (cid,)),  # fmt: skip
        "I": one("insert into core.period (company_id, start_date, end_date, period_type)"
                 " values (%s, '2026-09-30', '2026-09-30', 'instant') returning id", (cid,)),  # fmt: skip
    }
    span = {"FY": ("2025-01-01", "2025-12-31"), "Q": ("2026-07-01", "2026-09-30"), "I": ("2026-09-30", "2026-09-30")}
    for name in pr.HEADLINE_PROVED:
        ccid = one("insert into analytics.canonical_concept (name, statement, combination_mode)"
                   " values (%s, 'income_statement', 'first_match')"
                   " on conflict (name) do update set name = excluded.name returning id", (name,))  # fmt: skip
        for grain in pr._grains(name):
            conn.execute("insert into analytics.canonical_fact (company_id, canonical_concept_id, period_id, value,"
                         " source_fact_ids, rule_run_id, family) values (%s, %s, %s, 100, '{}', %s, 'is')",
                         (cid, ccid, periods[grain], run))  # fmt: skip
            start, end = span[grain]
            conn.execute(
                "insert into analytics.cell_proof (company_id, data_point_name, period_grain, period_start, period_end,"
                " shown_value, position_value, position_is_expected_line, verdict, detector_version)"
                " values (%s, %s, %s, %s, %s, 100, 100, true, 'PROVEN', 'v5')", (cid, name, grain, start, end))  # fmt: skip
            conn.execute(
                "insert into analytics.verifier_check (company_id, data_point_name, period_grain, period_start,"
                " period_end, verdict, shown_value, filing_value, accession, locator, draw_id, verifier_session)"
                " values (%s, %s, %s, %s, %s, 'right', 100, 100, '0000000555-26-000001', 'R4 row 3', 'seed1', 'v')",
                (cid, name, grain, start, end))  # fmt: skip
    conn.execute(
        "insert into analytics.verifier_check (company_id, data_point_name, period_grain, period_start, period_end,"
        " verdict, shown_value, filing_value, accession, locator, draw_id, verifier_session, checked_at)"
        " values (%s, 'market_cap', 'I', '2026-11-01', '2026-11-01', 'right', 5, 5, '0000000555-26-000001',"
        " 'price x shares', 'seed1', 'v', %s)", (cid, NOW - timedelta(days=2)))  # fmt: skip
    for dp in ("revenue", "inventory"):
        conn.execute(
            "insert into analytics.company_data_point_template (company_id, data_point, in_template, reason,"
            " effective_from, template, source, template_version) values (%s, %s, true, null, '2026-11-01',"
            " 'general', 'sector_default', 'tv')", (cid, dp))  # fmt: skip
        conn.execute("insert into analytics.data_point_registry (data_point_name, data_point_type)"
                     " values (%s, 'concept') on conflict do nothing", (dp,))  # fmt: skip
    # an old-pipeline summary saying revenue AND inventory have values: never read (one source)
    conn.execute("insert into analytics.company_data_point_coverage (company_id, data_point_name, has_value)"
                 " values (%s, 'revenue', true), (%s, 'inventory', true)", (cid, cid))  # fmt: skip
    conn.execute(
        "insert into analytics.cell_blank_reason (run_id, company_id, data_point_name, period_grain, period_start,"
        " period_end, state, rule_id, reason_code) values (%s, %s, 'inventory', 'I', '2026-09-30', '2026-09-30',"
        " 'not_presented', 'fsn.cells@1', 'line_not_presented')", (run, cid))  # fmt: skip
    conn.execute("insert into analytics.company_certification (company_id, state, open_findings)"
                 " values (%s, 'checks_clean', 0)", (cid,))  # fmt: skip
    conn.commit()
    return cid


def _state(conn, cid):
    return conn.execute(
        "select state, reconciled_at is not null, verified_at is not null, certified_at is not null"
        " from analytics.company_certification where company_id = %s", (cid,)).fetchone()  # fmt: skip


@pytest.mark.integration
def test_promote_end_to_end_on_real_sql(db, isolated_database_url):
    cid = _seed(db)
    (d,) = pr.promote(db, [cid], apply=False, as_of=date(2026, 11, 9), now=NOW)
    assert (d.new_state, d.blockers) == ("certified", ())
    assert _state(db, cid) == ("checks_clean", False, False, False)  # dry run wrote nothing
    db.rollback()

    pr.promote(db, [cid], apply=True, as_of=date(2026, 11, 9), now=NOW)
    assert _state(db, cid) == ("certified", True, True, True)
    psycopg = pytest.importorskip("psycopg")
    with psycopg.connect(isolated_database_url) as other:  # committed, not just visible here
        assert _state(other, cid) == ("certified", True, True, True)

    # a served value changes after its proof and its check: the proof is stale -> demoted
    db.execute("update analytics.canonical_fact set value = 101 where company_id = %s and canonical_concept_id ="
               " (select id from analytics.canonical_concept where name = 'cfo_resolved')", (cid,))  # fmt: skip
    db.commit()
    (d,) = pr.promote(db, [cid], apply=True, as_of=date(2026, 11, 9), now=NOW)
    assert d.new_state == "checks_clean" and d.blockers == ("reconciled:unproven:cfo_resolved:2_of_2",)
    assert _state(db, cid) == ("checks_clean", False, False, False)

    # a newer DISAGREE proof row for one capex cell also blocks once the value is restored
    db.execute("update analytics.canonical_fact set value = 100 where company_id = %s", (cid,))
    db.execute("insert into analytics.cell_proof (company_id, data_point_name, period_grain, period_start, period_end,"
               " shown_value, position_value, verdict, reason_code, detector_version, rule_id)"
               " values (%s, 'capex_resolved', 'Q', '2026-07-01', '2026-09-30', 100, 90, 'DISAGREE', 'x', 'v6',"
               " 'proof.cell_proof@2')", (cid,))  # fmt: skip
    db.commit()
    (d,) = pr.promote(db, [cid], apply=False, as_of=date(2026, 11, 9), now=NOW)
    assert "reconciled:disagree:capex_resolved:1" in d.blockers
    db.rollback()


@pytest.mark.integration
def test_open_wrong_verdict_and_unaccounted_template_cell(db):
    cid = _seed(db)
    db.execute(
        "insert into analytics.verifier_check (company_id, data_point_name, period_grain, period_start, period_end,"
        " verdict, shown_value, filing_value, accession, locator, draw_id, verifier_session) values"
        " (%s, 'sga_expense', 'FY', '2025-01-01', '2025-12-31', 'wrong', 7, 8, '0000000555-26-000001', 'R4 row 9',"
        " 'seed2', 'v')", (cid,))  # fmt: skip
    db.commit()
    (d,) = pr.promote(db, [cid], as_of=date(2026, 11, 9), now=NOW)
    assert (d.new_state, d.blockers) == ("reconciled", ("verified:open_wrong_verdicts:1",))
    db.rollback()
    db.execute("update analytics.verifier_check set superseded_at = now(), superseded_reason = 'class fixed'"
               " where verdict = 'wrong'")  # fmt: skip
    # the newest blank reason for inventory becomes an unclassified defect
    run = db.execute("select run_id from analytics.rule_run limit 1").fetchone()[0]
    db.execute(
        "insert into analytics.cell_blank_reason (run_id, company_id, data_point_name, period_grain, period_start,"
        " period_end, state, defect_class, owner, rule_id, reason_code, created_at) values (%s, %s, 'inventory', 'Q',"
        " '2026-07-01', '2026-09-30', 'defect', 'unclassified', 'triage', 'fsn.cells@1', 'u', now() + interval '1 day')",
        (run, cid))  # fmt: skip
    db.commit()
    (d,) = pr.promote(db, [cid], as_of=date(2026, 11, 9), now=NOW)
    assert (d.new_state, d.blockers) == ("verified", ("certified:template_cells_unaccounted:1_of_2",))
    db.rollback()


@pytest.mark.integration
def test_constraints_and_never_creates_a_row(db):
    psycopg = pytest.importorskip("psycopg")
    cid = _seed(db)
    for bad in ("'right', 100, null, '0000000555-26-000001', 'R4'",  # right needs the filing value
                "'wrong', 100, 90, null, 'R4'",  # a value verdict needs the accession
                "'right', 100, 100, 'bad-accession', 'R4'",
                "'right', 100, 100, '0000000555-26-000001', ' '"):  # and a locator  # fmt: skip
        with pytest.raises(psycopg.errors.CheckViolation):
            with db.transaction():
                db.execute(
                    "insert into analytics.verifier_check (company_id, data_point_name, period_grain, period_start,"
                    " period_end, verdict, shown_value, filing_value, accession, locator, draw_id, verifier_session)"
                    f" values ({cid}, 'x', 'FY', '2025-01-01', '2025-12-31', {bad}, 'd', 'v')")  # fmt: skip
    db.rollback()
    other = db.execute("insert into core.company (cik, company_name) values ('0000000556', 'NOROW') returning id").fetchone()[0]
    db.commit()
    assert pr.promote(db, [other], apply=True, as_of=date(2026, 11, 9), now=NOW) == []
    assert db.execute("select count(*) from analytics.company_certification where company_id = %s",
                      (other,)).fetchone()[0] == 0  # fmt: skip


@pytest.mark.integration
def test_newest_proof_row_decides_a_served_cell(db):
    """A re-proof that could not check the cell (UNCHECKED) supersedes the older PROVEN row."""
    cid = _seed(db)
    db.execute("insert into analytics.cell_proof (company_id, data_point_name, period_grain, period_start, period_end,"
               " shown_value, verdict, detector_version, rule_id, proved_at)"
               " values (%s, 'diluted_eps_resolved', 'FY', '2025-01-01', '2025-12-31', 100, 'UNCHECKED', 'v6',"
               " 'proof.cell_proof@2', now() + interval '1 hour')", (cid,))  # fmt: skip
    db.commit()
    (d,) = pr.promote(db, [cid], as_of=date(2026, 11, 9), now=NOW)
    assert (d.new_state, d.blockers) == ("checks_clean", ("reconciled:unproven:diluted_eps_resolved:1_of_2",))
    db.rollback()


@pytest.mark.integration
def test_one_source_the_hybrid(db):
    """Founder direction 2026-11-09: a served headline cell the hybrid did not write blocks
    reconciled, and the old company_data_point_coverage summary never accounts a template cell."""
    cid = _seed(db)
    old = db.execute("insert into analytics.rule_run (rule_id, rule_version, mode, flag_name, flag_state)"
                     " values ('cells.is_core@1', 1, 'apply', 'f', 'on') returning run_id").fetchone()[0]  # fmt: skip
    db.execute("update analytics.canonical_fact set rule_run_id = %s where company_id = %s and canonical_concept_id ="
               " (select id from analytics.canonical_concept where name = 'net_income_resolved')"
               " and period_id = (select id from core.period where company_id = %s and end_date = '2025-12-31')",
               (old, cid, cid))  # fmt: skip
    db.commit()
    (d,) = pr.promote(db, [cid], as_of=date(2026, 11, 9), now=NOW)
    assert (d.new_state, d.blockers) == ("checks_clean", ("reconciled:not_hybrid:net_income_resolved:1_of_2",))
    db.rollback()
    db.execute("update analytics.canonical_fact set rule_run_id = (select run_id from analytics.rule_run"
               " where rule_id = 'fsn.select@1') where company_id = %s", (cid,))  # fmt: skip
    db.execute("delete from analytics.cell_blank_reason where company_id = %s", (cid,))
    # an old-pipeline inventory value (non-fsn rule run) does not account the template cell either
    inv = db.execute("insert into analytics.canonical_concept (name, statement, combination_mode)"
                     " values ('inventory', 'balance_sheet', 'first_match') on conflict (name) do update"
                     " set name = excluded.name returning id").fetchone()[0]  # fmt: skip
    db.execute("insert into analytics.canonical_fact (company_id, canonical_concept_id, period_id, value,"
               " source_fact_ids, rule_run_id) select %s, %s, id, 7, '{}', %s from core.period"
               " where company_id = %s and end_date = '2026-09-30' and start_date = end_date",
               (cid, inv, old, cid))  # fmt: skip
    db.commit()
    (d,) = pr.promote(db, [cid], as_of=date(2026, 11, 9), now=NOW)
    # inventory: coverage says has_value, but no hybrid cell and no writer reason -> unaccounted
    assert (d.new_state, d.blockers) == ("verified", ("certified:template_cells_unaccounted:1_of_2",))
    db.rollback()
