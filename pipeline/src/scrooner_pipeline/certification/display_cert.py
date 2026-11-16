"""Display-coverage certification (founder decision 2026-11-16, doc 02; method in
data-team/strategy/approvals/CERTIFICATION-METHOD-2026-11-16.md).

The approver's checks, as a system:

1. Gate: no OPEN cell; every shown cell has a value, an accession and an R page; no row is
   both hidden and shown.
2. Shown draw: a seeded random sample of SHOWN_VALUE cells. Each is matched to the SEC
   Financial Statement and Notes data set (fsn.*) of the cited filing: same tag, same period
   end, same duration, same dimensions, and the tag is presented on the cited R page.
   fsn.* is SEC's own extraction of every filing, independent of our mapper and proof.
3. Census: every shown total_debt year is rebuilt from the filing's debt-family and
   lease facts, not from the parts the proof chose.
4. Hides: a HIDDEN_ROW must have no undimensioned fact of its family in any periodic
   filing of the company; a HIDDEN_YEAR must have no statement fact dated at that year end
   in any periodic filing (10-K, 10-Q, 20-F, 40-F, including comparative columns).
5. Bound: exact Clopper-Pearson upper bound on the shown-cell error rate.

Pure functions. The fact source is injected (`FactSource.facts(...)`), so the same checks run
on a live connection (`SqlFactSource`) or on an evidence bundle exported as JSON. Money and
counts are Decimal end to end.
"""

from __future__ import annotations

import csv
import hashlib
import json
import random
import re
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from math import comb
from pathlib import Path
from typing import Protocol

SHOWN = "SHOWN_VALUE"
HIDDEN_ROW = "HIDDEN_ROW"
HIDDEN_YEAR = "HIDDEN_YEAR"
OPEN = "OPEN"
DRAW_SIZE = 32  # 0 errors in 32 -> 8.94% per-company bound; the 0.10% target is pooled
PERIODIC_FORMS = (
    "10-K",
    "10-K/A",
    "10-Q",
    "10-Q/A",
    "20-F",
    "20-F/A",
    "40-F",
    "40-F/A",
)

# Balance-sheet and share data points are instants (qtrs 0); everything else is a duration.
INSTANT_DPS = frozenset(
    {
        "cash_and_equivalents",
        "accounts_receivable",
        "inventory",
        "current_assets",
        "ppe_net",
        "goodwill",
        "total_assets",
        "accounts_payable",
        "current_liabilities",
        "total_liabilities",
        "stockholders_equity",
        "shares_outstanding",
        "total_debt",
    }
)

# total_debt perimeter (founder 2026-11-04): face short-term debt and commercial paper, current
# and long-term debt, note finance leases, pre-842 capital leases. Never operating leases.
DEBT_FACE_TAGS = frozenset(
    {
        "ShortTermBorrowings",
        "CommercialPaper",
        "DebtCurrent",
        "ShortTermDebt",
        "OtherShortTermBorrowings",
        "LongTermDebtCurrent",
        "LongTermDebtNoncurrent",
        "LongTermDebt",
        "LongTermDebtAndCapitalLeaseObligationsCurrent",
        "LongTermDebtAndCapitalLeaseObligations",
        "LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities",
        "DebtAndCapitalLeaseObligations",
        "ConvertibleDebtCurrent",
        "ConvertibleDebtNoncurrent",
        "ConvertibleNotesPayableCurrent",
        "ConvertibleLongTermNotesPayable",
        "SeniorNotes",
        "SeniorNotesCurrent",
        "SeniorLongTermNotes",
        "LoansPayableCurrent",
        "LongTermLoansPayable",
        "NotesPayableCurrent",
        "LongTermNotesPayable",
        "UnsecuredLongTermDebt",
        "SecuredDebt",
        "FinanceLeaseLiabilityCurrent",
        "FinanceLeaseLiabilityNoncurrent",
        "CapitalLeaseObligationsCurrent",
        "CapitalLeaseObligationsNoncurrent",
    }
)
LEASE_TAGS = frozenset(
    {
        "FinanceLeaseLiability",
        "FinanceLeaseLiabilityCurrent",
        "FinanceLeaseLiabilityNoncurrent",
        "CapitalLeaseObligations",
        "CapitalLeaseObligationsCurrent",
        "CapitalLeaseObligationsNoncurrent",
    }
)
# A face debt tag whose definition already includes lease obligations.
LEASE_INCLUSIVE_FACE = frozenset(
    t for t in DEBT_FACE_TAGS if "CapitalLease" in t and t not in LEASE_TAGS
)

