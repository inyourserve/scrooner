"""Read-only CLI for Day 7 pilot readiness and deterministic sampling."""

import json

import typer

from scrooner_pipeline.db.connection import get_connection
from scrooner_pipeline.collector.storage import (
    SupabaseStorageClient,
    strip_bucket_prefix,
)
from scrooner_pipeline.pilot import (
    DEFAULT_DATABASE_LIMIT_BYTES,
    evaluate_readiness,
    load_eligible_candidates,
    mapped_tag_presence,
    read_inventory,
    select_stratified_sample,
)

app = typer.Typer()


@app.command()
def preflight(
    target: int = typer.Option(100, min=1, help="Desired number of pilot companies."),
    database_limit_mb: int = typer.Option(
        500, min=1, help="Current database capacity limit."
    ),
) -> None:
    """Fail closed unless universe, payload, quality, and capacity gates pass."""
    with get_connection() as conn:
        conn.execute("set transaction read only")
        inventory = read_inventory(conn)
    readiness = evaluate_readiness(
        inventory,
        target=target,
        database_limit_bytes=database_limit_mb * 1024 * 1024,
    )
    typer.echo(
        json.dumps(
            {
                "inventory": inventory.__dict__,
                "ready": readiness.ready,
                "blockers": readiness.blockers,
                "projected_database_size_bytes": readiness.projected_database_size_bytes,
                "database_limit_bytes": readiness.database_limit_bytes,
            },
            default=str,
            indent=2,
        )
    )
    if not readiness.ready:
        raise typer.Exit(1)


@app.command()
def sample(
    target: int = typer.Option(100, min=1),
    ciks_only: bool = typer.Option(False, help="Print a comma-separated CIK manifest."),
) -> None:
    """Print the deterministic manifest from the latest approved universe."""
    with get_connection() as conn:
        conn.execute("set transaction read only")
        candidates = load_eligible_candidates(conn)
    selected = select_stratified_sample(candidates, target)
    if ciks_only:
        typer.echo(",".join(row.cik for row in selected))
    else:
        typer.echo(json.dumps([row.__dict__ for row in selected], indent=2))


@app.command("mapping-preflight")
def mapping_preflight(
    limit: int = typer.Option(100, min=1, max=500),
    eligible_sample: bool = typer.Option(
        False,
        help="Measure the deterministic sample from the latest eligible-primary universe.",
    ),
) -> None:
    """Read existing Company Facts objects and report curated-tag presence.

    By default this preserves the original CIK-ordered inventory check. Use
    ``--eligible-sample`` for release evidence: it measures the exact
    deterministic cohort produced by ``sample --target LIMIT`` instead of a
    convenient but potentially ineligible first-N payload batch.
    """
    with get_connection() as conn:
        conn.execute("set transaction read only")
        with conn.cursor() as cur:
            if eligible_sample:
                candidates = load_eligible_candidates(conn)
                selected = select_stratified_sample(candidates, limit)
                target_ciks = [row.cik for row in selected]
                cur.execute(
                    """
                    select distinct on (cik) cik, storage_path
                    from raw.sec_companyfacts
                    where cik = any(%s)
                    order by cik, fetched_at desc, id desc
                    """,
                    (target_ciks,),
                )
            else:
                target_ciks = []
                cur.execute(
                    """
                    select distinct on (cik) cik, storage_path
                    from raw.sec_companyfacts
                    order by cik, fetched_at desc, id desc
                    limit %s
                    """,
                    (limit,),
                )
            paths = cur.fetchall()

    payloads = {}
    failures = []
    with SupabaseStorageClient() as storage:
        for cik, storage_path in paths:
            try:
                payloads[cik] = json.loads(
                    storage.download(strip_bucket_prefix(storage_path))
                )
            except Exception as exc:
                failures.append(
                    {
                        "cik": cik,
                        "error_type": type(exc).__name__,
                        "message": str(exc)[:300],
                    }
                )

    report = mapped_tag_presence(payloads)
    report["requested"] = len(paths)
    report["cohort"] = (
        "eligible_stratified_sample" if eligible_sample else "cik_ordered_inventory"
    )
    if eligible_sample:
        report["ciks"] = target_ciks
    report["download_failures"] = failures
    typer.echo(json.dumps(report, indent=2))
    if failures:
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
