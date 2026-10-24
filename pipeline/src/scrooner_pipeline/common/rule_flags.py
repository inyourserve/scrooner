"""ONE flag module for every value-changing rule (Release Manager procedure,
WO-REVIEW-release-manager step 6; doc 49). It replaces the per-lane copies
(lane 1 here raised on unknown IDs, lane 2's mapper/rule_flags.py ignored them,
so `rules_enabled=ttm.age_guard@1` would have crashed every lane-1 stage).

Modes of a rule (default OFF):
  off      legacy behavior, byte for byte.
  dry_run  the rule is evaluated and its decision logged/recorded, but the legacy
           value is what is written. A rule that has no dry-run path treats
           dry_run exactly like off (documented per rule in RULES below).
  on       the rule's value/blank is written.

Environment (set ONLY by a manual workflow_dispatch input of
pipeline-recompute.yml; never a repository variable, which would reach the
nightly and split the population on the first live run):
  SCROONER_RULES_ENABLED   comma/space separated rule IDs in mode on
  SCROONER_RULES_DRYRUN    comma/space separated rule IDs in mode dry_run
A rule in both lists is an error (an ambiguous flag stops the run). A
malformed ID is an error. An ID that is well formed but not in RULES is an
error too: that is a typo, and a typo that silently meant "off" would hide a
guard. Registering a new rule is one line in RULES.

Dispatch syntax (single workflow input `rules`): "on:a@1,b@1 dry_run:c@1".
`python -m scrooner_pipeline.common.rule_flags --dispatch "<text>"` validates
it and prints the two KEY=VALUE lines for $GITHUB_ENV, so a typo fails the job
before any stage runs.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from collections.abc import Mapping
from dataclasses import dataclass

ENV_ENABLED = "SCROONER_RULES_ENABLED"
ENV_DRYRUN = "SCROONER_RULES_DRYRUN"
ENV_VAR = ENV_ENABLED  # kept: earlier lane-1 code and tests import this name

OFF = "off"
DRY_RUN = "dry_run"
ON = "on"

# Same pattern as cell_contract.RULE_ID_PATTERN (migration 0100 branch); certify
# detectors cert.I<k>.<rule>@N are not flag-bearing and are not in RULES.
RULE_ID_PATTERN = r"^[a-z][a-z0-9_]*(\.[A-Za-z0-9_]+)+@[0-9]+$"
_RULE_ID_RE = re.compile(RULE_ID_PATTERN)


@dataclass(frozen=True)
class Rule:
    rule_id: str
    rf: str  # freeze register alias, or "-" when none
    lane: str  # who builds it
    dry_run: bool  # does the rule have a real dry-run path (else dry_run == off)
    what: str


def _r(rule_id: str, rf: str, lane: str, what: str, dry_run: bool = False) -> Rule:
    return Rule(rule_id, rf, lane, dry_run, what)


RULES: dict[str, Rule] = {
    r.rule_id: r
    for r in (
        # ---- lane 1: authority, identity, state
        _r(
            "source.periodic_form_only@1",
            "RF-03",
            "lane1",
            "Stage 2e + conflict-fill loader ignore non-periodic filings (W3)",
            dry_run=True,
        ),
        _r(
            "dedupe.matching_copies@1",
            "RF-46",
            "lane1",
            "copies equal within inferred rounding are not a conflict (WO-23)",
            dry_run=True,
        ),
        _r(
            "entity.shared_accession_primary_filer@1",
            "RF-21",
            "lane1",
            "combined-filing primary registrant owns the accession (P1)",
        ),
        _r(
            "identity.cik_name_ticker@1",
            "RF-20",
            "lane1",
            "audited identity fixes (script-applied; the override READ is data-driven, not flag-driven)",
        ),
        # ---- lane 2: metric-stage guards
        _r(
            "ttm.consecutive_window@1",
            "RF-01",
            "lane2",
            "date-based contiguous TTM windows (W1)",
            dry_run=True,
        ),
        _r("ttm.age_guard@1", "RF-02", "lane2", "TTM age guard (W2)", dry_run=True),
        _r(
            "ttm.age_guard@2",
            "RF-02",
            "lane2",
            "TTM age guard, second threshold version",
            dry_run=True,
        ),
        _r(
            "pershare.balance_sheet_date_anchor@1",
            "RF-10",
            "lane2",
            "per-share pairing on the balance-sheet date (W10)",
            dry_run=True,
        ),
        _r(
            "tsy.stale_component@1",
            "RF-02",
            "lane2",
            "total_shareholder_yield hidden when a component is stale or the windows do not end together",
            dry_run=True,
        ),
        # ---- lane 3: concept-level guards and fallbacks
        _r(
            "employee_count.no_yfinance_tier@1",
            "-",
            "lane3",
            "D-4: yfinance tier of employee_count_resolved off",
        ),
        _r(
            "debt.total_debt_consistency@1",
            "RF-11",
            "lane3",
            "held total-debt guards R1/R4/R5",
        ),
        _r(
            "revenue.total_disagreement@1",
            "RF-13",
            "lane3",
            "revenue total-disagreement guard (NA-8)",
        ),
        _r(
            "oi.derived_not_face@1",
            "RF-14",
            "lane3",
            "operating income derived-not-face guard (WO-14)",
        ),
        _r(
            "mcap.share_basis_guard@1",
            "RF-15",
            "lane3",
            "market cap publish guard at the share basis (WO-21)",
        ),
        _r(
            "scale.unit_plausibility@1",
            "RF-18",
            "lane3",
            "scale and unit publish guard (WO-27)",
        ),
        _r(
            "currency.non_usd_price_ratio@1",
            "RF-19",
            "lane3",
            "non-USD reporter price ratios (WO-28)",
        ),
        _r(
            "balance.identity_equity_basis@1",
            "-",
            "lane3",
            "balance-sheet identity fallback: liabilities = assets - total equity (incl NCI) - temporary equity (sign and NCI double count)",
            dry_run=True,
        ),
        _r(
            "revenue.structure_total@1",
            "RF-48",
            "lane3",
            "structure-based revenue total (Tier 2)",
        ),
        # ---- Period Engineer / other register families, registered so a dispatch naming them cannot crash a stage
        _r(
            "period.same_vintage_derivation@1",
            "RF-04",
            "period_engineer",
            "same-vintage Q4 derivation",
        ),
        _r(
            "period.fiscal_label_from_dates@1",
            "RF-05",
            "period_engineer",
            "fiscal label from dates (W5)",
        ),
        _r(
            "math.growth_nonpositive_base@1",
            "RF-06",
            "lane2",
            "growth over a non-positive base is not meaningful",
        ),
        _r(
            "math.ratio_nonpositive_denominator@1",
            "RF-07",
            "lane2",
            "ratio over a non-positive denominator is not meaningful",
        ),
        _r(
            "composite.unknown_not_zero@1",
            "RF-08",
            "lane1",
            "unknown component is not zero (W8); also the rule behind lane 2's total_shareholder_yield unevidenced-zero guard (Chief ruling 2026-10-22: no separate tsy.unevidenced_zero id)",
            dry_run=True,
        ),
        _r(
            "reason.no_sic_only_reason@1",
            "RF-09",
            "lane1",
            "no reason from SIC alone (W9)",
        ),
        _r(
            "pershare.never_derive@1",
            "RF-12",
            "period_engineer",
            "no derived Q4 EPS/DPS (RU-1)",
        ),
        _r(
            "pershare.fy_rate_guard@1",
            "RF-28",
            "period_engineer",
            "FY DPS must be at least the sum of Q1-Q3",
        ),
        _r(
            "derive.additive_allowlist@1",
            "RF-27",
            "period_engineer",
            "Q4 derivation only for the additive allowlist",
        ),
        _r(
            "cost.partial_cost_line@1",
            "RF-16",
            "lane3",
            "partial cost line guard (WO-20)",
        ),
        _r(
            "ni.profitloss_with_nci@1",
            "RF-17",
            "lane3",
            "ProfitLoss with NCI guard (WO-24)",
        ),
        _r(
            "split.event_basis@1",
            "RF-22",
            "period_engineer",
            "split event basis (WO-22)",
        ),
        _r(
            "stale.non_ttm_latest_period@1",
            "RF-23",
            "lane1",
            "_resolved obey the latest-period rule",
        ),
        _r(
            "lineage.required_for_display@1",
            "RF-24",
            "lane2",
            "lineage required for display",
        ),
        _r(
            "population.status_scan@1",
            "RF-25",
            "lane2",
            "population status scan (WO-26)",
        ),
        _r(
            "ingest.transition_10kt@1",
            "RF-42",
            "lane2",
            "10-KT transition filings (WO-19)",
        ),
        _r(
            "ownership.institutional_share_base@1",
            "RF-47",
            "lane2",
            "institutional ownership share base (WO-16)",
        ),
    )
}

# Names earlier lane-1 code imports.
RULE_PERIODIC_FORM_ONLY = "source.periodic_form_only@1"
RULE_MATCHING_COPIES = "dedupe.matching_copies@1"
RULE_SHARED_ACCESSION_PRIMARY = "entity.shared_accession_primary_filer@1"
RULE_IDENTITY = "identity.cik_name_ticker@1"
KNOWN_RULES = frozenset(RULES)


def parse_rule_ids(raw: str | None) -> frozenset[str]:
    """Comma/space separated IDs. Malformed or unregistered IDs raise."""
    ids: list[str] = []
    for token in re.split(r"[,\s]+", (raw or "").strip()):
        if not token:
            continue
        if not _RULE_ID_RE.match(token):
            raise ValueError(f"malformed rule id {token!r}; expected family.rule@N")
        if token not in RULES:
            raise ValueError(
                f"unregistered rule id {token!r}; register it in common/rule_flags.RULES "
                "(a typo here would silently mean 'off')"
            )
        ids.append(token)
    return frozenset(ids)


def _lists(environ: Mapping[str, str] | None) -> tuple[frozenset[str], frozenset[str]]:
    env = os.environ if environ is None else environ
    on, dry = parse_rule_ids(env.get(ENV_ENABLED)), parse_rule_ids(env.get(ENV_DRYRUN))
    both = on & dry
    if both:
        raise ValueError(
            f"rule(s) {sorted(both)} are in both {ENV_ENABLED} and {ENV_DRYRUN}"
        )
    return on, dry


def enabled_rules(environ: Mapping[str, str] | None = None) -> frozenset[str]:
    return _lists(environ)[0]


def rule_mode(rule_id: str, environ: Mapping[str, str] | None = None) -> str:
    if rule_id not in RULES:
        raise ValueError(f"unregistered rule {rule_id!r}")
    on, dry = _lists(environ)
    if rule_id in on:
        return ON
    if rule_id in dry:
        return DRY_RUN if RULES[rule_id].dry_run else OFF
    return OFF


def rule_enabled(rule_id: str, environ: Mapping[str, str] | None = None) -> bool:
    """True only in mode on."""
    return rule_mode(rule_id, environ) == ON


def rule_dry_run(rule_id: str, environ: Mapping[str, str] | None = None) -> bool:
    return rule_mode(rule_id, environ) == DRY_RUN


def parse_dispatch(text: str | None) -> tuple[frozenset[str], frozenset[str]]:
    """ "on:a@1,b@1 dry_run:c@1" -> (on, dry_run). Empty -> both empty."""
    on: set[str] = set()
    dry: set[str] = set()
    for part in (text or "").split():
        mode, sep, ids = part.partition(":")
        if not sep or mode not in (ON, DRY_RUN):
            raise ValueError(f"bad rules input {part!r}; use 'on:id,id dry_run:id'")
        (on if mode == ON else dry).update(parse_rule_ids(ids))
    if on & dry:
        raise ValueError(f"rule(s) {sorted(on & dry)} are both on and dry_run")
    return frozenset(on), frozenset(dry)


def env_lines(text: str | None) -> list[str]:
    on, dry = parse_dispatch(text)
    lines = []
    if on:
        lines.append(f"{ENV_ENABLED}={','.join(sorted(on))}")
    if dry:
        lines.append(f"{ENV_DRYRUN}={','.join(sorted(dry))}")
    return lines


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument(
        "--dispatch", default="", help="'on:a@1,b@1 dry_run:c@1' (workflow input)"
    )
    ap.add_argument("--list", action="store_true", help="print the registered rules")
    args = ap.parse_args(argv)
    if args.list:
        for r in RULES.values():
            print(
                f"{r.rule_id}\t{r.rf}\t{r.lane}\tdry_run={'yes' if r.dry_run else 'no'}\t{r.what}"
            )
        return 0
    try:
        for line in env_lines(args.dispatch):
            print(line)
    except ValueError as exc:
        print(f"::error::{exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