# Evidence that a hidden row IS reported: undimensioned facts on these tags in any periodic filing.
HIDE_FAMILY: dict[str, tuple[str, ...]] = {
    "interest_income": (
        "InvestmentIncomeInterest",
        "InterestIncomeOther",
        "InterestAndOtherIncome",
        "InvestmentIncomeInterestAndDividend",
        "InterestIncomeOperating",
        "InterestIncomeNonoperating",
    ),
    "interest_expense": (
        "InterestExpense",
        "InterestExpenseNonoperating",
        "InterestExpenseDebt",
        "InterestExpenseOperating",
        "InterestAndDebtExpense",
    ),
    "sbc": (
        "ShareBasedCompensation",
        "AllocatedShareBasedCompensationExpense",
        "ShareBasedCompensationArrangementByShareBasedPaymentAwardCompensationCost1",
    ),
    "sga_expense": (
        "SellingGeneralAndAdministrativeExpense",
        "GeneralAndAdministrativeExpense",
    ),
    "gross_profit": ("GrossProfit",),
    "operating_income": ("OperatingIncomeLoss",),
    "operating_expenses": (
        "OperatingExpenses",
        "CostsAndExpenses",
        "OperatingCostsAndExpenses",
    ),
    "shares_outstanding": ("CommonStockSharesOutstanding",),
    "cf_ap_change": (
        "IncreaseDecreaseInAccountsPayable",
        "IncreaseDecreaseInAccountsPayableTrade",
    ),
    "other_income_expense_net": (
        "OtherNonoperatingIncomeExpense",
        "NonoperatingIncomeExpense",
    ),
    "dividends_paid": ("PaymentsOfDividendsCommonStock", "PaymentsOfDividends"),
    "dividends_per_share": (
        "CommonStockDividendsPerShareDeclared",
        "CommonStockDividendsPerShareCashPaid",
    ),
    "share_buybacks": ("PaymentsForRepurchaseOfCommonStock",),
    "comprehensive_income": ("ComprehensiveIncomeNetOfTax",),
    "research_and_development": ("ResearchAndDevelopmentExpense",),
    "inventory": ("InventoryNet",),
    "cost_of_revenue": ("CostOfRevenue", "CostOfGoodsAndServicesSold"),
    "amortization_of_intangibles": ("AmortizationOfIntangibleAssets",),
    "depreciation_and_amortization": (
        "DepreciationDepletionAndAmortization",
        "DepreciationAndAmortization",
        "DepreciationAmortizationAndAccretionNet",
    ),
    "capex": (
        "PaymentsToAcquirePropertyPlantAndEquipment",
        "PaymentsToAcquireProductiveAssets",
    ),
    "goodwill": ("Goodwill",),
}


# ---------------------------------------------------------------- coverage and gate
@dataclass(frozen=True)
class Part:
    tag: str
    dims: str  # "" or "Axis=Member;..." normalized by norm_dims
    value: Decimal  # the fact as filed
    accession: str
    r_page: str  # "R5"
    sign: int = (
        1  # -1 when the proof subtracts this fact ("-Tag=..." in the parts column)
    )


@dataclass(frozen=True)
class Cell:
    data_point: str
    fiscal_year: str
    period_end: str
    display: str
    value: Decimal | None
    accession: str
    r_page: str
    tag: str
    parts: tuple[Part, ...] = ()

    @property
    def key(self) -> tuple[str, str]:
        return (self.data_point, self.fiscal_year)

    @property
    def qtrs(self) -> int:
        return 0 if self.data_point in INSTANT_DPS else 4


_PART_RX = re.compile(
    r"^(?P<neg>-?)(?P<tag>[A-Za-z0-9_]+)(?:\[(?P<dims>[^\]]*)\])?=(?P<val>-?[0-9.]+)@(?P<acc>[0-9-]+)#(?P<r>R?\d*)$"
)


def parse_parts(text: str) -> tuple[Part, ...]:
    out = []
    for raw in (text or "").split(";"):
        raw = raw.strip()
        if not raw:
            continue
        m = _PART_RX.match(raw)
        if not m:
            raise ValueError(f"unparseable part: {raw!r}")
        dims = norm_dims((m["dims"] or "").replace(",", ";"))
        r = m["r"] if m["r"].startswith("R") or not m["r"] else "R" + m["r"]
        out.append(
            Part(m["tag"], dims, Decimal(m["val"]), m["acc"], r, -1 if m["neg"] else 1)
        )
    return tuple(out)


def norm_dims(seg: str) -> str:
    """One spelling for a dimension set: fsn.dim.segments writes 'EquityComponents=AdditionalPaidInCapital;',
    a proof may write 'us-gaap:EquityComponentsAxis=us-gaap:AdditionalPaidInCapitalMember'."""
    out = []
    for kv in (seg or "").split(";"):
        if "=" not in kv:
            continue
        a, m = (x.strip().split(":")[-1] for x in kv.split("=", 1))
        out.append(f"{a.removesuffix('Axis')}={m.removesuffix('Member')}")
    return ";".join(sorted(out))


def _dec(s: str) -> Decimal | None:
    s = (s or "").strip()
    return Decimal(s) if s else None


def _rpage(s: str) -> str:
    s = (s or "").strip().removesuffix(".htm")
    return s if not s or s.startswith("R") else "R" + s


