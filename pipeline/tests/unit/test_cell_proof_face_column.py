"""R13 refinement: a copy is a candidate authoritative copy only if its filing prints the period as a
face column (common/authority.face_column_eligible); HD Goodwill 2015-02-01 is the live case."""

from __future__ import annotations

from datetime import date

import psycopg
import pytest
from scrooner_pipeline.common.authority import face_column_eligible
from scrooner_pipeline.proof import prove as pv
from scrooner_pipeline.proof.shown import load_shown

from tests.unit.test_cell_proof_claims_db import CASES, FY_END, _structure, _world


@pytest.mark.unit
def test_face_column_eligibility_rules():
    d = date
    kw = dict(form="10-K", period_type="instant")
    # HD: the FY2018 10-K files goodwill at 2015-02-01: not a face column
    assert not face_column_eligible(
        end_date=d(2015, 2, 1), period_of_report=d(2019, 2, 3), **kw
    )
    assert face_column_eligible(
        end_date=d(2018, 1, 28), period_of_report=d(2019, 2, 3), **kw
    )  # prior year end
    assert face_column_eligible(
        end_date=d(2015, 2, 1), period_of_report=d(2015, 2, 1), **kw
    )
    # durations: a 10-K prints three annual columns, a 10-Q up to 400 days back
    assert face_column_eligible(
        form="10-K",
        period_type="duration",
        end_date=d(2022, 12, 31),
        period_of_report=d(2024, 12, 31),
    )
    assert not face_column_eligible(
        form="10-K",
        period_type="duration",
        end_date=d(2021, 12, 31),
        period_of_report=d(2024, 12, 31),
    )
    assert not face_column_eligible(
        form="10-Q",
        period_type="duration",
        end_date=d(2022, 12, 31),
        period_of_report=d(2024, 3, 31),
    )
    # the filing of the period is always eligible, an unjudgeable copy stays eligible
    assert face_column_eligible(
        form="10-Q",
        period_type="duration",
        end_date=d(2020, 1, 1),
        period_of_report=d(2024, 3, 31),
        is_original=True,
    )
    assert face_column_eligible(
        form="10-K",
        period_type="instant",
        end_date=d(2015, 2, 1),
        period_of_report=None,
    )


@pytest.mark.integration
def test_an_ineligible_authoritative_copy_neither_disagrees_nor_is_the_authority(
    isolated_database_url,
):
    case = CASES["share_count"]
    tag = case["facts"][0][0]
    with psycopg.connect(isolated_database_url) as conn:
        cid = _world(conn, "0000000950", case, case["shown"])
        conn.execute(
            "insert into analytics.concept_mapping (canonical_concept_id, concept_id, priority, confidence) "
            "select cc.id, c.id, 1, 'approved' from analytics.canonical_concept cc, core.concept c "
            "where cc.name=%s and c.tag=%s",
            (case["name"], tag),
        )
        pid = conn.execute(
            "select id from core.period where company_id=%s and end_date=%s and start_date=%s",
            (cid, FY_END, date(2024, 1, 1)),
        ).fetchone()[0]
        # a 10-K for FY2027 that restates the FY2024 column: three years back, not a face column
        fid = conn.execute(
            "insert into core.filing (company_id, accession_number, form, filing_date, period_of_report, is_amendment) "
            "values (%s,'0000000031-28-000001','10-K','2028-02-20','2027-12-31',false) returning id",
            (cid,),
        ).fetchone()[0]
        conn.execute(
            "insert into core.fact (company_id, concept_id, unit_id, period_id, filing_id, value, is_authoritative, "
            "raw_object_id) select %s, c.id, u.id, %s, %s, 14000000000, true, (select max(id) from raw.sec_companyfacts) "
            "from core.concept c, core.unit u where c.tag=%s and u.unit_name='usd'",
            (cid, pid, fid, tag),
        )
        conn.commit()
        cells = [
            c
            for c in load_shown(conn, cid, floor=date(2015, 1, 1))
            if c.data_point_name == case["name"]
        ]
    assert len(cells) == 1
    assert cells[0].copies_disagree is None and cells[0].authoritative_disagrees is None
    p = pv.prove_cell(cells[0], _structure(case), "2025q1")
    assert p.verdict == pv.PROVEN, (p.reason_code, p.reason_text)
