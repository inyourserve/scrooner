"""Full-population income-statement cells (family is_core) in the common cell
format CELL-FORMAT-v1 (scrooner-8a, data-team/46-canonical-fact-v2/), for the
rebuild of analytics.canonical_fact (founder decision 2026-11-04: rebuild,
don't patch; every company and period, not diffs against production).
Stdlib, run with -I; no database.

Inputs are the outputs of the verified rules, unchanged:
  * is_replay.py run with IS_REPLAY_PROD=0 (production not read): one cell per
    (company, family, start, end) face column, state slot_value / hold_* /
    hide_restated_copies_disagree, with the core.fact ids behind the value;
  * is_not_presented.py per family (operating_income, gross_profit,
    cost_of_revenue): line_not_presented_in_filing where the original filing's
    face prints no such line (banks, insurers, BDCs and commercial filers);
  * is_filing_slots.jsonl: the per-filing slot (gate, face line, shape).
Every face column of every ORIGINAL filing (known from any family's cells)
gets a row in every data point: where the family has no cell and no reason,
the filing's own slot gate for that family is the held reason (a held filing
publishes no cell, so without this the column would be silently absent).

Rows: FY (12-month) and Q (3-month) only; 6- and 9-month YTD face columns are
not cells in v1 and are dropped as rows (counted). Quarters are never derived
here: a quarter the filer did not print as a 3-month column is fsn_select.py's
(FSN-STORE-DESIGN 2026-11-01 section 4, SAME_BASIS); the last file with the
lane's own derivation is is_core 2f98b025 (commit b9f3c4f).
Every key of the shared expected-period calendar (v1.1 section 2.3) gets a
row: a key no rule reached is defect no_filed_column_for_period.
States: value; not_presented; defect (holds, by DEFECT below; hides as
guard_hidden with reason restated_copies_disagree). The gate goes in
input_refs. New reason codes (the gates) are declared in the manifest.

usage: is_emit.py <replay_dir> <not_presented_root> <is_filing_slots.jsonl>
                  <is_fsn_dir> <company_ids.tsv> <expected_periods.csv.gz> <out_dir> [git_commit]
  company_ids.tsv: "cik<TAB>company_id" per line (core.company)
  writes <out_dir>/cells.jsonl.gz and <out_dir>/manifest.json
"""
import glob
import gzip
import hashlib
import json
import sys
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
from pathlib import Path

FAMILY = "is_core"
DATA_POINT = {
    "revenue": "revenue_sanity_resolved",
    "operating_income": "operating_income_resolved",
    "net_income": "net_income_resolved",
    "gross_profit": "gross_profit_resolved",
    "cost_of_revenue": "cost_of_revenue_resolved",
}
FAMILIES = tuple(DATA_POINT)
NOT_PRESENTED = {"operating_income": "is_oi", "gross_profit": "is_gross_profit", "cost_of_revenue": "is_cost_of_revenue"}
RULE = {f: f"slot.is_{f}@1" for f in FAMILIES}
# revenue's face sum tied to the filer's own tagged total is its own rule (release 2)
GATE_RULE = {"G3b_sum_ties_tagged_total": "slot.is_revenue_tagged_total_sum@1"}
OWNER_FAMILY = "data_engineer_l1"  # guard_hidden takes the rule family's owner
FY_DAYS, Q4_DAYS = (340, 380), (80, 120)  # q4_vintage_dryrun bands

