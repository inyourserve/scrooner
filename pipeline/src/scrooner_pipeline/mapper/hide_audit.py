"""Structural hide audit for the top-100 display (Dhairya brief 2026-11-21, engineering handoff step 1).

A hide must be proven by the company's own filings in the FSN store, not by the absence of a proof. Two rules re-check
the hides that top100_coverage.apply_display sets; each one that fails is reopened (display OPEN), citing the filing:

  (1) RULE_YEAR  a year hidden as pre-filing is wrong when ANY 10-K or 10-Q of the company (fsn.filing / fsn.value
                 ddate) prints a column for the period end, in its own or a comparative column (BA 2026-11-21). A
                 10-Q's balance sheet carries the prior fiscal year end; that presents an instant year.
  (2) RULE_ROW   a row hidden as never reported (structural_not_presented) is wrong when any filing of the company in
                 the window has a face or note line whose tag the resolver or the tag library maps to the data point,
                 or whose printed label is a learned label of the data point (MO other income, net: the FY2015 10-K
                 prints "Other income, net", OtherNonoperatingIncomeExpense).
  (3) a period that only a registration statement (Form 10, S-1) presents is out of V1 scope: it stays hidden, and
      its reason code is no_10k_presents_period (the legacy no_public_filing_for_period is renamed on display).

Pure helpers are unit-tested; the DB reads are `read_presenting_columns` and `load_line_hits` (read-only).
"""

from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

from scrooner_pipeline.certification.display_cert import HIDE_FAMILY
from scrooner_pipeline.mapper import comparative_guard as cg
from scrooner_pipeline.mapper import resolver_files as rf

QUARTERLY_FORMS = ("10-Q", "10-Q/A", "10-QT", "10-QT/A")
# every form whose columns can present a period: annual reports (10-K, 20-F, 40-F families) and quarterly reports
PRESENTING_FORMS = cg.ANNUAL_FORMS + QUARTERLY_FORMS
RULE_YEAR = "hidden_year_period_presented"
RULE_ROW = "hidden_row_line_reported"
NO_10K_REASON = cg.NO_10K_REASON
LEGACY_NO_FILING = cg.NO_FILING_REASON
LIBRARY_DIR = Path(__file__).resolve().parents[4] / "data-team" / "tags" / "library"
# a learned label counts only when this many companies print it for the data point (one company's label can be its own)
MIN_LABEL_COMPANIES = 2
# a one-word label ("other") names no line: WFC/SCHW/MS print "Other" under unrelated extension tags
MIN_LABEL_WORDS = 2
_ROLE_RE = re.compile(r"^([a-z0-9_]+):primary#\d+$")
_NODE_RE = re.compile(r"(?:^|[\s+(;,])([A-Za-z][\w\-]*)=")
# only a resolver row that maps the data point to ONE printed line names a tag of it; a single node of a
# component_sum or derived_not_printed row is an INPUT (GrossProfit for derived opex, net sales for gross profit)
_MAPPED = "mapped"


def stmts_for(instant: bool) -> tuple[str, ...]:
    """The face statements whose column presents a fiscal period: the balance sheet for an instant, the flow
    statements for a duration (an equity roll-forward's opening balance is not a balance-sheet column)."""
    return ("BS",) if instant else ("IS", "CF", "CI", "EQ")


def read_presenting_columns(
    conn: Any, company_ids: list[int]
) -> dict[int, list[cg.Column]]:
    """company id -> every statement column its stored 10-K / 10-Q / 20-F / 40-F filings print (read-only)."""
    return cg.read_columns(conn, company_ids, forms=PRESENTING_FORMS)


def presenting_column(
    columns: Iterable[cg.Column], period_end: date, instant: bool
) -> cg.Column | None:
    """The first column (by accession) of any 10-K / 10-Q that presents the period, else None. Pure."""
    hit = cg.presenting(columns, period_end, instant, stmts_for(instant))
    return hit[0] if hit else None


def norm_label(s: str | None) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


@dataclass(frozen=True)
class LineHit:
    """A line of one filing that reports the data point: by its tag or by its printed label."""

    accession: str
    form: str
    stmt: str
    report: int
    line: int
    tag: str
    plabel: str
    basis: str  # "tag" or "label"
    custom: bool = False  # fsn.tag.custom: a filer extension tag (a label match counts only on one of these)

    def cite(self) -> str:
        return (
            f"{self.form} {self.accession} R{self.report}.htm line {self.line} ({self.stmt}) "
            f"prints {self.plabel or '(no label)'!r} [{self.tag}] (by {self.basis})"
        )


