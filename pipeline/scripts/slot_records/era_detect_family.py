"""Family era detection from FSDS face rows (stdlib, run with -I).

Like era_detect.py but parameterized by family (family_config.py): fingerprints
each filing by its ordered family tags on the family's statements, collapses
consecutive identical fingerprints into eras, emits eras + boundary accessions.
usage: era_detect_family.py <pre_rows.jsonl> <family> <eras_out.json> <boundaries_out.txt>
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from family_config import FAMILIES, classify  # noqa: E402

family = sys.argv[2]
cfg = FAMILIES[family]


def iso(d: str) -> str:
    return f"{d[:4]}-{d[4:6]}-{d[6:]}" if d and len(d) == 8 and d.isdigit() else d


by_filing: dict[str, dict] = {}
lines = defaultdict(list)
for line in open(sys.argv[1]):
    r = json.loads(line)
    by_filing[r["adsh"]] = {
        "cik": r["cik"], "form": r["form"], "period": iso(r["period"]), "filed": iso(r["filed"]),
    }
    stmt = r.get("stmt", "CF")
    if stmt in cfg["stmts"] and cfg["match"].search(r["tag"]) and not cfg["exclude"].search(r["tag"]):
        lines[r["adsh"]].append(
            (stmt, r["report"], r["line"], r["tag"], r["custom"], classify(family, r["tag"], stmt))
        )

companies = defaultdict(list)
for adsh, meta in by_filing.items():
    fam_lines = sorted(lines.get(adsh, []))
    fp = tuple((s, t, c) for s, _, _, t, cu, c in fam_lines)
    members = [
        {"stmt": s, "tag": t, "custom": cu, "class": c}
        for s, _, _, t, cu, c in fam_lines
    ]
    companies[meta["cik"]].append((meta["filed"], meta["period"], adsh, meta["form"], fp, members))

eras_out = {}
boundaries = []
for cik, filings in companies.items():
    filings.sort()
    eras = []
    for filed, period, adsh, form, fp, members in filings:
        if eras and eras[-1]["fp"] == list(map(list, fp)):
            eras[-1]["last"] = adsh
            eras[-1]["period_to"] = period
            eras[-1]["n"] += 1
        else:
            eras.append(
                {"fp": list(map(list, fp)), "first": adsh, "last": adsh, "form": form,
                 "period_from": period, "period_to": period, "filed_from": filed, "n": 1,
                 "members": members}
            )
            boundaries.append((cik, adsh))
    eras_out[cik] = eras
with open(sys.argv[3], "w") as f:
    json.dump(eras_out, f)
with open(sys.argv[4], "w") as f:
    for cik, adsh in boundaries:
        f.write(f"{int(cik)} {adsh}\n")
print(
    f"family {family}: companies {len(eras_out)}  filings {len(by_filing)}  "
    f"eras {sum(len(v) for v in eras_out.values())}  boundaries {len(boundaries)}"
)
for cik in sorted(eras_out):
    print(f"  {cik}: {len(eras_out[cik])} eras")
