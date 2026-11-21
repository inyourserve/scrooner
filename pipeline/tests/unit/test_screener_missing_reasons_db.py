"""Screener exclusion reasons and include_missing on a migrated scratch database
(Postgres 16 in CI). A screener never drops a company silently: every company a
filter leaves out for a missing value carries a reason, and
matched + excluded + not_matched = total_candidates on both execution paths.

Fixture (one private dataset_version, rolled back at the end):
  P  revenue_growth_yoy 0.25 (passes > 0.10)       roe 0.10
  F  revenue_growth_yoy 0.05 (fails)               roe null, no row
  H  null; metric_value null row missing:prior_period at the snapshot period   roe 0.60
  T  null; company template OUT for revenue_growth_yoy                          roe null
  G  null; no metric_value row at all (our gap)                                 roe null
  I  inactive, null (never a candidate)
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import psycopg
import pytest
from psycopg import sql

from scrooner_pipeline.screener.query import explain_stored_exclusions, run_query
from scrooner_pipeline.screener.schema import ScreenQuery

VERSION = 990_001
METRICS = ("revenue_growth_yoy", "roe")


def _build(conn) -> tuple[dict[str, int], dict[str, int]]:
    catalog = {}
    for name in METRICS:
        catalog[name] = conn.execute(
            "insert into analytics.metric_definition (metric_name, formula_version, formula_description) "
            "values (%s, 1, 'test') returning id",
            (name,),
        ).fetchone()[0]
    parts = []
    for name in METRICS:
        parts += [
            sql.SQL("add column if not exists {} numeric").format(sql.Identifier(name)),
            sql.SQL("add column if not exists {} text").format(sql.Identifier(f"{name}__period_label")),
            sql.SQL("add column if not exists {} date").format(sql.Identifier(f"{name}__period_end")),
            sql.SQL("add column if not exists {} integer").format(sql.Identifier(f"{name}__formula_version")),
        ]
    conn.execute(sql.SQL("alter table analytics.company_screening_snapshot {}").format(sql.SQL(", ").join(parts)))

    end = date(2025, 12, 31)
    spec = {
        # key: (status, rgy value, rgy label, roe value)
        "P": ("active", Decimal("0.25"), "FY", Decimal("0.10")),
        "F": ("active", Decimal("0.05"), "FY", None),
        "H": ("active", None, "FY", Decimal("0.60")),
        "T": ("active", None, None, None),
        "G": ("active", None, None, None),
        "I": ("inactive", None, None, None),
    }
    ids = {}
    for i, (key, (status, rgy, rgy_label, roe)) in enumerate(spec.items()):
        cik = f"099000{i:04d}"
        cid = conn.execute(
            "insert into core.company (cik, company_name) values (%s, %s) returning id", (cik, f"Co {key}")
        ).fetchone()[0]
        ids[key] = cid
        conn.execute(
            "insert into analytics.company_screening_snapshot "
            "(company_id, cik, company_name, sic_code, status, dataset_version, "
            " revenue_growth_yoy, revenue_growth_yoy__period_label, revenue_growth_yoy__period_end, "
            " revenue_growth_yoy__formula_version, roe, roe__period_label, roe__period_end, roe__formula_version) "
            "values (%s, %s, %s, '7372', %s, %s, %s, %s, %s, 1, %s, %s, %s, 1)",
            (
                cid, cik, f"Co {key}", status, VERSION,
                rgy, rgy_label, end if rgy_label else None,
                roe, "FY" if roe is not None else None, end if roe is not None else None,
            ),
        )
    conn.execute(
        "insert into analytics.metric_value (company_id, metric_definition_id, period_start, period_end, "
        "period_label, value, is_null_reason) values (%s, %s, '2025-01-01', %s, 'FY', null, %s)",
        (ids["H"], catalog["revenue_growth_yoy"], end, "missing:prior_period(2024_FY)"),
    )
    conn.execute(
        "insert into analytics.company_data_point_template (company_id, data_point, in_template, reason, "
        "effective_from, template, source, template_version) "
        "values (%s, 'revenue_growth_yoy', false, 'not meaningful for this sector', '2020-01-01', "
        "'test', 'company_override', 'v1')",
        (ids["T"],),
    )
    return catalog, ids


def _flat(include_missing=False) -> ScreenQuery:
    return ScreenQuery.model_validate(
        {"metric_predicates": [{"metric_name": "revenue_growth_yoy", "operator": ">", "value": "0.10",
                                "include_missing": include_missing}]}
    )


def _where(include_missing=False) -> ScreenQuery:
    return ScreenQuery.model_validate(
        {"where": {"op": "and", "predicates": [{"metric_name": "revenue_growth_yoy", "operator": ">",
                                                 "value": "0.10", "include_missing": include_missing}]}}
    )


def _by_key(result, ids):
    inv = {v: k for k, v in ids.items()}
    matched = sorted(inv[m["company_id"]] for m in result["matched"])
    cik_to_key = {f"099000{i:04d}": k for i, k in enumerate("PFHTGI")}
    excluded = {cik_to_key[e["cik"]]: e for e in result["excluded_missing_data"]}
    return matched, excluded


@pytest.fixture
def db(isolated_database_url):
    with psycopg.connect(isolated_database_url) as conn:
        catalog, ids = _build(conn)
        yield conn, catalog, ids
        conn.rollback()


def _assert_invariant(result, matched, excluded, not_matched):
    s = result["exclusion_summary"]
    assert s["total_candidates"] == 5  # five active companies in this version, the inactive one is not a candidate
    assert (s["matched"], s["excluded"], s["not_matched"]) == (matched, excluded, not_matched)
    assert s["matched"] + s["excluded"] + s["not_matched"] == s["total_candidates"]
    assert s["matched"] == len(result["matched"]) and s["excluded"] == len(result["excluded_missing_data"])


@pytest.mark.integration
@pytest.mark.parametrize("make", [_flat, _where], ids=["flat", "where"])
def test_every_excluded_company_has_a_reason_and_counts_add_up(db, make):
    conn, catalog, ids = db
    result = run_query(conn, make(), dataset_version=VERSION, catalog=catalog)
    matched, excluded = _by_key(result, ids)
    assert matched == ["P"]
    assert set(excluded) == {"H", "T", "G"}
    buckets = {k: e["reasons"]["revenue_growth_yoy"]["bucket"] for k, e in excluded.items()}
    assert buckets == {"H": "history_horizon", "T": "not_in_template", "G": "open_gap"}
    assert excluded["H"]["reasons"]["revenue_growth_yoy"]["code"] == "missing:prior_period(2024_FY)"
    assert excluded["T"]["reasons"]["revenue_growth_yoy"]["code"] == "not meaningful for this sector"
    assert excluded["G"]["reasons"]["revenue_growth_yoy"]["code"] == "no_row"
    s = result["exclusion_summary"]
    assert s["by_bucket"] == {"not_in_template": 1, "history_horizon": 1, "open_gap": 1}
    assert s["by_metric"] == {"revenue_growth_yoy": {"not_in_template": 1, "history_horizon": 1, "open_gap": 1}}
    _assert_invariant(result, matched=1, excluded=3, not_matched=1)


@pytest.mark.integration
@pytest.mark.parametrize("make", [_flat, _where], ids=["flat", "where"])
def test_include_missing_keeps_companies_without_a_value_with_their_reason(db, make):
    conn, catalog, ids = db
    result = run_query(conn, make(include_missing=True), dataset_version=VERSION, catalog=catalog)
    matched, excluded = _by_key(result, ids)
    assert matched == ["G", "H", "P", "T"]
    assert excluded == {}
    inv = {v: k for k, v in ids.items()}
    cells = {inv[m["company_id"]]: m["metrics"]["revenue_growth_yoy"] for m in result["matched"]}
    assert cells["P"]["value"] == Decimal("0.25") and "missing" not in cells["P"]
    assert {k: cells[k]["missing"]["bucket"] for k in "HTG"} == {
        "H": "history_horizon", "T": "not_in_template", "G": "open_gap"}
    assert all(cells[k]["value"] is None for k in "HTG")
    _assert_invariant(result, matched=4, excluded=0, not_matched=1)


@pytest.mark.integration
def test_where_or_reports_not_matched_companies_with_a_missing_leaf(db):
    conn, catalog, ids = db
    query = ScreenQuery.model_validate({"where": {"op": "or", "predicates": [
        {"metric_name": "revenue_growth_yoy", "operator": ">", "value": "0.10"},
        {"metric_name": "roe", "operator": ">", "value": "0.5"},
    ]}})
    result = run_query(conn, query, dataset_version=VERSION, catalog=catalog)
    matched, excluded = _by_key(result, ids)
    assert matched == ["H", "P"]  # H has no growth value but matches through roe
    assert {k: e["missing_metrics"] for k, e in excluded.items()} == {
        "F": ["roe"], "T": ["revenue_growth_yoy", "roe"], "G": ["revenue_growth_yoy", "roe"]}
    assert result["exclusion_summary"]["by_bucket"] == {"not_in_template": 1, "open_gap": 2}
    _assert_invariant(result, matched=2, excluded=3, not_matched=0)


@pytest.mark.integration
def test_a_saved_run_page_recomputes_the_same_reasons_and_summary(db):
    conn, catalog, ids = db
    result = run_query(conn, _flat(), dataset_version=VERSION, catalog=catalog)
    cik_to_id = {f"099000{i:04d}": ids[k] for i, k in enumerate("PFHTGI")}
    stored = [  # what app.screen_result keeps, resolved back to ids/sic the way _read_page does
        {"cik": e["cik"], "company_name": e["company_name"], "missing_metrics": e["missing_metrics"],
         "company_id": cik_to_id[e["cik"]], "sic_code": "7372"}
        for e in result["excluded_missing_data"]
    ]
    excluded, summary = explain_stored_exclusions(
        conn, VERSION, stored, total_candidates=5, matched=len(result["matched"]), catalog=catalog)
    assert [e["reasons"] for e in excluded] == [e["reasons"] for e in result["excluded_missing_data"]]
    assert summary == result["exclusion_summary"]
