"""Tag-map selection of canonical facts (migration 0122, founder order 2026-11-11:
"FSN for learning, SEC for mapping").

For a company with rows in analytics.company_tag_map, a canonical fact is built ONLY from the map:

  * decision 'concept': the tag IS the concept; the fact of that tag whose period END lies in
    [era_from, era_to] is the value.
  * decision 'component': the fact is a summand of parent_concept_id, added with its sign (+1/-1), Decimal.
  * every value-bearing row ('concept' and 'component') carries sign: the served value is sign x fact value.
  * decision 'excluded': never used.
  * statement scope: a row only serves a concept on that concept's statement (IS/BS/CF); the same tag on another
    statement (NetIncomeLoss on the cash-flow statement) never feeds net income. Rows on another statement are
    counted in stats["stmt_mismatch_rows"], never silently applied.
  * only core.fact rows with is_authoritative are read; per (tag, period) the LATEST filing wins (filing_date,
    then filing id); EPS facts that are derived (is_derived) are never used.
  * two different values for one (concept, period) from different tags/routes are a conflict: nothing is written
    for that cell (counted in stats["conflict_cells"]), never an arbitrary pick.
  * calc-tree safety (Ritwik, 2026-11-11), per filing: (1) a printed 'concept' fact for C beats the
    'component' rows for C; (2) components are summed only when C is not printed, from ONE filing, and every
    component is a direct calc child of the component rows' evidence_cal_parent in that filing's calc arcs
    (fsn.calc_arc); where C is printed in the same filing the components must tie to it (checks.tol_of) or the
    cell is HELD; (3) a component set in which one member is a calc ancestor of another is refused (HELD).
    Held cells are written nowhere and returned in stats["held"] with a reason code.
  * decision 'combined': one printed line spanning several concepts. It NEVER feeds a concept (even if
    canonical_concept_id is set). It is served as the company's own line in analytics.company_combined_line
    (printed label, sign x stored value); each spanned concept without a separately printed value in that period
    is marked not_in_template "shown as the company's combined line '<plabel>'".
  * sign means: multiply the value STORED in core.fact (the tag's own direction, not the printed sign) by it. The
    mapper never takes abs() and never flips a sign from a label; core.fact is non-dimensional by construction.
  * decision 'not_presented' / 'not_in_template' (tagless, concept-level): for each of the company's periods in the
    era (instant periods for a balance-sheet concept, FY or quarter durations otherwise) that has no value cell the
    result is a reasoned blank (stats["blanks"], written to analytics.cell_blank_reason by resolve()). A printed
    value for that concept and period wins; the clash is reported in stats["blank_conflicts"].
  * no concept_mapping, no company_tag_preference, no fallback is consulted for these companies.

Companies without rows are not touched by this module. The hook in mapper/resolve.py calls it only when rule
company_tag_map.select@1 is ON (SCROONER_RULES_ENABLED), so nothing changes until it is switched on.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from typing import Any

import psycopg
import structlog

from scrooner_pipeline.common.authority import (
    FaceIndex,
    face_column_eligible,
    load_face_indexes,
    latest_complete_filing,
)
from scrooner_pipeline.common.tag_aliases import with_aliases
from scrooner_pipeline.common.fsn_dates import era_holds, fsn_end_matches
from scrooner_pipeline.common.rule_flags import ON, rule_mode
from scrooner_pipeline.fsn_store.checks import tol_of
from scrooner_pipeline.proof.prove import DETECTOR_VERSION

logger = structlog.get_logger()

RULE_ID = "company_tag_map.select@1"
FAMILY = "company_tag_map"

# canonical_concept.statement -> FSN statement codes allowed to feed it. Per-share dividends are printed on
# the income or equity statement although the concept row says cash_flow (DPS-EQUITY-STATEMENT proposal).
STATEMENT_CODE = {"income_statement": "IS", "balance_sheet": "BS", "cash_flow": "CF"}
EXTRA_STMT = {
    # bank cash: where the BS splits cash, cash = the cash-flow statement's printed ending-cash line (a concept row)
    # catalog concepts filed under income_statement whose library rows sit on another face (found in the 18-company
    # plan: sbc and D&A are cash-flow lines, comprehensive income has its own statement)
    "sbc": {"CF", "EQ"},
    "depreciation_and_amortization": {"CF"},
    "depreciation_and_amortization_resolved": {"CF"},
    "amortization_of_intangibles": {"CF"},
    "comprehensive_income": {"CI"},
    "cash_and_equivalents": {"CF"},
    "cash_and_equivalents_resolved": {"CF"},
    "dividends_per_share": {"IS", "EQ"},
    "dividends_per_share_resolved": {"IS", "EQ"},
}
# EPS is never derived (founder standing rule): derived facts are not eligible for these concepts.
NEVER_DERIVED = {
    "basic_eps",
    "basic_eps_resolved",
    "diluted_eps",
    "diluted_eps_resolved",
}

_FAR = date.max


@dataclass(frozen=True)
class MapRow:
    taxonomy: str | None
    tag: str | None
    stmt: str
    decision: str
    canonical_concept_id: int | None
    parent_concept_id: int | None
    sign: int | None
    era_from: date
    era_to: date | None
    evidence_cal_parent: str | None = None
    reason: str | None = None
    rule_id: str | None = None
    components: tuple[str, ...] | None = None
    evidence_plabel: str | None = None
    serve_note: str | None = None
    map_id: int | None = None
    reason_class: str | None = None
    scale: Decimal = Decimal(1)
    decided_by: str | None = None
    evidence_adsh: str | None = None
    evidence_report: int | None = None


@dataclass(frozen=True)
class Fact:
    value: Decimal
    fact_id: int
    end: date
    derived: bool
    filing_id: int
    accession: str
    filed: date | None = None
    ambiguous: bool = False  # two distinct values (other units) for this tag and period in the latest filing
    # Value source (founder decision 2026-11-12): standard-taxonomy tags are read from SEC companyfacts (core.fact,
    # 'sec_api'); CUSTOM tags from the filing's own XBRL via the FSN store (fsn.value, 'fsn_xbrl': undimensioned,
    # coreg empty, iprx 0), accepted only when the tag sits on that filing's face (fsn.line). For an fsn_xbrl fact
    # fact_id is the fsn.value id and filing_id is NEGATIVE (-fsn.filing.id) so it never equals a core.filing id.
    source: str = "sec_api"
    on_face: bool = True
    # period_of_report of the filing the fact was printed in: the filing's OWN period decides which map row (tag era)
    # that filing speaks under (per-filing tag era, MSFT revenue). None = unknown (only the fact's period is judged).
    por: date | None = None


STANDARD_TAXONOMIES = {"us-gaap", "ifrs-full", "dei", "srt"}


def is_custom(taxonomy: str | None) -> bool:
    return taxonomy is not None and taxonomy not in STANDARD_TAXONOMIES


def enabled(environ=None) -> bool:
    return rule_mode(RULE_ID, environ) == ON


def load_tag_map_company_ids(
    conn: psycopg.Connection, company_ids: set[int]
) -> set[int]:
    """Subset of company_ids that have at least one company_tag_map row (one indexed query)."""
    if not company_ids:
        return set()
    with conn.cursor() as cur:
        cur.execute(
            "select distinct company_id from analytics.company_tag_map where company_id = any(%s)",
            (sorted(company_ids),),
        )
        return {r[0] for r in cur.fetchall()}


def _load_rows(conn: psycopg.Connection, company_id: int) -> list[MapRow]:
    with conn.cursor() as cur:
        cur.execute(
            "select count(*) from information_schema.columns where table_schema = 'analytics' "
            "and table_name = 'company_tag_map' and column_name = 'scale'"
        )
        scale_col = (
            "scale" if cur.fetchone()[0] else "1::numeric"
        )  # 0123 adds the column
        cur.execute(
            f"""
            select taxonomy, tag, stmt, decision, canonical_concept_id, parent_concept_id, sign,
                   era_from, era_to, evidence_cal_parent, reason, rule_id, components, evidence_plabel, serve_note, id, reason_class,
                   {scale_col} as scale, decided_by, evidence_adsh, evidence_report
            from analytics.company_tag_map where company_id = %s
            """,
            (company_id,),
        )
        return [
            MapRow(
                taxonomy=r[0],
                tag=r[1],
                stmt=r[2],
                decision=r[3],
                canonical_concept_id=r[4],
                parent_concept_id=r[5],
                sign=r[6],
                era_from=r[7],
                era_to=r[8],
                evidence_cal_parent=r[9],
                reason=r[10],
                rule_id=r[11],
                components=tuple(r[12]) if r[12] else None,
                evidence_plabel=r[13],
                serve_note=r[14],
                map_id=r[15],
                reason_class=r[16],
                scale=Decimal(r[17]),
                decided_by=r[18],
                evidence_adsh=r[19],
                evidence_report=r[20],
            )
            for r in cur.fetchall()
        ]


def _load_facts(
    conn: psycopg.Connection,
    company_id: int,
    tags: set[tuple[str | None, str | None]],
    face: FaceIndex | None = None,
):
    """(taxonomy, tag) -> period_id -> Fact of the latest authoritative filing. Authoritative only:
    is_authoritative=false is a hard filter."""
    out: dict[tuple[str | None, str | None], dict[int, Fact]] = defaultdict(dict)
    for key, by_period in _load_fact_vintages(
        conn, company_id, tags, latest_only=True, face=face
    ).items():
        for period_id, prints in by_period.items():
            out[key][period_id] = prints[0]
    if tags:
        _merge_predecessor_facts(conn, company_id, tags, out)
    return out


def _load_fact_vintages(
    conn: psycopg.Connection,
    company_id: int,
    tags: set[tuple[str | None, str | None]],
    latest_only: bool = False,
    face: FaceIndex | None = None,
) -> dict[tuple[str | None, str | None], dict[int, list[Fact]]]:
    """(taxonomy, tag) -> period_id -> one Fact per filing, newest filing first: the authoritative copy, plus (not
    latest_only) every other filing's copy of the same value. Same source filters as _load_facts; predecessor
    windows are not included."""
    out: dict[tuple[str | None, str | None], dict[int, list[Fact]]] = defaultdict(dict)
    if not tags:
        return out
    with conn.cursor() as cur:
        cur.execute(
            """
            select taxonomy, tag, period_id, value, id, end_date, is_derived, filing_id, accession_number, filing_date,
                   is_authoritative, form, period_of_report, period_type, start_date
            from (
                select c.taxonomy, c.tag, f.period_id, f.value, f.id, p.end_date, f.is_derived, f.filing_id,
                       fl.accession_number, fl.filing_date, f.is_authoritative, fl.form, fl.period_of_report,
                       p.period_type, p.start_date,
                       rank() over (partition by c.taxonomy, c.tag, f.period_id
                                    order by fl.filing_date desc nulls last, f.filing_id desc) as rk
                from core.fact f
                join core.concept c on c.id = f.concept_id
                join core.period p on p.id = f.period_id
                join core.filing fl on fl.id = f.filing_id
                where f.company_id = %s
                  -- the authoritative copy; for vintages also every other filing's copy of the SAME value (the
                  -- same number as printed in that filing: a sum can then take all parts from one filing)
                  and (f.is_authoritative or (not %s and exists (
                      select 1 from core.fact a
                      where a.company_id = f.company_id and a.concept_id = f.concept_id and a.unit_id = f.unit_id
                        and a.period_id = f.period_id and a.is_authoritative and a.value = f.value)))
                  -- a filing in which THIS company is only a co-registrant (or quarantined) carries the filer's
                  -- statements, not its own: never a source (core.filing_registrant, rule
                  -- entity.shared_accession_primary_filer@1)
                  and not exists (
                      select 1 from core.filing_registrant r
                      where r.accession_number = fl.accession_number and r.company_id = f.company_id
                        and r.role in ('co_registrant', 'quarantined'))
                  -- the company's OWN filings inside an 'exclude' window belong to another entity
                  and not exists (
                      select 1 from core.company_history_source h
                      where h.company_id = f.company_id and h.relation = 'exclude'
                        and coalesce(fl.period_of_report, p.end_date) between h.valid_from and h.valid_to)
                  and c.tag = any(%s)
            ) t
            where rk = 1 or not %s
            order by taxonomy, tag, period_id, filing_date desc nulls last, filing_id desc, id desc
            """,
            (
                company_id,
                latest_only,
                sorted({t for _, t in tags if t is not None}),
                latest_only,
            ),
        )
        rows = cur.fetchall()
    # core.fact is unique per (company, tag, unit, period, filing): two values for one tag and period in one
    # filing can only come from two units. Never pick one: mark the fact ambiguous (blank downstream).
    grouped: dict[tuple, list[tuple]] = defaultdict(list)
    for r in rows:
        # a same-value copy in a filing that does not print the period as a face column (common/authority) is no
        # vintage: the sum's source filing is chosen among eligible prints only, as the proof's authority does
        if not r[10] and not (
            face.eligible(r[11], r[12], r[8], r[1], r[14], r[5], r[13])
            if face is not None
            else face_column_eligible(r[11], r[12], r[5], r[13])
        ):
            continue
        # statement coherence: even the authoritative copy must be one this filing's FACE statement prints (JPM
        # total assets served from a summary table of the next year's 10-Q): the mapper never serves it
        if (
            r[10]
            and face is not None
            and not face.printed_ok(r[8], r[1], r[14], r[5], r[13])
        ):
            continue
        grouped[(r[0], r[1], r[2], r[7])].append(r)
    for (taxonomy, tag, period_id, _), rs in grouped.items():
        if (taxonomy, tag) not in tags:
            continue
        first = rs[0]
        out[(taxonomy, tag)].setdefault(period_id, []).append(
            Fact(
                Decimal(first[3]),
                first[4],
                first[5],
                first[6],
                first[7],
                first[8],
                first[9],
                ambiguous=len({Decimal(x[3]) for x in rs}) > 1,
                por=first[12],
            )
        )
    return out


def _merge_predecessor_facts(conn, company_id, tags, out) -> None:
    """History of a 'predecessor' window (core.company_history_source): authoritative facts of filings of the
    predecessor's own core.company row whose period lies in [valid_from, valid_to], re-keyed onto THIS company's
    core.period by (start, end, type). A predecessor CIK without a core.company row has no facts in core.fact to
    read (its history needs ingestion first); nothing is invented for it. Latest filing wins on a clash."""
    with conn.cursor() as cur:
        cur.execute(
            """
            select distinct on (c.taxonomy, c.tag, sp.id)
                   c.taxonomy, c.tag, sp.id, f.value, f.id, p.end_date, f.is_derived,
                   f.filing_id, fl.accession_number, fl.filing_date
            from core.company_history_source h
            join core.company pc on pc.cik = h.source_cik
            join core.fact f on f.company_id = pc.id and f.is_authoritative
            join core.concept c on c.id = f.concept_id
            join core.period p on p.id = f.period_id
            join core.filing fl on fl.id = f.filing_id
            join core.period sp on sp.company_id = h.company_id and sp.start_date = p.start_date
                 and sp.end_date = p.end_date and sp.period_type = p.period_type
            where h.company_id = %s and h.relation = 'predecessor'
              and coalesce(fl.period_of_report, p.end_date) between h.valid_from and h.valid_to
              and c.tag = any(%s)
              and not exists (
                  select 1 from core.filing_registrant r
                  where r.accession_number = fl.accession_number and r.company_id = pc.id
                    and r.role in ('co_registrant', 'quarantined'))
            order by c.taxonomy, c.tag, sp.id, fl.filing_date desc nulls last, f.filing_id desc, f.id desc
            """,
            (company_id, sorted({t for _, t in tags if t is not None})),
        )
        for (
            taxonomy,
            tag,
            period_id,
            value,
            fact_id,
            end,
            derived,
            filing_id,
            acc,
            filed,
        ) in cur.fetchall():
            if (taxonomy, tag) not in tags:
                continue
            new = Fact(Decimal(value), fact_id, end, derived, filing_id, acc, filed)
            old = out[(taxonomy, tag)].get(period_id)
            if old is None or (new.filed or date.min, new.filing_id) > (
                old.filed or date.min,
                old.filing_id,
            ):
                out[(taxonomy, tag)][period_id] = new


def _load_fsn_facts(
    conn: psycopg.Connection,
    company_id: int,
    tags: set[tuple[str | None, str | None]],
    periods: dict[int, tuple[date, date, str]],
):
    """Custom-tag facts from the filing's own XBRL (fsn.value) mapped onto the company's core.period by the SEC's
    month-end rounding of ddate and the quarter count (qtrs 0 = instant, else a duration of ~qtrs x 91 days).
    The latest ACCEPTED filing that prints the tag for the period wins; a value whose tag has no face line in that
    filing (fsn.line) is flagged on_face = False (the cell is held, never served from a note-only value)."""
    out: dict[tuple[str | None, str | None], dict[int, Fact]] = defaultdict(dict)
    for key, by_period in _load_fsn_vintages(
        conn, company_id, tags, periods, custom_only=True
    ).items():
        for pid, prints in by_period.items():
            out[key][pid] = prints[0]
    return out


def _load_fsn_vintages(
    conn: psycopg.Connection,
    company_id: int,
    tags: set[tuple[str | None, str | None]],
    periods: dict[int, tuple[date, date, str]],
    custom_only: bool = False,
) -> dict[tuple[str | None, str | None], dict[int, list[Fact]]]:
    """(taxonomy, tag) -> period_id -> one fsn_xbrl Fact per filing, latest accepted first (the rules of
    _load_fsn_facts). custom_only=False also reads standard tags: the filing's own XBRL carries its us-gaap lines,
    so a sum with a custom part can read every part from that one filing (_single_source_parts)."""
    out: dict[tuple[str | None, str | None], dict[int, list[Fact]]] = defaultdict(dict)
    wanted = {(t, g) for t, g in tags if g is not None}
    if not wanted:
        return out
    tax_of = {g: t for t, g in wanted}
    with conn.cursor() as cur:
        cur.execute(
            """
            select t.tag, v.id, v.ddate, v.qtrs, v.value, f.id, f.accession, f.accepted, f.form, f.period,
                   exists (select 1 from fsn.line l where l.filing_id = v.filing_id and l.tag_id = v.tag_id)
            from fsn.value v
            join fsn.tag t on t.id = v.tag_id
            join fsn.filing f on f.id = v.filing_id
            where v.company_id = %s and (t.custom or not %s) and t.tag = any(%s)
              and v.dim_id = 0 and v.coreg = '' and v.iprx = 0 and v.value is not null
            order by f.accepted desc nulls last, v.id desc
            """,
            (company_id, custom_only, sorted(tax_of)),
        )
        rows = cur.fetchall()
    grouped: dict[tuple[str, int, int], list[tuple]] = defaultdict(list)
    for (
        tag,
        vid,
        ddate,
        qtrs,
        value,
        fid,
        acc,
        accepted,
        form,
        fperiod,
        on_face,
    ) in rows:
        match = [
            pid
            for pid, (start, end, ptype) in periods.items()
            if fsn_end_matches(ddate, end)
            and (
                ptype == "instant"
                if qtrs == 0
                else ptype == "duration"
                and qtrs * 91 - 20 <= (end - start).days <= qtrs * 91 + 20
            )
        ]
        if len(match) != 1:
            continue  # no unique core.period for it: never guess
        mstart, mend, mtype = periods[match[0]]
        if not face_column_eligible(form, fperiod, mend, mtype):
            continue  # a filing speaks for a period only where it prints that column (authority v2)
        grouped[(tag, match[0], fid)].append(
            (vid, ddate, Decimal(value), fid, acc, accepted, on_face, fperiod)
        )
    for (tag, pid, _), same in sorted(
        grouped.items(),
        key=lambda kv: max((r[5] is not None, r[5], r[0]) for r in kv[1]),
        reverse=True,
    ):  # one filing's prints of the tag for the period; filings latest accepted first
        same.sort(key=lambda r: r[0], reverse=True)
        on_face = any(r[6] for r in same)
        used = [r for r in same if r[6]] or same
        first = used[0]
        accepted = first[5]
        out[(tax_of[tag], tag)].setdefault(pid, []).append(
            Fact(
                first[2],
                first[0],
                periods[pid][1],
                False,
                -first[3],
                first[4],
                accepted.date() if accepted else None,
                ambiguous=len({r[2] for r in used}) > 1,
                source="fsn_xbrl",
                on_face=on_face,
                por=first[7],
            )
        )
    return out


def _load_proof_disagree(
    conn: psycopg.Connection, company_id: int
) -> dict[tuple[str, str, date, date], Decimal]:
    """(data point, grain, start, end) -> the value the cell's LAST proof verdict judged wrong (analytics.cell_proof
    keeps one row per cell key, upserted, so that row is the cell's latest verdict whichever run wrote it). A held
    cell is not served, so no later run re-proves it: its DISAGREE row is still the evidence. The hold applies only
    while the mapper would serve that same value (_proof_guard), so a corrected value is never hidden. (A latest-run
    window released the cells step 3 held and step 4 never saw: 358 served DISAGREE on 2026-11-12.) Only rows of the
    CURRENT detector version count: a held cell is never re-proved, so a row of an older detector would hold the
    cell for ever (48 MSFT DISAGREEs of the pre-R13 logic); once released the cell is served and the proof re-judges
    it, and a real disagreement is written at the current version and holds it again. Empty when the table is absent."""
    if conn.execute("select to_regclass('analytics.cell_proof')").fetchone()[0] is None:
        return {}
    return {
        (n, g, s, e): Decimal(v)
        for n, g, s, e, v in conn.execute(
            """
            select data_point_name, period_grain, period_start, period_end, shown_value
            from analytics.cell_proof
            where company_id = %s and basis = 'latest' and verdict = 'DISAGREE' and shown_value is not null
              and detector_version = %s
            """,
            (company_id, DETECTOR_VERSION),
        ).fetchall()
    }


def _load_no_authoritative(
    conn, company_id: int, tags: set[tuple[str | None, str | None]]
):
    """(taxonomy, tag) -> {period_id: fact count} for periods where the tag has facts but NONE is authoritative
    (an unresolved cross-filing conflict, core.fact.is_authoritative = false on every copy). Read only to give the
    cell a reason: a non-authoritative row is never a value."""
    out: dict[tuple[str | None, str | None], dict[int, int]] = defaultdict(dict)
    if not tags:
        return out
    with conn.cursor() as cur:
        cur.execute(
            """
            select c.taxonomy, c.tag, f.period_id, count(*)
            from core.fact f join core.concept c on c.id = f.concept_id
            where f.company_id = %s and c.tag = any(%s)
            group by c.taxonomy, c.tag, f.period_id
            having not bool_or(f.is_authoritative)
            """,
            (company_id, sorted({t for _, t in tags if t is not None})),
        )
        for taxonomy, tag, period_id, n in cur.fetchall():
            if (taxonomy, tag) in tags:
                out[(taxonomy, tag)][period_id] = n
    return out


def load_calc_evidence(conn: psycopg.Connection, accessions: set[str]):
    """(arcs, dcml): arcs[accession] = {(parent_tag, child_tag)} from fsn.calc_arc; dcml[(accession, tag, ddate)]
    = smallest decimals printed for that non-dimensional value (for the tie tolerance)."""
    arcs: dict[str, set[tuple[str, str]]] = defaultdict(set)
    dcml: dict[tuple[str, str, date], int] = {}
    if not accessions:
        return arcs, dcml
    with conn.cursor() as cur:
        cur.execute(
            """
            select f.accession, pt.tag, ct.tag
            from fsn.calc_arc a
            join fsn.filing f on f.id = a.filing_id
            join fsn.tag pt on pt.id = a.parent_tag_id
            join fsn.tag ct on ct.id = a.child_tag_id
            where f.accession = any(%s)
            """,
            (sorted(accessions),),
        )
        for acc, parent, child in cur.fetchall():
            arcs[acc].add((parent, child))
        cur.execute(
            """
            select f.accession, t.tag, v.ddate, min(v.dcml)
            from fsn.value v
            join fsn.filing f on f.id = v.filing_id
            join fsn.tag t on t.id = v.tag_id
            where f.accession = any(%s) and v.dim_id = 0 and v.dcml is not null
            group by 1, 2, 3
            """,
            (sorted(accessions),),
        )
        for acc, tag, ddate, d in cur.fetchall():
            dcml[(acc, tag, ddate)] = d
    return arcs, dcml


# Owners of a HELD cell (a definition or evidence the library has not settled): the cell is a defect that is
# guard-hidden, never "not presented". C8 (debt lane) and C6 (DPS) await a verified rule, R2 (no BS-parenthetical
# share count) a standardization ruling, cover-page / tax-note / conditional-template points a sector decision.
HELD_OWNERS = (
    ("held_c8", "verifier"),
    ("held_c6", "verifier"),
    ("held_r2", "standardization_lead"),
    ("held_cover_page", "sector_analyst"),
    ("held_tax_note", "sector_analyst"),
    ("held_template_seed", "sector_analyst"),
    ("held_read_verified_fail", "verifier"),
)


def _status_fields(row: MapRow) -> dict:
    """state / defect fields of a tagless status row's blank. reason_class held_* -> defect + guard_hidden (never
    shown as not_presented); everything else keeps the row's own decision as the state."""
    rc = (row.reason_class or "").lower()
    if rc.startswith("held_"):
        owner = next(
            (o for pre, o in HELD_OWNERS if rc.startswith(pre)), "standardization_lead"
        )
        return {
            "state": "defect",
            "defect_class": "guard_hidden",
            "owner": owner,
            "reason_code": rc,
        }
    out = {"state": row.decision}
    if rc:
        out["reason_code"] = rc
    return out


