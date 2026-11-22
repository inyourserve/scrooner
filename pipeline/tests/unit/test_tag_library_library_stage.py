"""The sec_tag_library stage is a thin reader of library.csv (2026-11-22, SYSTEMS.md #6: one tag library).

Before, it re-derived mapping status, concepts and metrics from the retired analytics.concept_mapping /
concept_tag_candidate. Now usage comes from company_sec_tag and every knowledge column from library.csv."""

import psycopg
import pytest

from scrooner_pipeline.mapper import tag_library

HEAD = "element,taxonomy,data_point,metrics,served_cells,proven_cells,certified_cells,full_row,company_overrides,legacy_decision\n"


@pytest.mark.integration
def test_library_stage_loads_status_data_points_and_metrics_from_library_csv(
    isolated_database_url, tmp_path
):
    lib = tmp_path / "library.csv"
    lib.write_text(
        HEAD
        + "Revenues,us-gaap,revenue,gross_margin;ps_ratio,40,30,5,yes,,\n"
        + "PaymentsToAcquireProductiveAssets,us-gaap,capex,,0,0,0,no,,\n"
        + "AcmeSpecialRevenue,custom,revenue,,3,0,0,no,,\n",
        encoding="utf-8",
    )
    conn = psycopg.connect(isolated_database_url)
    try:
        with conn.cursor() as cur:
            cur.execute(
                """insert into core.concept (taxonomy, tag) values
                   ('us-gaap', 'Revenues'), ('us-gaap', 'PaymentsToAcquireProductiveAssets'),
                   ('acme', 'AcmeSpecialRevenue'), ('us-gaap', 'AcmeSpecialRevenue'), ('us-gaap', 'UnknownTag')"""
            )
        conn.commit()
        stats = tag_library.build_tag_library(
            conn, stages={"library"}, library_path=lib
        )
        with conn.cursor() as cur:
            cur.execute(
                """select taxonomy || ':' || tag, mapping_status, mapped_concepts, candidate_for_concepts, feeds_metrics
                   from analytics.sec_tag_library order by 1"""
            )
            got = {r[0]: r[1:] for r in cur.fetchall()}
    finally:
        conn.close()
    assert stats["library_csv_rows"] == 3
    assert got["us-gaap:Revenues"] == (
        "approved",
        ["revenue"],
        [],
        ["gross_margin", "ps_ratio"],
    )
    assert got["us-gaap:PaymentsToAcquireProductiveAssets"] == (
        "candidate",
        [],
        ["capex"],
        [],
    )
    assert got["acme:AcmeSpecialRevenue"] == ("provisional", ["revenue"], [], [])
    # a company extension's name never maps a us-gaap concept, and an element the library does not know stays unmapped
    assert got["us-gaap:AcmeSpecialRevenue"][0] == "unmapped"
    assert got["us-gaap:UnknownTag"] == ("unmapped", [], [], [])
