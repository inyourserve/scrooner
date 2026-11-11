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
from decimal import Decimal
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
    # total debt is the debt lane's SUM (fsn_store.debt), never a mapped line: no seed may map anything as total debt
    # (FAMILY-RELEASE-CASE-2026-11-09 §2). The founder's perimeter (finance leases from the notes in, operating leases
    # out) lives in the lane, tested above (AMZN note finance leases; operating-lease members dropped).
    assert not [r["rule_id"] for r in rows if r["canonical_concept"] == "total_debt_resolved"]


def test_bs_seeds_are_the_exporter_output(tmp_path):
    """bs.jsonl is exported from the lane code, never retyped: a re-export equals the committed file
    (source_commit aside, which names the commit the export ran on)."""
    p = subprocess.run([sys.executable, str(S / "export_concept_rule_seeds_lanes.py"), str(tmp_path)],
                       capture_output=True, text=True, cwd=ROOT)
    assert p.returncode == 0, p.stderr

    def rows(path):
        return [{k: v for k, v in json.loads(x).items() if k != "source_commit"} for x in path.read_text().splitlines() if x.strip()]

    assert rows(tmp_path / "concept_rules" / "bs.jsonl") == rows(SEEDS)


# ---------------------------------------------------------------- review 2026-11-01 (BS-PORT-FIXES-2026-11-01.md)
SUB = ["fsn_set", "adsh", "cik", "form", "period", "filed", "accepted", "aciks"]
PRE = ["adsh", "report", "line", "stmt", "inpth", "tag", "version", "prole", "plabel", "negating"]
NUM = ["adsh", "tag", "version", "ddate", "qtrs", "uom", "dimh", "iprx", "value", "footnote", "footlen", "dimn", "coreg", "durp", "datp", "dcml"]
FACE = [("Assets", "Total assets"), ("LongTermDebtNoncurrent", "Long-term debt"),
        ("FinanceLeaseLiabilityNoncurrent", "Finance lease liabilities"), ("LiabilitiesAndStockholdersEquity", "Total")]


def _write(path, cols, rows):
    path.write_text("\t".join(cols) + "\n" + "".join("\t".join(str(r.get(c, "")) for c in cols) + "\n" for r in rows))


DEFAULT_MEMBERS = [{"tag": "LongTermDebtNoncurrent", "class": "borrowing", "side": "noncurrent", "custom": False},
                   {"tag": "FinanceLeaseLiabilityNoncurrent", "class": "finance_lease", "side": "noncurrent", "custom": False}]


def _synthetic(tmp_path, filings, face=None, members=None):
    """filings: [(adsh, form, period, accepted, {ddate: {tag: value}})] for CIK 1"""
    face = face or FACE
    d = tmp_path / "0000000001"
    d.mkdir()
    (d / "manifest.json").write_text('{"cik": "0000000001"}')
    _write(d / "sub.tsv", SUB, [{"fsn_set": "2020q1", "adsh": a, "cik": "1", "form": f, "period": p, "filed": acc[:8], "accepted": acc}
                                for a, f, p, acc, _ in filings])
    _write(d / "pre.tsv", PRE, [{"adsh": a, "report": 2, "line": i + 1, "stmt": "BS", "inpth": 0, "tag": t, "version": "us-gaap/2020",
                                 "prole": "terseLabel", "plabel": lab, "negating": 0} for a, *_ in filings for i, (t, lab) in enumerate(face)])
    _write(d / "num.tsv", NUM, [{"adsh": a, "tag": t, "version": "us-gaap/2020", "ddate": dd, "qtrs": 0, "uom": "USD", "dimh": "0x00000000",
                                 "iprx": 0, "value": v} for a, _f, _p, _acc, vals in filings for dd, tv in vals.items() for t, v in tv.items()])
    (tmp_path / "records.jsonl").write_text(json.dumps({
        "company": "SYN", "cik": "1", "filing_from": filings[0][0], "period_from": "2014-01-01", "period_to": "2030-12-31",
        "coverage_clean": True, "members": members or DEFAULT_MEMBERS}) + "\n")
    run("replay_debt_fsn.py", "--company", d, tmp_path / "records.jsonl", tmp_path / "replay.json")
    return {c["period_end"]: c for c in json.loads((tmp_path / "replay.json").read_text())["cells"]}


