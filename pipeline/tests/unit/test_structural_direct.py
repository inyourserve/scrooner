"""Structural resolver rows served directly (ruling 2026-11-14): the value is read from the stored facts of the
resolver row's own accession and column, the filing is chosen by authority v2, hand fix rows win, and the resolver's
CSV value is only a cross-check. DB-backed (CI: Postgres 16); each assertion is mutation-checked."""

from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal

import psycopg
import pytest

from scrooner_pipeline.mapper import company_tag_map as ctm
from scrooner_pipeline.mapper import structural_direct as sd

CIK = "0000000301"
END = date(2018, 12, 31)
HEAD = "cik,ticker,data_point,period_end,grain,decision,nodes,value,accession,column,calc_check,flags,resolver_version\n"


def _one(conn, sql, *args):
    return conn.execute(sql, args).fetchone()[0]


def _row(
    acc,
    value,
    tag="InvestmentIncomeNet",
    node=None,
    decision="mapped",
    dp="sd_inc",
    end=END,
    check="calc A: ok",
    tags=None,
    grain="FY",
):
    nodes = (
        tags or f"{tag}={node if node is not None else value} [NOTE] | why: note fact"
    )
    return f'{CIK},TST,{dp},{end},{grain},{decision},"{nodes}",{value},{acc},own,{check},core,r.1\n'


def _csv(tmp_path, *rows, monkeypatch):
    p = tmp_path / "resolver-all110-2026-11-14.csv"
    p.write_text(HEAD + "".join(rows))
    monkeypatch.setenv(sd.ENV_PATH, str(p))
    sd._claims_by_cik.cache_clear()
    return p


class W:
    """A scratch company with one yearly period, filings and stored facts."""

    def __init__(self, conn):
        self.conn = conn
        self.co = _one(
            conn,
            "insert into core.company (cik, company_name) values (%s,'t') returning id",
            CIK,
        )
        self.cc = {
            n: _one(
                conn,
                "insert into analytics.canonical_concept (name, statement, combination_mode) values (%s,'income_statement','first_match') returning id",
                n,
            )
            for n in ("sd_inc", "sd_da")
        }
        self.unit = _one(
            conn, "insert into core.unit (unit_name) values ('USD') returning id"
        )
        self.raw = _one(
            conn,
            "insert into raw.sec_companyfacts (cik, source_url, sha256, storage_path, http_status) values (%s,'u','s','p',200) returning id",
            CIK,
        )
        self.pid = _one(
            conn,
            "insert into core.period (company_id, start_date, end_date, period_type) values (%s,%s,%s,'duration') returning id",
            self.co,
            date(2018, 1, 1),
            END,
        )
        self.tags: dict[str, int] = {}
        self.fil: dict[str, int] = {}

    def filing(self, acc, filed, por, form="10-K"):
        self.fil[acc] = _one(
            self.conn,
            "insert into core.filing (company_id, accession_number, form, filing_date, period_of_report) values (%s,%s,%s,%s,%s) returning id",
            self.co,
            acc,
            form,
            filed,
            por,
        )

    def core_fact(self, acc, tag, value, auth=False):
        if tag not in self.tags:
            self.tags[tag] = _one(
                self.conn,
                "insert into core.concept (taxonomy, tag) values ('us-gaap', %s) returning id",
                tag,
            )
        return _one(
            self.conn,
            "insert into core.fact (company_id, concept_id, unit_id, period_id, filing_id, value, is_authoritative, raw_object_id) values (%s,%s,%s,%s,%s,%s,%s,%s) returning id",
            self.co,
            self.tags[tag],
            self.unit,
            self.pid,
            self.fil[acc],
            Decimal(value),
            auth,
            self.raw,
        )

    def fsn_fact(self, acc, tag, value, custom=True):
        fid = self.conn.execute(
            "select id from fsn.filing where accession = %s", (acc,)
        ).fetchone()
        if fid is None:
            fid = (
                _one(
                    self.conn,
                    "insert into fsn.filing (accession, cik, form, fsn_set, accepted, period) values (%s,%s,'10-K','t',%s,%s) returning id",
                    acc,
                    CIK,
                    datetime(2019, 2, 1, tzinfo=timezone.utc),
                    END,
                ),
            )
        tid = _one(
            self.conn,
            "insert into fsn.tag (tag, version, custom) values (%s,'2018',%s) returning id",
            tag,
            custom,
        )
        return _one(
            self.conn,
            "insert into fsn.value (filing_id, company_id, tag_id, ddate, qtrs, uom, dim_id, iprx, coreg, value) values (%s,%s,%s,%s,4,'USD',0,0,'',%s) returning id",
            fid[0],
            self.co,
            tid,
            END,
            Decimal(value),
        )

    def info(self):
        return {i: (n, "income_statement") for n, i in self.cc.items()}

    def periods(self):
        s, e = self.conn.execute(
            "select start_date, end_date from core.period where id = %s", (self.pid,)
        ).fetchone()
        return {self.pid: (s, e, "duration")}

    def cells(self, rows=()):
        return sd.direct_cells(
            self.conn, self.co, CIK, list(rows), self.periods(), self.info()
        )


