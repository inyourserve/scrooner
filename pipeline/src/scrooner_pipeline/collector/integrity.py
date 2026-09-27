"""Module 11 -- Data Integrity Checks (doc 06). Doc 08's Day 6 deliverable,
paired with collector/logs.py. "Confirms nothing was lost or silently
corrupted" (doc 06) between what raw.sec_companyfacts / raw.sec_submissions
/ raw.sec_filing_documents SAY got stored and what Supabase Storage
actually holds. This is the real, repeatable version of the manual
spot-check done by hand on Day 3 (see
doc/learnings/day-03-companyfacts-submissions.md, Problem 1: two objects
were checksummed and one Storage folder was listed manually) -- a tool
that can be rerun against the full accumulated dataset any time, not a
one-off script.

Two independent checks per DB row that carries a storage_path:

1. EXISTENCE -- does a real object exist at storage_path? Checked via
   SupabaseStorageClient.head(), which hits Supabase's object/info
   endpoint: metadata only (size/etag), no object bytes transferred.
   ALWAYS EXHAUSTIVE -- every row, every table, every run of this tool.
   There is no reason to sample this: verified live 2026-08-14 that
   head()-ing all 364 currently-stored rows (companyfacts + submissions)
   takes well under a minute and costs no meaningful bandwidth (metadata
   responses are a few hundred bytes each). This stays true even at
   doc 08's eventual ~8,000-company scale -- existence checking doesn't
   get more expensive per row as row content grows, only more numerous,
   and a few tens of thousands of small metadata calls is still cheap for
   a tool that's meant to be run periodically, not continuously.

2. HASH -- does the object's actual content still hash (SHA-256) to what
   was recorded at collection time? This is NOT free like existence
   checking -- it requires downloading the full object, and some
   companyfacts payloads are multi-MB (JPMorgan Chase's is ~7.9MB as of
   2026-08-14). This is the design call doc 08 Day 6 asks to be made and
   stated explicitly, not silently picked:

   DECISION: exhaustive (hash_sample_rate=1.0 by default), NOT sampled,
   at current scale.

   Reasoning: verified live 2026-08-14 against the real accumulated data
   -- 364 rows with a non-null storage_path (186 sec_companyfacts + 178
   sec_submissions; sec_filing_documents has zero rows with a
   storage_path yet, since Filing Document downloads -- doc 06 module 6
   -- haven't been built), totaling ~693MB. Re-downloading and re-hashing
   all 693MB is a one-time cost of well under a couple of minutes on a
   normal connection -- trivial for a tool meant to be run by a solo
   operator occasionally (after a bootstrap, before trusting a dataset
   for the next phase), not on every request or every minute. Sampling
   would save bandwidth that isn't currently a real constraint, at the
   cost of a genuine trust gap: an unsampled row could carry a silent
   corruption that this tool would then simply never notice. Per doc 05's
   "evidence before expansion" and doc 04's "manual verification is a
   feature" -- don't add sampling complexity against a hypothetical
   volume problem that doesn't exist yet; exhaustive is also just simpler
   (KISS) and this IS the first real run of this exact tool, so full
   confidence right now is worth more than saved bandwidth.

   THIS WILL NOT STAY THE RIGHT DEFAULT FOREVER. At doc 08's eventual
   ~8,000-company scale, with recurring bootstrap/incremental runs each
   adding their own companyfacts/submissions objects (this table is
   intentionally append-only -- lossless history, not a single current
   snapshot), full re-download of the entire accumulated archive on every
   reconciliation pass would become real, recurring bandwidth/time cost
   -- probably tens of GB and climbing. `hash_sample_rate` (0.0-1.0)
   exists specifically so that future switch is a config change, not a
   rewrite: e.g. drop to 0.05-0.1 once volume/size make exhaustive
   impractical, or always fully verify the golden-company set (doc 08)
   plus a random sample of everything else. Not implemented as the
   default now because it isn't needed yet -- see doc/learnings/
   day-06-logs-and-integrity.md for this reasoning restated alongside the
   real numbers from the run it was decided against.

Never repairs anything. A missing object or a hash mismatch is reported as
an issue, not "fixed" by re-deriving, re-fetching, or silently correcting
the DB row -- that would cross into the Normalizer's territory (deciding
what the data SHOULD be) instead of the Collector's job (recording what
IS, and flagging when what IS doesn't match what was recorded).
"""

import hashlib
import random
from dataclasses import dataclass, field
from datetime import datetime, timezone

import psycopg
import structlog

from scrooner_pipeline.collector.storage import (
    SupabaseStorageClient,
    strip_bucket_prefix,
)

