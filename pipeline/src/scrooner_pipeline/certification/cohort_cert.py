"""Cohort certificate (founder 2026-11-28, typed "everything is approve"): one cohort-sampled certificate over the
launch set replaces per-company certification (PIPELINE.md stage 5 Certify, step M3).

The preparer's half only. This module draws, machine-checks, queues reads and files a certificate REQUEST; it never
writes a verdict, a registry row or a certificate. Only the approver records those (PIPELINE.md section 3).

1. Draw: a seeded stratified random sample of SHOWN cells across the cohort's companies. Strata are statement family
   (metrics registry) x sector (the export's sector column) x rank band (RANK_BANDS, the cohort ladder). Allocation is
   display_cert.allocate: one cell per non-empty stratum first, the rest proportional by largest remainder. The pool
   is display_cert.draw_pool per company (every SHOWN_VALUE except total_debt, which is a census of its own).
2. Machine check: each company runs display_cert.certify with the cohort's cells as its sample, so a drawn cell gets
   exactly the per-company judge's checks: the claim check against the cited filing's fsn facts (check_cell /
   check_derived), the automated draw checker (draw_check, its own element families), identity-web corroboration and
   the filing reads; every census check (gate, badges, hide classes, hidden rows and years, total_debt, derived
   cells) runs on every company of the cohort as it does per company.
3. Outcome per drawn cell: FAIL (the claim check or a filing read found the shown value wrong), NEEDS_READ (the machine
   could not settle it and no read has: draw_check NEEDS_READ or AUTO_MISMATCH, an unsettled LOCATOR or NOT_FOUND), or
   PASS. A FAIL in any cell, or any census FAIL, makes the cohort's machine status FAIL; each opens an
   exceptions-queue item by root-cause family (exception_queue.Row; load it with `exception_queue load --extra-csv`).
4. Bound: the exact one-sided Clopper-Pearson 95% upper bound on the error rate (display_cert.clopper_pearson_upper),
   pooled and per stratum. Draw size: the smallest n whose 0-error bound is <= 0.5%:
   n >= ln(0.05) / ln(1 - 0.005) = 597.6, so n = 598 (597 gives 0.5018%).

Key: cohort id + coverage_sha256 + judge version. The cohort id names the company set (name + the first 12 hex of the
sha256 of its sorted company ids), so a new export of the same companies is a new sha under the same cohort id, and a
re-draw happens only on a new coverage sha or a new judge. Money is Decimal end to end.
"""

from __future__ import annotations

import csv
import hashlib
import random
import re
import tempfile
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path

from scrooner_pipeline.certification import display_cert as dc
from scrooner_pipeline.certification import draw_check as dck

COHORT_TARGET_UPPER_95 = 0.005
COHORT_DRAW_SIZE = dc.required_draw_size(COHORT_TARGET_UPPER_95, dc.ALPHA)  # 598
COHORT_JUDGE = "cohort_cert@1"
JUDGE_VERSION = f"{COHORT_JUDGE}+{dck.CHECKER_VERSION}"
# The cohort ladder (founder 2026-11-13; PIPELINE.md section 5): top 100, then 500, 1,000, 2,000, 5,000. The top 100
# splits at 50 so the first cohort already has two bands.
RANK_BANDS = ((1, 50), (51, 100), (101, 500), (501, 1000), (1001, 2000), (2001, 5000))
PASS, FAIL, NEEDS_READ = "PASS", "FAIL", "NEEDS_READ"
STATUS_FAIL, STATUS_READS, STATUS_READY = "FAIL", "NEEDS_READ", "READY_FOR_APPROVER"


def rank_band(rank: int) -> str:
    for lo, hi in RANK_BANDS:
        if lo <= rank <= hi:
            return f"r{lo:04d}-{hi:04d}"
    return f"r{RANK_BANDS[-1][1] + 1:04d}+" if rank > 0 else "r_unranked"


@dataclass
class Company:
    ticker: str
    company_id: str
    rank: int
    cells: list[dc.Cell]
    path: Path  # this company's rows of the cohort export, as certify() reads them


@dataclass(frozen=True)
class Drawn:
    ticker: str
    company_id: str
    rank: int
    stratum: str
    cell: dc.Cell

    @property
    def key(self) -> tuple[str, str, str]:
        return (self.ticker, *self.cell.key)


