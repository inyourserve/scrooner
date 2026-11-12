"""Apply hand-check verdicts to the shared tool's docmaps (Dhairya 2026-11-12): every hand-checked row gets
"check: hand <R page> agree|corrected: <why>" and its corrections; every other row "check: machine-full-filing".
The md data-point rows are rewritten from the CSV in the shared tool's column order, and a "## Hand check" section
records the counts and the disagreement rate on the random 10% mapped sample.

verdict file <TICKER>.json: {"ticker", "rows": {data_point: {"class": "CHECK"|"SAMPLE", "verdict": "agree"|"corrected",
  "page": "R6.htm", "why": "...", "set": {csv column: new value, ...}}}}
usage: apply_checks.py <reads_in> <verdicts_dir> <out_dir> TICKER [...]"""

import csv
import io
import json
import re
import sys
from pathlib import Path

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
STATUSES = {
    "mapped",
    "combined",
    "component sum",
    "component_in_note",
    "not_presented",
    "OUT",
}


def apply(src: Path, vdir: Path, dst: Path, tic: str) -> dict:
    rows = list(csv.DictReader((src / f"{tic}-docmap-2026-11-12.csv").open()))
    v = json.loads((vdir / f"{tic}.json").read_text())["rows"]
    unknown = set(v) - {r["data_point"] for r in rows}
    if unknown:
        raise SystemExit(f"{tic}: verdicts for unknown data points {sorted(unknown)}")
    stats = {"hand": 0, "corrected": 0, "sample": 0, "sample_disagree": 0}
    for r in rows:
        x = v.get(r["data_point"])
        if not x:
            r["note"] = (
                r["note"] + " | " if r["note"] else ""
            ) + "check: machine-full-filing"
            continue
        if x["verdict"] not in ("agree", "corrected") or not x.get("page"):
            raise SystemExit(
                f"{tic} {r['data_point']}: verdict needs agree|corrected and the R page"
            )
        for k, val in (x.get("set") or {}).items():
            if k not in COLS or k in ("ticker", "data_point"):
                raise SystemExit(f"{tic} {r['data_point']}: cannot set {k}")
            r[k] = str(val)
        if r["status"] not in STATUSES:
            raise SystemExit(
                f"{tic} {r['data_point']}: status {r['status']!r} outside the vocabulary"
            )
        stats["hand"] += 1
        stats["corrected"] += x["verdict"] == "corrected"
        if x.get("class") == "SAMPLE":
            stats["sample"] += 1
            stats["sample_disagree"] += x["verdict"] == "corrected"
        word = "agree" if x["verdict"] == "agree" else f"corrected: {x.get('why', '')}"
        r["evidence_class"] = "FILING-CHECKED"
        r["note"] = (
            r["note"] + " | " if r["note"] else ""
        ) + f"check: hand {x['page']} {word}".strip()
    dst.mkdir(parents=True, exist_ok=True)
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=COLS, lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    (dst / f"{tic}-docmap-2026-11-12.csv").write_text(buf.getvalue())
    md = (src / f"{tic}-docmap-2026-11-12.md").read_text().splitlines()
    by = {r["data_point"]: r for r in rows}
    new = []
    for line in md:
        m = re.match(r"\| ([a-z_]+) \| ", line)
        if m and m.group(1) in by:
            r = by[m.group(1)]
            line = (
                "| "
                + " | ".join(str(r.get(k, "")).replace("|", "/") for k in MD_COLS)
                + " |"
            )
        new.append(line)
    rate = (stats["sample_disagree"] / stats["sample"]) if stats["sample"] else 0.0
    new += [
        "",
        "## Hand check (Dhairya 2026-11-12)",
        (
            f"- Rows hand-checked against their R pages: {stats['hand']} of {len(rows)} (every not_presented, combined, "
            "component and NOTE row; mapped rows the machine flagged: no API value, extension tag, label match; and a "
            "seeded random 10% of the other mapped rows). All other rows: check: machine-full-filing."
        ),
        f"- Corrected by hand: {stats['corrected']}.",
        f"- Random mapped sample: {stats['sample']} rows, {stats['sample_disagree']} disagreements ({rate:.1%}).",
    ]
    (dst / f"{tic}-docmap-2026-11-12.md").write_text("\n".join(new) + "\n")
    return {"ticker": tic, **stats}


if __name__ == "__main__":
    src, vdir, dst = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    for t in sys.argv[4:]:
        print(json.dumps(apply(src, vdir, dst, t)))