logger = structlog.get_logger()

# Every raw.* table the Collector writes that carries a storage_path
# pointer to a real Supabase Storage object (doc 08's schema table).
# sec_filing_documents is included even though nothing has a non-null
# storage_path as of Day 6 (Filing Document downloads -- doc 06 module 6
# -- aren't built yet) so this tool doesn't need rewriting the day that
# module starts populating it; it will just start showing up in the
# report with real counts instead of zeros.
_CHECKED_TABLES: list[dict] = [
    {"table": "raw.sec_companyfacts", "key_cols": ["id"], "has_run_id": True},
    {"table": "raw.sec_submissions", "key_cols": ["id"], "has_run_id": True},
    {
        "table": "raw.sec_filing_documents",
        "key_cols": ["cik", "accession_number"],
        "has_run_id": False,
    },
]


@dataclass
class RowIssue:
    """One concrete, unexplained delta -- exactly what doc 08's "zero
    unexplained deltas" bar requires surfacing, never hiding."""

    table: str
    row_key: dict
    cik: str | None
    storage_path: str
    run_id: int | None
    issue_type: str  # "missing_object" | "hash_mismatch" | "check_failed"
    detail: str


@dataclass
class TableCounts:
    table: str
    rows_with_storage_path: int = 0
    existence_checked: int = 0
    existence_ok: int = 0
    existence_missing: int = 0
    hash_checked: int = 0
    hash_ok: int = 0
    hash_mismatch: int = 0
    hash_skipped_sampled_out: int = 0
    check_failed: int = 0


@dataclass
class RunCounts:
    """Per-run breakdown -- doc 08's "expected vs. actual object
    counts/hashes per run" phrasing, taken literally. run_id is None for
    pre-Day-4 rows (companyfacts/submissions rows written before the Day 4
    migration added run_id) or for tables that don't carry run_id at all
    (sec_filing_documents) -- bucketed separately rather than silently
    merged into run_id=0 or dropped."""

    table: str
    run_id: int | None
    rows: int = 0
    existence_ok: int = 0
    existence_missing: int = 0
    hash_ok: int = 0
    hash_mismatch: int = 0


@dataclass
class ReconciliationReport:
    generated_at: datetime
    hash_sample_rate: float
    seed: int | None
    table_counts: list[TableCounts] = field(default_factory=list)
    run_counts: list[RunCounts] = field(default_factory=list)
    issues: list[RowIssue] = field(default_factory=list)

    @property
    def clean(self) -> bool:
        """True iff every checked row exists at its storage_path and every
        hash-checked row's content still matches its recorded sha256 --
        doc 08's "zero unexplained deltas" bar, computed rather than
        asserted."""
        return len(self.issues) == 0

    @property
    def total_rows_checked(self) -> int:
        return sum(tc.rows_with_storage_path for tc in self.table_counts)


def _fetch_rows(conn: psycopg.Connection, table_cfg: dict) -> list[dict]:
    table = table_cfg["table"]
    cols = list(table_cfg["key_cols"]) + ["cik", "storage_path", "sha256"]
    if table_cfg["has_run_id"]:
        cols.append("run_id")
    col_list = ", ".join(cols)
    with conn.cursor() as cur:
        cur.execute(f"select {col_list} from {table} where storage_path is not null")  # noqa: S608 -- table is from a fixed internal allowlist, never user input
        colnames = [d.name for d in cur.description]
        return [dict(zip(colnames, row)) for row in cur.fetchall()]


