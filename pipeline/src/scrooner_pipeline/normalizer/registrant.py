"""P1 -- rule entity.shared_accession_primary_filer@1 (RF-21).

Problem (GATE-A-IDENTITY-REGISTRANT-CHECKS section 3, FILING-CHECKED on Entergy
0000065984-26-000174 and seven more accessions): a combined filing (Entergy,
Southern, Sempra, Edison, Eversource, Duke ... ) is ONE accession with several
registrants. core.filing is unique on accession_number and its upsert never
updates company_id, so the first CIK normalized claims the accession for ever,
and SEC companyfacts serves a parent's facts under a subsidiary's CIK for four
groups' Q2 2026 10-Qs. Result: nine large parents (SO, SRE, AEE, ETR, CTVA, EIX,
CMS, ES, TXNM) are stale and subsidiaries publish the parent's figures.

Rule (the instance is the evidence, not the SEC API):
- The PRIMARY filer of a shared accession is the CIK in the instance's
  UNDIMENSIONED (default-context) dei:EntityCentralIndexKey, corroborated by
  the FIRST FILER block of the submission header.
- If the two disagree, or the default-context CIK is missing, ambiguous or not a
  header filer, the whole accession is QUARANTINED (no company loads its facts)
  and a row with a reason is written; nobody guesses.
- Never use: the accession prefix (agent-filed: Eversource 0001628280; filer
  account reuse: WEC 0000107815-25-000182), companyfacts attribution (SEC
  moved four groups' Q2 2026 10-Qs to subsidiaries), dei:LegalEntityAxis in
  companyfacts (stripped), CIK sort order (the old behavior).
- A single-FILER accession is not shared: its filer is the primary (a dei CIK
  that contradicts the sole filer still quarantines it).

This module is pure (parsing and the decision). Fetching goes through
common/sec_client.py in scripts/p1_reload_dryrun.py, never from here. The
loader hooks (identity.py, facts.py, periods.py) are active only with the rule
flag on.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from html import unescape

from lxml import etree

_CIK_RE = re.compile(r"^\d{1,10}$")
_XBRLI = "http://www.xbrl.org/2003/instance"
_XBRLDI = "http://xbrl.org/2006/xbrldi"


def normalize_cik(value: str | int) -> str:
    s = str(value).strip()
    if not _CIK_RE.match(s):
        raise ValueError(f"not a CIK: {value!r}")
    return s.zfill(10)


# ------------------------------------------------------------------ header
_FILER_BLOCK_XML = re.compile(r"<FILER>(.*?)</FILER>", re.S)
_CIK_TAG = re.compile(r"<CIK>\s*(\d{1,10})")
_TOP_BLOCK_HEAD = re.compile(r"^([A-Z][A-Z ]+):\s*$", re.M)  # unindented, e.g. 'FILER:'
_CIK_LABEL = re.compile(r"CENTRAL INDEX KEY:\s*(\d{1,10})")


def parse_header_filers(header: str) -> list[str]:
    """Registrant CIKs of the FILER blocks, in header order, unique.

    Understands the SGML tag form (`<FILER> ... <CIK>0000065984 ... </FILER>`,
    the `.hdr.sgml` / `-index-headers.html` text) and the labelled text form
    (`FILER:` / `COMPANY DATA:` / `CENTRAL INDEX KEY:`). Other top-level blocks
    (SUBJECT COMPANY, FILED BY) are not registrants of a periodic report and
    are ignored."""
    text = unescape(
        re.sub(r"<(?!/?(?:FILER|CIK|SUBJECT-COMPANY|FILED-BY)\b)[^>]*>", "", header)
    )
    ciks: list[str] = []

    def add(raw: str) -> None:
        cik = normalize_cik(raw)
        if cik not in ciks:
            ciks.append(cik)

    blocks = _FILER_BLOCK_XML.findall(text)
    if blocks:
        for block in blocks:
            m = _CIK_TAG.search(block)
            if m:
                add(m.group(1))
        return ciks

    heads = list(_TOP_BLOCK_HEAD.finditer(text))
    for i, h in enumerate(heads):
        if h.group(1) != "FILER":
            continue
        end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
        m = _CIK_LABEL.search(text[h.end() : end])
        if m:
            add(m.group(1))
    return ciks


# ---------------------------------------------------------------- instance
class AmbiguousDeiCik(ValueError):
    """Two different undimensioned dei:EntityCentralIndexKey values."""


def extract_default_context_cik(document: bytes) -> str | None:
    """The undimensioned dei:EntityCentralIndexKey of an XBRL instance
    (classic `<xbrl>` XML or inline XBRL XHTML). None when absent. Raises
    AmbiguousDeiCik if the default context carries two different values.
    Untrusted input: no entity resolution, no network."""
    parser = etree.XMLParser(huge_tree=True, resolve_entities=False, no_network=True)
    root = etree.fromstring(document, parser)
    dimensioned: dict[str, bool] = {}
    for el in root.iter():
        if not isinstance(el.tag, str):
            continue
        if (
            etree.QName(el).localname == "context"
            and etree.QName(el).namespace == _XBRLI
        ):
            cid = el.get("id")
            if cid is None:
                continue
            has_dim = any(
                isinstance(d.tag, str)
                and etree.QName(d).namespace == _XBRLDI
                and etree.QName(d).localname in ("explicitMember", "typedMember")
                for d in el.iter()
            )
            dimensioned[cid] = has_dim
    found: set[str] = set()
    for el in root.iter():
        if not isinstance(el.tag, str):
            continue
        local = etree.QName(el).localname
        is_fact = (local == "EntityCentralIndexKey") or (
            local == "nonNumeric" and el.get("name") == "dei:EntityCentralIndexKey"
        )
        if not is_fact:
            continue
        ctx = el.get("contextRef")
        if ctx is None or dimensioned.get(ctx, True):
            continue  # unknown context or a dimensioned (member) context
        value = "".join(el.itertext()).strip()
        if value:
            found.add(normalize_cik(value))
    if len(found) > 1:
        raise AmbiguousDeiCik(f"default context carries {sorted(found)}")
    return next(iter(found)) if found else None


# ---------------------------------------------------------------- decision
PRIMARY = "primary"
CO_REGISTRANT = "co_registrant"
QUARANTINED = "quarantined"


@dataclass(frozen=True)
class PrimaryFilerDecision:
    accession_number: str
    registrant_ciks: tuple[str, ...]
    dei_default_cik: str | None
    header_first_filer_cik: str | None
    primary_cik: str | None
    shared: bool
    quarantine_reason: str | None

    @property
    def quarantined(self) -> bool:
        return self.quarantine_reason is not None

    def role_of(self, cik: str) -> str:
        if self.quarantined:
            return QUARANTINED
        return PRIMARY if cik == self.primary_cik else CO_REGISTRANT


def decide_primary(
    accession_number: str,
    dei_default_cik: str | None,
    header_filers: Iterable[str],
) -> PrimaryFilerDecision:
    filers = tuple(dict.fromkeys(normalize_cik(c) for c in header_filers))
    dei = normalize_cik(dei_default_cik) if dei_default_cik else None
    first = filers[0] if filers else None
    shared = len(filers) >= 2

    def quarantine(reason: str) -> PrimaryFilerDecision:
        return PrimaryFilerDecision(
            accession_number, filers, dei, first, None, shared, reason
        )

    if not filers:
        return quarantine("no FILER block in the submission header")
    if not shared:
        if dei is not None and dei != first:
            return quarantine(
                f"dei default-context CIK {dei} is not the sole filer {first}"
            )
        return PrimaryFilerDecision(
            accession_number, filers, dei, first, first, False, None
        )
    if dei is None:
        return quarantine(
            "shared accession without a default-context dei:EntityCentralIndexKey"
        )
    if dei not in filers:
        return quarantine(f"dei default-context CIK {dei} is not a header filer")
    if dei != first:
        return quarantine(
            f"dei default-context CIK {dei} disagrees with the first header filer {first}"
        )
    return PrimaryFilerDecision(accession_number, filers, dei, first, dei, True, None)


# --------------------------------------------------------------- candidates
def find_shared_accessions(
    accessions_by_cik: Mapping[str, Iterable[str]],
) -> dict[str, set[str]]:
    """Accessions listed in the submissions of 2 or more CIKs -> the CIKs.
    SEC lists a combined filing in every registrant's submissions."""
    seen: dict[str, set[str]] = {}
    for cik, accessions in accessions_by_cik.items():
        for acc in accessions:
            seen.setdefault(acc, set()).add(normalize_cik(cik))
    return {a: c for a, c in seen.items() if len(c) >= 2}


def accession_prefix_cik(accession_number: str) -> str:
    """CIK of the filer-ID prefix. Only a CANDIDATE signal (agents and reused
    filer accounts make it wrong, e.g. WEC): never an attribution rule."""
    return normalize_cik(accession_number.split("-")[0])
