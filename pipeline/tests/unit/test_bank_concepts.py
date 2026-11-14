"""Bank canonical concepts (mapper/bank_concepts.py): the seed adds exactly the 6, is idempotent and never
touches an existing row; the structural loader rejects a bank row before the seed and loads it after."""

from __future__ import annotations

from pathlib import Path

import psycopg
import pytest
from scrooner_pipeline.mapper import bank_concepts as bc
from scrooner_pipeline.mapper import docmap_loader as dl
from scrooner_pipeline.mapper import sector_templates as st
from scrooner_pipeline.mapper import structural_loader as sl

from test_structural_loader_db import CHK, _rrow, _rsrc, _setup

NAMES = {
    "deposits",
    "loans_net",
    "noninterest_expense",
    "noninterest_income",
    "provision_for_credit_losses",
    "total_interest_income",
}
BS = {"deposits", "loans_net"}
CATALOG = (
    Path(__file__).resolve().parents[3]
    / "data-team/47-fsn-store/company_tag_map/concepts_catalog.csv"
)


def test_definitions_are_wellformed():
    assert {c[0] for c in bc.BANK_CONCEPTS} == NAMES and len(bc.BANK_CONCEPTS) == 6
    for name, stmt, mode, desc in bc.BANK_CONCEPTS:
        assert stmt == ("balance_sheet" if name in BS else "income_statement")
        assert mode == "first_match" and desc
        assert dl.served_concept(name, NAMES) == name  # no alias, no _resolved


def test_catalog_has_them_and_templates_are_bank_only():
    assert NAMES <= set(st.load_catalog(CATALOG))
    for n in NAMES:
        assert st.GROUP_ONLY[n] == frozenset({"bank"})


@pytest.mark.integration
def test_seed_is_additive_idempotent_and_dry_plan_matches(isolated_database_url):
    with psycopg.connect(isolated_database_url) as conn:
        conn.execute(
            "delete from analytics.canonical_concept where name = any(%s)",
            (sorted(NAMES),),
        )
        conn.execute(
            "insert into analytics.canonical_concept (name, statement, combination_mode, description) "
            "values ('deposits', 'balance_sheet', 'sum', 'pre-existing')"
        )
        conn.commit()
        count = "select count(*) from analytics.canonical_concept"
        before = conn.execute(count).fetchone()[0]
        rows, present = bc.plan(conn)
        assert present == ["deposits"] and {r[0] for r in rows} == NAMES - {"deposits"}
        assert conn.execute(count).fetchone()[0] == before  # plan writes nothing
        assert bc.seed(conn) == {"considered": 6, "inserted": 5}
        assert bc.seed(conn) == {"considered": 6, "inserted": 0}
        assert conn.execute(count).fetchone()[0] == before + 5
        assert conn.execute(
            "select combination_mode, description from analytics.canonical_concept where name = 'deposits'"
        ).fetchone() == ("sum", "pre-existing")


@pytest.mark.integration
def test_loader_rejects_bank_row_before_seed_and_accepts_after(
    isolated_database_url, tmp_path: Path
):
    body = _rrow(
        "deposits",
        "2023-12-31",
        "mapped",
        "Deposits [R2.htm:9] | why: BS deposits line",
        100,
        "0000000099-24-000010",
        chk=CHK,
    )
    with psycopg.connect(isolated_database_url) as conn:
        conn.execute(
            "delete from analytics.canonical_concept where name = any(%s)",
            (sorted(NAMES),),
        )
        conn.commit()
        cid = _setup(conn)
        conn.execute(
            "insert into core.concept (taxonomy, tag) values ('us-gaap', 'Deposits')"
        )
        conn.commit()
        s = sl.load(conn, _rsrc(tmp_path, body), apply=True)
        assert [r["why"] for r in s["rejects"]] == ["no canonical concept of that name"]
        bc.seed(conn)
        s = sl.load(conn, _rsrc(tmp_path, body), apply=True)
        assert s["rejects"] == [] and s["blocked"] == {}
        n = conn.execute(
            "select count(*) from analytics.company_tag_map m join analytics.canonical_concept c "
            "on c.id = m.canonical_concept_id where m.company_id = %s and c.name = 'deposits'",
            (cid,),
        ).fetchone()[0]
        assert n >= 1
