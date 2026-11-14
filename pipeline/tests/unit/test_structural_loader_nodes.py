"""Structural loader, pure parts (no database). Each assertion below fails without its fix (mutation-checked):

- the resolver's `nodes` text: a signed node (`-Tag=v [R2:15]`) and a node whose bracket text holds `;`
  (`FinanceLeaseLiability=1 [NOTE note lease; ...]`) are parsed, not rejected as bad tags;
- years before the first 10-K (accession empty, flag before_first_10k) become no_public_filing_for_period claims, loaded
  only with evidence (no earlier periodic filing);
- a library hold (held_*) does not agree with a structural not_presented; a combined claim is not dropped because the
  library also prints the combined line;
- the one instant component sum with a cited ruling (ap_related_sum)."""

from __future__ import annotations

import csv
from datetime import date
from pathlib import Path

from scrooner_pipeline.mapper import era_predictor
from scrooner_pipeline.mapper import structural_loader as sl
from scrooner_pipeline.mapper import top100_coverage as tc

HEAD = [
    "cik",
    "ticker",
    "data_point",
    "period_end",
    "grain",
    "decision",
    "nodes",
    "value",
    "accession",
    "column",
    "calc_check",
    "flags",
    "resolver_version",
]


def _write(tmp_path: Path, *rows: dict) -> Path:
    p = tmp_path / "resolver-all110-2026-11-14.csv"
    with p.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=HEAD)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in HEAD})
    return p


def _row(**kw) -> dict:
    base = {
        "cik": "0000000301",
        "ticker": "TST",
        "data_point": "operating_expenses",
        "period_end": "2018-12-31",
        "grain": "FY",
        "decision": "component_sum",
        "accession": "0000000301-19-000001",
        "column": "own",
        "calc_check": "calc A: ok",
        "flags": "core",
        "resolver_version": "r.1",
    }
    base.update(kw)
    return base


def test_split_nodes_keeps_semicolons_inside_brackets():
    left = (
        "ShortTermBorrowings=5089000000.0000 [BS R5:30 debt-role tag]; "
        "FinanceLeaseLiability=1000000000.0000 [NOTE note lease; no ExtensibleList and no debt line "
        "contains it (location by absence: CHECK)] "
    )
    assert sl.split_nodes(left) == [
        "ShortTermBorrowings=5089000000.0000 [BS R5:30 debt-role tag]",
        "FinanceLeaseLiability=1000000000.0000 [NOTE note lease; no ExtensibleList and no debt line "
        "contains it (location by absence: CHECK)]",
    ]


def test_signed_node_and_lease_note_node_become_parts(tmp_path: Path):
    nodes = (
        "-GainLossOnDispositionOfAssets=75000000.0000 [R2:15]; "
        "GeneralAndAdministrativeExpense=4567000000.0000 [R2:13]; "
        "FinanceLeaseLiability=1000000000.0000 [NOTE note lease; location by absence: CHECK] "
        "| why: IS: -sum(weight x value)"
    )
    p = _write(tmp_path, _row(nodes=nodes, value="1"))
    claims, rejects, _ = sl.read_claims(p)
    assert rejects == []
    (c,) = claims
    assert [(sg, t) for sg, _x, t in c.parts] == [
        (-1, "GainLossOnDispositionOfAssets"),
        (1, "GeneralAndAdministrativeExpense"),
        (1, "FinanceLeaseLiability"),
    ]
    assert c.node_values == ("75000000.0000", "4567000000.0000", "1000000000.0000")


def test_member_part_is_rejected_with_its_own_reason(tmp_path: Path):
    nodes = "CostOfGoodsAndServicesSold[Product]=9682000000 [IS face line] | why: x"
    claims, rejects, _ = sl.read_claims(_write(tmp_path, _row(nodes=nodes, value="1")))
    assert claims == [] and [r["why"] for r in rejects] == ["member_not_supported"]


FIRST = "0001193125-21-060650"
WHY = (
    "| why: no 10-K covers this year: it is before the company's first 10-K "
    f"({FIRST}), and that 10-K's FY-1 column does not print the line"
)


