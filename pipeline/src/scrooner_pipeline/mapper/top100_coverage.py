"""Top-100 coverage report: the work queue for every session (read-only on the database).

One row per (company, template data point, fiscal year FY2015..latest FY) for ranks 1-100 of
doc/data-moat/team/top1000/shards.csv. Each cell is exactly one class:

  PROVEN     served value and the latest analytics.cell_proof verdict (basis='latest') is PROVEN for that value
  REASON     no served value and an evidenced reason is stored (cell_proof NOT_PRESENTED, cell_blank_reason
             not_presented / not_in_template / evidenced_zero / undefined_by_math / history_horizon,
             or an analytics.company_tag_map not_presented / not_in_template decision covering the period)
  HELD       no served value, withheld on purpose: a defect row that is a held_/hold_ code or whose defect_class is
             guard_hidden / finding_open / filer_error (guard-held wrong value, scale error, open finding). Not a reason
             (nothing proves the line is absent), not BLANK (the work queue knows why it is empty); it is not counted in
             pct_proven_plus_reason
  DISAGREE   latest cell_proof verdict is DISAGREE
  UNCHECKED  a value is served but no PROVEN verdict covers it (no proof row, verdict UNCHECKED, or the proof was for
             another value)
  BLANK      nothing served and no evidenced reason (reason_code carries the stored defect code or the docmap status
             that is not loaded yet, for the work queue)

Template: the per-company data-point list is the FILING-CHECKED docmap (data-team/companies/reads/<T>-docmap-*.csv, latest
file); rows with status OUT are not cells. analytics.company_data_point_template (0120) is empty live and the sector
templates file is an unsigned proposal, so it cannot define cells yet. A company with no docmap has no template: it is
listed in the summary as TEMPLATE_UNAVAILABLE with zero cells, never guessed.
"""

from __future__ import annotations

import csv
import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any

from scrooner_pipeline.certification.display_cert import (
    HIDE_FAMILY,
    PERIODIC_FORMS as CERT_PERIODIC_FORMS,
)
from scrooner_pipeline.common import instance_facts
from scrooner_pipeline.common.company_filings import (
    company_filings,
    core_filings_cte,
    fsn_filings_cte,
)
from scrooner_pipeline.common.fsn_dates import fsn_end_matches
from scrooner_pipeline.mapper import comparative_guard as cg
from scrooner_pipeline.mapper import structural_loader as sl
from scrooner_pipeline.mapper.note_report_lookup import load_lookup
from scrooner_pipeline.proof.prove import DETECTOR_VERSION
from scrooner_pipeline.proof.rules import row_is_current

CLASSES = ("PROVEN", "REASON", "DERIVED", "HELD", "DISAGREE", "UNCHECKED", "BLANK")
REASON_STATES = {
    "not_presented",
    "not_in_template",
    "evidenced_zero",
    "undefined_by_math",
    "history_horizon",
}
HELD_RE = re.compile(r"^(held|hold)_")
# A defect of these classes means a value (or a candidate) exists and a guard or an open finding withholds it:
# the cell is held, not blank and not a verified reason.
HELD_DEFECT_CLASSES = {"guard_hidden", "finding_open", "filer_error"}
# Point-in-time (balance sheet / cover) data points: the FY cell is the instant at fiscal year end.
INSTANT_DPS = {
    "cash_and_equivalents",
    "accounts_receivable",
    "inventory",
    "current_assets",
    "ppe_net",
    "goodwill",
    "total_assets",
    "accounts_payable",
    "current_liabilities",
    "total_liabilities",
    "stockholders_equity",
    "shares_outstanding",
    "total_debt",
    "deposits",
    "loans_net",
}
# canonical_fact.family of a served value the filing does not print (mapper/derived_cells.py): the cell is DERIVED
# only while every input cell is PROVEN at the current detector version and all inputs cite the same filing.
DERIVED_FAMILY = "company_tag_map:derived_not_printed"
DERIVED_CODE = "derived_not_printed"
DERIVED_UNPROVEN = "derived_inputs_unproven"
DERIVED_INPUTS = {
    "gross_profit": ("revenue", "cost_of_revenue"),
    "total_liabilities": ("total_assets", "stockholders_equity"),
}
FIRST_FY = 2015
UNMAPPED = "era_unmapped"
COMBINED = "line_presented_combined"
# reason_class values of a tagless not_in_template row that records a printed combined line
COMBINED_CLASSES = {
    COMBINED,
    "docmap_combined",
    "docmap_fix_combined",
    "line_presented_combined_with_others",
}
# docmap data point -> concept names looked up in order (resolved concept first: it is what is served).
SPECIAL_CANDIDATES = {"revenue": ["revenue_sanity_resolved", "revenue"]}

CSV_COLUMNS = [
    "rank",
    "ticker",
    "company_id",
    "data_point",
    "fiscal_year",
    "period_end",
    "class",
    "reason_code",
    "reason",
    "shown_value",
    "proof_verdict",
    "verdict",
    "accession",
    "r_page",
    "locator_source",
    "evidence",
    "tag",
    "value_source",
    "docmap_status",
    "parts",
    "display",
    "hide_class",
    "stated_zero",
    "text_stated",
]


# Display layer (founder 2026-11-16, doc 02): coverage = a real proven value in EVERY shown cell. A reason is no longer
# a covered shown cell: a row the company never reports is hidden, years before its first filing are hidden, and
# every other non-value cell is open work. Method: data-team/strategy/approvals/CERTIFICATION-METHOD-2026-11-16.md.
SHOWN_VALUE, HIDDEN_ROW, HIDDEN_YEAR, OPEN = (
    "SHOWN_VALUE",
    "HIDDEN_ROW",
    "HIDDEN_YEAR",
    "OPEN",
)
# THE SWITCH. Ruling (Dhairya, 2026-11-16): a year counts as presented only when a PERIODIC report (10-K, 10-Q, 20-F,
# 40-F, comparative columns included) presents it. A year that appears only in a Form 10, S-1 or F-1 is a pre-filing
# year and is HIDDEN_YEAR (GEV FY2022 balance-sheet cells). Default False. True would let a registration statement
# present a year; the pre-filing rule then cannot be proven from periodic filings and is switched off (only an
# evidenced no-period reason hides a year).
REGISTRATION_STATEMENT_PRESENTS_YEAR = False
# reason codes that evidence "the company does not present this line" (a row is hidden only when EVERY year is one)
NOT_PRESENTED_CODES = {
    "structural_not_presented",
    "docmap_not_presented",
    "company_tag_map:not_presented",
    "docmap_fix_not_presented",
}
# evidenced no filing presents the period (no_10k_presents_period is written by structural_loader / structural_direct;
# the guard that refuses the reason when a later 10-K presents the period lives there; here it is re-checked, never
# duplicated: a year that a periodic report presents is never hidden)
# the proof's own verdict for a year before the filing history (NOT_PRESENTED pre_filing_period, detector v21)
PRE_FILING_CODE = "pre_filing_period"
NO_PERIOD_CODES = {
    "no_public_filing_for_period",
    "no_10k_presents_period",
    PRE_FILING_CODE,  # no balance sheet of the shown filing presents the date (CRWD cash 2018-01-31)
}
WORK_TYPES = ("combined_split", "gap_fill", "proof", "blank", "held")


def candidates(dp: str) -> list[str]:
    return SPECIAL_CANDIDATES.get(dp, [f"{dp}_resolved", dp])


STATEMENT_STMTS = ("IS", "BS", "CF", "CI", "EQ")
# report titles that name a main statement (fsn.report.shortname), used only when fsn.line holds none of it
TITLE_PATTERNS = {
    "BS": re.compile(r"balance sheet|financial position|financial condition", re.I),
    "IS": re.compile(
        r"statements? of (consolidated )?(operations|income|earnings)|income statements?|results of operations",
        re.I,
    ),
}


@dataclass
class LocatorIndex:
    """The printed layout of the filings a cell may cite, from fsn.line (one accession = one filing).
    Every lookup is keyed by the accession, so a page can never come from another filing than the accession beside it."""

    pos: dict[tuple[str, int, int], tuple[str, str, str]] = field(
        default_factory=dict
    )  # (acc, report, line) -> (stmt, tag, plabel)
    line: dict[tuple[str, str, int], int] = field(
        default_factory=dict
    )  # (acc, stmt, line) -> report
    tag: dict[tuple[str, str], list[tuple[str, int]]] = field(
        default_factory=lambda: defaultdict(list)
    )  # (acc, tag) -> [(stmt, report)]
    plabel: dict[tuple[str, str], int] = field(
        default_factory=dict
    )  # (acc, plabel) -> report
    stmt_n: dict[tuple[str, str, int], int] = field(
        default_factory=lambda: defaultdict(int)
    )  # (acc, stmt, report) -> lines
    titles: dict[tuple[str, int], str] = field(
        default_factory=dict
    )  # (acc, report) -> the report's short name (fsn.report)

    def add(
        self, acc: str, report: int, line: int, stmt: str, tag: str, plabel: str | None
    ) -> None:
        self.pos[(acc, report, line)] = (stmt, tag, plabel or "")
        self.line.setdefault((acc, stmt, line), report)
        self.tag[(acc, tag)].append((stmt, report))
        if plabel:
            self.plabel.setdefault((acc, plabel), report)
        if stmt in STATEMENT_STMTS:
            self.stmt_n[(acc, stmt, report)] += 1

    def stmt_report(self, acc: str, stmt: str) -> int | None:
        """The report that carries most of the statement's lines in THIS filing (a parenthetical has few). A filing
        whose FSN load stored no lines for the statement (SHOP's 40-F balance sheet) falls back to the filing's own
        report list (fsn.report): the lowest report whose title names the statement."""
        best = [
            (n, -r) for (a, s, r), n in self.stmt_n.items() if a == acc and s == stmt
        ]
        if best:
            return -max(best)[1]
        pat = TITLE_PATTERNS.get(stmt)
        named = sorted(
            r
            for (a, r), title in self.titles.items()
            if a == acc
            and pat
            and pat.search(title)
            and "parenthetical" not in title.lower()
        )
        return named[0] if named else None


OWN_UNVERIFIED = "reason_own_filing_unverified"
# A 10-K ending at P prints the balance sheet for P and P-1 and the income and cash-flow statements for P, P-1, P-2.
_DAY_TOL = 12


def eligible_filings(
    filings: list[tuple[date, str]], period_end: date, instant: bool
) -> set[str]:
    """Accessions of the company's annual filings that present the fiscal year ending `period_end`: its own 10-K
    (period == year end) or a later one whose face columns still carry the year (one more year for a balance-sheet
    instant, two more for a duration). Pure."""
    span = (366 if instant else 2 * 366) + _DAY_TOL
    # fsn.filing.period is the SEC's month-end rounding: a 52/53-week year end (NVDA 2026-01-25, AAPL 2026-09-26) sits
    # up to ~16 days from it, so "own period" is fsn_end_matches, not a plain day window
    return {
        acc
        for p, acc in filings
        if fsn_end_matches(p, period_end, _DAY_TOL) or 0 < (p - period_end).days <= span
    }


