"""Regression check: emitted slot-record classes vs the Verifier-confirmed
expectations (expected_debt_classes.json). Exit 1 on any mismatch.
usage: check_expected_classes.py <results_dir>
"""
import json
import sys
from pathlib import Path

results = Path(sys.argv[1])
expected = json.loads((results / "expected_debt_classes.json").read_text())
failures = []
checked = 0
for f in sorted(results.glob("*_slots.jsonl")):
    for line in f.read_text().splitlines():
        r = json.loads(line)
        if r.get("kind") != "slot_record" or r["company"] not in expected:
            continue
        for m in r["members"]:
            want = expected[r["company"]].get(m["tag"])
            if want is None:
                continue
            checked += 1
            if m["class"] != want:
                failures.append(
                    f"{r['company']} {r['period_from']}..{r['period_to']} "
                    f"{m['tag']}: got {m['class']}, want {want}"
                )
print(f"checked {checked} member classes against fixtures")
for failure in failures:
    print("FAIL:", failure)
sys.exit(1 if failures else 0)
