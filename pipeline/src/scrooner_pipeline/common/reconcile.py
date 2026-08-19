"""Exact-ID, auditable reconciliation for pipeline dead letters."""

from collections.abc import Iterable
from typing import Any


ERROR_TABLES = {
    "collector": "raw.collector_errors",
    "normalizer": "core.normalizer_error",
    "mapper": "analytics.mapper_error",
}


def parse_error_ids(value: str) -> tuple[int, ...]:
    """Parse a comma-separated ID list into a unique, sorted tuple."""
    try:
        ids = {int(part.strip()) for part in value.split(",") if part.strip()}
    except ValueError as exc:
        raise ValueError("error IDs must be comma-separated integers") from exc
    if not ids or any(error_id <= 0 for error_id in ids):
        raise ValueError("at least one positive error ID is required")
    return tuple(sorted(ids))


def _validate_resolution(layer: str, error_ids: Iterable[int], note: str) -> tuple[str, tuple[int, ...], str]:
    if layer not in ERROR_TABLES:
        raise ValueError(f"unsupported layer {layer!r}; choose from {', '.join(ERROR_TABLES)}")
    ids = tuple(sorted(set(error_ids)))
    if not ids or any(not isinstance(error_id, int) or isinstance(error_id, bool) or error_id <= 0 for error_id in ids):
        raise ValueError("at least one positive integer error ID is required")
    clean_note = note.strip()
    if len(clean_note) < 20:
        raise ValueError("resolution note must contain at least 20 characters of evidence")
    return ERROR_TABLES[layer], ids, clean_note


def resolve_dead_letters(conn: Any, *, layer: str, error_ids: Iterable[int], note: str) -> dict[str, Any]:
    """Resolve exactly the requested rows or make no change.

    The table name comes only from ``ERROR_TABLES``; IDs and note remain query
    parameters.  Rows are locked before update so concurrent reconciliation
    cannot produce an ambiguous audit trail.
    """
    table, ids, clean_note = _validate_resolution(layer, error_ids, note)
    with conn.cursor() as cur:
        cur.execute(
            f"select id, resolved from {table} where id = any(%s) order by id for update",
            (list(ids),),
        )
        found = cur.fetchall()
        found_ids = {row[0] for row in found}
        missing = sorted(set(ids) - found_ids)
        if missing:
            raise ValueError(f"unknown {layer} error ID(s): {missing}")
        already_resolved = sorted(row[0] for row in found if row[1])
        if already_resolved:
            raise ValueError(f"already-resolved {layer} error ID(s): {already_resolved}")

        cur.execute(
            f"""update {table}
                set resolved = true,
                    resolved_at = now(),
                    resolution_note = %s
                where id = any(%s) and not resolved
                returning id""",
            (clean_note, list(ids)),
        )
        updated_ids = tuple(sorted(row[0] for row in cur.fetchall()))
        if updated_ids != ids:
            raise RuntimeError(
                f"concurrent reconciliation mismatch: requested {ids}, updated {updated_ids}"
            )

    return {"layer": layer, "resolved_count": len(ids), "resolved_ids": list(ids)}
