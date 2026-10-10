"""Period completeness check (2026-09-30, migration 0083; widened
2026-10-04, Phase 0 of the "every financial column filled since 2015"
plan -- see pipeline/CLAUDE.md's same-day entry).

For every active company, which quarters/years of a key concept are
missing, and why. Expected periods come from the company's own 10-Q/10-K
filings (period_of_report): a 10-Q should yield a quarter, a 10-K a full
year and a Q4 (derived is fine); balance-sheet concepts need the period-end
snapshot. Only (company, concept) pairs with at least one value since
HISTORY_START are checked -- a concept that is absent entirely is the tag
library's question (company_concept_lineage), not this one.

HISTORY_START is 2015-01-01 -- the project's floor for "every financial
column filled since 2015, or since listing if later." A company listed
after 2015 is automatically scoped correctly: expected_filing is built
from the company's own real core.filing rows, so nothing is expected
before its first real filing exists. CHECK_CONCEPTS covers 16 concepts,
deliberately the GAAP-universal ones only (see that dict's own comment
for which were left out and why) -- the population-conditional concepts
(dividends, buybacks, COGS-based concepts) need coverage_matrix.py's
applicable_population mechanism wired in here first, or they'd report
millions of real "a non-payer doesn't pay dividends" cells as fake gaps.

Every missing cell gets one cause (see analytics.period_gap's check list).
The cause is what makes a gap fixable: the same blank P/E can come from a
filing we never processed, a filing SEC's feed doesn't contain, or two
filings disagreeing by a rounding difference (Airbnb FY2025 net income,
$2,511,000,000 vs $2,511,277,000).

Findings are stored, not just printed:
- analytics.period_gap: one row per missing cell (rebuilt each run).
- analytics.period_completeness: expected / present / missing per pair.
- analytics.company_data_finding: one finding per (company, concept, cause),
  evidence->>'source' = 'period_completeness'. A cause that no longer occurs
  is marked 'fixed' with resolved_at, so the record of what was wrong and
  when it cleared is kept for the next round of improvements.

Usage:
  uv run python -m scrooner_pipeline.sanity.period_completeness
  uv run python -m scrooner_pipeline.sanity.period_completeness --ciks 0001559720,0000721371
"""

import json
from datetime import date
from decimal import Decimal

import psycopg
import structlog
import typer

from scrooner_pipeline.common.config import settings
from scrooner_pipeline.common.sec_client import SECClient

logger = structlog.get_logger()

# 2026-10-04, Phase 0 of the "every financial column filled since 2015"
# plan: widened from 2019-01-01. A company listed after this date is
# naturally unaffected -- expected_filing is built from the company's own
# real core.filing rows, so there's nothing to expect before it existed.
HISTORY_START = date(2015, 1, 1)
DATE_TOLERANCE_DAYS = 7
QUARTER_DAYS = (80, 100)
YEAR_DAYS = (340, 380)
# Filed values this close are a rounding difference (Airbnb: 0.011%), not
# a genuine disagreement.
ROUNDING_SPREAD = Decimal("0.001")

