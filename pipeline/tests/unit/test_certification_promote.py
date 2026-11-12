"""FSN-era certification ladder above checks_clean (certification/promote.py, migration 0124),
with one test per hole of the Verifier FIX 2026-11-09 (VERIFY-TEMPLATES-AND-LADDER-2026-11-09).
Unit tests decide on in-memory evidence; the integration tests run every SQL statement, the
writer guard and the --apply path on REAL Postgres (SCROONER_TEST_DATABASE_URL)."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal as D
from pathlib import Path

import pytest

from scrooner_pipeline.certification import promote as pr

NOW = datetime(2026, 11, 9, 12, tzinfo=timezone.utc)
FY, Q = date(2025, 12, 31), date(2026, 9, 30)
HASH = "h1"


def full_evidence(state="checks_clean") -> pr.Evidence:
    """A company that satisfies every rung."""
    ev = pr.Evidence(1, state)
    ev.template_rows = [("revenue", True), ("ebitda", True)]
    ev.template_cells = ev.template_accounted = 2
    ev.template_reasoned = 1
    ev.cells_hash = HASH
    at = NOW - timedelta(days=3)
    for c in pr.HEADLINE_PROVED:
        ev.served[c] = (40, 40)
        ev.hybrid[c] = 40
        for grain in pr._grains(c):
            end = Q if grain in ("Q", "I") else FY
            ev.latest[(c, grain)] = (end, D("100"))
            ev.checks.append(
                (c, grain, end, "right", D("100"), at, "head1", "headline", None)
            )
    ev.checks.append(
        (pr.MARKET_CAP, "I", Q, "right", D("5"), at, "head1", "headline", None)
    )
    for i in range(pr.ALL_CELLS_DRAW_MIN):
        ev.checks.append(
            (f"dp{i}", "FY", FY, "right", D(i), at, "all1", "all_cells", HASH)
        )
    ev.checks.append(
        ("inventory", "I", Q, "blank_right", None, at, "blank1", "blanks", None)
    )
    return ev


def decide(ev):
    return pr.decide(ev, NOW)


@pytest.mark.unit
class TestLadder:
    def test_full_evidence_is_certified(self):
        d = decide(full_evidence())
        assert (d.new_state, d.blockers) == ("certified", ())

    def test_uncertified_is_never_promoted(self):
        assert decide(full_evidence("uncertified")).new_state == "uncertified"

    def test_an_unproven_served_cell_stops_at_checks_clean(self):
        ev = full_evidence()
        ev.served["net_income_resolved"] = (40, 39)
        d = decide(ev)
        assert (d.new_state, d.blockers) == (
            "checks_clean",
            ("reconciled:unproven:net_income_resolved:1_of_40",),
        )

    def test_a_headline_with_no_served_cell_blocks_unless_out_of_template(self):
        ev = full_evidence()
        del ev.served["operating_income_resolved"]
        assert decide(ev).blockers == (
            "reconciled:no_served_cell:operating_income_resolved",
        )
        ev.template_rows.append(
            ("operating_income", False)
        )  # bank: OI not in its template
        ev.latest = {
            k: v for k, v in ev.latest.items() if k[0] != "operating_income_resolved"
        }
        assert decide(ev).new_state == "certified"

    def test_old_mapper_cell_blocks(self):
        ev = full_evidence()
        ev.hybrid["cfo_resolved"] = 39
        assert decide(ev).blockers == ("reconciled:not_hybrid:cfo_resolved:1_of_40",)

    def test_hole2_a_disagree_on_any_data_point_blocks(self):
        ev = full_evidence()
        ev.disagree["sga_expense_resolved"] = 1  # not a headline concept
        d = decide(ev)
        assert (d.new_state, d.blockers) == (
            "checks_clean",
            ("reconciled:disagree:sga_expense_resolved:1",),
        )

    def test_verified_needs_a_right_check_on_the_current_value_of_each_latest_cell(
        self,
    ):
        ev = full_evidence()
        ev.latest[("revenue_sanity_resolved", "Q")] = (Q, D("101"))
        assert decide(ev).blockers == (
            f"verified:no_right_check:revenue_sanity_resolved:Q:{Q}",
        )

    def test_verified_needs_both_fy_and_q_for_flows(self):
        ev = full_evidence()
        ev.checks = [
            c for c in ev.checks if not (c[0] == "cfo_resolved" and c[1] == "FY")
        ]
        assert decide(ev).blockers == (f"verified:no_right_check:cfo_resolved:FY:{FY}",)

    def test_open_wrong_verdict_blocks_verified(self):
        ev = full_evidence()
        ev.open_wrong = 1
        assert decide(ev).new_state == "reconciled"

    def test_market_cap_check_must_be_recent(self):
        ev = full_evidence()
        ev.checks = [c for c in ev.checks if c[0] != pr.MARKET_CAP]
        ev.checks.append(
            (
                pr.MARKET_CAP,
                "I",
                Q,
                "right",
                D("5"),
                NOW - timedelta(days=40),
                "h",
                "headline",
                None,
            )
        )
        assert decide(ev).blockers == ("verified:no_recent_right_check:market_cap",)

    def test_hole1_verified_needs_an_all_cells_draw_of_the_minimum_size(self):
        ev = full_evidence()
        ev.checks = [
            c for c in ev.checks if not (c[7] == "all_cells" and c[0] == "dp0")
        ]
        n = pr.ALL_CELLS_DRAW_MIN - 1
        assert decide(ev).blockers == (
            f"verified:all_cells_draw:{n}_of_min_{pr.ALL_CELLS_DRAW_MIN}",
        )

    def test_hole1_the_newest_all_cells_draw_decides_and_must_be_clean(self):
        ev = full_evidence()
        later = NOW - timedelta(days=1)  # a newer draw with one wrong blank
        ev.checks += [
            (f"x{i}", "FY", FY, "right", D(i), later, "all2", "all_cells", HASH)
            for i in range(19)
        ]
        ev.checks.append(
            ("x19", "FY", FY, "blank_wrong", None, later, "all2", "all_cells", HASH)
        )
        d = decide(ev)
        assert (
            d.blockers == ("verified:all_cells_draw_not_clean",)
            and d.new_state == "reconciled"
        )

    def test_hole6_a_change_to_any_shown_cell_after_the_draw_drops_verified(self):
        ev = full_evidence()
        ev.cells_hash = "h2"  # a nightly refresh changed a metric value after the draw
        d = decide(ev)
        assert (d.new_state, d.blockers) == (
            "reconciled",
            ("verified:cells_changed_since_draw",),
        )

    def test_reasons_must_pass_a_blank_draw(self):
        ev = full_evidence()
        ev.checks = [c for c in ev.checks if c[7] != "blanks"]
        d = decide(ev)
        assert (d.new_state, d.blockers) == (
            "verified",
            ("certified:blank_draw:0_right_of_0_min_1",),
        )
        ev.checks.append(
            ("inventory", "I", Q, "blank_wrong", None, NOW, "blank2", "blanks", None)
        )
        d = decide(
            ev
        )  # newest blanks draw has a wrong reason (open_wrong not set here: the draw alone blocks)
        assert d.blockers == ("certified:blank_draw:0_right_of_1_min_1",)

    def test_certified_needs_a_template_and_every_template_cell_accounted(self):
        ev = full_evidence()
        ev.template_accounted = 1
        assert decide(ev).blockers == ("certified:template_cells_unaccounted:1_of_2",)
        ev = full_evidence()
        (
            ev.template_rows,
            ev.template_cells,
            ev.template_accounted,
            ev.template_reasoned,
        ) = [], 0, 0, 0
        assert decide(ev).blockers == ("certified:no_sector_template",)

    def test_template_out_needs_every_variant_out(self):
        assert (
            pr.template_out([("revenue", True), ("revenue_sanity_resolved", False)])
            == set()
        )
        assert pr.template_out([("capex", False), ("capex_resolved", False)]) == {
            "capex"
        }


# --------------------------------------------------------------------------- real SQL


PENDING_0124 = (
    Path(__file__).resolve().parents[2]
    / "db"
    / "migrations"
    / "pending"
    / "0124_verifier_check.sql"
)


@pytest.fixture
def db(isolated_database_url):
    """A throwaway copy of the migrated test DB. 0124 is held in migrations/pending/ until 0123 exists on
    main (contiguity check), so CI's migration loop does not apply it: apply it here to the copy."""
    psycopg = pytest.importorskip("psycopg")
    conn = psycopg.connect(isolated_database_url)
    if not conn.execute(
        "select to_regclass('analytics.verifier_check') is not null"
    ).fetchone()[0]:
        if not conn.execute(
            "select to_regclass('analytics.cell_proof') is not null"
        ).fetchone()[0]:
            conn.close()
            pytest.skip("needs the migrated schema (cell_proof, 0114)")
        conn.execute(PENDING_0124.read_text())
        conn.commit()
    yield conn
    conn.close()