ACC1, ACC2 = "0000000301-19-000001", "0000000301-20-000002"


@pytest.mark.integration
def test_note_fact_serves_with_no_map_row_and_lineage_is_the_filing(
    isolated_database_url, tmp_path, monkeypatch
):
    """The MSFT InvestmentIncomeNet shape: a note fact no face line carries, no tag-era map row at all."""
    with psycopg.connect(isolated_database_url) as conn:
        w = W(conn)
        w.filing(ACC1, date(2019, 2, 1), END)
        fid = w.core_fact(ACC1, "InvestmentIncomeNet", "1234")
        _csv(tmp_path, _row(ACC1, "1234"), monkeypatch=monkeypatch)
        cells, st = w.cells()
        (c,) = cells
        assert (c["canonical_concept_id"], c["period_id"], c["value"]) == (
            w.cc["sd_inc"],
            w.pid,
            Decimal(1234),
        )
        assert (
            c["source_fact_ids"] == [fid]
            and c["value_source"] == "sec_api"
            and c["_accession"] == ACC1
        )
        assert (
            ACC1 in c["serve_note"]
            and "InvestmentIncomeNet=1234" in c["serve_note"]
            and "calc A: ok" in c["serve_note"]
        )
        # through the mapper: the tag-era path has no row and serves nothing; the direct path fills the cell
        stats = ctm.resolve_for_company(conn, w.co, set(), w.info(), commit=False)
        assert [(x["canonical_concept_id"], x["value"]) for x in stats["cells"]] == [
            (w.cc["sd_inc"], Decimal(1234))
        ]
        assert stats["structural_direct"]["served"] == 1


@pytest.mark.integration
def test_custom_tag_serves_from_the_filings_own_xbrl(
    isolated_database_url, tmp_path, monkeypatch
):
    with psycopg.connect(isolated_database_url) as conn:
        w = W(conn)
        w.filing(ACC1, date(2019, 2, 1), END)
        vid = w.fsn_fact(ACC1, "DepreciationAmortizationAndOther", "777")
        _csv(
            tmp_path,
            _row(ACC1, "777", tag="msft:DepreciationAmortizationAndOther", dp="sd_da"),
            monkeypatch=monkeypatch,
        )
        (c,), _ = w.cells()
        assert (
            c["value"],
            c["value_source"],
            c["source_value_ids"],
            c["source_fact_ids"],
        ) == (Decimal(777), "fsn_xbrl", [vid], [])


@pytest.mark.integration
def test_authority_picks_the_latest_eligible_filing_across_resolver_rows(
    isolated_database_url, tmp_path, monkeypatch
):
    with psycopg.connect(isolated_database_url) as conn:
        w = W(conn)
        w.filing(ACC1, date(2019, 2, 1), END)
        w.filing(
            ACC2, date(2020, 2, 1), date(2019, 12, 31)
        )  # the next 10-K prints the column too (restated)
        w.core_fact(ACC1, "InvestmentIncomeNet", "100")
        w.core_fact(ACC2, "InvestmentIncomeNet", "110")
        _csv(tmp_path, _row(ACC1, "100"), _row(ACC2, "110"), monkeypatch=monkeypatch)
        (c,), _ = w.cells()
        assert (c["value"], c["_accession"]) == (Decimal(110), ACC2)
        # a later filing that does not print the column (period_of_report 4 years on) is not eligible
        conn.execute(
            "update core.filing set period_of_report = %s where accession_number = %s",
            (date(2022, 12, 31), ACC2),
        )
        (c,), _ = w.cells()
        assert (c["value"], c["_accession"]) == (Decimal(100), ACC1)


