"""Direct serving of the Tag Expert's structural resolver rows (ruling 2026-11-14, Dhairya).

Why: structural-load turns resolver rows into company_tag_map rows with tag eras and the mapper then selects facts by
tag x era through the candidate/vintage loaders. A tag those loaders cannot reach (a NOTE fact such as MSFT
InvestmentIncomeNet, a custom tag off the face) finds no fact, and the cell is blank (era_unmapped) although the
resolver already found it in a named filing. This module serves the resolver's claim DIRECTLY:

  per (company, data point, period) the claim is the resolver row of the filing chosen by authority v2
  (common/authority: face_column_eligible, then latest_eligible: the latest eligible filing presenting that column);
  the value is read from the stored facts of exactly that accession and column (core.fact first, else fsn.value:
  undimensioned, no coreg, iprx 0), summed with the claim's part signs; the resolver CSV value is only a cross-check
  (a part that disagrees with its node value, or a total that disagrees with the CSV value, rejects the claim and
  the cell stays as the tag-era path built it). Lineage = the resolver row (accession, column, nodes, calc_check).

Why the CSV is read at serve time and not stored in company_tag_map: the table has no value column and no DDL is
allowed; its eras are the selection that failed. The committed CSV is the evidence (the same pattern as
common/instance_facts). Hand fix rows (company_tag_map.docmap_fix@1) still win their cells. Decisions served:
mapped, component_sum, and the two ruled derived_not_printed pairs (shares issued - treasury, CI total - NCI; same
filing and column, DERIVED_DIRECT); gross profit and total liabilities stay with the derived path (derived_cells). A filing whose own calc check FAILs is
quarantined (structural_loader.quarantined). Pure parts are unit-testable; the DB reads are two indexed queries.
"""

from __future__ import annotations

import os
from collections import defaultdict
from dataclasses import replace
from datetime import date
from decimal import Decimal
from functools import lru_cache
from pathlib import Path
from typing import Any

import psycopg

from scrooner_pipeline.common.authority import face_column_eligible, latest_eligible
from scrooner_pipeline.common import filer_xbrl_errors as fxe
from scrooner_pipeline.common.per_share_guard import (
    FILER_SCALE_REASON,
    at_or_above_floor,
    filer_scale_error,
)
from scrooner_pipeline.mapper.per_share_scale import other_columns
from scrooner_pipeline.common import fsn_dropped_facts as fsn_dropped
from scrooner_pipeline.common import member_facts
from scrooner_pipeline.common.fsn_dates import (
    era_holds,
    fsn_end_matches,
    nearest_month_ends,
)
from scrooner_pipeline.common.polarity import apply_polarity, flip_note
from scrooner_pipeline.mapper import comparative_guard as cg
from scrooner_pipeline.mapper import docmap_loader as dl
from scrooner_pipeline.mapper import reason_guard as rg
from scrooner_pipeline.mapper import structural_loader as sl

FIX_RULE_ID = "company_tag_map.docmap_fix@1"
ENV_PATH = "SCROONER_STRUCTURAL_RESOLVER"
ENV_OFF = "SCROONER_STRUCTURAL_DIRECT"  # "off" disables the path
LINE_MAP_DIR = Path(__file__).resolve().parents[4] / "data-team" / "tags" / "line_map"
SERVED = ("mapped", "component_sum")
DERIVED = "derived_not_printed"
CASH = "cash_and_equivalents"  # ruling 2026-11-14 (Dhairya): the BS face 'cash and cash equivalents' total line only


def resolver_path() -> Path | None:
    env = os.environ.get(ENV_PATH)
    if env:
        return Path(env)
    files = sorted(LINE_MAP_DIR.glob("resolver-all110-*.csv"))
    return files[-1] if files else None


@lru_cache(maxsize=4)
def _claims_by_cik(path: str) -> dict[str, tuple[sl.Claim, ...]]:
    claims, _rejects, _counts = sl.read_claims(Path(path))
    out: dict[str, list[sl.Claim]] = defaultdict(list)
    for c in claims:
        if derived_claim(
            c
        ):  # the loader's not_presented statement, with the parts the derivation needs
            c = replace(c, decision=DERIVED, parts=c.derived_parts, locs=c.derived_locs)
        if c.decision in (*SERVED, DERIVED) and c.cik:
            out[c.cik].append(c)
    return {k: tuple(v) for k, v in out.items()}


def derived_claim(c: sl.Claim) -> bool:
    """A derived_not_printed resolver row of a data point served directly (sl.DERIVED_DIRECT) that carries its flag."""
    spec = sl.DERIVED_DIRECT.get(c.data_point)
    return (
        c.decision == "not_presented"
        and bool(c.derived_parts)
        and spec is not None
        and spec[0] in c.flags
    )


