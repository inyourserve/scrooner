#!/usr/bin/env python3
"""Generates reason_class_map_v2.csv (Chief's review of v1, items 1-11). v1 (reason_class_map.csv) stays
as the record behind the 2026-10-20 scoreboard and is never edited.

Rows are keyed (pattern_key, family). family '*' is the default; a family row overrides it for data points
of that family (sb_lib.data_point_family). Items 3, 5 and 6 (family splits of the sector-income reasons,
zero_denominator and zero_base_value) are DATA-INFERRED and flagged queue_verifier_sample=yes.

usage: make_reason_class_map_v2.py [--cells PATH] [--out PATH]
"""
from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_reason_class_map as V1  # noqa: E402
import sb_lib as L  # noqa: E402

COLS = ["pattern_key", "family", "mode", "class", "owner", "rf_id", "root_cause_class", "candidate_state",
        "second_signal", "label", "queue_verifier_sample", "n_strings", "n_cells", "example",
        "evidence_class", "rationale"]

SECTOR = ("financial_institution_interest_income_not_revenue", "bank_interest_income_not_revenue",
          "reit_net_interest_income_not_revenue", "bdc_reports_investment_income_not_revenue")


def row(cls, owner, rf, why, *, root="", cand="", second="", label="DATA-INFERRED", queue="", mode="terminal"):
    return dict(mode=mode, **{"class": cls}, owner=owner, rf_id=rf, root_cause_class=root, candidate_state=cand,
                second_signal=second, label=label, queue_verifier_sample=queue, rationale=why)


# (pattern, family) -> overriding row. Defaults ('*') start from the v1 TERMINAL table.
OVERRIDES = {
    # item 9: owners move from sector_analyst to the RF-06/07 builder
    ("negative_ratio_undefined_cagr", "*"): row("evidence_pending", "data_engineer_l1", "RF-06",
        "candidate undefined_by_math; waits for the S3 value-proof rule (owner moved to RF-06 builder, v2 item 9)", cand="undefined_by_math"),
    ("non_positive_growth_not_meaningful", "*"): row("evidence_pending", "data_engineer_l1", "RF-06",
        "candidate undefined_by_math (non-positive growth); owner moved to RF-06 builder (item 9)", cand="undefined_by_math"),
    ("immaterial_prior_base", "*"): row("evidence_pending", "data_engineer_l1", "RF-06",
        "candidate undefined_by_math (materiality floor); owner moved to RF-06 builder (item 9)", cand="undefined_by_math"),
    # item 5: zero_denominator by what the cell divides by
    ("zero_denominator", "*"): row("evidence_pending", "data_engineer_l1", "RF-07",
        "candidate undefined_by_math (zero denominator); owner RF-07 builder (item 9); family not split", cand="undefined_by_math"),
    ("zero_denominator", "den_share_count"): row("resolver", "data_engineer_l1", "RF-15",
        "denominator is the share count: a zero share count is a resolver defect, not a math state (item 5)", queue="yes"),
    ("zero_denominator", "den_revenue"): row("evidence_pending", "sector_analyst", "RF-38",
        "revenue denominator: the pre-revenue overlay, needs filing evidence (item 5)", cand="undefined_by_math", queue="yes"),
    ("zero_denominator", "den_cost_of_revenue"): row("evidence_pending", "sector_analyst", "RF-32",
        "cost-of-revenue denominator: template candidate (row may not belong to the company group) (item 5)",
        cand="not_in_template", queue="yes"),
    # item 6: zero_base_value by data point
    ("zero_base_value", "*"): row("evidence_pending", "data_engineer_l1", "RF-06",
        "candidate undefined_by_math (zero base); owner RF-06 builder (item 9)", cand="undefined_by_math"),
    ("zero_base_value", "revenue_growth"): row("evidence_pending", "sector_analyst", "RF-38",
        "revenue growth from a zero base: the pre-revenue overlay (item 6)", cand="undefined_by_math", queue="yes"),
    ("zero_base_value", "dps_growth"): row("evidence_pending", "data_engineer_l1", "RF-06",
        "dividend-per-share growth from zero: could be a missed DPS tag, so tag_mapper must also look (item 6)",
        cand="undefined_by_math", second="tag_mapper", queue="yes"),
    ("zero_base_value", "eps_growth"): row("evidence_pending", "data_engineer_l1", "RF-06",
        "EPS growth from a zero base is undefined by math (item 6)", cand="undefined_by_math", queue="yes"),
    # item 4
    ("implausible:institutional_shares_exceed_shares_outstanding", "*"): row("guard_hidden", "data_engineer_l2",
        "RF-47", "the value is hidden by the plausibility guard; the root cause is the institutional share base (item 4)",
        root="resolver"),
    # item 2
    ("missing:prior_period(...)", "*"): row("period", "period_engineer", "RF-37",
        "a missing prior period is a period gap. history_horizon only with RF-37 evidence (earliest XBRL period across "
        "all filings); quarter-label bases (e.g. 2016_Q2 for a 10-year CAGR) are flagged to the Standardization Lead (item 2)",
        cand="history_horizon"),
    # item 7: cascades through gross_margin; this is the fallback when gross_margin is valued
    ("missing:fewer_than_3_years_gross_margin", "*"): row("period", "period_engineer", "RF-37",
        "walk through gross_margin; fallback when it is valued: fewer than 3 years of margin is a period matter until RF-37 evidence (item 7)",
        cand="history_horizon", mode="walk"),
    # item 8
    ("missing:share_count_1y_ago", "*"): row("period", "period_engineer", "RF-37",
        "the share count one year ago is missing: a period gap. NOT an alias for the current shares_outstanding cell (item 8)",
        cand="history_horizon"),
    # item 10
    ("no_dividend_history", "*"): row("evidence_pending", "sector_analyst", "RF-36",
        "candidate evidenced_zero (needs tag-agnostic filing evidence); tag_mapper is the second signal for a missed dividend tag (item 10)",
        cand="evidenced_zero", second="tag_mapper"),
}
# item 3: the four sector-income reasons by line
for pat in SECTOR:
    OVERRIDES[(pat, "*")] = row("evidence_pending", "sector_analyst", "RF-34",
        "sector reason asserted from classification, not a filing check (W9 family): fact-gated audit pending")
    OVERRIDES[(pat, "gp_cost_row")] = row("evidence_pending", "sector_analyst", "RF-34",
        "gross profit / cost of revenue: stays evidence_pending (item 3)", queue="yes")
    OVERRIDES[(pat, "opex_oi_row")] = row("definition_pending", "accountant", "RF-34",
        "operating expenses / operating income for an interest-income filer: a definition call for the named accountant (item 3)",
        queue="yes")
    OVERRIDES[(pat, "revenue_row")] = row("definition_pending", "accountant", "RF-34",
        "revenue row for an interest-income filer: what counts as revenue is a definition call for the accountant (item 3)",
        queue="yes")


