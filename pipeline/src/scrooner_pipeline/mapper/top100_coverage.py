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

from scrooner_pipeline.common import instance_facts
from scrooner_pipeline.mapper.note_report_lookup import load_lookup
from scrooner_pipeline.proof.prove import DETECTOR_VERSION

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
]


def candidates(dp: str) -> list[str]:
    return SPECIAL_CANDIDATES.get(dp, [f"{dp}_resolved", dp])


STATEMENT_STMTS = ("IS", "BS", "CF", "CI", "EQ")


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
        """The report that carries most of the statement's lines in THIS filing (a parenthetical has few)."""
        best = [
            (n, -r) for (a, s, r), n in self.stmt_n.items() if a == acc and s == stmt
        ]
        return -max(best)[1] if best else None


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
    return {acc for p, acc in filings if -_DAY_TOL <= (p - period_end).days <= span}


NO_FILING = (
    "no_public_filing_for_period"  # = structural_loader.NO_FILING_REASON (tested)
)
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
) -> tuple[str, str | None]:
    """A REASON stays REASON only when its locator accession presents the cell's own period; else UNCHECKED.
    no_public_filing_for_period has no filing of its own period by definition: it stays REASON only when the company's
    earliest 10-K/10-Q/20-F in core.filing (`earliest_filing`) was filed after the period end; otherwise UNCHECKED."""
    if cls == "REASON" and code == NO_FILING:
        if earliest_filing is not None and earliest_filing > period_end:
            return cls, code
        return "UNCHECKED", OWN_UNVERIFIED
    if cls == "REASON" and acc not in eligible_filings(filings, period_end, instant):
        return "UNCHECKED", OWN_UNVERIFIED
    return cls, code


def _annual_filings(conn: Any, ids: list[int]) -> dict[int, list[tuple[date, str]]]:
    out: dict[int, list[tuple[date, str]]] = defaultdict(list)
    for cid, period, acc in conn.execute(
        """select company_id, period, accession from fsn.filing
           where company_id = any(%s) and period is not null
             and form in ('10-K', '10-K/A', '10-KT', '10-KT/A', '20-F', '20-F/A', '40-F', '40-F/A')""",
        (ids,),
    ).fetchall():
        out[cid].append((period, acc))
    return out


def _earliest_filings(conn: Any, ids: list[int]) -> dict[int, date]:
    """company id -> filing date of its earliest periodic filing (10-K/10-Q/20-F/40-F and amendments) in core.filing."""
    return {
        cid: d
        for cid, d in conn.execute(
            "select company_id, min(filing_date) from core.filing "
            "where company_id = any(%s) and form = any(%s) group by company_id",
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
    statement, else (a parenthetical or off-face share count of an instant data point) the balance sheet."""
    for st in [stmt] + (["BS"] if instant else []):
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
    return end <= max(p for p, _ in filings) + timedelta(days=_DAY_TOL)


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
    """The verdict of each cell key: its newest analytics.cell_proof row written by the CURRENT detector version.
    A row of an older detector is history, never the verdict (a held cell is not re-proved, so a pre-R13
    restated_copies_disagree row outlived its rule for 48 MSFT cells)."""
    proofs: dict[tuple[int, str, date, date], tuple] = {}
    for row in conn.execute(
        """select distinct on (company_id, data_point_name, period_start, period_end)
                  company_id, data_point_name, period_start, period_end, verdict, reason_code, reason_text,
                  shown_value, shown_tag, shown_accession, position_source, fsn_stmt, fsn_line, checks
           from analytics.cell_proof
           where company_id = any(%s) and data_point_name = any(%s) and basis = 'latest'
             and detector_version = %s
             and period_grain in ('FY', 'I') and period_end >= %s
           order by company_id, data_point_name, period_start, period_end, proved_at desc, id desc""",
        (ids, names, DETECTOR_VERSION, date(FIRST_FY - 1, 1, 1)),
    ).fetchall():
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
    cited = {v[0] for v in stmt_pages.values()}
    cited |= {p[5] for p in proofs.values() if p[5]}
    cited |= {ev[6][0] for evs in tagmap.values() for ev in evs if ev[6][0]}
    shown_tags = {
        t.strip() for p in proofs.values() if p[4] for t in p[4].split(",") if t.strip()
    }
    idx = _locator_index(conn, cited, shown_tags)
    earliest = _earliest_filings(conn, ids)

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
                if lsrc in (
                    "none",
                    "note_fact_report_not_stored",
                    "evidence_acc_no_page",
                ) and not (acc and page):
                    own_acc, own_page = stmt_pages.get(
                        (c.company_id, e, dstmt), ("", "")
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
                    }
                )
    resolve_derived(rows)
    note = {
        c.company_id: (
            "TEMPLATE_UNAVAILABLE"
            + (f" (excluded: {c.excluded})" if c.excluded else " (no docmap)")
        )
        for c in companies
        if not templates[c.company_id]
    }
    return rows, note


def resolve_derived(rows: list[dict[str, Any]]) -> None:
    """In place. A served cell of family derived_not_printed is DERIVED only when every input data point of the same
    company and fiscal year is PROVEN and all inputs were proven against the same filing (the same shown_accession);
    the row then lists the derivation as `dp=value@accession`. Any other case is UNCHECKED derived_inputs_unproven."""
    by = {(r["company_id"], r["data_point"], r["fiscal_year"]): r for r in rows}
    for r in rows:
        if r.get("_family") != DERIVED_FAMILY or r["class"] in ("PROVEN", "DISAGREE"):
            continue
        inputs = [
            by.get((r["company_id"], dp, r["fiscal_year"]))
            for dp in DERIVED_INPUTS.get(r["data_point"], ())
        ]
        ok = (
            bool(inputs)
            and all(
                i is not None and i["class"] == "PROVEN" and i["_shown_acc"]
                for i in inputs
            )
            and len({i["_shown_acc"] for i in inputs if i}) == 1
        )
        if inputs:
            r["evidence"] = "; ".join(
                f"{i['data_point']}={i['shown_value']}@{i['_shown_acc'] or '?'}"
                for i in inputs
                if i is not None
            )
        first = next((i for i in inputs if i is not None), None)
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


def summarize(
    rows: list[dict[str, Any]],
    companies: list[Company],
    notes: dict[int, str],
    as_of: str,
) -> list[dict[str, Any]]:
    by: dict[int, dict[str, int]] = defaultdict(lambda: dict.fromkeys(CLASSES, 0))
    for r in rows:
        by[r["company_id"]][r["class"]] += 1
    out = []
    for c in companies:
        t = by.get(c.company_id, dict.fromkeys(CLASSES, 0))
        total = sum(t.values())
        out.append(
            {
                "rank": c.rank,
                "ticker": c.ticker,
                "company_id": c.company_id,
                "cells": total,
                **t,
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
        "pct_proven_plus_reason",
        "note",
        "as_of",
    ]
    write_csv(out_dir / "top100-coverage-summary.csv", summary, scols)
    tot = {k: sum(r[k] for r in summary) for k in CLASSES}
    pc = sum(1 for r in rows if r.get("parts"))
    pb = sum(r.get("_parts_blank", 0) for r in rows)
    print(
        f"top100 coverage as of {as_of}: {len(rows)} cells {tot}; component_sum cells {pc}, part pages blank {pb}"
    )
    return 0