def reconcile(
    conn: psycopg.Connection,
    storage: SupabaseStorageClient | None = None,
    hash_sample_rate: float = 1.0,
    tables: list[str] | None = None,
    seed: int | None = None,
) -> ReconciliationReport:
    """Runs the full Module 11 reconciliation: for every row in the
    checked tables with a non-null storage_path, confirm the object exists
    (always, every row) and -- subject to hash_sample_rate -- that its
    content still hashes to the recorded sha256.

    `tables`: restrict to a subset of raw.* table names (e.g. for a
    faster single-table check); default None checks all of
    _CHECKED_TABLES.

    `seed`: makes sampling reproducible when hash_sample_rate < 1.0 --
    irrelevant at the current default of 1.0 (exhaustive, no randomness
    involved) but wired through now so switching the default later
    doesn't require touching this function's signature.
    """
    own_storage = storage is None
    storage = storage or SupabaseStorageClient()
    rng = random.Random(seed)

    table_counts: list[TableCounts] = []
    run_counts_map: dict[tuple[str, int | None], RunCounts] = {}
    issues: list[RowIssue] = []

    try:
        for cfg in _CHECKED_TABLES:
            if tables is not None and cfg["table"] not in tables:
                continue
            rows = _fetch_rows(conn, cfg)
            tc = TableCounts(table=cfg["table"], rows_with_storage_path=len(rows))
            logger.info("integrity.table.start", table=cfg["table"], rows=len(rows))

            for i, row in enumerate(rows, start=1):
                if i % 25 == 0 or i == len(rows):
                    logger.info(
                        "integrity.table.progress",
                        table=cfg["table"],
                        checked=i,
                        of=len(rows),
                        existence_missing=tc.existence_missing,
                        hash_mismatch=tc.hash_mismatch,
                        check_failed=tc.check_failed,
                    )
                storage_path = row["storage_path"]
                run_id = row.get("run_id")
                row_key = {k: row[k] for k in cfg["key_cols"]}
                rc = run_counts_map.setdefault(
                    (cfg["table"], run_id), RunCounts(table=cfg["table"], run_id=run_id)
                )
                rc.rows += 1

                try:
                    object_path = strip_bucket_prefix(storage_path)
                except ValueError as exc:
                    tc.check_failed += 1
                    issues.append(
                        RowIssue(
                            table=cfg["table"],
                            row_key=row_key,
                            cik=row.get("cik"),
                            storage_path=storage_path,
                            run_id=run_id,
                            issue_type="check_failed",
                            detail=str(exc),
                        )
                    )
                    logger.error(
                        "integrity.bad_storage_path",
                        table=cfg["table"],
                        storage_path=storage_path,
                    )
                    continue

                tc.existence_checked += 1
                try:
                    meta = storage.head(object_path)
                except Exception as exc:
                    tc.check_failed += 1
                    issues.append(
                        RowIssue(
                            table=cfg["table"],
                            row_key=row_key,
                            cik=row.get("cik"),
                            storage_path=storage_path,
                            run_id=run_id,
                            issue_type="check_failed",
                            detail=f"head() failed: {exc!r}",
                        )
                    )
                    logger.error(
                        "integrity.head_failed",
                        table=cfg["table"],
                        storage_path=storage_path,
                        error=repr(exc),
                    )
                    continue

                if meta is None:
                    tc.existence_missing += 1
                    issues.append(
                        RowIssue(
                            table=cfg["table"],
                            row_key=row_key,
                            cik=row.get("cik"),
                            storage_path=storage_path,
                            run_id=run_id,
                            issue_type="missing_object",
                            detail="DB row records this storage_path but Storage returned 404 -- no object exists there",
                        )
                    )
                    logger.error(
                        "integrity.missing_object",
                        table=cfg["table"],
                        cik=row.get("cik"),
                        storage_path=storage_path,
                    )
                    continue

                tc.existence_ok += 1
                rc.existence_ok += 1

                if rng.random() >= hash_sample_rate:
                    tc.hash_skipped_sampled_out += 1
                    continue

                tc.hash_checked += 1
                try:
                    content = storage.download(object_path)
                except Exception as exc:
                    tc.check_failed += 1
                    issues.append(
                        RowIssue(
                            table=cfg["table"],
                            row_key=row_key,
                            cik=row.get("cik"),
                            storage_path=storage_path,
                            run_id=run_id,
                            issue_type="check_failed",
                            detail=f"download() failed: {exc!r}",
                        )
                    )
                    logger.error(
                        "integrity.download_failed",
                        table=cfg["table"],
                        storage_path=storage_path,
                        error=repr(exc),
                    )
                    continue

                actual_sha256 = hashlib.sha256(content).hexdigest()
                recorded_sha256 = row["sha256"]
                if actual_sha256 == recorded_sha256:
                    tc.hash_ok += 1
                    rc.hash_ok += 1
                else:
                    tc.hash_mismatch += 1
                    rc.hash_mismatch += 1
                    issues.append(
                        RowIssue(
                            table=cfg["table"],
                            row_key=row_key,
                            cik=row.get("cik"),
                            storage_path=storage_path,
                            run_id=run_id,
                            issue_type="hash_mismatch",
                            detail=f"recorded sha256={recorded_sha256} actual sha256={actual_sha256}",
                        )
                    )
                    logger.error(
                        "integrity.hash_mismatch",
                        table=cfg["table"],
                        cik=row.get("cik"),
                        storage_path=storage_path,
                        recorded=recorded_sha256,
                        actual=actual_sha256,
                    )

            table_counts.append(tc)
            logger.info(
                "integrity.table.done",
                table=cfg["table"],
                rows=tc.rows_with_storage_path,
                existence_ok=tc.existence_ok,
                existence_missing=tc.existence_missing,
                hash_ok=tc.hash_ok,
                hash_mismatch=tc.hash_mismatch,
                check_failed=tc.check_failed,
            )
    finally:
        if own_storage:
            storage.close()

    run_counts = sorted(
        run_counts_map.values(),
        key=lambda rc: (rc.table, rc.run_id if rc.run_id is not None else -1),
    )
    report = ReconciliationReport(
        generated_at=datetime.now(timezone.utc),
        hash_sample_rate=hash_sample_rate,
        seed=seed,
        table_counts=table_counts,
        run_counts=run_counts,
        issues=issues,
    )
    logger.info(
        "integrity.reconcile.done",
        total_rows_checked=report.total_rows_checked,
        clean=report.clean,
        issues=len(report.issues),
        hash_sample_rate=hash_sample_rate,
    )
    return report


