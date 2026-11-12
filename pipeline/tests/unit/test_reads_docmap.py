"""The document-first reader (pipeline/scripts/reads/docmap.py) reads printed R-page values the way the page prints
them: parentheses are negatives, the title's scale multiplies money and share counts but never per-share amounts, and
a printed value that disagrees with companyfacts for the same accession and period is a mismatch the filing decides."""

import gzip
import importlib.util
import json
import sys
from decimal import Decimal
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "reads" / "docmap.py"


def _mod():
    spec = importlib.util.spec_from_file_location("docmap_script", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = m  # dataclasses resolve annotations through sys.modules
    spec.loader.exec_module(m)
    return m


def test_printed_numbers_and_scales():
    m = _mod()
    assert m.parse_num("(1,234)") == Decimal(-1234)
    assert m.parse_num("$ 3.73") == Decimal("3.73")
    assert m.parse_num("—") is None
    assert m.scales(
        "CONSOLIDATED STATEMENTS OF OPERATIONS - USD ($) shares in Millions, $ in Millions"
    ) == (10**6, 10**6)
    assert m.scales("BALANCE SHEETS - USD ($) $ in Thousands") == (10**3, 1)
    assert m.scales(
        "STATEMENTS OF INCOME - USD ($) In Millions, except Per Share data"
    ) == (10**6, 10**6)
    assert m.scales(
        "STATEMENTS OF INCOME - USD ($) In Thousands, except Share data"
    ) == (10**3, 1)


def _row(elem, label, a, b):
    return (
        f"<tr><td class='pl'><a onclick=\"top.Show.showAR( this, 'defref_{elem}', window );\">{label}</a></td>"
        f"<td class='nump'>{a}</td><td class='nump'>{b}</td></tr>"
    )


def test_a_company_read_against_companyfacts(tmp_path):
    m = _mod()
    acc = "0000000001-26-000001"
    d = tmp_path / "0000000001" / acc
    d.mkdir(parents=True)
    (d / "FilingSummary.xml").write_text(
        "<FilingSummary><MyReports><Report><HtmlFileName>R2.htm</HtmlFileName>"
        "<LongName>0000002 - Statement - CONSOLIDATED STATEMENTS OF OPERATIONS</LongName><ShortName>x</ShortName>"
        "<MenuCategory>Statements</MenuCategory></Report></MyReports></FilingSummary>"
    )
    (d / "R2.htm").write_text(
        "<table class='report'><tr><th class='tl' rowspan='2'>STATEMENTS OF OPERATIONS - USD ($) $ in Millions</th>"
        "<th class='th' colspan='2'>12 Months Ended</th></tr><tr><th>Dec. 31, 2025</th><th>Dec. 31, 2024</th></tr>"
        + _row("us-gaap_Revenues", "Total revenues", "$ 1,000", "$ 900")
        + _row("us-gaap_InterestExpense", "Interest expense", "(20)", "(25)")
        + _row("us-gaap_NetIncomeLoss", "Net income", "$ 300", "$ 250")
        + _row("us-gaap_EarningsPerShareBasic", "Basic", "$ 3.00", "$ 2.50")
        + "</table>"
    )

    def f(val, end):
        return {
            "start": f"{end[:4]}-01-01",
            "end": end,
            "val": val,
            "accn": acc,
            "form": "10-K",
            "filed": "2026-02-01",
        }

    facts = {
        "facts": {
            "us-gaap": {
                "Revenues": {
                    "units": {
                        "USD": [f(1000000000, "2025-12-31"), f(900000000, "2024-12-31")]
                    }
                },
                "InterestExpense": {
                    "units": {
                        "USD": [f(20000000, "2025-12-31"), f(25000000, "2024-12-31")]
                    }
                },
                "NetIncomeLoss": {
                    "units": {
                        "USD": [f(301000000, "2025-12-31"), f(250000000, "2024-12-31")]
                    }
                },
                "EarningsPerShareBasic": {
                    "units": {
                        "USD/shares": [f(3.0, "2025-12-31"), f(2.5, "2024-12-31")]
                    }
                },
            }
        }
    }
    (tmp_path / "0000000001" / "companyfacts.json.gz").write_bytes(
        gzip.compress(json.dumps(facts).encode())
    )
    res = m.read_company(tmp_path, "0000000001", "TST", acc, "2026-02-01")
    rows = {r["data_point"]: r for r in res["rows"]}
    assert (rows["revenue"]["fy0_printed"], rows["revenue"]["match"]) == (
        "1000000000",
        "Y",
    )
    assert rows["interest_expense"]["fy0_printed"] == "-20000000"
    assert rows["interest_expense"]["match"].startswith("Y (sign differs")
    assert (rows["basic_eps"]["fy0_printed"], rows["basic_eps"]["match"]) == ("3", "Y")
    assert rows["net_income"]["match"].startswith("FY0 N")
    assert "the filing value stands" in rows["net_income"]["note"]
    assert rows["gross_profit"]["status"] == "not_presented"