# gate -> (defect_class, owner, meaning declared in the manifest)
DEFECT = {
    "hold_identity_gap": ("composition", "standardization_lead",
                          "the filing's own identity (NCI bridge, gross identity or face sum) does not tie within one printed unit"),
    "hold_identity_unverified": ("composition", "standardization_lead",
                                 "the available-to-common bridge is not fully tagged, so it cannot be tied"),
    "hold_sum_member_missing": ("composition", "standardization_lead",
                                "a printed line of the face sum has no fact in the filing"),
    "hold_multiple_roots": ("composition", "standardization_lead", "the face prints more than one candidate top line"),
    "hold_sibling_custom": ("composition", "standardization_lead",
                            "a custom sibling line sits next to the standard line; additivity is not established"),
    "hold_custom_cost_line": ("vocabulary", "tag_mapper", "the printed line uses a custom extension tag"),
    "hold_custom_gross_line": ("vocabulary", "tag_mapper", "the printed line uses a custom extension tag"),
    "hold_custom_operating_line": ("vocabulary", "tag_mapper", "the printed line uses a custom extension tag"),
    "hold_custom_revenue_line": ("vocabulary", "tag_mapper", "the printed line uses a custom extension tag"),
    "hold_parent_line_not_standard": ("vocabulary", "tag_mapper",
                                      "the face deducts NCI or preferred below a non-standard parent line"),
    "hold_perimeter_excl_da": ("definition_pending", "accountant",
                               "the printed cost line excludes depreciation and amortization"),
    "hold_label_not_gross": ("definition_pending", "accountant",
                             "the gross-profit-tagged line is labelled as something else"),
    "hold_label_before_tax": ("definition_pending", "accountant",
                              "the operating-tagged line is labelled as income before tax"),
    "hold_position_below_pretax": ("definition_pending", "accountant",
                                   "the operating-tagged line is printed below pretax income"),
    "hold_sector_bank": ("evidence_pending", "sector_analyst", "bank face: the line is not defined for the template yet"),
    "hold_sector_insurer": ("evidence_pending", "sector_analyst", "insurer face: the line is not defined for the template yet"),
    "hold_sector_bdc": ("evidence_pending", "sector_analyst", "BDC face: the line is not defined for the template yet"),
    "no_printed_operating_line": ("vocabulary", "tag_mapper",
                                  "no operating line was recognised, but an operating-like line is on the face"),
    "no_printed_gross_profit_line": ("vocabulary", "tag_mapper",
                                     "no gross profit line was recognised, but a gross-like line is on the face"),
    "no_printed_cost_line": ("vocabulary", "tag_mapper",
                             "no cost line was recognised, but a cost-like line is on the face"),
    "slot_fact_missing_in_companyfacts": ("ingestion", "data_engineer_l2",
                                          "the printed line has no fact for this column in core.fact"),
    "no_slot_record_for_filing": ("unclassified", "triage", "the filing has no slot record for this data point"),
    "no_filed_column_for_period": ("period", "period_engineer",
                                   "no filing of the company prints this period as a column and it cannot be derived "
                                   "from two year-to-date columns of the same fiscal year"),
}
DEFAULT_DEFECT = ("unclassified", "triage", "held by a slot rule")


def grain(start, end):
    days = (date.fromisoformat(end) - date.fromisoformat(start)).days + 1
    if 350 <= days <= 380:
        return "FY"
    if 80 <= days <= 100:
        return "Q"
    return None  # YTD: not a v1 cell


def fiscal(slot, end):
    """fiscal binding fields from the filing's own fy/fp (FSN sub)."""
    if not slot:
        return {}
    return {"fiscal_year": int(slot["fy"]) if slot.get("fy") else None,
            "fiscal_period": slot.get("fp"), "period_type": "duration", "fsn_end": end}


def base(cid, cik, fam, s0, e0, g):
    return {"company_id": cid, "cik": cik, "data_point_name": DATA_POINT[fam], "period_grain": g,
            "period_start": s0, "period_end": e0, "basis": "latest", "unit": None, "decimals": None,
            "source_fact_ids": [], "members": None, "derivation": None, "rule_run_id": None,
            "defect_class": None, "owner": None, "root_cause_class": None}


def defect(r, gate, reason_text=None):
    cls, owner, meaning = DEFECT.get(gate, DEFAULT_DEFECT)
    r.update(state="defect", value=None, reason_code=gate, reason_text=reason_text or meaning.capitalize() + ".",
             defect_class=cls, owner=owner, root_cause_class=cls if cls not in ("guard_hidden", "finding_open") else None)
    return r


def from_cell(cid, fam, c, g, fsn_of, slot):
    r = base(cid, c["cik"], fam, c["start"], c["end"], g)
    st = c["state"]
    acc = c.get("accession")
    r.update(accession=acc, tag=c.get("slot_tag"), rule_id=GATE_RULE.get(c.get("gate"), RULE[fam]),
             fsn_set=fsn_of.get(acc), fsn_stmt="IS", fsn_line=c.get("face_line"), evidence_level="DATA-INFERRED",
             **fiscal(slot, c["end"]))
    refs = {"gate": c.get("gate"), "form": c.get("form"), "label": c.get("label"), "original": c.get("original"),
            "copies": c.get("copies")}
    for k in ("identity_gap", "check_value", "missing", "copies_disagree", "face_axis"):
        if c.get(k) not in (None, [], {}, False):
            refs[k] = c[k]
    if c.get("members"):
        r["members"] = [{"tag": t, "value": v, "accession": acc, "label": None} for t, v in sorted(c["members"].items())]
    if st == "slot_value":
        r.update(state="value", value=c["slot_value"], unit="USD", source_fact_ids=c.get("source_fact_ids") or [],
                 reason_code=None, reason_text=None, evidence_level="FILING-CHECKED")
    elif st.startswith("hide"):
        r.update(state="defect", value=None, reason_code="restated_copies_disagree",
                 reason_text="Later filings print a different number for this period than the original filing.",
                 defect_class="guard_hidden", owner=OWNER_FAMILY, root_cause_class="period")
        refs["unpublished_value"] = c.get("slot_value")
    else:
        defect(r, st)
        if c.get("slot_value") is not None:
            refs["unpublished_value"] = c["slot_value"]
    r["input_refs"] = refs
    return r