def derived_problem(c: sl.Claim) -> str | None:
    """Why a derived row is not servable, or None. Exactly two parts of one filing and column: the plus tag of the
    data point's pair first, the minus tag second, each with its resolver node value and printed page. Pure."""
    spec = sl.DERIVED_DIRECT.get(c.data_point)
    if spec is None or spec[0] not in c.flags:
        return f"{c.data_point}: no derivation ruled for this data point"
    _flag, plus, minus = spec
    if len(c.parts) != 2:
        return f"derived row with {len(c.parts)} parts (exactly 2 are ruled)"
    (s0, _t0, g0), (s1, _t1, g1) = c.parts
    if s0 != 1 or s1 != -1 or g0 not in plus or g1 not in minus:
        return f"derived parts {g0}, {g1} are not the ruled pair {sorted(plus)} minus {sorted(minus)}"
    if len(c.node_values) != 2 or not all(c.node_values):
        return "derived row without a node value for each part"
    if len(c.locs) != 2 or not all(rp for rp, _ln in c.locs):
        return "derived row without a printed R page for each part"
    return None


def derived_value(c: sl.Claim, vals: list[Decimal]) -> tuple[Decimal | None, str]:
    """(value, evidence) of a derived claim from its two stored part values (plus part first), or (None, why). The
    evidence is the signed parts, tag=value@accession#R-page joined by ';' (the coverage export's parts format);
    the accession is the claim's own filing, the only one the parts were read from. Pure."""
    why = derived_problem(c)
    if why:
        return None, why
    if len(vals) != 2:
        return None, "derived row needs two stored part values"
    if c.data_point == "shares_outstanding" and not vals[0] > vals[1] >= 0:
        return (
            None,
            "issued shares must exceed treasury shares, which must not be negative",
        )
    ev = ";".join(
        f"{'-' if g < 0 else ''}{p[2]}={v}@{c.accession}#R{c.locs[i][0]}"
        for i, (g, p, v) in enumerate(zip((1, -1), c.parts, vals))
    )
    return vals[0] - vals[1], ev


def enabled() -> bool:
    return os.environ.get(ENV_OFF, "on").lower() != "off"


def _period_hits(
    periods: dict[int, tuple[date, date, str]], end: date, grain: str
) -> list[int]:
    """Every core.period that can stand for the claim's column: instants (grain I) or about-a-year durations (FY)
    whose end the FSN date (rounded to a month end) stands for (common/fsn_dates)."""
    want = "instant" if grain == "I" else "duration"
    return [
        pid
        for pid, (start, e, ptype) in periods.items()
        if ptype == want
        and fsn_end_matches(end, e)
        and (want == "instant" or 330 <= (e - start).days <= 400)
    ]


def _period_id(
    periods: dict[int, tuple[date, date, str]],
    end: date,
    grain: str,
    por_hints: frozenset[date] = frozenset(),
) -> tuple[int, date] | None:
    """The unique core.period (id, true end) of the claim's column. The resolver's period_end is the FSN date,
    rounded to a month end (a 52/53-week year ending 2015-12-26 is 2015-12-31 there), so several periods can match:
    the real year end and stray instants a few days around it (subsequent-event dates, 2018-02-02 vs 2018-02-03).
    Chosen by evidence in order: the exact end; then the period_of_report of a filing the claim is read from
    (por_hints); else ambiguous (None here: direct_cells then tries the stored facts, see _by_stored_facts)."""
    hits = _period_hits(periods, end, grain)
    if len(hits) > 1:
        exact = [pid for pid in hits if periods[pid][1] == end]
        hits = exact if len(exact) == 1 else hits
    if len(hits) > 1 and por_hints:
        by_por = [pid for pid in hits if periods[pid][1] in por_hints]
        hits = by_por if len(by_por) == 1 else hits
    return (hits[0], periods[hits[0]][1]) if len(hits) == 1 else None


def _by_stored_facts(
    periods: dict[int, tuple[date, date, str]],
    hits: list[int],
    claims: list[sl.Claim],
    core_pids: set[tuple[str, str, int]],
) -> tuple[int, date] | None:
    """Last evidence for an ambiguous column: exactly one candidate period holds a stored core.fact of a claim part
    in a claim's own accession (a stray period, e.g. a start one day off with a handful of facts, carries none of
    the filing's face facts). Keyed by period id, so two periods with the SAME end are told apart too."""
    keep = [
        pid
        for pid in hits
        if any(
            (c.accession, tag, pid) in core_pids
            for c in claims
            for _s, _t, tag in c.parts
        )
    ]
    return (keep[0], periods[keep[0]][1]) if len(keep) == 1 else None


def _core_period_hits(
    conn: psycopg.Connection,
    company_id: int,
    accessions: set[str],
    tags: set[str],
    pids: set[int],
) -> set[tuple[str, str, int]]:
    """(accession, tag, period_id) of the stored non-derived core.facts of the pinned filings on the given periods."""
    if not (accessions and tags and pids):
        return set()
    with conn.cursor() as cur:
        cur.execute(
            """select distinct fl.accession_number, c.tag, f.period_id
               from core.fact f
               join core.concept c on c.id = f.concept_id
               join core.filing fl on fl.id = f.filing_id
               where f.company_id = %s and f.period_id = any(%s) and fl.accession_number = any(%s)
                 and c.tag = any(%s) and not f.is_derived""",
            (company_id, sorted(pids), sorted(accessions), sorted(tags)),
        )
        return {(a, t, p) for a, t, p in cur.fetchall()}