def cohort_id(name: str, companies: Iterable[Company]) -> str:
    ids = ",".join(sorted(str(c.company_id) for c in companies))
    return f"{name}-{hashlib.sha256(ids.encode()).hexdigest()[:12]}"


def load_cohort(
    coverage: Path, work_dir: Path, company_ids: Iterable[str] | None = None
) -> list[Company]:
    """Split a multi-company export (top100-coverage.csv shape: rank, ticker, company_id + the per-company columns)
    into one file per company under work_dir and read each with display_cert.read_coverage."""
    with open(coverage, newline="") as fh:
        rd = csv.DictReader(fh)
        fields = list(rd.fieldnames or [])
        rows = list(rd)
    for col in ("rank", "ticker", "company_id"):
        if col not in fields:
            raise ValueError(
                f"{coverage}: no {col} column (a cohort export has one row set per company)"
            )
    keep = None if company_ids is None else {str(i) for i in company_ids}
    by: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        if keep is None or r["company_id"] in keep:
            by[r["company_id"]].append(r)
    out = []
    for cid, mine in by.items():
        p = work_dir / f"cohort-{cid}.csv"
        with open(p, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=fields)
            w.writeheader()
            w.writerows(mine)
        ranks = {r["rank"] for r in mine}
        tickers = {r["ticker"] for r in mine}
        if len(ranks) != 1 or len(tickers) != 1:
            raise ValueError(
                f"company {cid}: rows carry ranks {sorted(ranks)} and tickers {sorted(tickers)}"
            )
        out.append(
            Company(tickers.pop(), cid, int(ranks.pop() or 0), dc.read_coverage(p), p)
        )
    return sorted(out, key=lambda c: (c.rank, c.ticker))


# ---------------------------------------------------------------- draw
def stratum(c: dc.Cell, rank: int, statements: dict[str, str]) -> str:
    return f"{statements.get(c.data_point, 'other')}|{c.sector or 'general'}|{rank_band(rank)}"


def pool(
    companies: list[Company], statements: dict[str, str]
) -> dict[str, list[Drawn]]:
    """stratum -> every drawable shown cell of the cohort, in a fixed order (rank, ticker, data point, year)."""
    by: dict[str, list[Drawn]] = defaultdict(list)
    for co in sorted(companies, key=lambda c: (c.rank, c.ticker)):
        for c in dc.draw_pool(co.cells):
            s = stratum(c, co.rank, statements)
            by[s].append(Drawn(co.ticker, co.company_id, co.rank, s, c))
    return dict(by)


def draw_cohort(
    companies: list[Company],
    seed: str,
    n: int = COHORT_DRAW_SIZE,
    statements: dict[str, str] | None = None,
) -> tuple[list[Drawn], dict[str, tuple[int, int]]]:
    """Seeded stratified draw of min(n, pool) shown cells over the cohort. Returns (drawn cells, stratum -> (pool,
    drawn)). The same companies, export and seed always give the same draw."""
    st = dc.registry_statements() if statements is None else statements
    by = pool(companies, st)
    alloc = dc.allocate({k: len(v) for k, v in by.items()}, n)
    rng = random.Random(seed)
    out: list[Drawn] = []
    for k in sorted(by):
        out += rng.sample(by[k], alloc.get(k, 0))
    return out, {k: (len(by[k]), alloc.get(k, 0)) for k in sorted(by)}


# ---------------------------------------------------------------- reads
def load_cohort_reads(path: Path | None) -> dict[str, dict[tuple[str, str], dck.Read]]:
    """Filing reads of the queued cells (CSV: ticker, data_point, fiscal_year, verdict MATCH|MISMATCH, reader,
    evidence) -> ticker -> draw_check reads. A row without a reader or evidence is refused, as per company."""
    if path is None:
        return {}
    out: dict[str, dict[tuple[str, str], dck.Read]] = defaultdict(dict)
    with open(path, newline="") as fh:
        for i, r in enumerate(csv.DictReader(fh), start=2):
            v = (r.get("verdict") or "").strip().upper()
            reader, ev, t = (
                (r.get(k) or "").strip() for k in ("reader", "evidence", "ticker")
            )
            if v not in dck.READ_VERDICTS or not reader or not ev or not t:
                raise ValueError(
                    f"{path}:{i}: a read needs a ticker, verdict MATCH|MISMATCH, a reader and evidence"
                )
            k = (r["data_point"].strip(), str(r["fiscal_year"]).strip())
            out[t][k] = dck.Read(*k, v, reader, ev)
    return dict(out)


