"""Add the data points the shared tool never emits (NOTES-801-900 defect 1) to its docmaps, read by
pipeline/scripts/reads/docmap.py from the same latest 10-K's statement R pages and companyfacts.

The shared tool emits 38 of the 46 data points of the ABT format; these 8 are read here: comprehensive_income,
other_income_expense_net, interest_income, cf_ar_change, cf_inventory_change, cf_ap_change, dividends_per_share,
amortization_of_intangibles. A row is added only when this reader opened the same accession as the shared tool;
not_presented rows carry the MetaLinks whole-filing check (every candidate tag searched in MetaLinks.json).
usage: supplement.py <sec_docs> <reads_dir> <tool_cache> TICKER [...]   (rewrites the docmaps in reads_dir)"""

from __future__ import annotations

import csv
import importlib.util
import io
import json
import re
import sys
from pathlib import Path

MISSING = (
    "comprehensive_income",
    "other_income_expense_net",
    "interest_income",
    "cf_ar_change",
    "cf_inventory_change",
    "cf_ap_change",
    "dividends_per_share",
    "amortization_of_intangibles",
)
COLS = [
    "ticker",
    "data_point",
    "status",
    "tags",
    "stmt",
    "r_page",
    "label",
    "fy0_printed",
    "fy0_api",
    "fy1_printed",
    "fy1_api",
    "match",
    "era_from_note",
    "evidence_class",
    "note",
]
MD_COLS = [
    "data_point",
    "status",
    "tags",
    "r_page",
    "label",
    "fy0_printed",
    "fy0_api",
    "fy1_printed",
    "fy1_api",
    "match",
    "evidence_class",
    "note",
]
HERE = Path(__file__).resolve().parent


def _reader():
    spec = importlib.util.spec_from_file_location("reads_docmap", HERE / "docmap.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = m
    spec.loader.exec_module(m)
    return m


def key(url: str) -> str:
    return re.sub(r"\W", "_", url)[-150:]


def metalinks_tags(cache: Path, base: str) -> set[str] | None:
    f = cache / key(base + "MetaLinks.json")
    if not f.exists():
        return None
    try:
        inst = next(iter(json.loads(f.read_text())["instance"].values()))
    except (ValueError, KeyError, StopIteration):
        return None
    return {k.replace("_", ":", 1) for k in inst.get("tag", {})}


def main(docs: Path, reads: Path, cache: Path, tickers: list[str]) -> None:
    dm = _reader()
    summ = {
        r["ticker"]: r
        for r in json.loads((docs / "fetch_summary.json").read_text())
        if r.get("filed")
    }
    for tic in tickers:
        csv_p, md_p = (
            reads / f"{tic}-docmap-2026-11-12.csv",
            reads / f"{tic}-docmap-2026-11-12.md",
        )
        rows = list(csv.DictReader(csv_p.open()))
        have = {r["data_point"] for r in rows}
        md = md_p.read_text()
        m = re.search(r"10-K (\d{10}-\d\d-\d{6}) \(CIK (\d{10}), filed", md)
        rec = summ.get(tic)
        if not m or not rec:
            print(json.dumps({"ticker": tic, "skipped": "no latest filing"}))
            continue
        accn, cik = m.groups()
        if rec["accession"] != accn:
            print(
                json.dumps(
                    {
                        "ticker": tic,
                        "skipped": f"different accession {rec['accession']} vs tool {accn}",
                    }
                )
            )
            continue
        res = dm.read_company(docs, cik, tic, accn, rec["filed"])
        base = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accn.replace('-', '')}/"
        ml = metalinks_tags(cache, base)
        added = []
        for r in res["rows"]:
            dp = r["data_point"]
            if dp not in MISSING or dp in have:
                continue
            r = {k: r.get(k, "") for k in COLS}
            r["note"] = r["note"].replace(
                " | WHOLE-FILING CHECK PENDING (XBRL instance not fetched)", ""
            )
            if r["evidence_class"] == "PENDING":
                r["evidence_class"] = "FILING-CHECKED"
            if r["status"] in ("not_presented", "OUT"):
                spec = next(d for d in dm.DPS if d.name == dp)
                cands = [
                    t if ":" in t else f"us-gaap:{t}" for t in spec.tags + spec.combined
                ]
                if ml is None:
                    r["note"] += (
                        " | whole-filing check: MetaLinks.json not available, HAND REVIEW"
                    )
                else:
                    hits = [c for c in cands if c in ml]
                    r["note"] += (
                        f" | whole-filing check: none of {', '.join(c.split(':')[1] for c in cands)} in MetaLinks.json"
                        if not hits
                        else f" | whole-filing check: HAND REVIEW, MetaLinks.json has {', '.join(hits)}"
                    )
            r["note"] = (
                "check: machine-full-filing | supplement: not emitted by the shared tool, read by "
                "pipeline/scripts/reads/docmap.py from the same accession | "
                + r["note"]
            )
            r["era_from_note"] = r["era_from_note"] or ""
            rows.append(r)
            added.append(dp)
        buf = io.StringIO()
        w = csv.DictWriter(buf, fieldnames=COLS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
        csv_p.write_text(buf.getvalue())
        lines = md.splitlines()
        idx = max(
            i for i, line in enumerate(lines) if re.match(r"\| [a-z_]+ \| ", line)
        )
        new = [
            "| "
            + " | ".join(str(r.get(k, "")).replace("|", "/") for k in MD_COLS)
            + " |"
            for r in rows
            if r["data_point"] in added
        ]
        lines[idx + 1 : idx + 1] = new
        md_p.write_text("\n".join(lines) + "\n")
        print(json.dumps({"ticker": tic, "added": added}))


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), sys.argv[4:])
