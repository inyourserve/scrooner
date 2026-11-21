from decimal import Decimal as D

from scrooner_pipeline.mapper.top100_coverage import classify


def c(pv=None, pr=None, pval=None, sv=None, bs=None, br=None, tm=None, dm="mapped"):
    return classify(pv, pr, pval, sv, bs, br, tm, dm)


def test_proven_needs_matching_served_value():
    assert c("PROVEN", None, D(5), D(5)) == ("PROVEN", None)
    assert c("PROVEN", None, D(5), D(6)) == ("UNCHECKED", "proof_is_for_another_value")
    assert c("PROVEN", None, D(5), None) == (
        "BLANK",
        "proof_proven_but_no_served_value",
    )


def test_disagree_and_unchecked():
    assert c("DISAGREE", "x", D(5), D(5)) == ("DISAGREE", "x")
    assert c("UNCHECKED", None, None, D(1))[0] == "UNCHECKED"
    assert c(sv=D(1)) == ("UNCHECKED", "no_proof_row")


def test_reasons_only_without_a_served_value():
    assert c("NOT_PRESENTED", "np") == ("REASON", "np")
    assert c(bs="not_in_template", br="not_in_template")[0] == "REASON"
    assert c(bs="defect", br="held_pending_verifier")[0] == "HELD"
    assert c(bs="not_presented", sv=D(1))[0] == "UNCHECKED"
    assert c(tm="not_presented")[0] == "REASON"


def test_blank_variants():
    assert c(bs="defect", br="not_captured") == ("BLANK", "not_captured")
    assert c(dm="not_presented") == ("BLANK", "docmap_not_presented_not_loaded")
    assert c() == ("BLANK", "no_value_no_reason")


def test_held_is_its_own_class_not_blank_not_reason():
    # guard-held and open-finding defects are HELD whatever the code; plain capture defects stay BLANK
    assert c(bs="defect", br="proof_disagree") == ("BLANK", "proof_disagree")
    assert classify(
        None,
        None,
        None,
        None,
        "defect",
        "proof_disagree",
        None,
        "mapped",
        "guard_hidden",
    ) == (
        "HELD",
        "proof_disagree",
    )
    assert classify(
        None,
        None,
        None,
        None,
        "defect",
        "filer_scale_error",
        None,
        "mapped",
        "finding_open",
    ) == (
        "HELD",
        "filer_scale_error",
    )
    assert classify(
        None, None, None, None, "defect", "not_captured", None, "mapped", "unclassified"
    ) == (
        "BLANK",
        "not_captured",
    )
    assert (
        classify(None, None, None, D(1), "defect", "x", None, "mapped", "guard_hidden")[
            0
        ]
        == "UNCHECKED"
    )


def test_summary_pct_excludes_held():
    from scrooner_pipeline.mapper.top100_coverage import Company, summarize

    rows = [
        {"company_id": 1, "class": k} for k in ("PROVEN", "REASON", "HELD", "BLANK")
    ]
    out = summarize(rows, [Company(1, "X", 1, "")], {}, "t")
    assert out[0]["HELD"] == 1 and out[0]["pct_proven_plus_reason"] == "50.0"


def test_era_unmapped_is_a_gap_not_a_reason():
    assert c(bs="not_presented", br="era_unmapped") == ("BLANK", "era_unmapped")
    assert classify(
        None,
        None,
        None,
        None,
        None,
        None,
        "not_presented",
        "mapped",
        None,
        "era_unmapped",
    ) == ("BLANK", "era_unmapped")
    # a served value stays UNCHECKED, a genuine not_presented stays a reason
    assert c(bs="not_presented", br="era_unmapped", sv=D(1))[0] == "UNCHECKED"
    assert c(bs="not_presented", br="x")[0] == "REASON"


def test_not_in_template_on_an_in_template_point_is_blank():
    def k(bs=None, tm=None, tpl=None):
        return classify(None, None, None, None, bs, bs, tm, "mapped", None, None, tpl)

    assert k(bs="not_in_template", tpl=True) == (
        "BLANK",
        "not_in_template_but_in_template",
    )
    assert k(tm="not_in_template", tpl=True)[0] == "BLANK"
    assert k(bs="not_in_template", tpl=False)[0] == "REASON"
    assert k(bs="not_in_template", tpl=None)[0] == "REASON"
    assert k(bs="not_presented", tpl=True)[0] == "REASON"


