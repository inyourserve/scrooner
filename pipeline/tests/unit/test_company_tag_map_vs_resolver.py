"""The company tag map derives from the resolver, never the reverse (Dhairya 2026-11-16: stale library 'combined' rows vetoed cells the
resolver maps). A map row with decision 'combined' for (company, element) must not contradict a resolver cell that SERVES that element for
one of the row's concepts inside the row's era. Reviewed exceptions live in data-team/tags/line_map/rules/map_conflicts_reviewed.csv with
their reason; any NEW conflict fails: run data-team/tags/line_map/tools/map_reconcile.py apply (or review the row) in the same commit."""

import csv
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "data-team" / "tags" / "line_map" / "tools"))
import map_reconcile as M  # noqa: E402


@pytest.mark.unit
def test_no_combined_map_row_contradicts_the_resolver_except_reviewed_ones():
    rows = list(csv.DictReader(open(M.MAP)))
    found = M.conflicts(rows, M.resolver_cells(M.newest_resolver()))
    reviewed = {
        (r["cik"].zfill(10), r["tag"], r["era_from"])
        for r in csv.DictReader(open(ROOT / "data-team/tags/line_map/rules/map_conflicts_reviewed.csv"))
    }
    new = [
        f"{rows[i]['ticker']} {rows[i]['tag']} {rows[i]['era_from']}..{rows[i]['era_to']}"
        for i, _ in found
        if (rows[i]["cik"].zfill(10), rows[i]["tag"], rows[i]["era_from"]) not in reviewed
    ]
    assert not new, f"combined map rows contradict the resolver (run map_reconcile.py apply): {new}"


@pytest.mark.unit
def test_conflict_detection_and_conversion_on_a_synthetic_map(tmp_path):
    m = tmp_path / "map.csv"
    fields = ["cik", "ticker", "tag", "decision", "canonical_concept", "parent_concept", "combine_sign", "components",
              "reason_class", "reason", "era_from", "era_to", "decided_by", "rule_id"]
    with open(m, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerow(dict(cik="1", ticker="X", tag="InterestExpenseDebt", decision="combined", canonical_concept="", parent_concept="",
                        combine_sign="", components="interest_expense;interest_income", reason_class="c", reason="net (label)",
                        era_from="2015-01-01", era_to="2016-12-31", decided_by="library", rule_id=""))
    r = tmp_path / "resolver.csv"
    r.write_text("cik,ticker,data_point,period_end,decision,nodes,column,resolver_version\n"
                 "1,X,interest_expense,2015-12-31,mapped,InterestExpenseDebt=5 [NOTE] | why: x,own,v1\n"
                 "1,X,interest_expense,2016-12-31,mapped,InterestExpenseDebt=6 [NOTE] | why: x,own,v1\n")
    assert M.main("check", str(m), str(r)) == 1
    assert M.main("apply", str(m), str(r)) == 0
    row = next(csv.DictReader(open(m)))
    assert (row["decision"], row["canonical_concept"], row["decided_by"]) == ("concept", "interest_expense", "resolver")
    assert M.main("check", str(m), str(r)) == 0


@pytest.mark.unit
def test_a_combined_row_covered_by_a_concept_row_of_the_same_element_is_retired(tmp_path):
    # MS IncreaseDecreaseInReceivables: a 2015-2026 concept row already serves the element; the 2024-25 combined row is redundant
    m = tmp_path / "map.csv"
    fields = ["cik", "ticker", "tag", "stmt", "decision", "canonical_concept", "parent_concept", "combine_sign", "components",
              "reason_class", "reason", "era_from", "era_to", "decided_by", "rule_id"]
    base = dict(cik="1", ticker="X", tag="IncreaseDecreaseInReceivables", stmt="CF", parent_concept="", combine_sign="", reason_class="c",
                reason="r", decided_by="library", rule_id="")
    with open(m, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerow(dict(base, decision="concept", canonical_concept="cf_ar_change", components="", era_from="2015-01-01", era_to="2026-12-31"))
        w.writerow(dict(base, decision="combined", canonical_concept="", components="cf_ar_change", era_from="2024-01-01", era_to="2025-12-31"))
    r = tmp_path / "resolver.csv"
    r.write_text("cik,ticker,data_point,period_end,decision,nodes,column,resolver_version\n"
                 "1,X,cf_ar_change,2024-12-31,mapped,IncreaseDecreaseInReceivables=5 [R6.htm:9] | why: x,own,v1\n")
    M.main("apply", str(m), str(r))
    rows = list(csv.DictReader(open(m)))
    assert [x["decision"] for x in rows] == ["concept"]
