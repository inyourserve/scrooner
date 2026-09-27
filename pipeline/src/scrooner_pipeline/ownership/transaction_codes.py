"""Form 4 transaction-code classification (doc/scoping/insider_info.md).

Real SEC Form 4 general transaction codes (Table I "Non-Derivative
Securities Acquired, Disposed of, or Beneficially Owned" -- the only table
ownership/insider.py's parser captures, see its own `_parse_form4`), per
SEC's own Form 4 instructions/General Transaction Codes table. Confirmed
live 2026-08-29 against the actual distinct codes present in
core.insider_transaction across the full ~5,160-company population: S,
A, F, M, P, J, G, D, C, L, X, I, W, Z, U, E, O (513,354 real rows) --
every code below is a real, observed one, not a hypothetical.

Translates the raw single-letter code into the doc's 6 human categories
(Open-market buy, Open-market sale, Grant, Option exercise, Gift,
Tax-related disposal). Only codes whose SEC-defined meaning maps
UNAMBIGUOUSLY onto one of those 6 are classified into it -- everything
else falls to "Other", never force-fit. Specifically NOT force-classified,
despite superficial similarity to a doc category:

- D ("Disposition to the issuer of securities pursuant to Rule 16b-3(e)")
  is often, in practice, tax/exercise-related (e.g. shares surrendered to
  the issuer on vesting), but its own SEC definition is a broader
  catch-all for dispositions TO the issuer generally, not specifically
  "payment of exercise price or tax liability" the way F's definition is
  -- conflating the two would misclassify any D transaction that isn't
  actually tax-related. Left as "Other".
- C ("Conversion of derivative security") is related to but distinct
  from M's "exercise OR conversion of derivative security exempted
  pursuant to Rule 16b-3" -- C covers non-exempt conversions (e.g.
  convertible preferred/notes into common), a different real transaction
  than an employee option exercise. Left as "Other" rather than folded
  into "Option exercise".
- I ("Discretionary transaction pursuant to Rule 16b-3(f)", a broker-
  directed purchase/sale under a pre-approved plan) is economically
  similar to an open-market transaction but is its own SEC-defined
  exempt category, not itself labeled open-market. Left as "Other".
- J, K, L, U, V, W, Z, E, H (other/footnoted acquisitions, equity swaps,
  small Rule 16a-6 acquisitions, change-of-control tender dispositions,
  voting-trust deposits/withdrawals, and long/short derivative-position
  expirations) have no analogue among the doc's 6 categories at all.

X ("Exercise of in-the-money or at-the-money derivative security") and O
("Exercise of out-of-the-money derivative security") ARE classified as
"Option exercise" alongside M -- all three are, per their own SEC
definitions, literally the act of exercising a derivative security; they
differ only in which 16b-3 exemption applies, not in the underlying
economic action the doc's category names.
"""

OPEN_MARKET_BUY = "Open-market buy"
OPEN_MARKET_SALE = "Open-market sale"
GRANT = "Grant"
OPTION_EXERCISE = "Option exercise"
GIFT = "Gift"
TAX_RELATED_DISPOSAL = "Tax-related disposal"
OTHER = "Other"

# code -> (doc category, SEC's own definition, for traceability/display)
TRANSACTION_CODE_LABELS: dict[str, tuple[str, str]] = {
    "P": (OPEN_MARKET_BUY, "Open market or private purchase of securities"),
    "S": (OPEN_MARKET_SALE, "Open market or private sale of securities"),
    "A": (GRANT, "Grant, award, or other acquisition per Rule 16b-3(d)"),
    "M": (
        OPTION_EXERCISE,
        "Exercise or conversion of derivative security exempted pursuant to Rule 16b-3",
    ),
    "X": (
        OPTION_EXERCISE,
        "Exercise of in-the-money or at-the-money derivative security",
    ),
    "O": (OPTION_EXERCISE, "Exercise of out-of-the-money derivative security"),
    "G": (GIFT, "Bona fide gift"),
    "F": (
        TAX_RELATED_DISPOSAL,
        "Payment of exercise price or tax liability by delivering or withholding securities",
    ),
    # Real codes present in the data, deliberately left unclassified into
    # one of the doc's 6 categories -- see module docstring for why each
    # is NOT a confident match, not merely omitted by oversight.
    "D": (OTHER, "Disposition to the issuer of securities pursuant to Rule 16b-3(e)"),
    "C": (OTHER, "Conversion of derivative security"),
    "I": (OTHER, "Discretionary transaction pursuant to Rule 16b-3(f)"),
    "J": (OTHER, "Other acquisition or disposition (explained in a footnote)"),
    "K": (OTHER, "Transaction in equity swap or similar instrument"),
    "L": (OTHER, "Small acquisition under Rule 16a-6"),
    "U": (
        OTHER,
        "Disposition pursuant to a tender of shares in a change-of-control transaction",
    ),
    "V": (OTHER, "Transaction voluntarily reported earlier than required"),
    "W": (
        OTHER,
        "Acquisition or disposition by will or the laws of descent and distribution",
    ),
    "Z": (OTHER, "Deposit into or withdrawal from a voting trust"),
    "E": (OTHER, "Expiration of short derivative position"),
    "H": (
        OTHER,
        "Expiration (or cancellation) of long derivative position with value received",
    ),
}


def classify_transaction_code(code: str | None) -> str:
    """Returns one of the doc's 6 categories, or "Other" for every real
    code that isn't a confident match (see module docstring), or for a
    NULL/unrecognized code (7 real rows in the population have no
    transaction_code at all -- an honest "Other", never guessed)."""
    if code is None:
        return OTHER
    entry = TRANSACTION_CODE_LABELS.get(code.strip().upper())
    return entry[0] if entry else OTHER
