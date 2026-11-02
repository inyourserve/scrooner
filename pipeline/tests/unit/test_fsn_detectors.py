"""fsn_store.detectors: the capex / D&A lane (cf_da_capex_variants.evaluate, imported) as a map_filing detector.

Pure tests run decide() on real lane-shaped filing objects (cf_face_extract.py rows of the SEC FSN sets,
pipeline/tests/fixtures/fsn_cf_detectors/lane_filings.jsonl.gz). The integration test loads one real JPM 10-K
company directory into an isolated test database and maps it with the committed seeds, with and without the
detector (data-team/strategy/team/CAPEX-DA-DEBT-PORT-2026-11-01.md)."""

import gzip
import json
from pathlib import Path

import psycopg
import pytest

from scrooner_pipeline.fsn_store import detectors, load, mapping, rules

ROOT = Path(__file__).resolve().parents[3]
FX = ROOT / "pipeline" / "tests" / "fixtures" / "fsn_cf_detectors"
DA, CAPEX = detectors.DA, detectors.CAPEX


def _filings():
    return {(f["ticker"], f["period"]): f for f in map(json.loads, gzip.open(FX / "lane_filings.jsonl.gz", "rt"))}


def test_msft_combined_da_line_stays_combined():
    """Verifier: MSFT "Depreciation, amortization, and other" is combined, never D&A; capex maps its one line."""
    d = detectors.decide(_filings()[("MSFT", "20240630")])
    assert d[DA]["status"] == "held" and "da_combined_with_other_items" in d[DA]["reasons"]
    assert d[DA]["combined"]  # the combined line is returned `combined`
    assert d[CAPEX]["status"] == "mapped" and d[CAPEX]["tag"] == "PaymentsToAcquirePropertyPlantAndEquipment"


def test_hd_da_decided_per_filing_by_the_lane_release_class():
    """HD prints one cash-flow D&A line before FY2025 (one asset_da member per filing), but its income statement prints
    a different D&A total; the lane's release classes publish a single CF line only without an IS total or when they
    tie, so the Verifier-passed file holds every HD D&A cell. The decision is per filing: FY2019 holds for the IS
    difference, FY2024 for two asset lines."""
    f = _filings()
    one, two = detectors.decide(f[("HD", "20200131")]), detectors.decide(f[("HD", "20250131")])
    assert one[DA]["status"] == "held" and one[DA]["reasons"] == ["da_multi_member_unverified"]
    assert two[DA]["status"] == "held"
    assert one[CAPEX]["status"] == "mapped" and one[CAPEX]["tag"] == "PaymentsToAcquireProductiveAssets"


def test_single_da_line_maps_once_per_filing():
    f = _filings()
    w = detectors.decide(f[("WMT", "20240131")])
    assert w[DA]["status"] == "mapped" and w[DA]["stmt"] == "CF"
    j = detectors.decide(f[("JPM", "20231231")])
    assert j[DA]["status"] == "mapped" and j[DA]["tag"] == "DepreciationAmortizationAndAccretionNet"


def _flip_sign(monkeypatch, family, keys):
    """make the lane read a value with the opposite sign to the store's raw print for `family`"""
    lane = detectors._lane()
    real = lane.evaluate

    def evaluate(*a, **k):
        cells = real(*a, **k)
        for c in cells:
            if c["family"] == family:
                for key in keys:
                    if c.get(key) is not None:
                        c[key] = str(-detectors._dec(c[key]))
        return cells

    monkeypatch.setattr(lane, "evaluate", evaluate)


def test_raw_print_equal_to_the_lane_value_maps(monkeypatch):
    """control for the sign tests: untouched, the store's raw print equals the lane's value and the line maps"""
    d = detectors.decide(_filings()[("WMT", "20240131")])
    assert d[DA]["status"] == "mapped" and d[CAPEX]["status"] == "mapped"


def test_capex_print_with_the_opposite_sign_to_the_lane_value_holds(monkeypatch):
    """the lane reads signs as presented; a lane value of opposite sign to the store's raw print must hold the whole
    filing (store_print_differs_from_lane_value) instead of mapping a line whose stored value select would publish"""
    _flip_sign(monkeypatch, "capex", ("interim",))
    d = detectors.decide(_filings()[("WMT", "20240131")])
    assert d[CAPEX]["status"] == "held" and d[CAPEX]["tag"] is None
    assert "store_print_differs_from_lane_value" in d[CAPEX]["reasons"]
    assert d[DA]["status"] == "mapped"  # only the family whose print differs is held