def test_note_finance_lease_total_is_not_added_twice(tmp_path):
    """face: borrowings 100 + finance lease (noncurrent) 40; note: FinanceLeaseLiability 55 = current 15 + noncurrent 40.
    Total debt = 155 (the note adds only the 15 no member carries), never 195."""
    vals = {"Assets": 1000, "LiabilitiesAndStockholdersEquity": 1000, "LongTermDebtNoncurrent": 100, "LongTermDebt": 100,
            "FinanceLeaseLiabilityNoncurrent": 40, "FinanceLeaseLiability": 55, "FinanceLeaseLiabilityCurrent": 15}
    cells = _synthetic(tmp_path, [("0000000001-20-000001", "10-K", "20191231", "20200220120000", {"20191231": vals})])
    c = cells["2019-12-31"]
    assert c["verdict"] == "publishable", c
    assert c["slot_lease_inclusive"] == "155"
    assert c["note_finance_lease_added"] == "15"


def test_latest_accepted_print_wins_and_cells_start_2015(tmp_path):
    # LongTermDebt (note) = the noncurrent line: no current portion, so the replay's current-maturities check passes
    base = {"Assets": 1000, "LiabilitiesAndStockholdersEquity": 1000, "LongTermDebtNoncurrent": 100, "LongTermDebt": 100,
            "FinanceLeaseLiabilityNoncurrent": 0}
    restated = dict(base, LongTermDebtNoncurrent=120, LongTermDebt=120)
    cells = _synthetic(tmp_path, [
        ("0000000001-15-000001", "10-K", "20141231", "20150220120000", {"20141231": base, "20131231": base}),
        ("0000000001-16-000001", "10-K", "20151231", "20160220120000", {"20151231": base, "20141231": restated}),
        ("0000000001-16-000002", "10-Q", "20160331", "20160505120000", {"20160331": base, "20151231": restated})])
    assert sorted(cells) == ["2015-12-31", "2016-03-31"]  # 2013/2014 instants are values, never cells (I11)
    assert cells["2015-12-31"]["accession"] == "0000000001-16-000002"  # the later-accepted 10-Q comparative wins
    assert cells["2015-12-31"]["slot_lease_inclusive"] == "120"


def _gate_work(tmp_path, value="155"):
    import gzip as _gz
    w = tmp_path / "work"
    for side in ("old", "new", "company"):
        (w / side / "debt").mkdir(parents=True)
    with _gz.open(w / "instants.jsonl.gz", "wt") as f:
        f.write(json.dumps({"adsh": "A1", "cik": 1, "form": "10-K", "period": "20191231", "filed": "20200220",
                            "accepted": "20200220120000", "values": {}, "bs": []}) + "\n")
    cell = {"ticker": "SYN", "cik": 1, "period_end": "2019-12-31", "accession": "A1", "verdict": "publishable",
            "slot_lease_inclusive": value, "slot_borrowings": "100", "members": [], "record_filing_from": "A1"}
    for side in ("old", "new"):
        for f in ("bs_eras.json", "debt_eras.json"):
            (w / side / f).write_text("{}")
        for f in ("bs_boundaries.txt", "debt_boundaries.txt", "bs_records.jsonl", "debt/bs_pre_rows.jsonl",
                  "debt/lease_facts.csv", "debt_records.jsonl"):
            (w / side / f).write_text("")
        (w / side / "debt/adsh_period.json").write_text("{}")
    for p in ("old/debt_replay.json", "new/debt_replay.json", "new/debt_replay_first_filed.json"):
        (w / p).write_text(json.dumps({"cells": [dict(cell, slot_lease_inclusive="155")]}))
    for f in ("bs_eras.json", "debt_eras.json"):
        (w / "company" / f).write_text("{}")
    for f in ("bs_boundaries.txt", "debt_boundaries.txt", "bs_records.jsonl", "debt_records.jsonl"):
        (w / "company" / f).write_text("")
    (w / "company/debt_replay.json").write_text(json.dumps({"cells": [cell]}))
    (tmp_path / "v4.json").write_text(json.dumps({"cells": [dict(cell, slot_lease_inclusive="155", verdict="prod_blank")]}))
    (tmp_path / "v3.jsonl").write_text("")
    return w


