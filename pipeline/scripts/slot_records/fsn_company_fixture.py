"""Cut a small FSN-store company directory (plain .tsv, FORMATS-v1 columns) for tests: only the named
accessions, num limited to instants (qtrs 0, all the balance-sheet lane reads). Rows are copied, never edited.
usage: fsn_company_fixture.py <companies/<cik10>> <out_dir> <adsh,adsh,...>"""
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from fsn_company import table  # noqa: E402

src, out, keep = Path(sys.argv[1]), Path(sys.argv[2]), set(sys.argv[3].split(","))
out.mkdir(parents=True, exist_ok=True)
dims = set()
for t in ("sub", "pre", "cal", "num", "dim"):
    rows = []
    for r in table(src, t):
        if t == "dim":
            if r["dimhash"] in dims:
                rows.append(r)
            continue
        if r["adsh"] not in keep or (t == "num" and r["qtrs"] != "0"):
            continue
        if t == "num" and r["dimh"] != "0x00000000":
            dims.add(r["dimh"])
        rows.append(r)
    if rows:
        with open(out / f"{t}.tsv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, list(rows[0]), delimiter="\t", quoting=csv.QUOTE_NONE, escapechar="\\", lineterminator="\n")
            w.writeheader()
            w.writerows(rows)
m = json.load(open(src / "manifest.json"))
json.dump({"cik": m["cik"], "fixture_of": sorted(keep), "source_input_sha256": m["input_sha256"]}, open(out / "manifest.json", "w"), indent=1)
print(out, {p.name: sum(1 for _ in open(p)) - 1 for p in sorted(out.glob("*.tsv"))})
