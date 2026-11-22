"""Load and validate the metric registry (registry/*.csv, one file per family).

REGISTRY_VERSION is a hash of the metric files' names and bytes: any edit to any
row changes it.

registry/data_points.csv is the one definition table for the display data points (one row per
data point x sector template: standard definition, fallback order with a badge per step, sector
applicability, filter note; founder decision 2026-11-22). It is not a metric file: load it with
load_data_points(); DATA_POINTS_VERSION hashes it alone. A metric's own `version` is bumped by hand when its published formula
changes meaning; `formula_ref` is `metric_id@version`.
"""

from __future__ import annotations

import csv
import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path

from scrooner_pipeline.metrics import expr

REGISTRY_DIR = Path(__file__).parent / "registry"
TIERS = {"v1_locked", "expanded", "planned"}
STATUSES = {"engine_wired", "growth_wired", "described", "procedural", "planned"}
APPLIES_TO = {"all", "corporate", "bank", "insurer", "bank,lender"}
VALUE_TYPES = {"percentage", "currency", "multiple", "number"}
COLUMNS = [
    "metric_id",
    "version",
    "tier",
    "family",
    "label",
    "short_definition",
    "value_type",
    "unit",
    "formula_description",
    "expression",
    "expression_status",
    "seed_inputs",
    "calculator",
    "period_rule",
    "ttm_rows",
    "null_rules",
    "requires_price",
    "quarterly_needs_ttm",
    "bank_reason",
    "applies_to",
    "perimeter",
    "perimeter_spec",
    "notes",
]


class RegistryError(ValueError):
    pass


DATA_POINTS_FILE = "data_points.csv"
DATA_POINT_COLUMNS = [
    "data_point",
    "sector",
    "applies",
    "statement",
    "standard_definition",
    "fallback_order",
    "badges",
    "inputs_one_filing",
    "never_derive",
    "not_applicable_reason",
    "filter_note",
    "rulings",
]
# mapper/sector_templates.py sic_group() values (+ the bdc company assignment).
SECTORS = (
    "general",
    "bank",
    "lender",
    "broker_am",
    "insurer",
    "equity_reit",
    "utility",
    "bdc",
)
DATA_POINT_STATEMENTS = {"income_statement", "balance_sheet", "cash_flow"}
# Badge vocabulary, one per fallback step. A shown cell carries the badge of the step that
# produced it: as_printed (face line, undimensioned note fact or quoted text), combined:<what the
# printed line also holds>, derived:<formula over printed lines of ONE filing>, perimeter:<how the
# inputs' perimeter differs>. Cell states that carry no value are not badges: not_applicable
# (applies = no), not_disclosed (no filing prints the figure or its inputs) and included_in:<dp>
# (one printed line holds two template data points: it serves the one its label names first; the
# other cell is a filter-exclusion reason, never a blank or zero; Dhairya 2026-11-22).
BADGE_KINDS = ("as_printed", "combined:", "derived:", "perimeter:")
CELL_STATES = ("not_applicable", "not_disclosed", "included_in:")


@dataclass(frozen=True)
class Metric:
    metric_id: str
    version: int
    tier: str
    family: str
    label: str
    short_definition: str
    value_type: str
    unit: str
    formula_description: str
    expression: str
    expression_status: str
    seed_inputs: tuple[tuple[str, str], ...]
    calculator: str
    period_rule: str
    ttm_rows: bool
    null_rules: dict[str, str]
    requires_price: bool
    quarterly_needs_ttm: bool | None
    bank_reason: str
    applies_to: str
    perimeter: tuple[str, ...]
    perimeter_spec: dict[str, str]
    notes: str
    source_file: str = ""
    _ast: object = field(default=None, repr=False, compare=False)

    @property
    def formula_ref(self) -> str:
        return f"{self.metric_id}@{self.version}"

    @property
    def ast(self):
        return self._ast

    def classification(self):
        """(shape, [(concept, role)]) for a generic-engine metric, else None."""
        return expr.classify(self._ast) if self._ast is not None else None

    def input_roles(self) -> list[tuple[str, str]]:
        """The (concept, role) rows seeded into analytics.metric_definition_input."""
        cls = (
            self.classification() if self.expression_status == "engine_wired" else None
        )
        return list(cls[1]) if cls else list(self.seed_inputs)

    @property
    def shape(self) -> str | None:
        cls = (
            self.classification() if self.expression_status == "engine_wired" else None
        )
        return cls[0] if cls else None

    @property
    def fy_only(self) -> bool:
        return self.period_rule == "fy_only"

    @property
    def zero_when_absent(self) -> frozenset[str]:
        v = self.null_rules.get("zero_when_absent", "")
        return frozenset(x for x in v.split(",") if x)