def pick_claim(
    claims: list[sl.Claim],
    meta: dict[str, tuple[str | None, date | None, str, date | None]],
    end: date,
    ptype: str,
) -> sl.Claim | None:
    """Authority v2 across the claims of one cell: only claims whose filing prints the column as a face column
    (face_column_eligible) compete, the latest filed wins (ties to the lower accession). meta: accession ->
    (filing key, filed, form, period_of_report). Unknown filing: not eligible (no evidence it prints the column)."""
    elig: dict[str, date | None] = {}
    for c in claims:
        m = meta.get(c.accession)
        if m is None:
            continue
        if face_column_eligible(m[2], m[3], end, ptype):
            elig[c.accession] = m[1]
    best = latest_eligible(elig)
    if best is None:
        return None
    return next(c for c in claims if c.accession == best)


def _fix_covers(rows, concept_id: int, end: date) -> bool:
    return any(
        sl.hand_fix_wins(r.rule_id, r.serve_note)
        and r.decision != "excluded"
        and concept_id in (r.canonical_concept_id, r.parent_concept_id)
        and era_holds(r.era_from, r.era_to, end)
        for r in rows
    )


# a map row that says the company's filing prints this line as part of a combined line, or that the concept is not in
# the template: a resolver claim must not override it (JPM accounts receivable is 'Accrued interest and accounts
# receivable', 11 cells were served with no claim at all, 2026-11-14)
NO_SERVE_CLASSES = frozenset({"line_presented_combined", "combined"})


def map_forbids(rows, concept_id: int, end: date) -> str | None:
    """The reason a covering company_tag_map row forbids serving the concept at `end`, or None. Forbidden: a
    not_in_template / combined row (reason_class line_presented_combined or combined, or decision combined) that no
    value-bearing claim row (concept / component) of the same concept covers. Pure."""
    covering = [
        r
        for r in rows
        if concept_id in (r.canonical_concept_id, r.parent_concept_id)
        and era_holds(r.era_from, r.era_to, end)
    ]
    if any(r.decision in ("concept", "component") and r.tag for r in covering):
        return None
    for r in covering:
        if r.decision == "combined" or (
            r.decision == "not_in_template"
            and (r.reason_class or "") in NO_SERVE_CLASSES
        ):
            return f"map row {r.decision}/{r.reason_class or '-'} covers this period: the line is a combined line, not this concept"
    return None


STRUCTURAL_RULE_ID = sl.RULE_ID
PRINTED_ZERO = "printed_zero"
NO_STORED_FACT = "no stored fact for the part in that filing and column"


def printed_zero_ok(claim: sl.Claim, why: str, i: int = 0) -> bool:
    """Ruling 2026-11-14 (Dhairya): a line printed on the face with a dash or a zero is served as 0 with no fact id,
    the resolver's R page and line being the evidence. For a `mapped` claim flagged printed_zero whose value and node
    are exactly 0. Ruling 2026-11-16 (Dhairya): the same for a part of a `component_sum` (a dash inside the sum,
    NVDA FY2019 ConvertibleDebtCurrent): part `i`'s node is exactly 0 and printed on an R page (never a NOTE part).
    Both only when the filing stores no fact for the part (a stored fact is read as any other part). Pure."""
    if why != NO_STORED_FACT:
        return False
    try:
        if claim.decision == "component_sum":
            rp = claim.locs[i][0] if i < len(claim.locs) else None
            return (
                i < len(claim.node_values)
                and claim.node_values[i] != ""
                and Decimal(claim.node_values[i]) == 0
                and rp is not None
                and claim.stmts[i] != "NOTE"
            )
        if claim.decision != "mapped" or PRINTED_ZERO not in {
            f.strip() for f in claim.flags.split(";")
        }:
            return False
        return Decimal(claim.value) == 0 and all(
            Decimal(v) == 0 for v in claim.node_values if v
        )
    except (ArithmeticError, ValueError):
        return False


STATED_ZERO = sl.STATED_ZERO
TEXT_STATED = sl.TEXT_STATED


def stated_zero_claim_problem(claim: sl.Claim) -> str | None:
    """Ruling 2026-11-16 (Dhairya): a zero the filing STATES for the period is served as 0 with no fact id. The claim
    must carry the exact quote, the locator, the accession and a quote_period equal to its period. Pure."""
    return sl.stated_zero_problem(
        {
            "quote": claim.quote,
            "locator": claim.locator,
            "value": claim.value,
            "quote_period": claim.quote_period,
        },
        claim.period_end,
        claim.accession,
        sl.stated_kind(claim.decision, claim.flags) or STATED_ZERO,
    )


def comparative_refusals(
    conn: psycopg.Connection,
    company_id: int,
    rows,
    periods: dict[int, tuple[date, date, str]],
    concept_info: dict[int, tuple[str, str]],
) -> list[dict]:
    """Comparative-column guard (Ritwik 2026-11-15): a covering no-filing reason (no_public_filing_for_period /
    no_10k_presents_period) is refused for every period an accepted annual filing of the company prints a column
    for. Same shape as refuted_map_reasons entries; the cell stays open for the resolver. Read-only."""
    nf = [
        r
        for r in rows
        if (r.reason_class or "") in cg.NO_FILING_CODES
        and r.canonical_concept_id in concept_info
    ]
    if not nf:
        return []
    cols = cg.read_columns(conn, [company_id]).get(company_id, [])
    out = []
    for r in nf:
        cid = r.canonical_concept_id
        instant = concept_info[cid][1] == "balance_sheet"
        for pid, (_s, end, ptype) in periods.items():
            if (ptype == "instant") != instant or not era_holds(
                r.era_from, r.era_to, end
            ):
                continue
            hit = cg.presenting(cols, end, instant)
            if hit:
                out.append(
                    {
                        "canonical_concept_id": cid,
                        "period_id": pid,
                        "concept": concept_info[cid][0],
                        "period_end": end.isoformat(),
                        "accession": hit[0].accession,
                        "tag": "",
                        "value": "",
                        "decision": "comparative_presented",
                    }
                )
    return out