def read_coverage(path: Path) -> list[Cell]:
    with open(path, newline="") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        raise ValueError(f"{path}: empty coverage file")
    col = next((c for c in rows[0] if c.lower() in ("display", "display_class")), None)
    if col is None:
        raise ValueError(
            f"{path}: no display column (CERTIFICATION-METHOD-2026-11-16 needs the display export)"
        )
    cells = []
    for r in rows:
        parts = r.get("parts", "") or ""
        cells.append(
            Cell(
                data_point=r["data_point"],
                fiscal_year=r["fiscal_year"],
                period_end=r.get("period_end", ""),
                display=r[col],
                value=_dec(r.get("shown_value", "")),
                accession=r.get("accession", "").strip(),
                r_page=_rpage(r.get("r_page", "")),
                tag=(r.get("tag", "") or "").strip(),
                parts=parse_parts(parts) if "@" in parts else (),
            )
        )
    return cells


@dataclass(frozen=True)
class Finding:
    check: str  # gate | shown | debt | hidden_row | hidden_year | live
    data_point: str
    fiscal_year: str
    severity: str  # FAIL | REVIEW | INFO
    detail: str


def gate(cells: list[Cell]) -> list[Finding]:
    out = []
    shown_rows = {c.data_point for c in cells if c.display == SHOWN}
    for c in cells:
        if c.display == OPEN:
            out.append(Finding("gate", *c.key, "FAIL", "OPEN cell"))
        elif c.display == SHOWN:
            if c.value is None:
                out.append(Finding("gate", *c.key, "FAIL", "shown cell has no value"))
            if not c.accession or not c.r_page:
                out.append(
                    Finding(
                        "gate", *c.key, "FAIL", "shown cell has no accession or R page"
                    )
                )
            for p in c.parts:
                if not p.accession or not p.r_page:
                    out.append(
                        Finding(
                            "gate",
                            *c.key,
                            "FAIL",
                            f"part {p.tag} has no accession or R page",
                        )
                    )
            if (
                c.parts
                and c.value is not None
                and sum(p.sign * p.value for p in c.parts) != c.value
            ):
                out.append(
                    Finding(
                        "gate",
                        *c.key,
                        "FAIL",
                        f"signed parts sum {sum(p.sign * p.value for p in c.parts)} != shown {c.value}",
                    )
                )
        elif c.display == HIDDEN_ROW and c.data_point in shown_rows:
            out.append(
                Finding(
                    "gate",
                    *c.key,
                    "FAIL",
                    "row is hidden in this year but shown in another: a hidden row must be never reported",
                )
            )
    return out


def draw(cells: list[Cell], seed: str, n: int = DRAW_SIZE) -> list[Cell]:
    pool = sorted(
        (c for c in cells if c.display == SHOWN and c.data_point != "total_debt"),
        key=lambda c: c.key,
    )
    return random.Random(seed).sample(pool, min(n, len(pool)))


# ---------------------------------------------------------------- facts
@dataclass(frozen=True)
class Fact:
    accession: str
    tag: str
    ddate: str  # YYYY-MM-DD
    qtrs: int
    dims: str  # "" for undimensioned
    value: Decimal
    reports: tuple[
        str, ...
    ]  # R pages where the tag is presented in that filing ("R5", ...)


class FactSource(Protocol):
    def facts(self, accessions: Iterable[str], tags: Iterable[str]) -> list[Fact]: ...

    def company_facts(self, cik: str, tags: Iterable[str]) -> list[Fact]: ...

    def periodic_year_ends(self, cik: str) -> dict[str, list[str]]: ...


FACT_SQL = """
select f.accession, t.tag, v.ddate::text, v.qtrs, coalesce(d.segments, '') as segments, v.value,
       coalesce(array_agg(distinct 'R' || l.report) filter (where l.report is not null), '{}') as reports
from fsn.filing f
join fsn.value v on v.filing_id = f.id
join fsn.tag t on t.id = v.tag_id
join fsn.dim d on d.id = v.dim_id
left join fsn.line l on l.filing_id = f.id and l.tag_id = v.tag_id
where f.accession = any(%(acc)s) and t.tag = any(%(tags)s) and v.coreg is null
group by 1, 2, 3, 4, 5, 6
"""

COMPANY_FACT_SQL = """
select f.accession, t.tag, v.ddate::text, v.qtrs, '' as segments, v.value,
       coalesce(array_agg(distinct 'R' || l.report) filter (where l.report is not null), '{}') as reports
from fsn.filing f
join fsn.value v on v.filing_id = f.id and v.coreg is null
join fsn.dim d on d.id = v.dim_id and d.segments = ''
join fsn.tag t on t.id = v.tag_id
left join fsn.line l on l.filing_id = f.id and l.tag_id = v.tag_id
where ltrim(f.cik, '0') = ltrim(%(cik)s, '0') and f.form = any(%(forms)s) and t.tag = any(%(tags)s)
group by 1, 2, 3, 4, 5, 6
"""

