"""DQC validation checks over a company's SERVED cells (data-team/tags/validations/dqc-checks.csv).

Report-only by default: `check_company` reads analytics.canonical_fact (the served cells) and the printed
core.fact rows and returns Hits (check_id, company, data_point, period, values, on_fail). A check whose on_fail
starts with 'hold the cell' is a HOLD hit: with the explicit hold flag the plan (company_tag_map_plan.run) removes
that served cell and writes a visible defect reason instead. A missing value is NEVER derived from an identity.

Implemented checks are registered in EVALUATORS. Every CSV row that has no evaluator is reported as UNSUPPORTED with
a reason (UNSUPPORTED_REASONS); nothing is faked. Evidence labels: the identity tolerance is DATA-INFERRED (core.fact
does not carry the filer's dcml; the rounding unit of each operand is its trailing zeros, capped at 10^9, which is
the looser, never the stricter, reading).
"""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Callable

import psycopg

from scrooner_pipeline.mapper import company_tag_map as ctm

DEFAULT_CSV = (
    Path(__file__).resolve().parents[4] / "data-team/tags/validations/dqc-checks.csv"
)
DATA_WINDOW_START = date(2015, 1, 1)  # invariant I11
HOLD_PREFIX = "hold the cell"
MAX_UNIT_EXP = 9
DEI_WINDOW = timedelta(days=150)
RULE_ID = "dqc.checks@1"


@dataclass(frozen=True)
class Check:
    check_id: str
    source_rule: str
    check_type: str
    data_points: tuple[str, ...]
    condition: str
    on_fail: str
    source: str

    @property
    def hold(self) -> bool:
        return self.on_fail.strip().lower().startswith(HOLD_PREFIX)


@dataclass(frozen=True)
class Hit:
    check_id: str
    company_id: int
    data_point: str
    canonical_concept_id: int
    period_id: int
    period_start: date
    period_end: date
    period_type: str
    values: dict[str, str]
    on_fail: str
    hold: bool

    def as_row(self) -> dict[str, str]:
        return {
            "check_id": self.check_id,
            "company_id": str(self.company_id),
            "data_point": self.data_point,
            "period_end": self.period_end.isoformat(),
            "values": json.dumps(self.values, sort_keys=True),
            "on_fail": self.on_fail,
            "hold": "yes" if self.hold else "no",
        }


REPORT_COLUMNS = (
    "check_id",
    "company_id",
    "data_point",
    "period_end",
    "values",
    "on_fail",
    "hold",
)


def load_checks(path: Path | None = None) -> list[Check]:
    out: list[Check] = []
    with (path or DEFAULT_CSV).open(newline="") as fh:
        for r in csv.DictReader(fh):
            out.append(
                Check(
                    r["check_id"].strip(),
                    r["source_rule"].strip(),
                    r["check_type"].strip(),
                    tuple(x.strip() for x in r["data_points"].split(";") if x.strip()),
                    r["condition"].strip(),
                    r["on_fail"].strip(),
                    r["source"].strip(),
                )
            )
    ids = [c.check_id for c in out]
    if len(ids) != len(set(ids)):
        raise ValueError("dqc-checks.csv: duplicate check_id")
    return out


def write_report(hits: list[Hit], path: Path) -> None:
    with path.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=REPORT_COLUMNS)
        w.writeheader()
        for h in sorted(
            hits, key=lambda h: (h.company_id, h.check_id, h.data_point, h.period_end)
        ):
            w.writerow(h.as_row())


# --------------------------------------------------------------------------------------------------------------
# context: one company's served cells + printed facts
# --------------------------------------------------------------------------------------------------------------
@dataclass(frozen=True)
class Cell:
    concept: str
    canonical_concept_id: int
    period_id: int
    start: date
    end: date
    ptype: str
    value: Decimal


