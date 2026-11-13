"""40-F / 20-F annual reports are annual filings end to end (S6: SHOP filed a 20-F for FY2015 and 40-Fs for
FY2016-FY2023, 0001594805-16-000019 .. 0001594805-24-000007 on sec.gov; its first 10-K is FY2024).

Every form gate between the FSN store and the cell proof must treat them like a 10-K, and only like a 10-K."""

from __future__ import annotations

import re
from datetime import date, datetime
from pathlib import Path

import pytest
from scrooner_pipeline.common.periodic_forms import (
    ANNUAL_FORMS_ALL,
    FOREIGN_PERIODIC_FORMS,
)
from scrooner_pipeline.fsn_store import company_dir, pilot, select as sel
from scrooner_pipeline.proof import prove as pv, shown
from scrooner_pipeline.proof.fsn import FilingStructure, NumValue

SRC = Path(__file__).resolve().parents[2] / "src" / "scrooner_pipeline"


def test_fsn_store_loads_the_foreign_annual_reports():
    assert FOREIGN_PERIODIC_FORMS <= company_dir.PERIODIC_FORMS
    assert set(ANNUAL_FORMS_ALL) <= company_dir.PERIODIC_FORMS
    assert set(FOREIGN_PERIODIC_FORMS) <= set(shown.PERIODIC_FORMS)
    for (
        f
    ) in FOREIGN_PERIODIC_FORMS:  # an annual face: instants and 4-quarter columns only
        assert sel.FACE_QTRS[f] == {0, 4}
        assert sel._form_prints(f, 4) and not sel._form_prints(f, 1)


@pytest.mark.parametrize("form", ["40-F", "40-F/A", "20-F"])
def test_on_statement_face_reads_a_foreign_annual_like_a_10k(form):
    s = FilingStructure(
        "0001594805-18-000009",
        "0001594805",
        form,
        date(2018, 2, 20),
        date(2017, 12, 31),
    )
    year = NumValue("Revenues", "us-gaap/2017", date(2017, 12, 31), 4, "USD", 1, 0)
    quarter = NumValue("Revenues", "us-gaap/2017", date(2017, 12, 31), 1, "USD", 1, 0)
    ok, why = pv.on_statement_face(s, "IS", year)
    assert ok and form.split("/")[0] in why
    ok, _ = pv.on_statement_face(s, "IS", quarter)
    assert not ok  # a quarter value of an annual report is a note value


def test_store_keys_give_a_foreign_annual_its_fy_key():
    f = sel.Filing(
        1,
        "0001594805-18-000009",
        datetime(2018, 2, 20),
        "40-F",
        date(2017, 12, 31),
        2017,
        "FY",
    )
    assert ("FY", date(2017, 12, 31)) in pilot.store_keys([f], "revenue")


def test_era_extend_reads_the_foreign_annual_reports_too():
    """Every SQL form list of era_extend that names the domestic annual forms names the foreign ones as well."""
    src = (SRC / "mapper" / "era_extend.py").read_text()
    lists = re.findall(r"\(('10-K'[^)]*)\)", src)
    assert lists
    for lst in lists:
        assert "'40-F'" in lst and "'20-F'" in lst, lst
