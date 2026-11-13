"""Which companies are on the new (hybrid FSN) nightly path, so the old normalize/map writers skip them.

Founder decisions relayed by Dhairya 2026-11-11: once a company is written from the FSN store its nightly
updates come from the hybrid path only, and the old path skips it entirely, at the writer, not cell by cell.

A company is on the new path once an applied new-system write has landed for it: it holds
analytics.slot_protected_cell rows whose run is in apply mode and is either the tag-map writer
(company_tag_map.select@1, mapper/company_tag_map_plan.py; the write path after the founder's 2026-11-11
methodology change) or an `fsn.*` FSN cell write. Both writers save those rows in the same transaction as the
cells, so the switch happens in the same step as the write. A company with an analytics.company_value_owner
row (0119; the tag-map writer adds owner 'company_tag_map', 0123) is on the new path too, where that table exists.
A restore that removes the company's FSN protection rows takes it back to the old path.

The skip is behind HYBRID_NEW_PATH (off by default). With it on, a failure to read the set fails closed:
the caller raises (sanity) or skips the whole cohort (reprocess_recent_filers.sh) instead of writing.
"""

from __future__ import annotations

import os
from typing import Any

FLAG = "HYBRID_NEW_PATH"
STATEMENT_TIMEOUT = "15s"

NEW_PATH_SQL = """
select distinct p.company_id
from analytics.slot_protected_cell p
join analytics.rule_run r on r.run_id::text = p.run_id
where (r.rule_id like 'fsn.%%' or r.rule_id = 'company_tag_map.select@1') and r.mode = 'apply'
"""


def enabled() -> bool:
    return os.environ.get(FLAG, "off").strip().lower() == "on"


def company_ids(conn: Any, *, set_timeout: bool = True) -> set[int]:
    """Every company on the new path (read-only, indexed, statement_timeout 15s). set_timeout=False leaves the
    session's own statement_timeout alone (a caller inside its own run)."""
    if set_timeout:
        conn.execute(f"set statement_timeout = '{STATEMENT_TIMEOUT}'")
    ids = {int(r[0]) for r in conn.execute(NEW_PATH_SQL).fetchall()}
    if (
        conn.execute("select to_regclass('analytics.company_value_owner')").fetchone()[
            0
        ]
        is not None
    ):
        ids |= {
            int(r[0])
            for r in conn.execute(
                "select company_id from analytics.company_value_owner"
            ).fetchall()
        }
    if set_timeout:
        conn.execute("reset statement_timeout")
    return ids


# ---------------------------------------------------------------- the derived-metric stages
#
# Dhairya 2026-11-13 (before the flag switch): the derived-metric stages (calculate, growth, ttm-*, price, expanded,
# piotroski, quality flags, reconciliations, fcf growth, dividend streak) must read only canonical_fact for a new-path
# company, never the old mapping. Three reads did not (tests/unit/test_fsn_new_path_derived.py lists every table those
# stages read). With HYBRID_NEW_PATH=on, for a new-path company:
#   - quick_ratio's inventory evidence takes "which tags are inventory" from the company's tag map
#     (analytics.company_tag_map), not analytics.concept_mapping;
#   - market cap's weighted-diluted share count comes from canonical_fact weighted_diluted_shares (the tag map's
#     concept, 0122), not a hard-coded core.fact tag;
#   - the rendered-report share count (core.shares_outstanding_fallback, an old-path source) is not used.
_derived_cache: dict[str, set[int]] = {}


def canonical_only(conn: Any, company_id: int) -> bool:
    """True when a derived-metric stage must take this company's inputs from canonical_fact / the tag map only.
    Flag off: always False, and the database is not touched. On: the new-path set is read once per process."""
    if not enabled():
        return False
    if "ids" not in _derived_cache:
        _derived_cache["ids"] = company_ids(conn, set_timeout=False)
    return company_id in _derived_cache["ids"]


def reset_cache() -> None:
    _derived_cache.clear()


def ciks(conn: Any) -> list[str]:
    ids = sorted(company_ids(conn))
    rows = conn.execute(
        "select cik from core.company where id = any(%s) order by cik", (ids,)
    ).fetchall()
    return [r[0] for r in rows]


def excluded_company_ids(conn: Any) -> set[int]:
    """What an old-path writer must skip: the new-path companies when HYBRID_NEW_PATH=on, else nothing.
    A read failure raises (fail closed: the writer stops rather than write a new-path company)."""
    if not enabled():
        return set()
    return company_ids(conn)


# ---------------------------------------------------------------- the skip inside the writer commands
#
# Ritwik's PR #12 review (2026-11-12, data-team/tags/decisions/REVIEW-PR12-2026-11-12.md): the skip must live
# in the writer commands themselves, so that every entry point (reprocess_recent_filers.sh,
# pipeline-recompute.yml, reprocess_fiscal_year_relabel.sh, run_conflict_latest_filed.sh, a manual run) gets
# it. `scrooner-normalize` and `scrooner-map` are built on GuardedGroup: before a WRITER command parses its
# arguments, the new-path CIKs are taken out of its --ciks.
#
# What counts as a writer (founder 2026-11-11: the old path must not write canonical_fact for a new-path
# company; "SEC FOR MAPPING": the tag-map mapper reads core.fact): the old path's canonical-value writers and
# the normalizer stages that repair, derive or re-rank facts with old-path logic. The SEC ingestion stages
# (identity, periods, units, facts, dedupe, restatements, instance-fallback) are NOT writers here: they write
# the authoritative core.fact rows the tag-map mapper reads, so a new-path company keeps receiving its
# filings' facts. Every command of the two CLIs is classified in exactly one of the two sets
# (tests/unit/test_fsn_new_path_guard.py fails on an unclassified one).

