"""Data Sanity Layer (2026-09-08, explicit user request): an independent,
continuous cross-check of a handful of our own computed values against
yfinance (Yahoo Finance) -- a genuinely separate data source from SEC EDGAR,
so a real error in our own pipeline (a wrong shares-outstanding fallback, a
stale price, or the kind of "resolve() returns an authoritative-but-wrong
value" bug found live 2026-09-07, see
doc/learnings/2026-09-07-statement-table-coverage-and-revenue-zero-bug.md)
has a real chance of surfacing as a disagreement here, rather than staying
invisible because every check we have is downstream of the same pipeline.

Never a second source of TRUTH -- this project's own moat is SEC EDGAR,
parsed once, traceable to a filing (doc 01/02). yfinance here is an
observer, not an authority: a real mismatch means "go look," not "overwrite
our value with Yahoo's." See doc/planning/y-finance.md and doc 02's
decision register for the ToS-risk tradeoff already accepted for storing
y_sector/y_industry/y_about_text/y_website in company_master/
yfinance_industry.py -- this module extends that same accepted risk to a
new, narrow purpose (a sanity check, not a served product field) rather
than opening a new one.

**Widened 2026-09-08, same day, direct follow-up ("why not all the metric?").**
The first version checked only 3 metric_value-backed metrics plus the
revenue-zero special case -- deliberately narrow "clean unit match" scope.
Checking a real AAPL `.get_info()` payload directly (not assuming) showed
it already carries ~20 more fields with a genuine, checkable counterpart in
`analytics.metric_definition` -- and since `_fetch_info()` already pulls
the WHOLE payload per company for the original 3 checks, examining more of
it costs zero additional yfinance requests. METRIC_MAPPINGS below is the
resulting table-driven config -- every mapping was verified against a real
AAPL value before being added (see the two real unit-scale traps found
this way: yfinance's `dividendYield`/`debtToEquity` are on a "whole
percentage" scale (0.34 meaning 0.34%, 78.445 meaning 78.4%) while our own
`dividend_yield`/`debt_to_equity` are plain fractions -- both need a
normalize_ours/normalize_external transform, not a naive direct diff).

Two real, serious pipeline findings surfaced JUST from this verification
pass, before any code even shipped -- see
doc/learnings/2026-09-08-data-sanity-layer.md's "Part 3" section for the
full writeup:
  - Our stored `ebitda` metric_value for AAPL is $39.0B; yfinance's
    `ebitda` is $168.0B; AND our own `ev_ebitda` metric backs out to
    ~$168B if you divide enterprise value by it -- meaning we already
    compute the RIGHT ebitda figure somewhere internally, it just isn't
    what landed in the `ebitda` metric_value row itself. A real internal
    inconsistency between two of our own outputs, not a "which source is
    right" question.
  - `roa` disagrees by ~3.5x (ours 7.8%, yfinance's 27.1%) -- yfinance's
    figure is much closer to AAPL's well-known real ROA. Possibly a
    denominator issue in our own formula. Not root-caused this session --
    the sanity layer's job is to surface it, not silently fix a
    fundamentals formula without the same verification rigor every other
    Mapper change in this project gets.

`peg_ratio` is included with a deliberately WIDE tolerance (40%/80%) --
verified live that yfinance's own `pegRatio` (2.52) and our `peg_ratio`
(1.24) disagree by roughly 2x for AAPL even though both are real,
computed numbers; almost certainly a genuine trailing-vs-forward-growth
methodology difference, not a bug -- tracked loosely rather than either
silenced or flagged critical for a difference this structural.

Chosen fields (deliberately excludes anything doc 02 scopes OUT of this
product -- analyst targets/ratings, short interest, technical/beta,
governance/ESG risk scores -- since we don't compute those at all, so
there's nothing to sanity-check against them):

  market_cap, shares_outstanding, trailing_pe, dividend_yield,
  debt_to_equity, price_to_book, price_to_sales, roe, roa,
  operating_margin, gross_margin, ebitda_margin, net_margin, quick_ratio,
  current_ratio, institutional_ownership_pct, payout_ratio, ebitda,
  ev_ebitda, ev_sales, revenue_growth_yoy, peg_ratio
  revenue_zero_check   -- NOT a pct_diff check -- flags the exact failure
                          mode found live 2026-09-07 (resolve() returning an
                          authoritative-but-spurious $0 for Revenue): our
                          latest-period revenue is 0/null while yfinance's
                          totalRevenue is a real, material number.

Reuses company_master/security_type.py's resolve_primary_tickers() (the
same "most companies have exactly one Common-Stock/ADR listing" mechanism
Alpaca/yfinance_industry.py already use) and shares the EXACT SAME
CrossProcessRateLimiter lock file as yfinance_industry.py
(DEFAULT_RATE_LIMITER_LOCK_PATH imported directly, not a second lock path)
-- both modules hit the same Yahoo endpoint, so they must share one
aggregate budget, not each independently pace against the full limit and
double real throughput when both happen to run in the same window.

Bulk-loads every "our value" lookup with one query each up front (never a
query per company in a loop -- see pipeline/CLAUDE.md's restatements.py N+1
lesson); only the yfinance fetch itself is per-ticker (unavoidable, it's a
network call), mirroring yfinance_industry.py's own loop shape exactly."""

