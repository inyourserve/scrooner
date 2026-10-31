"""FSN pilot proof (Dhairya condition 3): for cohort filings whose own
_cal.xml / .xsd / MetaLinks we already hold (Verifier-passed cals), do the
Notes data set's cal.tsv arcs reproduce the filer's parent/child/weight set
exactly? cal.tsv has no role URIs (grp/arc sequence numbers), so the
comparison is on the set of (parent, child, weight) across all roles, and
separately on the statement-role subset being a subset of cal.tsv.
usage: fsn_cal_proof.py <quarter_cal.tsv(.zst|.xz)> <cal_dir1,cal_dir2,...> [max_filings]
"""
import csv
import io
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import build_debt_slots as b  # noqa: E402
import common  # noqa: E402

cal_tsv = Path(sys.argv[1])
cal_dirs = [Path(d) for d in sys.argv[2].split(",")]
limit = int(sys.argv[3]) if len(sys.argv) > 3 else 10**9


def open_text(p):
    if p.suffix == ".zst":
        return io.TextIOWrapper(subprocess.Popen(["zstd", "-dc", str(p)], stdout=subprocess.PIPE).stdout, encoding="utf-8", errors="replace")
    if p.suffix == ".xz":
        return io.TextIOWrapper(subprocess.Popen(["xz", "-dc", str(p)], stdout=subprocess.PIPE).stdout, encoding="utf-8", errors="replace")
    return open(p, encoding="utf-8", errors="replace")


fsn = defaultdict(set)  # adsh -> {(parent, child, weight)}
with open_text(cal_tsv) as fh:
    rd = csv.DictReader(fh, delimiter="\t")
    for row in rd:
        # FSN 'negative' IS the weight (1 or -1), not a boolean
        w = str(float(row.get("negative") or "1"))
        fsn[row["adsh"]].add((row["ptag"], row["ctag"], w))
print("cal.tsv filings:", len(fsn), "arcs:", sum(len(v) for v in fsn.values()))

held = {}
for d in cal_dirs:
    for sub in d.iterdir():
        if sub.is_dir() and sub.name in fsn:
            held[sub.name] = d
print("held cals that are in this quarter:", len(held))
exact = subset = differ = 0
details = []
for adsh, d in sorted(held.items())[:limit]:
    era, arcs = common.load_cal(d, adsh)
    ours_all = {(p, c, w) for (role, p), kids in arcs.items() for c, w, _cu in kids}
    ours_stmt = {(p, c, w) for (role, p), kids in arcs.items() if b.BS_ROLE_RX.search(role) and not b.NOTE_ROLE_RX.search(role) for c, w, _cu in kids}
    theirs = fsn[adsh]
    if ours_all == theirs:
        exact += 1
        verdict = "EXACT"
    elif ours_stmt <= theirs:
        subset += 1
        verdict = "statement_role_subset"
    else:
        differ += 1
        verdict = "DIFFERS"
    details.append((adsh, verdict, len(ours_all), len(theirs), len(ours_stmt - theirs)))
for row in details:
    print("  %s %-22s ours_all=%d fsn=%d statement_arcs_missing_in_fsn=%d" % row)
print(f"exact {exact}, statement-role subset {subset}, differs {differ}, checked {len(details)}")
