"""Backbone 2026-11-22 (SYSTEMS.md #14/#15): draw size for a <=1.5% bound, stratified draw, one registry row per
company with the history beside it, the mechanical re-check and the weekly certified re-check. (The flow gate reuses the flow self-check,
`certify_display.py --self-check-dir`, tested in test_display_cert_self_check.py.)"""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from decimal import Decimal as D
from pathlib import Path

import pytest

from scrooner_pipeline.certification import display_cert as dc
from scrooner_pipeline.certification import recheck as rc

REPO = Path(__file__).resolve().parents[3]
ACC = "0000000001-24-000001"
HDR = [
    "rank",
    "ticker",
    "company_id",
    "data_point",
    "fiscal_year",
    "period_end",
    "shown_value",
    "accession",
    "r_page",
    "tag",
    "parts",
    "display",
    "reason_code",
    "hide_class",
]


def row(dp, display=dc.SHOWN, value="100", hide_class="", ticker="T", cid="7"):
    shown = display == dc.SHOWN
    return [
        "1",
        ticker,
        cid,
        dp,
        "2023",
        "2023-12-31",
        value if shown else "",
        ACC if shown else "",
        "R4" if shown else "",
        "Revenues" if shown else "",
        "",
        display,
        "",
        hide_class,
    ]


def write(path: Path, rows: list[list[str]]) -> Path:
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(HDR)
        w.writerows(rows)
    return path


def fact(tag, value, qtrs=4):
    return dc.Fact(ACC, tag, "2023-12-31", qtrs, "", D(value), ("R4",))


class Src:
    def __init__(self, facts=(), company=()):
        self.f, self.c = list(facts), list(company)

    def facts(self, accessions, tags):
        return self.f

    def company_facts(self, cik, tags):
        return [*self.c, fact("Assets", "1", qtrs=0)]

    def periodic_year_ends(self, cik):
        return {ACC: ["2023-12-31"]}

    def presented_lines(self, cik, tags):
        return {ACC: {"Assets"}}


def shown_cell(dp, fy, badge=None, parts=(), tag="Revenues"):
    return dc.Cell(
        dp, str(fy), "2023-12-31", dc.SHOWN, D(1), ACC, "R4", tag, parts, badge=badge
    )


# ---------------------------------------------------------------- 1. draw size and strata
def test_draw_size_is_the_smallest_n_with_a_bound_at_most_1_5_percent():
    # n >= ln(0.05) / ln(1 - 0.015) = 198.2 -> 199
    assert dc.DRAW_SIZE == dc.required_draw_size() == 199
    assert dc.clopper_pearson_upper(0, 199) <= 0.015 < dc.clopper_pearson_upper(0, 198)
    assert dc.required_draw_size(0.01) == 299


def test_draw_is_stratified_by_statement_and_badge_class():
    st = {"rev": "income_statement", "ap": "balance_sheet", "tl": "balance_sheet"}
    part = dc.Part("X", "", D(1), ACC, "R4")
    cells = (
        [shown_cell("rev", i) for i in range(900)]
        + [
            shown_cell("ap", i, badge="combined:x", parts=(part, part))
            for i in range(99)
        ]
        + [shown_cell("tl", 0, tag="")]  # one derived cell (no tag, no parts)
    )
    s = dc.strata(cells, statements=st)
    assert s == {
        "balance_sheet|combined": (99, 20),
        "balance_sheet|derived": (1, 1),  # a stratum is never left undrawn
        "income_statement|as_printed": (900, 178),
    }
    d = dc.draw(cells, "seed", statements=st)
    assert len(d) == 199
    got = {k: sum(1 for c in d if dc.stratum(c, st) == k) for k in s}
    assert got == {k: a for k, (_m, a) in s.items()}
    assert d == dc.draw(cells, "seed", statements=st)


