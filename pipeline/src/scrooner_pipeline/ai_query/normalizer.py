"""Meaning-preserving normalization for natural-language screen queries.

Only spelling/syntax forms with one reviewed meaning belong here. Semantic
choices (for example, which kind of "growth" a user means) remain ambiguities
for the interpreter and are never repaired by this module.
"""

import re
import unicodedata
from dataclasses import dataclass


@dataclass(frozen=True)
class QueryCorrection:
    source_text: str
    corrected_text: str
    kind: str
    requires_confirmation: bool = False


@dataclass(frozen=True)
class NormalizedQueryText:
    text: str
    corrections: tuple[QueryCorrection, ...] = ()


# Longest and most specific phrases first. These are spelling/form repairs,
# never substitutions between different financial concepts.
_REVIEWED_REPLACEMENTS: tuple[tuple[str, str, str], ...] = (
    (r"\breturn\s+on\s+equit(?:iy|ityy|yi)\b", "return on equity", "metric_spelling"),
    (r"\bretrun\s+on\s+equit(?:y|iy|ity)\b", "return on equity", "metric_spelling"),
    (
        r"\breturn\s+on\s+invested\s+captial\b",
        "return on invested capital",
        "metric_spelling",
    ),
    (r"\bmarket\s+capitali[sz]ation\b", "market capitalization", "metric_spelling"),
    (r"\bmarket\s+capt?ali[sz]ation\b", "market capitalization", "metric_spelling"),
    (
        r"\bdebt\s+(?:to\s+)?equit(?:y|iy)\s+ratio\b",
        "debt to equity",
        "metric_spelling",
    ),
    (r"\bdebt\s+equit(?:y|iy)\b", "debt to equity", "metric_spelling"),
    (r"\bprice\s+to\s+earnings?\s+ratio\b", "price to earnings", "metric_form"),
    (r"\bgreater\s+then\b", "greater than", "operator_spelling"),
    (r"\bhigher\s+then\b", "higher than", "operator_spelling"),
    (r"\bless\s+then\b", "less than", "operator_spelling"),
    (r"\blower\s+then\b", "lower than", "operator_spelling"),
    (r"\bper\s*cent\b", "%", "unit_form"),
    (r"\bpercentage\b", "%", "unit_form"),
)


def normalize_query_text(text: str) -> NormalizedQueryText:
    normalized = unicodedata.normalize("NFKC", text)
    normalized = normalized.replace("≥", ">=").replace("≤", "<=").replace("≠", "!=")
    normalized = normalized.replace("’", "'").replace("‘", "'")
    corrections: list[QueryCorrection] = []

    for pattern, replacement, kind in _REVIEWED_REPLACEMENTS:
        regex = re.compile(pattern, re.IGNORECASE)

        def replace(match: re.Match[str]) -> str:
            source = match.group(0)
            if source.lower() != replacement.lower():
                corrections.append(QueryCorrection(source, replacement, kind))
            return replacement

        normalized = regex.sub(replace, normalized)

    normalized = re.sub(r"\s+", " ", normalized).strip()
    return NormalizedQueryText(normalized, tuple(corrections))
