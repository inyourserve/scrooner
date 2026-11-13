"""Per-filing tag era (MSFT revenue vintage), proof authority across tags (JNJ cash), the claim searched on every
statement (S16) and stale verdicts of unserved cells (NFLX total_debt). Pure except the DB test."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import psycopg
import pytest
from scrooner_pipeline.common.authority import latest_eligible
from scrooner_pipeline.mapper.company_tag_map import Fact, MapRow, build_cells
from scrooner_pipeline.proof import prove as pv
from scrooner_pipeline.proof.fsn import FilingStructure, NumValue, PreLine
from scrooner_pipeline.proof.runner import purge_unserved, write_proofs
from scrooner_pipeline.proof.shown import claim_for, era_tag_copies

D = date
REV = 1
INFO = {REV: ("revenue_sanity_resolved", "income_statement")}
FY16_END = D(2016, 6, 30)
OLD, NEW = "SalesRevenueNet", "RevenueFromContractWithCustomerExcludingAssessedTax"


def _rows():
    return [
        MapRow(
            "us-gaap",
            OLD,
            "IS",
            "concept",
            REV,
            None,
            1,
            D(2015, 3, 31),
            D(2017, 6, 30),
        ),
        MapRow("us-gaap", NEW, "IS", "concept", REV, None, 1, D(2017, 7, 1), None),
    ]


def _fact(value, fid, filing, acc, filed, por):
    return Fact(Decimal(value), fid, FY16_END, False, filing, acc, filed, por=por)


def _facts(new_por):
    return {
        ("us-gaap", OLD): {
            7: _fact("85320", 1, 10, "A-17", D(2017, 8, 3), D(2017, 6, 30))
        },
        ("us-gaap", NEW): {7: _fact("91154", 2, 11, "A-18", D(2018, 8, 3), new_por)},
    }


PERIODS = {7: (D(2015, 7, 1), FY16_END, "duration")}


def test_mapper_takes_the_latest_filings_print_under_the_tag_its_own_era_uses():
    cells, _ = build_cells(_rows(), _facts(D(2018, 6, 30)), INFO, {}, {}, PERIODS)
    assert [(c["value"], c["source_fact_ids"]) for c in cells] == [
        (Decimal("91154"), [2])
    ]


def test_a_filing_whose_own_period_is_outside_the_tag_era_is_not_a_candidate():
    # the FY2018 10-K's period (2018) is outside the NEW row if the new row started in 2019
    rows = [
        _rows()[0],
        MapRow("us-gaap", NEW, "IS", "concept", REV, None, 1, D(2019, 7, 1), None),
    ]
    cells, _ = build_cells(rows, _facts(D(2018, 6, 30)), INFO, {}, {}, PERIODS)
    assert [c["value"] for c in cells] == [Decimal("85320")]
    cells, _ = build_cells(
        _rows(), _facts(None), INFO, {}, {}, PERIODS
    )  # unknown period: only the fact's own era
    assert [c["value"] for c in cells] == [Decimal("85320")]


def test_claim_for_follows_the_filing_era_and_keeps_other_statements():
    rows = [
        (1, "concept", "IS", OLD, "x", None, 1, D(2015, 3, 31), D(2017, 6, 30)),
        (2, "concept", "IS", NEW, "x", None, 1, D(2017, 7, 1), None),
        (3, "concept", "CF", "CfTag", "x", None, 1, D(2015, 1, 1), None),
    ]
    assert claim_for(rows, "x", FY16_END).tags == (OLD,)
    c = claim_for(rows, "x", FY16_END, D(2018, 6, 30))
    assert c.tags == (NEW, OLD) and c.alts == (("CF", ("CfTag",), 1),)


def test_era_tag_copies_make_the_later_other_tag_filing_the_authority():
    rows = [
        (1, "concept", "IS", OLD, REVNAME, None, 1, D(2015, 3, 31), D(2017, 6, 30)),
        (2, "concept", "IS", NEW, REVNAME, None, 1, D(2017, 7, 1), None),
    ]
    copies = [("A-17", Decimal("85320"), OLD), ("A-18", Decimal("91154"), NEW)]
    por = {"A-17": D(2017, 6, 30), "A-18": D(2018, 6, 30)}
    got = era_tag_copies(copies, rows, REVNAME, (OLD,), por)
    assert got == [("A-18", Decimal("91154"), NEW)]
    assert era_tag_copies(copies, rows, REVNAME, (OLD,), {"A-18": D(2016, 6, 30)}) == []
    filed = {"A-17": D(2017, 8, 3), "A-18": D(2018, 8, 3)}
    assert latest_eligible(filed) == "A-18"
    assert latest_eligible({"B": D(2018, 1, 1), "A": D(2018, 1, 1)}) == "A"


REVNAME = "revenue_sanity_resolved"


def _structure(tag, stmt, value="34000000"):
    s = FilingStructure(
        "0000045810-15-000036", "0000045810", "10-K", D(2015, 3, 1), D(2015, 1, 31)
    )
    s.pre.append(PreLine(8, 1, stmt, tag, "us-gaap/2015", tag, False))
    s.num[(tag, D(2015, 1, 31), 4)].append(
        NumValue(
            tag, "us-gaap/2015", D(2015, 1, 31), 4, "USD/shares", Decimal("0.34"), 2
        )
    )
    return s


def _dps(claim):
    return pv.Shown(
        1,
        "dividends_per_share_resolved",
        "FY",
        D(2014, 1, 27),
        D(2015, 1, 25),
        Decimal("0.34"),
        ("CommonStockDividendsPerShareDeclared",),
        "0000045810-15-000036",
        (1,),
        False,
        6,
        claim=claim,
    )


def test_the_claim_is_searched_on_every_statement_not_only_the_latest_rows():
    tag = "CommonStockDividendsPerShareDeclared"
    s = _structure(tag, "EQ")
    claimed_is = pv.Claim("concept", "IS", tags=(tag,))
    moved = pv.printed_statement_claim(_dps(claimed_is), s)
    assert moved is not None and moved.stmt == "EQ" and moved.tags == (tag,)
    # an alternate statement the company's own rows name wins before the any-statement search
    alt = pv.Claim("concept", "IS", tags=("Other",), alts=(("EQ", (tag,), 1),))
    assert pv.printed_statement_claim(_dps(alt), s).stmt == "EQ"
    # the claimed statement prints the line: untouched; no face statement prints it: untouched
    assert (
        pv.printed_statement_claim(_dps(pv.Claim("concept", "EQ", tags=(tag,))), s)
        is None
    )
    assert (
        pv.printed_statement_claim(_dps(pv.Claim("concept", "IS", tags=("Nope",))), s)
        is None
    )
    p = pv.prove_cell(_dps(claimed_is), s, "q")
    assert p.verdict == pv.PROVEN and p.fsn_stmt == "EQ"


@pytest.mark.integration
def test_a_proven_verdict_of_a_cell_no_longer_served_is_deleted(isolated_database_url):
    with psycopg.connect(isolated_database_url) as conn:
        cid = conn.execute(
            "insert into core.company (cik, company_name) values ('0000000077', 'T') returning id"
        ).fetchone()[0]
        conn.commit()

        def proof(name, verdict, end=D(2015, 12, 31)):
            s = pv.Shown(cid, name, "I", end, end, Decimal("1"), ("t",), "A-1", (1,))
            return pv.Proof(
                shown=s,
                verdict=verdict,
                position_value=Decimal("1") if verdict == "PROVEN" else None,
                position_is_expected_line=True if verdict == "PROVEN" else None,
                reason_code="x" if verdict in ("DISAGREE", "NOT_PRESENTED") else None,
            )

        a = proof("total_debt_resolved", "PROVEN")
        b = proof("total_assets_resolved", "PROVEN")
        c = proof("cfo_resolved", "DISAGREE")
        d = proof("ppe_net_resolved", "NOT_PRESENTED")
        e = proof("inventory", "UNCHECKED")
        write_proofs(conn, [a, b, c, d, e])
        # only total_assets is still served
        assert purge_unserved(conn, cid, [b]) == 2
        conn.commit()
        left = sorted(
            r[0]
            for r in conn.execute(
                "select data_point_name from analytics.cell_proof where company_id=%s",
                (cid,),
            ).fetchall()
        )
        assert left == ["cfo_resolved", "ppe_net_resolved", "total_assets_resolved"]


@pytest.mark.integration
def test_another_tags_authoritative_flag_is_not_the_cells_authority(
    isolated_database_url,
):
    """JNJ cash 2022: tag U's FY2022 copy is authoritative for U; the cell's own tag T has a later authoritative copy.
    The differing earlier T copy is history, not 'the authoritative copy'."""
    from tests.unit.test_cell_proof_claims_db import CASES, _world
    from tests.unit.test_cell_proof_restated_db import _add_copy

    case = CASES["share_count"]
    tag = case["facts"][0][0]
    other = "OtherCashTag"
    with psycopg.connect(isolated_database_url) as conn:
        cid = _world(conn, "0000000088", case, case["shown"])
        conn.execute(
            "insert into core.concept (taxonomy, tag) values ('us-gaap', %s) on conflict do nothing",
            (other,),
        )
        conn.execute(
            "insert into analytics.concept_mapping (canonical_concept_id, concept_id, priority, confidence) "
            "select cc.id, c.id, 2, 'approved' from analytics.canonical_concept cc, core.concept c "
            "where cc.name=%s and c.tag=%s",
            (case["name"], other),
        )
        conn.execute(
            "insert into analytics.concept_mapping (canonical_concept_id, concept_id, priority, confidence) "
            "select cc.id, c.id, 1, 'approved' from analytics.canonical_concept cc, core.concept c "
            "where cc.name=%s and c.tag=%s and not exists (select 1 from analytics.concept_mapping m "
            "where m.canonical_concept_id=cc.id and m.concept_id=c.id)",
            (case["name"], tag),
        )
        conn.commit()
        _add_copy(
            conn, cid, tag, "14000000000", "0000000031-24-000001", False
        )  # earlier T copy, not authoritative
        # U's own authoritative copy, in the SAME earlier filing as the differing T copy
        conn.execute(
            "insert into core.fact (company_id, concept_id, unit_id, period_id, filing_id, value, is_authoritative, "
            "raw_object_id) select %s, c.id, u.id, p.id, fl.id, 14000000000, true, "
            "(select max(id) from raw.sec_companyfacts) from core.concept c, core.unit u, core.filing fl, core.period p "
            "where c.tag=%s and u.unit_name='usd' and fl.accession_number='0000000031-24-000001' "
            "and p.company_id=%s and p.end_date=%s and p.start_date=%s",
            (cid, other, cid, date(2024, 12, 31), date(2024, 1, 1)),
        )
        conn.commit()
        from datetime import date as _d

        from scrooner_pipeline.proof.shown import load_shown

        cells = [
            c
            for c in load_shown(conn, cid, floor=_d(2015, 1, 1))
            if c.data_point_name == case["name"]
        ]
    assert len(cells) == 1
    assert cells[0].copies_disagree  # the earlier T copy is restated history
    assert cells[0].authoritative_disagrees is None