@dataclass
class Ctx:
    company_id: int
    by_dp: dict[str, dict[int, list[Cell]]] = field(
        default_factory=dict
    )  # base name -> period_id -> cells
    cell_by_name: dict[tuple[str, int], Cell] = field(default_factory=dict)
    sources: list[tuple[str, int, str, Decimal, int]] = field(
        default_factory=list
    )  # concept, pid, tag, value, fact id
    facts: dict[str, dict[int, ctm.Fact]] = field(
        default_factory=dict
    )  # tag -> period_id -> printed fact
    mixed_revenue_filings: list[tuple[date, str]] = field(default_factory=list)
    src_tags: dict[tuple[str, int], set[str]] = field(default_factory=dict)

    def fact(self, tag: str, pid: int) -> Decimal | None:
        f = self.facts.get(tag, {}).get(pid)
        return None if f is None else f.value

    def served(self, dp: str, pid: int) -> Cell | None:
        cells = self.by_dp.get(dp, {}).get(pid)
        return cells[0] if cells else None

    def hits(
        self, check: Check, dp: str, pid: int, values: dict[str, str]
    ) -> list[Hit]:
        return [
            Hit(
                check.check_id,
                self.company_id,
                c.concept,
                c.canonical_concept_id,
                pid,
                c.start,
                c.end,
                c.ptype,
                values,
                check.on_fail,
                check.hold,
            )
            for c in self.by_dp.get(dp, {}).get(pid, [])
        ]


def _base(name: str) -> str:
    return name[: -len("_resolved")] if name.endswith("_resolved") else name


def _taxonomy(tag: str) -> str:
    return "dei" if tag.startswith("Entity") else "us-gaap"


def load_context(
    conn: psycopg.Connection,
    company_id: int,
    fact_tags: set[str],
    source_tags: set[str],
) -> Ctx:
    ctx = Ctx(company_id)
    with conn.cursor() as cur:
        cur.execute(
            """
            select cc.name, cf.canonical_concept_id, cf.period_id, p.start_date, p.end_date, p.period_type, cf.value
            from analytics.canonical_fact cf
            join analytics.canonical_concept cc on cc.id = cf.canonical_concept_id
            join core.period p on p.id = cf.period_id
            where cf.company_id = %s and p.end_date >= %s and cf.value is not null
            order by cc.name
            """,
            (company_id, DATA_WINDOW_START),
        )
        for name, ccid, pid, start, end, ptype, value in cur.fetchall():
            cell = Cell(name, ccid, pid, start, end, ptype, Decimal(value))
            ctx.cell_by_name[(name, pid)] = cell
            # ordered by name: a plain concept comes before its _resolved twin; the first cell is the value compared
            ctx.by_dp.setdefault(_base(name), {}).setdefault(pid, []).append(cell)
        cur.execute(
            """
            select cc.name, cf.period_id, c.tag, f.value, f.id
            from analytics.canonical_fact cf
            join analytics.canonical_concept cc on cc.id = cf.canonical_concept_id
            join core.period p on p.id = cf.period_id
            cross join lateral unnest(cf.source_fact_ids) as sid
            join core.fact f on f.id = sid
            join core.concept c on c.id = f.concept_id
            where cf.company_id = %s and p.end_date >= %s and c.tag = any(%s)
            """,
            (company_id, DATA_WINDOW_START, sorted(source_tags)),
        )
        for name, pid, tag, value, fid in cur.fetchall():
            ctx.sources.append((name, pid, tag, Decimal(value), fid))
            ctx.src_tags.setdefault((name, pid), set()).add(tag)
        cur.execute(
            """
            select p.end_date, fl.accession_number
            from core.fact f
            join core.concept c on c.id = f.concept_id
            join core.period p on p.id = f.period_id
            join core.filing fl on fl.id = f.filing_id
            where f.company_id = %s and f.is_authoritative and p.end_date >= %s and c.taxonomy = 'us-gaap'
              and (c.tag like 'RevenueFromContractWithCustomer%%'
                   or c.tag in ('SalesRevenueNet', 'SalesRevenueGoodsNet', 'SalesRevenueServicesNet'))
            group by p.end_date, fl.accession_number
            having bool_or(c.tag like 'RevenueFromContractWithCustomer%%')
               and bool_or(c.tag in ('SalesRevenueNet', 'SalesRevenueGoodsNet', 'SalesRevenueServicesNet'))
            """,
            (company_id, DATA_WINDOW_START),
        )
        ctx.mixed_revenue_filings = [(e, a) for e, a in cur.fetchall()]
    loaded = ctm._load_facts(conn, company_id, {(_taxonomy(t), t) for t in fact_tags})
    for (_, tag), by_period in loaded.items():
        # printed facts only: a derived or ambiguous (two units) value is never an operand
        ctx.facts[tag] = {
            pid: f for pid, f in by_period.items() if not f.derived and not f.ambiguous
        }
    return ctx


# --------------------------------------------------------------------------------------------------------------
# evaluators
# --------------------------------------------------------------------------------------------------------------
def _unit(v: Decimal) -> Decimal:
    exp = v.normalize().as_tuple().exponent if v != 0 else 0
    return Decimal(10) ** min(int(exp), MAX_UNIT_EXP)


