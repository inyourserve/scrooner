"""Per-company coverage export merge (scripts/ci/top100_coverage_merge.py), the in-flight detector and the
--company-ids filter of the export. Scale plan 2026-11-17 section 6 item 1: flow exports one company; hourly export atomic."""

import csv
import importlib.util
import json
import pathlib
import subprocess
import sys

import pytest
from scrooner_pipeline.mapper.top100_coverage import Company, select_companies

ROOT = pathlib.Path(__file__).resolve().parents[2]


def _load(name: str):
    spec = importlib.util.spec_from_file_location(
        name, ROOT / "scripts/ci" / f"{name}.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


merge = _load("top100_coverage_merge")
inflight = _load("top100_inflight")

SH = ["rank", "ticker", "company_id", "shown_values", "as_of"]
FH = ["rank", "ticker", "company_id", "data_point", "period_end", "display"]


def _write(path: pathlib.Path, header, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=header)
        w.writeheader()
        w.writerows(rows)


def _read(path):
    with path.open(newline="") as fh:
        return list(csv.DictReader(fh))


def _committed(tmp_path):
    into = tmp_path / "strategy"
    _write(
        into / merge.SUMMARY,
        SH,
        [
            {
                "rank": "1",
                "ticker": "NVDA",
                "company_id": "2733",
                "shown_values": "549",
                "as_of": "T0",
            },
            {
                "rank": "2",
                "ticker": "AAPL",
                "company_id": "3",
                "shown_values": "503",
                "as_of": "T0",
            },
            {
                "rank": "4",
                "ticker": "MSFT",
                "company_id": "4",
                "shown_values": "515",
                "as_of": "T0",
            },
        ],
    )
    _write(
        into / merge.FULL,
        FH,
        [
            {
                "rank": "1",
                "ticker": "NVDA",
                "company_id": "2733",
                "data_point": "revenue",
                "period_end": "2026-01-25",
                "display": "PROVEN",
            },
            {
                "rank": "2",
                "ticker": "AAPL",
                "company_id": "3",
                "data_point": "revenue",
                "period_end": "2025-09-27",
                "display": "PROVEN",
            },
            {
                "rank": "2",
                "ticker": "AAPL",
                "company_id": "3",
                "data_point": "eps",
                "period_end": "2025-09-27",
                "display": "OPEN",
            },
            {
                "rank": "4",
                "ticker": "MSFT",
                "company_id": "4",
                "data_point": "revenue",
                "period_end": "2025-06-30",
                "display": "PROVEN",
            },
        ],
    )
    return into


def _export(tmp_path, ids=("3",), shown="540", as_of="T1"):
    src = tmp_path / "export"
    srows = [
        {
            "rank": "2",
            "ticker": "AAPL",
            "company_id": "3",
            "shown_values": shown,
            "as_of": as_of,
        }
    ]
    frows = [
        {
            "rank": "2",
            "ticker": "AAPL",
            "company_id": "3",
            "data_point": "revenue",
            "period_end": "2025-09-27",
            "display": "PROVEN",
        }
    ]
    if "4" in ids:
        srows.append(
            {
                "rank": "4",
                "ticker": "MSFT",
                "company_id": "4",
                "shown_values": "0",
                "as_of": as_of,
            }
        )
        frows.append(
            {
                "rank": "4",
                "ticker": "MSFT",
                "company_id": "4",
                "data_point": "revenue",
                "period_end": "2025-06-30",
                "display": "BLANK",
            }
        )
    _write(src / merge.SUMMARY, SH, [r for r in srows if r["company_id"] in ids])
    _write(src / merge.FULL, FH, [r for r in frows if r["company_id"] in ids])
    return src


def test_one_company_replaces_only_its_own_rows(tmp_path):
    into, src = _committed(tmp_path), _export(tmp_path)
    assert merge.main(["--from", str(src), "--into", str(into)]) == 0
    s = _read(into / merge.SUMMARY)
    assert [r["company_id"] for r in s] == ["2733", "3", "4"], "rank order kept"
    assert {r["company_id"]: r["as_of"] for r in s} == {
        "2733": "T0",
        "3": "T1",
        "4": "T0",
    }
    assert s[1]["shown_values"] == "540"
    f = _read(into / merge.FULL)
    # AAPL had 2 rows (one OPEN eps); the export has 1: the stale eps row must go, NVDA/MSFT rows untouched
    assert [(r["company_id"], r["data_point"]) for r in f] == [
        ("2733", "revenue"),
        ("3", "revenue"),
        ("4", "revenue"),
    ]


def test_keep_ids_leaves_a_mid_reload_company_on_its_committed_row(tmp_path):
    into, src = _committed(tmp_path), _export(tmp_path, ids=("3", "4"))
    assert merge.main(["--from", str(src), "--into", str(into), "--keep-ids", "4"]) == 0
    s = {r["company_id"]: r for r in _read(into / merge.SUMMARY)}
    assert s["4"]["shown_values"] == "515" and s["4"]["as_of"] == "T0", (
        "MSFT in flight: half state (0) not published"
    )
    assert s["3"]["shown_values"] == "540"
    f = {r["company_id"]: r["display"] for r in _read(into / merge.FULL)}
    assert f["4"] == "PROVEN"


def test_company_ids_restricts_what_is_taken_from_the_export(tmp_path):
    into, src = _committed(tmp_path), _export(tmp_path, ids=("3", "4"))
    assert (
        merge.main(["--from", str(src), "--into", str(into), "--company-ids", "3"]) == 0
    )
    s = {r["company_id"]: r["shown_values"] for r in _read(into / merge.SUMMARY)}
    assert s == {"2733": "549", "3": "540", "4": "515"}


def test_summary_only_leaves_the_full_file_alone(tmp_path):
    into, src = _committed(tmp_path), _export(tmp_path)
    before = (into / merge.FULL).read_bytes()
    assert merge.main(["--from", str(src), "--into", str(into), "--summary-only"]) == 0
    assert (into / merge.FULL).read_bytes() == before
    assert {r["company_id"]: r["as_of"] for r in _read(into / merge.SUMMARY)}[
        "3"
    ] == "T1"


def test_header_mismatch_is_an_error_and_the_target_is_untouched(tmp_path):
    into = _committed(tmp_path)
    src = tmp_path / "export"
    _write(
        src / merge.SUMMARY,
        SH + ["extra"],
        [
            {
                "rank": "2",
                "ticker": "AAPL",
                "company_id": "3",
                "shown_values": "1",
                "as_of": "T1",
                "extra": "x",
            }
        ],
    )
    _write(src / merge.FULL, FH, [])
    before = (into / merge.SUMMARY).read_bytes()
    with pytest.raises(SystemExit):
        merge.main(["--from", str(src), "--into", str(into)])
    assert (into / merge.SUMMARY).read_bytes() == before
    assert not list(into.glob("*.tmp")), "no temp file left behind"


def test_new_company_is_appended_and_summary_sorted_by_rank(tmp_path):
    into = _committed(tmp_path)
    src = tmp_path / "export"
    _write(
        src / merge.SUMMARY,
        SH,
        [
            {
                "rank": "3",
                "ticker": "GOOG",
                "company_id": "9",
                "shown_values": "451",
                "as_of": "T1",
            }
        ],
    )
    _write(
        src / merge.FULL,
        FH,
        [
            {
                "rank": "3",
                "ticker": "GOOG",
                "company_id": "9",
                "data_point": "revenue",
                "period_end": "2025-12-31",
                "display": "PROVEN",
            }
        ],
    )
    assert merge.main(["--from", str(src), "--into", str(into)]) == 0
    assert [r["company_id"] for r in _read(into / merge.SUMMARY)] == [
        "2733",
        "3",
        "9",
        "4",
    ]


def test_missing_export_files_exit_2(tmp_path):
    into = _committed(tmp_path)
    assert merge.main(["--from", str(tmp_path / "nothing"), "--into", str(into)]) == 2


def test_cli_runs_isolated(tmp_path):
    into, src = _committed(tmp_path), _export(tmp_path)
    r = subprocess.run(
        [
            sys.executable,
            "-I",
            str(ROOT / "scripts/ci/top100_coverage_merge.py"),
            "--from",
            str(src),
            "--into",
            str(into),
            "--keep-ids",
            "",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert r.returncode == 0, r.stderr
    assert "replaced 1 company(ies) ['3']" in r.stdout


# ---- in-flight detector --------------------------------------------------------------------------------------------


def test_inflight_marks_only_unfinished_company_jobs(tmp_path):
    jobs = {
        "jobs": [
            {
                "name": "Wait while an FSN production write is in progress",
                "status": "completed",
            },
            {"name": "company 85", "status": "completed"},
            {"name": "company 1359", "status": "in_progress"},
            {"name": "company 4630", "status": "queued"},
            {"name": "publish 85", "status": "in_progress"},
        ]
    }
    assert inflight.inflight_from_jobs(jobs["jobs"]) == {"1359", "4630"}
    f = tmp_path / "jobs.json"
    f.write_text(json.dumps(jobs))
    r = subprocess.run(
        [
            sys.executable,
            "-I",
            str(ROOT / "scripts/ci/top100_inflight.py"),
            "--jobs-json",
            str(f),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert r.returncode == 0 and r.stdout.strip() == "1359,4630"


def test_inflight_fails_closed_when_gh_is_unusable(monkeypatch):
    monkeypatch.setenv("PATH", "/nonexistent")
    assert inflight.main([]) == 3


# ---- export filter -------------------------------------------------------------------------------------------------


def test_select_companies_filters_in_rank_order_and_rejects_unknown_ids():
    cos = [
        Company(1, "NVDA", 2733, ""),
        Company(2, "AAPL", 3, ""),
        Company(4, "MSFT", 4, ""),
    ]
    assert select_companies(cos, None) == cos
    assert [c.ticker for c in select_companies(cos, [4, 2733])] == ["NVDA", "MSFT"]
    with pytest.raises(SystemExit):
        select_companies(cos, [4, 99999])


def test_export_cli_parses_company_ids():
    spec = importlib.util.spec_from_file_location(
        "cov_cli", ROOT / "pipeline/scripts/top100_coverage.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    out, write, ids = mod.parse_args(
        ["outdir", "--write-display-state", "--company-ids", "4,3,4"]
    )
    assert (str(out), write, ids) == ("outdir", True, [3, 4])
    assert mod.parse_args([]) == (pathlib.Path("data-team/strategy"), False, None)
    with pytest.raises(SystemExit):
        mod.parse_args(["--company-ids", "x"])