from datetime import datetime, timezone
from decimal import Decimal

import psycopg
import structlog
import yfinance as yf
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed
from yfinance.exceptions import YFRateLimitError

from scrooner_pipeline.common.config import settings
from scrooner_pipeline.common.rate_limiter import CrossProcessRateLimiter
from scrooner_pipeline.company_master.security_type import resolve_primary_tickers
from scrooner_pipeline.company_master.yfinance_industry import DEFAULT_RATE_LIMITER_LOCK_PATH
from scrooner_pipeline.sanity.freshness_check import check_freshness, load_our_latest_period_ends, write_freshness_checks

logger = structlog.get_logger()

AGGREGATE_REQUEST_INTERVAL_SECONDS = 1.2  # matches yfinance_industry.py -- same shared lock file, must match its pace assumption
COMMIT_EVERY = 25

_rate_limiter = CrossProcessRateLimiter(
    max_per_second=1.0 / AGGREGATE_REQUEST_INTERVAL_SECONDS,
    lock_path=DEFAULT_RATE_LIMITER_LOCK_PATH,
)

# (our_metric_name, yfinance_info_key, minor_pct, major_pct, normalize_ours, normalize_external)
# -- the table-driven config every metric_value-backed check runs off.
# Severity thresholds are per-metric, not universal -- some metrics are
# expected to drift more than others (Alpaca's delayed-SIP price feed vs.
# whatever Yahoo's own quote source is, "trailing" window definitions
# rarely aligning to the day, or a genuine methodology difference like
# peg_ratio's). Chosen deliberately wide where real, expected drift exists
# -- not because a mismatch there doesn't matter, but because a tight
# threshold would flood every run with noise and bury the findings
# actually worth a human looking at. normalize_ours/normalize_external
# default to identity (None) -- only set when a real unit-scale mismatch
# was found and verified against a live value (see module docstring for
# the dividend_yield/debt_to_equity evidence).
_IDENTITY = None
_TIMES_100 = lambda v: v * Decimal(100)
_DIVIDE_100 = lambda v: v / Decimal(100)

