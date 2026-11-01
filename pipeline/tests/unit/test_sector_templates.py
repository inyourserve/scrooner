"""Sector templates (doc 02 ruling 2026-11-01, migration 0120): parsing, the per-company
plan (sector default plus company overrides), and, on REAL SQL when
SCROONER_TEST_DATABASE_URL is set, the 0120 constraints, the idempotent writer and
template-mode coverage (valued / template cells) in mapper/coverage_snapshot.py."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest
from scrooner_pipeline.mapper import sector_templates as st

TEMPLATES = """# Sector templates (test fixture)

template_version: tv-test-1
effective_from: 2026-11-01

## Sector assignment
| template | sic_from | sic_to |
|---|---|---|
| corporate | 100 | 6019 |
| bank | 6020 | 6036 |
| corporate | 6037 | 9999 |

## Company assignment
| cik | template | reason |
|---|---|---|
| 0000000003 | bank | files as a bank holding company under a non-bank SIC |

## Sector defaults
| template | data_point | in_template | reason |
|---|---|---|---|
| corporate | revenue | yes | |
| corporate | inventory | yes | |
| bank | revenue | yes | |
| bank | inventory | no | banks present no inventory line |

## Company overrides
| cik | data_point | in_template | reason |
|---|---|---|---|
| 0000000002 | inventory | no | service company, no inventory line on the face |
"""

COHORT = """shard,rank,company_id,cik,ticker,name,sic,mcap_bn,cells,filled,unexplained_blank,excluded
S001,1,11,0000000001,AAA,A CORP,3571,1,1,1,0,
S001,2,12,0000000002,BBB,B CORP,7372,1,1,1,0,
S001,3,13,0000000003,CCC,C BANCORP,6199,1,1,1,0,
S001,4,14,0000000004,DDD,D BANK,6022,1,1,1,0,
S001,5,15,0000000005,EEE,E GONE,3571,1,1,1,0,merged
"""


def _cohort(tmp_path: Path, text: str = COHORT) -> list[st.CohortCompany]:
    p = tmp_path / "shards.csv"
    p.write_text(text)
    return st.load_cohort(p)


def _plan(tmp_path: Path, templates: str = TEMPLATES) -> list[st.TemplateRow]:
    return st.build_plan(st.parse_templates(templates), _cohort(tmp_path))


def _cells(rows: list[st.TemplateRow]) -> dict[tuple[int, str], tuple[bool, str, str]]:
    return {
        (r.company_id, r.data_point): (r.in_template, r.template, r.source)
        for r in rows
    }


@pytest.mark.unit
class TestPlan:
    def test_sector_default_then_company_override(self, tmp_path):
        cells = _cells(_plan(tmp_path))
        assert cells == {
            (11, "inventory"): (True, "corporate", "sector_default"),
            (11, "revenue"): (True, "corporate", "sector_default"),
            # company override beats the corporate default
            (12, "inventory"): (False, "corporate", "company_override"),
            (12, "revenue"): (True, "corporate", "sector_default"),
            # company assignment beats the SIC range (6199 would be corporate)
            (13, "inventory"): (False, "bank", "sector_default"),
            (13, "revenue"): (True, "bank", "sector_default"),
            (14, "inventory"): (False, "bank", "sector_default"),
            (14, "revenue"): (True, "bank", "sector_default"),
        }

    def test_excluded_cohort_rows_are_not_seeded(self, tmp_path):
        assert 15 not in {r.company_id for r in _plan(tmp_path)}

    def test_reasons_and_version_carried(self, tmp_path):
        rows = {(r.company_id, r.data_point): r for r in _plan(tmp_path)}
        assert (
            rows[(12, "inventory")].reason
            == "service company, no inventory line on the face"
        )
        assert rows[(11, "revenue")].reason is None
        assert {r.template_version for r in rows.values()} == {"tv-test-1"}
        assert {r.effective_from for r in rows.values()} == {date(2026, 11, 1)}

    def test_summary(self, tmp_path):
        s = st.summarize(_plan(tmp_path))
        assert (
            s["companies"],
            s["rows"],
            s["template_cells"],
            s["excluded_cells"],
        ) == (4, 8, 5, 3)
        assert s["companies_per_template"] == {"bank": 2, "corporate": 2}

    def test_company_matching_no_template_fails_loudly(self, tmp_path):
        text = TEMPLATES.replace("| corporate | 6037 | 9999 |\n", "")
        with pytest.raises(st.TemplateError, match="0000000002 .* matches no template"):
            _plan(tmp_path, text)

    def test_override_for_company_outside_cohort_fails(self, tmp_path):
        text = TEMPLATES + "| 0000000099 | revenue | no | not in cohort |\n"
        with pytest.raises(st.TemplateError, match="0000000099"):
            _plan(tmp_path, text)

    def test_plan_csv_round_trip(self, tmp_path):
        out = tmp_path / "plan.csv"
        st.write_plan_csv(_plan(tmp_path), out)
        lines = out.read_text().splitlines()
        assert lines[0].startswith(
            "company_id,data_point,in_template,reason,effective_from"
        )
        assert len(lines) == 9


@pytest.mark.unit
class TestParseErrors:
    @pytest.mark.parametrize(
        ("old", "new", "message"),
        [
            (
                "| bank | inventory | no | banks present no inventory line |",
                "| bank | inventory | no | |",
                "excluded without a reason",
            ),
            (
                "| 0000000002 | inventory | no | service company, no inventory line on the face |",
                "| 0000000002 | inventory | no | |",
                "override 0000000002/inventory has no reason",
            ),
            (
                "| corporate | inventory | yes | |",
                "| corporate | revenue | yes | |",
                "duplicate default corporate/revenue",
            ),
            ("| bank | 6020 | 6036 |", "| bank | 6000 | 6036 |", "SIC ranges overlap"),
            (
                "| corporate | revenue | yes | |",
                "| corporate | revenue | maybe | |",
                "not yes/no",
            ),
            ("effective_from: 2026-11-01", "effective_from: 1 Nov", "not YYYY-MM-DD"),
            ("template_version: tv-test-1\n", "", "missing 'template_version"),
            (
                "| 0000000003 | bank |",
                "| 0000000003 | thrift |",
                "'thrift' has no sector defaults",
            ),
            (
                "| template | data_point | in_template | reason |",
                "| template | data_point | included | reason |",
                "columns",
            ),
        ],
    )
    def test_rejected(self, old, new, message):
        assert old in TEMPLATES
        with pytest.raises(st.TemplateError, match=message):
            st.parse_templates(TEMPLATES.replace(old, new, 1))

    def test_missing_defaults_section(self):
        text = TEMPLATES.split("## Sector defaults")[0]
        with pytest.raises(st.TemplateError, match="sector defaults' is missing"):
            st.parse_templates(text)


# --------------------------------------------------------------------------- real SQL


@pytest.fixture
def db(isolated_database_url):
    psycopg = pytest.importorskip("psycopg")
    conn = psycopg.connect(isolated_database_url)
    present = conn.execute(
        "select to_regclass('analytics.company_data_point_template') is not null"
    ).fetchone()[0]
    if not present:
        conn.close()
        pytest.skip("needs the migrated schema with migration 0120")
    yield conn
    conn.rollback()
    conn.close()


def _seed_db(conn) -> dict[str, int]:
    ids = {}
    for n in range(1, 5):
        ids[n] = conn.execute(
            "insert into core.company (cik, company_name) values (%s, %s) returning id",
            (f"{n:010d}", f"CO {n}"),
        ).fetchone()[0]
    concept = {}
    for name in ("revenue", "inventory"):
        concept[name] = conn.execute(
            "insert into analytics.canonical_concept (name, statement, combination_mode)"
            " values (%s, 'income_statement', 'first_match')"
            " on conflict (name) do update set name = excluded.name returning id",
            (name,),
        ).fetchone()[0]
    metric = conn.execute(
        "insert into analytics.metric_definition (metric_name, formula_description)"
        " values ('revenue', 'test') returning id"
    ).fetchone()[0]

    def fact(company: int, name: str) -> None:
        period = conn.execute(
            "insert into core.period (company_id, start_date, end_date, period_type)"
            " values (%s, '2025-01-01', '2025-12-31', 'duration')"
            " on conflict (company_id, start_date, end_date, period_type)"
            " do update set period_type = excluded.period_type returning id",
            (company,),
        ).fetchone()[0]
        conn.execute(
            "insert into analytics.canonical_fact"
            " (company_id, canonical_concept_id, period_id, value, source_fact_ids)"
            " values (%s, %s, %s, 1, '{}')",
            (company, concept[name], period),
        )

    # revenue concept valued for companies 1, 2, 3; inventory only for company 1 and
    # company 4 (4's template EXCLUDES inventory: its value must not count).
    for c in (1, 2, 3):
        fact(ids[c], "revenue")
    fact(ids[1], "inventory")
    fact(ids[4], "inventory")
    # revenue metric: a value for 1, a null-reason row for 2 (not valued)
    for c, v in ((1, Decimal(5)), (2, None)):
        conn.execute(
            "insert into analytics.metric_value (company_id, metric_definition_id, period_start,"
            " period_end, period_label, value) values (%s, %s, '2025-01-01', '2025-12-31', 'FY', %s)",
            (ids[c], metric, v),
        )
    conn.commit()
    return ids


def _db_cohort(tmp_path: Path, ids: dict[int, int]) -> list[st.CohortCompany]:
    text = COHORT
    for n, cid in ids.items():
        text = text.replace(f",{10 + n},{n:010d},", f",{cid},{n:010d},")
    return _cohort(tmp_path, text)


@pytest.mark.integration
class TestDatabase:
    def test_constraints_reject_reasonless_exclusion_and_override(self, db):
        ids = _seed_db(db)
        psycopg = pytest.importorskip("psycopg")
        base = "insert into analytics.company_data_point_template (company_id, data_point, in_template, reason, effective_from, template, source, template_version) values (%s, 'revenue', %s, %s, '2026-11-01', 'corporate', %s, 'tv')"  # fmt: skip
        for in_t, reason, source in ((False, None, "sector_default"),
                                     (True, " ", "company_override"),
                                     (True, None, "guess")):  # fmt: skip
            with pytest.raises(psycopg.errors.CheckViolation):
                with db.transaction():
                    db.execute(base, (ids[1], in_t, reason, source))
        with db.transaction():
            db.execute(base, (ids[1], True, None, "sector_default"))

    def test_write_is_idempotent_and_template_coverage_uses_template_cells(
        self, db, tmp_path
    ):
        from scrooner_pipeline.mapper.coverage_snapshot import compute_snapshot

        ids = _seed_db(db)
        rows = st.build_plan(st.parse_templates(TEMPLATES), _db_cohort(tmp_path, ids))
        st.validate_against_db(db, rows)
        first = st.write_plan(db, rows)
        again = st.write_plan(db, rows)
        assert (first["inserted"], first["deleted"]) == (8, 0)
        assert (again["inserted"], again["deleted"]) == (8, 8)
        count = "select count(*) from analytics.company_data_point_template"
        assert db.execute(count).fetchone()[0] == 8

        snap = compute_snapshot(db, date(2026, 11, 2))
        assert snap["template_mode"] is True
        by = {(r["item_type"], r["item_name"]): r for r in snap["rows"]}
        # revenue: in all 4 templates; concept valued at 1, 2, 3
        assert (by[("concept", "revenue")]["companies_covered"],
                by[("concept", "revenue")]["total_active_companies"]) == (3, 4)  # fmt: skip
        # revenue metric: only company 1 has a non-null value
        assert (by[("metric", "revenue")]["companies_covered"],
                by[("metric", "revenue")]["total_active_companies"]) == (1, 4)  # fmt: skip
        # inventory: in template only for company 1 (2 overridden out, 3 and 4 banks);
        # company 4's value is outside its template and does not count
        assert (by[("concept", "inventory")]["companies_covered"],
                by[("concept", "inventory")]["total_active_companies"]) == (1, 1)  # fmt: skip
        assert by[("concept", "inventory")]["coverage_pct"] == Decimal("100.00")
        # cells: revenue x4 (scored as the metric: 1 valued) + inventory x1 (1 valued)
        score = by[("score", "template_cell_coverage_score")]
        assert (score["companies_covered"], score["total_active_companies"]) == (2, 5)
        assert score["coverage_pct"] == Decimal("40.00")
        # a data point in no template is not a cell
        assert not any(r["item_name"] not in ("revenue", "inventory") for r in snap["rows"]
                       if r["item_type"] != "score")  # fmt: skip

    def test_template_before_effective_from_is_not_current(self, db, tmp_path):
        from scrooner_pipeline.mapper.coverage_snapshot import compute_snapshot

        ids = _seed_db(db)
        rows = st.build_plan(st.parse_templates(TEMPLATES), _db_cohort(tmp_path, ids))
        st.write_plan(db, rows)
        snap = compute_snapshot(db, date(2026, 10, 31))
        assert snap["template_mode"] is False

    def test_new_version_replaces_the_whole_set(self, db, tmp_path):
        from scrooner_pipeline.mapper.coverage_snapshot import compute_snapshot

        ids = _seed_db(db)
        cohort = _db_cohort(tmp_path, ids)
        st.write_plan(db, st.build_plan(st.parse_templates(TEMPLATES), cohort))
        v2 = (TEMPLATES.replace("effective_from: 2026-11-01", "effective_from: 2026-12-01")
                       .replace("| corporate | inventory | yes | |\n", "")
                       .replace("tv-test-1", "tv-test-2"))  # fmt: skip
        st.write_plan(db, st.build_plan(st.parse_templates(v2), cohort))
        snap = compute_snapshot(db, date(2026, 12, 2))
        by = {(r["item_type"], r["item_name"]): r for r in snap["rows"]}
        # inventory left the corporate template in v2; company 1's v1 row is history only
        assert ("concept", "inventory") not in by
        assert by[("concept", "revenue")]["total_active_companies"] == 4

    def test_unknown_data_point_rejected(self, db, tmp_path):
        ids = _seed_db(db)
        text = TEMPLATES.replace(
            "| bank | revenue | yes | |", "| bank | net_interest_margin | yes | |"
        )
        rows = st.build_plan(st.parse_templates(text), _db_cohort(tmp_path, ids))
        with pytest.raises(st.TemplateError, match="net_interest_margin"):
            st.validate_against_db(db, rows)


@pytest.mark.integration
def test_cohort_without_sic_reads_sic_from_core_company(db, tmp_path):
    ids = _seed_db(db)
    db.execute("update core.company set sic_code = '6022' where id = %s", (ids[1],))
    db.execute("update core.company set sic_code = null where id = %s", (ids[2],))
    p = tmp_path / "cohort.csv"
    p.write_text(
        "company_id,cik,ticker\n" + "".join(f"{ids[n]},{n:010d},T{n}\n" for n in (1, 2))
    )
    assert st.cohort_has_sic(p) is False
    filled = {c.company_id: c.sic for c in st.fill_sic_from_db(db, st.load_cohort(p))}
    assert filled == {ids[1]: 6022, ids[2]: None}
    p.write_text(f"company_id,cik\n{ids[1]},0000000099\n")
    with pytest.raises(st.TemplateError, match="!= core.company"):
        st.fill_sic_from_db(db, st.load_cohort(p))
