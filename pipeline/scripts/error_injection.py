"""Error-injection run: plant known errors into a copy of the top-100 export and measure each check's recall.

    # live, read-only (DATABASE_URL): plant ~20 per class across random companies, run every check, write the report
    python pipeline/scripts/error_injection.py --per-class 20 --out data-team/strategy/certification

    # record a small fixed set as an offline fixture (the CI test replays it with no database)
    python pipeline/scripts/error_injection.py --tickers AAPL,MSFT --per-class 2 --record-fixture DIR

    # replay a fixture offline: prints the score JSON
    python pipeline/scripts/error_injection.py --replay pipeline/tests/fixtures/error_injection

Method: certification/inject.py docstring. The export is read, never written; the database is read-only SELECTs.
"""

from __future__ import annotations

import argparse
import csv
import glob
import gzip
import json
import random
import sys
import time
from datetime import date
from pathlib import Path

from scrooner_pipeline.certification import display_cert as dc
from scrooner_pipeline.certification import inject as ij

REPO = Path(__file__).resolve().parents[2]
EXPORT = REPO / "data-team" / "strategy" / "top100-coverage.csv"
RESOLVER = REPO / "data-team" / "tags" / "line_map" / "resolver"


def dp_tags() -> dict:
    pd = ij.pattern_detectors()
    res = [r for p in sorted(glob.glob(str(RESOLVER / "*.csv"))) for r in pd.rows_of(p)]
    return pd.dp_tags_of(resolver_rows=res)


def evaluate(
    fields,
    base,
    mut,
    injections,
    ciks,
    sources,
    tags,
    seed,
    n_shown,
    n_hidden,
    log=print,
    release=None,
):
    rng = random.Random(seed + "-controls")
    by_t: dict[str, list] = {}
    for i in injections:
        by_t.setdefault(i.ticker, []).append(i)
    results = []
    for t in sorted(by_t):
        t0 = time.monotonic()
        excl = {(i.data_point, i.fiscal_year) for i in by_t[t]}
        ctl = ij.pick_controls(base[t], excl, n_shown, n_hidden, rng)
        rs = ij.evaluate_company(
            fields, base[t], mut[t], ciks[t], by_t[t], ctl, sources(t), tags
        )
        results += rs
        if release:
            release(t)
        log(
            f"{t}: {len(by_t[t])} planted, {sum(1 for r in rs if r.role == 'injected' and r.caught_any())} caught, "
            f"{time.monotonic() - t0:.1f}s",
        )
    return results


