"""Instance-sourced component parts (no DDL): a part `Tag[Axis=Member]` that exists only in a filing's XBRL instance
(MSFT FY2016 pre-ASC 842 capital leases, BalanceSheetLocationAxis; the FSN load drops these facts) resolves ONLY to a
row of the committed instance-facts file for that accession and column: loader, mapper, proof, perimeter."""

from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal

import psycopg
import pytest

from scrooner_pipeline.common import instance_facts as inst
from scrooner_pipeline.mapper import company_tag_map as ctm
from scrooner_pipeline.mapper import docmap_loader as dl
from scrooner_pipeline.proof.fsn import FilingStructure, NumValue, PreLine
from scrooner_pipeline.proof.perimeter import REASON, apply_perimeter
from scrooner_pipeline.proof.prove import (
    DISAGREE,
    PROVEN,
    UNCHECKED,
    Claim,
    Proof,
    Shown,
    prove_component,
)

ADSH = "0001564590-17-014900"
END = date(2016, 6, 30)
CUR = "CapitalLeaseObligationsCurrent[BalanceSheetLocation=OtherCurrentLiabilities]"
NONCUR = "CapitalLeaseObligationsNoncurrent[BalanceSheetLocation=OtherNoncurrentLiabilities]"
SPEC_CUR = "us-gaap:CapitalLeaseObligationsCurrent[BalanceSheetLocationAxis=OtherCurrentLiabilitiesMember]"
SPEC_NONCUR = "us-gaap:CapitalLeaseObligationsNoncurrent[BalanceSheetLocationAxis=OtherNoncurrentLiabilitiesMember]"
FACE = ("ShortTermBorrowings", "LongTermDebtCurrent", "LongTermDebtNoncurrent")
M = 1_000_000


# ---- loader -------------------------------------------------------------------------------------------------------
def _fix(tags: str, accession: str = ADSH, period_end: str = "2016-06-30"):
    csv_text = (
        "data_point,fiscal_year,period_end,decision,tags,stmt,accession,r_page,printed_value,note\n"
        f'total_debt,2016,{period_end},component sum,{tags},BS+BS+BS+NOTE+NOTE,{accession},R4.htm+R4.htm+R4.htm+R102.htm+R102.htm,54247000000,n\n'
    )
    return dl.parse_fixes(csv_text, "MSFT-fixes-2026-11-13.csv")


def _all_tags(*extra: str) -> str:
    return "+".join(
        ["us-gaap:ShortTermBorrowings", "us-gaap:LongTermDebtCurrent", "us-gaap:LongTermDebtNoncurrent", *extra]
    )


def test_loader_accepts_an_instance_part_that_resolves_to_the_file_row():
    rows, rejects = _fix(_all_tags(SPEC_CUR, SPEC_NONCUR))
    assert rejects == [] and len(rows) == 1
    assert [t for _s, _x, t in rows[0].parts][-2:] == [CUR, NONCUR]


@pytest.mark.parametrize(
    "tags,accession,end",
    [
        # a member the file has no row for
        (_all_tags("us-gaap:CapitalLeaseObligationsCurrent[BalanceSheetLocationAxis=AccruedLiabilitiesCurrentMember]"), ADSH, "2016-06-30"),
        # a column (period) the file has no row for
        (_all_tags(SPEC_CUR), ADSH, "2015-06-30"),
        # an accession the file has no row for
        (_all_tags(SPEC_CUR), "0001564590-16-662209", "2016-06-30"),
        # a malformed bracket
        (_all_tags("us-gaap:CapitalLeaseObligationsCurrent[BalanceSheetLocationAxis]"), ADSH, "2016-06-30"),
    ],
)
def test_loader_rejects_an_instance_part_that_does_not_resolve(tags, accession, end):
    rows, rejects = _fix(tags, accession, end)
    assert rows == [] and len(rejects) == 1
    assert rejects[0]["why"].startswith(("fix: member_not_supported", "fix: member_syntax"))


def test_docmap_rows_still_reject_any_member_part():
    with pytest.raises(ValueError, match="member_not_supported"):
        dl.parse_parts(SPEC_CUR)  # no (accession, column): never an instance part