YEAR_END_SQL = """
select f.accession, array_agg(distinct v.ddate::text)
from fsn.filing f join fsn.value v on v.filing_id = f.id and v.qtrs in (0, 4)
join fsn.dim d on d.id = v.dim_id and d.segments = ''
join fsn.tag t on t.id = v.tag_id
where ltrim(f.cik, '0') = ltrim(%(cik)s, '0') and f.form = any(%(forms)s)
  and t.tag in ('Assets', 'Revenues', 'RevenueFromContractWithCustomerExcludingAssessedTax', 'NetIncomeLoss',
                'NetCashProvidedByUsedInOperatingActivities', 'ProfitLoss')
group by 1
"""


def _fact(row) -> Fact:
    acc, tag, ddate, qtrs, seg, val, reports = row
    return Fact(
        acc,
        tag,
        str(ddate)[:10],
        int(qtrs),
        norm_dims(seg),
        Decimal(str(val)),
        tuple(sorted(reports or ())),
    )


class SqlFactSource:
    """Live source: read-only SELECTs on fsn.*, each under an explicit statement_timeout."""

    def __init__(self, conn, timeout_ms: int = 15000):
        self.conn = conn
        self.timeout_ms = timeout_ms

    def _q(self, sql: str, params: dict):
        with self.conn.cursor() as cur:
            cur.execute(f"set statement_timeout = {int(self.timeout_ms)}")
            cur.execute(sql, params)
            return cur.fetchall()

    def facts(self, accessions, tags):
        return [
            _fact(r)
            for r in self._q(
                FACT_SQL, {"acc": sorted(set(accessions)), "tags": sorted(set(tags))}
            )
        ]

    def company_facts(self, cik, tags):
        rows = self._q(
            COMPANY_FACT_SQL,
            {"cik": cik, "forms": list(PERIODIC_FORMS), "tags": sorted(set(tags))},
        )
        return [_fact(r) for r in rows]

    def periodic_year_ends(self, cik):
        return {
            acc: sorted(d)
            for acc, d in self._q(
                YEAR_END_SQL, {"cik": cik, "forms": list(PERIODIC_FORMS)}
            )
        }


class BundleFactSource:
    """Offline source: an evidence bundle (JSON) holding the rows of the three queries above."""

    def __init__(self, bundle: dict):
        self.b = bundle

    def facts(self, accessions, tags):
        acc, tg = set(accessions), set(tags)
        return [_fact(r) for r in self.b.get("facts", []) if r[0] in acc and r[1] in tg]

    def company_facts(self, cik, tags):
        tg = set(tags)
        return [_fact(r) for r in self.b.get("company_facts", []) if r[1] in tg]

    def periodic_year_ends(self, cik):
        return {k: sorted(v) for k, v in self.b.get("year_ends", {}).items()}


# ---------------------------------------------------------------- checks
@dataclass(frozen=True)
class Term:
    tag: str
    dims: str
    accession: str
    r_page: str
    sign: int = 1
    claimed: Decimal | None = None  # the part value the proof says it read


def terms(c: Cell) -> list[Term]:
    if c.parts:
        return [
            Term(p.tag, p.dims, p.accession, p.r_page, p.sign, p.value) for p in c.parts
        ]
    return [Term(c.tag.strip().split(":")[-1], "", c.accession, c.r_page)]


def _days(a: str, b: str) -> int:
    return abs((date.fromisoformat(a) - date.fromisoformat(b)).days)


def _pick(facts: list[Fact], term: Term, period_end: str, qtrs: int) -> Fact | None:
    """The fact for a term: same filing, tag, dimensions, duration, and a period end within 7 days
    (52/53-week fiscal years end on a weekday near the nominal date)."""
    cand = [
        f
        for f in facts
        if f.accession == term.accession
        and f.tag == term.tag
        and f.dims == term.dims
        and f.qtrs == qtrs
        and period_end
        and _days(f.ddate, period_end) <= 7
    ]
    cand.sort(key=lambda f: _days(f.ddate, period_end))
    return cand[0] if cand else None


@dataclass(frozen=True)
class CellCheck:
    cell: Cell
    result: str  # MATCH | MISMATCH | NOT_FOUND | LOCATOR
    filing_value: Decimal | None
    evidence: str


def check_cell(c: Cell, facts: list[Fact]) -> CellCheck:
    """A single-tag cell matches on magnitude (display sign conventions differ by row); a summed
    cell must match part by part, as filed, and its signed sum must equal the shown value."""
    ts = terms(c)
    total = Decimal(0)
    ev, locator_ok, part_ok = [], True, True
    for t in ts:
        f = _pick(facts, t, c.period_end, c.qtrs)
        if f is None:
            return CellCheck(
                c,
                "NOT_FOUND",
                None,
                f"no fsn fact {t.tag}[{t.dims}] qtrs={c.qtrs} near {c.period_end} in {t.accession}",
            )
        if t.r_page and f.reports and t.r_page not in f.reports:
            locator_ok = False
        if t.claimed is not None and t.claimed != f.value:
            part_ok = False
        total += abs(f.value) if len(ts) == 1 and not c.parts else t.sign * f.value
        ev.append(
            f"{'-' if t.sign < 0 else ''}{t.tag}{'[' + t.dims + ']' if t.dims else ''}={f.value}@{f.accession}#{t.r_page} (fsn reports {','.join(f.reports) or '-'})"
        )
    shown = c.value if c.value is not None else Decimal(0)
    if not part_ok or (total != shown if c.parts else abs(total) != abs(shown)):
        return CellCheck(c, "MISMATCH", total, "; ".join(ev))
    return CellCheck(c, "MATCH" if locator_ok else "LOCATOR", total, "; ".join(ev))


