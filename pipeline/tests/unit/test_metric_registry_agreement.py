"""The metric registry is the one source; every other copy must agree with it, for every metric.

tests/fixtures/metrics/legacy_snapshot.json is the frozen pre-registry state (captured 2026-11-13
from mapper/definitions.py, mapper/expanded_definitions.py, apps/backend/metric_catalog.py and the
calculate.py / ttm.py tables). The generated copies must reproduce it exactly (formulas are frozen
until top-100 certification); any difference is a drift-driven change and must be a listed fix.
"""

from __future__ import annotations

import csv
import json
import shutil
import sys
from pathlib import Path

import pytest

from scrooner_pipeline.common.sector_applicability import BANK_SUPPRESSED_METRICS
from scrooner_pipeline.mapper import calculate as C
from scrooner_pipeline.mapper import ttm as TTM
from scrooner_pipeline.mapper.definitions import METRIC_DEFINITIONS as V1
from scrooner_pipeline.mapper.expanded_definitions import METRIC_DEFINITIONS as EXPANDED
from scrooner_pipeline.mapper.main_calculator import METRIC_CALCULATOR_REGISTRY as CALC
from scrooner_pipeline.metrics import generate, lock
from scrooner_pipeline.metrics.registry import (
    REGISTRY_DIR, RegistryError, compute_registry_version, get_registry, load_registry, unknown_identifiers,
)

REPO = Path(__file__).resolve().parents[3]
SNAP = json.loads((Path(__file__).resolve().parents[1] / "fixtures/metrics/legacy_snapshot.json").read_text())
sys.path.insert(0, str(REPO / "apps/backend"))
import metric_catalog  # noqa: E402  (plain module, imports only the registry)

REG = get_registry()
SERVED = {k: m for k, m in REG.items() if m.tier != "planned"}


def _norm(rows):
    return {r[0]: json.loads(json.dumps(r[1:])) for r in rows}


@pytest.mark.unit
def test_registry_has_the_expected_metric_count_and_unique_ids():
    assert len(SERVED) == len(SNAP["order"]) == 82
    assert len(set(SNAP["order"])) == 82
    assert set(SERVED) == set(SNAP["order"])
    assert {k for k, m in REG.items() if m.tier == "planned"} == {"efficiency_ratio", "combined_ratio"}


@pytest.mark.unit
def test_pipeline_definitions_equal_the_frozen_pre_registry_copy():
    assert _norm(V1) == _norm(SNAP["v1"])
    assert _norm(EXPANDED) == _norm(SNAP["expanded"])
    assert len(V1) == 20


@pytest.mark.unit
def test_generic_engine_tables_equal_the_frozen_copy():
    assert C.FORMULA_SHAPES == SNAP["formula_shapes"]
    assert sorted(C.FY_ONLY_METRICS) == SNAP["fy_only"]
    assert {k: sorted(v) for k, v in C.ZERO_WHEN_ABSENT_CONCEPTS.items()} == SNAP["zero_when_absent"]
    assert {k: list(v) for k, v in TTM.GROWTH_METRICS.items()} == SNAP["growth_metrics"]


@pytest.mark.unit
def test_backend_catalog_presentation_equals_the_frozen_copy_and_never_falls_back():
    assert {
        k: [v.display_name, v.short_definition, v.category, v.value_type]
        for k, v in metric_catalog.METRIC_PRESENTATION.items()
    } == SNAP["presentation"]
    for mid, m in SERVED.items():
        p = metric_catalog.presentation_for(mid)
        assert (p.display_name, p.short_definition, p.category, p.value_type) == (
            m.label, m.short_definition, m.family, m.value_type)
        assert p.category != "Other" and p.short_definition != "Defined Scrooner metric."
        assert p.display_name != mid.replace("_", " ").title() or m.label == mid.replace("_", " ").title()


@pytest.mark.unit
def test_render_contract_every_metric_has_complete_display_metadata():
    for mid, m in REG.items():
        for col in ("label", "short_definition", "family", "unit", "value_type", "formula_description"):
            assert getattr(m, col).strip(), (mid, col)
        assert generate.formula_text(m).startswith(m.label)


@pytest.mark.unit
def test_calculator_module_agrees_with_the_main_calculator_registry():
    for mid, m in SERVED.items():
        assert CALC[mid]["module"] == m.calculator, mid


@pytest.mark.unit
def test_engine_deferral_sets_agree_with_the_registry():
    deferred = C.DEFERRED_TO_STAGE_3E | C.DEFERRED_TO_EXPANDED_METRICS
    for mid, m in SERVED.items():
        generic = m.expression_status == "engine_wired"
        priced = m.requires_price
        assert (mid in deferred) == (not generic and not priced), mid
        assert (mid in C.FORMULA_SHAPES) == generic, mid


@pytest.mark.unit
def test_bank_suppression_list_agrees_with_registry_bank_reason_both_ways():
    reg = {mid: m.bank_reason for mid, m in SERVED.items() if m.bank_reason}
    assert reg == BANK_SUPPRESSED_METRICS


@pytest.mark.unit
def test_every_expression_identifier_is_a_known_concept_or_metric():
    catalog = {r["name"] for r in csv.DictReader(
        (REPO / "data-team/47-fsn-store/company_tag_map/concepts_catalog.csv").open())}
    assert unknown_identifiers(REG, catalog) == {}


@pytest.mark.unit
def test_formulas_are_frozen_by_the_lock_until_a_version_bump():
    assert lock.lock_problems() == []


@pytest.mark.unit
def test_registry_version_is_a_hash_of_the_files(tmp_path):
    a = compute_registry_version()
    copy = tmp_path / "registry"
    shutil.copytree(REGISTRY_DIR, copy)
    assert compute_registry_version(copy) == a
    f = copy / "returns.csv"
    f.write_text(f.read_text().replace("Return on equity (ROE)", "Return on equity (ROE) x", 1))
    assert compute_registry_version(copy) != a


@pytest.mark.unit
def test_loader_rejects_bad_rows(tmp_path):
    copy = tmp_path / "registry"
    shutil.copytree(REGISTRY_DIR, copy)
    f = copy / "returns.csv"
    text = f.read_text()
    f.write_text(text.replace("net_income / stockholders_equity", "net_income / __import__(stockholders_equity)", 1))
    with pytest.raises(Exception):
        load_registry(copy)
    f.write_text(text.replace("net_income / stockholders_equity", "net_income ** 2", 1))
    with pytest.raises(Exception):
        load_registry(copy)
    f.write_text(text.replace("Returns,Return on equity (ROE)", "Returns,", 1))
    with pytest.raises(RegistryError):
        load_registry(copy)


@pytest.mark.unit
def test_perimeter_metadata_for_ebitda_fcf_roic_is_explicit():
    assert REG["ebitda"].perimeter_spec["addbacks"] == "none"
    assert REG["ebitda"].perimeter_spec["da_source"] == "cash_flow_statement"
    assert "leased_fleets" in REG["fcf"].perimeter_spec["capex_includes"]
    assert "oil_gas" in REG["fcf"].perimeter_spec["capex_excludes"]
    assert REG["roic"].perimeter_spec["operating_leases"] == "excluded_from_invested_capital"
    assert REG["roic"].perimeter_spec["finance_leases"] == "included_in_total_debt"
