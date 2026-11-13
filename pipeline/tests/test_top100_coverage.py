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
    assert c(bs="defect", br="held_pending_verifier") == (
        "REASON",
        "held_pending_verifier",
    )
    assert c(bs="not_presented", sv=D(1))[0] == "UNCHECKED"
    assert c(tm="not_presented")[0] == "REASON"


def test_blank_variants():
    assert c(bs="defect", br="not_captured") == ("BLANK", "not_captured")
    assert c(dm="not_presented") == ("BLANK", "docmap_not_presented_not_loaded")
    assert c() == ("BLANK", "no_value_no_reason")