def _in_era(row: MapRow, end: date) -> bool:
    """The map's eras are FSN dates (rounded to the nearest month end); a fact's period end is the TRUE end (a
    52/53-week year ends days off a month end). A true end is inside an era when it is, or its month-end
    rounding is (common/fsn_dates.nearest_month_ends)."""
    return era_holds(row.era_from, row.era_to, end)


def _filing_in_era(row: MapRow, fact: Fact) -> bool:
    """Per-filing tag era: a later filing that restates a period prints it under the tag ITS OWN period's map row
    uses (MSFT revenue: FY2016 SalesRevenueNet in the FY2017 10-K, RevenueFromContractWithCustomerExcludingAssessedTax
    in the FY2018 10-K, whose own period lies in the new tag's era). The fact is a candidate for the row when the
    filing it was printed in sits in the row's era, although the fact's own period does not. The newest-filing rule
    in build_cells then serves the latest eligible filing's print (facts are loaded face-column eligible only). Only a
    period that some concept row of the same concept already covers (any tag): the rule picks the tag, it never
    extends the map's coverage to earlier periods."""
    return fact.por is not None and _in_era(row, fact.por)


def _sign(row: MapRow) -> int:
    return int(row.sign or 1)


def _is_override(row: MapRow) -> bool:
    return (
        (row.decided_by or "").lower().replace("-", "_").startswith("company_override")
    )


