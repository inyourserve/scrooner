"""scripts/ci/top100_canary.py: canary snapshot, before/after compare and the gate in top100-auto-trigger."""
import json
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/ci/top100_canary.py"
CAN = "data-team/tags/line_map/canary/companies.csv"
OS_HDR = "work,rank,ticker,company_id,data_point,fiscal_year,period_end,class,reason_code,reason,shown_value,accession,r_page,parts\n"
SUM_HDR = "rank,ticker,company_id,open_shown,gate_ready,verifier_certified\n"
CL = "data-team/tags/line_map/CHANGELOG.md"


def sh(cwd, *a):
    return subprocess.run(a, cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()


def commit(repo, files):
    for p, t in files.items():
        f = repo / p
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(t)
    sh(repo, "git", "add", "-A")
    sh(repo, "git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "c")
    return sh(repo, "git", "rev-parse", "HEAD")


def run(cwd, *a):
    return subprocess.run([sys.executable, str(SCRIPT), *a], cwd=cwd, capture_output=True, text=True)


def os_rows(ticker, cid, plain=0, selfcheck=0, draw=0):
    out = []
    for i in range(plain):
        out.append(f"blank,1,{ticker},{cid},dp{i},2020,2020-12-31,BLANK,x,plain reason,,a,R2.htm,\n")
    for i in range(selfcheck):
        out.append(f"verifier_check,1,{ticker},{cid},sc{i},2021,2021-12-31,OPEN,x,verifier self-check shown: filing differs,,a,R2.htm,\n")
    for i in range(draw):
        out.append(
            f"verifier_check,1,{ticker},{cid},dc{i},2022,2022-12-31,OPEN,x,verifier self-check draw_check: AUTO_MISMATCH (x),,a,R2.htm,\n"
        )
    return OS_HDR + "".join(out)


CANARIES = "ticker,company_id,sector,reason\nAAA,11,bank,r\nCERT,22,certified,r\nZZZ,33,tech,r\n"


@pytest.fixture
def repo(tmp_path):
    r = tmp_path / "repo"
    r.mkdir()
    sh(r, "git", "init", "-q")
    base = commit(
        r,
        {
            CAN: CANARIES,
            CL: "| v |\n| .1 | old row canary-expected: AAA:* |\n",
            "data-team/strategy/top100-coverage-summary.csv": SUM_HDR + "1,AAA,11,3,no,no\n2,CERT,22,0,yes,yes\n3,ZZZ,33,0,no,no\n",
            "data-team/strategy/open-shown/AAA.csv": os_rows("AAA", 11, plain=2, selfcheck=1),
        },
    )
    return r, base


def snap(repo, base, head, tmp):
    out = tmp / "before.json"
    p = run(repo, "snapshot", "--repo", ".", "--base", base, "--head", head, "--out", str(out))
    assert p.returncode == 0, p.stderr
    return out


def art(tmp, cid, rows_text, line):
    d = tmp / "art" / f"flow-{cid}"
    (d / f"publish_c{cid}").mkdir(parents=True, exist_ok=True)
    if rows_text is not None:
        (d / f"publish_c{cid}" / "open-shown.csv").write_text(rows_text)
    if line is not None:
        (d / "flow_results.tsv").write_text(f"10:00Z\t{cid}\t{line}\n")
    return tmp / "art"


def compare(repo, before, a, tmp):
    md = tmp / "fail.md"
    p = run(repo, "compare", "--before", str(before), "--artifacts", str(a), "--sha", "abc123", "--date", "2026-11-22", "--out-md", str(md))
    return p, md


def all_ok(tmp):
    art(tmp, 11, os_rows("AAA", 11, plain=2, selfcheck=1), "AAA shown 1/2 50 open=3 NOT_GATE_READY")
    art(tmp, 22, os_rows("CERT", 22), "CERT shown 5/5 100 open=0 GATE_READY VERIFIER_CERTIFIED")
    return art(tmp, 33, os_rows("ZZZ", 33), "ZZZ shown 5/5 100 open=0 GATE_READY")


def test_ids_and_rest(repo):
    r, _ = repo
    assert run(r, "ids", "--canaries", CAN).stdout.strip() == "11,22,33"
    assert run(r, "rest", "--canaries", CAN, "--ids", "5,11,7,33,5").stdout.strip() == "5,7"
    assert run(r, "rest", "--canaries", CAN, "--ids", "11,22").stdout.strip() == ""
    assert run(r, "rest", "--canaries", CAN, "--ids", "1;rm").returncode == 2


def test_snapshot_reads_main_state_and_only_new_changelog_rows(repo, tmp_path):
    r, base = repo
    head = commit(r, {CL: "| v |\n| .1 | old row canary-expected: AAA:* |\n| .2 | new canary-expected: ZZZ:open_shown, AAA:draw_check_mismatch |\n"})
    b = json.loads(snap(r, base, head, tmp_path).read_text())
    assert b["companies"]["11"] == {
        "ticker": "AAA", "open_shown": 3, "self_check_fail": 1, "draw_check_mismatch": 0, "certified": False
    }
    assert b["companies"]["22"]["certified"] is True and b["companies"]["22"]["open_shown"] == 0  # no file = 0
    assert b["expected"] == {"AAA": ["draw_check_mismatch"], "ZZZ": ["open_shown"]}  # the old row's AAA:* is not this release's


def test_no_regression_passes_and_writes_nothing(repo, tmp_path):
    r, base = repo
    p, md = compare(r, snap(r, base, base, tmp_path), all_ok(tmp_path), tmp_path)
    assert p.returncode == 0, p.stdout + p.stderr
    assert "canary PASS" in p.stdout and not md.exists()


def test_improvement_passes(repo, tmp_path):
    r, base = repo
    all_ok(tmp_path)
    a = art(tmp_path, 11, os_rows("AAA", 11, plain=1), "AAA open=1 NOT_GATE_READY")
    p, md = compare(r, snap(r, base, base, tmp_path), a, tmp_path)
    assert p.returncode == 0 and not md.exists()


@pytest.mark.parametrize(
    "rows,metric",
    [
        (os_rows("AAA", 11, plain=3, selfcheck=1), "open_shown 3 -> 4"),
        (os_rows("AAA", 11, plain=1, selfcheck=2), "self_check_fail 1 -> 2"),
        (os_rows("AAA", 11, plain=1, selfcheck=0, draw=1), "draw_check_mismatch 0 -> 1"),
    ],
)
def test_each_metric_regression_blocks_with_a_failure_file(repo, tmp_path, rows, metric):
    r, base = repo
    all_ok(tmp_path)
    a = art(tmp_path, 11, rows, "AAA open=x NOT_GATE_READY")
    p, md = compare(r, snap(r, base, base, tmp_path), a, tmp_path)
    assert p.returncode == 1, p.stdout
    text = md.read_text()
    assert metric in text and "**BLOCKING**" in text and "| AAA | 11 |" in text and "NOT dispatched" in text


def test_expected_regression_listed_in_changelog_passes(repo, tmp_path):
    r, base = repo
    head = commit(r, {CL: "| v |\n| .2 | rule X | canary-expected: AAA:open_shown |\n"})
    all_ok(tmp_path)
    a = art(tmp_path, 11, os_rows("AAA", 11, plain=5, selfcheck=1), "AAA open=6 NOT_GATE_READY")
    p, md = compare(r, snap(r, base, head, tmp_path), a, tmp_path)
    assert p.returncode == 0, p.stdout
    assert "(expected)" in p.stdout and not md.exists()
    # a metric the row does not list still blocks
    a = art(tmp_path, 11, os_rows("AAA", 11, plain=2, selfcheck=2), "AAA open=4 NOT_GATE_READY")
    p, _ = compare(r, snap(r, base, head, tmp_path), a, tmp_path)
    assert p.returncode == 1


def test_certified_regression_always_blocks_even_if_expected(repo, tmp_path):
    r, base = repo
    head = commit(r, {CL: "| v |\n| .2 | canary-expected: CERT:* |\n"})
    all_ok(tmp_path)
    a = art(tmp_path, 22, os_rows("CERT", 22, plain=1), "CERT open=1 NOT_GATE_READY VERIFIER_CERTIFIED")
    p, md = compare(r, snap(r, base, head, tmp_path), a, tmp_path)
    assert p.returncode == 1
    assert "| CERT | 22 |" in md.read_text() and "(expected)" not in md.read_text()


def test_losing_certified_status_blocks(repo, tmp_path):
    r, base = repo
    all_ok(tmp_path)
    a = art(tmp_path, 22, os_rows("CERT", 22), "CERT shown 5/5 100 open=0 GATE_READY")
    p, md = compare(r, snap(r, base, base, tmp_path), a, tmp_path)
    assert p.returncode == 1 and "certified yes -> no" in md.read_text()


def test_certified_guard_marker_blocks_even_when_counts_are_equal(repo, tmp_path):
    r, base = repo
    head = commit(r, {CL: "| v |\n| .2 | canary-expected: ZZZ:* |\n"})
    all_ok(tmp_path)
    a = art(tmp_path, 33, os_rows("ZZZ", 33), "ZZZ open=0 GATE_READY HELD_CERTIFIED")
    p, md = compare(r, snap(r, base, head, tmp_path), a, tmp_path)
    assert p.returncode == 1 and "certified_guard" in md.read_text()


@pytest.mark.parametrize("rows,line", [(None, "AAA open=3"), ("keep", None), ("keep", "NO_RESULT_LINE (chain exited early)")])
def test_missing_evidence_blocks(repo, tmp_path, rows, line):
    r, base = repo
    all_ok(tmp_path)
    d = tmp_path / "art" / "flow-11"
    if rows is None:
        (d / "publish_c11" / "open-shown.csv").unlink()
    if line is None:
        (d / "flow_results.tsv").unlink()
    elif line.startswith("NO_RESULT"):
        (d / "flow_results.tsv").write_text(f"10:00Z\t11\t{line}\n")
    p, md = compare(r, snap(r, base, base, tmp_path), tmp_path / "art", tmp_path)
    assert p.returncode == 1 and "evidence" in md.read_text()


def test_unreadable_before_is_an_error_not_a_pass(repo, tmp_path):
    r, _ = repo
    bad = tmp_path / "b.json"
    bad.write_text("{")
    p, md = compare(r, bad, all_ok(tmp_path), tmp_path)
    assert p.returncode == 2 and not md.exists()


def test_committed_canary_set_is_ten_diverse_top100_companies():
    import csv

    rows = list(csv.DictReader(open(ROOT / CAN)))
    assert len(rows) == 10 and all(r["reason"].strip() for r in rows)
    assert {r["sector"] for r in rows} == {
        "bank", "insurer", "reit", "energy", "pharma", "tech", "retailer", "multi-class", "industrial", "certified"
    }
    summ = {r["company_id"]: r["ticker"] for r in csv.DictReader(open(ROOT / "data-team/strategy/top100-coverage-summary.csv"))}
    assert all(summ.get(r["company_id"]) == r["ticker"] for r in rows)
