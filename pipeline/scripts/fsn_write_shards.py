"""The FSN write's shard plan (pipeline-fsn-write.yml, seed job), run before any database connection.

The companies are cohort v1.1 in rank order (the first `limit` when set), or, with `ciks`, exactly that list
(Ritwik 2026-11-10, reload of the 98 companies lost in run 42561798991's dead shards):
  - every listed CIK must be in cohort v1.1, else the run fails here;
  - a CIK list is allowed only with stage load_map (select_write and restore stay on the done gate and the
    cohort path);
  - an empty `ciks` means the cohort path.
Shards are company_id % n (company-disjoint). Prints `shards=<json>` and `ciks_sha256=<hex>` for
$GITHUB_OUTPUT on stdout and the count, first and last CIK on stderr.

usage: python3 pipeline/scripts/fsn_write_shards.py <cohort csv> <stage> <shards> <limit or ""> <ciks or "">
Stdlib only.
"""

import csv
import hashlib
import json
import sys


class PlanError(Exception):
    pass


def plan(
    cohort: list[dict[str, str]], stage: str, shards: int, limit: str, ciks: str
) -> tuple[list[dict[str, object]], list[str], str]:
    """(shards, the CIKs in plan order, sha256 of the normalised CIK list or "" on the cohort path)."""
    rows = cohort
    listed = [c.strip().zfill(10) for c in ciks.split(",") if c.strip()]
    sha = ""
    if listed:
        if stage != "load_map":
            raise PlanError(
                f"a CIK list is allowed only with stage load_map, not {stage}"
            )
        by_cik = {r["cik"].zfill(10): r for r in cohort}
        outside = sorted(set(listed) - set(by_cik))
        if outside:
            raise PlanError(f"CIKs outside cohort v1.1: {','.join(outside)}")
        listed = sorted(set(listed))
        rows = [by_cik[c] for c in listed]
        sha = hashlib.sha256(",".join(listed).encode()).hexdigest()
    elif limit:
        rows = rows[: int(limit)]
    n = max(1, min(shards, len(rows)))
    parts: list[list[str]] = [[] for _ in range(n)]
    for r in rows:
        parts[int(r["company_id"]) % n].append(r["cik"].zfill(10))
    out = [{"i": i, "ciks": ",".join(c)} for i, c in enumerate(parts) if c]
    return out, [r["cik"].zfill(10) for r in rows], sha


def main(cohort_csv: str, stage: str, shards: str, limit: str, ciks: str) -> int:
    with open(cohort_csv) as fh:
        cohort = list(csv.DictReader(fh))
    try:
        parts, order, sha = plan(cohort, stage, int(shards), limit, ciks)
    except PlanError as exc:
        print(f"::error::{exc}", file=sys.stderr)
        return 1
    print(
        f"companies: {len(order)}; first {order[0] if order else '-'}, last {order[-1] if order else '-'}"
        + (f"; CIK list sha256 {sha}" if sha else "; cohort path"),
        file=sys.stderr,
    )
    print("shards=" + json.dumps(parts))
    print(f"ciks_sha256={sha}")
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:6]))
