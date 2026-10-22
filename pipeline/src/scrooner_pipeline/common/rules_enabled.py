"""The ``rules_enabled`` flag and dry-run switch for value-changing rule families.

Contract (WO-REVIEW-release-manager.md section 2.2, items 1-2):

* ``SCROONER_RULES_ENABLED`` holds rule IDs, comma separated (``family.rule@N``),
  default empty. Empty means every value-changing family behaves exactly as before.
* It is plumbed as a ``workflow_dispatch`` input of ``pipeline-recompute.yml`` (manual runs
  only) and flipped to a committed default only by the Release Manager's step-8 commit.
  It is deliberately NOT a GitHub repo variable: a variable would reach the nightly too and
  split the population on the first live run.
* ``SCROONER_RULES_DRYRUN=1`` makes every flagged family compute its change set and
  WRITE NOTHING; the planned changes are returned as ``PlannedChange`` rows so the caller
  can emit the before/after diff table (see ``common/rule_before_image.py``).

Matching is by exact rule ID, or by family (``family.rule``) so ``debt.total_debt_consistency``
enables every version of the family only when listed without ``@N``.
"""

from __future__ import annotations

import os

ENV_ENABLED = "SCROONER_RULES_ENABLED"
ENV_DRYRUN = "SCROONER_RULES_DRYRUN"


def enabled_rules(environ: dict[str, str] | None = None) -> frozenset[str]:
    env = os.environ if environ is None else environ
    raw = env.get(ENV_ENABLED, "")
    return frozenset(t.strip() for t in raw.split(",") if t.strip())


def is_enabled(rule_id: str, environ: dict[str, str] | None = None) -> bool:
    """True when ``rule_id`` (``family.rule@N``) is listed. A bare family name in the
    setting enables every version of it; a versioned entry enables only that version."""
    listed = enabled_rules(environ)
    if rule_id in listed:
        return True
    family = rule_id.split("@", 1)[0]
    return family in listed


def is_dry_run(environ: dict[str, str] | None = None) -> bool:
    env = os.environ if environ is None else environ
    return env.get(ENV_DRYRUN, "").strip().lower() in {"1", "true", "yes", "on"}
