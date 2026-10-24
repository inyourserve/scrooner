"""Visible-reason rules (reasons/ package): synthetic fixtures for every branch, a
determinism test, a no-write guard, and a smoke test over the committed inputs.

The synthetic tests build a tiny Context by hand so each rule's evidence is
explicit. The smoke test uses the real committed baseline, group assignment and
template (hash pinned) with no database."""

from __future__ import annotations

import random
import re
from pathlib import Path

import pytest
from scrooner_pipeline.common import rule_flags as rf
from scrooner_pipeline.reasons import db_evidence, rules
from scrooner_pipeline.reasons.inputs import (
    PINNED_SHA256,
    Evidence,
    GraphNode,
    GroupRow,
    InputHashError,
    LineEvidence,
    TagPresence,
    TemplateRow,
    load_baseline,
    load_groups,
)
from scrooner_pipeline.reasons.model import (
    ROOT_CAUSE_CLASSES,
    BaselineCell,
    Closure,
    to_blank_reason_row,
)


def cell(
    cid: int,
    dp: str,
    *,
    valued: bool = False,
    reason: str = "",
    klass: str = "unclassified",
    owner: str = "triage",
    cand: str = "",
) -> BaselineCell:
    return BaselineCell(
        cid,
        f"T{cid}",
        dp,
        "leaf_concept",
        valued,
        reason,
        klass if not valued else "",
        owner if not valued else "",
        cand,
        "",
    )


def group(
    cid: int,
    grp: str = "corporate",
    overlays: tuple[str, ...] = (),
    basis: str = "code",
    acc: str = "0000000000-26-000001",
    flags: str = "",
) -> GroupRow:
    return GroupRow(
        cid,
        grp,
        overlays,
        basis,
        acc,
        "10-K",
        "2025-12-31",
        flags,
        "cohort_file_v1",
        "group.assign@2/x",
    )


def trow(
    name: str, dp: str, rule: str, state: str, scope: str = "group"
) -> TemplateRow:
    return TemplateRow(scope, name, dp, rule, state, "tv1-draft-2026.10.22")


def ctx_of(
    cells: list[BaselineCell],
    *,
    groups=None,
    template=None,
    graph=None,
    evidence=None,
    f1=(),
    audited=None,
    zwa=None,
) -> rules.Context:
    return rules.Context(
        baseline={c.key: c for c in cells},
        groups=groups or {},
        template=template or {},
        graph=graph or {},
        evidence=evidence or Evidence(),
        f1_removed=tuple(f1),
        zero_when_absent=zwa or {},
        audited=audited or rules.Audited(),
    )


def only(closed, cid, dp):
    return closed.get((cid, dp))


# ---------------------------------------------------------------- model guards
def test_closure_requires_evidence_and_forbids_unclassified():
    with pytest.raises(ValueError, match="evidence"):
        Closure(
            1,
            "T",
            "x",
            "r.x@1",
            "not_in_template",
            None,
            None,
            None,
            None,
            None,
            "DATA-INFERRED",
            {},
        )
    with pytest.raises(ValueError, match="unclassified"):
        Closure(
            1,
            "T",
            "x",
            "r.x@1",
            "defect",
            "unclassified",
            "triage",
            None,
            None,
            None,
            "DATA-INFERRED",
            {"a": 1},
        )
    with pytest.raises(ValueError, match="defect_class"):
        Closure(
            1,
            "T",
            "x",
            "r.x@1",
            "not_presented",
            "vocabulary",
            None,
            None,
            None,
            None,
            "DATA-INFERRED",
            {"a": 1},
        )


# ---------------------------------------------------------------- rule 1
def tmpl_ctx(row_rule="NIT", **kw):
    cells = [cell(1, "bdc_total_investment_income")]
    return ctx_of(
        cells,
        groups={1: group(1, **kw.pop("g", {}))},
        template={
            ("group", "corporate", "bdc_total_investment_income"): trow(
                "corporate", "bdc_total_investment_income", row_rule, "not_in_template"
            ),
            **kw.pop("extra", {}),
        },
    )


