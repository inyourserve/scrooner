"""A cell served from the filing's own XBRL (value_source fsn_xbrl) carries fsn.value ids (source_value_ids), not
core.fact ids. The proof's source (a) must resolve its filing and tags from them: MSFT operating_expenses FY2015-17
(a component sum with the custom ImpairmentIntegrationAndRestructuringExpenses) was UNCHECKED 'no FSN structure
for the shown accession' because shown.py read source_fact_ids only."""

from __future__ import annotations

from datetime import date

import psycopg
import pytest
from scrooner_pipeline.proof.shown import load_shown

from tests.unit.test_cell_proof_claims_db import ADSH, CASES, FY_END, _world


@pytest.mark.integration
def test_fsn_xbrl_cell_resolves_its_accession_and_tags_from_source_value_ids(
    isolated_database_url,
):
    case = CASES["component_sum"]
    with psycopg.connect(isolated_database_url) as conn:
        cid = _world(conn, "0000000777", case, case["shown"])
        fid = conn.execute(
            "insert into fsn.filing (accession, company_id, cik, form, period, filed, fsn_set) "
            "values (%s, %s, '0000000777', '10-K', %s, '2025-02-20', 't') returning id",
            (ADSH, cid, FY_END),
        ).fetchone()[0]
        ids = []
        for tag, value in case["facts"]:
            tid = conn.execute(
                "insert into fsn.tag (tag, version, custom) values (%s, 'us-gaap/2024', false) returning id",
                (tag,),
            ).fetchone()[0]
            ids.append(
                conn.execute(
                    "insert into fsn.value (filing_id, company_id, tag_id, ddate, qtrs, uom, dim_id, value) "
                    "values (%s, %s, %s, %s, 0, 'USD', 0, %s) returning id",
                    (fid, cid, tid, FY_END, value),
                ).fetchone()[0]
            )
        # the mapper's fsn_xbrl lineage: no core.fact ids, only fsn.value ids
        conn.execute(
            "update analytics.canonical_fact set source_fact_ids = '{}', source_value_ids = %s where company_id = %s",
            (ids, cid),
        )
        conn.commit()
        cells = [
            c
            for c in load_shown(conn, cid, floor=date(2015, 1, 1))
            if c.data_point_name == case["name"]
        ]
    assert len(cells) == 1
    assert cells[0].accession == ADSH
    assert set(cells[0].tags) == {t for t, _ in case["facts"]}
