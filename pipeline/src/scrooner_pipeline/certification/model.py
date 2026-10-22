"""Data model shared by the invariant modules. Pure: no database access."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal

from scrooner_pipeline.common.periodic_forms import PERIODIC_FORMS_ALL

WRONG_VALUE = "wrong_value"
REVIEW = "review"
# Counted and shown in the report but NOT stored (the 0097 table only allows
# wrong_value|review): a non-authoritative source that is a recorded conflict fill.
INFO = "info"

INVARIANTS = ("I1", "I2", "I3", "I4", "I5", "I6", "I7", "I8", "I9", "I10", "I11")

# Forms whose financial-statement facts may be displayed (data-team/34 I6).
# Same list as common/staleness.PERIODIC_FORMS; kept as a tuple of the facts'
# form text. DEF 14A / 8-K / S-1 / 424B are never a source for a statement value.
PERIODIC_FORMS = PERIODIC_FORMS_ALL


def base_name(concept: str) -> str:
    """Base canonical concept for a stored name: `x_resolved` -> `x`, and the
    revenue resolution layer `revenue_sanity_resolved` -> `revenue`."""
    if concept == "revenue_sanity_resolved":
        return "revenue"
    if concept.endswith("_resolved"):
        return concept[: -len("_resolved")]
    return concept


def is_resolved(concept: str) -> bool:
    return concept.endswith("_resolved")


@dataclass(frozen=True)
class Cell:
    """One analytics.canonical_fact row with its period."""

    concept: str  # name as stored (may end with _resolved)
    value: Decimal
    period_id: int
    start: date | None
    end: date
    period_type: str | None  # 'duration' | 'instant'
    fiscal_year: int | None
    fiscal_period: str | None
    source_ids: tuple[int, ...] = ()

    @property
    def base(self) -> str:
        return base_name(self.concept)

    @property
    def resolved(self) -> bool:
        return is_resolved(self.concept)

    @property
    def days(self) -> int | None:
        """Length of a duration period in days (end - start); None for an instant."""
        if self.start is None or self.period_type == "instant":
            return None
        return (self.end - self.start).days


@dataclass(frozen=True)
class Source:
    """One core.fact row a canonical value was built from."""

    id: int
    tag: str
    value: Decimal
    authoritative: bool
    derived: bool
    form: str | None
    unit: str | None
    accession: str | None = None
    filing_date: date | None = None
    start: date | None = None
    end: date | None = None


@dataclass(frozen=True)
class ComponentFact:
    """An authoritative core.fact the checks read directly by tag (debt
    components, balance-sheet adjustments)."""

    id: int
    tag: str
    value: Decimal
    period_id: int
    end: date


@dataclass(frozen=True)
class Metric:
    """A displayed analytics.metric_value row (latest per metric and label class)."""

    name: str
    label: str | None
    period_end: date
    value: Decimal
    requires_price: bool = False
    source_ids: tuple[int, ...] = ()


@dataclass(frozen=True)
class GapRow:
    """One analytics.period_gap row (a missing cell with its classified cause)."""

    concept: str  # name as stored in period_gap (may end with _resolved)
    kind: str  # 'FY' | 'Q' | 'Q4' | 'I'
    end: date
    cause: str

    @property
    def base(self) -> str:
        return base_name(self.concept)


@dataclass(frozen=True)
class MetricCell:
    """One analytics.metric_value row of the history window (label FY or Q1..Q4)."""

    name: str
    label: str
    end: date
    value: Decimal | None
    reason: str | None


@dataclass(frozen=True)
class MetricSpec:
    """One active metric from analytics.metric_definition and its inputs
    (analytics.metric_definition_input). I11 reads the metric's period kinds and
    lookback from this registry text, never from a hard-coded list."""

    name: str
    description: str
    requires_price: bool = False
    inputs: tuple[str, ...] = ()  # input concept names as stored
    input_statements: tuple[str, ...] = ()  # statement of each input, same order


@dataclass
class CompanyData:
    company_id: int
    cik: str = ""
    ticker: str | None = None
    sic: str | None = None
    cells: list[Cell] = field(default_factory=list)
    sources: dict[int, Source] = field(default_factory=dict)
    # authoritative copies of the same (company, tag, period, unit) keyed by the
    # id of the NON-authoritative source fact they are copies of
    authoritative_copies: dict[int, list[Source]] = field(default_factory=dict)
    # copies of a non-periodic-form source (DEF 14A, 8-K) filed on a 10-K/10-Q-family form,
    # any authority, keyed by the id of the non-periodic source: the stored value is
    # compared with them (I6 non_periodic_form)
    periodic_copies: dict[int, list[Source]] = field(default_factory=dict)
    # accession -> number of facts the filing carries (8-K sources only): a recast 8-K
    # holds complete restated statements (hundreds of facts), an earnings release or a
    # proxy holds a handful
    filing_fact_counts: dict[str, int] = field(default_factory=dict)
    # (base concept, us-gaap tag) -> (mapping priority, confidence), analytics.concept_mapping
    tag_roles: dict[tuple[str, str], tuple[int, str]] = field(default_factory=dict)
    # other NON-authoritative copies of the same (company, tag, period, unit), keyed by source id
    conflict_copies: dict[int, list[Source]] = field(default_factory=dict)
    # consumed base concept -> distinct (start, end) of every fact (any authority) under a tag
    # mapped to it (analytics.concept_mapping, not 'rejected'): I11 cause evidence
    mapped_facts: dict[str, list[tuple[date | None, date]]] = field(
        default_factory=dict
    )
    mapped_tag_count: dict[str, int] = field(default_factory=dict)
    debt_facts: list[ComponentFact] = field(default_factory=list)
    adjustment_facts: list[ComponentFact] = field(default_factory=list)
    metrics: list[Metric] = field(default_factory=list)
    concept_modes: dict[str, str] = field(
        default_factory=dict
    )  # name -> combination_mode
    latest_filed: date | None = None
    splits: list[tuple[date, Decimal]] = field(default_factory=list)
    is_bank: bool = False
    bank_sic_without_evidence: bool = False
    bank_evidence_without_sic: bool = False
    price: tuple[date, Decimal] | None = None
    shares_fallback_filed: date | None = None
    as_of: date = field(default_factory=date.today)
    # I11 inputs
    filings: list[tuple[date, str]] = field(
        default_factory=list
    )  # (period_of_report, form), periodic forms, in window
    first_filing_period: date | None = (
        None  # earliest periodic filing ever (not window-limited)
    )
    period_gaps: list[GapRow] = field(default_factory=list)
    metric_history: list[MetricCell] = field(default_factory=list)
    metric_specs: dict[str, MetricSpec] = field(default_factory=dict)
    # metric name -> period kinds ('FY'|'Q') any company of the loaded chunk has a row for
    metric_kinds_seen: dict[str, set[str]] = field(default_factory=dict)
    # earliest period end of any canonical value of this company, not window-limited
    first_data_period: date | None = None
    consumed: dict[str, str] = field(
        default_factory=dict
    )  # consumed concept name -> statement
    window_start: date = date(2015, 1, 1)

    def cells_for(self, concept: str) -> list[Cell]:
        return [c for c in self.cells if c.concept == concept]

    def display_cells(self) -> list[Cell]:
        """The value a reader sees per (base concept, period): the `_resolved`
        row when one exists for that period, else the base row. Mirrors the
        display layer of sanity/accounting_identity."""
        resolved = {(c.base, c.period_id) for c in self.cells if c.resolved}
        return [
            c for c in self.cells if c.resolved or (c.base, c.period_id) not in resolved
        ]

    def display_by_concept(self) -> dict[str, list[Cell]]:
        out: dict[str, list[Cell]] = {}
        for c in self.display_cells():
            out.setdefault(c.base, []).append(c)
        for cells in out.values():
            cells.sort(key=lambda c: (c.end, c.start or c.end))
        return out

    def source_facts(self, cell: Cell) -> list[Source]:
        return [self.sources[i] for i in cell.source_ids if i in self.sources]


@dataclass
class Finding:
    company_id: int
    invariant: str
    severity: str
    data_point_name: str
    period_end: date | None
    stored_value: Decimal | None
    expected_or_other_value: Decimal | None
    evidence: dict
    source_fact_ids: list[int] = field(default_factory=list)

    def key(self) -> tuple:
        return (
            self.invariant,
            self.data_point_name,
            self.period_end,
            self.evidence.get("rule"),
        )


def finding(
    data: CompanyData,
    invariant: str,
    severity: str,
    rule: str,
    cell_or_name: Cell | str,
    *,
    stored: Decimal | None = None,
    other: Decimal | None = None,
    period_end: date | None = None,
    source_ids: list[int] | tuple[int, ...] = (),
    **evidence,
) -> Finding:
    """Build a Finding; `cell_or_name` is the offending Cell (name, period and
    value are taken from it) or a plain data-point name."""
    if isinstance(cell_or_name, Cell):
        name = cell_or_name.concept
        period_end = period_end or cell_or_name.end
        stored = cell_or_name.value if stored is None else stored
        if not source_ids:
            source_ids = cell_or_name.source_ids
    else:
        name = cell_or_name
    return Finding(
        company_id=data.company_id,
        invariant=invariant,
        severity=severity,
        data_point_name=name,
        period_end=period_end,
        stored_value=stored,
        expected_or_other_value=other,
        evidence={"rule": rule, **evidence},
        source_fact_ids=[int(i) for i in source_ids],
    )


# ---- shared concept sets (names come from analytics.canonical_concept; they
# were read from the registry on 2026-10-21, none is assumed) -----------------

ADDITIVE_FLOWS = frozenset(
    {
        "revenue",
        "cost_of_revenue",
        "gross_profit",
        "operating_expenses",
        "operating_income",
        "net_income",
        "income_before_tax",
        "income_tax_expense",
        "interest_expense",
        "cfo",
        "capex",
        "cash_flow_investing",
        "cash_flow_financing",
        "dividends_paid",
        "share_buybacks",
        "sbc",
        "depreciation_and_amortization",
        "sga_expense",
        "research_and_development",
    }
)

PER_SHARE = frozenset({"diluted_eps", "basic_eps", "dividends_per_share"})
SHARE_COUNTS = frozenset({"shares_outstanding"})
# Not monetary in USD: excluded from unit-family and USD scale checks.
NON_MONETARY = frozenset({"employee_count", "effective_tax_rate_reported"})
NON_ADDITIVE_DERIVED = (
    PER_SHARE | SHARE_COUNTS | {"effective_tax_rate_reported", "employee_count"}
)


def expected_unit(base: str) -> str | None:
    """Unit family a stored value of this base concept must come from, or None
    when no unit rule applies. Unit names are lower-case in core.unit."""
    if base in PER_SHARE:
        return "usd/shares"
    if base in SHARE_COUNTS:
        return "shares"
    if base in NON_MONETARY:
        return None
    return "usd"


def power_of_ten_signature(ratio: Decimal) -> bool:
    """True when `ratio` (> 0) is within -15%/+18% of 10^3, 10^6 or 10^9 (or their
    inverses): the shape of a thousands/millions scale error."""
    if ratio <= 0:
        return False
    for k in (3, 6, 9):
        p = Decimal(10) ** k
        for r in (ratio / p, ratio * p):
            if Decimal("0.85") <= r <= Decimal("1.18"):
                return True
    return False
