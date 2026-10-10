"""Sanity-triggered investigation and per-company fix (2026-09-08, explicit
user request): when the Data Sanity Layer (yfinance_check.py) flags a
critical/major finding, trace the "fetcher tree" for that ONE company --
every raw core.fact row under every tag currently mapped to the relevant
canonical concept, INCLUDING rows resolve.py marked is_authoritative=false
-- and check whether any of them actually reconciles against the
independent (yfinance) figure that triggered the finding.

Deliberately does NOT touch analytics.concept_mapping. resolve.py includes
every confidence tier except 'rejected' (checked directly), so a new
concept_mapping row -- even 'provisional' -- would change resolve()'s
output for EVERY company reporting that tag, not just the one this
investigation verified. A single company's tag reconciling against
yfinance is real evidence for THAT company; it is not evidence a global
tag-priority change is safe, the exact lesson doc 40's tag-coverage-library
work already learned the hard way. See migration 0049's own comment for
the full reasoning.

**Updated 2026-09-08, same day, explicit user direction: "for every data
fill or fix, use only SEC EDGAR, yfinance for sanity and matching only --
we have to store the sec tag wrt metric, company and fetch from sec
only."** The fix is now a per-(company, concept) TAG PREFERENCE
(analytics.company_tag_preference, migration 0051), not a per-(company,
concept, period) value snapshot (migration 0049's
canonical_fact_sanity_override, still present but no longer written to).
Once a specific SEC tag is confirmed to reconcile for a company, that
preference applies to EVERY period the company has data under that tag --
not just the one period the sanity check happened to flag -- since the
underlying reason resolve()'s normal tag priority is untrustworthy for
this company (a real, live example: Flowserve's own trivial cross-filing
rounding disagreements recur across 7 different fiscal years, not just
one). yfinance's role stops at "this is the tag that reconciles" -- the
VALUE that actually gets stored always comes from core.fact (a real SEC
filing), never from yfinance itself. resolve_company_tag_preferences()
below merges a company's preferred-tag facts into a THIRD, resolve()-
untouched concept (e.g. revenue_sanity_resolved) -- the same "new resolved
concept, zero concept_mapping rows" idiom already established by
total_debt_resolved (migration 0033) and gross_profit_resolved (migration
0047), just sourced from a per-company tag preference instead of a global
tag or an arithmetic derivation.

Currently wired for ONE concept: revenue (the resolve()-authoritative-$0
bug found 2026-09-07 is the only currently-understood failure mode with a
real, demonstrated fix path -- an alternate mapped tag's own non-
authoritative rows reconciling against an independent source).
shares_outstanding mismatches (Alphabet/Nike, see
doc/learnings/2026-09-08-data-sanity-layer.md) are investigated too, but
are expected to usually resolve to 'no_match_found' -- the standard
Company Facts API strips dimensional/per-share-class XBRL data entirely
(doc 22's finding), so the tag that would actually reconcile often isn't
in core.fact at all. That's an honest, correctly-reported outcome, not a
bug in the investigator."""

from decimal import Decimal

import psycopg
import structlog

logger = structlog.get_logger()