# ---------------------------------------------------------------- outcomes
@dataclass(frozen=True)
class CellResult:
    drawn: Drawn
    outcome: str  # PASS | FAIL | NEEDS_READ
    claim: str  # display_cert.check_cell result: MATCH | MISMATCH | NOT_FOUND | LOCATOR | (none)
    auto: str  # draw_check outcome, or "" when the checker did not run
    method: str  # draw_check method, or ""
    filing_value: Decimal | None
    family: str  # root-cause family of a FAIL or the read class of a NEEDS_READ; "" for PASS
    detail: str


@dataclass(frozen=True)
class CensusItem:
    ticker: str
    company_id: str
    check: str
    data_point: str
    fiscal_year: str
    severity: str  # FAIL | REVIEW
    family: str
    detail: str


_NUM = re.compile(r"-?\d[\d,.]*")


def census_family(check: str, detail: str) -> str:
    """One family per kind of census finding: the check and its detail with numbers, accessions and tags blanked."""
    d = _NUM.sub("#", detail.split(" from ")[0])
    d = re.sub(r"\b[A-Z][A-Za-z]{2,}[A-Z][A-Za-z]+\b", "<tag>", d)
    return f"census:{check}:{d.strip()[:80]}"


def cell_results(
    run: dc.Run, drawn: list[Drawn], statements: dict[str, str]
) -> list[CellResult]:
    """Each drawn cell's outcome from the company's Run, with the Run's own rules: errors (a claim MISMATCH or a read
    MISMATCH) are FAIL; pending reads and unsettled LOCATOR / NOT_FOUND claims are NEEDS_READ."""
    claim = {s.cell.key: s for s in run.shown}
    auto = {a.key: a for a in run.auto or ()}
    read_wrong = {(r.data_point, r.fiscal_year) for r in run.read_wrong}
    pending = {a.key for a in run.pending_reads}
    out = []
    for d in drawn:
        k = d.cell.key
        s, a, r = claim.get(k), auto.get(k), run.reads.get(k)
        dp = f"{statements.get(d.cell.data_point, 'other')}.{d.cell.data_point}"
        if s is not None and s.result == "MISMATCH":
            fam = (
                "per_share_implausible"
                if "implausible per-share" in s.evidence
                else "claim_mismatch"
            )
            res = (FAIL, f"{dp}:{fam}", s.evidence)
        elif k in read_wrong and r is not None:
            res = (FAIL, f"{dp}:read_mismatch", f"read by {r.reader}: {r.evidence}")
        elif (
            k in pending
            or (run.auto is None and r is None)
            or (
                s is not None
                and s.result in ("LOCATOR", "NOT_FOUND")
                and not run.settled_by_read(s)
                and r is None
            )
        ):
            why = (
                f"draw_check {a.outcome} ({a.method}): {a.detail}"
                if a is not None and a.outcome != dck.AUTO_MATCH
                else f"claim check {s.result}: {s.evidence}"
                if s is not None and s.result != "MATCH"
                else "draw checker did not run"
            )
            cls = (
                f"{a.outcome.lower()}:{a.method}"
                if a is not None and a.outcome != dck.AUTO_MATCH
                else f"claim_{s.result.lower()}"
                if s is not None
                else "no_checker"
            )
            res = (NEEDS_READ, cls, why)
        else:
            res = (
                PASS,
                "",
                (a.detail if a is not None else "") or (s.evidence if s else ""),
            )
        out.append(
            CellResult(
                d,
                res[0],
                s.result if s is not None else "",
                a.outcome if a is not None else "",
                a.method if a is not None else "",
                a.filing_value if a is not None else (s.filing_value if s else None),
                res[1],
                res[2],
            )
        )
    return out