def test_year_before_the_first_10k_is_a_no_filing_claim(tmp_path: Path):
    p = _write(
        tmp_path,
        _row(
            decision="not_presented",
            nodes=" " + WHY,
            accession="",
            flags="before_first_10k;before_first_10k",
        ),
    )
    claims, rejects, _ = sl.read_claims(p)
    assert rejects == []
    (c,) = claims
    assert c.no_filing and c.accession == FIRST and c.decision == "not_presented"
    rows = sl.build_rows(
        c,
        date(2019, 1, 1),
        date(2019, 12, 31),
        1,
        "0000000301",
        "operating_expenses",
        {"operating_expenses": "income_statement"},
        {},
    )
    (r,) = rows
    assert r["decision"] == "not_presented"
    assert r["reason_class"] == "no_public_filing_for_period"


def test_empty_accession_without_the_flag_or_the_first_10k_is_rejected(tmp_path: Path):
    p = _write(
        tmp_path,
        _row(decision="not_presented", nodes=" " + WHY, accession="", flags="core"),
        _row(
            decision="not_presented",
            nodes=" | why: no 10-K covers this year",
            accession="",
            flags="before_first_10k",
            period_end="2019-12-31",
        ),
    )
    claims, rejects, _ = sl.read_claims(p)
    assert claims == []
    assert [r["why"] for r in rejects] == [
        "accession is not an SEC accession number",
        "before_first_10k row names no first 10-K accession",
    ]


def test_no_filing_evidence_needs_no_earlier_periodic_filing():
    pe = date(2019, 12, 31)
    assert sl.no_filing_evidence(pe, date(2021, 3, 1), date(2021, 3, 1)) is None
    assert (
        sl.no_filing_evidence(pe, None, None) is not None
    )  # nothing stored: cannot show it
    assert (
        sl.no_filing_evidence(pe, date(2019, 12, 31), None) is not None
    )  # on the period end
    assert (
        sl.no_filing_evidence(pe, date(2019, 5, 1), None) is not None
    )  # an earlier 10-Q exists
    assert (
        sl.no_filing_evidence(pe, date(2021, 3, 1), date(2019, 6, 1)) is not None
    )  # named 10-K is early


def test_constants_agree_across_modules():
    assert (
        sl.NO_FILING_REASON
        == era_predictor.NO_FILING_REASON
        == tc.NO_FILING
        == "no_public_filing_for_period"
    )
    assert sl.PERIODIC_FORMS == tc.PERIODIC_FORMS
    from scrooner_pipeline.mapper import company_tag_map as ctm

    assert set(sl.STANDARD_TAXONOMIES_LOCAL) == ctm.STANDARD_TAXONOMIES


def test_coverage_keeps_a_no_filing_reason_only_with_evidence():
    pe = date(2019, 12, 31)
    keep = tc.own_period_reason(
        "REASON", tc.NO_FILING, "0001193125-21-060650", [], pe, False, date(2021, 3, 1)
    )
    assert keep == ("REASON", tc.NO_FILING)
    for earliest in (None, date(2019, 12, 31), date(2018, 5, 1)):
        assert tc.own_period_reason(
            "REASON", tc.NO_FILING, "x", [], pe, False, earliest
        ) == (
            "UNCHECKED",
            tc.OWN_UNVERIFIED,
        )
    # other reasons keep the own-period rule
    assert tc.own_period_reason(
        "REASON", "not_presented", "x", [], pe, False, date(2021, 3, 1)
    ) == (
        "UNCHECKED",
        tc.OWN_UNVERIFIED,
    )


def _claim(decision="not_presented", flags="", dp="operating_expenses", **kw):
    return sl.Claim(
        ticker="TST",
        cik="0000000301",
        data_point=dp,
        decision=decision,
        parts=(),
        stmts=("IS",),
        locs=((2, 11),),
        accession="0000000301-19-000001",
        period_end=date(2018, 12, 31),
        flags=flags,
        **kw,
    )


def test_instant_sum_ruling_is_narrow():
    c = _claim("component_sum", flags="bs_family;face;ap_related_sum")
    assert not sl.instant_sum_refused_for(
        c, "accounts_payable_resolved", "balance_sheet"
    )
    assert sl.instant_sum_refused_for(
        c, "inventory", "balance_sheet"
    )  # the ruling names accounts payable
    assert sl.instant_sum_refused_for(
        _claim("component_sum", flags="core"), "accounts_payable", "balance_sheet"
    )
    assert not sl.instant_sum_refused_for(
        _claim("component_sum"), "operating_expenses", "income_statement"
    )


