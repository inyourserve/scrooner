"""Per-company (--ciks) resolve stages on REAL SQL against the MIGRATED schema.

Review item for work/engineering/nightly-resolve-stages (2026-10-31): prove that

  1. a --ciks run of resolve-statement-fallbacks + resolve-conflict-fills writes,
     for the scoped company, exactly the rows the population-wide run writes,
     and touches nothing of any other company (no insert, no delete), and
  2. --dry-run writes nothing through the real CLI code path.

Needs SCROONER_TEST_DATABASE_URL pointing at a database where every migration
has been applied (CI: the repository-integrity job's Postgres service, after
its "Apply every migration" step). It skips, never fails, when the schema is
missing, and runs the opt-in isolated-database guard from conftest.py.

Unlike test_cell_store_sql.py / test_shared_accession_sql.py this file does NOT
rebuild `core`/`analytics` from a DDL fragment: the functions under test hard-code
those schema names and the point is to exercise the shipped constraints
(identity ids, FKs through raw.sec_companyfacts, the canonical_fact unique key
the ON CONFLICT clauses rely on). Everything it seeds is rolled back or deleted.
"""

from __future__ import annotations

from contextlib import contextmanager
from datetime import date
from decimal import Decimal

import psycopg
import pytest
from scrooner_pipeline.corporate_actions.stock_splits import (
    RETROACTIVE_ADJUSTMENT_CONCEPTS,
)
from scrooner_pipeline.jobs import map as map_job
from scrooner_pipeline.mapper import concept_fallback as cf
from scrooner_pipeline.mapper import conflict_resolution as cr

CIK_A, CIK_B = "0000000901", "0000000902"  # test-only CIKs, deleted on teardown

REQUIRED_CONCEPTS = sorted(
    {n for pair in cr.CONFLICT_FILL_TARGETS for n in pair}
    | {n for row in cf.ARITHMETIC_FALLBACKS for n in row[:4]}
    | set(RETROACTIVE_ADJUSTMENT_CONCEPTS)
    | set(RETROACTIVE_ADJUSTMENT_CONCEPTS.values())
    | {
        "capex",
        "capex_resolved",
        "depreciation_and_amortization_resolved",
        "revenue_sanity_resolved",
        "operating_income_resolved",
    }
)


def _has_migrated_schema(conn) -> bool:
    row = conn.execute(
        "select count(*) from information_schema.tables where (table_schema, table_name) in "
        "(('core','fact'), ('analytics','canonical_fact'), ('analytics','concept_mapping'), "
        "('raw','sec_companyfacts'), ('analytics','company_stock_split'))"
    ).fetchone()
    return row[0] == 5


def _concept_ids(conn) -> dict[str, int]:
    conn.execute(
        "insert into analytics.canonical_concept (name, statement, combination_mode) "
        "select n, 'income_statement', 'first_match' from unnest(%s::text[]) n "
        "where not exists (select 1 from analytics.canonical_concept c where c.name = n)",
        (REQUIRED_CONCEPTS,),
    )
    return dict(
        conn.execute(
            "select name, id from analytics.canonical_concept where name = any(%s)",
            (REQUIRED_CONCEPTS,),
        ).fetchall()
    )


def _one(conn, sql, params=()):
    return conn.execute(sql, params).fetchone()[0]