def test_r_page_comes_from_the_years_own_filing_not_the_docmap_read():
    from datetime import date

    from scrooner_pipeline.mapper.top100_coverage import _statement_pages

    class Cur:
        def fetchall(self):
            d15, d24 = date(2015, 6, 30), date(2024, 6, 30)
            return [
                (
                    4,
                    d15,
                    "0001193125-15-272806",
                    "BS",
                    4,
                    2,
                ),  # a parenthetical with few BS lines
                (
                    4,
                    d15,
                    "0001193125-15-272806",
                    "BS",
                    5,
                    40,
                ),  # the balance sheet itself
                (4, d15, "0001193125-15-272806", "CF", 7, 30),
                (4, d24, "0000950170-24-087843", "CF", 6, 30),
            ]

    class Conn:
        def execute(self, sql, params):
            assert "fsn.line" in sql
            return Cur()

    pages = _statement_pages(Conn(), [4])
    assert pages[(4, date(2015, 6, 30), "BS")] == ("0001193125-15-272806", "R5.htm")
    assert pages[(4, date(2015, 6, 30), "CF")][1] == "R7.htm"
    assert pages[(4, date(2024, 6, 30), "CF")][1] == "R6.htm"
    assert (
        4,
        date(2015, 6, 30),
        "IS",
    ) not in pages  # no guess where the filing prints nothing


def test_combined_line_with_filing_evidence_is_a_reason_bare_not_in_template_is_blank():
    def k(bs=None, tm=None, tpl=None, comb=False):
        return classify(
            None, None, None, None, bs, bs, tm, "mapped", None, None, tpl, comb
        )

    assert k(bs="not_in_template", tpl=True, comb=True) == (
        "REASON",
        "line_presented_combined",
    )
    assert k(tm="not_in_template", tpl=True, comb=True)[0] == "REASON"
    assert k(bs="not_in_template", tpl=True, comb=False)[0] == "BLANK"
    # evidence never overrides a served value
    assert (
        classify(
            None, None, None, D(1), None, None, None, "mapped", None, None, True, True
        )[0]
        == "UNCHECKED"
    )


# ---- one filing per locator, reason text, DERIVED ----
def _idx():
    from scrooner_pipeline.mapper.top100_coverage import LocatorIndex

    i = LocatorIndex()
    A, B = (
        "0001564590-18-019062",
        "0001564590-17-014900",
    )  # latest filing / the year's own filing
    i.add(A, 4, 9, "BS", "AssetsCurrent", "Total current assets")
    i.add(A, 4, 16, "BS", "Assets", "Total assets")
    i.add(A, 5, 1, "BS", "CommonStockSharesOutstanding", "shares")  # parenthetical
    i.add(A, 6, 19, "CF", "NetCashProvidedByUsedInOperatingActivities", "CFO")
    i.add(
        B, 5, 9, "BS", "AssetsCurrent", "Total current assets"
    )  # own-year layout differs: BS is R5
    i.add(B, 4, 1, "BS", "Other", "x")
    i.add(A, 40, 1, "UN", "InterestExpenseNonoperating", "Interest expense")
    return i


def test_proven_locator_page_comes_from_the_proofs_accession_only():
    from scrooner_pipeline.mapper.top100_coverage import proven_locator

    A, B = "0001564590-18-019062", "0001564590-17-014900"
    assert proven_locator(A, "BS", 9, "AssetsCurrent", _idx()) == (
        A,
        "R4.htm",
        "proof_line",
    )
    assert proven_locator(B, "BS", 9, "AssetsCurrent", _idx()) == (
        B,
        "R5.htm",
        "proof_line",
    )
    assert (
        proven_locator(
            A, "CF", None, "NetCashProvidedByUsedInOperatingActivities", _idx()
        )[1]
        == "R6.htm"
    )
    # a parenthetical tag lands on the parenthetical report of the SAME filing
    assert (
        proven_locator(A, "BS", None, "CommonStockSharesOutstanding", _idx())[1]
        == "R5.htm"
    )
    # a note line is found by tag (stmt UN)
    assert proven_locator(A, "UN", None, "InterestExpenseNonoperating", _idx()) == (
        A,
        "R40.htm",
        "proof_tag",
    )
    # a tag on no line of the filing: never the statement page, the page stays blank
    acc, page, src = proven_locator(A, "CF", None, "InterestPaid", _idx())
    assert (acc, page) == (A, "") and src == "note_fact_report_not_stored"
    assert proven_locator(None, "BS", 9, "Assets", _idx()) == ("", "", "none")


