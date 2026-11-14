"""reason_evidence (structural_loader) and refuted_map_reasons (structural_direct) with the reads stubbed: the tag set
is the concept's tags plus the company's own value-claim tags; a refused reason is reported, a clean one is not."""

from datetime import date
from decimal import Decimal as D
from types import SimpleNamespace

from scrooner_pipeline.mapper import reason_guard as rg
from scrooner_pipeline.mapper import structural_direct as sd
from scrooner_pipeline.mapper import structural_loader as sl

ACC = "0001413329-17-000014"
CI = "ComprehensiveIncomeNetOfTax"
NCI = "ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest"
END = date(2016, 12, 31)


def claim(**kw):
    base = dict(
        ticker="PM",
        cik="0001413329",
        data_point="comprehensive_income",
        decision="combined",
        parts=(),
        stmts=("",),
        locs=((None, None),),
        accession=ACC,
        period_end=END,
        path=f"{NCI} [R5.htm:13] | why: only the figure including noncontrolling interest is printed",
        grain="FY",
    )
    base.update(kw)
    return sl.Claim(**base)


def stub(monkeypatch, facts):
    monkeypatch.setattr(
        rg, "concept_tags", lambda conn, names: {"comprehensive_income": {CI, NCI}}
    )
    monkeypatch.setattr(
        rg,
        "read_facts",
        lambda conn, cid, pairs: {k: v for k, v in facts.items() if k in pairs},
    )
    monkeypatch.setattr(rg, "read_pages", lambda conn, pairs: {(ACC, CI): 5})


def test_loader_refuses_the_combined_claim_when_the_parent_tag_is_stored(monkeypatch):
    c = claim()
    stub(monkeypatch, {(ACC, CI): [rg.Fact(END, 4, False, "", D("6810000000"))]})
    got = sl.reason_evidence(None, 1, "0001413329", [c], [c], {"comprehensive_income"})
    ev, pages = got[c]
    assert ev[0]["tag"] == CI and ev[0]["value"] == D("6810000000") and pages == {CI: 5}


def test_loader_keeps_the_reason_when_nothing_is_stored(monkeypatch):
    c = claim()
    stub(monkeypatch, {(ACC, NCI): [rg.Fact(END, 4, False, "", D("7043000000"))]})
    assert (
        sl.reason_evidence(None, 1, "0001413329", [c], [c], {"comprehensive_income"})
        == {}
    )


def test_own_value_claim_tags_join_the_concept_tags(monkeypatch):
    c = claim(
        data_point="amortization_of_intangibles",
        decision="not_presented",
        path="no line",
    )
    v = claim(
        data_point="amortization_of_intangibles",
        decision="mapped",
        parts=((1, None, "AmortizationOfIntangibleAssets"),),
        period_end=date(2023, 12, 31),
    )
    monkeypatch.setattr(rg, "concept_tags", lambda conn, names: {})
    seen = {}
    monkeypatch.setattr(
        rg, "read_facts", lambda conn, cid, pairs: seen.setdefault("p", pairs) and {}
    )
    monkeypatch.setattr(rg, "read_pages", lambda conn, pairs: {})
    sl.reason_evidence(
        None, 1, "0001413329", [c], [c, v], {"amortization_of_intangibles"}
    )
    assert seen["p"] == {(ACC, "AmortizationOfIntangibleAssets")}


def test_serving_side_drops_the_refuted_map_reason(monkeypatch):
    row = SimpleNamespace(
        decision="not_in_template",
        reason_class="line_presented_combined",
        canonical_concept_id=7,
        evidence_adsh=ACC,
        era_from=date(2015, 1, 1),
        era_to=None,
        reason=f"combined line: {NCI}",
        evidence_plabel="Total comprehensive earnings",
    )
    monkeypatch.setattr(
        rg, "concept_tags", lambda conn, names: {"comprehensive_income": {CI, NCI}}
    )
    monkeypatch.setattr(
        rg,
        "read_facts",
        lambda conn, cid, pairs: {
            (ACC, CI): [rg.Fact(END, 4, False, "", D("6810000000"))]
        },
    )
    monkeypatch.setattr(sd, "enabled", lambda: False)
    periods = {11: (date(2016, 1, 1), END, "duration")}
    info = {7: ("comprehensive_income", "income_statement")}
    out = sd.refuted_map_reasons(None, 1, "0001413329", [row], periods, info)
    assert [(x["canonical_concept_id"], x["period_id"], x["tag"]) for x in out] == [
        (7, 11, CI)
    ]
    # no evidence stored: the reason is kept
    monkeypatch.setattr(rg, "read_facts", lambda conn, cid, pairs: {})
    assert sd.refuted_map_reasons(None, 1, "0001413329", [row], periods, info) == []
    # apply_direct drops the blank of a refuted key and nothing else
    stats = {
        "blanks": [
            {"canonical_concept_id": 7, "period_id": 11},
            {"canonical_concept_id": 8, "period_id": 11},
        ]
    }
    sd.apply_direct(None, [], stats, [], [{"canonical_concept_id": 7, "period_id": 11}])
    assert stats["blanks"] == [{"canonical_concept_id": 8, "period_id": 11}]
