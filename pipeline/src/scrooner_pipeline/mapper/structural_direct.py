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
mapped, component_sum (derived_not_printed stays with the derived path). A filing whose own calc check FAILs is
quarantined (structural_loader.quarantined). Pure parts are unit-testable; the DB reads are two indexed queries.
"""

from __future__ import annotations

import os
from collections import defaultdict
from datetime import date
from decimal import Decimal
from functools import lru_cache
from pathlib import Path
from typing import Any

import psycopg

from scrooner_pipeline.common.authority import face_column_eligible, latest_eligible
from scrooner_pipeline.common.fsn_dates import era_holds, fsn_end_matches
from scrooner_pipeline.common.polarity import apply_polarity, flip_note
from scrooner_pipeline.mapper import docmap_loader as dl
from scrooner_pipeline.mapper import structural_loader as sl

FIX_RULE_ID = "company_tag_map.docmap_fix@1"
ENV_PATH = "SCROONER_STRUCTURAL_RESOLVER"
ENV_OFF = "SCROONER_STRUCTURAL_DIRECT"  # "off" disables the path
LINE_MAP_DIR = Path(__file__).resolve().parents[4] / "data-team" / "tags" / "line_map"
SERVED = ("mapped", "component_sum")


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
        if c.decision in SERVED and c.cik:
            out[c.cik].append(c)
    return {k: tuple(v) for k, v in out.items()}


def enabled() -> bool:
    return os.environ.get(ENV_OFF, "on").lower() != "off"


def _period_id(
    periods: dict[int, tuple[date, date, str]], end: date, grain: str
) -> tuple[int, date] | None:
    """The unique core.period (id, true end) of the claim's column: instants (grain I) or about-a-year durations (FY).
    The resolver's period_end is the FSN date, rounded to a month end (a 52/53-week year ending 2015-12-26 is
    2015-12-31 there): matched by common/fsn_dates, the exact end preferred when two periods match."""
    want = "instant" if grain == "I" else "duration"
    hits = [
        pid
        for pid, (start, e, ptype) in periods.items()
        if ptype == want
        and fsn_end_matches(end, e)
        and (want == "instant" or 330 <= (e - start).days <= 400)
    ]
    if len(hits) > 1:
        exact = [pid for pid in hits if periods[pid][1] == end]
        hits = exact if len(exact) == 1 else hits
    return (hits[0], periods[hits[0]][1]) if len(hits) == 1 else None


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
        r.rule_id == FIX_RULE_ID
        and r.decision != "excluded"
        and concept_id in (r.canonical_concept_id, r.parent_concept_id)
        and era_holds(r.era_from, r.era_to, end)
        for r in rows
    )


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
    stats: dict[str, Any] = {"claims": 0, "served": 0, "rejected": [], "fix_won": 0}
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
    tags = {tag for cs in groups.values() for c in cs for _s, _t, tag in c.parts}
    col = {k: _period_id(periods, k[1], k[2]) for k in groups}
    ends = {v[1] for v in col.values() if v}
    stored = _stored_values(conn, company_id, accessions, tags, ends)
    cells: list[dict] = []
    for (name, end, grain), cs in sorted(groups.items(), key=lambda kv: repr(kv[0])):
        cid = ids[name]

        def reject(why: str, name: str = name, end: date = end) -> None:
            stats["rejected"].append(
                {"concept": name, "period_end": end.isoformat(), "why": why}
            )

        located = col[(name, end, grain)]
        if located is None:
            reject("no unique core.period for the claim's column")
            continue
        pid, te = located
        if _fix_covers(rows, cid, te):
            stats["fix_won"] += 1
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
        if c.decision == "component_sum" and periods[pid][2] == "instant":
            if sl.instant_sum_refused(name, concept_info[cid][1]):
                reject("instant component sum refused (only total_debt)")
                continue
        parts: list[tuple[int, str, Decimal, str, set[int]]] = []
        bad = None
        for i, (sign, _tax, tag) in enumerate(c.parts):
            want = (
                Decimal(c.node_values[i])
                if i < len(c.node_values) and c.node_values[i]
                else None
            )
            got = _part_value(stored[(c.accession, tag, te)], want)
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
        if c.decision == "mapped":
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
        fsn_src = any(p[3] == "fsn_xbrl" for p in parts)
        core_ids = sorted({i for p in parts if p[3] == "sec_api" for i in p[4]})
        vids = sorted({i for p in parts if p[3] == "fsn_xbrl" for i in p[4]})
        note = (
            f"structural resolver direct: {c.accession} column {end.isoformat()} "
            + "; ".join(f"{t}={v}" for _s, t, v, _x, _f in parts)
            + (f"; filing checks: {c.checks}" if c.checks else "")
        )
        if flipped:
            note += "; " + flip_note(parts[0][2])
        fid = meta[c.accession][0]
        cells.append(
            {
                "canonical_concept_id": cid,
                "period_id": pid,
                "value": served,
                "value_source": "fsn_xbrl" if fsn_src else "sec_api",
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
    return cells, stats


def apply_direct(
    conn: psycopg.Connection, cells: list[dict], stats: dict, direct: list[dict]
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
    stats["blanks"] = [
        b
        for b in stats.get("blanks", [])
        if (b.get("canonical_concept_id"), b.get("period_id")) not in keys
    ]
    return len(use)
