"""Shared (combined-filing) accessions: who is the primary filer, who are the
co-registrants (rule entity.shared_accession_primary_filer@1, flag-gated).

THE DEFECT (root cause, read from code 2026-10-26)
  A combined 10-K/10-Q (Entergy Corp + Entergy Arkansas + ..., Ameren Corp +
  Ameren Illinois, Corteva + EIDP) is ONE accession listed in the submissions
  JSON of EVERY registrant. Two places make the first company normalized own it
  forever:
    1. normalizer/identity.upsert_filings: `on conflict (accession_number) do
       update set filing_date..., items...` never updates company_id, so the
       registrant normalized first (Entergy Arkansas id 142, Ameren Illinois id
       257, EIDP id 351) keeps the row; the parent's own insert is a no-op.
    2. normalizer/facts._load_filing_lookup keeps only `where company_id = X`,
       so every companyfacts entry of the parent whose accn is owned by the
       co-registrant is counted `skipped_no_filing` and dropped.
  SEC attributes a combined filing's facts to ONE CIK in companyfacts (the
  parent/primary: ETR's payload carries 70 accessions incl. 16 10-Ks; Entergy
  Arkansas' payload carries 1 accession; zero overlap), so the parent loses all
  of its combined-filing history. company_master/status.py then sees no 10-K/10-Q
  owned by the parent and writes 'stale' (no_filing_since:2010-09-03 for ETR).

THE RULE
  registrants(accession) = every core.company whose latest submissions payload
    lists the accession (SEC itself lists a combined filing under each
    registrant). Only accessions with 2+ registrants are "shared".
  primary(accession), in this evidence order:
    1. companyfacts: exactly one registrant's companyfacts payload carries the
       accession (SEC's own attribution of the filing's facts). DATA-INFERRED
       from SEC feeds; FSN `sub.cik` is expected to agree (gate: Verifier check).
    2. no registrant's payload carries it (periodic forms only): the registrant
       whose CIK equals the accession-number prefix (the filer ID that submitted
       it). Non-periodic forms (8-K, 144, proxy) without payload evidence are
       quarantined: the prefix is only the submitter and is too weak to move
       ownership.
    3. otherwise quarantined: no primary, nothing is re-attributed.
    More than one payload carrying the accession is also quarantined.
  All registrants are kept in core.filing_registrant (role primary |
  co_registrant | quarantined), written only for shared accessions.

  Fact attribution: a fact comes from a company's OWN companyfacts payload and
  is attributed to that company; the filing row it points at is the shared
  core.filing row (looked up via owner OR primary-registrant link).
  Status: a company is not 'stale' while any filing it is a registrant of is
  recent (company_master/status.py, flag on).
  Re-attribution: core.filing.company_id of a shared accession moves to the
  primary; the former owner stays in core.filing_registrant as co_registrant.
  Facts of a non-primary company on a shared accession are NOT deleted by this
  module (reported only; Verifier decides).

Pure functions here; the SQL writers are explicit and refuse to run unless the
rule is ON. Nothing is applied by importing this module.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from scrooner_pipeline.common.rule_flags import (
    RULE_SHARED_ACCESSION_PRIMARY,
    rule_enabled,
)

RULE_ID = RULE_SHARED_ACCESSION_PRIMARY

PERIODIC_FORMS = frozenset(
    {"10-K", "10-K/A", "10-Q", "10-Q/A", "20-F", "20-F/A", "40-F", "40-F/A"}
)



@dataclass(frozen=True)
class Decision:
    accession_number: str
    registrant_ciks: tuple[str, ...]
    primary_cik: str | None
    basis: str | None  # agreeing signals e.g. 'header+prefix+payload'; None when quarantined
    quarantine_reason: str | None
    carriers: tuple[str, ...]  # registrants whose companyfacts carry the accession
    header_first_filer: str | None = None  # first FILER block of the SEC header, if read


def carrier_conflict(d: Decision) -> bool:
    """True when a payload carries the accession's facts but is NOT the primary:
    those facts are another registrant's numbers filed under the wrong CIK."""
    return d.primary_cik is not None and any(c != d.primary_cik for c in d.carriers)