@pytest.mark.integration
def test_hand_fix_row_wins_its_cell(isolated_database_url, tmp_path, monkeypatch):
    with psycopg.connect(isolated_database_url) as conn:
        w = W(conn)
        w.filing(ACC1, date(2019, 2, 1), END)
        w.core_fact(ACC1, "InvestmentIncomeNet", "100")
        w.core_fact(ACC1, "Other", "5")
        _csv(
            tmp_path,
            _row(ACC1, "100"),
            _row(ACC1, "5", tag="Other", dp="sd_da"),
            monkeypatch=monkeypatch,
        )
        fix = ctm.MapRow(
            "us-gaap",
            "X",
            "IS",
            "concept",
            w.cc["sd_inc"],
            None,
            1,
            date(2015, 1, 1),
            None,
            rule_id=sd.FIX_RULE_ID,
        )
        cells, st = w.cells([fix])
        assert [c["canonical_concept_id"] for c in cells] == [
            w.cc["sd_da"]
        ]  # only the cell the fix does not cover
        assert st["fix_won"] == 1


@pytest.mark.integration
@pytest.mark.parametrize(
    "row,why",
    [
        (
            _row(ACC1, "999", node="100"),
            "differs from the resolver value",
        ),  # CSV total disagrees with the stored fact
        (
            _row(ACC1, "100", node="999"),
            "differs from the resolver node",
        ),  # a node value disagrees
        (
            _row(ACC1, "100", tag="NoSuchTag"),
            "no stored fact",
        ),  # nothing stored for that accession and column
        (
            _row(ACC1, "100", check="calc A: FAIL"),
            "quarantined",
        ),  # the filing's own calc check failed
    ],
)
def test_value_mismatch_or_missing_fact_rejects_the_claim(
    isolated_database_url, tmp_path, monkeypatch, row, why
):
    with psycopg.connect(isolated_database_url) as conn:
        w = W(conn)
        w.filing(ACC1, date(2019, 2, 1), END)
        w.core_fact(ACC1, "InvestmentIncomeNet", "100")
        _csv(tmp_path, row, monkeypatch=monkeypatch)
        cells, st = w.cells()
        assert cells == [] and why in st["rejected"][0]["why"]


@pytest.mark.integration
def test_component_sum_signs_and_a_stored_fact_of_another_filing_is_never_used(
    isolated_database_url, tmp_path, monkeypatch
):
    with psycopg.connect(isolated_database_url) as conn:
        w = W(conn)
        w.filing(ACC1, date(2019, 2, 1), END)
        w.filing(ACC2, date(2020, 2, 1), date(2019, 12, 31))
        w.core_fact(ACC1, "A", "100")
        w.core_fact(ACC1, "B", "30")
        w.core_fact(
            ACC2, "A", "999"
        )  # the other filing's copy is not the claim's accession
        nodes = "A=100 [R4:1]; B=30 [R4:2] | why: sum"
        _csv(
            tmp_path,
            _row(ACC1, "70", decision="component_sum", tags=nodes),
            monkeypatch=monkeypatch,
        )
        (c,), st = w.cells()
        assert c["value"] == Decimal(70) and c["_accession"] == ACC1


@pytest.mark.integration
def test_fiscal_52_53_week_column_matches_the_fsn_rounded_resolver_date(
    isolated_database_url, tmp_path, monkeypatch
):
    """The resolver prints the FSN month-end date (2018-12-31); the filing's true column ends 2018-12-29."""
    with psycopg.connect(isolated_database_url) as conn:
        w = W(conn)
        conn.execute(
            "update core.period set end_date = %s where id = %s",
            (date(2018, 12, 29), w.pid),
        )
        w.filing(ACC1, date(2019, 2, 1), date(2018, 12, 29))
        w.core_fact(ACC1, "InvestmentIncomeNet", "100")
        _csv(tmp_path, _row(ACC1, "100"), monkeypatch=monkeypatch)
        (c,), _ = w.cells()
        assert (c["period_id"], c["value"]) == (w.pid, Decimal(100))


