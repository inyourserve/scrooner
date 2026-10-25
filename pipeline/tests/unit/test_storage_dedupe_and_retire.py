"""Collector hash-dedupe, integrity redirect, and the Rule S retirement executor."""

import hashlib
import json
import random
from datetime import datetime, timedelta, timezone

import pytest

from scrooner_pipeline.collector import integrity, storage_retire as sr
from scrooner_pipeline.collector.dedupe import partition_unchanged, sha256_hex


# ------------------------------------------------------------------ dedupe
def test_partition_unchanged_skips_only_identical_bytes_of_same_cik():
    same, other = b"{same}", b"{new}"
    latest = {"1": (10, sha256_hex(same)), "2": (11, sha256_hex(b"old"))}
    batch = [("1", "p1", same), ("2", "p2", other), ("3", "p3", same)]
    up, unchanged = partition_unchanged(batch, latest)
    assert [i[0] for i in up] == ["2", "3"]  # changed payload and unseen cik upload
    assert unchanged == [("1", sha256_hex(same), 10)]


def test_partition_does_not_dedupe_against_non_latest_version():
    a = b"A"
    # latest is B; payload A equals an OLDER version -> must still be stored
    up, unchanged = partition_unchanged([("1", "p", a)], {"1": (5, sha256_hex(b"B"))})
    assert up and not unchanged


# --------------------------------------------------------------- integrity
def test_retired_row_is_checked_at_keeper_path():
    retired = {("raw.sec_companyfacts", 7): "raw/sec/companyfacts/1/keeper.json"}
    row = {"id": 7, "storage_path": "raw/sec/companyfacts/1/old.json"}
    assert integrity.resolve_storage_path("raw.sec_companyfacts", row, retired) == (
        "raw/sec/companyfacts/1/keeper.json",
        True,
    )
    row2 = {"id": 8, "storage_path": "raw/x"}
    assert integrity.resolve_storage_path("raw.sec_companyfacts", row2, retired) == ("raw/x", False)
    # same id in another table never redirects
    assert integrity.resolve_storage_path("raw.sec_submissions", row, retired)[1] is False
    # filing documents have no integer id
    assert integrity.resolve_storage_path(
        "raw.sec_filing_documents", {"cik": "1", "storage_path": "raw/y"}, retired
    ) == ("raw/y", False)


# ------------------------------------------------------------ retire fakes
T0 = datetime(2026, 9, 1, tzinfo=timezone.utc)


def make_world(n_ciks=3, versions=4):
    """Per cik: `versions` rows with the SAME bytes (rows differ by fetched_at)."""
    rows, blobs = [], {}
    rid = 0
    for c in range(1, n_ciks + 1):
        payload = f"payload-{c}".encode()
        sha = hashlib.sha256(payload).hexdigest()
        for v in range(versions):
            rid += 1
            path = f"raw/sec/companyfacts/{c}/{v}.json"
            rows.append(sr.ObjectRow(rid, str(c), sha, T0 + timedelta(days=v), path, len(payload), f"etag-{c}"))
            blobs[path] = payload
    return rows, blobs


class FakeDb:
    def __init__(self, rows, referenced=()):
        self.rows, self.referenced = list(rows), set(referenced)
        self.retired = {}
        self.writes = 0
        self.exists = {r.storage_path for r in rows}
        self.has_table = True

    def fetch_rows(self):
        return [r for r in self.rows if r.storage_path in self.exists]

    def fetch_referenced(self):
        return set(self.referenced)

    def referenced_among(self, ids):
        return set(ids) & self.referenced

    def existing_paths(self, paths):
        return set(paths) & self.exists

    def retired_ids(self):
        return set(self.retired)

    def insert_retired(self, rows):
        self.writes += 1
        for r in rows:
            self.retired[r["raw_id"]] = r

    def fetch_retired(self, batch):
        return [r for r in self.retired.values() if batch is None or r["executor_batch"] == batch]

    def delete_retired(self, ids):
        for i in ids:
            self.retired.pop(i)

    def table_exists(self):
        return self.has_table


class FakeStore:
    def __init__(self, db, blobs):
        self.db, self.blobs = db, dict(blobs)
        self.deleted, self.copied = [], []

    def download(self, p):
        return self.blobs["raw/" + p]

    def delete_many(self, ps):
        for p in ps:
            self.db.exists.discard("raw/" + p)
            self.deleted.append("raw/" + p)

    def copy(self, s, d):
        self.db.exists.add("raw/" + d)
        self.copied.append(("raw/" + s, "raw/" + d))


def manifest_from(rows, referenced=()):
    plan = sr.build_rule_s_plan(rows, set(referenced))
    by = {r.raw_id: r for r in rows}
    return [
        sr.Candidate(i, by[i].cik, by[i].sha256, by[i].storage_path, by[i].size, k, by[k].storage_path)
        for i, k in plan.items()
    ]


