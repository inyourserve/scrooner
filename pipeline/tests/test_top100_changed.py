"""scripts/ci/top100_changed.py on a throwaway git repo: row-level resolver diff -> company ids, caps, requests."""
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/ci/top100_changed.py"
HDR = "cik,ticker,data_point,period_end,grain,decision,value,resolver_version\n"
RES = "data-team/tags/line_map/resolver-all110-x.csv"
REQ = "data-team/strategy/approvals/requests"


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


def run(repo, *a):
    return subprocess.run([sys.executable, str(SCRIPT), *a], cwd=repo, capture_output=True, text=True)


@pytest.fixture
def repo(tmp_path):
    sh(tmp_path, "git", "init", "-q")
    (tmp_path / "s.csv").write_text("ticker,company_id\nAAA,11\nBBB,22\nCCC,33\n")
    return tmp_path


def base_rows(v="v1", bval="2"):
    return (HDR + f"1,AAA,total_assets,2020-12-31,I,mapped,1,{v}\n2,BBB,total_assets,2020-12-31,I,mapped,{bval},{v}\n"
            f"3,CCC,total_assets,2020-12-31,I,mapped,3,{v}\n")


def test_only_changed_rows_map_to_ids(repo):
    a = commit(repo, {RES: base_rows()})
    b = commit(repo, {RES: base_rows(bval="9")})
    r = run(repo, "companies", a, b, "--summary", "s.csv")
    assert r.stdout.strip() == "22", r.stderr


def test_version_bump_alone_changes_nothing(repo):
    a = commit(repo, {RES: base_rows("v1")})
    b = commit(repo, {RES: base_rows("v2")})
    assert run(repo, "companies", a, b, "--summary", "s.csv").stdout.strip() == ""


def test_added_and_removed_rows_and_new_file(repo):
    a = commit(repo, {"x": "1"})
    b = commit(repo, {RES: base_rows()})
    assert run(repo, "companies", a, b, "--summary", "s.csv").stdout.strip() == "11,22,33"
    c = commit(repo, {RES: HDR + "1,AAA,total_assets,2020-12-31,I,mapped,1,v1\n"})
    assert run(repo, "companies", b, c, "--summary", "s.csv").stdout.strip() == "22,33"


def test_ticker_rules_file_and_unknown_ticker(repo):
    a = commit(repo, {"x": "1"})
    b = commit(repo, {"data-team/tags/line_map/BBB.csv": "t\n", "data-team/tags/line_map/ZZZ.csv": "t\n",
                      "data-team/tags/line_map/rules/roles.csv": "t\n"})
    r = run(repo, "companies", a, b, "--summary", "s.csv")
    assert r.stdout.strip() == "22" and "ZZZ" in r.stderr


def test_cap_is_an_error_not_a_truncation(repo):
    a = commit(repo, {"x": "1"})
    b = commit(repo, {RES: base_rows()})
    r = run(repo, "companies", a, b, "--summary", "s.csv", "--max", "2")
    assert r.returncode == 3 and r.stdout.strip() == ""


def test_zero_sha_is_refused(repo):
    a = commit(repo, {"x": "1"})
    assert run(repo, "companies", "0" * 40, a).returncode == 2


def test_requests_only_added_request_files(repo):
    a = commit(repo, {f"{REQ}/OLD-request-2026-11-15.md": "o"})
    b = commit(repo, {f"{REQ}/OLD-request-2026-11-15.md": "o2", f"{REQ}/NEW-request-2026-11-17.md": "n",
                      f"{REQ}/notes.md": "x"})
    assert run(repo, "requests", a, b).stdout.strip() == f"{REQ}/NEW-request-2026-11-17.md"
