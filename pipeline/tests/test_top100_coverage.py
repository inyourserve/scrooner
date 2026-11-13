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