# checked concept -> (shape, base concept whose mapped tags are traced)
CHECK_CONCEPTS: dict[str, tuple[str, str]] = {
    # Checked concept (the first tuple element) must be the *_resolved
    # display companion the company page/screener actually reads, not the
    # raw canonical concept -- found live 2026-10-02: the first run (09-30)
    # checked 5 of 6 raw concepts directly, so every conflict a later stage
    # (conflict_resolution.py's restatement fill, 8e5599e) already closed
    # still looked like an open gap. net_income_resolved already had
    # Airbnb's FY2025 ($2,511,277,000, the corrected latest-filing value)
    # and JPMorgan's full FY series on the exact run that reported them
    # missing. revenue was the one concept already done right.
    "revenue_sanity_resolved": ("duration", "revenue"),
    "net_income_resolved": ("duration", "net_income"),
    "diluted_eps_resolved": ("duration", "diluted_eps"),
    "cfo_resolved": ("duration", "cfo"),
    "total_assets_resolved": ("instant", "total_assets"),
    "stockholders_equity_resolved": ("instant", "stockholders_equity"),
    # Added 2026-10-04, Phase 0: every concept here is GAAP-universal for
    # a real operating company's statements (not merely common) -- every
    # 10-K/10-Q that has an income statement must have these income-
    # statement lines, every balance sheet must have these balance-sheet
    # lines, and every cash-flow statement is legally 3 sections
    # (operating/investing/financing), so a missing cell here is always a
    # real gap, never a structural non-applicability. Deliberately NOT
    # added: cost_of_revenue/gross_profit/operating_expenses (banks,
    # insurers, REITs genuinely lack a COGS-based P&L -- already
    # documented, needs population gating first), ppe_net/capex
    # (asset-light companies can genuinely have near-zero PP&E),
    # interest_expense (a real debt-free company has none to report),
    # dividends_paid/dividends_per_share/share_buybacks (population-
    # conditional on being a payer/repurchaser). Those need
    # coverage_matrix.py's applicable_population mechanism wired into
    # this checker before they can be added without manufacturing false
    # gaps -- a real, sized follow-on, not done here.
    "operating_income_resolved": ("duration", "operating_income"),
    "income_before_tax_resolved": ("duration", "income_before_tax"),
    "income_tax_expense_resolved": ("duration", "income_tax_expense"),
    "basic_eps_resolved": ("duration", "basic_eps"),
    "cash_flow_investing_resolved": ("duration", "cash_flow_investing"),
    "cash_flow_financing_resolved": ("duration", "cash_flow_financing"),
    "total_liabilities_resolved": ("instant", "total_liabilities"),
    "current_assets_resolved": ("instant", "current_assets"),
    "current_liabilities_resolved": ("instant", "current_liabilities"),
    "cash_and_equivalents_resolved": ("instant", "cash_and_equivalents"),
}

# cause -> (company_data_finding.finding_type, stable summary text)
CAUSES: dict[str, tuple[str, str]] = {
    "filing_not_processed": (
        "pipeline_bug",
        "Periods missing: filing never normalized",
    ),
    "not_in_sec_feed": (
        "data_limit",
        "Periods missing: filing absent from SEC Company Facts",
    ),
    "conflict_rounding": (
        "pipeline_bug",
        "Periods missing: filings disagree by a rounding difference",
    ),
    "conflict_split": (
        "pipeline_bug",
        "Periods missing: filings disagree by a stock-split ratio",
    ),
    "conflict_material": (
        "filer_error",
        "Periods missing: filings disagree materially",
    ),
    "not_resolved": (
        "pipeline_bug",
        "Periods missing: authoritative fact not resolved",
    ),
    "q4_not_derived": ("pipeline_bug", "Periods missing: Q4 not derived"),
    "quarter_not_derived": (
        "pipeline_bug",
        "Periods missing: quarter filed only as year-to-date",
    ),
    "no_mapped_tag": (
        "data_limit",
        "Periods missing: no mapped tag in the filing",
    ),
}


# Found live 2026-10-05 (cockpit triage, doc/planning/51 Finding 4):
# _is_split_ratio() was being applied to EVERY concept's conflicting
# values, with no awareness that only per-share/share-count concepts can
# legitimately be affected by a stock split. Real dollar-value concepts
# (total_assets, revenue, net_income, cfo, etc.) were showing up
# mislabeled "conflict_split" with ratios like 41x, 938x -- real material
# disagreements (in at least one case, Palatin Technologies' Q4 2019
# net income, a genuine ~1000x filer unit-scale typo) hidden under an
# incorrect "harmless split" label. Scoped to the same 4 concepts
# mapper/dedup_majority_resolver.py's own SPLIT_AWARE_CONCEPTS already
# treats as legitimately split-sensitive.
SPLIT_AWARE_BASE_CONCEPTS = frozenset(
    {"basic_eps", "diluted_eps", "dividends_per_share", "shares_outstanding"}
)