def test_plan_keeps_latest_per_hash_and_every_referenced():
    rows, _ = make_world()
    ids_c1 = [r.raw_id for r in rows if r.cik == "1"]  # 1..4, latest is 4
    plan = sr.build_rule_s_plan(rows, referenced={ids_c1[0]})
    assert ids_c1[3] not in plan  # keeper
    assert ids_c1[0] not in plan  # referenced stays (Rule S)
    assert set(ids_c1[1:3]) <= set(plan)
    assert all(plan[i] == ids_c1[3] for i in ids_c1[1:3])


def test_recheck_drops_now_referenced_and_changed():
    rows, _ = make_world()
    man = manifest_from(rows)
    victim = man[0].raw_id
    chk = sr.recheck_manifest(man, sr.build_rule_s_plan(rows, {victim}), rows)
    assert (victim, "not_in_today_plan") in chk.dropped
    assert victim not in {c.raw_id for c in chk.approved}
    rows[0].etag = "tampered"
    chk2 = sr.recheck_manifest(man, sr.build_rule_s_plan(rows, set()), rows)
    assert any(why == "etag_size_mismatch" for _i, why in chk2.dropped)


def run(db, store, man, mode, **kw):
    return sr.run(db, store, man, mode, **kw)


def test_dry_run_writes_nothing_and_reports_zero_referenced():
    rows, blobs = make_world()
    db, man = FakeDb(rows), manifest_from(rows)
    store = FakeStore(db, blobs)
    s = run(db, store, man, "dry-run")
    assert s["approved"] == len(man) == 9 and s["referenced_in_approved"] == 0
    assert db.writes == 0 and store.deleted == [] and db.retired == {}


def test_execute_requires_confirm_and_table():
    rows, blobs = make_world()
    db, man = FakeDb(rows), manifest_from(rows)
    store = FakeStore(db, blobs)
    with pytest.raises(sr.Abort):
        run(db, store, man, "execute")
    db.has_table = False
    with pytest.raises(sr.Abort):
        run(db, store, man, "execute", confirm=sr.CONFIRM_TOKEN)
    assert store.deleted == []


def test_execute_batches_ledger_and_resume(tmp_path):
    rows, blobs = make_world()
    db, man = FakeDb(rows), manifest_from(rows)
    store = FakeStore(db, blobs)
    led = tmp_path / "ledger.jsonl"
    s = run(db, store, man, "execute", batch_size=4, confirm=sr.CONFIRM_TOKEN, ledger=led, sha_sample=3)
    assert [e["objects"] for e in s["executed"]] == [4, 4, 1]
    assert len(store.deleted) == 9 and len(db.retired) == 9
    keepers = {c.keeper_storage_path for c in man}
    assert keepers <= db.exists and len(db.exists) == 3
    assert sum(len(json.loads(l)["raw_ids"]) for l in led.read_text().splitlines()) == 9
    again = run(db, store, man, "execute", confirm=sr.CONFIRM_TOKEN)  # resumable: nothing left
    assert again["executed"] == [] and again["approved"] == 0


def test_pilot_limits_to_sample_size():
    rows, blobs = make_world(n_ciks=5, versions=5)  # 20 candidates
    db, man = FakeDb(rows), manifest_from(rows)
    store = FakeStore(db, blobs)
    s = run(db, store, man, "pilot", pilot_n=6, confirm=sr.CONFIRM_TOKEN)
    assert len(store.deleted) == 6 and s["executed"][0]["objects"] == 6


def test_referenced_appearing_mid_run_aborts_before_any_delete_of_that_batch():
    rows, blobs = make_world()
    db, man = FakeDb(rows), manifest_from(rows)
    store = FakeStore(db, blobs)
    orig = db.referenced_among
    calls = {"n": 0}

    def late(ids):
        calls["n"] += 1
        return {ids[0]} if calls["n"] == 2 else orig(ids)  # second batch gets referenced

    db.referenced_among = late
    with pytest.raises(sr.Abort):
        run(db, store, man, "execute", batch_size=4, confirm=sr.CONFIRM_TOKEN)
    assert len(store.deleted) == 4  # only the first batch went


def test_byte_mismatch_aborts_before_redirect_rows_or_delete():
    rows, blobs = make_world()
    db, man = FakeDb(rows), manifest_from(rows)
    store = FakeStore(db, {p: b"corrupt" for p in blobs})
    with pytest.raises(sr.Abort):
        run(db, store, man, "execute", confirm=sr.CONFIRM_TOKEN, sha_sample=20)
    assert store.deleted == [] and db.retired == {}


def test_rollback_restores_from_keeper_and_removes_redirect():
    rows, blobs = make_world()
    db, man = FakeDb(rows), manifest_from(rows)
    store = FakeStore(db, blobs)
    s = run(db, store, man, "execute", batch_size=100, confirm=sr.CONFIRM_TOKEN)
    label = s["executed"][0]["batch"]
    before = set(db.exists)
    r = run(db, store, man, "rollback", confirm=sr.CONFIRM_TOKEN, rollback_batch=label)
    assert r["restored"] == 9 and db.retired == {}
    assert db.exists == {x.storage_path for x in rows} and before < db.exists
    assert all(src.endswith(".json") for src, _ in store.copied)
