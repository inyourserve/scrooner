"""Egress / write-load cuts in the facts normalizer (2026-11-28).

1. concept + unit lookups load once per normalize_facts run, not once per CIK; concepts first seen
   mid-run still resolve (cache extended in place from a re-query of only the new pairs).
2. core.fact rows are written by COPY into a temp stage + one set-based insert, with the exact
   result of the old per-row executemany (DB-backed tests below, Postgres 16 in CI).
"""

from __future__ import annotations

from contextlib import nullcontext
from decimal import Decimal

import psycopg
import pytest

from scrooner_pipeline.normalizer import facts as F


# ---- unit: lookups loaded once per run -------------------------------------------------

def test_lookups_loaded_once_per_run_and_passed_down(monkeypatch):
    calls = {"concept": 0, "unit": 0}
    seen = []

    def load_concepts(c):
        calls["concept"] += 1
        return {("us-gaap", "Revenues"): 1}

    def load_units(c):
        calls["unit"] += 1
        return {"usd": 2}

    def per_cik(storage, conn, cik, concept_by_pair=None, unit_by_name=None):
        seen.append((concept_by_pair, unit_by_name))
        return {"cik": cik, "status": "ok", "considered": 0}

    monkeypatch.setattr(F, "_load_concept_lookup", load_concepts)
    monkeypatch.setattr(F, "_load_unit_lookup", load_units)
    monkeypatch.setattr(F, "SupabaseStorageClient", lambda: nullcontext(None))
    monkeypatch.setattr(F, "normalize_facts_for_cik", per_cik)
    F.normalize_facts(None, {"0000000001", "0000000002", "0000000003"})
    assert calls == {"concept": 1, "unit": 1}
    assert len(seen) == 3
    assert seen[0][0] == {("us-gaap", "Revenues"): 1} and seen[0][1] == {"usd": 2}
    assert all(s[0] is seen[0][0] and s[1] is seen[0][1] for s in seen)  # the one shared dict


class _Cur:
    def __init__(self, log, rows):
        self.log, self.rows = log, rows

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def executemany(self, sql, params):
        self.log.append(("many", sql, list(params)))

    def execute(self, sql, params=None):
        self.log.append(("one", sql, params))

    def fetchall(self):
        return self.rows


class _Conn:
    def __init__(self, rows=()):
        self.log, self.rows, self.commits = [], list(rows), 0

    def cursor(self):
        return _Cur(self.log, self.rows)

    def commit(self):
        self.commits += 1


def test_upsert_concepts_with_cache_requeries_only_new_pairs():
    cache = {("us-gaap", "Revenues"): 1}
    conn = _Conn(rows=[("custom", "NewTag", 99)])
    out = F.upsert_concepts(conn, {("us-gaap", "Revenues"), ("custom", "NewTag")}, cache=cache)
    assert out is cache and cache == {("us-gaap", "Revenues"): 1, ("custom", "NewTag"): 99}
    inserted = [e for e in conn.log if e[0] == "many"][0][2]
    assert inserted == [("custom", "NewTag")]  # the cached pair is not re-inserted
    # no full-table scan: the only select is the unnest-restricted one
    selects = [e[1] for e in conn.log if e[0] == "one"]
    assert len(selects) == 1 and "unnest" in selects[0]
    assert conn.commits == 1


def test_upsert_concepts_with_cache_and_nothing_new_touches_no_db():
    cache = {("us-gaap", "Revenues"): 1}
    conn = _Conn()
    F.upsert_concepts(conn, {("us-gaap", "Revenues")}, cache=cache)
    assert conn.log == [] and conn.commits == 0


# ---- DB-backed: COPY path == old executemany path ------------------------------------

OLD_SQL = """
    insert into core.fact
        (company_id, concept_id, unit_id, period_id, filing_id, value, raw_object_id)
    values
        (%(company_id)s, %(concept_id)s, %(unit_id)s, %(period_id)s, %(filing_id)s,
         %(value)s, %(raw_object_id)s)
    on conflict (company_id, concept_id, unit_id, period_id, filing_id) do update
        set value = excluded.value
"""