def census_items(run: dc.Run, company_id: str) -> list[CensusItem]:
    """The company's census findings that block a certificate (FAIL) or need the approver (REVIEW). An OPEN cell is
    already its own exceptions-queue item (kind OPEN), so it is counted but carries family census:gate:OPEN cell."""
    out = []
    for f in run.gate + run.hides:
        if f.severity in ("FAIL", "REVIEW"):
            out.append(
                CensusItem(
                    run.ticker,
                    company_id,
                    f.check,
                    f.data_point,
                    f.fiscal_year,
                    f.severity,
                    census_family(f.check, f.detail),
                    f.detail,
                )
            )
    for d in run.debt:
        if d.result in ("MISMATCH", "REVIEW"):
            sev = "FAIL" if d.result == "MISMATCH" else "REVIEW"
            out.append(
                CensusItem(
                    run.ticker,
                    company_id,
                    "debt",
                    d.cell.data_point,
                    d.cell.fiscal_year,
                    sev,
                    f"census:debt:{d.result.lower()}",
                    d.evidence,
                )
            )
    for s in run.derived:
        if s.result != "MATCH":
            sev = "FAIL" if s.result == "MISMATCH" else "REVIEW"
            out.append(
                CensusItem(
                    run.ticker,
                    company_id,
                    "derived",
                    s.cell.data_point,
                    s.cell.fiscal_year,
                    sev,
                    f"census:derived:{s.cell.data_point}:{s.result.lower()}",
                    s.evidence,
                )
            )
    return out


# ---------------------------------------------------------------- the cohort result
@dataclass
class Cohort:
    cohort_id: str
    coverage: str  # what the request names as the export (repo path or CI artifact)
    coverage_sha256: str
    seed: str
    companies: list[Company]
    strata: dict[str, tuple[int, int]]
    cells: list[CellResult] = field(default_factory=list)
    census: list[CensusItem] = field(default_factory=list)
    judge: str = JUDGE_VERSION
    target_n: int = COHORT_DRAW_SIZE

    @property
    def key(self) -> str:
        return f"{self.cohort_id}|{self.coverage_sha256}|{self.judge}"

    @property
    def n(self) -> int:
        return len(self.cells)

    @property
    def errors(self) -> int:
        return sum(1 for c in self.cells if c.outcome == FAIL)

    @property
    def pending(self) -> list[CellResult]:
        return [c for c in self.cells if c.outcome == NEEDS_READ]

    @property
    def census_fail(self) -> list[CensusItem]:
        return [c for c in self.census if c.severity == "FAIL"]

    @property
    def status(self) -> str:
        """The preparer's machine status, never a verdict: FAIL (a wrong drawn cell or a census FAIL), NEEDS_READ
        (queued cells or census REVIEW left), else READY_FOR_APPROVER."""
        if self.errors or self.census_fail:
            return STATUS_FAIL
        if self.pending or any(c.severity == "REVIEW" for c in self.census):
            return STATUS_READS
        return STATUS_READY

    def upper(self) -> float:
        return dc.clopper_pearson_upper(self.errors, self.n, dc.ALPHA)

    def per_stratum(self) -> list[dict]:
        by: dict[str, list[CellResult]] = defaultdict(list)
        for c in self.cells:
            by[c.drawn.stratum].append(c)
        out = []
        for k, (m, a) in sorted(self.strata.items()):
            cs = by.get(k, [])
            e = sum(1 for c in cs if c.outcome == FAIL)
            st, sector, band = k.split("|")
            out.append(
                {
                    "stratum": k,
                    "statement": st,
                    "sector": sector,
                    "rank_band": band,
                    "pool": m,
                    "drawn": a,
                    "checked": len(cs),
                    "errors": e,
                    "needs_read": sum(1 for c in cs if c.outcome == NEEDS_READ),
                    "upper_95": dc.clopper_pearson_upper(e, len(cs), dc.ALPHA),
                }
            )
        return out


