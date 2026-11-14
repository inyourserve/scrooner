"""Read-only sweep: resolver not_presented / combined reasons whose cited filing's own column holds evidence of the
line (mapper/reason_guard.py). The Tag Expert fixes the resolver from the output.

usage: PYTHONPATH=pipeline/src python3 pipeline/scripts/false_reason_candidates.py <resolver.csv> <out.csv>
Columns: ticker, data_point, fiscal_year, accession, reason, evidence_tag, evidence_value, evidence R page,
evidence_kind (undimensioned | member_sum), resolver_version. No database write."""

import csv
import sys
from collections import Counter, defaultdict
from pathlib import Path

from scrooner_pipeline.db.connection import get_connection
from scrooner_pipeline.mapper import docmap_loader as dl
from scrooner_pipeline.mapper import structural_loader as sl
from scrooner_pipeline.mapper.note_report_lookup import load_lookup

COLUMNS = [
    "ticker",
    "data_point",
    "fiscal_year",
    "accession",
    "reason",
    "evidence_tag",
    "evidence_value",
    "evidence R page",
    "evidence_kind",
    "resolver_version",
]


def sweep(conn, resolver: Path) -> list[dict]:
    claims, _rej, _cnt = sl.read_claims(resolver)
    ver = {}
    with resolver.open(newline="") as fh:
        for r in csv.DictReader(fh):
            ver[(r["ticker"].upper(), r["data_point"], r["period_end"], r["decision"])] = r.get(
                "resolver_version", ""
            )
    with conn.cursor() as cur:
        cur.execute("select name from analytics.canonical_concept")
        names = {n for (n,) in cur.fetchall()}
        cur.execute("select cik, id from core.company where cik is not null")
        by_cik = dict(cur.fetchall())
    lookup = load_lookup()
    by_co: dict[str, list[sl.Claim]] = defaultdict(list)
    for c in claims:
        if c.cik:
            by_co[c.cik].append(c)
    out: list[dict] = []
    for cik, cs in sorted(by_co.items()):
        cid = by_cik.get(cik)
        if cid is None:
            continue
        todo = [c for c in cs if not c.no_filing and sl.rg.kind_of(c.decision)]
        if not todo:
            continue
        found = sl.reason_evidence(conn, cid, cik, todo, claims, names)
        for c, (evs, pages) in found.items():
            for e in evs:
                page = pages.get(e["tag"]) or lookup.get((c.accession, e["tag"]))
                out.append(
                    {
                        "ticker": c.ticker,
                        "data_point": c.data_point,
                        "fiscal_year": c.period_end.year,
                        "accession": c.accession,
                        "reason": c.decision,
                        "evidence_tag": e["tag"],
                        "evidence_value": e["value"]
                        if not e["member"]
                        else f"{e['value']} ({e['members']})",
                        "evidence R page": f"R{page}.htm" if page else "",
                        "evidence_kind": "member_sum" if e["member"] else "undimensioned",
                        "resolver_version": ver.get(
                            (c.ticker, c.data_point, c.period_end.isoformat(), c.decision), ""
                        ),
                    }
                )
    out.sort(key=lambda r: (r["ticker"], r["data_point"], r["fiscal_year"], r["evidence_tag"]))
    return out


def main(resolver: Path, out: Path) -> int:
    with get_connection() as conn:
        conn.execute("set transaction read only")
        conn.execute("set statement_timeout = '5min'")
        rows = sweep(conn, resolver)
    with out.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    by = Counter(r["data_point"] for r in rows)
    cells = {(r["ticker"], r["data_point"], r["fiscal_year"]) for r in rows}
    print(f"{len(rows)} evidence rows, {len(cells)} cells; per data point (rows):")
    for k, v in by.most_common():
        print(f"  {k}: {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1]), Path(sys.argv[2])))
