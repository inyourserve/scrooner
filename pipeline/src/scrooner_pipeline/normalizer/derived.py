"""Stage 2g -- Q4 derivation (doc 09). Companies file 10-Qs for Q1-Q3 and a
10-K for the full year -- there is normally no standalone Q4 filing, so a
Q4 value has to be derived as FY - Q1 - Q2 - Q3 and explicitly flagged
(is_derived=true), never presented as if it were directly reported.

Only duration facts need this -- an instant (balance-sheet) fact "as of"
fiscal year end already IS the Q4-end snapshot, nothing to derive. Uses
Stage 2b's fiscal_year/fiscal_period labels (robust across non-calendar
FYE companies -- verified Day 2 against AAPL/MSFT/NKE's real fiscal
calendars) to group FY/Q1/Q2/Q3 candidates, and only Stage 2e/2f's
resolved `is_authoritative` facts -- deriving from an unresolved or
superseded input would manufacture a new number nobody should trust,
compounding uncertainty instead of flagging it.

Lineage: a derived fact's filing_id/raw_object_id point at the FY fact's
own filing/raw object (the 10-K that anchors the full-year side of the
subtraction) -- no new schema field for "derived from 4 facts" needed,
since Q1/Q2/Q3's contributing values are always fully reconstructable by
querying the same (company, concept, unit, fiscal_year) with
fiscal_period in ('Q1','Q2','Q3'), same "don't scaffold new schema the
existing structure already answers" pattern as Stage 2e's is_authoritative.

If a company genuinely reports a discrete Q4 value directly somewhere
(rare, but checked for) the real reported fact is left alone -- derivation
never overwrites or duplicates a real value with a guess.

All lookups (existing periods, existing non-derived facts) are loaded
into memory up front and writes are batched, same pattern as
identity.py/periods.py/facts.py -- a first version of this module did a
handful of individual round-trip queries per candidate group instead, and
a large company (JPM, AAPL: thousands of groups) hit repeated
`SSL SYSCALL... Operation timed out` errors from the sheer round-trip
count over one long-lived connection, the same class of problem doc 08's
day-04 learnings entry already flagged for the Collector. Fixed by
batching, not by retrying harder.
"""

import re
from datetime import timedelta

import psycopg
import structlog

from scrooner_pipeline.common import rule_flags
from scrooner_pipeline.common.derivation_policy import (
    PER_SHARE_NOT_DERIVED_REASON,
    PERIODIC_FORMS_DOMESTIC,
)
from scrooner_pipeline.common.errors import log_error, safe_rollback

logger = structlog.get_logger()

# Periodic-form gate (2026-10-22, WO-2 RU-1): every INPUT to a derived quarter
# (FY, Q1-Q3, 6M/9M YTD) must come from a 10-K/10-Q-family filing. A proxy
# (DEF 14A) or 8-K fact can be authoritative when it is the only copy, and
# it fed wrong derivations: JPM Q4 2025 net income 12,977M from the proxy's
# rounded 57.0B (core.fact 182608846; the 10-K gives 13,025M) and WTRG Q4
# from American Water's statements furnished in an 8-K. See
# common/derivation_policy.py. Reported-Q4 lookups that only BLOCK
# derivation (_load_reported_duration_keys) are deliberately not gated: a
# non-periodic copy there leaves the cell for the authority gate (WO-1.4)
# instead of creating a second authoritative value beside it.
DERIVATION_INPUT_FORMS = sorted(PERIODIC_FORMS_DOMESTIC)
# Both RU-1 behaviours are flag-gated (default OFF = the legacy queries and
# no per-share guard, byte for byte): the form gate by its own rule, the
# per-share guard by the split re-base / RU-1 release pair.
FORM_GATE_RULE = "derive.periodic_inputs_only@1"


def _form_gate_on() -> bool:
    return rule_flags.rule_enabled(FORM_GATE_RULE)


_RU1_COUNTERS = frozenset(
    {"non_additive_not_derived", "demoted_full_year_q4_not_replaced"}
)


def _per_share_guard_on() -> bool:
    return rule_flags.per_share_pair_enabled()


# Same day-length bands periods.py itself uses to classify a duration
# span (see that module's own comment) -- reused here, not
# re-guessed, so "half-year" and "three-quarter" mean exactly the same
# thing in both places.
HALF_YEAR_MIN_DAYS, HALF_YEAR_MAX_DAYS = 170, 200
THREE_QUARTER_MIN_DAYS, THREE_QUARTER_MAX_DAYS = 260, 290
# A derived Q4 span must itself look like one quarter (13-14 weeks, with
# slack for 52/53-week calendars).
Q4_MIN_DAYS, Q4_MAX_DAYS = 80, 100