def _mult(row: MapRow) -> Decimal:
    """served value = sign x scale x STORED value (Decimal). A scale other than 1 is valid only on a row from a
    filing-checked company override; any other row is served unscaled (and the seeder refuses to load it)."""
    scale = row.scale if row.scale == 1 or _is_override(row) else Decimal(1)
    return Decimal(_sign(row)) * scale


def _scaled(row: MapRow) -> bool:
    return row.scale != 1 and _is_override(row)


def _lineage(pairs) -> dict:
    """value_source and lineage of a cell: core.fact ids (source_fact_ids) for sec_api, fsn.value ids
    (source_value_ids) for fsn_xbrl. canonical_fact has no value_source column: the family carries it."""
    src = "fsn_xbrl" if any(f.source == "fsn_xbrl" for _, f in pairs) else "sec_api"
    ids = sorted({f.fact_id for _, f in pairs if f.source == src})
    return {
        "value_source": src,
        "source_fact_ids": ids if src == "sec_api" else [],
        "source_value_ids": ids if src == "fsn_xbrl" else [],
    }


def _note(pairs) -> str | None:
    """The label note of the rows that built a cell (e.g. 'face line including restricted cash, as printed').
    canonical_fact has no per-cell note column: the note is returned with the cell and stays on the map row."""
    notes_set = {r.serve_note for r, _ in pairs if r.serve_note}
    for r, _ in pairs:
        if _scaled(
            r
        ):  # provenance of a filing-checked scale: what the filer printed, what is stored, the source
            notes_set.add(
                f"filer printed in scaled units, stored unscaled; scale x{r.scale:,} from override "
                f"{r.evidence_adsh} R{r.evidence_report}"
            )
    notes = sorted(notes_set)
    return "; ".join(notes) or None