@pytest.mark.integration
def test_a_tag_era_cell_from_a_strictly_later_filing_is_kept(
    isolated_database_url, tmp_path, monkeypatch
):
    """Authority v2 across the two paths: the resolver row speaks for its own filing; a restated column in a later
    eligible filing (which the tag-era path already chose) is not overwritten by the original filing's value."""
    with psycopg.connect(isolated_database_url) as conn:
        w = W(conn)
        w.filing(ACC1, date(2019, 2, 1), END)
        w.filing(ACC2, date(2020, 2, 1), date(2019, 12, 31))
        w.core_fact(ACC1, "InvestmentIncomeNet", "100")
        _csv(tmp_path, _row(ACC1, "100"), monkeypatch=monkeypatch)
        (d,), _ = w.cells()
        key = {
            "canonical_concept_id": d["canonical_concept_id"],
            "period_id": d["period_id"],
        }
        later = {**key, "value": Decimal(90), "_accession": ACC2}
        cells, stats = [dict(later)], {"held": [], "blanks": []}
        assert sd.apply_direct(conn, cells, stats, [d]) == 0
        assert cells[0]["value"] == Decimal(90) and stats[
            "structural_direct_kept_later_filing"
        ][0]["direct"] == Decimal(100)
        # the same or an earlier filing, or no cell: the resolver cell wins and clears the blank of that key
        same = {**key, "value": Decimal(90), "_accession": ACC1}
        cells, stats = [same], {"held": [], "blanks": [{**key}]}
        assert sd.apply_direct(conn, cells, stats, [d]) == 1
        assert cells[0]["value"] == Decimal(100) and stats["blanks"] == []


@pytest.mark.integration
def test_two_stored_units_resolve_only_by_evidence(
    isolated_database_url, tmp_path, monkeypatch
):
    """EPS-style: one tag, one filing and column, two units. The resolver node value picks the stored value; with no
    node value and no single authoritative copy the claim is rejected, never guessed."""
    with psycopg.connect(isolated_database_url) as conn:
        w = W(conn)
        w.filing(ACC1, date(2019, 2, 1), END)
        w.core_fact(ACC1, "InvestmentIncomeNet", "100")
        u2 = _one(
            conn, "insert into core.unit (unit_name) values ('USD/shares') returning id"
        )
        conn.execute(
            "insert into core.fact (company_id, concept_id, unit_id, period_id, filing_id, value, is_authoritative, raw_object_id) values (%s,%s,%s,%s,%s,%s,false,%s)",
            (
                w.co,
                w.tags["InvestmentIncomeNet"],
                u2,
                w.pid,
                w.fil[ACC1],
                Decimal("5"),
                w.raw,
            ),
        )
        _csv(tmp_path, _row(ACC1, "100"), monkeypatch=monkeypatch)
        (c,), _ = w.cells()
        assert c["value"] == Decimal(100)
        _csv(
            tmp_path,
            _row(ACC1, "100").replace("InvestmentIncomeNet=100", "InvestmentIncomeNet"),
            monkeypatch=monkeypatch,
        )
        cells, st = w.cells()
        assert cells == [] and "two stored values" in st["rejected"][0]["why"]


def test_period_id_disambiguates_stray_instants_by_the_filings_period_of_report():
    """Lowe's shape: the FSN date 2018-01-31 stands for the real year end 2018-02-02 and for a stray instant 2018-02-03
    (a subsequent-event date): no exact end, so the filing's period_of_report picks; without that evidence: None."""
    periods = {
        1: (date(2018, 2, 2), date(2018, 2, 2), "instant"),
        2: (date(2018, 2, 3), date(2018, 2, 3), "instant"),
    }
    jan31 = date(2018, 1, 31)
    assert sd._period_id(periods, jan31, "I") is None
    assert sd._period_id(periods, jan31, "I", frozenset({date(2018, 2, 2)})) == (
        1,
        date(2018, 2, 2),
    )
    assert sd._period_id(periods, date(2018, 2, 3), "I") == (2, date(2018, 2, 3))


@pytest.mark.integration
def test_ambiguous_column_resolves_by_the_stored_fact_of_the_claims_own_filing(
    isolated_database_url, tmp_path, monkeypatch
):
    """Two periods match the rounded date, the filing carries no usable period_of_report: only the real column holds
    the filing's stored fact, the stray period holds none."""
    with psycopg.connect(isolated_database_url) as conn:
        w = W(conn)
        conn.execute(
            "update core.period set end_date = %s where id = %s",
            (date(2018, 12, 29), w.pid),
        )
        stray = _one(
            conn,
            "insert into core.period (company_id, start_date, end_date, period_type) values (%s,%s,%s,'duration') returning id",
            w.co,
            date(2018, 1, 3),
            date(2019, 1, 2),
        )
        w.filing(ACC1, date(2019, 2, 1), None)
        w.core_fact(ACC1, "InvestmentIncomeNet", "100")
        _csv(tmp_path, _row(ACC1, "100"), monkeypatch=monkeypatch)
        periods = {
            pid: (s, e, "duration")
            for pid, s, e in conn.execute(
                "select id, start_date, end_date from core.period where company_id = %s",
                (w.co,),
            ).fetchall()
        }
        assert len(periods) == 2 and stray in periods
        cells, stats = sd.direct_cells(conn, w.co, CIK, [], periods, w.info())
        assert [(c["period_id"], c["value"]) for c in cells] == [(w.pid, Decimal(100))]
        assert stats["rejected"] == []


