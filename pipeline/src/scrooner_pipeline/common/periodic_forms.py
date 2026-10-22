"""The ONE definition of which SEC form types carry a registrant's own
financial statements (W3, rule source.periodic_form_only@1; AT-DE-09).

Two named sets, because two different questions need different answers:

- PERIODIC_FORMS_DOMESTIC: 10-K / 10-Q family (incl. 10-KT, 10-QT and their
  amendments). The only forms that can feed a derived quarter: a domestic
  issuer's Q1-Q3 come from 10-Qs and Q4 is FY minus YTD. Foreign private
  issuers (20-F/40-F) are outside V1 scope (doc 02) and file no 10-Q, so
  they have no quarter chain. Same name and members as the Period Engineer's
  held common/derivation_policy.py (RU-1), which should import it from here.
- PERIODIC_FORMS_ALL: domestic + 20-F/40-F (+ amendments). The authority
  question "may this form be the source of a stored annual or interim value"
  (Stage 2e, certification, staleness). A 20-F filer's statements are its own
  statements; demoting them would blank every FPI still in core.company
  before the scope decision on FPIs is taken.

Everything else (DEF 14A, 8-K, S-1/424B, 10-12B, 11-K, ...) is never the
source of a statement value (data-team/34 I6; ledger 2026-10-18 AEMD, 2026-10-22
JPM DEF 14A 0000019617-26-000096 R2: net income printed rounded to $0.1B).
"""

PERIODIC_FORMS_DOMESTIC = frozenset(
    {
        "10-K",
        "10-K/A",
        "10-KT",
        "10-KT/A",
        "10-Q",
        "10-Q/A",
        "10-QT",
        "10-QT/A",
    }
)

FOREIGN_PERIODIC_FORMS = frozenset({"20-F", "20-F/A", "40-F", "40-F/A"})

PERIODIC_FORMS_ALL = PERIODIC_FORMS_DOMESTIC | FOREIGN_PERIODIC_FORMS

# Stable order for SQL text and tuples (common/staleness.PERIODIC_FORMS keeps
# its historical order so generated SQL does not change).
PERIODIC_FORMS_ALL_ORDERED = (
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


# Which periodic forms may WIN a conflict in Stage 2e-b (conflict_latest_filed),
# built here so the lists cannot drift from PERIODIC_FORMS_ALL. An annual flow
# fact comes from an annual report; a discrete quarter from a quarterly report or
# from the annual report that closes the year.
ANNUAL_FORMS_ALL = (
    "10-K",
    "10-K/A",
    "10-KT",
    "10-KT/A",
    "20-F",
    "20-F/A",
    "40-F",
    "40-F/A",
)
QUARTERLY_FORMS = ("10-Q", "10-Q/A", "10-QT", "10-QT/A")
assert set(ANNUAL_FORMS_ALL) | set(QUARTERLY_FORMS) == PERIODIC_FORMS_ALL


def is_periodic_form(form: str | None) -> bool:
    """Domestic periodic report (derivation sources)."""
    return form is not None and form.strip().upper() in PERIODIC_FORMS_DOMESTIC


def is_periodic_source_form(form: str | None) -> bool:
    """Any periodic report incl. 20-F/40-F (authority / certification)."""
    return form is not None and form.strip().upper() in PERIODIC_FORMS_ALL
