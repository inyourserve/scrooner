#!/usr/bin/env python3
"""Generates maps/../reason_class_map.csv, the FROZEN reason-to-class map v1 (one row per
reason PATTERN: parameters in parentheses stripped). This script holds the judgement; the csv is
the artifact that is reviewed once by the Data Chief and then frozen by version. A change is a new
file reason_class_map_v2.csv, never an edit.

Classes and owners are the frozen enums of the freeze register (section 1). Evidence label of every
row: DATA-INFERRED (no filing opened). Terminal rows decide the class from the reason alone.
Walk rows are cascades (incomplete:*, missing:<input>): the class is INHERITED from the blocking input
cells at classification time (sb_lib.Classifier); the class/owner here is the fallback used only when
no input cell is blank.

usage: make_reason_class_map.py [--cells PATH] [--out PATH]
"""
from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sb_lib as L  # noqa: E402

# pattern -> (class, owner, rf_id, rationale)
TERMINAL = {
    "": ("unclassified", "triage", "", "no reason stored: shrinks only when K2 shrinks"),
    "line_not_presented_in_filing": ("evidence_pending", "sector_analyst", "RF-35",
        "evidence not proof (migration 0093; 14-34% of held values show no face line, F10): needs a FILING-CHECKED locator or an audited detector"),
    "line_presented_combined_with_others": ("evidence_pending", "sector_analyst", "RF-35",
        "combined presentation is evidence, not proof; never plain AP/AR; needs audited detector"),
    "line_in_filing_not_extracted": ("vocabulary", "tag_mapper", "RF-43",
        "the line is on the statement but no mapped tag captured it: a real investigable vocabulary gap"),
    "negative_ratio_undefined_cagr": ("evidence_pending", "sector_analyst", "RF-06",
        "candidate undefined_by_math; stays evidence_pending until the S3 value-proof rule exists"),
    "non_positive_growth_not_meaningful": ("evidence_pending", "sector_analyst", "RF-06",
        "candidate undefined_by_math (non-positive base); needs the S3 value-proof rule"),
    "zero_base_value": ("evidence_pending", "sector_analyst", "RF-06",
        "candidate undefined_by_math (zero base)"),
    "zero_denominator": ("evidence_pending", "sector_analyst", "RF-07",
        "candidate undefined_by_math (zero denominator)"),
    "immaterial_prior_base": ("evidence_pending", "sector_analyst", "RF-06",
        "candidate undefined_by_math (materiality floor)"),
    "immaterial_revenue_base": ("evidence_pending", "sector_analyst", "RF-38",
        "candidate undefined_by_math (revenue below floor)"),
    "financial_institution_interest_income_not_revenue": ("evidence_pending", "sector_analyst", "RF-34",
        "sector reason asserted from classification, not a filing check (W9 family): fact-gated audit pending"),
    "bank_interest_income_not_revenue": ("evidence_pending", "sector_analyst", "RF-34",
        "sector reason asserted from classification (W9 family): fact-gated audit pending"),
    "reit_net_interest_income_not_revenue": ("evidence_pending", "sector_analyst", "RF-34",
        "sector reason asserted from classification (W9 family): fact-gated audit pending"),
    "bdc_reports_investment_income_not_revenue": ("evidence_pending", "sector_analyst", "RF-34",
        "sector reason asserted from classification (W9 family): fact-gated audit pending"),
    "pre_revenue_biotech_pharma": ("evidence_pending", "sector_analyst", "RF-38",
        "pre-revenue overlay needs filing evidence, never SIC alone"),
    "pre_revenue_mining_exploration": ("evidence_pending", "sector_analyst", "RF-38",
        "pre-revenue overlay needs filing evidence, never SIC alone"),
    "no_dividend_history": ("evidence_pending", "sector_analyst", "RF-36",
        "candidate evidenced_zero; needs tag-agnostic filing evidence (S3 2.1); AT-7.5 contradiction"),
    "implausible:institutional_shares_exceed_shares_outstanding": ("resolver", "data_engineer_l2", "RF-47",
        "institutional share base does not reconcile to shares outstanding"),
    "missing:institutional_holdings": ("ingestion", "data_engineer_l2", "RF-47",
        "no institutional holdings rows for the company"),
    "missing:prior_period(...)": ("evidence_pending", "period_engineer", "RF-37",
        "candidate history_horizon: base period before first available period; needs earliest-XBRL-period evidence"),
    "missing:fewer_than_3_years_gross_margin": ("evidence_pending", "period_engineer", "RF-37",
        "candidate history_horizon (fewer than 3 years of margin)"),
    "missing:non_consecutive_years": ("period", "period_engineer", "RF-01",
        "years present but not consecutive"),
    "missing:4_consecutive_quarters": ("period", "period_engineer", "RF-01",
        "TTM needs four consecutive quarters"),
    "partial:missing_debt_or_cash": ("finding_open", "verifier", "RF-11",
        "VALUED cell that carries a reason: an EV shown while debt or cash is missing (W13 candidate, F6); not counted as a blank"),
}


def walk_fallback(pat: str):
    """Class used only if no input cell is blank. Judgement is stated in the rationale."""
    if "(" in pat:
        return ("period", "period_engineer", "RF-01",
                "walk: names a specific missing year/period; if every named input is valued at the latest period the gap is in a prior period")
    if "_ttm" in pat or "ttm_" in pat:
        return ("period", "period_engineer", "RF-01",
                "walk: TTM window not constructible although inputs hold a latest value (consecutive-window / basis)")
    return ("unclassified", "triage", "",
            "walk: no blank input cell found; the cause is unknown from the extract alone")


def build(cells: Path):
    ext = L.Extract(cells)
    patterns = defaultdict(lambda: {"strings": set(), "cells": 0, "example": ""})
    for c in ext.cells.values():
        if c["reason"] or not c["has_value"]:
            p = L.reason_pattern(c["reason"])
            d = patterns[p]
            d["strings"].add(c["reason"])
            d["cells"] += 1
            d["example"] = d["example"] or c["reason"]
    rows = []
    for p in sorted(patterns, key=lambda k: (-patterns[k]["cells"], k)):
        d = patterns[p]
        if p in TERMINAL:
            mode = "terminal"
            cls, owner, rf, why = TERMINAL[p]
        elif p.startswith(("missing:", "incomplete:")):
            mode = "walk"
            cls, owner, rf, why = walk_fallback(p)
        else:
            raise SystemExit(f"UNMAPPED pattern (add it deliberately): {p!r}")
        assert cls in L.CLASSES and owner in L.OWNERS, (p, cls, owner)
        rows.append({"pattern_key": p, "mode": mode, "class": cls, "owner": owner, "rf_id": rf,
                     "n_strings": len(d["strings"]), "n_cells": d["cells"],
                     "example": d["example"], "evidence_class": "DATA-INFERRED", "rationale": why})
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cells", type=Path, default=L.EXPORT_GZ)
    ap.add_argument("--out", type=Path, default=L.REASON_MAP)
    a = ap.parse_args(argv)
    rows = build(a.cells)
    cols = ["pattern_key", "mode", "class", "owner", "rf_id", "n_strings", "n_cells", "example",
            "evidence_class", "rationale"]
    with open(a.out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    modes = Counter(r["mode"] for r in rows)
    print(f"wrote {len(rows)} patterns to {a.out} ({dict(modes)}); strings covered "
          f"{sum(r['n_strings'] for r in rows)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