def _is_split_ratio(values: list[Decimal]) -> bool:
    """Pre- and post-split per-share values filed for the same period
    (Apple's 2020 4-for-1: $12.73 vs $3.18 diluted EPS). True when every
    value is the smallest in magnitude times a whole number >= 2, within 2%.
    Caller must restrict this to SPLIT_AWARE_BASE_CONCEPTS first -- see
    that constant's own comment for why."""
    nonzero = [abs(v) for v in values if v != 0]
    if len(nonzero) < 2 or len({v > 0 for v in values if v != 0}) > 1:
        return False
    base = min(nonzero)
    ratios = [v / base for v in nonzero if v != base]
    return bool(ratios) and all(
        r >= Decimal("1.9") and abs(r - r.to_integral_value()) <= Decimal("0.02") * r
        for r in ratios
    )


def classify(
    *,
    filing_has_facts: bool,
    later_filing_has_facts: bool,
    sec_feed_has_filing: bool | None = None,
    authoritative_facts: int,
    conflicting_values: list[Decimal],
    ytd_facts: int,
    period_kind: str,
    fy_present: bool,
    base_concept: str = "",
) -> str:
    """The single cause for one missing (company, concept, period) cell.
    `base_concept` (the CHECK_CONCEPTS base name, e.g. "total_assets")
    gates whether conflict_split classification is even attempted --
    see SPLIT_AWARE_BASE_CONCEPTS. Defaults to "" (never split-aware)
    so any other caller that doesn't pass it keeps the safe, conservative
    behavior rather than silently becoming split-aware by omission."""
    if not filing_has_facts:
        # Confirmed against SEC when checked; otherwise a later processed
        # filing means the payload was normalized and simply lacked it.
        if sec_feed_has_filing is True:
            return "filing_not_processed"
        if sec_feed_has_filing is False or later_filing_has_facts:
            return "not_in_sec_feed"
        return "filing_not_processed"
    if authoritative_facts:
        return "not_resolved"
    if conflicting_values:
        high = max(conflicting_values)
        low = min(conflicting_values)
        scale = max(abs(high), abs(low))
        if scale == 0 or (high - low) / scale <= ROUNDING_SPREAD:
            return "conflict_rounding"
        if base_concept in SPLIT_AWARE_BASE_CONCEPTS and _is_split_ratio(
            conflicting_values
        ):
            return "conflict_split"
        return "conflict_material"
    if period_kind == "Q4" and fy_present:
        return "q4_not_derived"
    if period_kind == "Q" and ytd_facts:
        return "quarter_not_derived"
    return "no_mapped_tag"


def _period_match_sql(alias: str, cell: str = "e") -> str:
    """SQL predicate: period `alias` matches expected cell `cell` (por, kind)."""
    return f"""
        abs({alias}.end_date - {cell}.por) <= {DATE_TOLERANCE_DAYS}
        and case {cell}.kind
            when 'I' then {alias}.period_type = 'instant'
            when 'FY' then {alias}.period_type = 'duration'
                 and ({alias}.end_date - {alias}.start_date) between {YEAR_DAYS[0]} and {YEAR_DAYS[1]}
            else {alias}.period_type = 'duration'
                 and ({alias}.end_date - {alias}.start_date) between {QUARTER_DAYS[0]} and {QUARTER_DAYS[1]}
        end"""


# Every 10-Q/10-K cover page carries this tag, so its companyconcept list
# of accessions shows which filings SEC's Company Facts actually contains.
# Found 2026-09-30: PayPal's 2026-07-28 10-Q was absent from SEC's own feed
# two months after filing, so "no facts" alone can't tell our miss from
# SEC's.
_FEED_PROBE_TAGS = (
    ("dei", "EntityCommonStockSharesOutstanding"),
    ("us-gaap", "Assets"),
)
# Give SEC's feed a week to pick a filing up before calling it absent.
FEED_GRACE_DAYS = 7