def test_da_print_with_the_opposite_sign_to_the_lane_value_holds(monkeypatch):
    _flip_sign(monkeypatch, "d_and_a", ("value",))
    d = detectors.decide(_filings()[("WMT", "20240131")])
    assert d[DA]["status"] == "held" and "store_print_differs_from_lane_value" in d[DA]["reasons"]
    assert d[CAPEX]["status"] == "mapped"


def test_net_da_label_failed_in_another_filing_is_held_here_too():
    """Verifier V11 (KEY FY2023): once a company's "net" D&A label fails V10 in one filing, the lane holds that label
    in every period. decide() takes the labels that failed elsewhere and holds the column that carries one."""
    f = _filings()[("WMT", "20240131")]
    base = detectors.decide(f)[DA]
    assert base["status"] == "mapped" and base["labels"]
    carried = detectors.decide(f, set(base["labels"]))[DA]
    assert carried["status"] == "held" and carried["tag"] is None
    assert carried["reasons"] == [detectors.NET_CARRIED]
    other = detectors.decide(f, {"a label this filing does not print"})[DA]
    assert other["status"] == "mapped"  # a different label is not touched


def _one(conn, sql, params=()):
    return conn.execute(sql, params).fetchone()[0]


@pytest.fixture
def conn(isolated_database_url):
    c = psycopg.connect(isolated_database_url)
    if _one(c, "select count(*) from information_schema.tables where table_schema = 'fsn' and table_name in ('filing', 'line', 'concept_rule')") != 3:
        c.close()
        pytest.skip("needs migration 0118")
    yield c
    c.close()


@pytest.mark.integration
def test_detector_leaves_one_da_line_where_the_seeds_map_several(conn):
    """JPM FY2023 10-K: the seeds map several lines to D&A (the pilot's conflicting_values_in_filing); with the detector
    exactly the lane's one line is mapped and every other seed-mapped D&A line is unmapped with the lane's evidence."""
    for name, stmt in ((DA, "cash_flow"), (CAPEX, "cash_flow"), ("cfo_resolved", "cash_flow")):
        conn.execute("insert into analytics.canonical_concept (name, statement, combination_mode) values (%s, %s, 'first_match') "
                     "on conflict (name) do nothing", (name, stmt))
    cid = _one(conn, "insert into core.company (cik, company_name) values ('0000019617', 'JPM TEST') returning id")
    conn.commit()
    load.load_company(conn, FX / "0000019617", loader_commit="test")
    conn.commit()
    res = rules.seed(conn, ROOT / "data-team" / "47-fsn-store" / "concept_rules" / "cf.jsonl", apply=True)
    assert not res["errors"], res["errors"]
    conn.commit()
    fid = _one(conn, "select id from fsn.filing where accession = '0000019617-24-000225'")
    da_id = _one(conn, "select id from analytics.canonical_concept where name = %s", (DA,))
    rule_set = mapping.load_rules(conn)

    def mapped_da():
        return _one(conn, "select count(*) from fsn.line_map where filing_id = %s and canonical_concept_id = %s and status = 'mapped'", (fid, da_id))

    mapping.map_filing(conn, fid, rule_set)
    seeds_only = mapped_da()
    mapping.map_filing(conn, fid, rule_set, detectors=detectors.DEFAULT)
    assert seeds_only >= 2  # the conflict the pilot reported
    assert mapped_da() == 1
    held = _one(conn, "select count(*) from fsn.line_map where filing_id = %s and rule_id = 'cf.capex_da_held@1'", (fid,))
    assert held >= seeds_only - 1
    _ = cid


def test_a_filing_holds_when_any_of_its_columns_holds():
    """AWK 10-Q 2015-03-31: one D&A column publishes, the other holds. select reads a mapped line in EVERY column of
    the filing, so mapping the line would publish the held column too: the whole filing holds (decided per filing)."""
    d = detectors.decide(_filings()[("AWK", "20150331")])
    assert d[DA]["status"] == "held"
    assert "da_multi_member_unverified" in d[DA]["reasons"]