def refuted_map_reasons(
    conn: psycopg.Connection,
    company_id: int,
    cik: str | None,
    rows,
    periods: dict[int, tuple[date, date, str]],
    concept_info: dict[int, tuple[str, str]],
    path: Path | None = None,
) -> list[dict]:
    """False-reason guard on the serving side (reason_guard): the covering not_presented / combined map rows whose
    cited filing's own column holds evidence of the line, as {canonical_concept_id, period_id, ...}. Those reasons
    are not served (their blanks are dropped, they never forbid a value): the cell stays open. Read-only."""
    comparative = comparative_refusals(conn, company_id, rows, periods, concept_info)
    cand = []
    for r in rows:
        kind = rg.kind_of(r.decision, r.reason_class)
        cid = r.canonical_concept_id
        if kind and r.evidence_adsh and cid in concept_info:
            cand.append((r, kind, cid))
    if not cand:
        return comparative
    names = {concept_info[cid][0] for _r, _k, cid in cand}
    ctags = rg.concept_tags(conn, names)
    path = path or resolver_path()
    own: dict[tuple[str, str], set[str]] = {}
    if enabled() and path is not None and cik:
        own = sl.claim_tags(list(_claims_by_cik(str(path)).get(cik.zfill(10), ())))
    todo = []  # (row, kind, cid, pid, end, instant, tags)
    for r, kind, cid in cand:
        name = rg.base_name(concept_info[cid][0])
        instant = concept_info[cid][1] == "balance_sheet"
        tags = ctags.get(name, set()) | own.get((cik or "", name), set())
        for pid, (_s, end, ptype) in periods.items():
            if (ptype == "instant") == instant and era_holds(r.era_from, r.era_to, end):
                todo.append((r, kind, cid, pid, end, instant, tags))
    facts = rg.read_facts(
        conn, company_id, {(t[0].evidence_adsh, g) for t in todo for g in t[6]}
    )
    ruled = rg.ruled_true_reasons()
    out = []
    for r, kind, cid, pid, end, instant, tags in todo:
        ev = rg.evidence_for(
            kind,
            end,
            instant,
            tags,
            f"{r.reason or ''} {r.evidence_plabel or ''}",
            {g: facts.get((r.evidence_adsh, g), []) for g in tags},
            rg.ruled_tags(
                ruled,
                r.evidence_adsh,
                rg.base_name(concept_info[cid][0]),
                {x.year for x in nearest_month_ends(end) | {end}},
                kind,
                tags,
            ),
        )
        if ev:
            out.append(
                {
                    "canonical_concept_id": cid,
                    "period_id": pid,
                    "concept": concept_info[cid][0],
                    "period_end": end.isoformat(),
                    "accession": r.evidence_adsh,
                    "tag": ev[0]["tag"],
                    "value": str(ev[0]["value"]),
                    "decision": r.decision,
                }
            )
    return comparative + out


def unclaimed(rows, cells: list[dict], periods, concept_info) -> list[dict]:
    """Claim sync: every cell served from the resolver must have a covering structural@1 value claim row in the map
    (company_tag_map.structural@1, decision concept/component). The cells that have none, as {concept, period_end}:
    structural-load did not write their claim (reject or conflict in its CSVs), so the serve and the map diverge. Pure."""
    out = []
    for c in cells:
        if c.get("value_source") in (STATED_ZERO, TEXT_STATED):
            continue  # carries its own quote and locator in the serve note; no map claim row by design
        cid = c["canonical_concept_id"]
        end = periods[c["period_id"]][1]
        if not any(
            r.rule_id == STRUCTURAL_RULE_ID
            and r.decision in ("concept", "component")
            and cid in (r.canonical_concept_id, r.parent_concept_id)
            and era_holds(r.era_from, r.era_to, end)
            for r in rows
        ):
            out.append({"concept": concept_info[cid][0], "period_end": end.isoformat()})
    return out


def _cash_components(
    conn: psycopg.Connection, accessions: set[str]
) -> set[tuple[str, str]]:
    """(accession, tag) of every tag that the filing's own calc tree makes a COMPONENT of a cash total printed on the
    balance-sheet face (AXP 2023: CashAndDueFromBanks 7,118 under 'Total cash and cash equivalents' 46,596). Such a
    node is a part of the face total, not the total: a cash_and_equivalents claim on it is not served."""
    if not accessions:
        return set()
    with conn.cursor() as cur:
        cur.execute(
            """select distinct f.accession, c.tag
               from fsn.calc_arc a
               join fsn.filing f on f.id = a.filing_id
               join fsn.tag p on p.id = a.parent_tag_id
               join fsn.tag c on c.id = a.child_tag_id
               where f.accession = any(%s) and p.tag like 'Cash%%' and p.tag <> c.tag
                 and exists (select 1 from fsn.line l
                             where l.filing_id = a.filing_id and l.stmt = 'BS' and l.tag_id = a.parent_tag_id)""",
            (sorted(accessions),),
        )
        return {(acc, tag) for acc, tag in cur.fetchall()}


