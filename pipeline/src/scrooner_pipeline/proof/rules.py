"""Rule registry for the cell proof: which rules a verdict used, and at what version (ONE-PATH step 1, founder
decision 2026-11-16, data-team/strategy/ONE-PATH-DESIGN-2026-11-16.md).

Why: any change to the proof used to bump the one global DETECTOR_VERSION, and coverage reads only rows of the current
version, so every change re-proved every cell (92% of open cells were `no_proof_row`). Now:

  * every verdict records the rules it used in analytics.cell_proof.checks['rules'] = {rule_id: version}
    (no migration). The record is built by `rules_used` from what ACTUALLY ran: a check key written into `checks`, or
    a Shown predicate for a rule that judges without writing a key. It is never declared by hand per cell;
  * a rule change bumps ONLY that rule's `version` here. A cell is re-proved when a rule it used is no longer at the
    version it ran (`reproof_rules`); every other cell keeps its verdict;
  * a row is current (`row_is_current`) when it is at the global floor DETECTOR_VERSION (prove.py) and every rule in
    its record is at its current version. The floor is for breaking changes: logic no rule owns, or a change that
    must re-prove everything. Bumping it makes every older row history, as before.

Adding a rule = adding one `Rule(...)` to RULES below. `owners` are the functions that implement it; the pin test
(tests/unit/test_detector_version_pin.py) fingerprints them per rule, so editing an owner without bumping that rule's
version fails, and all code NOT owned by a rule stays under the floor pin.

legacy_version: rows written before this registry carry no record. A legacy row ran the rule at `legacy_version`
(0 = the rule did not exist yet, so every cell that would use it is selected). The scoped run (proof/runner.py)
stamps legacy rows whose rules are all unchanged and re-proves the rest. Retire legacy_version at the next floor bump.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any

# the key inside analytics.cell_proof.checks that carries the record
RULES_KEY = "rules"


@dataclass(frozen=True)
class Rule:
    id: str
    version: int
    legacy_version: int = 1
    # a rule that runs writes one of these keys into the proof's checks
    check_keys: tuple[str, ...] = ()
    # a rule that judges without writing a key (or whose use is knowable from the cell alone): predicate on Shown
    applies: Callable[[Any], bool] | None = None
    # "module/path.py:function" implementing the rule, fingerprinted per rule by the pin test
    owners: tuple[str, ...] = ()
    note: str = ""


def _component_sum(shown: Any) -> bool:
    c = getattr(shown, "claim", None)
    return c is not None and c.kind == "component" and len(c.parts) > 1


def _has_splits(shown: Any) -> bool:
    return bool(getattr(shown, "combined_splits", ()))


def _stated_zero(shown: Any) -> bool:
    return bool(getattr(shown, "stated_zero", False))


def _always(_shown: Any) -> bool:
    return True


RULES: dict[str, Rule] = {
    r.id: r
    for r in (
        # per-cell checks written into `checks` by prove.py (their key is the rule)
        Rule("claim", 1, check_keys=("claim",)),
        Rule("period_length", 1, check_keys=("period_length",)),
        Rule("statement_face", 1, check_keys=("statement_face",)),
        Rule(
            "identity_tie",
            1,
            check_keys=("identity_tie",),
            owners=("proof/prove.py:_check_identity_tie",),
        ),
        Rule(
            "components_sum",
            1,
            check_keys=("components_sum",),
            owners=("proof/prove.py:_check_components_sum",),
        ),
        Rule("unit_scale", 1, check_keys=("unit_scale",)),
        Rule("component_parts", 1, check_keys=("component_parts",)),
        Rule("printed_zero", 1, check_keys=("printed_zero",)),
        Rule("restated_history", 1, check_keys=("restated_history",)),
        Rule("pre_filing", 1, check_keys=("pre_filing",)),
        Rule("derivation", 1, check_keys=("derivation", "derivation_attempt")),
        Rule(
            "non_interest_band",
            1,
            check_keys=("non_interest_band",),
            owners=("proof/prove.py:non_interest_band",),
        ),
        Rule("filer_xbrl_correction", 1, check_keys=("filer_xbrl_correction",)),
        Rule("quarantine_lifted", 1, check_keys=("quarantine_lifted",)),
        Rule("perimeter", 1, check_keys=("perimeter",)),
        # the cross-cell identities run over every served cell of a period (apply_identities)
        Rule("identities", 1, check_keys=("identity",), applies=_always),
        # v22 (2026-11-16): the FIRST rule-scoped changes
        Rule(
            "component_sum_authority",
            2,
            legacy_version=1,
            applies=_component_sum,
            owners=(
                "proof/shown.py:component_sum_authority_by_era",
                "proof/shown.py:component_sum_authority",
            ),
            note="v2: a filing's column is read with the cell's own parts when the filing's era part is not printed "
            "there (TMO total_debt Dec-2020)",
        ),
        Rule(
            "split_parts",
            1,
            legacy_version=0,
            check_keys=("split_parts",),
            applies=_has_splits,
            owners=(
                "proof/identities.py:_check_splits",
                "proof/shown.py:combined_splits_for",
            ),
            note="v1: split parts of a combined face line must sum to it (founder decision 2026-11-16)",
        ),
        # stated zero (ruling 2026-11-16): a cell served from a zero the filing states, value_source stated_zero
        Rule(
            "stated_zero",
            1,
            legacy_version=0,
            check_keys=("stated_zero",),
            applies=_stated_zero,
            owners=(
                "proof/prove.py:stated_zero_problem",
                "proof/prove.py:prove_stated_zero",
            ),
            note="v1: PROVEN when the exact quote, accession, locator and a quote period equal to the cell's are present",
        ),
    )
}


def rules_used(shown: Any, checks: Mapping[str, Any]) -> dict[str, int]:
    """{rule_id: version} of the rules this cell's proof used: a rule whose check key is in `checks`, or whose Shown
    predicate holds. Pure; the record written at proof time and the selection for a stored row use this one function."""
    out: dict[str, int] = {}
    for r in RULES.values():
        if any(k in checks for k in r.check_keys) or (
            r.applies is not None and shown is not None and r.applies(shown)
        ):
            out[r.id] = r.version
    return dict(sorted(out.items()))


def stored_rules(checks: Mapping[str, Any] | None) -> dict[str, int] | None:
    """The record of a stored row (None = a legacy row without one)."""
    rec = (checks or {}).get(RULES_KEY)
    return dict(rec) if isinstance(rec, dict) else None


def rules_current(rec: Mapping[str, int] | None) -> bool:
    """True when `rec` exists and every rule in it is a registered rule at its current version."""
    if rec is None:
        return False
    return all(rid in RULES and RULES[rid].version == v for rid, v in rec.items())


def row_is_current(
    detector_version: str | None, checks: Mapping[str, Any] | None, floor: str
) -> bool:
    """A proof row is the cell's verdict when it is at the floor version AND every rule it used is at its current
    version. A row without a record (legacy, not yet stamped) is not current: it cannot show which rules it ran."""
    return detector_version == floor and rules_current(stored_rules(checks))


def row_holds_disagree(
    detector_version: str | None, checks: Mapping[str, Any] | None, floor: str
) -> bool:
    """The mapper's proof guard keeps a wrong value held. Same as row_is_current, except an UNSTAMPED floor row still
    holds (the transition: a hold must not silently drop before the scoped run has judged the row)."""
    if detector_version != floor:
        return False
    rec = stored_rules(checks)
    return True if rec is None else rules_current(rec)


def reproof_rules(
    stored: Mapping[str, int] | None, shown: Any, checks: Mapping[str, Any]
) -> list[str]:
    """Why a stored row at the floor must be proved again: the rules it used (or that the cell would use now) whose
    version moved. Empty = the verdict stands. A legacy row (stored None) ran each rule at its legacy_version."""
    used = rules_used(shown, checks)
    eff = (
        dict(stored)
        if stored is not None
        else {rid: RULES[rid].legacy_version for rid in used}
    )
    out = {rid for rid, v in used.items() if eff.get(rid) != v}
    out |= {
        rid for rid, v in eff.items() if rid not in RULES or RULES[rid].version != v
    }
    return sorted(out)
