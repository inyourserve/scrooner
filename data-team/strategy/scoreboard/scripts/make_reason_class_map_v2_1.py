#!/usr/bin/env python3
"""Generates reason_class_map_v2_1.csv from the v2 rules plus the Chief's fixes (a)-(f). v2 stays as published.

(a) fewer_than_3_years_gross_margin fallback: unclassified, no candidate (issuers are long-history; history_horizon was wrong)
(b) missing:prior_period(...): class period, candidate history_horizon BLANKED (set only where the RF-37 earliest-period check passes)
(c) TTM dividend and buyback fallbacks: second_signal tag_mapper + candidate evidenced_zero
(d) missing:fcf_ttm: rationale corrected (the token resolves to the ANNUAL fcf metric)
(e) immaterial_revenue_base: candidate undefined_by_math
(f) currency is an orthogonal flag (a classifier change; no map column)

usage: make_reason_class_map_v2_1.py [--cells PATH] [--out PATH]
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_reason_class_map as V1  # noqa: E402
import make_reason_class_map_v2 as G  # noqa: E402
import sb_lib as L  # noqa: E402

row = G.row
OV = dict(G.OVERRIDES)

OV[("missing:fewer_than_3_years_gross_margin", "*")] = row(
    "unclassified", "triage", "",
    "walk through gross_margin; fallback when it is valued (all cells are margin_expanding_3yr). The issuers are mostly "
    "long-history (WMT, PG, COST, MMM, CAT, CVX), so history_horizon is wrong; the cause is unknown from the extract (v2.1 a)",
    mode="walk",
)
OV[("missing:prior_period(...)", "*")] = row(
    "period", "period_engineer", "RF-37",
    "a missing prior period is a period gap. No history_horizon candidate: the bases are mostly 2016+ quarter labels from "
    "label arithmetic in ttm.py, not young filers. Set history_horizon only where the RF-37 earliest-period check passes (v2.1 b)",
)
_ttm_why = (
    " TTM dividend/buyback fallback: the TTM window is not constructible although the annual cell holds a value; "
    "a zero or non-payer is possible (PFE, CMI, GOOG cases), so evidenced_zero is the candidate and tag_mapper the second signal (v2.1 c)"
)
for pat in ("missing:share_buybacks_ttm", "missing:dividends_paid_ttm", "missing:dividends_per_share_ttm"):
    OV[(pat, "*")] = row(
        "period", "period_engineer", "RF-01",
        "walk: TTM window not constructible although inputs hold a latest value (consecutive-window / basis)." + _ttm_why,
        cand="evidenced_zero", second="tag_mapper", mode="walk",
    )
OV[("missing:fcf_ttm", "*")] = row(
    "period", "period_engineer", "RF-01",
    "walk: the token fcf_ttm resolves to the ANNUAL fcf metric (the graph has no TTM fcf node), so this fallback fires when the "
    "annual fcf cell is valued. It does not show that the TTM construction failed; TTM fcf needs four consecutive quarterly fcf rows (v2.1 d)",
    mode="walk",
)
OV[("immaterial_revenue_base", "*")] = row(
    "evidence_pending", "sector_analyst", "RF-38",
    "candidate undefined_by_math (revenue below floor); candidate state set to match this rationale (v2.1 e)",
    cand="undefined_by_math",
)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cells", type=Path, default=L.EXPORT_GZ)
    ap.add_argument("--out", type=Path, default=L.REASON_MAP_V2_1)
    a = ap.parse_args(argv)
    G.OVERRIDES = OV
    rows = G.build(a.cells)
    with open(a.out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=G.COLS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {len(rows)} rows ({len({r['pattern_key'] for r in rows})} patterns) to {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