def _stored_values(
    conn: psycopg.Connection,
    company_id: int,
    accessions: set[str],
    tags: set[str],
    ends: set[date],
):
    """(accession, tag, end) -> {'core': {value: ids}, 'fsn': {value: ids}} for exactly the pinned filings."""
    out: dict[tuple[str, str, date], dict[str, dict[Decimal, set[int]]]] = defaultdict(
        lambda: {
            "core": defaultdict(set),
            "fsn": defaultdict(set),
            "auth": defaultdict(set),
        }
    )
    if not accessions or not tags:
        return out
    with conn.cursor() as cur:
        cur.execute(
            """select fl.accession_number, c.tag, p.end_date, f.value, f.id, f.is_authoritative
               from core.fact f
               join core.concept c on c.id = f.concept_id
               join core.period p on p.id = f.period_id
               join core.filing fl on fl.id = f.filing_id
               where f.company_id = %s and fl.accession_number = any(%s) and c.tag = any(%s)
                 and p.end_date = any(%s) and not f.is_derived""",
            (company_id, sorted(accessions), sorted(tags), sorted(ends)),
        )
        for acc, tag, end, value, fid, auth in cur.fetchall():
            out[(acc, tag, end)]["core"][Decimal(value)].add(fid)
            if auth:
                out[(acc, tag, end)]["auth"][Decimal(value)].add(fid)
        cur.execute(
            """select f.accession, t.tag, v.ddate, v.qtrs, v.value, v.id
               from fsn.value v
               join fsn.tag t on t.id = v.tag_id
               join fsn.filing f on f.id = v.filing_id
               where v.company_id = %s and f.accession = any(%s) and t.tag = any(%s)
                 and v.dim_id = 0 and v.coreg = '' and v.iprx = 0 and v.value is not null""",
            (company_id, sorted(accessions), sorted(tags)),
        )
        fsn_rows = cur.fetchall()
    for acc, tag, ddate, qtrs, value, vid in fsn_rows:
        for end in ends:
            if fsn_end_matches(ddate, end) and (
                qtrs == 0 or 3 <= qtrs <= 5
            ):  # instant, or a yearly column
                out[(acc, tag, end)]["fsn"][Decimal(value)].add(vid)
    return out


def _fix_fit(
    fix: fxe.Correction, got: tuple[Decimal, str, set[int]] | str
) -> str | None:
    """Why a filer XBRL correction does not fit the part's stored facts, or None. The CSV cross-check stays: a correcting
    row needs the stored value to be its xbrl_value (or already the printed one); a supplying row needs no stored fact
    for the column at all (a different stored value there means the CSV is stale). Pure."""
    if isinstance(got, str):
        if fix.supplies and got.startswith("no stored fact"):
            return None
        return f"filer_xbrl_errors row does not fit the stored facts: {got}"
    v = got[0]
    if fix.supplies:
        return (
            None
            if v == fix.printed_value
            else (f"filer_xbrl_errors supplies {fix.printed_value} but {v} is stored")
        )
    if v in (fix.xbrl_value, fix.printed_value):
        return None
    return f"stored {v} is neither the CSV xbrl_value {fix.xbrl_value} nor the printed {fix.printed_value}"


def _part_value(
    got: dict[str, dict[Decimal, set[int]]], want: Decimal | None
) -> tuple[Decimal, str, set[int]] | str:
    """One stored value for a part, its source and ids; or the reason there is none. Two stored values (units: EPS in
    USD and USD/shares, a restated copy) resolve only by evidence: exactly one authoritative value, else the one the
    resolver node printed (the node value picks among stored values, it is never a value itself)."""
    core, fsn = got["core"], got["fsn"]
    if len(core) > 1:
        auth = got["auth"]
        if len(auth) == 1:
            core = dict(auth)
        elif want is not None and want in core:
            core = {want: core[want]}
    if len(core) == 1:
        ((v, ids),) = core.items()
        if fsn and v not in fsn:
            return "core.fact and fsn.value print different values for the part"
        return v, "sec_api", ids
    if len(core) > 1:
        return "two stored values for the part in that filing (units)"
    if len(fsn) > 1 and want is not None and want in fsn:
        fsn = {want: fsn[want]}
    if len(fsn) == 1:
        ((v, ids),) = fsn.items()
        return v, "fsn_xbrl", ids
    if len(fsn) > 1:
        return "two fsn values for the part in that filing"
    return "no stored fact for the part in that filing and column"