def test_template_nit_is_pending_until_the_group_is_audited():
    closed = rules.run(tmpl_ctx(), [rules.RULE_TEMPLATE])
    c = only(closed, 1, "bdc_total_investment_income")
    assert (
        c is not None and c.state == "defect" and c.defect_class == "evidence_pending"
    )
    assert c.owner == "sector_analyst" and c.candidate_state == "not_in_template"
    assert c.evidence["group_evidence_accession"] == "0000000000-26-000001"
    assert c.evidence_level == "DATA-INFERRED"


def test_audited_group_promotes_to_the_legitimate_state():
    ctx = tmpl_ctx()
    ctx.audited = rules.Audited(groups=frozenset({"corporate"}))
    c = only(rules.run(ctx, [rules.RULE_TEMPLATE]), 1, "bdc_total_investment_income")
    assert (
        c is not None
        and c.state == "not_in_template"
        and c.defect_class is None
        and c.owner is None
    )


@pytest.mark.parametrize("row_rule", ["REQ", "COND", "REP"])
def test_template_non_nit_rows_never_close(row_rule):
    assert rules.run(tmpl_ctx(row_rule), [rules.RULE_TEMPLATE]) == {}


def test_template_needs_group_evidence_and_no_identity_flag():
    assert rules.run(tmpl_ctx(g={"acc": ""}), [rules.RULE_TEMPLATE]) == {}
    assert (
        rules.run(tmpl_ctx(g={"flags": "identity: renamed"}), [rules.RULE_TEMPLATE])
        == {}
    )
    assert (
        rules.run(tmpl_ctx(g={"basis": "excluded_rule"}), [rules.RULE_TEMPLATE]) == {}
    )
    assert (
        rules.run(
            ctx_of([cell(1, "bdc_total_investment_income")]), [rules.RULE_TEMPLATE]
        )
        == {}
    )


def test_overlay_row_that_keeps_the_cell_wins():
    keep = {
        ("overlay", "pre_revenue", "bdc_total_investment_income"): trow(
            "pre_revenue",
            "bdc_total_investment_income",
            "COND",
            "undefined_by_math",
            "overlay",
        )
    }
    assert (
        rules.run(
            tmpl_ctx(g={"overlays": ("pre_revenue",)}, extra=keep),
            [rules.RULE_TEMPLATE],
        )
        == {}
    )
    nit = {
        ("overlay", "pre_revenue", "bdc_total_investment_income"): trow(
            "pre_revenue",
            "bdc_total_investment_income",
            "NIT",
            "not_in_template",
            "overlay",
        )
    }
    assert rules.run(
        tmpl_ctx(g={"overlays": ("pre_revenue",)}, extra=nit), [rules.RULE_TEMPLATE]
    )


def test_valued_and_already_reasoned_cells_are_never_touched():
    ctx = tmpl_ctx()
    ctx.baseline = {
        (1, "bdc_total_investment_income"): cell(
            1,
            "bdc_total_investment_income",
            reason="missing:x",
            klass="period",
            owner="period_engineer",
        )
    }
    assert rules.run(ctx, rules.RULE_ORDER) == {}
    ctx.baseline = {
        (1, "bdc_total_investment_income"): cell(
            1, "bdc_total_investment_income", valued=True
        )
    }
    assert rules.run(ctx, rules.RULE_ORDER) == {}


# ---------------------------------------------------------------- rule 2
def line_ctx(ev: LineEvidence | None, dp="inventory", audited=None):
    e = Evidence(line={} if ev is None else {(1, dp): ev})
    return ctx_of([cell(1, dp)], evidence=e, audited=audited)


def lev(present, combined=False, label=None):
    return LineEvidence("BS", present, combined, label, "0000000000-26-000009", "10-K")