SPAN = {
    "FY": ("2025-01-01", "2025-12-31"),
    "Q": ("2026-07-01", "2026-09-30"),
    "I": ("2026-09-30", "2026-09-30"),
}
ACC = "0000000555-26-000001"


def _one(conn, sql, p=()):
    return conn.execute(sql, p).fetchone()[0]


def _verifier(conn, cid, dp, grain, verdict, value, draw, kind, cells_hash=None):
    s, e = SPAN[grain]
    conn.execute("set local scrooner.writer = 'verifier'")
    conn.execute(
        "insert into analytics.verifier_check (company_id, data_point_name, period_grain, period_start, period_end,"
        " verdict, shown_value, filing_value, accession, locator, face_label, draw_id, draw_kind, cells_hash,"
        " verifier_session, checked_at) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'R4 row 3', 'Total', %s, %s, %s,"
        " 'v', %s)",
        (cid, dp, grain, s, e, verdict, value, value, ACC if verdict in ("right", "wrong") else None,
         draw, kind, cells_hash, NOW - timedelta(days=2)))  # fmt: skip


def _seed(conn):
    """One company with every headline concept served on one FY and one Q (or one instant), each hybrid-written,
    proven with a face read on the latest print, verified (headline, all_cells, blanks) and template-accounted."""
    cid = _one(
        conn,
        "insert into core.company (cik, company_name) values ('0000000555', 'PROMO') returning id",
    )
    run = _one(conn, "insert into analytics.rule_run (rule_id, rule_version, mode, flag_name, flag_state)"
                     " values ('fsn.select@1', 1, 'apply', 'f', 'on') returning run_id")  # fmt: skip
    periods = {
        g: _one(
            conn,
            "insert into core.period (company_id, start_date, end_date, period_type)"
            " values (%s, %s, %s, %s) returning id",
            (cid, s, e, "instant" if g == "I" else "duration"),
        )  # fmt: skip
        for g, (s, e) in SPAN.items()
    }
    conn.execute(
        "insert into fsn.filing (accession, cik, form, fsn_set, company_id, accepted) values (%s, '0000000555', '10-K', '2026q1', %s, '2026-10-28')",
        (ACC, cid),
    )
    conn.execute("insert into fsn.filing (accession, cik, form, fsn_set, company_id, accepted) values ('0000000555-26-000002', '0000000555', '10-K', '2027q1', %s,"
                 " '2027-02-01')", (cid,))  # a later filing: prints nothing of ours unless a test adds it  # fmt: skip
    conn.execute(
        "insert into fsn.tag (tag, version) values ('Tagnet_income_resolved', 'us-gaap/2024')"
    )
    for name in pr.HEADLINE_PROVED:
        ccid = _one(conn, "insert into analytics.canonical_concept (name, statement, combination_mode)"
                          " values (%s, 'income_statement', 'first_match')"
                          " on conflict (name) do update set name = excluded.name returning id", (name,))  # fmt: skip
        for grain in pr._grains(name):
            conn.execute("insert into analytics.canonical_fact (company_id, canonical_concept_id, period_id, value,"
                         " source_fact_ids, rule_run_id, family) values (%s, %s, %s, 100, '{}', %s, 'is')",
                         (cid, ccid, periods[grain], run))  # fmt: skip
            s, e = SPAN[grain]
            conn.execute(
                "insert into analytics.cell_proof (company_id, data_point_name, period_grain, period_start, period_end,"
                " shown_value, shown_tag, shown_accession, position_value, position_is_expected_line, face_value,"
                " face_label, face_scale, verdict, detector_version) values (%s, %s, %s, %s, %s, 100, %s, %s, 100,"
                " true, 100, %s, 1, 'PROVEN', 'v5')", (cid, name, grain, s, e, "Tag" + name, ACC, "Total " + name))  # fmt: skip
            _verifier(conn, cid, name, grain, "right", 100, "head1", "headline")
    _verifier(conn, cid, "market_cap", "I", "right", 5, "head1", "headline")
    for dp in ("revenue", "inventory"):
        conn.execute(
            "insert into analytics.company_data_point_template (company_id, data_point, in_template, reason,"
            " effective_from, template, source, template_version) values (%s, %s, true, null, '2026-11-01',"
            " 'general', 'sector_default', 'tv')", (cid, dp))  # fmt: skip
    conn.execute(
        "insert into analytics.cell_blank_reason (run_id, company_id, data_point_name, period_grain, period_start,"
        " period_end, state, rule_id, reason_code) values (%s, %s, 'inventory', 'I', '2026-09-30', '2026-09-30',"
        " 'not_presented', 'fsn.cells@1', 'line_not_presented')", (run, cid))  # fmt: skip
    conn.execute("insert into analytics.company_certification (company_id, state, open_findings)"
                 " values (%s, 'checks_clean', 0)", (cid,))  # fmt: skip
    conn.commit()
    with conn.cursor() as cur:
        h = pr.company_cells_hash(cur, [cid])[cid]
    for i in range(pr.ALL_CELLS_DRAW_MIN):
        _verifier(conn, cid, f"dp{i}", "FY", "right", i, "all1", "all_cells", h)
    _verifier(conn, cid, "inventory", "I", "blank_right", None, "blank1", "blanks")
    conn.commit()
    return cid


