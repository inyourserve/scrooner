"""Self-test harness for a FUTURE fallback reader of filing facts (design + gate only).

Problem (S5, data-team/strategy/team/S5-derivation-history-fixability.md; detector
in `ingestion_detector.py`): some periodic filings are on EDGAR and in `core.filing`
but SEC's companyfacts object does not carry their facts yet (KO 10-Q
0001628280-26-050503, 88 companies / 576 TTM cells in the cohort). Waiting is the
correct default. A fallback reader that takes the facts from the filing itself
could close the gap sooner, but a second extraction path is a second way to be
wrong, so it must PROVE equivalence before it is ever allowed to write.

THE GATE (this module): a reader may be switched on only after `run_selftest`
reports `passed` on 50 distinct filings that companyfacts DOES carry, i.e.
every stored companyfacts fact of each filing is reproduced by the reader
(recall 100%, same taxonomy/tag, unit, period start/end, exactly equal value).
Facts the reader finds that companyfacts lacks (custom extension tags, dimensioned
facts) are counted as `extra` and never block the gate (ledger: custom extension
facts are absent from companyfacts by design) but they are NOT written either,
because companyfacts parity is the only contract the downstream layers know.

DESIGN of the reader (not built; no SEC fetch exists here):
  * Source: the filing's own XBRL instance from the EDGAR Archives folder of the
    accession (the extracted `<ticker>-<date>_htm.xml` instance or the inline XBRL
    document), through `common/sec_client.py` (declared User-Agent, shared limiter,
    one SEC process at a time). Never scrape R-files for values (sign and
    scale differences, ledger 2026-10-22 R-file rows).
  * Keep only facts with no dimensions, numeric, with a unit, in the taxonomies
    companyfacts publishes; value = reported value scaled by `decimals`/scale
    exactly (Decimal, never float).
  * Collector first: the fetched bytes are stored immutably (raw layer, sha256)
    BEFORE any parsing; `core.fact.raw_object_id` then points at that object, so
    every fallback fact is traceable to bytes.
  * Writes (only after the gate, through a committed migration or the existing
    `core.fact` upsert keyed on company, concept, unit, period, filing): the same
    `insert ... on conflict do update` the normal path uses, so when companyfacts
    later carries the accession the two paths converge on one row; a later value
    mismatch is an alarm, not an overwrite.
  * Scope: only filings the detector classifies `companyfacts_lacks_accession`.
  * Fallback facts do not enter derived values until a dry-run is reviewed.

This module contains: the comparison, the stratified sampler, the gate, and a
reader protocol. `StoredFilingReader` is a deliberately trivial reader (it replays
the stored facts) used to prove the harness itself; it is not a fallback.
"""

from __future__ import annotations

import csv
import json
import random
from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any, Protocol

REQUIRED_FILINGS = 50

FactKey = tuple[
    str, str, str, date | None, date
]  # taxonomy, tag, unit, start (None=instant), end


@dataclass(frozen=True)
class InstanceFact:
    taxonomy: str
    tag: str
    unit: str
    start: date | None
    end: date
    value: Decimal

    @property
    def key(self) -> FactKey:
        return (self.taxonomy, self.tag, self.unit, self.start, self.end)


@dataclass(frozen=True)
class SampleFiling:
    accession: str
    cik: str
    form: str
    filing_id: int
    period_of_report: date | None
    stratum: str = ""


class InstanceReader(Protocol):
    def read(self, filing: SampleFiling) -> list[InstanceFact]: ...


@dataclass
class FilingResult:
    accession: str
    form: str
    stratum: str
    stored: int
    matched: int
    missing: list[FactKey] = field(default_factory=list)
    mismatched: list[tuple[FactKey, Decimal, Decimal]] = field(default_factory=list)
    extra: int = 0
    duplicate_conflicts: int = 0

    @property
    def recall(self) -> float:
        return 1.0 if self.stored == 0 else self.matched / self.stored

    @property
    def passed(self) -> bool:
        return (
            self.stored > 0
            and not self.missing
            and not self.mismatched
            and not self.duplicate_conflicts
        )


def compare_filing(
    filing: SampleFiling, stored: list[InstanceFact], read: list[InstanceFact]
) -> FilingResult:
    """Every stored fact must be reproduced exactly. Reader duplicates of one key
    with different values are a conflict (the reader must not guess)."""
    by_key: dict[FactKey, set[Decimal]] = {}
    for f in read:
        by_key.setdefault(f.key, set()).add(f.value)
    result = FilingResult(
        filing.accession, filing.form, filing.stratum, stored=0, matched=0
    )
    stored_keys: set[FactKey] = set()
    for f in stored:
        if f.key in stored_keys:
            continue  # companyfacts repeats a fact per filing only once; ignore storage dupes
        stored_keys.add(f.key)
        result.stored += 1
        values = by_key.get(f.key)
        if not values:
            result.missing.append(f.key)
        elif len(values) > 1:
            result.duplicate_conflicts += 1
        elif next(iter(values)) != f.value:
            result.mismatched.append((f.key, f.value, next(iter(values))))
        else:
            result.matched += 1
    result.extra = len(set(by_key) - stored_keys)
    return result