def judge(
    name: str,
    coverage: Path,
    source,
    cik_of,
    seed: str | None = None,
    n: int = COHORT_DRAW_SIZE,
    reads: dict[str, dict[tuple[str, str], dck.Read]] | None = None,
    company_ids: Iterable[str] | None = None,
    coverage_label: str | None = None,
    statements: dict[str, str] | None = None,
    on_company=None,
) -> Cohort:
    """Draw over the cohort, then run the per-company judge (display_cert.certify) on each company with its drawn
    cells. source: a display_cert FactSource; cik_of(company_id) -> CIK. on_company(ticker, run): progress hook."""
    st = dc.registry_statements() if statements is None else statements
    sha = dc.sha256(coverage)
    with tempfile.TemporaryDirectory() as tmp:
        companies = load_cohort(coverage, Path(tmp), company_ids)
        cid = cohort_id(name, companies)
        seed = seed or f"{cid}-{sha[:12]}"
        drawn, strata = draw_cohort(companies, seed, n, st)
        co = Cohort(
            cid,
            coverage_label or str(coverage),
            sha,
            seed,
            companies,
            strata,
            target_n=n,
        )
        mine: dict[str, list[Drawn]] = defaultdict(list)
        for d in drawn:
            mine[d.company_id].append(d)
        for c in companies:
            ds = mine.get(c.company_id, [])
            run = dc.certify(
                c.ticker,
                cik_of(c.company_id),
                c.path,
                source,
                seed,
                reads=(reads or {}).get(c.ticker, {}),
                sample=[d.cell for d in ds],
            )
            co.cells += cell_results(run, ds, st)
            co.census += census_items(run, c.company_id)
            if on_company is not None:
                on_company(c.ticker, run)
    order = {d.key: i for i, d in enumerate(drawn)}
    co.cells.sort(key=lambda r: order[r.drawn.key])
    return co


# ---------------------------------------------------------------- outputs (a request, never a verdict)
CELL_COLUMNS = [
    "ticker",
    "company_id",
    "rank",
    "stratum",
    "data_point",
    "fiscal_year",
    "period_end",
    "badge",
    "shown_value",
    "accession",
    "r_page",
    "tag",
    "outcome",
    "claim_check",
    "draw_check",
    "method",
    "filing_value",
    "family",
    "detail",
]
READ_COLUMNS = ["ticker", "data_point", "fiscal_year", "verdict", "reader", "evidence"]


def cell_rows(co: Cohort) -> list[dict]:
    return [
        {
            "ticker": r.drawn.ticker,
            "company_id": r.drawn.company_id,
            "rank": r.drawn.rank,
            "stratum": r.drawn.stratum,
            "data_point": r.drawn.cell.data_point,
            "fiscal_year": r.drawn.cell.fiscal_year,
            "period_end": r.drawn.cell.period_end,
            "badge": r.drawn.cell.badge or "",
            "shown_value": ""
            if r.drawn.cell.value is None
            else str(r.drawn.cell.value),
            "accession": r.drawn.cell.accession,
            "r_page": r.drawn.cell.r_page,
            "tag": r.drawn.cell.tag,
            "outcome": r.outcome,
            "claim_check": r.claim,
            "draw_check": r.auto,
            "method": r.method,
            "filing_value": "" if r.filing_value is None else str(r.filing_value),
            "family": r.family,
            "detail": r.detail[:500],
        }
        for r in co.cells
    ]


