"""Automated draw checker (certification/draw_check.py, founder 2026-11-22): each drawn cell against the cited
filing's own XBRL facts; only NEEDS_READ and AUTO_MISMATCH cells go to a person or agent read."""

from __future__ import annotations

import csv
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
    # a rounded fact the shown value does not round to is still a mismatch
    c2 = cell(dp="amortization_of_intangibles", value="2700000000", tag="X")
    assert (
        chk(c2, [ff("AmortizationOfIntangibleAssets", "2800000000", dcml=-8)]).outcome
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
    assert chk(i, oi).outcome == dck.AUTO_MATCH


def test_parent_net_income_tagged_as_available_to_common_decides_before_profit_loss():
    facts = [
        ff("NetIncomeLossAvailableToCommonStockholdersBasic", "2998"),
        ff("ProfitLoss", "3003"),
    ]
    assert (
        chk(cell(dp="net_income", value="2998", tag="X"), facts).outcome
        == dck.AUTO_MATCH
    )
    assert (
        chk(cell(dp="net_income", value="3003", tag="X"), facts).outcome
        == dck.AUTO_MISMATCH
    )