# Weighted-average share counts are AVERAGES over their own window, not flows,
# so the additive rule FY - (Q1+Q2+Q3) is wrong: each quarter is about S, so it
# yields about -2S (measured live 2026-10-17: 444 of 469 derived diluted-share
# facts and 452 of 478 basic ones, companies 1-150, were negative, all stored
# as authoritative). The annual average is the mean of the quarterly averages,
# so the discrete quarter is recovered with the window-count weights instead:
#   Q4 = 4*FY - (Q1+Q2+Q3)        or  4*FY - 3*YTD9  when only the 9-month YTD exists
#   Q2 = 2*H1 - Q1                Q3 = 3*YTD9 - 2*H1
# Validated against yfinance's own quarterly Basic/Diluted Average Shares for 44
# company-FY-share-type cases (20 companies, varied fiscal year-ends): median
# error 0.024%, p90 0.20%, max 0.78%. It is an APPROXIMATION (assumes equal
# quarter lengths and ignores treasury-method effects), stored like any derived
# fact (is_derived=true), and a non-positive result is never stored. Adopted
# 2026-10-17 by the founder for this concept family only. EPS and other
# non-additive tags are deliberately unchanged.
AVERAGE_TAG_PATTERN = "WeightedAverage%"


# Per-share values and ratios are NEVER derived (2026-10-21, fix register
# item 12). FY - 9M (or FY - Q1 - Q2 - Q3) is only valid for additive flows;
# EPS and dividends per share divide by a different weighted share count (or
# a different declared-dividend basis) in every window, so the difference is
# not the quarter's value. FILING-CHECKED failures of the old behaviour:
# MSFT Q4 FY26 diluted EPS derived 4.80 vs 4.81 filed (core.fact 341935,
# 8-K 0001193125-26-323632 Ex. 99.1); AAPL Q4 FY25 1.84 vs 1.85 (8-K
# 0000320193-25-000077 Ex. 99.1); KLAC Q4 -22.61 (split-basis mix); V
# quarterly dividend on the full-year context giving Q4 DPS -1.18; negative
# derived DPS at AGNT (0001104659-26-019145 R6) and LEA.
#
# The guard is structural and tag-independent first: any unit that is a
# ratio (contains '/', e.g. usd/shares, usd/bbl, cad/usd) or 'pure' is not a
# flow. Belt and braces, a per-share tag name blocks derivation even if the
# filer used a monetary unit. A filed value (FY EPS from the 10-K, a
# discrete Q4 from a 10-K quarterly table) is a normal reported fact and is
# untouched; the derived cell simply stays empty, and consumers must show it
# as unavailable with NON_ADDITIVE_UNAVAILABLE_REASON.
#
# This stage only STOPS producing such rows. Rows derived before this change
# are deliberately not retired here: retirement is a shared-table write that
# needs its own reviewed dry-run (data-team rule), not a side effect of the
# nightly reprocess.
NON_ADDITIVE_UNAVAILABLE_REASON = PER_SHARE_NOT_DERIVED_REASON
PER_SHARE_TAG_REGEX = (
    r"Per(Basic|Diluted|BasicAndDiluted)?Share|PerOutstanding[A-Za-z]*Unit|PerUnit"
)
_PER_SHARE_TAG = re.compile(PER_SHARE_TAG_REGEX)


def is_ratio_unit(unit_name: str) -> bool:
    """True for a unit that is a ratio of two measures (per share, per unit,
    per barrel, an exchange rate) or dimensionless ('pure'). Unit names are
    case-folded in core.unit (units.canonicalize_unit)."""
    name = unit_name.strip().lower()
    return "/" in name or name == "pure"


def is_per_share_tag(tag: str) -> bool:
    return bool(_PER_SHARE_TAG.search(tag))


def _load_non_additive(conn: psycopg.Connection) -> tuple[set[int], set[int]]:
    """(ratio unit ids, per-share concept ids). Global lookups, not per company."""
    with conn.cursor() as cur:
        cur.execute("select id, unit_name from core.unit")
        unit_ids = {uid for uid, name in cur.fetchall() if is_ratio_unit(name)}
        cur.execute(
            "select id from core.concept where tag ~ %s", (PER_SHARE_TAG_REGEX,)
        )
        concept_ids = {row[0] for row in cur.fetchall()}
    return unit_ids, concept_ids


def _load_average_concept_ids(conn: psycopg.Connection) -> set[int]:
    with conn.cursor() as cur:
        cur.execute(
            "select id from core.concept where tag like %s",
            (AVERAGE_TAG_PATTERN,),
        )
        return {row[0] for row in cur.fetchall()}


def _q4_value(fy_value, first_three, *, is_average: bool, via_ytd: bool):
    """Discrete Q4 from the annual figure and the first three quarters.
    `first_three` is Q1+Q2+Q3 for the quarterly chain, or the 9-month YTD
    figure when via_ytd. Returns None when the average method yields a
    non-positive count (never store it)."""
    if not is_average:
        return fy_value - first_three
    weights = 3 if via_ytd else 1
    value = 4 * fy_value - weights * first_three
    return value if value > 0 else None


def _retire_derived(
    conn: psycopg.Connection,
    company_id: int,
    keys: list[tuple],
    existing_periods: dict,
) -> int:
    """Demote (never delete) derived facts the current method refuses to produce.

    keys are (concept_id, unit_id, start, end). When the weighted-average method
    declines a period (non-positive result), a derived row from the old
    FY - sum(quarters) formula may still sit there as an authoritative, impossible
    negative share count: 2,203 such rows (824 companies) remained after the
    2026-10-18 rollout. Only rows with is_derived are touched; the reported facts
    and the row itself stay inspectable."""
    params = [
        {
            "company_id": company_id,
            "concept_id": c,
            "unit_id": u,
            "period_id": existing_periods[(s, e)],
        }
        for (c, u, s, e) in keys
        if (s, e) in existing_periods
    ]
    if not params:
        return 0
    with conn.cursor() as cur:
        cur.executemany(
            "update core.fact set is_authoritative = false "
            "where company_id = %(company_id)s and concept_id = %(concept_id)s "
            "and unit_id = %(unit_id)s and period_id = %(period_id)s "
            "and is_derived and is_authoritative",
            params,
        )
    conn.commit()
    return len(params)


