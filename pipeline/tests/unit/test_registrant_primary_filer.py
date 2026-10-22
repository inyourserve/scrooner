"""P1 (entity.shared_accession_primary_filer@1) on REAL filing artifacts.

Fixtures (tests/fixtures/sec/registrants/): the SEC submission headers of eight
accessions and trimmed XBRL instances (only the dei CIK facts and the contexts
they use) of Entergy's 10-K, a Southern 10-Q and an Apple 10-Q, taken from the
Verifier's 2026-10-22 Gate A fetches (GATE-A-IDENTITY-REGISTRANT-CHECKS.md
section 3e, FILING-CHECKED). The expected rows are that report's table.
"""

import json
from pathlib import Path

import pytest

from scrooner_pipeline.common import rule_flags
from scrooner_pipeline.normalizer import registrant as r
from scrooner_pipeline.normalizer import registrant_loader as rl

FX = Path(__file__).resolve().parents[1] / "fixtures" / "sec" / "registrants"


def header(acc: str) -> str:
    return (FX / f"{acc}.header.txt").read_text()


def filers(acc: str) -> list[str]:
    return r.parse_header_filers(header(acc))


# accession -> (number of header FILER blocks, first filer, default-context dei CIK per the report)
TABLE = {
    "0000065984-26-000174": (7, "0000065984", "0000065984"),  # ETR 10-K
    "0000065984-26-000283": (
        7,
        "0000065984",
        "0000065984",
    ),  # ETR Q2 10-Q (companyfacts serves it under 7323)
    "0000092122-26-000054": (
        6,
        "0000092122",
        "0000092122",
    ),  # Southern (companyfacts: 1004155)
    "0001032208-26-000045": (
        3,
        "0001032208",
        "0001032208",
    ),  # Sempra (companyfacts: 92108)
    "0000827052-26-000059": (
        2,
        "0000827052",
        "0000827052",
    ),  # Edison (companyfacts: 92103)
    "0001628280-26-051906": (
        4,
        "0000072741",
        "0000072741",
    ),  # Eversource, agent-filed prefix
    "0000107815-25-000182": (
        1,
        "0000783325",
        "0000783325",
    ),  # WEC: prefix is Wisconsin Electric's account
    "0000320193-26-000020": (1, "0000320193", "0000320193"),  # AAPL
}


@pytest.mark.unit
@pytest.mark.parametrize("acc,expected", TABLE.items())
def test_header_filers_on_real_headers(acc, expected):
    n, first, _dei = expected
    got = filers(acc)
    assert len(got) == n and got[0] == first and len(set(got)) == n


@pytest.mark.unit
def test_header_filers_lists_the_seven_entergy_registrants():
    assert set(filers("0000065984-26-000174")) == {
        "0000065984",
        "0000007323",
        "0001348952",
        "0000066901",
        "0000071508",
        "0001427437",
        "0000202584",
    }


@pytest.mark.unit
def test_labelled_text_header_form_is_understood_and_other_blocks_ignored():
    text = (
        "ACCESSION NUMBER:\t\t0000065984-26-000283\nFILER:\n\n\tCOMPANY DATA:\n\t\tCOMPANY CONFORMED NAME:\tENTERGY CORP\n"
        "\t\tCENTRAL INDEX KEY:\t\t\t0000065984\n\nFILER:\n\n\tCOMPANY DATA:\n\t\tCOMPANY CONFORMED NAME:\tENTERGY ARKANSAS\n"
        "\t\tCENTRAL INDEX KEY:\t\t\t0000007323\n\nFILED BY:\n\n\tCOMPANY DATA:\n\t\tCENTRAL INDEX KEY:\t\t\t0000999999\n"
    )
    assert r.parse_header_filers(text) == ["0000065984", "0000007323"]