METRIC_MAPPINGS: list[tuple[str, str, float, float, object, object]] = [
    ("market_cap", "marketCap", 10.0, 30.0, _IDENTITY, _IDENTITY),
    ("shares_outstanding", "sharesOutstanding", 3.0, 15.0, _IDENTITY, _IDENTITY),
    ("trailing_pe", "trailingPE", 15.0, 40.0, _IDENTITY, _IDENTITY),
    # yfinance's dividendYield is a whole-percentage number (0.34 meaning
    # 0.34%); ours is a plain fraction (0.0034) -- verified live against a
    # real AAPL value before trusting this, not assumed.
    ("dividend_yield", "dividendYield", 15.0, 40.0, _TIMES_100, _IDENTITY),
    # yfinance's debtToEquity is likewise a whole-percentage-scaled ratio
    # (78.445 meaning a 0.78 ratio); ours is a plain ratio -- same
    # live-verified trap as dividend_yield, opposite normalization side.
    ("debt_to_equity", "debtToEquity", 15.0, 40.0, _IDENTITY, _DIVIDE_100),
    ("price_to_book", "priceToBook", 10.0, 30.0, _IDENTITY, _IDENTITY),
    ("price_to_sales", "priceToSalesTrailing12Months", 10.0, 30.0, _IDENTITY, _IDENTITY),
    ("roe", "returnOnEquity", 25.0, 60.0, _IDENTITY, _IDENTITY),
    # Verified live: yfinance's returnOnAssets (27.1%) is ~3.5x ours
    # (7.8%) for AAPL -- a real, unexplained divergence worth surfacing,
    # not silenced by an artificially wide tolerance. See module docstring.
    ("roa", "returnOnAssets", 25.0, 60.0, _IDENTITY, _IDENTITY),
    ("operating_margin", "operatingMargins", 10.0, 25.0, _IDENTITY, _IDENTITY),
    ("gross_margin", "grossMargins", 10.0, 25.0, _IDENTITY, _IDENTITY),
    ("ebitda_margin", "ebitdaMargins", 10.0, 25.0, _IDENTITY, _IDENTITY),
    ("net_margin", "profitMargins", 10.0, 25.0, _IDENTITY, _IDENTITY),
    ("quick_ratio", "quickRatio", 15.0, 40.0, _IDENTITY, _IDENTITY),
    ("current_ratio", "currentRatio", 10.0, 30.0, _IDENTITY, _IDENTITY),
    ("institutional_ownership_pct", "heldPercentInstitutions", 15.0, 40.0, _IDENTITY, _IDENTITY),
    ("payout_ratio", "payoutRatio", 20.0, 50.0, _IDENTITY, _IDENTITY),
    # Verified live: our ebitda ($39.0B) vs. yfinance's ($168.0B) for AAPL
    # -- a ~330% gap, and our OWN ev_ebitda metric implies the ~$168B
    # figure is the one consistent with the rest of our pipeline. A real,
    # serious internal inconsistency this check exists specifically to
    # catch -- see module docstring.
    ("ebitda", "ebitda", 20.0, 50.0, _IDENTITY, _IDENTITY),
    ("ev_ebitda", "enterpriseToEbitda", 20.0, 50.0, _IDENTITY, _IDENTITY),
    ("ev_sales", "enterpriseToRevenue", 15.0, 40.0, _IDENTITY, _IDENTITY),
    ("revenue_growth_yoy", "revenueGrowth", 20.0, 50.0, _IDENTITY, _IDENTITY),
    # Deliberately wide -- verified live that yfinance's own pegRatio and
    # ours disagree by ~2x for AAPL even though both are real numbers,
    # almost certainly a genuine trailing-vs-forward-growth methodology
    # difference, not a bug. Tracked loosely, not silenced or over-flagged.
    ("peg_ratio", "pegRatio", 40.0, 80.0, _IDENTITY, _IDENTITY),
]

# Real finding, first full-population run (2026-09-08): a margin/ratio
# metric's "worst findings" list was dominated by microcap/shell companies
# with near-zero revenue or assets, where the ratio blows up to an
# absurd magnitude (net_margin of -480,577 -- i.e. -48 MILLION percent --
# for a company yfinance simply reports as 0.0) rather than anything a
# human would call a real disagreement. This is the exact same ROE/ROIC/
# margin degeneracy this project already guards against elsewhere
# (expanded_metrics.py's peer-comparison ranking bounds ROIC/margins to
# +/-200% for the identical reason: "the well-known ROE/ROIC/margin
# degeneracy for a company with near-zero invested capital or revenue,
# not real outperformance"). Applied here as a skip (not a severity),
# same as "yfinance has no usable opinion" -- an implausible ratio isn't
# a meaningful comparison in either direction, not evidence of a bug.
DEGENERACY_GUARD_METRICS = frozenset(
    {"net_margin", "gross_margin", "operating_margin", "ebitda_margin", "roa", "roe", "peg_ratio", "revenue_growth_yoy"}
)
DEGENERACY_GUARD_BOUND = Decimal(3)  # 300% -- generous, matches this project's existing +/-200% precedent with headroom