# concept_name -> resolved_concept_name for concepts wired up with a
# fix-application path. A concept absent from this dict still gets
# investigated and recorded in data_sanity_investigation -- it just never
# reaches outcome='auto_fixed', since there's nowhere safe to write the
# fix without a matching *_sanity_resolved concept already seeded.
FIXABLE_CONCEPTS: dict[str, str] = {
    "revenue": "revenue_sanity_resolved",
    # Added 2026-09-08 -- yfinance_financials/compare.py's own
    # investigate_major_findings() was ALREADY calling investigate() for
    # major findings on these 4 concepts (it hands off whatever
    # canonical_concept a finding is against, unconditionally), but
    # every one landed at best in needs_review since none of them were
    # fixable -- a real, silent gap between "we already investigate
    # this" and "we can actually act on what we find". Each of these
    # already has a *_resolved concept from mapper/concept_fallback.py
    # (arithmetic-derivation fallback) as its merge target -- safe to
    # share because resolve_company_tag_preferences() (above) now only
    # ever touches preferred companies' own rows in that target, never
    # the arithmetic-fallback baseline the other writer owns.
    "cost_of_revenue": "cost_of_revenue_resolved",
    "gross_profit": "gross_profit_resolved",
    "operating_expenses": "operating_expenses_resolved",
    "total_debt": "total_debt_resolved",
    # Added 2026-10-02, triaging the 585-row needs_review backlog that had
    # built up in analytics.data_sanity_investigation: every one of these
    # 6 already has a *_resolved concept from mapper/concept_fallback.py,
    # so the only thing missing was this dict entry -- a pure wiring gap,
    # not a new tag-discovery problem. Every candidate tag involved is
    # already approved/provisional in concept_mapping (find_candidate_tags
    # only searches already-mapped tags); this just lets the existing
    # per-company tag-preference mechanism act on what it already finds,
    # instead of recording a lead nobody can apply. capex's own 0%
    # same-period coexistence rate (checked live) is expected, not
    # alarming -- PaymentsToAcquireProductiveAssets (priority 2) is a
    # genuinely BROADER figure than PaymentsToAcquirePropertyPlantAndEquipment
    # (priority 1, approved) for every company checked, and the broader one
    # is the one matching yfinance's own capex figure -- exactly the
    # per-company override this mechanism exists for, not a global
    # priority swap (which would need a full population-wide verification
    # pass this triage didn't do).
    "depreciation_and_amortization": "depreciation_and_amortization_resolved",
    "cash_and_equivalents": "cash_and_equivalents_resolved",
    "operating_income": "operating_income_resolved",
    "stockholders_equity": "stockholders_equity_resolved",
    "share_buybacks": "share_buybacks_resolved",
    "capex": "capex_resolved",
    # Deliberately NOT wired, both triaged 2026-10-02:
    #  - shares_outstanding: known multi-class-share structural divergence
    #    (Alphabet/Nike), not a resolvable tag mixup -- see this file's own
    #    module docstring.
    #  - net_income: us-gaap:ProfitLoss (a real candidate in the backlog)
    #    typically includes noncontrolling-interest income while
    #    us-gaap:NetIncomeLoss typically excludes it -- conceptually
    #    different, not interchangeable. Coexistence-test agreement was
    #    only 61.3% even restricted to the backlog's own companies. Needs
    #    an NCI-aware guard (e.g. skip when the company has a material
    #    MinorityInterest balance) before this concept can be wired safely;
    #    left as a follow-up, not force-added here.
}

# Concepts whose *_resolved baseline is owned by another writer that must
# NOT be back-filled from the raw primary concept. total_debt_resolved is
# built from core.fact by mapper/concept_fallback.resolve_total_debt_
# components() (2026-09-27), which deliberately leaves a period blank when
# the tags can't give a total; copying the raw sum-mode `total_debt` into
# those blanks would put back the exact wrong values it replaced (Chevron
# $0.4B). Preferred companies' own rows are still written here.
NO_BASELINE_COPY = frozenset({"total_debt"})

# How close a candidate tag's own value must land to the external
# (yfinance) figure before being trusted as the fix, not just a lead.
# Wider than the sanity check's own market_cap/trailing_pe thresholds --
# revenue's real reporting period doesn't line up exactly with yfinance's
# trailing-twelve-month window, so some genuine drift is expected even for
# a correct match.
AUTO_FIX_TOLERANCE_PCT = Decimal(20)


def _concept_id(conn: psycopg.Connection, name: str) -> int:
    with conn.cursor() as cur:
        cur.execute(
            "select id from analytics.canonical_concept where name = %s", (name,)
        )
        row = cur.fetchone()
        if row is None:
            raise ValueError(f"canonical_concept {name!r} does not exist")
        return row[0]


def _latest_period_id(
    conn: psycopg.Connection, company_id: int, concept_name: str
) -> int | None:
    with conn.cursor() as cur:
        cur.execute(
            """
            select cf.period_id
            from analytics.canonical_fact cf
            join analytics.canonical_concept cc on cc.id = cf.canonical_concept_id
            join core.period p on p.id = cf.period_id
            where cf.company_id = %s and cc.name = %s
            order by p.end_date desc
            limit 1
            """,
            (company_id, concept_name),
        )
        row = cur.fetchone()
        return row[0] if row else None


def find_candidate_tags(
    conn: psycopg.Connection, company_id: int, concept_name: str, period_id: int
) -> list[dict]:
    """Every raw core.fact row this company has, at this exact period, for
    any tag currently mapped to concept_name -- including
    is_authoritative=false rows, which is the whole point: the bug this
    exists to catch is specifically resolve() correctly-by-design refusing
    to pick between several near-consensus values, then first_match
    falling through to a worse tag's own authoritative-but-wrong one."""
    with conn.cursor() as cur:
        cur.execute(
            """
            select co.taxonomy, co.tag, f.value, f.is_authoritative, f.id
            from core.fact f
            join core.concept co on co.id = f.concept_id
            join analytics.concept_mapping cm on cm.concept_id = f.concept_id
            join analytics.canonical_concept cc on cc.id = cm.canonical_concept_id
            where f.company_id = %s and cc.name = %s and f.period_id = %s
            order by co.taxonomy, co.tag, f.is_authoritative desc
            """,
            (company_id, concept_name, period_id),
        )
        return [
            {
                "taxonomy": r[0],
                "tag": r[1],
                "value": r[2],
                "is_authoritative": r[3],
                "fact_id": r[4],
            }
            for r in cur.fetchall()
        ]


