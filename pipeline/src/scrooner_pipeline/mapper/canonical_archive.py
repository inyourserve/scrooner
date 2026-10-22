"""The ONE archive-then-replace path for analytics.canonical_fact (ruling
2026-10-22: shared by the RU-1 per-share retirement, the split-basis writer
and definition-version changes; owner: Period Engineer).

"Never delete" means "never lose" (doc 49 section 7.3 item 7): every row a
run replaces or removes is copied to analytics.canonical_fact_retired
(migration 0098) in the SAME transaction, and every key a run fills fresh is
logged there as action 'inserted'. restore_run() undoes a run exactly.

The functions take a cursor and never commit: the caller wraps archive and
write in one transaction, so a failure leaves neither. Writes are set-based
(one statement per batch), never one query per row. `schema` exists only so
the real-SQL tests can point at a scratch schema.
"""

import json
from dataclasses import dataclass
from decimal import Decimal

ARCHIVE_TABLE = "canonical_fact_retired"


@dataclass(frozen=True)
class CanonicalRow:
    company_id: int
    canonical_concept_id: int
    period_id: int
    value: Decimal
    source_fact_ids: tuple[int, ...]


def archive_and_remove(
    cur,
    canonical_fact_ids: list[int],
    *,
    reason_code: str,
    run_id: str,
    basis_version: str | None = None,
    schema: str = "analytics",
) -> int:
    """Copy the rows to the archive (action 'removed') and delete them.
    Returns the number removed. Ids that no longer exist are skipped."""
    if not canonical_fact_ids:
        return 0
    cur.execute(
        f"""
        with gone as (
            delete from {schema}.canonical_fact
            where id = any(%(ids)s::bigint[])
            returning id, company_id, canonical_concept_id, period_id, value,
                      source_fact_ids, resolved_at
        )
        insert into {schema}.{ARCHIVE_TABLE}
            (action, canonical_fact_id, company_id, canonical_concept_id, period_id,
             value, source_fact_ids, resolved_at, reason_code, run_id, basis_version)
        select 'removed', id, company_id, canonical_concept_id, period_id,
               value, source_fact_ids, resolved_at, %(reason)s, %(run)s, %(basis)s
        from gone
        """,
        {
            "ids": list(canonical_fact_ids),
            "reason": reason_code,
            "run": run_id,
            "basis": basis_version,
        },
    )
    return cur.rowcount