WRITER_COMMANDS: dict[str, frozenset[str]] = {
    "scrooner-normalize": frozenset(
        {
            "conflict-latest-filed",
            "conflicts",
            "derive-interim-quarters",
            "derive-q4",
            "demote-coregistrant-facts",
            "golden",
        }
    ),
    "scrooner-map": frozenset(
        {
            "resolve-facts",
            "split-rebase",
            "split-rebase-restore",
            "resolve-concept-fallbacks",
            "resolve-statement-fallbacks",
            "resolve-balance-sheet-fallback",
            "resolve-revenue",
            "resolve-dedup-holes",
            "resolve-employee-count-fallback",
            "resolve-conflict-fills",
            "run-parser",
            "resolve-parser-results",
        }
    ),
}
NOT_WRITER_COMMANDS: dict[str, frozenset[str]] = {
    "scrooner-normalize": frozenset(
        {
            # SEC ingestion: the authoritative core.fact rows the tag-map mapper reads
            "identity",
            "periods",
            "units",
            "facts",
            "dedupe",
            "restatements",
            "instance-fallback",
            # the new system's own stage, and a read-only report
            "tagmap-authority",
            "tagmap-dedupe",
            "errors",
        }
    ),
    "scrooner-map": frozenset(
        {
            # the new system (tag map seed and write path)
            "seed-company-tag-map",
            "docmap-load",
            "tagmap-plan",
            "dqc-check",  # read-only DQC report over served cells
            # derived metrics, recomputed from canonical_fact for every company
            "calculate",
            "growth",
            "ttm-returns",
            "ttm-margins",
            "calculate-price-metrics",
            "calculate-expanded-metrics",
            "calculate-piotroski",
            "calculate-quality-flags",
            "calculate-reconciliation",
            "calculate-tax-reconciliation",
            "calculate-fcf-growth",
            "calculate-dividend-streak",
            # seeds, reports, coverage, tag library: no company values
            "seed-concepts",
            "seed-definitions",
            "seed-statements",
            "seed-expanded-concepts",
            "seed-expanded-definitions",
            "seed-sector-templates",
            "coverage",
            "unmapped-tags",
            "balance-identity-dry-run",
            "snapshot-coverage",
            "errors",
            "validate",
            "parser-registry-summary",
            "probe-filing-lines",
            "build-coverage-matrix",
            "company-coverage",
            "company-coverage-report",
            "corrected-coverage-report",
            "build-tag-candidates",
            "tag-candidate-report",
            "build-tag-library",
            "gap-tags",
            "gap-report",
            "record-verdict",
            "record-finding",
            "calculator-registry",
        }
    ),
}


class NewPathRefused(Exception):
    """A writer command cannot run safely with HYBRID_NEW_PATH=on (no --ciks to filter)."""


def guard_args(args: list[str], skip: Any) -> list[str] | None:
    """A writer command's arguments with the new-path CIKs taken out of --ciks. None: nothing left to run.
    `skip` returns the new-path CIKs (called only when there is something to filter). Without --ciks a writer
    would run over its default company set, so it is refused (fail closed)."""
    out = list(args)
    idx = None
    for i, a in enumerate(out):
        if a == "--ciks" and i + 1 < len(out):
            idx, value = i + 1, out[i + 1]
            break
        if a.startswith("--ciks="):
            idx, value = i, a.split("=", 1)[1]
            break
    if idx is None:
        raise NewPathRefused(
            "HYBRID_NEW_PATH=on: an old-path writer needs --ciks so new-path companies can be left out"
        )
    new_path_ciks = {c.zfill(10) for c in skip()}
    kept = [
        c
        for c in value.split(",")
        if c.strip() and c.strip().zfill(10) not in new_path_ciks
    ]
    if not kept:
        return None
    joined = ",".join(kept)
    out[idx] = joined if out[idx] == value else f"--ciks={joined}"
    return out


def _db_new_path_ciks() -> list[str]:
    from scrooner_pipeline.db.connection import get_connection

    with get_connection() as conn:
        found = ciks(conn)
        conn.rollback()
    return found


def guarded_group(program: str) -> type:
    """A TyperGroup class for `program` whose writer subcommands leave new-path companies out."""
    import typer
    from typer.core import TyperGroup

    writers = WRITER_COMMANDS[program]

    class GuardedGroup(TyperGroup):
        def resolve_command(self, ctx: Any, args: list[str]) -> Any:
            name, cmd, rest = super().resolve_command(ctx, args)
            if name in writers and enabled():
                try:
                    filtered = guard_args(rest, _db_new_path_ciks)
                except NewPathRefused as exc:
                    raise typer.BadParameter(str(exc)) from exc
                if filtered is None:
                    typer.echo(
                        f"{program} {name}: every requested company is on the new path; skipped (HYBRID_NEW_PATH)"
                    )
                    ctx.exit(0)
                rest = filtered
            return name, cmd, rest

    GuardedGroup.__name__ = f"GuardedGroup[{program}]"
    return GuardedGroup


def refuse_population_writer(conn: Any, writer: str) -> None:
    """A population-wide old-path writer (one set-based pass over every company, no company list to filter)
    must not run once any company is on the new path with HYBRID_NEW_PATH=on: it raises instead (fail closed).
    Called at the top of mapper.concept_fallback.resolve_all_arithmetic_fallbacks,
    mapper.conflict_resolution.resolve_all_conflict_fills and mapper.dedup_majority_resolver.
    resolve_all_safe_concepts (pipeline-recompute.yml's population phase calls the first two directly)."""
    if enabled() and company_ids(conn):
        raise NewPathRefused(
            f"HYBRID_NEW_PATH=on: {writer} is population-wide and would write new-path companies; "
            "run it per company (--ciks) or not at all"
        )
