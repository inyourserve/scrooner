"""scripts/ci/top100_gate.py: a PASS writes a certify request that names the coverage file and the resolver version."""
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
GATE = ROOT / "scripts/ci/top100_gate.py"
COV_HDR = "company_id,ticker,data_point,fiscal_year,display,accession,r_page,parts,reason_code\n"
SHOWN = "7,TICK,total_assets,2024,SHOWN_VALUE,0000000001-24-000001,R2.htm,,\n"
RES_HDR = "cik,ticker,data_point,period_end,grain,decision,value,resolver_version\n"


def gate(tmp, cov_rows, resolver):
    cov = tmp / "cov.csv"
    cov.write_text(COV_HDR + cov_rows)
    out = tmp / "out"
    prove = tmp / "prove.py"
    prove.write_text('DETECTOR_VERSION = "d9"\n')
    r = subprocess.run([sys.executable, str(GATE), "--coverage-csv", str(cov), "--company-id", "7",
                        "--out-dir", str(out), "--prove-py", str(prove), "--resolver", str(resolver)],
                       capture_output=True, text=True)
    return r, out


def test_pass_request_names_coverage_and_resolver_version(tmp_path):
    res = tmp_path / "resolver"
    res.mkdir()
    (res / "TICK.csv").write_text(RES_HDR + "1,TICK,total_assets,2024-12-31,I,mapped,5,resolver-all110-.90\n")
    (res / "OTHER.csv").write_text(RES_HDR + "2,OTHER,total_assets,2024-12-31,I,mapped,5,resolver-all110-.70\n")
    r, out = gate(tmp_path, SHOWN, res)
    assert r.returncode == 0, r.stdout + r.stderr
    md = next(out.glob("TICK-request-*.md")).read_text()
    assert "- coverage csv: `data-team/strategy/certification/TICK-coverage-" in md
    assert "- resolver_version: `resolver-all110-.90`" in md and ".70" not in md
    assert f"- resolver file: `{res / 'TICK.csv'}`" in md
    # the certify reader still finds its own "- resolver:" line, unchanged
    assert f"- resolver: `{res}`" in md


def test_single_resolver_file_reads_only_this_ticker(tmp_path):
    f = tmp_path / "resolver-all110-x.csv"
    f.write_text(RES_HDR + "1,TICK,total_assets,2024-12-31,I,mapped,5,v2\n2,OTHER,total_assets,2024-12-31,I,mapped,5,v1\n")
    r, out = gate(tmp_path, SHOWN, f)
    assert r.returncode == 0
    assert "- resolver_version: `v2`" in next(out.glob("TICK-request-*.md")).read_text()


def test_fail_writes_no_request(tmp_path):
    r, out = gate(tmp_path, SHOWN + "7,TICK,revenue,2024,OPEN,,,,\n", tmp_path)
    assert r.returncode == 1 and not list(out.glob("*-request-*.md"))