def test_reason_locator_uses_one_evidence_row_and_never_mixes_filings():
    from scrooner_pipeline.mapper.top100_coverage import reason_locator

    A = "0001564590-18-019062"
    assert reason_locator([(A, 7, None, "Interest and other", "IS")], "IS", _idx())[
        :3
    ] == (A, "R7.htm", "evidence_report")
    # no report: the label finds the report in the same filing; then the line position
    assert reason_locator([(A, None, None, "Total assets", "BS")], "BS", _idx())[
        :2
    ] == (A, "R4.htm")
    assert reason_locator([(A, None, 16, "", "BS")], "BS", _idx())[:2] == (A, "R4.htm")
    assert reason_locator([(A, None, 16, "", "BS")], "BS", _idx())[3] == "Total assets"
    assert reason_locator([], "BS", _idx()) == ("", "", "none", "")


def test_combined_reason_quotes_the_evidence_label():
    from scrooner_pipeline.mapper.top100_coverage import combined_reason_text as f

    assert f("combined line '' (a,b): x", "Depreciation, amortization, and other") == (
        "combined line 'Depreciation, amortization, and other' (a,b): x"
    )
    assert "''" not in f("combined line '' (a,b): x", "")
    assert f("combined line 'L': x", "Other") == "combined line 'L': x"


def _row(dp, cls="PROVEN", acc="A", fam="", fy=2024, val="1"):
    return {
        "company_id": 1,
        "data_point": dp,
        "fiscal_year": fy,
        "class": cls,
        "_shown_acc": acc,
        "_family": fam,
        "shown_value": val,
        "reason_code": "",
        "reason": "",
        "evidence": "",
        "accession": acc,
        "r_page": "R2.htm",
        "locator_source": "proof_line",
    }


def test_derived_counts_only_with_proven_inputs_of_one_filing():
    from scrooner_pipeline.mapper.top100_coverage import (
        DERIVED_FAMILY,
        Company,
        resolve_derived,
        summarize,
    )

    def run(rev_acc="A", cor_acc="A", cor_cls="PROVEN"):
        rows = [
            _row("revenue", acc=rev_acc),
            _row("cost_of_revenue", cls=cor_cls, acc=cor_acc),
            _row("gross_profit", cls="UNCHECKED", acc="", fam=DERIVED_FAMILY),
        ]
        resolve_derived(rows)
        return rows

    r = run()
    assert (r[2]["class"], r[2]["reason_code"]) == ("DERIVED", "derived_not_printed")
    assert r[2]["evidence"] == "revenue=1@A; cost_of_revenue=1@A"
    for r in (run(cor_acc="B"), run(cor_cls="UNCHECKED"), run(cor_acc="")):
        assert (r[2]["class"], r[2]["reason_code"]) == (
            "UNCHECKED",
            "derived_inputs_unproven",
        )
    out = summarize(
        [dict(company_id=1, **{"class": k}) for k in ("DERIVED", "BLANK")],
        [Company(1, "X", 1, "")],
        {},
        "t",
    )
    assert out[0]["DERIVED"] == 1 and out[0]["pct_proven_plus_reason"] == "50.0"


def test_locator_index_fetch_is_keyed_by_accession():
    from scrooner_pipeline.mapper.top100_coverage import _locator_index

    class Conn:
        def execute(self, sql, params):
            assert "f.accession = any" in sql

            class C:
                def fetchall(self):
                    if "fsn.report" in sql:
                        return [("A", 3, "Consolidated Balance Sheets")]
                    return [("A", 4, 9, "BS", "AssetsCurrent", "Total current assets")]

            return C()

    idx = _locator_index(Conn(), {"A", ""}, {"AssetsCurrent"})
    assert idx.line[("A", "BS", 9)] == 4
    assert idx.titles[("A", 3)] == "Consolidated Balance Sheets"


