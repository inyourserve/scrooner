"""Per-year status rows FY2015 to latest, each decided on that year's own 10-K (fy_era_status.py)."""

import csv
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "tag_library" / "fy_era_status.py"
MAP_COLS = ["company_id", "cik", "taxonomy", "tag", "stmt", "decision", "canonical_concept", "parent_concept", "combine_sign",
            "components", "reason_class", "reason", "era_from", "era_to", "evidence_adsh", "evidence_report", "evidence_line",
            "evidence_plabel", "evidence_cal_parent", "decided_by", "rule_id", "rank", "ticker", "lines", "filings", "value_source"]


def _w(path, cols, rows):
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in cols})


def _map_row(**kw):
    r = {"company_id": "7", "cik": "1", "ticker": "XYZ", "rank": "9", "decided_by": "library"}
    r.update(kw)
    return r


BASE_MAP = [
    _map_row(tag="AmortizationOfIntangibleAssets", stmt="CF", decision="concept", canonical_concept="amortization_of_intangibles",
             era_from="2015-01-01", era_to="2016-12-31", company_id="8", ticker="OTH"),
    _map_row(tag="AccountsPayableAndAccruedLiabilitiesCurrent", stmt="BS", decision="combined", components="accounts_payable;accrued_liabilities",
             era_from="2015-01-01", era_to="2026-12-31", company_id="8", ticker="OTH"),
    _map_row(tag="", stmt="CF", decision="not_presented", canonical_concept="amortization_of_intangibles", reason_class="not_presented_read_verified",
             era_from="2025-12-31", era_to="2025-12-31", decided_by="fy_status"),
]
FILINGS = [
    {"company_id": "7", "accession": "A2019", "form": "10-K", "period": "2019-12-31", "accepted": "2020-02-10", "faces": "3"},
    {"company_id": "7", "accession": "A2019X", "form": "10-K/A", "period": "2019-12-31", "accepted": "2020-04-30", "faces": "0"},
    {"company_id": "7", "accession": "A2020", "form": "10-K", "period": "2020-12-31", "accepted": "2021-02-10", "faces": "3"},
    {"company_id": "7", "accession": "A2021", "form": "10-K", "period": "2021-12-31", "accepted": "2022-02-10", "faces": "3"},
    {"company_id": "7", "accession": "A2025", "form": "10-K", "period": "2025-12-31", "accepted": "2026-02-10", "faces": "3"},
]
CATALOG = [{"name": "amortization_of_intangibles", "statement": "cash_flow"}, {"name": "accounts_payable", "statement": "balance_sheet"}]


def _run(tmp_path, cells, lines, extra_map=()):
    p = {k: tmp_path / f"{k}.csv" for k in ("map", "cells", "filings", "lines", "cat", "out", "gaps")}
    _w(p["map"], MAP_COLS, BASE_MAP + list(extra_map))
    _w(p["cells"], ["company_id", "data_point", "period_end"], cells)
    _w(p["filings"], list(FILINGS[0]), FILINGS)
    _w(p["lines"], ["accession", "report", "rfile", "line", "stmt", "tag", "custom", "plabel"], lines)
    _w(p["cat"], ["name", "statement"], CATALOG)
    subprocess.run([sys.executable, "-I", str(SCRIPT), *(str(p[k]) for k in ("map", "cells", "filings", "lines", "cat", "out", "gaps"))],
                   check=True, capture_output=True)
    new = [r for r in csv.DictReader(open(p["out"])) if r["decided_by"] == "fy_era_status"]
    return new, list(csv.DictReader(open(p["gaps"])))


def _cell(dp, p):
    return {"company_id": "7", "data_point": dp, "period_end": p}


def _line(acc, tag, plabel, stmt="CF", custom="f"):
    return {"accession": acc, "report": "4", "rfile": "R4.htm", "line": "3", "stmt": stmt, "tag": tag, "custom": custom, "plabel": plabel}