def accession_prefix_cik(accession_number: str) -> str:
    """Filer ID that submitted the accession (first block), zero-padded to 10."""
    return accession_number.split("-", 1)[0].zfill(10)


def registrants_by_accession(
    filings_by_cik: Mapping[str, Iterable[dict]],
) -> dict[str, dict[str, str]]:
    """accession -> {cik: form}, only accessions listed by 2+ CIKs.
    `filings_by_cik` rows are identity._parse_filings_block dicts."""
    seen: dict[str, dict[str, str]] = defaultdict(dict)
    for cik, filings in filings_by_cik.items():
        for f in filings:
            seen[f["accession_number"]][cik] = f["form"]
    return {a: d for a, d in seen.items() if len(d) >= 2}


def decide(
    accession_number: str,
    registrant_ciks: Iterable[str],
    carrier_ciks: Iterable[str],
    form: str | None = None,
    header_first_filer: str | None = None,
) -> Decision:
    """Primary = the registrant backed by at least TWO independent signals and
    strictly more than any other registrant:
      H  first FILER block of the submission header   (FILING-CHECKED, may be None)
      P  accession-number prefix (submitter filer ID)  (periodic forms only)
      C  the single registrant whose companyfacts payload carries the accession
    Why not "the carrier alone": FILING-CHECKED 2026-10-26, SEC companyfacts attributes
    the latest combined 10-Q of Entergy / Edison / Sempra to a SUBSIDIARY CIK (Arkansas
    7323 / SCE 92103 / SoCalGas 92108) with the parent's consolidated values
    (Assets 71.89B = Entergy Corp). H and P name the parent there; C alone would hand
    the parent's numbers to the subsidiary. Why not "header alone": Southern Co's 2017
    10-K lists Alabama Power first while P and C name Southern Co.
    Fewer than two agreeing signals -> quarantined; nothing is re-attributed."""
    regs = tuple(sorted(set(registrant_ciks)))
    regset = set(regs)
    carriers = tuple(sorted(set(carrier_ciks) & regset))
    votes: dict[str, list[str]] = defaultdict(list)
    if header_first_filer and header_first_filer in regset:
        votes[header_first_filer].append("header")
    prefix = accession_prefix_cik(accession_number)
    if (form is None or form in PERIODIC_FORMS) and prefix in regset:
        votes[prefix].append("prefix")
    if len(carriers) == 1:
        votes[carriers[0]].append("payload")
    if not carriers and (form is not None and form not in PERIODIC_FORMS):
        return Decision(
            accession_number, regs, None, None, "non_periodic_without_payload_evidence",
            carriers, header_first_filer,
        )
    ranked = sorted(votes.items(), key=lambda kv: (-len(kv[1]), kv[0]))
    if len(carriers) > 1 and not ranked:
        return Decision(
            accession_number,
            regs,
            None,
            None,
            "multiple_companyfacts_payloads_carry_accession",
            carriers,
            header_first_filer,
        )
    if ranked and len(ranked[0][1]) >= 2 and (
        len(ranked) == 1 or len(ranked[1][1]) < len(ranked[0][1])
    ):
        cik, signals = ranked[0]
        return Decision(
            accession_number, regs, cik, "+".join(signals), None, carriers, header_first_filer
        )
    reason = "no_primary_evidence" if not ranked else "signals_do_not_agree"
    return Decision(accession_number, regs, None, None, reason, carriers, header_first_filer)


def plan_decisions(
    shared: Mapping[str, Mapping[str, str]],
    carriers_by_accession: Mapping[str, Iterable[str]],
    header_first_by_accession: Mapping[str, str | None] | None = None,
) -> list[Decision]:
    headers = header_first_by_accession or {}
    return [
        decide(
            a,
            regs.keys(),
            carriers_by_accession.get(a, ()),
            next(iter(regs.values())),
            headers.get(a),
        )
        for a, regs in sorted(shared.items())
    ]


# ---- SQL writers (apply path; refuse unless the rule is ON) -----------------

