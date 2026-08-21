"""Stage 6b -- Rule-based interpreter (doc 15). A deterministic keyword/
pattern matcher, not a real NL parser -- explicitly bounded, per doc 15
Sec 1: anything outside this grammar is reported as unrecognized, never
guessed. Implements the NLInterpreter protocol so a real LLM (6c, not
built here) can be swapped in later behind the same contract.

Clause grammar (joined only by " and ", matching the Screener's own
AND-only combination, doc 14):
    "{metric} {operator_phrase} {value}[%]"        -- comparison
    "{metric} between {low}[%] and {high}[%]"       -- between
    "top {n} [by] {metric}" / "bottom {n} [by] {metric}"  -- ranked
    "{sector}" / "{sector} companies" / "companies in {sector}"  -- categorical

Known limitation, documented rather than silently handled: a "between"
clause is never combined with another AND-joined clause in the same
query -- the word "and" inside "between X and Y" would otherwise be
ambiguous with the clause-joining "and". If "between" appears anywhere in
the input, the whole input is parsed as a single between-clause. Doc 15's
own test queries never combine the two, so this bound doesn't block any
named test case -- it's a real scope limit of the rule-based grammar, not
a bug, and exactly the kind of thing a real LLM (6c) would handle better.
"""

import re
from decimal import Decimal

from scrooner_pipeline.ai_query.aliases import (
    AMBIGUOUS_METRIC_PHRASES,
    METRIC_ALIASES,
    OPERATOR_ALIASES,
    SECTOR_ALIASES,
    SECTOR_BUCKET_ALIASES,
)
from scrooner_pipeline.ai_query.interpreter import AmbiguityNote, InterpretationResult
from scrooner_pipeline.screener.schema import CategoricalPredicate, MetricPredicate, ScreenQuery

TOP_BOTTOM_RE = re.compile(r"^(top|bottom)\s+(\d+)\s+(?:by\s+)?(.+)$", re.IGNORECASE)
BETWEEN_RE = re.compile(r"^(.*?)\s+between\s+([\d.]+)(%)?\s+and\s+([\d.]+)(%)?$", re.IGNORECASE)


def _parse_value(number_str: str, has_percent: bool) -> Decimal:
    value = Decimal(number_str)
    return value / Decimal(100) if has_percent else value


# A small, explicit list of leading filler phrases to strip before metric
# lookup -- not a generic stopword remover, a curated, reviewed list, same
# discipline as the alias tables themselves. Found live 2026-08-17:
# "companies with ROE above 30%" failed to parse at all because "companies
# with roe" doesn't match "roe" in METRIC_ALIASES verbatim.
METRIC_PHRASE_FILLER_PREFIXES = ["companies with ", "companies that have ", "with ", "where ", "having "]


def _strip_filler(phrase: str) -> str:
    normalized = phrase.strip().lower()
    for prefix in METRIC_PHRASE_FILLER_PREFIXES:
        if normalized.startswith(prefix):
            normalized = normalized[len(prefix) :]
    return normalized.strip()


def _lookup_metric(phrase: str) -> tuple[str | None, list[str] | None]:
    """Returns (metric_name, None) on a confident match, (None, candidates)
    on a known ambiguous phrase, or (None, None) if nothing matched at all."""
    normalized = _strip_filler(phrase)
    if normalized in AMBIGUOUS_METRIC_PHRASES:
        return None, AMBIGUOUS_METRIC_PHRASES[normalized]
    if normalized in METRIC_ALIASES:
        return METRIC_ALIASES[normalized], None
    return None, None


def _lookup_sector(phrase: str) -> tuple[str, str] | None:
    """Returns (field, value) -- field is "sic_code" for an exact
    SECTOR_ALIASES match (checked first, so existing behavior for
    already-covered phrases like "software companies" never changes),
    or "sector" for a SECTOR_BUCKET_ALIASES match (doc 28, broader
    phrases with no prior exact-SIC coverage)."""
    normalized = phrase.strip().lower()
    normalized = re.sub(r"^companies in\s+", "", normalized)
    normalized = re.sub(r"\s+companies$", "", normalized)

    sic_hit = SECTOR_ALIASES.get(normalized) or SECTOR_ALIASES.get(normalized + " companies")
    if sic_hit:
        return "sic_code", sic_hit

    bucket_hit = SECTOR_BUCKET_ALIASES.get(normalized) or SECTOR_BUCKET_ALIASES.get(normalized + " companies")
    if bucket_hit:
        return "sector", bucket_hit

    return None


def _find_operator(clause: str) -> tuple[str, str, str] | None:
    """Finds the longest operator phrase present in the clause; returns
    (metric_phrase, operator, value_phrase), or None if no known operator
    phrase is present at all."""
    best = None
    for phrase, op in OPERATOR_ALIASES.items():
        idx = clause.lower().find(f" {phrase} ")
        if idx != -1 and (best is None or len(phrase) > len(best[0])):
            best = (phrase, op, idx)
    if best is None:
        return None
    phrase, op, idx = best
    metric_part = clause[:idx].strip()
    value_part = clause[idx + len(phrase) + 2 :].strip()
    return metric_part, op, value_part


