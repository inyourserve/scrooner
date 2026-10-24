"""The five reason rules and the engine that applies them in a fixed order.

Order and precedence follow the freeze register (section 1): template
membership first, then line presentation, then evidenced zero, then state
propagation (twin and passthrough, repeated to a fixed point).

Promotion rule. A rule whose evidence is a detector (or a group membership)
that has not passed its audit emits `defect(evidence_pending, <family owner>)`
carrying the legitimate state it would become (`candidate_state`). The reason is
visible and the cell has an owner, but the cell does NOT count as covered.
Promotion to the legitimate state is a config event (`Audited`), never a code
edit, and is covered by a test.

No rule invents a value. No rule closes a cell without an evidence reference.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field

from scrooner_pipeline.common import rule_flags
from scrooner_pipeline.reasons.inputs import (
    TEMPLATE_VERSION,
    Evidence,
    GraphNode,
    GroupRow,
    TemplateRow,
)
from scrooner_pipeline.reasons.model import (
    LEGIT_STATES,
    BaselineCell,
    CellKey,
    Closure,
)

RULE_TEMPLATE = "template.membership@1"
RULE_LINE = "evidence.not_presented@1"
RULE_TAG_NP = "evidence.not_presented_tag_absent@1"
RULE_ZERO = "evidence.evidenced_zero@1"
RULE_TWIN = "reason.twin_inherit@1"
RULE_PASSTHROUGH = "reason.passthrough@1"
RULE_ORDER = (
    RULE_TEMPLATE,
    RULE_LINE,
    RULE_TAG_NP,
    RULE_ZERO,
    RULE_TWIN,
    RULE_PASSTHROUGH,
)

OWNER_BY_RULE = {
    RULE_TEMPLATE: "sector_analyst",  # RF-32
    RULE_LINE: "sector_analyst",  # RF-35
    RULE_TAG_NP: "sector_analyst",  # RF-35
    RULE_ZERO: "sector_analyst",  # RF-36
}


# --- tag-absence configuration (rules 3 and 3b) ------------------------------
# A company is a candidate for "the activity did not occur" / "the line is not
# presented" only when it filed NO tag at all (any namespace, any period; the
# authoritative facts held in analytics.company_sec_tag) that signals the
# activity or line, and filed enough tags that an ingestion hole cannot explain
# the absence. Matching is by tag NAME, not by our concept mapping, so "no mapped
# tag" never counts as evidence. The signal patterns are deliberately wide: a
# false hit only keeps a cell open, a false miss would invent a reason.
@dataclass(frozen=True)
class Family:
    name: str
    include: str
    exclude: str
    legit_state: str  # evidenced_zero | not_presented
    detail: str  # wording key detail


# Not offered as a family: collaborative_arrangement_revenue. Checked live
# 2026-10-24: REGN, VRTX, ALNY, BMY and LLY all disclose collaboration revenue yet
# have no "Collaborat" tag among their undimensioned facts (the disclosure sits
# under dimension members or custom extensions, which analytics.company_sec_tag
# does not hold), so tag-name absence proves nothing for dimension-only lines.
# Also not offered: other_income_expense_net and amortization_of_intangibles.
# Their template rows are marked "judgement" (no presence evidence), and the wording
# differs by filer (UNH presents "investment and other income" under other tags).
FAMILIES: dict[str, Family] = {
    f.name: f
    for f in (
        Family(
            "dividends",
            r"Dividend|PaymentsOfDistributions|DistributionsMade|DistributionMade|PaymentsOfCapitalDistribution",
            r"ExpectedDividend|FairValueAssumptions|EquityMethodInvestment|DividendIncome|InterestAndDividend|ProceedsFrom",
            "evidenced_zero",
            "dividends",
        ),
        Family(
            "buybacks",
            r"Repurchase|TreasuryStockValueAcquired|TreasuryStockSharesAcquired|TreasuryStockAcquired",
            r"AgreementsToRepurchase|AgreementToRepurchase|RepurchaseAgreement|ShareBasedCompensation|DebtInstrument|ExtinguishmentOfDebt|ProceedsFrom",
            "evidenced_zero",
            "buybacks",
        ),
        Family(
            "interest",
            r"InterestExpense|InterestPaid|InterestAndDebtExpense|InterestCostsIncurred|InterestIncomeExpense|PaymentsForInterest",
            r"^$",
            "evidenced_zero",
            "interest",
        ),
        Family(
            "capex",
            r"PaymentsToAcquire|CapitalExpenditure|PaymentsForCapital|PaymentsToDevelop|PropertyPlantAndEquipmentAdditions|CapitalizedComputerSoftwareAdditions",
            r"^$",
            "evidenced_zero",
            "capex",
        ),
        Family(
            "ar_change",
            r"(IncreaseDecrease|Change|Adjustment|Increase|Decrease)[A-Za-z]*Receivable|Receivable[A-Za-z]*(IncreaseDecrease|Change|Adjustment)",
            r"^$",
            "not_presented",
            "absent",
        ),
        Family(
            "ap_change",
            r"(IncreaseDecrease|Change|Adjustment|Increase|Decrease)[A-Za-z]*Payable|Payable[A-Za-z]*(IncreaseDecrease|Change|Adjustment)",
            r"^$",
            "not_presented",
            "absent",
        ),
        Family(
            "inventory_change",
            r"(IncreaseDecrease|Change|Adjustment|Increase|Decrease)[A-Za-z]*Inventor|Inventor[A-Za-z]*(IncreaseDecrease|Change|Adjustment)",
            r"^$",
            "not_presented",
            "absent",
        ),
    )
}
FAMILY_BY_DATA_POINT: dict[str, str] = {
    "dividends_paid": "dividends",
    "dividends_paid_resolved": "dividends",
    "dividends_per_share": "dividends",
    "dividends_per_share_resolved": "dividends",
    "share_buybacks": "buybacks",
    "share_buybacks_resolved": "buybacks",
    "interest_expense": "interest",
    "interest_expense_resolved": "interest",
    "capex": "capex",
    "capex_resolved": "capex",
    "cf_ar_change": "ar_change",
    "cf_ap_change": "ap_change",
    "cf_inventory_change": "inventory_change",
}
MIN_TAGS_FOR_ABSENCE = 100


def family_signal(tag: str, family: str) -> bool:
    f = FAMILIES[family]
    return re.search(f.include, tag) is not None and re.search(f.exclude, tag) is None


# --- rule 2 configuration: statement lines read by migration 0093 -----------
LINE_DATA_POINTS = frozenset(
    {
        "accounts_payable",
        "accounts_receivable",
        "cost_of_revenue",
        "goodwill",
        "gross_profit",
        "interest_income",
        "inventory",
        "operating_expenses",
        "research_and_development",
    }
)

# --- propagation configuration ----------------------------------------------
PASS_ROLES = frozenset(
    {
        "req",
        "numerator",
        "denominator",
        "add",
        "subtract",
        "base",
        "base_t",
        "base_t_minus_1",
    }
)
ZERO_BASE_ROLES = frozenset({"denominator", "base_t", "base_t_minus_1"})


@dataclass(frozen=True)
class Audited:
    """What has passed its audit (empty today: no audit has been run).
    `groups`: group names whose membership passed the 30-per-group audit.
    `detectors`: rule ids whose detector version passed its audit.
    `f1_approved`: the founder approved F-1."""

    groups: frozenset[str] = frozenset()
    detectors: frozenset[str] = frozenset()
    f1_approved: bool = (
        False  # founder item F-1 (base rows of the 30 twin pairs leave the denominator)
    )


@dataclass
class Context:
    baseline: Mapping[CellKey, BaselineCell]
    groups: Mapping[int, GroupRow]
    template: Mapping[tuple[str, str, str], TemplateRow]
    graph: Mapping[str, GraphNode]
    evidence: Evidence
    f1_removed: tuple[str, ...] = ()
    zero_when_absent: Mapping[str, frozenset[str]] = field(default_factory=dict)
    audited: Audited = field(default_factory=Audited)


@dataclass(frozen=True)
class _St:
    """A cell state as seen by an inheriting cell."""

    state: str
    defect_class: str | None
    owner: str | None
    candidate: str | None
    wording: str | None
    cand_wording: str | None
    level: str

    @property
    def effective(self) -> str:
        return self.candidate or self.state


def _wording(state: str, detail: str | None = None) -> str | None:
    return {
        "not_in_template": None,
        "not_presented": "state.np." + (detail or "absent"),
        "evidenced_zero": "state.zero." + (detail or "activity"),
        "undefined_by_math": "state.nm." + (detail or "input"),
        "history_horizon": "state.history",
        "defect": "state.defect",
    }.get(state)


def _make(
    cell: BaselineCell,
    rule_id: str,
    legit: str,
    audited: bool,
    owner: str,
    evidence_level: str,
    evidence: dict[str, object],
    detail: str | None = None,
) -> Closure:
    if audited:
        return Closure(
            cell.company_id,
            cell.ticker,
            cell.data_point,
            rule_id,
            legit,
            None,
            None,
            None,
            _wording(legit, detail),
            None,
            evidence_level,
            evidence,
        )
    return Closure(
        cell.company_id,
        cell.ticker,
        cell.data_point,
        rule_id,
        "defect",
        "evidence_pending",
        owner,
        legit,
        _wording("defect"),
        _wording(legit, detail),
        evidence_level,
        evidence,
    )


# --- rule 1: template membership --------------------------------------------
def _template_rule(cell: BaselineCell, ctx: Context) -> Closure | None:
    g = ctx.groups.get(cell.company_id)
    if (
        g is None
        or g.basis == "excluded_rule"
        or g.review_flags.startswith("identity:")
    ):
        return None
    if not g.evidence_accession:
        return None  # a group without a filing reference is not evidence
    row = ctx.template.get(("group", g.group, cell.data_point))
    if row is None or row.rule != "NIT":
        return None
    for ov in (
        g.overlays
    ):  # step 0: base group UNION overlays; any overlay row that keeps the cell wins
        orow = ctx.template.get(("overlay", ov, cell.data_point))
        if orow is not None and orow.rule != "NIT":
            return None
    return _make(
        cell,
        RULE_TEMPLATE,
        "not_in_template",
        g.group in ctx.audited.groups,
        OWNER_BY_RULE[RULE_TEMPLATE],
        "DATA-INFERRED",
        {
            "kind": "template_membership",
            "template_version": row.template_version or TEMPLATE_VERSION,
            "group": g.group,
            "overlays": list(g.overlays),
            "group_rule": row.rule,
            "group_basis": g.basis,
            "group_rule_path": g.rule_path,
            "group_evidence_accession": g.evidence_accession,
            "group_evidence_form": g.evidence_form,
            "group_evidence_period_end": g.evidence_period_end,
            "group_audited": g.group in ctx.audited.groups,
        },
    )


# --- rule 2: filing line presentation (migration 0093) ----------------------
def _line_rule(cell: BaselineCell, ctx: Context) -> Closure | None:
    ev = ctx.evidence.line
    if ev is None or cell.data_point not in LINE_DATA_POINTS:
        return None
    row = ev.get(cell.key)
    if row is None or row.line_present is None:
        return None  # statement could not be located: no evidence either way
    ref: dict[str, object] = {
        "kind": "filing_line_evidence",
        "table": "analytics.company_filing_line_evidence",
        "statement": row.statement,
        "line_present": row.line_present,
        "combined": row.combined,
        "matched_label": row.matched_label,
        "accession": row.accession_number,
        "form": row.form,
    }
    audited = RULE_LINE in ctx.audited.detectors
    if not row.line_present:
        return _make(
            cell,
            RULE_LINE,
            "not_presented",
            audited,
            "sector_analyst",
            "DATA-INFERRED",
            ref,
            "absent",
        )
    if row.combined:
        return _make(
            cell,
            RULE_LINE,
            "not_presented",
            audited,
            "sector_analyst",
            "DATA-INFERRED",
            ref,
            "combined",
        )
    # The line IS on the statement and we hold no value: a real extraction gap.
    return Closure(
        cell.company_id,
        cell.ticker,
        cell.data_point,
        RULE_LINE,
        "defect",
        "vocabulary",
        "tag_mapper",
        None,
        _wording("defect"),
        None,
        "DATA-INFERRED",
        ref,
    )


# --- rules 3 / 3b: tag-agnostic absence ---------------------------------------
def _absence(
    cell: BaselineCell, ctx: Context, rule_id: str, legit: str
) -> Closure | None:
    fam_name = FAMILY_BY_DATA_POINT.get(cell.data_point)
    tags = ctx.evidence.tags
    if fam_name is None or tags is None:
        return None
    fam = FAMILIES[fam_name]
    if fam.legit_state != legit:
        return None
    t = tags.get(cell.company_id)
    if t is None or t.tag_count < MIN_TAGS_FOR_ABSENCE or fam_name in t.families:
        return None
    if legit == "not_presented":
        # not_presented is only a legitimate outcome where the template allows the
        # line to be absent (COND/not_presented); a required line stays a defect.
        g = ctx.groups.get(cell.company_id)
        row = ctx.template.get(("group", g.group, cell.data_point)) if g else None
        if row is None or row.rule != "COND" or row.state_if_false != "not_presented":
            return None
    return _make(
        cell,
        rule_id,
        legit,
        rule_id in ctx.audited.detectors,
        "sector_analyst",
        "DATA-INFERRED",
        {
            "kind": "tag_agnostic_absence",
            "table": "analytics.company_sec_tag",
            "family": fam_name,
            "signal_include": fam.include,
            "signal_exclude": fam.exclude,
            "distinct_tags_filed": t.tag_count,
            "min_tags_floor": MIN_TAGS_FOR_ABSENCE,
            "scope": "all tags the company ever filed, any namespace; not filing text",
        },
        fam.detail,
    )


def _zero_rule(cell: BaselineCell, ctx: Context) -> Closure | None:
    return _absence(cell, ctx, RULE_ZERO, "evidenced_zero")


def _tag_np_rule(cell: BaselineCell, ctx: Context) -> Closure | None:
    return _absence(cell, ctx, RULE_TAG_NP, "not_presented")


# --- propagation -------------------------------------------------------------
def _st_from_closure(c: Closure) -> _St:
    return _St(
        c.state,
        c.defect_class,
        c.owner,
        c.candidate_state,
        c.wording_key,
        c.candidate_wording_key,
        c.evidence_level,
    )


def _st_from_baseline(b: BaselineCell) -> _St | None:
    if not b.classified:
        return None
    cand = b.candidate_state or None
    return _St(
        "defect",
        b.defect_class,
        b.owner,
        cand,
        "state.defect",
        _wording(cand) if cand else None,
        "DATA-INFERRED",
    )


def _inherit(st: _St, role: str) -> _St | None:
    """What a dependent cell becomes when `st` is the state of one of its inputs
    in `role` (S3 P1/P2). Returns None when the input state does not by itself
    decide the dependent."""
    eff = st.effective
    if eff == "evidenced_zero":
        if role not in ZERO_BASE_ROLES:
            return None  # a zero numerator would yield a value, not a blank
        if st.state == "defect":
            return _St(
                "defect",
                "evidence_pending",
                st.owner,
                "undefined_by_math",
                "state.defect",
                _wording("undefined_by_math", "zero_base"),
                st.level,
            )
        return _St(
            "undefined_by_math",
            None,
            None,
            None,
            _wording("undefined_by_math", "zero_base"),
            None,
            st.level,
        )
    return st


def _close_from(
    cell: BaselineCell, rule_id: str, st: _St, evidence: dict[str, object]
) -> Closure:
    return Closure(
        cell.company_id,
        cell.ticker,
        cell.data_point,
        rule_id,
        st.state,
        st.defect_class,
        st.owner,
        st.candidate,
        st.wording,
        st.cand_wording,
        st.level,
        evidence,
    )


def twin_of(data_point: str, graph: Mapping[str, GraphNode]) -> str | None:
    """The displayed `_resolved` twin of an F-1 base data point."""
    special = {
        "revenue": "revenue_sanity_resolved",
        "total_debt_split": "total_debt_resolved",
    }
    cand = special.get(data_point, data_point + "_resolved")
    return cand if cand in graph else None


def _state_of(
    key: CellKey, ctx: Context, closed: Mapping[CellKey, Closure]
) -> tuple[_St, str] | None:
    if key in closed:
        return _st_from_closure(closed[key]), closed[key].rule_id
    b = ctx.baseline.get(key)
    if b is None or b.valued:
        return None
    s = _st_from_baseline(b)
    return (s, "baseline:" + b.gap_reason) if s is not None else None


def _twin_rule(
    cell: BaselineCell, ctx: Context, closed: Mapping[CellKey, Closure]
) -> Closure | None:
    if cell.data_point not in ctx.f1_removed:
        return None
    twin = twin_of(cell.data_point, ctx.graph)
    if twin is None:
        return None
    got = _state_of((cell.company_id, twin), ctx, closed)
    if got is None:
        tb = ctx.baseline.get((cell.company_id, twin))
        if tb is not None and not tb.valued:
            return None  # twin is blank without a state: nothing to inherit
        # The displayed cell of record (the twin) is valued; the base row is an
        # internal input. Whether base rows are shown at all is founder item F-1.
        ev: dict[str, object] = {
            "kind": "f1_base_row_twin_valued",
            "twin": twin,
            "decision": "F-1 (data-team/strategy/FREEZE-REGISTER-2026-10-22.md section 4)",
            "f1_approved": ctx.audited.f1_approved,
        }
        if ctx.audited.f1_approved:
            return _make(
                cell,
                RULE_TWIN,
                "not_in_template",
                True,
                "standardization_lead",
                "DATA-INFERRED",
                ev,
            )
        return _make(
            cell,
            RULE_TWIN,
            "not_in_template",
            False,
            "standardization_lead",
            "DATA-INFERRED",
            ev,
        )
    st, src = got
    return _close_from(
        cell,
        RULE_TWIN,
        st,
        {
            "kind": "twin_state",
            "twin": twin,
            "twin_source": src,
            "note": "base row of an F-1 pair: blank for the same cause as the displayed _resolved twin",
        },
    )


def _passthrough_rule(
    cell: BaselineCell, ctx: Context, closed: Mapping[CellKey, Closure]
) -> Closure | None:
    node = ctx.graph.get(cell.data_point)
    if node is None or not node.inputs:
        return None
    best: tuple[int, int, _St, str, str, str] | None = None
    for idx, (inp, role) in enumerate(node.inputs):
        if role not in PASS_ROLES:
            continue
        if inp in ctx.zero_when_absent.get(cell.data_point, frozenset()):
            continue  # an absent input is zero by definition of this metric
        got = _state_of((cell.company_id, inp), ctx, closed)
        if got is None:
            continue
        inh = _inherit(got[0], role)
        if inh is None:
            continue
        # S3 P1: a legitimate input state decides; otherwise the first defect input (P2).
        rank = 0 if inh.effective in LEGIT_STATES else 1
        cand = (rank, idx, inh, inp, role, got[1])
        if best is None or cand[:2] < best[:2]:
            best = cand
    if best is None:
        return None
    _, _, inh, inp, role, src = best
    return _close_from(
        cell,
        RULE_PASSTHROUGH,
        inh,
        {"kind": "input_state", "input": inp, "role": role, "input_source": src},
    )


# --- engine ------------------------------------------------------------------
def active_rules(environ: Mapping[str, str] | None = None) -> frozenset[str]:
    """Rules that are on or in dry-run according to the common flag module. Empty
    when no flag is set: the default is OFF and nothing is evaluated."""
    return frozenset(
        r
        for r in RULE_ORDER
        if rule_flags.rule_mode(r, environ) in (rule_flags.ON, rule_flags.DRY_RUN)
    )


def reasonless_cells(baseline: Mapping[CellKey, BaselineCell]) -> list[BaselineCell]:
    return sorted(
        (b for b in baseline.values() if b.reasonless),
        key=lambda b: (b.company_id, b.data_point),
    )


def run(ctx: Context, rules: Iterable[str]) -> dict[CellKey, Closure]:
    """Evaluate the named rules over the reasonless cells. Pure: reads ctx only."""
    enabled = set(rules)
    unknown = enabled - set(RULE_ORDER)
    if unknown:
        raise ValueError(f"unknown rules {sorted(unknown)}")
    targets = reasonless_cells(ctx.baseline)
    closed: dict[CellKey, Closure] = {}
    for rid, fn in (
        (RULE_TEMPLATE, _template_rule),
        (RULE_LINE, _line_rule),
        (RULE_TAG_NP, _tag_np_rule),
        (RULE_ZERO, _zero_rule),
    ):
        if rid not in enabled:
            continue
        for cell in targets:
            if cell.key in closed:
                continue  # precedence: an earlier rule already decided this cell
            c = fn(cell, ctx)
            if c is not None:
                closed[cell.key] = c
    propagators = [
        pfn
        for rid, pfn in ((RULE_TWIN, _twin_rule), (RULE_PASSTHROUGH, _passthrough_rule))
        if rid in enabled
    ]
    # Rounds against a frozen snapshot of the previous round, so the result does
    # not depend on cell iteration order. Terminates: each round closes at least
    # one new cell or stops, and cells are never reopened.
    while propagators:
        snapshot = dict(closed)
        new: dict[CellKey, Closure] = {}
        for cell in targets:
            if cell.key in snapshot:
                continue
            for pfn in propagators:
                c = pfn(cell, ctx, snapshot)
                if c is not None:
                    new[cell.key] = c
                    break
        if not new:
            break
        closed.update(new)
    return closed