def test_line_absent_combined_and_present_but_not_extracted():
    a = only(rules.run(line_ctx(lev(False)), [rules.RULE_LINE]), 1, "inventory")
    assert (
        a
        and a.candidate_state == "not_presented"
        and a.candidate_wording_key == "state.np.absent"
    )
    assert a.evidence["accession"] == "0000000000-26-000009"
    b = only(
        rules.run(
            line_ctx(lev(True, True, "Accounts payable and accrued")), [rules.RULE_LINE]
        ),
        1,
        "inventory",
    )
    assert b and b.candidate_wording_key == "state.np.combined"
    c = only(rules.run(line_ctx(lev(True)), [rules.RULE_LINE]), 1, "inventory")
    assert (
        c
        and (c.state, c.defect_class, c.owner) == ("defect", "vocabulary", "tag_mapper")
        and c.candidate_state is None
    )


def test_line_statement_not_located_is_no_evidence():
    assert rules.run(line_ctx(lev(None)), [rules.RULE_LINE]) == {}
    assert rules.run(line_ctx(None), [rules.RULE_LINE]) == {}
    ctx = line_ctx(lev(False))
    ctx.evidence = Evidence(line=None)  # not loaded: NOT_RUN
    assert rules.run(ctx, [rules.RULE_LINE]) == {}


def test_line_rule_ignores_derived_twins_and_other_points():
    assert (
        rules.run(line_ctx(lev(False), dp="gross_profit_resolved"), [rules.RULE_LINE])
        == {}
    )


def test_line_audited_detector_promotes():
    c = only(
        rules.run(
            line_ctx(
                lev(False),
                audited=rules.Audited(detectors=frozenset({rules.RULE_LINE})),
            ),
            [rules.RULE_LINE],
        ),
        1,
        "inventory",
    )
    assert c and c.state == "not_presented" and c.defect_class is None


# ---------------------------------------------------------------- rules 3 / 3b
def tag_ctx(dp, fams=(), n=400, group_row=None, audited=None):
    tmpl = {} if group_row is None else {("group", "corporate", dp): group_row}
    return ctx_of(
        [cell(1, dp)],
        groups={1: group(1)},
        template=tmpl,
        evidence=Evidence(tags={1: TagPresence(n, frozenset(fams))}),
        audited=audited,
    )


def test_family_signal_patterns():
    assert rules.family_signal("PaymentsOfDividendsCommonStock", "dividends")
    assert not rules.family_signal(
        "ShareBasedCompensationArrangementByShareBasedPaymentAwardFairValueAssumptionsExpectedDividendRate",
        "dividends",
    )
    assert not rules.family_signal(
        "EquityMethodInvestmentDividendsOrDistributions", "dividends"
    )
    assert rules.family_signal("PaymentsForRepurchaseOfCommonStock", "buybacks")
    assert not rules.family_signal(
        "SecuritiesSoldUnderAgreementsToRepurchase", "buybacks"
    )
    assert rules.family_signal(
        "IncreaseDecreaseInAccountsPayableAndAccruedLiabilities", "ap_change"
    )


def test_zero_requires_absence_and_enough_tags():
    c = only(
        rules.run(tag_ctx("dividends_paid"), [rules.RULE_ZERO]), 1, "dividends_paid"
    )
    assert (
        c
        and c.candidate_state == "evidenced_zero"
        and c.candidate_wording_key == "state.zero.dividends"
    )
    assert c.evidence["distinct_tags_filed"] == 400
    assert (
        rules.run(tag_ctx("dividends_paid", fams=("dividends",)), [rules.RULE_ZERO])
        == {}
    )
    assert (
        rules.run(
            tag_ctx("dividends_paid", n=rules.MIN_TAGS_FOR_ABSENCE - 1),
            [rules.RULE_ZERO],
        )
        == {}
    )
    assert rules.run(tag_ctx("dividends_paid"), [rules.RULE_ZERO]) != {}
    assert (
        rules.run(ctx_of([cell(1, "dividends_paid")]), [rules.RULE_ZERO]) == {}
    )  # tags not loaded