@dataclass
class SelftestReport:
    results: list[FilingResult]
    required: int = REQUIRED_FILINGS

    @property
    def distinct_filings(self) -> int:
        return len({r.accession for r in self.results})

    @property
    def passed(self) -> bool:
        """Gate: at least `required` distinct filings, every one passing at 100%."""
        return self.distinct_filings >= self.required and all(
            r.passed for r in self.results
        )

    def summary(self) -> dict[str, Any]:
        return {
            "required_filings": self.required,
            "filings": len(self.results),
            "distinct_filings": self.distinct_filings,
            "passed_filings": sum(1 for r in self.results if r.passed),
            "failed_filings": [r.accession for r in self.results if not r.passed],
            "stored_facts": sum(r.stored for r in self.results),
            "matched_facts": sum(r.matched for r in self.results),
            "extra_facts_not_written": sum(r.extra for r in self.results),
            "gate_passed": self.passed,
        }


def run_selftest(
    reader: InstanceReader,
    filings: list[SampleFiling],
    load_stored: Any,
    required: int = REQUIRED_FILINGS,
) -> SelftestReport:
    """`load_stored(filing) -> list[InstanceFact]` returns the companyfacts-derived
    facts stored for that filing (core.fact rows of the filing)."""
    results = [compare_filing(f, load_stored(f), reader.read(f)) for f in filings]
    return SelftestReport(results, required)


# ------------------------------------------------------------------ sampling


def stratify(
    candidates: list[SampleFiling], n: int, seed: int = 1
) -> list[SampleFiling]:
    """Deterministic stratified draw of n filings: round-robin across strata
    (form x fiscal-year-end month x size class set by the caller in `stratum`)
    so that 10-K and 10-Q, December and off-calendar year ends, and 52/53-week
    filers are all represented. Same seed, same list."""
    rng = random.Random(seed)
    buckets: dict[str, list[SampleFiling]] = {}
    for c in sorted(candidates, key=lambda x: x.accession):
        buckets.setdefault(c.stratum, []).append(c)
    for items in buckets.values():
        rng.shuffle(items)
    out: list[SampleFiling] = []
    keys = sorted(buckets)
    while len(out) < n and any(buckets.values()):
        for k in keys:
            if buckets[k] and len(out) < n:
                out.append(buckets[k].pop())
    return out


def stratum_label(
    form: str, period_of_report: date | None, weeks_calendar: bool
) -> str:
    month = period_of_report.month if period_of_report else 0
    kind = "annual" if form.startswith("10-K") else "quarterly"
    return f"{kind}|fye_month_{month:02d}|{'52_53_week' if weeks_calendar else 'month_end'}"


def load_candidates(
    conn: Any, limit_per_company: int = 1, since: date = date(2024, 1, 1)
) -> list[SampleFiling]:  # pragma: no cover - database
    """Periodic filings with facts, one per company, from light indexed reads.
    Weeks-calendar flag: the period end is not a month end."""
    out: list[SampleFiling] = []
    with conn.cursor() as cur:
        cur.execute(
            "select id, cik from core.company where status = 'active' order by id"
        )
        companies = cur.fetchall()
    for i in range(0, len(companies), 100):
        part = companies[i : i + 100]
        with conn.cursor() as cur:
            cur.execute(
                """
                select distinct on (f.company_id) f.company_id, f.id, f.accession_number, f.form, f.period_of_report
                from core.filing f
                where f.company_id = any(%s) and f.form in ('10-K','10-Q') and f.filing_date >= %s
                  and exists (select 1 from core.fact x where x.filing_id = f.id)
                order by f.company_id, f.filing_date desc
                """,
                ([c[0] for c in part], since),
            )
            ciks = {c[0]: c[1] for c in part}
            for company_id, filing_id, accn, form, por in cur.fetchall():
                month_end = por is not None and (por + timedelta(days=1)).day == 1
                out.append(
                    SampleFiling(
                        accn,
                        ciks[company_id],
                        form,
                        filing_id,
                        por,
                        stratum_label(form, por, not month_end),
                    )
                )
    return out


def load_stored_facts(
    conn: Any, filing: SampleFiling
) -> list[InstanceFact]:  # pragma: no cover - database
    with conn.cursor() as cur:
        cur.execute(
            """
            select co.taxonomy, co.tag, u.unit_name, p.start_date, p.end_date, p.period_type, x.value
            from core.fact x
            join core.concept co on co.id = x.concept_id
            join core.unit u on u.id = x.unit_id
            join core.period p on p.id = x.period_id
            where x.filing_id = %s
            """,
            (filing.filing_id,),
        )
        return [
            InstanceFact(
                tax,
                tag,
                unit,
                None if ptype == "instant" else start,
                end,
                Decimal(value),
            )
            for tax, tag, unit, start, end, ptype, value in cur.fetchall()
        ]


class StoredFilingReader:
    """Replays the stored facts: proves the harness only. NOT a fallback reader."""

    def __init__(self, conn: Any) -> None:
        self.conn = conn

    def read(
        self, filing: SampleFiling
    ) -> list[InstanceFact]:  # pragma: no cover - database
        return load_stored_facts(self.conn, filing)


def write_report(report: SelftestReport, out_csv: Path, out_json: Path) -> None:
    with out_csv.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(
            [
                "accession",
                "form",
                "stratum",
                "stored",
                "matched",
                "missing",
                "mismatched",
                "extra",
                "duplicate_conflicts",
                "passed",
            ]
        )
        for r in report.results:
            w.writerow(
                [
                    r.accession,
                    r.form,
                    r.stratum,
                    r.stored,
                    r.matched,
                    len(r.missing),
                    len(r.mismatched),
                    r.extra,
                    r.duplicate_conflicts,
                    r.passed,
                ]
            )
    out_json.write_text(json.dumps(report.summary(), indent=2))
