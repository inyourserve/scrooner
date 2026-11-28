"""Guard rail: a change to the proof's verdict logic must bump a version (ONE-PATH step 1, 2026-11-16).

Two pins. (1) Code a rule OWNS (proof/rules.py Rule.owners) is fingerprinted per rule: editing an owner function
fails until that rule's `version` is bumped and its pin here is re-set. Only the cells that used the rule are
re-proved. (2) Everything else in the verdict sources is pinned together with the global floor DETECTOR_VERSION
(proof/prove.py): a change there bumps the floor and re-proves every cell, exactly as before.

Original rationale of the floor:

The mapper's proof guard (company_tag_map._load_proof_disagree) reads only proof rows of the CURRENT detector
version. If prove.py / shown.py change what a verdict means but the version stays, old DISAGREE rows keep
holding cells the fixed proof never re-judges (MSFT sga_expense FY2016-17, 2026-11-13).

How: a sha256 of the AST (comments and formatting do not count) of every verdict-relevant source is pinned next
to the version it belongs with. Editing any of them fails this test until the pin is updated TOGETHER with a
DETECTOR_VERSION bump (a pure refactor that keeps verdicts the same may re-pin the hash with the same version,
said so in the commit message).
"""

from __future__ import annotations

import ast
import hashlib
from pathlib import Path

from scrooner_pipeline.proof.prove import DETECTOR_VERSION
from scrooner_pipeline.proof.rules import RULES

SRC = Path(__file__).resolve().parents[2] / "src" / "scrooner_pipeline"
VERDICT_SOURCES = (
    "proof/prove.py",
    "proof/shown.py",
    "proof/dims.py",
    "proof/identities.py",
    "proof/perimeter.py",
    "proof/fsn_db.py",
    "common/filer_xbrl_errors.py",
    "common/filer_calc_lift.py",
    "common/fsn_dropped_facts.py",
    "common/authority.py",
    "common/presentation_scale.py",
    "common/tag_aliases.py",
    "common/instance_facts.py",
    "common/polarity.py",
)

PINNED_VERSION = "cell_proof_v21_2026-11-16"
# 2026-11-29: same floor; renamed_part_printed (rule component_sum_authority v3, resolver_beats_combined v5): an absent-part zero is vetoed when the column prints the line under a renamed component tag (IBM total_debt FY2019-21)
# 2026-11-28: re-pinned at the same floor; common/authority.py reads face rows through the local FSN read cache (egress fix), same rows, no verdict change
# 2026-11-22: re-pinned at the same floor; prove_component moved under rule component_parts (v2), no floor change
# 2026-11-22: re-pinned at the same floor; stated_family_concepts added to shown.py (loads cells that had no proof row), no verdict changes; rule resolver_beats_combined v2 (load_shown)
# 2026-11-23 (resolver .90): re-pinned at the same floor; the verdict changes live in the new rules authority_tag_sum,
# authority_copy_role, printed_zero_note and element_family (their call sites in locate/prove_note/load_shown and the
# Shown.authority_skips field change no verdict a rule does not select); resolver_beats_combined v3 (load_shown)
# 2026-11-28: same floor and hash; the identity web (3b15184b7) moved out of proof/identities.py into
# proof/identity_web.py (certification only, no verdict caller). Rule pins: e5f031779 authority_tag_sum v2,
# resolver_beats_combined v4 (load_shown).
# 2026-11-29 (Stage 4 Prove, M1): re-pinned at the same floor; prove.py gains the DEBT_COMPOSITION_TAGS constant and the
# call site of the new rule debt_composition in _prove_cell. The call returns None (old path unchanged) for every cell
# the rule does not select (total_debt_resolved without a claim, composition tags only); the verdicts that change are
# the rule's (legacy_version 0, so the rule-scoped re-prove selects exactly them).
PINNED_HASH = "aeb09f6fecca9763c2fe44aaff97796c3847ff1e93f3bda6aae338df44f116b9"
# rule id -> (rule version, fingerprint of its owner functions); only rules that own code are listed
RULE_PINS = {
    "identity_tie": (
        1,
        "b94e6b59a25fcc2327c812959fa1e8f4711efac36d91e3b7af754131cde88734",
    ),
    "components_sum": (
        1,
        "80c19adb6ce597f70cc7d8e1eab8ab4f35fcce2a4da2c1ea6adf43a35ed69587",
    ),
    "component_parts": (
        3,
        "8238832bae65593ba5beaf09b8832bc840d6f436be7af1c0e86d419b004bf94c",
    ),
    "non_interest_band": (
        1,
        "4ac1940ff6c942d8b4227374b56001d624883f5dc3a62704a2b9da9ee5fed0e0",
    ),
    "component_sum_authority": (
        3,
        "749f4d585ca3f87988255c6e2fc9720f404403f8192015a983e7480ea6eef2f7",
    ),
    "resolver_beats_combined": (
        5,
        "9d34e1d7692dcb371412e2b86f1902ff0c25fbb098ed711b795261c41e71d009",
    ),
    "authority_tag_sum": (
        2,
        "ef75b7c7fa50f6417eca3ad6d71c4a319188d1e8caaeb91b26a9e0c5ded4a1ba",
    ),
    "authority_copy_role": (
        1,
        "ca3ac64963767553da2ebd76f35e3e43c582d3f97506756467156d62babbd991",
    ),
    "printed_zero_note": (
        1,
        "80221d028b398be5c526669337babeb7394dc7bf2e9b15c52b5c01364314d47c",
    ),
    "element_family": (
        1,
        "33c822dfcc25cd85d35d8a0673f4648f39e433ed0c7de5b3855407d4a613393b",
    ),
    "split_parts": (
        2,
        "a0680a9dd345c1e43f261f5a685ac97466d047564527d875e30ff4e55918d364",
    ),
    "stated_zero": (
        1,
        "c69cb33c7d31bdd099334c657ac49296a6c3a9150c0e69466be406db9fdc6b5f",
    ),
    "text_stated": (
        1,
        "4c0d6c12693cd5225b11b41d775bc64af17234db1efd2e27390d14320abd2059",
    ),
    "debt_composition": (
        1,
        "ce3fc78c8168e0f76a0d48d45e3c3d398a96879fd32916ce905fe11d16ab8c7b",
    ),
}


