"""Every numeric threshold of the certification suite, in one place.

Changing a number here changes the measuring instrument, so the Verifier's
false-positive measurement (data-team/36) must be repeated afterwards. Each
value says which rule uses it and why it has that size. Names, tag lists and
concept sets stay in their modules; only numbers live here.
"""

from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

# ---- periods (history.py, period_integrity.py, scale.py, ties.py, splits.py) ----
TOLERANCE_DAYS = (
    7  # cell vs filing period end: 52/53-week years and amendments differ by days
)
YEAR_MIN, YEAR_MAX = (
    350,
    380,
)  # annual duration: 364 and 371 days are both real (ledger 2026-10-18)
QUARTER_MIN, QUARTER_MAX = 61, 121  # quarter 91 +/- 30
FY_MIN_DAYS, FY_MAX_DAYS = YEAR_MIN, YEAR_MAX
QUARTER_MAX_DAYS = QUARTER_MAX
MAX_DURATION_DAYS = 400  # longer than a 53-week year plus slack: cumulative / inception-to-date windows are not periods
TILE_GAP_DAYS = 7  # quarters may start a few days off the previous end
LATE_START_DAYS = (
    120  # first filing later than window start + this -> history_starts_after_window
)
LOOKBACK_SLACK_DAYS = 45  # metric lookback vs first stored period (fiscal drift)

# ---- I1/I2 ties.py ----
LIABILITIES_NCI_TOLERANCE = Decimal(
    "0.005"
)  # calculated total liabilities vs assets - equity - NCI
WRONG_GAP = Decimal(
    "0.25"
)  # identity gap above 25% of its basis is a wrong component, not rounding
SCALE_RATIO = Decimal(
    50
)  # net income tie is wrong_value only when stored/expected is >= 50x apart
CASH_ROLL_TOLERANCE = Decimal(
    "0.10"
)  # FX and restricted cash make small cash-roll gaps normal
CASH_DATE_SLACK_DAYS = 4

# ---- I4 scale.py ----
NEIGHBOUR_RATIO = Decimal(
    1000
)  # >= 3 orders of magnitude against the median of the nearest same-length periods
NEIGHBOURS_EACH_SIDE = 2
MIN_NEIGHBOURS = 2
CROSS_CONCEPT_REVIEW = Decimal("0.00001")  # net income etc. below 1e-5 of revenue
CROSS_CONCEPT_WRONG = Decimal("0.000001")  # below 1e-6 of revenue
MIN_SIGN_CONFLICT = Decimal(1_000_000)  # both layers at least $1M and of opposite sign
LAYER_RATIO = Decimal(
    100
)  # base vs resolved layer of one cell, per-share and share counts excluded
EPS_SHARES_RATIO = Decimal(3)
MARKET_CAP_MAX = Decimal("10000000000000")  # $10T: above any listed company
MARKET_CAP_PRICE_RATIO = Decimal(2)
PE_FLOOR = Decimal(2)
PE_BASIS_RATIO = Decimal(5)
SHARES_LOOKAROUND_DAYS = 120
# R-STATEMENT-ROLE (a value from a different statement line under the same tag)
ROLE_RATIO = Decimal(5)  # >= 5x (or <= 1/5) against neighbours / own median intensity
ROLE_MIN_NEIGHBOURS = 4
ROLE_SIGNALS_WRONG = (
    2  # independent signals needed for wrong_value; one signal is review
)
ROLE_LAYER_CONFLICT = Decimal(
    "0.05"
)  # revenue-like flow: resolved vs base layer differ by > 5%

# ---- I5 period_integrity.py ----
OLD_COMPARATIVE_DAYS = 800  # a quarter filed >800 days after its end is older than any 10-K's quarterly comparatives
SUM_REVIEW = Decimal("0.02")  # four quarters vs the year, same filing vintage
FACE_MAX_PRIORITY = 2  # an approved mapping at priority 1-2 is a face-line tag; priority 3+ are components
SUM_WRONG = Decimal("0.10")
MIN_EQUAL_VALUE = Decimal(
    1_000_000
)  # equal quarter/window values below $1M are coincidence
VINTAGE_LATE_FILING_DAYS = 200  # an FY value filed > 200 days after its year end is a later filing (re-presentation)