@dataclass(frozen=True)
class DebtCheck:
    cell: Cell
    result: str  # MATCH | MISMATCH | REVIEW
    perimeter: Decimal
    evidence: str


def check_debt(c: Cell, facts: list[Fact]) -> DebtCheck:
    """Rebuild total_debt from the cited filing's own facts at the year end: every undimensioned
    face debt-family fact presented on the balance sheet, plus the lease total from the notes
    unless the face debt tags already include leases or carry the lease lines themselves."""
    acc = c.parts[0].accession if c.parts else c.accession
    at = [
        f
        for f in facts
        if f.accession == acc
        and f.qtrs == 0
        and c.period_end
        and _days(f.ddate, c.period_end) <= 7
    ]
    face = {f.tag: f.value for f in at if f.tag in DEBT_FACE_TAGS and f.dims == ""}
    # Prefer totals over their components when the filing prints both.
    if "LongTermDebt" in face and (
        {"LongTermDebtCurrent", "LongTermDebtNoncurrent"} & set(face)
    ):
        face.pop("LongTermDebt")
    if "DebtAndCapitalLeaseObligations" in face and len(face) > 1:
        face = {
            "DebtAndCapitalLeaseObligations": face["DebtAndCapitalLeaseObligations"]
        }
    lease = Decimal(0)
    lease_ev = (
        "leases inside face lines"
        if (set(face) & (LEASE_INCLUSIVE_FACE | LEASE_TAGS))
        else "no lease facts"
    )
    if not set(face) & (LEASE_INCLUSIVE_FACE | LEASE_TAGS):
        tot = [
            f
            for f in at
            if f.tag in ("FinanceLeaseLiability", "CapitalLeaseObligations")
            and f.dims == ""
        ]
        parts = [
            f
            for f in at
            if f.tag
            in LEASE_TAGS - {"FinanceLeaseLiability", "CapitalLeaseObligations"}
        ]
        if tot:
            lease, lease_ev = (
                tot[0].value,
                f"{tot[0].tag}={tot[0].value} ({','.join(tot[0].reports)})",
            )
        elif parts:
            lease = sum(f.value for f in parts)
            lease_ev = "; ".join(f"{f.tag}[{f.dims}]={f.value}" for f in parts)
    perim = sum(face.values(), Decimal(0)) + lease
    ev = f"face {dict(sorted(face.items()))}; lease {lease_ev}"
    if c.value is not None and perim == c.value:
        return DebtCheck(c, "MATCH", perim, ev)
    # A face line outside the debt family (custom tag) or a lease location the facts cannot show
    # needs the approver's eye; a perimeter that is strictly larger than the served value is a fail.
    res = "MISMATCH" if c.value is not None and perim > c.value else "REVIEW"
    return DebtCheck(c, res, perim, ev)


def check_hidden_rows(cells: list[Cell], company_facts: list[Fact]) -> list[Finding]:
    out = []
    hidden = sorted({c.data_point for c in cells if c.display == HIDDEN_ROW})
    for dp in hidden:
        fam = set(HIDE_FAMILY.get(dp, ()))
        if not fam:
            out.append(
                Finding(
                    "hidden_row",
                    dp,
                    "*",
                    "REVIEW",
                    "no tag family on file for this data point: approver checks the filings by hand",
                )
            )
            continue
        hits = [
            f
            for f in company_facts
            if f.tag in fam and f.dims == "" and (f.qtrs == 0) == (dp in INSTANT_DPS)
        ]
        if hits:
            ex = sorted(hits, key=lambda f: f.ddate)[-3:]
            out.append(
                Finding(
                    "hidden_row",
                    dp,
                    "*",
                    "FAIL",
                    f"reported: {len(hits)} undimensioned fact(s), e.g. "
                    + "; ".join(
                        f"{f.tag}={f.value}@{f.accession} {f.ddate} {','.join(f.reports)}"
                        for f in ex
                    ),
                )
            )
        else:
            out.append(
                Finding(
                    "hidden_row",
                    dp,
                    "*",
                    "INFO",
                    f"no undimensioned {sorted(fam)} fact in any periodic filing",
                )
            )
    return out


