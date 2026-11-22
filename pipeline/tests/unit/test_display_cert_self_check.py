"""Flow self-check (founder 2026-11-22): the verifier's checks run on every company's flow export and each failure
becomes an OPEN cell with the check's reason, so gate_ready means "would pass the verifier's mechanical checks"."""

from __future__ import annotations

import csv
import importlib.util
from decimal import Decimal as D
from pathlib import Path

from scrooner_pipeline.certification import display_cert as dc

REPO = Path(__file__).resolve().parents[3]
ACC = "0000000001-24-000001"
COLS = [
    "rank",
    "ticker",
    "company_id",
    "data_point",
    "fiscal_year",
    "period_end",
    "class",
    "reason_code",
    "reason",
    "shown_value",
    "accession",
    "r_page",
    "tag",
    "parts",
    "display",
    "hide_class",
]
SUMMARY = [
    "rank",
    "ticker",
    "company_id",
    "shown_cells",
    "shown_values",
    "open_shown",
    "hidden_rows",
    "hidden_years",
    "pct_shown_values",
    "gate_ready",
    "verifier_certified",
    "note",
]
OPEN_COLS = [
    "work",
    "rank",
    "ticker",
    "company_id",
    "data_point",
    "fiscal_year",
    "reason",
]


def _spec():
    s = importlib.util.spec_from_file_location(
        "certify_display", REPO / "pipeline" / "scripts" / "certify_display.py"
    )
    m = importlib.util.module_from_spec(s)
    assert s.loader
    s.loader.exec_module(m)
    return m


class Src:
    def __init__(self, revenue="100", broken=False):
        self.revenue, self.broken = revenue, broken

    def facts(self, accessions, tags):
        if self.broken:
            raise RuntimeError("statement timeout")
        return [dc.Fact(ACC, "Revenues", "2023-12-31", 4, "", D(self.revenue), ("R4",))]

    def company_facts(self, cik, tags):
        return [dc.Fact(ACC, "Assets", "2023-12-31", 0, "", D(1), ("R2",))]

    def periodic_year_ends(self, cik):
        return {ACC: ["2023-12-31|4", "2023-12-31|0"]}

    def presented_lines(self, cik, tags):
        return {ACC: {"Assets"}}


def _row(cid, tk, dp, display, hide_class="", value="", tag="", acc="", r=""):
    return dict(
        rank="1",
        ticker=tk,
        company_id=cid,
        data_point=dp,
        fiscal_year="2023",
        period_end="2023-12-31",
        **{"class": "PROVEN" if display == dc.SHOWN else "REASON"},
        reason_code="",
        reason="",
        shown_value=value,
        accession=acc,
        r_page=r,
        tag=tag,
        parts="",
        display=display,
        hide_class=hide_class,
    )


def _write(path, cols, rows):
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)


def _read(path):
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def _dir(tmp_path, hide_class="verified_absent"):
    rows = [
        _row(
            "7",
            "T",
            "revenue",
            dc.SHOWN,
            value="100",
            tag="Revenues",
            acc=ACC,
            r="R4.htm",
        ),
        # verified_absent on a whole hidden row is not a doc 02 class fit: the verifier fails it
        _row("7", "T", "inventory", dc.HIDDEN_ROW, hide_class=hide_class),
        _row("8", "U", "inventory", dc.HIDDEN_ROW, hide_class="verified_absent"),
    ]
    _write(tmp_path / "top100-coverage.csv", COLS, rows)
    summ = [
        {
            "rank": "1",
            "ticker": "T",
            "company_id": "7",
            "shown_cells": "1",
            "shown_values": "1",
            "open_shown": "0",
            "hidden_rows": "1",
            "hidden_years": "0",
            "pct_shown_values": "100.0",
            "gate_ready": "yes",
            "verifier_certified": "no",
            "note": "",
        },
        {
            "rank": "2",
            "ticker": "U",
            "company_id": "8",
            "shown_cells": "0",
            "shown_values": "0",
            "open_shown": "0",
            "hidden_rows": "1",
            "hidden_years": "0",
            "pct_shown_values": "",
            "gate_ready": "yes",
            "verifier_certified": "no",
            "note": "",
        },
    ]
    _write(tmp_path / "top100-coverage-summary.csv", SUMMARY, summ)
    _write(tmp_path / "top100-open-shown-cells-20261122T0000Z.csv", OPEN_COLS, [])
    return tmp_path