def library_primary_tags(rows: Iterable[dict[str, str]]) -> dict[str, set[str]]:
    """data point -> elements the tag library ranks as a PRIMARY tag of it (role_kind `<dp>:primary#N`; a part or
    component tag is not the data point). Pure."""
    out: dict[str, set[str]] = defaultdict(set)
    for r in rows:
        for role in (r.get("role_kind") or "").split(";"):
            m = _ROLE_RE.match(role.strip())
            if m:
                out[m.group(1)].add(r["element"])
    return out


def node_tags(nodes: str | None) -> list[str]:
    """The tags a resolver `nodes` cell names (`Tag=value [R5.htm:21] | why: ...`). Pure."""
    head = (nodes or "").split(" | why")[0]
    return _NODE_RE.findall(head)


def resolver_direct_tags(
    rows: Iterable[dict[str, str]],
) -> dict[tuple[str, str], set[str]]:
    """(ticker, data point) -> the tag of every single-line `mapped` resolver row of that company. A mapping is a
    company's own judgment (one filer's only "other" line is its debt-extinguishment loss), so it never carries over
    to another company. Pure."""
    by_co: dict[tuple[str, str], set[str]] = defaultdict(set)
    for r in rows:
        if r.get("decision") != _MAPPED:
            continue
        tags = node_tags(r.get("nodes"))
        if len(tags) == 1:
            by_co[(r["ticker"], r["data_point"])].add(tags[0])
    return dict(by_co)


def library_known_tags(rows: Iterable[dict[str, str]]) -> dict[str, set[str]]:
    """element -> every data point the tag library associates it with (data_point column and roles). Pure."""
    out: dict[str, set[str]] = defaultdict(set)
    for r in rows:
        dps = {d.strip() for d in (r.get("data_point") or "").split(";") if d.strip()}
        for role in (r.get("role_kind") or "").split(";"):
            if ":" in role:
                dps.add(role.split(":")[0].strip())
        if dps:
            out[r["element"]] |= dps
    return dict(out)


def learned_dp_labels(
    rows: Iterable[dict[str, str]], primary: dict[str, set[str]]
) -> dict[str, set[str]]:
    """data point -> normalized labels learned from proven cells of at least MIN_LABEL_COMPANIES companies whose
    most-used element is a primary tag of the data point ("loss on extinguishment of debt" is a component of other
    income, its element is not primary: excluded). Pure."""
    out: dict[str, set[str]] = defaultdict(set)
    for r in rows:
        try:
            n = int(r.get("companies") or 0)
        except ValueError:
            continue
        top = (r.get("elements") or "").split(";")[0].strip().split(" ")[0]
        if n >= MIN_LABEL_COMPANIES and top in primary.get(r["data_point"], set()):
            lab = norm_label(r.get("label"))
            if len(lab.split()) >= MIN_LABEL_WORDS:
                out[r["data_point"]].add(lab)
    return out


@dataclass
class LineVocab:
    """What reports a data point: tags (any company), tags per (ticker, dp), labels, and the tag library's
    element -> data points (a label match on a tag the library gives to ANOTHER data point is that one's line)."""

    tags: dict[str, set[str]]
    company_tags: dict[tuple[str, str], set[str]]
    labels: dict[str, set[str]]
    known: dict[str, set[str]] = field(default_factory=dict)

    def label_allowed(self, tag: str, dp: str) -> bool:
        k = self.known.get(tag)
        return not k or dp in k

    def all_tags(self) -> list[str]:
        s = {t for v in self.tags.values() for t in v}
        s |= {t for v in self.company_tags.values() for t in v}
        return sorted(s)

    def all_labels(self) -> list[str]:
        return sorted({x for v in self.labels.values() for x in v})


