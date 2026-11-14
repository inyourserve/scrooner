"""normalize_facts totals tolerate a predecessor CIK: it has no company of its own, so its result carries only the
predecessor routes (its facts are written under the successors), no counts."""

from contextlib import nullcontext

from scrooner_pipeline.normalizer import facts as F


def test_totals_skip_missing_counts_of_a_predecessor_cik(monkeypatch):
    results = {
        "0000000001": {
            "cik": "0000000001",
            "status": "ok",
            "predecessor_routes": [5351],
        },
        "0000000002": {
            "cik": "0000000002",
            "status": "ok",
            **{k: 1 for k in ("considered", "written")},
        },
    }
    monkeypatch.setattr(F, "SupabaseStorageClient", lambda: nullcontext(None))
    monkeypatch.setattr(
        F, "normalize_facts_for_cik", lambda storage, conn, cik: results[cik]
    )
    out = F.normalize_facts(None, set(results))
    assert out["errored"] == []