def test_proven_cell_carries_no_reason_code_or_text():
    from scrooner_pipeline.mapper.top100_coverage import reason_fields

    assert reason_fields("PROVEN", "x", "the line is not mapped for this era") == (
        "",
        "",
    )
    assert reason_fields("REASON", "np", "why") == ("np", "why")
    assert reason_fields("BLANK", None, None) == ("", "")


def test_note_only_fact_gets_its_page_from_the_cached_pre_lookup_of_the_same_filing():
    from scrooner_pipeline.mapper.top100_coverage import proven_locator

    A, B = "0001564590-18-019062", "0001564590-17-014900"
    look = {(A, "InterestPaid"): 53, (B, "InterestPaid"): 9}
    assert proven_locator(A, "CF", None, "InterestPaid", _idx(), look) == (
        A,
        "R53.htm",
        "note_report_from_pre",
    )
    # the lookup is keyed by accession: another filing's page is never borrowed
    other = "0000000000-00-000001"
    assert proven_locator(other, "CF", None, "InterestPaid", _idx(), look) == (
        other,
        "",
        "note_fact_report_not_stored",
    )
    # a statement line still wins over the lookup
    assert proven_locator(A, "BS", 9, "AssetsCurrent", _idx(), look)[2] == "proof_line"


def test_scan_pre_keeps_only_wanted_pairs_and_lookup_roundtrip(tmp_path):
    import csv
    import subprocess

    from scrooner_pipeline.mapper import note_report_lookup as nl

    d = tmp_path / "2024q1"
    d.mkdir()
    tsv = d / "2024q1_pre.tsv"
    tsv.write_text(
        "adsh\treport\tline\tstmt\tinpth\ttag\tversion\tprole\tplabel\tnegating\n"
        "A-1\t53\t4\t\t0\tInterestPaid\tus-gaap/2023\tterseLabel\tInterest paid\t0\n"
        "A-1\t60\t2\t\t0\tInterestPaid\tus-gaap/2023\tterseLabel\tInterest paid\t0\n"
        "A-1\t4\t2\tBS\t0\tAssets\tus-gaap/2023\tterseLabel\tAssets\t0\n"
        "B-2\t7\t1\t\t0\tInterestPaid\tus-gaap/2023\tterseLabel\tx\t0\n"
    )
    subprocess.run(["zstd", "-q", "--rm", str(tsv)], check=True)
    got = nl.scan_pre(d / "2024q1_pre.tsv.zst", {("A-1", "InterestPaid")})
    assert list(got) == [("A-1", "InterestPaid")]
    assert sorted(r for r, _l, _p in got[("A-1", "InterestPaid")]) == [53, 60]
    rows, missing = nl.build_rows(tmp_path, {("A-1", "InterestPaid"), ("C-3", "X")})
    assert rows[0]["report"] == 53 and rows[0]["n_reports"] == 2
    assert missing == {("C-3", "X")}
    p = tmp_path / "l.csv"
    with p.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=nl.COLUMNS)
        w.writeheader()
        w.writerows(rows)
    assert nl.load_lookup(p) == {("A-1", "InterestPaid"): 53}


def _checks(tags, note=()):
    return {
        "claim": {"kind": "component", "stmt": "BS", "tags": tags},
        "component_parts": {
            "found": [
                {"tag": t, "sign": 1, "value": f"{i + 1}000000.0000"}
                for i, t in enumerate(tags)
            ],
            "note_facts": list(note),
        },
    }


def test_parts_list_every_part_with_its_own_page_of_the_same_filing_only():
    from scrooner_pipeline.mapper.top100_coverage import parts_locator

    A, B = "0001564590-18-019062", "0001564590-17-014900"
    ch = _checks(
        ["AssetsCurrent", "Assets", "FinanceLeaseLiability"],
        note=["FinanceLeaseLiability"],
    )
    look = {(A, "FinanceLeaseLiability"): 90, (B, "FinanceLeaseLiability"): 7}
    got, blank = parts_locator(ch, A, _idx(), look, None)
    assert got == (
        f"AssetsCurrent=1000000@{A}#R4;Assets=2000000@{A}#R4;"
        f"FinanceLeaseLiability=3000000@{A}#R90"
    )
    assert blank == 0
    # another filing's page is never borrowed: unknown stays blank and is counted
    Z = "0000000000-00-000001"
    got, blank = parts_locator(ch, Z, _idx(), look, None)
    assert got == (
        f"AssetsCurrent=1000000@{Z}#;Assets=2000000@{Z}#;"
        f"FinanceLeaseLiability=3000000@{Z}#"
    )
    assert blank == 3
    # the fix rows' page of the same accession fills a part; a non-component claim lists nothing
    got, _ = parts_locator(_checks(["X"]), "Z", _idx(), None, {"X": 21})
    assert got == "X=1000000@Z#R21"
    assert parts_locator({"claim": {"kind": "concept"}}, A, _idx(), look, None) == (
        "",
        0,
    )


