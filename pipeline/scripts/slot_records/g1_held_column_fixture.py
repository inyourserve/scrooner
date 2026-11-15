"""G1 fixture: quarters is_core 77f5846a derived over a held 3-month column
(stdlib, run with -I). Rulings (Dhairya 2026-11-01, FSN-STORE-DESIGN section 4):
a printed 3-month column always wins, even when held; the winner among
prints is the latest `accepted` print on a mapped line.

The six keys are the cells where 77f5846a published a derived quarter while
the original filing of that quarter had a held column (gate D of
IS-PORT-REGRESSION-2026-11-01). A print = an undimensioned 3-month value
(num qtrs 1, dimn 0, iprx 0, no coreg) of a slot tag at the period end, in any
filing of the company (the original or a later 10-Q's comparative column).
Expected fsn_select outcome:
  * a print in a LATER filing   -> that latest print's value, provided its
    line maps to the concept (the fixture names the filing; the line_map of
    that filing decides; if it is held too, the next rule applies);
  * else a print in the original on a held line -> blank with that gate;
  * else a print in the original on a mapped line -> that value;
  * no print at all -> derived if SAME_BASIS holds, else blank
    mixed_vintage_inputs / no_basis_witness.
usage: g1_held_column_fixture.py <is_core_77f5846a cells.jsonl.gz> <dir with sub.tsv, num.tsv> <out.json>
  <dir>: FSN sub and num rows of the cases' accessions (bucket fsn-notes)
"""
import csv
import gzip
import json
import sys

# key -> (slot tag(s), the original filing of the quarter, its gate in the 77f5846a slot run)
CASES = {
    (1227, "net_income_resolved", "Q", "2023-04-01", "2023-06-30"): ("NetIncomeLoss", "0000352541-23-000091", "G1_printed_line"),
    (1227, "net_income_resolved", "Q", "2023-07-01", "2023-09-30"): ("NetIncomeLoss", "0000352541-23-000108", "G1_printed_line"),
    (3922, "revenue_sanity_resolved", "Q", "2019-04-01", "2019-06-30"):
        ("RevenueFromContractWithCustomerExcludingAssessedTax", "0001564590-19-028999", "G1_printed_total"),
    (3922, "revenue_sanity_resolved", "Q", "2019-07-01", "2019-09-30"):
        ("RevenueFromContractWithCustomerExcludingAssessedTax", "0001564590-19-040692", "G1_printed_total"),
    (5448, "revenue_sanity_resolved", "Q", "2020-08-02", "2020-10-31"):
        ("RevenueFromContractWithCustomerIncludingAssessedTax,Revenues", "0001558370-20-014262", "hold_multiple_roots"),
    (5904, "operating_income_resolved", "Q", "2021-07-01", "2021-09-30"): ("OperatingIncomeLoss", "0001451505-21-000086", "G1_printed_line"),
}
NUM_COLS = ("tag", "ddate", "qtrs", "uom", "dimn", "coreg", "iprx", "value", "dcml")


def tsv(path):
    return list(csv.DictReader(open(path), delimiter="\t", quoting=csv.QUOTE_NONE))


def is_print(n, end):
    return n["ddate"] == end and n["qtrs"] == "1" and n["dimn"] == "0" and n["iprx"] == "0" and not n["coreg"]