def _pct_diff(candidate: Decimal, external: Decimal) -> Decimal:
    denom = abs(external) if external != 0 else Decimal(1)
    return abs(candidate - external) / denom * Decimal(100)


def investigate(
    conn: psycopg.Connection,
    company_id: int,
    concept_name: str,
    external_value: Decimal,
    data_sanity_check_id: int | None = None,
    period_id: int | None = None,
) -> dict:
    """Investigates one (company, concept) sanity finding against
    `external_value` (the independent figure, e.g. yfinance's totalRevenue).
    `period_id`, when given, investigates that EXACT period instead of the
    concept's latest one -- lets a caller checking every quarter (not just
    "most recent", e.g. the yfinance full-statement comparison system)
    reuse this same fix pipeline for whichever period it flagged, rather
    than duplicating the tag-tracing/reconciliation logic. Always writes
    exactly one analytics.data_sanity_investigation row (upserted, so a
    rerun updates rather than duplicates) -- 'no candidate tags at all'
    and 'candidates exist but none reconcile' are both recorded outcomes,
    not silence. Returns the outcome dict."""
    if period_id is None:
        period_id = _latest_period_id(conn, company_id, concept_name)
    if period_id is None:
        outcome = {
            "outcome": "no_match_found",
            "note": "no canonical_fact period for this concept at all",
            "candidate": None,
        }
        _write_investigation(
            conn,
            data_sanity_check_id,
            company_id,
            concept_name,
            None,
            external_value,
            outcome,
        )
        return outcome

    candidates = find_candidate_tags(conn, company_id, concept_name, period_id)
    if not candidates:
        outcome = {
            "outcome": "no_match_found",
            "note": "no raw core.fact rows under any currently-mapped tag for this period",
            "candidate": None,
        }
        _write_investigation(
            conn,
            data_sanity_check_id,
            company_id,
            concept_name,
            period_id,
            external_value,
            outcome,
        )
        return outcome

    outcome = _score_and_decide(candidates, external_value, concept_name)
    if outcome["outcome"] == "auto_fixed":
        _write_tag_preference(
            conn,
            company_id,
            concept_name,
            outcome["candidate"],
            external_value,
            outcome["pct_diff"],
        )

    _write_investigation(
        conn,
        data_sanity_check_id,
        company_id,
        concept_name,
        period_id,
        external_value,
        outcome,
    )
    return outcome


def _score_and_decide(
    candidates: list[dict], external_value: Decimal, concept_name: str
) -> dict:
    """Pure decision logic, no DB access -- scores every candidate tag's
    value against the external figure, picks the closest, and decides
    whether it's close enough to trust (and, if so, whether this concept
    even has a *_sanity_resolved concept wired up to apply the fix into).
    Split out from investigate() specifically so this decision can be
    unit-tested without a database."""
    scored = [
        (c, _pct_diff(Decimal(str(c["value"])), external_value)) for c in candidates
    ]
    scored.sort(key=lambda pair: pair[1])
    best_candidate, best_pct_diff = scored[0]

    if best_pct_diff <= AUTO_FIX_TOLERANCE_PCT:
        resolved_concept_name = FIXABLE_CONCEPTS.get(concept_name)
        if resolved_concept_name is not None:
            return {
                "outcome": "auto_fixed",
                "candidate": best_candidate,
                "pct_diff": best_pct_diff,
                "note": f"{best_candidate['taxonomy']}:{best_candidate['tag']} reconciles within {best_pct_diff:.1f}% -- applied as override",
            }
        return {
            "outcome": "needs_review",
            "candidate": best_candidate,
            "pct_diff": best_pct_diff,
            "note": f"{best_candidate['taxonomy']}:{best_candidate['tag']} reconciles within {best_pct_diff:.1f}%, "
            f"but {concept_name!r} has no *_sanity_resolved concept wired up yet -- recorded as a lead, not applied",
        }
    return {
        "outcome": "no_match_found",
        "candidate": best_candidate,
        "pct_diff": best_pct_diff,
        "note": f"closest candidate ({best_candidate['taxonomy']}:{best_candidate['tag']}) still off by {best_pct_diff:.1f}%, "
        f"over the {AUTO_FIX_TOLERANCE_PCT}% tolerance -- likely a real structural difference (e.g. multi-share-class, "
        f"TTM-vs-period timing), not a resolvable tag mixup",
    }