def test_reason_is_evidence_only_from_the_cells_own_period_filing():
    from datetime import date

    from scrooner_pipeline.mapper.top100_coverage import (
        OWN_UNVERIFIED,
        eligible_filings,
        own_period_reason,
    )

    f = [
        (date(2016, 12, 31), "A16"),
        (date(2017, 12, 31), "A17"),
        (date(2018, 12, 31), "A18"),
        (date(2019, 12, 31), "A19"),
    ]
    fy16 = date(2016, 12, 31)
    assert eligible_filings(f, fy16, False) == {
        "A16",
        "A17",
        "A18",
    }  # three printed years
    assert eligible_filings(f, fy16, True) == {
        "A16",
        "A17",
    }  # a balance sheet prints two
    assert own_period_reason("REASON", "not_presented", "A16", f, fy16, False) == (
        "REASON",
        "not_presented",
    )
    assert own_period_reason("REASON", "not_presented", "A19", f, fy16, False) == (
        "UNCHECKED",
        OWN_UNVERIFIED,
    )
    assert own_period_reason("REASON", "x", "", f, fy16, False) == (
        "UNCHECKED",
        OWN_UNVERIFIED,
    )
    assert own_period_reason("PROVEN", None, "A19", f, fy16, False) == ("PROVEN", None)


def test_instance_part_gets_the_r_page_of_the_instance_facts_file():
    from scrooner_pipeline.mapper.top100_coverage import parts_locator

    B = "0001564590-17-014900"
    tag = "CapitalLeaseObligationsCurrent[BalanceSheetLocation=OtherCurrentLiabilities]"
    pages = {(B, tag): "R102.htm"}
    ch = _checks([tag])
    got, blank = parts_locator(ch, B, _idx(), None, None, pages)
    assert got == f"{tag}=1000000@{B}#R102" and blank == 0
    # another filing's page is never used
    got, blank = parts_locator(ch, "0000000000-00-000001", _idx(), None, None, pages)
    assert got.endswith("#") and blank == 1


def test_msft_fy2016_capital_lease_parts_have_r102_from_the_committed_file():
    from scrooner_pipeline.mapper.top100_coverage import instance_part_page

    B = "0001564590-17-014900"
    for t in (
        "CapitalLeaseObligationsCurrent[BalanceSheetLocation=OtherCurrentLiabilities]",
        "CapitalLeaseObligationsNoncurrent[BalanceSheetLocation=OtherNoncurrentLiabilities]",
    ):
        assert instance_part_page(B, t) == "R102.htm"


def test_reason_with_accession_and_no_page_gets_that_filings_balance_sheet_page():
    from scrooner_pipeline.mapper.top100_coverage import (
        LocatorIndex,
        statement_page_fallback,
    )

    A, Z = "0001564590-17-002142", "0000000000-00-000001"
    i = LocatorIndex()
    for ln in range(1, 6):
        i.add(A, 5, ln, "BS", "Assets", "x")
    i.add(A, 6, 1, "PAR", "CommonStockSharesIssued", "p")
    i.add(Z, 9, 1, "BS", "Assets", "x")
    assert statement_page_fallback(A, "PAR", True, i) == (
        "R5.htm",
        "evidence_acc_stmt_page",
    )
    assert statement_page_fallback(A, "PAR", False, i) == ("", "")
    # a filing without the statement stays blank: no other filing's page
    assert statement_page_fallback("0000000000-00-000002", "PAR", True, i) == ("", "")