NO_FILING = (
    "no_public_filing_for_period"  # = structural_loader.NO_FILING_REASON (tested)
)
NO_FILING_CODES = cg.NO_FILING_CODES  # both codes claim no filing presents the period
COMPARATIVE_PRESENTED = "reason_refused_comparative_presented"
# = structural_loader.PERIODIC_FORMS (tested): forms that prove the company was filing periodic reports
PERIODIC_FORMS = (
    "10-K",
    "10-K/A",
    "10-KT",
    "10-KT/A",
    "10-Q",
    "10-Q/A",
    "10-QT",
    "10-QT/A",
    "20-F",
    "20-F/A",
    "40-F",
    "40-F/A",
)


def own_period_reason(
    cls: str,
    code: str | None,
    acc: str,
    filings: list[tuple[date, str]],
    period_end: date,
    instant: bool,
    earliest_filing: date | None = None,
    columns: list[cg.Column] | None = None,
    stmts: tuple[str, ...] | None = None,
) -> tuple[str, str | None]:
    """A REASON stays REASON only when its locator accession presents the cell's own period; else UNCHECKED.
    no_public_filing_for_period has no filing of its own period by definition: it stays REASON only when the company's
    earliest 10-K/10-Q/20-F in core.filing (`earliest_filing`) was filed after the period end; otherwise UNCHECKED."""
    if cls == "REASON" and code in NO_FILING_CODES:
        # comparative guard: a filing that prints a column for the period refutes "no filing presents it"; the cell is
        # open for the resolver to fill from that column, never a reason
        if cg.presenting(columns or (), period_end, instant, stmts):
            return "UNCHECKED", COMPARATIVE_PRESENTED
        if earliest_filing is not None and earliest_filing > period_end:
            return cls, code
        return "UNCHECKED", OWN_UNVERIFIED
    if cls == "REASON" and acc not in eligible_filings(filings, period_end, instant):
        return "UNCHECKED", OWN_UNVERIFIED
    return cls, code


# annual reports: 10-K, 20-F and 40-F families all count as periodic filings (resolver .34, Dhairya 2026-11-16)
ANNUAL_FORMS = (
    "10-K",
    "10-K/A",
    "10-KT",
    "10-KT/A",
    "20-F",
    "20-F/A",
    "40-F",
    "40-F/A",
)


def year_presence(
    filings: list[tuple[date, str]],
    earliest_filing: date | None,
    period_end: date,
    instant: bool,
) -> dict[str, Any]:
    """How the company's annual reports (10-K / 20-F / 40-F) present the year ending `period_end`. Pure.
    presented: some annual report's face columns carry it (a later comparative column counts).
    before_first: it ends before the company's first periodic filing and no annual report presents it.
    comparative_only: the FIRST annual report presents it only as a comparative column (the year ends before that
    report's own fiscal year); first_presenting is the earliest accession that carries it (the evidence column is
    the period end). From the first report's own fiscal year onward this is false: every shown cell must hold a value."""
    ok = eligible_filings(filings, period_end, instant)
    presenting = sorted((p, a) for p, a in filings if a in ok)
    first_period = min((p for p, _ in filings), default=None)
    return {
        "presented": bool(presenting),
        "before_first": bool(
            earliest_filing is not None
            and period_end < earliest_filing
            and not presenting
        ),
        "comparative_only": bool(
            presenting
            and first_period is not None
            and not fsn_end_matches(first_period, period_end, _DAY_TOL)
            and first_period > period_end
            and presenting[0][1] == min(filings)[1]
        ),
        "first_presenting": presenting[0][1] if presenting else "",
    }


def _annual_filings(conn: Any, ids: list[int]) -> dict[int, list[tuple[date, str]]]:
    out: dict[int, list[tuple[date, str]]] = defaultdict(list)
    for cid, period, acc in conn.execute(
        "with "
        + fsn_filings_cte("co.id = any(%s)")
        + """ select company_id, period, accession from company_filings
           where period is not null and form = any(%s)""",
        (ids, list(ANNUAL_FORMS)),
    ).fetchall():
        out[cid].append((period, acc))
    return out


def _earliest_filings(conn: Any, ids: list[int]) -> dict[int, date]:
    """company id -> filing date of its earliest periodic filing (10-K/10-Q/20-F/40-F and amendments) in core.filing."""
    return {
        cid: d
        for cid, d in conn.execute(
            "with "
            + core_filings_cte("co.id = any(%s)")
            + " select company_id, min(filed) from company_core_filings"
            " where form = any(%s) group by company_id",
            (ids, list(PERIODIC_FORMS)),
        ).fetchall()
        if d is not None
    }


def _page(report: int | None) -> str:
    return "" if report is None else f"R{report}.htm"


def proven_locator(
    acc: str | None,
    stmt: str | None,
    line: int | None,
    tags: str | None,
    idx: LocatorIndex,
    note_lookup: dict[tuple[str, str], int] | None = None,
) -> tuple[str, str, str]:
    """(accession, r_page, source) for a cell with a proof: the proof's accession and a report of THAT filing only.
    Order: the proof's own (stmt, line) position; the statement line carrying the shown tag(s) (note line for a note
    claim); the filing's main report of the claimed statement. No page found: the accession alone, page blank."""
    if not acc:
        return "", "", "none"
    if stmt and line is not None and (acc, stmt, line) in idx.line:
        return acc, _page(idx.line[(acc, stmt, line)]), "proof_line"
    votes: dict[int, int] = defaultdict(int)
    for t in (x.strip() for x in (tags or "").split(",") if x.strip()):
        hits = idx.tag.get((acc, t), [])
        same = [r for s_, r in hits if s_ == stmt] or [r for _s, r in hits]
        if same:
            votes[min(same)] += 1
    if votes:
        return acc, _page(min(votes, key=lambda r: (-votes[r], r))), "proof_tag"
    if stmt in STATEMENT_STMTS and not (tags or "").strip():
        # no tag to place: the statement's main report. A tag on no line of this filing (a note-only fact) is
        # NEVER placed on the statement page: the page stays blank.
        rep = idx.stmt_report(acc, stmt)
        if rep is not None:
            return acc, _page(rep), "proof_stmt"
    # a note-only fact: the report of the SAME filing's SEC pre.tsv (cached lookup, note_report_lookup.py)
    reps = [
        note_lookup[(acc, t)]
        for t in (x.strip() for x in (tags or "").split(",") if x.strip())
        if note_lookup and (acc, t) in note_lookup
    ]
    if reps:
        return acc, _page(min(reps)), "note_report_from_pre"
    return acc, "", "note_fact_report_not_stored"


def _num(v: Any) -> str:
    d = Decimal(str(v))
    return format(d.quantize(Decimal(1)) if d == d.to_integral_value() else d, "f")


def load_fix_pages(
    reads_dir: Path, lines_dir: Path | None = None
) -> dict[tuple[str, str, str, str], dict[str, int]]:
    """(ticker, data_point, period_end, accession) -> {tag: R page} from the per-part evidence of the fix rows
    (reads/fixes/*.csv, node text 'Tag=value [BS R4:20 ...]') and of the structural total_debt CSV
    (tags/line_map/total_debt-*.csv). A NOTE node carries no page, so it is never in the result. Keyed by accession:
    a page is used only for the same filing."""
    out: dict[tuple[str, str, str, str], dict[str, int]] = {}
    node = re.compile(r"(?:^|;\s*)([A-Za-z0-9]+)=[-0-9.]+ \[(?:IS|BS|CF|CI|EQ) R(\d+):")

    def take(t: str, dp: str, pe: str, acc: str, nodes: str) -> None:
        for m in node.finditer(nodes or ""):
            out.setdefault((t, dp, pe, acc), {})[m.group(1)] = int(m.group(2))

    for f in sorted((reads_dir / "fixes").glob("*-fixes-*.csv")):
        t = f.name.split("-fixes-")[0]
        with f.open(newline="") as fh:
            for r in csv.DictReader(fh):
                tags = (r.get("tags") or "").split("+")
                pages = (r.get("r_page") or "").split("+")
                if len(tags) == len(pages):
                    for tg, pg in zip(tags, pages):
                        m = re.fullmatch(r"R(\d+)\.htm", pg.strip())
                        if m:
                            out.setdefault(
                                (
                                    t,
                                    r.get("data_point", ""),
                                    r.get("period_end", ""),
                                    r.get("accession", ""),
                                ),
                                {},
                            )[tg.split(":")[-1].strip()] = int(m.group(1))
    ld = lines_dir or reads_dir.parent.parent / "tags" / "line_map"
    for f in sorted(ld.glob("total_debt-*.csv")):
        with f.open(newline="") as fh:
            for r in csv.DictReader(fh):
                take(
                    r.get("ticker", ""),
                    "total_debt",
                    r.get("period_end", ""),
                    r.get("accession", ""),
                    r.get("nodes", ""),
                )
    return out


def instance_pages(path: Path | None = None) -> dict[tuple[str, str], str]:
    """(accession, 'Tag[Axis=Member]') -> 'R<n>.htm' from the r_page column of the committed instance-facts file
    (read here, not in common/instance_facts.py, which is a hashed proof source). A conflicting page drops the key."""
    out: dict[tuple[str, str], str] = {}
    bad: set[tuple[str, str]] = set()
    p = path or instance_facts.FACTS_PATH
    if not p.exists():
        return out
    with p.open(newline="") as fh:
        for r in csv.DictReader(fh):
            member = (r.get("balance_sheet_location_member") or "").strip()
            page = (r.get("r_page") or "").strip()
            if not member or not page:
                continue
            name = member.rpartition(":")[2]
            if name.endswith("Member") and name != "Member":
                name = name[: -len("Member")]
            k = (
                r["adsh"].strip(),
                instance_facts.part_tag(
                    r["tag"].strip(), f"{instance_facts.LOCATION_AXIS}={name};"
                ),
            )
            if k in out and out[k] != page:
                bad.add(k)
            out[k] = page
    for k in bad:
        del out[k]
    return out


def instance_part_page(
    acc: str, tag: str, pages: dict[tuple[str, str], str] | None = None
) -> str:
    """'R<n>.htm' of an instance-sourced part `Tag[Axis=Member]` in filing `acc`, from the instance-facts file's
    r_page. Unknown: ''. Never another filing's page."""
    return (pages if pages is not None else instance_pages()).get((acc, tag), "")


def statement_page_fallback(
    acc: str, stmt: str, instant: bool, idx: LocatorIndex
) -> tuple[str, str]:
    """(R page, source) of the cell's statement in filing `acc` ONLY: the docmap statement if it is a main
    statement, else (a parenthetical or off-face share count of an instant data point) the balance sheet. A cell with
    no statement (a not_presented reason: the line is absent) cites the statement where its absence is shown: the
    balance sheet for an instant data point, the income statement otherwise (Dhairya, 2026-11-14)."""
    # a note stmt (NOTE, UN: the data point lives in a note, so this filing's faces do not print it) is "no
    # statement" here: the live PM amortization FY2022 REASON has stmt NOTE and cited no page (2026-11-14)
    stmt = "" if stmt in ("NOTE", "UN") else stmt
    # a main statement the filing does not carry as its own report (META dividends per share: no EQ report) falls
    # back the same way: the income statement shows the absence of a duration line
    fallback = ["BS"] if instant else ["IS"]
    for st in [stmt] + fallback:
        rep = idx.stmt_report(acc, st) if st else None
        if rep is not None:
            return _page(rep), "evidence_acc_stmt_page"
    return "", ""