def _old_write(conn, rows):
    with conn.cursor() as cur:
        cur.executemany(OLD_SQL, rows)


@pytest.fixture
def world(isolated_database_url):
    with psycopg.connect(isolated_database_url) as conn:
        conn.execute("insert into core.unit (unit_name) values ('usd') on conflict do nothing")
        cid = conn.execute(
            "insert into core.company (cik, company_name, fiscal_year_end) values ('0000000007', 'X', '1231') returning id"
        ).fetchone()[0]
        raw = conn.execute(
            "insert into raw.sec_companyfacts (cik, source_url, sha256, storage_path, http_status) "
            "values ('0000000007', 'u', 'h', 'p', 200) returning id"
        ).fetchone()[0]
        unit = conn.execute("select id from core.unit where unit_name = 'usd'").fetchone()[0]
        concepts = [
            conn.execute(
                "insert into core.concept (taxonomy, tag) values ('us-gaap', %s) returning id", (t,)
            ).fetchone()[0]
            for t in ("A", "B")
        ]
        periods = [
            conn.execute(
                "insert into core.period (company_id, start_date, end_date, period_type) "
                "values (%s, %s, %s, 'instant') returning id",
                (cid, d, d),
            ).fetchone()[0]
            for d in ("2024-12-31", "2025-12-31")
        ]
        filings = [
            conn.execute(
                "insert into core.filing (company_id, accession_number, form, filing_date, period_of_report) "
                "values (%s, %s, '10-K', '2026-02-01', '2025-12-31') returning id",
                (cid, a),
            ).fetchone()[0]
            for a in ("acc-1", "acc-2")
        ]
        conn.commit()
        yield conn, dict(cid=cid, raw=raw, unit=unit, concepts=concepts, periods=periods, filings=filings)


def _rows(w):
    def r(ci, pi, fi, v):
        return {
            "company_id": w["cid"], "concept_id": w["concepts"][ci], "unit_id": w["unit"],
            "period_id": w["periods"][pi], "filing_id": w["filings"][fi], "value": v,
            "raw_object_id": w["raw"],
        }

    return [
        r(0, 0, 0, Decimal("123456789012345.123456789")),  # more digits than a float holds
        r(0, 1, 0, 7),  # int
        r(1, 0, 1, Decimal("1E+3")),  # exponent text
        r(1, 1, 1, Decimal("-0.000000000000001")),
        r(0, 0, 0, Decimal("5.5")),  # duplicate key inside one batch: last value wins, first position kept
    ]


def _dump(conn):
    return conn.execute(
        "select company_id, concept_id, unit_id, period_id, filing_id, value::text, raw_object_id "
        "from core.fact order by id"
    ).fetchall()


@pytest.mark.integration
def test_copy_path_matches_old_executemany_path(world):
    conn, w = world
    rows = _rows(w)
    # a pre-existing row the batch must update on conflict (same ON CONFLICT ... set value)
    pre = {**rows[1], "value": Decimal("1")}
    _old_write(conn, [pre])
    conn.commit()
    _old_write(conn, rows)
    conn.commit()
    old = _dump(conn)
    conn.execute("delete from core.fact")
    conn.commit()
    F.write_fact_rows(conn, [pre])
    conn.commit()
    F.write_fact_rows(conn, rows)
    conn.commit()
    new = _dump(conn)
    assert new == old and len(old) == 4
    by_key = {(r[1], r[3]): r[5] for r in new}
    assert by_key[(w["concepts"][0], w["periods"][0])] == "5.5"  # duplicate: last wins
    assert by_key[(w["concepts"][0], w["periods"][1])] == "7"  # updated over the pre-existing 1
    # rerun is idempotent: no new keys
    F.write_fact_rows(conn, rows)
    conn.commit()
    assert _dump(conn) == old


@pytest.mark.integration
def test_copy_path_keeps_decimal_text_exactly(world):
    conn, w = world
    F.write_fact_rows(conn, _rows(w)[:4])
    conn.commit()
    got = {r[5] for r in _dump(conn)}
    assert "123456789012345.123456789" in got  # float would have rounded this
    assert "-0.000000000000001" in got