def _yes(v: str, where: str) -> bool:
    if v == "yes":
        return True
    if v in ("no", ""):
        return False
    raise RegistryError(f"{where}: expected yes/no, got {v!r}")


def _null_rules(raw: str, where: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for tok in filter(None, raw.split(";")):
        key, sep, val = tok.partition("=")
        if not sep or key not in {
            "div0",
            "floor",
            "zero_when_absent",
            "growth_base",
            "neg",
        }:
            raise RegistryError(f"{where}: bad null rule {tok!r}")
        out[key] = val
    return out


def _perimeter_spec(raw: str, where: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for tok in filter(None, raw.split(";")):
        key, sep, val = tok.partition("=")
        if not sep or not key or not val:
            raise RegistryError(f"{where}: bad perimeter_spec item {tok!r}")
        out[key] = val
    return out


def _seed_inputs(raw: str, where: str) -> tuple[tuple[str, str], ...]:
    out = []
    for tok in filter(None, raw.split(";")):
        c, sep, r = tok.partition(":")
        if not sep or not c or not r:
            raise RegistryError(f"{where}: bad seed input {tok!r}")
        out.append((c, r))
    return tuple(out)


def registry_files(directory: Path | None = None) -> list[Path]:
    """The metric family files (every registry CSV except the data-point table)."""
    return sorted(
        p
        for p in (directory or REGISTRY_DIR).glob("*.csv")
        if p.name != DATA_POINTS_FILE
    )


def compute_registry_version(directory: Path | None = None) -> str:
    h = hashlib.sha256()
    for p in registry_files(directory):
        h.update(p.name.encode() + b"\0" + p.read_bytes() + b"\0")
    return h.hexdigest()[:16]


def unknown_identifiers(
    metrics: dict[str, Metric], concept_names: set[str]
) -> dict[str, list[str]]:
    """Identifiers in expressions that are neither a canonical concept (a `<name>_resolved`
    concept follows its base name), another metric, nor reserved. Checked in tests against
    data-team/47-fsn-store/company_tag_map/concepts_catalog.csv, not at load time, because the
    concept list is data owned by the mapper."""
    ok = set(concept_names) | set(metrics) | expr.RESERVED_NAMES
    bad: dict[str, list[str]] = {}
    for m in metrics.values():
        if m.ast is None:
            continue
        for n in expr.names(m.ast):
            base = n[: -len("_resolved")] if n.endswith("_resolved") else n
            if n not in ok and base not in ok:
                bad.setdefault(m.metric_id, []).append(n)
    return bad


def load_registry(
    directory: Path | None = None, *, validate: bool = True
) -> dict[str, Metric]:
    metrics: dict[str, Metric] = {}
    for path in registry_files(directory):
        with path.open(newline="") as fh:
            reader = csv.DictReader(fh)
            if reader.fieldnames != COLUMNS:
                raise RegistryError(
                    f"{path.name}: columns {reader.fieldnames} != {COLUMNS}"
                )
            for i, row in enumerate(reader, start=2):
                where = f"{path.name}:{i}"
                mid = row["metric_id"]
                if mid in metrics:
                    raise RegistryError(f"{where}: duplicate metric {mid}")
                text = row["expression"]
                ast = expr.parse(text) if text else None
                try:
                    version = int(row["version"])
                except ValueError as exc:
                    raise RegistryError(f"{where}: version must be an integer") from exc
                qtt = row["quarterly_needs_ttm"]
                metrics[mid] = Metric(
                    metric_id=mid,
                    version=version,
                    tier=row["tier"],
                    family=row["family"],
                    label=row["label"],
                    short_definition=row["short_definition"],
                    value_type=row["value_type"],
                    unit=row["unit"],
                    formula_description=row["formula_description"],
                    expression=text,
                    expression_status=row["expression_status"],
                    seed_inputs=_seed_inputs(row["seed_inputs"], where),
                    calculator=row["calculator"],
                    period_rule=row["period_rule"],
                    ttm_rows=_yes(row["ttm_rows"], where),
                    null_rules=_null_rules(row["null_rules"], where),
                    requires_price=_yes(row["requires_price"], where),
                    quarterly_needs_ttm=None if qtt == "" else _yes(qtt, where),
                    bank_reason=row["bank_reason"],
                    applies_to=row["applies_to"],
                    perimeter_spec=_perimeter_spec(row["perimeter_spec"], where),
                    perimeter=tuple(x for x in row["perimeter"].split(";") if x),
                    notes=row["notes"],
                    source_file=path.name,
                    _ast=ast,
                )
    if validate:
        validate_registry(metrics)
    return metrics


def validate_registry(metrics: dict[str, Metric]) -> None:
    problems: list[str] = []
    for m in metrics.values():
        w = m.metric_id
        if m.version < 1:
            problems.append(f"{w}: version < 1")
        if m.tier not in TIERS:
            problems.append(f"{w}: tier {m.tier!r}")
        if m.expression_status not in STATUSES:
            problems.append(f"{w}: expression_status {m.expression_status!r}")
        if m.value_type not in VALUE_TYPES:
            problems.append(f"{w}: value_type {m.value_type!r}")
        for col in (
            "label",
            "short_definition",
            "family",
            "unit",
            "formula_description",
            "calculator",
            "period_rule",
        ):
            if not getattr(m, col).strip():
                problems.append(
                    f"{w}: {col} is empty (no metric may fall back to generic presentation)"
                )
        if m.applies_to not in APPLIES_TO:
            problems.append(f"{w}: applies_to {m.applies_to!r}")
        if m.expression_status in ("procedural", "planned"):
            if m.expression:
                problems.append(f"{w}: procedural metric must not carry an expression")
        else:
            if not m.expression:
                problems.append(f"{w}: {m.expression_status} needs an expression")
        if m.expression_status == "engine_wired":
            if m.classification() is None:
                problems.append(
                    f"{w}: engine_wired expression is not one of the six generic shapes"
                )
            if m.seed_inputs:
                problems.append(
                    f"{w}: engine_wired derives its inputs; seed_inputs must be empty"
                )
        if m.expression_status == "growth_wired":
            if not (isinstance(m.ast, expr.Call) and m.ast.func == "growth"):
                problems.append(f"{w}: growth_wired must be growth(name, n)")
        if m.bank_reason and m.bank_reason not in {
            "not applicable to banks",
            "bank revenue definition pending",
            "bank net interest income mapping pending",
        }:
            problems.append(f"{w}: unknown bank_reason {m.bank_reason!r}")
    if problems:
        raise RegistryError("; ".join(problems))


@dataclass(frozen=True)
class DataPointDefinition:
    data_point: str
    sector: str
    applies: bool
    statement: str
    standard_definition: str
    fallback_order: tuple[str, ...]
    badges: tuple[str, ...]
    inputs_one_filing: bool
    never_derive: bool
    not_applicable_reason: str
    filter_note: str
    rulings: str


def _badge_ok(b: str) -> bool:
    if b == "as_printed":
        return True
    kind, sep, what = b.partition(":")
    return bool(sep) and f"{kind}:" in BADGE_KINDS[1:] and bool(what.strip())


def load_data_points(
    directory: Path | None = None,
) -> dict[tuple[str, str], DataPointDefinition]:
    """registry/data_points.csv keyed by (data_point, sector); every rule is checked on load."""
    path = (directory or REGISTRY_DIR) / DATA_POINTS_FILE
    out: dict[tuple[str, str], DataPointDefinition] = {}
    problems: list[str] = []
    with path.open(newline="") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames != DATA_POINT_COLUMNS:
            raise RegistryError(
                f"{path.name}: columns {reader.fieldnames} != {DATA_POINT_COLUMNS}"
            )
        for i, row in enumerate(reader, start=2):
            w = f"{path.name}:{i}"
            key = (row["data_point"], row["sector"])
            if key in out:
                problems.append(f"{w}: duplicate {key}")
            if row["sector"] not in SECTORS:
                problems.append(f"{w}: sector {row['sector']!r}")
            if row["statement"] not in DATA_POINT_STATEMENTS:
                problems.append(f"{w}: statement {row['statement']!r}")
            try:
                applies = _yes(row["applies"], w)
                one = _yes(row["inputs_one_filing"], w)
                never = _yes(row["never_derive"], w)
            except RegistryError as exc:
                problems.append(str(exc))
                continue
            steps = tuple(
                x.strip() for x in row["fallback_order"].split(" > ") if x.strip()
            )
            badges = tuple(x.strip() for x in row["badges"].split("|") if x.strip())
            if not row["standard_definition"].strip():
                problems.append(f"{w}: standard_definition is empty")
            if not steps or len(steps) != len(badges):
                problems.append(
                    f"{w}: {len(steps)} fallback steps but {len(badges)} badges"
                )
            if (
                badges
                and badges[0] != "as_printed"
                and not badges[0].startswith("derived:sum(")
            ):
                problems.append(
                    f"{w}: the first step must be the printed line (as_printed)"
                )
            for b in badges:
                if not _badge_ok(b):
                    problems.append(f"{w}: badge {b!r} not in {BADGE_KINDS}")
            if never and any(b.startswith(("derived:", "perimeter:")) for b in badges):
                problems.append(f"{w}: never_derive data point has a derived step")
            if not one:
                problems.append(
                    f"{w}: inputs_one_filing must be yes (no two-filing derivation)"
                )
            if applies == bool(row["not_applicable_reason"].strip()):
                problems.append(
                    f"{w}: not_applicable_reason must be set exactly when applies = no"
                )
            if applies and not row["filter_note"].strip():
                problems.append(f"{w}: filter_note is empty")
            out[key] = DataPointDefinition(
                data_point=row["data_point"],
                sector=row["sector"],
                applies=applies,
                statement=row["statement"],
                standard_definition=row["standard_definition"],
                fallback_order=steps,
                badges=badges,
                inputs_one_filing=one,
                never_derive=never,
                not_applicable_reason=row["not_applicable_reason"],
                filter_note=row["filter_note"],
                rulings=row["rulings"],
            )
    for dp in {k[0] for k in out}:
        missing = [s for s in SECTORS if (dp, s) not in out]
        if missing:
            problems.append(f"{path.name}: {dp} has no row for sector(s) {missing}")
    if problems:
        raise RegistryError("; ".join(problems[:30]))
    return out


class BadgeUndecided(RegistryError):
    """The resolver row does not name exactly one fallback step of its data point: the cell gets no badge and stays
    OPEN (never defaulted to as_printed; one-display-path plan 2026-11-22, section 3)."""


# Resolver flags that name the derivation of a derived_not_printed row (RESOLVER-OUTPUT-FORMAT.md, "Derived pairs
# served directly") -> the data_points.csv badge of that step.
DERIVED_FLAG_BADGES = {
    "derived_issued_less_treasury": "derived:shares_issued-treasury_shares",
    "ci_parent_derived": "derived:ci_incl_nci-ci_nci",
    "equity_parent_derived": "derived:total_equity-noncontrolling_interest",
}
_QUOTED_LABEL = re.compile(r"'([^']+)'")
_PLACEHOLDER = re.compile(r"<[^>]*>")


def resolver_flags(row: dict) -> set[str]:
    return {f.strip() for f in (row.get("flags") or "").split(";") if f.strip()}


def printed_label(row: dict) -> str:
    """The printed line label the resolver quotes in its `why:` evidence (first quoted text), or ''."""
    nodes = row.get("nodes") or ""
    why = nodes.split("| why:", 1)[1] if "| why:" in nodes else ""
    m = _QUOTED_LABEL.search(why)
    return m.group(1).strip() if m else ""


def _derived_formula(badge: str) -> str:
    return badge[len("derived:") :]


def badge_for(
    dp: str,
    sector: str,
    resolver_row: dict,
    data_points: dict[tuple[str, str], DataPointDefinition] | None = None,
) -> str:
    """The badge of the fallback step that produced a resolver row's value (registry/data_points.csv `badges`).

    mapped -> as_printed (face line, note fact, printed zero, quoted text); combined -> the data point's combined step,
    its <placeholder> filled with the printed label; derived_not_printed (or a DERIVED flag) -> the derived step the
    flag names (DERIVED_FLAG_BADGES), else the data point's only derived step that is not a sum of printed lines;
    component_sum -> the data point's only additive derived step (sum(...) or a+b, no minus). Anything else, an
    ambiguous step, or a step the data point does not have raises BadgeUndecided. A perimeter badge is never inferred:
    the resolver output carries no perimeter signal yet."""
    defs = data_points if data_points is not None else _data_points()
    d = defs.get((dp, sector))
    if d is None:
        raise BadgeUndecided(f"{dp}/{sector}: no data_points.csv row")
    if not d.applies:
        raise BadgeUndecided(
            f"{dp}/{sector}: not_applicable is a cell state, not a badge"
        )
    decision = resolver_row.get("decision") or ""
    flags = resolver_flags(resolver_row)
    derived = [b for b in d.badges if b.startswith("derived:")]
    where = f"{dp}/{sector} {decision} {sorted(flags)}"
    # the resolver names the step it took (resolver .89: flag `derived:<formula>` from this file's badges, e.g. opex
    # X117 derived:total_costs_and_expenses-cost_of_revenue vs X89 derived:sum(printed operating lines)): that step.
    # A filing read's VALUE row is `mapped` and carries the reader's `badge=derived:<formula>` as this flag
    # (filing_reads.badge_flag): the value is that derivation, not a printed line (WMT other income FY2015 = 0 by the
    # pretax identity, 2026-11-22)
    stepped = [f for f in flags if f.startswith("derived:") and f in d.badges]
    if (
        decision in ("component_sum", "derived_not_printed", "mapped")
        and len(stepped) == 1
    ):
        return stepped[0]
    if decision == "derived_not_printed" or "DERIVED" in flags:
        named = [DERIVED_FLAG_BADGES[f] for f in flags if f in DERIVED_FLAG_BADGES]
        if named:
            cands = [b for b in named if b in d.badges]
        else:
            cands = [
                b
                for b in derived
                if not _derived_formula(b).startswith(("sum(", "zero_balance:"))
            ]
    elif decision == "component_sum":
        cands = [
            b
            for b in derived
            if "-" not in _derived_formula(b)
            and not _derived_formula(b).startswith("zero_balance:")
        ]
    elif decision == "mapped":
        cands = ["as_printed"] if "as_printed" in d.badges else []
    elif decision == "combined":
        label = printed_label(resolver_row)
        cands = list(dict.fromkeys(b for b in d.badges if b.startswith("combined:")))
        if len(cands) > 1:
            low = label.lower()
            cands = [
                b
                for b in cands
                if not _PLACEHOLDER.search(b) and b[len("combined:") :].lower() in low
            ]
        if len(cands) == 1 and _PLACEHOLDER.search(cands[0]):
            if not label:
                raise BadgeUndecided(f"{where}: combined line without a printed label")
            cands = ["combined:" + label]
    else:
        raise BadgeUndecided(f"{where}: decision carries no value")
    cands = list(dict.fromkeys(cands))
    if len(cands) != 1:
        raise BadgeUndecided(f"{where}: {len(cands)} matching steps {cands}")
    return cands[0]


def _data_points() -> dict[tuple[str, str], DataPointDefinition]:
    if "dps" not in _CACHE:
        _CACHE["dps"] = load_data_points()
    return _CACHE["dps"]  # type: ignore[return-value]


def compute_data_points_version(directory: Path | None = None) -> str:
    p = (directory or REGISTRY_DIR) / DATA_POINTS_FILE
    return hashlib.sha256(p.name.encode() + b"\0" + p.read_bytes()).hexdigest()[:16]


_CACHE: dict[str, object] = {}


def get_registry() -> dict[str, Metric]:
    if "reg" not in _CACHE:
        _CACHE["reg"] = load_registry()
    return _CACHE["reg"]  # type: ignore[return-value]


def registry_version() -> str:
    return compute_registry_version()


def __getattr__(name: str):
    if name == "REGISTRY_VERSION":
        return compute_registry_version()
    if name == "DATA_POINTS_VERSION":
        return compute_data_points_version()
    raise AttributeError(name)
