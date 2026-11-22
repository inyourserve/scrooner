"""Certify one company's display coverage export (CERTIFICATION-METHOD-2026-11-16.md).

No SEC downloads: every check reads SEC's Financial Statement and Notes data already held in fsn.*.

  # live (CI, or anywhere DATABASE_URL is set)
  python pipeline/scripts/certify_display.py --ticker BA --cik 12927 --coverage BA.csv --live --out-dir OUT

  # where only a SQL console reaches the database: emit the one read-only query, run it, save the JSON
  python pipeline/scripts/certify_display.py --ticker BA --cik 12927 --coverage BA.csv --emit-sql > ba.sql
  python pipeline/scripts/certify_display.py --ticker BA --cik 12927 --coverage BA.csv --bundle ba.json --out-dir OUT

Writes OUT/<TICKER>-display-cert-<date>.md (verdict), OUT/<TICKER>-display-cert-<date>-evidence.csv,
OUT/<TICKER>-display-cert-<date>.json (certificate), appends the verdict to registry-history.csv and
rewrites --registry (default data-team/strategy/approvals/registry.csv) as one latest row per company,
printing the pooled bound over every company whose latest row is PASS. Exit code 0 PASS, 1 FAIL, 2 REVIEW.

Draw: min(199, shown cells) cells, stratified by statement and badge class; 199 is the smallest n whose
0-error Clopper-Pearson 95% upper bound is <= 1.5% (n >= ln(0.05)/ln(1-0.015) = 198.2).

--mechanical: every census check (gate, hide classes and proofs, badges, total_debt, derived and combined
cells) with no draw. Writes OUT/<TICKER>-mechanical-<date>.md and -evidence.csv only: no certificate, no
registry row. Used by the weekly certified re-check.

  # top-100 flow self-check (founder 2026-11-22): the same checks on one company's flow export, read-only on the DB;
  # every failure becomes an OPEN cell with the check's reason in DIR's export, open-shown file and summary row
  python pipeline/scripts/certify_display.py --self-check-dir RUN/coverage --company-id 1134 --cik 104169

Self-check writes DIR/verifier-self-check-<company_id>.csv (every finding, FAIL and REVIEW), never the registry, and
exits 0 when the checks ran (opened or not), 3 when they could not run (the company is then marked not gate-ready).
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from scrooner_pipeline.certification import display_cert as dc

REPO = Path(__file__).resolve().parents[2]
DEFAULT_REGISTRY = REPO / "data-team/strategy/approvals/registry.csv"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument(
        "--request",
        type=Path,
        help="a requests/<T>-request-<date>.md file; sets ticker and coverage and checks the sha256",
    )
    ap.add_argument("--ticker")
    ap.add_argument(
        "--cik",
        help="needed without --live; with --live it is read from fsn.filing by company id",
    )
    ap.add_argument("--coverage", type=Path)
    ap.add_argument(
        "--seed", help="default: <TICKER>-<first 12 hex of the coverage file's sha256>"
    )
    src = ap.add_mutually_exclusive_group()
    src.add_argument("--live", action="store_true", help="read fsn.* over DATABASE_URL")
    src.add_argument(
        "--bundle", type=Path, help="evidence bundle JSON from the --emit-sql query"
    )
    src.add_argument(
        "--emit-sql", action="store_true", help="print the bundle query and exit"
    )
    ap.add_argument("--out-dir", type=Path, default=Path("."))
    ap.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    ap.add_argument("--no-registry", action="store_true")
    ap.add_argument("--approver", default="Ritwik (cloud)")
    ap.add_argument(
        "--mechanical",
        action="store_true",
        help="census checks only, no draw: no certificate and no registry row",
    )
    ap.add_argument("--date", default=date.today().isoformat())
    ap.add_argument(
        "--self-check-dir",
        type=Path,
        help="a top100_coverage output dir: run the checks on --company-id's rows and open every failing cell there",
    )
    ap.add_argument("--company-id", help="with --self-check-dir")
    a = ap.parse_args(argv)
    if a.self_check_dir:
        if not (a.company_id and a.cik):
            ap.error("--self-check-dir needs --company-id and --cik")
        return self_check(a.self_check_dir, a.company_id, a.cik)
    if not (a.live or a.bundle or a.emit_sql):
        ap.error("one of --live, --bundle, --emit-sql is required")
    company_id = None
    req = None
    if a.request:
        req = dc.read_request(a.request)
        a.ticker, company_id = req.ticker, req.company_id
        a.coverage = a.coverage or REPO / req.coverage
        if dc.sha256(a.coverage) != req.sha256:
            ap.error(
                f"{a.coverage}: sha256 differs from the request; the file changed after the gate ran"
            )
    if not (a.ticker and a.coverage):
        ap.error("give --request, or --ticker and --coverage")
    if not a.cik and not (a.live and company_id is not None):
        ap.error("--cik is required unless --live with --request")
    t = a.ticker.upper()

    if a.emit_sql:
        n = 0 if a.mechanical else dc.DRAW_SIZE
        print(dc.bundle_sql(a.cik, dc.plan(t, a.coverage, a.seed, n)))
        return 0
    if a.live:
        from scrooner_pipeline.db.connection import get_connection

        with get_connection() as conn:
            assert a.cik or company_id is not None  # argparse checks above
            cik = a.cik or dc.resolve_cik(conn, company_id or 0)
            run = dc.certify(
                t, cik, a.coverage, dc.SqlFactSource(conn), a.seed, a.mechanical
            )
    else:
        raw = json.loads(a.bundle.read_text())
        bundle = raw[0]["bundle"] if isinstance(raw, list) else raw.get("bundle", raw)
        run = dc.certify(
            t, a.cik, a.coverage, dc.BundleFactSource(bundle), a.seed, a.mechanical
        )

    a.out_dir.mkdir(parents=True, exist_ok=True)
    if a.mechanical:
        md = a.out_dir / f"{t}-mechanical-{a.date}.md"
        md.write_text(dc.render(run, a.date, a.approver))
        with open(
            a.out_dir / f"{t}-mechanical-{a.date}-evidence.csv", "w", newline=""
        ) as fh:
            csv.writer(fh).writerows(dc.evidence_rows(run))
        print(f"mechanical {run.verdict} {t}; wrote {md}")
        return {"PASS": 0, "FAIL": 1}.get(run.verdict, 2)
    md = a.out_dir / f"{t}-display-cert-{a.date}.md"
    md.write_text(dc.render(run, a.date))
    # machine-readable certificate for the registry loader (schema display-certificate/1)
    (a.out_dir / f"{t}-display-cert-{a.date}.json").write_text(
        json.dumps(dc.certificate(run, req, a.date, a.approver), indent=1) + "\n"
    )
    with open(
        a.out_dir / f"{t}-display-cert-{a.date}-evidence.csv", "w", newline=""
    ) as fh:
        csv.writer(fh).writerows(dc.evidence_rows(run))
    if not a.no_registry:
        n, k = len(run.shown), run.errors
        dc.record_verdict(
            a.registry,
            {
                "ticker": t,
                "date": a.date,
                "verdict": run.verdict,
                "coverage_sha256": run.coverage_sha256,
                "seed": run.seed,
                "n": n,
                "errors": k,
                "upper_bound_95": f"{dc.clopper_pearson_upper(k, n):.6f}",
                "approver": a.approver,
            },
        )
        pn, pk, pub = dc.pooled_bound(a.registry)
        print(f"pooled over PASS companies: {pk}/{pn} wrong, 95% upper bound {pub:.4%}")
    print(dc.to_json(run))
    print(f"wrote {md}")
    return {"PASS": 0, "FAIL": 1}.get(run.verdict, 2)


def _read(path: Path) -> tuple[list[str], list[dict]]:
    with open(path, newline="") as fh:
        rd = csv.DictReader(fh)
        return list(rd.fieldnames or []), list(rd)


def _write(path: Path, fields: list[str], rows: list[dict]) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    tmp.replace(path)


def self_check(cov_dir: Path, company_id: str, cik: str, source=None) -> int:
    """Run certify() on one company's rows of cov_dir/top100-coverage.csv and write the failures back as OPEN cells:
    the export, the newest top100-open-shown-cells-*.csv (rows appended with work=verifier_check) and the summary row
    (display counts recomputed, gate_ready no when anything opened or the checks could not run)."""
    cov = cov_dir / "top100-coverage.csv"
    summ = cov_dir / "top100-coverage-summary.csv"
    fields, rows = _read(cov)
    mine = [r for r in rows if r.get("company_id") == str(company_id)]
    if not mine:
        print(f"self-check {company_id}: no rows in {cov}")
        return 3
    ticker = mine[0]["ticker"]
    one = cov_dir / f".self-check-{company_id}.csv"
    _write(one, fields, mine)
    findings, company, err = [], [], ""
    try:
        if source is None:
            from scrooner_pipeline.db.connection import get_connection

            with get_connection() as conn:
                conn.read_only = True
                run = dc.certify(ticker, cik, one, dc.SqlFactSource(conn))
                conn.rollback()
        else:
            run = dc.certify(ticker, cik, one, source)
        findings = dc.self_check_findings(run)
        review = [f for f in run.gate + run.hides if f.severity == "REVIEW"] + [
            dc.Finding(k, *s.cell.key, "REVIEW", s.result + ": " + s.evidence)
            for k, lst in (("shown", run.shown), ("derived", run.derived))
            for s in lst
            if s.result in ("LOCATOR", "NOT_FOUND")
        ]
    except Exception as e:  # noqa: BLE001 -- the checks could not run: never a pass
        err, review = f"{type(e).__name__}: {e}"[:300], []
    finally:
        one.unlink(missing_ok=True)
    opened, company = dc.apply_self_check(mine, findings)
    with open(cov_dir / f"verifier-self-check-{company_id}.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(
            ["ticker", "check", "data_point", "fiscal_year", "severity", "detail"]
        )
        for f in findings + review:
            w.writerow(
                [ticker, f.check, f.data_point, f.fiscal_year, f.severity, f.detail]
            )
        if err:
            w.writerow([ticker, "error", "*", "*", "FAIL", err])
    _write(
        cov, fields, rows
    )  # `mine` are the same dicts: opened cells are OPEN in the export now
    opens = sorted(cov_dir.glob("top100-open-shown-cells-*.csv"))
    if opened and opens:
        ofields, orows = _read(opens[-1])
        orows += [{**r, "work": dc.SELF_CHECK_WORK} for r in opened]
        _write(opens[-1], ofields, orows)
    if summ.exists():
        sfields, srows = _read(summ)
        for s in srows:
            if s.get("company_id") != str(company_id):
                continue
            shown = sum(1 for r in mine if r.get("display") in (dc.SHOWN, dc.OPEN))
            vals = sum(1 for r in mine if r.get("display") == dc.SHOWN)
            s.update(
                shown_cells=str(shown),
                shown_values=str(vals),
                open_shown=str(sum(1 for r in mine if r.get("display") == dc.OPEN)),
                hidden_rows=str(
                    len(
                        {
                            r["data_point"]
                            for r in mine
                            if r.get("display") == dc.HIDDEN_ROW
                        }
                    )
                ),
                hidden_years=str(
                    sum(1 for r in mine if r.get("display") == dc.HIDDEN_YEAR)
                ),
                pct_shown_values=f"{100 * vals / shown:.1f}" if shown else "",
            )
            if opened or company or err:
                s["gate_ready"] = "no"
                why = (
                    f"{SELF_NOTE}: {len(opened)} opened"
                    + (f", {company[0].detail}" if company else "")
                    + (f", error {err}" if err else "")
                )
                s["note"] = f"{s.get('note')}; {why}" if s.get("note") else why
        _write(summ, sfields, srows)
    print(
        f"verifier self-check {ticker}: {len(findings)} failure(s), {len(opened)} cell(s) opened, "
        f"{len(review)} review item(s){', company-level: ' + company[0].detail if company else ''}{', ERROR ' + err if err else ''}"
    )
    return 3 if err else 0


SELF_NOTE = "verifier self-check"


if __name__ == "__main__":
    sys.exit(main())
