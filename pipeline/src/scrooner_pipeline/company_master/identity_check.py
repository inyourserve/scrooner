"""Identity invariant against the per-CIK SEC submissions JSON (rule
identity.cik_name_ticker@1, RF-20; Gate A step 1, GATE-A-IDENTITY-REGISTRANT-
CHECKS section 2). Pure: compares what we store with what SEC says; the caller
supplies both (the script fetches live or reads fixtures).

Why submissions and not company_tickers.json: that file lags renames (PSKY) and
drops acquired issuers (WBD), so it under-detects. The per-CIK JSON carries the
current name, the dated former names, the tickers and the filing list.

Findings are CANDIDATES for a reviewed fix, never an automatic edit:
  name_not_current              stored company_name is not SEC's current name
  ticker_not_in_submissions     stored primary ticker is not among SEC's tickers
                                (or SEC lists none)
  deregistration_after_last_periodic
                                a Form 25/25-NSE/15-12B/15-12G/15-15D is dated after the last
                                10-K/10-Q we hold (a Form 15 can cover preferred or plan
                                interests, so this still needs the class line read)
  name_or_ticker_event          an 8-K with Item 2.01/3.01/5.03 after the last periodic filing
  display_name_unrelated        vendor display name shares no word with the SEC
                                name or any former name (VMRK shown as AvalonBay)
  pseudo_ticker                 the "ticker" is a bond, preferred or subordinated note
                                of a subsidiary registrant, not common equity
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date

_SUFFIX = re.compile(r"\s*/[A-Za-z]{2,4}/?\s*$")
_CORP_WORDS = {
    "INC",
    "CORP",
    "CORPORATION",
    "CO",
    "COMPANY",
    "LTD",
    "LLC",
    "LP",
    "PLC",
    "THE",
    "L",
    "P",
    "C",
}
_DEREG_FORMS = {
    "25",
    "25-NSE",
    "15-12B",
    "15-12G",
    "15-15D",
    "15F-12B",
    "15F-12G",
    "15F-15D",
}
_EVENT_ITEMS = {"2.01", "3.01", "5.03"}
_PSEUDO_NAME = re.compile(
    r"\d+(\.\d+)?\s*%|\b(BD|NT|NTS|PFD|JR SUB|NOTES?|DEBENTURES?|PREFERRED|DEP SH)\b",
    re.I,
)
_PSEUDO_TICKER = re.compile(r"-P[A-Z]?$")


def norm_name(name: str | None) -> str:
    if not name:
        return ""
    s = _SUFFIX.sub("", name.strip()).upper().replace("&", " AND ")
    s = re.sub(r"[^A-Z0-9 ]+", " ", s)
    return " ".join(w for w in s.split() if w not in _CORP_WORDS)


def _words(name: str | None) -> set[str]:
    return set(norm_name(name).split()) - {"AND", "OF"}


@dataclass(frozen=True)
class StoredIdentity:
    cik: str
    company_name: str
    display_name: str | None
    primary_ticker: str | None
    status: str | None
    latest_periodic_date: date | None = None
    is_subsidiary_registrant: bool = False  # from core.filing_registrant (P1), optional


@dataclass(frozen=True)
class SecIdentity:
    cik: str
    name: str
    tickers: tuple[str, ...]
    former_names: tuple[str, ...]
    events: tuple[
        tuple[str, str, date, str], ...
    ] = ()  # (accession, form, date, items)

    @classmethod
    def from_submissions(cls, doc: dict) -> "SecIdentity":
        events = []
        for e in doc.get("events", []):
            events.append(
                (
                    e["accessionNumber"],
                    e["form"],
                    date.fromisoformat(e["filingDate"]),
                    e.get("items", ""),
                )
            )
        return cls(
            cik=str(doc["cik"]).zfill(10),
            name=doc["name"],
            tickers=tuple(doc.get("tickers", [])),
            former_names=tuple(f["name"] for f in doc.get("formerNames", [])),
            events=tuple(events),
        )


@dataclass(frozen=True)
class Finding:
    kind: str
    cik: str
    detail: str
    accessions: tuple[str, ...] = field(default=())


def compare_identity(stored: StoredIdentity, sec: SecIdentity) -> list[Finding]:
    out: list[Finding] = []
    cik = stored.cik

    if norm_name(stored.company_name) != norm_name(sec.name):
        former = norm_name(stored.company_name) in {
            norm_name(f) for f in sec.former_names
        }
        out.append(
            Finding(
                "name_not_current",
                cik,
                f"stored {stored.company_name!r} vs SEC {sec.name!r}"
                + (" (stored name is a former name)" if former else ""),
            )
        )

    if stored.primary_ticker:
        if not sec.tickers:
            out.append(
                Finding(
                    "ticker_not_in_submissions",
                    cik,
                    f"SEC lists no tickers; stored {stored.primary_ticker!r}",
                )
            )
        elif stored.primary_ticker not in sec.tickers:
            out.append(
                Finding(
                    "ticker_not_in_submissions",
                    cik,
                    f"stored {stored.primary_ticker!r} not in {list(sec.tickers)}",
                )
            )

    last = stored.latest_periodic_date
    dereg = [
        e for e in sec.events if e[1] in _DEREG_FORMS and (last is None or e[2] > last)
    ]
    if dereg:
        out.append(
            Finding(
                "deregistration_after_last_periodic",
                cik,
                "; ".join(f"{e[1]} {e[2]}" for e in dereg),
                tuple(e[0] for e in dereg),
            )
        )
    ev = [
        e
        for e in sec.events
        if e[1] == "8-K"
        and _EVENT_ITEMS & set(e[3].split(","))
        and (last is None or e[2] > last)
    ]
    if ev:
        out.append(
            Finding(
                "name_or_ticker_event",
                cik,
                "; ".join(f"8-K {e[2]} items {e[3]}" for e in ev),
                tuple(e[0] for e in ev),
            )
        )

    if stored.display_name:
        known = _words(sec.name)
        for f in sec.former_names:
            known |= _words(f)
        if not (_words(stored.display_name) & known):
            out.append(
                Finding(
                    "display_name_unrelated",
                    cik,
                    f"{stored.display_name!r} vs SEC {sec.name!r}",
                )
            )

    if stored.primary_ticker and (
        _PSEUDO_TICKER.search(stored.primary_ticker)
        or (stored.display_name and _PSEUDO_NAME.search(stored.display_name))
    ):
        out.append(
            Finding(
                "pseudo_ticker",
                cik,
                f"{stored.primary_ticker!r} / {stored.display_name!r} looks like a bond, preferred or note"
                + (
                    "; company is a subsidiary registrant"
                    if stored.is_subsidiary_registrant
                    else ""
                ),
            )
        )
    return out