def _write_investigation(
    conn: psycopg.Connection,
    data_sanity_check_id: int | None,
    company_id: int,
    concept_name: str,
    period_id: int | None,
    external_value: Decimal,
    outcome: dict,
) -> None:
    candidate = outcome.get("candidate")
    with conn.cursor() as cur:
        cur.execute(
            """
            insert into analytics.data_sanity_investigation
                (data_sanity_check_id, company_id, concept_name, period_id, candidate_taxonomy, candidate_tag,
                 candidate_value, external_value, pct_diff_vs_external, outcome, note)
            values (%(check_id)s, %(company_id)s, %(concept_name)s, %(period_id)s, %(taxonomy)s, %(tag)s,
                    %(value)s, %(external_value)s, %(pct_diff)s, %(outcome)s, %(note)s)
            on conflict (company_id, concept_name, period_id) do update
                set data_sanity_check_id = excluded.data_sanity_check_id, candidate_taxonomy = excluded.candidate_taxonomy,
                    candidate_tag = excluded.candidate_tag, candidate_value = excluded.candidate_value,
                    external_value = excluded.external_value, pct_diff_vs_external = excluded.pct_diff_vs_external,
                    outcome = excluded.outcome, note = excluded.note, investigated_at = now()
            """,
            {
                "check_id": data_sanity_check_id,
                "company_id": company_id,
                "concept_name": concept_name,
                "period_id": period_id,
                "taxonomy": candidate["taxonomy"] if candidate else None,
                "tag": candidate["tag"] if candidate else None,
                "value": candidate["value"] if candidate else None,
                "external_value": external_value,
                "pct_diff": outcome.get("pct_diff"),
                "outcome": outcome["outcome"],
                "note": outcome["note"],
            },
        )
    conn.commit()


def _write_tag_preference(
    conn: psycopg.Connection,
    company_id: int,
    concept_name: str,
    candidate: dict,
    external_value: Decimal,
    pct_diff: Decimal,
) -> None:
    concept_id = _concept_id(conn, concept_name)
    evidence = (
        f"Sanity investigation 2026-09-08: raw tag {candidate['taxonomy']}:{candidate['tag']} "
        f"(is_authoritative={candidate['is_authoritative']}) = {candidate['value']}, "
        f"yfinance (detection/matching only, never the stored value) = {external_value}, {pct_diff:.1f}% apart."
    )
    with conn.cursor() as cur:
        cur.execute(
            """
            insert into analytics.company_tag_preference
                (company_id, canonical_concept_id, taxonomy, tag, confidence, evidence)
            values (%(company_id)s, %(concept_id)s, %(taxonomy)s, %(tag)s, 'provisional', %(evidence)s)
            on conflict (company_id, canonical_concept_id) do update
                set taxonomy = excluded.taxonomy, tag = excluded.tag,
                    evidence = excluded.evidence, discovered_at = now()
            """,
            {
                "company_id": company_id,
                "concept_id": concept_id,
                "taxonomy": candidate["taxonomy"],
                "tag": candidate["tag"],
                "evidence": evidence,
            },
        )
    conn.commit()


def _reconcile_by_mode(
    rows: list[tuple[int, object, int]],
) -> dict[int, tuple[object, int]]:
    """rows: (period_id, value, fact_id) tuples, possibly several per
    period (the exact "3 filings, trivially disagreeing" shape this whole
    system exists to handle -- see Flowserve/doc/learnings/2026-09-07).
    Picks the most-common value per period (a real, if small, majority
    vote across independent filings of the same fact), tie-broken by the
    highest fact_id (the most recently-inserted row) -- deterministic,
    no guessing between two equally-supported values."""
    from collections import Counter, defaultdict

    by_period: dict[int, list[tuple[object, int]]] = defaultdict(list)
    for period_id, value, fact_id in rows:
        by_period[period_id].append((value, fact_id))

    result: dict[int, tuple[object, int]] = {}
    for period_id, pairs in by_period.items():
        counts = Counter(value for value, _fact_id in pairs)
        max_count = max(counts.values())
        most_common_values = [
            value for value, count in counts.items() if count == max_count
        ]
        # Deterministic tie-break: among equally-supported values, prefer
        # the one attached to the highest fact_id.
        best_value = max(
            most_common_values,
            key=lambda v: max(fact_id for value, fact_id in pairs if value == v),
        )
        best_fact_id = max(fact_id for value, fact_id in pairs if value == best_value)
        result[period_id] = (best_value, best_fact_id)
    return result


def _load_all_facts_for_tag(
    conn: psycopg.Connection, company_id: int, taxonomy: str, tag: str
) -> list[tuple[int, object, int]]:
    with conn.cursor() as cur:
        cur.execute(
            """
            select f.period_id, f.value, f.id
            from core.fact f
            join core.concept co on co.id = f.concept_id
            where f.company_id = %s and co.taxonomy = %s and co.tag = %s
            """,
            (company_id, taxonomy, tag),
        )
        return cur.fetchall()