def test_fix_row_in_the_msft_file_carries_the_five_parts():
    text = (inst.REPO / "data-team/companies/reads/fixes/MSFT-fixes-2026-11-13.csv").read_text()
    rows, rejects = dl.parse_fixes(text, "MSFT-fixes-2026-11-13.csv")
    assert rejects == []
    (r,) = [x for x in rows if x.data_point == "total_debt" and x.era_to == END]
    assert [t for _s, _x, t in r.parts] == [*FACE, CUR, NONCUR]
    tr = dl.table_rows(r, 4, "0000789019", {"total_debt": "balance_sheet"})
    assert [(x["stmt"], x["evidence_report"]) for x in tr] == [("BS", 4)] * 3 + [("UN", 102)] * 2


# ---- mapper -------------------------------------------------------------------------------------------------------
TD = 187
INFO = {TD: ("total_debt_resolved", "balance_sheet")}


def _fsn_fact(vid, value, tag_instance=""):
    return ctm.Fact(
        Decimal(value), vid, END, False, -5, ADSH, date(2017, 8, 2), source="fsn_xbrl", instance=tag_instance
    )


def _cells(with_instance_facts: bool):
    rows = [
        ctm.MapRow("us-gaap", t, "BS", "component", None, TD, 1, date(2015, 7, 1), END)
        for t in FACE
    ] + [
        ctm.MapRow("us-gaap", CUR, "UN", "component", None, TD, 1, date(2015, 7, 1), END, evidence_report=102),
        ctm.MapRow("us-gaap", NONCUR, "UN", "component", None, TD, 1, date(2015, 7, 1), END, evidence_report=102),
    ]
    facts = {
        ("us-gaap", FACE[0]): {1: _fsn_fact(11, 12904 * M)},
        ("us-gaap", FACE[1]): {1: _fsn_fact(12, 0)},
        ("us-gaap", FACE[2]): {1: _fsn_fact(13, 40557 * M)},
    }
    if with_instance_facts:
        facts[("us-gaap", CUR)] = {1: _fsn_fact(0, 25 * M, f"{ADSH} {CUR} decimals -6")}
        facts[("us-gaap", NONCUR)] = {1: _fsn_fact(0, 761 * M, f"{ADSH} {NONCUR} decimals -6")}
    return ctm.build_cells(rows, facts, INFO, {}, {}, periods={1: (END, END, "instant")})


def test_instance_part_is_summed_with_instance_lineage():
    cells, stats = _cells(True)
    assert stats["held"] == []
    (c,) = cells
    assert c["value"] == Decimal(54247 * M)
    assert c["value_source"] == "fsn_xbrl:instance"
    assert c["source_value_ids"] == [11, 12, 13]  # the instance parts have no fsn.value id
    assert f"instance fact {ADSH} {CUR} decimals -6 R102" in c["serve_note"]
    assert f"instance fact {ADSH} {NONCUR} decimals -6 R102" in c["serve_note"]


def test_missing_instance_fact_holds_the_cell_never_a_partial_sum():
    cells, stats = _cells(False)
    assert cells == [] and stats["held"][0]["reason"] == "component_missing_for_period"


def _fsn_filing_conn(isolated_database_url):
    conn = psycopg.connect(isolated_database_url)
    conn.execute(
        "insert into fsn.filing (accession, cik, form, fsn_set, accepted, period) values (%s,'0000789019','10-K','t',%s,%s)",
        (ADSH, datetime(2017, 8, 2, 16, 15, tzinfo=timezone.utc), date(2017, 6, 30)),
    )
    conn.commit()
    return conn


@pytest.mark.integration
def test_instance_loader_resolves_only_file_rows_of_filings_fsn_holds(isolated_database_url):
    periods = {1: (END, END, "instant"), 2: (date(2016, 7, 1), date(2016, 7, 1), "instant")}  # SEC month-end rounding matches both
    with _fsn_filing_conn(isolated_database_url) as conn:
        got = ctm._load_instance_vintages(conn, {("us-gaap", CUR), ("us-gaap", NONCUR)}, periods)
        (f,) = got[("us-gaap", CUR)][1]
        assert (f.value, f.accession, f.source, f.on_face, f.fact_id) == (Decimal(25 * M), ADSH, "fsn_xbrl", True, 0)
        assert f.instance == f"{ADSH} {CUR} decimals -6" and f.filing_id < 0
        assert got[("us-gaap", NONCUR)][1][0].value == Decimal(761 * M)
        # a tag the file does not hold, or a filing fsn does not hold, gives nothing
        other = "CapitalLeaseObligationsCurrent[BalanceSheetLocation=AccruedLiabilitiesCurrent]"
        assert ctm._load_instance_vintages(conn, {("us-gaap", other)}, periods) == {}
        conn.execute("delete from fsn.filing where accession = %s", (ADSH,))
        assert ctm._load_instance_vintages(conn, {("us-gaap", CUR)}, periods) == {}


