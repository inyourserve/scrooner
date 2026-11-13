"""Statement coherence (Dhairya 2026-11-13, tag expert identity triage): a copy is face-eligible only if that filing's
FACE statement prints the tag for the column (not a summary table or note); every served member of one statement and
period comes from the ONE latest face-eligible filing that prints the column; NOTE-claimed tags keep their own rule.
Real SQL (CI: Postgres 16). Fixture filings exist in core (the API copy) and in fsn (what the face prints)."""

from __future__ import annotations

from datetime import date

import psycopg
import pytest

from scrooner_pipeline.common.authority import (
    FaceIndex,
    load_face_indexes,
    statement_filing,
)
from scrooner_pipeline.mapper.company_tag_map import _load_fact_vintages
from scrooner_pipeline.normalizer import conflict_latest_filed as clf


@pytest.fixture(autouse=True)
def _flag_on(monkeypatch):
    monkeypatch.setenv("SCROONER_RULES_ENABLED", "company_tag_map.select@1")


class Shape:
    """One company with a balance-sheet instant period; filings added with the tags their FACE prints."""

    def __init__(self, conn, cik, end="2015-03-31"):
        self.conn, self.end = conn, end
        self.cid = conn.execute(
            "insert into core.company (cik, company_name) values (%s,'T') returning id",
            (cik,),
        ).fetchone()[0]
        conn.execute(
            "insert into core.unit (unit_name) values ('usd') on conflict do nothing"
        )
        self.uid = conn.execute(
            "select id from core.unit where unit_name='usd'"
        ).fetchone()[0]
        self.pid = conn.execute(
            "insert into core.period (company_id, start_date, end_date, period_type) values (%s,%s,%s,'instant') returning id",
            (self.cid, end, end),
        ).fetchone()[0]
        self.rid = conn.execute(
            "insert into raw.sec_companyfacts (cik, source_url, sha256, storage_path, http_status) values (%s,'u','h',%s,200) returning id",
            (cik, f"raw/{cik}"),
        ).fetchone()[0]
        self.cik, self.facts, self.core_filing = cik, {}, {}

    def _concept(self, tag):
        self.conn.execute(
            "insert into core.concept (taxonomy, tag) values ('us-gaap', %s) on conflict do nothing",
            (tag,),
        )
        return self.conn.execute(
            "select id from core.concept where taxonomy='us-gaap' and tag=%s", (tag,)
        ).fetchone()[0]

    def filing(self, accn, form, filed, por, face_columns=None):
        """face_columns: {tag: ddate printed on the face} (None = the filing is not in the FSN store)."""
        c = self.conn
        self.core_filing[accn] = c.execute(
            "insert into core.filing (company_id, accession_number, form, filing_date, period_of_report, is_amendment) "
            "values (%s,%s,%s,%s,%s,false) returning id",
            (self.cid, accn, form, filed, por),
        ).fetchone()[0]
        if face_columns is None:
            return
        ff = c.execute(
            "insert into fsn.filing (accession, cik, form, fsn_set, company_id, period, filed, accepted) "
            "values (%s,%s,%s,'t',%s,%s,%s,%s) returning id",
            (accn, self.cik, form, self.cid, por, filed, f"{filed} 10:00+00"),
        ).fetchone()[0]
        for i, (tag, ddate) in enumerate(face_columns.items(), 1):
            tid = c.execute(
                "insert into fsn.tag (tag, version, custom) values (%s,'us-gaap/2015',false) "
                "on conflict (tag, version) do update set tag=excluded.tag returning id",
                (tag,),
            ).fetchone()[0]
            c.execute(
                "insert into fsn.line (filing_id, report, line, stmt, tag_id) values (%s,2,%s,'BS',%s)",
                (ff, i, tid),
            )
            c.execute(
                "insert into fsn.value (filing_id, company_id, tag_id, ddate, qtrs, uom, dim_id, iprx, coreg, value) "
                "values (%s,%s,%s,%s,0,'USD',0,0,'',1)",
                (ff, self.cid, tid, ddate),
            )

    def fact(self, accn, tag, value, auth=False):
        kid = self._concept(tag)
        self.facts[(accn, tag)] = self.conn.execute(
            "insert into core.fact (company_id, concept_id, unit_id, period_id, filing_id, value, is_authoritative, raw_object_id) "
            "values (%s,%s,%s,%s,%s,%s,%s,%s) returning id",
            (
                self.cid,
                kid,
                self.uid,
                self.pid,
                self.core_filing[accn],
                value,
                auth,
                self.rid,
            ),
        ).fetchone()[0]

    def auth(self, tag):
        return sorted(
            a
            for (a, t), i in self.facts.items()
            if t == tag
            and self.conn.execute(
                "select is_authoritative from core.fact where id=%s", (i,)
            ).fetchone()[0]
        )

    def run(self):
        self.conn.commit()
        plan = clf.plan_tag_map_promotions(self.conn, [self.cid])
        clf.apply_tag_map_promotions(self.conn, plan)
        self.conn.commit()
        return plan