# Stale display rows, dropped so the baseline copy below refills them. The
# baseline copy is ON CONFLICT DO NOTHING, so without this a corrected
# primary value never reaches the display concept. Two narrow shapes:
#  1. A single-source row whose cited core.fact now holds a different value.
#     derive-q4 rewrites a mistagged "Q4 = full year" fact in place (NiSource
#     Q4 2025 revenue: $6.52B -> $1.89B), which left the display at $6.52B.
#  2. A row whose every source fact is a filed Q4 fact that derive-q4 demoted
#     for carrying the full-year value (normalizer/derived.py
#     _mistagged_full_year_q4), when it was a separate row from the derived one.
# Rows backed by any other kind of fact are left alone: the display value is
# sometimes the right one (American Tower Q3 2020: $2.0B display vs $131.6M
# in the primary concept). Measured 2026-09-27: shape 1 matched 2 revenue and
# 5 gross-profit rows population-wide.
_DROP_STALE_DISPLAY_ROWS_SQL = """
delete from analytics.canonical_fact cf
where cf.canonical_concept_id = %(resolved_id)s
  and cardinality(cf.source_fact_ids) > 0
  and (
      (
          cardinality(cf.source_fact_ids) = 1
          and exists (
              select 1 from core.fact f
              where f.id = cf.source_fact_ids[1] and f.value <> cf.value
          )
      )
      or (
          exists (
              select 1 from core.period cp
              where cp.id = cf.period_id and cp.fiscal_period = 'Q4'
          )
          and not exists (
              select 1
              from unnest(cf.source_fact_ids) sid
              join core.fact q on q.id = sid
              join core.period qp on qp.id = q.period_id
              where q.is_authoritative
                 or q.is_derived
                 or qp.fiscal_period <> 'Q4'
                 or not exists (
                     select 1
                     from core.fact fy
                     join core.period fp on fp.id = fy.period_id
                     where fy.company_id = q.company_id
                       and fy.concept_id = q.concept_id
                       and fy.unit_id = q.unit_id
                       and fy.is_authoritative
                       and fp.fiscal_period = 'FY'
                       and fp.end_date = qp.end_date
                       and fy.value = q.value
                 )
          )
      )
  )
"""


_FILL_UNCOVERED_FROM_PRIMARY_SQL = """
insert into analytics.canonical_fact (company_id, canonical_concept_id, period_id, value, source_fact_ids)
select f.company_id, %(resolved_id)s, f.period_id, f.value, f.source_fact_ids
from analytics.canonical_fact f
join core.period p on p.id = f.period_id
where f.canonical_concept_id = %(primary_id)s
  and f.company_id = %(company_id)s
  and (
      p.end_date > (select max(end_date) from core.period where id = any(%(pref_period_ids)s))
      or f.value <> 0
  )
on conflict (company_id, canonical_concept_id, period_id) do nothing
"""


