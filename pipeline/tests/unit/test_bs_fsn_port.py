"""Balance-sheet lane on the FSN store (data-team/strategy/team/BS-PORT-2026-11-01.md).

The lane scripts run the way the gate and the lane run them (python -I <script> --company <dir>) on two
company directories cut from real FSN-store shards (pipeline/tests/fixtures/fsn_company_bs, plain .tsv,
rows copied from the SEC FSN data sets by fsn_company_fixture.py). Expected values are the
Verifier-passed lane outputs, read from the committed result files, not retyped:
  - AMZN 2023-12-31 total debt from results/debt_fsn_pilot_v1/report_v4.json (Verifier debt v3 14/14 +
    VERIFY-DEBT-RELEASE1-AMZN 3/3): note finance leases inside total debt (founder rule)
  - OXY 0000797468-16-000023 total-liabilities members from results/bs_records_v3.jsonl: the FSN cal
    group must be the filing's own face group (common.fsn_cal_arcs face_tags)
Plus the concept_rule seeds: valid FORMATS-v1 rows that carry the founder's debt perimeter.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
S = ROOT / "pipeline" / "scripts" / "slot_records"
FX = ROOT / "pipeline" / "tests" / "fixtures" / "fsn_company_bs"
SEEDS = ROOT / "data-team" / "47-fsn-store" / "concept_rules" / "bs.jsonl"


def run(script, *args):
    p = subprocess.run([sys.executable, "-I", str(S / script), *map(str, args)], capture_output=True, text=True)
    assert p.returncode == 0, p.stderr
    return p.stdout


@pytest.fixture(scope="module")
def amzn(tmp_path_factory):
    d = tmp_path_factory.mktemp("amzn")
    (d / "cohort.csv").write_text("cik,ticker\n1018724,AMZN\n")
    run("era_detect.py", "--company", FX / "0001018724", d / "eras.json", d / "boundaries.txt")
    run("assemble_fsn.py", "--company", FX / "0001018724", d / "eras.json", d / "cohort.csv", d / "records.jsonl")
    run("replay_debt_fsn.py", "--company", FX / "0001018724", d / "records.jsonl", d / "replay.json")
    return d


def test_debt_company_mode_reproduces_the_verifier_value_with_note_finance_leases(amzn):
    cells = {c["period_end"]: c for c in json.loads((amzn / "replay.json").read_text())["cells"]}
    v4 = next(c for c in json.loads((S / "results/debt_fsn_pilot_v1/report_v4.json").read_text())["cells"]
              if c["ticker"] == "AMZN" and c["period_end"] == "2023-12-31")
    got = cells["2023-12-31"]
    assert got["accession"] == v4["accession"]
    assert got["verdict"] == "publishable"  # production is never read: no prod_* verdict
    assert got["prod_value"] is None
    for f in ("slot_lease_inclusive", "slot_borrowings", "note_finance_lease_added", "note_current_portion_added", "note_flag"):
        assert got[f] == v4[f], f
    assert got["slot_lease_inclusive"] == "78917000000.0000"  # 58,314 + 8,494 + finance leases 12,109 (note)


def test_debt_records_drop_operating_lease_members_and_keep_coverage(amzn):
    recs = [json.loads(x) for x in (amzn / "records.jsonl").read_text().splitlines()]
    assert recs and all(r["coverage_clean"] for r in recs)
    replay = json.loads((amzn / "replay.json").read_text())
    for c in replay["cells"]:
        assert all(cls != "operating_lease" for _t, cls, _s in c.get("members") or [])


def test_bs_assemble_company_mode_picks_the_face_cal_group(tmp_path):
    run("bs_totals_detect.py", "--company", FX / "0000797468", tmp_path / "eras.json", tmp_path / "b.txt")
    run("bs_assemble.py", "--company", FX / "0000797468", tmp_path / "eras.json", tmp_path / "records.jsonl")
    got = [json.loads(x) for x in (tmp_path / "records.jsonl").read_text().splitlines()]
    v3 = [json.loads(x) for x in (S / "results/bs_records_v3.jsonl").read_text().splitlines()]
    ref = next(r for r in v3 if r["filing_from"] == "0000797468-16-000023")
    assert len(got) == 1
    assert got[0]["cal_source"] == "own"
    assert [(m["tag"], m["weight"]) for m in got[0]["total_liabilities_members"]] == \
        [(m["tag"], m["weight"]) for m in ref["total_liabilities_members"]]
    for f in ("total_liabilities_rule", "requires_identity_tie", "nci_tag"):
        assert got[0][f] == ref[f], f
    # v3 carries None here; bs_replay reads `equity_parent_tag or "StockholdersEquity"`, so both read the same line
    assert (got[0]["equity_parent_tag"] or "StockholdersEquity") == (ref["equity_parent_tag"] or "StockholdersEquity")


def test_bs_seeds_are_valid_and_carry_the_debt_perimeter():
    sys.path.insert(0, str(ROOT / "pipeline" / "src"))
    from scrooner_pipeline.fsn_store import rules

    rows = [json.loads(x) for x in SEEDS.read_text().splitlines() if x.strip()]
    names = {r["canonical_concept"] for r in rows} | {c for r in rows for c in (r.get("components") or [])} | {
        (r.get("position") or {}).get("anchor_concept") for r in rows} - {None}
    assert rules.validate(rows, {n: i for i, n in enumerate(sorted(names))}) == []
    debt_slots = {(r["position"]["slot"], r["position"]["anchor_concept"]) for r in rows
                  if r["canonical_concept"] == "total_debt_resolved" and r["match_kind"] == "calc_position"}
    for slot in ("borrowing", "finance_lease", "combined"):  # founder: finance leases and debt+finance-lease lines are debt
        assert (slot, "current_liabilities_resolved") in debt_slots and (slot, "total_liabilities_resolved") in debt_slots, slot
    assert not any(s == "operating_lease" for s, _ in debt_slots)  # operating leases never enter total debt


def test_bs_seeds_are_the_exporter_output(tmp_path):
    """bs.jsonl is exported from the lane code, never retyped: a re-export equals the committed file
    (source_commit aside, which names the commit the export ran on)."""
    p = subprocess.run([sys.executable, str(S / "export_concept_rule_seeds_lanes.py"), str(tmp_path)],
                       capture_output=True, text=True, cwd=ROOT)
    assert p.returncode == 0, p.stderr

    def rows(path):
        return [{k: v for k, v in json.loads(x).items() if k != "source_commit"} for x in path.read_text().splitlines() if x.strip()]

    assert rows(tmp_path / "concept_rules" / "bs.jsonl") == rows(SEEDS)