def test_not_presented_by_tag_absence_needs_a_cond_template_row():
    cond = trow("corporate", "cf_ar_change", "COND", "not_presented")
    c = only(
        rules.run(tag_ctx("cf_ar_change", group_row=cond), [rules.RULE_TAG_NP]),
        1,
        "cf_ar_change",
    )
    assert c and c.candidate_state == "not_presented"
    assert (
        rules.run(
            tag_ctx(
                "cf_ar_change",
                group_row=trow("corporate", "cf_ar_change", "REQ", "defect"),
            ),
            [rules.RULE_TAG_NP],
        )
        == {}
    )
    assert rules.run(tag_ctx("cf_ar_change"), [rules.RULE_TAG_NP]) == {}
    assert (
        rules.run(
            tag_ctx("cf_ar_change", fams=("ar_change",), group_row=cond),
            [rules.RULE_TAG_NP],
        )
        == {}
    )


def test_zero_rule_does_not_emit_not_presented_and_vice_versa():
    cond = trow("corporate", "cf_ar_change", "COND", "not_presented")
    assert rules.run(tag_ctx("cf_ar_change", group_row=cond), [rules.RULE_ZERO]) == {}
    assert rules.run(tag_ctx("dividends_paid"), [rules.RULE_TAG_NP]) == {}


# ---------------------------------------------------------------- twin
GRAPH = {
    "a_resolved": GraphNode("a_resolved", "resolved_concept", (("a", "base"),)),
    "a": GraphNode("a", "leaf_concept", ()),
}


def test_twin_inherits_the_twin_state_and_marks_valued_twin_pending_f1():
    ctx = ctx_of(
        [
            cell(1, "a"),
            cell(
                1,
                "a_resolved",
                reason="line_not_presented_in_filing",
                klass="evidence_pending",
                owner="sector_analyst",
            ),
            cell(2, "a"),
            cell(2, "a_resolved", valued=True),
            cell(3, "a"),
            cell(3, "a_resolved"),
        ],
        graph=GRAPH,
        f1=("a",),
    )
    closed = rules.run(ctx, [rules.RULE_TWIN])
    c1 = closed[(1, "a")]
    assert (c1.state, c1.defect_class, c1.owner) == (
        "defect",
        "evidence_pending",
        "sector_analyst",
    )
    assert c1.evidence["twin"] == "a_resolved"
    c2 = closed[(2, "a")]
    assert (
        c2.candidate_state == "not_in_template" and c2.evidence["f1_approved"] is False
    )
    assert (3, "a") not in closed  # twin blank without a state: nothing to inherit
    ctx.audited = rules.Audited(f1_approved=True)
    assert rules.run(ctx, [rules.RULE_TWIN])[(2, "a")].state == "not_in_template"


def test_twin_only_for_f1_removed_rows():
    ctx = ctx_of([cell(2, "a"), cell(2, "a_resolved", valued=True)], graph=GRAPH, f1=())
    assert rules.run(ctx, [rules.RULE_TWIN]) == {}


def test_twin_of_special_cases():
    g = {
        "revenue_sanity_resolved": None,
        "total_debt_resolved": None,
        "x_resolved": None,
    }
    assert rules.twin_of("revenue", g) == "revenue_sanity_resolved"
    assert rules.twin_of("total_debt_split", g) == "total_debt_resolved"
    assert rules.twin_of("x", g) == "x_resolved"
    assert rules.twin_of("y", g) is None


# ---------------------------------------------------------------- passthrough
def metric_graph(role="numerator"):
    return {
        "ratio": GraphNode("ratio", "metric", (("in_a", role), ("in_b", "denominator")))
    }


def test_passthrough_inherits_a_classified_input():
    ctx = ctx_of(
        [
            cell(1, "ratio"),
            cell(
                1, "in_a", reason="missing:x", klass="period", owner="period_engineer"
            ),
            cell(1, "in_b", valued=True),
        ],
        graph=metric_graph(),
    )
    c = rules.run(ctx, [rules.RULE_PASSTHROUGH])[(1, "ratio")]
    assert (c.state, c.defect_class, c.owner) == ("defect", "period", "period_engineer")
    assert c.evidence["input"] == "in_a" and c.evidence["input_source"].startswith(
        "baseline:"
    )


