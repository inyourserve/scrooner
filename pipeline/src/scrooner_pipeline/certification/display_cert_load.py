"""Load a signed display certificate (markdown, produced by display_cert.render) into
analytics.display_cell_certificate (migration 0132). Review-response plan P1.3.

Dry-run is the default: it parses and checks, prints the rows, writes nothing. `--apply` inserts (one transaction,
ON CONFLICT DO NOTHING, so re-loading the same certificate is a no-op) and needs the founder's typed words because it
is a production write. The checks refuse a certificate whose cited coverage file does not hash to the sha256 it
states, whose verdict is not PASS, or whose drawn cell is not a SHOWN_VALUE cell of that coverage file with the same
accession and value.

    python -m scrooner_pipeline.certification.display_cert_load CERT.md --proof-version V [--apply]

proof_version must be the resolver_version string the draw ran under (the value cell_display_state.resolver_version
holds for those cells), because the status view compares the two. It is not in the markdown, so it is required.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from scrooner_pipeline.mapper.cell_display_state import grain_of

TITLE_RE = re.compile(r"^# (\S+) display certification, (\d{4}-\d{2}-\d{2}).*?: (\w+)\s*$", re.M)
APPROVER_RE = re.compile(r"^Approver: (.+?)(?:, session \S+)?\. Request:", re.M)
COVERAGE_RE = re.compile(r"^Coverage: `([^`]+)`, sha256 `([0-9a-f]{64})`", re.M)
SEED_RE = re.compile(r"\(seed `([^`]+)`\)")
ROW_RE = re.compile(
    r"^\| (\d+) \| (\S+) \| (\d{4}) \| (-?[0-9.]+) \| (\d{10}-\d{2}-\d{6}) \| (R\d+) \| (.+?) \|\s*$", re.M
)


@dataclass(frozen=True)
class CertCell:
    company_id: int
    data_point: str
    period_end: str
    grain: str
    fiscal_year: int
    shown_value: Decimal
    accession: str
    r_page: str
    tag: str


@dataclass(frozen=True)
class Certificate:
    ticker: str
    verdict: str
    certified_on: str
    approver: str
    coverage_path: str
    sample_hash: str
    seed: str | None
    cells: tuple[CertCell, ...]
    path: str


def parse(md_path: Path, repo_root: Path) -> Certificate:
    """Parse and verify one certificate against its coverage file. Raises ValueError on any disagreement."""
    text = md_path.read_text(encoding="utf-8")
    t = TITLE_RE.search(text)
    a = APPROVER_RE.search(text)
    c = COVERAGE_RE.search(text)
    if not (t and a and c):
        raise ValueError(f"{md_path.name}: title, approver or coverage line not found")
    ticker, day, verdict = t.group(1), t.group(2), t.group(3)
    if verdict != "PASS":
        raise ValueError(f"{md_path.name}: verdict is {verdict}, only PASS certificates are loaded")
    cov_path = repo_root / c.group(1)
    actual = hashlib.sha256(cov_path.read_bytes()).hexdigest()
    if actual != c.group(2):
        raise ValueError(f"{md_path.name}: coverage file hashes to {actual}, certificate states {c.group(2)}")
    shown: dict[tuple[str, str], dict[str, str]] = {}
    with cov_path.open(newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["display"] == "SHOWN_VALUE":
                shown[(r["data_point"], r["fiscal_year"])] = r
    cells: list[CertCell] = []
    for m in ROW_RE.finditer(text):
        _n, dp, fy, val, acc, rpage, tag = m.groups()
        r = shown.get((dp, fy))
        if r is None:
            raise ValueError(f"{md_path.name}: drawn cell {dp} FY{fy} is not a SHOWN_VALUE cell of the coverage file")
        if r["accession"] != acc:
            raise ValueError(f"{md_path.name}: {dp} FY{fy} accession {acc} != coverage {r['accession']}")
        if Decimal(r["shown_value"]) != Decimal(val):
            raise ValueError(f"{md_path.name}: {dp} FY{fy} shown {val} != coverage {r['shown_value']}")
        cells.append(CertCell(int(r["company_id"]), dp, r["period_end"], grain_of(dp), int(fy), Decimal(val), acc, rpage, tag))
    if not cells:
        raise ValueError(f"{md_path.name}: no drawn-cell table rows found")
    seed = SEED_RE.search(text)
    return Certificate(ticker, verdict, day, a.group(1), c.group(1), c.group(2), seed.group(1) if seed else None, tuple(cells), str(md_path.relative_to(repo_root)) if md_path.is_absolute() and repo_root in md_path.parents else str(md_path))


INSERT = """
insert into analytics.display_cell_certificate
  (company_id, data_point, period_end, grain, fiscal_year, shown_value, proof_version, accession, r_page, tag,
   sample_hash, draw_seed, certificate_path, approver, certified_at)
values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
on conflict (company_id, data_point, period_end, grain, sample_hash) do nothing
"""


def rows(cert: Certificate, proof_version: str) -> list[tuple]:
    when = datetime.fromisoformat(cert.certified_on).replace(tzinfo=timezone.utc)
    return [
        (c.company_id, c.data_point, c.period_end, c.grain, c.fiscal_year, c.shown_value, proof_version, c.accession,
         c.r_page, c.tag, cert.sample_hash, cert.seed, cert.path, cert.approver, when)
        for c in cert.cells
    ]


def load(conn, cert: Certificate, proof_version: str, apply: bool) -> int:
    """Insert (apply) or only count what would be inserted (dry run). Returns rows that are / would be new."""
    data = rows(cert, proof_version)
    with conn.cursor() as cur:
        cur.execute("set local statement_timeout = 60000")
        if not apply:
            cur.execute(
                "select count(*) from unnest(%s::bigint[], %s::text[], %s::date[], %s::text[]) "
                "as t(c, d, p, g) where not exists (select 1 from analytics.display_cell_certificate x "
                "where x.company_id = t.c and x.data_point = t.d and x.period_end = t.p and x.grain = t.g "
                "and x.sample_hash = %s)",
                ([r[0] for r in data], [r[1] for r in data], [r[2] for r in data], [r[3] for r in data], cert.sample_hash),
            )
            n = cur.fetchone()[0]
            conn.rollback()
            return n
        before = cur.execute("select count(*) from analytics.display_cell_certificate").fetchone()[0]
        cur.executemany(INSERT, data)
        after = cur.execute("select count(*) from analytics.display_cell_certificate").fetchone()[0]
    conn.commit()
    return after - before


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("certificate", type=Path)
    ap.add_argument("--proof-version", required=True)
    ap.add_argument("--apply", action="store_true", help="write (production write: founder's typed words)")
    ap.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[4])
    ap.add_argument("--db-url", default=os.environ.get("DATABASE_URL"))
    args = ap.parse_args(argv)
    cert = parse(args.certificate.resolve(), args.repo_root)
    print(f"{cert.ticker} {cert.certified_on} {cert.verdict}: {len(cert.cells)} drawn cells, sample_hash {cert.sample_hash[:12]}")
    if not args.db_url:
        print("dry run (no DATABASE_URL): parsed and verified against the coverage file only")
        return 0
    import psycopg

    with psycopg.connect(args.db_url) as conn:
        n = load(conn, cert, args.proof_version, args.apply)
    print(f"{'inserted' if args.apply else 'would insert'} {n} row(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