def check_hidden_years(
    cells: list[Cell], year_ends: dict[str, list[str]]
) -> list[Finding]:
    out = []
    presented = sorted({d for ds in year_ends.values() for d in ds})
    for c in cells:
        if c.display != HIDDEN_YEAR or not c.period_end:
            continue
        near = [d for d in presented if _days(d, c.period_end) <= 7]
        if near:
            out.append(
                Finding(
                    "hidden_year",
                    *c.key,
                    "FAIL",
                    f"a periodic filing presents {near[0]} (comparative or own column): not a pre-filing year",
                )
            )
    return out


def clopper_pearson_upper(k: int, n: int, alpha: float = 0.05) -> float:
    """Exact one-sided upper bound: the p with P(X <= k | n, p) = alpha."""
    if n <= 0:
        return 1.0
    if k >= n:
        return 1.0
    lo, hi = 0.0, 1.0
    for _ in range(100):
        p = (lo + hi) / 2
        cdf = sum(comb(n, i) * p**i * (1 - p) ** (n - i) for i in range(k + 1))
        lo, hi = (p, hi) if cdf > alpha else (lo, p)
    return hi


# ---------------------------------------------------------------- run and verdict
@dataclass
class Run:
    ticker: str
    coverage_path: str
    coverage_sha256: str
    seed: str
    counts: dict[str, int]
    gate: list[Finding] = field(default_factory=list)
    shown: list[CellCheck] = field(default_factory=list)
    debt: list[DebtCheck] = field(default_factory=list)
    hides: list[Finding] = field(default_factory=list)

    @property
    def errors(self) -> int:
        return sum(1 for s in self.shown if s.result in ("MISMATCH", "NOT_FOUND"))

    @property
    def verdict(self) -> str:
        if any(f.severity == "FAIL" for f in self.gate + self.hides):
            return "FAIL"
        if self.errors or any(d.result == "MISMATCH" for d in self.debt):
            return "FAIL"
        if (
            any(s.result == "LOCATOR" for s in self.shown)
            or any(d.result == "REVIEW" for d in self.debt)
            or any(f.severity == "REVIEW" for f in self.hides)
        ):
            return "REVIEW"
        return "PASS"


def sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


@dataclass(frozen=True)
class Plan:
    cells: list[Cell]
    sha: str
    seed: str
    sample: list[Cell]
    debt: list[Cell]
    family_tags: frozenset[str]

    @property
    def debt_acc(self) -> set[str]:
        return {(c.parts[0].accession if c.parts else c.accession) for c in self.debt}


def plan(ticker: str, coverage: Path, seed: str | None = None) -> Plan:
    """Everything the checks will read, decided from the coverage file alone (so an offline bundle
    and a live run look at exactly the same cells)."""
    cells = read_coverage(coverage)
    sha = sha256(coverage)
    seed = seed or f"{ticker}-{sha[:12]}"
    debt = [c for c in cells if c.display == SHOWN and c.data_point == "total_debt"]
    fam = frozenset(
        t
        for dp in {c.data_point for c in cells if c.display == HIDDEN_ROW}
        for t in HIDE_FAMILY.get(dp, ())
    )
    return Plan(cells, sha, seed, draw(cells, seed), debt, fam)


def certify(
    ticker: str, cik: str, coverage: Path, source: FactSource, seed: str | None = None
) -> Run:
    p = plan(ticker, coverage, seed)
    counts: dict[str, int] = defaultdict(int)
    for c in p.cells:
        counts[c.display] += 1
    run = Run(ticker, str(coverage), p.sha, p.seed, dict(counts), gate=gate(p.cells))
    need_tags = (
        {t.tag for c in p.sample for t in terms(c)} | DEBT_FACE_TAGS | LEASE_TAGS
    )
    need_acc = {t.accession for c in p.sample for t in terms(c)} | p.debt_acc
    facts = source.facts(need_acc, need_tags)
    run.shown = [check_cell(c, facts) for c in p.sample]
    run.debt = [check_debt(c, facts) for c in p.debt]
    year_ends = source.periodic_year_ends(cik)
    if not year_ends:
        # A wrong CIK would make every hide look evidenced: refuse instead.
        run.gate.append(
            Finding(
                "gate",
                "*",
                "*",
                "FAIL",
                f"no periodic filing for CIK {cik} in fsn.*: wrong CIK or company not loaded",
            )
        )
        return run
    run.hides = check_hidden_rows(
        p.cells, source.company_facts(cik, p.family_tags) if p.family_tags else []
    )
    if counts.get(HIDDEN_YEAR):
        run.hides += check_hidden_years(p.cells, year_ends)
    return run


def _lit(v: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9_/\-]*", v):
        raise ValueError(f"refusing to inline {v!r}")
    return "'" + v + "'"


