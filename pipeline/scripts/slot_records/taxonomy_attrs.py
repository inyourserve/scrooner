"""US-GAAP element attributes from the one-time FASB fetch (fasb_elements.py):
balance (debit/credit), period type, abstract. The structural guard behind the
lexical ones: a standard element with a DEBIT balance printed in the
liabilities zone (NFG UnamortizedLossReacquiredDebtNoncurrent) is never a
liability member; an ABSTRACT element is never a member. Elements absent from
the CSV (retired tags, custom tags) return None and the lexical guards decide.
"""
import csv
from pathlib import Path

_CSV = Path(__file__).parent / "results" / "us_gaap_2025_elements.csv"
_ATTRS: dict[str, dict] | None = None


def attrs(tag: str) -> dict | None:
    global _ATTRS
    if _ATTRS is None:
        _ATTRS = {}
        if _CSV.exists():
            with open(_CSV, newline="") as f:
                for r in csv.DictReader(f):
                    _ATTRS[r["name"]] = r
    return _ATTRS.get(tag)


def balance(tag: str) -> str | None:
    a = attrs(tag)
    return (a or {}).get("balance") or None


def is_abstract(tag: str) -> bool | None:
    a = attrs(tag)
    return None if a is None else a.get("abstract") == "1"
