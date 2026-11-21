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
PER_SHARE_DPS = frozenset({"basic_eps", "diluted_eps", "dividends_per_share"})
PER_SHARE_CEILING = Decimal(
    1000
)  # above any US per-share EPS or dividend on record (BRK-A excluded)
CONTROL_TAG = "Assets"  # every periodic filer reports it undimensioned
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
# DebtCurrent is the total of these; when it is on the face they are its components, not additions.
CURRENT_DEBT_COMPONENTS = frozenset(
    {
        "ShortTermBorrowings",
        "CommercialPaper",
        "ShortTermDebt",
        "OtherShortTermBorrowings",
        "LongTermDebtCurrent",
        "ConvertibleDebtCurrent",
        "ConvertibleNotesPayableCurrent",
        "SeniorNotesCurrent",
        "LoansPayableCurrent",
        "NotesPayableCurrent",
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
    "cf_inventory_change": ("IncreaseDecreaseInInventories",),
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
    reason_code: str | None = None  # None when the export has no reason_code column
    hide_class: str | None = (
        None  # None when the export has no hide_class column (before main 532fc006)
    )

    @property
    def hide_basis(self) -> str | None:
        """The hide class the checks judge: the export's hide_class when it writes one, else the
        legacy reason_code (which then stays the evidence)."""
        return self.hide_class if self.hide_class is not None else self.reason_code

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
                reason_code=(r["reason_code"] or "").strip()
                if "reason_code" in r
                else None,
                hide_class=(r["hide_class"] or "").strip()
                if "hide_class" in r
                else None,
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
    # Census, not sample: a per-share value no reader could believe fails wherever it sits.
    # STX FY2022 dividends per share (2,770,000) passed a later draw only because it was not drawn.
    for c in cells:
        if (
            c.display == SHOWN
            and c.data_point in PER_SHARE_DPS
            and c.value is not None
            and abs(c.value) > PER_SHARE_CEILING
        ):
            out.append(
                Finding(
                    "gate",
                    *c.key,
                    "FAIL",
                    f"implausible per-share value {c.value} (> {PER_SHARE_CEILING}) from {c.accession}",
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

    def presented_lines(self, cik: str, tags: Iterable[str]) -> dict[str, set[str]]: ...


FACT_SQL = """
select f.accession, t.tag, v.ddate::text, v.qtrs, coalesce(d.segments, '') as segments, v.value,
       coalesce(array_agg(distinct 'R' || l.report) filter (where l.report is not null), '{}') as reports
from fsn.filing f
join fsn.value v on v.filing_id = f.id
join fsn.tag t on t.id = v.tag_id
join fsn.dim d on d.id = v.dim_id
left join fsn.line l on l.filing_id = f.id and l.tag_id = v.tag_id
where f.accession = any(%(acc)s) and t.tag = any(%(tags)s) and coalesce(v.coreg, '') = '' and v.value is not null
group by 1, 2, 3, 4, 5, 6
"""

COMPANY_FACT_SQL = """
select f.accession, t.tag, v.ddate::text, v.qtrs, '' as segments, v.value,
       coalesce(array_agg(distinct 'R' || l.report) filter (where l.report is not null), '{}') as reports
from fsn.filing f
join fsn.value v on v.filing_id = f.id and coalesce(v.coreg, '') = '' and v.value is not null
join fsn.dim d on d.id = v.dim_id and d.segments = ''
join fsn.tag t on t.id = v.tag_id
left join fsn.line l on l.filing_id = f.id and l.tag_id = v.tag_id
where ltrim(f.cik, '0') = ltrim(%(cik)s, '0') and f.form = any(%(forms)s) and t.tag = any(%(tags)s)
group by 1, 2, 3, 4, 5, 6
"""

YEAR_END_SQL = """
select f.accession, array_agg(distinct v.ddate::text || '|' || v.qtrs)
from fsn.filing f join fsn.value v on v.filing_id = f.id and v.qtrs in (0, 4)
join fsn.dim d on d.id = v.dim_id and d.segments = ''
join fsn.tag t on t.id = v.tag_id
where ltrim(f.cik, '0') = ltrim(%(cik)s, '0') and f.form = any(%(forms)s)
  and t.tag in ('Assets', 'Revenues', 'RevenueFromContractWithCustomerExcludingAssessedTax', 'NetIncomeLoss',
                'NetCashProvidedByUsedInOperatingActivities', 'ProfitLoss')
group by 1
"""

# Statement lines a periodic filing presents, whether or not a column holds a value: a printed
# dash has a line and no fact, and it still counts as printed.
PRESENTED_LINES_SQL = """
select f.accession, array_agg(distinct t.tag)
from fsn.filing f join fsn.line l on l.filing_id = f.id
join fsn.tag t on t.id = l.tag_id
where ltrim(f.cik, '0') = ltrim(%(cik)s, '0') and f.form = any(%(forms)s) and t.tag = any(%(tags)s)
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

    def presented_lines(self, cik, tags):
        rows = self._q(
            PRESENTED_LINES_SQL,
            {"cik": cik, "forms": list(PERIODIC_FORMS), "tags": sorted(set(tags))},
        )
        return {acc: set(t) for acc, t in rows}


class BundleFactSource:
    """Offline source: an evidence bundle (JSON) holding the rows of the three queries above."""

    def __init__(self, bundle: dict):
        self.b = bundle

    def facts(self, accessions, tags):
        acc, tg = set(accessions), set(tags)
        return [
            _fact(r)
            for r in self.b.get("facts", [])
            if r[0] in acc and r[1] in tg and r[5] is not None
        ]

    def company_facts(self, cik, tags):
        tg = set(tags)
        return [
            _fact(r)
            for r in self.b.get("company_facts", [])
            if r[1] in tg and r[5] is not None
        ]

    def periodic_year_ends(self, cik):
        return {k: sorted(v) for k, v in self.b.get("year_ends", {}).items()}

    def presented_lines(self, cik, tags):
        tg = set(tags)
        return {k: set(v) & tg for k, v in self.b.get("lines", {}).items()}


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
    if c.data_point in PER_SHARE_DPS and abs(shown) > PER_SHARE_CEILING:
        # Matching the filing is not enough: STX's FY2024 10-K tags FY2022 dividends per share as
        # 2,770,000 (a filer scale error). A shown value no reader could believe is wrong.
        return CellCheck(
            c,
            "MISMATCH",
            total,
            f"implausible per-share value {shown} (> {PER_SHARE_CEILING}); "
            + "; ".join(ev),
        )
    if not part_ok or (total != shown if c.parts else abs(total) != abs(shown)):
        return CellCheck(c, "MISMATCH", total, "; ".join(ev))
    return CellCheck(c, "MATCH" if locator_ok else "LOCATOR", total, "; ".join(ev))


TOTAL_EQUITY_TAGS = (
    "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
    "StockholdersEquity",
)
SHARES_ISSUED_TAGS = ("CommonStockSharesIssued",)
TREASURY_SHARES_TAGS = ("TreasuryStockCommonShares", "TreasuryStockShares")
DERIVED_TAGS = frozenset({*SHARES_ISSUED_TAGS, *TREASURY_SHARES_TAGS}) | frozenset(
    {
        "Assets",
        "LiabilitiesAndStockholdersEquity",
        "MinorityInterest",
        *TOTAL_EQUITY_TAGS,
    }
)


def is_derived(c: Cell) -> bool:
    return not c.tag and not c.parts


def check_derived(c: Cell, cells: list[Cell], facts: list[Fact]) -> CellCheck:
    """A value the filing does not print, computed from printed lines. Only the identities below
    are checked mechanically; any other derived cell goes to the approver."""
    shown = c.value if c.value is not None else Decimal(0)
    if c.data_point == "total_liabilities":
        at = {
            f.tag: f.value
            for f in facts
            if f.accession == c.accession
            and f.qtrs == 0
            and f.dims == ""
            and c.period_end
            and _days(f.ddate, c.period_end) <= 7
            and f.tag in DERIVED_TAGS
        }
        assets = at.get("Assets", at.get("LiabilitiesAndStockholdersEquity"))
        equity = next((at[t] for t in TOTAL_EQUITY_TAGS if t in at), None)
        if assets is None or equity is None:
            return CellCheck(
                c,
                "NOT_FOUND",
                None,
                f"no Assets or total equity fact at {c.period_end} in {c.accession}",
            )
        ev = f"Assets {assets} - total equity incl. NCI {equity} ({', '.join(f'{k}={v}' for k, v in sorted(at.items()))})"
        return CellCheck(
            c, "MATCH" if assets - equity == shown else "MISMATCH", assets - equity, ev
        )
    if c.data_point in ("basic_eps", "diluted_eps"):
        # Founder approvals 2026-11-17 (doc 02, 93c8d6ba): EPS is never derived.
        return CellCheck(
            c,
            "MISMATCH",
            None,
            "EPS is never derived (founder 2026-11-17): it must be the filing's printed EPS",
        )
    if c.data_point == "shares_outstanding":
        # Founder approvals 2026-11-17 (doc 02, 93c8d6ba): shares issued minus treasury shares,
        # both printed in the same filing at the same date.
        at = {
            f.tag: f.value
            for f in facts
            if f.accession == c.accession
            and f.qtrs == 0
            and f.dims == ""
            and c.period_end
            and _days(f.ddate, c.period_end) <= 7
            and f.tag in DERIVED_TAGS
        }
        issued = next((at[t] for t in SHARES_ISSUED_TAGS if t in at), None)
        treasury = next((at[t] for t in TREASURY_SHARES_TAGS if t in at), None)
        if issued is None or treasury is None:
            return CellCheck(
                c,
                "NOT_FOUND",
                None,
                f"no shares issued or treasury shares fact at {c.period_end} in {c.accession}",
            )
        return CellCheck(
            c,
            "MATCH" if issued - treasury == shown else "MISMATCH",
            issued - treasury,
            f"shares issued {issued} - treasury shares {treasury} in {c.accession}",
        )
    if c.data_point == "gross_profit":
        same = {
            x.data_point: x.value
            for x in cells
            if x.fiscal_year == c.fiscal_year and x.display == SHOWN
        }
        rev, cor = same.get("revenue"), same.get("cost_of_revenue")
        if rev is None or cor is None:
            return CellCheck(
                c,
                "NOT_FOUND",
                None,
                "revenue or cost_of_revenue not shown for this year",
            )
        return CellCheck(
            c,
            "MATCH" if rev - abs(cor) == shown else "MISMATCH",
            rev - abs(cor),
            f"shown revenue {rev} - shown cost_of_revenue {cor}",
        )
    return CellCheck(
        c,
        "NOT_FOUND",
        None,
        "derived cell with no tag, parts or known identity: approver checks by hand",
    )


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
    # Face = presented on the balance-sheet page the cell cites. A debt tag that only appears in a
    # note (JNJ DebtCurrent 7,000 beside face ShortTermBorrowings 7,004) is not a face line.
    bs = {p.r_page for p in c.parts if p.r_page} or ({c.r_page} if c.r_page else set())
    face = {
        f.tag: f.value
        for f in at
        if f.tag in DEBT_FACE_TAGS and f.dims == "" and (not bs or bs & set(f.reports))
    }
    # Prefer totals over their components when the filing prints both.
    if "DebtCurrent" in face:
        for t in CURRENT_DEBT_COMPONENTS:
            face.pop(t, None)
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
            lease = sum((f.value for f in parts), Decimal(0))
            lease_ev = "; ".join(f"{f.tag}[{f.dims}]={f.value}" for f in parts)
    perim = sum(face.values(), Decimal(0)) + lease
    ev = f"face {dict(sorted(face.items()))}; lease {lease_ev}"
    if c.value is not None and perim == c.value:
        return DebtCheck(c, "MATCH", perim, ev)
    # A face line outside the debt family (custom tag) or a lease location the facts cannot show
    # needs the approver's eye; a perimeter that is strictly larger than the served value is a fail.
    res = "MISMATCH" if c.value is not None and perim > c.value else "REVIEW"
    return DebtCheck(c, res, perim, ev)


# Hide classes doc 02 allows (founder decision 2026-11-16 and "Display rules under the
# 2026-11-16 founder decision", main 2bc5a106): a line never presented, a line reported only
# combined, a pre-filing year, an allowlisted absence. A hide whose reason is anything else (an
# unmapped era, an unverified reason) is a pipeline gap shown as a hide, and fails.
HIDE_REASONS = frozenset(
    {"structural_not_presented", "line_presented_combined", "only_after_tax_disclosed"}
)
ONLY_COMBINED = "line_presented_combined"


HC_STRUCTURAL = "structural_not_presented"
HC_PRE_FILING = "pre_filing"
HC_VERIFIED_ABSENT = "verified_absent"
# ruling 2026-11-21 (Dhairya): sbc disclosed only after tax is never served as sbc. Like only-combined, the pure
# (pre-tax) line is not printed; a hidden year of this class passes the same printed-line test on the row's own line.
HC_AFTER_TAX = "only_after_tax_disclosed"
HIDE_CLASSES = frozenset(
    {HC_STRUCTURAL, ONLY_COMBINED, HC_PRE_FILING, HC_VERIFIED_ABSENT, HC_AFTER_TAX}
)
# hide classes whose hidden year inside the filing window is judged by the printed-line test, not the allowlist
LINE_NOT_PURE = frozenset({ONLY_COMBINED, HC_AFTER_TAX})


def _hide_fail(c: Cell, why: str) -> Finding:
    return Finding("hide_reason", *c.key, "FAIL", why)


def check_hide_reasons(cells: list[Cell]) -> list[Finding]:
    """Each hide must name a doc 02 hide class. With a hide_class column (main 532fc006) that is
    the class, exactly one of HIDE_CLASSES, and the class must fit the cell; reason_code is evidence only.
    Without it, the legacy reason_code is judged. Whether the class is TRUE is proved elsewhere:
    check_hidden_rows (facts), check_hidden_years (pre-filing, printed lines)."""
    out = []
    for c in cells:
        if c.display not in (HIDDEN_ROW, HIDDEN_YEAR):
            continue
        if c.hide_class is not None:
            hc = c.hide_class
            if hc not in HIDE_CLASSES:
                out.append(
                    _hide_fail(
                        c,
                        f"hide_class {hc or '(none)'!r} is not one of the doc 02 classes",
                    )
                )
            elif hc == HC_PRE_FILING and c.display != HIDDEN_YEAR:
                out.append(
                    _hide_fail(c, "pre_filing applies to a year, not a whole row")
                )
            elif hc == HC_VERIFIED_ABSENT and c.display != HIDDEN_YEAR:
                # doc 02 rule 1 defines it for a year inside the filing window; a row hidden in
                # every year is structural_not_presented (JNJ 2026-11-16 passed this misfit)
                out.append(
                    _hide_fail(
                        c,
                        "verified_absent applies to a year, not a whole row (that is structural_not_presented)",
                    )
                )
            elif hc == HC_VERIFIED_ABSENT and c.data_point not in HIDE_YEAR_ALLOWLIST:
                out.append(
                    _hide_fail(
                        c,
                        f"verified_absent, but {c.data_point} is not on the VERIFIED_ABSENT_HIDE allowlist",
                    )
                )
            continue
        if c.reason_code is None:
            continue
        if c.display == HIDDEN_YEAR and c.reason_code in (
            "",
            "pre_filing",
            "before_first_10k",
        ):
            continue  # a pre-filing year needs no line reason; check_hidden_years proves it
        if c.reason_code not in HIDE_REASONS:
            out.append(
                _hide_fail(
                    c,
                    f"hidden with reason {c.reason_code or '(none)'!r}, which is not a doc 02 hide class "
                    "(never presented, only combined, pre-filing year, allowlisted absence)",
                )
            )
    return out


def check_hidden_rows(cells: list[Cell], company_facts: list[Fact]) -> list[Finding]:
    """A hidden row fails when the company presents a fact of the row's family for one of the
    display years: undimensioned, on a rendered page (a fact no page shows is not reported to a
    reader), annual for a duration row, dated at a fiscal year end in the coverage."""
    out = []
    year_ends = sorted({c.period_end for c in cells if c.period_end})
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
            if f.tag in fam
            and f.dims == ""
            and f.reports
            and f.qtrs == (0 if dp in INSTANT_DPS else 4)
            and any(_days(f.ddate, y) <= 7 for y in year_ends)
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
                    f"no presented, undimensioned, annual {sorted(fam)} fact at a display-year end in any periodic filing",
                )
            )
    return out


# Doc 02, "Display rules under the 2026-11-16 founder decision" (main 2bc5a106), rule 1
# (VERIFIED_ABSENT_HIDE): for these data points a HIDDEN_YEAR is also valid inside the filing
# window when no periodic filing that presents the period prints the row's line (a dash counts as
# printed). Rule 2: a year hidden as reported only combined passes the same printed-line test on
# the row's own (pure) line. Every other hidden year must be a pre-filing year (rule 4).
HIDE_YEAR_ALLOWLIST = frozenset(
    {
        "operating_income",
        "shares_outstanding",
        "share_buybacks",
        "dividends_paid",
        "gross_profit",
        "total_debt",
        "current_assets",
        "current_liabilities",
    }
)
YEAR_HIDE_FAMILY: dict[str, frozenset[str]] = {
    "total_debt": DEBT_FACE_TAGS,
    "current_assets": frozenset({"AssetsCurrent"}),
    "current_liabilities": frozenset({"LiabilitiesCurrent"}),
}


def _year_end(entry: str) -> tuple[str, int | None]:
    """'2019-12-31|4' -> ('2019-12-31', 4); a bare date (older bundles) matches either kind."""
    d, _, q = entry.partition("|")
    return d, (int(q) if q else None)


def row_tags(cells: list[Cell], dp: str) -> frozenset[str]:
    """The tags that print this row: its tag family plus every tag its shown cells cite."""
    tags = set(HIDE_FAMILY.get(dp, ())) | set(YEAR_HIDE_FAMILY.get(dp, ()))
    for c in cells:
        if c.data_point == dp and c.display == SHOWN:
            tags |= {t.tag for t in terms(c) if t.tag}
    return frozenset(tags)


def check_hidden_years(
    cells: list[Cell],
    year_ends: dict[str, list[str]],
    lines: dict[str, set[str]] | None = None,
) -> list[Finding]:
    out = []
    lines = lines or {}
    for c in cells:
        if c.display != HIDDEN_YEAR or not c.period_end:
            continue
        want = 0 if c.data_point in INSTANT_DPS else 4
        presenting = sorted(
            acc
            for acc, ends in year_ends.items()
            if any(
                _days(d, c.period_end) <= 7 and q in (None, want)
                for d, q in map(_year_end, ends)
            )
        )
        if not presenting:
            continue  # a pre-filing year: no periodic filing presents it
        if (
            c.data_point not in HIDE_YEAR_ALLOWLIST
            and c.hide_basis not in LINE_NOT_PURE
        ):
            out.append(
                Finding(
                    "hidden_year",
                    *c.key,
                    "FAIL",
                    f"periodic filing {presenting[0]} presents {c.period_end} (own or comparative column): not a pre-filing year, "
                    f"and {c.data_point} is neither on the hide allowlist nor hidden as reported only combined",
                )
            )
            continue
        tags = row_tags(cells, c.data_point)
        printed = [acc for acc in presenting if lines.get(acc, set()) & tags]
        if printed:
            out.append(
                Finding(
                    "hidden_year",
                    *c.key,
                    "FAIL",
                    f"{printed[0]} presents {c.period_end} and prints the line ({', '.join(sorted(lines[printed[0]] & tags))}); "
                    "a printed value or dash must be shown",
                )
            )
        else:
            out.append(
                Finding(
                    "hidden_year",
                    *c.key,
                    "INFO",
                    f"{'only combined' if c.hide_basis == ONLY_COMBINED else 'only after tax' if c.hide_basis == HC_AFTER_TAX else 'allowlisted'}: {len(presenting)} periodic filing(s) present {c.period_end}, none prints a {c.data_point} line",
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
    cells: list[Cell] = field(default_factory=list)  # every cell of the coverage file

    @property
    def errors(self) -> int:
        return sum(1 for s in self.shown if s.result == "MISMATCH")

    @property
    def verdict(self) -> str:
        if any(f.severity == "FAIL" for f in self.gate + self.hides):
            return "FAIL"
        if self.errors or any(d.result == "MISMATCH" for d in self.debt):
            return "FAIL"
        if (
            any(s.result in ("LOCATOR", "NOT_FOUND") for s in self.shown)
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
    run.cells = p.cells
    run.hides += check_hide_reasons(p.cells)
    need_tags = (
        {t.tag for c in p.sample for t in terms(c)}
        | DEBT_FACE_TAGS
        | LEASE_TAGS
        | DERIVED_TAGS
    )
    need_acc = {t.accession for c in p.sample for t in terms(c)} | p.debt_acc
    facts = source.facts(need_acc, need_tags)
    if (p.sample or p.debt) and not facts:
        # Positive control: the drawn filings always carry facts. None at all means the source
        # or its filters are broken (2026-11-16: a coreg filter matched nothing), never a pass.
        run.gate.append(
            Finding(
                "gate",
                "*",
                "*",
                "FAIL",
                "fact source returned no facts for the drawn filings: source broken",
            )
        )
    run.shown = [
        check_derived(c, p.cells, facts) if is_derived(c) else check_cell(c, facts)
        for c in p.sample
    ]
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
    company = source.company_facts(cik, p.family_tags | {CONTROL_TAG})
    if not any(f.tag == CONTROL_TAG for f in company):
        # Positive control for the hide checks: without it an empty result would read as
        # "never reported" for every hidden row.
        run.gate.append(
            Finding(
                "gate",
                "*",
                "*",
                "FAIL",
                f"company fact query returned no {CONTROL_TAG} control fact: source broken",
            )
        )
        return run
    run.hides += check_hidden_rows(
        p.cells, [f for f in company if f.tag != CONTROL_TAG]
    )
    if counts.get(HIDDEN_YEAR):
        allow = {
            c.data_point
            for c in p.cells
            if c.display == HIDDEN_YEAR
            and (c.data_point in HIDE_YEAR_ALLOWLIST or c.hide_basis in LINE_NOT_PURE)
        }
        lines: dict[str, set[str]] = {}
        if allow:
            tags = frozenset().union(*(row_tags(p.cells, dp) for dp in allow)) | {
                CONTROL_TAG
            }
            lines = source.presented_lines(cik, tags)
            if not any(CONTROL_TAG in t for t in lines.values()):
                # Positive control: every periodic filing presents an Assets line.
                run.gate.append(
                    Finding(
                        "gate",
                        "*",
                        "*",
                        "FAIL",
                        f"presented-lines query returned no {CONTROL_TAG} line: source broken",
                    )
                )
                return run
        run.hides += check_hidden_years(p.cells, year_ends, lines)
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
    fam = ",".join(_lit(t) for t in sorted(p.family_tags | {CONTROL_TAG}))
    forms = ",".join(_lit(f) for f in PERIODIC_FORMS)
    return f"""set statement_timeout = '30s';
with want(acc, tag, pe) as (values {vals}),
fact as (
  select f.accession, t.tag, v.ddate, v.qtrs, d.segments, v.value, v.filing_id, v.tag_id
  from want w join fsn.filing f on f.accession = w.acc
  join fsn.value v on v.filing_id = f.id and v.ddate between w.pe - 7 and w.pe + 7 and coalesce(v.coreg, '') = '' and v.value is not null
  join fsn.tag t on t.id = v.tag_id and (t.tag = w.tag or (w.tag = '' and t.tag in ({debt_tags})))
  join fsn.dim d on d.id = v.dim_id
),
fam as (
  select * from (
    select f.accession, t.tag, v.ddate, v.qtrs, '' as segments, v.value, v.filing_id, v.tag_id,
           row_number() over (partition by t.tag order by v.ddate desc) as rn
    from fsn.filing f join fsn.value v on v.filing_id = f.id and coalesce(v.coreg, '') = '' and v.value is not null
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
    allowed = [
        f for f in run.hides if f.severity == "INFO" and f.check == "hidden_year"
    ]
    if allowed:
        lines += (
            ["## Hidden years evidenced (allowlist)", ""]
            + [f"- {f.data_point} FY{f.fiscal_year}: {f.detail}" for f in allowed]
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
    detector_version: str | None = None  # "proof DETECTOR_VERSION" line
    resolver: str | None = None  # "resolver" line (repo path)
    code_sha: str | None = None  # "code" line (git sha the export was built from)


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

    def line(name: str) -> str | None:
        hit = re.search(rf"^- {name}: `([^`]+)`", text, re.MULTILINE)
        return hit[1] if hit else None

    return Request(
        m["t"],
        int(m["c"]),
        cov[1],
        sha[1],
        detector_version=line("proof DETECTOR_VERSION"),
        resolver=line("resolver"),
        code_sha=line("code"),
    )


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


# ---------------------------------------------------------------- machine-readable certificate
CERTIFICATE_SCHEMA = "display-certificate/1"
CERTIFICATE_SCHEMA_PATH = (
    Path(__file__).parent / "schemas" / "display_certificate.v1.schema.json"
)


def _grain(dp: str) -> str:
    """analytics.cell_display_state grain (0130): 'I' instant, 'FY' annual duration."""
    return "I" if dp in INSTANT_DPS else "FY"


def certificate(
    run: Run, req: Request | None, certified_at: str, approver: str
) -> dict:
    """The certificate as data (schema display-certificate/1), one entry per cell of the coverage
    file. evidence: drawn = individually matched to the filing; census = every total_debt year and
    every hidden cell's hide proof; sampled = covered by the bound, not individually checked."""
    drawn = {s.cell.key: s for s in run.shown}
    debt = {d.cell.key: d for d in run.debt}
    row_hide = {f.data_point: f for f in run.hides if f.check == "hidden_row"}
    year_hide = {
        (f.data_point, f.fiscal_year): f for f in run.hides if f.check == "hidden_year"
    }
    reason_fail = {
        (f.data_point, f.fiscal_year): f for f in run.hides if f.check == "hide_reason"
    }
    gate_fail = {(f.data_point, f.fiscal_year): f for f in run.gate}
    cells = []
    for c in run.cells:
        if c.key in drawn:
            ev, res, why = "drawn", drawn[c.key].result, drawn[c.key].evidence
        elif c.key in debt:
            ev, res, why = "census", debt[c.key].result, debt[c.key].evidence
        elif c.display in (HIDDEN_ROW, HIDDEN_YEAR):
            f = reason_fail.get(c.key) or (
                row_hide.get(c.data_point)
                if c.display == HIDDEN_ROW
                else year_hide.get(c.key)
            )
            ev = "census"
            if f is None:  # a hidden year that no periodic filing presents
                res, why = (
                    "MATCH",
                    "pre-filing year: no periodic filing presents this period",
                )
            else:
                res, why = (
                    {"INFO": "MATCH", "FAIL": "MISMATCH"}.get(f.severity, "REVIEW"),
                    f.detail,
                )
        elif c.display == SHOWN:
            ev, res, why = (
                "sampled",
                "SAMPLED",
                "covered by the certificate's bound; not individually checked",
            )
        else:
            ev, res, why = "census", "MISMATCH", "OPEN cell"
        if c.key in gate_fail:
            res, why = "MISMATCH", gate_fail[c.key].detail
        cells.append(
            {
                "data_point": c.data_point,
                "fiscal_year": c.fiscal_year,
                "period_end": c.period_end,
                "grain": _grain(c.data_point),
                "display": c.display,
                "hide_class": c.hide_class or None,
                "reason_code": c.reason_code or None,
                "shown_value": None if c.value is None else str(c.value),
                "accession": c.accession or None,
                "r_page": c.r_page or None,
                "tag": c.tag or None,
                "parts": [
                    {
                        "tag": x.tag,
                        "dims": x.dims,
                        "value": str(x.value),
                        "sign": x.sign,
                        "accession": x.accession,
                        "r_page": x.r_page,
                    }
                    for x in c.parts
                ],
                "evidence": ev,
                "result": res,
                "detail": why,
            }
        )
    n, k = len(run.shown), run.errors
    return {
        "schema": CERTIFICATE_SCHEMA,
        "ticker": run.ticker,
        "company_id": req.company_id if req else None,
        "verdict": run.verdict,
        "coverage_path": req.coverage if req else run.coverage_path,
        "coverage_sha256": run.coverage_sha256,
        "sample_hash": run.coverage_sha256,
        "seed": run.seed,
        "detector_version": req.detector_version if req else None,
        "resolver": req.resolver if req else None,
        "code_sha": req.code_sha if req else None,
        "method": "data-team/strategy/approvals/CERTIFICATION-METHOD-2026-11-16.md",
        "approver": approver,
        "certified_at": certified_at,
        "counts": dict(sorted(run.counts.items())),
        "bound": {
            "n": n,
            "errors": k,
            "upper_95": f"{clopper_pearson_upper(k, n):.6f}",
        },
        "gate": [
            {
                "data_point": f.data_point,
                "fiscal_year": f.fiscal_year,
                "severity": f.severity,
                "detail": f.detail,
            }
            for f in run.gate
        ],
        "cells": cells,
    }