def seed_company(conn, cik: str, cid: dict[str, int]) -> dict:
    """One company with: a plain net_income canonical fact (baseline pass-through
    target), a dedupe conflict on NetIncomeLoss for a second period (two non-
    authoritative facts, 100 vs 105: within MAX_SAFE_RATIO, so conflict-fill
    picks the later fact), and revenue + cost_of_revenue canonical facts so the
    arithmetic fallback derives gross_profit_resolved = revenue - cost."""
    company_id = _one(
        conn,
        "insert into core.company (cik, company_name, status) values (%s, %s, 'active') returning id",
        (cik, f"TEST CO {cik}"),
    )
    raw_id = _one(
        conn,
        "insert into raw.sec_companyfacts (cik, source_url, sha256, storage_path, http_status) "
        "values (%s, 'test://companyfacts', repeat('0', 64), 'raw/test/' || %s, 200) returning id",
        (cik, cik),
    )
    unit_id = _one(
        conn,
        "insert into core.unit (unit_name) values ('usd') on conflict (unit_name) do update "
        "set unit_name = excluded.unit_name returning id",
    )
    concept_id = _one(
        conn,
        "insert into core.concept (taxonomy, tag) values ('us-gaap', 'NetIncomeLoss') "
        "on conflict (taxonomy, tag) do update set tag = excluded.tag returning id",
    )
    conn.execute(
        "insert into analytics.concept_mapping (canonical_concept_id, concept_id, priority, confidence) "
        "values (%s, %s, 1, 'approved') on conflict (canonical_concept_id, concept_id) do nothing",
        (cid["net_income"], concept_id),
    )
    p_plain = _one(
        conn,
        "insert into core.period (company_id, start_date, end_date, period_type, fiscal_year, fiscal_period) "
        "values (%s, '2026-01-01', '2026-03-31', 'duration', 2026, 'Q1') returning id",
        (company_id,),
    )
    p_conflict = _one(
        conn,
        "insert into core.period (company_id, start_date, end_date, period_type, fiscal_year, fiscal_period) "
        "values (%s, '2026-04-01', '2026-06-30', 'duration', 2026, 'Q2') returning id",
        (company_id,),
    )
    filings = [
        _one(
            conn,
            "insert into core.filing (company_id, accession_number, form, filing_date) "
            "values (%s, %s, '10-Q', %s) returning id",
            (company_id, f"{cik}-26-00000{i}", d),
        )
        for i, d in ((1, date(2026, 5, 1)), (2, date(2026, 8, 1)))
    ]
    fact_ids = []
    for filing_id, value in zip(filings, (Decimal(100), Decimal(105))):
        fact_ids.append(
            _one(
                conn,
                "insert into core.fact (company_id, concept_id, unit_id, period_id, filing_id, value, "
                "is_authoritative, raw_object_id) values (%s, %s, %s, %s, %s, %s, false, %s) returning id",
                (company_id, concept_id, unit_id, p_conflict, filing_id, value, raw_id),
            )
        )
    for name, value in (
        ("net_income", Decimal(1000)),
        ("revenue", Decimal(5000)),
        ("cost_of_revenue", Decimal(3000)),
    ):
        conn.execute(
            "insert into analytics.canonical_fact (company_id, canonical_concept_id, period_id, value, source_fact_ids) "
            "values (%s, %s, %s, %s, %s)",
            (company_id, cid[name], p_plain, value, [fact_ids[0]]),
        )
    return {
        "company_id": company_id,
        "p_plain": p_plain,
        "p_conflict": p_conflict,
        "fact_ids": fact_ids,
    }


def resolved_rows(conn, company_id: int, cid: dict[str, int]) -> set[tuple]:
    """(concept name, period role, value, sorted source ids) for every row of the
    company -- company-independent so two companies' outputs can be compared."""
    name_by_id = {v: k for k, v in cid.items()}
    rows = conn.execute(
        "select canonical_concept_id, period_id, value, source_fact_ids, "
        "(select fiscal_period from core.period p where p.id = cf.period_id) "
        "from analytics.canonical_fact cf where company_id = %s",
        (company_id,),
    ).fetchall()
    facts = conn.execute(
        "select id, value from core.fact where company_id = %s", (company_id,)
    ).fetchall()
    value_of = {fid: v for fid, v in facts}
    return {
        (
            name_by_id.get(c, str(c)),
            fp,
            str(v),
            tuple(sorted(str(value_of.get(f, f"?{f}")) for f in (srcs or []))),
        )
        for c, _p, v, srcs, fp in rows
    }


def run_both(conn, company_ids):
    cf.resolve_all_arithmetic_fallbacks(conn, company_ids)
    cr.resolve_all_conflict_fills(conn, company_ids)


@pytest.fixture
def db(isolated_database_url):
    conn = psycopg.connect(isolated_database_url)
    if not _has_migrated_schema(conn):
        conn.close()
        pytest.skip(
            "needs the migrated core/analytics/raw schema (CI applies every migration)"
        )
    yield conn
    conn.close()