_UPSERT_REGISTRANT = """
insert into core.filing_registrant
    (accession_number, registrant_cik, company_id, role, filer_count,
     quarantine_reason, header_first_filer_cik, rule_id)
values (%(accession_number)s, %(registrant_cik)s, %(company_id)s, %(role)s,
        %(filer_count)s, %(quarantine_reason)s, %(header_first_filer_cik)s, %(rule_id)s)
on conflict (accession_number, registrant_cik) do update
    set company_id = excluded.company_id, role = excluded.role,
        filer_count = excluded.filer_count,
        quarantine_reason = excluded.quarantine_reason,
        header_first_filer_cik = excluded.header_first_filer_cik,
        rule_id = excluded.rule_id, determined_at = now()
"""

_REOWN_FILING = """
update core.filing set company_id = %(company_id)s
 where accession_number = %(accession_number)s
   and company_id is distinct from %(company_id)s
"""


def registrant_rows(
    decisions: Iterable[Decision], company_id_by_cik: Mapping[str, int]
) -> list[dict]:
    rows = []
    for d in decisions:
        for cik in d.registrant_ciks:
            if d.primary_cik is None:
                role = "quarantined"
            elif cik == d.primary_cik:
                role = "primary"
            else:
                role = "co_registrant"
            rows.append(
                {
                    "accession_number": d.accession_number,
                    "registrant_cik": cik,
                    "company_id": company_id_by_cik.get(cik),
                    "role": role,
                    "filer_count": len(d.registrant_ciks),
                    "quarantine_reason": d.quarantine_reason
                    if role == "quarantined"
                    else None,
                    "header_first_filer_cik": d.header_first_filer,
                    "rule_id": RULE_ID,
                }
            )
    return rows


def apply_decisions(
    conn, decisions: list[Decision], company_id_by_cik: Mapping[str, int]
) -> dict:
    """Writes core.filing_registrant and moves core.filing.company_id to the
    primary. Raises unless the rule is ON; one transaction (rollback on error)."""
    if not rule_enabled(RULE_ID):
        raise RuntimeError(f"{RULE_ID} is not ON; refusing to write")
    rows = registrant_rows(decisions, company_id_by_cik)
    reown = [
        {
            "accession_number": d.accession_number,
            "company_id": company_id_by_cik[d.primary_cik],
        }
        for d in decisions
        if d.primary_cik is not None and d.primary_cik in company_id_by_cik
    ]
    with conn.cursor() as cur:
        cur.executemany(_UPSERT_REGISTRANT, rows)
        cur.executemany(_REOWN_FILING, reown)
    conn.commit()
    return {"registrant_rows": len(rows), "filings_considered_for_reown": len(reown)}


# ---- evidence gathering (read-only) -----------------------------------------


def build_plan(
    filings_by_cik: Mapping[str, list[dict]],
    carrier_accessions_fn,
    header_first_filer_fn=None,
) -> list[Decision]:
    """filings_by_cik: cik -> identity filing dicts (whole population in scope).
    carrier_accessions_fn(cik, wanted: set[str]) -> accessions among `wanted`
    that this cik's companyfacts payload carries. Only registrants of shared
    accessions are asked, and only about their shared accessions."""
    shared = registrants_by_accession(filings_by_cik)
    wanted_by_cik: dict[str, set[str]] = defaultdict(set)
    for accession_number, regs in shared.items():
        for cik in regs:
            wanted_by_cik[cik].add(accession_number)
    carriers: dict[str, set[str]] = defaultdict(set)
    for cik, wanted in sorted(wanted_by_cik.items()):
        for accession_number in carrier_accessions_fn(cik, wanted):
            carriers[accession_number].add(cik)
    headers: dict[str, str | None] = {}
    if header_first_filer_fn is not None:
        for accession_number, regs in shared.items():
            form = next(iter(regs.values()))
            if form in PERIODIC_FORMS or accession_number in carriers:
                headers[accession_number] = header_first_filer_fn(
                    accession_number, sorted(regs)
                )
    return plan_decisions(shared, carriers, headers)


def summarize(decisions: Iterable[Decision]) -> dict:
    out = {"shared_accessions": 0, "primary": 0, "quarantined": 0}
    by_basis: dict[str, int] = defaultdict(int)
    for d in decisions:
        out["shared_accessions"] += 1
        if d.primary_cik is None:
            out["quarantined"] += 1
            by_basis[d.quarantine_reason or "?"] += 1
        else:
            out["primary"] += 1
            by_basis[d.basis or "?"] += 1
    out["by_basis"] = dict(by_basis)
    return out