def parts_locator(
    checks: Any,
    acc: str | None,
    idx: LocatorIndex,
    note_lookup: dict[tuple[str, str], int] | None,
    fix_pages: dict[str, int] | None,
    inst_pages: dict[tuple[str, str], str] | None = None,
) -> tuple[str, int]:
    """(parts text, parts whose page is unknown) of a component-sum cell: ';'-joined tag=value@acc#R<page>, one per
    part of the proof's checks.component_parts. The accession is the proof's shown accession and every page is of
    THAT filing: a face part from fsn.line, a note part (checks.note_facts) from the same filing's pre.tsv lookup,
    then the fix rows' per-part page of that same accession. Unknown page: blank after '#'."""
    if not acc or not isinstance(checks, dict):
        return "", 0
    cp = checks.get("component_parts") or {}
    found = cp.get("found") or []
    if not found or (checks.get("claim") or {}).get("kind") != "component":
        return "", 0
    stmt = (checks.get("claim") or {}).get("stmt")
    notes = set(cp.get("note_facts") or [])
    out, blank = [], 0
    for p in found:
        tag = p.get("tag") or ""
        rep: int | None = None
        if tag in notes:
            rep = (note_lookup or {}).get((acc, tag))
        else:
            hits = idx.tag.get((acc, tag), [])
            same = [r for s_, r in hits if s_ == stmt] or [
                r for s_, r in hits if s_ in STATEMENT_STMTS
            ]
            rep = min(same) if same else None
            if rep is None:
                rep = (note_lookup or {}).get((acc, tag))
        if rep is None and fix_pages:
            rep = fix_pages.get(tag)
        page = "" if rep is None else f"R{rep}"
        if rep is None and instance_facts.is_instance_part(tag):
            # an instance-sourced part (Tag[Axis=Member]): the page of the committed instance-facts file, for THIS filing
            page = instance_part_page(acc, tag, inst_pages).replace(".htm", "")
        if not page and "[" in tag:
            # a member part (Tag[Axis=Member]: shares by class on the balance-sheet parenthetical, cost of revenue by
            # product on the income statement, a related-party line): its member row is printed on the report that
            # prints the BASE tag in THIS filing (statement line first, then the note lookup)
            base = tag.split("[", 1)[0]
            hits = idx.tag.get((acc, base), [])
            same = [r for s_, r in hits if s_ == stmt] or [
                r for s_, r in hits if s_ in STATEMENT_STMTS
            ]
            brep = min(same) if same else (note_lookup or {}).get((acc, base))
            if brep is not None:
                page = f"R{brep}"
        if not page:
            blank += 1
        sign = "-" if p.get("sign") == -1 else ""
        out.append(f"{sign}{tag}={_num(p.get('value'))}@{acc}#{page}")
    return ";".join(out), blank


def reason_locator(
    evidence: list[tuple], stmt: str | None, idx: LocatorIndex
) -> tuple[str, str, str, str]:
    """(accession, r_page, source, printed label) from the covering map rows' evidence
    (adsh, report, line, plabel, row stmt). The adsh and the report are of one row, so one filing."""
    for adsh, rep, ln, label, rstmt in evidence:
        if not adsh:
            continue
        if rep is None and ln is not None and rstmt and (adsh, rstmt, ln) in idx.line:
            rep = idx.line[(adsh, rstmt, ln)]
        if not label and rep is not None and ln is not None:
            label = idx.pos.get((adsh, rep, ln), ("", "", ""))[2]
        if rep is None and label and (adsh, label) in idx.plabel:
            rep = idx.plabel[(adsh, label)]
        if rep is not None:
            return adsh, _page(rep), "evidence_report", label or ""
        srep = idx.stmt_report(adsh, stmt or rstmt or "")
        if srep is not None:
            return adsh, _page(srep), "evidence_stmt", label or ""
        return adsh, "", "evidence_acc_no_page", label or ""
    return "", "", "none", ""


def reason_fields(cls: str, code: str | None, text: str | None) -> tuple[str, str]:
    """(reason_code, reason_text): only a non-PROVEN cell carries them (a stale text on a value contradicts it)."""
    if cls == "PROVEN":
        return "", ""
    return code or "", text or ""


def combined_reason_text(text: str | None, label: str) -> str:
    """The stored combined reason quotes the printed label; an empty quote is replaced by the evidence's label."""
    text = text or ""
    if "combined line ''" in text:
        text = text.replace(
            "combined line ''",
            f"combined line '{label}'"
            if label
            else "combined line (printed label not recorded)",
        )
    return text


def cls_is_value(svalue: Any, verdict: str | None) -> bool:
    """Parts are listed for a cell that serves a value with a proof row."""
    return svalue is not None and verdict is not None


def classify(
    proof_verdict: str | None,
    proof_reason: str | None,
    proof_value: Decimal | None,
    served_value: Decimal | None,
    blank_state: str | None,
    blank_reason: str | None,
    tagmap_decision: str | None,
    docmap_status: str | None,
    blank_defect_class: str | None = None,
    tagmap_reason_class: str | None = None,
    in_template: bool | None = None,
    combined_evidence: bool = False,
) -> tuple[str, str | None]:
    """(class, reason_code). Pure. Precedence: proof verdict, served-but-unproven value, stored reason, blank."""
    if proof_verdict == "PROVEN":
        if served_value is None:
            return "BLANK", "proof_proven_but_no_served_value"
        if proof_value is None or served_value != proof_value:
            return "UNCHECKED", "proof_is_for_another_value"
        return "PROVEN", None
    if proof_verdict == "DISAGREE":
        return "DISAGREE", proof_reason
    if proof_verdict == "UNCHECKED":
        return "UNCHECKED", proof_reason or "proof_unchecked"
    if served_value is not None:
        return "UNCHECKED", "no_proof_row"
    if proof_verdict == "NOT_PRESENTED":
        return "REASON", proof_reason or "not_presented"
    # a combined line with filing evidence (accession, printed line, R page) is the reason: the filing prints one line
    # that spans this data point and others. Without evidence a not_in_template on an in-template point is a contradiction.
    if combined_evidence:
        return "REASON", COMBINED
    # era_unmapped: the era guard found no filing-checked mapping for that year. A gap in the map, not a reason.
    if blank_reason == UNMAPPED or (
        tagmap_decision and tagmap_reason_class == UNMAPPED and not blank_state
    ):
        return "BLANK", UNMAPPED
    # not_in_template on a data point the company's current template includes is a contradiction, never a reason
    if in_template and (
        blank_state == "not_in_template" or tagmap_decision == "not_in_template"
    ):
        return "BLANK", "not_in_template_but_in_template"
    if blank_state in REASON_STATES:
        return "REASON", blank_reason or blank_state
    if blank_state == "defect" and (
        (blank_reason and HELD_RE.match(blank_reason))
        or blank_defect_class in HELD_DEFECT_CLASSES
    ):
        return "HELD", blank_reason or blank_defect_class
    if tagmap_decision in ("not_presented", "not_in_template"):
        return "REASON", f"company_tag_map:{tagmap_decision}"
    if blank_state == "defect":
        return "BLANK", blank_reason or "defect"
    if docmap_status and docmap_status != "mapped":
        return "BLANK", f"docmap_{docmap_status.replace(' ', '_')}_not_loaded"
    return "BLANK", "no_value_no_reason"


@dataclass(frozen=True)
class Company:
    rank: int
    ticker: str
    company_id: int
    excluded: str


def load_top(path: Path, n: int = 100) -> list[Company]:
    out = []
    with path.open(newline="") as fh:
        for r in csv.DictReader(fh):
            if r["rank"].isdigit() and int(r["rank"]) <= n:
                out.append(
                    Company(
                        int(r["rank"]),
                        r["ticker"],
                        int(r["company_id"]),
                        (r.get("excluded") or "").strip(),
                    )
                )
    return sorted(out, key=lambda c: c.rank)


def load_docmap(reads_dir: Path, ticker: str) -> dict[str, dict[str, str]]:
    files = sorted(reads_dir.glob(f"{ticker}-docmap-*.csv"))
    if not files:
        return {}
    with files[-1].open(newline="") as fh:
        return {r["data_point"]: r for r in csv.DictReader(fh)}


def reached_by_filing(
    end: date, filings: list[tuple[date, str]] | None, today: date
) -> bool:
    """True when `end` can be a cell period: it is not in the future and some annual filing has reached it (a 10-K whose
    period ends on or after `end`, within the day tolerance). The period table also holds cover-page instants that
    carry fiscal_period 'FY' (e.g. 2026-09-12 for a company whose last 10-K ends 2025-12-31); no filing has reached
    them, so they are not cells. A company with no annual filing in the store is left unfiltered (no evidence either
    way; the template check reports it). Pure."""
    if end > today:
        return False
    if not filings:
        return True
    last = max(p for p, _ in filings)
    return end <= last + timedelta(days=_DAY_TOL) or fsn_end_matches(
        last, end, _DAY_TOL
    )


def _fy_periods(
    conn: Any,
    ids: list[int],
    today: date,
    annual: dict[int, list[tuple[date, str]]] | None = None,
) -> dict[tuple[int, int, str], tuple[date, date]]:
    """(company, fiscal_year, 'duration'|'instant') -> (start, end) of the FY period ending last (duration >= 300 days)
    among the periods an annual filing has reached (reached_by_filing)."""
    cur = conn.execute(
        """select company_id, fiscal_year, period_type, start_date, end_date from core.period
           where company_id = any(%s) and fiscal_period = 'FY' and fiscal_year >= %s and end_date <= %s""",
        (ids, FIRST_FY, today),
    )
    best: dict[tuple[int, int, str], tuple[date, date]] = {}
    for cid, fy, ptype, s, e in cur.fetchall():
        if ptype == "duration" and (e - s).days < 300:
            continue
        if annual is not None and not reached_by_filing(e, annual.get(cid), today):
            continue
        key = (cid, fy, ptype)
        if key not in best or e > best[key][1]:
            best[key] = (s, e)
    return best


