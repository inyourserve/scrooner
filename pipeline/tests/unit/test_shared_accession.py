import pytest

from scrooner_pipeline.common import rule_flags
from scrooner_pipeline.normalizer import shared_accession as sa

ETR, ARK = "0000065984", "0000007323"
ACC = "0000065984-26-000012"


def f(acc, form="10-K"):
    return {"accession_number": acc, "form": form}


def test_registrants_only_shared_accessions():
    shared = sa.registrants_by_accession(
        {ETR: [f(ACC), f("0000065984-26-000013")], ARK: [f(ACC)]}
    )
    assert list(shared) == [ACC]
    assert set(shared[ACC]) == {ETR, ARK}


def test_header_and_prefix_beat_a_wrong_carrier():
    # FILING-CHECKED 2026-10-26: 0000065984-26-000283 header first FILER = Entergy Corp,
    # prefix = Entergy Corp, but SEC companyfacts carries it under Arkansas
    d = sa.decide("0000065984-26-000283", [ARK, ETR], [ARK], "10-Q", header_first_filer=ETR)
    assert d.primary_cik == ETR and d.basis == "header+prefix"
    assert sa.carrier_conflict(d)


def test_payload_and_prefix_beat_a_disagreeing_header():
    # Southern Co 2017 10-K: header lists Alabama Power first
    a, s = "0000003153", "0000092122"
    d = sa.decide("0000092122-17-000024", [a, s], [s], "10-K", header_first_filer=a)
    assert d.primary_cik == s and d.basis == "prefix+payload"
    assert not sa.carrier_conflict(d)


def test_all_three_agree():
    d = sa.decide(ACC, [ARK, ETR], [ETR], "10-K", header_first_filer=ETR)
    assert (d.primary_cik, d.basis) == (ETR, "header+prefix+payload")


def test_one_signal_is_not_enough():
    assert sa.decide(ACC, [ARK, ETR], [], "10-K").primary_cik is None  # prefix only
    assert sa.decide("0000999999-26-000001", [ARK, ETR], [ETR], "10-K").primary_cik is None  # carrier only
    assert sa.decide("0000999999-26-000001", [ARK, ETR], [], "10-K", ETR).primary_cik is None  # header only


def test_two_signals_without_header():
    d = sa.decide(ACC, [ARK, ETR], [ETR], "10-Q")
    assert (d.primary_cik, d.basis) == (ETR, "prefix+payload")


def test_non_periodic_without_payload_never_moves():
    d = sa.decide(ACC, [ARK, ETR], [], "8-K", header_first_filer=ETR)
    assert d.primary_cik is None
    assert d.quarantine_reason == "non_periodic_without_payload_evidence"


def test_three_way_disagreement_quarantines():
    d = sa.decide("0000000001-26-000001", [ARK, ETR, "0000000001"], [ARK], "10-K", header_first_filer=ETR)
    assert d.primary_cik is None and d.quarantine_reason == "signals_do_not_agree"


def test_two_payloads_carry_and_nothing_else_quarantines():
    d = sa.decide("0000999999-26-000001", [ARK, ETR], [ARK, ETR], "10-K")
    assert d.primary_cik is None
    assert d.quarantine_reason == "multiple_companyfacts_payloads_carry_accession"


def test_carrier_outside_registrants_is_ignored():
    d = sa.decide(ACC, [ARK, ETR], ["0000000001"], "10-K", header_first_filer=ETR)
    assert (d.primary_cik, d.basis) == (ETR, "header+prefix")


def test_registrant_rows_roles_and_check_constraint_shape():
    d = sa.decide(ACC, [ARK, ETR], [ETR], "10-K")
    rows = sa.registrant_rows([d], {ETR: 694, ARK: 142})
    roles = {r["registrant_cik"]: r["role"] for r in rows}
    assert roles == {ETR: "primary", ARK: "co_registrant"}
    assert all(r["quarantine_reason"] is None for r in rows)
    q = sa.registrant_rows([sa.decide("0000999999-26-000001", [ARK, ETR], [ARK, ETR], "10-K")], {})
    assert {r["role"] for r in q} == {"quarantined"}
    assert all(r["quarantine_reason"] for r in q)


def test_build_plan_asks_only_registrants_about_shared_accessions():
    asked = []

    def carriers(cik, wanted):
        asked.append((cik, set(wanted)))
        return wanted if cik == ETR else set()

    plan = sa.build_plan(
        {ETR: [f(ACC), f("0000065984-26-000013")], ARK: [f(ACC)]}, carriers
    )
    assert [d.primary_cik for d in plan] == [ETR]
    assert all(w == {ACC} for _, w in asked)


def test_apply_refuses_when_rule_off(monkeypatch):
    monkeypatch.delenv(rule_flags.ENV_ENABLED, raising=False)
    with pytest.raises(RuntimeError):
        sa.apply_decisions(object(), [], {})


def test_rule_registered_and_off_by_default(monkeypatch):
    monkeypatch.delenv(rule_flags.ENV_ENABLED, raising=False)
    monkeypatch.delenv(rule_flags.ENV_DRYRUN, raising=False)
    assert sa.RULE_ID in rule_flags.RULES
    assert rule_flags.rule_enabled(sa.RULE_ID) is False
