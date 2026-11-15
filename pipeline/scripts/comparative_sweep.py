"""Read-only sweep: every top-100 REASON cell with a no-filing code whose period a later (or own) annual filing presents.

usage: python3 pipeline/scripts/comparative_sweep.py <top100-coverage.csv> <out.csv>
Writes ticker, data_point, fiscal_year, period_end, reason_code, presenting_accession, form, stmt, r_page,
tags_with_stored_value (tag=value of the concept's mapped tags, undimensioned, in that filing's column), n_columns.
Run it from pipeline/ (settings read .env from the cwd). Logic: scrooner_pipeline.mapper.comparative_guard."""

import csv
import sys
from datetime import date
from decimal import Decimal

from scrooner_pipeline.db.connection import get_connection
from scrooner_pipeline.common.fsn_dates import fsn_end_matches
from scrooner_pipeline.mapper import comparative_guard as cg
from scrooner_pipeline.mapper import reason_guard as rg
from scrooner_pipeline.mapper.top100_coverage import INSTANT_DPS


def main(src: str, out: str) -> int:
    rows = [
        r
        for r in csv.DictReader(open(src, newline=""))
        if r["class"] == "REASON" and r["reason_code"] in cg.NO_FILING_CODES
    ]
    ids = sorted({int(r["company_id"]) for r in rows})
    with get_connection() as conn:
        conn.execute("set transaction read only")
        conn.execute("set statement_timeout = '10min'")
        cols = cg.read_columns(conn, ids)
        tags = rg.concept_tags(conn, {r["data_point"] for r in rows})
        result = []
        for r in rows:
            cid = int(r["company_id"])
            end = date.fromisoformat(r["period_end"])
            instant = r["data_point"] in INSTANT_DPS
            hit = cg.presenting(cols.get(cid, []), end, instant)
            if not hit:
                continue
            h = hit[0]
            facts = rg.read_facts(
                conn, cid, {(h.accession, t) for t in tags.get(r["data_point"], set())}
            )
            vals = []
            for t in sorted(tags.get(r["data_point"], set())):
                for f in facts.get((h.accession, t), []):
                    if not f.dim and fsn_end_matches(f.ddate, end) and f.qtrs == h.qtrs:
                        vals.append(f"{t}={Decimal(f.value)}")
            result.append(
                {
                    "ticker": r["ticker"],
                    "data_point": r["data_point"],
                    "fiscal_year": r["fiscal_year"],
                    "period_end": r["period_end"],
                    "reason_code": r["reason_code"],
                    "presenting_accession": h.accession,
                    "form": h.form,
                    "stmt": h.stmt,
                    "r_page": f"R{h.report}.htm" if h.report else "",
                    "stored_value": ";".join(vals),
                    "n_columns": len(hit),
                }
            )
    with open(out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(result[0]) if result else [])
        w.writeheader()
        w.writerows(result)
    print(
        len(rows),
        "no-filing REASON cells;",
        len(result),
        "presented by an annual filing",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