@pytest.mark.integration
def test_jpm_shape_summary_table_copy_in_a_later_10q_is_not_eligible(
    isolated_database_url,
):
    """JPM total assets 2015-03-31: the original 10-Q prints it on the face; the next year's 10-Q carries the same
    date only in a summary table (its face prints 2016-03-31). The summary copy was authoritative and the other
    members came from the original: it is demoted and the face copy wins."""
    with psycopg.connect(isolated_database_url) as conn:
        s = Shape(conn, "0000000201")
        s.filing(
            "A15",
            "10-Q",
            "2015-05-05",
            "2015-03-31",
            {"Assets": "2015-03-31", "Liabilities": "2015-03-31"},
        )
        s.filing(
            "A16",
            "10-Q",
            "2016-05-05",
            "2016-03-31",
            {"Assets": "2016-03-31", "Liabilities": "2016-03-31"},
        )
        s.fact("A15", "Assets", 2577148, auth=False)
        s.fact(
            "A16", "Assets", 2576619, auth=True
        )  # summary-table copy, within the 400-day window
        s.run()
        assert s.auth("Assets") == ["A15"]
        idx = load_face_indexes(conn, [s.cid])[s.cid]
        d = date(2015, 3, 31)
        assert (
            idx.eligible("10-Q", date(2016, 3, 31), "A16", "Assets", d, d, "instant")
            is False
        )
        assert idx.eligible("10-Q", d, "A15", "Assets", d, d, "instant")
        # the mapper's loader never serves the summary-table copy even if it were flagged authoritative
        conn.execute(
            "update core.fact set is_authoritative = (filing_id = %s)",
            (s.core_filing["A16"],),
        )
        conn.commit()
        got = _load_fact_vintages(
            conn, s.cid, {("us-gaap", "Assets")}, latest_only=True, face=idx
        )
        assert not got.get(("us-gaap", "Assets"))


@pytest.mark.integration
def test_restated_member_beside_original_members_all_come_from_the_latest_printing_filing(
    isolated_database_url,
):
    """Assets, Liabilities, equity on the same balance sheet and period: the FY2016 10-K restates two members
    (ASC 606 style); every restated member must be that filing's copy, never one restated beside an original."""
    with psycopg.connect(isolated_database_url) as conn:
        s = Shape(conn, "0000000202", end="2015-12-31")
        cols = {
            t: "2015-12-31" for t in ("Assets", "Liabilities", "StockholdersEquity")
        }
        s.filing("A15", "10-K", "2016-02-20", "2015-12-31", cols)
        s.filing(
            "A16", "10-K", "2017-02-20", "2016-12-31", dict(cols)
        )  # prints 2015-12-31 as the comparative column
        for tag, v15, v16 in (
            ("Assets", 1000, 1000),
            ("Liabilities", 600, 590),
            ("StockholdersEquity", 400, 410),
        ):
            s.fact(
                "A15", tag, v15, auth=True
            )  # an earlier pick left the original authoritative
            s.fact("A16", tag, v16, auth=False)
        s.run()
        assert s.auth("Liabilities") == ["A16"] and s.auth("StockholdersEquity") == [
            "A16"
        ]
        idx = load_face_indexes(conn, [s.cid])[s.cid]
        d = date(2015, 12, 31)
        assert idx.statement_filing("BS", d, d, "instant") == "A16"
        assert statement_filing(conn, s.cid, "BS", d, d, "instant") == "A16"


@pytest.mark.integration
def test_note_claimed_tag_keeps_its_own_rule_without_a_face_print(
    isolated_database_url,
):
    """A tag the map claims as NOTE is never judged on the face: its later copy stays eligible."""
    with psycopg.connect(isolated_database_url) as conn:
        s = Shape(conn, "0000000203")
        s.filing("A15", "10-Q", "2015-05-05", "2015-03-31", {"Assets": "2015-03-31"})
        s.filing("A16", "10-Q", "2016-05-05", "2016-03-31", {"Assets": "2016-03-31"})
        s.fact("A15", "LeaseNote", 7, auth=False)
        s.fact(
            "A16", "LeaseNote", 9, auth=True
        )  # printed in a note, in no face statement
        cc = conn.execute(
            "insert into analytics.canonical_concept (name, statement, combination_mode) values ('lease_note_t','balance_sheet','first_match') returning id"
        ).fetchone()[0]
        conn.execute(
            "insert into analytics.company_tag_map (company_id, taxonomy, tag, stmt, decision, canonical_concept_id, era_from, decided_by, rule_id) "
            "values (%s,'us-gaap','LeaseNote','UN','concept',%s,'2015-01-01','t','tm.r@1')",
            (s.cid, cc),
        )
        s.run()
        assert s.auth("LeaseNote") == [
            "A16"
        ]  # the note rule: not demoted for lacking a face line
        idx = load_face_indexes(conn, [s.cid])[s.cid]
        d = date(2015, 3, 31)
        assert "LeaseNote" in idx.note_tags
        assert idx.eligible(
            "10-Q", date(2016, 3, 31), "A16", "LeaseNote", d, d, "instant"
        )


def test_face_index_orders_and_ties_without_a_database():
    ix = FaceIndex(
        filings={
            "B": ("10-K", date(2016, 12, 31), (date(2017, 2, 1), 1.0)),
            "A": ("10-K", date(2016, 12, 31), (date(2017, 2, 1), 1.0)),
            "OLD": ("10-K", date(2015, 12, 31), (date(2016, 2, 1), 1.0)),
        },
        prints={
            (a, "Assets"): [("BS", date(2015, 12, 31), 0)] for a in ("A", "B", "OLD")
        },
    )
    end = date(2015, 12, 31)
    assert (
        ix.statement_filing("BS", None, end, "instant") == "A"
    )  # same filed and accepted: the lower accession
    assert ix.statement_filing("IS", None, end, "instant") is None
    assert not ix.eligible(
        "10-K", date(2016, 12, 31), "A", "Other", None, end, "instant"
    )  # judged, not printed
    assert ix.eligible(
        "10-K", date(2016, 12, 31), "UNKNOWN", "Other", None, end, "instant"
    )  # not in the FSN store
