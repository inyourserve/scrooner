"""Automated draw checker (certification/draw_check.py, founder 2026-11-22): each drawn cell against the cited
filing's own XBRL facts; only NEEDS_READ and AUTO_MISMATCH cells go to a person or agent read."""

from __future__ import annotations

import csv
import dataclasses
import importlib.util
import json
from decimal import Decimal as D
from pathlib import Path

import pytest
from scrooner_pipeline.certification import display_cert as dc
from scrooner_pipeline.certification import draw_check as dck
from test_display_cert import _check_schema

REPO = Path(__file__).resolve().parents[3]
ACC = "0000000001-24-000001"
PE = "2023-12-31"


def ff(tag, value, ddate=PE, qtrs=4, dims="", acc=ACC, dcml=-6):
    return dck.FilingFact(acc, tag, ddate, qtrs, dims, D(value), dcml)


def ln(tag, label, acc=ACC, stmt="BS"):
    return dck.FilingLine(acc, tag, 2, stmt, label)


def isl(tag, label, line, acc=ACC, negating=False):
    """A printed income-statement line at a position (fsn.line.line)."""
    return dck.FilingLine(acc, tag, 4, "IS", label, line, negating)


def cell(
    dp="revenue", value="100", tag="Revenues", parts=(), badge=None, acc=ACC, pe=PE
):
    return dc.Cell(
        dp, "2023", pe, dc.SHOWN, D(value), acc, "R4", tag, tuple(parts), badge=badge
    )


def part(tag, value, sign=1, acc=ACC, dims=""):
    return dc.Part(tag, dims, D(value), acc, "R4", sign)


def _rows(path):
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def chk(c, facts, lines=()):
    return dck.check_cell(c, dck.Filing(list(facts), list(lines)))


# ---------------------------------------------------------------- as printed: the checker's own families
def test_as_printed_matches_the_family_fact_and_ignores_the_exports_tag():
    # The export cites a custom tag; the checker finds revenue through its own family, not the cited tag.
    a = chk(cell(tag="abc_CustomRevenue"), [ff("Revenues", "100")])
    assert (a.outcome, a.method, a.filing_value) == (dck.AUTO_MATCH, "family", D(100))
    # A resolver that picked the wrong element is caught: the cited tag holds the shown value, the family fact differs.
    b = chk(
        cell(dp="net_income", value="120", tag="ProfitLoss"),
        [ff("NetIncomeLoss", "100"), ff("ProfitLoss", "120")],
    )
    assert b.outcome == dck.AUTO_MISMATCH and "NetIncomeLoss=100" in b.detail


def test_only_the_first_tier_the_filing_tags_decides():
    assert (
        chk(cell(dp="net_income", tag="ProfitLoss"), [ff("ProfitLoss", "100")]).outcome
        == dck.AUTO_MATCH
    )
    assert (
        chk(
            cell(dp="net_income"), [ff("NetIncomeLoss", "90"), ff("ProfitLoss", "100")]
        ).outcome
        == dck.AUTO_MISMATCH
    )


def test_period_duration_and_dimensions_must_match():
    # 52/53-week year: an end within 7 days is the same period
    assert (
        chk(cell(), [ff("Revenues", "100", ddate="2023-12-29")]).outcome
        == dck.AUTO_MATCH
    )
    assert (
        chk(cell(), [ff("Revenues", "100", ddate="2022-12-31")]).outcome
        == dck.NEEDS_READ
    )
    assert chk(cell(), [ff("Revenues", "100", qtrs=1)]).outcome == dck.NEEDS_READ
    assert (
        chk(cell(), [ff("Revenues", "100", dims="Segment=A")]).outcome == dck.NEEDS_READ
    )
    assert chk(cell(), [ff("Revenues", "100", acc="other")]).outcome == dck.NEEDS_READ
    # a balance is an instant
    assert (
        chk(
            cell(dp="goodwill", tag="Goodwill"), [ff("Goodwill", "100", qtrs=0)]
        ).outcome
        == dck.AUTO_MATCH
    )
    assert (
        chk(
            cell(dp="goodwill", tag="Goodwill"), [ff("Goodwill", "100", qtrs=4)]
        ).outcome
        == dck.NEEDS_READ
    )


def test_the_finest_decimals_fact_is_the_printed_figure():
    # WMT FY2023 ShortTermBorrowings-style duplicate: 372 at dcml -6 (face), 400 at dcml -8 (note)
    facts = [ff("Revenues", "372", dcml=-6), ff("Revenues", "400", dcml=-8)]
    assert chk(cell(value="372"), facts).outcome == dck.AUTO_MATCH
    r = chk(cell(value="400"), facts)
    assert r.outcome == dck.AUTO_MISMATCH and "rounded duplicate" in r.detail


def test_text_stated_cell_needs_a_read():
    a = chk(cell(tag=""), [ff("Revenues", "100")])
    assert (a.outcome, a.method) == (dck.NEEDS_READ, "text")


def test_per_share_plausibility():
    a = chk(
        cell(dp="dividends_per_share", value="2770000", tag="X"),
        [ff("CommonStockDividendsPerShareDeclared", "2770000")],
    )
    assert (a.outcome, a.method) == (dck.AUTO_MISMATCH, "per_share")
    assert (
        chk(
            cell(dp="basic_eps", value="2.5", tag="X"),
            [ff("EarningsPerShareBasic", "2.5")],
        ).outcome
        == dck.AUTO_MATCH
    )


def test_sign_per_polarity():
    # capex is fixed positive (polarity ruling): the payment shown as a magnitude matches a negative-tagged fact
    capex = [ff("PaymentsToAcquirePropertyPlantAndEquipment", "-50")]
    assert chk(cell(dp="capex", value="50", tag="X"), capex).outcome == dck.AUTO_MATCH
    neg = chk(cell(dp="capex", value="-50", tag="X"), capex)
    assert (neg.outcome, neg.method) == (dck.AUTO_MISMATCH, "sign")
    # a signed data point shows the filing's own sign
    flipped = chk(cell(dp="net_income", value="-100"), [ff("NetIncomeLoss", "100")])
    assert flipped.outcome == dck.AUTO_MISMATCH and flipped.detail.startswith("sign")


# ---------------------------------------------------------------- combined, derived
def test_combined_equals_the_printed_combined_line_found_by_its_label():
    b = "combined:accounts payable and accrued liabilities"
    lines = [ln("abc_ApAndAccrued", "Accounts payable and accrued liabilities")]
    facts = [
        ff("abc_ApAndAccrued", "70", qtrs=0),
        ff("AccountsPayableCurrent", "50", qtrs=0),
    ]
    ok = chk(
        cell(dp="accounts_payable", value="70", tag="whatever", badge=b), facts, lines
    )
    assert (ok.outcome, ok.method) == (dck.AUTO_MATCH, "label")
    bad = chk(
        cell(dp="accounts_payable", value="50", tag="whatever", badge=b), facts, lines
    )
    assert bad.outcome == dck.AUTO_MISMATCH
    assert (
        chk(cell(dp="accounts_payable", value="70", badge=b), facts, []).outcome
        == dck.NEEDS_READ
    )


def test_derived_parts_are_re_read_from_the_filing_and_summed():
    b = "derived:selling_and_marketing+general_and_administrative"
    facts = [
        ff("GeneralAndAdministrativeExpense", "30"),
        ff("SellingAndMarketingExpense", "20"),
    ]
    ps = [
        part("GeneralAndAdministrativeExpense", "30"),
        part("SellingAndMarketingExpense", "20"),
    ]
    assert (
        chk(
            cell(dp="sga_expense", value="50", tag="", parts=ps, badge=b), facts
        ).outcome
        == dck.AUTO_MATCH
    )
    # the sum differs
    assert (
        chk(
            cell(dp="sga_expense", value="55", tag="", parts=ps, badge=b), facts
        ).outcome
        == dck.AUTO_MISMATCH
    )
    # a claimed part the filing tags differently
    wrong = [
        part("GeneralAndAdministrativeExpense", "35"),
        part("SellingAndMarketingExpense", "15"),
    ]
    r = chk(cell(dp="sga_expense", value="50", tag="", parts=wrong, badge=b), facts)
    assert r.outcome == dck.AUTO_MISMATCH and "claimed 35" in r.detail
    # a part with no fact
    gone = [part("GeneralAndAdministrativeExpense", "30"), part("MissingExpense", "20")]
    assert (
        chk(
            cell(dp="sga_expense", value="50", tag="", parts=gone, badge=b), facts
        ).outcome
        == dck.NEEDS_READ
    )
    # the registry formula adds: a subtracted part is the wrong shape
    minus = [
        part("GeneralAndAdministrativeExpense", "30"),
        part("SellingAndMarketingExpense", "-20", sign=-1),
    ]
    facts2 = [
        ff("GeneralAndAdministrativeExpense", "30"),
        ff("SellingAndMarketingExpense", "-20"),
    ]
    s = chk(cell(dp="sga_expense", value="50", tag="", parts=minus, badge=b), facts2)
    assert s.outcome == dck.AUTO_MISMATCH and "subtracts nothing" in s.detail