def from_reason(cid, fam, n, g, fsn_of, slot):
    r = base(cid, n["cik"], fam, n["period_start"], n["period_end"], g)
    acc = n["input_refs"]["accession"]
    r.update(state="not_presented", value=None, reason_code=n["reason_code"], reason_text=n["reason_text"][0].upper() + n["reason_text"][1:] + ".",
             rule_id=n["rule_id"], accession=acc, tag=None, fsn_set=fsn_of.get(acc), fsn_stmt="IS", fsn_line=None,
             evidence_level="DATA-INFERRED", input_refs={**n["input_refs"]}, **fiscal(slot, n["period_end"]))
    return r


def from_held_filing(cid, cik, fam, key, acc, g, fsn_of, slot):
    _, s0, e0 = key
    r = base(cid, cik, fam, s0, e0, g)
    r.update(accession=acc, tag=slot.get("tag") if slot else None, rule_id=RULE[fam], fsn_set=fsn_of.get(acc),
             fsn_stmt="IS", fsn_line=slot.get("line") if slot else None, evidence_level="DATA-INFERRED",
             **fiscal(slot, e0))
    defect(r, slot["gate"] if slot else "no_slot_record_for_filing")
    r["input_refs"] = {"gate": slot["gate"] if slot else None, "form": slot["form"] if slot else None,
                       "shape": slot.get("shape") if slot else None, "face_report": slot.get("report") if slot else None,
                       "column_from": "face column of the original filing (another data point's cell)"}
    return r


def _days(s0, e0):
    return (date.fromisoformat(e0) - date.fromisoformat(s0)).days + 1


def load_calendar(path):
    """Expected duration keys per CIK from the shared calendar (CELL-FORMAT-v1.1 section 2.3)."""
    import csv
    opener = gzip.open if str(path).endswith(".gz") else open
    cal = defaultdict(list)
    with opener(path, "rt") as fh:
        for r in csv.DictReader(fh):
            if r["period_type"] == "duration":
                cal[r["cik"].zfill(10)].append((r["period_start"], r["period_end"], r["fiscal_year"], r["fiscal_period"]))
    return cal


def from_calendar(cid, cik, fam, s0, e0, fy, fp):
    r = base(cid, cik, fam, s0, e0, "FY" if fp == "FY" else "Q")
    r.update(rule_id=RULE[fam], accession=None, tag=None, fsn_set=None, fsn_stmt=None, fsn_line=None,
             evidence_level="DATA-INFERRED", fiscal_year=int(fy), fiscal_period=fp, period_type="duration",
             fsn_end=None)
    defect(r, "no_filed_column_for_period")
    r["input_refs"] = {"from": "expected-period calendar"}
    return r