def _compare(tmp_path, w, *extra):
    return subprocess.run([sys.executable, "-I", str(S / "bs_port_compare.py"), str(w), str(tmp_path / "v4.json"),
                           str(tmp_path / "v3.jsonl"), *map(str, extra)], capture_output=True, text=True)


def test_gate_fails_closed(tmp_path):
    """review 2026-11-01: the gate could not fail. Identical outputs pass; one changed value fails, strict or pinned."""
    ok = _compare(tmp_path, _gate_work(tmp_path))
    assert ok.returncode == 0, ok.stdout + ok.stderr
    bad_dir = tmp_path / "b"
    bad_dir.mkdir()
    (bad_dir / "v4.json").write_text((tmp_path / "v4.json").read_text())
    (bad_dir / "v3.jsonl").write_text("")
    w = _gate_work(bad_dir, value="195")  # the double-counted total of the synthetic lease case
    strict = _compare(bad_dir, w)
    assert strict.returncode == 1 and "FAIL" in strict.stdout
    obs = json.loads((w / "observed_diffs.json").read_text())
    assert obs and all(d["class"] == "value_differs" for d in obs)
    (bad_dir / "pin.json").write_text(json.dumps(obs))  # a generic class can never be pinned
    pinned = _compare(bad_dir, w, "--expected", bad_dir / "pin.json")
    assert pinned.returncode == 1 and "REFUSED PIN" in pinned.stdout



def test_note_lease_not_added_when_the_total_is_a_face_member(tmp_path):
    """review 2026-11-01 (sibling case): the face member is the TOTAL FinanceLeaseLiability 45; the note prints the
    current part 5. Total debt = 100 + 45 = 145; nothing is added from the note (never 190)."""
    vals = {"Assets": 1000, "LiabilitiesAndStockholdersEquity": 1000, "LongTermDebtNoncurrent": 100, "LongTermDebt": 100,
            "FinanceLeaseLiability": 45, "FinanceLeaseLiabilityCurrent": 5}
    face = [("Assets", "Total assets"), ("LongTermDebtNoncurrent", "Long-term debt"),
            ("FinanceLeaseLiability", "Finance lease liabilities"), ("LiabilitiesAndStockholdersEquity", "Total")]
    members = [{"tag": "LongTermDebtNoncurrent", "class": "borrowing", "side": "noncurrent", "custom": False},
               {"tag": "FinanceLeaseLiability", "class": "finance_lease", "side": "noncurrent", "custom": False}]
    cells = _synthetic(tmp_path, [("0000000001-20-000001", "10-K", "20191231", "20200220120000", {"20191231": vals})], face, members)
    c = cells["2019-12-31"]
    assert c["verdict"] == "publishable", c
    assert c["slot_lease_inclusive"] == "145"
    assert not c["note_finance_lease_added"]


# ---------------------------------------------------------------- equity-block guard (Verifier debt-port draw 2026-11-01)
def _detect_face(tmp_path, face):
    """One synthetic 10-K whose balance-sheet face is `face` [(tag, label)]; returns the era's (skeleton, guarded tags)."""
    d = tmp_path / "0000000002"
    d.mkdir()
    (d / "manifest.json").write_text('{"cik": "0000000002"}')
    _write(d / "sub.tsv", SUB, [{"fsn_set": "2020q1", "adsh": "0000000002-20-000001", "cik": "2", "form": "10-K", "period": "20191231",
                                 "filed": "20200220", "accepted": "20200220120000"}])
    _write(d / "pre.tsv", PRE, [{"adsh": "0000000002-20-000001", "report": 2, "line": i + 1, "stmt": "BS", "inpth": 0, "tag": t,
                                 "version": "us-gaap/2020", "prole": "terseLabel", "plabel": lab, "negating": 0}
                                for i, (t, lab) in enumerate(face)])
    run("bs_totals_detect.py", "--company", d, tmp_path / "eras.json", tmp_path / "b.txt")
    era = json.loads((tmp_path / "eras.json").read_text())["0000000002"][0]
    return era["skeleton"], {z["tag"] for z in era["zone_lines"] if z.get("equity_block_guard")}


