from contextlib import contextmanager

import pytest
from fastapi import HTTPException

from routers import watchlists


OWNER = "11111111-1111-1111-1111-111111111111"
OTHER = "22222222-2222-2222-2222-222222222222"


class WatchlistCursor:
    def __init__(self, conn):
        self.conn = conn
        self._row = None
        self._rows = []

    def __enter__(self): return self
    def __exit__(self, *_args): return False

    def execute(self, sql, params=()):
        normalized = " ".join(sql.split())
        if normalized.startswith("select w.company_id"):
            user_id, company_id, _ = params
            self._rows = [
                (item, self.conn.companies[item][0], self.conn.companies[item][1], self.conn.companies[item][2], "2026-10-04T00:00:00Z", self.conn.notes.get((owner, item)), None, None, None, None, getattr(self.conn, "pe", None), None, None, None, False, "0000320193", *getattr(self.conn, "valuation_cols", (None, None, None)))
                for owner, item in self.conn.items
                if owner == user_id and (company_id is None or item == company_id)
            ]
        elif normalized.startswith("select c.id from core.company c where c.id = any"):
            self._rows = [(cid,) for cid in params[0] if cid in getattr(self.conn, "bank_ids", set())]
        elif normalized.startswith("with values_ranked as"):
            self._rows = list(getattr(self.conn, "fundamental_rows", []))
        elif normalized.startswith("select company_id, form, filing_date::text"):
            self._rows = []
        elif normalized.startswith("insert into app.watchlist_item"):
            user_id, company_id = params
            if company_id not in self.conn.companies or (user_id, company_id) in self.conn.items:
                self._row = None
            else:
                self.conn.items.add((user_id, company_id))
                self._row = (company_id,)
        elif normalized.startswith("select 1 from core.company"):
            self._row = (1,) if params[0] in self.conn.companies else None
        elif normalized.startswith("delete from app.watchlist_item"):
            user_id, company_id = params
            if (user_id, company_id) in self.conn.items:
                self.conn.items.remove((user_id, company_id))
                self._row = (company_id,)
            else:
                self._row = None
        elif normalized.startswith("update app.watchlist_item"):
            has_note, note, mark_reviewed, user_id, company_id = params
            if (user_id, company_id) not in self.conn.items:
                self._row = None
            else:
                if has_note:
                    self.conn.notes[(user_id, company_id)] = note
                self._row = (self.conn.notes.get((user_id, company_id)), "2026-10-04T01:00:00Z" if mark_reviewed else None)
        elif normalized.startswith("insert into app.watchlist_review"):
            self._row = None
        else:
            raise AssertionError(f"Unexpected watchlist SQL: {normalized}")

    def fetchone(self): return self._row
    def fetchall(self): return list(self._rows)


class WatchlistConnection:
    companies = {1: ("Apple Inc.", "AAPL", "Technology")}

    def __init__(self): self.items = set(); self.notes = {}
    def cursor(self): return WatchlistCursor(self)


@pytest.mark.unit
def test_watchlist_is_idempotent_and_user_scoped(monkeypatch):
    conn = WatchlistConnection()

    @contextmanager
    def connection(): yield conn

    monkeypatch.setattr(watchlists, "get_pooled_connection", connection)

    body = watchlists.WatchlistCreate(company_id=1)
    assert watchlists.add_to_watchlist(body, OWNER)["in_watchlist"] is True
    assert watchlists.add_to_watchlist(body, OWNER)["in_watchlist"] is True
    assert watchlists.list_watchlist(None, OWNER)["contains"] is True
    assert watchlists.list_watchlist(None, OTHER)["items"] == []

    with pytest.raises(HTTPException) as other_remove:
        watchlists.remove_from_watchlist(1, OTHER)
    assert other_remove.value.status_code == 404

    assert watchlists.remove_from_watchlist(1, OWNER)["in_watchlist"] is False


@pytest.mark.unit
def test_watchlist_note_and_review_are_user_scoped(monkeypatch):
    conn = WatchlistConnection()
    conn.items.add((OWNER, 1))

    @contextmanager
    def connection(): yield conn

    monkeypatch.setattr(watchlists, "get_pooled_connection", connection)
    result = watchlists.update_watchlist_item(1, watchlists.WatchlistUpdate(note="Watch margins", mark_reviewed=True), OWNER)
    assert result["note"] == "Watch margins"
    assert result["reviewed_at"] is not None
    with pytest.raises(HTTPException) as exc:
        watchlists.update_watchlist_item(1, watchlists.WatchlistUpdate(note="Other"), OTHER)
    assert exc.value.status_code == 404


@pytest.mark.unit
def test_watchlist_rejects_unknown_company(monkeypatch):
    conn = WatchlistConnection()

    @contextmanager
    def connection(): yield conn

    monkeypatch.setattr(watchlists, "get_pooled_connection", connection)
    with pytest.raises(HTTPException) as exc:
        watchlists.add_to_watchlist(watchlists.WatchlistCreate(company_id=999), OWNER)
    assert exc.value.status_code == 404


@pytest.mark.unit
def test_watchlist_hides_suppressed_fundamentals_for_a_bank_only(monkeypatch):
    # (company_id, metric, value, period_end, period_label, rank)
    rows = [
        (1, "operating_margin", "0.3", "2026-06-30", "Q2", 1),
        (2, "operating_margin", "0.4", "2026-06-30", "Q2", 1),
        (2, "diluted_eps", "1.1", "2026-06-30", "Q2", 1),
    ]

    class BankConnection(WatchlistConnection):
        companies = {1: ("Apple Inc.", "AAPL", "Technology"), 2: ("Some Bank", "BNK", "Financials")}
        bank_ids = {2}
        fundamental_rows = rows

    conn = BankConnection()
    conn.items.update({(OWNER, 1), (OWNER, 2)})

    @contextmanager
    def pooled_connection():
        yield conn

    monkeypatch.setattr(watchlists, "get_pooled_connection", pooled_connection)
    result = watchlists.list_watchlist(company_id=None, user_id=OWNER)
    by_id = {item["company_id"]: item["fundamentals"] for item in result["items"]}
    assert "operating_margin" in by_id[1]            # industrial unchanged
    assert "operating_margin" not in by_id[2]        # bank: suppressed
    assert by_id[2]["diluted_eps"]["latest"]["value"] == "1.1"   # EPS kept
