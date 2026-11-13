"""A component sum is judged as a sum against the filing that prints every part (common/authority.
latest_complete_filing, the function the mapper takes its parts with), never part against total.

MSFT sga_expense FY2016/FY2017: G&A kept its original copy (identical values in later 10-Ks), S&M was restated in
a later 10-K; the mapper reads both parts from that later 10-K (the newest filing printing every part) and the
proof flagged DISAGREE 'shown_is_not_the_authoritative_copy' because G&A's authoritative copy sat in another
filing and its value differs from the SUM."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import psycopg
import pytest
from scrooner_pipeline.common.authority import latest_complete_filing
from scrooner_pipeline.mapper.company_tag_map import Fact, MapRow, _one_filing_parts
from scrooner_pipeline.proof.shown import component_sum_authority, load_shown

from tests.unit.test_cell_proof_claims_db import ADSH, FY_END, _world

LATER = "0000000031-27-000001"


def test_latest_complete_filing_picks_the_newest_filing_printing_every_part():
    a = {"f16": date(2016, 7, 28), "f17": date(2017, 8, 2), "f18": date(2018, 8, 3)}
    b = {"f18": date(2018, 8, 3)}  # S&M only has the restated print
    assert latest_complete_filing([a, b]) == "f18"
    assert latest_complete_filing([a, {}]) is None
    assert latest_complete_filing([]) is None
    # tie on filing date: the higher key
    assert (
        latest_complete_filing([{"a": date(2020, 1, 1), "b": date(2020, 1, 1)}]) == "b"
    )


def test_component_sum_authority_is_the_sum_of_the_latest_complete_filing():
    copies = [
        ("f16", Decimal(4563), "GA"),
        ("f18", Decimal(4563), "GA"),
        ("f16", Decimal(14697), "SM"),
        ("f18", Decimal(14635), "SM"),
    ]
    filed = {"f16": date(2016, 7, 28), "f18": date(2018, 8, 3)}
    got = component_sum_authority(copies, ((1, "GA"), (1, "SM")), filed)
    assert got == ("f18", Decimal(19198))
    # a part never printed together with the other: no sum authority
    assert component_sum_authority(copies[:2], ((1, "GA"), (1, "SM")), filed) is None


def test_mapper_picks_the_filing_the_authority_picks():
    def fact(fid, acc, filed, value):
        return Fact(Decimal(value), fid, date(2016, 6, 30), False, fid, acc, filed)

    def row(tag):
        return MapRow(
            "us-gaap", tag, "IS", "component", None, 1, 1, date(2015, 1, 1), None
        )

    ga_new = fact(18, "f18", date(2018, 8, 3), 4563)
    ga_old = fact(16, "f16", date(2016, 7, 28), 4563)
    sm_new = fact(18, "f18", date(2018, 8, 3), 14635)
    vint = {
        ("us-gaap", "GA"): {1: [ga_new, ga_old]},
        ("us-gaap", "SM"): {1: [sm_new]},
    }
    got = _one_filing_parts([(row("GA"), ga_old), (row("SM"), sm_new)], vint, 1)
    assert got is not None and {f.accession for _, f in got} == {"f18"}


@pytest.mark.integration
def test_component_sum_from_the_restating_filing_does_not_disagree(
    isolated_database_url,
):
    case = dict(
        name="sga_expense",
        stmt="IS",
        rows=[
            ("component", "IS", "SellingAndMarketingExpense", 1),
            ("component", "IS", "GeneralAndAdministrativeExpense", 1),
        ],
        facts=[
            ("SellingAndMarketingExpense", "6000000000"),
            ("GeneralAndAdministrativeExpense", "4000000000"),
        ],
        kind="duration",
    )
    with psycopg.connect(isolated_database_url) as conn:
        cid = _world(conn, "0000000960", case, "9900000000")
        pid = conn.execute(
            "select id from core.period where company_id=%s and end_date=%s and start_date=%s",
            (cid, FY_END, date(2024, 1, 1)),
        ).fetchone()[0]
        for prio, tag in enumerate(
            ("SellingAndMarketingExpense", "GeneralAndAdministrativeExpense"), 1
        ):
            conn.execute(
                "insert into analytics.concept_mapping (canonical_concept_id, concept_id, priority, confidence) "
                "select cc.id, c.id, %s, 'approved' from analytics.canonical_concept cc, core.concept c "
                "where cc.name='sga_expense' and c.tag=%s",
                (prio, tag),
            )
        # the original 10-K keeps G&A authoritative; S&M was restated in a 10-K two years later
        lf = conn.execute(
            "insert into core.filing (company_id, accession_number, form, filing_date, period_of_report, is_amendment) "
            "values (%s,%s,'10-K','2027-02-20','2026-12-31',false) returning id",
            (cid, LATER),
        ).fetchone()[0]
        new_ids = []
        for tag, value, auth in (
            ("SellingAndMarketingExpense", "5900000000", True),
            ("GeneralAndAdministrativeExpense", "4000000000", False),
        ):
            new_ids.append(
                conn.execute(
                    "insert into core.fact (company_id, concept_id, unit_id, period_id, filing_id, value, "
                    "is_authoritative, raw_object_id) select %s, c.id, u.id, %s, %s, %s, %s, "
                    "(select max(id) from raw.sec_companyfacts) from core.concept c, core.unit u "
                    "where c.tag=%s and u.unit_name='usd' returning id",
                    (cid, pid, lf, value, auth, tag),
                ).fetchone()[0]
            )
        conn.execute(
            "update core.fact set is_authoritative = false from core.concept c where c.id = core.fact.concept_id "
            "and core.fact.company_id=%s and core.fact.filing_id <> %s and c.tag='SellingAndMarketingExpense'",
            (cid, lf),
        )
        conn.execute(
            "update analytics.canonical_fact set value=9900000000, source_fact_ids=%s where company_id=%s",
            (new_ids, cid),
        )
        conn.commit()
        cells = [
            c
            for c in load_shown(conn, cid, floor=date(2015, 1, 1))
            if c.data_point_name == "sga_expense"
        ]
    assert len(cells) == 1
    assert cells[0].accession == LATER and ADSH != LATER
    assert cells[0].authoritative_disagrees is None, cells[0].authoritative_disagrees
    assert cells[0].copies_disagree is None