QUARTERLY_CANDIDATES_SQL_LEGACY = """
            select f.id, f.concept_id, f.unit_id, f.value, f.filing_id, f.raw_object_id,
                   p.fiscal_year, p.fiscal_period, p.start_date, p.end_date
            from core.fact f
            join core.period p on p.id = f.period_id
            where f.company_id = %s
              and f.is_authoritative
              and p.period_type = 'duration'
              and p.fiscal_period in ('FY', 'Q1', 'Q2', 'Q3')
            """

NINE_MONTH_YTD_SQL_LEGACY = """
            select f.concept_id, f.unit_id, p.start_date, p.end_date, f.value
            from core.fact f
            join core.period p on p.id = f.period_id
            where f.company_id = %s
              and f.is_authoritative
              and p.period_type = 'duration'
              and p.fiscal_period is null
              and (p.end_date - p.start_date) between %s and %s
            """

ALL_DURATION_FACTS_SQL_LEGACY = """
            select f.id, f.concept_id, f.unit_id, f.value, f.filing_id, f.raw_object_id,
                   p.fiscal_year, p.fiscal_period, p.start_date, p.end_date
            from core.fact f
            join core.period p on p.id = f.period_id
            where f.company_id = %s
              and f.is_authoritative
              and p.period_type = 'duration'
            """

QUARTERLY_CANDIDATES_SQL = """
    select f.id, f.concept_id, f.unit_id, f.value, f.filing_id, f.raw_object_id,
           p.fiscal_year, p.fiscal_period, p.start_date, p.end_date
    from core.fact f
    join core.period p on p.id = f.period_id
    join core.filing fl on fl.id = f.filing_id
    where f.company_id = %(company_id)s
      and f.is_authoritative
      and fl.form = any(%(forms)s)
      and p.period_type = 'duration'
      and p.fiscal_period in ('FY', 'Q1', 'Q2', 'Q3')
"""

NINE_MONTH_YTD_SQL = """
    select f.concept_id, f.unit_id, p.start_date, p.end_date, f.value
    from core.fact f
    join core.period p on p.id = f.period_id
    join core.filing fl on fl.id = f.filing_id
    where f.company_id = %(company_id)s
      and f.is_authoritative
      and fl.form = any(%(forms)s)
      and p.period_type = 'duration'
      and p.fiscal_period is null
      and (p.end_date - p.start_date) between %(min_days)s and %(max_days)s
"""

ALL_DURATION_FACTS_SQL = """
    select f.id, f.concept_id, f.unit_id, f.value, f.filing_id, f.raw_object_id,
           p.fiscal_year, p.fiscal_period, p.start_date, p.end_date
    from core.fact f
    join core.period p on p.id = f.period_id
    join core.filing fl on fl.id = f.filing_id
    where f.company_id = %(company_id)s
      and f.is_authoritative
      and fl.form = any(%(forms)s)
      and p.period_type = 'duration'
"""


def _load_quarterly_candidates(
    conn: psycopg.Connection, company_id: int
) -> list[tuple]:
    with conn.cursor() as cur:
        if _form_gate_on():
            cur.execute(
                QUARTERLY_CANDIDATES_SQL,
                {"company_id": company_id, "forms": DERIVATION_INPUT_FORMS},
            )
        else:
            cur.execute(QUARTERLY_CANDIDATES_SQL_LEGACY, (company_id,))
        return cur.fetchall()


def _load_nine_month_ytd(
    conn: psycopg.Connection, company_id: int
) -> dict[tuple, list]:
    """(concept_id, unit_id, start_date) -> [(end_date, value)] for every
    authoritative, unlabeled ~9-month cumulative (YTD) duration fact. The Q3
    10-Q reports this "nine months ended" figure alongside the discrete
    quarter; periods.py correctly leaves it unlabeled (it isn't a quarter)."""
    with conn.cursor() as cur:
        if _form_gate_on():
            cur.execute(
                NINE_MONTH_YTD_SQL,
                {
                    "company_id": company_id,
                    "forms": DERIVATION_INPUT_FORMS,
                    "min_days": THREE_QUARTER_MIN_DAYS,
                    "max_days": THREE_QUARTER_MAX_DAYS,
                },
            )
        else:
            cur.execute(
                NINE_MONTH_YTD_SQL_LEGACY,
                (company_id, THREE_QUARTER_MIN_DAYS, THREE_QUARTER_MAX_DAYS),
            )
        out: dict[tuple, list] = {}
        for concept_id, unit_id, start, end, value in cur.fetchall():
            out.setdefault((concept_id, unit_id, start), []).append((end, value))
        return out