def _sec_feed_accessions(client: SECClient, cik: str) -> set[str] | None:
    """Found live 2026-10-09 (cockpit ticket-status deep dive): this used
    to return on the FIRST 200-status response, even when that response's
    own `units` dict was EMPTY -- confirmed via direct comparison against
    SEC's bulk companyfacts endpoint (and our own already-fetched
    raw.sec_companyfacts blob) for 3 real, large, actively-filing
    companies (V. F. Corporation, Monro Inc, Masco Corp): SEC's
    companyconcept single-tag endpoint returns `{"units": {"USD": {}}}`
    (an empty dict, not even an empty list) for `us-gaap:Assets` for all
    three, despite the bulk companyfacts endpoint and our own stored
    payload both having 100+ real Assets facts spanning decades for the
    same CIK. A real, actively-filing company always has SOME historical
    accession under at least one of these cover-page-universal tags --
    an empty result from EVERY probe tag means the companyconcept
    endpoint itself is unreliable for this CIK, not that the filing is
    genuinely absent. Fixed: only trust a probe's result if it's
    non-empty, and keep trying the remaining probe tags before giving up;
    return None (unknown, not "confirmed absent") only when every probe
    tag comes back empty or unreachable -- `classify()`'s caller then
    correctly falls through to "filing_not_processed" (ours to fix) for
    the real not_in_sec_feed-labeled findings this bug fabricated,
    instead of the misleading "data_limit" (not fixable) label."""
    for taxonomy, tag in _FEED_PROBE_TAGS:
        url = f"https://data.sec.gov/api/xbrl/companyconcept/CIK{cik}/{taxonomy}/{tag}.json"
        try:
            resp = client.get(url)
        except Exception:  # 404 for a company without the tag, network errors
            continue
        if resp.status_code != 200:
            continue
        units = resp.json().get("units", {})
        accessions = {row["accn"] for rows in units.values() for row in rows}
        if accessions:
            return accessions
    return None


def _verify_against_sec_feed(cur) -> dict:
    """Mark each filing that has no facts (and nothing newer processed) as
    present in / absent from SEC's feed, on expected_filing."""
    cur.execute("alter table expected_filing add column sec_feed_has_filing boolean")
    cur.execute(
        """
        select f.filing_id, c.cik, fl.accession_number
        from expected_filing f
        join core.company c on c.id = f.company_id
        join core.filing fl on fl.id = f.filing_id
        left join last_processed lp on lp.company_id = f.company_id
        where not f.has_facts
          and not coalesce(lp.last_date > f.filing_date, false)
          and f.filing_date <= current_date - %s
        """,
        (FEED_GRACE_DAYS,),
    )
    by_cik: dict[str, list] = {}
    for filing_id, cik, accession in cur.fetchall():
        by_cik.setdefault(cik, []).append((filing_id, accession))
    stats = {"checked": 0, "in_feed": 0, "absent": 0, "unknown": 0}
    results = []
    with SECClient() as client:
        for cik, filings in by_cik.items():
            accessions = _sec_feed_accessions(client, cik)
            for filing_id, accession in filings:
                stats["checked"] += 1
                if accessions is None:
                    stats["unknown"] += 1
                    continue
                present = accession in accessions
                stats["in_feed" if present else "absent"] += 1
                results.append((present, filing_id))
    if results:
        cur.executemany(
            "update expected_filing set sec_feed_has_filing = %s where filing_id = %s",
            results,
        )
    logger.info("period_completeness.sec_feed_verified", **stats)
    return stats


def _build_expected_filings(cur, company_ids: list[int] | None) -> None:
    cur.execute(
        """
        create temp table expected_filing on commit drop as
        select f.id as filing_id, f.company_id, f.form, f.period_of_report as por,
               f.filing_date,
               exists (select 1 from core.fact x where x.filing_id = f.id) as has_facts
        from core.filing f
        join core.company c on c.id = f.company_id and c.status = 'active'
        where f.form in ('10-Q', '10-K') and not f.is_amendment
          and f.period_of_report between %(start)s and current_date
          and (%(ids)s::bigint[] is null or f.company_id = any(%(ids)s::bigint[]))
        """,
        {"start": HISTORY_START, "ids": company_ids},
    )
    cur.execute(
        """
        create temp table last_processed on commit drop as
        select company_id, max(filing_date) as last_date
        from expected_filing where has_facts group by company_id
        """
    )