def test_allocation_caps_at_the_pool_and_never_exceeds_a_stratum():
    assert dc.allocate({"a": 3, "b": 2}, 199) == {"a": 3, "b": 2}
    a = dc.allocate({"a": 500, "b": 5, "c": 1}, 199)
    assert sum(a.values()) == 199 and a["c"] == 1 and a["b"] <= 5
    assert dc.allocate({"a": 10, "b": 10, "c": 10}, 2) == {"a": 1, "b": 1, "c": 0}


def test_certificate_records_n_bound_and_strata(tmp_path):
    cov = write(tmp_path / "c.csv", [row(f"d{i}") for i in range(250)])
    run = dc.certify("T", "1", cov, Src([fact("Revenues", "100")]))
    assert run.verdict == "PASS" and len(run.shown) == 199
    cert = dc.certificate(run, None, "2026-11-22", "Ritwik (cloud)")
    b = cert["bound"]
    assert (b["n"], b["errors"], b["required_n"], b["pool"], b["census"]) == (
        199,
        0,
        199,
        250,
        False,
    )
    assert float(b["upper_95"]) <= 0.015 and b["target_upper_95"] == "0.015000"
    assert sum(x["drawn"] for x in b["strata"]) == 199
    assert sum(1 for c in cert["cells"] if c["evidence"] == "drawn") == 199
    assert "1.49%" in dc.render(run, "2026-11-22")


# ---------------------------------------------------------------- mechanical re-check
def test_mechanical_run_draws_nothing_still_fails_a_bad_hide_and_is_never_a_certificate(
    tmp_path,
):
    cov = write(
        tmp_path / "c.csv",
        [
            row("revenue"),
            row("sbc", dc.HIDDEN_ROW, hide_class="structural_not_presented"),
        ],
    )
    ok = dc.certify("T", "1", cov, Src([fact("Revenues", "100")]), mechanical=True)
    assert ok.verdict == "PASS" and ok.shown == [] and ok.mechanical
    with pytest.raises(ValueError):
        dc.certificate(ok, None, "d", "a")
    # the hidden row has a family fact in a periodic filing: the census catches it with no draw
    bad = dc.certify(
        "T",
        "1",
        cov,
        Src([fact("Revenues", "100")], company=[fact("ShareBasedCompensation", "3")]),
        mechanical=True,
    )
    assert bad.verdict == "FAIL"


# ---------------------------------------------------------------- 2. registry dedupe
def _reg_row(t, d, v):
    return {
        "ticker": t,
        "date": d,
        "verdict": v,
        "coverage_sha256": "s",
        "seed": "x",
        "n": 199,
        "errors": 0,
        "upper_bound_95": "0.014941",
        "approver": "R",
    }


def test_record_verdict_keeps_one_latest_row_per_company_and_the_full_history(tmp_path):
    reg = tmp_path / "registry.csv"
    # a legacy registry with duplicate rows seeds the history first: nothing is lost
    with open(reg, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=dc.REGISTRY_HEADER)
        w.writeheader()
        for r in (
            _reg_row("A", "2026-11-16", "PASS"),
            _reg_row("A", "2026-11-16", "FAIL"),
        ):
            w.writerow(r)
    dc.record_verdict(reg, _reg_row("B", "2026-11-20", "FAIL"))
    dc.record_verdict(reg, _reg_row("B", "2026-11-22", "PASS"))
    rows = list(csv.DictReader(open(reg)))
    hist = list(csv.DictReader(open(dc.history_path(reg))))
    assert [(r["ticker"], r["verdict"]) for r in rows] == [("A", "FAIL"), ("B", "PASS")]
    assert len(hist) == 4 and dc.registry_problems(reg) == []
    assert dc.certified_tickers(reg) == ["B"]
    # a duplicate written by hand is reported
    with open(reg, "a", newline="") as fh:
        csv.DictWriter(fh, fieldnames=dc.REGISTRY_HEADER).writerow(
            _reg_row("B", "2026-11-22", "PASS")
        )
    assert "B: more than one registry row" in dc.registry_problems(reg)