def _q4_from_nine_month_ytd(fy: dict, nine_month: list) -> tuple | None:
    """FY - 9-month YTD, when the YTD shares the fiscal year's start and
    leaves a quarter-length remainder. Returns (q4_start, q4_end, ytd_value)
    or None. Used only when the Q1+Q2+Q3 chain isn't available -- a single
    cumulative figure from the Q3 10-Q, rather than three separately
    filed quarters that must all be present, authoritative and contiguous."""
    candidates = [
        (end, value)
        for end, value in nine_month
        if end < fy["end_date"]
        and Q4_MIN_DAYS <= (fy["end_date"] - end).days <= Q4_MAX_DAYS
    ]
    if not candidates:
        return None
    ends = {end for end, _ in candidates}
    if len(ends) != 1:
        return None  # ambiguous: more than one 9-month span for this FY
    end, value = candidates[0]
    if len({v for _, v in candidates}) != 1:
        return None  # disagreeing authoritative values -- don't pick one
    return end + timedelta(days=1), fy["end_date"], value


def _load_existing_periods(
    conn: psycopg.Connection, company_id: int
) -> dict[tuple, int]:
    """(start_date, end_date) -> period_id, for this company's duration periods."""
    with conn.cursor() as cur:
        cur.execute(
            "select start_date, end_date, id from core.period where company_id = %s and period_type = 'duration'",
            (company_id,),
        )
        return {(start, end): pid for start, end, pid in cur.fetchall()}


def _load_reported_duration_keys(
    conn: psycopg.Connection, company_id: int
) -> set[tuple]:
    """(concept_id, unit_id, start_date, end_date) for every REPORTED
    (not derived) duration fact -- used to skip derivation when a company
    genuinely already reports a discrete Q4 value directly."""
    with conn.cursor() as cur:
        cur.execute(
            """
            select f.concept_id, f.unit_id, p.start_date, p.end_date
            from core.fact f
            join core.period p on p.id = f.period_id
            where f.company_id = %s and p.period_type = 'duration' and f.is_derived = false
            """,
            (company_id,),
        )
        return set(cur.fetchall())


def _load_authoritative_reported_quarters(
    conn: psycopg.Connection, company_id: int
) -> dict[tuple, list[tuple]]:
    """(concept_id, unit_id, start_date, end_date) -> [(fact_id, value)] for
    authoritative, REPORTED Q4 duration facts. Used to spot a filed "Q4"
    that actually carries the full-year value."""
    with conn.cursor() as cur:
        cur.execute(
            """
            select f.concept_id, f.unit_id, p.start_date, p.end_date, f.id, f.value
            from core.fact f
            join core.period p on p.id = f.period_id
            where f.company_id = %s and p.period_type = 'duration'
              and f.is_derived = false and f.is_authoritative
              and p.fiscal_period = 'Q4'
            """,
            (company_id,),
        )
        out: dict[tuple, list[tuple]] = {}
        for concept_id, unit_id, start, end, fact_id, value in cur.fetchall():
            out.setdefault((concept_id, unit_id, start, end), []).append(
                (fact_id, value)
            )
        return out


def _mistagged_full_year_q4(
    reported: list[tuple], fy_value, first_three_quarters
) -> list[int]:
    """Fact ids of a reported Q4 that is really the full-year figure: its
    value equals FY while Q1-Q3 are non-zero, so the true Q4 can't equal FY.
    Found 2026-09-27: 95 companies' own 10-Ks tag the annual value with a
    Q4 context (L3Harris $21.3B, NiSource $6.5B "Q4" revenue)."""
    if not reported or first_three_quarters == 0:
        return []
    if all(value == fy_value for _fact_id, value in reported):
        return [fact_id for fact_id, _value in reported]
    return []