def tolerance(values: list[Decimal]) -> Decimal:
    """Half a rounding unit per operand (DATA-INFERRED dcml: trailing zeros, capped at 10^9)."""
    return sum((_unit(v) / 2 for v in values), Decimal(0))


Spec = tuple[str, str]  # ('tag', name) | ('served', data point)


def _tag(t: str) -> Spec:
    return ("tag", t)


def _srv(d: str) -> Spec:
    return ("served", d)


def _val(ctx: Ctx, spec: Spec, pid: int) -> Decimal | None:
    kind, name = spec
    if kind == "tag":
        return ctx.fact(name, pid)
    c = ctx.served(name, pid)
    return None if c is None else c.value


def _periods(ctx: Ctx, spec: Spec) -> list[int]:
    kind, name = spec
    return sorted(ctx.facts.get(name, {}) if kind == "tag" else ctx.by_dp.get(name, {}))


def _tie(
    ctx: Ctx, check: Check, lhs: Spec, terms: list[Spec], dps: list[str], label: str
) -> list[Hit]:
    """lhs = sum(terms) at the same period when EVERY operand is printed/served; a failure is a hit on each listed
    data point that has a served cell there. Nothing is derived when an operand is missing."""
    out: list[Hit] = []
    for pid in _periods(ctx, lhs):
        a = _val(ctx, lhs, pid)
        bs = [_val(ctx, t, pid) for t in terms]
        if a is None or any(b is None for b in bs):
            continue
        rhs = sum((b for b in bs if b is not None), Decimal(0))
        tol = tolerance([a, *[b for b in bs if b is not None]])
        if abs(a - rhs) > tol:
            vals = {
                "identity": label,
                "lhs": str(a),
                "rhs": str(rhs),
                "diff": str(a - rhs),
                "tolerance": str(tol),
            }
            for dp in dps:
                out += ctx.hits(check, dp, pid, vals)
    return out


def _eval_4_01(ctx, c):
    return _tie(
        ctx,
        c,
        _srv("total_assets"),
        [_tag("LiabilitiesAndStockholdersEquity")],
        ["total_assets"],
        "Assets = LiabilitiesAndStockholdersEquity",
    )


def _eval_4_02(ctx, c):
    return _tie(
        ctx,
        c,
        _srv("total_assets"),
        [_tag("AssetsCurrent"), _tag("AssetsNoncurrent")],
        ["total_assets", "current_assets"],
        "Assets = AssetsCurrent + AssetsNoncurrent",
    )


def _eval_4_03(ctx, c):
    return _tie(
        ctx,
        c,
        _srv("total_liabilities"),
        [_tag("LiabilitiesCurrent"), _tag("LiabilitiesNoncurrent")],
        ["total_liabilities", "current_liabilities"],
        "Liabilities = LiabilitiesCurrent + LiabilitiesNoncurrent",
    )


def _eval_4_04(ctx, c):
    return _tie(
        ctx,
        c,
        _tag("StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"),
        [_tag("StockholdersEquity"), _tag("MinorityInterest")],
        ["stockholders_equity"],
        "equity incl NCI = StockholdersEquity + MinorityInterest",
    )


def _eval_4_05(ctx, c):
    return _tie(
        ctx,
        c,
        _tag("LiabilitiesAndStockholdersEquity"),
        [
            _tag(
                "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"
            ),
            _tag("Liabilities"),
            _tag(
                "TemporaryEquityCarryingAmountIncludingPortionAttributableToNoncontrollingInterests"
            ),
        ],
        ["total_liabilities", "stockholders_equity"],
        "L&SE = equity incl NCI + Liabilities + TemporaryEquity",
    )


def _eval_4_06(ctx, c):
    out: list[Hit] = []
    for dp, kind, cont, disc in (
        (
            "cfo",
            "Operating",
            "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations",
            "CashProvidedByUsedInOperatingActivitiesDiscontinuedOperations",
        ),
        (
            "cash_flow_investing",
            "Investing",
            "NetCashProvidedByUsedInInvestingActivitiesContinuingOperations",
            "CashProvidedByUsedInInvestingActivitiesDiscontinuedOperations",
        ),
        (
            "cash_flow_financing",
            "Financing",
            "NetCashProvidedByUsedInFinancingActivitiesContinuingOperations",
            "CashProvidedByUsedInFinancingActivitiesDiscontinuedOperations",
        ),
    ):
        out += _tie(
            ctx,
            c,
            _srv(dp),
            [_tag(cont), _tag(disc)],
            [dp],
            f"net cash {kind} = continuing + discontinued",
        )
    return out


