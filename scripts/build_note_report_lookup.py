"""Build data-team/47-fsn-store/note_report_lookup.csv from the coverage export + the local SEC FSN quarter cache.

usage: build_note_report_lookup.py <top100-coverage.csv or glob of several> <fsn cache dir> [out.csv] [--edgar]
Wanted pairs = rows of locator_source note_fact_report_not_stored (accession, each tag), plus every `parts` entry
(tag=value@accession#page) that has no page. Existing lookup rows are kept.
"""

import csv
import glob
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pipeline" / "src"))
from scrooner_pipeline.mapper import note_report_lookup as nl


PART = re.compile(r"([^=;]+)=[^@;]*@([^#;]+)#([^;]*)$")


def wanted_pairs(covs: list[Path]) -> set[tuple[str, str]]:
    wanted: set[tuple[str, str]] = set()
    for cov in covs:
        for r in csv.DictReader(cov.open(newline="")):
            if r["locator_source"] == "note_fact_report_not_stored" and r["accession"]:
                for t in r["tag"].split(","):
                    if t.strip():
                        wanted.add((r["accession"], t.strip()))
            for part in (r.get("parts") or "").split(";"):
                m = PART.match(part.strip())
                if m and not m.group(3):  # a part with no R page
                    wanted.add((m.group(2), m.group(1)))
    return wanted


def main(covs: list[Path], cache: Path, out: Path) -> int:
    wanted = wanted_pairs(covs)
    have = nl.load_lookup(out) if out.exists() else {}
    old = list(csv.DictReader(out.open(newline=""))) if out.exists() else []
    rows, missing = nl.build_rows(cache, {k for k in wanted if k not in have})
    if (
        missing and "--edgar" in sys.argv
    ):  # Option B for filings newer than the cached SEC data sets
        import os

        from scrooner_pipeline.fsn_store.edgar_fetch import EdgarClient

        client = EdgarClient(os.environ["SEC_USER_AGENT"])
        by_acc: dict[str, set[str]] = {}
        for a, t in missing:
            by_acc.setdefault(a, set()).add(t)
        for a, ts in sorted(by_acc.items()):
            try:
                got = nl.scan_edgar(client, int(a.split("-")[0]), a, ts)
            except Exception as e:  # noqa: BLE001
                print("edgar failed", a, repr(e)[:120])
                continue
            for t, (rep, n) in got.items():
                rows.append(
                    {
                        "accession": a,
                        "tag": t,
                        "report": rep,
                        "n_reports": n,
                        "line": "",
                        "plabel": "",
                    }
                )
                missing.discard((a, t))
    allrows = sorted(old + rows, key=lambda r: (r["accession"], r["tag"]))
    with out.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=nl.COLUMNS, lineterminator="\n")
        w.writeheader()
        w.writerows(allrows)
    print(
        f"wanted {len(wanted)} new {len(rows)} total {len(allrows)} not_found {len(missing)}"
    )
    for a, t in sorted(missing):
        print("not found:", a, t)
    return 0


if __name__ == "__main__":
    out = (
        Path(sys.argv[3])
        if len(sys.argv) > 3 and not sys.argv[3].startswith("--")
        else nl.DEFAULT_PATH
    )
    covs = [Path(x) for x in sorted(glob.glob(sys.argv[1]))]
    sys.exit(main(covs, Path(sys.argv[2]), out))
