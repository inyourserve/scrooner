"""Check the Verifier's membership and value anchors. Exit 1 on any failure.
usage: check_anchors.py <results_dir> <records.jsonl> <replay_report.json>
"""
import json
import sys
from pathlib import Path

results = Path(sys.argv[1])
records = [json.loads(line) for line in open(sys.argv[2])]
report = json.load(open(sys.argv[3]))
failures = []

membership = json.loads((results / "expected_membership.json").read_text())
for ticker, fixtures in membership.items():
    if ticker.startswith("_"):
        continue
    for fx in fixtures:
        covering = [
            r for r in records
            if r["company"] == ticker and r["period_from"][:7] <= fx["covering"] <= r["period_to"][:7]
        ]
        if not covering:
            failures.append(f"{ticker}: no record covering {fx['covering']}")
            continue
        alts = fx["tag"] if isinstance(fx["tag"], list) else [fx["tag"]]
        for r in covering:
            member_tags = {m["tag"] for m in r["members"]}
            excluded_tags = {e["tag"] for e in r.get("excluded_candidates", [])}
            if fx["expect"] == "member" and not any(t in member_tags for t in alts):
                failures.append(f"{ticker} {r['period_from']}..{r['period_to']}: none of {alts} a member")
            if fx["expect"] == "excluded" and (
                any(t in member_tags for t in alts) or not any(t in excluded_tags for t in alts)
            ):
                failures.append(f"{ticker} {r['period_from']}..{r['period_to']}: {alts} not excluded")

values = json.loads((results / "expected_values.json").read_text())
cells = {(c["ticker"], c["period_end"]): c for c in report["cells"]}
for a in values["anchors"]:
    cell = cells.get((a["ticker"], a["period_end"]))
    if "lease_inclusive" in a:
        if cell is None:
            failures.append(f"{a['ticker']} {a['period_end']}: no replay cell for value anchor")
        elif cell["slot_lease_inclusive"] != a["lease_inclusive"]:
            failures.append(
                f"{a['ticker']} {a['period_end']}: slot {cell['slot_lease_inclusive']} != anchor {a['lease_inclusive']}"
            )
    if "member_present" in a:
        covered = any(
            r["company"] == a["ticker"]
            and r["period_from"][:7] <= a["period_end"][:7] <= r["period_to"][:7]
            and a["member_present"] in {m["tag"] for m in r["members"]}
            for r in records
        )
        if not covered:
            failures.append(f"{a['ticker']} {a['period_end']}: member {a['member_present']} absent")

print(f"anchors checked: membership {sum(len(v) for k, v in membership.items() if not k.startswith('_'))}, values {len(values['anchors'])}")
for f in failures:
    print("FAIL:", f)
sys.exit(1 if failures else 0)
