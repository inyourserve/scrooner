"""RF-10 `pershare.balance_sheet_date_anchor@1` (W10): per-share balance-sheet
metrics are anchored on the balance-sheet date.

Defect (DATA-INFERRED, AAPL read 2026-10-22; FILING-CHECKED in doc 46 W10 with
10-Q 0000320193-26-000020): `book_value_per_share` and `net_cash_per_share`
take their anchor periods from the UNION of all their instant inputs. The share
count has two dates per filing: the balance-sheet date (AAPL 2026-06-27, 14.609B
shares, fact 71681) and the later cover-page date (2026-07-17, 14.594B, fact
68114). The cover date is an anchor too, but equity/cash/debt do not exist on
that date, so the newest row is a null `incomplete:numerator` / `incomplete:add`
while the valid row (7.3599 at 2026-06-27) sits one row older. Readers take the
newest row, so the cell shows blank.

Rule: anchor on the balance-sheet date, i.e. only the instants of the
non-denominator inputs (equity; cash and debt). The share count is matched on
that same date, as before. Stated share-date rule: the share count must be dated
on the balance-sheet date; NO cover-date fallback is paired (a count taken weeks
later can span buybacks, offerings or a split, and pairing across filings is
what the Period Engineer's filing-checked pairing rule must define). A company
with only a cover-dated count keeps `incomplete:denominator` at the balance-sheet
date, visibly unavailable with a reason, never a guessed value. The earlier idea
"fall back to the latest non-null row" is rejected (it can surface an older row
and fights the staleness guard; doc 49 ruling).

Default OFF (see rule_flags.py). Pure functions only.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Any

BS_ANCHORED_METRICS = frozenset({"book_value_per_share", "net_cash_per_share"})


def anchor_inputs(
    metric_name: str,
    duration_inputs: list[tuple[Any, ...]],
    instant_inputs: list[tuple[Any, ...]],
) -> list[tuple[Any, ...]]:
    """Inputs whose periods define the metric's rows under RF-10.

    inputs are (concept_name, concept_id, role, is_instant). Metrics outside
    BS_ANCHORED_METRICS, or with any duration input, keep the legacy rule.
    """
    legacy = duration_inputs or instant_inputs
    if metric_name not in BS_ANCHORED_METRICS or duration_inputs:
        return legacy
    anchored = [i for i in instant_inputs if i[2] != "denominator"]
    return anchored or legacy


@dataclass(frozen=True)
class LatestEffect:
    end_now: date | None
    value_now: Decimal | None
    reason_now: str | None
    end_after: date | None
    value_after: Decimal | None
    reason_after: str | None

    @property
    def fixes_latest_cell(self) -> bool:
        """The newest row is blank now and valued after the anchor change."""
        return self.value_now is None and self.value_after is not None

    @property
    def changes_latest_row(self) -> bool:
        return (self.end_now, self.value_now, self.reason_now) != (
            self.end_after,
            self.value_after,
            self.reason_after,
        )


def latest_effect(
    rows: list[tuple[date, Decimal | None, str | None]],
    anchor_dates: set[date],
) -> LatestEffect:
    """Newest stored row now vs the newest row whose date is an anchor date.

    rows: (period_end, value, is_null_reason) of one company/metric (FY and
    quarter rows). anchor_dates: balance-sheet dates of the non-share inputs.
    """
    if not rows:
        return LatestEffect(None, None, None, None, None, None)
    now = max(rows, key=lambda r: r[0])
    kept = [r for r in rows if r[0] in anchor_dates]
    after = max(kept, key=lambda r: r[0]) if kept else (None, None, None)
    return LatestEffect(now[0], now[1], now[2], after[0], after[1], after[2])
