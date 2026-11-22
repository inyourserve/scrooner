"""metrics/registry.py::badge_for: the resolver row's fallback step -> its data_points.csv badge (one-display-path
plan 2026-11-22, step 1). A step that is not exactly one of the data point's steps raises; never as_printed by default."""

import re

import pytest
from scrooner_pipeline.mapper import resolver_files as rf
from scrooner_pipeline.metrics import registry as reg

DPS = reg.load_data_points()


def _row(decision, flags="roles", label=""):
    nodes = "X=1 [R2.htm:3]" + (f" | why: face prints '{label}'" if label else "")
    return {"decision": decision, "flags": flags, "nodes": nodes}


def _matches_a_step(badge, d):
    """badge is one of d's badges, or a <placeholder> badge of d filled with printed text."""
    for b in d.badges:
        if b == badge:
            return True
        if "<" in b:
            pat = re.escape(b[: b.index("<")]) + ".+"
            if re.fullmatch(pat, badge):
                return True
    return False


def test_every_printed_step_gives_as_printed():
    for (dp, sector), d in DPS.items():
        if d.applies and "as_printed" in d.badges:
            assert reg.badge_for(dp, sector, _row("mapped")) == "as_printed"


@pytest.mark.parametrize(
    "dp,decision,flags,badge",
    [
        (
            "gross_profit",
            "derived_not_printed",
            "core;DERIVED",
            "derived:revenue-cost_of_revenue",
        ),
        (
            "total_liabilities",
            "derived_not_printed",
            "core;DERIVED",
            "derived:liabilities_and_equity-total_equity-temporary_equity",
        ),
        (
            "income_before_tax",
            "derived_not_printed",
            "core",
            "derived:net_income_incl_nci+income_tax_expense",
        ),
        (
            "shares_outstanding",
            "derived_not_printed",
            "roles;derived_issued_less_treasury",
            "derived:shares_issued-treasury_shares",
        ),
        (
            "comprehensive_income",
            "derived_not_printed",
            "roles;ci_parent_derived",
            "derived:ci_incl_nci-ci_nci",
        ),
        (
            "stockholders_equity",
            "derived_not_printed",
            "roles;equity_parent_derived",
            "derived:total_equity-noncontrolling_interest",
        ),
        (
            "total_debt",
            "component_sum",
            "total_debt",
            "derived:sum(printed debt lines)+finance_leases",
        ),
        (
            "sga_expense",
            "component_sum",
            "roles",
            "derived:selling_and_marketing+general_and_administrative",
        ),
        ("capex", "component_sum", "cf_family", "derived:sum(printed capex lines)"),
        (
            "operating_expenses",
            "component_sum",
            "band",
            "derived:sum(printed operating lines)",
        ),
        (
            "weighted_basic_shares",
            "component_sum",
            "class_sum",
            "derived:sum(class weighted basic shares)",
        ),
    ],
)
def test_derived_and_sum_rows_get_their_derived_step(dp, decision, flags, badge):
    got = reg.badge_for(dp, "general", _row(decision, flags))
    assert got == badge
    assert got != "as_printed"


def test_a_derived_row_is_never_as_printed():
    # the DERIVED flag wins over a 'mapped' decision: the value is not a printed line
    assert (
        reg.badge_for("gross_profit", "general", _row("mapped", "core;DERIVED"))
        == "derived:revenue-cost_of_revenue"
    )


def test_combined_row_names_the_label_items():
    got = reg.badge_for(
        "accounts_payable",
        "general",
        _row(
            "combined",
            "roles;only_combined",
            "Accounts payable and accrued liabilities",
        ),
    )
    assert got == "combined:Accounts payable and accrued liabilities"
    # a fixed combined step is returned as written
    assert (
        reg.badge_for(
            "capex",
            "general",
            _row(
                "combined", "cf_family", "Purchases of property and intangible assets"
            ),
        )
        == "combined:intangible assets"
    )


def test_two_combined_steps_are_told_apart_by_the_label():
    ie = "interest_expense"
    assert (
        reg.badge_for(
            ie,
            "general",
            _row("combined", label="Interest expense, net of interest income"),
        )
        == "combined:net of interest income"
    )
    assert (
        reg.badge_for(
            ie, "general", _row("combined", label="Interest and other expense")
        )
        == "combined:other expense"
    )
    with pytest.raises(reg.BadgeUndecided):
        reg.badge_for(ie, "general", _row("combined", label="Financing costs"))