@pytest.mark.unit
def test_default_context_cik_on_real_instances_ignores_member_contexts():
    etr = (FX / "etr-20251231_htm.trimmed.xml").read_bytes()
    assert r.extract_default_context_cik(etr) == "0000065984"
    assert (FX / "etr-20251231_htm.trimmed.xml").read_text().count(
        "EntityCentralIndexKey"
    ) >= 14  # 7 facts, open+close
    assert (
        r.extract_default_context_cik((FX / "so-10q.trimmed.xml").read_bytes())
        == "0000092122"
    )
    assert (
        r.extract_default_context_cik((FX / "aapl-10q.trimmed.htm").read_bytes())
        == "0000320193"
    )


@pytest.mark.unit
def test_default_context_cik_none_and_ambiguous():
    ns = 'xmlns="http://www.xbrl.org/2003/instance" xmlns:dei="http://xbrl.sec.gov/dei/2025" xmlns:xbrldi="http://xbrl.org/2006/xbrldi"'
    only_member = (
        f'<xbrl {ns}><context id="m"><entity><segment><xbrldi:explicitMember dimension="dei:LegalEntityAxis">x:A</xbrldi:explicitMember>'
        '</segment></entity></context><dei:EntityCentralIndexKey contextRef="m">0000007323</dei:EntityCentralIndexKey></xbrl>'
    )
    assert r.extract_default_context_cik(only_member.encode()) is None
    two = (
        f'<xbrl {ns}><context id="a"><entity/></context><context id="b"><entity/></context>'
        '<dei:EntityCentralIndexKey contextRef="a">1</dei:EntityCentralIndexKey>'
        '<dei:EntityCentralIndexKey contextRef="b">2</dei:EntityCentralIndexKey></xbrl>'
    )
    with pytest.raises(r.AmbiguousDeiCik):
        r.extract_default_context_cik(two.encode())


@pytest.mark.unit
def test_instance_parser_does_not_resolve_entities(tmp_path):
    secret = tmp_path / "secret.txt"
    secret.write_text("0000000001")
    evil = (
        f'<?xml version="1.0"?><!DOCTYPE x [<!ENTITY e SYSTEM "file://{secret}">]>'
        '<xbrl xmlns="http://www.xbrl.org/2003/instance" xmlns:dei="http://xbrl.sec.gov/dei/2025">'
        '<context id="c"><entity/></context><dei:EntityCentralIndexKey contextRef="c">&e;</dei:EntityCentralIndexKey></xbrl>'
    ).encode()
    # if the entity were resolved the file's content would come back as a CIK
    with pytest.raises(ValueError):
        r.extract_default_context_cik(evil)


@pytest.mark.unit
@pytest.mark.parametrize("acc,expected", TABLE.items())
def test_primary_filer_rule_on_the_gate_a_table(acc, expected):
    n, first, dei = expected
    d = r.decide_primary(acc, dei, filers(acc))
    assert not d.quarantined and d.primary_cik == first and d.shared == (n >= 2)
    assert d.role_of(first) == r.PRIMARY
    for other in d.registrant_ciks[1:]:
        assert d.role_of(other) == r.CO_REGISTRANT


@pytest.mark.unit
def test_the_accession_prefix_is_not_evidence():
    # WEC: prefix 0000107815 is Wisconsin Electric's filer account, the registrant is 0000783325
    assert r.accession_prefix_cik("0000107815-25-000182") == "0000107815"
    d = r.decide_primary(
        "0000107815-25-000182", "0000783325", filers("0000107815-25-000182")
    )
    assert d.primary_cik == "0000783325"
    # Eversource: agent prefix 0001628280
    d = r.decide_primary(
        "0001628280-26-051906", "0000072741", filers("0001628280-26-051906")
    )
    assert d.primary_cik == "0000072741"
    # companyfacts served the Entergy Q2 10-Q under 7323: the rule does not consult it at all
    d = r.decide_primary(
        "0000065984-26-000283", "0000065984", filers("0000065984-26-000283")
    )
    assert d.primary_cik == "0000065984" and d.role_of("0000007323") == r.CO_REGISTRANT