def _eval_4_07(ctx, c):
    return _tie(
        ctx,
        c,
        _tag(
            "ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest"
        ),
        [_tag("ProfitLoss"), _tag("OtherComprehensiveIncomeLossNetOfTax")],
        ["comprehensive_income"],
        "comprehensive income incl NCI = ProfitLoss + OCI",
    ) + _tie(
        ctx,
        c,
        _tag(
            "ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest"
        ),
        [
            _tag("ComprehensiveIncomeNetOfTaxAttributableToNoncontrollingInterest"),
            _tag("ComprehensiveIncomeNetOfTax"),
        ],
        ["comprehensive_income"],
        "comprehensive income incl NCI = NCI + parent",
    )


def _eval_9_01(ctx, c):
    out: list[Hit] = []
    for pid, cells in ctx.by_dp.get("shares_outstanding", {}).items():
        v = cells[0].value
        iss = ctx.fact("CommonStockSharesIssued", pid)
        auth = ctx.fact("CommonStockSharesAuthorized", pid)
        if iss is not None and v > iss:
            out += ctx.hits(
                c,
                "shares_outstanding",
                pid,
                {
                    "outstanding": str(v),
                    "issued": str(iss),
                    "note": "outstanding > issued",
                },
            )
        if iss is not None and auth is not None and iss > auth:
            out += ctx.hits(
                c,
                "shares_outstanding",
                pid,
                {
                    "issued": str(iss),
                    "authorized": str(auth),
                    "note": "issued > authorized",
                },
            )
    return out


def _eval_shr(ctx, c):
    out: list[Hit] = []
    dei = list(ctx.facts.get("EntityCommonStockSharesOutstanding", {}).values())
    for pid, cells in ctx.by_dp.get("shares_outstanding", {}).items():
        cell = cells[0]
        near = [f for f in dei if abs(f.end - cell.end) <= DEI_WINDOW]
        if not near or cell.value <= 0:
            continue
        f = min(near, key=lambda f: abs((f.end - cell.end).days))
        if f.value <= 0:
            continue
        ratio = cell.value / f.value
        if not (Decimal("0.5") <= ratio <= 2):
            out += ctx.hits(
                c,
                "shares_outstanding",
                pid,
                {
                    "served": str(cell.value),
                    "cover_count": str(f.value),
                    "ratio": str(ratio.quantize(Decimal("0.0001"))),
                    "cover_date": f.end.isoformat(),
                },
            )
    return out


def _eval_65(ctx, c):
    out: list[Hit] = []
    for pid, cells in ctx.by_dp.get("cash_paid_for_interest", {}).items():
        tags = ctx.src_tags.get((cells[0].concept, pid), set())
        if "InterestPaid" in tags and "InterestPaidNet" not in tags:
            out += ctx.hits(
                c,
                "cash_paid_for_interest",
                pid,
                {
                    "source_tag": "InterestPaid",
                    "interest_paid_net_printed": str(
                        ctx.fact("InterestPaidNet", pid) is not None
                    ).lower(),
                },
            )
    return out


def _eval_it(ctx, c):
    out: list[Hit] = []
    jur = {
        "IncomeTaxPaidFederalAfterRefundReceived",
        "IncomeTaxPaidStateAndLocalAfterRefundReceived",
        "IncomeTaxPaidForeignAfterRefundReceived",
    }
    for pid, cells in ctx.by_dp.get("cash_paid_for_income_taxes", {}).items():
        tags = ctx.src_tags.get((cells[0].concept, pid), set())
        net = ctx.fact("IncomeTaxesPaidNet", pid)
        if tags & jur:
            out += ctx.hits(
                c,
                "cash_paid_for_income_taxes",
                pid,
                {
                    "source_tags": ",".join(sorted(tags)),
                    "note": "component_sum candidate",
                },
            )
        elif "IncomeTaxesPaid" in tags and net is not None:
            out += ctx.hits(
                c,
                "cash_paid_for_income_taxes",
                pid,
                {"source_tag": "IncomeTaxesPaid", "IncomeTaxesPaidNet": str(net)},
            )
    return out