def test_passthrough_never_launders_an_unclassified_input():
    ctx = ctx_of(
        [
            cell(1, "ratio"),
            cell(1, "in_a", reason="incomplete:numerator"),
            cell(1, "in_b", valued=True),
        ],
        graph=metric_graph(),
    )
    assert rules.run(ctx, [rules.RULE_PASSTHROUGH]) == {}
    ctx = ctx_of(
        [cell(1, "ratio"), cell(1, "in_a"), cell(1, "in_b", valued=True)],
        graph=metric_graph(),
    )
    assert (
        rules.run(ctx, [rules.RULE_PASSTHROUGH]) == {}
    )  # reasonless input stays reasonless


def test_passthrough_skips_zero_when_absent_inputs():
    ctx = ctx_of(
        [
            cell(1, "ratio"),
            cell(1, "in_a", reason="x", klass="vocabulary", owner="tag_mapper"),
            cell(1, "in_b", valued=True),
        ],
        graph=metric_graph(),
        zwa={"ratio": frozenset({"in_a"})},
    )
    assert rules.run(ctx, [rules.RULE_PASSTHROUGH]) == {}


def test_evidenced_zero_input_decides_only_a_zero_base_role():
    base = [
        cell(1, "ratio"),
        cell(
            1,
            "in_a",
            reason="no_dividend_history",
            klass="evidence_pending",
            owner="sector_analyst",
            cand="evidenced_zero",
        ),
        cell(1, "in_b", valued=True),
    ]
    assert (
        rules.run(
            ctx_of(base, graph=metric_graph("numerator")), [rules.RULE_PASSTHROUGH]
        )
        == {}
    )
    c = rules.run(ctx_of(base, graph=metric_graph("base_t")), [rules.RULE_PASSTHROUGH])[
        (1, "ratio")
    ]
    assert (
        c.candidate_state == "undefined_by_math"
        and c.candidate_wording_key == "state.nm.zero_base"
    )


def test_legit_input_state_wins_over_a_defect_input():
    g = {
        "ratio": GraphNode(
            "ratio", "metric", (("d", "numerator"), ("n", "denominator"))
        )
    }
    cells = [
        cell(1, "ratio"),
        cell(1, "d", reason="x", klass="period", owner="period_engineer"),
        cell(
            1,
            "n",
            reason="line_not_presented_in_filing",
            klass="evidence_pending",
            owner="sector_analyst",
            cand="not_presented",
        ),
    ]
    c = rules.run(ctx_of(cells, graph=g), [rules.RULE_PASSTHROUGH])[(1, "ratio")]
    assert c.candidate_state == "not_presented" and c.evidence["input"] == "n"


def test_propagation_chains_through_closed_cells_and_is_order_independent():
    g = {
        "m2": GraphNode("m2", "metric", (("m1", "req"),)),
        "m1": GraphNode("m1", "metric", (("leaf", "req"),)),
        "leaf": GraphNode("leaf", "leaf_concept", ()),
    }
    names = ["m2", "m1", "leaf"]
    results = []
    for seed in range(6):
        order = names[:]
        random.Random(seed).shuffle(order)
        cells = [
            cell(
                1,
                n,
                **(
                    {"reason": "r", "klass": "vocabulary", "owner": "tag_mapper"}
                    if n == "leaf"
                    else {}
                ),
            )
            for n in order
        ]
        closed = rules.run(ctx_of(cells, graph=g), [rules.RULE_PASSTHROUGH])
        results.append(
            sorted((k, v.defect_class, v.evidence["input"]) for k, v in closed.items())
        )
    assert results[0] == [
        ((1, "m1"), "vocabulary", "leaf"),
        ((1, "m2"), "vocabulary", "m1"),
    ]
    assert all(r == results[0] for r in results)


