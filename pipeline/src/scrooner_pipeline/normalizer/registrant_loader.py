"""Loader side of P1 (entity.shared_accession_primary_filer@1, RF-21): what the
Normalizer stages do with the registrant decisions stored in
core.filing_registrant (migration 0100). Active only with the rule flag on
(common/rule_flags.py); with it off every function here is a no-op and the
stages behave exactly as before.

- identity: a company never claims an accession on which it is a co-registrant
  or which is quarantined (`filings_to_skip`). core.filing.company_id is still
  never UPDATEd by the identity upsert: moving an existing claim is the
  reviewed reload (registrant_reload.py), not a side effect of a nightly.
- periods / facts: the primary filer's payload is rebuilt from every payload that
  SEC serves its accessions under (`adjust_payload`): entries of accessions this
  company is only a co-registrant of or that are quarantined are dropped from
  its own payload, and entries of accessions it is primary for are merged in
  from the co-registrants' payloads (SEC served the Q2 2026 10-Qs of Entergy,
  Sempra, Southern and Edison under a subsidiary's CIK). Each merged entry
  carries the raw object it came from, so provenance stays exact.
"""

from __future__ import annotations

import copy
from collections.abc import Callable, Iterable

import psycopg

from scrooner_pipeline.common.rule_flags import (
    RULE_SHARED_ACCESSION_PRIMARY,
    rule_enabled,
)

RAW_OBJECT_KEY = "_raw_object_id"


def flag_on() -> bool:
    return rule_enabled(RULE_SHARED_ACCESSION_PRIMARY)


def registrant_roles(
    conn: psycopg.Connection, cik: str
) -> dict[str, tuple[str, list[str]]]:
    """accession -> (this cik's role, [co-registrant ciks that are not this one])
    for every accession on which `cik` is a recorded registrant."""
    with conn.cursor() as cur:
        cur.execute(
            """
            select r.accession_number, r.role,
                   coalesce((select array_agg(o.registrant_cik order by o.registrant_cik)
                             from core.filing_registrant o
                             where o.accession_number = r.accession_number
                               and o.registrant_cik <> r.registrant_cik), '{}')
            from core.filing_registrant r
            where r.registrant_cik = %s
            """,
            (cik,),
        )
        return {a: (role, list(others)) for a, role, others in cur.fetchall()}


def filings_to_skip(conn: psycopg.Connection, cik: str) -> set[str]:
    """Accessions this company must not claim: co-registrant or quarantined."""
    if not flag_on():
        return set()
    return {
        acc
        for acc, (role, _others) in registrant_roles(conn, cik).items()
        if role != "primary"
    }


def _entries(payload: dict) -> Iterable[tuple[dict, str]]:
    for taxonomy, concepts in payload.get("facts", {}).items():
        for tag, cdata in concepts.items():
            for unit, entries in cdata.get("units", {}).items():
                for e in entries:
                    yield e, f"{taxonomy}|{tag}|{unit}"


def filter_payload(
    payload: dict, keep: Callable[[str | None], bool], tag_raw_id: int | None = None
) -> dict:
    """Copy of a companyfacts payload keeping only entries whose accn passes
    `keep`. Optionally stamps each kept entry with its raw object id."""
    out = copy.deepcopy(payload)
    for concepts in out.get("facts", {}).values():
        for cdata in concepts.values():
            for unit in list(cdata.get("units", {})):
                kept = [e for e in cdata["units"][unit] if keep(e.get("accn"))]
                if tag_raw_id is not None:
                    for e in kept:
                        e[RAW_OBJECT_KEY] = tag_raw_id
                cdata["units"][unit] = kept
    return out


def merge_payloads(base: dict, extra: dict) -> dict:
    """Add the entries of `extra` that `base` does not already hold (identity of
    an entry = tag, unit, accn, start, end, val). `base` is not modified."""
    out = copy.deepcopy(base)
    out.setdefault("facts", {})
    have: set[tuple] = set()
    for e, key in _entries(out):
        have.add((key, e.get("accn"), e.get("start"), e.get("end"), str(e.get("val"))))
    for taxonomy, concepts in extra.get("facts", {}).items():
        for tag, cdata in concepts.items():
            for unit, entries in cdata.get("units", {}).items():
                target = (
                    out["facts"]
                    .setdefault(taxonomy, {})
                    .setdefault(tag, {k: v for k, v in cdata.items() if k != "units"})
                    .setdefault("units", {})
                    .setdefault(unit, [])
                )
                for e in entries:
                    ident = (
                        f"{taxonomy}|{tag}|{unit}",
                        e.get("accn"),
                        e.get("start"),
                        e.get("end"),
                        str(e.get("val")),
                    )
                    if ident in have:
                        continue
                    have.add(ident)
                    target.append(e)
    return out


def adjust_payload(
    conn: psycopg.Connection,
    cik: str,
    payload: dict,
    load_payload: Callable[[str], tuple[int, dict] | None],
) -> dict:
    """The payload a Normalizer stage should use for `cik` (see module doc).
    `load_payload(co_cik)` returns (raw_object_id, payload) of a
    co-registrant, or None. Flag off or no registrant rows: `payload` itself."""
    if not flag_on():
        return payload
    roles = registrant_roles(conn, cik)
    if not roles:
        return payload
    drop = {a for a, (role, _o) in roles.items() if role != "primary"}
    own = {a for a, (role, _o) in roles.items() if role == "primary"}
    result = filter_payload(payload, lambda accn: accn not in drop) if drop else payload
    co_ciks = sorted({c for a in own for c in roles[a][1]})
    for co in co_ciks:
        loaded = load_payload(co)
        if loaded is None:
            continue
        raw_id, co_payload = loaded
        # only the entries of accessions this company is primary for, and
        # never an accession some other company is primary for
        extra = filter_payload(co_payload, lambda accn: accn in own, tag_raw_id=raw_id)
        result = merge_payloads(result, extra)
    return result
