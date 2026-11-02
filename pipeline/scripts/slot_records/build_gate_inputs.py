"""Build the inputs of bs_port_gate.sh from the fsn-notes bucket (READ ONLY: no database, no bucket writes).

  <period_dir>/<p>/<p>_{sub,pre,num,cal}.tsv.zst   per-period extracts filtered to the cohort's filings
                                                   (registrant or co-registrant in sub.cik/aciks, all forms)
  <companies_dir>/<cik10>/                         fsn_store.shard output (company directories)

usage: build_gate_inputs.py <cohort.csv> <period_dir> <companies_dir> <cache_dir> [periods,comma,list]
Needs SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in the environment and `zstd` on PATH.
"""
import csv
import shutil
import subprocess
import sys
from pathlib import Path

from scrooner_pipeline.fsn_store import shard


def filter_table(src: Path, dst: Path, keep) -> int:
    """Rows of a zstd TSV whose keep(header_index, fields) is true; header kept. Returns rows written."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    rd = subprocess.Popen(["zstd", "-dc", str(src)], stdout=subprocess.PIPE)
    wr = subprocess.Popen(["zstd", "-q", "-f", "-o", str(dst)], stdin=subprocess.PIPE)
    assert rd.stdout is not None and wr.stdin is not None
    header = rd.stdout.readline()
    wr.stdin.write(header)
    idx = {c: i for i, c in enumerate(header.decode("utf-8").rstrip("\r\n").split("\t"))}
    n = 0
    for line in rd.stdout:
        if keep(idx, line.decode("utf-8", "replace").rstrip("\r\n").split("\t")):
            wr.stdin.write(line)
            n += 1
    wr.stdin.close()
    if wr.wait() or rd.wait():
        raise SystemExit(f"zstd failed on {src}")
    return n


def main() -> None:
    cohort, per, comp, cache = (Path(a) for a in sys.argv[1:5])
    ciks = {r["cik"].zfill(10) for r in csv.DictReader(open(cohort))}
    periods = sys.argv[5].split(",") if len(sys.argv) > 5 else shard.list_periods()
    print(f"cohort {len(ciks)} companies, {len(periods)} periods", flush=True)
    for p in periods:
        paths = {t: shard.download(p, t, cache) for t in ("sub", "pre", "num", "cal")}
        adshs: set[str] = set()

        def keep_sub(i, f):
            mine = {f[i["cik"]].zfill(10)} | {c.zfill(10) for c in f[i["aciks"]].split() if c}
            if mine & ciks:
                adshs.add(f[i["adsh"]])
                return True
            return False

        n = filter_table(paths["sub"], per / p / f"{p}_sub.tsv.zst", keep_sub)
        for t in ("pre", "num", "cal"):
            filter_table(paths[t], per / p / f"{p}_{t}.tsv.zst", lambda i, f: f[i["adsh"]] in adshs)
        shutil.rmtree(cache / p, ignore_errors=True)
        print(f"  {p}: {n} filings", flush=True)
    out = shard.run(comp, {c: None for c in sorted(ciks)}, periods, cache / "_shard")
    print("shard:", out, flush=True)
    if not out["complete"] or out["companies"] != len(ciks):
        raise SystemExit(f"shard incomplete: {out} (expected {len(ciks)} companies)")


if __name__ == "__main__":
    main()