def resolve_company_tag_preferences(
    conn: psycopg.Connection, concept_name: str, resolved_concept_name: str
) -> int:
    """The resolved concept is the primary concept's own value for every
    company WITHOUT a preference (set-based, bulk -- the common case,
    ~5,200 of ~5,216 companies), EXCEPT for the small number of companies
    WITH a company_tag_preference row, where their preferred tag's own
    (mode-reconciled) values win for EVERY period it covers -- not just
    one flagged period -- since the preference exists specifically
    because the primary concept's resolution is untrustworthy for that
    company. The per-company loop below is intentionally NOT a batch-job
    N+1 concern (see pipeline/CLAUDE.md's restatements.py lesson) --
    preference rows are rare, investigation-driven, and this is exactly
    the shape doc 40 already established (`resolve_fallback_for_company`)
    for a genuinely small per-company set. Safe to rerun; idempotent.

    Scoping fixed 2026-09-08, widening FIXABLE_CONCEPTS past `revenue`:
    the baseline used to be a blanket DELETE of the whole resolved
    concept, then a bulk re-INSERT sourced ONLY from the primary
    concept's own canonical_fact -- fine when this was the resolved
    concept's only writer (revenue_sanity_resolved), but for a concept
    ALSO populated by mapper/concept_fallback.py's arithmetic fallback
    (operating_expenses_resolved etc.), that blanket delete would have
    silently wiped every arithmetic-derived row (companies with no
    primary tag at all) on every run -- the same shared-table
    "must scope on every dimension another writer keys on" trap this
    project has hit and documented multiple times already. Fixed by
    never touching a non-preferred company's existing row at all: the
    baseline INSERT now only fills rows that don't already exist
    (whatever wrote them first -- resolve() or concept_fallback.py --
    stays authoritative), and the DELETE is scoped to preferred
    companies only, never the whole concept."""
    primary_id = _concept_id(conn, concept_name)
    resolved_id = _concept_id(conn, resolved_concept_name)

    with conn.cursor() as cur:
        cur.execute(
            "select company_id, taxonomy, tag from analytics.company_tag_preference where canonical_concept_id = %s",
            (primary_id,),
        )
        preferences = cur.fetchall()
    preferred_company_ids = [company_id for company_id, _t, _g in preferences]

    with conn.cursor() as cur:
        if concept_name not in NO_BASELINE_COPY:
            cur.execute(_DROP_STALE_DISPLAY_ROWS_SQL, {"resolved_id": resolved_id})
            if cur.rowcount:
                logger.info(
                    "sanity.tag_investigator.dropped_stale_display_rows",
                    concept=resolved_concept_name,
                    rows=cur.rowcount,
                )
        cur.execute(
            "delete from analytics.canonical_fact where canonical_concept_id = %(resolved_id)s and company_id = any(%(preferred_ids)s)",
            {
                "resolved_id": resolved_id,
                "preferred_ids": preferred_company_ids or [-1],
            },
        )
        if concept_name not in NO_BASELINE_COPY:
            cur.execute(
                """
            insert into analytics.canonical_fact (company_id, canonical_concept_id, period_id, value, source_fact_ids)
            select company_id, %(resolved_id)s, period_id, value, source_fact_ids
            from analytics.canonical_fact
            where canonical_concept_id = %(primary_id)s
              and company_id != all(%(preferred_ids)s)
            on conflict (company_id, canonical_concept_id, period_id) do nothing
            """,
                {
                    "resolved_id": resolved_id,
                    "primary_id": primary_id,
                    "preferred_ids": preferred_company_ids or [-1],
                },
            )

        for company_id, taxonomy, tag in preferences:
            facts = _load_all_facts_for_tag(conn, company_id, taxonomy, tag)
            reconciled = _reconcile_by_mode(facts)
            if reconciled:
                cur.executemany(
                    """
                    insert into analytics.canonical_fact (company_id, canonical_concept_id, period_id, value, source_fact_ids)
                    values (%(company_id)s, %(resolved_id)s, %(period_id)s, %(value)s, %(source_fact_ids)s)
                    """,
                    [
                        {
                            "company_id": company_id,
                            "resolved_id": resolved_id,
                            "period_id": period_id,
                            "value": value,
                            "source_fact_ids": [fact_id],
                        }
                        for period_id, (value, fact_id) in reconciled.items()
                    ],
                )
                if concept_name not in NO_BASELINE_COPY:
                    # A company can stop filing its preferred tag. Mohawk's
                    # SalesRevenueGoodsNet ends in 2018, so its revenue
                    # stopped at 2017 on the stock page while the primary
                    # concept had correct values through 2026 (found
                    # 2026-09-27). Periods AFTER the preferred tag's last
                    # one can't be what the preference was created to fix,
                    # so the primary concept fills them.
                    # Widened 2026-10-03: a period the preferred tag simply
                    # doesn't cover (before its first filing or between
                    # filings: Flowserve FY2007-2010 had $3.8-4.5B primary
                    # revenue and a blank display) is also not one the
                    # preference corrected. Those get the primary's value
                    # too, but never a $0, since a spurious $0 is exactly
                    # what most preferences exist to replace.
                    cur.execute(
                        _FILL_UNCOVERED_FROM_PRIMARY_SQL,
                        {
                            "resolved_id": resolved_id,
                            "primary_id": primary_id,
                            "company_id": company_id,
                            "pref_period_ids": list(reconciled),
                        },
                    )

        cur.execute(
            "select count(*) from analytics.canonical_fact where canonical_concept_id = %s",
            (resolved_id,),
        )
        count = cur.fetchone()[0]
    conn.commit()
    return count


def investigate_open_findings(
    conn: psycopg.Connection,
    severities: tuple[str, ...] = ("critical", "major"),
    company_id: int | None = None,
) -> dict:
    """Entry point for `scrooner-sanity investigate`: pulls every current
    critical/major analytics.data_sanity_check row, investigates each,
    then re-merges every concept in FIXABLE_CONCEPTS so any newly-applied
    override takes effect immediately.

    `company_id` optionally scopes to one company -- added 2026-09-08
    for incidents/verifier.py, which needs to verify a single company's
    fix without reprocessing every other company's open findings (the
    daily cron's own `sanity investigate` call still omits it, covering
    the whole population as before)."""
    stats = {"considered": 0, "auto_fixed": 0, "needs_review": 0, "no_match_found": 0}
    with conn.cursor() as cur:
        if company_id is None:
            cur.execute(
                "select id, company_id, metric_name, external_value from analytics.data_sanity_check where severity = any(%s)",
                (list(severities),),
            )
        else:
            cur.execute(
                "select id, company_id, metric_name, external_value from analytics.data_sanity_check where severity = any(%s) and company_id = %s",
                (list(severities), company_id),
            )
        rows = cur.fetchall()

    # revenue_zero_check's own "concept" for investigation purposes is
    # 'revenue' (the metric_name and the canonical_concept diverge by
    # design -- the check is named for what it tests, not 1:1 with a
    # concept). market_cap/trailing_pe/shares_outstanding map more
    # directly, but shares_outstanding is the only OTHER one with a real
    # underlying concept to trace -- market_cap/trailing_pe are computed
    # metrics, not raw tags, so there is no "fetcher tree" to trace for them.
    CONCEPT_FOR_METRIC = {
        "revenue_zero_check": "revenue",
        "shares_outstanding": "shares_outstanding",
    }

    for check_id, company_id, metric_name, external_value in rows:
        concept_name = CONCEPT_FOR_METRIC.get(metric_name)
        if concept_name is None or external_value is None:
            continue
        stats["considered"] += 1
        outcome = investigate(
            conn,
            company_id,
            concept_name,
            Decimal(external_value),
            data_sanity_check_id=check_id,
        )
        stats[outcome["outcome"]] += 1

    for concept_name, resolved_name in FIXABLE_CONCEPTS.items():
        written = resolve_company_tag_preferences(conn, concept_name, resolved_name)
        logger.info(
            "sanity.tag_investigator.merged", concept=resolved_name, rows=written
        )

    logger.info("sanity.tag_investigator.done", **stats)
    return stats