def test_a_verifier_failure_opens_the_cell_and_clears_gate_ready(tmp_path):
    d = _dir(tmp_path)
    assert _spec().self_check(d, "7", "1", source=Src()) == 0
    cov = {
        (r["company_id"], r["data_point"]): r for r in _read(d / "top100-coverage.csv")
    }
    inv = cov[("7", "inventory")]
    assert inv["display"] == dc.OPEN and inv["hide_class"] == ""
    assert inv["reason"].startswith(
        "verifier self-check hide_reason: verified_absent applies to a year"
    )
    assert cov[("7", "revenue")]["display"] == dc.SHOWN  # a matching cell stays shown
    assert (
        cov[("8", "inventory")]["display"] == dc.HIDDEN_ROW
    )  # another company's rows are untouched
    s = {r["company_id"]: r for r in _read(d / "top100-coverage-summary.csv")}
    assert (
        s["7"]["gate_ready"] == "no"
        and s["7"]["open_shown"] == "1"
        and s["7"]["shown_cells"] == "2"
    )
    assert (
        s["7"]["hidden_rows"] == "0"
        and "verifier self-check: 1 opened" in s["7"]["note"]
    )
    assert s["8"]["gate_ready"] == "yes"
    (o,) = _read(d / "top100-open-shown-cells-20261122T0000Z.csv")
    assert (
        o["work"] == dc.SELF_CHECK_WORK
        and o["ticker"] == "T"
        and o["data_point"] == "inventory"
    )
    (f,) = _read(d / "verifier-self-check-7.csv")
    assert f["check"] == "hide_reason" and f["severity"] == "FAIL"


def test_a_clean_company_keeps_gate_ready(tmp_path):
    d = _dir(tmp_path, hide_class="structural_not_presented")
    assert _spec().self_check(d, "7", "1", source=Src()) == 0
    s = {r["company_id"]: r for r in _read(d / "top100-coverage-summary.csv")}
    assert s["7"]["gate_ready"] == "yes" and s["7"]["open_shown"] == "0"


def test_a_value_mismatch_opens_the_shown_cell(tmp_path):
    d = _dir(tmp_path, hide_class="structural_not_presented")
    assert _spec().self_check(d, "7", "1", source=Src(revenue="99")) == 0
    cov = {
        (r["company_id"], r["data_point"]): r for r in _read(d / "top100-coverage.csv")
    }
    assert cov[("7", "revenue")]["display"] == dc.OPEN
    assert cov[("7", "revenue")]["reason"].startswith(
        "verifier self-check shown: filing differs"
    )


def test_checks_that_cannot_run_are_never_a_pass(tmp_path):
    d = _dir(tmp_path, hide_class="structural_not_presented")
    assert _spec().self_check(d, "7", "1", source=Src(broken=True)) == 3
    s = {r["company_id"]: r for r in _read(d / "top100-coverage-summary.csv")}
    assert s["7"]["gate_ready"] == "no" and "error RuntimeError" in s["7"]["note"]


def test_open_cells_are_not_reopened_and_hidden_row_findings_open_every_year():
    rows = [
        {
            "data_point": "sbc",
            "fiscal_year": y,
            "display": dc.HIDDEN_ROW,
            "hide_class": "structural_not_presented",
            "reason": "",
        }
        for y in ("2022", "2023")
    ] + [
        {
            "data_point": "revenue",
            "fiscal_year": "2023",
            "display": dc.OPEN,
            "hide_class": "",
            "reason": "proof",
        }
    ]
    fs = [
        dc.Finding("hidden_row", "sbc", "*", "FAIL", "reported: 2 facts"),
        dc.Finding("gate", "revenue", "2023", "FAIL", "shown cell has no value"),
        dc.Finding("gate", "*", "*", "FAIL", "source broken"),
    ]
    opened, company = dc.apply_self_check(rows, fs)
    assert sorted(r["fiscal_year"] for r in opened) == ["2022", "2023"]
    assert rows[2]["reason"] == "proof" and [f.detail for f in company] == [
        "source broken"
    ]


