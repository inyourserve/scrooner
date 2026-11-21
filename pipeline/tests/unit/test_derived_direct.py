"""Derived_not_printed serving of shares_outstanding (issued - treasury) and comprehensive_income (total incl. NCI -
NCI), Dhairya's revised ruling 2026-11-16 (RULEBOOK X60/X67). Same filing and column only. Pure tests read a resolver
CSV through the loader; the DB test proves a part stored only in ANOTHER filing is never used. Mutation-checked."""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal

import psycopg
import pytest

from scrooner_pipeline.mapper import structural_direct as sd
from scrooner_pipeline.mapper import structural_loader as sl

CIK = "0000000301"
ACC = "0000000301-19-000001"
HEAD = "cik,ticker,data_point,period_end,grain,decision,nodes,value,accession,column,calc_check,flags,resolver_version\n"
SH_NODES = (
    "CommonStockSharesIssued=2442676580 [R3.htm:5]; -TreasuryStockShares=527460237 [R3.htm:6]"
    " | why: BS parenthetical"
)
CI_NODES = (
    "ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest=6328000000 [R4.htm:22];"
    " -ComprehensiveIncomeNetOfTaxAttributableToNoncontrollingInterest=-3000000 [R4.htm:23] | why: CI statement"
)


def _csv(tmp_path, dp, nodes, value, flags, grain="I", end="2018-12-31", acc=ACC):
    p = tmp_path / "resolver-all110-2026-11-14.csv"
    p.write_text(
        HEAD
        + f'{CIK},TST,{dp},{end},{grain},derived_not_printed,"{nodes}",{value},{acc},own,calc A: ok,{flags},r.1\n'
    )
    return p


def _claim(tmp_path, *a, **kw):
    claims, rejects, counts = sl.read_claims(_csv(tmp_path, *a, **kw))
    return claims, rejects, counts


def _direct(c):
    """The claim as structural_direct holds it (what _claims_by_cik builds)."""
    return replace(
        c, decision="derived_not_printed", parts=c.derived_parts, locs=c.derived_locs
    )


def test_shares_issued_less_treasury_is_derived_with_signed_parts_as_evidence(tmp_path):
    claims, rejects, counts = _claim(
        tmp_path,
        "shares_outstanding",
        SH_NODES,
        1915216343,
        "roles;derived_issued_less_treasury",
    )
    (c,) = claims
    assert not rejects and counts["derived_loaded_as_not_presented"] == 1
    assert (
        c.decision == "not_presented"
    )  # the loader keeps the map statement; the value is never loaded there
    assert sd.derived_claim(c)
    raw = _direct(c)
    v, ev = sd.derived_value(raw, [Decimal(2442676580), Decimal(527460237)])
    assert v == Decimal(1915216343)
    assert ev == (
        f"CommonStockSharesIssued=2442676580@{ACC}#R3;-TreasuryStockShares=527460237@{ACC}#R3"
    )


def test_comprehensive_income_parent_is_total_less_nci_and_a_negative_nci_adds(
    tmp_path,
):
    claims, _r, _c = _claim(
        tmp_path,
        "comprehensive_income",
        CI_NODES,
        6331000000,
        "roles;ci_parent_derived",
        grain="FY",
    )
    assert sd.derived_claim(claims[0])
    raw = _direct(claims[0])
    v, ev = sd.derived_value(raw, [Decimal(6328000000), Decimal(-3000000)])
    assert v == Decimal(6331000000)
    assert ev.endswith(
        f"-ComprehensiveIncomeNetOfTaxAttributableToNoncontrollingInterest=-3000000@{ACC}#R4"
    )
    assert ev.startswith(
        f"ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest=6328000000@{ACC}#R4;"
    )


def test_derivation_needs_its_own_flag_and_the_ruled_pair_only(tmp_path):
    # no flag: the row is not served directly (and the loader keeps skipping it)
    claims, _r, counts = _claim(tmp_path, "shares_outstanding", SH_NODES, 1, "roles")
    assert not claims and counts.get("skipped_derived_not_printed") == 1
    # a data point outside the two rulings never derives, whatever its flag says
    claims, _r, _c = _claim(
        tmp_path, "revenue", SH_NODES, 1, "roles;derived_issued_less_treasury"
    )
    assert not claims
    # wrong pair, three parts, swapped signs, issued <= treasury
    base = sl.read_claims(
        _csv(
            tmp_path, "shares_outstanding", SH_NODES, 1, "derived_issued_less_treasury"
        )
    )[0][0]
    raw = _direct(base)
    swapped = replace(
        raw,
        parts=((-1, None, "CommonStockSharesIssued"), (1, None, "TreasuryStockShares")),
    )
    assert "ruled pair" in sd.derived_problem(swapped)
    other = replace(
        raw,
        parts=(
            (1, None, "CommonStockSharesIssued"),
            (-1, None, "AccountsPayableCurrent"),
        ),
    )
    assert "ruled pair" in sd.derived_problem(other)
    three = replace(raw, parts=raw.parts + raw.parts[:1])
    assert "3 parts" in sd.derived_problem(three)
    assert sd.derived_value(raw, [Decimal(5), Decimal(5)])[0] is None
    assert sd.derived_value(raw, [Decimal(5), Decimal(-1)])[0] is None
    nopage = replace(raw, locs=((None, None), (3, 6)))
    assert "R page" in sd.derived_problem(nopage)


