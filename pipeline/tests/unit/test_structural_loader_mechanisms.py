"""Loader mechanisms from the top-100 open-cell causes (Tag Expert, 2026-11-15). Each assertion fails without its fix:

- 52/53-week period key: a component-sum claim's stored facts are matched by the FSN month end, not by equality (NVDA
  FY2018: resolver 2018-01-31, facts 2018-01-28);
- derived_not_printed gross profit / total liabilities load as the map's not_presented statement (mapper/derived_cells
  needs it), other derived rows stay unloaded;
- a reason ruled `true_reason` by the false-reason sweep rulings is not refused by the guard (AMZN D&A, buybacks)."""

from __future__ import annotations

import csv
from datetime import date
from decimal import Decimal
from pathlib import Path

from scrooner_pipeline.mapper import reason_guard as rg
from scrooner_pipeline.mapper import structural_loader as sl
from test_structural_loader_nodes import _row, _write


class _Cur:
    def __init__(self, rows):
        self.rows = rows

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def execute(self, sql, params=None):
        self.params = params

    def fetchall(self):
        lo, hi = self.params[2], self.params[3]
        return [r for r in self.rows if lo <= r[2] <= hi]


class _Conn:
    def __init__(self, rows):
        self.rows = rows

    def cursor(self):
        return _Cur(self.rows)


def test_fact_options_match_a_52_53_week_end_by_its_fsn_month_end():
    conn = _Conn([(1, "LongTermDebt", date(2018, 1, 28), Decimal(1985))])
    got = sl.fact_options(conn, [(1, "LongTermDebt", date(2018, 1, 31))])
    assert got[(1, "LongTermDebt", date(2018, 1, 31))] == {Decimal(1985)}


def test_fact_options_prefer_the_exact_end_over_a_stray_nearby_one():
    conn = _Conn(
        [
            (1, "T", date(2018, 1, 31), Decimal(5)),
            (1, "T", date(2018, 2, 2), Decimal(9)),
        ]
    )
    got = sl.fact_options(conn, [(1, "T", date(2018, 1, 31))])
    assert got[(1, "T", date(2018, 1, 31))] == {Decimal(5)}


def test_fact_options_do_not_reach_a_different_year():
    conn = _Conn([(1, "T", date(2017, 1, 29), Decimal(7))])
    assert not sl.fact_options(conn, [(1, "T", date(2018, 1, 31))])


def test_derived_gross_profit_and_total_liabilities_load_as_not_presented(
    tmp_path: Path,
):
    why = " | why: the income statement prints no gross profit (ruling C1)"
    p = _write(
        tmp_path,
        _row(
            data_point="gross_profit",
            decision="derived_not_printed",
            nodes="Revenues=10 [R2.htm:2]; -CostOfRevenue=4 [R2.htm:8]" + why,
            value="6",
        ),
        _row(
            data_point="total_liabilities",
            decision="derived_not_printed",
            nodes="Liabilities=1 [R4.htm:20]" + why,
            value="1",
        ),
        _row(
            data_point="stockholders_equity",
            decision="derived_not_printed",
            nodes="StockholdersEquity=1 [R4.htm:30]" + why,
            value="1",
        ),
    )
    claims, rejects, counts = sl.read_claims(p)
    assert rejects == []
    assert {(c.data_point, c.decision) for c in claims} == {
        ("gross_profit", "not_presented"),
        ("total_liabilities", "not_presented"),
    }
    assert counts["skipped_derived_not_printed"] == 1  # stockholders_equity


def _rulings(d: Path, *rows: dict) -> None:
    cols = [
        "ticker",
        "data_point",
        "fiscal_year",
        "accession",
        "evidence_tags",
        "decision_before",
        "decision_now",
        "verdict",
    ]
    with (d / "_false-reason-rulings-2026-11-14.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in cols})


def test_ruled_true_reasons_are_read_and_filter_the_guard(tmp_path: Path):
    ok = {
        "ticker": "AMZN",
        "data_point": "share_buybacks",
        "accession": "0001018724-19-000004",
        "evidence_tags": "StockRepurchasedDuringPeriodValue",
        "decision_before": "not_presented",
        "decision_now": "not_presented",
        "verdict": "true_reason",
    }
    _rulings(
        tmp_path,
        ok,
        {**ok, "data_point": "other", "verdict": "reason_corrected"},
        {**ok, "data_point": "changed", "decision_now": "mapped"},
    )
    rg.ruled_true_reasons.cache_clear()
    got = rg.ruled_true_reasons(str(tmp_path))
    rg.ruled_true_reasons.cache_clear()
    assert got == {
        (
            "0001018724-19-000004",
            "share_buybacks",
            "StockRepurchasedDuringPeriodValue",
        )
    }
    tag = "StockRepurchasedDuringPeriodValue"
    facts = {tag: [rg.Fact(date(2018, 12, 31), 4, False, "", Decimal(0))]}
    args = ("not_presented", date(2018, 12, 31), False, {tag}, "", facts)
    assert rg.evidence_for(*args)
    assert rg.evidence_for(*args, {tag}) == []


def _fix_row(note: str) -> dict:
    return {
        "id": 5,
        "rule_id": sl.HAND_FIX_RULE_ID,
        "decided_by": "t",
        "era_from": date(2018, 1, 1),
        "era_to": date(2018, 12, 31),
        "canonical_concept_id": 7,
        "parent_concept_id": None,
        "decision": "concept",
        "taxonomy": "us-gaap",
        "tag": "FinanceLeaseLiability",
        "sign": 1,
        "components": None,
        "reason_class": None,
        "serve_note": note,
        "evidence_adsh": "0000000301-20-000001",
    }


def _plan_value(existing, tmp_path: Path):
    p = _write(
        tmp_path,
        _row(
            decision="mapped",
            nodes="AnyTag=5 [R4.htm:9] | why: IS line 9",
            value="5",
        ),
    )
    (c,) = sl.read_claims(p)[0]
    rows = sl.build_rows(
        c,
        date(2018, 1, 1),
        date(2018, 12, 31),
        1,
        "0000000301",
        "operating_expenses",
        {"operating_expenses": "income_statement"},
        {"AnyTag": "us-gaap"},
    )
    rows = [
        sl.normalize(r, {}, {"operating_expenses": 7}, sl.RULE_ID, []) for r in rows
    ]
    return sl.plan_company(
        existing,
        [(c, date(2018, 1, 1), date(2018, 12, 31), rows)],
        {7: "operating_expenses"},
    )


def test_a_hand_fix_written_from_an_earlier_resolver_run_does_not_win_its_cell(
    tmp_path: Path,
):
    stale = _plan_value(
        [_fix_row("fill; source=line_map; comparative column of X")], tmp_path
    )
    assert stale.exceptions == []  # not a hand fix any more
    assert 5 in stale.deletes  # cut like a library row the resolver disagrees with
    real = _plan_value([_fix_row("a reader's own read of the 10-K")], tmp_path)
    assert len(real.exceptions) == 1 and 5 not in real.deletes
