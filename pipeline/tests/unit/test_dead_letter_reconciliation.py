import pytest

from scrooner_pipeline.common.reconcile import parse_error_ids, resolve_dead_letters


pytestmark = pytest.mark.unit


class FakeCursor:
    def __init__(self, rows: list[tuple[int, bool]], updated: list[int] | None = None) -> None:
        self.rows = rows
        self.updated = updated
        self.executions: list[tuple[str, tuple]] = []
        self._result: list[tuple] = []

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None

    def execute(self, query: str, params: tuple) -> None:
        self.executions.append((query, params))
        if query.lstrip().startswith("select"):
            self._result = self.rows
        else:
            ids = self.updated if self.updated is not None else [row[0] for row in self.rows]
            self._result = [(error_id,) for error_id in ids]

    def fetchall(self) -> list[tuple]:
        return self._result


class FakeConnection:
    def __init__(self, cursor: FakeCursor) -> None:
        self.fake_cursor = cursor

    def cursor(self) -> FakeCursor:
        return self.fake_cursor


def test_parse_error_ids_normalizes_deduplicates_and_sorts() -> None:
    assert parse_error_ids("7, 2,7") == (2, 7)


@pytest.mark.parametrize("value", ["", "0", "-1,2", "one"])
def test_parse_error_ids_rejects_invalid_input(value: str) -> None:
    with pytest.raises(ValueError):
        parse_error_ids(value)


def test_resolve_updates_only_locked_exact_ids_with_audit_note() -> None:
    cursor = FakeCursor([(2, False), (7, False)])
    conn = FakeConnection(cursor)

    result = resolve_dead_letters(
        conn,
        layer="mapper",
        error_ids=[7, 2],
        note="Golden-ten mapper rerun succeeded and validation is clean.",
    )

    assert result == {"layer": "mapper", "resolved_count": 2, "resolved_ids": [2, 7]}
    assert "analytics.mapper_error" in cursor.executions[0][0]
    assert "for update" in cursor.executions[0][0]
    assert cursor.executions[1][1][1] == [2, 7]
    assert "resolved_at = now()" in cursor.executions[1][0]


def test_resolve_refuses_missing_id_before_update() -> None:
    cursor = FakeCursor([(2, False)])
    with pytest.raises(ValueError, match=r"unknown mapper error ID\(s\): \[7\]"):
        resolve_dead_letters(
            FakeConnection(cursor), layer="mapper", error_ids=[2, 7], note="Enough evidence for exact reconciliation."
        )
    assert len(cursor.executions) == 1


def test_resolve_refuses_already_resolved_id_before_update() -> None:
    cursor = FakeCursor([(2, True)])
    with pytest.raises(ValueError, match="already-resolved"):
        resolve_dead_letters(
            FakeConnection(cursor), layer="mapper", error_ids=[2], note="Enough evidence for exact reconciliation."
        )
    assert len(cursor.executions) == 1


@pytest.mark.parametrize("layer,note", [("unknown", "Long enough evidence note for the test."), ("mapper", "too short")])
def test_resolve_validates_layer_and_note_before_sql(layer: str, note: str) -> None:
    cursor = FakeCursor([])
    with pytest.raises(ValueError):
        resolve_dead_letters(FakeConnection(cursor), layer=layer, error_ids=[1], note=note)
    assert cursor.executions == []


def test_resolve_detects_concurrent_update_mismatch() -> None:
    cursor = FakeCursor([(2, False), (7, False)], updated=[2])
    with pytest.raises(RuntimeError, match="concurrent reconciliation mismatch"):
        resolve_dead_letters(
            FakeConnection(cursor),
            layer="mapper",
            error_ids=[2, 7],
            note="Enough evidence for exact reconciliation.",
        )