def bundle_sql(cik: str, p: Plan, per_tag: int = 3) -> str:
    """One read-only SELECT that returns the evidence bundle as JSON, for running where only a SQL
    console reaches the database. Narrowed to the exact (filing, tag, year end) of each check, so
    the bundle stays small; hidden-row evidence keeps the latest `per_tag` facts of each tag."""
    want = sorted(
        {
            (t.accession, t.tag, c.period_end)
            for c in p.sample
            for t in terms(c)
            if c.period_end
        }
    )
    want += sorted(
        {
            (a, "", c.period_end)
            for c in p.debt
            for a in [c.parts[0].accession if c.parts else c.accession]
        }
    )
    debt_tags = ",".join(_lit(t) for t in sorted(DEBT_FACE_TAGS | LEASE_TAGS))
    vals = (
        ",".join(f"({_lit(a)},{_lit(t)},date {_lit(d)})" for a, t, d in want)
        or "(null,null,null)"
    )
    fam = ",".join(_lit(t) for t in sorted(p.family_tags)) or "null"
    forms = ",".join(_lit(f) for f in PERIODIC_FORMS)
    return f"""set statement_timeout = '30s';
with want(acc, tag, pe) as (values {vals}),
fact as (
  select f.accession, t.tag, v.ddate, v.qtrs, d.segments, v.value, v.filing_id, v.tag_id
  from want w join fsn.filing f on f.accession = w.acc
  join fsn.value v on v.filing_id = f.id and v.ddate between w.pe - 7 and w.pe + 7 and v.coreg is null
  join fsn.tag t on t.id = v.tag_id and (t.tag = w.tag or (w.tag = '' and t.tag in ({debt_tags})))
  join fsn.dim d on d.id = v.dim_id
),
fam as (
  select * from (
    select f.accession, t.tag, v.ddate, v.qtrs, '' as segments, v.value, v.filing_id, v.tag_id,
           row_number() over (partition by t.tag order by v.ddate desc) as rn
    from fsn.filing f join fsn.value v on v.filing_id = f.id and v.coreg is null
    join fsn.dim d on d.id = v.dim_id and d.segments = ''
    join fsn.tag t on t.id = v.tag_id and t.tag in ({fam})
    where ltrim(f.cik, '0') = {_lit(cik.lstrip("0"))} and f.form in ({forms})) x where rn <= {per_tag}
),
ye as (
  select f.accession, array_agg(distinct v.ddate::text) as d
  from fsn.filing f join fsn.value v on v.filing_id = f.id and v.qtrs in (0, 4)
  join fsn.dim d on d.id = v.dim_id and d.segments = ''
  join fsn.tag t on t.id = v.tag_id and t.tag in ('Assets', 'Revenues', 'RevenueFromContractWithCustomerExcludingAssessedTax',
    'NetIncomeLoss', 'NetCashProvidedByUsedInOperatingActivities', 'ProfitLoss')
  where ltrim(f.cik, '0') = {_lit(cik.lstrip("0"))} and f.form in ({forms})
  group by 1
)
select json_build_object(
  'facts', (select coalesce(json_agg(json_build_array(x.accession, x.tag, x.ddate::text, x.qtrs, x.segments, x.value::text,
             (select coalesce(array_agg(distinct 'R' || l.report), '{{}}') from fsn.line l where l.filing_id = x.filing_id and l.tag_id = x.tag_id))), '[]') from fact x),
  'company_facts', (select coalesce(json_agg(json_build_array(x.accession, x.tag, x.ddate::text, x.qtrs, x.segments, x.value::text,
             (select coalesce(array_agg(distinct 'R' || l.report), '{{}}') from fsn.line l where l.filing_id = x.filing_id and l.tag_id = x.tag_id))), '[]') from fam x),
  'year_ends', (select coalesce(json_object_agg(accession, d), '{{}}') from ye)) as bundle"""


