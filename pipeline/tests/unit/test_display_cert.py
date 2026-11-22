"""Display certification (CERTIFICATION-METHOD-2026-11-16.md): pure checks over an injected fact source."""

from __future__ import annotations

import csv
from decimal import Decimal as D
from pathlib import Path

import pytest

from scrooner_pipeline.certification import display_cert as dc

HDR = [
    "data_point",
    "fiscal_year",
    "period_end",
    "shown_value",
    "accession",
    "r_page",
    "tag",
    "parts",
    "display",
]
ACC = "0000000001-24-000001"


def write_cov(tmp_path: Path, rows: list[list[str]]) -> Path:
    p = tmp_path / "cov.csv"
    with open(p, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(HDR)
        w.writerows(rows)
    return p


def fact(tag, value, ddate="2023-12-31", qtrs=4, dims="", acc=ACC, reports=("R4",)):
    return dc.Fact(acc, tag, ddate, qtrs, dims, D(value), tuple(reports))


def cell(
    dp="revenue",
    value="100",
    tag="Revenues",
    parts=(),
    r="R4",
    pe="2023-12-31",
    display=dc.SHOWN,
):
    return dc.Cell(
        dp,
        "2023",
        pe,
        display,
        D(value) if value is not None else None,
        ACC,
        r,
        tag,
        tuple(parts),
    )


# ---------------------------------------------------------------- parsing
def test_parse_parts_keeps_sign_and_normalizes_dims():
    ps = dc.parse_parts(
        f"-GainLoss=-1000@{ACC}#R2;Debt[us-gaap:DebtInstrumentAxis=us-gaap:NotesMember]=5@{ACC}#3"
    )
    assert ps[0].sign == -1 and ps[0].value == D(-1000) and ps[0].r_page == "R2"
    assert (
        ps[1].sign == 1
        and ps[1].dims == "DebtInstrument=Notes"
        and ps[1].r_page == "R3"
    )


def test_norm_dims_matches_fsn_spelling():
    assert (
        dc.norm_dims("EquityComponents=AdditionalPaidInCapital;")
        == "EquityComponents=AdditionalPaidInCapital"
    )
    assert dc.norm_dims("b=y;a=x") == "a=x;b=y"


def test_read_coverage_requires_display_column(tmp_path):
    p = tmp_path / "c.csv"
    p.write_text("data_point,fiscal_year\nrevenue,2023\n")
    with pytest.raises(ValueError, match="display"):
        dc.read_coverage(p)


# ---------------------------------------------------------------- gate
def test_gate_fails_open_missing_locator_and_bad_parts_sum():
    parts = dc.parse_parts(f"A=10@{ACC}#R4;-B=3@{ACC}#R4")
    cells = [
        cell(display=dc.OPEN),
        cell(r=""),
        cell(value="13", parts=parts),  # signed sum is 7
        cell(value="7", parts=parts),
    ]
    fails = [f.detail for f in dc.gate(cells)]
    assert "OPEN cell" in fails
    assert any("no accession or R page" in f for f in fails)
    assert sum("signed parts sum" in f for f in fails) == 1


def test_gate_fails_row_hidden_and_shown():
    cells = [cell(dp="sbc", display=dc.HIDDEN_ROW), cell(dp="sbc")]
    assert [f.severity for f in dc.gate(cells)] == ["FAIL"]


# ---------------------------------------------------------------- shown cells
def test_check_cell_match_mismatch_locator_notfound():
    facts = [fact("Revenues", "-100")]
    assert (
        dc.check_cell(cell(), facts).result == "MATCH"
    )  # magnitude match for single-tag cells
    assert dc.check_cell(cell(value="101"), facts).result == "MISMATCH"
    assert dc.check_cell(cell(r="R9"), facts).result == "LOCATOR"
    assert dc.check_cell(cell(tag="Other"), facts).result == "NOT_FOUND"
    # a 52/53-week year end a few days off still matches; a different year does not
    assert dc.check_cell(cell(pe="2023-12-29"), facts).result == "MATCH"
    assert dc.check_cell(cell(pe="2022-12-31"), facts).result == "NOT_FOUND"


def test_check_cell_duration_and_dimensions_must_match():
    facts = [fact("Revenues", "100", qtrs=1), fact("Revenues", "100", dims="Segment=X")]
    assert dc.check_cell(cell(), facts).result == "NOT_FOUND"


def test_check_cell_signed_parts():
    parts = dc.parse_parts(f"A=10@{ACC}#R4;-B=3@{ACC}#R4")
    facts = [fact("A", "10"), fact("B", "3")]
    assert dc.check_cell(cell(value="7", parts=parts), facts).result == "MATCH"
    # a part the proof misread fails even when the shown value happens to agree
    assert (
        dc.check_cell(
            cell(value="7", parts=parts), [fact("A", "11"), fact("B", "4")]
        ).result
        == "MISMATCH"
    )


# ---------------------------------------------------------------- total debt
def debt_cell(value):
    return cell(dp="total_debt", value=value, tag="", pe="2023-12-31")


def test_debt_adds_note_finance_leases():
    facts = [
        fact("LongTermDebtNoncurrent", "100", qtrs=0),
        fact("CommercialPaper", "20", qtrs=0),
        fact("FinanceLeaseLiability", "5", qtrs=0, reports=("R40",)),
    ]
    assert dc.check_debt(debt_cell("125"), facts).result == "MATCH"
    r = dc.check_debt(debt_cell("120"), facts)  # proof missed the leases
    assert r.result == "MISMATCH" and r.perimeter == D(125)


def test_debt_does_not_double_count_leases_inside_face_tag():
    facts = [
        fact("LongTermDebtAndCapitalLeaseObligations", "100", qtrs=0),
        fact("CapitalLeaseObligations", "5", qtrs=0),
    ]
    assert dc.check_debt(debt_cell("100"), facts).result == "MATCH"


def test_debt_prefers_components_over_longtermdebt_total():
    facts = [
        fact("LongTermDebt", "110", qtrs=0),
        fact("LongTermDebtCurrent", "10", qtrs=0),
        fact("LongTermDebtNoncurrent", "100", qtrs=0),
    ]
    assert dc.check_debt(debt_cell("110"), facts).result == "MATCH"


def test_debt_smaller_perimeter_is_review_not_pass():
    facts = [fact("LongTermDebtNoncurrent", "100", qtrs=0)]
    assert dc.check_debt(debt_cell("130"), facts).result == "REVIEW"


# ---------------------------------------------------------------- hides
def test_hidden_row_fails_when_family_fact_exists():
    cells = [cell(dp="interest_income", display=dc.HIDDEN_ROW)]
    hit = dc.check_hidden_rows(cells, [fact("InvestmentIncomeInterest", "9")])
    assert hit[0].severity == "FAIL"
    assert (
        dc.check_hidden_rows(
            cells, [fact("InvestmentIncomeInterest", "9", dims="Segment=X")]
        )[0].severity
        == "INFO"
    )
    assert dc.check_hidden_rows(cells, [])[0].severity == "INFO"


def test_hidden_row_unknown_family_needs_review():
    assert (
        dc.check_hidden_rows([cell(dp="mystery", display=dc.HIDDEN_ROW)], [])[
            0
        ].severity
        == "REVIEW"
    )


def test_hidden_year_fails_when_any_periodic_filing_presents_it():
    # revenue is not on the hide allowlist: only a pre-filing year may be hidden
    cells = [cell(display=dc.HIDDEN_YEAR, pe="2019-12-31")]
    assert (
        dc.check_hidden_years(cells, {ACC: ["2019-12-31", "2020-12-31"]})[0].severity
        == "FAIL"
    )
    assert dc.check_hidden_years(cells, {ACC: ["2020-12-31|4"]}) == []


def test_allowlisted_hidden_year_needs_no_printed_line_in_any_presenting_filing():
    """Dhairya ruling 2026-11-16: an allowlisted row may hide a presented year only when no
    periodic filing presenting that period prints the row's line (a dash counts as printed)."""
    shown = cell(
        dp="dividends_paid", tag="PaymentsOfDividendsCommonStock", pe="2018-12-31"
    )
    hidden = cell(
        dp="dividends_paid", display=dc.HIDDEN_YEAR, pe="2023-12-31", value=None, tag=""
    )
    cells = [shown, hidden]
    ye = {"A": ["2023-12-31|4", "2023-12-31|0"], "B": ["2018-12-31|4"]}
    ok = dc.check_hidden_years(cells, ye, {"B": {"PaymentsOfDividendsCommonStock"}})
    assert [f.severity for f in ok] == ["INFO"]
    # the 2023 10-K prints the line (value or dash): the hide is wrong
    bad = dc.check_hidden_years(cells, ye, {"A": {"PaymentsOfDividendsCommonStock"}})
    assert [f.severity for f in bad] == ["FAIL"]
    # a duration row is presented only by an annual column, not by a balance-sheet date
    assert (
        dc.check_hidden_years(
            cells, {"A": ["2023-12-31|0"]}, {"A": {"PaymentsOfDividendsCommonStock"}}
        )
        == []
    )


def test_clopper_pearson_known_values():
    assert dc.clopper_pearson_upper(0, 32) == pytest.approx(0.0894, abs=1e-4)
    assert dc.clopper_pearson_upper(0, 2995) == pytest.approx(0.0010, abs=1e-5)
    assert dc.clopper_pearson_upper(1, 32) == pytest.approx(0.1392, abs=1e-3)
    assert dc.clopper_pearson_upper(0, 0) == 1.0


def test_draw_is_deterministic_and_excludes_total_debt():
    cells = [cell(dp=f"d{i}") for i in range(50)] + [debt_cell("1")]
    a, b = dc.draw(cells, "s"), dc.draw(cells, "s")
    assert a == b and len(a) == 32 and all(c.data_point != "total_debt" for c in a)
    assert dc.draw(cells, "t") != a


class Src:
    def __init__(self, facts=(), company=(), years=None, control=True):
        self.control = control
        self.f, self.c, self.y = (
            list(facts),
            list(company),
            years if years is not None else {ACC: ["2023-12-31"]},
        )

    def facts(self, accessions, tags):
        return self.f

    def company_facts(self, cik, tags):
        return [*self.c, fact("Assets", "1", qtrs=0)] if self.control else self.c

    def periodic_year_ends(self, cik):
        return self.y

    def presented_lines(self, cik, tags):
        return {ACC: {"Assets"}}


def test_certify_pass_fail_and_wrong_cik(tmp_path):
    cov = write_cov(
        tmp_path,
        [
            [
                "revenue",
                "2023",
                "2023-12-31",
                "100",
                ACC,
                "R4.htm",
                "Revenues",
                "",
                dc.SHOWN,
            ],
            ["sbc", "2023", "2023-12-31", "", "", "", "", "", dc.HIDDEN_ROW],
        ],
    )
    ok = dc.certify("T", "1", cov, Src([fact("Revenues", "100")]))
    assert ok.verdict == "PASS" and ok.errors == 0 and len(ok.shown) == 1
    # fsn.* can miss a fact: NOT_FOUND goes to the approver (REVIEW), it is not counted as a wrong value
    nf = dc.certify("T", "1", cov, Src([fact("Revenues", "100", acc="other")]))
    assert nf.verdict == "REVIEW" and nf.errors == 0
    assert dc.certify("T", "1", cov, Src([fact("Revenues", "99")])).verdict == "FAIL"
    assert (
        dc.certify(
            "T",
            "1",
            cov,
            Src(
                [fact("Revenues", "100")], company=[fact("ShareBasedCompensation", "3")]
            ),
        ).verdict
        == "FAIL"
    )
    assert (
        dc.certify("T", "1", cov, Src([fact("Revenues", "100")], years={})).verdict
        == "FAIL"
    )
    assert "PASS" in dc.render(ok, "2026-11-16")


def test_bundle_source_round_trip(tmp_path):
    cov = write_cov(
        tmp_path,
        [["revenue", "2023", "2023-12-31", "100", ACC, "R4", "Revenues", "", dc.SHOWN]],
    )
    bundle = {
        "facts": [
            [ACC, "Revenues", "2023-12-31", 4, "", "100", ["R4"]],
            [ACC, "Revenues", "2023-12-31", 4, "", None, []],
        ],
        "company_facts": [[ACC, "Assets", "2023-12-31", 0, "", "1", ["R2"]]],
        "year_ends": {ACC: ["2023-12-31"]},
    }
    assert dc.certify("T", "1", cov, dc.BundleFactSource(bundle)).verdict == "PASS"
    sql = dc.bundle_sql("1", dc.plan("T", cov))
    assert "fsn.value" in sql and ACC in sql and "statement_timeout" in sql
    with pytest.raises(ValueError):
        dc._lit("x'; drop table y; --")


def test_pooled_bound_uses_latest_pass_rows(tmp_path):
    reg = tmp_path / "r.csv"
    with open(reg, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(dc.REGISTRY_HEADER)
        w.writerow(["A", "d", "FAIL", "", "", 32, 1, "", ""])
        w.writerow(["A", "d", "PASS", "", "", 32, 0, "", ""])
        w.writerow(["B", "d", "PASS", "", "", 32, 0, "", ""])
        w.writerow(["C", "d", "FAIL", "", "", 32, 2, "", ""])
    n, k, ub = dc.pooled_bound(reg)
    assert (n, k) == (64, 0) and ub == pytest.approx(dc.clopper_pearson_upper(0, 64))


def test_read_request(tmp_path):
    p = tmp_path / "r.md"
    p.write_text(
        "# Certification request: BA (company 207), 2026-11-15\n\n- coverage csv: `x/BA.csv`\n- sha256: `"
        + "a" * 64
        + "`\n"
    )
    r = dc.read_request(p)
    assert (r.ticker, r.company_id, r.coverage) == ("BA", 207, "x/BA.csv")


def test_positive_controls_fail_a_broken_source(tmp_path):
    """2026-11-16: a coreg filter made every query empty; hides then read as 'never reported'."""
    cov = write_cov(
        tmp_path,
        [
            [
                "revenue",
                "2023",
                "2023-12-31",
                "100",
                ACC,
                "R4",
                "Revenues",
                "",
                dc.SHOWN,
            ],
            ["sbc", "2023", "2023-12-31", "", "", "", "", "", dc.HIDDEN_ROW],
        ],
    )
    no_control = dc.certify(
        "T", "1", cov, Src([fact("Revenues", "100")], control=False)
    )
    assert no_control.verdict == "FAIL"
    empty = dc.certify("T", "1", cov, Src([]))
    assert empty.verdict == "FAIL" and any(
        "source broken" in f.detail for f in empty.gate
    )


def test_debt_counts_face_lines_only_and_debtcurrent_supersedes_components():
    # JNJ FY2015: DebtCurrent 7,000 is a note figure; the face prints ShortTermBorrowings 7,004
    jnj = [
        fact("ShortTermBorrowings", "7004", qtrs=0),
        fact("DebtCurrent", "7000", qtrs=0, reports=("R40",)),
        fact("LongTermDebtNoncurrent", "12857", qtrs=0),
    ]
    assert dc.check_debt(debt_cell("19861"), jnj).result == "MATCH"
    # GILD: face DebtCurrent is the total of the current portion printed beside it
    gild = [
        fact("DebtCurrent", "982", qtrs=0),
        fact("LongTermDebtCurrent", "982", qtrs=0),
        fact("LongTermDebtNoncurrent", "21073", qtrs=0),
    ]
    assert dc.check_debt(debt_cell("22055"), gild).result == "MATCH"


def test_hidden_row_evidence_must_be_presented_annual_and_in_window():
    cells = [cell(dp="sga_expense", display=dc.HIDDEN_ROW)]
    unpresented = fact("GeneralAndAdministrativeExpense", "5", reports=())
    quarterly = fact("GeneralAndAdministrativeExpense", "5", qtrs=1)
    out_of_window = fact("GeneralAndAdministrativeExpense", "5", ddate="2014-09-30")
    for f in (unpresented, quarterly, out_of_window):
        assert dc.check_hidden_rows(cells, [f])[0].severity == "INFO", f
    assert (
        dc.check_hidden_rows(cells, [fact("GeneralAndAdministrativeExpense", "5")])[
            0
        ].severity
        == "FAIL"
    )


def test_implausible_per_share_value_is_wrong_even_when_it_matches_the_filing():
    stx = [fact("CommonStockDividendsPerShareDeclared", "2770000")]
    c = cell(
        dp="dividends_per_share",
        value="2770000",
        tag="CommonStockDividendsPerShareDeclared",
    )
    assert dc.check_cell(c, stx).result == "MISMATCH"
    ok = cell(
        dp="dividends_per_share",
        value="2.77",
        tag="CommonStockDividendsPerShareDeclared",
    )
    assert (
        dc.check_cell(ok, [fact("CommonStockDividendsPerShareDeclared", "2.77")]).result
        == "MATCH"
    )


def test_derived_total_liabilities_uses_total_equity_including_nci():
    # GILD FY2022: 63,171 - 21,209 (incl. NCI -31) = 41,962; parent-only equity would give 41,931
    facts = [
        fact("Assets", "63171", qtrs=0),
        fact("StockholdersEquity", "21240", qtrs=0),
        fact(
            "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
            "21209",
            qtrs=0,
        ),
    ]
    c = cell(dp="total_liabilities", value="41962", tag="")
    assert dc.check_derived(c, [c], facts).result == "MATCH"
    assert (
        dc.check_derived(
            cell(dp="total_liabilities", value="41931", tag=""), [c], facts
        ).result
        == "MISMATCH"
    )


def test_derived_gross_profit_is_shown_revenue_less_cost():
    cells = [
        cell(dp="revenue", value="28754"),
        cell(dp="cost_of_revenue", value="6251"),
    ]
    gp = cell(dp="gross_profit", value="22503", tag="")
    assert dc.check_derived(gp, cells, []).result == "MATCH"
    assert (
        dc.check_derived(
            cell(dp="gross_profit", value="22500", tag=""), cells, []
        ).result
        == "MISMATCH"
    )
    assert (
        dc.check_derived(cell(dp="ebitda", value="1", tag=""), cells, []).result
        == "NOT_FOUND"
    )


def test_presented_lines_positive_control(tmp_path):
    cov = write_cov(
        tmp_path,
        [
            [
                "revenue",
                "2023",
                "2023-12-31",
                "100",
                ACC,
                "R4",
                "Revenues",
                "",
                dc.SHOWN,
            ],
            [
                "dividends_paid",
                "2022",
                "2022-12-31",
                "",
                "",
                "",
                "",
                "",
                dc.HIDDEN_YEAR,
            ],
        ],
    )

    class NoLines(Src):
        def presented_lines(self, cik, tags):
            return {}

    years = {ACC: ["2023-12-31|4", "2022-12-31|4"]}
    ok = dc.certify("T", "1", cov, Src([fact("Revenues", "100")], years=years))
    assert ok.verdict == "PASS"
    broken = dc.certify("T", "1", cov, NoLines([fact("Revenues", "100")], years=years))
    assert broken.verdict == "FAIL" and any(
        "presented-lines" in f.detail for f in broken.gate
    )


def test_hide_reason_must_be_a_doc02_hide_class():
    ok = dc.Cell(
        "sbc",
        "2023",
        "2023-12-31",
        dc.HIDDEN_ROW,
        None,
        "",
        "",
        "",
        (),
        "structural_not_presented",
    )
    combined = dc.Cell(
        "sbc",
        "2022",
        "2022-12-31",
        dc.HIDDEN_ROW,
        None,
        "",
        "",
        "",
        (),
        "line_presented_combined",
    )
    era = dc.Cell(
        "sga_expense",
        "2016",
        "2016-12-31",
        dc.HIDDEN_ROW,
        None,
        "",
        "",
        "",
        (),
        "era_unmapped",
    )
    old_export = dc.Cell(
        "sga_expense", "2016", "2016-12-31", dc.HIDDEN_ROW, None, "", "", ""
    )
    pre = dc.Cell(
        "revenue", "2014", "2014-12-31", dc.HIDDEN_YEAR, None, "", "", "", (), ""
    )
    out = dc.check_hide_reasons([ok, combined, era, old_export, pre])
    assert [(f.data_point, f.severity) for f in out] == [("sga_expense", "FAIL")]


def test_only_combined_hidden_year_passes_the_printed_line_test():
    """Doc 02 rule 2: years hidden as reported only combined are valid if the pure line is not printed."""
    shown = cell(
        dp="comprehensive_income", tag="ComprehensiveIncomeNetOfTax", pe="2021-12-31"
    )
    hid = dc.Cell(
        "comprehensive_income",
        "2017",
        "2017-12-31",
        dc.HIDDEN_YEAR,
        None,
        "",
        "",
        "",
        (),
        "line_presented_combined",
    )
    ye = {"A": ["2017-12-31|4"]}
    assert [f.severity for f in dc.check_hidden_years([shown, hid], ye, {})] == ["INFO"]
    printed = dc.check_hidden_years(
        [shown, hid], ye, {"A": {"ComprehensiveIncomeNetOfTax"}}
    )
    assert [f.severity for f in printed] == ["FAIL"]
    no_reason = dc.Cell(
        "comprehensive_income", "2017", "2017-12-31", dc.HIDDEN_YEAR, None, "", "", ""
    )
    assert [f.severity for f in dc.check_hidden_years([shown, no_reason], ye, {})] == [
        "FAIL"
    ]


def test_certify_fails_a_hide_with_a_non_doc02_reason(tmp_path):
    p = tmp_path / "cov.csv"
    with open(p, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow([*HDR, "reason_code"])
        w.writerow(
            [
                "revenue",
                "2023",
                "2023-12-31",
                "100",
                ACC,
                "R4",
                "Revenues",
                "",
                dc.SHOWN,
                "",
            ]
        )
        w.writerow(
            [
                "sbc",
                "2023",
                "2023-12-31",
                "",
                "",
                "",
                "",
                "",
                dc.HIDDEN_ROW,
                "era_unmapped",
            ]
        )
    run = dc.certify("T", "1", p, Src([fact("Revenues", "100")]))
    assert run.verdict == "FAIL" and any(f.check == "hide_reason" for f in run.hides)


def test_hide_class_column_is_authoritative_and_reason_code_is_evidence():
    """main 532fc006: the export writes hide_class, exactly one of four doc 02 classes."""

    def hid(dp, display, hc, reason="no_role"):
        return dc.Cell(
            dp, "2022", "2022-12-31", display, None, "", "", "", (), reason, hc
        )

    ok = [
        hid(
            "sbc",
            dc.HIDDEN_ROW,
            "structural_not_presented",
            "not_presented_in_any_filing",
        ),
        hid("cf_ap_change", dc.HIDDEN_ROW, "line_presented_combined", "flag_combined"),
        hid("revenue", dc.HIDDEN_YEAR, "pre_filing", "no_public_filing_for_period"),
        hid("dividends_paid", dc.HIDDEN_YEAR, "verified_absent"),
    ]
    assert dc.check_hide_reasons(ok) == []
    bad = [
        hid("sbc", dc.HIDDEN_ROW, ""),
        hid("sbc", dc.HIDDEN_ROW, "era_unmapped"),
        hid("sbc", dc.HIDDEN_ROW, "pre_filing"),
        hid("research_and_development", dc.HIDDEN_YEAR, "verified_absent"),
    ]
    assert [f.severity for f in dc.check_hide_reasons(bad)] == ["FAIL"] * 4


def test_hide_class_combined_year_uses_the_printed_line_test():
    shown = cell(
        dp="comprehensive_income", tag="ComprehensiveIncomeNetOfTax", pe="2021-12-31"
    )
    hid = dc.Cell(
        "comprehensive_income",
        "2017",
        "2017-12-31",
        dc.HIDDEN_YEAR,
        None,
        "",
        "",
        "",
        (),
        "flag_x",
        "line_presented_combined",
    )
    ye = {"A": ["2017-12-31|4"]}
    assert [f.severity for f in dc.check_hidden_years([shown, hid], ye, {})] == ["INFO"]


def test_derived_shares_outstanding_and_eps_never_derived():
    """Founder approvals 2026-11-17 (doc 02, 93c8d6ba)."""
    facts = [
        fact("CommonStockSharesIssued", "3119843000", qtrs=0),
        fact("TreasuryStockCommonShares", "712000000", qtrs=0),
    ]
    so = cell(dp="shares_outstanding", value="2407843000", tag="")
    assert dc.check_derived(so, [so], facts).result == "MATCH"
    assert (
        dc.check_derived(
            cell(dp="shares_outstanding", value="3119843000", tag=""), [so], facts
        ).result
        == "MISMATCH"
    )
    assert (
        dc.check_derived(cell(dp="diluted_eps", value="5.51", tag=""), [], []).result
        == "MISMATCH"
    )


def test_gate_censuses_implausible_per_share_values_outside_the_draw():
    bad = cell(
        dp="dividends_per_share",
        value="2770000",
        tag="CommonStockDividendsPerShareDeclared",
    )
    ok = cell(dp="diluted_eps", value="5.51", tag="EarningsPerShareDiluted")
    assert [f.severity for f in dc.gate([bad, ok])] == ["FAIL"]


def _check_schema(obj, schema, path="$"):
    """Minimal validator for the subset of JSON Schema the certificate schema uses (no new dependency)."""
    t = schema.get("type")
    if t is not None:
        kinds = t if isinstance(t, list) else [t]
        py = {
            "object": dict,
            "array": list,
            "string": str,
            "integer": int,
            "null": type(None),
        }
        assert any(
            isinstance(obj, py[k]) and not (k == "integer" and isinstance(obj, bool))
            for k in kinds
        ), (path, obj, t)
    if "const" in schema:
        assert obj == schema["const"], (path, obj)
    if "enum" in schema:
        assert obj in schema["enum"], (path, obj)
    if "pattern" in schema and isinstance(obj, str):
        import re as _re

        assert _re.search(schema["pattern"], obj), (path, obj)
    if isinstance(obj, dict):
        for k in schema.get("required", []):
            assert k in obj, (path, k)
        props = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            assert set(obj) <= set(props), (path, set(obj) - set(props))
        for k, v in obj.items():
            if k in props:
                _check_schema(v, props[k], f"{path}.{k}")
    if isinstance(obj, list) and "items" in schema:
        for i, v in enumerate(obj):
            _check_schema(v, schema["items"], f"{path}[{i}]")


def test_certificate_json_matches_schema_and_classifies_every_cell(tmp_path):
    import json

    p = tmp_path / "cov.csv"
    with open(p, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow([*HDR, "reason_code", "hide_class"])
        w.writerow(
            [
                "revenue",
                "2023",
                "2023-12-31",
                "100",
                ACC,
                "R4",
                "Revenues",
                "",
                dc.SHOWN,
                "",
                "",
            ]
        )
        w.writerow(
            [
                "sbc",
                "2023",
                "2023-12-31",
                "",
                "",
                "",
                "",
                "",
                dc.HIDDEN_ROW,
                "x",
                "structural_not_presented",
            ]
        )
        w.writerow(
            [
                "total_debt",
                "2023",
                "2023-12-31",
                "120",
                ACC,
                "R4",
                "",
                f"LongTermDebtNoncurrent=100@{ACC}#R4;CommercialPaper=20@{ACC}#R4",
                dc.SHOWN,
                "",
                "",
            ]
        )
    facts = [
        fact("Revenues", "100"),
        fact("LongTermDebtNoncurrent", "100", qtrs=0),
        fact("CommercialPaper", "20", qtrs=0),
    ]
    run = dc.certify("T", "1", p, Src(facts))
    req = dc.Request(
        "T", 7, "x/T.csv", run.coverage_sha256, "cell_proof_v21", "res.csv", "abc123"
    )
    cert = json.loads(
        json.dumps(dc.certificate(run, req, "2026-11-21", "Ritwik (cloud)"))
    )
    _check_schema(cert, json.loads(dc.CERTIFICATE_SCHEMA_PATH.read_text()))
    assert (
        cert["verdict"] == "PASS"
        and cert["sample_hash"] == run.coverage_sha256
        and cert["company_id"] == 7
    )
    ev = {
        c["data_point"]: (c["evidence"], c["result"], c["grain"]) for c in cert["cells"]
    }
    assert ev == {
        "revenue": ("drawn", "MATCH", "FY"),
        "sbc": ("census", "MATCH", "FY"),
        "total_debt": ("census", "MATCH", "I"),
    }
    assert cert["detector_version"] == "cell_proof_v21" and cert["bound"] == {
        "n": 1,
        "errors": 0,
        "upper_95": "0.950000",
    }


def test_certificate_marks_undrawn_shown_cells_sampled_and_failed_hides_mismatch(
    tmp_path,
):
    cells = [cell(dp=f"d{i}") for i in range(40)]
    run = dc.Run("T", "c", "0" * 64, "s", {}, cells=cells)
    run.shown = [dc.CellCheck(cells[0], "MATCH", D(100), "ok")]
    hid = dc.Cell(
        "sga_expense",
        "2016",
        "2016-12-31",
        dc.HIDDEN_ROW,
        None,
        "",
        "",
        "",
        (),
        "era_unmapped",
        None,
    )
    run.cells.append(hid)
    run.hides = [dc.Finding("hide_reason", "sga_expense", "2016", "FAIL", "bad class")]
    cert = dc.certificate(run, None, "2026-11-21", "a")
    by = {(c["data_point"], c["fiscal_year"]): c for c in cert["cells"]}
    assert by[("d0", "2023")]["evidence"] == "drawn"
    assert (
        by[("d1", "2023")]["evidence"] == "sampled"
        and by[("d1", "2023")]["result"] == "SAMPLED"
    )
    assert by[("sga_expense", "2016")]["result"] == "MISMATCH"


def test_only_after_tax_hidden_year_is_a_doc02_class_judged_by_the_printed_line_test():
    """Ruling 2026-11-21 (Dhairya): sbc disclosed only after tax is never served as sbc. The class is valid and, like
    only-combined, a presented year passes when the pure line is not printed. Mutation: drop it from LINE_NOT_PURE."""
    shown = cell(dp="sbc", tag="ShareBasedCompensation", pe="2024-12-31")
    hid = dc.Cell(
        "sbc",
        "2019",
        "2019-12-31",
        dc.HIDDEN_YEAR,
        None,
        "",
        "",
        "",
        (),
        hide_class="only_after_tax_disclosed",
    )
    assert dc.check_hide_reasons([hid]) == []
    ye = {"A": ["2019-12-31|4"]}
    assert [f.severity for f in dc.check_hidden_years([shown, hid], ye, {})] == ["INFO"]
    printed = dc.check_hidden_years([shown, hid], ye, {"A": {"ShareBasedCompensation"}})
    assert [f.severity for f in printed] == ["FAIL"]


def test_verified_absent_is_a_year_class_and_json_writes_null_not_empty():
    row = dc.Cell(
        "operating_income",
        "2022",
        "2022-12-31",
        dc.HIDDEN_ROW,
        None,
        "",
        "",
        "",
        (),
        "x",
        "verified_absent",
    )
    year = dc.Cell(
        "operating_income",
        "2022",
        "2022-12-31",
        dc.HIDDEN_YEAR,
        None,
        "",
        "",
        "",
        (),
        "x",
        "verified_absent",
    )
    assert [f.severity for f in dc.check_hide_reasons([row])] == ["FAIL"]
    assert dc.check_hide_reasons([year]) == []
    shown = dc.Cell(
        "revenue",
        "2023",
        "2023-12-31",
        dc.SHOWN,
        D(1),
        ACC,
        "R4",
        "Revenues",
        (),
        "",
        "",
    )
    run = dc.Run("T", "c", "0" * 64, "s", {}, cells=[shown])
    c = dc.certificate(run, None, "d", "a")["cells"][0]
    assert c["hide_class"] is None and c["reason_code"] is None


def test_cf_inventory_change_hide_has_a_tag_family():
    cells = [cell(dp="cf_inventory_change", display=dc.HIDDEN_ROW)]
    assert dc.check_hidden_rows(cells, [])[0].severity == "INFO"
    assert (
        dc.check_hidden_rows(cells, [fact("IncreaseDecreaseInInventories", "5")])[
            0
        ].severity
        == "FAIL"
    )


def test_derived_total_liabilities_excludes_temporary_equity():
    # GILD FY2015 per the FY2016 10-K R2: 9,890 + 21,073 + 1,243 + 395 = 32,601 liabilities;
    # 51,716 assets - 19,113 total equity = 32,603 includes 2 of temporary equity.
    facts = [
        fact("Assets", "51716", qtrs=0),
        fact(
            "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
            "19113",
            qtrs=0,
        ),
        fact("TemporaryEquityCarryingAmountAttributableToParent", "2", qtrs=0),
    ]
    c = cell(dp="total_liabilities", value="32601", tag="")
    assert dc.check_derived(c, [c], facts).result == "MATCH"
    assert (
        dc.check_derived(
            cell(dp="total_liabilities", value="32603", tag=""), [c], facts
        ).result
        == "MISMATCH"
    )


def test_every_derived_cell_is_checked_not_only_drawn_ones(tmp_path):
    rows = [
        [f"d{i}", "2023", "2023-12-31", "100", ACC, "R4", "Revenues", "", dc.SHOWN]
        for i in range(40)
    ]
    rows += [
        ["shares_outstanding", str(y), f"{y}-12-31", "90", ACC, "R2", "", "", dc.SHOWN]
        for y in range(2015, 2025)
    ]
    cov = write_cov(tmp_path, rows)

    def facts(bad_year=None):
        out = [fact("Revenues", "100")]
        for y in range(2015, 2025):
            out.append(
                fact("CommonStockSharesIssued", "100", ddate=f"{y}-12-31", qtrs=0)
            )
            out.append(
                fact(
                    "TreasuryStockCommonShares",
                    "11" if y == bad_year else "10",
                    ddate=f"{y}-12-31",
                    qtrs=0,
                )
            )
        return out

    run = dc.certify("T", "1", cov, Src(facts()), seed="s")
    assert (
        run.derived
        and all(d.result == "MATCH" for d in run.derived)
        and run.verdict == "PASS"
    )
    undrawn = int(
        run.derived[0].cell.fiscal_year
    )  # a derived cell the draw did not pick
    assert dc.certify("T", "1", cov, Src(facts(undrawn)), seed="s").verdict == "FAIL"


def _bcell(dp, badge, value="10", tag="X", parts=(), acc=ACC):
    return dc.Cell(
        dp,
        "2023",
        "2023-12-31",
        dc.SHOWN,
        D(value),
        acc,
        "R4",
        tag,
        tuple(parts),
        "",
        "",
        badge,
    )


def test_badges_follow_the_real_registry():
    """Founder decision 2026-11-22 (doc 02): registry metrics/registry/data_points.csv."""
    ok = [
        _bcell("shares_outstanding", "derived:shares_issued-treasury_shares", tag=""),
        _bcell("inventory", "combined:inventories and supplies"),
        _bcell("revenue", "as_printed"),
    ]
    assert dc.check_badges(ok) == []
    bad = [
        _bcell(
            "diluted_eps", "derived:net_income/weighted_diluted_shares", tag=""
        ),  # never derived
        _bcell(
            "inventory", "derived:raw+wip+finished", tag=""
        ),  # not an inventory fallback step
        _bcell("revenue", ""),  # shown with no badge
        dc.Cell(
            "current_assets",
            "2023",
            "2023-12-31",
            dc.SHOWN,
            D(1),
            ACC,
            "R2",
            "AssetsCurrent",
            (),
            "",
            "",
            "as_printed",
            "bank",
        ),
    ]
    out = dc.check_badges(bad)
    assert [f.data_point for f in out] == [
        "diluted_eps",
        "inventory",
        "revenue",
        "current_assets",
    ]
    assert "never derived" in out[0].detail and "not applicable" in out[3].detail


def test_derived_badge_must_use_one_filing():
    parts = dc.parse_parts(f"A=10@{ACC}#R4;-B=3@0000000002-24-000002#R4")
    c = _bcell("ppe_net", "derived:ppe_gross-accumulated_depreciation", "7", "", parts)
    assert [f.severity for f in dc.check_badges([c])] == ["FAIL"]


def test_export_without_badge_column_skips_badge_checks():
    assert dc.check_badges([cell()]) == []


def test_every_combined_cell_is_value_checked_not_only_drawn_ones(tmp_path):
    years = range(2015, 2025)
    p = tmp_path / "cov.csv"
    with open(p, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow([*HDR, "badge"])
        for dp in ("revenue", "cfo", "net_income", "income_tax_expense"):
            for y in years:
                w.writerow(
                    [
                        dp,
                        str(y),
                        f"{y}-12-31",
                        "100",
                        ACC,
                        "R4",
                        "Revenues",
                        "",
                        dc.SHOWN,
                        "as_printed",
                    ]
                )
        for y in years:
            w.writerow(
                [
                    "inventory",
                    str(y),
                    f"{y}-12-31",
                    "50",
                    ACC,
                    "R2",
                    "InventoryAndSupplies",
                    "",
                    dc.SHOWN,
                    "combined:inventories and supplies",
                ]
            )

    def facts(bad=None):
        return [fact("Revenues", "100", ddate=f"{y}-12-31") for y in years] + [
            fact(
                "InventoryAndSupplies",
                "51" if y == bad else "50",
                ddate=f"{y}-12-31",
                qtrs=0,
                reports=("R2",),
            )
            for y in years
        ]

    run = dc.certify("T", "1", p, Src(facts()), seed="s")
    assert run.derived and run.verdict == "PASS", [f.detail for f in run.gate]
    undrawn = int(run.derived[0].cell.fiscal_year)
    assert dc.certify("T", "1", p, Src(facts(undrawn)), seed="s").verdict == "FAIL"


def test_sql_compares_the_padded_cik_so_the_index_is_used():
    """WMT timed out at 15 s with ltrim(f.cik); fsn.filing.cik is always 10 zero-padded digits."""
    for sql in (dc.COMPANY_FACT_SQL, dc.YEAR_END_SQL, dc.PRESENTED_LINES_SQL):
        assert "ltrim(f.cik" not in sql and "f.cik = lpad(" in sql
    cells = [cell()]
    import tempfile
    from pathlib import Path

    p = Path(tempfile.mkdtemp()) / "c.csv"
    p.write_text(
        "data_point,fiscal_year,period_end,shown_value,accession,r_page,tag,parts,display\nrevenue,2023,2023-12-31,100,%s,R4,Revenues,,SHOWN_VALUE\n"
        % ACC
    )
    sql = dc.bundle_sql("104169", dc.plan("T", p))
    assert "ltrim(f.cik" not in sql and "'0000104169'" in sql and cells
