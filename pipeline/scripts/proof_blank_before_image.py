"""Read-only before-image for the proof_blank stage (pipeline-fsn-write.yml), in the pilot-prod CSV format so
`scrooner-cells restore --before-image <dir>` works on it (stage=restore).

Scope: the companies (and data points) of the proof-blank cell files <proof_blank dir>/<family>/cells.jsonl.gz.
Writes <out>/{canonical_fact,cell_blank_reason,slot_protected_cell}.csv.gz, companies.txt, data_points.txt.
Nothing is written to the database; the session is read-only.

usage: uv run --project pipeline python pipeline/scripts/proof_blank_before_image.py <proof_blank dir> <out dir>
Exit 0 with no files when the directory holds no cell file (nothing to blank)."""

import gzip
import json
import sys
from pathlib import Path

TABLES = (
    "analytics.canonical_fact",
    "analytics.cell_blank_reason",
    "analytics.slot_protected_cell",
)


def scope(proof_dir: Path) -> tuple[list[int], list[str]]:
    ids: set[int] = set()
    points: set[str] = set()
    for path in sorted(proof_dir.glob("*/cells.jsonl.gz")):
        with gzip.open(path, "rt") as fh:
            for line in fh:
                if line.strip():
                    r = json.loads(line)
                    ids.add(int(r["company_id"]))
                    points.add(r["data_point_name"])
    return sorted(ids), sorted(points)


def main(proof_dir: str, out_dir: str) -> int:
    ids, points = scope(Path(proof_dir))
    if not ids:
        print("proof_blank before-image: no cell files, nothing to export")
        return 0
    from scrooner_pipeline.db.connection import get_connection

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    with get_connection() as conn:
        conn.execute("set transaction read only")
        conn.execute("set statement_timeout = '10min'")
        for table in TABLES:
            path = out / f"{table.split('.')[1]}.csv.gz"
            with (
                gzip.open(path, "wb") as fh,
                conn.cursor().copy(
                    f"copy (select * from {table} where company_id = any(%s) order by 1) to stdout with csv header",
                    (ids,),
                ) as cp,
            ):
                for chunk in cp:
                    fh.write(bytes(chunk))
        conn.rollback()
    (out / "companies.txt").write_text("\n".join(str(i) for i in ids) + "\n")
    (out / "data_points.txt").write_text(",".join(points) + "\n")
    print(f"proof_blank before-image: {len(ids)} companies, {len(points)} data points")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