def render(run: Run, today: str, approver: str = "Ritwik (cloud), approver") -> str:
    n, k = len(run.shown), run.errors
    ub = clopper_pearson_upper(k, n)
    lines = [
        f"# {run.ticker} display certification ({approver}, {today}): {run.verdict}",
        "",
        f"Coverage `{run.coverage_path}` (sha256 `{run.coverage_sha256}`). Cells by display class: "
        + ", ".join(f"{k_}={v}" for k_, v in sorted(run.counts.items()))
        + f". Seed `{run.seed}`.",
        "Method: CERTIFICATION-METHOD-2026-11-16.md. Each shown value is matched to SEC's Financial Statement and Notes data "
        "set for the cited filing (fsn.*): same tag, period end, duration and dimensions, presented on the cited R page.",
        "",
        "| Check | Result |",
        "|---|---|",
        f"| Gate (no OPEN; value, accession and R page on every shown cell and part; parts sum) | {sum(1 for f in run.gate if f.severity == 'FAIL')} failing |",
        f"| {n} random shown cells | {sum(1 for s in run.shown if s.result == 'MATCH')} match, {k} wrong, {sum(1 for s in run.shown if s.result == 'LOCATOR')} locator only |",
        f"| total_debt census ({len(run.debt)} years) | {sum(1 for d in run.debt if d.result == 'MATCH')} match, {sum(1 for d in run.debt if d.result == 'MISMATCH')} wrong, {sum(1 for d in run.debt if d.result == 'REVIEW')} for review |",
        f"| Hidden rows and years | {sum(1 for f in run.hides if f.severity == 'FAIL')} failing, {sum(1 for f in run.hides if f.severity == 'REVIEW')} for review, {sum(1 for f in run.hides if f.severity == 'INFO')} evidenced |",
        "",
        f"**Bound:** {k} error(s) in {n} random shown cells: Clopper-Pearson 95% upper bound **{ub:.2%}** for {run.ticker} alone "
        "(per-company screen; the 0.10% target is pooled across certified companies in registry.csv).",
        "",
    ]
    bad = [s for s in run.shown if s.result != "MATCH"] + [
        d for d in run.debt if d.result != "MATCH"
    ]
    fails = [f for f in run.gate + run.hides if f.severity in ("FAIL", "REVIEW")]
    if bad or fails:
        lines += ["## Findings", ""]
        for f in fails:
            lines.append(
                f"- **{f.severity}** {f.check} {f.data_point} {f.fiscal_year}: {f.detail}"
            )
        for s in bad:
            filed = s.filing_value if isinstance(s, CellCheck) else s.perimeter
            lines.append(
                f"- **{s.result}** {s.cell.data_point} FY{s.cell.fiscal_year}: served {s.cell.value}, filing {filed}. {s.evidence}"
            )
        lines.append("")
    lines += (
        ["## Hidden rows evidenced", ""]
        + [
            f"- {f.data_point}: {f.detail}"
            for f in run.hides
            if f.severity == "INFO" and f.check == "hidden_row"
        ]
        + [""]
    )
    lines += [
        "## Limits",
        "",
        "- This certifies the evidence for the cells listed; it does not authorize a production write (founder's typed words in the applying session).",
        "- A change to any cell, a proof-version bump that changes a verdict, or a new filing period voids the affected cells until re-sampled.",
        "",
    ]
    return "\n".join(lines)


def evidence_rows(run: Run) -> list[list[str]]:
    rows = [
        ["check", "data_point", "fiscal_year", "result", "served", "filing", "evidence"]
    ]
    for s in run.shown:
        rows.append(
            [
                "shown",
                s.cell.data_point,
                s.cell.fiscal_year,
                s.result,
                str(s.cell.value),
                str(s.filing_value),
                s.evidence,
            ]
        )
    for d in run.debt:
        rows.append(
            [
                "total_debt",
                d.cell.data_point,
                d.cell.fiscal_year,
                d.result,
                str(d.cell.value),
                str(d.perimeter),
                d.evidence,
            ]
        )
    for f in run.gate + run.hides:
        rows.append(
            [f.check, f.data_point, f.fiscal_year, f.severity, "", "", f.detail]
        )
    return rows


REGISTRY_HEADER = [
    "ticker",
    "date",
    "verdict",
    "coverage_sha256",
    "seed",
    "n",
    "errors",
    "upper_bound_95",
    "approver",
]


def pooled_bound(registry: Path) -> tuple[int, int, float]:
    """Pool the random shown draws of every PASS row (latest per ticker)."""
    if not Path(registry).exists():
        return 0, 0, 1.0
    latest: dict[str, dict] = {}
    with open(registry, newline="") as fh:
        for r in csv.DictReader(fh):
            latest[r["ticker"]] = r
    passed = [r for r in latest.values() if r["verdict"] == "PASS"]
    n = sum(int(r["n"]) for r in passed)
    k = sum(int(r["errors"]) for r in passed)
    return n, k, clopper_pearson_upper(k, n)


@dataclass(frozen=True)
class Request:
    ticker: str
    company_id: int
    coverage: str  # repo-relative path
    sha256: str


_REQ_TITLE = re.compile(
    r"^# Certification request: (?P<t>[A-Z.\-]+) \(company (?P<c>\d+)\)", re.MULTILINE
)


def read_request(path: Path) -> Request:
    text = Path(path).read_text()
    m = _REQ_TITLE.search(text)
    cov = re.search(r"coverage csv: `([^`]+)`", text)
    sha = re.search(r"sha256: `([0-9a-f]{64})`", text)
    if not (m and cov and sha):
        raise ValueError(
            f"{path}: not a certification request (needs title, coverage csv and sha256 lines)"
        )
    return Request(m["t"], int(m["c"]), cov[1], sha[1])


def resolve_cik(conn, company_id: int) -> str:
    with conn.cursor() as cur:
        cur.execute("set statement_timeout = 15000")
        cur.execute(
            "select distinct ltrim(cik, '0') from fsn.filing where company_id = %s",
            (company_id,),
        )
        ciks = [r[0] for r in cur.fetchall()]
    if len(ciks) != 1:
        raise ValueError(
            f"company {company_id}: expected one CIK in fsn.filing, found {ciks}"
        )
    return ciks[0]


def to_json(run: Run) -> str:
    return json.dumps(
        {
            "ticker": run.ticker,
            "verdict": run.verdict,
            "coverage_sha256": run.coverage_sha256,
            "seed": run.seed,
            "counts": run.counts,
            "n": len(run.shown),
            "errors": run.errors,
        },
        indent=1,
    )