def base_row(pat: str):
    if pat in V1.TERMINAL:
        cls, owner, rf, why = V1.TERMINAL[pat]
        return row(cls, owner, rf, why)
    if pat.startswith(("missing:", "incomplete:")):
        cls, owner, rf, why = V1.walk_fallback(pat)
        return row(cls, owner, rf, why, mode="walk")
    raise SystemExit(f"UNMAPPED pattern (add it deliberately): {pat!r}")


def build(cells: Path):
    ext = L.Extract(cells)
    graph = L.load_graph()
    seen = defaultdict(lambda: {"strings": set(), "example": "", "fam": Counter()})
    for (cid, dp), c in ext.cells.items():
        if c["reason"] or not c["has_value"]:
            p = L.reason_pattern(c["reason"])
            d = seen[p]
            d["strings"].add(c["reason"])
            d["example"] = d["example"] or c["reason"]
            d["fam"][L.data_point_family(dp, graph)] += 1
    rows = []
    for pat in sorted(seen, key=lambda k: (-sum(seen[k]["fam"].values()), k)):
        d = seen[pat]
        keys = {"*": OVERRIDES.get((pat, "*")) or base_row(pat)}
        for (p2, fam), r in OVERRIDES.items():
            if p2 == pat and fam != "*":
                keys[fam] = r
        covered = Counter()
        for fam, n in d["fam"].items():
            covered[fam if fam in keys else "*"] += n
        for fam in sorted(keys, key=lambda f: (f != "*", f)):
            r = dict(keys[fam])
            assert r["class"] in L.CLASSES and r["owner"] in L.OWNERS, (pat, fam)
            r.update(pattern_key=pat, family=fam, n_strings=len(d["strings"]), n_cells=covered.get(fam, 0),
                     example=d["example"], evidence_class="DATA-INFERRED")
            rows.append(r)
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cells", type=Path, default=L.EXPORT_GZ)
    ap.add_argument("--out", type=Path, default=L.REASON_MAP_V2)
    a = ap.parse_args(argv)
    rows = build(a.cells)
    with open(a.out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {len(rows)} rows ({len({r['pattern_key'] for r in rows})} patterns) to {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