def replace_rows(
    cur,
    rows: list[CanonicalRow],
    *,
    reason_code: str,
    run_id: str,
    basis_version: str | None = None,
    schema: str = "analytics",
) -> dict[str, int]:
    """Make canonical_fact hold exactly `rows` at their keys. A key whose
    stored value and sources already match is untouched (idempotent: a second
    run changes nothing). A differing stored row is archived ('replaced')
    then overwritten; a missing key is inserted and logged ('inserted')."""
    stats = {"unchanged": 0, "replaced": 0, "inserted": 0}
    if not rows:
        return stats
    keys = [(r.company_id, r.canonical_concept_id, r.period_id) for r in rows]
    if len(set(keys)) != len(keys):
        raise ValueError("replace_rows: duplicate (company, concept, period) key")
    cur.execute(
        f"""
        select cf.id, cf.company_id, cf.canonical_concept_id, cf.period_id, cf.value,
               cf.source_fact_ids
        from {schema}.canonical_fact cf
        join unnest(%(c)s::bigint[], %(k)s::bigint[], %(p)s::bigint[]) as k(c, k, p)
          on cf.company_id = k.c and cf.canonical_concept_id = k.k and cf.period_id = k.p
        """,
        {
            "c": [k[0] for k in keys],
            "k": [k[1] for k in keys],
            "p": [k[2] for k in keys],
        },
    )
    stored = {(c, k, p): (cid, v, tuple(s)) for cid, c, k, p, v, s in cur.fetchall()}
    to_replace: list[tuple[int, CanonicalRow]] = []
    to_insert: list[CanonicalRow] = []
    for row, key in zip(rows, keys):
        hit = stored.get(key)
        if hit is None:
            to_insert.append(row)
        elif hit[1] == row.value and hit[2] == tuple(row.source_fact_ids):
            stats["unchanged"] += 1
        else:
            to_replace.append((hit[0], row))
    params = {"reason": reason_code, "run": run_id, "basis": basis_version}
    if to_replace:
        ids = [cid for cid, _ in to_replace]
        cur.execute(
            f"""
            insert into {schema}.{ARCHIVE_TABLE}
                (action, canonical_fact_id, company_id, canonical_concept_id, period_id,
                 value, source_fact_ids, resolved_at, reason_code, run_id, basis_version)
            select 'replaced', id, company_id, canonical_concept_id, period_id,
                   value, source_fact_ids, resolved_at, %(reason)s, %(run)s, %(basis)s
            from {schema}.canonical_fact where id = any(%(ids)s::bigint[])
            """,
            {**params, "ids": ids},
        )
        cur.executemany(
            f"""
            update {schema}.canonical_fact
            set value = %(value)s, source_fact_ids = %(sources)s, resolved_at = now()
            where id = %(id)s
            """,
            [
                {"id": cid, "value": r.value, "sources": list(r.source_fact_ids)}
                for cid, r in to_replace
            ],
        )
        stats["replaced"] = len(to_replace)
    if to_insert:
        # One statement: insert the batch and log each new key as 'inserted'.
        # Rows travel as JSON because source_fact_ids arrays are ragged.
        payload = json.dumps(
            [
                {
                    "c": r.company_id,
                    "k": r.canonical_concept_id,
                    "p": r.period_id,
                    "v": str(r.value),
                    "s": list(r.source_fact_ids),
                }
                for r in to_insert
            ]
        )
        cur.execute(
            f"""
            with src as (
                select * from jsonb_to_recordset(%(rows)s::jsonb)
                    as t(c bigint, k bigint, p bigint, v numeric, s bigint[])
            ), new as (
                insert into {schema}.canonical_fact
                    (company_id, canonical_concept_id, period_id, value, source_fact_ids)
                select c, k, p, v, s from src
                returning id, company_id, canonical_concept_id, period_id
            )
            insert into {schema}.{ARCHIVE_TABLE}
                (action, canonical_fact_id, company_id, canonical_concept_id, period_id,
                 reason_code, run_id, basis_version)
            select 'inserted', id, company_id, canonical_concept_id, period_id,
                   %(reason)s, %(run)s, %(basis)s
            from new
            """,
            {**params, "rows": payload},
        )
        stats["inserted"] = len(to_insert)
    return stats


def restore_run(cur, run_id: str, *, schema: str = "analytics") -> int:
    """Undo one run: delete what it inserted, put back what it replaced or
    removed, stamp restored_at. Returns the number of archive rows restored.
    Restoring twice is a no-op (restored rows are skipped)."""
    cur.execute(
        f"""
        delete from {schema}.canonical_fact cf
        using {schema}.{ARCHIVE_TABLE} a
        where a.run_id = %(run)s and a.restored_at is null
          and cf.company_id = a.company_id
          and cf.canonical_concept_id = a.canonical_concept_id
          and cf.period_id = a.period_id
        """,
        {"run": run_id},
    )
    cur.execute(
        f"""
        insert into {schema}.canonical_fact
            (company_id, canonical_concept_id, period_id, value, source_fact_ids, resolved_at)
        select company_id, canonical_concept_id, period_id, value, source_fact_ids, resolved_at
        from {schema}.{ARCHIVE_TABLE}
        where run_id = %(run)s and restored_at is null and action <> 'inserted'
        """,
        {"run": run_id},
    )
    cur.execute(
        f"""
        update {schema}.{ARCHIVE_TABLE} set restored_at = now()
        where run_id = %(run)s and restored_at is null
        """,
        {"run": run_id},
    )
    return cur.rowcount
