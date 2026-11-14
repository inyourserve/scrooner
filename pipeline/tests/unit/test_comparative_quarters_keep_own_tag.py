"""Rule 3 (Dhairya 2026-11-14): a year's own quarters keep the tag their own 10-Qs print, even when the next 10-K's
comparative switched the fiscal-year tag (HD income_before_tax and 15 others). Generic: no per-company fix rows."""

from __future__ import annotations

from datetime import date

from scrooner_pipeline.mapper import docmap_loader as dl
from scrooner_pipeline.mapper import era_extend as ee

A = frozenset({"IncomeLossBeforeTaxOld"})
B = frozenset({"IncomeLossBeforeTaxNew"})
Y0, Y1 = date(2019, 2, 1), date(2020, 1, 31)
TENQS = {"Q1": date(2019, 5, 5), "Q2": date(2019, 8, 4), "Q3": date(2019, 11, 3)}


def test_quarter_split_when_every_10q_prints_the_old_tag():
    printed = {k: {"IncomeLossBeforeTaxOld"} for k in TENQS}
    sp = ee.quarter_split(Y0, Y1, B, [A, B], TENQS, printed)
    assert sp is not None
    assert (sp.tags, sp.last_quarter_end, sp.adsh) == (A, date(2019, 11, 3), "Q3")


def test_no_split_when_a_10q_already_prints_the_comparative_tag():
    printed = {k: {"IncomeLossBeforeTaxOld"} for k in TENQS}
    printed["Q2"] = {"IncomeLossBeforeTaxOld", "IncomeLossBeforeTaxNew"}
    printed["Q1"] = printed["Q3"] = {"IncomeLossBeforeTaxNew"}
    assert ee.quarter_split(Y0, Y1, B, [A, B], TENQS, printed) is None


def test_no_split_without_10qs_or_when_10qs_disagree():
    assert ee.quarter_split(Y0, Y1, B, [A, B], {}, {}) is None
    printed = {"Q1": {"IncomeLossBeforeTaxOld"}, "Q2": set(), "Q3": set()}
    assert ee.quarter_split(Y0, Y1, B, [A, B], TENQS, printed) is None


def _row(tag, era_from, era_to, by):
    return {
        "company_id": 1,
        "cik": "0000000001",
        "canonical_concept_id": 9,
        "parent_concept_id": None,
        "decision": "concept",
        "taxonomy": "us-gaap",
        "tag": tag,
        "sign": 1,
        "stmt": "IS",
        "era_from": era_from,
        "era_to": era_to,
        "decided_by": by,
        "rule_id": "x@1",
        "scale": 1,
    }


def test_comparative_rows_give_the_quarters_the_10q_tag_and_the_fy_cell_the_comparative_tag(
    monkeypatch,
):
    rows = [
        _row(
            "IncomeLossBeforeTaxOld",
            date(2015, 2, 1),
            date(2018, 1, 31),
            "tag_expert_predictor",
        ),
        _row("IncomeLossBeforeTaxNew", date(2021, 1, 31), None, "docmap"),
    ]
    nxt = "0000000001-21-000001"
    monkeypatch.setattr(
        ee,
        "fetch_printed",
        lambda conn, cid, tags, ids=None: (
            {nxt: date(2021, 1, 31)},
            {
                (nxt, "IncomeLossBeforeTaxNew"): {
                    date(2020, 1, 31): {"annual"},
                    date(2021, 1, 31): {"annual"},
                }
            },
            {(nxt, "IncomeLossBeforeTaxNew"): {"annual"}},
            {},
        ),
    )
    monkeypatch.setattr(
        ee,
        "fetch_quarter_prints",
        lambda conn, cid, tags: (TENQS, {k: {"IncomeLossBeforeTaxOld"} for k in TENQS}),
    )
    out = dl.comparative_rows(None, 1, "0000000001", rows, {"income_before_tax": 9}, [])
    got = {(r["tag"], r["era_from"], r["era_to"]) for r in out}
    assert (
        "IncomeLossBeforeTaxOld",
        date(2019, 2, 1),
        date(2019, 11, 3),
    ) in got
    assert ("IncomeLossBeforeTaxNew", date(2019, 11, 4), date(2020, 1, 31)) in got
