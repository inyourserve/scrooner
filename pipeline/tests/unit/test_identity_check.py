"""identity.cik_name_ticker@1 invariant on REAL per-CIK SEC submissions (fetched
2026-10-22, trimmed to name/tickers/formerNames/event filings) against the values
we store (read-only lookups 2026-10-22, DATA-INFERRED; GATE-A-IDENTITY-REGISTRANT-
CHECKS sections 1-2 for the filing-checked verdicts)."""

import json
from datetime import date
from pathlib import Path

import pytest

from scrooner_pipeline.company_master.identity_check import (
    SecIdentity,
    StoredIdentity,
    compare_identity,
    norm_name,
)

FX = Path(__file__).resolve().parents[1] / "fixtures" / "sec" / "submissions"


def sec(cik):
    return SecIdentity.from_submissions(json.loads((FX / f"{cik}.json").read_text()))


def kinds(stored, cik):
    return sorted(f.kind for f in compare_identity(stored, sec(cik)))


@pytest.mark.unit
def test_vivmark_is_correct_but_its_display_name_is_not():
    s = StoredIdentity(
        "0000906107",
        "VIVMARK RESIDENTIAL",
        "AvalonBay Communities, Inc.",
        "VMRK",
        "active",
        date(2026, 7, 24),
    )
    f = compare_identity(s, sec("0000906107"))
    assert [x.kind for x in f if x.kind != "name_or_ticker_event"] == [
        "display_name_unrelated"
    ]
    assert any(
        x.kind == "name_or_ticker_event" and "0001140361-26-033377" in x.accessions
        for x in f
    )


@pytest.mark.unit
def test_skydance_stale_name_and_the_5_03_event():
    s = StoredIdentity(
        "0002041610",
        "Paramount Skydance Corp",
        None,
        "PSKY",
        "active",
        date(2026, 8, 4),
    )
    f = {x.kind: x for x in compare_identity(s, sec("0002041610"))}
    assert "name_not_current" in f and "Skydance Corp" in f["name_not_current"].detail
    assert (
        "name_or_ticker_event" in f
        and "0001104659-26-113913" in f["name_or_ticker_event"].accessions
    )
    assert (
        "ticker_not_in_submissions" not in f
    )  # PSKY is still listed beside SKYD: only the event shows it moved


@pytest.mark.unit
def test_avalonbay_and_wbd_deregistration_after_the_last_periodic_filing():
    avb = StoredIdentity(
        "0000915912",
        "AVALONBAY COMMUNITIES INC",
        "AvalonBay Communities Inc",
        "AVB",
        "active",
        date(2026, 7, 30),
    )
    f = {x.kind: x for x in compare_identity(avb, sec("0000915912"))}
    assert {"ticker_not_in_submissions", "deregistration_after_last_periodic"} <= set(f)
    assert (
        "0001104659-26-102433" in f["deregistration_after_last_periodic"].accessions
    )  # 15-12G
    wbd = StoredIdentity(
        "0001437107",
        "Warner Bros. Discovery, Inc.",
        None,
        "WBD",
        "active",
        date(2026, 8, 6),
    )
    f = {x.kind: x for x in compare_identity(wbd, sec("0001437107"))}
    assert "0001193125-26-423513" in f["deregistration_after_last_periodic"].accessions


@pytest.mark.unit
def test_form_15_before_the_last_periodic_filing_is_not_flagged():
    # Form 15 on preferred or plan interests while the common keeps filing 10-Qs (BMY, PG, APO pattern)
    wbd = StoredIdentity(
        "0001437107",
        "Warner Bros. Discovery, Inc.",
        None,
        "WBD",
        "active",
        date(2026, 11, 30),
    )
    assert "deregistration_after_last_periodic" not in kinds(wbd, "0001437107")


@pytest.mark.unit
@pytest.mark.parametrize(
    "cik,name,display,ticker",
    [
        (
            "0000007323",
            "ENTERGY ARKANSAS, LLC",
            "Entergy Arkansas, Inc. 1M BD 4.875%66",
            "EAI",
        ),
        (
            "0000041091",
            "GEORGIA POWER CO",
            "Georgia Power Company 5% JR SUB NT 77",
            "GPJA",
        ),
        ("0000201533", "CONSUMERS ENERGY CO", "Consumers Energy Company", "CMS-PB"),
        (
            "0000081023",
            "PUBLIC SERVICE CO OF NEW MEXICO",
            "Public Service Company of New Mexico PFD 4.58%",
            "PNMXO",
        ),
    ],
)
def test_subsidiary_bond_and_preferred_tickers_are_pseudo(cik, name, display, ticker):
    s = StoredIdentity(
        cik,
        name,
        display,
        ticker,
        "active",
        date(2026, 8, 1),
        is_subsidiary_registrant=True,
    )
    f = [x for x in compare_identity(s, sec(cik)) if x.kind == "pseudo_ticker"]
    assert len(f) == 1 and "subsidiary registrant" in f[0].detail


@pytest.mark.unit
def test_apple_is_clean_and_name_normalization():
    s = StoredIdentity(
        "0000320193", "Apple Inc.", "Apple Inc.", "AAPL", "active", date(2026, 7, 31)
    )
    assert [
        x.kind
        for x in compare_identity(s, sec("0000320193"))
        if x.kind != "name_or_ticker_event"
    ] == []
    assert norm_name("COSTCO WHOLESALE CORP /NEW") == "COSTCO WHOLESALE"
    assert norm_name("AT&T Inc.") == norm_name("AT & T INC")
    assert norm_name("ENTERGY ARKANSAS, LLC") == norm_name("Entergy Arkansas, Inc.")


@pytest.mark.unit
def test_case_and_suffix_differences_are_not_a_stale_name():
    s = StoredIdentity(
        "0000320193", "APPLE INC", "Apple Inc.", "AAPL", "active", date(2026, 7, 31)
    )
    assert "name_not_current" not in kinds(s, "0000320193")
