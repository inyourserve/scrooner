"""The production FSN write's default data_points (.github/workflows/pipeline-fsn-write.yml).

The write keeps only cells whose data_point_name is in this list, so a name the store never emits is a silent
no-op and a name whose store rule is unsound writes wrong values to canonical_fact. Evidence:
data-team/strategy/team/FAMILY-RELEASE-CASE-2026-11-09.md."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
WORKFLOW = ROOT / ".github" / "workflows" / "pipeline-fsn-write.yml"
RULES = ROOT / "data-team" / "47-fsn-store" / "concept_rules"

# Families held out of the default until their store rule is fixed and the release approver clears them
# (FAMILY-RELEASE-CASE-2026-11-09 §2-3): the seed calc_position rules map ANY custom child of current
# liabilities as total debt and any custom child of Liabilities as total liabilities.
HELD = {"total_debt_resolved", "total_liabilities_resolved"}
# Seeded but never emitted by the pilot (FAMILY-RELEASE-CASE-2026-11-09 §6): CommonStockSharesOutstanding is a
# balance-sheet PARENTHETICAL line at most filers (mapping excludes inpth lines), and where it is a face line the
# pilot selects USD prints only, so its "shares" prints are dropped. Listing it implied coverage that never existed.
NEVER_EMITTED = {"shares_outstanding_resolved"}


def default_data_points() -> list[str]:
    text = WORKFLOW.read_text()
    m = re.search(
        r"^      data_points:\n(?:        .*\n)*?        default: \"([^\"]*)\"",
        text,
        re.MULTILINE,
    )
    assert m, "data_points input with a default not found"
    return m.group(1).split(",")


def seeded_concepts() -> set[str]:
    out: set[str] = set()
    for f in RULES.glob("*.jsonl"):
        if f.name.startswith("_"):
            continue
        out |= {
            json.loads(line)["canonical_concept"] for line in f.open() if line.strip()
        }
    return out


def test_default_names_are_seeded_store_concepts():
    names = default_data_points()
    assert len(names) == len(set(names)), "duplicate data point"
    assert all(n.endswith("_resolved") for n in names)
    missing = set(names) - seeded_concepts()
    assert not missing, (
        f"no concept rule seeds these, so the store never emits them: {sorted(missing)}"
    )


def test_held_families_stay_out_of_the_default():
    assert not HELD & set(default_data_points())


def test_no_name_the_pilot_never_emits():
    assert not NEVER_EMITTED & set(default_data_points())


def test_capex_and_da_are_in_the_default():
    names = set(default_data_points())
    assert {"capex_resolved", "depreciation_and_amortization_resolved"} <= names
