"""Before-image manifest and restore diff (no database)."""

import hashlib
import json
from decimal import Decimal

from scrooner_pipeline.mapper import ttm_guards_before_image as bi


def row(cid, metric, value, reason=None, end="2026-10-18"):
    return {
        "company_id": cid,
        "cik": "0000001",
        "ticker": "T",
        "metric_name": metric,
        "period_label": "TTM",
        "period_start": end,
        "period_end": end,
        "value": value,
        "is_null_reason": reason,
        "source_fact_ids": None,
    }


def test_manifest_records_rows_and_sha(tmp_path):
    out = tmp_path / "img.csv"
    m = bi.write_before_image(
        [row(225, "ebitda", Decimal("1019295000"))], out, {"ciks": ["0000001"]}
    )
    assert (
        m["rows"] == 1 and m["sha256"] == hashlib.sha256(out.read_bytes()).hexdigest()
    )
    assert (
        json.loads(out.with_suffix(".manifest.json").read_text())["sha256"]
        == m["sha256"]
    )
    assert m["attach_as_artifact"] is False


def test_restore_diff_is_zero_when_values_come_back_on_a_new_date(tmp_path):
    out = tmp_path / "img.csv"
    before = [
        row(225, "ebitda", Decimal("1019295000")),
        row(225, "ev_ebitda", None, "missing:market_cap"),
    ]
    bi.write_before_image(before, out, {})
    restored = [
        row(225, "ebitda", Decimal("1019295000.00"), end="2026-10-23"),
        row(225, "ev_ebitda", None, "missing:market_cap", end="2026-10-23"),
    ]
    assert bi.diff_images(bi.read_image(out), restored) == []


def test_diff_reports_a_guard_effect_and_a_missing_row(tmp_path):
    out = tmp_path / "img.csv"
    bi.write_before_image(
        [row(225, "ebitda", Decimal("5")), row(225, "fcf_per_share", Decimal("1"))],
        out,
        {},
    )
    after = [row(225, "ebitda", None, "guard:non_contiguous_ttm_window:ebitda")]
    diffs = bi.diff_images(bi.read_image(out), after)
    assert {(d["company_id"], d["metric_name"]) for d in diffs} == {
        ("225", "ebitda"),
        ("225", "fcf_per_share"),
    }