@pytest.mark.integration
def test_two_periods_with_the_same_end_resolve_by_the_stored_fact_of_the_own_filing(
    isolated_database_url, tmp_path, monkeypatch
):
    """BofA shape: a stray year period with the SAME end and a start one day later holds a few facts of another
    filing only; the claim goes to the period that holds the claim's own filing's fact."""
    with psycopg.connect(isolated_database_url) as conn:
        w = W(conn)
        stray = _one(
            conn,
            "insert into core.period (company_id, start_date, end_date, period_type) values (%s,%s,%s,'duration') returning id",
            w.co,
            date(2018, 1, 2),
            END,
        )
        w.filing(ACC1, date(2019, 2, 1), END)
        w.core_fact(ACC1, "InvestmentIncomeNet", "100")
        _csv(tmp_path, _row(ACC1, "100"), monkeypatch=monkeypatch)
        periods = {
            pid: (s, e, "duration")
            for pid, s, e in conn.execute(
                "select id, start_date, end_date from core.period where company_id = %s",
                (w.co,),
            ).fetchall()
        }
        assert stray in periods and w.pid in periods
        cells, stats = sd.direct_cells(conn, w.co, CIK, [], periods, w.info())
        assert [(c["period_id"], c["value"]) for c in cells] == [(w.pid, Decimal(100))]
        assert stats["rejected"] == []


@pytest.mark.integration
def test_cash_claim_on_a_component_of_the_bs_face_total_is_rejected(
    isolated_database_url, tmp_path, monkeypatch
):
    """AXP shape: the resolver picked CashAndDueFromBanks, the calc child of the BS face 'Total cash and cash
    equivalents'; the cell is not served from it. A cash claim on the total itself is served."""
    with psycopg.connect(isolated_database_url) as conn:
        w = W(conn)
        cc = _one(
            conn,
            "insert into analytics.canonical_concept (name, statement, combination_mode) values ('cash_and_equivalents','balance_sheet','first_match') returning id",
        )
        conn.execute(
            "update core.period set start_date = end_date, period_type = 'instant' where id = %s",
            (w.pid,),
        )
        w.filing(ACC1, date(2019, 2, 1), END)
        w.core_fact(ACC1, "CashAndDueFromBanks", "7118")
        w.core_fact(
            ACC1,
            "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents",
            "46596",
        )
        fid = w.fsn_fact(ACC1, "CashAndDueFromBanks", "7118", custom=False)
        filing = conn.execute(
            "select id from fsn.filing where accession = %s", (ACC1,)
        ).fetchone()[0]
        tid = {
            t: _one(conn, "select id from fsn.tag where tag = %s", t)
            for t in ["CashAndDueFromBanks"]
        }
        parent = _one(
            conn,
            "insert into fsn.tag (tag, version, custom) values ('CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents','2018',false) returning id",
        )
        conn.execute(
            "insert into fsn.line (filing_id, report, line, stmt, tag_id) values (%s,6,13,'BS',%s)",
            (filing, parent),
        )
        conn.execute(
            "insert into fsn.calc_arc (filing_id, grp, arc, parent_tag_id, child_tag_id, weight) values (%s,1,1,%s,%s,1)",
            (filing, parent, tid["CashAndDueFromBanks"]),
        )
        assert fid
        info = {cc: ("cash_and_equivalents", "balance_sheet")}
        periods = {w.pid: (END, END, "instant")}
        rows = [
            _row(
                ACC1,
                "7118",
                tag="CashAndDueFromBanks",
                dp="cash_and_equivalents",
                grain="I",
            ),
        ]
        _csv(tmp_path, *rows, monkeypatch=monkeypatch)
        cells, stats = sd.direct_cells(conn, w.co, CIK, [], periods, info)
        assert cells == []
        assert "component of the BS face total" in stats["rejected"][0]["why"]
        rows = [
            _row(
                ACC1,
                "46596",
                tag="CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents",
                dp="cash_and_equivalents",
                grain="I",
            )
        ]
        _csv(tmp_path, *rows, monkeypatch=monkeypatch)
        cells, stats = sd.direct_cells(conn, w.co, CIK, [], periods, info)
        assert [c["value"] for c in cells] == [Decimal(46596)]