def derive_q4_for_company(conn: psycopg.Connection, company_id: int) -> dict:
    rows = _load_quarterly_candidates(conn, company_id)
    average_ids = _load_average_concept_ids(conn)
    ratio_unit_ids, per_share_concept_ids = (
        _load_non_additive(conn) if _per_share_guard_on() else (set(), set())
    )
    groups: dict[tuple, dict] = {}
    for (
        fact_id,
        concept_id,
        unit_id,
        value,
        filing_id,
        raw_object_id,
        fiscal_year,
        fiscal_period,
        start_date,
        end_date,
    ) in rows:
        key = (concept_id, unit_id, fiscal_year)
        groups.setdefault(key, {})[fiscal_period] = {
            "fact_id": fact_id,
            "value": value,
            "filing_id": filing_id,
            "raw_object_id": raw_object_id,
            "start_date": start_date,
            "end_date": end_date,
        }

    existing_periods = _load_existing_periods(conn, company_id)
    reported_keys = _load_reported_duration_keys(conn, company_id)
    reported_q4 = _load_authoritative_reported_quarters(conn, company_id)
    nine_month_ytd = _load_nine_month_ytd(conn, company_id)

    stats = {
        "candidate_groups": len(groups),
        "derived": 0,
        "derived_from_ytd": 0,
        "already_reported": 0,
        "replaced_full_year_q4": 0,
        "incomplete": 0,
        "non_additive_not_derived": 0,
        "demoted_full_year_q4_not_replaced": 0,
    }
    new_periods: list[
        tuple
    ] = []  # (start, end, fiscal_year) -- may contain duplicates across concepts, deduped below
    to_derive: list[dict] = []
    demote_fact_ids: list[int] = []
    retire_keys: list[tuple] = []

    for (concept_id, unit_id, fiscal_year), by_period in groups.items():
        fy = by_period.get("FY")
        chain = None
        if fy is not None and all(k in by_period for k in ("Q1", "Q2", "Q3")):
            q1, q2, q3 = by_period["Q1"], by_period["Q2"], by_period["Q3"]
            # Labels alone are not sufficient evidence that subtraction is
            # valid. A malformed or unusually tagged filing can place a
            # Q1/Q2/Q3 label on spans with gaps, overlaps, or dates outside
            # the matching fiscal year. Only derive when the four duration
            # contexts form one contiguous, nested fiscal-year partition.
            # Unit comparability is already enforced by the grouping key.
            if (
                q1["start_date"] == fy["start_date"]
                and q2["start_date"] == q1["end_date"] + timedelta(days=1)
                and q3["start_date"] == q2["end_date"] + timedelta(days=1)
                and q3["end_date"] < fy["end_date"]
            ):
                chain = (
                    q3["end_date"] + timedelta(days=1),
                    fy["end_date"],
                    q1["value"] + q2["value"] + q3["value"],
                )

        # Fallback (2026-09-27): FY - 9-month YTD. The Q1+Q2+Q3 chain needs
        # three separate authoritative, contiguous quarters; 1,326 recent
        # company-years (1,017 companies, net income alone) had a FY and a
        # 9-month YTD from the Q3 10-Q but no Q4, which left their TTM
        # figures (margins, P/E, FCF yield) blank or a year stale.
        via_ytd = False
        if chain is None and fy is not None:
            ytd = nine_month_ytd.get((concept_id, unit_id, fy["start_date"]))
            if ytd:
                chain = _q4_from_nine_month_ytd(fy, ytd)
                via_ytd = chain is not None

        if unit_id in ratio_unit_ids or concept_id in per_share_concept_ids:
            # Never derived (see NON_ADDITIVE_UNAVAILABLE_REASON). A filed
            # "Q4" carrying the full-year value is still demoted, as before,
            # but nothing replaces it: the cell becomes unavailable.
            stats["non_additive_not_derived"] += 1
            if chain is not None and fy is not None:
                cell_key = (concept_id, unit_id, chain[0], chain[1])
                if cell_key in reported_keys:
                    bad = _mistagged_full_year_q4(
                        reported_q4.get(cell_key, []), fy["value"], chain[2]
                    )
                    if bad:
                        demote_fact_ids.extend(bad)
                        stats["demoted_full_year_q4_not_replaced"] += 1
            continue

        if chain is None:
            stats["incomplete"] += 1
            continue

        assert fy is not None  # every chain construction above requires fy
        q4_start, q4_end, first_three_quarters = chain

        q4_value = _q4_value(
            fy["value"],
            first_three_quarters,
            is_average=concept_id in average_ids,
            via_ytd=via_ytd,
        )
        if q4_value is None:
            stats["incomplete"] += 1
            retire_keys.append((concept_id, unit_id, q4_start, q4_end))
            continue

        q4_key = (concept_id, unit_id, q4_start, q4_end)
        if q4_key in reported_keys:
            bad = _mistagged_full_year_q4(
                reported_q4.get(q4_key, []), fy["value"], first_three_quarters
            )
            if not bad:
                stats["already_reported"] += 1
                continue
            demote_fact_ids.extend(bad)
            stats["replaced_full_year_q4"] += 1

        if (q4_start, q4_end) not in existing_periods:
            new_periods.append((q4_start, q4_end, fiscal_year))

        to_derive.append(
            {
                "concept_id": concept_id,
                "unit_id": unit_id,
                "start": q4_start,
                "end": q4_end,
                "value": q4_value,
                "filing_id": fy["filing_id"],
                "raw_object_id": fy["raw_object_id"],
            }
        )
        if via_ytd:
            stats["derived_from_ytd"] += 1

    # Insert any new Q4 periods first (deduped -- several concepts share the
    # same company-wide Q4 span), one round trip, then fold the new ids into
    # the same lookup dict used for the fact rows below.
    distinct_new_periods = {(s, e): fy for s, e, fy in new_periods}
    if distinct_new_periods:
        with conn.cursor() as cur:
            cur.executemany(
                """
                insert into core.period (company_id, start_date, end_date, period_type, fiscal_year, fiscal_period)
                values (%(company_id)s, %(start)s, %(end)s, 'duration', %(fiscal_year)s, 'Q4')
                on conflict (company_id, start_date, end_date, period_type) do nothing
                """,
                [
                    {"company_id": company_id, "start": s, "end": e, "fiscal_year": fy}
                    for (s, e), fy in distinct_new_periods.items()
                ],
            )
        conn.commit()
        existing_periods = _load_existing_periods(conn, company_id)

    if retire_keys:
        _retire_derived(conn, company_id, retire_keys, existing_periods)

    if demote_fact_ids:
        # Kept, not deleted: the filed value stays inspectable, it just stops
        # being the authoritative Q4.
        with conn.cursor() as cur:
            cur.execute(
                "update core.fact set is_authoritative = false where id = any(%s)",
                (demote_fact_ids,),
            )
        conn.commit()

    if to_derive:
        rows_to_insert = [
            {
                "company_id": company_id,
                "concept_id": d["concept_id"],
                "unit_id": d["unit_id"],
                "period_id": existing_periods[(d["start"], d["end"])],
                "filing_id": d["filing_id"],
                "value": d["value"],
                "raw_object_id": d["raw_object_id"],
            }
            for d in to_derive
        ]
        with conn.cursor() as cur:
            cur.executemany(
                """
                insert into core.fact
                    (company_id, concept_id, unit_id, period_id, filing_id, value, is_derived, is_authoritative, raw_object_id)
                values
                    (%(company_id)s, %(concept_id)s, %(unit_id)s, %(period_id)s, %(filing_id)s, %(value)s, true, true, %(raw_object_id)s)
                on conflict (company_id, concept_id, unit_id, period_id, filing_id) do update
                    set value = excluded.value, is_derived = true, is_authoritative = true
                """,
                rows_to_insert,
            )
        conn.commit()
        stats["derived"] = len(rows_to_insert)

    logger.info("derived.q4_resolved", company_id=company_id, **stats)
    if not _per_share_guard_on():  # legacy output keys, unchanged
        stats = {k: v for k, v in stats.items() if k not in _RU1_COUNTERS}
    return stats