def load_current_proofs(
    conn: Any, ids: list[int], names: list[str]
) -> dict[tuple[int, str, date, date], tuple]:
    """The verdict of each cell key: its newest analytics.cell_proof row at the CURRENT floor version whose recorded rules
    are all at their current version (proof/rules.py row_is_current; a row with no record is not current).
    A row of an older detector is history, never the verdict (a held cell is not re-proved, so a pre-R13
    restated_copies_disagree row outlived its rule for 48 MSFT cells)."""
    proofs: dict[tuple[int, str, date, date], tuple] = {}
    # chunked by company: one scan over the whole top-100 dropped the pooled connection (3 of 3 runs, 2026-11-16)
    for i in range(0, len(ids), 10):
        for row in conn.execute(
            """select distinct on (company_id, data_point_name, period_start, period_end)
                      company_id, data_point_name, period_start, period_end, verdict, reason_code, reason_text,
                      shown_value, shown_tag, shown_accession, position_source, fsn_stmt, fsn_line, checks
               from analytics.cell_proof
               where company_id = any(%s) and data_point_name = any(%s) and basis = 'latest'
                 and detector_version = %s
                 and period_grain in ('FY', 'I') and period_end >= %s
               order by company_id, data_point_name, period_start, period_end, proved_at desc, id desc""",
            (ids[i : i + 10], names, DETECTOR_VERSION, date(FIRST_FY - 1, 1, 1)),
        ).fetchall():
            # ONE-PATH step 1: current = at the floor AND every rule the row used is at its current version
            if row_is_current(DETECTOR_VERSION, row[13], DETECTOR_VERSION):
                proofs[(row[0], row[1], row[2], row[3])] = row[4:]
    return proofs


def _statement_pages(
    conn: Any, ids: list[int]
) -> dict[tuple[int, date, str], tuple[str, str]]:
    """(company, fiscal year end, statement code) -> (accession, 'R<n>.htm') of that year's own 10-K: the report that
    carries most of the statement's lines (fsn.line.stmt) in the filing whose period is the year end."""
    best: dict[tuple[int, date, str], tuple[int, str, str]] = {}
    for cid, period, acc, stmt, report, n in conn.execute(
        """select f.company_id, f.period, f.accession, l.stmt, l.report, count(*)
           from fsn.filing f join fsn.line l on l.filing_id = f.id
           where f.company_id = any(%s) and f.form in ('10-K', '10-K/A', '10-KT') and f.period is not null
             and l.stmt in ('IS', 'BS', 'CF', 'CI', 'EQ')
           group by f.company_id, f.period, f.accession, l.stmt, l.report""",
        (ids,),
    ).fetchall():
        k = (cid, period, stmt)
        if k not in best or (n, acc) > (best[k][0], best[k][1]):
            best[k] = (n, acc, f"R{report}.htm")
    return {k: (v[1], v[2]) for k, v in best.items()}


def own_year_page(
    stmt_pages: dict[tuple[int, date, str], tuple[str, str]],
    cid: int,
    end: date,
    stmt: str,
    by_cs: dict[tuple[int, str], list[tuple[date, tuple[str, str]]]] | None = None,
) -> tuple[str, str]:
    """The own-year statement page for a cell whose true period end is `end`. stmt_pages is keyed on fsn.filing.period
    (month-end rounding), so an exact lookup misses every 52/53-week year end; match with fsn_end_matches. Pure."""
    hit = stmt_pages.get((cid, end, stmt))
    if hit:
        return hit
    for p2, v in sorted(
        by_cs.get((cid, stmt), ()) if by_cs else _scan(stmt_pages, cid, stmt)
    ):
        if fsn_end_matches(p2, end, _DAY_TOL):
            return v
    return ("", "")


def _scan(
    stmt_pages: dict[tuple[int, date, str], tuple[str, str]], cid: int, stmt: str
) -> list[tuple[date, tuple[str, str]]]:
    return [(p, v) for (c, p, s), v in stmt_pages.items() if c == cid and s == stmt]


def stmt_pages_by_company(
    stmt_pages: dict[tuple[int, date, str], tuple[str, str]],
) -> dict[tuple[int, str], list[tuple[date, tuple[str, str]]]]:
    out: dict[tuple[int, str], list[tuple[date, tuple[str, str]]]] = defaultdict(list)
    for (c, p, s), v in stmt_pages.items():
        out[(c, s)].append((p, v))
    return out


def _locator_index(conn: Any, accessions: set[str], tags: set[str]) -> LocatorIndex:
    """fsn.line of the cited filings: every statement line, and the note lines (any stmt) of the tags shown."""
    idx = LocatorIndex()
    accs = sorted(a for a in accessions if a)
    for i in range(0, len(accs), 200):
        for acc, report, line, stmt, tag, plabel in conn.execute(
            """select f.accession, l.report, l.line, l.stmt, t.tag, l.plabel
               from fsn.line l join fsn.filing f on f.id = l.filing_id join fsn.tag t on t.id = l.tag_id
               where f.accession = any(%s) and (l.stmt = any(%s) or t.tag = any(%s))""",
            (accs[i : i + 200], list(STATEMENT_STMTS), sorted(tags)),
        ).fetchall():
            idx.add(acc, report, line, stmt, tag, plabel)
        for acc, report, title in conn.execute(
            """select f.accession, r.report, r.shortname
               from fsn.report r join fsn.filing f on f.id = r.filing_id
               where f.accession = any(%s) and r.shortname is not null""",
            (accs[i : i + 200],),
        ).fetchall():
            idx.titles[(acc, report)] = title
    return idx


def build_rows(
    conn: Any,
    companies: list[Company],
    reads_dir: Path,
    today: date,
    note_lookup: dict[tuple[str, str], int] | None = None,
    fix_pages: dict[tuple[str, str, str, str], dict[str, int]] | None = None,
) -> tuple[list[dict[str, Any]], dict[int, str]]:
    templates = {c.company_id: load_docmap(reads_dir, c.ticker) for c in companies}
    live = [c for c in companies if templates[c.company_id]]
    ids = [c.company_id for c in live]
    annual = _annual_filings(conn, ids)
    periods = _fy_periods(conn, ids, today, annual)
    names = sorted(
        {n for c in live for dp in templates[c.company_id] for n in candidates(dp)}
    )
    concept_id = {
        n: i
        for i, n in conn.execute(
            "select id, name from analytics.canonical_concept where name = any(%s)",
            (names,),
        ).fetchall()
    }
    served: dict[tuple[int, str, date, date], Decimal] = {}
    served_family: dict[tuple[int, str, date, date], str] = {}
    for cid, name, s, e, v, fam in conn.execute(
        """select f.company_id, c.name, p.start_date, p.end_date, f.value, f.family
           from analytics.canonical_fact f join core.period p on p.id = f.period_id
           join analytics.canonical_concept c on c.id = f.canonical_concept_id
           where f.company_id = any(%s) and c.name = any(%s) and p.fiscal_period = 'FY' and p.fiscal_year >= %s""",
        (ids, names, FIRST_FY),
    ).fetchall():
        served[(cid, name, s, e)] = v
        served_family[(cid, name, s, e)] = fam or ""
    proofs = load_current_proofs(conn, ids, names)
    blanks: dict[tuple[int, str, date, date], tuple] = {}
    for row in conn.execute(
        """select distinct on (company_id, data_point_name, period_start, period_end)
                  company_id, data_point_name, period_start, period_end, state, reason_code, reason_text,
                  defect_class
           from analytics.cell_blank_reason
           where company_id = any(%s) and data_point_name = any(%s) and basis = 'latest'
             and period_grain in ('FY', 'I') and period_end >= %s
           order by company_id, data_point_name, period_start, period_end, created_at desc, id desc""",
        (ids, names, date(FIRST_FY - 1, 1, 1)),
    ).fetchall():
        blanks[(row[0], row[1], row[2], row[3])] = row[4:]
    tagmap: dict[tuple[int, str], list[tuple]] = defaultdict(list)
    for (
        cid,
        name,
        dec,
        ef,
        et,
        reason,
        rclass,
        eadsh,
        erep,
        elab,
        eline,
        mstmt,
    ) in conn.execute(
        """select m.company_id, c.name, m.decision, m.era_from, m.era_to, m.reason, m.reason_class,
                  m.evidence_adsh, m.evidence_report, m.evidence_plabel, m.evidence_line, m.stmt
           from analytics.company_tag_map m join analytics.canonical_concept c on c.id = m.canonical_concept_id
           where m.company_id = any(%s) and m.decision in ('not_presented', 'not_in_template', 'combined')""",
        (ids,),
    ).fetchall():
        tagmap[(cid, name)].append(
            (
                dec,
                ef,
                et,
                reason,
                rclass,
                bool(eadsh and (erep or elab)),
                (eadsh, erep, eline, elab, mstmt),
            )
        )

    # the company's CURRENT sector template (latest effective_from <= today): data point -> in_template
    in_tpl: dict[tuple[int, str], bool] = {}
    for cid, dp, inn in conn.execute(
        """select t.company_id, t.data_point, t.in_template from analytics.company_data_point_template t
           where t.company_id = any(%s) and t.effective_from = (
             select max(effective_from) from analytics.company_data_point_template x
             where x.company_id = t.company_id and x.effective_from <= %s)""",
        (ids, today),
    ).fetchall():
        in_tpl[(cid, dp)] = bool(inn)

    stmt_pages = _statement_pages(conn, ids)
    stmt_by_cs = stmt_pages_by_company(stmt_pages)
    cited = {v[0] for v in stmt_pages.values()}
    cited |= {p[5] for p in proofs.values() if p[5]}
    cited |= {ev[6][0] for evs in tagmap.values() for ev in evs if ev[6][0]}
    shown_tags = {
        t.strip() for p in proofs.values() if p[4] for t in p[4].split(",") if t.strip()
    }
    idx = _locator_index(conn, cited, shown_tags)
    earliest = _earliest_filings(conn, ids)
    columns = cg.read_columns(conn, ids)

    rows: list[dict[str, Any]] = []
    for c in live:
        years = sorted({fy for (cid, fy, _t) in periods if cid == c.company_id})
        if not years:
            continue
        for dp, dm in sorted(templates[c.company_id].items()):
            if dm["status"] == "OUT":
                continue
            ptype = "instant" if dp in INSTANT_DPS else "duration"
            for fy in years:
                per = periods.get((c.company_id, fy, ptype))
                if per is None:
                    continue
                s, e = per
                cand = candidates(dp)
                svalue = sname = None
                sfam = ""
                for n in cand:
                    if (c.company_id, n, s, e) in served:
                        svalue, sname = served[(c.company_id, n, s, e)], n
                        sfam = served_family.get((c.company_id, n, s, e), "")
                        break
                prow = brow = pname = None
                for n in ([sname] if sname else []) + cand:
                    if prow is None and (c.company_id, n, s, e) in proofs:
                        prow, pname = proofs[(c.company_id, n, s, e)], n
                    if brow is None and (c.company_id, n, s, e) in blanks:
                        brow = blanks[(c.company_id, n, s, e)]
                tm = None
                comb = False
                covering: list[tuple[bool, tuple]] = []
                for n in cand:
                    for dec, ef, et, why, rcl, evid, evt in tagmap.get(
                        (c.company_id, n), []
                    ):
                        if (ef is None or ef <= e) and (et is None or et >= e):
                            is_comb = dec == "combined" or rcl in COMBINED_CLASSES
                            if evid and is_comb:
                                comb = True
                            if evt[0]:
                                covering.append((is_comb, evt))
                            if dec != "combined":
                                tm = (dec, why, rcl)
                (
                    verdict,
                    preason,
                    ptext,
                    pval,
                    ptag,
                    pacc,
                    psrc,
                    pstmt,
                    pline,
                    pchecks,
                ) = prow if prow else (None,) * 10
                parts, parts_blank = (
                    parts_locator(
                        pchecks,
                        pacc,
                        idx,
                        note_lookup,
                        (fix_pages or {}).get(
                            (c.ticker, dp, e.isoformat(), pacc or "")
                        ),
                    )
                    if cls_is_value(svalue, verdict)
                    else ("", 0)
                )
                cls, code = classify(
                    verdict,
                    preason,
                    pval,
                    svalue,
                    brow[0] if brow else None,
                    brow[1] if brow else None,
                    tm[0] if tm else None,
                    dm["status"],
                    brow[3] if brow else None,
                    tm[2] if tm else None,
                    in_tpl.get((c.company_id, dp)),
                    comb,
                )
                # ONE filing per locator: the accession and the page always come from the same fsn filing.
                #  - a cell with a proof: the proof's shown_accession and that filing's line/report of the shown tag;
                #  - a REASON: the covering map row's evidence_adsh and its evidence_report;
                #  - otherwise the year's own 10-K (accession and statement report both from it).
                dstmt = dm.get("stmt", "")
                label = ""
                if cls == "REASON" and covering:
                    # only evidence of a filing that presents THIS period counts; prefer such a row
                    ok_accs = eligible_filings(
                        annual.get(c.company_id, []), e, ptype == "instant"
                    )
                    covering = [x for x in covering if x[1][0] in ok_accs] or covering
                    pref = sorted(
                        covering,
                        key=lambda x: (x[0] != (code == COMBINED), x[1][1] is None),
                    )
                    acc, page, lsrc, label = reason_locator(
                        [x[1] for x in pref], dstmt, idx
                    )
                else:
                    acc, page, lsrc = proven_locator(
                        pacc, pstmt, pline, ptag, idx, note_lookup
                    )
                if (
                    lsrc
                    in (
                        "none",
                        "note_fact_report_not_stored",
                        "evidence_acc_no_page",
                    )
                    and not (acc and page)
                    and not (
                        # a PROVEN cell whose shown tag is a note fact cites that filing's NOTE page, never the
                        # statement page of the year (PM interest_expense: IS prints only 'Interest expense, net')
                        cls == "PROVEN" and lsrc == "note_fact_report_not_stored"
                    )
                ):
                    own_acc, own_page = own_year_page(
                        stmt_pages, c.company_id, e, dstmt, stmt_by_cs
                    )
                    if own_acc and not acc:
                        acc, page, lsrc = own_acc, own_page, "own_year"
                    elif own_acc and acc == own_acc and own_page:
                        page, lsrc = own_page, "own_year"
                if cls == "REASON" and acc and not page:
                    # accession without a page: the page of the cell's statement in THAT filing (a parenthetical
                    # share count is placed on the balance sheet of an instant data point); never another filing's
                    page_, lsrc_ = statement_page_fallback(
                        acc, dstmt, ptype == "instant", idx
                    )
                    if page_:
                        page, lsrc = page_, lsrc_
                # a REASON is evidence only from the cell's own-period filing (or a later one that presents the
                # period); a reason cited from any other filing is not evidence for this period
                cls, code = own_period_reason(
                    cls,
                    code,
                    acc,
                    annual.get(c.company_id, []),
                    e,
                    ptype == "instant",
                    earliest.get(c.company_id),
                    columns.get(c.company_id),
                )
                # reason text only on a non-PROVEN cell; a combined reason quotes the printed label of its evidence
                reason_text = reason_fields(
                    cls,
                    code,
                    ptext or (brow[2] if brow else None) or (tm[1] if tm else None),
                )[1]
                if cls == "REASON" and code == COMBINED:
                    reason_text = combined_reason_text(
                        reason_text
                        or next(
                            (
                                w
                                for n in cand
                                for d_, f_, t_, w, rc_, ev_, et_ in tagmap.get(
                                    (c.company_id, n), []
                                )
                                if (f_ is None or f_ <= e)
                                and (t_ is None or t_ >= e)
                                and w
                            ),
                            "",
                        ),
                        label,
                    )
                ef_ = earliest.get(c.company_id)
                ann = annual.get(c.company_id, [])
                yp = year_presence(ann, ef_, e, ptype == "instant")
                in_window = [(p_, a_) for p_, a_ in ann if p_.year >= FIRST_FY - 1]
                shown = (
                    svalue
                    if svalue is not None
                    else (pval if cls == "DISAGREE" else None)
                )
                rows.append(
                    {
                        "rank": c.rank,
                        "ticker": c.ticker,
                        "company_id": c.company_id,
                        "data_point": dp,
                        "fiscal_year": fy,
                        "period_end": e.isoformat(),
                        "class": cls,
                        "reason_code": reason_fields(cls, code, "")[0],
                        "reason": reason_text or "",
                        "shown_value": "" if shown is None else format(shown, "f"),
                        "proof_verdict": verdict or "",
                        "verdict": verdict or "",
                        "accession": acc,
                        "r_page": page,
                        "locator_source": lsrc,
                        "evidence": "",
                        "_shown_acc": pacc or "",
                        "_family": sfam,
                        "tag": ptag or "",
                        "value_source": psrc
                        or ("canonical_fact" if svalue is not None else ""),
                        "docmap_status": dm["status"],
                        "parts": parts,
                        "_parts_blank": parts_blank,
                        "_before_first_filing": yp["before_first"],
                        "_comparative_only": yp["comparative_only"],
                        "_presented": yp["presented"],
                        "_earliest_filing": ef_.isoformat() if ef_ else "",
                        "_first_presenting": yp["first_presenting"],
                        "_latest_10k": max(ann)[1] if ann else "",
                        "_first_10k": min(in_window)[1] if in_window else "",
                    }
                )
    rows, _out = split_out_of_template(rows, load_not_in_template())
    resolve_derived(rows, load_input_prints(conn, rows))
    attach_only_combined(rows, load_only_combined())
    attach_absent_in_own(rows, load_absent_in_own())
    attach_presence(rows, load_presence(conn, ids))
    attach_stated_zero(rows, load_stated_zero())
    apply_display(rows)
    note = {
        c.company_id: (
            "TEMPLATE_UNAVAILABLE"
            + (f" (excluded: {c.excluded})" if c.excluded else " (no docmap)")
        )
        for c in companies
        if not templates[c.company_id]
    }
    return rows, note


