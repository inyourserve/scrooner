"""Direct serving honours the filer XBRL corrections (common/filer_xbrl_errors). DB-backed (CI: Postgres 16)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import psycopg
import pytest

from scrooner_pipeline.common import filer_xbrl_errors as fxe
from tests.unit.test_structural_direct import ACC1, END, W, _csv, _row  # noqa: F401


def _fix_csv(tmp_path, monkeypatch, acc, xbrl, printed, tag="InvestmentIncomeNet"):
    p = tmp_path / "filer_xbrl_errors.csv"
    p.write_text(
        "accession,tag,qtrs,xbrl_value,printed_value,evidence\n"
        f'{acc},{tag},4,{xbrl},{printed},"R4.htm prints {printed}"\n'
    )
    monkeypatch.setattr(fxe, "CSV_PATH", p)
    fxe._load.cache_clear()


OTHER = "0000000999-00-000000"


@pytest.mark.integration
def test_correction_serves_the_printed_value(
    isolated_database_url, tmp_path, monkeypatch
):
    """A wrong-sign stored fact: the resolver node prints 1234, the stored fact is -1234. Without the CSV row the claim
    is rejected; with it the cell serves 1234 as filer_xbrl_correction and the note carries the evidence."""
    with psycopg.connect(isolated_database_url) as conn:
        w = W(conn)
        w.filing(ACC1, date(2019, 2, 1), END)
        w.core_fact(ACC1, "InvestmentIncomeNet", "-1234")
        _csv(tmp_path, _row(ACC1, "1234"), monkeypatch=monkeypatch)
        _fix_csv(tmp_path, monkeypatch, OTHER, "-1", "1")
        cells, st = w.cells()
        assert cells == []
        assert "differs from the resolver node" in st["rejected"][0]["why"]
        _fix_csv(tmp_path, monkeypatch, ACC1, "-1234", "1234")
        (c,), st = w.cells()
        assert (c["value"], c["value_source"]) == (
            Decimal(1234),
            "filer_xbrl_correction",
        )
        assert c["source_fact_ids"] == [] and c["source_value_ids"] == []
        assert "R4.htm prints 1234" in c["serve_note"]
        assert "filer_xbrl_correction" in c["serve_note"]
        # a stored value that is neither the CSV xbrl_value nor the printed one rejects: the CSV is stale
        _fix_csv(tmp_path, monkeypatch, ACC1, "-99", "1234")
        cells, st = w.cells()
        assert cells == [] and "neither the CSV xbrl_value" in st["rejected"][0]["why"]


@pytest.mark.integration
def test_correction_supplies_an_untagged_fact(
    isolated_database_url, tmp_path, monkeypatch
):
    with psycopg.connect(isolated_database_url) as conn:
        w = W(conn)
        w.filing(ACC1, date(2019, 2, 1), END)  # no stored fact for the column at all
        _csv(tmp_path, _row(ACC1, "1234"), monkeypatch=monkeypatch)
        _fix_csv(tmp_path, monkeypatch, OTHER, "-1", "1")
        cells, _ = w.cells()
        assert cells == []
        _fix_csv(tmp_path, monkeypatch, ACC1, "", "1234")
        (c,), _ = w.cells()
        assert (c["value"], c["value_source"]) == (
            Decimal(1234),
            "filer_xbrl_correction",
        )
