import asyncio

import pytest
from fastapi import HTTPException

import auth


class FakeResponse:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        return self._payload


class FakeAsyncClient:
    def __init__(self, response):
        self.response = response
        self.requests = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_args):
        return False

    async def get(self, url, **kwargs):
        self.requests.append((url, kwargs))
        return self.response


@pytest.mark.unit
@pytest.mark.parametrize("header", [None, "", "Token abc", "Bearer "])
def test_missing_or_malformed_authorization_is_rejected_without_network(header):
    with pytest.raises(HTTPException) as exc:
        asyncio.run(auth.get_current_user_id(header))

    assert exc.value.status_code == 401


@pytest.mark.unit
def test_invalid_token_is_rejected(monkeypatch):
    fake = FakeAsyncClient(FakeResponse(401, {"message": "invalid"}))
    monkeypatch.setattr(auth.httpx, "AsyncClient", lambda: fake)

    with pytest.raises(HTTPException) as exc:
        asyncio.run(auth.get_current_user_id("Bearer bad-token"))

    assert exc.value.status_code == 401
    assert fake.requests[0][1]["headers"]["Authorization"] == "Bearer bad-token"


@pytest.mark.unit
def test_valid_token_resolves_exact_user_id(monkeypatch):
    user_id = "11111111-1111-1111-1111-111111111111"
    fake = FakeAsyncClient(FakeResponse(200, {"id": user_id}))
    monkeypatch.setattr(auth.httpx, "AsyncClient", lambda: fake)

    assert asyncio.run(auth.get_current_user_id("Bearer valid-token")) == user_id


@pytest.mark.unit
def test_success_response_without_user_id_fails_closed(monkeypatch):
    fake = FakeAsyncClient(FakeResponse(200, {}))
    monkeypatch.setattr(auth.httpx, "AsyncClient", lambda: fake)

    with pytest.raises(HTTPException) as exc:
        asyncio.run(auth.get_current_user_id("Bearer incomplete-token"))

    assert exc.value.status_code == 401


@pytest.mark.unit
def test_cache_hit_never_touches_the_network(monkeypatch):
    # Found live 2026-09-12: this real network call cost ~370-710ms on
    # EVERY authenticated request, often more than the endpoint's own
    # work. A cached resolution must skip it entirely, not just skip
    # re-verifying.
    user_id = "22222222-2222-2222-2222-222222222222"
    monkeypatch.setattr(auth, "get_cached_auth_user_id", lambda _token: user_id)

    def fail_if_called():
        raise AssertionError("a cache hit must never construct an httpx client")

    monkeypatch.setattr(auth.httpx, "AsyncClient", fail_if_called)

    assert asyncio.run(auth.get_current_user_id("Bearer cached-token")) == user_id


@pytest.mark.unit
def test_cache_miss_populates_the_cache_after_a_real_resolution(monkeypatch):
    user_id = "33333333-3333-3333-3333-333333333333"
    fake = FakeAsyncClient(FakeResponse(200, {"id": user_id}))
    monkeypatch.setattr(auth.httpx, "AsyncClient", lambda: fake)
    monkeypatch.setattr(auth, "get_cached_auth_user_id", lambda _token: None)
    recorded = {}
    monkeypatch.setattr(
        auth,
        "set_cached_auth_user_id",
        lambda token, uid: recorded.update(token=token, user_id=uid),
    )

    result = asyncio.run(auth.get_current_user_id("Bearer fresh-token"))

    assert result == user_id
    assert recorded == {"token": "fresh-token", "user_id": user_id}


@pytest.mark.unit
def test_an_invalid_token_is_never_cached(monkeypatch):
    fake = FakeAsyncClient(FakeResponse(401, {"message": "invalid"}))
    monkeypatch.setattr(auth.httpx, "AsyncClient", lambda: fake)
    monkeypatch.setattr(auth, "get_cached_auth_user_id", lambda _token: None)

    def fail_if_called(*_args, **_kwargs):
        raise AssertionError(
            "a failed verification must never be cached as a resolved identity"
        )

    monkeypatch.setattr(auth, "set_cached_auth_user_id", fail_if_called)

    with pytest.raises(HTTPException):
        asyncio.run(auth.get_current_user_id("Bearer bad-token"))