# EVERY rule's version, owner or not (2026-11-22). A version bump makes every proof row that used the rule NOT current:
# coverage shows those cells as UNCHECKED proof_stale (mapper/top100_coverage.py) until a rule-scoped
# `scrooner-proof run --write` re-proves them (the top100_flow.sh proof step, or for every affected company at once
# `scrooner-proof run --ciks <top-100> --write --only-stale`). The hourly export is read-only and only reports them.
# So a bump is not done when this pin is re-set: it is done when the re-prove has run (the component_parts v1->v3 bumps
# left ~460 PROVEN cells reported as missing proof, open shown 1,485 -> 1,648, values unchanged).
RULE_VERSIONS = {
    "claim": 1,
    "period_length": 1,
    "statement_face": 1,
    "identity_tie": 1,
    "components_sum": 1,
    "unit_scale": 1,
    "component_parts": 3,
    "printed_zero": 1,
    "restated_history": 1,
    "pre_filing": 1,
    "derivation": 1,
    "non_interest_band": 1,
    "filer_xbrl_correction": 1,
    "quarantine_lifted": 1,
    "perimeter": 1,
    "identities": 1,
    "component_sum_authority": 3,
    "resolver_beats_combined": 5,
    "authority_tag_sum": 2,
    "authority_copy_role": 1,
    "printed_zero_note": 1,
    "element_family": 1,
    "split_parts": 2,
    "stated_zero": 1,
    "text_stated": 1,
    "debt_composition": 1,
}


def _owner_nodes(tree: ast.Module, rel: str) -> dict[str, ast.FunctionDef]:
    wanted = {
        o.split(":")[1]
        for r in RULES.values()
        for o in r.owners
        if o.split(":")[0] == rel
    }
    return {
        n.name: n
        for n in tree.body
        if isinstance(n, ast.FunctionDef) and n.name in wanted
    }


def source_hash() -> str:
    """Floor pin: every verdict source with the owner functions of every rule blanked (their bodies are pinned per rule)."""
    h = hashlib.sha256()
    for rel in VERDICT_SOURCES:
        tree = ast.parse((SRC / rel).read_text())
        for fn in _owner_nodes(tree, rel).values():
            fn.body = [ast.Pass()]
        for node in ast.walk(tree):  # DETECTOR_VERSION's own value is pinned separately
            if isinstance(node, ast.Assign) and any(
                getattr(t, "id", "") == "DETECTOR_VERSION" for t in node.targets
            ):
                node.value = ast.Constant("")
        h.update(rel.encode() + ast.dump(tree).encode())
    return h.hexdigest()


def rule_hash(rule_id: str) -> str:
    h = hashlib.sha256()
    for owner in RULES[rule_id].owners:
        rel, name = owner.split(":")
        tree = ast.parse((SRC / rel).read_text())
        fn = _owner_nodes(tree, rel)[
            name
        ]  # KeyError = the registry names a function that is gone
        h.update(owner.encode() + ast.dump(fn).encode())
    return h.hexdigest()


def test_verdict_logic_change_needs_detector_version_bump():
    assert PINNED_VERSION == DETECTOR_VERSION, (
        "DETECTOR_VERSION changed: set PINNED_VERSION and PINNED_HASH here to match"
    )
    assert source_hash() == PINNED_HASH, (
        "a verdict-relevant proof source NOT owned by a rule changed. If verdicts can differ, bump the floor "
        "DETECTOR_VERSION in proof/prove.py (re-proves every cell) or move the code under a rule's owners in "
        "proof/rules.py; then set PINNED_VERSION and PINNED_HASH here to "
        f"{source_hash()}"
    )


def test_rule_owner_change_needs_rule_version_bump():
    owned = {rid for rid, r in RULES.items() if r.owners}
    assert owned == set(RULE_PINS), (
        "every rule with owners needs a pin here, and no pin without a rule"
    )
    for rid, (version, fp) in RULE_PINS.items():
        assert RULES[rid].version == version, (
            f"rule {rid} is at version {RULES[rid].version}, pin says {version}: re-set the pin together"
        )
        assert rule_hash(rid) == fp, (
            f"the code rule {rid} owns changed. Bump its version in proof/rules.py (only cells that used it are "
            f"re-proved), then set RULE_PINS[{rid!r}] to ({RULES[rid].version}, {rule_hash(rid)!r})"
        )


def test_every_rule_version_is_pinned_and_a_bump_names_the_reprove():
    current = {rid: r.version for rid, r in RULES.items()}
    assert current == RULE_VERSIONS, (
        "a rule version in proof/rules.py changed (or a rule was added/removed). Every proof row that used a bumped "
        "rule is now proof_stale in coverage until re-proved: run `scrooner-proof run --ciks <top-100> --write "
        "--only-stale` (rule-scoped, writes only the stale cells) or the top100_flow.sh proof step per company, then "
        f"set RULE_VERSIONS here to {current}"
    )
