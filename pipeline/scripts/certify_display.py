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
An AUTO_MISMATCH of the automated draw checker is one of those failures (check draw_check).

Automated draw checker (certification/draw_check.py, 2026-11-22): every drawn cell is checked against the cited
filing's own XBRL facts (AUTO_MATCH / AUTO_MISMATCH / NEEDS_READ). Only NEEDS_READ and AUTO_MISMATCH cells go to a
person or agent read:

  # the reads of those cells (CSV: data_point, fiscal_year, verdict MATCH|MISMATCH, reader, evidence)
  python pipeline/scripts/certify_display.py --request R.md --live --reads READS.csv --out-dir OUT
  # the verifier samples the checker: a seeded 5% of AUTO_MATCH cells for an agent read, then its agreement
  python pipeline/scripts/certify_display.py --request R.md --live --audit-out AUDIT.csv --out-dir OUT
  python pipeline/scripts/certify_display.py --request R.md --live --audit-reads AUDIT.csv --out-dir OUT
  # read-only run over every company of a top100-coverage.csv: outcomes, mismatches, needs-read, runtime per company
  python pipeline/scripts/certify_display.py --draw-check-all data-team/strategy/top100-coverage.csv --out-dir OUT

Identity web (proof/identities.py, 2026-11-22): every accounting identity over every company x fiscal year, read-only.
The self-check opens each BREAK's suspect cell (check identity); a drawn NEEDS_READ cell an exact identity corroborates
is AUTO_MATCH (method identity).

  # every company of the export, and (--resolver) the same identities over the resolver files read as cells
  python pipeline/scripts/certify_display.py --identity-web-all data-team/strategy/top100-coverage.csv --out-dir OUT
  python pipeline/scripts/certify_display.py --identity-web-all data-team/strategy/top100-coverage.csv --resolver \
      data-team/tags/line_map/resolver --out-dir OUT
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from scrooner_pipeline.certification import display_cert as dc
from scrooner_pipeline.certification import draw_check as dck

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
    ap.add_argument(
        "--reads",
        type=Path,
        help="filing reads of the drawn cells the automated checker sent to a read (draw_check.load_reads)",
    )
    ap.add_argument(
        "--audit-out",
        type=Path,
        help="write the checker audit sheet: a seeded 5%% of AUTO_MATCH cells for an agent filing read",
    )
    ap.add_argument(
        "--audit-reads",
        type=Path,
        help="the filled audit sheet: report the agent reads' agreement with the machine in the certificate",
    )
    ap.add_argument(
        "--draw-check-all",
        type=Path,
        help="a top100-coverage.csv: run the automated draw checker on every company's draw (read-only), with --out-dir",
    )
    ap.add_argument(
        "--identity-web-all",
        type=Path,
        help="a top100-coverage.csv: run the identity web over every company x fiscal year (read-only), with --out-dir",
    )
    ap.add_argument(
        "--resolver",
        type=Path,
        help="with --identity-web-all: the resolver directory (one <TICKER>.csv per company), judged as shown cells",
    )
    a = ap.parse_args(argv)
    if a.identity_web_all:
        return identity_web_all(a.identity_web_all, a.out_dir, a.date, a.resolver)
    if a.draw_check_all:
        return draw_check_all(a.draw_check_all, a.out_dir, a.date)
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
                t,
                cik,
                a.coverage,
                dc.SqlFactSource(conn),
                a.seed,
                a.mechanical,
                reads=dck.load_reads(a.reads),
            )
    else:
        raw = json.loads(a.bundle.read_text())
        bundle = raw[0]["bundle"] if isinstance(raw, list) else raw.get("bundle", raw)
        run = dc.certify(
            t,
            a.cik,
            a.coverage,
            dc.BundleFactSource(bundle),
            a.seed,
            a.mechanical,
            reads=dck.load_reads(a.reads),
        )
    if run.auto is not None:
        sample = dck.audit_sample(run.auto, run.seed)
        if a.audit_out:
            dck.write_audit_request(a.audit_out, sample)
            print(
                f"checker audit: {len(sample)} AUTO_MATCH cell(s) for an agent read -> {a.audit_out}"
            )
        if a.audit_reads:
            run.audit = dck.audit_agreement(sample, dck.load_reads(a.audit_reads))
            print(f"checker audit agreement: {json.dumps(run.audit)}")

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
        review = (
            [f for f in run.gate + run.hides if f.severity == "REVIEW"]
            + [
                dc.Finding(k, *s.cell.key, "REVIEW", s.result + ": " + s.evidence)
                for k, lst in (("shown", run.shown), ("derived", run.derived))
                for s in lst
                if s.result in ("LOCATOR", "NOT_FOUND")
            ]
            + [
                dc.Finding(
                    "draw_check",
                    x.data_point,
                    x.fiscal_year,
                    "REVIEW",
                    f"NEEDS_READ ({x.method}): {x.detail}",
                )
                for x in run.auto or ()
                if x.outcome == dck.NEEDS_READ
            ]
            # an identity break whose every member matches its filing fact: the filing or the operand set, not a
            # shown value; reported for the tag expert, never opened
            + [
                dc.Finding(
                    "identity",
                    ",".join(m.data_point for m in r.members),
                    r.fiscal_year,
                    "REVIEW",
                    f"FILING_BREAK {r.identity}: {r.lhs} vs {r.rhs} (tolerance {r.tolerance}); {r.detail}",
                )
                for r in run.web or ()
                if r.status == "FILING_BREAK"
            ]
            # a banded identity's break on a proven cell: a read, not an open
            + [
                dc.Finding("identity", dp, r.fiscal_year, "REVIEW", r.reason(dp))
                for r in run.web or ()
                for dp in r.suspects
                if not r.opens(dp)
            ]
        )
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

