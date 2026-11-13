"""S17 dry run: which red cells would the predecessor-companyfacts backfill fill? READ ONLY, no database write.

Inputs (files only; the live DB is not touched by this script):
  --redcells   data-team/tags/red-cells/top100-redcells-v2-*.csv (rows with systemic_id S17)
  --tagmap     JSON dump of analytics.company_tag_map joined to canonical_concept.name, one list per row:
               [company_id, cik, taxonomy, tag, stmt, decision, concept_name, sign, era_from, era_to, ...]
  --windows    data-team/47-fsn-store/company_history_sources.csv (the applied predecessor windows)
  --facts-dir  folder with SEC companyfacts payloads cf_<CIK10>.json (data.sec.gov, at most 4 requests/s)

A cell is FILLED when (a) the company's tag map has a 'concept' claim for its data point whose era covers the
cell's period end, and (b) the predecessor CIK's companyfacts holds an annual-form (10-K family) fact under that
(taxonomy, tag) whose period end is within TOL days of the cell's period end (about one year long for a flow, an
instant for a balance-sheet point) and inside the predecessor window of core.company_history_source. That is
evidence the facts exist; the mapper and the cell proof still decide the served value. Other outcomes:
  component_claim          the claim is a sum of components, not one fact (counted apart)
  claim_but_no_fact        a concept claim covers the era but the predecessor payload has no such fact
  reason_claim_only:<d>    only a reason row (not_presented, not_in_template) covers the era: the cell is a
                           reasoned blank once the map is served, not filled by the backfill
  no_tag_map_claim_for_era no map row covers the era: the era must be extended (reader or era_extend) after the
                           backfill; the facts alone do not fill it
  outside_window           the period end is outside every predecessor window of the company"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

TOL = 7  # days: 52/53-week year ends
ANNUAL_FORMS = {"10-K", "10-K405", "10-KT", "10-K/A", "20-F", "40-F"}
COMPANY_OF_TICKER = {
    "XOM": 5351,
    "MRVL": 2683,
    "BLK": 4123,
    "LIN": 4841,
    "AVGO": 5116,
    "DIS": 5261,
}
INSTANT = {
    "cash_and_equivalents",
    "total_assets",
    "total_liabilities",
    "stockholders_equity",
    "current_assets",
    "current_liabilities",
    "accounts_receivable",
    "accounts_payable",
    "inventory",
    "goodwill",
    "ppe_net",
    "shares_outstanding",
}
SERVED_ALIAS = {"revenue": "revenue_sanity_resolved"}


def _d(s):
    return date.fromisoformat(s[:10]) if s and s not in ("None", "") else None


def served_names(data_point: str) -> set[str]:
    """The names a data point is stored under in the tag map (base name, or its '_resolved' served concept)."""
    return {data_point, f"{data_point}_resolved", SERVED_ALIAS.get(data_point, "")}


def load_windows(path: Path) -> dict[int, list[tuple[str, date, date]]]:
    out: dict[int, list[tuple[str, date, date]]] = defaultdict(list)
    for r in csv.DictReader(path.open()):
        if r["relation"] == "predecessor":
            out[int(r["company_id"])].append(
                (r["source_cik"], _d(r["valid_from"]), _d(r["valid_to"]))
            )
    return out


def predecessor_facts(facts_dir: Path, cik: str) -> dict:
    """(taxonomy, tag) -> [(start, end, accn)] of annual-form numeric facts of one companyfacts payload."""
    p = facts_dir / f"cf_{cik}.json"
    out: dict = defaultdict(list)
    if not p.exists():
        return out
    for tax, tags in json.loads(p.read_text())["facts"].items():
        for tag, body in tags.items():
            for units in body["units"].values():
                for e in units:
                    if e.get("form") in ANNUAL_FORMS and isinstance(
                        e.get("val"), (int, float)
                    ):
                        out[(tax, tag)].append(
                            (_d(e.get("start")), _d(e["end"]), e["accn"])
                        )
    return out


def classify(
    data_point: str, period_end: date, claims: list, windows: list, facts_for
) -> tuple[str, str]:
    """(status, detail) of one cell. claims: the company's tag-map rows; windows: its predecessor windows
    [(source_cik, from, to)]; facts_for(cik) -> predecessor_facts(...). Pure."""
    wins = [(c, f, t) for c, f, t in windows if f <= period_end <= t]
    if not wins:
        return "outside_window", "period end not inside any predecessor window"
    names = served_names(data_point)
    covering = [
        c
        for c in claims
        if c[6] in names
        and (_d(c[8]) is None or _d(c[8]) <= period_end)
        and (_d(c[9]) is None or period_end <= _d(c[9]))
    ]
    values = [c for c in covering if c[5] == "concept"]
    comps = [c for c in covering if c[5] == "component"]
    facts = facts_for(wins[0][0])
    status, detail = "no_tag_map_claim_for_era", ""
    if covering and not values and not comps:
        status, detail = f"reason_claim_only:{covering[0][5]}", covering[0][10] or ""
    if comps:
        status, detail = "component_claim", f"{comps[0][2]}:{comps[0][3]}"
    for c in values:
        hit = [
            (s, e, acc)
            for s, e, acc in facts.get((c[2], c[3]), [])
            if abs((e - period_end).days) <= TOL
            and (s is None or 340 <= (e - s).days <= 380 or data_point in INSTANT)
        ]
        if hit:
            return "FILLED", f"{c[2]}:{c[3]} {hit[0][2]}"
        status, detail = "claim_but_no_fact", f"{c[2]}:{c[3]}"
    return status, detail


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--redcells", required=True)
    ap.add_argument("--tagmap", required=True)
    ap.add_argument(
        "--windows", default="data-team/47-fsn-store/company_history_sources.csv"
    )
    ap.add_argument("--facts-dir", required=True)
    ap.add_argument("--out", help="CSV of per-cell results")
    a = ap.parse_args()

    windows = load_windows(Path(a.windows))
    claims: dict[int, list] = defaultdict(list)
    for r in json.loads(Path(a.tagmap).read_text()):
        claims[int(r[0])].append(r)
    cache: dict[str, dict] = {}

    def facts_for(cik: str) -> dict:
        if cik not in cache:
            cache[cik] = predecessor_facts(Path(a.facts_dir), cik)
        return cache[cik]

    rows = [r for r in csv.DictReader(open(a.redcells)) if r["systemic_id"] == "S17"]
    res, tally = [], Counter()
    for r in rows:
        cid = COMPANY_OF_TICKER[r["ticker"]]
        status, detail = classify(
            r["data_point"], _d(r["period_end"]), claims[cid], windows[cid], facts_for
        )
        tally[(r["ticker"], status)] += 1
        res.append(
            {
                **{
                    k: r[k]
                    for k in ("ticker", "data_point", "fiscal_year", "period_end")
                },
                "status": status,
                "detail": detail,
            }
        )
    print(f"S17 red cells: {len(rows)}")
    for t in COMPANY_OF_TICKER:
        print(t, {s: n for (tk, s), n in sorted(tally.items()) if tk == t})
    print("FILLED total", sum(n for (_, s), n in tally.items() if s == "FILLED"))
    if a.out:
        with open(a.out, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(res[0]))
            w.writeheader()
            w.writerows(res)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