THRESHOLDS = {name: (minor, major) for name, _, minor, major, _, _ in METRIC_MAPPINGS}
_INFO_KEY_BY_METRIC = {name: info_key for name, info_key, *_ in METRIC_MAPPINGS}
_NORMALIZERS_BY_METRIC = {name: (norm_ours, norm_ext) for name, _, _, _, norm_ours, norm_ext in METRIC_MAPPINGS}

SEVERITY_OK = "ok"
SEVERITY_MINOR = "minor"
SEVERITY_MAJOR = "major"
SEVERITY_CRITICAL = "critical"
SEVERITY_MISSING_OURS = "missing_ours"
SEVERITY_MISSING_EXTERNAL = "missing_external"

REVENUE_ZERO_CHECK_MATERIAL_THRESHOLD = Decimal(1_000_000)


def _fetch_info_once(ticker: str) -> dict:
    _rate_limiter.wait()
    return yf.Ticker(ticker).get_info()


@retry(
    retry=retry_if_exception_type(YFRateLimitError),
    stop=stop_after_attempt(3),
    wait=wait_fixed(60),
    reraise=True,
)
def _fetch_info(ticker: str) -> dict:
    return _fetch_info_once(ticker)


def _severity_for(metric_name: str, pct_diff: Decimal) -> str:
    minor_pct, major_pct = THRESHOLDS[metric_name]
    abs_pct = abs(pct_diff)
    if abs_pct >= major_pct:
        return SEVERITY_MAJOR
    if abs_pct >= minor_pct:
        return SEVERITY_MINOR
    return SEVERITY_OK


def _pct_diff(our_value: Decimal, external_value: Decimal) -> Decimal:
    denom = abs(external_value) if external_value != 0 else Decimal(1)
    return (our_value - external_value) / denom * Decimal(100)


def _load_our_values(conn: psycopg.Connection, company_ids: list[int]) -> dict[int, dict[str, Decimal | None]]:
    """One query per metric source (metric_value, canonical_fact), never a
    query per company -- see module docstring."""
    values: dict[int, dict[str, Decimal | None]] = {cid: {} for cid in company_ids}

    with conn.cursor() as cur:
        # market_cap / trailing_pe: most-recent value per company (TTM-
        # preferred/latest-period_end, the same rule as screener/resolve.py
        # and apps/app's getLatestMetrics -- kept as a direct SQL port
        # here too, same reasoning: no cross-language import possible).
        metric_value_names = [name for name in _INFO_KEY_BY_METRIC if name not in ("shares_outstanding",)]
        cur.execute(
            """
            with ranked as (
                select mv.company_id, md.metric_name, mv.value,
                       row_number() over (
                           partition by mv.company_id, md.metric_name
                           order by (mv.period_label = 'TTM') desc, mv.period_end desc
                       ) as rn
                from analytics.metric_value mv
                join analytics.metric_definition md on md.id = mv.metric_definition_id
                where mv.company_id = any(%s) and md.metric_name = any(%s)
                  and mv.value is not null
            )
            select company_id, metric_name, value from ranked where rn = 1
            """,
            (company_ids, metric_value_names),
        )
        for company_id, metric_name, value in cur.fetchall():
            values[company_id][metric_name] = value

        # shares_outstanding: latest instant canonical_fact (a point-in-time
        # balance, not a period flow -- "most recent end_date" is the right
        # rule here, not TTM-preferred).
        cur.execute(
            """
            select cf.company_id, cf.value
            from analytics.canonical_fact cf
            join analytics.canonical_concept cc on cc.id = cf.canonical_concept_id
            join core.period p on p.id = cf.period_id
            where cf.company_id = any(%s) and cc.name = 'shares_outstanding'
            order by cf.company_id, p.end_date desc
            """,
            (company_ids,),
        )
        seen_shares: set[int] = set()
        for company_id, value in cur.fetchall():
            if company_id not in seen_shares:  # first row per company_id is the latest, since ordered end_date desc
                values[company_id]["shares_outstanding"] = value
                seen_shares.add(company_id)

        # revenue: latest-period value (any granularity) -- used only for
        # the zero-check special case below, never a pct_diff comparison
        # (a single quarter's revenue is not comparable to yfinance's
        # genuinely-TTM totalRevenue). Also tracks whether the company has
        # ANY revenue history at all -- calibrated live 2026-09-08: TSM,
        # Enbridge, and Ares Capital (a BDC -- see revenue's own doc 42
        # sector-isolation note, bdc_total_investment_income is the real
        # concept for BDCs) all have ZERO revenue canonical_fact rows ever,
        # a real, already-documented structural absence (Foreign Private
        # Issuer / BDC business-model reasons), NOT the resolve()
        # authoritative-$0 bug this check exists to catch. Without this
        # distinction, all three fired as false-positive "critical"
        # findings on the very first golden-10 test run.
        cur.execute(
            """
            select cf.company_id, cf.value
            from analytics.canonical_fact cf
            join analytics.canonical_concept cc on cc.id = cf.canonical_concept_id
            join core.period p on p.id = cf.period_id
            where cf.company_id = any(%s) and cc.name = 'revenue'
            order by cf.company_id, p.end_date desc
            """,
            (company_ids,),
        )
        seen_revenue: set[int] = set()
        for company_id, value in cur.fetchall():
            values[company_id]["revenue_has_history"] = Decimal(1)
            if company_id not in seen_revenue:
                values[company_id]["revenue_latest"] = value
                seen_revenue.add(company_id)

    return values