CAP_FACE = [("Assets", "Total assets"), ("CommonStockValue", "Common stock"), ("RetainedEarningsAccumulatedDeficit", "Retained earnings"),
            ("StockholdersEquity", "Total common equity"), ("LongTermDebtNoncurrent", "Long-term debt"),
            ("CapitalizationLongtermDebtAndEquity", "Total Capitalization"), ("LiabilitiesCurrent", "Total current liabilities"),
            ("OtherLiabilitiesNoncurrent", "Other"), ("LiabilitiesAndStockholdersEquity", "Total")]


@pytest.mark.parametrize("debt_tag", ["LongTermDebtNoncurrent", "LongTermDebtAndCapitalLeaseObligations",
                                      "LongTermDebtIncludesRedeemablePreferredStockAtRedemptionValue"])
def test_guard_keeps_long_term_debt_inside_total_capitalization_a_liability(tmp_path, debt_tag):
    """NI/FE/AWK (Verifier 7 of 7 false holds): equity, then long-term debt, then 'Total Capitalization'. Equity + debt =
    Total capitalization, so the debt line is a liability; the old guard turned it into an equity component."""
    face = [(debt_tag if t == "LongTermDebtNoncurrent" else t, lab) for t, lab in CAP_FACE]
    skeleton, guarded = _detect_face(tmp_path, face)
    assert debt_tag in skeleton
    assert debt_tag not in guarded


def test_guard_still_catches_a_non_debt_liability_inside_the_equity_block(tmp_path):
    """UPS 2017: 'Deferred compensation obligations' printed between equity rows, no capitalization total."""
    face = [("Assets", "Total assets"), ("LiabilitiesCurrent", "Total current liabilities"), ("CommonStockValue", "Common stock"),
            ("DeferredCompensationLiabilityClassifiedNoncurrent", "Deferred compensation obligations"),
            ("TreasuryStockValue", "Treasury stock"), ("StockholdersEquity", "Total equity"),
            ("LiabilitiesAndStockholdersEquity", "Total")]
    skeleton, guarded = _detect_face(tmp_path, face)
    assert guarded == {"DeferredCompensationLiabilityClassifiedNoncurrent"}
    assert "DeferredCompensationLiabilityClassifiedNoncurrent" not in skeleton


def test_guard_still_holds_a_debt_line_when_there_is_no_capitalization_total(tmp_path):
    """BX/OXY-style records stay as before: a debt-looking line after equity with no filer capitalization subtotal is guarded."""
    face = [t for t in CAP_FACE if t[0] != "CapitalizationLongtermDebtAndEquity"]
    skeleton, guarded = _detect_face(tmp_path, face)
    assert "LongTermDebtNoncurrent" in guarded and "LongTermDebtNoncurrent" not in skeleton


def test_guard_still_catches_a_non_debt_liability_before_the_capitalization_total(tmp_path):
    face = [(("DeferredCompensationLiabilityClassifiedNoncurrent", "Deferred compensation") if t == "LongTermDebtNoncurrent" else (t, lab))
            for t, lab in CAP_FACE]
    skeleton, guarded = _detect_face(tmp_path, face)
    assert guarded == {"DeferredCompensationLiabilityClassifiedNoncurrent"}


def test_guard_keeps_capital_lease_lines_inside_total_capitalization_a_liability(tmp_path):
    face = [("CapitalLeaseObligationsNoncurrent" if t == "LongTermDebtNoncurrent" else t, lab) for t, lab in CAP_FACE]
    skeleton, guarded = _detect_face(tmp_path, face)
    assert "CapitalLeaseObligationsNoncurrent" in skeleton and not guarded


# ---------------------------------------------------------------- debt Verifier traps (VERIFY-DEBT-PORT-2026-11-01.md)
# Fixtures: two real filings per company cut from the SEC FSN data sets (tests/fixtures/fsn_company_bs_traps).
TRAPS = ROOT / "pipeline" / "tests" / "fixtures" / "fsn_company_bs_traps"


def _trap_cells(tmp_path, cik):
    (tmp_path / "cohort.csv").write_text(f"cik,ticker\n{int(cik)},X\n")
    d = TRAPS / cik
    run("era_detect.py", "--company", d, tmp_path / "eras.json", tmp_path / "boundaries.txt")
    run("assemble_fsn.py", "--company", d, tmp_path / "eras.json", tmp_path / "cohort.csv", tmp_path / "records.jsonl")
    run("replay_debt_fsn.py", "--company", d, tmp_path / "records.jsonl", tmp_path / "replay.json")
    return {c["period_end"]: c for c in json.loads((tmp_path / "replay.json").read_text())["cells"]}