def exception_rows(co: Cohort, source_path: str) -> list:
    """exceptions-queue rows (exception_queue.Row): one SAMPLE_FAIL per root-cause family of the wrong drawn cells, one
    CENSUS_FAIL per census family (OPEN cells excluded: they are OPEN items already), one NEEDS_READ per queued cell.
    Every key carries the cohort key (cohort id + coverage sha + judge)."""
    from scrooner_pipeline.certification.exception_queue import Row

    out = []
    fails: dict[str, list[CellResult]] = defaultdict(list)
    for r in co.cells:
        if r.outcome == FAIL:
            fails[r.family].append(r)
    for fam, rs in sorted(fails.items()):
        out.append(
            Row(
                idempotency_key=f"SAMPLE_FAIL|{co.key}|{fam}",
                kind="SAMPLE_FAIL",
                cell_key=f"{co.key}:{fam}",
                root_cause_family=fam,
                owner_lane="verifier",
                cells_affected=len(rs),
                ticker=rs[0].drawn.ticker
                if len({x.drawn.ticker for x in rs}) == 1
                else None,
                data_point=rs[0].drawn.cell.data_point,
                detail="; ".join(
                    f"{x.drawn.ticker} {x.drawn.cell.data_point} FY{x.drawn.cell.fiscal_year}"
                    for x in rs
                )[:1000],
                source_sha=co.coverage_sha256,
                source_path=source_path,
                evidence_locator=f"cohort draw seed {co.seed}",
                judge_version=co.judge,
            )
        )
    cens: dict[str, list[CensusItem]] = defaultdict(list)
    for c in co.census_fail:
        if c.detail != "OPEN cell":
            cens[c.family].append(c)
    for fam, cs in sorted(cens.items()):
        tickers = sorted({c.ticker for c in cs})
        out.append(
            Row(
                idempotency_key=f"CENSUS_FAIL|{co.key}|{fam}",
                kind="CENSUS_FAIL",
                cell_key=f"{co.key}:{fam}",
                root_cause_family=fam,
                owner_lane="resolver" if ":gate:" in fam else "proof",
                cells_affected=len(cs),
                ticker=tickers[0] if len(tickers) == 1 else None,
                detail=(
                    f"{len(tickers)} companies: "
                    + ", ".join(tickers)
                    + f"; e.g. {cs[0].detail}"
                )[:1000],
                source_sha=co.coverage_sha256,
                source_path=source_path,
                evidence_locator=f"cohort census {co.cohort_id}",
                judge_version=co.judge,
            )
        )
    for r in co.pending:
        c = r.drawn.cell
        out.append(
            Row(
                idempotency_key=f"NEEDS_READ|{co.key}|{r.drawn.ticker}|{c.data_point}|{c.fiscal_year}",
                kind="NEEDS_READ",
                cell_key=f"{c.data_point}|{c.fiscal_year}|{c.period_end}",
                root_cause_family=r.family,
                owner_lane="approver",
                ticker=r.drawn.ticker,
                company_id=int(r.drawn.company_id),
                data_point=c.data_point,
                period_end=c.period_end or None,
                detail=r.detail[:1000],
                source_sha=co.coverage_sha256,
                source_path=source_path,
                evidence_locator=" ".join(x for x in (c.accession, c.r_page) if x)
                or None,
                judge_version=co.judge,
            )
        )
    return out


def write_csv(path: Path, fields: list[str], rows: list[dict]) -> None:
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def write_exceptions(path: Path, rows: list) -> None:
    from scrooner_pipeline.certification.exception_queue import COLUMNS

    write_csv(path, list(COLUMNS), [{k: getattr(r, k) for k in COLUMNS} for r in rows])


def write_read_queue(path: Path, co: Cohort) -> None:
    """The read sheet the verifier or approver fills (verdict, reader, evidence), in load_cohort_reads' format."""
    write_csv(
        path,
        READ_COLUMNS
        + ["outcome_class", "shown_value", "accession", "r_page", "detail"],
        [
            {
                "ticker": r.drawn.ticker,
                "data_point": r.drawn.cell.data_point,
                "fiscal_year": r.drawn.cell.fiscal_year,
                "verdict": "",
                "reader": "",
                "evidence": "",
                "outcome_class": r.family,
                "shown_value": ""
                if r.drawn.cell.value is None
                else str(r.drawn.cell.value),
                "accession": r.drawn.cell.accession,
                "r_page": r.drawn.cell.r_page,
                "detail": r.detail[:500],
            }
            for r in sorted(
                co.pending,
                key=lambda x: (not x.family.startswith("auto_mismatch"), x.drawn.key),
            )
        ],
    )


REQ_TITLE = re.compile(
    r"^# Cohort certification request: (?P<id>[A-Za-z0-9_.\-]+), (?P<d>\d{4}-\d{2}-\d{2})",
    re.M,
)