def _check_metric(company_id: int, metric_name: str, our_value: Decimal | None, external_value) -> dict | None:
    if external_value is None:
        return None  # yfinance itself has no opinion -- not our data problem, don't record noise
    external_decimal = Decimal(str(external_value))
    if not external_decimal.is_finite():
        # Real crash found live 2026-09-08, first full-population run:
        # yfinance genuinely returns inf/nan for some ratios (trailingPE
        # for a company with ~zero trailing earnings is a real, not-rare
        # case) -- `Decimal('Infinity') - Decimal('Infinity')` (which
        # `_pct_diff`'s subtract-then-divide-by-abs(external) can produce
        # even from a single infinite input) raises InvalidOperation, not
        # a normal float-style inf/inf=nan. An infinite ratio isn't a
        # comparable number anyway -- treat it the same as "yfinance has
        # no usable opinion" rather than crashing the whole batch.
        return None
    normalize_ours, normalize_external = _NORMALIZERS_BY_METRIC.get(metric_name, (_IDENTITY, _IDENTITY))
    if normalize_external is not None:
        external_decimal = normalize_external(external_decimal)
    if our_value is None:
        return {
            "company_id": company_id, "metric_name": metric_name, "our_value": None,
            "external_value": external_decimal, "pct_diff": None, "severity": SEVERITY_MISSING_OURS,
            "note": None,
        }
    if metric_name in DEGENERACY_GUARD_METRICS and abs(our_value) > DEGENERACY_GUARD_BOUND:
        return None  # implausible ratio (near-zero revenue/assets denominator) -- not a meaningful comparison either way
    normalized_ours = normalize_ours(our_value) if normalize_ours is not None else our_value
    pct_diff = _pct_diff(normalized_ours, external_decimal)
    return {
        # Stored NORMALIZED, not raw -- so a report reader sees both
        # values already on the same scale (e.g. dividend_yield shown as
        # 0.34 vs 0.34, not the misleading-looking 0.0034 vs 0.34) rather
        # than needing to know this metric's own normalization rule to
        # make sense of the row.
        "company_id": company_id, "metric_name": metric_name, "our_value": normalized_ours,
        "external_value": external_decimal, "pct_diff": pct_diff,
        "severity": _severity_for(metric_name, pct_diff), "note": None,
    }


