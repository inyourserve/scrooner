"""Which metric family applies to which company group, and why a metric is OUT.

Banks and insurers have their own metric families (net interest income, efficiency ratio,
combined ratio); a corporate metric for them is OUT with a stated reason, never a silent null.
Metadata only: nothing here changes a stored or served value (formulas are frozen until the
top-100 inputs certify); the serving suppression today is common/sector_applicability.py and
the agreement test holds the registry's `bank_reason` equal to it.

Groups are the sector-template groups of mapper/sector_templates.py (bank, lender, broker_am,
insurer, equity_reit, utility, bdc, general). OUT sources, first match wins:
  1. family: the metric's `applies_to` does not include the group;
  2. template: an input concept is OUT for the group (sector_templates.GROUP_OUT / GROUP_ONLY),
     derived from the formula, not authored.
"""

from __future__ import annotations

from dataclasses import dataclass

from scrooner_pipeline.mapper.sector_templates import GROUP_ONLY, GROUP_OUT
from scrooner_pipeline.metrics import generate
from scrooner_pipeline.metrics.registry import Metric, get_registry

BANK_FAMILY_GROUPS = {"bank", "lender"}
OTHER_FINANCIAL_GROUPS = {"insurer", "broker_am"}

# Insurers mirror the bank decision (2026-10-19) until an insurer family exists: metrics with
# applies_to `all` (ROE, ROA, EPS, book value per share, P/B, P/E, the dividend family) are IN;
# corporate-only metrics (net margin, pretax margin, ...) are OUT with this reason.
NOT_APPLICABLE_INSURER = "not_applicable_insurer"

# Input aliases by family, never per company: an MLP prints partners' equity, common units and
# unitholder distributions; the formulas read stockholders_equity, shares_outstanding and
# dividends_paid. `mlp` is a company family; the `all` metrics stay IN for it, the aliases only
# say which printed line feeds which formula input (per-share, payout and ROE metrics).
MLP_INPUT_ALIASES: dict[str, str] = {
    "partners_equity": "stockholders_equity",
    "common_units": "shares_outstanding",
    "unitholder_distributions": "dividends_paid",
}
FAMILY_INPUT_ALIASES: dict[str, dict[str, str]] = {"mlp": MLP_INPUT_ALIASES}


def alias_inputs(group: str, printed: dict) -> dict:
    """Rename a family's printed concepts to the formula concepts (a family without aliases is unchanged)."""
    amap = FAMILY_INPUT_ALIASES.get(group, {})
    return {amap.get(k, k): v for k, v in printed.items()}


@dataclass(frozen=True)
class Applicability:
    status: str  # IN | OUT
    reason: str | None
    source: str | None  # family | template | None


def _base(name: str) -> str:
    return name[: -len("_resolved")] if name.endswith("_resolved") else name


def leaf_concepts(m: Metric, _seen: frozenset[str] = frozenset()) -> set[str]:
    """Concept ids a metric ultimately reads (other metrics expanded)."""
    reg = get_registry()
    out: set[str] = set()
    for n in generate.inputs_of(m):
        if n in reg and n not in _seen and n != m.metric_id:
            out |= leaf_concepts(reg[n], _seen | {m.metric_id})
        elif n not in reg and n != "price":
            out.add(n)
    return out


def applicability(m: Metric, group: str) -> Applicability:
    fam = m.applies_to
    if fam == "corporate" and group in BANK_FAMILY_GROUPS:
        return Applicability(
            "OUT",
            m.bank_reason or "corporate metric; the bank family applies",
            "family",
        )
    if fam == "corporate" and group in {"insurer"}:
        return Applicability("OUT", NOT_APPLICABLE_INSURER, "family")
    if fam in ("bank", "bank,lender") and group not in {"bank", "lender"}:
        return Applicability("OUT", "bank family metric", "family")
    if fam == "insurer" and group != "insurer":
        return Applicability("OUT", "insurer family metric", "family")
    for c in sorted(leaf_concepts(m)):
        b = _base(c)
        if b in GROUP_OUT.get(group, frozenset()):
            return Applicability(
                "OUT", f"input {c} is outside the {group} template", "template"
            )
        if b in GROUP_ONLY and group not in GROUP_ONLY[b]:
            return Applicability(
                "OUT", f"input {c} applies only to {sorted(GROUP_ONLY[b])}", "template"
            )
    return Applicability("IN", None, None)