def direct_cells(
    conn: psycopg.Connection,
    company_id: int,
    cik: str | None,
    rows,
    periods: dict[int, tuple[date, date, str]],
    concept_info: dict[int, tuple[str, str]],
    path: Path | None = None,
) -> tuple[list[dict], dict[str, Any]]:
    """Cells served straight from the resolver, and counters (rejects carry the reason)."""
    stats: dict[str, Any] = {
        "claims": 0,
        "served": 0,
        "rejected": [],
        "fix_won": 0,
        "fix_won_cells": [],
        "no_claim_row": [],
    }
    stats["refuted_reasons"] = refuted_map_reasons(
        conn, company_id, cik, rows, periods, concept_info, path
    )
    refuted_keys = {
        (x["canonical_concept_id"], x["period_id"]) for x in stats["refuted_reasons"]
    }
    path = path or resolver_path()
    if not enabled() or path is None or not cik:
        return [], stats
    mine = _claims_by_cik(str(path)).get(cik.zfill(10), ())
    if not mine:
        return [], stats
    ids = {n: i for i, (n, _s) in concept_info.items()}
    groups: dict[tuple[str, date, str], list[sl.Claim]] = defaultdict(list)
    for c in mine:
        name = dl.served_concept(c.data_point, set(ids))
        if name in ids:
            groups[(name, c.period_end, c.grain)].append(c)
    stats["claims"] = len(groups)
    accessions = {c.accession for cs in groups.values() for c in cs}
    with conn.cursor() as cur:
        cur.execute(
            "select accession_number, id, filing_date, form, period_of_report from core.filing "
            "where accession_number = any(%s)",
            (sorted(accessions),),
        )
        meta = {a: (i, fd, form, por) for a, i, fd, form, por in cur.fetchall()}
        missing = sorted(accessions - set(meta))
        if missing:
            cur.execute(
                "select accession, id, accepted, form, period from fsn.filing where accession = any(%s)",
                (missing,),
            )
            for a, i, acc, form, per in cur.fetchall():
                meta[a] = (-i, acc.date() if acc else None, form, per)
    tags = {
        tag
        for cs in groups.values()
        for c in cs
        for _s, _t, tag in c.parts
        if not member_facts.is_member_part(tag)
    }
    member_rows = member_facts.read_member_rows(
        conn,
        company_id,
        accessions,
        {b for cs in groups.values() for c in cs for b in sl.member_bases(c.parts)},
    )

    def por_hints(cs: list[sl.Claim]) -> frozenset[date]:
        return frozenset(
            m[3] for c in cs if (m := meta.get(c.accession)) and isinstance(m[3], date)
        )

    col = {
        k: _period_id(periods, k[1], k[2], por_hints(cs)) for k, cs in groups.items()
    }
    ambiguous = {
        k: _period_hits(periods, k[1], k[2]) for k, v in col.items() if v is None
    }
    amb_pids = {p for hs in ambiguous.values() for p in hs}
    core_pids = _core_period_hits(conn, company_id, accessions, tags, amb_pids)
    for k, hs in ambiguous.items():
        if len(hs) > 1:
            col[k] = _by_stored_facts(periods, hs, groups[k], core_pids)
    stored = _stored_values(
        conn,
        company_id,
        accessions,
        tags,
        {v[1] for v in col.values() if v},
    )
    cash_parts = _cash_components(
        conn,
        {c.accession for k, cs in groups.items() if k[0] == CASH for c in cs},
    )
    cells: list[dict] = []
    fixes = fxe.load()
    dropped_facts = fsn_dropped.load()
    for (name, end, grain), cs in sorted(groups.items(), key=lambda kv: repr(kv[0])):
        cid = ids[name]

        def reject(why: str, name: str = name, end: date = end) -> None:
            stats["rejected"].append(
                {"concept": name, "period_end": end.isoformat(), "why": why}
            )

        located = col[(name, end, grain)]
        if located is None:
            cand = sorted(
                periods[p][1].isoformat() for p in _period_hits(periods, end, grain)
            )
            reject(
                "no unique core.period for the claim's column: "
                + (f"candidate ends {cand}" if cand else "no matching period")
            )
            continue
        pid, te = located
        if _fix_covers(rows, cid, te):
            stats["fix_won"] += 1
            stats["fix_won_cells"].append(
                {"concept": name, "period_end": te.isoformat()}
            )
            continue
        forbid = None if (cid, pid) in refuted_keys else map_forbids(rows, cid, te)
        if forbid:
            reject(forbid)
            continue
        live = [c for c in cs if sl.quarantined(c) is None]
        if not live:
            reject("every claim's filing is quarantined (its own calc check failed)")
            continue
        picked = pick_claim(live, meta, te, periods[pid][2])
        if picked is None:
            reject("no filing that prints the column as a face column")
            continue
        c = picked
        if c.decision == DERIVED:
            why = derived_problem(c)
            if why:
                reject(why)
                continue
        if name == CASH and any(
            (c.accession, tag) in cash_parts for _s, _t, tag in c.parts
        ):
            reject(
                "cash node is a component of the BS face total cash line, not the total"
            )
            continue
        if c.decision == "component_sum" and periods[pid][2] == "instant":
            if sl.instant_sum_refused_for(c, name, concept_info[cid][1]):
                reject("instant component sum refused (only total_debt)")
                continue
        kind = sl.stated_kind(c.decision, c.flags)
        if kind:
            why = stated_zero_claim_problem(c)
            if why:
                reject(why)
                continue
            cells.append(
                {
                    "canonical_concept_id": cid,
                    "period_id": pid,
                    "value": Decimal(c.value) if kind == TEXT_STATED else Decimal(0),
                    "value_source": kind,
                    "source_fact_ids": [],
                    "source_value_ids": [],
                    "serve_note": (
                        f"structural resolver direct: {c.accession} column {end.isoformat()}; {kind}: "
                        f"the filing states the value in its text, served with no fact id; "
                        f'locator: {c.locator}; quote: "{c.quote}"'
                    ),
                    "_scaled": False,
                    "_filing_id": meta[c.accession][0],
                    "_accession": c.accession,
                    "_filed": meta[c.accession][1],
                    "_dcml_keys": [],
                    "_structural_direct": True,
                }
            )
            continue
        parts: list[tuple[int, str, Decimal, str, set[int]]] = []
        used_fixes: list[fxe.Correction] = []
        used_dropped: list[fsn_dropped.DroppedFact] = []
        member_cites: dict[str, str] = {}
        bad = None
        for i, (sign, _tax, tag) in enumerate(c.parts):
            want = (
                Decimal(c.node_values[i])
                if i < len(c.node_values) and c.node_values[i]
                else None
            )
            if member_facts.is_member_part(tag):
                spec = member_facts.split_member_part(tag)
                hit = member_facts.resolve_member_part(
                    member_rows.get((c.accession, spec.base), []),
                    spec,
                    te,
                    want,
                    member_facts.axis_hint_of(c.flags),
                )
                if isinstance(hit, str):
                    bad = f"{tag}: {hit}"
                    break
                v, src, got_ids = hit.value, "fsn_xbrl", set(hit.ids)
                if hit.dropped:  # the filing prints it, the FSN ingest dropped it: the CSV row is the source
                    src = fsn_dropped.VALUE_SOURCE
                    used_dropped.extend(hit.dropped)
                tag = hit.part_tag
                rp, ln = c.locs[i] if i < len(c.locs) else (None, None)
                if rp:
                    member_cites[tag] = f"R{rp}" + (f":{ln}" if ln else "")
            else:
                got = _part_value(stored[(c.accession, tag, te)], want)
                fix = fxe.pick(
                    fixes.get((c.accession, tag, 0 if grain == "I" else 4), ()),
                    None if isinstance(got, str) else got[0],
                )
                if fix is not None:
                    why = _fix_fit(fix, got)
                    if why:
                        bad = f"{tag}: {why}"
                        break
                    parts.append(
                        (sign, tag, fix.printed_value, fxe.VALUE_SOURCE, set())
                    )
                    used_fixes.append(fix)
                    if i < len(c.node_values) and c.node_values[i]:
                        if Decimal(c.node_values[i]) != fix.printed_value:
                            bad = f"{tag}: printed {fix.printed_value} differs from the resolver node {c.node_values[i]}"
                            break
                    continue
                drop = dropped_facts.get(
                    (c.accession, tag, 0 if grain == "I" else 4, "")
                )
                if drop is not None and (
                    isinstance(got, str) and got.startswith("no stored fact")
                ):  # an undimensioned fact the filing prints and the FSN ingest dropped
                    parts.append(
                        (sign, tag, drop.value, fsn_dropped.VALUE_SOURCE, set())
                    )
                    used_dropped.append(drop)
                    continue
                if isinstance(got, str) and printed_zero_ok(c, got, i):
                    parts.append((sign, tag, Decimal(0), PRINTED_ZERO, set()))
                    continue
                if isinstance(got, str):
                    bad = f"{tag}: {got}"
                    break
                v, src, got_ids = got
            if i < len(c.node_values) and c.node_values[i]:
                if Decimal(c.node_values[i]) != v:
                    bad = f"{tag}: stored {v} differs from the resolver node {c.node_values[i]}"
                    break
            parts.append((sign, tag, v, src, got_ids))
        if bad:
            reject(bad)
            continue
        if c.decision == DERIVED:
            served, dev = derived_value(c, [p[2] for p in parts])
            flipped = False
            if served is None:
                reject(dev)
                continue
        elif c.decision == "mapped":
            served, flipped = apply_polarity(name, parts[0][2])
        else:
            signs = tuple(p[0] for p in parts)
            if c.value:  # the resolver's nodes carry no weights: the signs under which the stored parts sum to it
                sg, why = sl.solve_signs(c, [{p[2]} for p in parts])
                if sg is None:
                    reject(f"component sum not verified: {why}")
                    continue
                signs = sg
            served = Decimal(sum(g * p[2] for g, p in zip(signs, parts)))
            flipped = False
        if c.value and Decimal(c.value) != served:
            reject(f"stored value {served} differs from the resolver value {c.value}")
            continue
        if at_or_above_floor(name, served):
            # filer-scale hold (common/per_share_guard.py): a rare cell, so its other columns are read here (one batched
            # read of its (accession, tag) pairs); a filer_xbrl_errors correction already replaced the part value above
            _oth = other_columns(conn, company_id, {(c.accession, p[1]) for p in parts})
            if filer_scale_error(name, served, [o for vs in _oth.values() for o in vs]):
                reject(
                    f"{FILER_SCALE_REASON}: {served} is 10^3 or 10^6 times the filing's other columns of the tag"
                )
                continue
        fix_src = any(p[3] == fxe.VALUE_SOURCE for p in parts)
        drop_src = any(p[3] == fsn_dropped.VALUE_SOURCE for p in parts)
        zero_src = any(p[3] == PRINTED_ZERO for p in parts)
        fsn_src = any(p[3] == "fsn_xbrl" for p in parts)
        core_ids = sorted({i for p in parts if p[3] == "sec_api" for i in p[4]})
        vids = sorted({i for p in parts if p[3] == "fsn_xbrl" for i in p[4]})
        note = (
            f"structural resolver direct: {c.accession} column {end.isoformat()} "
            + "; ".join(
                f"{t}={v}" + (f" [{member_cites[t]}]" if t in member_cites else "")
                for _s, t, v, _x, _f in parts
            )
            + (f"; filing checks: {c.checks}" if c.checks else "")
        )
        if flipped:
            note += "; " + flip_note(parts[0][2])
        for fx in used_fixes:
            note += "; " + fx.note()
        for df in used_dropped:
            note += "; " + df.note()
        if zero_src:
            zi = next(i for i, p in enumerate(parts) if p[3] == PRINTED_ZERO)
            rp, ln = c.locs[zi] if zi < len(c.locs) else (None, None)
            note += f"; printed_zero: the line is printed with a dash or 0 (R{rp}:{ln}), served as 0 with no fact id"
        fid = meta[c.accession][0]
        if c.decision == DERIVED:
            cells.append(
                {
                    "canonical_concept_id": cid,
                    "period_id": pid,
                    "value": served,
                    "value_source": DERIVED,
                    "source_fact_ids": [],
                    "source_value_ids": [],
                    "serve_note": f"{DERIVED}: {dev} (printed in the same filing and column; the filing prints no {c.data_point} line)"
                    + (f"; filing checks: {c.checks}" if c.checks else ""),
                    "_scaled": False,
                    "_derived_not_printed": True,
                    "_filing_id": fid,
                    "_accession": c.accession,
                    "_filed": meta[c.accession][1],
                    "_dcml_keys": [],
                    "_structural_direct": True,
                }
            )
            continue
        cells.append(
            {
                "canonical_concept_id": cid,
                "period_id": pid,
                "value": served,
                "value_source": PRINTED_ZERO
                if zero_src
                else (
                    fxe.VALUE_SOURCE
                    if fix_src
                    else (
                        fsn_dropped.VALUE_SOURCE
                        if drop_src
                        else ("fsn_xbrl" if fsn_src else "sec_api")
                    )
                ),
                "source_fact_ids": [] if fsn_src else core_ids,
                "source_value_ids": vids if fsn_src else [],
                "serve_note": note,
                "_scaled": False,
                "_filing_id": fid,
                "_accession": c.accession,
                "_filed": meta[c.accession][1],
                "_dcml_keys": [],
                "_structural_direct": True,
            }
        )
    stats["served"] = len(cells)
    stats["no_claim_row"] = unclaimed(rows, cells, periods, concept_info)
    return cells, stats


