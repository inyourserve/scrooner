"""Cut a small FSN-store company directory (plain .tsv, FORMATS-v1 columns) for tests: only the named
accessions, num limited to instants (qtrs 0, all the balance-sheet lane reads). Rows are copied, never edited.
usage: fsn_company_fixture.py <companies/<cik10>> <out_dir> <adsh,adsh,...> [--all]
  --all: every table of FORMATS-v1 (sub pre num cal ren tag dim) and every num row of the accessions (durations too),
  for fixtures that fsn_store.load reads (the cash-flow detectors)."""
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from fsn_company import table  # noqa: E402

src, out, keep = Path(sys.argv[1]), Path(sys.argv[2]), set(sys.argv[3].split(","))
ALL = "--all" in sys.argv
out.mkdir(parents=True, exist_ok=True)
dims = set()
tags = set()
for t in (("sub", "pre", "cal", "num", "ren", "dim", "tag") if ALL else ("sub", "pre", "cal", "num", "dim")):
    rows = []
    for r in table(src, t):
        if t == "dim":
            if r["dimhash"] in dims:
                rows.append(r)
            continue
        if t == "tag":
            if (r["tag"], r["version"]) in tags:
                rows.append(r)
            continue
        if r["adsh"] not in keep or (t == "num" and r["qtrs"] != "0" and not ALL):
            continue
        if t in ("pre", "num"):
            tags.add((r["tag"], r["version"]))
        if t == "cal":
            tags.update({(r["ptag"], r["pversion"]), (r["ctag"], r["cversion"])})
        if t == "num" and r["dimh"] != "0x00000000":
            dims.add(r["dimh"])
        rows.append(r)
    if rows:
        with open(out / f"{t}.tsv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, list(rows[0]), delimiter="\t", quoting=csv.QUOTE_NONE, escapechar="\\", lineterminator="\n")
            w.writeheader()
            w.writerows(rows)
m = json.load(open(src / "manifest.json"))
import hashlib  # noqa: E402
TABLES = ("sub", "pre", "num", "cal", "ren", "tag", "dim")
shas = {t: (hashlib.sha256((out / f"{t}.tsv").read_bytes()).hexdigest() if (out / f"{t}.tsv").exists() else "") for t in TABLES}
json.dump({"cik": m["cik"], "company_id": None, "fsn_sets": m.get("fsn_sets"), "accessions": sorted(keep),
           "row_counts": {t: (sum(1 for _ in open(out / f"{t}.tsv")) - 1 if (out / f"{t}.tsv").exists() else 0) for t in TABLES},
           "file_sha256": shas, "input_sha256": hashlib.sha256("\n".join(shas[t] for t in TABLES).encode()).hexdigest(),
           "fixture_of": sorted(keep), "source_input_sha256": m["input_sha256"]}, open(out / "manifest.json", "w"), indent=1)
print(out, {p.name: sum(1 for _ in open(p)) - 1 for p in sorted(out.glob("*.tsv"))})
