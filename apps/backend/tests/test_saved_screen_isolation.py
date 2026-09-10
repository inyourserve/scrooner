from contextlib import contextmanager
from uuid import UUID

import pytest
from fastapi import HTTPException

from routers import saved_screens


OWNER = "11111111-1111-1111-1111-111111111111"
OTHER = "22222222-2222-2222-2222-222222222222"


class ScreenCursor:
    def __init__(self, conn):
        self.conn = conn
        self._row = None
        self._rows = []

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def execute(self, sql, params=()):
        normalized = " ".join(sql.split())
        if normalized.startswith("select id, name, slug, query"):
            user_id = params[0]
            self._rows = [
                (screen_id, screen["name"], screen["slug"], screen["query"], screen["created_at"], screen["updated_at"])
                for screen_id, screen in sorted(self.conn.screens.items())
                if str(screen["user_id"]) == user_id
            ]
        elif normalized.startswith("select user_id"):
            screen = self.conn.screens.get(params[0])
            self._row = (screen["user_id"],) if screen else None
        elif normalized.startswith("update app.saved_screen"):
            name, screen_id = params
            self.conn.screens[screen_id]["name"] = name
        elif normalized.startswith("delete from app.saved_screen"):
            self.conn.screens.pop(params[0], None)
        else:
            raise AssertionError(f"Unexpected saved-screen SQL: {normalized}")

    def fetchone(self):
        return self._row

    def fetchall(self):
        return list(self._rows)


class ScreenConnection:
    def __init__(self):
        self.screens = {
            1: {
                "user_id": UUID(OWNER),
                "name": "Original",
                "slug": "original",
                "query": {"metric_predicates": []},
                "created_at": "2026-08-18T00:00:00Z",
                "updated_at": "2026-08-18T00:00:00Z",
            }
        }
        self.commits = 0

    def cursor(self):
        return ScreenCursor(self)

    def commit(self):
        self.commits += 1

    @contextmanager
    def transaction(self):
        # A real psycopg3 Connection.transaction() rolls back and
        # re-raises on any exception in its block, same as a plain
        # try/finally with nothing suppressed -- this fake matches that
        # exact hands-off behavior, since rename/delete's 404 path relies
        # on the HTTPException still propagating out.
        yield


@pytest.mark.unit
def test_saved_screen_owner_can_mutate_and_other_user_cannot(monkeypatch):
    conn = ScreenConnection()

    @contextmanager
    def connection():
        yield conn

    monkeypatch.setattr(saved_screens, "get_pooled_connection", connection)

    assert [row["id"] for row in saved_screens.list_screens(OWNER)] == [1]
    assert saved_screens.list_screens(OTHER) == []

    assert saved_screens.rename_screen(1, saved_screens.SavedScreenRename(name="Renamed"), OWNER) == {
        "id": 1,
        "name": "Renamed",
    }
    assert conn.screens[1]["name"] == "Renamed"

    with pytest.raises(HTTPException) as rename_exc:
        saved_screens.rename_screen(1, saved_screens.SavedScreenRename(name="Stolen"), OTHER)
    assert rename_exc.value.status_code == 404
    assert conn.screens[1]["name"] == "Renamed"

    with pytest.raises(HTTPException) as delete_exc:
        saved_screens.delete_screen(1, OTHER)
    assert delete_exc.value.status_code == 404
    assert 1 in conn.screens

    assert saved_screens.delete_screen(1, OWNER) == {"deleted": 1}
    assert 1 not in conn.screens
