"""The proof accepts a cell equal to the filing's PRINTED line when the filer's XBRL is wrong or missing
(data-team/tags/line_map/rules/filer_xbrl_errors.csv and fsn_dropped_facts.csv). Pure."""

from __future__ import annotations

from decimal import Decimal

import pytest

from scrooner_pipeline.common import filer_xbrl_errors as fxe
from scrooner_pipeline.common import fsn_dropped_facts as fdf
from scrooner_pipeline.proof import prove as pv
from scrooner_pipeline.proof.fsn import NumValue
from scrooner_pipeline.proof.fsn_db import apply_filer_corrections
from tests.unit.test_cell_proof import ADSH, DDATE, shown, structure

NI = "NetIncomeLoss"
PRINTED = "112010000000"


def _fx(tmp_path, monkeypatch, row):
    p = tmp_path / "fx.csv"
    p.write_text("accession,tag,qtrs,xbrl_value,printed_value,evidence\n" + row)
    monkeypatch.setattr(fxe, "CSV_PATH", p)
    fxe._load.cache_clear()


def _fd(tmp_path, monkeypatch, rows=""):
    p = tmp_path / "fd.csv"
    p.write_text("accession,tag,qtrs,segment,value,evidence\n" + rows)
    monkeypatch.setattr(fdf, "CSV_PATH", p)
    fdf._load.cache_clear()


def _prove(s):
    return pv.prove_cell(shown("net_income_resolved", PRINTED, tags=(NI,)), s, "2025q4")


@pytest.mark.unit
def test_sign_error_in_the_filers_xbrl_is_proven_against_the_printed_line(
    tmp_path, monkeypatch
):
    s = structure()
    s.num[(NI, DDATE, 4)] = [
        NumValue(NI, "us-gaap/2025", DDATE, 4, "USD", Decimal("-" + PRINTED), -6)
    ]
    _fd(tmp_path, monkeypatch)
    _fx(
        tmp_path,
        monkeypatch,
        f'{ADSH},{NI},4,-{PRINTED},{PRINTED},"R4.htm prints 112,010"\n',
    )
    assert (
        _prove(s).verdict == pv.DISAGREE
    )  # without applying the correction the stored sign is wrong
    apply_filer_corrections(s)
    p = _prove(s)
    assert p.verdict == pv.PROVEN
    assert (
        p.checks["filer_xbrl_correction"]["corrections"][0]["evidence"]
        == "R4.htm prints 112,010"
    )


@pytest.mark.unit
def test_untagged_fact_is_supplied_and_proven(tmp_path, monkeypatch):
    s = structure()
    del s.num[(NI, DDATE, 4)]
    _fd(tmp_path, monkeypatch)
    _fx(
        tmp_path,
        monkeypatch,
        f'{ADSH},{NI},4,,{PRINTED},"R4.htm prints 112,010; XBRL omits it"\n',
    )
    assert _prove(s).verdict != pv.PROVEN
    apply_filer_corrections(s)
    p = _prove(s)
    assert p.verdict == pv.PROVEN and "filer_xbrl_correction" in p.checks


@pytest.mark.unit
def test_a_wrong_shown_value_still_disagrees_after_the_correction(
    tmp_path, monkeypatch
):
    s = structure()
    s.num[(NI, DDATE, 4)] = [
        NumValue(NI, "us-gaap/2025", DDATE, 4, "USD", Decimal("-" + PRINTED), -6)
    ]
    _fd(tmp_path, monkeypatch)
    _fx(tmp_path, monkeypatch, f'{ADSH},{NI},4,-{PRINTED},{PRINTED},"R4.htm"\n')
    apply_filer_corrections(s)
    p = pv.prove_cell(
        shown("net_income_resolved", "-" + PRINTED, tags=(NI,)), s, "2025q4"
    )
    assert p.verdict == pv.DISAGREE


@pytest.mark.unit
def test_dropped_member_fact_is_read_as_stored(tmp_path, monkeypatch):
    s = structure()
    _fx(tmp_path, monkeypatch, "")
    _fd(
        tmp_path,
        monkeypatch,
        f'{ADSH},AmortizationOfIntangibleAssets,4,IncomeStatementLocation=CostOfSales;,58000000,"R60 line 3"\n',
    )
    apply_filer_corrections(s)
    v = s.dim_num[
        (
            "AmortizationOfIntangibleAssets",
            DDATE,
            4,
            "IncomeStatementLocation=CostOfSales;",
        )
    ]
    assert v[0].value == Decimal(58000000)
    # the store caught up: a stored member fact is never overwritten
    s2 = structure()
    s2.dim_num[
        (
            "AmortizationOfIntangibleAssets",
            DDATE,
            4,
            "IncomeStatementLocation=CostOfSales;",
        )
    ].append(
        NumValue(
            "AmortizationOfIntangibleAssets",
            "v",
            DDATE,
            4,
            "USD",
            Decimal(58000000),
            -6,
        )
    )
    apply_filer_corrections(s2)
    assert (
        len(
            s2.dim_num[
                (
                    "AmortizationOfIntangibleAssets",
                    DDATE,
                    4,
                    "IncomeStatementLocation=CostOfSales;",
                )
            ]
        )
        == 1
    )
    assert s2.corrections == []