def derive_q4(conn: psycopg.Connection, ciks: set[str]) -> dict:
    with conn.cursor() as cur:
        cur.execute(
            "select cik, id from core.company where cik = any(%s)", (sorted(ciks),)
        )
        company_id_by_cik = dict(cur.fetchall())

    totals = {
        "considered": 0,
        "ok": 0,
        "no_company": 0,
        "errored": 0,
        "candidate_groups": 0,
        "derived": 0,
        "derived_from_ytd": 0,
        "already_reported": 0,
        "incomplete": 0,
        "non_additive_not_derived": 0,
        "demoted_full_year_q4_not_replaced": 0,
    }
    for cik in sorted(ciks):
        totals["considered"] += 1
        company_id = company_id_by_cik.get(cik)
        if company_id is None:
            totals["no_company"] += 1
            continue
        try:
            stats = derive_q4_for_company(conn, company_id)
        except Exception as exc:
            totals["errored"] += 1
            log_error(conn, "core.normalizer_error", cik, "derive_q4", exc)
            conn = safe_rollback(conn, stage="derive_q4", cik=cik)
            continue
        totals["ok"] += 1
        for k in (
            "candidate_groups",
            "derived",
            "derived_from_ytd",
            "already_reported",
            "incomplete",
            "non_additive_not_derived",
            "demoted_full_year_q4_not_replaced",
        ):
            totals[k] += stats.get(k, 0)

    logger.info("derived.q4.done", **totals)
    if not _per_share_guard_on():  # legacy output keys, unchanged
        totals = {k: v for k, v in totals.items() if k not in _RU1_COUNTERS}
    return totals


# --- Interim-quarter derivation (Stage 2g follow-on, doc 24/25 --
# closing a real gap found live 2026-08-17 while building
# mapper/price_metrics.py's FCF Yield: several companies' quarterly
# cash-flow-statement facts are tagged cumulative-year-to-date (a normal
# GAAP presentation choice, most common on cash-flow lines -- income-
# statement lines are usually reported discretely per quarter instead),
# which classify_period() above correctly leaves unclassified rather
# than mislabel as a single quarter. Confirmed live against AAPL's real
# CFO facts before writing this: Q1 $29.935B (discrete), a 6-month span
# $53.887B, a 9-month span $81.754B, FY $111.482B -- every one of these
# was already sitting in core.fact, just never decomposed into discrete
# quarters. Implied Q2 = $23.952B, Q3 = $27.867B, Q4 = $29.728B, all
# positive and reasonable, summing back to the real FY figure exactly by
# construction.
#
# Purely additive: does not modify derive_q4_for_company above. Derives
# Q2/Q3 as new is_derived=true/is_authoritative=true facts; derive_q4
# (already-existing logic, unchanged) then picks them up automatically
# on its own next run, the same way it already would for any other
# authoritative Q1-Q3 set -- no code path in derive_q4_for_company knows
# or needs to know these particular Q2/Q3 facts were derived rather than
# directly reported.
def _load_all_duration_facts(conn: psycopg.Connection, company_id: int) -> list[tuple]:
    with conn.cursor() as cur:
        if _form_gate_on():
            cur.execute(
                ALL_DURATION_FACTS_SQL,
                {"company_id": company_id, "forms": DERIVATION_INPUT_FORMS},
            )
        else:
            cur.execute(ALL_DURATION_FACTS_SQL_LEGACY, (company_id,))
        return cur.fetchall()