def _state(conn, cid):
    return conn.execute(
        "select state, reconciled_at is not null, verified_at is not null, certified_at is not null"
        " from analytics.company_certification where company_id = %s", (cid,)).fetchone()  # fmt: skip


def _decide(db, cid):
    (d,) = pr.promote(db, [cid], as_of=date(2026, 11, 9), now=NOW)
    db.rollback()
    return d


@pytest.mark.integration
def test_promote_end_to_end_on_real_sql(db, isolated_database_url):
    psycopg = pytest.importorskip("psycopg")
    cid = _seed(db)
    d = _decide(db, cid)
    assert (d.new_state, d.blockers) == ("certified", ())
    assert _state(db, cid) == (
        "checks_clean",
        False,
        False,
        False,
    )  # dry run wrote nothing
    db.rollback()
    pr.promote(db, [cid], apply=True, as_of=date(2026, 11, 9), now=NOW)
    with psycopg.connect(
        isolated_database_url
    ) as other:  # committed, not just visible here
        assert _state(other, cid) == ("certified", True, True, True)
    # a served value changes: stale proof -> demoted, timestamps cleared
    db.execute("update analytics.canonical_fact set value = 101 where company_id = %s and canonical_concept_id ="
               " (select id from analytics.canonical_concept where name = 'cfo_resolved')", (cid,))  # fmt: skip
    db.commit()
    (d,) = pr.promote(db, [cid], apply=True, as_of=date(2026, 11, 9), now=NOW)
    assert d.blockers == ("reconciled:unproven:cfo_resolved:2_of_2",)
    assert _state(db, cid) == ("checks_clean", False, False, False)
    db.rollback()


