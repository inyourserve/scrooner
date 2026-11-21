"""Build data-team/47-fsn-store/note_report_lookup.csv from the coverage export + the local SEC FSN quarter cache.

usage: build_note_report_lookup.py <top100-coverage.csv or glob of several> <fsn cache dir> [out.csv] [--edgar] [--attempted file]
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
            if (
                "--parts-only" not in sys.argv
                and r["locator_source"] == "note_fact_report_not_stored"
                and r["accession"]
            ):
                for t in r["tag"].split(","):
                    if t.strip():
                        wanted.add((r["accession"], t.strip()))
            for part in (r.get("parts") or "").split(";"):
                m = PART.match(part.strip())
                if m and not m.group(3):  # a part with no R page
                    wanted.add((m.group(2), m.group(1)))
    return wanted


def edgar_cik(acc: str, ciks: dict[str, str]) -> int:
    """The CIK for an EDGAR archive path. The accession prefix is the FILER AGENT's id, not the company's
    (0001628280-26-005939 is PM's, under agent 1628280: the path 404s), so the company CIK comes first (fsn.filing.cik)
    and the prefix is only the fallback for an accession the store does not know."""
    return int(ciks.get(acc) or acc.split("-")[0])


def read_ciks(accessions: set[str]) -> dict[str, str]:
    """accession -> registrant CIK from fsn.filing (read-only; empty when the database is not reachable)."""
    if not accessions:
        return {}
    try:
        from scrooner_pipeline.db.connection import get_connection

        with get_connection() as conn:
            conn.execute("set transaction read only")
            return dict(
                conn.execute(
                    "select accession, cik from fsn.filing where accession = any(%s)",
                    (sorted(accessions),),
                ).fetchall()
            )
    except Exception as e:  # noqa: BLE001
        print("cik lookup failed, using accession prefixes:", repr(e)[:100], flush=True)
        return {}


def write_rows(out: Path, rows: list[dict[str, object]]) -> None:
    rows = sorted(rows, key=lambda r: (str(r["accession"]), str(r["tag"])))
    tmp = out.with_suffix(".tmp")
    with tmp.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=nl.COLUMNS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    tmp.replace(out)


def main(covs: list[Path], cache: Path, out: Path, attempted: Path | None) -> int:
    wanted = wanted_pairs(covs)
    have = nl.load_lookup(out) if out.exists() else {}
    allrows: list[dict[str, object]] = (
        list(csv.DictReader(out.open(newline=""))) if out.exists() else []
    )
    rows, missing = nl.build_rows(cache, {k for k in wanted if k not in have})
    allrows += rows
    if rows:
        write_rows(out, allrows)
    if missing and "--edgar" in sys.argv:  # filings newer than the cached SEC data sets
        import os

        from scrooner_pipeline.fsn_store.edgar_fetch import EdgarClient

        # the SEC budget is 2/s in total for every session on the machine (common/sec_rate.py clamps the client)
        client = EdgarClient(os.environ["SEC_USER_AGENT"], max_per_second=2.0)
        done = (
            set(attempted.read_text().split())
            if attempted and attempted.exists()
            else set()
        )
        by_acc: dict[str, set[str]] = {}
        for a, t in missing:
            by_acc.setdefault(a, set()).add(t)
        todo = [a for a in sorted(by_acc) if a not in done]
        if (
            "--limit" in sys.argv
        ):  # at most N filings per run (the driver commits between runs)
            todo = todo[: int(sys.argv[sys.argv.index("--limit") + 1])]
        ciks = read_ciks(set(todo))
        for i, a in enumerate(todo, 1):
            try:
                got = nl.scan_edgar(client, edgar_cik(a, ciks), a, by_acc[a])
            except Exception as e:  # noqa: BLE001
                print("edgar failed", a, repr(e)[:120], flush=True)
                continue
            for t, (rep, n) in got.items():
                allrows.append(
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
            write_rows(out, allrows)  # checkpoint after each accession
            if attempted:
                with attempted.open("a") as fh:
                    fh.write(a + "\n")
            print(
                f"[{i}/{len(todo)}] {a} found {len(got)}/{len(by_acc[a])}", flush=True
            )
    print(f"wanted {len(wanted)} total {len(allrows)} not_found {len(missing)}")
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
    att = None
    if (
        "--attempted" in sys.argv
    ):  # accessions already scanned (found or not): skipped on restart
        att = Path(sys.argv[sys.argv.index("--attempted") + 1])
    sys.exit(main(covs, Path(sys.argv[2]), out, att))