# Root cause 1 bulk sweep (2026-10-02): the resolve()-authoritative-$0 bug
# (pipeline/CLAUDE.md's 2026-09-07/08 entries -- Flowserve, ~20 other named
# companies, sized at 883 companies/11,992 zero-revenue periods but
# deliberately left unfixed pending "its own careful pass" rather than a
# same-session bolt-on). This is that pass. `investigate_open_findings()`
# above only ever reaches a company once it happens to surface as a
# critical/major sanity finding (pick_rotation_batch()'s slow coldest-
# checked-first rotation) AND investigate()'s own AUTO_FIX_TOLERANCE_PCT
# (20% vs. yfinance) gates the fix -- wrong bar for this bug class: a bank
# like Commerce Bancshares' best honest alternate tag (interest income
# alone) is STILL ~78% off from yfinance's full revenue figure (missing
# non-interest income), yet $0 is still categorically, obviously wrong.
# This sweep instead uses INTERNAL corroboration (does switching to an
# alternate ALREADY-MAPPED tag -- any confidence, any is_authoritative --
# fix most of this company's OWN currently-zero periods), never yfinance,
# and reaches every qualifying company in one bulk pass rather than
# waiting for the daily rotation to eventually land on each one.
def find_internal_tag_preference_candidates(
    zero_period_ids: set[int],
    by_tag: dict[tuple[str, str], dict[int, object]],
    min_ratio: Decimal = Decimal("0.5"),
    min_fixes: int = 2,
    min_coverage_floor: int = 5,
) -> dict | None:
    """Pure decision logic, no DB access -- unit-testable the same way
    _score_and_decide() is. For ONE company: picks whichever alternate
    (taxonomy, tag) pair under the concept's own concept_mapping fixes the
    most of this company's currently-zero periods (ties broken by total
    period coverage, i.e. prefer the alternate with the deeper history).
    Requires BOTH a majority fix ratio (>= min_ratio, default half) AND
    either a real absolute fix count (>= min_fixes) or a deep enough
    overall tag history (>= min_coverage_floor) -- guards against a
    single-period fluke (a pre-revenue biotech's one-off stray nonzero
    value under an otherwise-unused tag) looking identical to a real,
    systematic tag-priority bug on a thin sample. Verified against the
    real population 2026-10-02: this bar selects 31 real, named companies
    (Commerce Bancshares, Flowserve, Eaton, Dentsply Sirona, PriceSmart,
    Tetra Technologies, OGE Energy, Qorvo, Baker Hughes, Oscar Health
    among them) and correctly excludes companies where the best alternate
    tag only fixes 1-3 of 10-46 zero periods (genuine pre-revenue biotechs
    with a rare stray nonzero fact, not a systematic bug)."""
    best: tuple[int, int, str, str] | None = None
    for (taxonomy, tag), period_map in by_tag.items():
        fixes = sum(
            1 for pid in zero_period_ids if period_map.get(pid) not in (None, 0)
        )
        if fixes == 0:
            continue
        coverage = len(period_map)
        candidate = (fixes, coverage, taxonomy, tag)
        if best is None or candidate[:2] > best[:2]:
            best = candidate

    if best is None:
        return None
    fixes, coverage, taxonomy, tag = best
    ratio = Decimal(fixes) / Decimal(max(1, len(zero_period_ids)))
    if ratio >= min_ratio and (fixes >= min_fixes or coverage >= min_coverage_floor):
        return {
            "taxonomy": taxonomy,
            "tag": tag,
            "fixes": fixes,
            "zero_periods": len(zero_period_ids),
            "coverage": coverage,
            "ratio": ratio,
        }
    return None