# ---- I6 source_integrity.py ----
CROSS_VINTAGE_MAX_DIFF = Decimal(
    "0.05"
)  # beyond 5% the gap is a different problem (scale, definition), not a vintage drift
CROSS_VINTAGE_MIN_DIFF = Decimal(
    "0.001"
)  # an input restated by >= 0.1% between filings makes mixed-vintage arithmetic wrong
PROXY_ROUNDING_MAX = Decimal(
    "0.01"
)  # a proxy copy rounded to millions/billions differs from the 10-K by <= 1%
ROUNDING_TOLERANCE = Decimal("0.0001")  # 0.01%, the ledger's rounding skip (2026-10-18)
CONFLICT_FILL_MAX_SPREAD = Decimal(
    "0.15"
)  # mapper/conflict_resolution.py fills only <= 15% disagreement

RECAST_8K_MIN_FACTS = 100  # an 8-K with this many facts carries full statements (a recast), not a cover page

# ---- I7 currency.py ----
ANNUAL_ONLY_MAX_GAP_DAYS = 650  # public float / employee count: a 10-K-only item may be ~20 months older than the latest 10-Q
INPUT_MAX_AGE_DAYS = 456  # 15 months

# ---- I8 composition.py ----
# Debt lines that include finance leases: a balance sheet line 'Long-term debt and finance
# lease obligations' (BAX 6,055M at 2020-06-30) is a debt component the Mapper registry
# does not list. Perimeter is a definition question (KR's borrowings-only 15,909M vs 17,633M
# with leases is a stated perimeter), so a total is wrong against these only when it is
# below LEASE_TOTAL_TOLERANCE of them (BAX stored 319M = 5%). DATA-INFERRED tag names.
LEASE_INCLUSIVE_DEBT_TAGS = (
    "LongTermDebtAndCapitalLeaseObligations",
    "LongTermDebtAndCapitalLeaseObligationsCurrent",
    "DebtAndCapitalLeaseObligations",
)
DEBT_DIP_MIN_ASSET_SHARE = Decimal(
    "0.05"
)  # neighbouring debt below 5% of total assets is immaterial: the dip is real
DEBT_DIP_RATIO = Decimal(
    5
)  # total debt below 1/5 of both neighbouring balance sheets is a missing component
LEASE_TOTAL_TOLERANCE = Decimal("0.5")
TOTAL_TOLERANCE = Decimal("0.98")  # stored total may be 2% under a component
DPS_RATE_TOLERANCE = Decimal(
    "0.02"
)  # R-RATE-ON-YTD: year value within 2% of the quarterly rate
Q4_RATE_TOLERANCE = Decimal(
    "0.01"
)  # derived Q4 tax rate vs Q4 tax / Q4 pretax: one point
Q4_EPS_TOLERANCE = Decimal(
    "0.03"
)  # derived Q4 EPS vs the net-income / implied-shares recompute: 3%
DPS_PAID_MAX_RATIO = Decimal(
    "0.6"
)  # FY DPS x shares / dividends paid above this: a full-year total, not a quarterly rate
DPS_PAID_RATE_MIN = Decimal(
    "0.15"
)  # year DPS x shares / dividends paid between these: the year value is ONE quarterly rate
DPS_PAID_RATE_MAX = Decimal("0.40")
DPS_RATE_MIN_QUARTERS = (
    2  # positive, equal quarterly rates needed to call the year value a rate
)

# ---- I9 splits.py ----
JUMP_FACTOR = Decimal("1.5")  # a share count change of >= 1.5x needs a split on record
SPLIT_WINDOW_BEFORE = timedelta(days=30)
SPLIT_WINDOW_AFTER = timedelta(days=150)
INTEGER_TOLERANCE = Decimal("0.05")
BASIS_RATIO = Decimal(5)
MIN_RESTATED_RATIO = Decimal(
    "1.2"
)  # a restated comparative proves a split only if the value moved by >= 1.2x
DUPLICATE_EVENT_DAYS = 400  # same-ratio split rows closer than this are ONE event when the filing-dated share series steps at most once between them
DUPLICATE_STEP_WINDOW_DAYS = (
    120  # filings reporting a split come up to ~4 months after its effective date
)
BASIS_CELL_TOLERANCE = Decimal(
    "0.10"
)  # stored/as-filed against the factor its source filing date implies
NON_INTEGER_RATIOS = (
    Decimal("1.25"),
    Decimal("1.5"),
    Decimal("2.5"),
)  # 5-for-4, 3-for-2, 5-for-2 (ODFL 3-for-2 of 2020)
CLEAN_RATIOS = (
    2,
    3,
    4,
    5,
    6,
    7,
    8,
    10,
    12,
    15,
    16,
    20,
    25,
    30,
    40,
    50,
)  # split ratios seen in practice
BREAK_TOLERANCE = Decimal(
    "0.08"
)  # a series jump within 8% of a clean ratio is a basis break

# ---- loader.py ----
SOURCE_BATCH = 20_000