@pytest.mark.parametrize(
    "dp,row",
    [
        # a sum where the data point has no additive derived step (its only derived step subtracts)
        ("gross_profit", _row("component_sum")),
        # a sum of a data point with no derived step at all
        ("accounts_payable", _row("component_sum")),
        # two non-sum derived steps and no flag naming one
        ("operating_income", _row("derived_not_printed", "core;DERIVED")),
        # a combined line where the data point has no combined step
        ("basic_eps", _row("combined", label="Earnings per share")),
        # a combined placeholder step but no printed label to fill it
        ("accounts_payable", _row("combined")),
        # decisions that carry no value
        ("revenue", _row("not_presented")),
        ("revenue", _row("not_in_template")),
        ("revenue", _row("no_role")),
        # a data point the registry does not define
        ("intangible_assets", _row("mapped")),
    ],
)
def test_ambiguous_or_valueless_steps_raise(dp, row):
    with pytest.raises(reg.BadgeUndecided):
        reg.badge_for(dp, "general", row)


def test_not_applicable_is_a_state_not_a_badge():
    assert not DPS[("accounts_payable", "bank")].applies
    with pytest.raises(reg.BadgeUndecided):
        reg.badge_for("accounts_payable", "bank", _row("mapped"))


def test_every_badge_from_the_live_resolver_output_is_a_step_of_its_data_point():
    """Sweep the committed resolver output: every badge badge_for returns is one of the data point's own steps, every
    mapped row of a data point with a printed step is as_printed, and each derived step badge_for can reach is
    reached by some row."""
    if not rf.resolver_files():
        pytest.skip("no resolver output in this checkout")
    seen: set[str] = set()
    undecided = 0
    with rf.open_rows() as rows:
        for r in rows:
            key = (r["data_point"], "general")
            if key not in DPS or not DPS[key].applies:
                continue
            if r["decision"] not in (
                "mapped",
                "component_sum",
                "derived_not_printed",
                "combined",
            ):
                continue
            try:
                b = reg.badge_for(r["data_point"], "general", r)
            except reg.BadgeUndecided:
                assert r["decision"] != "mapped" or "as_printed" not in DPS[key].badges
                undecided += 1
                continue
            assert reg._badge_ok(b), b
            assert _matches_a_step(b, DPS[key]), (
                r["ticker"],
                r["data_point"],
                r["decision"],
                b,
            )
            if r["decision"] in (
                "component_sum",
                "derived_not_printed",
            ) or "DERIVED" in reg.resolver_flags(r):
                assert b.startswith("derived:"), (r["ticker"], r["data_point"], b)
            seen.add(b)
    assert "as_printed" in seen
    assert any(b.startswith("derived:") for b in seen)
    assert any(b.startswith("combined:") for b in seen)


def test_a_derived_flag_on_the_resolver_row_names_the_step():
    """resolver .89: an opex component_sum names its step in a `derived:` flag (X117 costs total - COR vs X89 sum of
    the printed operating lines); without a flag the only additive step is the answer."""
    row = _row(
        "component_sum", "roles;derived:total_costs_and_expenses-cost_of_revenue"
    )
    assert (
        reg.badge_for("operating_expenses", "general", row)
        == "derived:total_costs_and_expenses-cost_of_revenue"
    )
    assert (
        reg.badge_for("operating_expenses", "general", _row("component_sum", "roles"))
        == "derived:sum(printed operating lines)"
    )
    # a flag that is not one of the data point's steps is ignored
    row = _row("component_sum", "roles;derived:revenue-cost_of_revenue")
    assert (
        reg.badge_for("operating_expenses", "general", row)
        == "derived:sum(printed operating lines)"
    )


@pytest.mark.parametrize(
    "dp,flags,badge",
    [
        # MA and WMT certifications 2026-11-22: shown sums of printed lines had no registry step, so no badge
        (
            "interest_expense",
            "roles;band",
            "derived:sum(printed interest expense lines)",
        ),
        (
            "other_income_expense_net",
            "roles;band",
            "derived:sum(printed nonoperating lines)",
        ),
        (
            "shares_outstanding",
            "bs_family;class_sum",
            "derived:sum(class shares outstanding)",
        ),
    ],
)
def test_printed_line_sums_have_their_own_registry_step(dp, flags, badge):
    for sector in reg.SECTORS:
        assert reg.badge_for(dp, sector, _row("component_sum", flags)) == badge
        assert (
            DPS[(dp, sector)].badges[1] == badge
        )  # step 2, right after the printed line


def test_a_filing_read_value_carrying_a_derived_badge_gets_that_step_not_as_printed():
    """A filing read VALUE row is `mapped`; its reader badge (filing_reads.badge_flag) names the derivation (WMT other
    income FY2015 = 0 by the pretax identity)."""
    f = "filing_read;stated_zero;replaces:not_presented;derived:income_before_tax-operating_income+interest_expense-interest_income"
    assert (
        reg.badge_for("other_income_expense_net", "general", _row("mapped", f))
        == "derived:income_before_tax-operating_income+interest_expense-interest_income"
    )
    # a derived flag the data point does not list never overrides the printed step
    assert (
        reg.badge_for(
            "revenue", "general", _row("mapped", "filing_read;derived:nonsense")
        )
        == "as_printed"
    )
