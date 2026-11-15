"""Onboarding helpers: no-filing classification, predecessor detection from SEC data (injected loaders), the
reviewed-history validator, and the structure of the two onboarding workflows. No database, no network."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from scrooner_pipeline.onboarding import history_apply, no_filing, predecessors

ROOT = Path(__file__).resolve().parents[3]


def row(**kw):
    base = {"id": 1, "cik": "0000000001", "first_10k_period": date(2015, 12, 31), "predecessor_to": None, "n_filings": 10}
    return {**base, **kw}


@pytest.mark.unit
def test_no_filing_rule_matches_the_five_hard_coded_ciks():
    rows = [
        row(cik="0001594805", first_10k_period=date(2024, 12, 31)),  # SHOP
        row(cik="0001996810", first_10k_period=date(2024, 12, 31)),  # GEV
        row(cik="0002023554", first_10k_period=date(2025, 6, 27)),  # SNDK
        row(cik="0002115436", predecessor_to=date(2026, 3, 31)),  # ExxonMobil Holdings
        row(cik="0002012383", predecessor_to=date(2024, 6, 30)),  # BlackRock Inc
        row(cik="0001321655", first_10k_period=date(2020, 12, 31)),  # PLTR: has 10-Ks since 2020
        row(cik="0001543151", first_10k_period=date(2019, 12, 31)),
        row(cik="0000000009", n_filings=0),  # nothing loaded: unknown, never no_filing
    ]
    assert no_filing.no_filing_ciks(rows) == ["0001594805", "0001996810", "0002012383", "0002023554", "0002115436"]
    assert no_filing.classify(rows[-1])[0] == "unknown"
    assert no_filing.classify(row(first_10k_period=None))[0] == "no_filing"


@pytest.mark.unit
def test_cutoff_is_an_input():
    r = row(first_10k_period=date(2020, 12, 31))
    assert no_filing.classify(r, date(2020, 1, 1))[0] == "no_filing"
    assert no_filing.classify(r, date(2021, 1, 1))[0] == "has_filing"


HEADER = """<SEC-HEADER>FILER:
 COMPANY DATA: COMPANY CONFORMED NAME: NEWCO INC CENTRAL INDEX KEY: 0002000001
FILER:
 COMPANY DATA: COMPANY CONFORMED NAME: OLDCO CORP CENTRAL INDEX KEY: 0000012345