@pytest.mark.integration
def test_cross_filing_parts_are_rejected_same_filing_serves(
    isolated_database_url, tmp_path, monkeypatch
):
    """Issued is stored in the claim's filing, treasury only in ANOTHER filing: nothing is served. Then both in the
    claim's own filing: served as derived_not_printed with the parts in the note and no fact id."""
    acc2 = "0000000301-20-000002"
    end = date(2018, 12, 31)
    with psycopg.connect(isolated_database_url) as conn:

        def one(sql, *a):
            return conn.execute(sql, a).fetchone()[0]

        co = one(
            "insert into core.company (cik, company_name) values (%s,'t') returning id",
            CIK,
        )
        cc = one(
            "insert into analytics.canonical_concept (name, statement, combination_mode) values ('shares_outstanding','balance_sheet','first_match') returning id"
        )
        unit = one("insert into core.unit (unit_name) values ('shares') returning id")
        raw = one(
            "insert into raw.sec_companyfacts (cik, source_url, sha256, storage_path, http_status) values (%s,'u','s','p',200) returning id",
            CIK,
        )
        pid = one(
            "insert into core.period (company_id, start_date, end_date, period_type) values (%s,%s,%s,'instant') returning id",
            co,
            end,
            end,
        )
        fil = {
            a: one(
                "insert into core.filing (company_id, accession_number, form, filing_date, period_of_report) values (%s,%s,'10-K',%s,%s) returning id",
                co,
                a,
                d,
                end,
            )
            for a, d in ((ACC, date(2019, 2, 1)), (acc2, date(2020, 2, 1)))
        }
        tag = {
            t: one(
                "insert into core.concept (taxonomy, tag) values ('us-gaap', %s) returning id",
                t,
            )
            for t in ("CommonStockSharesIssued", "TreasuryStockShares")
        }

        def fact(acc, t, v):
            conn.execute(
                "insert into core.fact (company_id, concept_id, unit_id, period_id, filing_id, value, is_authoritative, raw_object_id) values (%s,%s,%s,%s,%s,%s,false,%s)",
                (co, tag[t], unit, pid, fil[acc], Decimal(v), raw),
            )

        p = _csv(
            tmp_path,
            "shares_outstanding",
            SH_NODES,
            1915216343,
            "roles;derived_issued_less_treasury",
        )
        monkeypatch.setenv(sd.ENV_PATH, str(p))
        sd._claims_by_cik.cache_clear()
        periods = {pid: (end, end, "instant")}
        info = {cc: ("shares_outstanding", "balance_sheet")}

        fact(ACC, "CommonStockSharesIssued", "2442676580")
        fact(acc2, "TreasuryStockShares", "527460237")  # the other filing's copy
        cells, st = sd.direct_cells(conn, co, CIK, [], periods, info)
        assert cells == [] and "no stored fact" in st["rejected"][0]["why"]

        fact(ACC, "TreasuryStockShares", "527460237")
        cells, st = sd.direct_cells(conn, co, CIK, [], periods, info)
        (c,) = cells
        assert (
            c["value"] == Decimal(1915216343)
            and c["value_source"] == "derived_not_printed"
        )
        assert c["source_fact_ids"] == [] and c["_accession"] == ACC
        assert f"-TreasuryStockShares=527460237@{ACC}#R3" in c["serve_note"]
        assert acc2 not in c["serve_note"]


EQ_NODES = (
    "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest=100575000000 [R6.htm:43];"
    " -MinorityInterest=1338000000 [R6.htm:42] | why: parent equity not printed"
)


def test_parent_equity_is_total_equity_less_nci_with_its_flag_only(tmp_path):
    # VZ FY2024 (Dhairya ruling 2026-11-21): stockholders_equity = total equity minus NCI from one filing, derived
    claims, rejects, counts = _claim(
        tmp_path,
        "stockholders_equity",
        EQ_NODES,
        99237000000,
        "core;DERIVED;equity_parent_derived",
    )
    (c,) = claims
    assert not rejects and counts["derived_loaded_as_not_presented"] == 1
    assert sd.derived_claim(c)
    v, ev = sd.derived_value(_direct(c), [Decimal(100575000000), Decimal(1338000000)])
    assert v == Decimal(99237000000)
    assert ev.endswith(f"-MinorityInterest=1338000000@{ACC}#R6")
    # without the flag the derived row is counted, not served
    claims2, _r, counts2 = _claim(
        tmp_path, "stockholders_equity", EQ_NODES, 99237000000, "core;DERIVED"
    )
    assert not claims2 and counts2.get("derived_loaded_as_not_presented", 0) == 0
