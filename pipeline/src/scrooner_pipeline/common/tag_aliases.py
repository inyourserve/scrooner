"""One printed line carried under two filer-extension names across filings (a rename, same line, same value).

A component sum names the tag of the era it was read in; a later filing that restates the period may print the
same line under the renamed tag. The sum then still takes every part from ONE filing (the latest that prints all
of them), reading the renamed tag where the later filing uses it. Evidence required per entry: both tags are
face lines between the same two subtotals and print the same value for a period both filings print.

MSFT: FY2016 10-K / FY2017 10-K print custom ImpairmentIntegrationAndRestructuringExpenses (1,110M for FY2016, an
IS line between Gross margin and Operating income); the FY2018 10-K prints the same line as custom
ImpairmentAndRestructuringExpenses (FY2016 = 1,110M, IS line 13 of 0001564590-18-019062).
"""

from __future__ import annotations

TAG_ALIASES: dict[str, tuple[str, ...]] = {
    "ImpairmentIntegrationAndRestructuringExpenses": (
        "ImpairmentAndRestructuringExpenses",
    ),
    "ImpairmentAndRestructuringExpenses": (
        "ImpairmentIntegrationAndRestructuringExpenses",
    ),
}


def with_aliases(tag: str) -> tuple[str, ...]:
    return (tag, *TAG_ALIASES.get(tag, ()))