@pytest.mark.unit
@pytest.mark.parametrize(
    "dei,header,reason",
    [
        (
            "0000007323",
            ["0000065984", "0000007323"],
            "disagrees with the first header filer",
        ),
        (None, ["0000065984", "0000007323"], "without a default-context"),
        ("0000999999", ["0000065984", "0000007323"], "not a header filer"),
        ("0000065984", ["0000007323"], "not the sole filer"),
        (None, [], "no FILER block"),
    ],
)
def test_disagreement_quarantines_the_whole_accession(dei, header, reason):
    d = r.decide_primary("0000065984-26-000283", dei, header)
    assert d.quarantined and reason in d.quarantine_reason and d.primary_cik is None
    assert all(d.role_of(c) == r.QUARANTINED for c in d.registrant_ciks)


@pytest.mark.unit
def test_sole_filer_without_a_dei_cik_is_accepted():
    d = r.decide_primary("0000320193-26-000020", None, ["0000320193"])
    assert not d.quarantined and d.primary_cik == "0000320193" and not d.shared


@pytest.mark.unit
def test_find_shared_accessions_from_submission_lists():
    subs = {
        "0000065984": [
            "0000065984-26-000174",
            "0000065984-26-000283",
            "0000065984-26-000001",
        ],
        "7323": [
            "0000065984-26-000174",
            "0000065984-26-000283",
            "0000007323-26-000009",
        ],
        "0000320193": ["0000320193-26-000020"],
    }
    shared = r.find_shared_accessions(subs)
    assert shared == {
        "0000065984-26-000174": {"0000065984", "0000007323"},
        "0000065984-26-000283": {"0000065984", "0000007323"},
    }


# ---------------------------------------------------------------- payload merge
def _payload(entries_by_tag, name="X"):
    return {
        "cik": 1,
        "entityName": name,
        "facts": {
            "us-gaap": {
                tag: {"label": tag, "units": {"USD": entries}}
                for tag, entries in entries_by_tag.items()
            }
        },
    }


Q2 = "0000065984-26-000283"
K = "0000065984-26-000174"
ETR_OWN = _payload(
    {"Assets": [{"end": "2025-12-31", "val": 71890730000, "accn": K, "form": "10-K"}]},
    "ENTERGY CORP",
)
# SEC served the Q2 2026 10-Q under Entergy Arkansas (entityName ENTERGY CORPORATION); the values are Entergy Corp's
EAI_PAYLOAD = _payload(
    {
        "Assets": [
            {"end": "2026-06-30", "val": 79002618000, "accn": Q2, "form": "10-Q"},
            {"end": "2025-12-31", "val": 71890730000, "accn": K, "form": "10-K"},
            {
                "end": "2025-12-31",
                "val": 16470902000,
                "accn": "0000007323-26-000009",
                "form": "10-K",
            },
        ]
    },
    "ENTERGY CORPORATION",
)


@pytest.fixture
def roles(monkeypatch):
    table = {
        "0000065984": {Q2: ("primary", ["0000007323"]), K: ("primary", ["0000007323"])},
        "0000007323": {
            Q2: ("co_registrant", ["0000065984"]),
            K: ("co_registrant", ["0000065984"]),
        },
    }
    monkeypatch.setattr(rl, "registrant_roles", lambda conn, cik: table.get(cik, {}))
    monkeypatch.setenv(rule_flags.ENV_VAR, rule_flags.RULE_SHARED_ACCESSION_PRIMARY)
    return table


def loader(co_cik):
    return (777, EAI_PAYLOAD) if co_cik == "0000007323" else None


def accns(payload):
    return sorted(
        e["accn"]
        for c in payload["facts"].values()
        for t in c.values()
        for u in t["units"].values()
        for e in u
    )


@pytest.mark.unit
def test_flag_off_payload_is_returned_untouched(monkeypatch):
    monkeypatch.delenv(rule_flags.ENV_VAR, raising=False)
    monkeypatch.setattr(
        rl, "registrant_roles", lambda *a: pytest.fail("must not even look")
    )
    assert rl.adjust_payload(None, "0000065984", ETR_OWN, loader) is ETR_OWN
    assert rl.filings_to_skip(None, "0000007323") == set()