@pytest.mark.integration
def test_ciks_run_equals_population_run_and_touches_no_other_company(db, monkeypatch):
    conn = db
    conn.commit = lambda: None  # one transaction; rolled back at the end
    try:
        cid = _concept_ids(conn)
        a = seed_company(conn, CIK_A, cid)
        b = seed_company(conn, CIK_B, cid)
        # B already has a stale derived row that the population-wide run DELETES
        # (resolve_capex_with_software rebuilds capex_resolved from `capex`, and B
        # has no capex fact, so the row simply disappears). A scoped run for A must
        # leave it exactly as it is. capex_resolved feeds no other derivation here,
        # so the stale value cannot leak into another concept's first pass.
        conn.execute(
            "insert into analytics.canonical_fact (company_id, canonical_concept_id, period_id, value, source_fact_ids) "
            "values (%s, %s, %s, 4242, %s)",
            (b["company_id"], cid["capex_resolved"], b["p_plain"], [b["fact_ids"][0]]),
        )
        # ... and a detected split for B: detect_stock_splits rebuilds that table
        # (population-wide: a full delete) -- scoped to A it must not touch B's row.
        conn.execute(
            "insert into analytics.company_stock_split (company_id, effective_date, ratio, raw_value, source_fact_id, source_tag) "
            "values (%s, '2025-06-01', 2, 2, %s, 'StockholdersEquityNoteStockSplitConversionRatio1')",
            (b["company_id"], b["fact_ids"][0]),
        )
        splits_before = conn.execute(
            "select company_id, effective_date, ratio from analytics.company_stock_split order by 1, 2"
        ).fetchall()
        b_before = resolved_rows(conn, b["company_id"], cid)

        run_both(conn, [a["company_id"]])  # --ciks A
        a_scoped = resolved_rows(conn, a["company_id"], cid)
        assert resolved_rows(conn, b["company_id"], cid) == b_before, (
            "scoped run touched company B"
        )
        assert (
            conn.execute(
                "select company_id, effective_date, ratio from analytics.company_stock_split order by 1, 2"
            ).fetchall()
            == splits_before
        ), "scoped run touched company B's stock-split row"

        # what a --ciks run must produce for A
        assert (
            "net_income_resolved",
            "Q1",
            "1000",
            ("100",),
        ) in a_scoped  # baseline pass-through
        assert (
            "net_income_resolved",
            "Q2",
            "105",
            ("105",),
        ) in a_scoped  # conflict fill, later fact
        assert (
            "cost_of_revenue_resolved",
            "Q1",
            "3000",
            ("100",),
        ) in a_scoped  # arithmetic pass-through
        # gross_profit_resolved is NOT derived on a first pass: ARITHMETIC_FALLBACKS
        # computes it from cost_of_revenue_resolved, which the next entry only then
        # creates (pre-existing stage order, converges on the next run) -- so the
        # test asserts scoped == population rather than a hand-expected gross profit.
        assert not {r for r in a_scoped if r[0] == "gross_profit_resolved"}

        run_both(conn, None)  # population-wide: first pass for B, second pass for A
        a_population = resolved_rows(conn, a["company_id"], cid)
        b_population = resolved_rows(conn, b["company_id"], cid)
        # B is seeded identically to A, so the population run's first pass over B
        # must equal the scoped run's first pass over A, row for row (B's stale
        # capex_resolved row is gone, exactly as A never had one).
        assert b_population == a_scoped
        assert not {r for r in b_population if r[0] == "capex_resolved"}
        assert ("cost_of_revenue_resolved", "Q1", "3000", ("100",)) in b_population
        # A's second pass adds only the lagged gross_profit derivation (see above);
        # nothing the first pass wrote changes.
        assert a_scoped <= a_population
        assert {r[0] for r in a_population - a_scoped} == {"gross_profit_resolved"}
        # and a second scoped pass converges to the same state as the population pass
        run_both(conn, [a["company_id"]])
        assert resolved_rows(conn, a["company_id"], cid) == a_population
    finally:
        conn.rollback()


@pytest.mark.integration
def test_dry_run_through_the_cli_writes_nothing(db, isolated_database_url, monkeypatch):
    conn = db
    cid = _concept_ids(conn)
    a = seed_company(conn, CIK_A, cid)
    conn.commit()  # the seed must be visible to the CLI's own connection
    try:

        @contextmanager
        def test_connection():
            with psycopg.connect(isolated_database_url) as c:
                yield c

        monkeypatch.setattr(map_job, "get_connection", test_connection)
        map_job.resolve_statement_fallbacks_cmd(
            ciks=CIK_A, dry_run=True, statement_timeout="1min"
        )
        map_job.resolve_conflict_fills_cmd(
            ciks=CIK_A, dry_run=True, statement_timeout="1min"
        )

        after = resolved_rows(conn, a["company_id"], cid)
        assert not {r for r in after if r[0].endswith("_resolved")}, after
        assert (
            _one(
                conn,
                "select count(*) from analytics.canonical_fact where company_id = %s",
                (a["company_id"],),
            )
            == 3
        )

        # and the same two commands WITHOUT --dry-run do write (sanity of the seam)
        map_job.resolve_statement_fallbacks_cmd(
            ciks=CIK_A, dry_run=False, statement_timeout="1min"
        )
        map_job.resolve_conflict_fills_cmd(
            ciks=CIK_A, dry_run=False, statement_timeout="1min"
        )
        assert ("net_income_resolved", "Q2", "105", ("105",)) in resolved_rows(
            conn, a["company_id"], cid
        )
    finally:
        conn.rollback()
        for sql in (
            "delete from analytics.canonical_fact where company_id = %s",
            "delete from analytics.company_stock_split where company_id = %s",
            "delete from core.fact where company_id = %s",
            "delete from core.filing where company_id = %s",
            "delete from core.period where company_id = %s",
            "delete from core.company where id = %s",
        ):
            conn.execute(sql, (a["company_id"],))
        conn.execute("delete from raw.sec_companyfacts where cik = %s", (CIK_A,))
        conn.commit()
