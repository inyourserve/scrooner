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
    cells = [cell(display=dc.HIDDEN_YEAR, pe="2019-12-31")]
    assert (
        dc.check_hidden_years(cells, {ACC: ["2019-12-31", "2020-12-31"]})[0].severity
        == "FAIL"
    )
    assert dc.check_hidden_years(cells, {ACC: ["2020-12-31"]}) == []


# ---------------------------------------------------------------- bound and run
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
        "facts": [[ACC, "Revenues", "2023-12-31", 4, "", "100", ["R4"]]],
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