@pytest.mark.integration
def test_hole2_disagree_on_a_non_headline_cell_blocks(db):
    cid = _seed(db)
    db.execute("insert into analytics.cell_proof (company_id, data_point_name, period_grain, period_start, period_end,"
               " shown_value, position_value, verdict, reason_code, detector_version) values (%s,"
               " 'sga_expense_resolved', 'FY', '2025-01-01', '2025-12-31', 7, 9, 'DISAGREE', 'x', 'v5')", (cid,))  # fmt: skip
    db.commit()
    assert _decide(db, cid).blockers == ("reconciled:disagree:sga_expense_resolved:1",)


@pytest.mark.integration
def test_hole3_proven_without_a_face_read_or_on_a_segment_line_does_not_count(db):
    cid = _seed(db)
    db.execute("update analytics.cell_proof set face_value = null where company_id = %s"
               " and data_point_name = 'net_income_resolved' and period_grain = 'FY'", (cid,))  # fmt: skip
    db.execute("update analytics.cell_proof set face_label = 'Total segment operating income' where company_id = %s"
               " and data_point_name = 'operating_income_resolved' and period_grain = 'Q'", (cid,))  # fmt: skip
    db.execute("update analytics.cell_proof set face_value = 99 where company_id = %s"
               " and data_point_name = 'capex_resolved' and period_grain = 'Q'", (cid,))  # fmt: skip
    db.execute("update analytics.cell_proof set face_label = ' ' where company_id = %s"
               " and data_point_name = 'diluted_eps_resolved' and period_grain = 'FY'", (cid,))  # a blank label is no read  # fmt: skip
    db.commit()
    assert set(_decide(db, cid).blockers) == {
        "reconciled:unproven:net_income_resolved:1_of_2",
        "reconciled:unproven:operating_income_resolved:1_of_2",
        "reconciled:unproven:capex_resolved:1_of_2",
        "reconciled:unproven:diluted_eps_resolved:1_of_2",
    }


