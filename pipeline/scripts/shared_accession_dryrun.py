"""READ-ONLY dry-run of rule entity.shared_accession_primary_filer@1 over the
whole population (normalizer/shared_accession.py). Writes NOTHING to Postgres.

What it does, in order (each phase checkpoints to --workdir so a restart resumes):
  A. submissions: latest raw.sec_submissions batch of every core.company CIK,
     downloaded from storage (HTTP threads, not DB connections), parsed with the
     normalizer's own _parse_filings_block -> accession -> {cik: form}.
  B. carriers: for registrants of SHARED accessions only, the latest companyfacts
     payload; which shared accessions it carries, with the (fy, fp, end) periods
     and entry counts behind each.
  C. headers: SEC -index-headers.html of each shared periodic/carried accession,
     first FILER block's CENTRAL INDEX KEY (SECClient, shared rate limiter).
  D. decisions + impact: plan_decisions; current core.filing owner per accession;
     core.fact rows of the current owner on accessions that would move (what a
     co-registrant could LOSE on re-normalization); registrant rows that WOULD be
     written to core.filing_registrant; status effect on the named companies.

One Postgres connection, statement_timeout set per statement, chunked reads only.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import psycopg

from scrooner_pipeline.collector.storage import SupabaseStorageClient, strip_bucket_prefix
from scrooner_pipeline.common.sec_client import SECClient
from scrooner_pipeline.company_master.status import QUALIFYING_FORMS
from scrooner_pipeline.normalizer import shared_accession as sa
from scrooner_pipeline.normalizer.identity import _parse_filings_block

HEADER_CIK_RE = re.compile(r"FILER:.*?CENTRAL INDEX KEY:\s*(\d{10})", re.S)
NAMED = {  # the nine cohort companies with NO financial data (task, 2026-10-31)
    694: "ETR", 1008: "ES", 1081: "SO", 1525: "CMS", 1576: "EIX",
    2144: "AEE", 2503: "SRE", 3562: "TXNM", 5394: "CTVA",
}


def log(msg: str) -> None:
    print(time.strftime("%H:%M:%S"), msg, flush=True)


def chunks(seq, n):
    seq = list(seq)
    for i in range(0, len(seq), n):
        yield seq[i : i + n]


def q(conn, sql, params=None, timeout="5min"):
    with conn.cursor() as cur:
        cur.execute(f"set statement_timeout = '{timeout}'")
        cur.execute(sql, params)
        return cur.fetchall()


# ---- phase A: submissions ----------------------------------------------------


def latest_submission_paths(conn) -> dict[str, list[str]]:
    rows = q(
        conn,
        """
        select s.cik, s.storage_path
        from raw.sec_submissions s
        join (select cik, max(fetched_at) as fetched_at from raw.sec_submissions
              where cik in (select cik from core.company) group by cik) m
          on m.cik = s.cik and m.fetched_at = s.fetched_at
        order by s.cik, s.storage_path
        """,
        timeout="10min",
    )
    out: dict[str, list[str]] = defaultdict(list)
    for cik, path in rows:
        out[cik].append(path)
    return out


def _download_json(storage, path):
    return json.loads(storage.download(strip_bucket_prefix(path)))


def phase_a(conn, workdir: Path, threads: int) -> dict[str, list[dict]]:
    ckpt = workdir / "A_filings.jsonl"
    done: dict[str, list[dict]] = {}
    if ckpt.exists():
        for line in ckpt.open():
            rec = json.loads(line)
            done[rec["cik"]] = rec["filings"]
        log(f"A: resumed {len(done)} CIKs from checkpoint")
    paths = latest_submission_paths(conn)
    todo = {cik: p for cik, p in paths.items() if cik not in done}
    log(f"A: {len(paths)} CIKs with submissions, {len(todo)} to download")

    def work(cik, plist):
        filings = []
        with SupabaseStorageClient() as storage:
            for p in plist:
                payload = _download_json(storage, p)
                block = payload["filings"]["recent"] if "filings" in payload else payload
                for f in _parse_filings_block(block):
                    filings.append(
                        {
                            "accession_number": f["accession_number"],
                            "form": f["form"],
                            "filing_date": f["filing_date"].isoformat() if f["filing_date"] else None,
                            "period_of_report": f["period_of_report"].isoformat()
                            if f["period_of_report"]
                            else None,
                        }
                    )
        return cik, filings

    n = 0
    with ckpt.open("a") as out, ThreadPoolExecutor(threads) as ex:
        futs = [ex.submit(work, c, p) for c, p in sorted(todo.items())]
        for fut in as_completed(futs):
            try:
                cik, filings = fut.result()
            except Exception as exc:  # noqa: BLE001
                log(f"A: download failed: {exc!r}")
                continue
            done[cik] = filings
            out.write(json.dumps({"cik": cik, "filings": filings}) + "\n")
            n += 1
            if n % 250 == 0:
                out.flush()
                log(f"A: {n}/{len(todo)} downloaded")
    log(f"A: done, {len(done)} CIKs")
    return done


# ---- phase B: carriers -------------------------------------------------------


def phase_b(conn, workdir: Path, wanted_by_cik: dict[str, set[str]], threads: int) -> dict:
    """cik -> {accession: {"entries": n, "periods": [[fy, fp, end], ...]}}"""
    ckpt = workdir / "B_carriers.jsonl"
    done: dict[str, dict] = {}
    if ckpt.exists():
        for line in ckpt.open():
            rec = json.loads(line)
            done[rec["cik"]] = rec["carried"]
        log(f"B: resumed {len(done)} CIKs")
    todo = sorted(c for c in wanted_by_cik if c not in done)
    rows = q(
        conn,
        """
        select distinct on (cik) cik, storage_path from raw.sec_companyfacts
        where cik = any(%s) order by cik, fetched_at desc
        """,
        (todo,),
    )
    path_by_cik = dict(rows)
    log(f"B: {len(todo)} registrant CIKs to scan, {len(path_by_cik)} have companyfacts")

    def work(cik):
        wanted = wanted_by_cik[cik]
        carried: dict[str, dict] = {}
        path = path_by_cik.get(cik)
        if path is None:
            return cik, carried, "no_companyfacts"
        with SupabaseStorageClient() as storage:
            payload = _download_json(storage, path)
        periods: dict[str, set] = defaultdict(set)
        entries: dict[str, int] = defaultdict(int)
        for _tax, concepts in payload.get("facts", {}).items():
            for _name, body in concepts.items():
                for _unit, items in body.get("units", {}).items():
                    for e in items:
                        accn = e.get("accn")
                        if accn in wanted:
                            entries[accn] += 1
                            periods[accn].add((e.get("fy"), e.get("fp"), e.get("end")))
        for accn in entries:
            carried[accn] = {"entries": entries[accn], "periods": sorted(
                [list(p) for p in periods[accn]], key=lambda x: (str(x[2]), str(x[0]), str(x[1]))
            )}
        return cik, carried, "ok"

    with ckpt.open("a") as out, ThreadPoolExecutor(threads) as ex:
        futs = [ex.submit(work, c) for c in todo]
        for i, fut in enumerate(as_completed(futs), 1):
            try:
                cik, carried, st = fut.result()
            except Exception as exc:  # noqa: BLE001
                log(f"B: failed: {exc!r}")
                continue
            done[cik] = carried
            out.write(json.dumps({"cik": cik, "carried": carried, "status": st}) + "\n")
            if i % 50 == 0:
                out.flush()
                log(f"B: {i}/{len(todo)}")
    log("B: done")
    return done


# ---- phase C: headers --------------------------------------------------------


def phase_c(workdir: Path, accessions: list[str]) -> dict[str, str | None]:
    ckpt = workdir / "C_headers.jsonl"
    done: dict[str, str | None] = {}
    if ckpt.exists():
        for line in ckpt.open():
            rec = json.loads(line)
            done[rec["accession_number"]] = rec["header_first_filer"]
        log(f"C: resumed {len(done)} headers")
    todo = [a for a in accessions if a not in done]
    log(f"C: {len(todo)} headers to fetch from SEC")
    with ckpt.open("a") as out, SECClient() as sec:
        for i, acc in enumerate(todo, 1):
            prefix = acc.split("-", 1)[0]
            nodash = acc.replace("-", "")
            url = f"https://www.sec.gov/Archives/edgar/data/{int(prefix)}/{nodash}/{acc}-index-headers.html"
            first = None
            err = None
            try:
                resp = sec.get(url)
                if resp.status_code == 200:
                    m = HEADER_CIK_RE.search(resp.text)
                    first = m.group(1) if m else None
                else:
                    err = f"http_{resp.status_code}"
            except Exception as exc:  # noqa: BLE001
                err = repr(exc)[:120]
            done[acc] = first
            out.write(
                json.dumps({"accession_number": acc, "header_first_filer": first, "error": err}) + "\n"
            )
            if i % 100 == 0:
                out.flush()
                log(f"C: {i}/{len(todo)}")
    log("C: done")
    return done


# ---- phase D: decisions and impact ------------------------------------------


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workdir", required=True)
    ap.add_argument("--threads", type=int, default=6)
    ap.add_argument("--skip-headers", action="store_true")
    args = ap.parse_args()
    workdir = Path(args.workdir)
    workdir.mkdir(parents=True, exist_ok=True)

    conn = psycopg.connect(os.environ["DATABASE_URL"], connect_timeout=30)
    conn.read_only = True  # belt and braces: the session refuses writes
    log("connected (read-only session)")

    companies = q(conn, "select id, cik, company_name, status, status_reason from core.company")
    id_by_cik = {cik: cid for cid, cik, *_ in companies}
    name_by_id = {cid: name for cid, _c, name, *_ in companies}
    status_by_id = {cid: (st, reason) for cid, _c, _n, st, reason in companies}

    filings_by_cik = phase_a(conn, workdir, args.threads)
    shared = sa.registrants_by_accession(filings_by_cik)
    log(f"shared accessions (2+ registrants): {len(shared)}")
    wanted_by_cik: dict[str, set[str]] = defaultdict(set)
    for acc, regs in shared.items():
        for cik in regs:
            wanted_by_cik[cik].add(acc)

    carried_by_cik = phase_b(conn, workdir, wanted_by_cik, args.threads)
    carriers: dict[str, set[str]] = defaultdict(set)
    for cik, carried in carried_by_cik.items():
        for acc in carried:
            carriers[acc].add(cik)

    headers: dict[str, str | None] = {}
    if not args.skip_headers:
        need = sorted(
            a for a, regs in shared.items()
            if next(iter(regs.values())) in sa.PERIODIC_FORMS or a in carriers
        )
        headers = phase_c(workdir, need)

    decisions = sa.plan_decisions(shared, carriers, headers)
    summary = sa.summarize(decisions)
    log(f"decisions: {summary}")

    # current owner / filing id per shared accession
    owner: dict[str, tuple[int, int]] = {}
    for part in chunks(sorted(shared), 2000):
        for acc, fid, cid in q(
            conn,
            "select accession_number, id, company_id from core.filing where accession_number = any(%s)",
            (part,),
        ):
            owner[acc] = (fid, cid)
    log(f"owner rows: {len(owner)} of {len(shared)} shared accessions exist in core.filing")

    form_by_acc = {a: next(iter(r.values())) for a, r in shared.items()}
    date_by_acc: dict[str, str | None] = {}
    for cik, fl in filings_by_cik.items():
        for f in fl:
            if f["accession_number"] in shared and f["accession_number"] not in date_by_acc:
                date_by_acc[f["accession_number"]] = f["filing_date"]

    moves = []  # accessions whose core.filing.company_id would change
    gain: dict[int, dict] = defaultdict(lambda: {"accessions": 0, "entries": 0, "periods": set(), "forms": defaultdict(int)})
    conflicts = []
    for d in decisions:
        if d.primary_cik is None:
            continue
        if sa.carrier_conflict(d):
            conflicts.append(d)
        pid = id_by_cik.get(d.primary_cik)
        cur = owner.get(d.accession_number)
        if pid is None or cur is None:
            continue
        fid, cur_cid = cur
        if cur_cid != pid:
            moves.append((d.accession_number, fid, cur_cid, pid, d.basis))
            carried = carried_by_cik.get(d.primary_cik, {}).get(d.accession_number)
            g = gain[pid]
            g["accessions"] += 1
            g["forms"][form_by_acc[d.accession_number]] += 1
            if carried:
                g["entries"] += carried["entries"]
                g["periods"].update(tuple(p) for p in carried["periods"])
    log(f"accessions that would move owner: {len(moves)}; carrier conflicts: {len(conflicts)}")

    # what the current owner could LOSE: its core.fact rows on moving filings
    lose: dict[int, int] = defaultdict(int)
    fids_by_owner: dict[int, list[int]] = defaultdict(list)
    for _acc, fid, cur_cid, _pid, _b in moves:
        fids_by_owner[cur_cid].append(fid)
    for cur_cid, fids in fids_by_owner.items():
        for part in chunks(fids, 500):
            (n,) = q(
                conn,
                "select count(*) from core.fact where filing_id = any(%s) and company_id = %s",
                (part, cur_cid),
                timeout="10min",
            )[0]
            lose[cur_cid] += n
    log(f"owners with core.fact rows on moving filings: {sum(1 for v in lose.values() if v)}")

    reg_rows = sa.registrant_rows(decisions, id_by_cik)
    roles = defaultdict(int)
    for r in reg_rows:
        roles[r["role"]] += 1
    unmapped = sum(1 for r in reg_rows if r["company_id"] is None)

    # status effect: latest qualifying filing date via ownership vs via registrant link
    def latest_via_link(cid: int) -> str | None:
        best = None
        for d in decisions:
            if d.primary_cik is None or form_by_acc[d.accession_number] not in QUALIFYING_FORMS:
                continue
            if cid in {id_by_cik.get(c) for c in d.registrant_ciks}:
                fd = date_by_acc.get(d.accession_number)
                if fd and (best is None or fd > best):
                    best = fd
        return best

    named_report = {}
    for cid, tkr in NAMED.items():
        g = gain.get(cid)
        named_report[tkr] = {
            "company_id": cid,
            "name": name_by_id.get(cid),
            "status_now": status_by_id.get(cid),
            "latest_qualifying_filing_via_registrant_link": latest_via_link(cid),
            "accessions_recovered": g["accessions"] if g else 0,
            "forms_recovered": dict(g["forms"]) if g else {},
            "fact_entries_recovered": g["entries"] if g else 0,
            "periods_recovered": len(g["periods"]) if g else 0,
            "period_end_range": [min(p[2] for p in g["periods"] if p[2]), max(p[2] for p in g["periods"] if p[2])]
            if g and any(p[2] for p in g["periods"]) else None,
            "shared_accessions_as_registrant": sum(
                1 for d in decisions if cid in {id_by_cik.get(c) for c in d.registrant_ciks}
            ),
            "quarantined_as_registrant": sum(
                1 for d in decisions
                if d.primary_cik is None and cid in {id_by_cik.get(c) for c in d.registrant_ciks}
            ),
        }

    gain_report = sorted(
        (
            {
                "company_id": cid,
                "name": name_by_id.get(cid),
                "status_now": status_by_id.get(cid, (None, None))[0],
                "accessions_recovered": g["accessions"],
                "forms": dict(g["forms"]),
                "fact_entries_recovered": g["entries"],
                "periods_recovered": len(g["periods"]),
            }
            for cid, g in gain.items()
        ),
        key=lambda r: -r["fact_entries_recovered"],
    )
    lose_report = sorted(
        (
            {
                "company_id": cid,
                "name": name_by_id.get(cid),
                "filings_losing_ownership": len(fids_by_owner[cid]),
                "core_fact_rows_on_those_filings": n,
            }
            for cid, n in lose.items()
        ),
        key=lambda r: -r["core_fact_rows_on_those_filings"],
    )
    quarantine_examples = defaultdict(list)
    for d in decisions:
        if d.primary_cik is None and len(quarantine_examples[d.quarantine_reason]) < 5:
            quarantine_examples[d.quarantine_reason].append(
                {"accession": d.accession_number, "form": form_by_acc[d.accession_number],
                 "registrants": list(d.registrant_ciks), "carriers": list(d.carriers),
                 "header": headers.get(d.accession_number)}
            )

    report = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "read_only": True,
        "population_ciks": len(filings_by_cik),
        "shared_accessions": len(shared),
        "shared_by_form": dict(sorted(defaultdict(int, {f: sum(1 for a in shared if form_by_acc[a] == f) for f in set(form_by_acc.values())}).items())),
        "decisions": summary,
        "headers_fetched": len(headers),
        "headers_missing": sum(1 for v in headers.values() if v is None),
        "shared_in_core_filing": len(owner),
        "filing_rows_that_would_move_owner": len(moves),
        "carrier_conflicts": len(conflicts),
        "carrier_conflict_examples": [
            {"accession": d.accession_number, "form": form_by_acc[d.accession_number],
             "primary": d.primary_cik, "carriers": list(d.carriers), "basis": d.basis}
            for d in conflicts[:10]
        ],
        "filing_registrant_rows_that_would_be_written": {"total": len(reg_rows), **roles,
                                                        "with_null_company_id": unmapped},
        "companies_gaining": gain_report,
        "companies_losing_ownership": lose_report,
        "named_nine": named_report,
        "quarantine_examples": dict(quarantine_examples),
        "moves_sample": [
            {"accession": a, "from_company_id": c, "to_company_id": p, "basis": b} for a, _f, c, p, b in moves[:25]
        ],
    }
    (workdir / "REPORT.json").write_text(json.dumps(report, indent=2, default=str))
    (workdir / "moves.jsonl").write_text(
        "".join(json.dumps({"accession": a, "filing_id": f, "from": c, "to": p, "basis": b}) + "\n" for a, f, c, p, b in moves)
    )
    log(f"REPORT written: {workdir / 'REPORT.json'}")
    conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
