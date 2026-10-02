"""Saved-screens list/detail Redis cache (2026-09-15) -- mirrors
test_screen_run_cache.py's own discipline: every test that exercises a
cache read/write monkeypatches the cache functions directly (REDIS_URL is
deliberately unreachable in tests, conftest.py), never relies on a real
Redis instance being present.
"""

from contextlib import contextmanager

import pytest

from routers import saved_screens


@pytest.mark.unit
def test_list_screens_uses_cache_without_database(monkeypatch):
    expected = [{"id": 1, "name": "Cached", "slug": "cached"}]
    monkeypatch.setattr(
        saved_screens,
        "get_cached_screens_list",
        lambda user_id: expected if user_id == "user-a" else None,
    )

    class NoDatabaseAccess:
        def cursor(self):
            raise AssertionError("a cache hit should never query Postgres")

    @contextmanager
    def pooled_connection():
        yield NoDatabaseAccess()

    monkeypatch.setattr(saved_screens, "get_pooled_connection", pooled_connection)
    assert saved_screens.list_screens("user-a") == expected


@pytest.mark.unit
def test_list_screens_caches_a_fresh_database_read(monkeypatch):
    monkeypatch.setattr(saved_screens, "get_cached_screens_list", lambda _user_id: None)
    recorded = {}
    monkeypatch.setattr(
        saved_screens,
        "set_cached_screens_list",
        lambda user_id, screens: recorded.update(user_id=user_id, screens=screens),
    )

    class FakeCursor:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def execute(self, _sql, _params):
            pass

        def fetchall(self):
            return [
                (
                    1,
                    "Name",
                    "slug",
                    {"metric_predicates": []},
                    "2026-01-01",
                    "2026-01-02",
                )
            ]

    class FakeConnection:
        def cursor(self):
            return FakeCursor()

    @contextmanager
    def pooled_connection():
        yield FakeConnection()

    monkeypatch.setattr(saved_screens, "get_pooled_connection", pooled_connection)
    screens = saved_screens.list_screens("user-a")
    assert screens == [
        {
            "id": 1,
            "name": "Name",
            "slug": "slug",
            "query": {"metric_predicates": []},
            "created_at": "2026-01-01",
            "updated_at": "2026-01-02",
        }
    ]
    assert recorded == {"user_id": "user-a", "screens": screens}


@pytest.mark.unit
def test_get_screen_uses_cached_metadata_but_still_reads_the_run_page(monkeypatch):
    meta = {
        "id": 1,
        "name": "Cached",
        "slug": "cached",
        "query": {"metric_predicates": []},
        "last_run_id": "run-1",
        "created_at": "2026-01-01",
        "updated_at": "2026-01-02",
    }
    monkeypatch.setattr(
        saved_screens,
        "get_cached_screen_detail",
        lambda user_id, slug: meta if (user_id, slug) == ("user-a", "cached") else None,
    )

    class NoDatabaseAccess:
        def cursor(self):
            raise AssertionError(
                "a cached-metadata hit should never query app.saved_screen"
            )

    @contextmanager
    def pooled_connection():
        yield NoDatabaseAccess()

    monkeypatch.setattr(saved_screens, "get_pooled_connection", pooled_connection)
    read_page_calls = []
    monkeypatch.setattr(
        saved_screens,
        "_read_page",
        lambda conn, run_id, user_id, page_size, cursor: (
            read_page_calls.append((run_id, user_id, page_size, cursor))
            or {"run_id": run_id}
        ),
    )

    # page_size/cursor passed explicitly -- called directly (not through
    # FastAPI's own request pipeline), so the parameter's `Query(...)`
    # marker default would otherwise reach _read_page unresolved, the same
    # reason test_screen_run_cache.py's own _read_page tests always pass
    # page_size explicitly too.
    result = saved_screens.get_screen(
        "cached", cursor=None, page_size=50, user_id="user-a"
    )
    assert result == {
        "id": 1,
        "name": "Cached",
        "slug": "cached",
        "query": {"metric_predicates": []},
        "created_at": "2026-01-01",
        "updated_at": "2026-01-02",
        "run": {"run_id": "run-1"},
    }
    assert read_page_calls == [("run-1", "user-a", 50, None)]


@pytest.mark.unit
def test_create_screen_invalidates_the_list_cache(monkeypatch):
    class FakeCursor:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def execute(self, sql, _params=()):
            normalized = " ".join(sql.split())
            if normalized.startswith("select 1 from app.saved_screen"):
                self._result = None
            elif normalized.startswith("select slug from app.saved_screen"):
                self._result = []
            elif normalized.startswith("insert into app.saved_screen"):
                self._result = (7,)

        def fetchall(self):
            return self._result

        def fetchone(self):
            return self._result

    class FakeConnection:
        def cursor(self):
            return FakeCursor()

    @contextmanager
    def pooled_connection():
        yield FakeConnection()

    monkeypatch.setattr(saved_screens, "get_pooled_connection", pooled_connection)
    invalidated = []
    monkeypatch.setattr(
        saved_screens,
        "invalidate_screens_list",
        lambda user_id: invalidated.append(user_id),
    )

    from scrooner_pipeline.screener.schema import ScreenQuery

    body = saved_screens.SavedScreenCreate(
        name="My Screen", query=ScreenQuery(metric_predicates=[])
    )
    saved_screens.create_screen(body, user_id="user-a")
    assert invalidated == ["user-a"]