def _load_zero_periods_by_company(
    conn: psycopg.Connection, resolved_concept_id: int, real_operating_company_sql: str
) -> dict[int, set[int]]:
    with conn.cursor() as cur:
        cur.execute(
            f"""
            select cf.company_id, array_agg(cf.period_id)
            from analytics.canonical_fact cf
            join analytics.canonical_concept cc on cc.id = cf.canonical_concept_id
            where cc.name = (select name from analytics.canonical_concept where id = %(resolved_id)s)
              and cf.value = 0
              and cf.company_id in ({real_operating_company_sql})
            group by cf.company_id
            """,
            {"resolved_id": resolved_concept_id},
        )
        return {r[0]: set(r[1]) for r in cur.fetchall()}


def _load_tags_for_company(
    conn: psycopg.Connection, company_id: int, concept_name: str
) -> dict[tuple[str, str], dict[int, object]]:
    with conn.cursor() as cur:
        cur.execute(
            """
            select co.taxonomy, co.tag, f.period_id, f.value
            from core.fact f
            join core.concept co on co.id = f.concept_id
            join analytics.concept_mapping cm on cm.concept_id = f.concept_id
            join analytics.canonical_concept cc on cc.id = cm.canonical_concept_id
            where f.company_id = %s and cc.name = %s
            """,
            (company_id, concept_name),
        )
        by_tag: dict[tuple[str, str], dict[int, object]] = {}
        for taxonomy, tag, period_id, value in cur.fetchall():
            by_tag.setdefault((taxonomy, tag), {})[period_id] = value
        return by_tag


def run_internal_tag_preference_sweep(
    conn: psycopg.Connection,
    concept_name: str = "revenue",
    resolved_concept_name: str = "revenue_sanity_resolved",
) -> dict:
    """The actual bulk entry point: scans every company in the
    real_operating_company population (mapper/coverage_matrix.py's own
    corrected-denominator population -- never raw status='active', which
    includes ~400 SPACs/trusts with no real revenue by construction) with
    at least one zero `resolved_concept_name` period, applies
    find_internal_tag_preference_candidates()'s bar, and writes a
    company_tag_preference row (confidence='provisional', same tier every
    other tag_investigator fix uses) for every company that clears it.
    Does NOT itself call resolve_company_tag_preferences() -- the caller
    (the CLI command) runs that once, after this, so the merge sees the
    final preference set in one pass rather than N incremental ones."""
    # Local import to avoid a module-level circular import (coverage_matrix
    # doesn't import tag_investigator, but keeping the dependency direction
    # explicit and narrow here is cheap).
    from scrooner_pipeline.mapper.coverage_matrix import POPULATION_QUERIES

    concept_id = _concept_id(conn, concept_name)
    resolved_id = _concept_id(conn, resolved_concept_name)

    zero_by_company = _load_zero_periods_by_company(
        conn, resolved_id, POPULATION_QUERIES["real_operating_company"]
    )

    stats = {"considered": len(zero_by_company), "applied": 0, "no_candidate": 0}
    applied: list[dict] = []
    for company_id, zero_period_ids in zero_by_company.items():
        by_tag = _load_tags_for_company(conn, company_id, concept_name)
        decision = find_internal_tag_preference_candidates(zero_period_ids, by_tag)
        if decision is None:
            stats["no_candidate"] += 1
            continue

        evidence = (
            f"Internal-corroboration sweep 2026-10-02 (root cause 1, revenue_zero_check): "
            f"{decision['taxonomy']}:{decision['tag']} fixes {decision['fixes']}/{decision['zero_periods']} "
            f"of this company's own zero {concept_name} periods (ratio {decision['ratio']:.2f}, "
            f"{decision['coverage']} total periods under this tag) -- no yfinance anchor used, "
            f"same-company internal evidence only. resolve()'s own priority tag is a real, repeated "
            f"authoritative $0 for this company (not a conflict-driven fallthrough), and this alternate, "
            f"already-mapped tag consistently carries the real value instead."
        )
        with conn.cursor() as cur:
            cur.execute(
                """
                insert into analytics.company_tag_preference
                    (company_id, canonical_concept_id, taxonomy, tag, confidence, evidence)
                values (%(company_id)s, %(concept_id)s, %(taxonomy)s, %(tag)s, 'provisional', %(evidence)s)
                on conflict (company_id, canonical_concept_id) do update
                    set taxonomy = excluded.taxonomy, tag = excluded.tag,
                        evidence = excluded.evidence, discovered_at = now()
                """,
                {
                    "company_id": company_id,
                    "concept_id": concept_id,
                    "taxonomy": decision["taxonomy"],
                    "tag": decision["tag"],
                    "evidence": evidence,
                },
            )
        conn.commit()
        stats["applied"] += 1
        applied.append({"company_id": company_id, **decision})

    logger.info("sanity.tag_investigator.internal_sweep_done", **stats)
    return {**stats, "applied_companies": applied}
