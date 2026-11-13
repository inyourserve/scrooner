"""R13 end to end on a migrated scratch database: an earlier copy that differs is restated history
unless it is the authoritative copy (core.fact.is_authoritative)."""

from __future__ import annotations

from datetime import date

import psycopg
import pytest
from scrooner_pipeline.proof import prove as pv
from scrooner_pipeline.proof.shown import load_shown

from tests.unit.test_cell_proof_claims_db import (
    ADSH,
    CASES,
    FY_END,
    _structure,
    _world,
)


def _add_copy(conn, cid, tag, value, accession, authoritative):
    """Another periodic filing's copy of the case's FY2024 cell."""
    pid = conn.execute(
        "select id from core.period where company_id=%s and end_date=%s and start_date=%s",
        (cid, FY_END, date(2024, 1, 1)),
    ).fetchone()[0]
    fid = conn.execute(
        "insert into core.filing (company_id, accession_number, form, filing_date, period_of_report, is_amendment) "
        "values (%s,%s,'10-K','2024-02-20',%s,false) returning id",
        (cid, accession, FY_END),
    ).fetchone()[0]
    conn.execute(
        "insert into core.fact (company_id, concept_id, unit_id, period_id, filing_id, value, is_authoritative, "
        "raw_object_id) select %s, c.id, u.id, %s, %s, %s, %s, (select max(id) from raw.sec_companyfacts) "
        "from core.concept c, core.unit u where c.tag=%s and u.unit_name='usd'",
        (cid, pid, fid, value, authoritative, tag),
    )
    conn.commit()


@pytest.mark.integration
@pytest.mark.parametrize("earlier_is_authoritative", [False, True])
def test_earlier_differing_copy_is_history_unless_it_is_the_authoritative_one(
    isolated_database_url, earlier_is_authoritative
):
    case = CASES["share_count"]
    cik = f"000000009{int(earlier_is_authoritative)}"
    tag = case["facts"][0][0]
    with psycopg.connect(isolated_database_url) as conn:
        cid = _world(conn, cik, case, case["shown"])
        conn.execute(
            "insert into analytics.concept_mapping (canonical_concept_id, concept_id, priority, confidence) "
            "select cc.id, c.id, 1, 'approved' from analytics.canonical_concept cc, core.concept c "
            "where cc.name=%s and c.tag=%s and not exists (select 1 from analytics.concept_mapping m "
            "where m.canonical_concept_id=cc.id and m.concept_id=c.id)",
            (case["name"], tag),
        )
        _add_copy(
            conn,
            cid,
            tag,
            "14000000000",
            "0000000031-24-000001",
            earlier_is_authoritative,
        )
        cells = [
            c
            for c in load_shown(conn, cid, floor=date(2015, 1, 1))
            if c.data_point_name == case["name"]
        ]
    assert len(cells) == 1 and cells[0].accession == ADSH
    assert cells[0].copies_disagree
    p = pv.prove_cell(cells[0], _structure(case), "2025q1")
    if earlier_is_authoritative:
        assert p.verdict == pv.DISAGREE
        assert p.reason_code == "shown_is_not_the_authoritative_copy"
    else:
        assert p.verdict == pv.PROVEN, (p.reason_code, p.reason_text)
        assert p.checks["restated_history"]["copies"][0]["value"].startswith(
            "14000000000"
        )