def _local(tag: str | None) -> str | None:
    return None if tag is None else tag.rsplit(":", 1)[-1]


def _descendants(arcs: set[tuple[str, str]], tag: str) -> set[str]:
    seen: set[str] = set()
    stack = [tag]
    while stack:
        cur = stack.pop()
        for parent, child in arcs:
            if parent == cur and child not in seen:
                seen.add(child)
                stack.append(child)
    return seen


def _check_components(
    comps: list[tuple[MapRow, Fact]],
    arcs: dict[str, set[tuple[str, str]]],
    founder_definition: bool = False,
) -> str | None:
    """Reason code if the component set must not be summed (rules 2 and 3), else None. total_debt is the
    founder's definition (doc 02, 2026-11-04): its listed debt lines are summed as defined, not as one calc
    parent's children, so only the single-filing and ambiguity checks apply."""
    if len({f.source for _, f in comps}) > 1:
        return "mixed_value_sources"  # a cell is single-source: SEC companyfacts or the filing's own XBRL
    if any(not f.on_face for _, f in comps):
        return "fsn_value_not_on_face_line"
    if any(f.ambiguous for _, f in comps):
        return "ambiguous_values_in_filing"
    if len({f.filing_id for _, f in comps}) != 1:
        return "components_from_different_filings"
    if founder_definition:
        return None
    acc = comps[0][1].accession
    filing_arcs = arcs.get(acc, set())
    if not filing_arcs:
        return "no_calc_evidence"
    tags = [str(r.tag) for r, _ in comps]
    for r, _ in comps:  # rule 3: no member may be an ancestor of another member
        if _descendants(filing_arcs, str(r.tag)) & (set(tags) - {r.tag}):
            return "ancestor_in_component_set"
    # evidence_cal_parent may list several parents ('A;B', the line's calc parents): the components must share
    # one parent, and each must be a DIRECT child of it in this filing's arcs (rule 2)
    parent_sets = [
        {_local(p) for p in (r.evidence_cal_parent or "").split(";") if p.strip()}
        for r, _ in comps
    ]
    common = set.intersection(*parent_sets)
    if not common:
        return "components_without_single_calc_parent"
    if not any(all((p, r.tag) in filing_arcs for r, _ in comps) for p in common):
        return "component_not_direct_child_of_parent"
    return None


def _face_lines_of_one_filing(
    comps: list[tuple[MapRow, Fact]], arcs: dict[str, set[tuple[str, str]]]
) -> bool:
    """Every part of the sum is a calculation child (a line of a statement) in the one filing it is read from,
    with no ancestor among the other parts (checked before) and a tolerance of 0.5 unit x n parts at the proof.
    Calc arcs of the filing exist (a filing with none gives no line evidence) and name each part as a child."""
    acc = comps[0][1].accession
    children = {child for _parent, child in arcs.get(acc, set())}
    return bool(children) and all(str(r.tag) in children for r, _ in comps)


def _grain(start: date, end: date, ptype: str) -> str | None:
    if ptype == "instant":
        return "I"
    days = (end - start).days
    if 350 <= days <= 380:
        return "FY"
    if 80 <= days <= 100:
        return "Q"
    return None


# A filing with no calculation arcs (MSFT FY2024 10-K, Q1 FY2025 10-Q) gives no parent/child evidence for a sum.
# The statement face still proves it: operating expenses must tie gross profit - opex = operating income of the
# same filing (_opex_tie), and an SG&A sum is accepted only when all its lines are parts of that tied opex.
TIE_EVIDENCE = {"operating_expenses", "sga_expense"}
# Calc evidence that is absent (no arcs) or does not isolate one parent for the printed lines (MSFT: R&D, S&M and
# G&A hang off different calc parents across filings, so no single parent lists them) is replaced by the face tie
# for these concepts: the printed lines between gross profit and operating income must sum to GP - OI.
TIE_REASONS = {
    "no_calc_evidence",
    "components_without_single_calc_parent",
    "component_not_direct_child_of_parent",
}


def _one_filing_parts(
    comps: list[tuple[MapRow, Fact]],
    vintages: dict[tuple[str | None, str | None], dict[int, list[Fact]]],
    period_id: int,
    statement_accession: str | None = None,
) -> list[tuple[MapRow, Fact]] | None:
    """All parts of one sum from ONE filing: the statement filing when it prints every part (common/authority
    FaceIndex.statement_filing), else the newest filing that prints every one of them (never a restated part next
    to an unrestated one). None when no single filing prints them all, or a part is not a sec_api vintage."""
    by_filing: list[dict[int, Fact]] = []
    for row, f in comps:
        if f.source != "sec_api":
            return None
        prints = {
            v.filing_id: v
            for v in vintages.get((row.taxonomy, row.tag), {}).get(period_id, [])
        }
        if not prints:
            return None
        by_filing.append(prints)
    prefer = next(
        (
            fid
            for fid, v in by_filing[0].items()
            if statement_accession is not None and v.accession == statement_accession
        ),
        None,
    )
    best = latest_complete_filing(
        [{fid: v.filed for fid, v in prints.items()} for prints in by_filing], prefer
    )
    if best is None:
        return None
    return [(row, prints[best]) for (row, _), prints in zip(comps, by_filing)]


def _single_source_parts(
    comps: list[tuple[MapRow, Fact]],
    fsn_vintages: dict[tuple[str | None, str | None], dict[int, list[Fact]]],
    period_id: int,
    statement_accession: str | None = None,
) -> list[tuple[MapRow, Fact]] | None:
    """A sum with a custom (fsn_xbrl) part reads EVERY part from ONE filing's own XBRL: the latest face-column-
    eligible filing that prints every part (common/authority.latest_complete_filing), never the filing the custom
    part happened to come from nor a fix row's accession (MSFT FY2016-17 opex was served from the FY2016/17 10-K
    while the FY2018 10-K restates the period). A renamed extension tag counts as the same line
    (common/tag_aliases). None when no single filing prints every part."""
    by_part: list[dict[str, Fact]] = []
    for row, _f in comps:
        prints: dict[str, Fact] = {}
        if _f.source == "fsn_xbrl":
            prints[_f.accession] = _f  # the part's own print always competes
        for tag in with_aliases(str(row.tag)):
            for v in fsn_vintages.get((row.taxonomy, tag), {}).get(period_id, []):
                prints.setdefault(v.accession, v)
        if not prints:
            return None
        by_part.append(prints)
    best = latest_complete_filing(
        [{acc: v.filed for acc, v in prints.items()} for prints in by_part],
        statement_accession,
    )
    if best is None:
        return None
    return [(row, prints[best]) for (row, _), prints in zip(comps, by_part)]


def _proof_grain(start: date, end: date, ptype: str) -> str:
    return (
        _grain(start, end, ptype) or "TP"
    )  # a year-to-date column is 'TP' in analytics.cell_proof