# ---- proof --------------------------------------------------------------------------------------------------------
def _structure(face_values: dict[str, int]) -> FilingStructure:
    s = FilingStructure(ADSH, "0000789019", "10-K", date(2017, 8, 2), date(2017, 6, 30))
    for i, (tag, v) in enumerate(face_values.items()):
        s.pre.append(PreLine(4, i, "BS", tag, "us-gaap/2017", tag, False))
        s.num[(tag, END, 0)].append(NumValue(tag, "us-gaap/2017", END, 0, "USD", Decimal(v * M), -6))
    return s


def _shown(value: int, parts: tuple[str, ...]) -> Shown:
    return Shown(
        1, "total_debt_resolved", "I", END, END, Decimal(value * M), FACE, ADSH, (1,),
        claim=Claim("component", "BS", parts=tuple((1, t) for t in parts), part_stmts=("BS",) * 3 + ("UN",) * (len(parts) - 3)),
    )


FACE_VALUES = {"ShortTermBorrowings": 12904, "LongTermDebtCurrent": 0, "LongTermDebtNoncurrent": 40557}


def _prove(value: int, parts, structure=None) -> Proof:
    s = _shown(value, parts)
    return prove_component(s, structure or _structure(FACE_VALUES), Proof(shown=s, verdict=UNCHECKED))


def test_proof_judges_an_instance_part_against_the_file_row():
    p = _prove(54247, (*FACE, CUR, NONCUR))
    assert p.verdict == PROVEN
    found = {f["tag"]: f for f in p.checks["component_parts"]["found"]}
    assert found[CUR]["value"] == str(25 * M) and found[CUR]["source"].startswith("instance:")
    # the shown value must match the file row: a different total is a DISAGREE, not a pass
    assert _prove(54250, (*FACE, CUR, NONCUR)).verdict == DISAGREE


def test_proof_of_an_unknown_instance_part_is_unchecked_not_a_guess():
    other = "CapitalLeaseObligationsCurrent[BalanceSheetLocation=AccruedLiabilitiesCurrent]"
    p = _prove(54247, (*FACE, other, NONCUR))
    assert p.verdict == UNCHECKED and p.checks["component_parts"]["missing"] == [other]


# ---- perimeter ----------------------------------------------------------------------------------------------------
def _perimeter(parts, value, facts=None):
    s = _shown(value, parts)
    p = Proof(s, PROVEN, position_accession=ADSH)
    n = apply_perimeter([p], {ADSH: _structure(FACE_VALUES)}, instance=facts)
    return p, n


def test_perimeter_passes_when_the_located_note_leases_are_in_the_claim():
    p, n = _perimeter((*FACE, CUR, NONCUR), 54247)
    assert (p.verdict, n, p.checks["perimeter"]) == (PROVEN, 0, {"status": "pass"})


def test_perimeter_fails_when_a_located_note_lease_is_left_out():
    p, n = _perimeter(FACE, 53461)  # the pre-fix claim: 12,904 + 0 + 40,557
    assert (p.verdict, p.reason_code, n) == (DISAGREE, REASON, 1)
    assert p.checks["perimeter"]["missing"] == [
        {"tag": CUR, "value": str(25 * M), "kind": "instance_capital_lease"},
        {"tag": NONCUR, "value": str(761 * M), "kind": "instance_capital_lease"},
    ]
    p, n = _perimeter((*FACE, CUR), 54486)  # one of the two named: the other is still owed
    assert [m["tag"] for m in p.checks["perimeter"]["missing"]] == [NONCUR]


def test_perimeter_leaves_a_lease_inside_a_debt_line_or_without_location_alone(tmp_path):
    f = tmp_path / "x.csv"
    f.write_text(
        "cik,adsh,instance,ddate,tag,balance_sheet_location_member,value,decimals\n"
        f"0000789019,{ADSH},m.xml,2016-06-30,CapitalLeaseObligationsCurrent,us-gaap:LongTermDebtMember,25000000,-6\n"
        f"0000789019,{ADSH},m.xml,2016-06-30,CapitalLeaseObligations,,761000000,-6\n"
    )
    facts = inst.load(f)
    p, n = _perimeter(FACE, 53461, facts)
    assert (p.verdict, n) == (PROVEN, 0)  # in debt: not owed; unlocated: never owed here (a reader decides)
