"""A filer's presentation scale, and "the same number within it".

core.fact stores no XBRL `decimals`, so two copies of one figure that differ
only by rounding (630,587,000 in a filing presented in thousands, 631,000,000
in the next one presented in millions; a 9M YTD of 327 vs Q1+Q2+Q3 = 326) have
to be recognised from the values themselves. The scale of a company is the
median trailing-zero exponent of its authoritative full-year USD facts (0 =
units, 3 = thousands, 6 = millions), capped at millions; two values agree when
they differ by at most UNITS_SLACK units of that scale (a sum of three rounded
numbers can be off by 1.5 units). Same rule as normalizer/q4_vintage_hold.py
(branch work/engineering/same-vintage-q4-hold); unify when both are on main.
"""

from __future__ import annotations

from collections.abc import Iterable
from decimal import Decimal

import psycopg

MAX_SCALE_EXPONENT = 6
UNITS_SLACK = Decimal("1.5")
REL_SLACK = Decimal("0.0005")


def presentation_scale(values: Iterable[Decimal]) -> int:
    exps: list[int] = []
    for v in values:
        if v == 0:
            continue
        e = Decimal(v).normalize().as_tuple().exponent
        if isinstance(e, int):
            exps.append(max(0, min(MAX_SCALE_EXPONENT, e)))
    if not exps:
        return 0
    exps.sort()
    return exps[len(exps) // 2]


def company_presentation_scale(conn: psycopg.Connection, company_id: int) -> int:
    with conn.cursor() as cur:
        cur.execute(
            """
            select f.value from core.fact f
            join core.period p on p.id = f.period_id
            join core.unit u on u.id = f.unit_id
            where f.company_id = %s and p.period_type = 'duration' and p.fiscal_period = 'FY'
              and f.is_authoritative and not f.is_derived and u.unit_name = 'usd'
            """,
            (company_id,),
        )
        return presentation_scale(Decimal(r[0]) for r in cur.fetchall())


def abs_slack(scale: int) -> Decimal:
    return UNITS_SLACK * (Decimal(10) ** scale)


def same_number(a: Decimal, b: Decimal, scale: int) -> bool:
    """True when a and b are one figure at this presentation scale."""
    if a == b:
        return True
    return abs(a - b) <= max(REL_SLACK * max(abs(a), abs(b)), abs_slack(scale))