def _proof_guard(
    cells: list[dict],
    concept_info,
    periods: dict[int, tuple[date, date, str]],
    stats: dict,
    proof_disagree: dict[tuple[str, str, date, date], Decimal],
) -> list[dict]:
    """A cell whose LATEST cell_proof verdict is DISAGREE is never served (Dhairya 2026-11-12): held with
    proof_disagree. The verdict applies only while it judged the value about to be served (its shown_value equals
    it): a value that changed since the proof is served and proved again, and a later PROVEN verdict (one row per
    cell key, upserted) serves the cell on the next plan. No manual clearing."""
    if not proof_disagree:
        return cells
    kept = []
    for c in cells:
        period = periods.get(c["period_id"])
        shown = None
        if period is not None:
            start, end, ptype = period
            name = concept_info[c["canonical_concept_id"]][0]
            shown = proof_disagree.get(
                (name, _proof_grain(start, end, ptype), start, end)
            )
        if shown is not None and shown == c["value"]:
            stats["held"].append(
                {
                    "canonical_concept_id": c["canonical_concept_id"],
                    "period_id": c["period_id"],
                    "reason": "proof_disagree",
                }
            )
            continue
        kept.append(c)
    return kept


HOLD_OWNERS = {
    "proof_disagree": "verifier",
    "component_without_authoritative_fact": "data_engineer_l1",
    "component_missing_for_period": "data_engineer_l1",
}


def _held_reasons(stats: dict, concept_info, periods) -> None:
    """Every held cell gets its reason written (defect, guard_hidden), so a held cell is never a blank without
    one. A cell that already has a reasoned blank keeps it; year-to-date columns (no FY/Q/I grain) are skipped,
    as for every blank."""
    have = {(b["canonical_concept_id"], b["period_id"]) for b in stats["blanks"]}
    for h in stats["held"]:
        key = (h["canonical_concept_id"], h["period_id"])
        if key in have or h["period_id"] not in periods:
            continue
        start, end, ptype = periods[h["period_id"]]
        grain = _grain(start, end, ptype)
        if grain is None:
            continue
        have.add(key)
        stats["blanks"].append(
            {
                "canonical_concept_id": key[0],
                "concept_name": concept_info[key[0]][0],
                "period_id": key[1],
                "state": "defect",
                "defect_class": "guard_hidden",
                "owner": HOLD_OWNERS.get(h["reason"], "standardization_lead"),
                "reason_code": h["reason"],
                "reason": f"held by the tag-map mapper: {h['reason']}",
                "rule_id": RULE_ID,
                "period_start": start,
                "period_end": end,
                "grain": grain,
            }
        )


def _sga_inside_tied_opex(cells: list[dict], concept_info, stats: dict) -> list[dict]:
    """An sga sum without calc arcs stands only when the same period's opex was built from components of the same
    filing, tied to gross profit and operating income (it survived _opex_tie), and contains every sga line."""
    opex = {
        c["period_id"]: c
        for c in cells
        if c.get("_from_components")
        and _base(concept_info[c["canonical_concept_id"]][0]) == "operating_expenses"
    }
    kept = []
    for c in cells:
        if not (
            c.get("_needs_tie")
            and _base(concept_info[c["canonical_concept_id"]][0]) == "sga_expense"
        ):
            kept.append(c)
            continue
        o = opex.get(c["period_id"])
        if (
            o is None
            or o["_accession"] != c["_accession"]
            or not set(c["_dcml_keys"]) <= set(o["_dcml_keys"])
        ):
            stats["held"].append(
                {
                    "canonical_concept_id": c["canonical_concept_id"],
                    "period_id": c["period_id"],
                    "reason": c.get("_tie_reason") or "no_calc_evidence",
                }
            )
            continue
        kept.append(c)
    return kept


