"""Filings missing from the FSN store are told apart from quarters that cannot be derived (data chief's #1 blocker,
2026-11-09: the fsn-notes bucket stops at the 2026m09 set, so the latest 10-Q of ~319 companies is not stored and the
pilot reported those keys as quarter_not_printed_or_derivable); a pre-run coverage check counts them; and a new SEC
set can be added at the bucket's top level, where the shard lists sets."""

import gzip
from datetime import date

import httpx
import pytest

from scrooner_pipeline.fsn_store import extract_sec as ex
from scrooner_pipeline.fsn_store import pilot

Q3 = date(2026, 9, 30)
STORED = [
    date(2026, 3, 31),
    date(2026, 6, 30),
]  # through the 10-Q for June; the September 10-Q not stored


def _cause(
    concept="revenue_sanity_resolved", grain="Q", end=Q3, periods=STORED, mapped=None
):
    mapped = (
        {"revenue_sanity_resolved", "total_assets_resolved"}
        if mapped is None
        else mapped
    )
    return pilot.gap_cause(
        concept,
        grain,
        end,
        "general",
        {"revenue_sanity_resolved", "total_assets_resolved"},
        mapped,
        periods,
    )


def test_a_key_whose_filing_is_not_stored_is_filing_not_in_store():
    assert _cause() == "filing_not_in_store"
    assert _cause(concept="total_assets_resolved", grain="I") == "filing_not_in_store"


def test_a_stored_filing_keeps_the_derivation_causes():
    assert _cause(end=date(2026, 6, 30)) == "quarter_not_printed_or_derivable"
    assert (
        _cause(concept="total_assets_resolved", grain="I", end=date(2026, 6, 30))
        == "no_face_print_for_period"
    )
    # a 52-53 week quarter end (2026-06-27) is the June filing, within 10 days
    assert _cause(end=date(2026, 6, 27)) == "quarter_not_printed_or_derivable"


def test_rule_and_definition_causes_come_first():
    assert _cause(concept="capex_resolved") == "no_concept_rule"


def _calendar(tmp_path, rows):
    p = tmp_path / "cal.csv.gz"
    with gzip.open(p, "wt") as fh:
        fh.write(
            "company_id,cik,fiscal_year,fiscal_period,period_type,period_start,period_end\n"
        )
        for cid, end in rows:
            fh.write(f"{cid},{cid:010d},2026,Q3,duration,2026-07-01,{end}\n")
    return p


def test_store_coverage_counts_companies_without_their_newest_expected_filing(tmp_path):
    cal = _calendar(
        tmp_path,
        [(1, "2026-06-30"), (1, "2026-09-30"), (2, "2026-09-26"), (3, "2026-06-30")],
    )
    expected = pilot.newest_expected(cal, {1, 2, 3})
    assert expected == {1: Q3, 2: date(2026, 9, 26), 3: date(2026, 6, 30)}
    rep = pilot.store_coverage(expected, {1: STORED, 2: [date(2026, 9, 30)], 3: STORED})
    assert rep["companies"] == 3 and rep["newest_filing_missing"] == 1
    assert rep["missing"] == {1: "2026-09-30"} and rep["missing_by_period_end"] == {
        "2026-09-30": 1
    }


# ---------------------------------------------------------------- adding a new SEC set to the bucket
def test_a_set_sec_has_not_published_writes_nothing(tmp_path, monkeypatch):
    def not_yet(s, dest, ua):
        raise ex.NotPublished(s)

    monkeypatch.setattr(ex, "download_zip", not_yet)
    assert ex.run_set(
        "2026m11", {"0000320193"}, tmp_path, "ua", apply=True, prefix=""
    ) == {"published": 0}
    assert not list(tmp_path.iterdir())


def test_download_reports_a_404_as_not_published(tmp_path, monkeypatch):
    def handler(request):
        return httpx.Response(404)

    client = httpx.Client(transport=httpx.MockTransport(handler))
    monkeypatch.setattr(
        ex.httpx, "stream", lambda method, url, **k: client.stream(method, url)
    )
    with pytest.raises(ex.NotPublished):
        ex.download_zip("2026m11", tmp_path / "z.zip", "ua")


def test_a_cohort_set_goes_to_the_top_level_where_the_shard_lists_sets(
    monkeypatch, tmp_path
):
    sent = []
    monkeypatch.setenv("SUPABASE_URL", "https://example.invalid")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "k")
    monkeypatch.setattr(
        ex.httpx,
        "post",
        lambda url, **k: (
            sent.append(url) or httpx.Response(200, request=httpx.Request("POST", url))
        ),
    )
    f = tmp_path / "x.tsv.zst"
    f.write_bytes(b"x")
    assert ex.upload("2026m10", "sub", f, "") == "2026m10/2026m10_sub.tsv.zst"
    assert ex.upload("2026m10", "sub", f) == "predecessors/2026m10/2026m10_sub.tsv.zst"
    assert sent[0].endswith("/object/fsn-notes/2026m10/2026m10_sub.tsv.zst")
    with pytest.raises(ValueError):
        ex.run_set("2026m10", set(), tmp_path, "ua", apply=False, prefix="elsewhere/")