def write_report(
    out: Path, day: str, sc: dict, results, injections, meta: dict
) -> tuple[Path, Path]:
    out.mkdir(parents=True, exist_ok=True)
    csv_path = out / f"error-injection-{day}.csv"
    inj_by = {i.key: i for i in injections}
    rows = ij.result_rows(results)
    for r in rows:
        i = (
            inj_by.get((r["ticker"], r["data_point"], r["fiscal_year"]))
            if r["role"] == "injected"
            else None
        )
        r["note"] = i.note if i else ""
    with open(csv_path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=ij.RESULT_COLUMNS + ["note"])
        w.writeheader()
        w.writerows(rows)
    pct = lambda x: "-" if x is None else f"{100 * x:.0f}%"
    L = [
        f"# Error-injection recall of the certification checks ({day})",
        "",
        f"Harness `{ij.HARNESS_VERSION}` (`pipeline/src/scrooner_pipeline/certification/inject.py`, run by "
        f"`pipeline/scripts/error_injection.py`). Export copy: `{meta['export']}` (sha256 `{meta['sha'][:16]}`, read-only); "
        f"seed `{meta['seed']}`; {meta['companies']} companies; read-only SELECTs on fsn.*. Per-cell rows: `{csv_path.name}`.",
        "",
        "Method: plant one error per cell (at most one per company row) into a copy of the export, run every existing check on "
        "the mutated and the untouched copy, and count a planted cell caught by a check when the check flags it in the mutated "
        "copy and did not flag it the same way in the untouched copy. Checks: **self_check** = the top100-flow self-check / "
        "`certify_display.py --mechanical` census (gate incl. parts sum and per-share ceiling, registry badges, hide classes, "
        "hidden rows and years against fsn, derived and total_debt census); **patterns** = tag-expert detectors P02, P03, "
        "P05/P06, P08; **cell_match** = the drawn-cell fsn match (`display_cert.check_cell` / `check_derived`); "
        "**draw_check** = the automated draw checker (`draw_check@2`, AUTO_MISMATCH). cell_match and draw_check see a cell "
        "only when certify draws it, so they are run on every planted cell as if drawn; **one run** is the expected recall of a "
        "single certify: a census catch, else a draw catch times the chance the 199-cell draw takes the cell.",
        "",
        "| Class | Planted | self_check | patterns | cell_match | draw_check | Any check | Census only | One certify run |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for cls in ij.CLASSES:
        r = sc["classes"][cls]
        n = r["planted"]
        L.append(
            f"| {cls} | {n} | {r['self_check']} | {r['patterns']} | {r['cell_match']} | {r['draw_check']} | "
            f"**{r['any']} ({pct(r['recall'])})** | {r['census']} ({pct(r['census'] / n if n else None)}) | {pct(r['one_run'])} |"
        )
    o = sc["overall"]
    L.append(
        f"| **overall** | {o['planted']} | | | | | **{o['caught']} ({pct(o['recall'])})** | {o['census']} "
        f"({pct(o['census'] / o['planted'] if o['planted'] else None)}) | {pct(o['one_run'])} |"
    )
    c = sc["controls"]
    L += [
        "",
        f"**False positives (untouched control cells, {c['cells']}: up to {meta['n_shown']} shown and {meta['n_hidden']} hidden "
        f"per evaluated company).** New flags after the injection (spillover): {c['spillover']} "
        f"({', '.join(f'{k} {v}' for k, v in c['spillover_by_check'].items())}). Flagged in the untouched export itself: "
        f"{c['base_flagged']} of {c['cells']} ({pct(c['base_flagged'] / c['cells'] if c['cells'] else None)}; "
        f"{', '.join(f'{k} {v}' for k, v in c['base_flagged_by_check'].items())}): an upper bound on the false-positive "
        "rate, since a flag on an untouched cell may also be a real error in the export.",
        "",
        "## Weakest classes",
        "",
    ]
    weak = sorted(
        (cls for cls in ij.CLASSES if sc["classes"][cls]["planted"]),
        key=lambda k: (sc["classes"][k]["recall"], sc["classes"][k]["one_run"]),
    )
    for cls in weak[:5]:
        r = sc["classes"][cls]
        L.append(
            f"- **{cls}**: {r['any']}/{r['planted']} caught by any check; {pct(r['one_run'])} in one certify run."
        )
    L += (
        [
            "",
            "## Notes",
            "",
        ]
        + [f"- {x}" for x in meta.get("notes", [])]
        + [
            "",
            "## CI baseline",
            "",
            "`pipeline/tests/test_error_injection.py` replays a fixed small injection set (`pipeline/tests/fixtures/error_injection/`, "
            "offline bundle, no database) and fails when any class's recall drops below `baseline.json`.",
            "",
        ]
    )
    md = out / f"error-injection-{day}.md"
    md.write_text("\n".join(L))
    return md, csv_path


def record_fixture(
    d: Path, fields, base, injections, ciks, sources, tags, seed, n_shown, n_hidden, sc
) -> None:
    d.mkdir(parents=True, exist_ok=True)
    rows = [r for t in sorted(base) if t in ciks for r in base[t]]
    ij.write_rows(d / "export.csv.gz", fields, rows)
    ij.write_injections(d / "injections.csv", injections)
    bundles = {t: sources(t).bundle for t in sorted(ciks)}
    with gzip.open(d / "bundles.json.gz", "wt") as fh:
        json.dump(
            {
                "ciks": ciks,
                "dp_tags": {k: sorted(v) for k, v in tags.items()},
                "bundles": bundles,
            },
            fh,
            default=str,
        )
    (d / "meta.json").write_text(
        json.dumps(
            {
                "seed": seed,
                "n_shown": n_shown,
                "n_hidden": n_hidden,
                "version": ij.HARNESS_VERSION,
            },
            indent=1,
        )
        + "\n"
    )
    base_json = {
        cls: sc["classes"][cls]["recall"]
        for cls in ij.CLASSES
        if sc["classes"][cls]["planted"]
    }
    (d / "baseline.json").write_text(
        json.dumps(base_json, indent=1, sort_keys=True) + "\n"
    )


def replay(d: Path, log=print) -> tuple[dict, list]:
    fields, rows = ij.read_rows(d / "export.csv.gz")
    base = ij.by_company(rows)
    injections = ij.read_injections(d / "injections.csv")
    with gzip.open(d / "bundles.json.gz", "rt") as fh:
        b = json.load(fh)
    meta = json.loads((d / "meta.json").read_text())
    mut = ij.apply_injections(base, injections)
    srcs = {t: ij.BundleSource(x) for t, x in b["bundles"].items()}
    tags = {k: set(v) for k, v in b["dp_tags"].items()}
    results = evaluate(
        fields,
        base,
        mut,
        injections,
        b["ciks"],
        srcs.__getitem__,
        tags,
        meta["seed"],
        meta["n_shown"],
        meta["n_hidden"],
        log,
    )
    return ij.score(results), results


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--coverage", type=Path, default=EXPORT)
    ap.add_argument("--per-class", type=int, default=20)
    ap.add_argument("--seed", default="error-injection-2026-11-22")
    ap.add_argument("--tickers", help="comma list: plant only in these companies")
    ap.add_argument("--classes", help="comma list of classes (default all)")
    ap.add_argument("--controls-shown", type=int, default=8)
    ap.add_argument("--controls-hidden", type=int, default=2)
    ap.add_argument(
        "--out", type=Path, help="write error-injection-<date>.md/.csv here"
    )
    ap.add_argument("--date", default=date.today().isoformat())
    ap.add_argument("--record-fixture", type=Path)
    ap.add_argument("--replay", type=Path)
    ap.add_argument("--note", action="append", default=[])
    a = ap.parse_args(argv)
    if a.replay:
        sc, _ = replay(a.replay)
        print(json.dumps(sc, indent=1))
        return 0

    fields, rows = ij.read_rows(a.coverage)
    fields = ij.add_badges(fields, rows)
    base = ij.by_company(rows)
    if a.tickers:
        want = {t.strip().upper() for t in a.tickers.split(",")}
        base = {t: rs for t, rs in base.items() if t in want}
    classes = (
        [c.strip() for c in a.classes.split(",")] if a.classes else list(ij.CLASSES)
    )
    from scrooner_pipeline.db.connection import get_connection

    with get_connection() as conn:
        conn.read_only = True
        srcs: dict[str, ij.RecordingSource] = {}

        rec = a.record_fixture is not None
        plain = dc.SqlFactSource(conn, timeout_ms=60000)

        def source(t):
            if t not in srcs:
                srcs[t] = ij.RecordingSource(conn, record=rec)
            return srcs[t]

        def facts_for(t, acc, pe):
            # a fixture records the planting reads too (replayed offline); a full run keeps no copy of them
            return (source(t) if rec else plain).filing_facts(acc, pe)[0]

        t0 = time.monotonic()
        mut, injections, planted = ij.plant_all(
            base, a.per_class, a.seed, facts_for, classes
        )
        print(f"planted {planted} in {time.monotonic() - t0:.0f}s", flush=True)
        ciks = {}
        with (
            conn.cursor() as cur
        ):  # the flow's CIK (top100_flow.sh): core.company, never a predecessor's
            cur.execute("set statement_timeout = 15000")
            for t in sorted({i.ticker for i in injections}):
                cur.execute(
                    "select ltrim(cik, '0') from core.company where id = %s",
                    (int(base[t][0]["company_id"]),),
                )
                ciks[t] = cur.fetchone()[0]
        tags = dp_tags()
        results = evaluate(
            fields,
            base,
            mut,
            injections,
            ciks,
            source,
            tags,
            a.seed,
            a.controls_shown,
            a.controls_hidden,
            log=lambda s: print(s, flush=True),
            release=None if rec else srcs.pop,
        )
        conn.rollback()
    sc = ij.score(results)
    print(json.dumps(sc, indent=1))
    if a.out:
        meta = {
            "export": str(a.coverage.relative_to(REPO))
            if a.coverage.is_relative_to(REPO)
            else str(a.coverage),
            "sha": dc.sha256(a.coverage),
            "seed": a.seed,
            "companies": len(ciks),
            "n_shown": a.controls_shown,
            "n_hidden": a.controls_hidden,
            "notes": a.note,
        }
        md, cp = write_report(a.out, a.date, sc, results, injections, meta)
        print(f"wrote {md} and {cp}")
    if a.record_fixture:
        record_fixture(
            a.record_fixture,
            fields,
            base,
            injections,
            ciks,
            source,
            tags,
            a.seed,
            a.controls_shown,
            a.controls_hidden,
            sc,
        )
        print(f"recorded fixture {a.record_fixture}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