</SEC-HEADER>"""


def _subs(forms):
    return [{"accessionNumber": a, "form": f, "filingDate": d, "reportDate": r} for a, f, d, r in forms]


@pytest.mark.unit
def test_header_filers_excludes_own_cik():
    assert predecessors.header_filers(HEADER, "2000001") == ["0000012345"]


@pytest.mark.unit
def test_detect_proposes_a_predecessor_window_from_an_8k12b():
    subs = {
        "0002000001": _subs([("0001-24-000001", "8-K12B", "2024-03-01", ""), ("0001-25-000002", "10-K", "2025-02-20", "2024-12-31")]),
        "0000012345": _subs([("x1", "10-K", "2015-02-20", "2014-12-31"), ("x2", "10-Q", "2024-02-01", "2023-12-31"),
                             ("x3", "8-K", "2024-02-02", "2024-02-01")]),
    }
    rows, queue = predecessors.detect_company(
        7, "0002000001", lambda c: subs[c], lambda cik, adsh: HEADER, ["Old Name"], lambda c: "OLDCO CORP"
    )
    assert queue == []
    (r,) = rows
    assert (r["company_id"], r["source_cik"], r["relation"]) == (7, "0000012345", "predecessor")
    assert (r["valid_from"], r["valid_to"], r["filings"]) == ("2014-01-01", "2023-12-31", "2")  # the 8-K is not periodic
    assert r["status"] == "PROPOSED_REVIEW" and r["klass"] == "" and "Old Name" in r["evidence"]
    # the proposal is not applicable until a reviewer fills klass
    assert any("not reviewed" in p for p in history_apply.validate(rows))
    assert history_apply.validate([{**r, "klass": "A"}]) == []


@pytest.mark.unit
def test_uncertain_detection_goes_to_the_queue_not_to_a_row():
    late = {"0002000002": _subs([("a", "10-K", "2019-03-01", "2018-12-31")])}
    rows, queue = predecessors.detect_company(8, "0002000002", lambda c: late[c], lambda *a: "", [])
    assert rows == [] and queue[0]["reason"] == "late_first_filing_no_predecessor_found"
    # an 8-K12B whose header lists only the successor (live: ExxonMobil Holdings, BlackRock Inc) is queued, not guessed
    only_self = {"0002000004": _subs([("s", "8-K12B", "2026-07-01", ""), ("t", "10-Q", "2026-08-01", "2026-06-30")])}
    rows, queue = predecessors.detect_company(
        10, "0002000004", lambda c: only_self[c], lambda *a: "CENTRAL INDEX KEY: 0002000004", ["BlackRock, Inc."]
    )
    assert rows == [] and [q["reason"] for q in queue] == ["successor_notice_without_predecessor_cik"]
    assert "BlackRock, Inc." in queue[0]["detail"]
    # a candidate that filed nothing periodic in the window is queued too
    subs = {"0002000003": _subs([("e", "8-K12G3", "2020-01-01", "")]), "0000012345": _subs([("z", "8-K", "2020-01-02", "")])}
    rows, queue = predecessors.detect_company(9, "0002000003", lambda c: subs[c], lambda *a: HEADER.replace("2000001", "2000003"), [])
    assert rows == [] and queue[0]["reason"] == "candidate_without_periodic_filing_in_window"


@pytest.mark.unit
def test_existing_rows_are_skipped():
    r = {"company_id": "7", "source_cik": "0000012345"}
    assert predecessors.drop_existing([r], {(7, "0000012345")}) == []
    assert predecessors.drop_existing([r], set()) == [r]


@pytest.mark.unit
def test_history_validate_refuses_bad_rows():
    ok = {"company_id": "1", "source_cik": "0000000002", "relation": "predecessor", "source_name": "x",
          "valid_from": "2014-01-01", "valid_to": "2020-06-30", "reason": "r", "evidence": "", "klass": "A"}
    assert history_apply.validate([ok]) == []
    assert history_apply.validate([{**ok, "valid_to": "2020-06-29"}])  # not a month end
    assert history_apply.validate([{**ok, "relation": "other"}])
    assert history_apply.validate([ok, {**ok, "source_cik": "0000000003", "valid_from": "2019-01-01", "valid_to": "2021-01-31"}])  # overlap
    assert history_apply.validate([ok, ok])  # duplicate key


@pytest.mark.unit
def test_top100_flow_has_no_hard_coded_no_filing_list():
    text = (ROOT / "scripts/top100_flow.sh").read_text()
    assert "2115436" not in text and "1996810" not in text  # the old NOFILE CIKs
    assert "onboarding.no_filing" in text and '--no-filing-ciks "$NOFILE"' in text


@pytest.mark.unit
def test_norm_ciks_shards_and_tickers():
    from scrooner_pipeline.onboarding import ciks

    assert ciks.norm_ciks("320193, 0000789019\n320193") == ["0000320193", "0000789019"]
    with pytest.raises(ValueError):
        ciks.norm_ciks("12ab")
    assert ciks.shard(["1", "2", "3", "4", "5"], 2) == ["1,3,5", "2,4"]
    assert ciks.shard(["1"], 8) == ["1"]
    with pytest.raises(ValueError):
        ciks.shard(["1"], 0)
    sec = {"0": {"cik_str": 320193, "ticker": "AAPL"}}
    assert ciks.tickers_to_ciks(["aapl"], sec) == ["0000320193"]
    with pytest.raises(ValueError):
        ciks.tickers_to_ciks(["ZZZZ"], sec)


@pytest.mark.unit
@pytest.mark.parametrize("name",["onboard-company-identity.yml", "onboard-company-filings.yml"])
def test_onboarding_workflows_are_guarded(name):
    """Text-level parse (pyyaml is not a pipeline dependency)."""
    text = (ROOT / ".github/workflows" / name).read_text()
    apply_input = text.split("      apply:")[1].split("\n\n")[0]
    assert "default: false" in apply_input  # dry run by default
    assert "group: manual-db-jobs" in text and "cancel-in-progress: false" in text
    assert 'GITHUB_REF" != "refs/heads/main"' in text  # main only
    assert "heavy_job_guard.sh wait-for-write" in text and "heavy_job_guard.sh refuse-if-heavy" in text
    assert 'SCROONER_EDGAR_MAX_RPS: "2"' in text and 'SEC_MAX_REQUESTS_PER_SECOND: "2"' in text
    assert "golden" not in text  # --ciks always set, never the golden fallback
    assert name in (ROOT / "scripts/ci/heavy_job_guard.sh").read_text()  # registered with the guard