def build_vocab(
    library_dir: Path = LIBRARY_DIR, resolver_dir: Path | None = None
) -> LineVocab:
    """The vocabulary from HIDE_FAMILY, the tag library (library.csv primary roles, learned_labels.csv) and the
    current resolver output. A missing file contributes nothing."""
    lib = library_dir / "library.csv"
    if (
        library_dir == LIBRARY_DIR
    ):  # the repo library: library.csv lives in Storage (storage-manifest.csv), not git
        from scrooner_pipeline.common import repo_archive

        lib = repo_archive.resolve("data-team/tags/library/library.csv") or lib
    primary: dict[str, set[str]] = defaultdict(set)
    known: dict[str, set[str]] = {}
    if lib.exists():
        with lib.open(newline="") as fh:
            lib_rows = list(csv.DictReader(fh))
        primary.update(library_primary_tags(lib_rows))
        known = library_known_tags(lib_rows)
    tags: dict[str, set[str]] = defaultdict(set)
    for dp, ts in primary.items():
        tags[dp] |= ts
    for dp, ts in HIDE_FAMILY.items():
        tags[dp] |= set(ts)
    company_tags: dict[tuple[str, str], set[str]] = {}
    rdir = resolver_dir or rf.LINE_MAP_DIR
    if rf.resolver_files(rdir):
        with rf.open_rows(rdir) as rows:
            company_tags = resolver_direct_tags(rows)
    labels: dict[str, set[str]] = {}
    ll = library_dir / "learned_labels.csv"
    if ll.exists():
        with ll.open(newline="") as fh:
            labels = learned_dp_labels(csv.DictReader(fh), tags)
    return LineVocab(dict(tags), dict(company_tags), labels, known)


_LINE_SQL = """
select f.company_id, f.accession, f.form, l.stmt, l.report, l.line, t.tag, coalesce(l.plabel, ''), t.custom
from fsn.filing f
join fsn.line l on l.filing_id = f.id
join fsn.tag t on t.id = l.tag_id
where f.company_id = any(%s) and f.form = any(%s) and f.period >= %s
  and (t.tag = any(%s)
       or btrim(regexp_replace(lower(coalesce(l.plabel, '')), '[^a-z0-9]+', ' ', 'g')) = any(%s))
  and exists (select 1 from fsn.value v where v.filing_id = f.id and v.tag_id = l.tag_id and v.dim_id = 0
              and v.coreg = '' and v.value is not null)
"""


def load_line_hits(
    conn: Any,
    company_ids: list[int],
    vocab: LineVocab,
    since: date,
    chunk: int = 10,
) -> list[tuple[int, LineHit]]:
    """(company id, line) for every line of a 10-K / 10-Q (period on or after `since`) whose tag or printed label is
    in the vocabulary and that carries an undimensioned value in that filing. Read-only."""
    out: list[tuple[int, LineHit]] = []
    tags, labels = vocab.all_tags(), vocab.all_labels()
    for i in range(0, len(company_ids), chunk):
        ids = company_ids[i : i + chunk]
        for cid, acc, form, stmt, rep, ln, tag, plabel, custom in conn.execute(
            _LINE_SQL, (ids, list(PRESENTING_FORMS), since, tags, labels)
        ).fetchall():
            out.append(
                (
                    cid,
                    LineHit(
                        acc,
                        form,
                        stmt,
                        int(rep),
                        int(ln),
                        tag,
                        plabel,
                        "",
                        bool(custom),
                    ),
                )
            )
    return out


def hits_by_row(
    lines: Iterable[tuple[int, LineHit]],
    vocab: LineVocab,
    ticker_of: dict[int, str],
    wanted: Iterable[tuple[int, str]],
    instant_dps: set[str] | frozenset[str] = frozenset(),
) -> dict[tuple[int, str], list[LineHit]]:
    """(company id, data point) -> the lines that report it, tag matches first, then by accession. A line counts only
    on a statement of the data point's kind (the balance sheet for an instant, any other statement for a duration:
    a balance-sheet "Accounts payable" line is not the cash-flow change). Pure."""
    want = set(wanted)
    dps_of: dict[int, set[str]] = defaultdict(set)
    for cid, dp in want:
        dps_of[cid].add(dp)
    out: dict[tuple[int, str], list[LineHit]] = defaultdict(list)
    for cid, h in lines:
        lab = norm_label(h.plabel)
        for dp in dps_of.get(cid, ()):
            if (h.stmt == "BS") != (dp in instant_dps):
                continue
            if h.tag in vocab.tags.get(dp, ()) or h.tag in vocab.company_tags.get(
                (ticker_of.get(cid, ""), dp), ()
            ):
                basis = "tag"
            elif (
                h.custom
                and lab
                and lab in vocab.labels.get(dp, ())
                and vocab.label_allowed(h.tag, dp)
            ):
                basis = "label"
            else:
                continue
            out[(cid, dp)].append(
                LineHit(
                    h.accession,
                    h.form,
                    h.stmt,
                    h.report,
                    h.line,
                    h.tag,
                    h.plabel,
                    basis,
                    h.custom,
                )
            )
    return {
        k: sorted(v, key=lambda h: (h.basis != "tag", h.accession, h.report, h.line))
        for k, v in out.items()
    }


