"""A hand fix that read ONE printed line of a component_sum does not win the cell (Stage 3 Resolve, M2).

KO other_income_expense_net FY2015: the 2026-11-13 reader fix maps OtherNonoperatingIncomeExpense (631M) while the
filing's IS band between operating income and pretax holds that line AND IncomeLossFromEquityMethodInvestments
(489M); the resolver claims the component_sum 1,120M. The fix won, so production served the one part and the census
listed the cell as 'derived:sum badge without parts' (31 cells, 10 companies, 2026-11-28). Both paths share
structural_loader.sum_supersedes_fix: direct serving serves the sum, and the loader cuts the fix row so the map
carries the two parts. Pure tests; each assertion fails with the predicate reverted to `return False`."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from types import SimpleNamespace

from scrooner_pipeline.mapper import structural_direct as sd
from scrooner_pipeline.mapper import structural_loader as sl
from test_structural_loader_nodes import _row, _write

DP = "other_income_expense_net"
KO_NODES = (
    "IncomeLossFromEquityMethodInvestments=489000000.0000 [R2.htm:13]; "
    "OtherNonoperatingIncomeExpense=631000000.0000 [R2.htm:14] | why: IS lines between OperatingIncomeLoss (R2:10) "
    "and pretax (R2:15): the line(s) that are not interest expense or interest income"
)


def _ko_claim(tmp_path: Path, decision: str = "component_sum") -> sl.Claim:
    nodes = KO_NODES
    if decision == "mapped":
        nodes = "OtherNonoperatingIncomeExpense=631000000.0000 [R2.htm:14] | why: IS line 14"
    p = _write(
        tmp_path,
        _row(
            data_point=DP,
            decision=decision,
            nodes=nodes,
            value="1120000000" if decision == "component_sum" else "631000000",
            flags="roles;band",
        ),
    )
    (c,) = sl.read_claims(p)[0]
    return c


def test_predicate_one_part_of_a_sum_is_superseded(tmp_path: Path):
    c = _ko_claim(tmp_path)
    assert sl.sum_supersedes_fix(["OtherNonoperatingIncomeExpense"], c)
    # the fix names both parts (not a strict subset), another tag, or nothing: the fix still wins
    assert not sl.sum_supersedes_fix(
        ["OtherNonoperatingIncomeExpense", "IncomeLossFromEquityMethodInvestments"], c
    )
    assert not sl.sum_supersedes_fix(["NonoperatingIncomeExpense"], c)
    assert not sl.sum_supersedes_fix([None], c)
    assert not sl.sum_supersedes_fix(["OtherNonoperatingIncomeExpense"], None)


def _fix_maprow(tag: str) -> SimpleNamespace:
    return SimpleNamespace(
        rule_id=sl.HAND_FIX_RULE_ID,
        serve_note="reader fix (company_tag_map.docmap_fix@1), FY ending 2015-12-31: printed value 631000000",
        decision="concept",
        tag=tag,
        canonical_concept_id=7,
        parent_concept_id=None,
        era_from=date(2018, 1, 1),
        era_to=date(2018, 12, 31),
    )


def test_direct_serving_serves_the_sum_over_a_one_part_fix(tmp_path: Path):
    end = date(2018, 12, 31)
    one_part = [_fix_maprow("OtherNonoperatingIncomeExpense")]
    assert not sd._fix_covers(one_part, 7, end, _ko_claim(tmp_path))
    # a mapped claim, no claim, or a fix outside the sum: the fix wins as before
    assert sd._fix_covers(one_part, 7, end, _ko_claim(tmp_path, "mapped"))
    assert sd._fix_covers(one_part, 7, end)
    assert sd._fix_covers(
        [_fix_maprow("NonoperatingIncomeExpense")], 7, end, _ko_claim(tmp_path)
    )


def _fix_row(tag: str) -> dict:
    return {
        "id": 5,
        "rule_id": sl.HAND_FIX_RULE_ID,
        "decided_by": "reader_fix",
        "era_from": date(2018, 1, 1),
        "era_to": date(2018, 12, 31),
        "canonical_concept_id": 7,
        "parent_concept_id": None,
        "decision": "concept",
        "taxonomy": "us-gaap",
        "tag": tag,
        "sign": 1,
        "components": None,
        "reason_class": None,
        "serve_note": "reader fix (company_tag_map.docmap_fix@1): a reader's own read of the 10-K",
        "evidence_adsh": "0000000301-19-000001",
    }


def _plan(existing: list[dict], tmp_path: Path) -> sl.Plan:
    c = _ko_claim(tmp_path)
    rows = sl.build_rows(
        c,
        date(2018, 1, 1),
        date(2018, 12, 31),
        1,
        "0000000301",
        DP,
        {DP: "income_statement"},
        {
            "IncomeLossFromEquityMethodInvestments": "us-gaap",
            "OtherNonoperatingIncomeExpense": "us-gaap",
        },
    )
    rows = [sl.normalize(r, {}, {DP: 7}, sl.RULE_ID, []) for r in rows]
    return sl.plan_company(
        existing, [(c, date(2018, 1, 1), date(2018, 12, 31), rows)], {7: DP}
    )


def test_loader_cuts_a_one_part_fix_and_writes_both_parts(tmp_path: Path):
    plan = _plan([_fix_row("OtherNonoperatingIncomeExpense")], tmp_path)
    assert [e["agrees"] for e in plan.exceptions] == ["superseded"]
    assert 5 in plan.deletes
    assert sorted(r["tag"] for r in plan.inserts if r.get("rule_id") == sl.RULE_ID) == [
        "IncomeLossFromEquityMethodInvestments",
        "OtherNonoperatingIncomeExpense",
    ]
    assert plan.value_cells == 1
    # a fix naming a line outside the sum is a different reading: it still wins its cell
    other = _plan([_fix_row("NonoperatingIncomeExpense")], tmp_path)
    assert [e["agrees"] for e in other.exceptions] == ["no"]
    assert 5 not in other.deletes and other.value_cells == 0