def derive_interim_quarters_for_company(
    conn: psycopg.Connection, company_id: int
) -> dict:
    rows = _load_all_duration_facts(conn, company_id)
    average_ids = _load_average_concept_ids(conn)
    ratio_unit_ids, per_share_concept_ids = (
        _load_non_additive(conn) if _per_share_guard_on() else (set(), set())
    )
    groups: dict[tuple, dict] = {}
    for (
        fact_id,
        concept_id,
        unit_id,
        value,
        filing_id,
        raw_object_id,
        fiscal_year,
        fiscal_period,
        start_date,
        end_date,
    ) in rows:
        if fiscal_year is None:
            continue
        key = (concept_id, unit_id, fiscal_year)
        entry = {
            "fact_id": fact_id,
            "value": value,
            "filing_id": filing_id,
            "raw_object_id": raw_object_id,
            "start_date": start_date,
            "end_date": end_date,
        }
        duration_days = (end_date - start_date).days
        if fiscal_period == "Q1":
            groups.setdefault(key, {})["Q1"] = entry
        elif fiscal_period == "FY":
            groups.setdefault(key, {})["FY"] = entry
        elif (
            fiscal_period is None
            and HALF_YEAR_MIN_DAYS <= duration_days <= HALF_YEAR_MAX_DAYS
        ):
            groups.setdefault(key, {})["HALF"] = entry
        elif (
            fiscal_period is None
            and THREE_QUARTER_MIN_DAYS <= duration_days <= THREE_QUARTER_MAX_DAYS
        ):
            groups.setdefault(key, {})["THREE_Q"] = entry
        elif fiscal_period is None:
            # Found live 2026-10-03 (Albertsons' real FY2026 Q2 cfo gap):
            # a company whose real first quarter falls outside the normal
            # 80-100-day quarter band (its own 52/53-week calendar made Q1
            # 111 days) never gets periods.py's 'Q1' label, so it landed
            # here instead of the Q1 bucket above -- correct, since
            # labeling it 'Q1' from here would be a different module's
            # job. Kept as an unlabeled candidate list, resolved against
            # HALF's own start/end below by structural nesting, not a
            # day-band guess (unlike HALF/THREE_Q, Q1's real length has
            # no universal band to check against).
            groups.setdefault(key, {}).setdefault("UNLABELED", []).append(entry)
        # Q2/Q3/Q4/other non-standard spans: not this derivation's
        # concern -- Q2/Q3 already discrete means nothing to derive;
        # anything else falls outside the clean day-length bands and is
        # correctly left alone rather than forced.

    existing_periods = _load_existing_periods(conn, company_id)
    reported_keys = _load_reported_duration_keys(conn, company_id)

    stats = {
        "candidate_groups": len(groups),
        "q2_derived": 0,
        "q3_derived": 0,
        "already_reported": 0,
        "incomplete_or_inconsistent": 0,
        "non_additive_not_derived": 0,
    }
    new_periods: dict[
        tuple, dict
    ] = {}  # (start, end) -> {"fiscal_year": ..., "fiscal_period": "Q2"|"Q3"}
    to_derive: list[dict] = []
    retire_keys: list[tuple] = []

    for (concept_id, unit_id, fiscal_year), by_span in groups.items():
        if unit_id in ratio_unit_ids or concept_id in per_share_concept_ids:
            # H1 EPS - Q1 EPS is not Q2 EPS (see NON_ADDITIVE_UNAVAILABLE_REASON).
            stats["non_additive_not_derived"] += 1
            continue
        q1, half, three_q = (
            by_span.get("Q1"),
            by_span.get("HALF"),
            by_span.get("THREE_Q"),
        )
        if q1 is None and half is not None:
            # Structural fallback: any unlabeled fact that starts exactly
            # where HALF starts and ends before HALF ends IS the first
            # quarter, whatever its real length -- see the UNLABELED
            # bucket's own comment above. Exactly one match is the only
            # safe case; 0 or 2+ candidates means this group is genuinely
            # ambiguous/incomplete, left for "incomplete_or_inconsistent"
            # exactly as before.
            candidates = [
                c
                for c in by_span.get("UNLABELED", [])
                if c["start_date"] == half["start_date"]
                and c["end_date"] < half["end_date"]
            ]
            if len(candidates) == 1:
                q1 = candidates[0]

        # Q2 = HALF - Q1, only when both share the same start (the true
        # fiscal-year start) -- never subtract spans that don't actually
        # nest inside one another.
        if (
            q1 is not None
            and half is not None
            and q1["start_date"] == half["start_date"]
        ):
            q2_start, q2_end = q1["end_date"] + timedelta(days=1), half["end_date"]
            q2_value = (
                2 * half["value"] - q1["value"]
                if concept_id in average_ids
                else half["value"] - q1["value"]
            )
            if q2_value <= 0 and concept_id in average_ids:
                stats["incomplete_or_inconsistent"] += 1
                retire_keys.append((concept_id, unit_id, q2_start, q2_end))
            elif (concept_id, unit_id, q2_start, q2_end) not in reported_keys:
                if (q2_start, q2_end) not in existing_periods:
                    new_periods[(q2_start, q2_end)] = {
                        "fiscal_year": fiscal_year,
                        "fiscal_period": "Q2",
                    }
                to_derive.append(
                    {
                        "concept_id": concept_id,
                        "unit_id": unit_id,
                        "start": q2_start,
                        "end": q2_end,
                        "value": q2_value,
                        "filing_id": half["filing_id"],
                        "raw_object_id": half["raw_object_id"],
                        "metric": "q2_derived",
                    }
                )
            else:
                stats["already_reported"] += 1
        else:
            stats["incomplete_or_inconsistent"] += 1

        # Q3 = THREE_Q - HALF, same nesting requirement.
        if (
            half is not None
            and three_q is not None
            and half["start_date"] == three_q["start_date"]
        ):
            q3_start, q3_end = half["end_date"] + timedelta(days=1), three_q["end_date"]
            q3_value = (
                3 * three_q["value"] - 2 * half["value"]
                if concept_id in average_ids
                else three_q["value"] - half["value"]
            )
            if q3_value <= 0 and concept_id in average_ids:
                stats["incomplete_or_inconsistent"] += 1
                retire_keys.append((concept_id, unit_id, q3_start, q3_end))
            elif (concept_id, unit_id, q3_start, q3_end) not in reported_keys:
                if (q3_start, q3_end) not in existing_periods:
                    new_periods[(q3_start, q3_end)] = {
                        "fiscal_year": fiscal_year,
                        "fiscal_period": "Q3",
                    }
                to_derive.append(
                    {
                        "concept_id": concept_id,
                        "unit_id": unit_id,
                        "start": q3_start,
                        "end": q3_end,
                        "value": q3_value,
                        "filing_id": three_q["filing_id"],
                        "raw_object_id": three_q["raw_object_id"],
                        "metric": "q3_derived",
                    }
                )
            else:
                stats["already_reported"] += 1
        else:
            stats["incomplete_or_inconsistent"] += 1

    if new_periods:
        with conn.cursor() as cur:
            cur.executemany(
                """
                insert into core.period (company_id, start_date, end_date, period_type, fiscal_year, fiscal_period)
                values (%(company_id)s, %(start)s, %(end)s, 'duration', %(fiscal_year)s, %(fiscal_period)s)
                on conflict (company_id, start_date, end_date, period_type) do update
                    set fiscal_period = excluded.fiscal_period
                """,
                [
                    {"company_id": company_id, "start": s, "end": e, **info}
                    for (s, e), info in new_periods.items()
                ],
            )
        conn.commit()
        existing_periods = _load_existing_periods(conn, company_id)

    if retire_keys:
        _retire_derived(conn, company_id, retire_keys, existing_periods)

    if to_derive:
        rows_to_insert = [
            {
                "company_id": company_id,
                "concept_id": d["concept_id"],
                "unit_id": d["unit_id"],
                "period_id": existing_periods[(d["start"], d["end"])],
                "filing_id": d["filing_id"],
                "value": d["value"],
                "raw_object_id": d["raw_object_id"],
            }
            for d in to_derive
        ]
        with conn.cursor() as cur:
            cur.executemany(
                """
                insert into core.fact
                    (company_id, concept_id, unit_id, period_id, filing_id, value, is_derived, is_authoritative, raw_object_id)
                values
                    (%(company_id)s, %(concept_id)s, %(unit_id)s, %(period_id)s, %(filing_id)s, %(value)s, true, true, %(raw_object_id)s)
                on conflict (company_id, concept_id, unit_id, period_id, filing_id) do update
                    set value = excluded.value, is_derived = true
                """,
                rows_to_insert,
            )
        conn.commit()
        for d in to_derive:
            stats[d["metric"]] += 1

    logger.info("derived.interim_quarters_resolved", company_id=company_id, **stats)
    if not _per_share_guard_on():  # legacy output keys, unchanged
        stats = {k: v for k, v in stats.items() if k not in _RU1_COUNTERS}
    return stats