def attach_period_presence(
    rows: list[dict[str, Any]],
    columns: dict[int, list[cg.Column]],
    instant_dps: set[str] | frozenset[str],
) -> None:
    """Set `_period_presenting` (the first 10-K / 10-Q column that prints the cell's period, or None). Pure."""
    for r in rows:
        r["_period_presenting"] = presenting_column(
            columns.get(r["company_id"], ()),
            date.fromisoformat(r["period_end"]),
            r["data_point"] in instant_dps,
        )


def attach_line_hits(
    rows: list[dict[str, Any]], hits: dict[tuple[int, str], list[LineHit]]
) -> None:
    """Set `_line_hits` (the lines of any filing that report the cell's data point). Pure."""
    for r in rows:
        r["_line_hits"] = hits.get((r["company_id"], r["data_point"]), [])


def reopen(r: dict[str, Any], rule: str, prior: str, acc: str, evidence: str) -> None:
    """Mark a hidden cell OPEN under an audit rule, keeping the hide it replaced. Pure, in place."""
    r["_reopen_rule"], r["_reopen_prior"] = rule, prior
    r["_reopen_accession"] = acc
    r["evidence"] = evidence
    r["display"], r["hide_class"] = "OPEN", ""


def year_evidence(col: cg.Column) -> str:
    return (
        f"{RULE_YEAR}: {col.form} {col.accession} prints a {col.stmt} column for the period"
        + (f" on R{col.report}.htm" if col.report else "")
        + f" (ddate {col.ddate.isoformat()}); a presented year is never hidden as pre-filing"
    )


def row_evidence(hits: list[LineHit]) -> str:
    more = f" (+{len(hits) - 1} more lines)" if len(hits) > 1 else ""
    return f"{RULE_ROW}: {hits[0].cite()}{more}; a reported line is never hidden as never reported"


def no_10k_evidence(r: dict[str, Any]) -> str:
    first = r.get("_earliest_filing") or "unknown"
    return (
        f"{NO_10K_REASON}: no 10-K or 10-Q in the FSN store presents {r['period_end']} (first periodic filing "
        f"{first}); a period shown only by a registration statement is out of V1 scope"
    )


AUDIT_COLUMNS = [
    "rule",
    "rank",
    "ticker",
    "company_id",
    "data_point",
    "fiscal_year",
    "period_end",
    "prior_hide_class",
    "class",
    "reason_code",
    "evidence_accession",
    "evidence",
]


def audit_rows(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """One row per cell an audit rule reopened. Pure."""
    out = [
        {
            "rule": r["_reopen_rule"],
            **{k: r.get(k, "") for k in AUDIT_COLUMNS[1:7]},
            "prior_hide_class": r.get("_reopen_prior") or "",
            "class": r.get("class", ""),
            "reason_code": r.get("reason_code", ""),
            "evidence_accession": r.get("_reopen_accession") or "",
            "evidence": r.get("evidence") or "",
        }
        for r in rows
        if r.get("_reopen_rule")
    ]
    return sorted(
        out, key=lambda x: (x["rule"], x["rank"], x["data_point"], x["fiscal_year"])
    )


def audit_summary(audit: list[dict[str, Any]]) -> dict[str, Any]:
    """Cells reopened per rule (and prior hide class) and per company. Pure."""
    per_rule = Counter((a["rule"], a["prior_hide_class"]) for a in audit)
    per_co = Counter((a["ticker"], a["rule"]) for a in audit)
    return {
        "total": len(audit),
        "per_rule": {f"{k[0]}:{k[1]}": v for k, v in sorted(per_rule.items())},
        "per_company": {f"{k[0]}:{k[1]}": v for k, v in sorted(per_co.items())},
    }