def _eval_180(ctx, c):
    out: list[Hit] = []
    for pid, cells in ctx.by_dp.get("dividends_per_share", {}).items():
        tags = ctx.src_tags.get((cells[0].concept, pid), set())
        if "DividendsPayableAmountPerShare" in tags:
            out += ctx.hits(
                c,
                "dividends_per_share",
                pid,
                {
                    "source_tag": "DividendsPayableAmountPerShare",
                    "note": "an instant, not period DPS",
                },
            )
        elif (
            "CommonStockDividendsPerShareCashPaid" in tags
            and ctx.fact("CommonStockDividendsPerShareDeclared", pid) is not None
        ):
            out += ctx.hits(
                c,
                "dividends_per_share",
                pid,
                {
                    "source_tag": "CommonStockDividendsPerShareCashPaid",
                    "declared": str(
                        ctx.fact("CommonStockDividendsPerShareDeclared", pid)
                    ),
                },
            )
    return out


def _eval_187(ctx, c):
    return _tie(
        ctx,
        c,
        _tag("PropertyPlantAndEquipmentGross"),
        [
            _tag("PropertyPlantAndEquipmentNet"),
            _tag(
                "AccumulatedDepreciationDepletionAndAmortizationPropertyPlantAndEquipment"
            ),
        ],
        ["ppe_net"],
        "PPE gross = net + accumulated depreciation",
    )


def _eval_67(ctx, c):
    out: list[Hit] = []
    for end, accession in ctx.mixed_revenue_filings:
        for pid, cells in ctx.by_dp.get("revenue", {}).items():
            if cells[0].end == end:
                out += ctx.hits(
                    c,
                    "revenue",
                    pid,
                    {
                        "accession": accession,
                        "note": "RevenueFromContractWithCustomer* and SalesRevenue* in one filing",
                    },
                )
    return out


def _nonneg(tags: tuple[str, ...]) -> Callable[[Ctx, Check], list[Hit]]:
    def run(ctx: Ctx, c: Check) -> list[Hit]:
        out: list[Hit] = []
        seen: set[tuple[str, int, str]] = set()
        for concept, pid, tag, value, _fid in ctx.sources:
            if tag not in tags or value >= 0 or (concept, pid, tag) in seen:
                continue
            seen.add((concept, pid, tag))
            cell = ctx.cell_by_name[(concept, pid)]
            out.append(
                Hit(
                    c.check_id,
                    ctx.company_id,
                    concept,
                    cell.canonical_concept_id,
                    pid,
                    cell.start,
                    cell.end,
                    cell.ptype,
                    {"tag": tag, "fact_value": str(value), "served": str(cell.value)},
                    c.on_fail,
                    c.hold,
                )
            )
        return out

    return run


EVALUATORS: dict[str, Callable[[Ctx, Check], list[Hit]]] = {
    "DQC4-01": _eval_4_01,
    "DQC4-02": _eval_4_02,
    "DQC4-03": _eval_4_03,
    "DQC4-04": _eval_4_04,
    "DQC4-05": _eval_4_05,
    "DQC4-06": _eval_4_06,
    "DQC4-07": _eval_4_07,
    "DQC9-01": _eval_9_01,
    "SEC-SHR-01": _eval_shr,
    "DQC65-01": _eval_65,
    "IT-01": _eval_it,
    "DQC180-01": _eval_180,
    "DQC187-01": _eval_187,
    "DQC67-01": _eval_67,
}
NONNEG_TAGS: dict[str, tuple[str, ...]] = {
    "SEC-NEG-IE": (
        "InterestExpense",
        "InterestExpenseNonoperating",
        "InterestExpenseOperating",
        "InterestExpenseDebt",
    ),
}
# check_id -> why there is no evaluator (never faked)
UNSUPPORTED_REASONS: dict[str, str] = {
    "DQC181-01": "needs the filer's calculation tree (calc-parent of InterestExpense); not in core.fact (FSN calc arcs are not read here)",
    "DQC51-01": "needs the filer's calculation tree (income-tax descendants of the pretax/NCI lines)",
    "DQC119-01": "needs the calculation tree (equity-method income inside the pretax total)",
    "DQC71-01": "needs ProductOrServiceAxis members; core.fact is non-dimensional by construction",
    "DQC227-01": "two-class (participating securities) filers cannot be detected from core.fact, so the skip rule cannot be applied; a check without it would false-hit",
    "DQC230-01": "needs calculation-tree sibling relations between an aggregate and its 'other' concept",
    "DQC57-01": "needs the cash-flow statement structure (which opening/closing cash element is used) per filing era",
    "DQC206-01": "needs DisaggregationOfIncomeStatementExpenseCaptionIdentifierAxis / IncomeStatementLocationAxis members (dimensional)",
    "DISE-01": "its second branch (no cost-of-sales child) needs the calculation tree; the tie alone would mislabel legitimate opex",
}