def test_a_derivation_uses_one_filing():
    b = "derived:sum(printed capex lines)"
    ps = [
        part("PaymentsToAcquirePropertyPlantAndEquipment", "5"),
        part("PaymentsToAcquireSoftware", "5", acc="other"),
    ]
    facts = [
        ff("PaymentsToAcquirePropertyPlantAndEquipment", "5"),
        ff("PaymentsToAcquireSoftware", "5", acc="other"),
    ]
    r = chk(cell(dp="capex", value="10", tag="", parts=ps, badge=b), facts)
    assert r.outcome == dck.AUTO_MISMATCH and "more than one filing" in r.detail


def test_derived_identity_without_parts_reads_the_filing_not_the_shown_cells():
    b = "derived:liabilities_and_equity-total_equity-temporary_equity"
    facts = [
        ff("Assets", "51716", qtrs=0),
        ff(
            "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
            "19113",
            qtrs=0,
        ),
        ff("TemporaryEquityCarryingAmountAttributableToParent", "2", qtrs=0),
    ]
    assert (
        chk(cell(dp="total_liabilities", value="32601", tag="", badge=b), facts).outcome
        == dck.AUTO_MATCH
    )
    assert (
        chk(cell(dp="total_liabilities", value="32603", tag="", badge=b), facts).outcome
        == dck.AUTO_MISMATCH
    )
    assert (
        chk(cell(dp="total_liabilities", value="1", tag="", badge=b), facts[:1]).outcome
        == dck.NEEDS_READ
    )


# ---------------------------------------------------------------- independence
def test_checker_never_reads_resolver_output_or_canonical_fact():
    src = (
        REPO / "pipeline/src/scrooner_pipeline/certification/draw_check.py"
    ).read_text()
    code = src.split('"""', 2)[
        2
    ]  # skip the module docstring, which names what it never reads
    for banned in (
        "canonical_fact",
        "line_map",
        "standard_extract",
        "company_tag_map",
        "structural_loader",
        "cell_proof",
    ):
        assert banned not in code, banned
    # its own SQL reads every fact of the filing at the drawn periods, not only the cited tags
    assert (
        "t.tag = any" not in dck.FILING_FACT_SQL and "fsn.value" in dck.FILING_FACT_SQL
    )


# ---------------------------------------------------------------- certify integration, reads, certificate
class Src:
    def __init__(self, ffacts, lines=(), shown_facts=None):
        self.ff, self.lines = list(ffacts), list(lines)
        self.shown = shown_facts

    def facts(self, accessions, tags):
        return (
            self.shown
            if self.shown is not None
            else [
                dc.Fact(
                    f.accession,
                    f.tag,
                    f.ddate,
                    f.qtrs,
                    f.dims,
                    f.value,
                    ("R4",),
                    f.dcml,
                )
                for f in self.ff
            ]
        )

    def company_facts(self, cik, tags):
        return [dc.Fact(ACC, "Assets", PE, 0, "", D(1), ("R2",))]

    def periodic_year_ends(self, cik):
        return {ACC: [PE]}

    def presented_lines(self, cik, tags):
        return {ACC: {"Assets"}}

    def filing_facts(self, accessions, period_ends):
        return self.ff, self.lines