def build_cells(
    rows: list[MapRow],
    facts: dict[tuple[str | None, str | None], dict[int, Fact]],
    concept_info: dict[int, tuple[str, str]],
    arcs: dict[str, set[tuple[str, str]]] | None = None,
    dcml: dict[tuple[str, str | None, date], int] | None = None,
    periods: dict[int, tuple[date, date, str]] | None = None,
    alt_facts: dict[tuple[str | None, str | None], dict[int, Fact]] | None = None,
    no_auth: dict[tuple[str | None, str | None], dict[int, int]] | None = None,
    vintages: dict[tuple[str | None, str | None], dict[int, list[Fact]]] | None = None,
    fsn_vintages: dict[tuple[str | None, str | None], dict[int, list[Fact]]]
    | None = None,
    proof_disagree: dict[tuple[str, str, date, date], Decimal] | None = None,
    face: FaceIndex | None = None,
) -> tuple[list[dict], dict]:
    """Pure core: map rows + facts + calc evidence -> canonical cells. concept_info: id -> (name, statement).
    vintages: every authoritative filing's print of the component tags (sec_api), so a sum whose parts' latest
    prints sit in different filings can take ALL its parts from the newest filing that prints every one."""
    arcs = arcs or {}
    vintages = vintages or {}
    fsn_vintages = fsn_vintages or {}
    dcml = dcml or {}
    periods = periods or {}
    stats: dict[str, Any] = {
        "stmt_mismatch_rows": 0,
        "conflict_cells": 0,
        "derived_eps_skipped": 0,
        "held": [],
        "blanks": [],
        "blank_conflicts": [],
        "combined_lines": [],
    }

    def stmt_ok(concept_id: int, stmt: str) -> bool:
        name, statement = concept_info[concept_id]
        # follow the row's stmt as given: 'UN' (unclassified) can be the real entity's only statement
        # (a co-registrant UN statement is excluded by the library through its own rows, not here)
        return stmt == "UN" or stmt in (
            {STATEMENT_CODE[statement]} | EXTRA_STMT.get(name, set())
        )

    direct: dict[tuple[int, int], list[tuple[MapRow, Fact]]] = defaultdict(list)
    comp: dict[tuple[int, int], list[tuple[MapRow, Fact]]] = defaultdict(list)
    for row in rows:
        if row.decision in ("excluded", "not_presented", "not_in_template", "combined"):
            continue  # 'combined' never feeds a concept (only a reasoned blank below)
        target = (
            row.parent_concept_id
            if row.decision == "component"
            else row.canonical_concept_id
        )
        if target is None or not stmt_ok(target, row.stmt):
            stats["stmt_mismatch_rows"] += 1
            continue
        for period_id, fact in facts.get((row.taxonomy, row.tag), {}).items():
            if not (
                _in_era(row, fact.end)
                or (
                    row.decision == "concept"
                    and _filing_in_era(row, fact)
                    and any(
                        o.decision == "concept"
                        and o.canonical_concept_id == row.canonical_concept_id
                        and _in_era(o, fact.end)
                        for o in rows
                    )
                )
            ):
                continue
            if fact.derived and concept_info[target][0] in NEVER_DERIVED:
                stats["derived_eps_skipped"] += 1
                continue
            (comp if row.decision == "component" else direct)[
                (target, period_id)
            ].append((row, fact))

    def hold(key, reason):
        stats["held"].append(
            {"canonical_concept_id": key[0], "period_id": key[1], "reason": reason}
        )

    cells: list[dict] = []
    conflicts: set[tuple[int, int]] = set()
    for key in sorted(set(direct) | set(comp)):
        d = direct.get(key, [])
        c = comp.get(key, [])
        if d:
            # several 'concept' rows may list different tags for one concept (10-Q vs 10-K tags, a mid-year
            # switch; never printed together in one filing): the LATEST filing's value wins, never a sum, never
            # tag order. Two listed tags printing different values in that same latest filing: reasoned blank.
            newest = max((f.filed or date.min, f.filing_id) for _, f in d)
            d = [(r, f) for r, f in d if (f.filed or date.min, f.filing_id) == newest]
            if any(not f.on_face for _, f in d):
                hold(key, "fsn_value_not_on_face_line")
                continue
            if len({f.value * _mult(r) for r, f in d}) > 1 or any(
                f.ambiguous for _, f in d
            ):
                stats["conflict_cells"] += 1
                hold(key, "conflicting_values_in_filing")
                conflicts.add(key)
                continue
            ref = d[0][1]
            ref_value = ref.value * _mult(d[0][0])
            # rule 1: the printed concept wins; components of the SAME filing must still tie (rule 2)
            same = [(r, f) for r, f in c if f.filing_id == ref.filing_id]
            if same:
                total = sum(f.value * _mult(r) for r, f in same)
                tol = tol_of(
                    [dcml.get((f.accession, r.tag, f.end)) for r, f in same]
                    + [dcml.get((ref.accession, d[0][0].tag, ref.end))]
                )
                if abs(total - ref_value) > tol:
                    hold(key, "printed_total_does_not_tie_to_components")
                    continue
            cells.append(
                {
                    "canonical_concept_id": key[0],
                    "period_id": key[1],
                    "value": ref_value,
                    **_lineage(d),
                    "serve_note": _note(d),
                    "_scaled": any(_scaled(r) for r, _ in d),
                    "_filing_id": ref.filing_id,
                    "_accession": ref.accession,
                    "_dcml_keys": [(f.accession, r.tag, f.end) for r, f in d],
                }
            )
            continue
        pname, pstmt = concept_info[key[0]]
        if pstmt == "balance_sheet" and _base(pname) != "total_debt":
            # D3 / doc 02: instants are never derived; the only instant component sum is total debt
            hold(key, "instant_component_sum_not_allowed")
            continue
        # every part the map lists for the period must be present: a missing part is unknown, not zero, and
        # summing the rest serves a partial total (MSFT sga FY2016 = G&A alone: S&M's copies were all
        # non-authoritative, and its Q4 could not be derived). Eras are cut to where a line is printed.
        present = {(r.taxonomy, r.tag) for r, _ in c}
        end = c[0][1].end
        missing = [
            r
            for r in rows
            if r.decision == "component"
            and r.parent_concept_id == key[0]
            and (r.taxonomy, r.tag) not in present
            and _in_era(r, end)
        ]
        if missing:
            hold(
                key,
                "component_without_authoritative_fact"
                if any(
                    (no_auth or {}).get((r.taxonomy, r.tag), {}).get(key[1])
                    for r in missing
                )
                else "component_missing_for_period",
            )
            continue
        sf = None
        if face is not None and key[1] in periods and pstmt in STATEMENT_CODE:
            pstart, pend, ptype_ = periods[key[1]]
            sf = face.statement_filing(STATEMENT_CODE[pstmt], pstart, pend, ptype_)
        if len({f.source for _, f in c}) > 1:
            c = _single_source_parts(c, fsn_vintages, key[1], sf) or c
        if len({f.filing_id for _, f in c}) > 1:
            c = _one_filing_parts(c, vintages, key[1], sf) or c
        reason = _check_components(c, arcs, _base(pname) == "total_debt")
        needs_tie = reason in TIE_REASONS and _base(pname) in TIE_EVIDENCE
        if (
            reason == "components_without_single_calc_parent"
            and not needs_tie
            and _face_lines_of_one_filing(c, arcs)
        ):
            reason = None  # S9: face lines of one filing, no single calc parent: the proof judges the sum
        if reason and not needs_tie:
            hold(key, reason)
            continue
        cells.append(
            {
                "canonical_concept_id": key[0],
                "period_id": key[1],
                "value": sum((f.value * _mult(r) for r, f in c), Decimal(0)),
                **_lineage(c),
                "serve_note": _note(c),
                "_scaled": any(_scaled(r) for r, _ in c),
                "_filing_id": c[0][1].filing_id,
                "_accession": c[0][1].accession,
                "_from_components": True,
                "_needs_tie": needs_tie,
                "_tie_reason": reason if needs_tie else None,
                "_dcml_keys": [(f.accession, r.tag, f.end) for r, f in c],
            }
        )
    # gross profit / operating income as printed in EACH filing (not only the latest print), so a sum read from
    # an older filing ties to that filing's own face
    tie_prints: dict[tuple[str, int, str], dict] = {}
    for row in rows:
        base = _tie_base(concept_info.get(row.canonical_concept_id or -1, ("",))[0])
        if row.decision != "concept" or base not in TIE_BASES:
            continue
        for vs in (vintages, fsn_vintages):
            for pid, prints in vs.get((row.taxonomy, row.tag), {}).items():
                for f in prints:
                    if _in_era(row, f.end) and not f.ambiguous:
                        tie_prints.setdefault(
                            (base, pid, f.accession),
                            {
                                "value": f.value * _mult(row),
                                "_accession": f.accession,
                                "_dcml_keys": [(f.accession, row.tag, f.end)],
                            },
                        )
    cells = _opex_tie(cells, concept_info, dcml, stats, tie_prints)
    cells = _sga_inside_tied_opex(cells, concept_info, stats)
    cells = _scale_sanity(cells, concept_info, periods, stats)
    cells = _proof_guard(cells, concept_info, periods, stats, proof_disagree or {})
    value_keys = {(c["canonical_concept_id"], c["period_id"]) for c in cells}
    held_keys = {(h["canonical_concept_id"], h["period_id"]) for h in stats["held"]}
    name_to_id = {n: i for i, (n, _) in concept_info.items()}
    for row in rows:
        if row.decision == "combined":
            # one printed line spanning several concepts (founder ruling doc 02, sector templates item 3): it is
            # SERVED as the company's own combined line (analytics.company_combined_line: label, sign x stored
            # value) and never feeds a spanned concept; each spanned concept leaves the company's template for
            # that period (state not_in_template), unless a separate 'concept' row prints it.
            for period_id, fact in sorted(
                facts.get((row.taxonomy, row.tag), {}).items()
            ):
                if not _in_era(row, fact.end) or period_id not in (periods or {}):
                    continue
                start, end, ptype = periods[period_id]
                grain = _grain(start, end, ptype)
                if grain is None:
                    continue
                stats["combined_lines"].append(
                    {
                        "period_id": period_id,
                        "stmt": row.stmt,
                        "taxonomy": row.taxonomy,
                        "tag": row.tag,
                        "plabel": row.evidence_plabel or row.tag,
                        "components": list(row.components or ()),
                        "value": fact.value * _mult(row),
                        "source_fact_ids": [fact.fact_id]
                        if fact.source == "sec_api"
                        else [],
                        "tag_map_id": row.map_id,
                    }
                )
                for name in row.components or ():
                    cid = name_to_id.get(name)
                    if cid is not None and (cid, period_id) in value_keys:
                        continue  # a separate 'concept' row prints it: the value wins
                    stats["blanks"].append(
                        {
                            "canonical_concept_id": cid,
                            "concept_name": name,
                            "period_id": period_id,
                            "state": "not_in_template",
                            "reason": f"shown as the company's combined line '{row.evidence_plabel}'",
                            "rule_id": row.rule_id,
                            "period_start": start,
                            "period_end": end,
                            "grain": grain,
                        }
                    )
            continue
        if row.decision not in ("not_presented", "not_in_template"):
            continue
        concept = row.canonical_concept_id
        if concept not in concept_info or not stmt_ok(concept, row.stmt):
            stats["stmt_mismatch_rows"] += 1
            continue
        for period_id, (start, end, ptype) in sorted((periods or {}).items()):
            key = (concept, period_id)
            if not _in_era(row, end) or key in held_keys:
                continue
            if (ptype == "instant") != (concept_info[concept][1] == "balance_sheet"):
                continue
            grain = _grain(start, end, ptype)
            if grain is None:
                continue
            if (
                key in value_keys
            ):  # a printed value wins; the clash is reported, never hidden
                stats["blank_conflicts"].append(
                    {
                        "canonical_concept_id": concept,
                        "period_id": period_id,
                        "state": row.decision,
                    }
                )
                continue
            stats["blanks"].append(
                {
                    "canonical_concept_id": concept,
                    "concept_name": concept_info[concept][0],
                    "period_id": period_id,
                    **_status_fields(row),
                    "reason": row.reason,
                    "rule_id": row.rule_id,
                    "period_start": start,
                    "period_end": end,
                    "grain": grain,
                }
            )
    # Inside a concept row's era the value comes ONLY from that row's tag. A period where an excluded alternate
    # tag of the same concept (reason_class alternate_tag_overlapping) has a fact but the winner tag has none is a
    # reasoned blank, never a fallback to the alternate.
    value_now = {(c["canonical_concept_id"], c["period_id"]) for c in cells}
    held_now = {(h["canonical_concept_id"], h["period_id"]) for h in stats["held"]}
    for row in rows:
        if row.decision != "concept" or row.canonical_concept_id is None:
            continue
        cname = concept_info[row.canonical_concept_id][0]
        for alt in rows:
            if (
                alt.decision != "excluded"
                or alt.reason_class != "alternate_tag_overlapping"
            ):
                continue
            if alt.stmt != row.stmt or alt.tag == row.tag:
                continue
            if alt.canonical_concept_id is not None:
                if alt.canonical_concept_id != row.canonical_concept_id:
                    continue
            elif f"same concept {cname} " not in (alt.reason or ""):
                continue
            for period_id, afact in sorted(
                (alt_facts or {}).get((alt.taxonomy, alt.tag), {}).items()
            ):
                key = (row.canonical_concept_id, period_id)
                if (
                    not _in_era(row, afact.end)
                    or not _in_era(alt, afact.end)
                    or period_id not in periods
                ):
                    continue
                if key in value_now or key in held_now:
                    continue
                if period_id in facts.get((row.taxonomy, row.tag), {}):
                    continue  # the winner has a fact; it was refused or conflicted for its own reason
                start, end, ptype = periods[period_id]
                grain = _grain(start, end, ptype)
                if grain is None:
                    continue
                stats["blanks"].append(
                    {
                        "canonical_concept_id": row.canonical_concept_id,
                        "concept_name": cname,
                        "period_id": period_id,
                        "state": "defect",
                        "defect_class": "finding_open",
                        "owner": "tag_mapper",
                        "reason_code": "no_fact_under_winner_tag",
                        "reason": f"no fact under {row.tag} for this period",
                        "rule_id": RULE_ID,
                        "period_start": start,
                        "period_end": end,
                        "grain": grain,
                    }
                )
                held_now.add(key)
    # A listed tag has facts for a period inside the row's era but none of them is authoritative: the cell is a
    # reasoned blank (an open data defect upstream of the mapper), never a value from a non-authoritative copy.
    value_now2 = {(c["canonical_concept_id"], c["period_id"]) for c in cells}
    held_now2 = {(h["canonical_concept_id"], h["period_id"]) for h in stats["held"]} | {
        (b["canonical_concept_id"], b["period_id"])
        for b in stats["blanks"]
        if b.get("canonical_concept_id")
    }
    for row in rows:
        if row.decision not in ("concept", "component") or row.tag is None:
            continue
        target = (
            row.parent_concept_id
            if row.decision == "component"
            else row.canonical_concept_id
        )
        if target is None or not stmt_ok(target, row.stmt):
            continue
        for period_id, n in sorted(
            (no_auth or {}).get((row.taxonomy, row.tag), {}).items()
        ):
            key = (target, period_id)
            if period_id not in periods or key in value_now2 or key in held_now2:
                continue
            start, end, ptype = periods[period_id]
            if not _in_era(row, end):
                continue
            grain = _grain(start, end, ptype)
            if grain is None:
                continue
            stats["blanks"].append(
                {
                    "canonical_concept_id": target,
                    "concept_name": concept_info[target][0],
                    "period_id": period_id,
                    "state": "defect",
                    "defect_class": "ingestion",
                    "owner": "data_engineer_l1",
                    "reason_code": "no_authoritative_fact",
                    "reason": f"{n} fact(s) under {row.tag} for this period, none authoritative (unresolved cross-filing conflict)",
                    "rule_id": RULE_ID,
                    "period_start": start,
                    "period_end": end,
                    "grain": grain,
                }
            )
            held_now2.add(key)
    for concept, period_id in sorted(conflicts):
        if period_id not in (periods or {}):
            continue
        start, end, ptype = periods[period_id]
        grain = _grain(start, end, ptype)
        if grain is None:
            continue
        stats["blanks"].append(
            {
                "canonical_concept_id": concept,
                "concept_name": concept_info[concept][0],
                "period_id": period_id,
                "state": "defect",
                "defect_class": "finding_open",
                "owner": "tag_mapper",
                "reason_code": "conflicting_values_in_filing",
                "reason": "two listed tags print different values for this concept in the latest filing",
                "rule_id": RULE_ID,
                "period_start": start,
                "period_end": end,
                "grain": grain,
            }
        )
    _held_reasons(stats, concept_info, periods)
    return cells, stats


