"""Accounting identity checks (2026-09-29) -- migration 0082.

Every other data-quality score in this project measures COVERAGE (does a
value exist) or PLAUSIBILITY (is it in a sane range) or AGREEMENT WITH A
THIRD PARTY (yfinance). None measures whether a company's own numbers
agree with each other. Identities that must hold for any correct set of
financial statements are the cheapest, strongest correctness signal
available: zero external calls, they catch wrong-tag mappings,
wrong-period picks, unit-scale bugs and bad derived quarters, and they
apply to every company. XBRL US's Data Quality Committee rules and the
publishing gates of commercial fundamentals vendors are built on the
same idea.

Design:
- IDENTITIES is declarative: a target concept, signed terms, optional
  us-gaap adjustment tags read from core.fact, a tolerance and the
  concept the tolerance is relative to. Adding a check is one entry.
- evaluate() is a pure function (unit-tested without a database).
- Adjustments are OPTIONAL reconciliations, not required terms: a period
  passes if the base terms agree OR base terms plus every reported
  adjustment agree. Checked live (10% sample, 2026-09-29) before trusting
  this: 68% of balance-sheet "failures" were noncontrolling interest or
  mezzanine/temporary equity, which sit outside both total_liabilities
  and parent stockholders_equity; adding them moved the net-income
  identity from 89.1% to 95.2% (discontinued ops, NCI, equity-method).
  Without them the check reports legitimate accounting as data errors.
- Tautology guard: a target whose source_fact_ids overlap its terms'
  source_fact_ids was derived from those terms (e.g. an arithmetic-
  fallback gross_profit_resolved = revenue - cost_of_revenue). Checking it
  proves nothing, so it is skipped, not counted as a pass.
- Loads per chunk of companies with one set-based pivot query per
  identity (never a query per company), stores a per-company summary plus
  failing periods only. Passing periods are counted, not stored.
- `display` layer = the *_resolved concept the company page shows when
  one exists, else the base concept. `raw` layer = base concepts only
  (what calculate.py's metrics read). Running both measures whether the
  resolution layer made the data more or less self-consistent.

Observer only: never writes a fix into canonical_fact, same role as
every other module in sanity/.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from decimal import Decimal

import psycopg
import structlog

logger = structlog.get_logger()

KIND_EQUALS = "equals"          # target == sum(terms) within tolerance
KIND_AT_MOST = "at_most"        # target <= sum(terms) within tolerance
KIND_NONNEGATIVE = "nonnegative"  # target >= 0

LAYERS = ("display", "raw")
CHUNK_SIZE = 500


@dataclass(frozen=True)
class Identity:
    name: str
    kind: str
    target: str
    terms: tuple[tuple[str, int], ...] = ()
    adjustments: tuple[tuple[str, int], ...] = ()  # (us-gaap tag, sign)
    tolerance: Decimal = Decimal("0")
    basis: str | None = None  # concept the tolerance is relative to
    description: str = ""

    @property
    def concepts(self) -> tuple[str, ...]:
        names = [self.target] + [c for c, _ in self.terms]
        if self.basis and self.basis not in names:
            names.append(self.basis)
        return tuple(dict.fromkeys(names))


IDENTITIES: tuple[Identity, ...] = (
    Identity(
        name="balance_sheet",
        kind=KIND_EQUALS,
        target="total_assets",
        terms=(("total_liabilities", 1), ("stockholders_equity", 1)),
        adjustments=(
            ("MinorityInterest", 1),
            ("TemporaryEquityCarryingAmountAttributableToParent", 1),
            ("TemporaryEquityCarryingAmountIncludingPortionAttributableToNoncontrollingInterest", 1),
            ("RedeemableNoncontrollingInterestEquityCarryingAmount", 1),
        ),
        tolerance=Decimal("0.02"),
        basis="total_assets",
        description="Assets = Liabilities + Equity (+ NCI + temporary equity)",
    ),
    Identity(
        name="gross_profit",
        kind=KIND_EQUALS,
        target="gross_profit",
        terms=(("revenue", 1), ("cost_of_revenue", -1)),
        tolerance=Decimal("0.01"),
        basis="revenue",
        description="Gross Profit = Revenue - Cost of Revenue",
    ),
    Identity(
        name="net_income",
        kind=KIND_EQUALS,
        target="net_income",
        terms=(("income_before_tax", 1), ("income_tax_expense", -1)),
        adjustments=(
            ("IncomeLossFromDiscontinuedOperationsNetOfTax", 1),
            ("NetIncomeLossAttributableToNoncontrollingInterest", -1),
            ("IncomeLossFromEquityMethodInvestments", 1),
        ),
        tolerance=Decimal("0.05"),
        basis="income_before_tax",
        description="Net Income = Pretax Income - Tax (+ disc. ops - NCI + equity method)",
    ),
    Identity(
        name="current_assets_within_total",
        kind=KIND_AT_MOST,
        target="current_assets",
        terms=(("total_assets", 1),),
        tolerance=Decimal("0.001"),
        basis="total_assets",
        description="Current Assets <= Total Assets",
    ),
    Identity(
        name="cash_within_total",
        kind=KIND_AT_MOST,
        target="cash_and_equivalents",
        terms=(("total_assets", 1),),
        tolerance=Decimal("0.001"),
        basis="total_assets",
        description="Cash <= Total Assets",
    ),
    Identity(
        name="revenue_nonnegative",
        kind=KIND_NONNEGATIVE,
        target="revenue",
        description="Revenue >= 0 (catches bad derived quarters)",
    ),
)


@dataclass
class Result:
    passed: bool
    expected: Decimal | None
    actual: Decimal
    rel_gap: Decimal | None
    used_adjustments: bool = False
    extra: dict = field(default_factory=dict)


def _rel(gap: Decimal, basis: Decimal) -> Decimal:
    denom = abs(basis) if basis else Decimal("1")
    return abs(gap) / max(denom, Decimal("1"))


def evaluate(
    identity: Identity,
    values: dict[str, Decimal],
    adjustments: dict[str, Decimal] | None = None,
) -> Result:
    """Pure evaluation of one identity for one company-period. `values`
    must contain every concept in identity.concepts. `adjustments` maps
    adjustment tag -> reported value (absent means not reported)."""
    actual = values[identity.target]
    if identity.kind == KIND_NONNEGATIVE:
        return Result(passed=actual >= 0, expected=None, actual=actual, rel_gap=None)

    base = sum((values[c] * sign for c, sign in identity.terms), Decimal("0"))
    basis = values[identity.basis] if identity.basis else base
    adj_total = sum(
        (adjustments[tag] * sign for tag, sign in identity.adjustments if adjustments and tag in adjustments),
        Decimal("0"),
    )
    candidates = [(base, False)]
    if adj_total:
        candidates.append((base + adj_total, True))

    best: Result | None = None
    for expected, used_adj in candidates:
        if identity.kind == KIND_EQUALS:
            gap = _rel(actual - expected, basis)
            passed = gap <= identity.tolerance
        else:  # KIND_AT_MOST
            over = actual - expected
            gap = _rel(over, basis) if over > 0 else Decimal("0")
            passed = gap <= identity.tolerance
        result = Result(passed=passed, expected=expected, actual=actual, rel_gap=gap, used_adjustments=used_adj)
        if passed:
            return result
        if best is None or gap < best.rel_gap:
            best = result
    return best


def _layer_concept_name(name: str, layer: str, known: set[str]) -> str:
    if layer == "raw":
        return name
    resolved = "revenue_sanity_resolved" if name == "revenue" else f"{name}_resolved"
    return resolved if resolved in known else name


def _load_rows(
    conn: psycopg.Connection,
    identity: Identity,
    concept_ids: dict[str, int],
    adjustment_ids: dict[str, int],
    company_ids: list[int],
) -> list[tuple]:
    """One pivot query per (identity, chunk). Returns
    (company_id, period_id, period_end, v_0..v_n, s_target, s_terms,
    adj_0..adj_m) for company-periods where every concept is present."""
    names = identity.concepts
    ids = [concept_ids[n] for n in names]
    value_cols = ", ".join(
        f"max(value) filter (where canonical_concept_id = {cid}) as v{i}" for i, cid in enumerate(ids)
    )
    term_ids = [concept_ids[c] for c, _ in identity.terms]
    source_cols = (
        f", array_agg(src) filter (where canonical_concept_id = {ids[0]}) as s_target"
        f", array_agg(src) filter (where canonical_concept_id = any(array[{','.join(map(str, term_ids)) or '0'}]::bigint[])) as s_terms"
    )
    adj_cols = "".join(
        f", (select max(f.value) from core.fact f where f.company_id = p.company_id and f.period_id = p.period_id"
        f" and f.is_authoritative and f.concept_id = {adjustment_ids.get(tag, -1)}) as a{j}"
        for j, (tag, _sign) in enumerate(identity.adjustments)
    )
    present = " and ".join(f"v{i} is not null" for i in range(len(ids)))
    sql = f"""
        with v as (
            select cf.company_id, cf.period_id, cf.canonical_concept_id, cf.value, cf.source_fact_ids,
                   unnest(case when cardinality(cf.source_fact_ids) > 0 then cf.source_fact_ids else array[null::bigint] end) as src
            from analytics.canonical_fact cf
            where cf.company_id = any(%(company_ids)s) and cf.canonical_concept_id = any(%(ids)s)
        ),
        p as (
            select company_id, period_id, {value_cols} {source_cols}
            from v group by company_id, period_id
        )
        select p.*, pe.end_date {adj_cols}
        from p join core.period pe on pe.id = p.period_id
        where {present}
    """
    with conn.cursor() as cur:
        cur.execute(sql, {"company_ids": company_ids, "ids": ids})
        return cur.fetchall()


def check_chunk(
    conn: psycopg.Connection,
    identity: Identity,
    layer: str,
    concept_ids: dict[str, int],
    adjustment_ids: dict[str, int],
    company_ids: list[int],
) -> tuple[dict[int, list], list[dict], int]:
    """Returns (summary_by_company, failures, skipped_tautologies)."""
    known = set(concept_ids)
    layered = Identity(
        name=identity.name,
        kind=identity.kind,
        target=_layer_concept_name(identity.target, layer, known),
        terms=tuple((_layer_concept_name(c, layer, known), s) for c, s in identity.terms),
        adjustments=identity.adjustments,
        tolerance=identity.tolerance,
        basis=_layer_concept_name(identity.basis, layer, known) if identity.basis else None,
    )
    names = layered.concepts
    rows = _load_rows(conn, layered, concept_ids, adjustment_ids, company_ids)

    summary: dict[int, list] = {}  # company_id -> [checked, passed, worst_gap]
    failures: list[dict] = []
    skipped = 0
    n = len(names)
    for row in rows:
        company_id, period_id = row[0], row[1]
        values = dict(zip(names, row[2 : 2 + n]))
        s_target, s_terms = row[2 + n], row[3 + n]
        period_end = row[4 + n]
        adj_values = row[5 + n :]
        target_sources = {s for s in (s_target or ()) if s is not None}
        term_sources = {s for s in (s_terms or ()) if s is not None}
        if target_sources & term_sources:
            skipped += 1
            continue
        adjustments = {
            tag: val for (tag, _s), val in zip(layered.adjustments, adj_values) if val is not None
        }
        result = evaluate(layered, values, adjustments)
        entry = summary.setdefault(company_id, [0, 0, None])
        entry[0] += 1
        if result.passed:
            entry[1] += 1
            continue
        if result.rel_gap is not None and (entry[2] is None or result.rel_gap > entry[2]):
            entry[2] = result.rel_gap
        failures.append(
            {
                "company_id": company_id,
                "identity_name": identity.name,
                "layer": layer,
                "period_id": period_id,
                "period_end": period_end,
                "expected": result.expected,
                "actual": result.actual,
                "rel_gap": result.rel_gap,
                "operands": json.dumps(
                    {**{k: str(v) for k, v in values.items()}, **{k: str(v) for k, v in adjustments.items()}}
                ),
            }
        )
    return summary, failures, skipped


def _write_chunk(
    conn: psycopg.Connection,
    identity_name: str,
    layer: str,
    company_ids: list[int],
    summary: dict[int, list],
    failures: list[dict],
) -> None:
    """Delete-then-reinsert scoped to exactly (identity, layer, chunk
    companies) -- every dimension this writer owns, nothing wider."""
    scope = {"identity_name": identity_name, "layer": layer, "company_ids": company_ids}
    with conn.cursor() as cur:
        for table in ("identity_check_failure", "identity_check_summary"):
            cur.execute(
                f"delete from analytics.{table} where identity_name = %(identity_name)s"
                " and layer = %(layer)s and company_id = any(%(company_ids)s)",
                scope,
            )
        if summary:
            cur.executemany(
                """
                insert into analytics.identity_check_summary
                    (company_id, identity_name, layer, checked, passed, worst_rel_gap)
                values (%s, %s, %s, %s, %s, %s)
                """,
                [(cid, identity_name, layer, c, p, g) for cid, (c, p, g) in summary.items()],
            )
        for start in range(0, len(failures), 5000):
            cur.executemany(
                """
                insert into analytics.identity_check_failure
                    (company_id, identity_name, layer, period_id, period_end, expected, actual, rel_gap, operands)
                values (%(company_id)s, %(identity_name)s, %(layer)s, %(period_id)s, %(period_end)s,
                        %(expected)s, %(actual)s, %(rel_gap)s, %(operands)s)
                """,
                failures[start : start + 5000],
            )
    conn.commit()


def run_all(
    conn: psycopg.Connection,
    layers: tuple[str, ...] = LAYERS,
    ciks: set[str] | None = None,
    identity_names: set[str] | None = None,
) -> dict:
    with conn.cursor() as cur:
        cur.execute("select name, id from analytics.canonical_concept")
        concept_ids = dict(cur.fetchall())
        tags = sorted({tag for i in IDENTITIES for tag, _ in i.adjustments})
        cur.execute(
            "select tag, id from core.concept where taxonomy = 'us-gaap' and tag = any(%s)", (tags,)
        )
        adjustment_ids = dict(cur.fetchall())
        if ciks:
            cur.execute("select id from core.company where cik = any(%s) order by id", (list(ciks),))
        else:
            cur.execute("select id from core.company where status = 'active' order by id")
        company_ids = [r[0] for r in cur.fetchall()]

    identities = [i for i in IDENTITIES if not identity_names or i.name in identity_names]
    stats: dict[str, dict] = {}
    for start in range(0, len(company_ids), CHUNK_SIZE):
        chunk = company_ids[start : start + CHUNK_SIZE]
        for identity in identities:
            for layer in layers:
                summary, failures, skipped = check_chunk(
                    conn, identity, layer, concept_ids, adjustment_ids, chunk
                )
                _write_chunk(conn, identity.name, layer, chunk, summary, failures)
                s = stats.setdefault(f"{identity.name}/{layer}", {"checked": 0, "passed": 0, "tautology_skipped": 0})
                s["checked"] += sum(v[0] for v in summary.values())
                s["passed"] += sum(v[1] for v in summary.values())
                s["tautology_skipped"] += skipped
        logger.info("identity_check.chunk_done", done=min(start + CHUNK_SIZE, len(company_ids)), total=len(company_ids))
    for s in stats.values():
        s["pass_pct"] = round(100 * s["passed"] / s["checked"], 2) if s["checked"] else None
    return stats
