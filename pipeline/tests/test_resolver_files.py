"""resolver_files: per-company resolver layout (scale plan 2026-11-17 s.6 #5). Also guards main against two sources."""

import csv
from pathlib import Path

import pytest

from scrooner_pipeline.mapper import resolver_files as rf

H = [
    "cik",
    "ticker",
    "data_point",
    "period_end",
    "grain",
    "decision",
    "nodes",
    "value",
    "resolver_version",
]


def _all110(tmp_path: Path, name="resolver-all110-2026-11-14.csv", version="v1"):
    rows = [
        {
            "cik": "0000000004",
            "ticker": "MSFT",
            "data_point": "revenue",
            "period_end": "2025-06-30",
            "grain": "FY",
            "decision": "mapped",
            "nodes": "",
            "value": "2",
            "resolver_version": version,
        },
        {
            "cik": "0000000003",
            "ticker": "AAPL",
            "data_point": "revenue",
            "period_end": "2025-09-27",
            "grain": "FY",
            "decision": "mapped",
            "nodes": "",
            "value": "1",
            "resolver_version": version,
        },
        {
            "cik": "0000000003",
            "ticker": "AAPL",
            "data_point": "eps",
            "period_end": "2024-09-28",
            "grain": "FY",
            "decision": "mapped",
            "nodes": "",
            "value": "9",
            "resolver_version": version,
        },
    ]
    p = tmp_path / name
    with p.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=H)
        w.writeheader()
        w.writerows(rows)
    return p


def test_single_file_is_the_fallback_source(tmp_path):
    p = _all110(tmp_path)
    assert rf.resolver_source(tmp_path) == p
    assert rf.resolver_files(tmp_path) == [p]
    assert len(list(rf.iter_rows(tmp_path))) == 3
    assert rf.resolver_version(tmp_path) == "v1"
    assert rf.conflict(tmp_path) == []


def test_split_writes_one_sorted_file_per_ticker_and_the_directory_wins(tmp_path):
    p = _all110(tmp_path)
    counts = rf.split_all110(p, rf.split_dir(tmp_path))
    assert counts == {"AAPL": 2, "MSFT": 1}
    assert rf.resolver_source(tmp_path) == rf.split_dir(tmp_path)
    aapl = list(csv.DictReader((rf.split_dir(tmp_path) / "AAPL.csv").open()))
    assert [r["data_point"] for r in aapl] == ["eps", "revenue"], (
        "sorted by key inside the file"
    )
    assert [r["ticker"] for r in rf.iter_rows(tmp_path)] == ["AAPL", "AAPL", "MSFT"]
    assert [r["ticker"] for r in rf.iter_rows(tmp_path, tickers=["MSFT"])] == ["MSFT"]
    assert (
        rf.iter_rows(tmp_path, tickers=["NOPE"]) is not None
        and list(rf.iter_rows(tmp_path, tickers=["NOPE"])) == []
    )
    assert rf.conflict(tmp_path) == [p], "the stale single file is reported"
    # re-split is byte-identical
    before = (rf.split_dir(tmp_path) / "AAPL.csv").read_bytes()
    rf.split_all110(p, rf.split_dir(tmp_path))
    assert (rf.split_dir(tmp_path) / "AAPL.csv").read_bytes() == before


def test_split_prunes_tickers_no_longer_in_the_source(tmp_path):
    p = _all110(tmp_path)
    rf.split_all110(p, rf.split_dir(tmp_path))
    (rf.split_dir(tmp_path) / "OLD.csv").write_text("cik,ticker\n1,OLD\n")
    rf.split_all110(p, rf.split_dir(tmp_path))
    assert sorted(x.name for x in rf.split_files(tmp_path)) == ["AAPL.csv", "MSFT.csv"]


def test_split_rejects_an_unusable_ticker(tmp_path):
    p = tmp_path / "resolver-all110-2026-11-14.csv"
    p.write_text("cik,ticker,data_point\n1,bad ticker,revenue\n")
    with pytest.raises(ValueError):
        rf.split_all110(p, rf.split_dir(tmp_path))


def test_no_source_at_all(tmp_path):
    assert rf.resolver_source(tmp_path) is None
    assert rf.resolver_files(tmp_path) == []
    assert rf.resolver_version(tmp_path) is None


def test_main_carries_one_resolver_source_only():
    """The repo must not hold a resolver-all110-*.csv next to a non-empty resolver/ directory (two truths)."""
    assert rf.conflict(rf.LINE_MAP_DIR) == []
    assert rf.split_files(rf.LINE_MAP_DIR), (
        "the per-company resolver directory is missing on this checkout"
    )