def _vkey(v: Any) -> str:
    return format(Decimal(str(v)).normalize(), "f")


def _pending_derived(
    rows: list[dict[str, Any]],
) -> list[tuple[dict[str, Any], list[dict[str, Any] | None]]]:
    by = {(r["company_id"], r["data_point"], r["fiscal_year"]): r for r in rows}
    return [
        (
            r,
            [
                by.get((r["company_id"], dp, r["fiscal_year"]))
                for dp in DERIVED_INPUTS.get(r["data_point"], ())
            ],
        )
        for r in rows
        if r.get("_family") == DERIVED_FAMILY
        and r["class"] not in ("PROVEN", "DISAGREE")
    ]


def load_input_prints(
    conn: Any, rows: list[dict[str, Any]]
) -> dict[tuple[int, str, str, str], set[str]]:
    """(company, period_end, tag, value) -> accessions of the annual filings that print that fact, for the single-tag
    PROVEN inputs of the derived cells still unresolved (C1 same-filing: one filing must print both inputs)."""
    want: set[tuple[int, str, str, str]] = set()
    for _r, inputs in _pending_derived(rows):
        for i in inputs:
            tags = [t for t in (i["tag"] or "").split(",") if t] if i else []
            if (
                i
                and i["class"] == "PROVEN"
                and len(tags) == 1
                and i["shown_value"] != ""
            ):
                want.add(
                    (i["company_id"], i["period_end"], tags[0], _vkey(i["shown_value"]))
                )
    out: dict[tuple[int, str, str, str], set[str]] = defaultdict(set)
    if not want:
        return out
    ids = sorted({k[0] for k in want})
    tags = sorted({k[2] for k in want})
    ends = sorted({date.fromisoformat(k[1]) for k in want})
    for cid, tag, end, start, ptype, value, acc in conn.execute(
        """select f.company_id, c.tag, p.end_date, p.start_date, p.period_type, f.value, fl.accession_number
           from core.fact f join core.concept c on c.id = f.concept_id join core.period p on p.id = f.period_id
           join core.filing fl on fl.id = f.filing_id
           where f.company_id = any(%s) and c.tag = any(%s) and p.end_date = any(%s) and not f.is_derived
             and fl.form in ('10-K', '10-K/A', '10-KT', '10-KT/A', '20-F', '20-F/A', '40-F', '40-F/A')""",
        (ids, tags, ends),
    ).fetchall():
        if ptype == "duration" and (end - start).days < 300:
            continue
        key = (cid, end.isoformat(), tag, _vkey(value))
        if key in want:
            out[key].add(acc)
    return out


def resolve_derived(
    rows: list[dict[str, Any]],
    prints: dict[tuple[int, str, str, str], set[str]] | None = None,
) -> None:
    """In place. A served cell of family derived_not_printed is DERIVED only when every input data point of the same
    company and fiscal year is PROVEN and all inputs sit in ONE filing: either the same shown_accession, or (`prints`,
    C1 same-filing) one annual filing that prints each input's served value under its tag, one of the inputs'
    locators being in that filing. The row then lists the derivation as `dp=value@accession`. Any other case is
    UNCHECKED derived_inputs_unproven."""
    for r, inputs in _pending_derived(rows):
        ok = (
            bool(inputs)
            and all(
                i is not None and i["class"] == "PROVEN" and i["_shown_acc"]
                for i in inputs
            )
            and len({i["_shown_acc"] for i in inputs if i}) == 1
        )
        host = None
        if (
            not ok
            and prints
            and inputs
            and all(i is not None and i["class"] == "PROVEN" for i in inputs)
        ):
            sets: list[set[str]] = []
            for i in inputs:
                tags = [t for t in (i["tag"] or "").split(",") if t] if i else []
                if i is None or len(tags) != 1 or i["shown_value"] == "":
                    sets = []
                    break
                sets.append(
                    prints.get(
                        (
                            i["company_id"],
                            i["period_end"],
                            tags[0],
                            _vkey(i["shown_value"]),
                        ),
                        set(),
                    )
                )
            common = set.intersection(*sets) if sets else set()
            host = next(
                (i for i in inputs if i and i["_shown_acc"] in common and i["r_page"]),
                None,
            )
            ok = host is not None
        if inputs:
            r["evidence"] = "; ".join(
                f"{i['data_point']}={i['shown_value']}@"
                f"{(host['_shown_acc'] if host else i['_shown_acc']) or '?'}"
                for i in inputs
                if i is not None
            )
        first = host or next((i for i in inputs if i is not None), None)
        if ok and first is not None:
            r["class"], r["reason_code"] = "DERIVED", DERIVED_CODE
            r["reason"] = (
                f"{r['data_point']} is not printed; derived from {r['evidence']}, "
                "inputs proven against one filing"
            )
            r["accession"], r["r_page"], r["locator_source"] = (
                first["accession"],
                first["r_page"],
                "derived_input",
            )
        else:
            r["class"], r["reason_code"] = "UNCHECKED", DERIVED_UNPROVEN