def test_a_crlf_registry_with_a_hand_appended_row_is_reported_and_record_verdict_heals_it(
    tmp_path,
):
    reg = tmp_path / "registry.csv"
    hist = dc.history_path(reg)
    for f in (reg, hist):
        with open(f, "w", newline="") as fh:  # the csv default: CRLF
            w = csv.DictWriter(fh, fieldnames=dc.REGISTRY_HEADER)
            w.writeheader()
            w.writerow(_reg_row("A", "2026-11-16", "PASS"))
        f.write_bytes(
            f.read_bytes()[:-3] + b'"R\r"\n'
        )  # the damage seen on main: a quoted CR in the last field
    assert any("carriage return" in p for p in dc.registry_problems(reg))
    assert any("malformed row for 'A'" in p for p in dc.registry_problems(reg))
    dc.record_verdict(reg, _reg_row("B", "2026-11-22", "PASS"))
    assert b"\r" not in reg.read_bytes() and b"\r" not in hist.read_bytes()
    assert dc.registry_problems(reg) == []
    assert [r["approver"] for r in csv.DictReader(open(reg))] == ["R", "R"]


def test_committed_registry_has_one_row_per_company_matching_its_history():
    reg = REPO / "data-team/strategy/approvals/registry.csv"
    assert dc.history_path(reg).exists()
    assert dc.registry_problems(reg) == []


def _bundle(tmp_path: Path) -> Path:
    b = tmp_path / "b.json"
    b.write_text(
        json.dumps(
            {
                "facts": [[ACC, "Revenues", "2023-12-31", 4, "", "100", ["R4"]]],
                "company_facts": [[ACC, "Assets", "2023-12-31", 0, "", "1", ["R2"]]],
                "year_ends": {ACC: ["2023-12-31"]},
            }
        )
    )
    return b


def test_certify_display_cli_dedupes_the_registry_and_writes_the_approver(tmp_path):
    cov = write(tmp_path / "c.csv", [row("revenue")])
    reg = tmp_path / "registry.csv"
    cmd = [
        sys.executable,
        str(REPO / "pipeline/scripts/certify_display.py"),
        "--ticker",
        "T",
        "--cik",
        "1",
        "--coverage",
        str(cov),
        "--bundle",
        str(_bundle(tmp_path)),
        "--out-dir",
        str(tmp_path / "o"),
        "--registry",
        str(reg),
    ]
    for _ in range(2):
        assert (
            subprocess.run(cmd, capture_output=True, text=True, cwd=REPO).returncode
            == 0
        )
    rows = list(csv.DictReader(open(reg)))
    assert len(rows) == 1 and rows[0]["approver"] == "Ritwik (cloud)"
    assert len(list(csv.DictReader(open(dc.history_path(reg))))) == 2
    cert = json.loads(next((tmp_path / "o").glob("T-display-cert-*.json")).read_text())
    assert cert["bound"]["n"] == 1 and cert["bound"]["census"] is True
    # --mechanical: a report only, no certificate and no registry row
    m = subprocess.run(
        [
            *cmd[:-2],
            "--registry",
            str(tmp_path / "r2.csv"),
            "--out-dir",
            str(tmp_path / "m"),
            "--mechanical",
        ],
        capture_output=True,
        text=True,
        cwd=REPO,
    )
    assert m.returncode == 0, m.stdout + m.stderr
    assert not (tmp_path / "r2.csv").exists() and not list(
        (tmp_path / "m").glob("*.json")
    )
    assert list((tmp_path / "m").glob("T-mechanical-*.md"))


# ---------------------------------------------------------------- 3. weekly certified re-check
def _registry(tmp_path: Path) -> Path:
    reg = tmp_path / "registry.csv"
    for r in (_reg_row("T", "2026-11-22", "PASS"), _reg_row("U", "2026-11-22", "FAIL")):
        dc.record_verdict(reg, r)
    return reg