def _cov(tmp_path, rows):
    p = tmp_path / "cov.csv"
    with open(p, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(
            [
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
        )
        w.writerows(rows)
    return p


def _two(tmp_path):
    return _cov(
        tmp_path,
        [
            ["revenue", "2023", PE, "100", ACC, "R4", "Revenues", "", dc.SHOWN],
            [
                "research_and_development",
                "2023",
                PE,
                "7",
                ACC,
                "R4",
                "abc_RandD",
                "",
                dc.SHOWN,
            ],
        ],
    )


def test_certify_sends_only_unsettled_cells_to_a_read_and_the_certificate_says_who_verified(
    tmp_path,
):
    cov = _two(tmp_path)
    # revenue AUTO_MATCH; R&D tagged with a custom element the checker has no family for -> NEEDS_READ
    facts = [ff("Revenues", "100"), ff("abc_RandD", "7")]
    run = dc.certify("T", "1", cov, Src(facts))
    assert dck.counts(run.auto) == {
        dck.AUTO_MATCH: 1,
        dck.AUTO_MISMATCH: 0,
        dck.NEEDS_READ: 1,
    }
    assert run.verdict == "REVIEW" and [a.data_point for a in run.pending_reads] == [
        "research_and_development"
    ]
    reads = tmp_path / "reads.csv"
    reads.write_text(
        "data_point,fiscal_year,verdict,reader,evidence\nresearch_and_development,2023,MATCH,agent-7,R4 line 9 prints 7\n"
    )
    done = dc.certify("T", "1", cov, Src(facts), reads=dck.load_reads(reads))
    assert done.verdict == "PASS" and not done.pending_reads
    cert = json.loads(
        json.dumps(dc.certificate(done, None, "2026-11-22", "Ritwik (cloud)"))
    )
    _check_schema(cert, json.loads(dc.CERTIFICATE_SCHEMA_PATH.read_text()))
    by = {c["data_point"]: c["verified_by"] for c in cert["cells"]}
    assert by == {"revenue": "machine", "research_and_development": "read:agent-7"}
    blk = cert["draw_check"]
    assert (blk["auto_matched"], blk["auto_mismatched"], blk["needs_read"]) == (1, 0, 1)
    assert (
        blk["verified_by_machine"],
        blk["verified_by_read"],
        blk["pending_read"],
    ) == (1, 1, 0)
    assert blk["read_cells"][0]["reader"] == "agent-7"
    assert "Automated draw checker" in dc.render(done, "2026-11-22")


def test_a_read_that_finds_the_cell_wrong_fails_the_company_and_counts_as_an_error(
    tmp_path,
):
    cov = _two(tmp_path)
    reads = tmp_path / "reads.csv"
    reads.write_text(
        "data_point,fiscal_year,verdict,reader,evidence\nresearch_and_development,2023,MISMATCH,agent-7,R4 prints 8\n"
    )
    run = dc.certify(
        "T",
        "1",
        cov,
        Src([ff("Revenues", "100"), ff("abc_RandD", "7")]),
        reads=dck.load_reads(reads),
    )
    assert run.verdict == "FAIL" and run.errors == 1


def test_auto_mismatch_is_pending_until_read(tmp_path):
    cov = _two(tmp_path)
    # the certifier's claim check matches the cited custom tag, but the checker's family says otherwise
    facts = [
        ff("Revenues", "100"),
        ff("abc_RandD", "7"),
        ff("ResearchAndDevelopmentExpense", "9"),
    ]
    run = dc.certify("T", "1", cov, Src(facts))
    (bad,) = [a for a in run.auto if a.outcome == dck.AUTO_MISMATCH]
    assert bad.data_point == "research_and_development" and run.verdict == "REVIEW"
    assert dck.read_queue(run.auto)[0].outcome == dck.AUTO_MISMATCH


def test_reads_need_a_reader_and_evidence(tmp_path):
    p = tmp_path / "r.csv"
    p.write_text(
        "data_point,fiscal_year,verdict,reader,evidence\nrevenue,2023,MATCH,,seen\n"
    )
    with pytest.raises(ValueError):
        dck.load_reads(p)


def test_draw_checker_positive_control(tmp_path):
    run = dc.certify(
        "T",
        "1",
        _two(tmp_path),
        Src([], shown_facts=[dc.Fact(ACC, "Revenues", PE, 4, "", D(100), ("R4",))]),
    )
    assert run.verdict == "FAIL" and any(
        "draw checker read no facts" in f.detail for f in run.gate
    )


def test_source_without_a_filing_read_leaves_the_checker_off(tmp_path):
    class Old(Src):
        filing_facts = None  # an old evidence bundle

    run = dc.certify(
        "T", "1", _two(tmp_path), Old([ff("Revenues", "100"), ff("abc_RandD", "7")])
    )
    assert run.auto is None and run.verdict == "PASS"
    assert dc.certificate(run, None, "d", "a")["draw_check"] == {
        "checker": dck.CHECKER_VERSION,
        "ran": False,
    }


def test_bundle_source_feeds_the_checker():
    b = {
        "filing_facts": [[ACC, "Revenues", PE, 4, "", "100", -6]],
        "filing_lines": [[ACC, "Revenues", 4, "IS", "Revenue"]],
    }
    facts, lines = dc.BundleFactSource(b).filing_facts([ACC], [PE])
    assert facts == [ff("Revenues", "100")] and lines[0].plabel == "Revenue"
    assert dc.BundleFactSource({}).filing_facts([ACC], [PE]) is None


# ---------------------------------------------------------------- the verifier samples the checker
def test_audit_samples_five_percent_of_auto_matches_and_reports_agreement(tmp_path):
    checks = [
        dck.AutoCheck(f"d{i}", "2023", dck.AUTO_MATCH, "family", D(1), "")
        for i in range(41)
    ] + [dck.AutoCheck("x", "2023", dck.NEEDS_READ, "text", None, "")]
    s = dck.audit_sample(checks, "T-abc")
    assert len(s) == 3 and all(
        a.outcome == dck.AUTO_MATCH for a in s
    )  # ceil(0.05 x 41)
    assert s == dck.audit_sample(checks, "T-abc") and s != dck.audit_sample(
        checks, "T-xyz"
    )
    p = tmp_path / "audit.csv"
    dck.write_audit_request(p, s)
    rows = _rows(p)
    rows[0].update(verdict="MATCH", reader="agent-1", evidence="R2 prints it")
    rows[1].update(verdict="MISMATCH", reader="agent-1", evidence="R2 prints 2")
    with open(p, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=dck.AUDIT_COLUMNS)
        w.writeheader()
        w.writerows(rows[:2])
    ag = dck.audit_agreement(s, dck.load_reads(p))
    assert (
        ag["sampled"],
        ag["read"],
        ag["agree"],
        ag["agreement"],
        ag["complete"],
    ) == (3, 2, 1, "0.5000", False)
    assert dck.audit_sample([], "T") == []


# ---------------------------------------------------------------- flow self-check
def test_self_check_opens_auto_mismatch_cells_with_the_reason(tmp_path):
    cov = _two(tmp_path)
    run = dc.certify(
        "T",
        "1",
        cov,
        Src(
            [
                ff("Revenues", "100"),
                ff("abc_RandD", "7"),
                ff("ResearchAndDevelopmentExpense", "9"),
            ]
        ),
    )
    fs = [f for f in dc.self_check_findings(run) if f.check == "draw_check"]
    assert [(f.data_point, f.severity) for f in fs] == [
        ("research_and_development", "FAIL")
    ]
    rows = [
        {
            "data_point": "research_and_development",
            "fiscal_year": "2023",
            "display": dc.SHOWN,
            "hide_class": "",
            "reason": "",
        },
        {
            "data_point": "revenue",
            "fiscal_year": "2023",
            "display": dc.SHOWN,
            "hide_class": "",
            "reason": "",
        },
    ]
    opened, _ = dc.apply_self_check(rows, fs)
    assert [r["data_point"] for r in opened] == ["research_and_development"]
    assert rows[0]["display"] == dc.OPEN and rows[0]["reason"].startswith(
        "verifier self-check draw_check: AUTO_MISMATCH"
    )
    assert rows[1]["display"] == dc.SHOWN


def _script():
    s = importlib.util.spec_from_file_location(
        "certify_display", REPO / "pipeline" / "scripts" / "certify_display.py"
    )
    m = importlib.util.module_from_spec(s)
    assert s.loader
    s.loader.exec_module(m)
    return m


def test_draw_check_all_reports_counts_and_runtime_per_company(tmp_path):
    cols = [
        "rank",
        "ticker",
        "company_id",
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
    p = tmp_path / "top100-coverage.csv"
    with open(p, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        w.writerow(
            [
                "1",
                "T",
                "7",
                "revenue",
                "2023",
                PE,
                "100",
                ACC,
                "R4",
                "Revenues",
                "",
                dc.SHOWN,
            ]
        )
        w.writerow(
            [
                "1",
                "T",
                "7",
                "net_income",
                "2023",
                PE,
                "5",
                ACC,
                "R4",
                "NetIncomeLoss",
                "",
                dc.SHOWN,
            ]
        )
        w.writerow(
            [
                "2",
                "U",
                "8",
                "revenue",
                "2023",
                PE,
                "100",
                ACC,
                "R4",
                "abc_Rev",
                "",
                dc.SHOWN,
            ]
        )
    src = Src([ff("Revenues", "100"), ff("NetIncomeLoss", "6")])
    assert _script().draw_check_all(p, tmp_path / "out", "2026-11-22", source=src) == 0
    summ = {
        r["ticker"]: r
        for r in _rows(tmp_path / "out" / "draw-check-summary-2026-11-22.csv")
    }
    assert (
        summ["T"]["auto_match"],
        summ["T"]["auto_mismatch"],
        summ["T"]["needs_read"],
    ) == ("1", "1", "0")
    assert summ["U"]["pct_auto_match"] == "100.0" and float(summ["T"]["seconds"]) >= 0
    cells = _rows(tmp_path / "out" / "draw-check-2026-11-22.csv")
    assert {(r["ticker"], r["data_point"], r["outcome"]) for r in cells} == {
        ("T", "revenue", dck.AUTO_MATCH),
        ("T", "net_income", dck.AUTO_MISMATCH),
        ("U", "revenue", dck.AUTO_MATCH),
    }


# ---------------------------------------------------------------- measured on the top-100 draw (2026-11-22)
def test_a_rounded_note_mention_is_not_a_mismatch_but_a_read():
    # MRK FY2025: the CF line prints 2,793; the only family fact is a note's "$2.8 billion" (dcml -8)
    c = cell(
        dp="amortization_of_intangibles",
        value="2793000000",
        tag="AdjustmentForAmortization",
    )
    r = chk(c, [ff("AmortizationOfIntangibleAssets", "2800000000", dcml=-8)])
    assert r.outcome == dck.NEEDS_READ and "rounded" in r.detail
    # reads 2026-11-24: a dcml -8 mention never proves a mismatch, even when the shown value does not round to it
    # (BMY 2020 amortization 9,688 shown, the note's "$9.9 billion"; the face line is right)
    c2 = cell(dp="amortization_of_intangibles", value="9688000000", tag="X")
    assert (
        chk(c2, [ff("AmortizationOfIntangibleAssets", "9900000000", dcml=-8)]).outcome
        == dck.NEEDS_READ
    )
    # a finer fact still proves it
    assert (
        chk(c2, [ff("AmortizationOfIntangibleAssets", "9900000000", dcml=-6)]).outcome
        == dck.AUTO_MISMATCH
    )


def test_a_sum_of_printed_lines_keeps_each_lines_weight():
    # AMZN operating expenses: an income line inside the expense band is subtracted
    b = "derived:sum(printed operating lines)"
    ps = [
        part("GeneralAndAdministrativeExpense", "30"),
        part("OtherOperatingIncomeExpenseNet", "-2", sign=-1),
    ]
    facts = [
        ff("GeneralAndAdministrativeExpense", "30"),
        ff("OtherOperatingIncomeExpenseNet", "-2"),
    ]
    assert (
        chk(
            cell(dp="operating_expenses", value="32", tag="", parts=ps, badge=b), facts
        ).outcome
        == dck.AUTO_MATCH
    )
    # a named a-b formula whose parts only add is the wrong shape (QCOM FY2021 badge vs its R&D+SG&A parts)
    b2 = "derived:total_costs_and_expenses-cost_of_revenue"
    ps2 = [
        part("GeneralAndAdministrativeExpense", "30"),
        part("ResearchAndDevelopmentExpense", "2"),
    ]
    facts2 = [
        ff("GeneralAndAdministrativeExpense", "30"),
        ff("ResearchAndDevelopmentExpense", "2"),
    ]
    r = chk(
        cell(dp="operating_expenses", value="32", tag="", parts=ps2, badge=b2), facts2
    )
    assert r.outcome == dck.AUTO_MISMATCH and "subtracts a term" in r.detail


def test_derived_without_parts_matches_a_printed_line_or_its_own_identity_only():
    b = "derived:liabilities_and_equity-total_equity-temporary_equity"
    facts = [
        ff("Liabilities", "2814", qtrs=0),
        ff("Assets", "7370", qtrs=0),
        ff("StockholdersEquity", "4469", qtrs=0),
    ]
    r = chk(
        cell(dp="total_liabilities", value="2814", tag="Liabilities", badge=b), facts
    )
    assert (r.outcome, r.method) == (dck.AUTO_MATCH, "family")
    # a sum-of-lines badge with no parts is not rebuilt by the other-income identity
    oi = [
        ff(
            "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",
            "100",
        ),
        ff("OperatingIncomeLoss", "90"),
        ff("InterestExpense", "5"),
        ff("InvestmentIncomeInterest", "1"),
    ]
    s = cell(
        dp="other_income_expense_net",
        value="7",
        tag="X",
        badge="derived:sum(printed nonoperating lines)",
    )
    assert chk(s, oi).outcome == dck.NEEDS_READ
    i = cell(
        dp="other_income_expense_net",
        value="14",
        tag="",
        badge="derived:income_before_tax-operating_income+interest_expense-interest_income",
    )
    # the identity is the printed band (definition 2026-11-21 d): it needs the income statement's own lines
    assert chk(i, oi).outcome == dck.NEEDS_READ
    band = [
        isl("OperatingIncomeLoss", "Operating income", 10),
        isl("InterestExpense", "Interest expense", 11),
        isl(
            "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",
            "Income before income taxes",
            13,
        ),
    ]
    assert chk(i, oi, band).outcome == dck.AUTO_MATCH


def test_parent_net_income_is_profit_loss_less_the_printed_nci_share_not_available_to_common():
    # CAT/SCCO shape: ProfitLoss 3,003 with an NCI share of 5 printed on the income statement -> parent 2,998
    facts = [
        ff("NetIncomeLossAvailableToCommonStockholdersBasic", "2998"),
        ff("ProfitLoss", "3003"),
        ff("NetIncomeLossAttributableToNoncontrollingInterest", "5"),
    ]
    nci = [isl("NetIncomeLossAttributableToNoncontrollingInterest", "Less: NCI", 20)]
    assert (
        chk(cell(dp="net_income", value="2998", tag="X"), facts, nci).outcome
        == dck.AUTO_MATCH
    )
    assert (
        chk(cell(dp="net_income", value="3003", tag="X"), facts, nci).outcome
        == dck.AUTO_MISMATCH
    )
    # AVGO FY2020 (0001730168-20-000226 R4): net income 2,960 (ProfitLoss, NCI 0 printed); 2,663 is available to
    # common after preferred dividends, outside the definition
    avgo = [
        ff("ProfitLoss", "2960000000", ddate="2020-11-01"),
        ff(
            "NetIncomeLossAttributableToNoncontrollingInterest", "0", ddate="2020-11-01"
        ),
        ff(
            "NetIncomeLossAvailableToCommonStockholdersBasic",
            "2663000000",
            ddate="2020-11-01",
        ),
    ]
    c = cell(dp="net_income", value="2960000000", tag="ProfitLoss", pe="2020-11-01")
    assert chk(c, avgo, nci).outcome == dck.AUTO_MATCH
    c2 = cell(dp="net_income", value="2663000000", tag="X", pe="2020-11-01")
    assert chk(c2, avgo, nci).outcome == dck.AUTO_MISMATCH
    # MA FY2019: the NCI share (-1) is printed only in the equity statement; ProfitLoss 8,118 is the parent line
    ma = [
        ff("ProfitLoss", "8118000000", ddate="2019-12-31"),
        ff(
            "NetIncomeLossAttributableToNoncontrollingInterest",
            "-1000000",
            ddate="2019-12-31",
        ),
    ]
    eq = [
        ln(
            "NetIncomeLossAttributableToNoncontrollingInterest",
            "Activity related to NCI",
            stmt="EQ",
        )
    ]
    c3 = cell(dp="net_income", value="8118000000", tag="ProfitLoss", pe="2019-12-31")
    assert chk(c3, ma, eq).outcome == dck.AUTO_MATCH
    # TMO tags its "Net Income" line only as available to common: the last tier
    c4 = cell(dp="net_income", value="2938000000", tag="X")
    assert (
        chk(
            c4, [ff("NetIncomeLossAvailableToCommonStockholdersBasic", "2938000000")]
        ).outcome
        == dck.AUTO_MATCH
    )


# ---------------------------------------------------------------- fixes from the 2026-11-24 filing reads
# Each test is built from the real cell that exposed the checker error (reads-2026-11-24/, checker-fixes-2026-11-24.txt).
PRE = "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest"


def cfl(tag, label, acc=ACC):
    return dck.FilingLine(acc, tag, 8, "CF", label, 1)


def test_a_fact_in_another_currency_is_never_the_shown_figure():
    # CB FY2024 (0000896159-25-000004): DPS tagged 3.59 USD and 3.15 CHF on the same element and period
    facts = [
        dck.FilingFact(
            ACC,
            "CommonStockDividendsPerShareDeclared",
            "2024-12-31",
            4,
            "",
            D("3.15"),
            2,
            "CHF",
        ),
        dck.FilingFact(
            ACC,
            "CommonStockDividendsPerShareDeclared",
            "2024-12-31",
            4,
            "",
            D("3.59"),
            2,
            "USD",
        ),
    ]
    c = cell(
        dp="dividends_per_share",
        value="3.59",
        tag="CommonStockDividendsPerShareDeclared",
        pe="2024-12-31",
    )
    assert chk(c, facts).outcome == dck.AUTO_MATCH
    assert (
        chk(
            cell(dp="dividends_per_share", value="3.15", tag="X", pe="2024-12-31"),
            facts,
        ).outcome
        == dck.AUTO_MISMATCH
    )
    assert (
        dck.usd_unit("USD")
        and dck.usd_unit("USD/shares")
        and dck.usd_unit("shares")
        and dck.usd_unit("")
    )
    assert not dck.usd_unit("CHF") and not dck.usd_unit("EUR/shares")
    # the offline bundle carries the unit as its 8th column
    got = dck.bundle_filing_facts(
        {
            "filing_facts": [[ACC, "Revenues", PE, 4, "", "1", -6, "CHF"]],
            "filing_lines": [],
        },
        [ACC],
    )
    assert got[0][0].uom == "CHF"


def test_cash_taxes_compare_as_a_magnitude():
    # UNP FY2021: IncomeTaxesPaidNet tagged -1,658 (payment stored negative), shown 1,658
    c = cell(
        dp="cash_paid_for_income_taxes", value="1658000000", tag="IncomeTaxesPaidNet"
    )
    assert chk(c, [ff("IncomeTaxesPaidNet", "-1658000000")]).outcome == dck.AUTO_MATCH


def test_a_finer_shown_value_matches_a_coarser_fact_at_the_facts_decimals():
    # DHR FY2016: the CF prints 583.1 (dcml -5), the note tags 583 (dcml -6)
    facts = [ff("AmortizationOfIntangibleAssets", "583000000", dcml=-6)]
    c = cell(dp="amortization_of_intangibles", value="583100000", tag="X")
    assert chk(c, facts).outcome == dck.AUTO_MATCH
    assert (
        chk(
            cell(dp="amortization_of_intangibles", value="590100000", tag="X"), facts
        ).outcome
        == dck.AUTO_MISMATCH
    )


def test_an_unprinted_family_fact_never_overrules_a_printed_line_but_a_note_split_still_does():
    # WELL FY2019: the CF prints "Cash distributions to stockholders" 1,400,712 (company tag); the family's
    # PaymentsOfDividendsCommonStock 1,404,977 is unprinted (the equity-statement charge) -> a read, not a mismatch
    facts = [
        ff("PaymentsOfDividendsCommonStock", "1404977000", dcml=-3),
        ff("CashDistributionsToStockholders", "1400712000", dcml=-3),
    ]
    c = cell(
        dp="dividends_paid", value="1400712000", tag="CashDistributionsToStockholders"
    )
    r = chk(
        c,
        facts,
        [cfl("CashDistributionsToStockholders", "Cash distributions to stockholders")],
    )
    assert r.outcome == dck.NEEDS_READ and "not printed" in r.detail
    # ACN FY2022 (X16): the face's "Receivables and contract assets" 11,776,775 vs the note split 10,484,211
    acn = [
        ff("AccountsReceivableNetCurrent", "10484211000", qtrs=0, dcml=-3),
        ff("ReceivablesAndContractAssets", "11776775000", qtrs=0, dcml=-3),
    ]
    a = cell(
        dp="accounts_receivable",
        value="11776775000",
        tag="ReceivablesAndContractAssets",
    )
    assert (
        chk(
            a,
            acn,
            [ln("ReceivablesAndContractAssets", "Receivables and contract assets")],
        ).outcome
        == dck.AUTO_MISMATCH
    )
    # BMY FY2016: the cited face line is a lower family tier; the tier-1 note split decides
    bmy = [
        ff("AccountsReceivableNetCurrent", "3774000000", qtrs=0),
        ff("ReceivablesNetCurrent", "5543000000", qtrs=0),
    ]
    b = cell(dp="accounts_receivable", value="5543000000", tag="ReceivablesNetCurrent")
    assert (
        chk(b, bmy, [ln("ReceivablesNetCurrent", "Receivables")]).outcome
        == dck.AUTO_MISMATCH
    )


def test_a_printed_tier_decides_or_ranks_with_an_unprinted_first_tier():
    # LRCX FY2023: the face prints PP&E with finance-lease ROU 1,856,672; PropertyPlantAndEquipmentNet 1,802,951
    # is unprinted
    pe = "2023-06-25"
    t2 = "PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization"
    facts = [
        ff("PropertyPlantAndEquipmentNet", "1802951000", qtrs=0, dcml=-3, ddate=pe),
        ff(t2, "1856672000", qtrs=0, dcml=-3, ddate=pe),
    ]
    lines = [ln(t2, "Property and equipment, net")]
    assert (
        chk(cell(dp="ppe_net", value="1856672000", tag=t2, pe=pe), facts, lines).outcome
        == dck.AUTO_MATCH
    )
    assert (
        chk(
            cell(dp="ppe_net", value="1802951000", tag="X", pe=pe), facts, lines
        ).outcome
        == dck.AUTO_MISMATCH
    )
    # WELL FY2025: the printed CF payment ranks with the unprinted common-dividend element (AVGO's printed line also
    # holds preferred dividends, so the first tier still counts)
    div = [
        ff("PaymentsOfDividendsCommonStock", "1877289000", dcml=-3),
        ff("PaymentsOfDividends", "1877959000", dcml=-3),
    ]
    dl = [cfl("PaymentsOfDividends", "Cash distributions to stockholders")]
    for v in ("1877959000", "1877289000"):
        assert (
            chk(cell(dp="dividends_paid", value=v, tag="X"), div, dl).outcome
            == dck.AUTO_MATCH
        )
    # MS FY2017: CashAndCashEquivalentsAtCarryingValue 80,395 is only the CF total; the face prints cash and due
    # from banks 24,816
    cash = [
        ff("CashAndCashEquivalentsAtCarryingValue", "80395000000", qtrs=0),
        ff("CashAndDueFromBanks", "24816000000", qtrs=0),
    ]
    cl = [
        cfl(
            "CashAndCashEquivalentsAtCarryingValue",
            "Cash and cash equivalents, end of period",
        ),
        ln("CashAndDueFromBanks", "Cash and due from banks"),
    ]
    c = cell(dp="cash_and_equivalents", value="24816000000", tag="CashAndDueFromBanks")
    assert chk(c, cash, cl).outcome == dck.AUTO_MATCH
    assert (
        chk(c, cash, cl[:1] + [cfl("CashAndDueFromBanks", "x")]).outcome
        == dck.AUTO_MISMATCH
    )


def test_cash_never_comes_from_the_restricted_cash_cf_total():
    # CVX FY2019: the face prints "Cash and cash equivalents" 5,686 (company tag); 6,911 is the CF reconciliation
    rc = "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents"
    cvx = "CashandCashEquivalentsExcludingTimeDepositsatCarryingValue"
    facts = [ff(rc, "6911000000", qtrs=0), ff(cvx, "5686000000", qtrs=0)]
    lines = [
        cfl(rc, "Cash, Cash Equivalents and Restricted Cash at December 31"),
        ln(cvx, "Cash and cash equivalents"),
    ]
    assert (
        chk(
            cell(dp="cash_and_equivalents", value="5686000000", tag=cvx), facts, lines
        ).outcome
        == dck.AUTO_MATCH
    )
    r = chk(cell(dp="cash_and_equivalents", value="6911000000", tag=rc), facts, lines)
    assert r.outcome == dck.AUTO_MISMATCH and "5686000000" in r.detail
    # CAT FY2019: "Cash and short-term investments" 8,284 on the face, 8,292 with restricted cash on the CF
    cat = [
        ff(rc, "8292000000", qtrs=0),
        ff("CashCashEquivalentsAndShortTermInvestments", "8284000000", qtrs=0),
    ]
    cl = [
        cfl(rc, "Cash at end of year"),
        ln(
            "CashCashEquivalentsAndShortTermInvestments",
            "Cash and short-term investments",
        ),
    ]
    assert (
        chk(
            cell(dp="cash_and_equivalents", value="8284000000", tag="X"), cat, cl
        ).outcome
        == dck.AUTO_MATCH
    )
    # a restricted-cash total the balance sheet itself prints is the registry's step 2 (BAC, AXP)
    assert (
        chk(
            cell(dp="cash_and_equivalents", value="6911000000", tag=rc),
            facts[:1],
            [ln(rc, "Cash")],
        ).outcome
        == dck.AUTO_MATCH
    )


def test_revenue_is_not_the_total_with_other_income_when_a_narrower_line_is_printed():
    # CVX FY2017: "Sales and other operating revenues" 134,674 (OilAndGasRevenue); "Total Revenues and Other Income"
    # 141,722 (Revenues)
    facts = [ff("Revenues", "141722000000"), ff("OilAndGasRevenue", "134674000000")]
    lines = [
        isl("OilAndGasRevenue", "Sales and other operating revenues", 3),
        isl("Revenues", "Total Revenues and Other Income", 6),
    ]
    assert (
        chk(cell(value="134674000000", tag="X"), facts, lines).outcome == dck.AUTO_MATCH
    )
    assert (
        chk(cell(value="141722000000", tag="Revenues"), facts, lines).outcome
        == dck.AUTO_MISMATCH
    )


def test_buybacks_take_the_equity_statement_line_when_the_cf_line_says_and_other():
    # AXP FY2023: CF "Repurchase of American Express common shares and other" 3,650; equity statement 3,519
    facts = [
        ff("PaymentsForRepurchaseOfCommonStock", "3650000000"),
        ff("TreasuryStockValueAcquiredCostMethod", "3519000000"),
    ]
    c = cell(
        dp="share_buybacks",
        value="3519000000",
        tag="TreasuryStockValueAcquiredCostMethod",
    )
    lines = [
        cfl(
            "PaymentsForRepurchaseOfCommonStock",
            "Repurchase of American Express common shares and other",
        )
    ]
    assert chk(c, facts, lines).outcome == dck.AUTO_MATCH
    assert (
        chk(
            c,
            facts,
            [cfl("PaymentsForRepurchaseOfCommonStock", "Repurchase of common shares")],
        ).outcome
        == dck.AUTO_MISMATCH
    )


def test_operating_expenses_is_never_total_costs_and_expenses():
    # BMY FY2018: CostsAndExpenses 16,593 holds cost of products sold; shown 10,980 is not proved wrong by it
    bmy = [
        ff("CostsAndExpenses", "16593000000"),
        ff("CostOfGoodsAndServicesSold", "6547000000"),
    ]
    assert (
        chk(cell(dp="operating_expenses", value="10980000000", tag="X"), bmy).outcome
        == dck.NEEDS_READ
    )
    # QCOM FY2021: derived total_costs_and_expenses-cost_of_revenue = 23,777 - 14,262, cited parts R&D + SG&A
    b = "derived:total_costs_and_expenses-cost_of_revenue"
    ps = [
        part("ResearchAndDevelopmentExpense", "7176000000"),
        part("SellingGeneralAndAdministrativeExpense", "2339000000"),
    ]
    facts = [
        ff("ResearchAndDevelopmentExpense", "7176000000"),
        ff("SellingGeneralAndAdministrativeExpense", "2339000000"),
        ff("CostsAndExpenses", "23777000000"),
        ff("CostOfRevenue", "14262000000"),
    ]
    r = chk(
        cell(dp="operating_expenses", value="9515000000", tag="", parts=ps, badge=b),
        facts,
    )
    assert (r.outcome, r.method) == (dck.AUTO_MATCH, "identity")


def _band_lines(*mid):
    return [
        isl("OperatingIncomeLoss", "Operating income", 10),
        *mid,
        isl(PRE, "Income before income taxes", 30),
    ]


def test_other_income_is_the_printed_band_without_its_interest_lines():
    # BLK FY2018 (0001564590-21-008796 R4): OI 5,457; net gain on investments 1; interest and dividend income 104;
    # interest expense 184; pretax 5,378 -> other income 1 (NonoperatingIncomeExpense -79 is the band with interest)
    facts = [
        ff(PRE, "5378000000"),
        ff("OperatingIncomeLoss", "5457000000"),
        ff("GainLossOnInvestments", "1000000"),
        ff("InvestmentIncomeInterestAndDividend", "104000000"),
        ff("InterestExpense", "184000000"),
        ff("NonoperatingIncomeExpense", "-79000000"),
    ]
    lines = _band_lines(
        isl("GainLossOnInvestments", "Net gain (loss) on investments", 26),
        isl("InvestmentIncomeInterestAndDividend", "Interest and dividend income", 27),
        isl("InterestExpense", "Interest expense", 28),
        isl("NonoperatingIncomeExpense", "Total nonoperating income (expense)", 29),
    )
    c = cell(
        dp="other_income_expense_net", value="1000000", tag="GainLossOnInvestments"
    )
    assert chk(c, facts, lines).outcome == dck.AUTO_MATCH
    r = chk(
        cell(
            dp="other_income_expense_net",
            value="-79000000",
            tag="NonoperatingIncomeExpense",
        ),
        facts,
        lines,
    )
    assert r.outcome == dck.AUTO_MISMATCH and "band" in r.detail


def test_unprinted_interest_income_inside_other_income_is_taken_out():
    # PANW FY2019 (0001327567-21-000029 R4): OI -54.1, interest expense 83.9, "Other income, net" 63.4, pretax
    # -74.6; the note's interest income 69.8 sits inside other income -> 63.4 is not the data point
    facts = [
        ff(PRE, "-74600000", dcml=-5),
        ff("OperatingIncomeLoss", "-54100000", dcml=-5),
        ff("InterestExpense", "83900000", dcml=-5),
        ff("OtherNonoperatingIncomeExpenseNet", "63400000", dcml=-5),
        ff("InterestIncomeOther", "69800000", dcml=-5),
    ]
    lines = _band_lines(
        isl("InterestExpense", "Interest expense", 18),
        isl("OtherNonoperatingIncomeExpenseNet", "Other income, net", 19),
    )
    r = chk(
        cell(
            dp="other_income_expense_net",
            value="63400000",
            tag="OtherNonoperatingIncomeExpenseNet",
        ),
        facts,
        lines,
    )
    assert r.outcome == dck.AUTO_MISMATCH
    assert (
        chk(
            cell(dp="other_income_expense_net", value="-6400000", tag="X"), facts, lines
        ).outcome
        == dck.AUTO_MATCH
    )
    # PM FY2023: "Interest expense, net" -1,061 already holds interest income (note 465): either reading may hold
    pm = [
        ff(PRE, "10450000000"),
        ff("OperatingIncomeLoss", "11556000000"),
        ff("InterestIncomeExpenseNet", "-1061000000"),
        ff("InvestmentIncomeInterest", "465000000"),
    ]
    pl = _band_lines(
        isl("InterestIncomeExpenseNet", "Interest expense, net (Note 15)", 20)
    )
    assert (
        chk(
            cell(dp="other_income_expense_net", value="-45000000", tag="X"), pm, pl
        ).outcome
        == dck.AUTO_MATCH
    )
    # AMGN FY2023: the only interest income fact is a rounded note mention (dcml -8): a read, never a mismatch
    am = [
        ff(PRE, "7855000000"),
        ff("OperatingIncomeLoss", "7897000000"),
        ff("InterestExpenseDebt", "2875000000"),
        ff("InvestmentIncomeInterest", "1200000000", dcml=-8),
    ]
    al = _band_lines(
        isl("InterestExpenseDebt", "Interest expense, net", 17),
        isl("NonoperatingIncomeExpense", "Other income, net", 18),
    )
    assert (
        chk(
            cell(dp="other_income_expense_net", value="1608000000", tag="X"), am, al
        ).outcome
        == dck.NEEDS_READ
    )
    # even a shown value outside the mention's rounding: the "$1.2 billion" cannot prove it wrong
    assert (
        chk(
            cell(dp="other_income_expense_net", value="1500000000", tag="X"), am, al
        ).outcome
        == dck.NEEDS_READ
    )


def test_an_interest_block_subtotal_stands_for_its_lines():
    # WMT FY2017: Interest: debt, finance lease, interest income (100), "Interest, net" 2,267; the sole other line
    # is a 0 loss on extinguishment
    facts = [
        ff(PRE, "20497000000", ddate="2017-01-31"),
        ff("OperatingIncomeLoss", "22764000000", ddate="2017-01-31"),
        ff("InterestExpenseDebt", "2044000000", ddate="2017-01-31"),
        ff("InvestmentIncomeInterest", "100000000", ddate="2017-01-31"),
        ff("InterestIncomeExpenseNet", "-2267000000", ddate="2017-01-31"),
    ]
    lines = _band_lines(
        isl("InterestExpenseDebt", "Debt", 11),
        isl("InvestmentIncomeInterest", "Interest income", 12),
        isl("InterestIncomeExpenseNet", "Interest, net", 13),
    )
    c = cell(
        dp="other_income_expense_net",
        value="0",
        tag="GainsLossesOnExtinguishmentOfDebt",
        pe="2017-01-31",
    )
    assert chk(c, facts, lines).outcome == dck.AUTO_MATCH


def test_an_expense_positive_custom_other_line_must_be_shown_flipped():
    # IBM FY2020: ibm:OtherIncomeAndExpense 802 printed "Other (income) and expense" (not negated); no OI line
    facts = [ff("OtherIncomeAndExpense", "802000000")]
    lines = [isl("OtherIncomeAndExpense", "Other (income) and expense (Note A)", 12)]
    c = cell(
        dp="other_income_expense_net", value="802000000", tag="OtherIncomeAndExpense"
    )
    r = chk(c, facts, lines)
    assert (r.outcome, r.method) == (dck.AUTO_MISMATCH, "sign")
    # a standard element printed with a negated "(income)" label is income-positive already (KLAC, JNJ)
    neg = [
        isl("OtherIncomeAndExpense", "Other expense (income), net", 12, negating=True)
    ]
    assert chk(c, facts, neg).outcome == dck.NEEDS_READ


def test_a_sum_part_whose_tag_sign_contradicts_the_printed_band_follows_the_band():
    # T FY2019: equity in net income of affiliates tagged -6, the printed total identity proves +6
    facts = [
        ff(PRE, "18468000000"),
        ff("OperatingIncomeLoss", "27955000000"),
        ff("InterestExpense", "8422000000"),
        ff("IncomeLossFromEquityMethodInvestments", "-6000000"),
        ff("OtherNonoperatingIncomeExpense", "-1071000000"),
    ]
    lines = _band_lines(isl("InterestExpense", "Interest expense", 21))
    ps = [
        part("IncomeLossFromEquityMethodInvestments", "6000000"),
        part("OtherNonoperatingIncomeExpense", "-1071000000"),
    ]
    c = cell(
        dp="other_income_expense_net",
        value="-1065000000",
        tag="",
        parts=ps,
        badge="derived:sum(printed nonoperating lines)",
    )
    assert chk(c, facts, lines).outcome == dck.AUTO_MATCH
    assert (
        chk(c, facts).outcome == dck.AUTO_MISMATCH
    )  # no printed band: the part's sign is all there is


def test_missing_family_tags_from_the_reads():
    # KLAC FY2025 cf_ar_change 367,897 (ExcludingAcquisitionRelated) beside IncreaseDecreaseInAccountsReceivable 430,874
    k = [
        ff("IncreaseDecreaseInAccountsReceivable", "430874000", dcml=-3),
        ff(
            "IncreaseDecreaseInAccountsReceivableExcludingAcquisitionRelated",
            "367897000",
            dcml=-3,
        ),
    ]
    assert (
        chk(cell(dp="cf_ar_change", value="367897000", tag="X"), k).outcome
        == dck.AUTO_MATCH
    )
    # LMT FY2015 D&A: the CF add-back 1,026 including discontinued operations; segment note 945 continuing only
    lm = [
        ff("DepreciationAndAmortization", "945000000"),
        ff("DepreciationAndAmortizationIncludingDiscontinuedOperations", "1026000000"),
    ]
    assert (
        chk(
            cell(dp="depreciation_and_amortization", value="1026000000", tag="X"), lm
        ).outcome
        == dck.AUTO_MATCH
    )
    # BMY FY2017 IS face bmy:AmortizationofAcquiredIntangibleAssets 97 (the note's AmortizationOfIntangibleAssets 190)
    bm = [
        ff("AmortizationOfIntangibleAssets", "190000000"),
        ff("AmortizationofAcquiredIntangibleAssets", "97000000"),
    ]
    assert (
        chk(
            cell(dp="amortization_of_intangibles", value="97000000", tag="X"), bm
        ).outcome
        == dck.AUTO_MATCH
    )
    # GE FY2023 printed CF cash taxes 1,041 (company tag) beside the ASU 2023-09 note total 994
    ge = [
        ff("IncomeTaxesPaidNet", "994000000"),
        ff("CashPaidReceivedForIncomeTaxesNetOfDiscontinuedOperations", "1041000000"),
    ]
    assert (
        chk(
            cell(dp="cash_paid_for_income_taxes", value="1041000000", tag="X"), ge
        ).outcome
        == dck.AUTO_MATCH
    )


def test_label_gated_family_members():
    # GILD FY2015 CF "Amortization expense" 937 (AdjustmentForAmortization) is intangible amortization ...
    g = [ff("AdjustmentForAmortization", "937000000")]
    c = cell(
        dp="amortization_of_intangibles",
        value="937000000",
        tag="AdjustmentForAmortization",
    )
    assert (
        chk(c, g, [cfl("AdjustmentForAmortization", "Amortization expense")]).outcome
        == dck.AUTO_MATCH
    )
    # ... WELL's "Other amortization expenses" (debt costs) is not
    assert (
        chk(
            c, g, [cfl("AdjustmentForAmortization", "Other amortization expenses")]
        ).outcome
        == dck.NEEDS_READ
    )
    # SCCO "Interest expense" tagged InterestCostsIncurred 360.9
    s = [ff("InterestCostsIncurred", "360900000", dcml=-5)]
    ie = cell(dp="interest_expense", value="360900000", tag="InterestCostsIncurred")
    assert (
        chk(ie, s, [isl("InterestCostsIncurred", "Interest expense", 20)]).outcome
        == dck.AUTO_MATCH
    )
    assert (
        chk(
            ie, s, [isl("InterestCostsIncurred", "Interest costs incurred", 20)]
        ).outcome
        == dck.NEEDS_READ
    )
    # FTNT "Interest income" tagged InvestmentIncomeNet 5,295
    f = [ff("InvestmentIncomeNet", "5295000", dcml=-3)]
    ii = cell(dp="interest_income", value="5295000", tag="InvestmentIncomeNet")
    assert (
        chk(ii, f, [isl("InvestmentIncomeNet", "INTEREST INCOME", 20)]).outcome
        == dck.AUTO_MATCH
    )
    assert (
        chk(ii, f, [isl("InvestmentIncomeNet", "Investment income, net", 20)]).outcome
        == dck.NEEDS_READ
    )


def test_gated_tiers_continuing_eps_and_total_equity():
    # ADI FY2017 "Basic earnings per common share" 2.32 tagged as continuing operations, no discontinued line
    e = [ff("IncomeLossFromContinuingOperationsPerBasicShare", "2.32", dcml=2)]
    c = cell(
        dp="basic_eps",
        value="2.32",
        tag="IncomeLossFromContinuingOperationsPerBasicShare",
    )
    assert chk(c, e).outcome == dck.AUTO_MATCH
    # DELL FY2020: a discontinued-operations line exists, the continuing figure is not total EPS
    assert (
        chk(c, [*e, ff("IncomeLossFromDiscontinuedOperationsNetOfTax", "100")]).outcome
        == dck.NEEDS_READ
    )
    # AVGO FY2024 "Total stockholders' equity" 67,678 with no NCI line
    t = [
        ff(
            "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
            "67678000000",
            qtrs=0,
        )
    ]
    s = cell(dp="stockholders_equity", value="67678000000", tag="X")
    assert chk(s, t).outcome == dck.AUTO_MATCH
    assert (
        chk(s, [*t, ff("MinorityInterest", "76000000", qtrs=0)]).outcome
        == dck.NEEDS_READ
    )


def test_derived_cells_without_a_derived_badge_and_the_parent_equity_identity():
    # GILD FY2015 total liabilities exported with a blank badge: assets 51,716 - total equity 19,113 - temporary
    # equity 2 = 32,601
    facts = [
        ff("Assets", "51716000000", qtrs=0),
        ff(
            "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
            "19113000000",
            qtrs=0,
        ),
        ff("TemporaryEquityCarryingAmountAttributableToParent", "2000000", qtrs=0),
    ]
    c = cell(dp="total_liabilities", value="32601000000", tag="", badge="as_printed")
    assert chk(c, facts).outcome == dck.AUTO_MATCH
    assert (
        chk(
            cell(
                dp="total_liabilities", value="32603000000", tag="", badge="as_printed"
            ),
            facts,
        ).outcome
        == dck.NEEDS_READ
    )
    # CAT FY2016: badge total_equity-noncontrolling_interest but the value is the total with NCI (13,213, NCI 76)
    cat = [
        ff(
            "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
            "13213000000",
            qtrs=0,
        ),
        ff("MinorityInterest", "76000000", qtrs=0),
    ]
    b = "derived:total_equity-noncontrolling_interest"
    r = chk(cell(dp="stockholders_equity", value="13213000000", tag="X", badge=b), cat)
    assert r.outcome == dck.AUTO_MISMATCH and "13137000000" in r.detail
    assert (
        chk(
            cell(dp="stockholders_equity", value="13137000000", tag="X", badge=b), cat
        ).outcome
        == dck.AUTO_MATCH
    )


def test_dps_on_the_company_level_common_stock_member():
    # MA FY2020 (0001141391-23-000020 R94): CommonStockDividendsPerShareDeclared[EquityComponents=CommonStock]=1.64
    p = part(
        "CommonStockDividendsPerShareDeclared",
        "1.64",
        dims="EquityComponents=CommonStock",
    )
    c = cell(
        dp="dividends_per_share",
        value="1.64",
        tag="",
        parts=[p],
        badge="as_printed",
        pe="2020-12-31",
    )
    f = [
        ff(
            "CommonStockDividendsPerShareDeclared",
            "1.64",
            ddate="2020-12-31",
            dims="EquityComponents=CommonStock",
            dcml=2,
        )
    ]
    assert chk(c, f).outcome == dck.AUTO_MATCH
    f2 = [
        ff(
            "CommonStockDividendsPerShareDeclared",
            "1.81",
            ddate="2020-12-31",
            dims="EquityComponents=CommonStock",
            dcml=2,
        )
    ]
    assert chk(c, f2).outcome == dck.AUTO_MISMATCH


# ---------------------------------------------------------------- three-source agreement (FSN, companyfacts, R page)
CIK = "0000000001"
_RPAGE = """<table class="report">
<tr><th class="tl" colspan="1" rowspan="2"><div><strong>CONSOLIDATED STATEMENTS OF INCOME - USD ($)<br>
 shares in Thousands, $ in Millions</strong></div></th><th class="th" colspan="2">12 Months Ended</th></tr>
<tr><th class="th"><div>Dec. 31, 2023</div></th><th class="th"><div>Dec. 31, 2022</div></th></tr>
<tr class="re"><td class="pl"><a onclick="Show.showAR( this, 'defref_us-gaap_Revenues', window );">Revenue</a></td>
<td class="nump">$ 100</td><td class="nump">$ 90</td></tr>
<tr class="ro"><td class="pl"><a onclick="Show.showAR( this, 'defref_us-gaap_CostOfRevenue', window );">Cost</a></td>
<td class="nump">(40)</td><td class="nump">(35)</td></tr>
<tr class="ro"><td class="pl"><a onclick="Show.showAR( this, 'defref_us-gaap_EarningsPerShareBasic', window );">Basic</a></td>
<td class="nump">$ 1.25</td><td class="nump">$ 1.10</td></tr>
<tr class="ro"><td class="pl"><a onclick="Show.showAR( this, 'defref_us-gaap_WeightedAverageNumberOfSharesOutstandingBasic', window );">Shares</a></td>
<td class="nump">80,000</td><td class="nump">81,000</td></tr>
</table>"""


def _cf(*facts):
    """companyfacts JSON: (tag, value, uom[, start, end, accn])."""
    out: dict = {}
    for t in facts:
        tag, val, uom = t[:3]
        start, end, accn = (t[3:] + ("2023-01-01", PE, ACC)[len(t) - 3 :])[:3]
        row = {"end": end, "val": val, "accn": accn, "form": "10-K"}
        if start:
            row["start"] = start
        out.setdefault(tag, {"units": {}})["units"].setdefault(uom, []).append(row)
    return {"cik": 1, "facts": {"us-gaap": out}}


def _store(tmp_path, cf=None, page=_RPAGE):
    if cf is not None:
        (tmp_path / "cf").mkdir(parents=True, exist_ok=True)
        (tmp_path / "cf" / f"CIK{CIK}.json").write_text(json.dumps(cf))
    if page is not None:
        (tmp_path / "r" / ACC).mkdir(parents=True, exist_ok=True)
        (tmp_path / "r" / ACC / "R4.htm").write_text(page)
    return dck.SourceStore(tmp_path)


def three(c, facts, store, lines=()):
    fl = dck.Filing(list(facts), list(lines))
    return dck.three_source_cell(c, dck.check_cell(c, fl), fl, store, CIK)


def test_three_sources_agree_and_the_certificate_says_so(tmp_path):
    st = _store(tmp_path, _cf(("Revenues", 100_000_000, "USD")))
    s = three(cell(value="100000000", tag="abc_X"), [ff("Revenues", "100000000")], st)
    assert s.outcome == dck.AGREE3, s
    (leg,) = s.legs
    # the checker's own fact's tag, never the export's cited tag
    assert leg["tag"] == "Revenues" and leg["rpage"] == "100000000"
    assert leg["agree"] == {"fsn": True, "companyfacts": True, "rpage": True}


def test_one_missing_source_is_agree2_and_none_but_one_is_single(tmp_path):
    rev = [ff("Revenues", "100000000")]
    c = cell(value="100000000")
    # companyfacts holds nothing for that accession (a custom tag, a later filing's comparative)
    st = _store(
        tmp_path,
        _cf(("Revenues", 100_000_000, "USD", "2023-01-01", PE, "0000000009-25-000001")),
    )
    assert three(c, rev, st).outcome == dck.AGREE2
    # no printed page and no companyfacts: the FSN fact alone never proves a cell
    assert three(c, rev, dck.SourceStore(tmp_path / "empty")).outcome == dck.SINGLE
    # a cell the checker sends to a read has no decided fact: SINGLE
    assert (
        three(
            cell(dp="research_and_development", value="7", tag="abc_RandD"),
            [ff("abc_RandD", "7")],
            st,
        ).outcome
        == dck.SINGLE
    )


def test_a_source_that_differs_is_disagree(tmp_path):
    rev = [ff("Revenues", "100000000")]
    c = cell(value="100000000")
    # companyfacts differs
    s = three(c, rev, _store(tmp_path / "a", _cf(("Revenues", 101_000_000, "USD"))))
    assert s.outcome == dck.DISAGREE and s.legs[0]["agree"]["companyfacts"] is False
    # the printed line differs (the page prints 100 million; the shown and filed 103 million)
    s = three(
        cell(value="103000000"),
        [ff("Revenues", "103000000")],
        _store(tmp_path / "b", _cf(("Revenues", 103_000_000, "USD"))),
    )
    assert s.outcome == dck.DISAGREE and s.legs[0]["agree"]["rpage"] is False
    # the checker's own AUTO_MISMATCH is a disagreeing FSN source whatever the others say
    s = three(
        cell(value="90000000"),
        rev,
        _store(tmp_path / "c", _cf(("Revenues", 90_000_000, "USD"))),
    )
    assert s.outcome == dck.DISAGREE


def test_companyfacts_matches_tag_accession_period_and_duration():
    cf = dck.CompanyFacts(
        _cf(
            ("Revenues", 100, "USD"),
            ("Revenues", 25, "USD", "2023-10-01", PE, ACC),  # a quarter
            ("Revenues", 90, "USD", "2022-01-01", "2022-12-31", ACC),  # prior year
            ("Revenues", 7, "EUR"),  # another currency
            ("Assets", 500, "USD", "", PE, ACC),
        )
    )
    assert [f.value for f in cf.values("Revenues", ACC, PE, 4)] == [D(100)]
    assert [f.value for f in cf.values("Assets", ACC, "2024-01-03", 0)] == [
        D(500)
    ]  # +-7 days
    assert (
        cf.values("Assets", ACC, PE, 4) == []
        and cf.values("Revenues", "x", PE, 4) == []
    )


def test_printed_values_scale_by_the_lines_unit_and_take_the_cited_period_column(
    tmp_path,
):
    page = _store(tmp_path, page=_RPAGE).rpage(CIK, ACC, "R4.htm")
    assert page.rows[0].tag == "Revenues" and page.share_multiplier == 1000
    pv = dck.printed_values
    assert pv(page, "Revenues", PE, 4, "USD") == [(D(100_000_000), D(1_000_000))]
    assert pv(page, "Revenues", "2022-12-31", 4, "USD")[0][0] == D(90_000_000)
    assert pv(page, "EarningsPerShareBasic", PE, 4, "USD/shares") == [
        (D("1.25"), D("0.01"))
    ]
    assert pv(page, "WeightedAverageNumberOfSharesOutstandingBasic", PE, 4, "shares")[
        0
    ][0] == D(80_000_000)
    assert (
        pv(page, "Revenues", "2021-12-31", 4, "USD") == []
        and pv(None, "Revenues", PE, 4, "USD") == []
    )
    # 'Share data in Millions' scales share counts, never money (WMT FY2015 prints $ 462,000,000 in full)
    from scrooner_pipeline.verification.filing_kit import (
        money_multiplier,
        share_multiplier,
    )

    wmt = "Shareholder's Equity (Narrative)(Details) (USD $) Share data in Millions, unless otherwise specified"
    assert (money_multiplier(wmt), share_multiplier(wmt)) == (1, 1_000_000)


def test_printed_sign_follows_the_label_and_per_share_is_unscaled(tmp_path):
    st = _store(
        tmp_path,
        _cf(
            ("CostOfRevenue", 40_000_000, "USD"),
            ("EarningsPerShareBasic", 1.25, "USD/shares"),
        ),
    )
    s = three(
        cell(dp="cost_of_revenue", value="40000000", tag="CostOfRevenue"),
        [ff("CostOfRevenue", "40000000")],
        st,
    )
    assert s.outcome == dck.AGREE3, s  # printed (40) is the magnitude 40 million
    # FSN tags EPS in 'USD': the per-share line is still read unscaled
    eps = [dck.FilingFact(ACC, "EarningsPerShareBasic", PE, 4, "", D("1.25"), 2, "USD")]
    assert (
        three(
            cell(dp="basic_eps", value="1.25", tag="EarningsPerShareBasic"), eps, st
        ).outcome
        == dck.AGREE3
    )
    # without a companyfacts unit, the data point decides: the per-share line is unscaled, not $ in millions
    st2 = _store(tmp_path / "noeps", _cf(("Revenues", 1, "USD")))
    assert (
        three(
            cell(dp="basic_eps", value="1.25", tag="EarningsPerShareBasic"), eps, st2
        ).outcome
        == dck.AGREE2
    )


def test_summed_cells_check_each_part_across_the_sources(tmp_path):
    st = _store(
        tmp_path,
        _cf(("Revenues", 100_000_000, "USD"), ("CostOfRevenue", 40_000_000, "USD")),
    )
    facts = [ff("Revenues", "100000000"), ff("CostOfRevenue", "40000000")]
    c = cell(
        dp="sga_expense",
        value="140000000",
        tag="",
        parts=(part("Revenues", "100000000"), part("CostOfRevenue", "40000000")),
        badge="derived:selling_and_marketing+general_and_administrative",
    )
    a = dck.check_cell(c, dck.Filing(facts, []))
    assert a.outcome == dck.AUTO_MATCH, a
    s = dck.three_source_cell(c, a, dck.Filing(facts, []), st, CIK)
    assert s.outcome == dck.AGREE3 and [g["tag"] for g in s.legs] == [
        "Revenues",
        "CostOfRevenue",
    ]
    # the parts do not sum to the shown value: the checker's mismatch is a disagreeing FSN source, never SINGLE
    bad = dataclasses.replace(c, value=D("150000000"))
    a2 = dck.check_cell(bad, dck.Filing(facts, []))
    assert a2.outcome == dck.AUTO_MISMATCH
    assert (
        dck.three_source_cell(bad, a2, dck.Filing(facts, []), st, CIK).outcome
        == dck.DISAGREE
    )


def test_certificate_and_draw_check_all_record_source_agreement(tmp_path):
    cov = _two(tmp_path)
    st = _store(tmp_path / "cache", _cf(("Revenues", 100, "USD")), page=None)
    run = dc.certify(
        "T", "1", cov, Src([ff("Revenues", "100"), ff("abc_RandD", "7")]), store=st
    )
    assert dck.agreement_counts(run.three) == {
        dck.AGREE3: 0,
        dck.AGREE2: 1,
        dck.DISAGREE: 0,
        dck.SINGLE: 1,
    }
    reads = tmp_path / "reads.csv"
    reads.write_text(
        "data_point,fiscal_year,verdict,reader,evidence\nresearch_and_development,2023,MATCH,a,R4 7\n"
    )
    done = dc.certify(
        "T",
        "1",
        cov,
        Src([ff("Revenues", "100"), ff("abc_RandD", "7")]),
        reads=dck.load_reads(reads),
        store=st,
    )
    cert = json.loads(
        json.dumps(dc.certificate(done, None, "2026-11-22", "Ritwik (cloud)"))
    )
    _check_schema(cert, json.loads(dc.CERTIFICATE_SCHEMA_PATH.read_text()))
    by = {c["data_point"]: c["source_agreement"]["outcome"] for c in cert["cells"]}
    assert by == {"revenue": dck.AGREE2, "research_and_development": dck.SINGLE}
    assert cert["draw_check"]["three_source"][dck.AGREE2] == 1
    # the read-only top-100 run: every shown cell (--all-shown), agreement columns and per-company counts
    p = tmp_path / "top100-coverage.csv"
    with open(p, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(
            [
                "rank",
                "ticker",
                "company_id",
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
        )
        w.writerow(
            [
                "1",
                "T",
                "7",
                "revenue",
                "2023",
                PE,
                "100",
                ACC,
                "R4",
                "Revenues",
                "",
                dc.SHOWN,
            ]
        )
    sc = _script()
    assert (
        sc.draw_check_all(
            p,
            tmp_path / "o",
            "d",
            source=Src([ff("Revenues", "100")]),
            store=st,
            all_shown=True,
            cik_of=lambda i: CIK,
        )
        == 0
    )
    (row,) = _rows(tmp_path / "o" / "draw-check-d.csv")
    assert (row["agreement"], row["fsn"], row["companyfacts"]) == (
        dck.AGREE2,
        "100",
        "100",
    )
    (summ,) = _rows(tmp_path / "o" / "draw-check-summary-d.csv")
    assert (summ["agree3"], summ["agree2"]) == ("0", "1")
    # --all-shown checks every shown cell, not only the draw of 199
    with open(p, "a", newline="") as fh:
        w = csv.writer(fh)
        for y in range(1800, 1800 + dc.DRAW_SIZE):
            w.writerow(
                [
                    "1",
                    "T",
                    "7",
                    "revenue",
                    str(y),
                    PE,
                    "100",
                    ACC,
                    "R4",
                    "Revenues",
                    "",
                    dc.SHOWN,
                ]
            )
    for every, n in ((True, dc.DRAW_SIZE + 1), (False, dc.DRAW_SIZE)):
        sc.draw_check_all(
            p,
            tmp_path / "o2",
            "d",
            source=Src([ff("Revenues", "100")]),
            store=st,
            all_shown=every,
            cik_of=lambda i: CIK,
        )
        assert len(_rows(tmp_path / "o2" / "draw-check-d.csv")) == n


def test_a_text_stated_drawn_cell_is_settled_only_by_its_matching_read(tmp_path):
    """BMY accounts_receivable FY2020/22/25 (2026-11-28): a text-stated cell (badge printed, no tag, no parts) is LOCATOR
    in the claim check and NEEDS_READ in the draw checker; its MATCH read settled the draw checker but the LOCATOR kept
    the company REVIEW forever. Mutation: the verdict ignoring settled_by_read stays REVIEW and fails this test."""

    def badged(name, rows):
        p = tmp_path / name
        with open(p, "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(
                [
                    "data_point",
                    "fiscal_year",
                    "period_end",
                    "shown_value",
                    "accession",
                    "r_page",
                    "tag",
                    "parts",
                    "display",
                    "badge",
                ]
            )
            w.writerows([r + ["as_printed"] for r in rows])
        return p

    cov = badged(
        "cov.csv",
        [
            ["revenue", "2023", PE, "100", ACC, "R4", "Revenues", "", dc.SHOWN],
            ["accounts_receivable", "2023", PE, "7", ACC, "R4", "", "", dc.SHOWN],
        ],
    )
    facts = [ff("Revenues", "100")]
    run = dc.certify("T", "1", cov, Src(facts))
    assert run.verdict == "REVIEW"
    assert [
        s.result for s in run.shown if s.cell.data_point == "accounts_receivable"
    ] == ["LOCATOR"]

    def with_read(verdict):
        reads = tmp_path / f"reads-{verdict}.csv"
        reads.write_text(
            f"data_point,fiscal_year,verdict,reader,evidence\naccounts_receivable,2023,{verdict},agent-7,R81 prints 7\n"
        )
        return dc.certify("T", "1", cov, Src(facts), reads=dck.load_reads(reads))

    assert with_read("MATCH").verdict == "PASS"
    # the certificate agrees with the verdict: display_cert_load refuses a PASS whose drawn cell is not MATCH
    cert = json.loads(
        json.dumps(
            dc.certificate(with_read("MATCH"), None, "2026-11-28", "Ritwik (cloud)")
        )
    )
    (ar,) = [c for c in cert["cells"] if c["data_point"] == "accounts_receivable"]
    assert (ar["evidence"], ar["result"], ar["verified_by"]) == (
        "drawn",
        "MATCH",
        "read:agent-7",
    )
    assert "settled by filing read (agent-7)" in ar["detail"]
    wrong = with_read("MISMATCH")
    assert wrong.verdict == "FAIL" and wrong.errors == 1
    # a read never settles a tagged cell's LOCATOR (value found off the cited page): the approver still looks
    tagged = badged(
        "tagged.csv",
        [["revenue", "2023", PE, "100", ACC, "R9", "Revenues", "", dc.SHOWN]],
    )
    reads = tmp_path / "reads-tagged.csv"
    reads.write_text(
        "data_point,fiscal_year,verdict,reader,evidence\nrevenue,2023,MATCH,agent-7,R4 prints 100\n"
    )
    t = dc.certify("T", "1", tagged, Src(facts), reads=dck.load_reads(reads))
    assert [s.result for s in t.shown] == ["LOCATOR"] and t.verdict == "REVIEW"
