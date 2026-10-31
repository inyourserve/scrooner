"""period.duplicate_column_merge@1: pure planning tests."""

from datetime import date
from decimal import Decimal

import pytest
from scrooner_pipeline.common.presentation_scale import presentation_scale, same_number
from scrooner_pipeline.normalizer import duplicate_columns as dc


def P(id, start, end, n, fy=2026, fp="Q2", typ="duration"):
    return dc.PeriodRow(
        id, date.fromisoformat(start), date.fromisoformat(end), typ, fy, fp, n
    )


def F(id, concept, value, filing, unit=1, auth=True):
    return dc.FactCopy(id, concept, unit, Decimal(value), filing, auth, False)


@pytest.mark.unit
def test_clusters_need_same_label_close_end_close_length_and_facts_on_both_rows():
    rows = [
        P(1, "2025-06-29", "2025-09-27", 77),  # RBC: the statement
        P(2, "2025-07-01", "2025-09-27", 1),  # same quarter, start spelled differently
        P(3, "2025-07-01", "2025-09-27", 0, fp="Q2"),  # empty duplicate: ignored
        P(
            4, "2025-01-01", "2025-09-27", 40, fp="Q2"
        ),  # a YTD mislabeled Q2: length differs -> not a column twin
        P(
            5, "2026-05-14", "2026-05-14", 0, fp="Q1", typ="instant"
        ),  # bank event date, no facts
        P(6, "2026-05-13", "2026-05-13", 0, fp="Q1", typ="instant"),
        P(7, "2025-12-31", "2025-12-31", 30, fp="FY", typ="instant"),
        P(
            8, "2026-01-01", "2026-01-01", 2, fp="FY", typ="instant"
        ),  # balance-sheet date spelled +1 day
    ]
    clusters = dc.cluster_periods(rows)
    assert sorted((c.canonical.id, [d.id for d in c.duplicates]) for c in clusters) == [
        (1, [2]),
        (7, [8]),
    ]


@pytest.mark.unit
def test_canonical_is_the_row_with_more_facts_tie_lowest_id():
    rows = [P(10, "2025-07-01", "2025-09-30", 5), P(11, "2025-07-02", "2025-09-30", 5)]
    assert dc.cluster_periods(rows)[0].canonical.id == 10


@pytest.mark.unit
def test_repoint_merge_and_hide():
    can, dup = P(1, "2025-06-29", "2025-09-27", 3), P(2, "2025-07-01", "2025-09-27", 3)
    clusters = [dc.Cluster(can, [dup])]
    facts = {
        1: [F(101, 10, "1000000", filing=500), F(102, 20, "250000", filing=500)],
        2: [
            F(201, 10, "1000000", filing=600),  # same value, other filing -> repoint
            F(
                202, 20, "251000", filing=500
            ),  # 1,000 apart on a thousands filer: same number, same filing -> demote
            F(203, 30, "77", filing=600),  # no counterpart -> repoint
        ],
    }
    actions = {a.concept_id: a for a in dc.plan_cells(7, clusters, facts, scale=3)}
    assert (
        actions[10].action == dc.MERGE
        and actions[10].repoint_fact_ids == [201]
        and not actions[10].demote_fact_ids
    )
    assert (
        actions[20].action == dc.MERGE
        and actions[20].demote_fact_ids == [202]
        and not actions[20].repoint_fact_ids
    )
    assert actions[30].action == dc.REPOINT and actions[30].repoint_fact_ids == [203]


@pytest.mark.unit
def test_msft_recast_is_hidden_on_both_rows_not_merged():
    can = P(1, "2016-07-01", "2016-09-30", 60, fy=2017, fp="Q1")
    dup = P(2, "2016-07-02", "2016-09-30", 40, fy=2017, fp="Q1")
    facts = {
        1: [F(1, 10, "20453000000", filing=1)],
        2: [F(2, 10, "21928000000", filing=2)],
    }
    (a,) = dc.plan_cells(5, [dc.Cluster(can, [dup])], facts, scale=6)
    assert a.action == dc.HIDE
    assert sorted(a.demote_fact_ids) == [1, 2] and a.repoint_fact_ids == []
    reasons = dc.hide_reasons(5, a, ["revenue", "revenue_sanity_resolved"])
    assert {r.key.data_point_name for r in reasons} == {
        "revenue",
        "revenue_sanity_resolved",
    }
    r = reasons[0]
    assert (r.key.period_grain, r.key.period_start, r.key.period_end) == (
        "Q",
        can.start,
        can.end,
    )
    assert (
        r.reason_code == dc.REASON_CODE_DIFFER
        and r.state == "defect"
        and r.owner == "period_engineer"
    )
    assert "20453000000" in r.reason_text and "21928000000" in r.reason_text


@pytest.mark.unit
def test_recast_picker_hook_demotes_only_the_loser():
    can = P(1, "2016-07-01", "2016-09-30", 60, fy=2017, fp="Q1")
    dup = P(2, "2016-07-02", "2016-09-30", 40, fy=2017, fp="Q1")
    facts = {
        1: [F(1, 10, "20453000000", filing=1)],
        2: [F(2, 10, "21928000000", filing=2)],
    }
    (a,) = dc.plan_cells(
        5, [dc.Cluster(can, [dup])], facts, scale=6, recast_picker=lambda *_: dup
    )
    assert a.action == dc.HIDE and a.demote_fact_ids == [
        1
    ]  # the original loses, the recast stays


@pytest.mark.unit
def test_presentation_scale_and_same_number():
    D = Decimal
    assert presentation_scale([D("630587000"), D("631000000"), D("2599000000")]) == 6
    assert presentation_scale([D("1234000"), D("5678000")]) == 3
    assert same_number(D("630587000"), D("631000000"), 6)
    assert not same_number(D("20453000000"), D("21928000000"), 6)
    assert same_number(D("251000"), D("250000"), 3) and not same_number(
        D("251000"), D("250000"), 0
    )


@pytest.mark.unit
def test_rule_registered_and_off_by_default(monkeypatch):
    from scrooner_pipeline.common import rule_flags as rf

    monkeypatch.delenv(rf.ENV_ENABLED, raising=False)
    monkeypatch.delenv(rf.ENV_DRYRUN, raising=False)
    assert dc.RULE_ID in rf.RULES and rf.rule_mode(dc.RULE_ID) == rf.OFF
    assert rf.RULES[dc.RULE_ID].dry_run is True