def _check_concept(cur, concept: str, shape: str, base: str) -> dict:
    cur.execute(
        "select id from analytics.canonical_concept where name = %s", (concept,)
    )
    concept_id = cur.fetchone()[0]
    cur.execute("select id from analytics.canonical_concept where name = %s", (base,))
    base_id = cur.fetchone()[0]

    kinds = (
        "array['I']"
        if shape == "instant"
        else "case when f.form = '10-K' then array['FY', 'Q4'] else array['Q'] end"
    )
    cur.execute("drop table if exists cell, cfp, gap_cell, gap_period, company_tag")
    # Present canonical periods for this concept, one row per period.
    cur.execute(
        """
        create temp table cfp on commit drop as
        select cf.company_id, p.start_date, p.end_date, p.period_type
        from analytics.canonical_fact cf
        join core.period p on p.id = cf.period_id
        where cf.canonical_concept_id = %s and p.end_date >= %s
          and cf.company_id in (select distinct company_id from expected_filing)
        """,
        (concept_id, HISTORY_START),
    )
    cur.execute("create index on cfp (company_id, end_date)")
    cur.execute(
        f"""
        create temp table cell on commit drop as
        select f.filing_id, f.company_id, f.por, f.filing_date, f.has_facts,
               coalesce(lp.last_date > f.filing_date, false) as later_has_facts,
               f.sec_feed_has_filing,
               k.kind
        from expected_filing f
        cross join lateral unnest({kinds}) as k(kind)
        left join last_processed lp on lp.company_id = f.company_id
        where f.company_id in (select distinct company_id from cfp)
        """
    )
    cur.execute(
        f"""
        create temp table gap_cell on commit drop as
        select e.* from cell e
        where not exists (select 1 from cfp p where p.company_id = e.company_id
                          and {_period_match_sql("p")})
        """
    )
    # Trace the base concept's mapped tags (plus any company preference) for
    # every missing cell: authoritative count, conflicting values, YTD facts.
    # Three exact steps so every core.fact lookup is a (company_id,
    # concept_id, period_id) index hit -- a first version joined core.fact by
    # tag and scanned for minutes per concept.
    cur.execute("drop table if exists gap_period, company_tag")
    cur.execute(
        f"""
        create temp table gap_period on commit drop as
        select e.company_id, e.filing_id, e.por, e.kind, p.id as period_id,
               p.start_date, p.end_date, p.period_type
        from gap_cell e
        join core.period p on p.company_id = e.company_id
             and p.end_date between e.por - {DATE_TOLERANCE_DAYS} and e.por + {DATE_TOLERANCE_DAYS}
        where e.has_facts
        """
    )
    cur.execute(
        """
        create temp table company_tag on commit drop as
        select g.company_id, m.concept_id
        from (select distinct company_id from gap_period) g
        cross join analytics.concept_mapping m
        where m.canonical_concept_id = %(base)s and m.confidence <> 'rejected'
        union
        select tp.company_id, c.id
        from analytics.company_tag_preference tp
        join core.concept c on c.taxonomy = tp.taxonomy and c.tag = tp.tag
        where tp.canonical_concept_id = %(base)s
        """,
        {"base": base_id},
    )
    cur.execute(
        f"""
        with traced as (
            select gp.company_id, gp.filing_id, gp.por, gp.kind, f.value, f.is_authoritative,
                   (gp.end_date - gp.start_date) as span, gp.period_type,
                   ({_period_match_sql("gp", "gp")}) as match
            from gap_period gp
            join company_tag t on t.company_id = gp.company_id
            join core.fact f on f.company_id = gp.company_id and f.concept_id = t.concept_id
                 and f.period_id = gp.period_id
        ),
        agg as (
            select company_id, filing_id, por, kind,
                   count(*) filter (where is_authoritative and match) as n_auth,
                   array_agg(distinct value) filter (where not is_authoritative and match) as conflicts,
                   count(*) filter (where kind = 'Q' and period_type = 'duration'
                                    and span > {QUARTER_DAYS[1]}) as n_ytd
            from traced group by 1, 2, 3, 4
        )
        select e.company_id, e.filing_id, e.por, e.kind, e.has_facts, e.later_has_facts,
               e.sec_feed_has_filing,
               coalesce(a.n_auth, 0), a.conflicts, coalesce(a.n_ytd, 0),
               exists (select 1 from cfp y where y.company_id = e.company_id
                       and abs(y.end_date - e.por) <= {DATE_TOLERANCE_DAYS}
                       and y.period_type = 'duration'
                       and (y.end_date - y.start_date) between {YEAR_DAYS[0]} and {YEAR_DAYS[1]})
        from gap_cell e
        left join agg a on a.company_id = e.company_id and a.filing_id = e.filing_id
             and a.por = e.por and a.kind = e.kind
        """
    )
    rows = cur.fetchall()

    gaps = []
    for (
        company_id,
        filing_id,
        por,
        kind,
        has_facts,
        later,
        in_feed,
        n_auth,
        conflicts,
        n_ytd,
        fy_present,
    ) in rows:
        cause = classify(
            filing_has_facts=has_facts,
            later_filing_has_facts=later,
            sec_feed_has_filing=in_feed,
            authoritative_facts=n_auth or 0,
            conflicting_values=list(conflicts or []),
            ytd_facts=n_ytd or 0,
            period_kind=kind,
            fy_present=fy_present,
            base_concept=base,
        )
        detail = {"filing_id": filing_id}
        if in_feed is not None:
            detail["sec_feed_has_filing"] = in_feed
        if conflicts:
            detail["filed_values"] = [str(v) for v in sorted(conflicts)]
        gaps.append(
            (company_id, concept_id, kind, por, filing_id, cause, json.dumps(detail))
        )

    # A Q4 whose full year is itself missing has the full year's cause.
    fy_cause = {(g[0], g[3]): g[5] for g in gaps if g[2] == "FY"}
    gaps = [
        (*g[:5], fy_cause.get((g[0], g[3]), g[5]), g[6]) if g[2] == "Q4" else g
        for g in gaps
    ]

    cur.execute(
        "select company_id, count(*), min(por), max(por) from cell group by company_id"
    )
    expected = {r[0]: r[1:] for r in cur.fetchall()}
    missing_by_company: dict[int, int] = {}
    for g in gaps:
        missing_by_company[g[0]] = missing_by_company.get(g[0], 0) + 1
    return {
        "concept_id": concept_id,
        "gaps": gaps,
        "completeness": [
            (
                cid,
                concept_id,
                n,
                n - missing_by_company.get(cid, 0),
                missing_by_company.get(cid, 0),
                first,
                last,
            )
            for cid, (n, first, last) in expected.items()
        ],
    }


