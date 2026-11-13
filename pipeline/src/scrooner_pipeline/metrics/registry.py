"""Load and validate the metric registry (registry/*.csv, one file per family).

REGISTRY_VERSION is a hash of the registry files' names and bytes: any edit to any
row changes it. A metric's own `version` is bumped by hand when its published formula
changes meaning; `formula_ref` is `metric_id@version`.
"""

from __future__ import annotations

import csv
import hashlib
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
        if not sep or key not in {"div0", "floor", "zero_when_absent", "growth_base", "neg"}:
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
    return sorted((directory or REGISTRY_DIR).glob("*.csv"))


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
    raise AttributeError(name)