@pytest.mark.unit
def test_create_screen_rejects_a_duplicate_name_for_the_same_user(monkeypatch):
    # Found live 2026-10-03: saving the same name twice silently created
    # two separate rows (same name, different auto-disambiguated slugs)
    # -- _available_slug was built to dodge the collision, not reject it.
    class FakeCursor:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def execute(self, sql, _params=()):
            normalized = " ".join(sql.split())
            if normalized.startswith("select 1 from app.saved_screen"):
                self._result = (1,)  # an existing row with this name
            else:
                pytest.fail(f"must not reach a second query: {normalized}")

        def fetchone(self):
            return self._result

    class FakeConnection:
        def cursor(self):
            return FakeCursor()

    @contextmanager
    def pooled_connection():
        yield FakeConnection()

    monkeypatch.setattr(saved_screens, "get_pooled_connection", pooled_connection)

    from fastapi import HTTPException
    from scrooner_pipeline.screener.schema import ScreenQuery

    body = saved_screens.SavedScreenCreate(
        name="  My Screen  ", query=ScreenQuery(metric_predicates=[])
    )
    with pytest.raises(HTTPException) as excinfo:
        saved_screens.create_screen(body, user_id="user-a")
    assert excinfo.value.status_code == 409
    assert "My Screen" in excinfo.value.detail


@pytest.mark.unit
def test_rename_screen_invalidates_detail_and_list_cache_using_the_returned_slug(
    monkeypatch,
):
    class FakeCursor:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def execute(self, _sql, _params):
            self._result = ("original-slug",)

        def fetchone(self):
            return self._result

    class FakeConnection:
        def cursor(self):
            return FakeCursor()

    @contextmanager
    def pooled_connection():
        yield FakeConnection()

    monkeypatch.setattr(saved_screens, "get_pooled_connection", pooled_connection)
    detail_calls, list_calls = [], []
    monkeypatch.setattr(
        saved_screens,
        "invalidate_screen_detail",
        lambda user_id, slug: detail_calls.append((user_id, slug)),
    )
    monkeypatch.setattr(
        saved_screens,
        "invalidate_screens_list",
        lambda user_id: list_calls.append(user_id),
    )

    result = saved_screens.rename_screen(
        1, saved_screens.SavedScreenRename(name="New Name"), user_id="user-a"
    )
    assert result == {"id": 1, "name": "New Name"}
    assert detail_calls == [("user-a", "original-slug")]
    assert list_calls == ["user-a"]


@pytest.mark.unit
def test_delete_screen_invalidates_detail_and_list_cache_using_the_returned_slug(
    monkeypatch,
):
    class FakeCursor:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def execute(self, _sql, _params):
            self._result = ("original-slug",)

        def fetchone(self):
            return self._result

    class FakeConnection:
        def cursor(self):
            return FakeCursor()

    @contextmanager
    def pooled_connection():
        yield FakeConnection()

    monkeypatch.setattr(saved_screens, "get_pooled_connection", pooled_connection)
    detail_calls, list_calls = [], []
    monkeypatch.setattr(
        saved_screens,
        "invalidate_screen_detail",
        lambda user_id, slug: detail_calls.append((user_id, slug)),
    )
    monkeypatch.setattr(
        saved_screens,
        "invalidate_screens_list",
        lambda user_id: list_calls.append(user_id),
    )

    result = saved_screens.delete_screen(1, user_id="user-a")
    assert result == {"deleted": 1}
    assert detail_calls == [("user-a", "original-slug")]
    assert list_calls == ["user-a"]


@pytest.mark.unit
def test_refresh_screen_invalidates_detail_and_list_cache(monkeypatch):
    class FakeCursor:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def execute(self, sql, _params=()):
            normalized = " ".join(sql.split())
            if normalized.startswith("select saved.query"):
                self._result = ({"metric_predicates": []}, "ROE above 20%")
            else:
                self._result = None

        def fetchone(self):
            return self._result

    class FakeConnection:
        def cursor(self):
            return FakeCursor()

    @contextmanager
    def pooled_connection():
        yield FakeConnection()

    monkeypatch.setattr(saved_screens, "get_pooled_connection", pooled_connection)
    monkeypatch.setattr(
        saved_screens,
        "create_run_from_query",
        lambda *_args, **_kwargs: {"run_id": "run-2"},
    )
    detail_calls, list_calls = [], []
    monkeypatch.setattr(
        saved_screens,
        "invalidate_screen_detail",
        lambda user_id, slug: detail_calls.append((user_id, slug)),
    )
    monkeypatch.setattr(
        saved_screens,
        "invalidate_screens_list",
        lambda user_id: list_calls.append(user_id),
    )

    result = saved_screens.refresh_screen("original-slug", user_id="user-a")
    assert result == {"run_id": "run-2"}
    assert detail_calls == [("user-a", "original-slug")]
    assert list_calls == ["user-a"]
