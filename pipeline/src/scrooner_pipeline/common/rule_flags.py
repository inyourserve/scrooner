"""Rule flags (Release Manager procedure, WO-REVIEW-release-manager step 6).

A value-changing rule family ships with its flag OFF. The flag name is the
rule ID itself (freeze register 3.1). It is switched on for one run only by
the environment variable SCROONER_RULES_ENABLED, a comma/space separated list
of rule IDs, which the recompute workflow sets from a manual dispatch input
(`rules_enabled=<rule ids>`). A repository variable is deliberately NOT read,
because that would reach the nightly run.
"""

import os
import re

# Same pattern as cell_contract.RULE_ID_PATTERN (migration 0100 branch);
# repeated so this module stands alone until both are on main.
RULE_ID_PATTERN = r"^[a-z][a-z0-9_]*(\.[A-Za-z0-9_]+)+@[0-9]+$"
_RULE_ID_RE = re.compile(RULE_ID_PATTERN)

ENV_VAR = "SCROONER_RULES_ENABLED"

# Registered rule IDs that have a flag. Looking up an unregistered ID is a
# programming error (a typo would silently mean "off" forever).
RULE_PERIODIC_FORM_ONLY = "source.periodic_form_only@1"  # RF-03, W3
RULE_MATCHING_COPIES = "dedupe.matching_copies@1"  # RF-46, WO-23
RULE_SHARED_ACCESSION_PRIMARY = "entity.shared_accession_primary_filer@1"  # RF-21, P1

KNOWN_RULES = frozenset(
    {RULE_PERIODIC_FORM_ONLY, RULE_MATCHING_COPIES, RULE_SHARED_ACCESSION_PRIMARY}
)


def enabled_rules(environ: dict[str, str] | None = None) -> frozenset[str]:
    raw = (environ if environ is not None else os.environ).get(ENV_VAR, "")
    ids = [t for t in re.split(r"[,\s]+", raw.strip()) if t]
    for rule_id in ids:
        if not _RULE_ID_RE.match(rule_id):
            raise ValueError(f"{ENV_VAR} has a malformed rule ID {rule_id!r}")
        if rule_id not in KNOWN_RULES:
            raise ValueError(f"{ENV_VAR} names an unknown rule {rule_id!r}")
    return frozenset(ids)


def rule_enabled(rule_id: str, environ: dict[str, str] | None = None) -> bool:
    if rule_id not in KNOWN_RULES:
        raise ValueError(f"unregistered rule {rule_id!r}")
    return rule_id in enabled_rules(environ)