# every tag an evaluator reads from core.fact, and every source tag it looks up behind a served cell
FACT_TAGS = {
    "LiabilitiesAndStockholdersEquity",
    "AssetsCurrent",
    "AssetsNoncurrent",
    "LiabilitiesCurrent",
    "LiabilitiesNoncurrent",
    "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
    "StockholdersEquity",
    "MinorityInterest",
    "Liabilities",
    "TemporaryEquityCarryingAmountIncludingPortionAttributableToNoncontrollingInterests",
    "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations",
    "CashProvidedByUsedInOperatingActivitiesDiscontinuedOperations",
    "NetCashProvidedByUsedInInvestingActivitiesContinuingOperations",
    "CashProvidedByUsedInInvestingActivitiesDiscontinuedOperations",
    "NetCashProvidedByUsedInFinancingActivitiesContinuingOperations",
    "CashProvidedByUsedInFinancingActivitiesDiscontinuedOperations",
    "ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest",
    "ProfitLoss",
    "OtherComprehensiveIncomeLossNetOfTax",
    "ComprehensiveIncomeNetOfTaxAttributableToNoncontrollingInterest",
    "ComprehensiveIncomeNetOfTax",
    "CommonStockSharesIssued",
    "CommonStockSharesAuthorized",
    "EntityCommonStockSharesOutstanding",
    "InterestPaidNet",
    "IncomeTaxesPaidNet",
    "CommonStockDividendsPerShareDeclared",
    "PropertyPlantAndEquipmentGross",
    "PropertyPlantAndEquipmentNet",
    "AccumulatedDepreciationDepletionAndAmortizationPropertyPlantAndEquipment",
}
PREFERENCE_SOURCE_TAGS = {
    "InterestPaid",
    "InterestPaidNet",
    "IncomeTaxesPaid",
    "IncomeTaxesPaidNet",
    "IncomeTaxPaidFederalAfterRefundReceived",
    "IncomeTaxPaidStateAndLocalAfterRefundReceived",
    "IncomeTaxPaidForeignAfterRefundReceived",
    "DividendsPayableAmountPerShare",
    "CommonStockDividendsPerShareCashPaid",
}


def nonneg_tags(check: Check) -> tuple[str, ...] | None:
    """The tags a non_negative row covers: SEC-NEG-IE lists four; DQC15-<Tag> is its own tag."""
    if check.check_type != "non_negative":
        return None
    if check.check_id in NONNEG_TAGS:
        return NONNEG_TAGS[check.check_id]
    if check.check_id.startswith("DQC15-"):
        return (check.check_id[len("DQC15-") :],)
    return None


def evaluator(check: Check) -> Callable[[Ctx, Check], list[Hit]] | None:
    if check.check_id in EVALUATORS:
        return EVALUATORS[check.check_id]
    tags = nonneg_tags(check)
    return _nonneg(tags) if tags else None


def split_checks(checks: list[Check]) -> tuple[list[Check], dict[str, str]]:
    """(implemented checks, unsupported check_id -> reason). A row with no evaluator and no stated reason is still
    reported unsupported, never silently dropped."""
    impl = [c for c in checks if evaluator(c) is not None]
    unsupported = {
        c.check_id: UNSUPPORTED_REASONS.get(c.check_id, "no evaluator registered")
        for c in checks
        if evaluator(c) is None
    }
    return impl, unsupported


def check_company(
    conn: psycopg.Connection, company_id: int, checks: list[Check]
) -> list[Hit]:
    """Hits of the implemented checks over the company's served cells (as they are in this transaction)."""
    impl, _ = split_checks(checks)
    if not impl:
        return []
    source_tags = set(PREFERENCE_SOURCE_TAGS)
    for c in impl:
        source_tags |= set(nonneg_tags(c) or ())
    ctx = load_context(conn, company_id, set(FACT_TAGS), source_tags)
    out: list[Hit] = []
    for c in impl:
        ev = evaluator(c)
        assert ev is not None
        out += ev(ctx, c)
    return out


def hits_by_check(hits: list[Hit]) -> dict[str, int]:
    n: dict[str, int] = defaultdict(int)
    for h in hits:
        n[h.check_id] += 1
    return dict(sorted(n.items()))
