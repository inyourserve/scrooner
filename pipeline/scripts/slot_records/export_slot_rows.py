"""Export slot records as rows shaped like analytics.company_slot_record
(migration 0110) so the certify suite and an independent approver agent can
read them. Writes JSONL only; NOTHING is inserted (the table is not applied).

Rows per BS-totals record: total_liabilities (slot_composition) and
equity_parent (tag_mapping). Rows per debt record: total_debt
(slot_composition). status is always 'proposed'; approved_by is null; the
preparer (created_by) can never approve.
usage: DATABASE_URL=... export_slot_rows.py <family: bs|debt> <records.jsonl> <out_rows.jsonl>
"""
import json
import os
import sys

import psycopg

family, src, dst = sys.argv[1], sys.argv[2], sys.argv[3]
CONCEPT = {"total_liabilities": "total_liabilities", "equity_parent": "stockholders_equity", "total_debt": "total_debt"}

conn = psycopg.connect(os.environ["DATABASE_URL"])
cur = conn.cursor()
cur.execute("set statement_timeout = '20s'")
cur.execute("select id, name from analytics.canonical_concept where name = any(%s)", (list(CONCEPT.values()),))
concept_id = {name: cid for cid, name in cur.fetchall()}
cur.execute("select cik, id from core.company")
company_id = dict(cur.fetchall())
conn.close()

n = 0
with open(dst, "w") as out:
    for line in open(src):
        r = json.loads(line)
        cid = company_id.get(r["cik"])
        if cid is None:
            continue
        base = {
            "company_id": cid, "sector_code": None,
            "taxonomy_era_from": r.get("taxonomy_era_from"), "taxonomy_era_to": r.get("taxonomy_era_to"),
            "filing_from": r["filing_from"], "filing_to": r["filing_to"],
            "period_from": r["period_from"], "period_to": r["period_to"],
            "filings_observed": r.get("filings_observed"),
            "fingerprint_hash": None, "cal_source": r.get("cal_source"),
            "evidence_accession": r["evidence_accession"], "evidence_level": r.get("evidence_level", "DATA-INFERRED"),
            "source": r.get("source"), "status": "proposed", "approved_by": None, "approved_at": None,
            "review_note": None, "supersedes_id": None, "created_by": "scrooner-25",
            "record": r,
        }
        rows = []
        if family == "bs":
            rows.append({**base, "canonical_concept_id": concept_id["total_liabilities"],
                         "slot": "bs_totals.total_liabilities", "rule_type": "slot_composition",
                         "composition_rule": r["total_liabilities_rule"],
                         "member_tags": r["total_liabilities_members"],
                         "requires_identity_tie": bool(r.get("requires_identity_tie"))})
            if r.get("equity_parent_tag"):
                rows.append({**base, "canonical_concept_id": concept_id["stockholders_equity"],
                             "slot": "bs_totals.equity_parent", "rule_type": "tag_mapping",
                             "composition_rule": "printed_total",
                             "member_tags": [{"tag": r["equity_parent_tag"], "custom": False, "weight": "1.0"}],
                             "requires_identity_tie": False})
        else:
            rows.append({**base, "canonical_concept_id": concept_id["total_debt"],
                         "slot": "total_debt.lease_inclusive", "rule_type": "slot_composition",
                         "composition_rule": "face_sum" if r.get("coverage_clean", True) else "hold_uncovered_candidates",
                         "member_tags": r["members"], "requires_identity_tie": False})
        for row in rows:
            out.write(json.dumps(row, default=str) + "\n")
            n += 1
print(f"rows {n} -> {dst} (status=proposed, nothing inserted)")