DRAW_CHECK_COLUMNS = [
    "ticker",
    "company_id",
    "data_point",
    "fiscal_year",
    "period_end",
    "badge",
    "outcome",
    "method",
    "shown_value",
    "filing_value",
    "accession",
    "detail",
]
DRAW_SUMMARY_COLUMNS = [
    "ticker",
    "company_id",
    "shown",
    "drawn",
    "auto_match",
    "auto_mismatch",
    "needs_read",
    "pct_auto_match",
    "seconds",
]


WEB_COLUMNS = [
    "source",
    "ticker",
    "company_id",
    "identity",
    "fiscal_year",
    "status",
    "suspects",
    "members",
    "lhs",
    "rhs",
    "diff",
    "tolerance",
    "detail",
]
WEB_SUMMARY_COLUMNS = [
    "source",
    "ticker",
    "company_id",
    "identity",
    "checked",
    "pass",
    "break",
    "filing_break",
    "fiscal_years",
]

RESOLVER_SERVED = ("mapped", "component_sum", "derived_not_printed")


def resolver_cells(path: Path, fy_of: dict[str, str]) -> tuple[str, list[dc.Cell]]:
    """(cik, cells) of one resolver file read as shown cells: every row with a value and a served decision; the
    fiscal year from the export's period end when known, else the period end's year; the first node's tag."""
    _f, rows = _read(path)
    cik, cells = "", []
    for r in rows:
        cik = cik or r.get("cik", "")
        if (
            r.get("decision") not in RESOLVER_SERVED
            or not (r.get("value") or "").strip()
        ):
            continue
        node = (r.get("nodes") or "").split("|")[0].split(";")[0].strip()
        tag = (
            node.split("=")[0].strip()
            if r["decision"] == "mapped" and "=" in node
            else ""
        )
        pe = r.get("period_end", "")
        cells.append(
            dc.Cell(
                r["data_point"],
                fy_of.get(pe, pe[:4]),
                pe,
                dc.SHOWN,
                dc._dec(r["value"]),
                (r.get("accession") or "").strip(),
                "",
                tag,
            )
        )
    return cik.lstrip("0"), cells