def render_request(
    co: Cohort, today: str, code_sha: str, files: dict[str, str], preparer: str
) -> str:
    """The certificate request the approver reads (read_request parses it). States the machine status; never a
    verdict."""
    fam: dict[str, int] = defaultdict(int)
    for ci in co.census:
        fam[f"{ci.severity} {ci.family}"] += 1
    outcome = {
        k: sum(1 for c in co.cells if c.outcome == k) for k in (PASS, FAIL, NEEDS_READ)
    }
    auto = {k: sum(1 for c in co.cells if c.auto == k) for k in dck.OUTCOMES}
    pool_n = sum(m for m, _ in co.strata.values())
    reads_by: dict[str, int] = defaultdict(int)
    for c in co.pending:
        reads_by[c.family] += 1
    lines = [
        f"# Cohort certification request: {co.cohort_id}, {today}",
        "",
        'Stage 5 Certify, M3. Founder 2026-11-28 ("everything is approve"): one cohort-sampled certificate over the '
        "launch set replaces per-company certification. The preparer filed this request read-only; only the approver "
        "records the verdict, the registry row and the certificate (PIPELINE.md section 3). Nothing below is a verdict.",
        "",
        f"- cohort id: `{co.cohort_id}`",
        f"- companies: `{len(co.companies)}`",
        f"- coverage csv: `{co.coverage}`",
        f"- sha256: `{co.coverage_sha256}`",
        f"- judge: `{co.judge}`",
        f"- key: `{co.key}`",
        f"- seed: `{co.seed}`",
        f"- draw size rule: `n = ceil(ln({dc.ALPHA}) / ln(1 - {COHORT_TARGET_UPPER_95})) = {COHORT_DRAW_SIZE}`",
        f"- n drawn: `{co.n}`",
        f"- code: `{code_sha}`",
        f"- preparer: `{preparer}`",
        *[f"- {k}: `{v}`" for k, v in files.items()],
        f"- machine status: `{co.status}`",
        "",
        "## Draw",
        "",
        f"Pool: {pool_n} shown cells (total_debt excluded: census) over {len(co.companies)} companies, "
        f"{len(co.strata)} strata (statement family x sector x rank band). Drawn {co.n} of target {co.target_n}; "
        "every non-empty stratum gets one cell first, the rest proportional.",
        "",
        "| stratum | pool | drawn | errors | needs read | upper 95% |",
        "|---|---:|---:|---:|---:|---:|",
        *[
            f"| {s['stratum']} | {s['pool']} | {s['drawn']} | {s['errors']} | {s['needs_read']} | {s['upper_95']:.4%} |"
            for s in co.per_stratum()
        ],
        "",
        "## Machine check",
        "",
        f"- draw checker: AUTO_MATCH {auto[dck.AUTO_MATCH]}, AUTO_MISMATCH {auto[dck.AUTO_MISMATCH]}, "
        f"NEEDS_READ {auto[dck.NEEDS_READ]}",
        f"- cell outcome: PASS {outcome[PASS]}, FAIL {outcome[FAIL]}, NEEDS_READ {outcome[NEEDS_READ]}",
        f"- pooled: {co.errors}/{co.n} wrong; exact Clopper-Pearson 95% upper bound {co.upper():.4%} "
        f"(target {COHORT_TARGET_UPPER_95:.2%}). With {len(co.pending)} cells unread this bound holds only if every "
        f"queued read is a MATCH; each queued read that is a MISMATCH adds one error.",
        "",
        "## Read queue (by class)",
        "",
        *(
            [f"- {k}: {v}" for k, v in sorted(reads_by.items(), key=lambda kv: -kv[1])]
            or ["- none"]
        ),
        "",
        "## Census (every company of the cohort; counts by family)",
        "",
        *(
            [
                f"- {k}: {v}"
                for k, v in sorted(fam.items(), key=lambda kv: (-kv[1], kv[0]))[:60]
            ]
            or ["- none"]
        ),
        "",
    ]
    return "\n".join(lines)


@dataclass(frozen=True)
class CohortRequest:
    cohort_id: str
    date: str
    coverage: str
    sha256: str
    judge: str
    key: str
    seed: str
    n: int


def read_request(path: Path) -> CohortRequest:
    text = Path(path).read_text()
    m = REQ_TITLE.search(text)

    def line(name: str) -> str | None:
        hit = re.search(rf"^- {name}: `([^`]+)`", text, re.M)
        return hit[1] if hit else None

    names = ("coverage csv", "sha256", "judge", "key", "seed", "n drawn")
    found = {k: line(k) for k in names}
    if not m or any(v is None for v in found.values()):
        raise ValueError(
            f"{path}: not a cohort certification request (title, coverage, sha256, judge, key, seed, n)"
        )
    got = {k: str(v) for k, v in found.items()}
    req = CohortRequest(
        m["id"],
        m["d"],
        got["coverage csv"],
        got["sha256"],
        got["judge"],
        got["key"],
        got["seed"],
        int(got["n drawn"]),
    )
    if req.key != f"{req.cohort_id}|{req.sha256}|{req.judge}":
        raise ValueError(f"{path}: key {req.key} is not cohort id + sha256 + judge")
    return req
