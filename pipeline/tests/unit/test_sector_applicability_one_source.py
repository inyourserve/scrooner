"""Backbone #12: sector applicability has ONE source (metrics/registry/data_points.csv + sectors.csv,
read through mapper/sector_templates.py; the bank metric list is the registry `bank_reason` column).

The scan fails if any module in pipeline/src, pipeline/scripts or apps/backend defines its own copy:
  * a literal table keyed by two or more sector template groups (a GROUP_OUT / SECTOR_OUT copy);
  * a function returning two or more sector group names (a sic_group copy);
  * a literal list of bank-suppressed metric ids next to a bank reason (a BANK_SUPPRESSED_METRICS copy).
"""

from __future__ import annotations

import ast
import csv
import shutil
from pathlib import Path

import pytest
from scrooner_pipeline.common import sector_applicability as sa
from scrooner_pipeline.mapper import sector_templates as st
from scrooner_pipeline.metrics import applicability as ma
from scrooner_pipeline.metrics.registry import (
    REGISTRY_DIR,
    SECTORS,
    RegistryError,
    get_registry,
    load_data_points,
    load_sectors,
)

ROOT = Path(__file__).resolve().parents[3]
SCAN = [
    ROOT / "pipeline/src/scrooner_pipeline",
    ROOT / "pipeline/scripts",
    ROOT / "apps/backend",
]
# Modules the scan matches that are kept on purpose, each with its reason; nothing else may.
LEGACY = {
    "pipeline/src/scrooner_pipeline/fsn_store/pilot.py": "frozen 2026-11-01 FSN pilot gate (jobs/fsn.py pilot"
    " commands): its SIC map and OUT sets predate the s8 approvals by design; retire with the pilot"
    " (SYSTEMS.md #25), never extend",
    "pipeline/src/scrooner_pipeline/pilot.py": "issuer_kind() is the Collector-era sampling stratum (SIC 6000-6099"
    " bank, reit, blank_check_candidate), not template applicability",
    "pipeline/scripts/slot_records/is_detect.py": "shape_of() reads a filing's own face tags (bank/insurer/bdc"
    " statement shape, evidence for a group), not a SIC map or an applicability set",
}
GROUPS = set(SECTORS)
BANK_REASONS = set(sa.BANK_SUPPRESSED_METRICS.values())
BANK_REASON_NAMES = {
    "NOT_APPLICABLE_TO_BANKS",
    "BANK_REVENUE_PENDING",
    "BANK_NII_PENDING",
}
BANK_METRICS = set(sa.BANK_SUPPRESSED_METRICS)


def _strs(nodes) -> set[str]:
    return {
        n.value
        for n in nodes
        if isinstance(n, ast.Constant) and isinstance(n.value, str)
    }


def _violations(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    text = path.read_text(encoding="utf-8")
    names_reason = any(r in text for r in BANK_REASONS | BANK_REASON_NAMES)
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Dict) and len(_strs(node.keys) & GROUPS) >= 2:
            out.append(f"line {node.lineno}: table keyed by sector groups")
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            rets = {
                n.value.value
                for n in ast.walk(node)
                if isinstance(n, ast.Return)
                and isinstance(n.value, ast.Constant)
                and n.value.value in GROUPS
            }
            if len(rets) >= 2:
                out.append(
                    f"line {node.lineno}: {node.name}() returns sector groups {sorted(rets)}"
                )
        if names_reason and isinstance(node, (ast.Tuple, ast.List, ast.Set, ast.Dict)):
            elts = node.keys if isinstance(node, ast.Dict) else node.elts
            if len(_strs(elts) & BANK_METRICS) >= 5:
                out.append(f"line {node.lineno}: literal bank-suppressed metric list")
    return out


def _scan() -> dict[str, list[str]]:
    found = {}
    for base in SCAN:
        for p in sorted(base.rglob("*.py")):
            rel = p.relative_to(ROOT).as_posix()
            if "/tests/" in rel or rel in LEGACY:
                continue
            v = _violations(p)
            if v:
                found[rel] = v
    return found


@pytest.mark.unit
def test_no_module_defines_its_own_applicability_set():
    assert _scan() == {}


@pytest.mark.unit
def test_the_scan_catches_a_copy(tmp_path):
    copy = tmp_path / "copy.py"
    copy.write_text(
        'OUT = {"bank": {"inventory"}, "insurer": {"capex"}}\n'
        'def group(sic):\n    if sic == 6021:\n        return "bank"\n    return "general"\n'
        'R = "not applicable to banks"\n'
        'M = ("ebitda", "fcf", "current_ratio", "quick_ratio", "working_capital")\n'
    )
    assert len(_violations(copy)) == 3
    for legacy in LEGACY:
        assert _violations(ROOT / legacy), (
            f"{legacy} no longer holds a copy: drop it from LEGACY"
        )


@pytest.mark.unit
def test_the_three_modules_read_the_registry():
    dps = load_data_points()
    for (dp, sector), d in dps.items():
        assert st.data_point_applies(dp, sector) == d.applies, (dp, sector)
        assert st.data_point_applies(f"{dp}_resolved", sector) == d.applies
    assert ma.GROUP_OUT is st.GROUP_OUT and ma.GROUP_ONLY is st.GROUP_ONLY
    assert ma.BANK_FAMILY_GROUPS == {"bank", "lender"}
    assert ma.INSURER_FAMILY_GROUPS == {"insurer"}
    reg = get_registry()
    assert sa.BANK_SUPPRESSED_METRICS == {
        k: m.bank_reason
        for k, m in reg.items()
        if m.tier != "planned" and m.bank_reason
    }
    sectors = load_sectors()
    assert tuple(sectors) == SECTORS
    for s, d in sectors.items():
        for cik in d.ciks:
            assert st.sic_group(cik, 7372) == s
        for lo, hi in d.sic_ranges:
            assert (
                st.sic_group("0000000001", lo) == s
                and st.sic_group("0000000001", hi) == s
            )
    assert st.sic_group("0000000001", None) == "general"


@pytest.mark.unit
def test_bdc_total_investment_income_is_bdc_only():
    assert st.GROUP_ONLY["bdc_total_investment_income"] == frozenset({"bdc"})
    cat = {
        r["name"]
        for r in csv.DictReader(
            (
                ROOT / "data-team/47-fsn-store/company_tag_map/concepts_catalog.csv"
            ).open()
        )
    }
    gated = set(st.GROUP_ONLY) | {dp for v in st.GROUP_OUT.values() for dp in v}
    assert gated <= cat, sorted(gated - cat)


@pytest.mark.unit
def test_sectors_loader_rejects_bad_rows(tmp_path):
    copy = tmp_path / "registry"
    shutil.copytree(REGISTRY_DIR, copy)
    f = copy / "sectors.csv"
    text = f.read_text()
    assert load_sectors(copy)
    bad = [
        text.replace("6798", "6022", 1),  # SIC overlap with bank
        text.replace(",0001287750;", ",0002065601;", 1),  # one CIK in two sectors
        text.replace("lender,bank,", "lender,banking,", 1),  # unknown metric family
        text.replace("bank,bank,6021-6022", "bank,bank,6022-6021", 1),  # reversed range
        text.replace(",corporate,default,", ",corporate,,", 1),  # no default sector
    ]
    for b in bad:
        assert b != text
        f.write_text(b)
        with pytest.raises(RegistryError):
            load_sectors(copy)