def main(replay_dir, np_root, slots_path, is_fsn, company_ids, calendar, out_dir, git_commit="unknown"):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    cid_of = dict(line.rstrip("\n").split("\t") for line in open(company_ids) if line.strip())
    cid_of = {k.zfill(10): int(v) for k, v in cid_of.items()}
    cells, cols = {}, {}
    for fam in FAMILIES:
        cells[fam] = [json.loads(line) for line in open(Path(replay_dir) / f"is_{fam}_cells.jsonl")]
        for c in cells[fam]:
            if c["state"].startswith("prod_only"):
                raise SystemExit(f"{fam}: production-derived row in the replay; rerun is_replay.py (it no longer reads production)")
            if c.get("original") and c.get("accession"):
                cols.setdefault((c["cik"], c["start"], c["end"]), c["accession"])
    accs = set(cols.values()) | {c.get("accession") for f in FAMILIES for c in cells[f]}
    slots = {}
    for line in open(slots_path):
        sl = json.loads(line)
        if sl["adsh"] in accs:
            slots[(sl["adsh"], sl["family"])] = sl
    fsn_of = {}
    for p in sorted(glob.glob(f"{is_fsn}/*_is_pre.jsonl.gz")):
        per = Path(p).name.split("_")[0]
        for line in gzip.open(p, "rt"):
            a = line[line.find('"adsh": "') + 9:][:20]
            if a in accs:
                fsn_of.setdefault(a, per)
    rows, stats, codes = [], defaultdict(Counter), {}
    cal = load_calendar(calendar)
    odd_calendar = set()  # calendar keys whose length does not match their fiscal period
    missing_company = set()
    for fam in FAMILIES:
        got = {}
        reasons = []
        if fam in NOT_PRESENTED:
            p = Path(np_root) / fam / f"{NOT_PRESENTED[fam]}_not_presented_prod_blank_reason_only.jsonl"
            reasons = [json.loads(line) for line in open(p)]
        for kind, items in (("cell", cells[fam]), ("reason", reasons)):
            for x in items:
                key = (x["cik"], x.get("start") or x["period_start"], x.get("end") or x["period_end"])
                g = grain(key[1], key[2])
                if g is None:
                    stats[fam]["dropped_ytd_not_a_v1_grain"] += 1
                    continue
                if key in got:
                    stats[fam][f"{kind}_key_already_has_a_row"] += 1
                    continue
                cid = cid_of.get(key[0])
                if cid is None:
                    missing_company.add(key[0])
                    continue
                acc = x.get("accession") or x["input_refs"]["accession"]
                slot = slots.get((acc, fam))
                got[key] = (from_cell(cid, fam, x, g, fsn_of, slot) if kind == "cell"
                            else from_reason(cid, fam, x, g, fsn_of, slot))
        for key, acc in cols.items():
            g = grain(key[1], key[2])
            if key in got or g is None:
                continue
            cid = cid_of.get(key[0])
            if cid is None:
                missing_company.add(key[0])
                continue
            got[key] = from_held_filing(cid, key[0], fam, key, acc, g, fsn_of, slots.get((acc, fam)))
            stats[fam]["held_column_of_original_filing"] += 1
        for cik, keys in cal.items():
            cid = cid_of.get(cik)
            for s0, e0, fy, fp in keys:
                d = _days(s0, e0)
                if not (FY_DAYS[0] <= d <= FY_DAYS[1] if fp == "FY" else Q4_DAYS[0] <= d <= Q4_DAYS[1]):
                    odd_calendar.add((cik, s0, e0, fp))
                    continue
                if (cik, s0, e0) in got:
                    stats[fam][f"calendar_key_has_row:{got[(cik, s0, e0)]['state']}"] += 1
                elif cid is not None:
                    got[(cik, s0, e0)] = from_calendar(cid, cik, fam, s0, e0, fy, fp)
                    stats[fam]["calendar_key_blank_no_filed_column"] += 1
        for r in got.values():
            stats[fam][f"state:{r['state']}"] += 1
            if r["state"] == "defect":
                stats[fam][f"defect:{r['reason_code']}"] += 1
                if r["reason_code"] in DEFECT:
                    codes[r["reason_code"]] = DEFECT[r["reason_code"]][2]
            stats[fam][f"grain:{r['period_grain']}"] += 1
        rows += [got[k] for k in sorted(got)]
    keys = [(r["company_id"], r["data_point_name"], r["period_grain"], r["period_start"], r["period_end"]) for r in rows]
    assert len(keys) == len(set(keys)), "duplicate cell key"
    bad = [r for r in rows if r["period_end"] < "2014-01-01"]
    rows = [r for r in rows if r["period_end"] >= "2014-01-01"]
    body = "".join(json.dumps(r, sort_keys=True) + "\n" for r in rows).encode()
    path = out / "cells.jsonl.gz"
    with gzip.GzipFile(path, "wb", mtime=0) as fh:
        fh.write(body)
    manifest = {
        "family": FAMILY, "rule_id": "slot.is_core@1", "rule_ids": sorted({r["rule_id"] for r in rows}),
        "git_commit": git_commit, "produced_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "rows": len(rows), "sha256": hashlib.sha256(body).hexdigest(), "sha256_gz": hashlib.sha256(path.read_bytes()).hexdigest(),
        "companies": len({r["company_id"] for r in rows}), "data_points": sorted(DATA_POINT.values()),
        "period_floor": "2014-01-01", "fsn_sets": [min(fsn_of.values()), max(fsn_of.values())],
        "reason_codes_declared": dict(sorted(codes.items())),
        "dropped_before_floor": len(bad),
        "calendar_keys_skipped_length_not_their_period": sorted(map(list, odd_calendar)), "cohort_ciks_without_company_id": sorted(missing_company),
        "by_data_point": {DATA_POINT[f]: dict(sorted(stats[f].items(), key=lambda x: -x[1])) for f in FAMILIES},
        "notes": [
            "value cells are the filing's own printed face line (core.fact of that accession)",
            "6- and 9-month YTD columns are dropped (v1 grains are FY/Q/I); no quarter is derived here (fsn_select.py derives under SAME_BASIS)",
            "restated periods whose copies disagree are defect/guard_hidden restated_copies_disagree (founder ruling)",
        ],
    }
    json.dump(manifest, open(out / "manifest.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in manifest.items() if k != "by_data_point"}, indent=1))
    for dp, s in manifest["by_data_point"].items():
        print(dp, {k: v for k, v in s.items() if k.startswith(("state:", "grain:", "dropped", "held_col"))})


if __name__ == "__main__":
    main(*sys.argv[1:9])