@pytest.mark.integration
def test_hole3_a_face_printed_in_millions_counts_with_its_scale(db):
    cid = _seed(db)
    db.execute("update analytics.cell_proof set face_value = 0.0001, face_scale = 1000000 where company_id = %s"
               " and data_point_name = 'cfo_resolved' and period_grain = 'FY'", (cid,))  # fmt: skip
    db.commit()
    assert _decide(db, cid).new_state == "certified"


@pytest.mark.integration
def test_hole4_a_later_filing_printing_the_column_makes_the_proof_stale(db):
    cid = _seed(db)
    later = _one(
        db, "select id from fsn.filing where accession = '0000000555-26-000002'"
    )
    tag = _one(db, "select id from fsn.tag where tag = 'Tagnet_income_resolved'")
    # FY 2025-12-31 re-printed by the later 10-K (qtrs 4)
    db.execute("insert into fsn.value (filing_id, company_id, tag_id, ddate, qtrs, uom, value, dim_id)"
               " values (%s, %s, %s, '2025-12-31', 4, 'USD', 120, 0)", (later, cid, tag))  # fmt: skip
    db.commit()
    assert _decide(db, cid).blockers == (
        "reconciled:unproven:net_income_resolved:1_of_2",
    )
    # a re-print of a different column (qtrs 1) does not touch the FY cell
    db.execute("update fsn.value set qtrs = 1 where filing_id = %s", (later,))
    db.commit()
    assert _decide(db, cid).new_state == "certified"


@pytest.mark.integration
def test_hole4_fsn_ddate_is_month_end_rounded(db):
    """A 52/53-week year ending 2025-12-27 is stored by FSN under 2025-12-31."""
    cid = _seed(db)
    db.execute(
        "update core.period set end_date = '2025-12-27' where company_id = %s and end_date = '2025-12-31'",
        (cid,),
    )
    db.execute("update analytics.cell_proof set period_end = '2025-12-27' where company_id = %s and period_grain = 'FY'",
               (cid,))  # fmt: skip
    later = _one(
        db, "select id from fsn.filing where accession = '0000000555-26-000002'"
    )
    tag = _one(db, "select id from fsn.tag where tag = 'Tagnet_income_resolved'")
    db.execute("insert into fsn.value (filing_id, company_id, tag_id, ddate, qtrs, uom, value, dim_id)"
               " values (%s, %s, %s, '2025-12-31', 4, 'USD', 120, 0)", (later, cid, tag))  # fmt: skip
    db.commit()
    assert "reconciled:unproven:net_income_resolved:1_of_2" in _decide(db, cid).blockers


@pytest.mark.integration
def test_hole5_a_derived_cell_counts_only_with_proven_inputs_and_a_witness(db):
    cid = _seed(db)
    upd = ("update analytics.cell_proof set face_value = null, face_label = null, checks = %s where company_id = %s"
           " and data_point_name = 'revenue_sanity_resolved' and period_grain = 'Q'")  # fmt: skip
    db.execute(
        upd,
        (
            '{"derived": "true", "inputs_proven": "false", "same_basis_witness": "acc"}',
            cid,
        ),
    )
    db.commit()
    assert _decide(db, cid).blockers == (
        "reconciled:unproven:revenue_sanity_resolved:1_of_2",
    )
    db.execute(upd, ('{"derived": "true", "inputs_proven": "true"}', cid))  # no witness
    db.commit()
    assert _decide(db, cid).blockers == (
        "reconciled:unproven:revenue_sanity_resolved:1_of_2",
    )
    db.execute(
        upd,
        (
            '{"derived": "true", "inputs_proven": "true", "same_basis_witness": "0000000555-26-000001"}',
            cid,
        ),
    )
    db.commit()
    assert _decide(db, cid).new_state == "certified"