def test_trap_meta_2018_filer_context_error_is_not_a_liability(tmp_path):
    """FY2019 10-K R47 prints non-current lease 418 in the Dec. 31, 2018 context (473 = 55 + 418 is the 2019 total).
    META had no debt and no finance lease at 2018-12-31: the value is 0, never 418. 2019 keeps 473."""
    cells = _trap_cells(tmp_path, "0001326801")
    assert cells["2018-12-31"]["verdict"] == "publishable"
    assert Decimal(cells["2018-12-31"]["slot_lease_inclusive"]) == 0
    assert Decimal(cells["2019-12-31"]["slot_lease_inclusive"]) == 473_000_000


def test_trap_nvda_2017_01_29_latest_copy_drops_a_lease_line_the_total_does_not_fall(tmp_path):
    """FY2018 10-K no longer prints the 6 noncurrent capital lease; its debt lines equal the FY2017 10-K's.
    796 + 1,983 + 4 + 6 = 2,789 (a reader of the latest copy alone gives 2,783, wrong by 6)."""
    c = _trap_cells(tmp_path, "0001045810")["2017-01-31"]
    assert c["verdict"] == "publishable"
    assert Decimal(c["slot_lease_inclusive"]) == 2_789_000_000
    assert c["accession"] == "0001045810-18-000010"  # the latest print still decides the debt values


def test_trap_amzn_2016_capital_lease_is_present_value_never_the_gross_9406(tmp_path):
    """CapitalLeaseObligations 9,406 (FY2016 10-K) is gross minimum payments; present value is 4,000 + 5,080.
    7,694 + 1,056 + 9,080 = 17,830 (v4's 18,156 added the gross)."""
    c = _trap_cells(tmp_path, "0001018724")["2016-12-31"]
    assert c["verdict"] == "publishable"
    assert Decimal(c["slot_lease_inclusive"]) == 17_830_000_000
    assert Decimal(c["note_finance_lease_added"]) == 9_080_000_000


def test_trap_goog_2024_finance_leases_are_in_total_debt(tmp_path):
    """10,883 + 999 + finance leases 1,677 = 13,559 (v4's 11,882 missed the 1,677)."""
    c = _trap_cells(tmp_path, "0001652044")["2024-12-31"]
    assert c["verdict"] == "publishable"
    assert Decimal(c["slot_lease_inclusive"]) == 13_559_000_000
    assert Decimal(c["note_finance_lease_added"]) == 1_677_000_000


def test_latest_copy_without_lease_note_is_filled_from_the_earlier_copy_only_when_the_debt_lines_are_equal(tmp_path):
    """META 2025-12-31 pattern: the later 10-Q prints the debt line but no lease note. Equal debt lines -> the 10-K's lease
    is added; a debt line that differs between the copies -> the hold stays (the latest print cannot be completed)."""
    lease = {"FinanceLeaseLiability": 50, "FinanceLeaseLiabilityNoncurrent": 40, "FinanceLeaseLiabilityCurrent": 10}
    first = {"Assets": 1000, "LiabilitiesAndStockholdersEquity": 1000, "LongTermDebtNoncurrent": 100, "LongTermDebt": 100, **lease}
    later = {"Assets": 1000, "LiabilitiesAndStockholdersEquity": 1000, "LongTermDebtNoncurrent": 100, "LongTermDebt": 100}
    k = ("0000000001-20-000001", "10-K", "20191231", "20200220120000", {"20191231": first})
    q = ("0000000001-20-000009", "10-Q", "20200331", "20200505120000", {"20200331": later, "20191231": later})
    (tmp_path / "a").mkdir()
    same = _synthetic(tmp_path / "a", [k, q])
    assert same["2019-12-31"]["verdict"] == "publishable" and same["2019-12-31"]["slot_lease_inclusive"] == "150"
    other = dict(later, LongTermDebtNoncurrent=90, LongTermDebt=90)
    q2 = ("0000000001-20-000009", "10-Q", "20200331", "20200505120000", {"20200331": other, "20191231": other})
    (tmp_path / "b").mkdir()
    held = _synthetic(tmp_path / "b", [k, q2])
    assert held["2019-12-31"]["verdict"] == "latest_copy_lacks_note_finance_lease"