def _base(name: str) -> str:
    return name.removesuffix("_resolved")


SHARE_CONCEPTS = {
    "weighted_basic_shares",
    "weighted_diluted_shares",
    "shares_outstanding",
}
SCALE_RATIO = Decimal(
    100
)  # a gross mismatch (a unit-scale error), never rounding / NCI / preferred


def _scale_sanity(cells: list[dict], concept_info, periods, stats: dict) -> list[dict]:
    """Scale sanity, never a silent rescale (filer_scale_error). A share-count cell is BLOCKED when it is 100x or
    more off (a) the company's other share facts of the same period end, or (b) the per-share identity:
    |EPS x weighted shares| against net income. EPS and net income stay as served."""
    by_name: dict[tuple[str, int], dict] = {}
    for c in cells:
        by_name[(_base(concept_info[c["canonical_concept_id"]][0]), c["period_id"])] = c
    blocked: dict[int, str] = {}  # id(cell) -> reason

    def block(cell: dict, why: str) -> None:
        if not cell.get(
            "_scaled"
        ):  # an explicit filing-checked override scale is exempt from the sanity block
            blocked.setdefault(id(cell), why)

    eps_of = {
        "weighted_basic_shares": "basic_eps",
        "weighted_diluted_shares": "diluted_eps",
    }
    for (name, pid), cell in list(by_name.items()):
        eps_name = eps_of.get(name)
        if eps_name is None:
            continue
        eps, ni = by_name.get((eps_name, pid)), by_name.get(("net_income", pid))
        if eps and ni and ni["value"] != 0 and eps["value"] != 0:
            ratio = abs(eps["value"] * cell["value"] / ni["value"])
            if ratio >= SCALE_RATIO or ratio <= 1 / SCALE_RATIO:
                block(
                    cell,
                    f"{name} {cell['value']} x {eps_name} {eps['value']} is {ratio:.6g}x net income {ni['value']}: implausible unit scale",
                )
    ends: dict = defaultdict(list)  # period end -> share cells of that date
    for (name, pid), cell in by_name.items():
        if name in SHARE_CONCEPTS and pid in (periods or {}) and cell["value"] > 0:
            ends[periods[pid][1]].append((name, cell))
    for group in ends.values():
        if len(group) < 2:
            continue
        hi = max(group, key=lambda g: g[1]["value"])
        for name, cell in group:
            if hi[1]["value"] / cell["value"] >= SCALE_RATIO:
                block(
                    cell,
                    f"{name} {cell['value']} is {hi[1]['value'] / cell['value']:.6g}x smaller than {hi[0]} {hi[1]['value']} of the same date: implausible unit scale",
                )
    kept = []
    for c in cells:
        why = blocked.get(id(c))
        if why is None:
            kept.append(c)
            continue
        pid = c["period_id"]
        stats["held"].append(
            {
                "canonical_concept_id": c["canonical_concept_id"],
                "period_id": pid,
                "reason": "filer_scale_error",
            }
        )
        if pid in (periods or {}):
            start, end, ptype = periods[pid]
            grain = _grain(start, end, ptype)
            if grain:
                stats["blanks"].append(
                    {
                        "canonical_concept_id": c["canonical_concept_id"],
                        "concept_name": concept_info[c["canonical_concept_id"]][0],
                        "period_id": pid,
                        "state": "defect",
                        "defect_class": "finding_open",
                        "owner": "tag_mapper",
                        "reason_code": "filer_scale_error",
                        "reason": why,
                        "rule_id": RULE_ID,
                        "period_start": start,
                        "period_end": end,
                        "grain": grain,
                    }
                )
    return kept


TIE_BASES = ("gross_profit", "operating_income", "revenue", "cost_of_revenue")


def _tie_base(name: str) -> str:
    b = _base(name)
    return "revenue" if b == "revenue_sanity" else b


def _span_start(by_name: dict, tie_prints: dict | None, period_id: int, acc: str):
    """The subtotal the operating-expense lines start from: the printed gross profit of the filing, or (no gross
    profit line: NFLX, GOOG, META, WMT) revenue less cost of revenue, the span from cost of revenue to operating
    income (S12). Each print must be of the filing the components were read from."""
    prints = tie_prints or {}

    def get(base: str):
        c = by_name.get((base, period_id))
        if c is None or c.get("_accession") != acc:
            c = prints.get((base, period_id, acc), c)
        return c if c is not None and c.get("_accession") == acc else None

    gp = get("gross_profit")
    if gp is not None:
        return gp
    rev, cor = get("revenue"), get("cost_of_revenue")
    if rev is None or cor is None:
        return None
    return {
        "value": rev["value"] - cor["value"],
        "_accession": acc,
        "_dcml_keys": rev["_dcml_keys"] + cor["_dcml_keys"],
    }


def _opex_tie(
    cells: list[dict], concept_info, dcml, stats: dict, tie_prints: dict | None = None
) -> list[dict]:
    """operating_expenses built from component lines (no opex total printed) must tie, per filing, to the
    printed statement: gross profit - sum(components) = operating income within the rounding tolerance
    (checks.tol_of). No gross profit / operating income of the same filing, or no tie: the cell is HELD."""
    by_name: dict[tuple[str, int], dict] = {}
    for c in cells:
        by_name.setdefault(
            (_tie_base(concept_info[c["canonical_concept_id"]][0]), c["period_id"]), c
        )
    kept = []
    for c in cells:
        if not (
            c.get("_from_components")
            and _base(concept_info[c["canonical_concept_id"]][0])
            == "operating_expenses"
        ):
            kept.append(c)
            continue
        gp = _span_start(by_name, tie_prints, c["period_id"], c["_accession"])
        oi = by_name.get(("operating_income", c["period_id"]))
        if oi is None or oi["_accession"] != c["_accession"]:
            oi = (tie_prints or {}).get(
                ("operating_income", c["period_id"], c["_accession"]), oi
            )
        key = (c["canonical_concept_id"], c["period_id"])
        if (
            gp is None
            or oi is None
            or gp["_accession"] != c["_accession"]
            or oi["_accession"] != c["_accession"]
        ):
            stats["held"].append(
                {
                    "canonical_concept_id": key[0],
                    "period_id": key[1],
                    "reason": "opex_tie_needs_gross_profit_and_operating_income_of_the_filing",
                }
            )
            continue
        tol = tol_of(
            [dcml.get(k) for k in c["_dcml_keys"] + gp["_dcml_keys"] + oi["_dcml_keys"]]
        )
        if abs(gp["value"] - c["value"] - oi["value"]) > tol:
            stats["held"].append(
                {
                    "canonical_concept_id": key[0],
                    "period_id": key[1],
                    "reason": "opex_components_do_not_tie_gross_profit_to_operating_income",
                }
            )
            continue
        kept.append(c)
    return kept


