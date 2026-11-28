"""Missing FSN filings of the ranked cohort as a list (read-only; loads nothing).

core.filing 10-K/10-Q since 2015-01-01 of the top-1,000 cohort (doc/data-moat/team/top1000/shards.csv, excluded
rows removed) with no fsn.filing of the same accession. The same query the nightly freshness check counts; the
output feeds a later `scrooner-fsn` load dispatch. A separate command because `scrooner-operations` is invoked
without a subcommand by CI.
"""

import csv
import sys

import typer

from scrooner_pipeline.db.connection import get_connection
from scrooner_pipeline.operations import (
    age_bucket,
    fetch_fsn_missing_filings,
    load_fsn_cohort_ids,
)

app = typer.Typer()


@app.command()
def main(
    bucket: str = typer.Option(
        "", help="Only this age bucket: le_1d, d2_30, d31_90 or gt_90. Default: all."
    ),
    accessions_only: bool = typer.Option(
        False, help="Print one accession per line instead of CSV."
    ),
) -> None:
    """Print the missing accession list; performs no writes."""
    with get_connection() as conn:
        conn.execute("set transaction read only")
        rows = fetch_fsn_missing_filings(conn, load_fsn_cohort_ids())
    rows = [r for r in rows if not bucket or age_bucket(int(r[5])) == bucket]
    if accessions_only:
        for r in rows:
            typer.echo(r[1])
        return
    w = csv.writer(sys.stdout, lineterminator="\n")
    w.writerow(
        ["company_id", "accession", "form", "period", "filed", "age_days", "bucket"]
    )
    for r in rows:
        w.writerow([*r, age_bucket(int(r[5]))])


if __name__ == "__main__":
    app()