@pytest.mark.unit
def test_primary_gets_the_10q_that_sec_served_under_the_subsidiary(roles):
    merged = rl.adjust_payload(None, "0000065984", ETR_OWN, loader)
    assets = merged["facts"]["us-gaap"]["Assets"]["units"]["USD"]
    by_accn = {e["accn"]: e for e in assets}
    assert set(by_accn) == {
        K,
        Q2,
    }  # the subsidiary's own 10-K (0000007323-26-000009) is NOT pulled in
    assert by_accn[Q2]["val"] == 79002618000 and by_accn[Q2][rl.RAW_OBJECT_KEY] == 777
    assert (
        rl.RAW_OBJECT_KEY not in by_accn[K]
    )  # own entry keeps the company's own raw object
    assert (
        len(assets) == 2
    )  # the duplicate FY2025 Assets copy served under 7323 is not added twice


@pytest.mark.unit
def test_subsidiary_payload_loses_the_shared_accessions_but_keeps_its_own(roles):
    mine = rl.adjust_payload(None, "0000007323", EAI_PAYLOAD, loader)
    assert accns(mine) == ["0000007323-26-000009"]
    assert rl.filings_to_skip(None, "0000007323") == {Q2, K}
    assert rl.filings_to_skip(None, "0000065984") == set()


@pytest.mark.unit
def test_adjust_payload_does_not_mutate_its_inputs_and_is_idempotent(roles):
    before = (
        json.dumps(EAI_PAYLOAD, sort_keys=True),
        json.dumps(ETR_OWN, sort_keys=True),
    )
    once = rl.adjust_payload(None, "0000065984", ETR_OWN, loader)
    twice = rl.adjust_payload(None, "0000065984", once, loader)
    assert json.dumps(once, sort_keys=True) == json.dumps(twice, sort_keys=True)
    assert (
        json.dumps(EAI_PAYLOAD, sort_keys=True),
        json.dumps(ETR_OWN, sort_keys=True),
    ) == before


@pytest.mark.unit
def test_company_with_no_registrant_rows_is_untouched_even_with_the_flag_on(roles):
    other = _payload(
        {"Assets": [{"end": "2025-12-31", "val": 1, "accn": "0000320193-26-000020"}]}
    )
    assert rl.adjust_payload(None, "0000320193", other, loader) is other


@pytest.mark.unit
def test_identity_stage_does_not_claim_accessions_it_only_co_registers(monkeypatch):
    from scrooner_pipeline.normalizer import identity

    seen = {}
    filings = [
        {"accession_number": Q2, "form": "10-Q"},
        {"accession_number": "0000007323-26-000009", "form": "10-K"},
    ]
    monkeypatch.setattr(
        identity,
        "load_company_identity",
        lambda storage, conn, cik: {
            "cik": cik,
            "company_name": "ENTERGY ARKANSAS",
            "fiscal_year_end": "1231",
            "listings": [],
            "filings": list(filings),
            "raw_submission_id_by_filing": [(f, 9) for f in filings],
        },
    )
    monkeypatch.setattr(identity, "upsert_company", lambda *a, **k: 142)
    monkeypatch.setattr(identity, "upsert_listings", lambda *a, **k: 0)
    monkeypatch.setattr(
        identity,
        "upsert_filings",
        lambda conn, company_id, fl, pairs: (
            seen.update(
                filings=[f["accession_number"] for f in fl],
                pairs=[p[0]["accession_number"] for p in pairs],
            )
            or len(fl)
        ),
    )
    monkeypatch.setattr(identity, "filings_to_skip", lambda conn, cik: {Q2})
    identity.normalize_identity_for_cik(None, None, "0000007323")
    assert seen == {
        "filings": ["0000007323-26-000009"],
        "pairs": ["0000007323-26-000009"],
    }
    monkeypatch.setattr(identity, "filings_to_skip", lambda conn, cik: set())
    identity.normalize_identity_for_cik(None, None, "0000007323")
    assert seen["filings"] == [Q2, "0000007323-26-000009"]