# ---------------------------------------------------------------- engine
def test_precedence_template_beats_absence_beats_zero():
    cond = trow("corporate", "cf_ar_change", "COND", "not_presented")
    nit = trow("corporate", "cf_ar_change", "NIT", "not_in_template")
    base = tag_ctx("cf_ar_change", group_row=nit)
    assert (
        rules.run(base, rules.RULE_ORDER)[(1, "cf_ar_change")].rule_id
        == rules.RULE_TEMPLATE
    )
    base = tag_ctx("cf_ar_change", group_row=cond)
    assert (
        rules.run(base, rules.RULE_ORDER)[(1, "cf_ar_change")].rule_id
        == rules.RULE_TAG_NP
    )


def test_run_evaluates_only_the_named_rules_and_rejects_unknown_ones():
    ctx = tmpl_ctx()
    assert rules.run(ctx, []) == {}
    assert rules.run(ctx, [rules.RULE_ZERO]) == {}
    with pytest.raises(ValueError, match="unknown"):
        rules.run(ctx, ["template.membership@2"])


def test_flags_default_off_and_rules_registered():
    assert rules.active_rules({}) == frozenset()
    for rid in rules.RULE_ORDER:
        assert rid in rf.RULES and rf.RULES[rid].dry_run
    env = {rf.ENV_DRYRUN: f"{rules.RULE_TEMPLATE},{rules.RULE_ZERO}"}
    assert rules.active_rules(env) == {rules.RULE_TEMPLATE, rules.RULE_ZERO}
    env = {rf.ENV_ENABLED: rules.RULE_PASSTHROUGH}
    assert rules.active_rules(env) == {rules.RULE_PASSTHROUGH}


# ---------------------------------------------------------------- inputs / outputs
def test_pinned_input_hash_mismatch_is_loud(tmp_path: Path):
    p = tmp_path / "group_assignment_v2.csv"
    p.write_text("company_id\n1\n")
    with pytest.raises(InputHashError):
        load_groups(p)
    assert set(PINNED_SHA256) == {"group_assignment_v2.csv", "template_v1_draft.csv"}


def test_blank_reason_row_matches_migration_0100_constraints():
    pend = Closure(
        1,
        "T",
        "x",
        "template.membership@1",
        "defect",
        "evidence_pending",
        "sector_analyst",
        "not_in_template",
        "state.defect",
        None,
        "DATA-INFERRED",
        {"k": 1},
    )
    row = to_blank_reason_row(pend, "FY", "2025-01-01", "2025-12-31")
    assert row["state"] == "defect" and row["defect_class"] and row["owner"]
    assert row["root_cause_class"] in ROOT_CAUSE_CLASSES
    assert re.match(r"^[a-z][a-z0-9_]*(\.[A-Za-z0-9_]+)+@[0-9]+$", row["rule_id"])
    legit = Closure(
        1,
        "T",
        "x",
        "template.membership@1",
        "not_in_template",
        None,
        None,
        None,
        None,
        None,
        "DATA-INFERRED",
        {"k": 1},
    )
    r2 = to_blank_reason_row(legit, "FY", "2025-01-01", "2025-12-31")
    assert (
        r2["defect_class"] is None
        and r2["owner"] is None
        and r2["root_cause_class"] is None
    )


def test_the_package_cannot_write_to_a_database():
    root = Path(rules.__file__).parent
    text = "\n".join(p.read_text() for p in root.glob("*.py"))
    code = re.sub(r'""".*?"""', "", text, flags=re.DOTALL)
    assert not re.search(
        r"\b(insert\s+into|delete\s+from|update\s+\w+\s+set|truncate\s|alter\s+table|create\s+table|drop\s+table)\b",
        code,
        re.IGNORECASE,
    )
    assert "default_transaction_read_only=on" in Path(db_evidence.__file__).read_text()
    assert (
        db_evidence.STATEMENT_TIMEOUT_MS == 20_000
        and db_evidence.MAX_APP_BACKENDS == 12
    )