def render_report(report: ReconciliationReport) -> str:
    """Human-readable text rendering -- what jobs/report.py's `reconcile`
    command prints. Deliberately plain text over a dashboard/JSON blob:
    this is meant to be read directly in a terminal by a solo operator,
    doc 05's "manual verification is a feature" applied to the report
    format itself."""
    lines: list[str] = []
    lines.append(
        "=== Scrooner Collector -- Integrity Reconciliation Report (Module 11) ==="
    )
    lines.append(f"generated_at: {report.generated_at.isoformat()}")
    mode = (
        "EXHAUSTIVE"
        if report.hash_sample_rate >= 1.0
        else f"SAMPLED (rate={report.hash_sample_rate}, seed={report.seed})"
    )
    lines.append(f"existence check: exhaustive (always)")
    lines.append(f"hash re-verification: {mode}")
    lines.append("")

    header = (
        f"{'table':<28} {'w/storage_path':>14} {'exist_ok':>9} {'exist_missing':>13} "
        f"{'hash_checked':>12} {'hash_ok':>8} {'hash_mismatch':>13} {'check_failed':>12}"
    )
    lines.append(header)
    lines.append("-" * len(header))
    totals = TableCounts(table="TOTAL")
    for tc in report.table_counts:
        lines.append(
            f"{tc.table:<28} {tc.rows_with_storage_path:>14} {tc.existence_ok:>9} {tc.existence_missing:>13} "
            f"{tc.hash_checked:>12} {tc.hash_ok:>8} {tc.hash_mismatch:>13} {tc.check_failed:>12}"
        )
        totals.rows_with_storage_path += tc.rows_with_storage_path
        totals.existence_checked += tc.existence_checked
        totals.existence_ok += tc.existence_ok
        totals.existence_missing += tc.existence_missing
        totals.hash_checked += tc.hash_checked
        totals.hash_ok += tc.hash_ok
        totals.hash_mismatch += tc.hash_mismatch
        totals.hash_skipped_sampled_out += tc.hash_skipped_sampled_out
        totals.check_failed += tc.check_failed
    lines.append("-" * len(header))
    lines.append(
        f"{'TOTAL':<28} {totals.rows_with_storage_path:>14} {totals.existence_ok:>9} {totals.existence_missing:>13} "
        f"{totals.hash_checked:>12} {totals.hash_ok:>8} {totals.hash_mismatch:>13} {totals.check_failed:>12}"
    )
    lines.append("")

    lines.append("Per-run breakdown:")
    run_header = f"{'table':<24} {'run_id':>8} {'rows':>6} {'exist_ok':>9} {'exist_missing':>13} {'hash_ok':>8} {'hash_mismatch':>13}"
    lines.append(run_header)
    lines.append("-" * len(run_header))
    for rc in report.run_counts:
        run_label = str(rc.run_id) if rc.run_id is not None else "(none)"
        lines.append(
            f"{rc.table:<24} {run_label:>8} {rc.rows:>6} {rc.existence_ok:>9} {rc.existence_missing:>13} "
            f"{rc.hash_ok:>8} {rc.hash_mismatch:>13}"
        )
    lines.append("")

    lines.append(f"issues found: {len(report.issues)}")
    if report.issues:
        for issue in report.issues:
            lines.append(
                f"  [{issue.issue_type}] table={issue.table} row_key={issue.row_key} cik={issue.cik} "
                f"run_id={issue.run_id} storage_path={issue.storage_path}"
            )
            lines.append(f"      {issue.detail}")
        lines.append("")
        lines.append(
            "=== NOT CLEAN -- unexplained deltas above require investigation, not silent acceptance ==="
        )
    else:
        lines.append("")
        lines.append("=== CLEAN -- zero unexplained deltas ===")

    return "\n".join(lines)
