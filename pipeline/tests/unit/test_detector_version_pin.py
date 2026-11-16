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
PINNED_HASH = "a16f14cd30f96b770a7b529af95322af56a83422b622b323d7b52627a5d2f425"
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
    "non_interest_band": (
        1,
        "4ac1940ff6c942d8b4227374b56001d624883f5dc3a62704a2b9da9ee5fed0e0",
    ),
    "component_sum_authority": (
        2,
        "33d1e97595eeda814ef895ed873996455c08ff8d4c1e7c5dd05597b26c3a5c81",
    ),
    "split_parts": (
        1,
        "f9de84f1ed2fb4feeb5f3ed7fcf9749ef6baf95cf5b0fd7f49ba48cc8d3f19cd",
    ),
    "text_stated": (
        1,
        "4c0d6c12693cd5225b11b41d775bc64af17234db1efd2e27390d14320abd2059",
    ),
    "stated_zero": (
        1,
        "c69cb33c7d31bdd099334c657ac49296a6c3a9150c0e69466be406db9fdc6b5f",
    ),
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