def test_reason_without_statement_cites_that_filings_income_statement_or_balance_sheet():
    from scrooner_pipeline.mapper.top100_coverage import (
        LocatorIndex,
        statement_page_fallback,
    )

    A = "0001413329-23-000025"
    i = LocatorIndex()
    i.add(A, 3, 1, "IS", "Revenues", "x")
    i.add(A, 6, 1, "BS", "Assets", "x")
    i.add(A, 8, 1, "CF", "NetIncomeLoss", "x")
    # a not_presented duration cell with no statement: the IS page of THAT filing
    assert statement_page_fallback(A, "", False, i) == (
        "R3.htm",
        "evidence_acc_stmt_page",
    )
    # an instant one: the balance sheet
    assert statement_page_fallback(A, "", True, i) == (
        "R6.htm",
        "evidence_acc_stmt_page",
    )
    # a cell whose own statement is known keeps it, never IS
    assert statement_page_fallback(A, "CF", False, i) == (
        "R8.htm",
        "evidence_acc_stmt_page",
    )
    # a filing not in the index stays blank
    assert statement_page_fallback("0000000000-00-000009", "", False, i) == ("", "")


def test_period_no_filing_has_reached_is_not_a_cell():
    """A cover-page instant labelled FY (2026-09-12) after the last 10-K (2025-12-31) is not a cell period."""
    from datetime import date

    from scrooner_pipeline.mapper.top100_coverage import _fy_periods, reached_by_filing

    today = date(2026, 11, 14)
    f = [(date(2024, 12, 31), "A24"), (date(2025, 12, 31), "A25")]
    assert reached_by_filing(date(2025, 12, 31), f, today)
    assert reached_by_filing(date(2023, 12, 31), f, today)
    assert not reached_by_filing(date(2026, 9, 12), f, today)
    assert not reached_by_filing(date(2026, 12, 31), f, today)  # future
    assert reached_by_filing(
        date(2026, 9, 12), None, today
    )  # no filing in the store: unfiltered

    class Conn:
        def execute(self, *_a):
            return self

        def fetchall(self):
            D = date
            return [
                (1, 2025, "instant", D(2025, 12, 31), D(2025, 12, 31)),
                (1, 2026, "instant", D(2026, 9, 12), D(2026, 9, 12)),
                (1, 2025, "duration", D(2025, 1, 1), D(2025, 12, 31)),
            ]

    got = _fy_periods(Conn(), [1], today, {1: f})
    assert set(got) == {(1, 2025, "instant"), (1, 2025, "duration")}
    # without the annual map the stray instant is kept (old behaviour), so the filter is what removes it
    assert (1, 2026, "instant") in _fy_periods(Conn(), [1], today)


def test_derived_counts_when_one_filing_prints_both_served_inputs():
    """C1 same-filing: inputs proven against different shown accessions still count when ONE annual filing prints
    both served values under their tags (ETN gross profit 2017: revenue cited from one 10-K, cost from another)."""
    from scrooner_pipeline.mapper.top100_coverage import DERIVED_FAMILY, resolve_derived

    def run(prints):
        rows = [
            {
                **_row("revenue", acc="B", val="20"),
                "tag": "Revenues",
                "period_end": "2024-12-31",
            },
            {
                **_row("cost_of_revenue", acc="A", val="8"),
                "tag": "CostOfRevenue",
                "period_end": "2024-12-31",
            },
            {
                **_row("gross_profit", cls="UNCHECKED", acc="", fam=DERIVED_FAMILY),
                "tag": "",
                "period_end": "2024-12-31",
            },
        ]
        resolve_derived(rows, prints)
        return rows[2]

    both = {
        (1, "2024-12-31", "Revenues", "20"): {"A", "B"},
        (1, "2024-12-31", "CostOfRevenue", "8"): {"A"},
    }
    r = run(both)
    assert (r["class"], r["accession"]) == ("DERIVED", "A")
    assert r["evidence"] == "revenue=20@A; cost_of_revenue=8@A"
    # no filing prints both
    split = {**both, (1, "2024-12-31", "Revenues", "20"): {"B"}}
    assert run(split)["class"] == "UNCHECKED"
    # a filing prints a different value for the input: not a print of the served value
    assert run({(1, "2024-12-31", "CostOfRevenue", "8"): {"A"}})["class"] == "UNCHECKED"
    assert run(None)["class"] == "UNCHECKED"