def _load_periods(
    conn: psycopg.Connection, company_id: int
) -> dict[int, tuple[date, date, str]]:
    with conn.cursor() as cur:
        cur.execute(
            "select id, start_date, end_date, period_type from core.period where company_id = %s",
            (company_id,),
        )
        return {i: (s, e, t) for i, s, e, t in cur.fetchall()}


def resolve_for_company(
    conn: psycopg.Connection,
    company_id: int,
    managed_concept_ids: set[int],
    concept_info: dict[int, tuple[str, str]],
    run_id: str | None = None,
    commit: bool = True,
    skip_concept_ids: frozenset[int] | set[int] = frozenset(),
) -> dict:
    """Rebuild this company's canonical_fact rows from its tag map. Deletes every concept resolve() manages
    (plus every concept the map targets), so no value of the old path survives for a tag-map company.
    skip_concept_ids (per-concept coverage gate): those concepts are left exactly as served today: not deleted,
    not rewritten, no blank reason written."""
    rows = _load_rows(conn, company_id)
    used: set[tuple[str | None, str | None]] = {
        (r.taxonomy, r.tag)
        for r in rows
        if r.tag is not None and r.decision != "excluded"
    }
    periods = _load_periods(conn, company_id)
    face = load_face_indexes(conn, [company_id])[company_id]
    facts = _load_facts(
        conn, company_id, {k for k in used if not is_custom(k[0])}, face
    )
    custom_used = {k for k in used if is_custom(k[0])}
    for k, by_period in _load_fsn_facts(conn, company_id, custom_used, periods).items():
        facts[k] = by_period
    alt_tags: set[tuple[str | None, str | None]] = set()
    for r in rows:
        if (
            r.decision == "excluded"
            and r.reason_class == "alternate_tag_overlapping"
            and r.tag is not None
        ):
            alt_tags.add((r.taxonomy, r.tag))
    alt_tags -= used
    alt_facts = _load_facts(
        conn, company_id, alt_tags
    )  # read only to detect winner-tag gaps, never a value
    comp_tags = {(r.taxonomy, r.tag) for r in rows if r.decision == "component"}
    vintages = _load_fact_vintages(
        conn, company_id, {k for k in comp_tags if not is_custom(k[0])}, face=face
    )
    # standard parts of a sum that has a custom part are also read from the filings' own XBRL (one source a cell)
    custom_parents = {
        r.parent_concept_id
        for r in rows
        if r.decision == "component" and is_custom(r.taxonomy)
    }
    tie_tags = {
        (r.taxonomy, r.tag)
        for r in rows
        if r.decision == "concept"
        and r.tag is not None
        and _tie_base(concept_info.get(r.canonical_concept_id or -1, ("",))[0])
        in TIE_BASES
    }
    for k, by_period in _load_fact_vintages(
        conn, company_id, {k for k in tie_tags if not is_custom(k[0])}, face=face
    ).items():
        vintages.setdefault(k, by_period)
    fsn_vintages = _load_fsn_vintages(
        conn,
        company_id,
        {
            (r.taxonomy, alias)
            for r in rows
            if r.decision == "component"
            and r.parent_concept_id in custom_parents
            and r.tag is not None
            for alias in with_aliases(r.tag)
        }
        | (tie_tags if custom_parents else set()),
        periods,
    )
    accessions = {
        f.accession for k in comp_tags | used for f in facts.get(k, {}).values()
    } | {
        f.accession
        for vs in (vintages, fsn_vintages)
        for by_period in vs.values()
        for fs in by_period.values()
        for f in fs
    }
    arcs, dcml = load_calc_evidence(conn, accessions)
    no_auth = _load_no_authoritative(conn, company_id, used)
    cells, stats = build_cells(
        rows,
        facts,
        concept_info,
        arcs,
        dcml,
        periods,
        alt_facts,
        no_auth,
        vintages,
        fsn_vintages,
        _load_proof_disagree(conn, company_id),
        face,
    )
    from scrooner_pipeline.mapper.derived_cells import (
        add_derived_cells,
    )  # circular via dqc_checks

    add_derived_cells(conn, company_id, cells, stats, concept_info, periods)
    targets = set(managed_concept_ids)
    for r in rows:
        targets.update(
            x for x in (r.canonical_concept_id, r.parent_concept_id) if x is not None
        )
    if skip_concept_ids:
        targets -= set(skip_concept_ids)
        cells = [c for c in cells if c["canonical_concept_id"] not in skip_concept_ids]
        stats["blanks"] = [
            b
            for b in stats["blanks"]
            if b.get("canonical_concept_id") not in skip_concept_ids
        ]
    with conn.cursor() as cur:
        cur.execute(
            "delete from analytics.canonical_fact where company_id = %s and canonical_concept_id = any(%s)",
            (company_id, sorted(targets)),
        )
        if cells:
            cur.executemany(
                """
                insert into analytics.canonical_fact
                    (company_id, canonical_concept_id, period_id, value, source_fact_ids, source_value_ids, family, rule_run_id)
                values (%s, %s, %s, %s, %s, %s, %s, %s::uuid)
                """,
                [
                    (
                        company_id,
                        c["canonical_concept_id"],
                        c["period_id"],
                        c["value"],
                        c["source_fact_ids"],
                        c["source_value_ids"],
                        FAMILY
                        if c["value_source"] == "sec_api"
                        else f"{FAMILY}:{c['value_source']}",
                        run_id,
                    )
                    for c in cells
                ],
            )
        cur.execute(
            "delete from analytics.company_combined_line where company_id = %s",
            (company_id,),
        )
        if stats["combined_lines"]:
            cur.executemany(
                """
                insert into analytics.company_combined_line
                    (company_id, period_id, stmt, taxonomy, tag, plabel, components, value,
                     source_fact_ids, tag_map_id, run_id)
                values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::uuid)
                """,
                [
                    (
                        company_id,
                        b["period_id"],
                        b["stmt"],
                        b["taxonomy"],
                        b["tag"],
                        b["plabel"],
                        b["components"],
                        b["value"],
                        b["source_fact_ids"],
                        b["tag_map_id"],
                        run_id,
                    )
                    for b in stats["combined_lines"]
                ],
            )
        if stats["blanks"]:
            if run_id is None:
                raise ValueError(
                    "blank reasons need the rule_run id of the resolve run"
                )
            _write_blanks(conn, company_id, run_id, stats["blanks"], concept_info)
        if commit:
            conn.commit()
    stats["resolved"] = len(cells)
    stats["held_cells"] = len(stats["held"])
    stats["cells"] = (
        cells  # the written rows (the write path protects exactly these keys)
    )
    stats["blank_cells"] = len(stats["blanks"])
    stats["combined_line_cells"] = len(stats["combined_lines"])
    logger.info(
        "company_tag_map.company_done",
        company_id=company_id,
        **{
            k: v
            for k, v in stats.items()
            if k not in ("held", "blanks", "blank_conflicts", "combined_lines", "cells")
        },
    )
    return stats


def _write_blanks(
    conn, company_id: int, run_id: str, blanks: list[dict], concept_info
) -> int:
    """Reasoned blanks into analytics.cell_blank_reason (state not_presented / not_in_template); the data point
    name is the canonical concept name; the reason and rule_id come from the map row."""
    from scrooner_pipeline.common import cell_store as cs
    from scrooner_pipeline.common.cell_contract import CellKey

    return cs.write_blank_reasons(
        conn,
        run_id,
        [
            cs.BlankReason(
                key=CellKey(
                    company_id,
                    b["concept_name"],
                    b["grain"],
                    b["period_start"],
                    b["period_end"],
                ),
                state=b["state"],
                rule_id=b["rule_id"],
                reason_code=b.get("reason_code", b["state"]),
                defect_class=b.get("defect_class"),
                owner=b.get("owner"),
                reason_text=b["reason"],
                input_refs={"source": "analytics.company_tag_map", "selector": RULE_ID},
            )
            for b in blanks
        ],
    )


def load_concept_info(conn: psycopg.Connection) -> dict[int, tuple[str, str]]:
    with conn.cursor() as cur:
        cur.execute("select id, name, statement from analytics.canonical_concept")
        return {i: (n, s) for i, n, s in cur.fetchall()}


def without_tag_map_ciks(conn: psycopg.Connection, ciks: set[str]) -> set[str]:
    """For the stages that rewrite canonical_fact after resolve (fallbacks, fills, dedup, split rebase): when rule
    company_tag_map.select@1 is ON, companies that have company_tag_map rows are skipped (the tag-map write path
    owns their cells). Flag off: returns ciks unchanged, no query."""
    if not enabled() or not ciks:
        return ciks
    with conn.cursor() as cur:
        cur.execute(
            """select c.cik from core.company c
               where c.cik = any(%s) and exists (select 1 from analytics.company_tag_map m where m.company_id = c.id)""",
            (sorted(ciks),),
        )
        skip = {r[0] for r in cur.fetchall()}
    return ciks - skip