def _lib(
    decision,
    reason_class,
    rule="tagmap.fy_status@1",
    era=(date(2018, 12, 31), date(2018, 12, 31)),
    **kw,
):
    return {
        "id": kw.pop("id", 1),
        "rule_id": rule,
        "decided_by": "t",
        "era_from": era[0],
        "era_to": era[1],
        "canonical_concept_id": kw.pop("concept", 7),
        "parent_concept_id": None,
        "decision": decision,
        "taxonomy": None,
        "tag": None,
        "sign": 1,
        "components": kw.pop("components", None),
        "reason_class": reason_class,
        **kw,
    }


def _plan(claim, existing, names=None):
    rows = sl.build_rows(
        claim,
        date(2018, 1, 1),
        date(2018, 12, 31),
        1,
        "0000000301",
        claim.data_point,
        {claim.data_point: "income_statement"},
        {},
    )
    rows = [sl.normalize(r, {}, {claim.data_point: 7}, sl.RULE_ID, []) for r in rows]
    return sl.plan_company(
        existing,
        [(claim, date(2018, 1, 1), date(2018, 12, 31), rows)],
        names or {7: claim.data_point},
    )


def test_structural_not_presented_replaces_a_library_hold_instead_of_agreeing():
    hold = _lib("not_presented", "held_c6")
    plan = _plan(_claim("not_presented"), [hold])
    # the structural reason covers the whole year, the hold's day is clipped away (not left standing as 'agree')
    assert plan.agree == 0
    assert [r["era_from"] for r in plan.inserts if r["rule_id"] == sl.RULE_ID] == [
        date(2018, 1, 1)
    ]
    assert [r["era_to"] for r in plan.inserts if r["rule_id"] == sl.RULE_ID] == [
        date(2018, 12, 31)
    ]
    assert 1 in plan.deletes


def test_structural_not_presented_still_agrees_with_a_plain_library_not_presented():
    plan = _plan(_claim("not_presented"), [_lib("not_presented", "off_statement")])
    assert plan.agree == 1


def test_combined_claim_is_not_dropped_by_a_library_combined_line():
    combined_line = _lib(
        "combined",
        "line_presented_combined_with_others",
        rule="company_tag_map.library@1",
        era=(date(2015, 3, 31), date(2026, 6, 30)),
        concept=None,
        components=["operating_expenses", "interest_income"],
    )
    plan = _plan(_claim("combined"), [combined_line])
    assert plan.dropped == 0 and plan.reason_cells == 1
    # a non-combined claim is still left to the Tag Expert
    plan2 = _plan(_claim("not_presented"), [combined_line])
    assert plan2.dropped == 1


class _Cur:
    def __init__(self, answers):
        self.answers, self.rows = answers, []

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def execute(self, sql, params=None):
        for key, rows in self.answers.items():
            if key in sql:
                self.rows = rows
                return
        raise AssertionError(f"unexpected query: {sql[:80]}")

    def fetchall(self):
        return self.rows


class _Conn:
    def __init__(self, answers):
        self.answers = answers

    def cursor(self):
        return _Cur(self.answers)


def test_extension_tag_takes_the_company_prefix_only_when_the_store_knows_it_custom():
    conn = _Conn(
        {
            "from analytics.company_sec_tag": [],
            "from core.concept": [("Known", ["us-gaap"])],
            "from fsn.tag": [("MarketingAdministrationAndResearchCosts",)],
            "from core.company": [(5, "mcd")],
            "from analytics.company_tag_map": [],
        }
    )
    out, _ = sl.taxonomies(
        conn, {5}, {"Known", "MarketingAdministrationAndResearchCosts", "TypoTag"}
    )
    assert out[5] == {
        "Known": "us-gaap",
        "MarketingAdministrationAndResearchCosts": "mcd",
    }  # TypoTag is not custom in the store: left out, its row is rejected alone
    # the company's own existing extension prefix wins over the ticker
    conn.answers["from analytics.company_tag_map"] = [(5, ["mcdonalds"])]
    out, _ = sl.taxonomies(conn, {5}, {"MarketingAdministrationAndResearchCosts"})
    assert out[5]["MarketingAdministrationAndResearchCosts"] == "mcdonalds"