RESOLVER_DIR = Path("data-team/tags/line_map")
OC_EVIDENCE_RE = re.compile(r"reported only combined: ([^|,]*)")


def load_not_in_template(
    resolver_dir: Path = RESOLVER_DIR,
) -> set[tuple[str, str]]:
    """(ticker, data_point) pairs the CURRENT resolver (newest resolver-all110-*.csv) decides `not_in_template` in every
    one of its rows (resolver .57: the bank data points for the non-bank companies). The pair is outside the company's
    grid. A pair with any other decision in some row is not returned. Missing file: empty."""
    files = sorted(resolver_dir.glob("resolver-all110-*.csv"))
    seen: dict[tuple[str, str], bool] = {}
    if not files:
        return set()
    with files[-1].open(newline="") as fh:
        for r in csv.DictReader(fh):
            key = (r["ticker"], r["data_point"])
            seen[key] = seen.get(key, True) and r.get("decision") == "not_in_template"
    return {k for k, all_out in seen.items() if all_out}


def split_out_of_template(
    rows: list[dict[str, Any]], out: set[tuple[str, str]]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """(kept, out_of_template). A cell whose (ticker, data_point) the resolver decides not_in_template is OUT: not a
    shown cell, not OPEN, in no count (Dhairya 2026-11-16). The existing in-template contradiction guard (a
    company_tag_map / blank-state not_in_template on a template point) is a different case and is untouched. Pure."""
    kept = [r for r in rows if (r["ticker"], r["data_point"]) not in out]
    dropped = [r for r in rows if (r["ticker"], r["data_point"]) in out]
    return kept, dropped


def load_only_combined(
    resolver_dir: Path = RESOLVER_DIR,
) -> dict[tuple[str, str, str], tuple[str, str, str]]:
    """(ticker, data_point, period_end) -> (hide kind 'row'|'years', evidence text, accession) from the CURRENT resolver
    file on main (the newest resolver-all110-*.csv; the flags are read, never recomputed, and no resolver version is
    pinned). only_combined_row: the company never reports the pure figure in any year; only_combined_years: it does in
    other years (Dhairya 2026-11-16). Missing file or no flags: empty."""
    files = sorted(resolver_dir.glob("resolver-all110-*.csv"))
    out: dict[tuple[str, str, str], tuple[str, str, str]] = {}
    if not files:
        return out
    with files[-1].open(newline="") as fh:
        for r in csv.DictReader(fh):
            flags = (r.get("flags") or "").split(";")
            if "only_combined" not in flags or r.get("grain") != "FY":
                continue
            kind = "row" if "only_combined_row" in flags else "years"
            m = OC_EVIDENCE_RE.search(r.get("nodes") or "")
            line = (m.group(1).strip() if m else "") or "unnamed line"
            out[(r["ticker"], r["data_point"], r["period_end"])] = (
                kind,
                f"reported only combined: {line}",
                r.get("accession") or "",
            )
    return out


def attach_only_combined(
    rows: list[dict[str, Any]],
    oc: dict[tuple[str, str, str], tuple[str, str, str]],
) -> None:
    """Carry the resolver's only_combined hide, its evidence text and its accession on each flagged non-value cell. The
    combined printed number stays in the data as evidence and is never shown as the standard data point. Pure."""
    # the resolver keys on the FSN month end (ADI 2016-10-31), a cell on the true 52/53-week end (2016-10-29): match with
    # fsn_end_matches on the same ticker and data point, and only when exactly one resolver period matches
    by_key: dict[tuple[str, str], list[tuple[date, tuple[str, str, str]]]] = (
        defaultdict(list)
    )
    for (tk, dp, pe), v in oc.items():
        by_key[(tk, dp)].append((date.fromisoformat(pe), v))
    for r in rows:
        if r["class"] in ("PROVEN", "DERIVED"):
            continue
        hit = oc.get((r["ticker"], r["data_point"], r["period_end"]))
        if hit is None:
            end = date.fromisoformat(r["period_end"])
            near = [
                v
                for d, v in by_key.get((r["ticker"], r["data_point"]), ())
                if fsn_end_matches(d, end)
            ]
            hit = near[0] if len(near) == 1 else None
        if hit:
            r["_only_combined"], r["evidence"], r["_oc_accession"] = hit
            if not r.get("accession"):
                r["accession"] = hit[2]


ABSENT_EVIDENCE = "no face-statement line for this role in the year's own 10-K (resolver not_presented, column own)"
_VALUED_DECISIONS = ("mapped", "component_sum", "derived_not_printed", "combined")


# ALLOWLIST: only data points checked against the filings may be hidden by this rule. The resolver's not_presented is a
# tag-list lookup and misses printed content: custom tags (QCOM interest paid, CVX sbc, CRM amortization), notes (NFLX
# trade receivables), MD&A (PH interest income), a line tagged as another element (T inventories as PrepaidExpenseCurrent),
# per-plan or quarterly-only prints (SCCO sbc, C/DHR/SYK dividends per share). FILING-CHECKED 2026-11-16, two verifier
# samples, 40 cells: operating_income 6/6, shares_outstanding 3/3, share_buybacks 6/6, 0 wrong. A data point is added
# here only after a >=20-cell filing check with 0 wrong; every other data point stays OPEN for the resolver to fill.
VERIFIED_ABSENT_HIDE = frozenset(
    {
        "operating_income",
        "shares_outstanding",
        "share_buybacks",
        # round 3, FILING-CHECKED 2026-11-16, 0 wrong each: current_assets + current_liabilities 20, gross_profit 20,
        # dividends_paid 20, total_debt 37 (all), share_buybacks re-sample 20. research_and_development FAILED
        # (MCK FY2021 R&D $74M stated in Item 1 after the face line was dropped) and stays out.
        "current_assets",
        "current_liabilities",
        "gross_profit",
        "dividends_paid",
        "total_debt",
        # round 4, FILING-CHECKED 2026-11-17: inventory 20 checked, 0 wrong (resolver .63+ face-label fix). sbc FAILED
        # (XOM/CVX note totals) and ppe_net FAILED outside the sample filter (GS Other-assets note 2014-21); both stay out.
        "inventory",
    }
)


def load_absent_in_own(
    resolver_dir: Path = RESOLVER_DIR,
) -> dict[tuple[str, str], tuple[dict[str, str], list[date]]]:
    """Only VERIFIED_ABSENT_HIDE data points. (ticker, data_point) -> ({period_end: own accession} for cells the CURRENT resolver (newest resolver-all110-*.csv)
    decides `not_presented` in the year's own 10-K, the resolver periods where the line IS printed). The resolver has no
    flag literally named absent_in_own_filing: the meaning is decision = not_presented, column = own, and not a
    before_first_10k / line_not_printed pre-filing year (those are other hides). `accession` is the evidence column.
    The printed periods feed the later-filing guard. Missing file: empty."""
    files = sorted(resolver_dir.glob("resolver-all110-*.csv"))
    absent: dict[tuple[str, str], dict[str, str]] = defaultdict(dict)
    printed: dict[tuple[str, str], list[date]] = defaultdict(list)
    if not files:
        return {}
    # a comparative_fill row's accession is a LATER filing's: that filing's own period is the period_end of the `own`
    # rows carrying the same accession (any data point)
    own_period: dict[tuple[str, str], date] = {}
    comparative: list[tuple[tuple[str, str], str, date]] = []
    with files[-1].open(newline="") as fh:
        for r in csv.DictReader(fh):
            key = (r["ticker"], r["data_point"])
            if r.get("column") == "own" and r.get("accession"):
                own_period[(r["ticker"], r["accession"])] = date.fromisoformat(
                    r["period_end"]
                )
            if r["data_point"] not in VERIFIED_ABSENT_HIDE:
                continue  # unverified data point: never hidden by this rule, stays open for the resolver
            if r.get("decision") in _VALUED_DECISIONS:
                pe = date.fromisoformat(r["period_end"])
                if r.get("column") == "comparative" and r.get("accession"):
                    comparative.append((key, r["accession"], pe))
                else:
                    printed[key].append(pe)
                continue
            flags = (r.get("flags") or "").split(";")
            if (
                r.get("decision") != "not_presented"
                or r.get("column") != "own"
                or "before_first_10k" in flags
                or "line_not_printed" in flags
                or not r.get("accession")
            ):
                continue
            absent[key][r["period_end"]] = r["accession"]
    for key, acc, pe in comparative:
        # the line is printed by the filing that fills the comparative, not by a filing OF that period: the later-filing
        # guard asks whether THAT filing's columns carry the absent year (DHR/UBER FY2022 buybacks are filled from the
        # FY2024 10-K, which does not carry FY2020-21; the FY2022 10-K itself prints no line). Filing unknown: the
        # period itself (the strict old behaviour).
        printed[key].append(own_period.get((key[0], acc), pe))
    return {k: (v, printed.get(k, [])) for k, v in absent.items()}


def attach_absent_in_own(
    rows: list[dict[str, Any]],
    absent: dict[tuple[str, str], tuple[dict[str, str], list[date]]],
) -> None:
    """Mark each non-value cell the resolver decides not_presented in its own annual report as `_absent_own`, carrying
    the resolver accession as evidence (Dhairya 2026-11-16). Matching is only_combined's: same ticker and data point,
    exact period or fsn_end_matches, exactly one candidate. Guard, never hide a year a later annual report prints for
    the data point: a later resolver period inside the span eligible_filings gives (the later report's own column; it
    carries the year as a comparative) where the line is printed keeps the cell open, so the resolver fills it. Pure."""
    for r in rows:
        if r["class"] in ("PROVEN", "DERIVED"):
            continue
        got = absent.get((r["ticker"], r["data_point"]))
        if not got:
            continue
        cells, printed = got
        end = date.fromisoformat(r["period_end"])
        acc = cells.get(r["period_end"])
        if acc is None:
            near = [
                a
                for d, a in cells.items()
                if fsn_end_matches(date.fromisoformat(d), end)
            ]
            acc = near[0] if len(near) == 1 else None
        if acc is None:
            continue
        instant = r["data_point"] in INSTANT_DPS
        later = [
            d
            for d in printed
            if d > end
            and not fsn_end_matches(d, end, _DAY_TOL)
            and eligible_filings([(d, "L")], end, instant)
        ]
        if later:
            continue
        r["_absent_own"] = True
        r["_oc_accession"] = acc
        r["evidence"] = r.get("evidence") or ABSENT_EVIDENCE
        if not r.get("accession"):
            r["accession"] = acc


STATED_ZERO_FAMILY = "company_tag_map:stated_zero"
TEXT_STATED_FAMILY = "company_tag_map:text_stated"
# (accession, locator, quote, kind, value)
StatedRec = tuple[str, str, str, str, Decimal]


def load_stated_zero(
    resolver_dir: Path = RESOLVER_DIR,
) -> dict[tuple[str, str], dict[str, StatedRec]]:
    """Rulings 2026-11-16 (Dhairya): (ticker, data_point) -> {period_end: (accession, locator, quote, kind, value)} for
    every VALID stated_zero / text_stated row of the newest resolver-all110-*.csv (same validation as serving: quote,
    locator, accession, value 0 / nonzero, quote_period == period_end). An invalid row is absent, so its cell stays
    what it was. Missing file: empty."""
    files = sorted(resolver_dir.glob("resolver-all110-*.csv"))
    out: dict[tuple[str, str], dict[str, StatedRec]] = defaultdict(dict)
    if not files:
        return {}
    with files[-1].open(newline="") as fh:
        for r in csv.DictReader(fh):
            kind = sl.stated_kind(r.get("decision", ""), r.get("flags", ""))
            if not kind:
                continue
            try:
                pe = date.fromisoformat(r["period_end"])
            except ValueError:
                continue
            if sl.stated_zero_problem(r, pe, r.get("accession", ""), kind):
                continue
            out[(r["ticker"], r["data_point"])][r["period_end"]] = (
                r["accession"],
                r["locator"].strip(),
                r["quote"].strip(),
                kind,
                Decimal(r["value"]),
            )
    return dict(out)


def attach_stated_zero(
    rows: list[dict[str, Any]],
    sz: dict[tuple[str, str], dict[str, StatedRec]],
) -> None:
    """A cell SERVED by the stated_zero or text_stated family whose resolver row is valid, of the same kind and the same
    value, is a shown value: `_stated_zero`, accession = the filing that states it, r_page = the section/page locator
    (the page gate accepts a section), evidence = the exact quote, column `stated_zero` or `text_stated` = Y so Ritwik
    can sample every such cell. Matching is the same ticker and data point and the exact period or exactly one
    fsn_end_matches period. Pure."""
    fam = {STATED_ZERO_FAMILY: sl.STATED_ZERO, TEXT_STATED_FAMILY: sl.TEXT_STATED}
    for r in rows:
        kind = fam.get(r.get("_family", ""))
        if kind is None or r.get("shown_value") in ("", None):
            continue
        got = sz.get((r["ticker"], r["data_point"]))
        if not got:
            continue
        rec = got.get(r["period_end"])
        if rec is None:
            end = date.fromisoformat(r["period_end"])
            near = [
                v for d, v in got.items() if fsn_end_matches(date.fromisoformat(d), end)
            ]
            rec = near[0] if len(near) == 1 else None
        if rec is None or rec[3] != kind or Decimal(r["shown_value"]) != rec[4]:
            continue
        r["_stated_zero"] = True
        r[kind] = "Y"
        r["accession"], r["r_page"], r["evidence"] = rec[0], rec[1], rec[2]
        r["locator_source"] = kind


# LINE-level presence (Dhairya 2026-11-16): a cell is never hidden when ANY periodic filing of the company (10-K, 10-Q,
# 20-F, 40-F, own or comparative column, via the shared company_filings()) prints THIS data point's line or fact at that
# period end: an undimensioned, valued fact on a tag of the data point's family (HIDE_FAMILY, the approver's own family
# list) that sits on a rendered line. A period some filing presents while none prints the line does not block a hide
# (a period-level test would make every year inside the filing window unhideable). Not matched: a line printed under a
# custom tag or only by label, which the family list cannot see.
_FAMILY_TAGS = sorted({t for tags in HIDE_FAMILY.values() for t in tags})
_PRESENCE_SQL = """
select v.filing_id, t.tag, v.ddate, v.qtrs
from fsn.value v
join fsn.tag t on t.id = v.tag_id
join fsn.dim d on d.id = v.dim_id and d.segments = ''
where v.filing_id = any(%s) and coalesce(v.coreg, '') = '' and v.value is not null
  and v.qtrs in (0, 4) and t.tag = any(%s)
  and exists (select 1 from fsn.line l where l.filing_id = v.filing_id and l.tag_id = v.tag_id)
"""


def load_presence(
    conn: Any, company_ids: list[int], chunk: int = 10
) -> dict[int, list[tuple[date, str, int]]]:
    """company id -> (ddate, tag, qtrs) of every undimensioned, valued, rendered fact on a HIDE_FAMILY tag
    in ANY periodic filing of the company (company_filings(): predecessors inside their windows). Read-only."""
    tags = _FAMILY_TAGS
    out: dict[int, list[tuple[date, str, int]]] = defaultdict(list)
    for i in range(0, len(company_ids), chunk):
        ids = company_ids[i : i + chunk]
        owner = {
            f.id: f.company_id
            for f in company_filings(conn, ids, source="fsn", forms=CERT_PERIODIC_FORMS)
        }
        if not owner:
            continue
        for fid, tag, dd, q in conn.execute(
            _PRESENCE_SQL, (list(owner), tags)
        ).fetchall():
            out[owner[fid]].append((dd, tag, int(q)))
    return out


def attach_presence(
    rows: list[dict[str, Any]],
    presence: dict[int, list[tuple[date, str, int]]],
) -> None:
    """Set `_family_hit`: a fact on the data point's own tag family, undimensioned, rendered, annual (instant for a
    balance-sheet point), dated at the cell's period, in any periodic filing. The cell is then not hidden, and a row with
    any such year is not 'never reported'. Pure."""
    by_co: dict[int, dict[str, list[tuple[date, int]]]] = {}
    for cid, facts in presence.items():
        fam: dict[str, list[tuple[date, int]]] = defaultdict(list)
        for d, t, q in facts:
            fam[t].append((d, q))
        by_co[cid] = fam
    for r in rows:
        fam = by_co.get(r["company_id"], {})
        end = date.fromisoformat(r["period_end"])
        want = 0 if r["data_point"] in INSTANT_DPS else 4
        r["_family_hit"] = any(
            q == want and fsn_end_matches(d, end, 7)
            for t in HIDE_FAMILY.get(r["data_point"], ())
            for d, q in fam.get(t, ())
        )


# HIDE CLASSES (doc 02, "Display rules under the 2026-11-16 founder decision"; certify_display.check_hide_reasons).
# A cell may be HIDDEN_ROW or HIDDEN_YEAR only on one of these bases; every other reason is a PIPELINE STATE (era_unmapped,
# *_unverified, no_role, proof_unchecked, no_proof_row, predictor_candidate, open_period, held_*, anything new) and stays
# OPEN. The value is the cell's `hide_class` column.
HC_STRUCTURAL = "structural_not_presented"
HC_COMBINED = "line_presented_combined"
HC_PRE_FILING = "pre_filing"
HC_VERIFIED_ABSENT = "verified_absent"
HIDE_ELIGIBLE: dict[str, str] = {
    **{code: HC_STRUCTURAL for code in NOT_PRESENTED_CODES},
    **{code: HC_PRE_FILING for code in NO_PERIOD_CODES},
    "line_presented_combined": HC_COMBINED,
    "only_combined": HC_COMBINED,
}


def apply_display(rows: list[dict[str, Any]]) -> None:
    """Set row['display'] and row['hide_class'] for every cell. Pure, in place. Precedence per cell: a proven or derived
    value is shown; a year that NO periodic report presents (row['_presented'] false) and that either ends before the
    company's first periodic filing (row['_before_first_filing']) or carries an evidenced no-period reason is a hidden
    year (a later 10-K comparative column makes it presented, so it is never hidden); a row whose every non-hidden-year
    cell is an evidenced not-presented reason is a hidden row; everything else is open. A hide needs a HIDE_ELIGIBLE
    class (never a pipeline-state reason), also on the row-collapse path."""
    by_row: dict[tuple[Any, Any], list[dict[str, Any]]] = defaultdict(list)
    for r in rows:
        code = r.get("reason_code")
        is_reason = r["class"] == "REASON"
        reason_hc = HIDE_ELIGIBLE.get(code) if is_reason and code else None
        before = bool(
            r.get("_before_first_filing") and not REGISTRATION_STATEMENT_PRESENTS_YEAR
        )
        no_period = before or reason_hc == HC_PRE_FILING
        hc: str | None = None
        if r["class"] in ("PROVEN", "DERIVED") or r.get("_stated_zero"):
            r["display"] = SHOWN_VALUE
        elif r.get("_only_combined") == "years":
            r["display"], hc = HIDDEN_YEAR, HC_COMBINED
        elif r.get("_only_combined") == "row":
            r["display"], hc = HIDDEN_ROW, HC_COMBINED
        elif r.get("_absent_own") and r.get("data_point") in VERIFIED_ABSENT_HIDE:
            r["display"], hc = HIDDEN_YEAR, HC_VERIFIED_ABSENT
        elif no_period and not r.get("_presented"):
            r["display"], hc = HIDDEN_YEAR, HC_PRE_FILING
        elif r.get("_comparative_only") and reason_hc in (
            HC_PRE_FILING,
            HC_STRUCTURAL,
        ):
            # Dhairya 2026-11-16: the FIRST annual report presents the year only as a comparative column and no line
            # is printed there (an evidenced reason, no value): hidden for that row, evidenced by that accession
            r["display"], hc = HIDDEN_YEAR, reason_hc
        else:
            r["display"] = OPEN
        if r["display"] == HIDDEN_YEAR and r.get("_family_hit"):
            # ONE line-level presence test for EVERY hidden-year route (only_combined years, absent_in_own, comparative-only,
            # no-period reasons): a period in which any periodic filing prints THIS data point's line is never hidden; it
            # stays OPEN until filled (BA 2026-11-16). A period presented without the line may still be hidden.
            r["display"], hc = OPEN, None
        r["hide_class"] = hc or ""
        by_row[(r["company_id"], r.get("data_point"))].append(r)
    for cells in by_row.values():
        rest = [c for c in cells if c["display"] != HIDDEN_YEAR]
        if rest and all(
            c["display"] == HIDDEN_ROW
            or (c["class"] == "REASON" and c.get("reason_code") in NOT_PRESENTED_CODES)
            for c in rest
        ):
            for c in rest:
                if c["display"] != HIDDEN_ROW:
                    c["hide_class"] = HC_STRUCTURAL
                c["display"] = HIDDEN_ROW
        elif any(c["display"] == SHOWN_VALUE for c in cells):
            # the resolver says the pure figure is never reported but a value is shown in this row: a contradiction
            # that stays visible as open work, never a silent hide
            for c in cells:
                if c["display"] == HIDDEN_ROW and c.get("_only_combined") == "row":
                    c["display"] = OPEN
                    c["hide_class"] = ""
        elif not rest and cells:
            # every year is before the first filing: nothing of this row can be shown
            for c in cells:
                c["display"] = HIDDEN_ROW
        if any(c.get("_family_hit") for c in cells):
            # a row hidden as never reported must have no year whose own filing prints the line (MO other income FY2015):
            # a row with any printed year is not a hidden row; its cells are judged per year (open until filled)
            for c in cells:
                if c["display"] == HIDDEN_ROW:
                    c["display"] = OPEN
                    c["hide_class"] = ""


def work_type(r: dict[str, Any]) -> str:
    """The work an OPEN cell needs: combined_split (printed combined, split from notes), gap_fill (an evidenced reason
    or a gap inside a row that must carry a value), proof (value served or candidate, not proven), blank, held. Pure."""
    cls, code = r["class"], r["reason_code"]
    if cls == "HELD":
        return "held"
    if cls == "BLANK":
        return "blank"
    if cls == "REASON":
        return "combined_split" if code in {COMBINED, *COMBINED_CLASSES} else "gap_fill"
    return "proof"  # UNCHECKED, DISAGREE


HIDDEN_ROW_COLUMNS = [
    "rank",
    "ticker",
    "company_id",
    "data_point",
    "years",
    "reason_codes",
    "hide_class",
    "method",
    "latest_10k",
    "first_10k",
    "cell_evidence_accessions",
    "both_10ks_cited",
    "evidence",
]
HIDDEN_YEAR_COLUMNS = [
    "rank",
    "ticker",
    "company_id",
    "data_point",
    "fiscal_year",
    "period_end",
    "reason_code",
    "hide_class",
    "earliest_filing_date",
    "earliest_10k_presenting",
    "basis",
    "evidence",
    "evidence_accession",
]


def hidden_evidence(
    rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Evidence the certifier checks (method points 4 and 5): per hidden row the latest and first in-window 10-K and the
    accessions the cells cite; per hidden year the first filing and the earliest 10-K presenting it. 'method' is the
    stored evidence kind (locator source), so a row whose cells do not cite both 10-Ks is visible as
    both_10ks_cited = no and still needs the face-and-notes check. Pure."""
    groups: dict[tuple[Any, str], list[dict[str, Any]]] = defaultdict(list)
    years_out = []
    for r in rows:
        if r["display"] == HIDDEN_ROW:
            groups[(r["company_id"], r["data_point"])].append(r)
        elif r["display"] == HIDDEN_YEAR:
            years_out.append(
                {
                    **{k: r[k] for k in HIDDEN_YEAR_COLUMNS if k in r},
                    "earliest_filing_date": r.get("_earliest_filing") or "",
                    "earliest_10k_presenting": r.get("_first_presenting") or "",
                    "basis": "before_first_periodic_filing"
                    if r.get("_before_first_filing")
                    else "reported_only_combined"
                    if r.get("_only_combined")
                    else "absent_in_own_filing"
                    if r.get("_absent_own")
                    else "first_report_comparative_only"
                    if r.get("_comparative_only")
                    else "evidenced_no_period_reason",
                    "evidence": r.get("evidence") or "",
                    "evidence_accession": r.get("_oc_accession")
                    or r.get("_first_presenting")
                    or "",
                }
            )
    rows_out = []
    for cells in groups.values():
        c0 = cells[0]
        accs = sorted({c["accession"] for c in cells if c.get("accession")})
        latest, first = c0.get("_latest_10k", ""), c0.get("_first_10k", "")
        rows_out.append(
            {
                **{k: c0[k] for k in ("rank", "ticker", "company_id", "data_point")},
                "years": ",".join(str(c["fiscal_year"]) for c in cells),
                "reason_codes": ",".join(sorted({c["reason_code"] for c in cells})),
                "hide_class": ",".join(
                    sorted({c.get("hide_class") or "" for c in cells} - {""})
                ),
                "method": ",".join(
                    sorted({c.get("locator_source") or "none" for c in cells})
                ),
                "latest_10k": latest,
                "first_10k": first,
                "cell_evidence_accessions": ",".join(accs),
                "evidence": " || ".join(
                    sorted({c["evidence"] for c in cells if c.get("evidence")})
                ),
                "both_10ks_cited": "yes"
                if latest and first and latest in accs and first in accs
                else "no",
            }
        )
    return sorted(rows_out, key=lambda r: (r["rank"], r["data_point"])), sorted(
        years_out, key=lambda r: (r["rank"], r["data_point"], r["fiscal_year"])
    )


def pageless_counts(rows: list[dict[str, Any]]) -> dict[int, dict[str, int]]:
    """Per company: PROVEN / REASON / DERIVED cells with no r_page, and the component parts whose page is blank
    (the page gate, Ritwik 2026-11-14). Pure."""
    out: dict[int, dict[str, int]] = defaultdict(
        lambda: dict.fromkeys(PAGELESS_COLS, 0)
    )
    for r in rows:
        o = out[r["company_id"]]
        if r["class"] in ("PROVEN", "REASON", "DERIVED") and not r.get("r_page"):
            o["pageless_" + r["class"].lower()] += 1
        o["parts_blank"] += r.get("_parts_blank", 0) or 0
    return out


PAGELESS_COLS = [
    "pageless_proven",
    "pageless_reason",
    "pageless_derived",
    "parts_blank",
]


def summarize(
    rows: list[dict[str, Any]],
    companies: list[Company],
    notes: dict[int, str],
    as_of: str,
) -> list[dict[str, Any]]:
    if any("display" not in r for r in rows):
        apply_display(rows)
    by: dict[int, dict[str, int]] = defaultdict(lambda: dict.fromkeys(CLASSES, 0))
    for r in rows:
        by[r["company_id"]][r["class"]] += 1
    pl = pageless_counts(rows)
    disp: dict[int, dict[str, int]] = defaultdict(
        lambda: {
            SHOWN_VALUE: 0,
            OPEN: 0,
            HIDDEN_ROW: 0,
            HIDDEN_YEAR: 0,
            "rows": 0,
            "pageless_shown": 0,
            "parts_blank_shown": 0,
        }
    )
    seen_rows: set[tuple[Any, Any]] = set()
    for r in rows:
        d = disp[r["company_id"]]
        d[r["display"]] += 1
        key = (r["company_id"], r.get("data_point"))
        if r["display"] == HIDDEN_ROW and key not in seen_rows:
            seen_rows.add(key)
            d["rows"] += 1
        if r["display"] == SHOWN_VALUE:
            d["pageless_shown"] += 0 if r.get("r_page") and r.get("accession") else 1
            d["parts_blank_shown"] += r.get("_parts_blank", 0) or 0
    out = []
    for c in companies:
        t = by.get(c.company_id, dict.fromkeys(CLASSES, 0))
        total = sum(t.values())
        dd = disp.get(c.company_id)
        shown = (dd[SHOWN_VALUE] + dd[OPEN]) if dd else 0
        out.append(
            {
                "rank": c.rank,
                "ticker": c.ticker,
                "company_id": c.company_id,
                "cells": total,
                **t,
                **pl.get(c.company_id, dict.fromkeys(PAGELESS_COLS, 0)),
                "shown_cells": shown,
                "shown_values": dd[SHOWN_VALUE] if dd else 0,
                "open_shown": dd[OPEN] if dd else 0,
                "hidden_rows": dd["rows"] if dd else 0,
                "hidden_years": dd[HIDDEN_YEAR] if dd else 0,
                "pageless_shown": dd["pageless_shown"] if dd else 0,
                "parts_blank_shown": dd["parts_blank_shown"] if dd else 0,
                "pct_shown_values": f"{100 * dd[SHOWN_VALUE] / shown:.1f}"
                if dd and shown
                else "",
                "display_certified": "yes"
                if dd
                and shown
                and dd[OPEN] == 0
                and dd["pageless_shown"] == 0
                and dd["parts_blank_shown"] == 0
                else "no",
                "pct_proven_plus_reason": f"{100 * (t['PROVEN'] + t['REASON'] + t['DERIVED']) / total:.1f}"
                if total
                else "",
                "note": notes.get(c.company_id, ""),
                "as_of": as_of,
            }
        )
    return out


def write_csv(path: Path, rows: list[dict[str, Any]], columns: list[str]) -> None:
    with path.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=columns, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


OPEN_COLUMNS = [
    "work",
    "rank",
    "ticker",
    "company_id",
    "data_point",
    "fiscal_year",
    "period_end",
    "class",
    "reason_code",
    "reason",
    "shown_value",
    "accession",
    "r_page",
    "parts",
]
SUMMARY_DISPLAY_COLS = [
    "shown_cells",
    "shown_values",
    "open_shown",
    "hidden_rows",
    "hidden_years",
    "pct_shown_values",
    "pageless_shown",
    "parts_blank_shown",
    "display_certified",
]


def open_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """One row per OPEN cell with its work type: the work queue. Pure."""
    return [
        {**r, "work": work_type(r)}
        for r in sorted(
            (r for r in rows if r["display"] == OPEN),
            key=lambda r: (r["rank"], r["data_point"], r["fiscal_year"]),
        )
    ]


def main(out_dir: Path, shards: Path, reads_dir: Path, n: int = 100) -> int:
    from scrooner_pipeline.db.connection import get_connection

    companies = load_top(shards, n)
    now = datetime.now(timezone.utc)
    with get_connection() as conn:
        conn.execute("set transaction read only")
        conn.execute("set statement_timeout = '10min'")
        rows, notes = build_rows(
            conn,
            companies,
            reads_dir,
            now.date(),
            load_lookup(),
            load_fix_pages(reads_dir),
        )
    as_of = now.strftime("%Y-%m-%dT%H:%MZ")
    summary = summarize(rows, companies, notes, as_of)
    write_csv(out_dir / "top100-coverage.csv", rows, CSV_COLUMNS)
    scols = [
        "rank",
        "ticker",
        "company_id",
        "cells",
        *CLASSES,
        *PAGELESS_COLS,
        "pct_proven_plus_reason",
        *SUMMARY_DISPLAY_COLS,
        "note",
        "as_of",
    ]
    write_csv(out_dir / "top100-coverage-summary.csv", summary, scols)
    oq = open_rows(rows)
    stamp = now.strftime("%Y%m%dT%H%MZ")
    write_csv(out_dir / f"top100-open-shown-cells-{stamp}.csv", oq, OPEN_COLUMNS)
    hr, hy = hidden_evidence(rows)
    write_csv(out_dir / f"top100-hidden-rows-{stamp}.csv", hr, HIDDEN_ROW_COLUMNS)
    write_csv(out_dir / f"top100-hidden-years-{stamp}.csv", hy, HIDDEN_YEAR_COLUMNS)
    wt = {k: sum(1 for r in oq if r["work"] == k) for k in WORK_TYPES}
    print(
        f"display: shown values {sum(r['shown_values'] for r in summary)} of "
        f"{sum(r['shown_cells'] for r in summary)} shown cells; open {len(oq)} {wt}; "
        f"hidden rows {sum(r['hidden_rows'] for r in summary)}, hidden years {sum(r['hidden_years'] for r in summary)}; "
        f"certified {sum(1 for r in summary if r['display_certified'] == 'yes')}"
    )
    tot = {k: sum(r[k] for r in summary) for k in CLASSES}
    pc = sum(1 for r in rows if r.get("parts"))
    pb = sum(r.get("_parts_blank", 0) for r in rows)
    pg = {k: sum(r[k] for r in summary) for k in PAGELESS_COLS}
    print(
        f"top100 coverage as of {as_of}: {len(rows)} cells {tot}; component_sum cells {pc}, part pages blank {pb}"
    )
    print(f"page gate (cells with no r_page): {pg}")
    for r in summary:
        if any(r[k] for k in PAGELESS_COLS):
            print(
                "  "
                + r["ticker"]
                + " "
                + " ".join(f"{k}={r[k]}" for k in PAGELESS_COLS)
            )
    return 0