def _parse_clause(clause: str) -> tuple[MetricPredicate | None, CategoricalPredicate | None, str | None, AmbiguityNote | None]:
    """Returns exactly one of (metric predicate, categorical predicate,
    unrecognized-text, ambiguity-note) populated, the rest None."""
    clause = clause.strip()

    top_bottom = TOP_BOTTOM_RE.match(clause)
    if top_bottom:
        direction, n, metric_phrase = top_bottom.groups()
        metric_name, candidates = _lookup_metric(metric_phrase)
        if candidates:
            return None, None, None, AmbiguityNote(metric_phrase.strip(), candidates)
        if metric_name is None:
            return None, None, clause, None
        op = "top_n" if direction.lower() == "top" else "bottom_n"
        return MetricPredicate(metric_name=metric_name, operator=op, n=int(n)), None, None, None

    sector_hit = _lookup_sector(clause)
    if sector_hit:
        field, value = sector_hit
        return None, CategoricalPredicate(field=field, operator="=", value=value), None, None

    found_op = _find_operator(clause)
    if found_op:
        metric_phrase, op, value_phrase = found_op
        metric_name, candidates = _lookup_metric(metric_phrase)
        if candidates:
            return None, None, None, AmbiguityNote(metric_phrase, candidates)
        if metric_name is None:
            return None, None, clause, None
        m = re.match(r"^([\d.]+)(%)?$", value_phrase)
        if not m:
            return None, None, clause, None
        value = _parse_value(m.group(1), bool(m.group(2)))
        return MetricPredicate(metric_name=metric_name, operator=op, value=value), None, None, None

    return None, None, clause, None


def interpret(text: str) -> InterpretationResult:
    text = text.strip()
    if not text:
        return InterpretationResult(query=None, explanation="Empty query.", unrecognized=[""])

    between_match = BETWEEN_RE.match(text)
    if between_match:
        metric_phrase, low_str, low_pct, high_str, high_pct = between_match.groups()
        metric_name, candidates = _lookup_metric(metric_phrase)
        if candidates:
            return InterpretationResult(
                query=None,
                explanation="Ambiguous metric in 'between' clause.",
                ambiguous=[AmbiguityNote(metric_phrase.strip(), candidates)],
            )
        if metric_name is None:
            return InterpretationResult(query=None, explanation="Could not recognize the metric.", unrecognized=[metric_phrase.strip()])
        low = _parse_value(low_str, bool(low_pct))
        high = _parse_value(high_str, bool(high_pct))
        predicate = MetricPredicate(metric_name=metric_name, operator="between", value_range=(low, high))
        query = ScreenQuery(metric_predicates=[predicate])
        explanation = f"Filtering for: {metric_name} between {low} and {high}."
        return InterpretationResult(query=query, explanation=explanation, recognized_query=query)

    clauses = [c.strip() for c in re.split(r"\s+and\s+", text, flags=re.IGNORECASE) if c.strip()]
    metric_predicates: list[MetricPredicate] = []
    categorical_predicates: list[CategoricalPredicate] = []
    unrecognized: list[str] = []
    ambiguous: list[AmbiguityNote] = []

    for clause in clauses:
        mp, cp, unrec, amb = _parse_clause(clause)
        if mp:
            metric_predicates.append(mp)
        elif cp:
            categorical_predicates.append(cp)
        elif amb:
            ambiguous.append(amb)
        elif unrec is not None:
            unrecognized.append(unrec)

    if unrecognized or ambiguous:
        parts = []
        if unrecognized:
            parts.append(f"could not understand: {', '.join(unrecognized)}")
        if ambiguous:
            parts.append("; ".join(f"'{a.phrase}' could mean: {', '.join(a.candidates)}" for a in ambiguous))
        recognized_query = None
        if metric_predicates or categorical_predicates:
            recognized_query = ScreenQuery(
                metric_predicates=metric_predicates,
                categorical_predicates=categorical_predicates,
            )
        return InterpretationResult(
            query=None,
            explanation="; ".join(parts),
            unrecognized=unrecognized,
            ambiguous=ambiguous,
            recognized_query=recognized_query,
        )

    if not metric_predicates and not categorical_predicates:
        return InterpretationResult(query=None, explanation="Nothing recognized in this query.", unrecognized=[text])

    query = ScreenQuery(metric_predicates=metric_predicates, categorical_predicates=categorical_predicates)
    explanation_parts = [f"{p.metric_name} {p.operator} {p.value if p.value is not None else p.n}" for p in metric_predicates]
    explanation_parts += [f"{p.field} = {p.value}" for p in categorical_predicates]
    explanation = "Filtering for: " + "; ".join(explanation_parts) + "."
    return InterpretationResult(query=query, explanation=explanation, recognized_query=query)