def test_an_older_year_is_not_presented_only_when_its_own_10k_carries_no_tag_and_no_label(tmp_path):
    new, gaps = _run(tmp_path, [_cell("amortization_of_intangibles", "2020-12-31")], [_line("A2020", "Revenues", "Revenue", stmt="IS")])
    assert [(r["decision"], r["era_from"], r["era_to"], r["evidence_adsh"]) for r in new] == [("not_presented", "2020-12-31", "2020-12-31", "A2020")]
    assert new[0]["reason_class"] == "not_presented_whole_filing" and gaps == []


def test_a_candidate_tag_anywhere_in_the_years_filing_is_a_gap_never_a_reason(tmp_path):
    lines = [_line("A2020", "AmortizationOfIntangibleAssets", "Amortization expense", stmt="UN")]  # a note page, not the face
    new, gaps = _run(tmp_path, [_cell("amortization_of_intangibles", "2020-12-31")], lines)
    assert new == []
    assert [(g["kind"], g["tag"], g["report"]) for g in gaps] == [("GAP", "AmortizationOfIntangibleAssets", "R4.htm")]


def test_a_combined_tag_spanning_the_data_point_is_not_in_template_with_the_line_as_evidence(tmp_path):
    lines = [_line("A2020", "AccountsPayableAndAccruedLiabilitiesCurrent", "Accounts payable and accrued liabilities", stmt="BS")]
    new, gaps = _run(tmp_path, [_cell("accounts_payable", "2020-12-31")], lines)
    assert [(r["decision"], r["reason_class"], r["evidence_report"]) for r in new] == \
        [("not_in_template", "line_presented_combined_with_others", "R4.htm")]
    assert gaps == []


def test_a_custom_tag_with_the_data_points_label_goes_to_review_not_to_a_reason(tmp_path):
    lines = [_line("A2020", "xyz:AmortizationOfAcquiredIntangibles", "Amortization of acquired intangible assets", stmt="UN", custom="t")]
    new, gaps = _run(tmp_path, [_cell("amortization_of_intangibles", "2020-12-31")], lines)
    assert new == [] and [g["kind"] for g in gaps] == ["review"]


def test_a_standard_tag_label_on_another_statements_note_does_not_block_not_presented(tmp_path):
    lines = [_line("A2020", "FiniteLivedIntangibleAssetsAccumulatedAmortization", "Accumulated amortization of intangible assets", stmt="UN")]
    new, gaps = _run(tmp_path, [_cell("amortization_of_intangibles", "2020-12-31")], lines)
    assert [r["decision"] for r in new] == ["not_presented"] and gaps == []


def test_the_latest_10k_status_is_never_carried_to_another_year_and_a_covered_cell_is_left_alone(tmp_path):
    cells = [_cell("amortization_of_intangibles", "2025-12-31"), _cell("amortization_of_intangibles", "2022-12-31")]
    new, gaps = _run(tmp_path, cells, [])
    assert new == [] and gaps == []  # 2025 already has its status row; 2022 has no 10-K in the store: no row, no gap


def test_an_amendment_without_face_statements_never_decides_the_year(tmp_path):
    new, _ = _run(tmp_path, [_cell("amortization_of_intangibles", "2019-12-31")], [])
    assert [r["evidence_adsh"] for r in new] == ["A2019"]


def test_a_rerun_re_decides_its_own_rows_instead_of_keeping_them(tmp_path):
    first, _ = _run(tmp_path, [_cell("amortization_of_intangibles", "2021-12-31")], [])
    assert [r["decision"] for r in first] == ["not_presented"]
    lines = [_line("A2021", "AmortizationOfIntangibleAssets", "Amortization of intangibles")]  # the store now has the line
    again, gaps = _run(tmp_path, [_cell("amortization_of_intangibles", "2021-12-31")], lines, extra_map=first)
    assert again == [] and [g["kind"] for g in gaps] == ["GAP"]