@pytest.mark.integration
def test_hole6_a_metric_change_after_the_draw_drops_verified(db):
    cid = _seed(db)
    md = _one(db, "insert into analytics.metric_definition (metric_name, formula_description)"
                  " values ('pe_test', 't') returning id")  # fmt: skip
    db.execute("insert into analytics.metric_value (company_id, metric_definition_id, period_start, period_end,"
               " period_label, value) values (%s, %s, '2026-09-30', '2026-09-30', 'TTM', 21)", (cid, md))  # fmt: skip
    db.commit()
    d = _decide(db, cid)
    assert (d.new_state, d.blockers) == (
        "reconciled",
        ("verified:cells_changed_since_draw",),
    )


@pytest.mark.integration
def test_hole1_superseded_draws_do_not_count(db):
    cid = _seed(db)
    db.execute("set local scrooner.writer = 'verifier'")
    db.execute("update analytics.verifier_check set superseded_at = now(), superseded_reason = 'redraw'"
               " where draw_kind = 'all_cells'")  # fmt: skip
    db.commit()
    assert _decide(db, cid).blockers == (
        f"verified:all_cells_draw:0_of_min_{pr.ALL_CELLS_DRAW_MIN}",
    )


@pytest.mark.integration
def test_blank_draw_on_real_sql(db):
    cid = _seed(db)
    db.execute("set local scrooner.writer = 'verifier'")
    db.execute("update analytics.verifier_check set superseded_at = now(), superseded_reason = 'redraw'"
               " where draw_kind = 'blanks'")  # fmt: skip
    db.commit()
    assert _decide(db, cid).blockers == ("certified:blank_draw:0_right_of_0_min_1",)


@pytest.mark.integration
def test_the_record_is_the_verifiers_and_constraints_hold(db):
    psycopg = pytest.importorskip("psycopg")
    cid = _seed(db)
    with pytest.raises(psycopg.errors.RaiseException, match="Verifier only"):
        with db.transaction():
            db.execute(
                "insert into analytics.verifier_check (company_id, data_point_name, period_grain, period_start,"
                " period_end, verdict, shown_value, filing_value, accession, locator, face_label, draw_id, draw_kind,"
                " verifier_session) values (%s, 'x', 'FY', '2025-01-01', '2025-12-31', 'right', 1, 1, %s, 'R4',"
                " 'L', 'd', 'headline', 'builder')", (cid, ACC))  # fmt: skip
    for bad in ("'right', 100, null, %(acc)s, 'R4', 'L', 'headline', null",  # right needs the filing value
                "'wrong', 100, 90, null, 'R4', 'L', 'headline', null",  # a value verdict needs the accession
                "'right', 100, 100, 'bad', 'R4', 'L', 'headline', null",
                "'right', 100, 100, %(acc)s, 'R4', ' ', 'headline', null",  # and a face label
                "'right', 100, 100, %(acc)s, 'R4', 'L', 'all_cells', null"):  # an all_cells row needs its hash  # fmt: skip
        with pytest.raises(psycopg.errors.CheckViolation):
            with db.transaction():
                db.execute("set local scrooner.writer = 'verifier'")
                db.execute(
                    "insert into analytics.verifier_check (company_id, data_point_name, period_grain, period_start,"
                    " period_end, verdict, shown_value, filing_value, accession, locator, face_label, draw_kind,"
                    " cells_hash, draw_id, verifier_session)"
                    f" values (%(cid)s, 'x', 'FY', '2025-01-01', '2025-12-31', {bad}, 'd', 'v')",
                    {"cid": cid, "acc": ACC})  # fmt: skip
    db.rollback()
    other = _one(
        db,
        "insert into core.company (cik, company_name) values ('0000000556', 'NOROW') returning id",
    )
    db.commit()
    assert pr.promote(db, [other], apply=True, as_of=date(2026, 11, 9), now=NOW) == []
    assert (
        _one(
            db,
            "select count(*) from analytics.company_certification where company_id = %s",
            (other,),
        )
        == 0
    )