def identity_web_all(
    cov: Path, out_dir: Path, today: str, resolver: Path | None = None, source=None
) -> int:
    """The identity web over every company x fiscal year of a top100-coverage.csv (and of the resolver files), read
    only. Writes OUT/identity-web-<date>.csv (every BREAK and FILING_BREAK) and OUT/identity-web-summary-<date>.csv
    (checked / pass / break / filing_break per company x identity)."""
    _fields, rows = _read(cov)
    by: dict[str, list[dict]] = {}
    for r in rows:
        by.setdefault(r["company_id"], []).append(r)
    out_dir.mkdir(parents=True, exist_ok=True)
    conn_cm = None
    if source is None:
        from scrooner_pipeline.db.connection import get_connection

        conn_cm = get_connection()
        conn = conn_cm.__enter__()
        conn.read_only = True
        source = dc.SqlFactSource(conn, timeout_ms=60000)
    breaks, summ = [], []

    def record(kind: str, ticker: str, cid: str, results: list) -> None:
        agg: dict[str, dict[str, int]] = {}
        fys: dict[str, set[str]] = {}
        for r in results:
            a = agg.setdefault(
                r.identity, {"checked": 0, "PASS": 0, "BREAK": 0, "FILING_BREAK": 0}
            )
            a["checked"] += 1
            a[r.status] += 1
            fys.setdefault(r.identity, set()).add(r.fiscal_year)
            if r.status != "PASS":
                breaks.append(
                    {
                        "source": kind,
                        "ticker": ticker,
                        "company_id": cid,
                        "identity": r.identity,
                        "fiscal_year": r.fiscal_year,
                        "status": r.status,
                        "suspects": ";".join(r.suspects),
                        "members": "; ".join(
                            f"{m.data_point}={m.value} [{m.support}]" for m in r.members
                        ),
                        "lhs": str(r.lhs),
                        "rhs": str(r.rhs),
                        "diff": str(r.lhs - r.rhs),
                        "tolerance": str(r.tolerance),
                        "detail": r.detail,
                    }
                )
        for ident, a in sorted(agg.items()):
            summ.append(
                {
                    "source": kind,
                    "ticker": ticker,
                    "company_id": cid,
                    "identity": ident,
                    "checked": a["checked"],
                    "pass": a["PASS"],
                    "break": a["BREAK"],
                    "filing_break": a["FILING_BREAK"],
                    "fiscal_years": len(fys[ident]),
                }
            )

    try:
        for cid, mine in sorted(
            by.items(), key=lambda kv: int(kv[1][0].get("rank") or 0)
        ):
            t0 = time.monotonic()
            ticker = mine[0]["ticker"]
            one = out_dir / f".identity-web-{cid}.csv"
            _write(one, _fields, mine)
            try:
                cells = dc.read_coverage(one)
            finally:
                one.unlink(missing_ok=True)
            rpath = resolver / f"{ticker}.csv" if resolver else None
            fy_of = {c.period_end: c.fiscal_year for c in cells if c.period_end}
            rcik, rcells = (
                resolver_cells(rpath, fy_of) if rpath and rpath.is_file() else ("", [])
            )
            try:
                cik = rcik or (
                    dc.resolve_cik(source.conn, int(cid)) if conn_cm is not None else ""
                )
                got = dc.identity_web_check(cells, cik, source)
                res = got[0] if got else []
                record("export", ticker, cid, res)
                rres: list = []
                if rcells:
                    rgot = dc.identity_web_check(rcells, cik, source)
                    rres = rgot[0] if rgot else []
                    record("resolver", ticker, cid, rres)
            except Exception as e:  # noqa: BLE001 -- one company's read failing never stops the run
                print(
                    f"identity-web {ticker}: ERROR {type(e).__name__}: {e}"[:300],
                    flush=True,
                )
                res, rres = [], []
            finally:
                if conn_cm is not None:
                    source.conn.rollback()
            nb = sum(1 for r in res if r.status == "BREAK")
            print(
                f"identity-web {ticker}: {len(res)} checked, {nb} break, "
                f"{sum(1 for r in res if r.status == 'FILING_BREAK')} filing-break; resolver {len(rres)} checked, "
                f"{sum(1 for r in rres if r.status == 'BREAK')} break; {time.monotonic() - t0:.1f}s",
                flush=True,
            )
    finally:
        if conn_cm is not None:
            conn_cm.__exit__(None, None, None)
    _write(out_dir / f"identity-web-{today}.csv", WEB_COLUMNS, breaks)
    _write(out_dir / f"identity-web-summary-{today}.csv", WEB_SUMMARY_COLUMNS, summ)
    for kind in ("export", "resolver"):
        rows_k = [s for s in summ if s["source"] == kind]
        if rows_k:
            print(
                f"identity-web {kind}: {len({s['ticker'] for s in rows_k})} companies, "
                f"{sum(s['checked'] for s in rows_k)} identity x year checks, {sum(s['pass'] for s in rows_k)} pass, "
                f"{sum(s['break'] for s in rows_k)} break, {sum(s['filing_break'] for s in rows_k)} filing-break"
            )
    return 0