def _derived_pair_claim(dp="comprehensive_income", flag="ci_parent_derived"):
    from datetime import date

    from scrooner_pipeline.mapper import structural_loader as sl

    tags = {
        "comprehensive_income": (
            "ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest",
            "ComprehensiveIncomeNetOfTaxAttributableToNoncontrollingInterest",
        ),
        "shares_outstanding": ("CommonStockSharesIssued", "TreasuryStockShares"),
    }[dp]
    return sl.Claim(
        ticker="T",
        cik="0000000001",
        data_point=dp,
        decision="derived_not_printed",
        parts=((1, None, tags[0]), (-1, None, tags[1])),
        stmts=("", ""),
        locs=((4, 22), (4, 23)),
        accession="0000000001-16-000099",
        period_end=date(2015, 12, 31),
        flags=flag,
        node_values=("6328000000", "-3000000"),
    )


def test_direct_derived_evidence_needs_printed_parts_that_sum_to_the_served_value():
    from decimal import Decimal as D

    from scrooner_pipeline.mapper.top100_coverage import direct_derived_evidence

    c = _derived_pair_claim()
    good = [D(6328000000), D(-3000000)]
    text, acc, page = direct_derived_evidence(c, good, "6331000000")
    assert acc == "0000000001-16-000099" and page == "R4"
    assert text == (
        "ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest=6328000000"
        "@0000000001-16-000099#R4;-ComprehensiveIncomeNetOfTaxAttributableToNoncontrollingInterest=-3000000"
        "@0000000001-16-000099#R4"
    )
    assert direct_derived_evidence(c, good, "6330000000") is None  # not the served sum
    assert (
        direct_derived_evidence(c, [D(6328000001), D(-3000000)], "6331000001") is None
    )  # the filing differs from the node
    assert (
        direct_derived_evidence(c, good[:1], "6328000000") is None
    )  # a part is missing


def test_resolve_derived_classifies_a_derived_pair_as_derived_with_parts_and_page():
    from scrooner_pipeline.mapper.top100_coverage import (
        DERIVED_FAMILY,
        resolve_derived,
    )

    def run(direct):
        r = {
            **_row("comprehensive_income", cls="UNCHECKED", acc="", fam=DERIVED_FAMILY),
            "period_end": "2015-12-31",
            "parts": "",
            "r_page": "",
        }
        resolve_derived([r], None, direct)
        return r

    ev = ("A=1@acc#R4;-B=2@acc#R4", "acc", "R4")
    r = run({(1, "comprehensive_income", "2015-12-31"): ev})
    assert (r["class"], r["reason_code"]) == ("DERIVED", "derived_not_printed")
    assert r["parts"] == ev[0] and r["accession"] == "acc" and r["r_page"] == "R4"
    # no verified parts (cross-filing, missing, wrong sum): never DERIVED
    assert run({})["class"] == "UNCHECKED"
    assert run(None)["class"] == "UNCHECKED"