def main(cells_path, fsn_dir, out_path):
    lane = {}
    for line in gzip.open(cells_path, "rt"):
        r = json.loads(line)
        k = (r["company_id"], r["data_point_name"], r["period_grain"], r["period_start"], r["period_end"])
        if k in CASES:
            lane[k] = r
    sub = {r["adsh"]: r for r in tsv(f"{fsn_dir}/sub.tsv")}
    num = tsv(f"{fsn_dir}/num.tsv")
    cases = []
    for k, (tags, orig, gate) in CASES.items():
        cell = lane[k]
        assert cell["state"] == "derived", k
        tagset = set(tags.split(","))
        end = k[4].replace("-", "")
        cik = sub[orig]["cik"]
        accs = sorted({a for a, s in sub.items() if s["cik"] == cik} | set(cell["derivation"]["input_accessions"]),
                      key=lambda a: (sub[a].get("accepted") or "", a))
        filings = []
        for a in accs:
            s = sub[a]
            rows = [{c: n[c] for c in NUM_COLS} for n in num if n["adsh"] == a and n["tag"] in tagset and n["dimn"] == "0"]
            if not rows and a not in cell["derivation"]["input_accessions"] and a != orig:
                continue
            filings.append({
                "accession": a, "cik": s["cik"].zfill(10), "name": s["name"], "form": s["form"], "period": s["period"],
                "filed": s["filed"], "accepted": s.get("accepted"), "fy": s["fy"], "fp": s["fp"], "fsn_set": s["fsn_set"],
                "aciks": s.get("aciks") or "", "role": "original" if a == orig else (
                    "ytd_input" if a in cell["derivation"]["input_accessions"] else
                    "later_filing" if (s.get("accepted") or "") > (sub[orig].get("accepted") or "") else "earlier_filing"),
                "slot_gate_77f5846a": gate if a == orig else None,
                "prints_this_quarter": [r for r in rows if is_print(r, end)],
                "num_undimensioned": rows,
            })
        orig_f = next(f for f in filings if f["role"] == "original")
        later = [f for f in filings if f["role"] != "original" and f["prints_this_quarter"]
                 and (f["accepted"] or "") > (orig_f["accepted"] or "")]
        if later:
            w = later[-1]
            exp = {"state": "value", "value": w["prints_this_quarter"][0]["value"], "accession": w["accession"],
                   "condition": "the line of that filing maps to the concept (its line_map decides)",
                   "why": "the latest accepted print of the 3-month column wins (a later 10-Q's comparative column)"}
        elif orig_f["prints_this_quarter"] and not gate.startswith("G"):
            exp = {"state": "defect", "reason_code": gate, "value": None,
                   "why": "only the original filing prints the 3-month column, on a held line: the printed column "
                          "wins even when held, so no YTD difference is published"}
        elif orig_f["prints_this_quarter"]:
            exp = {"state": "value", "value": orig_f["prints_this_quarter"][0]["value"], "accession": orig_f["accession"],
                   "why": "printed 3-month column on a mapped line"}
        else:
            exp = {"state": "derived_or_blank", "value_if_same_basis": cell["value"],
                   "blank_reasons_otherwise": ["mixed_vintage_inputs", "no_basis_witness"],
                   "why": "no filing of the company has an undimensioned 3-month value for the slot tag at this period "
                          "end, so there is no printed candidate and the held-column rule does not apply"}
        cases.append({"case": f"{k[1]}:{k[0]}:{k[3]}..{k[4]}", "company_id": k[0], "canonical_concept": k[1],
                      "period_grain": k[2], "period_start": k[3], "period_end": k[4],
                      "lane_77f5846a": {"state": "derived", "value": cell["value"],
                                        "formula": cell["derivation"]["formula"],
                                        "inputs": cell["derivation"]["input_values"],
                                        "input_accessions": cell["derivation"]["input_accessions"]},
                      "slot_tags": sorted(tagset), "filings": filings, "expected_fsn_select": exp})
    doc = {"fixture": "G1 held printed 3-month column (FSN-STORE-DESIGN section 4; Dhairya 2026-11-01)",
           "source": "is_core 77f5846a derived cells over a held column; FSN sub/num rows of the companies' 10-Qs "
                     "around each quarter (bucket fsn-notes, undimensioned only); original-filing gates from the "
                     "77f5846a slot run (is_filing_slots of commit 78ca35e)",
           "cases": cases}
    json.dump(doc, open(out_path, "w"), indent=1)
    for c in cases:
        e = c["expected_fsn_select"]
        print(c["case"], "->", e["state"], e.get("value") or e.get("value_if_same_basis") or e.get("reason_code"),
              e.get("accession", ""))


if __name__ == "__main__":
    main(*sys.argv[1:4])
