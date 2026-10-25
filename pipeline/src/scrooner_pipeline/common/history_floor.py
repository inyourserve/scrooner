"""Storage history floor for the Normalizer (founder decision 2026-10-25).

core keeps facts and periods whose END date is on or after HISTORY_FLOOR
(2014-01-01). Anything ending earlier is not materialised. The raw SEC
payload in Storage still holds all history, so this is re-derivable.

This is the STORAGE floor. It is deliberately different from the DISPLAY
floor (2015-01-01, doc 38 rule 5, `sanity/period_completeness.py
HISTORY_START`): one calendar year more is kept so that 2015 growth,
opening balances (the 2014-12-31 instants) and 2015 derived quarters of
non-calendar fiscal years stay computable. Do not merge the two constants.

Boundary rule (decided on `end`, never on `start`): a duration that starts
before the floor and ends on or after it is KEPT (5,519 such periods exist),
an instant dated 2013-12-31 is DROPPED.

Design refs: data-team/strategy/team/STORAGE-DELETE-DRYRUN-2026-10-25.md
section 7.4.
"""

from datetime import date

HISTORY_FLOOR = date(2014, 1, 1)


def is_before_floor(end_date: date, floor: date = HISTORY_FLOOR) -> bool:
    """True when a fact/period ending on `end_date` must not be stored."""
    return end_date < floor