def _write(cur, results: list[dict], company_ids: list[int] | None) -> dict:
    concept_ids = [r["concept_id"] for r in results]
    scope = "and company_id = any(%(ids)s::bigint[])" if company_ids else ""
    params = {"concepts": concept_ids, "ids": company_ids}
    cur.execute(
        f"delete from analytics.period_gap where canonical_concept_id = any(%(concepts)s) {scope}",
        params,
    )
    cur.execute(
        f"delete from analytics.period_completeness where canonical_concept_id = any(%(concepts)s) {scope}",
        params,
    )
    gaps = [g for r in results for g in r["gaps"]]
    for i in range(0, len(gaps), 5000):
        cur.executemany(
            """
            insert into analytics.period_gap
                (company_id, canonical_concept_id, period_kind, period_end, filing_id, gap_cause, detail)
            values (%s, %s, %s, %s, %s, %s, %s)
            on conflict do nothing
            """,
            gaps[i : i + 5000],
        )
    completeness = [c for r in results for c in r["completeness"]]
    for i in range(0, len(completeness), 5000):
        cur.executemany(
            """
            insert into analytics.period_completeness
                (company_id, canonical_concept_id, expected, present, missing, first_expected, last_expected)
            values (%s, %s, %s, %s, %s, %s, %s)
            """,
            completeness[i : i + 5000],
        )

    # One finding per (company, concept, cause).
    grouped: dict[tuple, list] = {}
    for company_id, concept_id, kind, por, _filing, cause, _detail in gaps:
        grouped.setdefault((company_id, concept_id, cause), []).append((por, kind))
    findings = []
    for (company_id, concept_id, cause), periods in grouped.items():
        finding_type, summary = CAUSES[cause]
        periods.sort(reverse=True)
        evidence = {
            "source": "period_completeness",
            "cause": cause,
            "missing_periods": len(periods),
            "latest": [f"{p.isoformat()} {k}" for p, k in periods[:12]],
        }
        findings.append(
            (company_id, concept_id, finding_type, summary, json.dumps(evidence))
        )
    for i in range(0, len(findings), 5000):
        cur.executemany(
            """
            insert into analytics.company_data_finding
                (company_id, canonical_concept_id, finding_type, summary, evidence)
            values (%s, %s, %s, %s, %s)
            on conflict (company_id, canonical_concept_id, summary) do update
                set evidence = excluded.evidence,
                    finding_type = excluded.finding_type,
                    status = case when analytics.company_data_finding.status = 'wont_fix'
                                  then 'wont_fix' else 'open' end,
                    resolved_at = case when analytics.company_data_finding.status = 'wont_fix'
                                       then analytics.company_data_finding.resolved_at end
            """,
            findings[i : i + 5000],
        )
    # Causes that no longer occur are fixed; the row stays as history.
    cur.execute(
        "create temp table current_finding (company_id bigint, concept_id bigint, summary text) on commit drop"
    )
    cur.executemany(
        "insert into current_finding values (%s, %s, %s)",
        [(f[0], f[1], f[3]) for f in findings],
    )
    cur.execute(
        f"""
        update analytics.company_data_finding d
        set status = 'fixed', resolved_at = now()
        where d.evidence->>'source' = 'period_completeness'
          and d.status = 'open'
          and d.canonical_concept_id = any(%(concepts)s)
          {scope.replace("company_id", "d.company_id")}
          and not exists (select 1 from current_finding c
                          where c.company_id = d.company_id and c.concept_id = d.canonical_concept_id
                            and c.summary = d.summary)
        """,
        params,
    )
    fixed = cur.rowcount
    return {
        "gaps": len(gaps),
        "findings": len(findings),
        "findings_marked_fixed": fixed,
    }


