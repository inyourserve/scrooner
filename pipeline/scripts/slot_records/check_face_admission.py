"""Fixture check for the face-admission guards (stdlib, -I).

For each fixture filing: face rows (FSDS pre, BS statement) + its own cal ->
statement-role members (build_debt_slots.debt_observation) -> every standard
debt-reading face line not among the members goes through face_admission.admit.
Prints admitted / rejected per filing and, with an expectations file, PASS/FAIL
per expectation: {"<adsh>": {"must_admit": [tags], "must_not_admit": [tags]}}.
usage: check_face_admission.py <face_rows.jsonl> <cal_dir> [expected.json]
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import build_debt_slots as b  # noqa: E402
import era_detect_rx as rx  # noqa: E402
import face_admission as fa  # noqa: E402

rows = defaultdict(list)
meta = {}
for line in open(sys.argv[1]):
    r = json.loads(line)
    if r.get("stmt") != "BS":
        continue
    rows[r["adsh"]].append((r["report"], r["line"], {"tag": r["tag"], "custom": r["custom"], "label": r.get("label") or ""}))
    meta[r["adsh"]] = (r["cik"], r["form"], r["period"])
cal_dir = Path(sys.argv[2])
expected = json.load(open(sys.argv[3])) if len(sys.argv) > 3 else {}

fails = 0
for adsh in sorted(rows):
    face = [d for _, _, d in sorted(rows[adsh], key=lambda x: (x[0], x[1]))]
    cals = sorted((cal_dir / adsh).glob("*_cal.xml")) or sorted((cal_dir / adsh).glob("*.xsd"))
    metalinks = cal_dir / adsh / "MetaLinks.json"
    if cals:
        cal = b.parse_cal(cals[0])
    elif metalinks.exists():
        cal = b.parse_metalinks(metalinks)
    else:
        print(adsh, "NO CAL")
        continue
    cik, form, period = meta[adsh]
    obs = b.debt_observation(adsh, form, period, cal)
    members = {m["tag"] for m in obs["members"] if not m["class"].startswith("excluded_")}
    print(f"== {adsh} cik {cik} {form} {period}  statement-role members: {sorted(members)}")
    decided = {}
    for d in face:
        tag = d["tag"]
        if tag in members or d["custom"]:
            continue
        if not (rx.DEBT_RX.search(tag) or rx.LABEL_RX.search(d["label"])) or rx.EXCLUDE_RX.search(tag):
            continue
        if not b.DEBT_RX.search(tag) or b.EXCLUDE_RX.search(tag):
            continue  # label-only or structurally excluded: never admitted (existing rule)
        side = ("current" if re.search(r"Current$|^ShortTerm", tag)
                else "noncurrent" if re.search(r"Noncurrent$|^LongTerm", tag) else None)
        if side is None:
            decided[tag] = (False, "no_side_by_name", None)
        else:
            decided[tag] = fa.admit(tag, face, cal["arcs"], members, side)
        ok, reason, tie = decided[tag]
        print(f"   {'ADMIT ' if ok else 'reject'} {tag:55} {d['label'][:45]:45} {reason}"
              + (f"  tie->{tie['total']} roots={len(tie['roots'])}" if ok and tie and tie.get('computable') else
                 ("  tie not computable (hold)" if ok else "")))
    exp = expected.get(adsh, {})
    for t in exp.get("must_admit", []):
        got = decided.get(t, (t in members, "already_member", None))[0]
        print(f"   {'PASS' if got else 'FAIL'} must_admit {t}")
        fails += 0 if got else 1
    for t in exp.get("must_not_admit", []):
        got = decided.get(t, (False, "not_a_candidate", None))[0]
        print(f"   {'PASS' if not got else 'FAIL'} must_not_admit {t}")
        fails += 1 if got else 0
print("FIXTURE FAILS:", fails)
sys.exit(1 if fails else 0)
