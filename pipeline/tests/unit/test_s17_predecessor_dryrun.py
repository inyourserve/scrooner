"""scripts/s17_predecessor_dryrun.py: which S17 red cells would the predecessor-companyfacts backfill fill (pure)."""

from __future__ import annotations

import importlib.util
from datetime import date
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "s17_predecessor_dryrun.py"
spec = importlib.util.spec_from_file_location("s17_dryrun", SCRIPT)
dry = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dry)

PRAXAIR = "0000884905"
WINDOWS = [(PRAXAIR, date(2014, 1, 1), date(2018, 9, 30))]
FY17 = date(2017, 12, 31)


def claim(name, tag, decision="concept", era_from=None, era_to=None, reason=None):
    # [company_id, cik, taxonomy, tag, stmt, decision, concept, sign, era_from, era_to, reason_class]
    return [
        4841,
        "0001707925",
        "us-gaap",
        tag,
        "IS",
        decision,
        name,
        1,
        era_from,
        era_to,
        reason,
    ]


def facts(*rows):
    out = {}
    for tag, start, end, accn in rows:
        out.setdefault(("us-gaap", tag), []).append((start, end, accn))
    return lambda cik: out if cik == PRAXAIR else {}


def test_filled_when_a_claim_covers_the_era_and_the_predecessor_holds_the_annual_fact():
    f = facts(("Revenues", date(2017, 1, 1), FY17, "0000884905-18-000014"))
    got = dry.classify(
        "revenue", FY17, [claim("revenue_sanity_resolved", "Revenues")], WINDOWS, f
    )
    assert got == ("FILLED", "us-gaap:Revenues 0000884905-18-000014")


def test_a_quarter_long_fact_does_not_fill_an_annual_cell_but_an_instant_does():
    q = facts(("Revenues", date(2017, 10, 1), FY17, "a"))
    assert (
        dry.classify(
            "revenue", FY17, [claim("revenue_sanity_resolved", "Revenues")], WINDOWS, q
        )[0]
        == "claim_but_no_fact"
    )
    i = facts(("Assets", None, FY17, "a"))
    assert (
        dry.classify(
            "total_assets", FY17, [claim("total_assets_resolved", "Assets")], WINDOWS, i
        )[0]
        == "FILLED"
    )


def test_the_other_outcomes_are_told_apart():
    f = facts(("Revenues", date(2017, 1, 1), FY17, "a"))
    # no claim covers the era (the claim starts after it): the era must be extended, facts alone do not fill
    late = claim("revenue_sanity_resolved", "Revenues", era_from="2019-01-01")
    assert (
        dry.classify("revenue", FY17, [late], WINDOWS, f)[0]
        == "no_tag_map_claim_for_era"
    )
    # only a reason row covers it
    why = claim(
        "revenue_sanity_resolved",
        None,
        decision="not_presented",
        reason="docmap_not_presented",
    )
    assert dry.classify("revenue", FY17, [why], WINDOWS, f) == (
        "reason_claim_only:not_presented",
        "docmap_not_presented",
    )
    # a component claim is counted apart; a period outside every window is not the backfill's
    comp = claim("revenue_sanity_resolved", "Revenues", decision="component")
    assert dry.classify("revenue", FY17, [comp], WINDOWS, f)[0] == "component_claim"
    assert (
        dry.classify("revenue", date(2019, 12, 31), [comp], WINDOWS, f)[0]
        == "outside_window"
    )