def run(conn: psycopg.Connection, ciks: set[str] | None = None) -> dict:
    with conn.cursor() as cur:
        cur.execute("set local statement_timeout = '20min'")
        company_ids = None
        if ciks:
            cur.execute(
                "select id from core.company where cik = any(%s)", (sorted(ciks),)
            )
            company_ids = [r[0] for r in cur.fetchall()]
        _build_expected_filings(cur, company_ids)
        feed = _verify_against_sec_feed(cur)
        results = []
        for concept, (shape, base) in CHECK_CONCEPTS.items():
            result = _check_concept(cur, concept, shape, base)
            logger.info(
                "period_completeness.concept_done",
                concept=concept,
                gaps=len(result["gaps"]),
            )
            results.append(result)
        stats = _write(cur, results, company_ids)
        stats["sec_feed_check"] = feed
    conn.commit()
    logger.info("period_completeness.done", **stats)
    return stats


app = typer.Typer(add_completion=False)


@app.command()
def main(
    ciks: str = typer.Option(None, help="Comma-separated CIKs (default: all active)."),
) -> None:
    target = {c.strip().zfill(10) for c in ciks.split(",")} if ciks else None
    with psycopg.connect(settings.database_url) as conn:
        stats = run(conn, target)
    typer.echo(json.dumps(stats, indent=2))


if __name__ == "__main__":
    app()
