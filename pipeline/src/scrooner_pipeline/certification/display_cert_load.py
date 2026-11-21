"""Load a PASS display certificate (JSON, schema display-certificate/1, written by pipeline/scripts/certify_display.py)
into analytics.display_cell_certificate (migration 0132). Review-response plan P1.3; approver rulings
data-team/strategy/approvals/CERT-REGISTRY-rulings-2026-11-21.md.

Every cell of the certificate is loaded, shown and hidden, each with its evidence class (drawn / census / sampled).
Versions and identity (sample_hash, detector_version, resolver, code_sha) come from the certificate; there is no
version argument. Money is parsed with Decimal from the decimal strings.

Dry-run is the default: it validates and counts, writes nothing. `--apply` inserts in one transaction (ON CONFLICT DO
NOTHING, so a re-load is a no-op), then calls analytics.invalidate_display_cell_certificates(company) in the same
transaction so an older certificate of the company is marked superseded. It is a production write and needs the
founder's typed words. Refused: a non-PASS verdict, a schema violation, a coverage file that does not hash to the stated
sha256, a SHOWN cell that disagrees with the coverage file, a sampled cell not marked SAMPLED, a drawn cell not MATCH,
a bound whose n is not the drawn count.

    python -m scrooner_pipeline.certification.display_cert_load CERT.json [--apply]
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any

SCHEMA_PATH = (
    Path(__file__).resolve().parent / "schemas" / "display_certificate.v1.schema.json"
)
CHUNK = 5000


@dataclass(frozen=True)
class CertCell:
    data_point: str
    fiscal_year: int
    period_end: date
    grain: str
    display: str
    hide_class: str | None
    reason_code: str | None
    shown_value: Decimal | None
    accession: str | None
    r_page: str | None
    tag: str | None
    restate_keys: tuple[
        tuple[str, str], ...
    ]  # (tag, dims) the restatement check compares
    evidence: str
    result: str


@dataclass(frozen=True)
class Certificate:
    ticker: str
    company_id: int
    verdict: str
    certified_at: datetime
    approver: str
    coverage_path: str
    sample_hash: str
    seed: str | None
    detector_version: str | None
    resolver: str | None
    code_sha: str | None
    drawn: int
    cells: tuple[CertCell, ...]
    path: str


def validate(instance: Any, schema: dict, where: str = "$") -> list[str]:
    """Minimal JSON Schema check for the keywords display_certificate.v1 uses (no new dependency)."""
    errs: list[str] = []
    if "const" in schema and instance != schema["const"]:
        errs.append(f"{where}: expected {schema['const']!r}")
    if "enum" in schema and instance not in schema["enum"]:
        errs.append(f"{where}: {instance!r} not in {schema['enum']}")
    t = schema.get("type")
    if t is not None:
        types = t if isinstance(t, list) else [t]
        py = {
            "string": str,
            "integer": int,
            "object": dict,
            "array": list,
            "null": type(None),
        }
        ok = any(
            isinstance(instance, py[x])
            and not (x == "integer" and isinstance(instance, bool))
            for x in types
        )
        if not ok:
            return errs + [f"{where}: expected {types}, got {type(instance).__name__}"]
    if isinstance(instance, str):
        if "pattern" in schema and not re.search(schema["pattern"], instance):
            errs.append(f"{where}: {instance!r} does not match {schema['pattern']}")
        if len(instance) < schema.get("minLength", 0):
            errs.append(f"{where}: shorter than {schema['minLength']}")
    if isinstance(instance, dict):
        for req in schema.get("required", []):
            if req not in instance:
                errs.append(f"{where}: missing {req}")
        props = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            for k in instance:
                if k not in props:
                    errs.append(f"{where}: unexpected {k}")
        for k, sub in props.items():
            if k in instance:
                errs += validate(instance[k], sub, f"{where}.{k}")
        ap = schema.get("additionalProperties")
        if isinstance(ap, dict):
            for k, v in instance.items():
                if k not in props:
                    errs += validate(v, ap, f"{where}.{k}")
    if isinstance(instance, list) and "items" in schema:
        for i, v in enumerate(instance):
            errs += validate(v, schema["items"], f"{where}[{i}]")
    return errs


def _opt(v: Any) -> Any:
    """An optional text field: '' or whitespace is NULL (0134 CHECK; a '' hide_class read every shown cell as stale_display)."""
    if isinstance(v, str):
        v = v.strip()
        return v or None
    return v


def _restate_keys(cell: dict) -> tuple[tuple[str, str], ...]:
    if cell["display"] != "SHOWN_VALUE":
        return ()
    if cell["parts"]:
        return tuple(
            dict.fromkeys((p["tag"], p.get("dims") or "") for p in cell["parts"])
        )
    return ((cell["tag"], ""),) if cell["tag"] else ()


def parse(json_path: Path, repo_root: Path) -> Certificate:
    """Validate one certificate against the schema and its coverage file. Raises ValueError on any disagreement."""
    name = json_path.name
    doc = json.loads(json_path.read_text(encoding="utf-8"), parse_float=Decimal)
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    errs = validate(doc, schema)
    if errs:
        raise ValueError(f"{name}: schema violations: " + "; ".join(errs[:5]))
    if doc["verdict"] != "PASS":
        raise ValueError(
            f"{name}: verdict is {doc['verdict']}, only PASS certificates are loaded"
        )
    if doc["company_id"] is None:
        raise ValueError(
            f"{name}: company_id is null (certificate made without --request)"
        )
    if doc["sample_hash"] != doc["coverage_sha256"]:
        raise ValueError(f"{name}: sample_hash differs from coverage_sha256")
    cov_path = repo_root / doc["coverage_path"]
    actual = hashlib.sha256(cov_path.read_bytes()).hexdigest()
    if actual != doc["coverage_sha256"]:
        raise ValueError(
            f"{name}: coverage file hashes to {actual}, certificate states {doc['coverage_sha256']}"
        )
    shown: dict[tuple[str, str], dict[str, str]] = {}
    with cov_path.open(newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["display"] == "SHOWN_VALUE":
                shown[(r["data_point"], r["fiscal_year"])] = r
    cells: list[CertCell] = []
    seen: set[tuple[str, str, str]] = set()
    for c in doc["cells"]:
        key = (c["data_point"], c["period_end"], c["grain"])
        if key in seen:
            raise ValueError(f"{name}: duplicate cell {key}")
        seen.add(key)
        if (c["evidence"] == "sampled") != (c["result"] == "SAMPLED"):
            raise ValueError(
                f"{name}: {key} evidence {c['evidence']} with result {c['result']}"
            )
        if c["evidence"] == "drawn" and c["result"] != "MATCH":
            raise ValueError(
                f"{name}: drawn cell {key} result {c['result']}, a PASS certificate needs MATCH"
            )
        value = None
        if c["display"] == "SHOWN_VALUE":
            sr = shown.get((c["data_point"], c["fiscal_year"]))
            if sr is None or c["shown_value"] is None or c["accession"] is None:
                raise ValueError(
                    f"{name}: shown cell {key} is not a complete SHOWN_VALUE cell of the coverage file"
                )
            value = Decimal(c["shown_value"])
            if sr["accession"] != c["accession"] or Decimal(sr["shown_value"]) != value:
                raise ValueError(
                    f"{name}: {key} disagrees with the coverage file (accession or value)"
                )
        elif c["shown_value"] is not None:
            raise ValueError(f"{name}: hidden cell {key} carries a shown_value")
        cells.append(
            CertCell(
                c["data_point"],
                int(c["fiscal_year"]),
                date.fromisoformat(c["period_end"]),
                c["grain"],
                c["display"],
                _opt(c["hide_class"]),
                _opt(c["reason_code"]),
                value,
                _opt(c["accession"]),
                _opt(c["r_page"]),
                _opt(c["tag"]),
                _restate_keys(c),
                c["evidence"],
                c["result"],
            )
        )
    drawn = sum(1 for x in cells if x.evidence == "drawn")
    if drawn != doc["bound"]["n"]:
        raise ValueError(f"{name}: bound.n {doc['bound']['n']} != {drawn} drawn cells")
    if not cells:
        raise ValueError(f"{name}: no cells")
    when = datetime.fromisoformat(doc["certified_at"])
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)
    try:
        rel = str(json_path.relative_to(repo_root))
    except ValueError:
        rel = str(json_path)
    return Certificate(
        doc["ticker"],
        doc["company_id"],
        doc["verdict"],
        when,
        doc["approver"],
        doc["coverage_path"],
        doc["sample_hash"],
        _opt(doc["seed"]),
        _opt(doc["detector_version"]),
        _opt(doc["resolver"]),
        _opt(doc["code_sha"]),
        drawn,
        tuple(cells),
        rel,
    )


INSERT = """
insert into analytics.display_cell_certificate
  (company_id, data_point, period_end, grain, fiscal_year, display, hide_class, reason_code, shown_value, accession,
   r_page, tag, restate_keys, evidence, result, sample_hash, detector_version, resolver, code_sha, draw_seed,
   certificate_path, approver, certified_at)