def _check_revenue_zero(company_id: int, our_revenue: Decimal | None, has_revenue_history: bool, external_total_revenue) -> dict | None:
    if external_total_revenue is None or not has_revenue_history:
        # No revenue concept ever captured for this company at all -- a
        # real, structural absence (Foreign Private Issuer/BDC/etc, see
        # this function's caller), not the bug this check targets. Stays
        # silent rather than recording a guaranteed-false "critical" --
        # coverage of "do we have revenue at all" is doc/status/
        # DATA_COVERAGE.md's job, not this layer's.
        return None
    external_decimal = Decimal(str(external_total_revenue))
    is_ours_zero_or_missing = our_revenue is None or our_revenue == 0
    is_external_material = external_decimal >= REVENUE_ZERO_CHECK_MATERIAL_THRESHOLD
    if is_ours_zero_or_missing and is_external_material:
        return {
            "company_id": company_id, "metric_name": "revenue_zero_check",
            "our_value": our_revenue if our_revenue is not None else Decimal(0),
            "external_value": external_decimal, "pct_diff": None, "severity": SEVERITY_CRITICAL,
            "note": "Our most-recent revenue is 0/missing while yfinance reports a material totalRevenue -- "
                    "same SHAPE as the resolve() authoritative-$0 bug found 2026-09-07, but not necessarily the "
                    "same root cause (a real, different example found live 2026-09-08: Commerce Bancshares, a "
                    "bank whose only mapped revenue tag is interest income alone, missing non-interest income -- "
                    "a completeness gap, not a resolve() bug). Run `scrooner-sanity investigate` to find the real cause.",
        }
    return None  # not every company gets a row here -- this check only ever fires on the failure mode, not routinely


def run_sanity_checks(conn: psycopg.Connection, company_ids: list[int]) -> dict:
    stats = {"considered": len(company_ids), SEVERITY_OK: 0, SEVERITY_MINOR: 0, SEVERITY_MAJOR: 0,
              SEVERITY_CRITICAL: 0, SEVERITY_MISSING_OURS: 0, SEVERITY_MISSING_EXTERNAL: 0, "no_ticker": 0}
    if not company_ids:
        return stats

    our_values = _load_our_values(conn, company_ids)
    ticker_by_company = resolve_primary_tickers(conn, _ciks_for(conn, company_ids))
    cik_by_company = _cik_by_company(conn, company_ids)
    latest_period_end_by_company = load_our_latest_period_ends(conn, company_ids)

    pending: list[dict] = []
    freshness_pending: list[dict] = []
    evaluated_ids: list[int] = []  # companies we got a real yfinance answer for THIS run -- see _write_batch's
                                    # own docstring for why only these get their stale rows cleared, not a
                                    # company we skipped due to a transient fetch failure/no ticker/rate limit.
    for i, company_id in enumerate(company_ids):
        cik = cik_by_company.get(company_id)
        ticker = ticker_by_company.get(cik) if cik else None
        if ticker is None:
            stats["no_ticker"] += 1
            continue

        try:
            info = _fetch_info(ticker)
        except YFRateLimitError:
            logger.warning("sanity.rate_limited", ticker=ticker)
            continue
        except Exception as e:  # yfinance's own network/parsing failures are not typed consistently
            logger.warning("sanity.fetch_failed", ticker=ticker, error=str(e))
            continue

        evaluated_ids.append(company_id)

        if not info or info.get("quoteType") is None:
            stats[SEVERITY_MISSING_EXTERNAL] += 1
            continue

        rows = []
        for metric_name, info_key in _INFO_KEY_BY_METRIC.items():
            row = _check_metric(company_id, metric_name, our_values[company_id].get(metric_name), info.get(info_key))
            if row is not None:
                rows.append(row)
        revenue_row = _check_revenue_zero(
            company_id, our_values[company_id].get("revenue_latest"),
            our_values[company_id].get("revenue_has_history") is not None, info.get("totalRevenue"),
        )
        if revenue_row is not None:
            rows.append(revenue_row)

        for row in rows:
            stats[row["severity"]] += 1
        pending.extend(rows)

        # Freshness (doc 45 P0): reuses this SAME `info` payload, zero
        # extra yfinance requests. Unix timestamp -> date, matching
        # core.period.end_date's own type.
        most_recent_quarter_ts = info.get("mostRecentQuarter")
        most_recent_quarter_date = (
            datetime.fromtimestamp(most_recent_quarter_ts, tz=timezone.utc).date() if most_recent_quarter_ts else None
        )
        freshness_pending.append(
            check_freshness(company_id, latest_period_end_by_company.get(company_id), most_recent_quarter_date)
        )

        if len(evaluated_ids) >= COMMIT_EVERY or i == len(company_ids) - 1:
            conn = _write_batch(conn, evaluated_ids, pending)
            write_freshness_checks(conn, freshness_pending)
            pending = []
            evaluated_ids = []
            freshness_pending = []

    logger.info("sanity.done", **stats)
    return stats