def test_recheck_opens_a_regression_entry_when_a_certified_company_fails(tmp_path):
    reg = _registry(tmp_path)
    exp = write(
        tmp_path / "export.csv",
        [
            row("revenue"),
            row("sbc", dc.HIDDEN_ROW, hide_class="structural_not_presented"),
            row("revenue", ticker="U", cid="8"),
        ],
    )
    ok = rc.recheck(
        reg,
        exp,
        {"T": "1"},
        lambda t: Src([fact("Revenues", "100")]),
        tmp_path / "w",
        tmp_path / "reg",
        "2026-11-23",
    )
    assert [(r.ticker, r.status) for r in ok] == [("T", "PASS")] and rc.exit_code(
        ok
    ) == 0
    assert not (tmp_path / "reg").exists()
    bad_src = Src(
        [fact("Revenues", "100")], company=[fact("ShareBasedCompensation", "3")]
    )
    bad = rc.recheck(
        reg,
        exp,
        {"T": "1"},
        lambda t: bad_src,
        tmp_path / "w",
        tmp_path / "reg",
        "2026-11-23",
    )
    assert [(r.ticker, r.status) for r in bad] == [
        ("T", "REGRESSION")
    ] and rc.exit_code(bad) == 1
    text = (tmp_path / "reg" / "T-2026-11-23.md").read_text()
    assert "Certified regression: T" in text and "FAIL" in text


def test_recheck_is_loud_on_a_missing_company_and_on_a_broken_source(tmp_path):
    reg = _registry(tmp_path)
    exp = write(tmp_path / "export.csv", [row("revenue", ticker="U", cid="8")])
    miss = rc.recheck(
        reg, exp, {"T": "1"}, lambda t: Src(), tmp_path / "w", tmp_path / "reg", "d"
    )
    assert miss[0].status == "REGRESSION" and rc.exit_code(miss) == 1
    exp2 = write(tmp_path / "export2.csv", [row("revenue")])

    def boom(_t):
        raise RuntimeError("timeout")

    err = rc.recheck(
        reg, exp2, {"T": "1"}, boom, tmp_path / "w", tmp_path / "reg2", "d"
    )
    assert err[0].status == "ERROR" and rc.exit_code(err) == 2


def test_recheck_lists_ids_as_the_workflow_calls_it(tmp_path):
    reg = _registry(tmp_path)
    summ = tmp_path / "s.csv"
    summ.write_text("rank,ticker,company_id\n1,T,7\n2,U,8\n")
    r = subprocess.run(
        [
            sys.executable,
            str(REPO / "pipeline/scripts/recheck_certified.py"),
            "--registry",
            str(reg),
            "--summary",
            str(summ),
            "--list-ids",
        ],
        capture_output=True,
        text=True,
        cwd=REPO,
    )
    assert r.returncode == 0 and r.stdout.strip() == "7"
    summ.write_text(
        "rank,ticker,company_id\n2,U,8\n"
    )  # a certified company that cannot be found is an error
    r = subprocess.run(
        [
            sys.executable,
            str(REPO / "pipeline/scripts/recheck_certified.py"),
            "--registry",
            str(reg),
            "--summary",
            str(summ),
            "--list-ids",
        ],
        capture_output=True,
        text=True,
        cwd=REPO,
    )
    assert r.returncode != 0


def test_weekly_workflow_is_scheduled_read_only_and_fails_loudly():
    wf = (REPO / ".github/workflows/certified-recheck-weekly.yml").read_text()
    assert "schedule:" in wf and "cron:" in wf
    assert "recheck_certified.py --list-ids" in wf and "--live" in wf
    assert (
        "default_transaction_read_only=on" in wf and "--write-display-state" not in wf
    )
    assert "approvals/regressions" in wf and "exit 1;;" in wf
