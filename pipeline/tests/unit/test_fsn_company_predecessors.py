"""Lane readers of an FSN store company directory (pipeline/scripts/slot_records/fsn_company*.py) read a predecessor
registrant's filings as the company's own history when FSN_PREDECESSORS names it (the store's
core.company_history_source alias), report them under the company's CIK, and still skip other filers' rows.
Found 2026-11-11: MDT, LIN, AVGO, MRVL, XOM, DIS and BLK lost every filing before their reorganisation."""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
S = ROOT / "pipeline" / "scripts" / "slot_records"

PROBE = """
import json, sys
sys.path.insert(0, sys.argv[1])
import fsn_company, fsn_company_bs
d = sys.argv[2]
subs = fsn_company_bs.own_subs(d)
print(json.dumps({"own": sorted(fsn_company.own_ciks(d)), "subs": {a: s["cik"] for a, s in sorted(subs.items())}}))
"""


def _dir(tmp_path):
    d = tmp_path / "0001613103"
    d.mkdir()
    (d / "manifest.json").write_text(json.dumps({"cik": "0001613103"}))
    cols = ["adsh", "cik", "form", "period", "filed", "fy", "fp", "aciks"]
    rows = [
        [
            "0000064670-14-000010",
            "64670",
            "10-K",
            "20140430",
            "20140620",
            "2014",
            "FY",
            "",
        ],  # Medtronic Inc
        [
            "0001613103-15-000028",
            "1613103",
            "10-K",
            "20150430",
            "20150623",
            "2015",
            "FY",
            "",
        ],  # Medtronic plc
        [
            "0000999999-15-000001",
            "999999",
            "10-Q",
            "20150131",
            "20150301",
            "2015",
            "Q3",
            "1613103",
        ],  # other filer
    ]
    (d / "sub.tsv").write_text("\n".join("\t".join(r) for r in [cols, *rows]) + "\n")
    return d


def _run(d, env_extra):
    import os

    env = dict(os.environ, **env_extra)
    env.pop("FSN_PREDECESSORS", None) if not env_extra else None
    r = subprocess.run(
        [sys.executable, "-I", "-c", PROBE, str(S), str(d)],
        capture_output=True,
        text=True,
        env=env,
    )
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout)


def test_predecessor_filings_are_read_under_the_company_cik(tmp_path):
    d = _dir(tmp_path)
    got = _run(d, {"FSN_PREDECESSORS": "0000064670=0001613103,0000034088=0002115436"})
    assert got["own"] == ["0000064670", "0001613103"]
    assert got["subs"] == {
        "0000064670-14-000010": "0001613103",
        "0001613103-15-000028": "0001613103",
    }


def test_without_the_alias_only_the_company_s_own_filings_are_read(tmp_path):
    d = _dir(tmp_path)
    got = _run(d, {})
    assert got["subs"] == {"0001613103-15-000028": "0001613103"}