class _FakeCursor:
    def __init__(self, n):
        self.n = n

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def execute(self, *a, **k):
        pass

    def fetchone(self):
        return (self.n,)


class _FakeConn:
    def __init__(self, n):
        self.n = n

    def cursor(self):
        return _FakeCursor(self.n)


def test_backend_guard_refuses_when_too_many_sessions_are_open():
    assert db_evidence.check_backend_guard(_FakeConn(12)) == 12
    with pytest.raises(db_evidence.BackendGuardError):
        db_evidence.check_backend_guard(_FakeConn(13))


# ---------------------------------------------------------------- smoke on the committed inputs
def test_committed_baseline_and_rules_reconcile_without_a_database():
    from scrooner_pipeline.reasons import dry_run

    ctx = dry_run.build_context(Evidence())
    base = load_baseline()
    assert sum(1 for b in base.values() if not b.valued) == 37392
    reasonless = rules.reasonless_cells(ctx.baseline)
    assert len(reasonless) == 13349
    closed = rules.run(ctx, rules.RULE_ORDER)
    assert len(closed) >= 5000
    assert all(ctx.baseline[k].reasonless for k in closed)
    summary = dry_run.summarize(ctx, closed)
    assert summary["closed"] + len(summary["residue"]) == summary["targets"]  # type: ignore[arg-type]
    # every closure carries evidence and is never 'unclassified'
    assert all(c.evidence and c.defect_class != "unclassified" for c in closed.values())
    # none of the evidence rules ran: their cells are untouched, not guessed
    assert not any(
        c.rule_id in (rules.RULE_LINE, rules.RULE_TAG_NP, rules.RULE_ZERO)
        for c in closed.values()
    )


def test_precedence_template_beats_zero_when_both_apply():
    nit = trow("corporate", "dividends_paid", "NIT", "not_in_template")
    ctx = tag_ctx("dividends_paid", group_row=nit)
    assert (
        rules.run(ctx, rules.RULE_ORDER)[(1, "dividends_paid")].rule_id
        == rules.RULE_TEMPLATE
    )
    assert (
        rules.run(ctx, [rules.RULE_ZERO])[(1, "dividends_paid")].rule_id
        == rules.RULE_ZERO
    )


def test_propagation_rounds_read_a_frozen_snapshot_of_the_previous_round():
    # "a_m" sorts before "x_metric": an in-place pass would let x_metric see a_m's
    # fresh closure and prefer it (legit beats defect); the round semantics do not.
    g = {
        "a_m": GraphNode("a_m", "metric", (("leaf", "req"),)),
        "x_metric": GraphNode("x_metric", "metric", (("d", "req"), ("a_m", "req"))),
    }
    cells = [
        cell(1, "a_m"),
        cell(1, "x_metric"),
        cell(1, "d", reason="x", klass="period", owner="period_engineer"),
        cell(
            1,
            "leaf",
            reason="line_not_presented_in_filing",
            klass="evidence_pending",
            owner="sector_analyst",
            cand="not_presented",
        ),
    ]
    closed = rules.run(ctx_of(cells, graph=g), [rules.RULE_PASSTHROUGH])
    assert closed[(1, "x_metric")].evidence["input"] == "d"
    assert closed[(1, "a_m")].evidence["input"] == "leaf"


def test_collaboration_revenue_is_not_closed_by_tag_absence():
    # REGN, VRTX, ALNY, BMY and LLY disclose collaboration revenue with no
    # undimensioned "Collaborat" tag; tag-name absence is not evidence there.
    assert "collaborative_arrangement_revenue" not in rules.FAMILY_BY_DATA_POINT
    assert not any("Collaborat" in f.include for f in rules.FAMILIES.values())
    # the working-capital change families also catch custom change-style names
    assert rules.family_signal("CompanyChangeInReceivables", "ar_change")
    assert rules.family_signal("IncreaseDecreaseInInventories", "inventory_change")