def _ciks_for(conn: psycopg.Connection, company_ids: list[int]) -> set[str]:
    with conn.cursor() as cur:
        cur.execute("select cik from core.company where id = any(%s)", (company_ids,))
        return {r[0] for r in cur.fetchall()}


def _cik_by_company(conn: psycopg.Connection, company_ids: list[int]) -> dict[int, str]:
    with conn.cursor() as cur:
        cur.execute("select id, cik from core.company where id = any(%s)", (company_ids,))
        return dict(cur.fetchall())


_INSERT_SQL = """
    insert into analytics.data_sanity_check
        (company_id, metric_name, our_value, external_value, pct_diff, severity, note, checked_at)
    values
        (%(company_id)s, %(metric_name)s, %(our_value)s, %(external_value)s, %(pct_diff)s, %(severity)s, %(note)s, %(checked_at)s)
    on conflict (company_id, metric_name) do update
        set our_value = excluded.our_value, external_value = excluded.external_value,
            pct_diff = excluded.pct_diff, severity = excluded.severity, note = excluded.note,
            checked_at = excluded.checked_at
"""


def _write_batch(conn: psycopg.Connection, evaluated_company_ids: list[int], rows: list[dict]) -> psycopg.Connection:
    """Delete-then-reinsert, scoped to the companies actually evaluated
    this run -- NOT a plain per-row upsert. Found live 2026-09-08, first
    real test run: a check that no longer fires (e.g. revenue_zero_check
    after the false-positive fix below) leaves NO row in `rows` for that
    (company_id, metric_name), so a plain upsert never touches the OLD
    row from a previous run when that finding was still (wrongly) firing
    -- it just sits there stale forever. Deleting every existing row for
    each evaluated company before reinserting is the same discipline this
    project already uses everywhere else a batch job's output set can
    shrink between runs (resolve.py, concept_fallback.py). Only companies
    we got a REAL yfinance answer for this run are in evaluated_company_ids
    -- a company skipped for a transient fetch failure/rate limit/no
    ticker keeps its last-known-good rows untouched, not wiped just
    because this run couldn't reach it.

    Returns the connection to keep using -- see yfinance_industry.py's own
    _write_batch for why a long-running fetch loop needs this exact
    reconnect-on-drop shape."""
    if not evaluated_company_ids:
        return conn
    now = datetime.now(timezone.utc)
    params = [{**row, "checked_at": now} for row in rows]
    try:
        with conn.cursor() as cur:
            cur.execute("delete from analytics.data_sanity_check where company_id = any(%s)", (evaluated_company_ids,))
            if params:
                cur.executemany(_INSERT_SQL, params)
        conn.commit()
        return conn
    except psycopg.OperationalError:
        logger.warning("sanity.connection_dropped_reconnecting", rows=len(rows))
        fresh_conn = psycopg.connect(settings.database_url)
        with fresh_conn.cursor() as cur:
            cur.execute("delete from analytics.data_sanity_check where company_id = any(%s)", (evaluated_company_ids,))
            if params:
                cur.executemany(_INSERT_SQL, params)
        fresh_conn.commit()
        return fresh_conn


def pick_rotation_batch(conn: psycopg.Connection, limit: int) -> list[int]:
    """Coldest-checked-first rotation: a company never checked comes before
    one checked yesterday. This is what makes 'continuous run' actually
    cycle through the whole active population over time instead of the
    same handful of companies every day -- see module docstring's yfinance
    rate-limit reasoning for why we can't just check everyone daily."""
    with conn.cursor() as cur:
        cur.execute(
            """
            select c.id
            from core.company c
            left join (
                select company_id, max(checked_at) as last_checked
                from analytics.data_sanity_check
                group by company_id
            ) s on s.company_id = c.id
            where c.status = 'active'
            order by s.last_checked asc nulls first, c.id
            limit %s
            """,
            (limit,),
        )
        return [r[0] for r in cur.fetchall()]
