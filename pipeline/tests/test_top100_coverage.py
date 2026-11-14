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
                    return [("A", 4, 9, "BS", "AssetsCurrent", "Total current assets")]

            return C()

    idx = _locator_index(Conn(), {"A", ""}, {"AssetsCurrent"})
    assert idx.line[("A", "BS", 9)] == 4


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