def draw_check_all(cov: Path, out_dir: Path, today: str, source=None) -> int:
    """The automated draw checker over every company of a top100-coverage.csv, read-only: the same seeded draw
    certify() would take (plan), checked against the cited filings' facts. Writes OUT/draw-check-<date>.csv (one row
    per drawn cell) and OUT/draw-check-summary-<date>.csv (counts and seconds per company)."""
    fields, rows = _read(cov)
    by: dict[str, list[dict]] = {}
    for r in rows:
        by.setdefault(r["company_id"], []).append(r)
    out_dir.mkdir(parents=True, exist_ok=True)
    cells_out, summ = [], []
    conn_cm = None
    if source is None:
        from scrooner_pipeline.db.connection import get_connection

        conn_cm = get_connection()
        conn = conn_cm.__enter__()
        conn.read_only = True
        source = dc.SqlFactSource(conn, timeout_ms=60000)
    try:
        for cid, mine in sorted(
            by.items(), key=lambda kv: int(kv[1][0].get("rank") or 0)
        ):
            t0 = time.monotonic()
            ticker = mine[0]["ticker"]
            one = out_dir / f".draw-check-{cid}.csv"
            _write(one, fields, mine)
            try:
                p = dc.plan(ticker, one)
            finally:
                one.unlink(missing_ok=True)
            got = source.filing_facts(*dck.needs(p.sample)) if p.sample else ([], [])
            if conn_cm is not None:
                source.conn.rollback()
            checks = dck.check_draw(p.sample, *got) if p.sample else []
            secs = time.monotonic() - t0
            k = dck.counts(checks)
            badge = {c.key: c for c in p.sample}
            for x in checks:
                c = badge[x.key]
                cells_out.append(
                    {
                        "ticker": ticker,
                        "company_id": cid,
                        "data_point": x.data_point,
                        "fiscal_year": x.fiscal_year,
                        "period_end": c.period_end,
                        "badge": c.badge or "",
                        "outcome": x.outcome,
                        "method": x.method,
                        "shown_value": "" if c.value is None else str(c.value),
                        "filing_value": ""
                        if x.filing_value is None
                        else str(x.filing_value),
                        "accession": c.accession,
                        "detail": x.detail,
                    }
                )
            summ.append(
                {
                    "ticker": ticker,
                    "company_id": cid,
                    "shown": sum(1 for c in p.cells if c.display == dc.SHOWN),
                    "drawn": len(checks),
                    "auto_match": k[dck.AUTO_MATCH],
                    "auto_mismatch": k[dck.AUTO_MISMATCH],
                    "needs_read": k[dck.NEEDS_READ],
                    "pct_auto_match": f"{100 * k[dck.AUTO_MATCH] / len(checks):.1f}"
                    if checks
                    else "",
                    "seconds": f"{secs:.2f}",
                }
            )
            print(
                f"draw-check {ticker}: {len(checks)} drawn, {k[dck.AUTO_MATCH]} auto-match, "
                f"{k[dck.AUTO_MISMATCH]} mismatch, {k[dck.NEEDS_READ]} needs read, {secs:.1f}s",
                flush=True,
            )
    finally:
        if conn_cm is not None:
            conn_cm.__exit__(None, None, None)
    _write(out_dir / f"draw-check-{today}.csv", DRAW_CHECK_COLUMNS, cells_out)
    _write(out_dir / f"draw-check-summary-{today}.csv", DRAW_SUMMARY_COLUMNS, summ)
    tot = dck.counts(
        dck.AutoCheck(r["data_point"], r["fiscal_year"], r["outcome"], "", None, "")
        for r in cells_out
    )
    n = len(cells_out)
    print(
        f"draw-check total: {n} drawn cells over {len(summ)} companies; "
        f"AUTO_MATCH {tot[dck.AUTO_MATCH]} ({100 * tot[dck.AUTO_MATCH] / n if n else 0:.1f}%), "
        f"AUTO_MISMATCH {tot[dck.AUTO_MISMATCH]}, NEEDS_READ {tot[dck.NEEDS_READ]}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