def apply_direct(
    conn: psycopg.Connection,
    cells: list[dict],
    stats: dict,
    direct: list[dict],
    refuted: list[dict] | None = None,
) -> int:
    """Splice direct cells into the tag-era cells, and drop the held/blank entries of a replaced key (the resolver
    found the value). Authority v2 still rules between the two paths: a resolver row speaks for its own filing, so a
    tag-era cell read from a STRICTLY LATER eligible filing (the restated column: ABT 2016 operating income) stays;
    from the same or an earlier filing, or no cell at all, the resolver cell wins. Kept cells that differ are listed
    in stats['structural_direct_kept_later_filing']. Returns how many cells were replaced or added."""
    have = {(c["canonical_concept_id"], c["period_id"]): c for c in cells}
    accs = sorted({c["_accession"] for c in have.values() if c.get("_accession")})
    filed: dict[str, date | None] = {}
    if accs:
        with conn.cursor() as cur:
            cur.execute(
                "select accession_number, filing_date from core.filing where accession_number = any(%s)",
                (accs,),
            )
            filed = dict(cur.fetchall())
    use: list[dict] = []
    kept: list[dict] = []
    for d in direct:
        k = (d["canonical_concept_id"], d["period_id"])
        old = have.get(k)
        if old is not None and old.get("_accession"):
            of, nf = filed.get(old["_accession"]), d.get("_filed")
            if of and nf and of > nf:
                if old["value"] != d["value"]:
                    kept.append(
                        {
                            "key": k,
                            "kept": old["value"],
                            "direct": d["value"],
                            "kept_filing": old["_accession"],
                        }
                    )
                continue
        use.append(d)
    stats["structural_direct_kept_later_filing"] = kept
    keys = {(d["canonical_concept_id"], d["period_id"]) for d in use}
    cells[:] = [
        c for c in cells if (c["canonical_concept_id"], c["period_id"]) not in keys
    ] + use
    stats["held"] = [
        h
        for h in stats.get("held", [])
        if (h["canonical_concept_id"], h["period_id"]) not in keys
    ]
    gone = keys | {(x["canonical_concept_id"], x["period_id"]) for x in (refuted or [])}
    stats["blanks"] = [
        b
        for b in stats.get("blanks", [])
        if (b.get("canonical_concept_id"), b.get("period_id")) not in gone
    ]
    return len(use)
