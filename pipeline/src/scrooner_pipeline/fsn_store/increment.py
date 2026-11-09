"""Nightly hybrid incremental: the day's new 10-K/10-Q filings -> EDGAR-built FSN rows -> company dirs.

Design: data-team/strategy/team/FSN-NIGHTLY-INCREMENTAL-DESIGN-2026-11-09.md.

1. `candidates`: cohort companies' periodic filings (10-K, 10-Q, their transition forms and
   amendments) with a period on or after the 2014-01-01 floor, filed in the last `lookback_days`,
   whose accession the store does not hold yet (fsn.filing). One indexed read, statement_timeout 15s.
2. `build`: per filing, fetch its XBRL from EDGAR (edgar_fetch, sec.gov, <= 4 req/s) and convert it
   (xbrl_fsn). One filing failing never stops the night: it is reported and the next night's
   lookback picks it up again, because it is still not in fsn.filing.
3. `write_dirs`: companies/<cik>/ directories in the shard layout (FORMATS-v1 §1), fsn_set
   'edgar:<date>', one sha256 per accession, for `scrooner-fsn load --increment`.

When the SEC FSN set holding an accession later arrives, the full company reload (fsn_store.load)
replaces the EDGAR-built copy of that accession (dedupe by accession) and keeps the rest.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable

import structlog

from scrooner_pipeline.fsn_store.company_dir import PERIODIC_FORMS, TABLES
from scrooner_pipeline.fsn_store.xbrl_fsn import (
    COLUMNS,
    ConversionError,
    FilingFiles,
    convert,
    shard_filter,
)

logger = structlog.get_logger()
PERIOD_FLOOR = "2014-01-01"
EDGAR_SET_PREFIX = "edgar:"  # = fsn_store.load.EDGAR_SET_PREFIX
STATEMENT_TIMEOUT = "15s"


@dataclass
class Candidate:
    company_id: int
    cik: str
    accession: str
    form: str
    filing_date: str
    period: str


@dataclass
class BuildResult:
    built: dict[str, list[dict[str, list[dict[str, str]]]]] = field(
        default_factory=lambda: defaultdict(list)
    )
    failed: list[dict[str, Any]] = field(default_factory=list)
    deferred: list[dict[str, Any]] = field(default_factory=list)
    requests_seconds: float = 0.0


def set_end(fsn_set: str) -> date | None:
    """Last day an FSN set covers: '2026m10' -> 2026-10-31, '2026q3' -> 2026-09-30."""
    import re
    from calendar import monthrange

    m = re.fullmatch(r"(\d{4})m(\d{2})", fsn_set) or re.fullmatch(
        r"(\d{4})q([1-4])", fsn_set
    )
    if not m:
        return None
    year, n = int(m.group(1)), int(m.group(2))
    month = n if "m" in fsn_set else 3 * n
    return date(year, month, monthrange(year, month)[1])


def since_last_set(conn: Any) -> date | None:
    """The day after the latest SEC FSN set the store holds (EDGAR-built filings excluded): every
    periodic filing from then on is either built by this path or still missing (backfill)."""
    conn.execute(f"set statement_timeout = '{STATEMENT_TIMEOUT}'")
    sets = [
        r[0]
        for r in conn.execute(
            "select distinct fsn_set from fsn.filing where fsn_set not like 'edgar:%'"
        ).fetchall()
    ]
    conn.rollback()
    ends = [e for e in (set_end(s) for s in sets) if e is not None]
    return (max(ends) + timedelta(days=1)) if ends else None


def candidates(conn: Any, ciks: list[str], since: date) -> list[Candidate]:
    """New periodic filings of the given companies not yet in the store (read-only)."""
    conn.execute(f"set statement_timeout = '{STATEMENT_TIMEOUT}'")
    rows = conn.execute(
        """
        select f.company_id, c.cik, f.accession_number, f.form, f.filing_date::text, f.period_of_report::text
        from core.company c
        join core.filing f on f.company_id = c.id
        where c.cik = any(%s)
          and f.form = any(%s)
          and f.filing_date >= %s
          and f.period_of_report >= %s
          and not exists (select 1 from fsn.filing s where s.accession = f.accession_number)
        order by f.filing_date, c.cik, f.accession_number
        """,
        ([c.zfill(10) for c in ciks], sorted(PERIODIC_FORMS), since, PERIOD_FLOOR),
    ).fetchall()
    conn.rollback()
    return [Candidate(int(a), b, c, d, e, f) for a, b, c, d, e, f in rows]


def build(
    cands: list[Candidate],
    fetch: Callable[[Candidate], FilingFiles],
    *,
    max_seconds: float | None = None,
    clock: Callable[[], float] = time.monotonic,
) -> BuildResult:
    """Fetch and convert each candidate; failures and the over-budget rest are reported, not raised."""
    out = BuildResult()
    t0 = clock()
    for i, c in enumerate(cands):
        if max_seconds is not None and clock() - t0 > max_seconds:
            out.deferred.extend(
                {"cik": d.cik, "accession": d.accession} for d in cands[i:]
            )
            logger.warning("fsn_nightly.time_budget", deferred=len(cands) - i)
            break
        try:
            tables = convert(fetch(c))
            sub = tables["sub"][0]
            if sub["form"] not in PERIODIC_FORMS:
                raise ConversionError(f"form {sub['form']!r} is not periodic")
            out.built[c.cik].append(tables)
        except Exception as exc:  # noqa: BLE001  one filing must not stop the night
            out.failed.append(
                {"cik": c.cik, "accession": c.accession, "error": repr(exc)[:300]}
            )
            logger.warning(
                "fsn_nightly.filing_failed",
                cik=c.cik,
                accession=c.accession,
                error=repr(exc)[:200],
            )
    out.requests_seconds = round(clock() - t0, 1)
    return out


def _zst(path: Path, columns: tuple[str, ...], rows: list[dict[str, str]]) -> str:
    body = (
        "\n".join(
            [
                "\t".join(columns),
                *("\t".join(r.get(c, "") for c in columns) for r in rows),
            ]
        )
        + "\n"
    )
    raw = subprocess.run(
        ["zstd", "-q", "-c", "-3"], input=body.encode(), capture_output=True, check=True
    ).stdout
    path.write_bytes(raw)
    return hashlib.sha256(raw).hexdigest()


def accession_sha256(tables: dict[str, list[dict[str, str]]]) -> str:
    """A stable hash of one filing's converted rows (the increment's idempotency key)."""
    h = hashlib.sha256()
    for t in TABLES:
        cols = [c for c in COLUMNS[t] if c != "fsn_set"]
        for r in tables.get(t, []):
            h.update(("\t".join(r.get(c, "") for c in cols) + "\n").encode())
    return h.hexdigest()


def write_dirs(
    root: Path,
    built: dict[str, list[dict[str, list[dict[str, str]]]]],
    company_ids: dict[str, int],
    fsn_set: str,
) -> list[str]:
    """companies/<cik>/ per company with the shard's filter applied; returns the CIKs written."""
    written = []
    for cik, filings in sorted(built.items()):
        d = root / cik
        d.mkdir(parents=True, exist_ok=True)
        merged: dict[str, list[dict[str, str]]] = {t: [] for t in TABLES}
        acc_sha = {}
        seen_tag: set[tuple[str, str]] = set()
        seen_dim: set[str] = set()
        for tables in filings:
            view = shard_filter(tables)
            for r in view["sub"]:
                r["fsn_set"] = fsn_set
            acc_sha[view["sub"][0]["adsh"]] = accession_sha256(view)
            for t in ("sub", "pre", "num", "cal", "ren"):
                merged[t].extend(view[t])
            for r in view["tag"]:
                if (r["tag"], r["version"]) not in seen_tag:
                    seen_tag.add((r["tag"], r["version"]))
                    merged["tag"].append(r)
            for r in view["dim"]:
                if r["dimhash"] not in seen_dim:
                    seen_dim.add(r["dimhash"])
                    merged["dim"].append(r)
        shas = {t: _zst(d / f"{t}.tsv.zst", COLUMNS[t], merged[t]) for t in TABLES}
        manifest = {
            "cik": cik,
            "company_id": company_ids.get(cik),
            "fsn_sets": [fsn_set],
            "increment": True,
            "accessions": sorted(acc_sha),
            "accession_sha256": acc_sha,
            "row_counts": {t: len(merged[t]) for t in TABLES},
            "file_sha256": shas,
            "input_sha256": hashlib.sha256(
                "\n".join(shas[t] for t in TABLES).encode()
            ).hexdigest(),
            "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }
        (d / "manifest.json").write_text(json.dumps(manifest, indent=1))
        written.append(cik)
    return written
