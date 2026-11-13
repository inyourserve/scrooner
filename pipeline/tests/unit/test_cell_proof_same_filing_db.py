"""R13: a second, differing authoritative fact inside the SAME filing the shown value came from (MSFT
SG&A 8,263M vs 1,823M, HD total debt) is no other vintage: the proof judges the shown value against
that filing, it does not return shown_is_not_the_authoritative_copy."""

from __future__ import annotations

from datetime import date

import psycopg
import pytest
from scrooner_pipeline.proof import prove as pv
from scrooner_pipeline.proof.shown import load_shown

from tests.unit.test_cell_proof_claims_db import ADSH, CASES, _structure, _world


@pytest.mark.integration
def test_differing_authoritative_fact_in_the_same_filing_is_not_another_vintage(
    isolated_database_url,
):
    case = CASES["share_count"]
    tag = case["facts"][0][0]
    with psycopg.connect(isolated_database_url) as conn:
        cid = _world(conn, "0000000960", case, case["shown"])
        conn.execute(
            "insert into analytics.concept_mapping (canonical_concept_id, concept_id, priority, confidence) "
            "select cc.id, c.id, 1, 'approved' from analytics.canonical_concept cc, core.concept c "
            "where cc.name=%s and c.tag=%s",
            (case["name"], tag),
        )
        # a second source tag of the same cell (MSFT SG&A = two tags), same filing, another value
        conn.execute(
            "insert into core.concept (taxonomy, tag) values ('us-gaap','OtherTagOfTheCell') on conflict do nothing"
        )
        conn.execute(
            "insert into analytics.concept_mapping (canonical_concept_id, concept_id, priority, confidence) "
            "select cc.id, c.id, 2, 'approved' from analytics.canonical_concept cc, core.concept c "
            "where cc.name=%s and c.tag='OtherTagOfTheCell'",
            (case["name"],),
        )
        fid = conn.execute(
            "insert into core.fact (company_id, concept_id, unit_id, period_id, filing_id, value, is_authoritative, "
            "raw_object_id) select f.company_id, (select id from core.concept where tag='OtherTagOfTheCell'), f.unit_id, "
            "f.period_id, f.filing_id, 14000000000, true, f.raw_object_id from core.fact f "
            "join core.concept c on c.id=f.concept_id join core.filing fl on fl.id=f.filing_id "
            "where f.company_id=%s and c.tag=%s and fl.accession_number=%s returning id",
            (cid, tag, ADSH),
        ).fetchone()[0]
        conn.execute(
            "update analytics.canonical_fact set source_fact_ids = source_fact_ids || %s::bigint "
            "where company_id=%s",
            (fid, cid),
        )
        conn.commit()
        cells = [
            c
            for c in load_shown(conn, cid, floor=date(2015, 1, 1))
            if c.data_point_name == case["name"]
        ]
    assert len(cells) == 1 and cells[0].accession == ADSH
    assert cells[0].authoritative_disagrees is None
    assert cells[0].copies_disagree  # still recorded as history
    p = pv.prove_cell(cells[0], _structure(case), "2025q1")
    assert p.reason_code != "shown_is_not_the_authoritative_copy"
    assert p.verdict == pv.PROVEN, (p.reason_code, p.reason_text)