values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
on conflict (company_id, data_point, period_end, grain, sample_hash) do nothing
"""


def rows(cert: Certificate) -> list[tuple]:
    from psycopg.types.json import Jsonb

    return [
        (
            cert.company_id,
            c.data_point,
            c.period_end,
            c.grain,
            c.fiscal_year,
            c.display,
            c.hide_class,
            c.reason_code,
            c.shown_value,
            c.accession,
            c.r_page,
            c.tag,
            Jsonb([{"tag": t, "dims": d} for t, d in c.restate_keys]),
            c.evidence,
            c.result,
            cert.sample_hash,
            cert.detector_version,
            cert.resolver,
            cert.code_sha,
            cert.seed,
            cert.path,
            cert.approver,
            cert.certified_at,
        )
        for c in cert.cells
    ]


def load(conn, cert: Certificate, apply: bool) -> int:
    """Insert (apply) or only count what would be inserted (dry run). Returns rows that are / would be new."""
    data = rows(cert)
    with conn.cursor() as cur:
        cur.execute("set local statement_timeout = 120000")
        if not apply:
            cur.execute(
                "select count(*) from unnest(%s::text[], %s::date[], %s::text[]) as t(d, p, g) "
                "where not exists (select 1 from analytics.display_cell_certificate x where x.company_id = %s "
                "and x.data_point = t.d and x.period_end = t.p and x.grain = t.g and x.sample_hash = %s)",
                (
                    [r[1] for r in data],
                    [r[2] for r in data],
                    [r[3] for r in data],
                    cert.company_id,
                    cert.sample_hash,
                ),
            )
            n = cur.fetchone()[0]
            conn.rollback()
            return n
        count_sql = "select count(*) from analytics.display_cell_certificate where company_id = %s"
        before = cur.execute(count_sql, (cert.company_id,)).fetchone()[0]
        for i in range(0, len(data), CHUNK):
            cur.executemany(INSERT, data[i : i + CHUNK])
        after = cur.execute(count_sql, (cert.company_id,)).fetchone()[0]
        cur.execute(
            "select analytics.invalidate_display_cell_certificates(%s)",
            (cert.company_id,),
        )
    conn.commit()
    return after - before


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("certificate", type=Path)
    ap.add_argument(
        "--apply",
        action="store_true",
        help="write (production write: founder's typed words)",
    )
    ap.add_argument(
        "--repo-root", type=Path, default=Path(__file__).resolve().parents[4]
    )
    ap.add_argument("--db-url", default=os.environ.get("DATABASE_URL"))
    args = ap.parse_args(argv)
    cert = parse(args.certificate.resolve(), args.repo_root)
    by: dict[str, int] = {}
    for c in cert.cells:
        by[c.evidence] = by.get(c.evidence, 0) + 1
    print(
        f"{cert.ticker} {cert.certified_at.date()} {cert.verdict}: {len(cert.cells)} cells {by}, sample_hash {cert.sample_hash[:12]}"
    )
    if not args.db_url:
        print(
            "dry run (no DATABASE_URL): validated against the schema and the coverage file only"
        )
        return 0
    import psycopg

    with psycopg.connect(args.db_url) as conn:
        n = load(conn, cert, args.apply)
    print(f"{'inserted' if args.apply else 'would insert'} {n} row(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