def test_fy_period_is_anchored_to_the_annual_filing_not_the_latest_end():
    """PG FY2024 -> 2024-06-30, MU FY2023 -> 2023-08-31, MU FY2026 balance sheet -> 2026-09-03 (Dhairya 2026-11-21:
    78 open cells were keyed to a stray later period). MU is a 52/53-week filer: its filings' period says 08-31."""
    from datetime import date

    from scrooner_pipeline.mapper.top100_coverage import pick_fy_period

    D = date
    pg = [(D(2023, 6, 30), "a"), (D(2024, 6, 30), "b"), (D(2025, 6, 30), "c")]
    mu = [(D(2023, 8, 31), "a"), (D(2024, 8, 31), "b"), (D(2026, 8, 31), "c")]
    assert pick_fy_period(
        [(D(2023, 7, 1), D(2024, 6, 30)), (D(2023, 10, 1), D(2024, 9, 30))], pg
    )[1] == D(2024, 6, 30)
    assert pick_fy_period(
        [(D(2022, 9, 2), D(2023, 8, 31)), (D(2023, 1, 1), D(2023, 12, 31))], mu
    )[1] == D(2023, 8, 31)
    assert pick_fy_period(
        [(D(2026, 9, 3), D(2026, 9, 3)), (D(2026, 9, 12), D(2026, 9, 12))], mu
    )[1] == D(2026, 9, 3)
    assert pick_fy_period([(D(2023, 9, 1), D(2024, 8, 29))], mu, weekly=True)[1] == D(
        2024, 8, 29
    ), "52/53-week end matches 08-31"
    # Deere (52/53 weeks; its 10-Ks say 10-31): FY2015 ended 2015-11-01, FY2016 ended 2016-10-30 (scrooner-bd, 2026-11-21)
    de = [(D(2015, 10, 31), "a"), (D(2016, 10, 31), "b"), (D(2017, 10, 31), "c")]
    assert pick_fy_period(
        [(D(2014, 11, 1), D(2015, 10, 31)), (D(2014, 11, 3), D(2015, 11, 1))],
        de,
        weekly=True,
    )[1] == D(2015, 11, 1)
    assert pick_fy_period(
        [(D(2015, 11, 1), D(2016, 10, 31)), (D(2015, 11, 2), D(2016, 10, 30))],
        de,
        weekly=True,
    )[1] == D(2016, 10, 30)
    assert pick_fy_period(
        [(D(2016, 10, 31), D(2017, 10, 29)), (D(2017, 1, 1), D(2017, 12, 31))],
        de,
        weekly=True,
    )[1] == D(2017, 10, 29)
    # calendar filers keep their 365/366-day year beside a stray 364-day duplicate (BLK 2019, BAC 2018)
    blk = [(D(2019, 12, 31), "a"), (D(2018, 12, 31), "b")]
    assert pick_fy_period(
        [(D(2019, 1, 1), D(2019, 12, 31)), (D(2019, 1, 2), D(2019, 12, 30))], blk
    )[1] == D(2019, 12, 31)
    assert pick_fy_period(
        [(D(2018, 1, 2), D(2018, 12, 31)), (D(2018, 1, 1), D(2018, 12, 31))], blk
    )[0] == D(2018, 1, 1)
    # no annual filing matches: the latest end, as before
    assert pick_fy_period(
        [(D(2014, 1, 1), D(2014, 12, 31)), (D(2014, 4, 1), D(2015, 3, 31))], pg
    )[1] == D(2015, 3, 31)
    assert pick_fy_period([(D(2014, 1, 1), D(2014, 12, 31))], None)[1] == D(
        2014, 12, 31
    )


def test_fy_instant_is_the_chosen_year_end_mu_fy2026():
    from datetime import date as D

    from scrooner_pipeline.mapper.top100_coverage import _fy_periods

    class Conn:
        def execute(self, *_a):
            return self

        def fetchall(self):
            return [
                (1, 2026, "duration", D(2025, 8, 29), D(2026, 9, 3)),
                (1, 2026, "instant", D(2026, 9, 12), D(2026, 9, 12)),
                (1, 2026, "instant", D(2026, 9, 3), D(2026, 9, 3)),
            ]

    got = _fy_periods(Conn(), [1], D(2026, 11, 21), {1: [(D(2026, 8, 31), "acc")]})
    assert got[(1, 2026, "instant")] == (D(2026, 9, 3), D(2026, 9, 3))
    assert got[(1, 2026, "duration")][1] == D(2026, 9, 3)


def test_fy_periods_votes_the_company_year_style():
    """A 52/53-week filer (single-candidate years of 364 days) takes Deere's real FY2016 end; a calendar filer keeps 12-31."""
    from datetime import date as D

    from scrooner_pipeline.mapper.top100_coverage import _fy_periods

    rows = [
        (1, 2017, "duration", D(2016, 10, 31), D(2017, 10, 29)),
        (1, 2018, "duration", D(2017, 10, 30), D(2018, 10, 28)),
        (1, 2016, "duration", D(2015, 11, 1), D(2016, 10, 31)),
        (1, 2016, "duration", D(2015, 11, 2), D(2016, 10, 30)),
        (2, 2018, "duration", D(2018, 1, 1), D(2018, 12, 31)),
        (2, 2019, "duration", D(2019, 1, 1), D(2019, 12, 31)),
        (2, 2019, "duration", D(2019, 1, 2), D(2019, 12, 30)),
    ]

    class Conn:
        def execute(self, *_a):
            return self

        def fetchall(self):
            return rows

    ann = {
        1: [(D(y, 10, 31), "a") for y in (2016, 2017, 2018)],
        2: [(D(y, 12, 31), "b") for y in (2018, 2019)],
    }
    got = _fy_periods(Conn(), [1, 2], D(2026, 11, 21), ann)
    assert got[(1, 2016, "duration")][1] == D(2016, 10, 30)
    assert got[(2, 2019, "duration")][1] == D(2019, 12, 31)