def test_findings_exclude_open_cells_and_review_items():
    run = dc.Run("T", "c", "0" * 64, "s", {})
    run.gate = [
        dc.Finding("gate", "a", "2023", "FAIL", "OPEN cell"),
        dc.Finding(
            "gate", "b", "2023", "FAIL", "shown cell has no accession or R page"
        ),
    ]
    run.hides = [dc.Finding("hidden_row", "c", "*", "REVIEW", "no tag family")]
    assert [f.data_point for f in dc.self_check_findings(run)] == ["b"]


def test_flow_runs_the_self_check_before_the_flow_line():
    flow = (REPO / "scripts" / "top100_flow.sh").read_text()
    assert "certify_display.py --self-check-dir $CV" in flow
    assert flow.index("--self-check-dir") > flow.index("CV=$O/coverage;")
    assert flow.index("--self-check-dir") < flow.index("GATE_READY")


class _Printed(Src):
    """A presenting filing that prints the interest-income line; records which tags the lines query asked for."""

    def __init__(self, printed: set[str]):
        super().__init__()
        self.printed, self.asked = printed, set()

    def presented_lines(self, cik, tags):
        self.asked |= set(tags)
        return {ACC: {"Assets"} | (self.printed & set(tags))}


def _va_dir(tmp_path, evidence):
    cols = COLS + ["evidence"]
    rows = [
        dict(_row("7", "T", "revenue", dc.SHOWN, value="100", tag="Revenues", acc=ACC, r="R4.htm"), evidence=""),
        dict(_row("7", "T", "interest_income", dc.HIDDEN_YEAR, hide_class="verified_absent"), evidence=evidence),
    ]
    _write(tmp_path / "top100-coverage.csv", cols, rows)
    _write(tmp_path / "top100-coverage-summary.csv", SUMMARY, [dict(
        rank="1", ticker="T", company_id="7", shown_cells="1", shown_values="1", open_shown="0", hidden_rows="0",
        hidden_years="1", pct_shown_values="100.0", gate_ready="yes", verifier_certified="no", note="")])
    _write(tmp_path / "top100-open-shown-cells-20261122T0000Z.csv", OPEN_COLS, [])
    return tmp_path


SEARCH = 'EDGAR full-text search forms=10-K,10-Q q="interest income" (FY2023): 0 hits'


def test_self_check_keeps_a_search_evidenced_verified_absent_year_and_tests_its_line(tmp_path):
    """Ruling 2026-11-22: the year stays hidden, and certify() still asks the filings for the row's line (mutation:
    leave it out of the presented-lines allow set -> the printed case below would wrongly pass)."""
    d = _va_dir(tmp_path, SEARCH)
    src = _Printed(set())
    assert _spec().self_check(d, "7", "1", source=src) == 0
    cov = {r["data_point"]: r for r in _read(d / "top100-coverage.csv")}
    assert cov["interest_income"]["display"] == dc.HIDDEN_YEAR
    assert "InvestmentIncomeInterest" in src.asked


def test_self_check_opens_a_search_evidenced_year_whose_line_is_printed(tmp_path):
    d = _va_dir(tmp_path, SEARCH)
    assert _spec().self_check(d, "7", "1", source=_Printed({"InvestmentIncomeInterest"})) == 0
    cov = {r["data_point"]: r for r in _read(d / "top100-coverage.csv")}
    assert cov["interest_income"]["display"] == dc.OPEN
    assert "prints the line" in cov["interest_income"]["reason"]


def test_self_check_opens_an_unevidenced_verified_absent_year(tmp_path):
    d = _va_dir(tmp_path, "absent in own filing")
    assert _spec().self_check(d, "7", "1", source=_Printed(set())) == 0
    cov = {r["data_point"]: r for r in _read(d / "top100-coverage.csv")}
    assert cov["interest_income"]["display"] == dc.OPEN