def derive_interim_quarters(conn: psycopg.Connection, ciks: set[str]) -> dict:
    with conn.cursor() as cur:
        cur.execute(
            "select cik, id from core.company where cik = any(%s)", (sorted(ciks),)
        )
        company_id_by_cik = dict(cur.fetchall())

    totals = {
        "considered": 0,
        "ok": 0,
        "no_company": 0,
        "errored": 0,
        "candidate_groups": 0,
        "q2_derived": 0,
        "q3_derived": 0,
        "already_reported": 0,
        "incomplete_or_inconsistent": 0,
        "non_additive_not_derived": 0,
    }
    for cik in sorted(ciks):
        totals["considered"] += 1
        company_id = company_id_by_cik.get(cik)
        if company_id is None:
            totals["no_company"] += 1
            continue
        try:
            stats = derive_interim_quarters_for_company(conn, company_id)
        except Exception as exc:
            totals["errored"] += 1
            log_error(
                conn, "core.normalizer_error", cik, "derive_interim_quarters", exc
            )
            # Found live 2026-10-03, full-population sharded run: a dead
            # connection (Supabase pooler drop) was never reconnected here,
            # unlike derive_q4() just above, which already does this --
            # so every remaining company after the first drop in each of
            # 6 parallel shards failed too (4,265 of 5,216 companies,
            # 82% of the population, errored this way in one run).
            conn = safe_rollback(conn, stage="derive_interim_quarters", cik=cik)
            continue
        totals["ok"] += 1
        for k in (
            "candidate_groups",
            "q2_derived",
            "q3_derived",
            "already_reported",
            "incomplete_or_inconsistent",
            "non_additive_not_derived",
        ):
            totals[k] += stats.get(k, 0)

    logger.info("derived.interim_quarters.done", **totals)
    if not _per_share_guard_on():  # legacy output keys, unchanged
        totals = {k: v for k, v in totals.items() if k not in _RU1_COUNTERS}
    return totals
