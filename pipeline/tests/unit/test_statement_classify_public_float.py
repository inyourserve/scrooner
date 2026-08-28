"""Unit tests for statements/classify.py's `public_float` canonical concept
(doc 23 Stage B / doc 31 section 2 Task 2) -- dei:EntityPublicFloat, a
real market-cap proxy already sitting in raw.sec_companyfacts, mapped
additively the same way every other statement-only concept in this
module is (see NEW_CANONICAL_CONCEPTS/NEW_CONCEPT_MAPPINGS). Uses a
hand-rolled fake cursor/connection, same style as test_restatements.py --
no real DB connection needed."""

import pytest

from scrooner_pipeline.statements.classify import (
    NEW_CANONICAL_CONCEPTS,
    NEW_CONCEPT_MAPPINGS,
    seed_new_canonical_concepts,
    seed_new_concept_mappings,
)


class FakeCursor:
    def __init__(self, conn):
        self.conn = conn
        self._rows = []

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def execute(self, sql, params=()):
        normalized = " ".join(sql.split())
        if normalized.startswith("select name, id from analytics.canonical_concept"):
            self._rows = list(self.conn.canonical_concepts.items())
        elif normalized.startswith("select id from core.concept where taxonomy = %s and tag = %s"):
            taxonomy, tag = params
            concept_id = self.conn.core_concepts.get((taxonomy, tag))
            self._rows = [(concept_id,)] if concept_id is not None else []
        elif normalized.startswith("insert into analytics.concept_mapping"):
            canonical_id, concept_id, priority, confidence, notes = params
            self.conn.concept_mappings.append(
                {
                    "canonical_concept_id": canonical_id,
                    "concept_id": concept_id,
                    "priority": priority,
                    "confidence": confidence,
                    "notes": notes,
                }
            )
            self._rows = []
        else:
            raise AssertionError(f"Unexpected SQL in classify test: {normalized}")

    def executemany(self, sql, rows):
        normalized = " ".join(sql.split())
        if normalized.startswith("insert into analytics.canonical_concept"):
            for name, statement, combination_mode, description in rows:
                if name not in self.conn.canonical_concepts:
                    self.conn.canonical_concepts[name] = len(self.conn.canonical_concepts) + 1
        else:
            raise AssertionError(f"Unexpected executemany SQL in classify test: {normalized}")

    def fetchall(self):
        return list(self._rows)

    def fetchone(self):
        return self._rows[0] if self._rows else None


class FakeConnection:
    def __init__(self, core_concepts):
        self.core_concepts = core_concepts
        self.canonical_concepts: dict[str, int] = {}
        self.concept_mappings: list[dict] = []
        self.commits = 0

    def cursor(self):
        return FakeCursor(self)

    def commit(self):
        self.commits += 1


@pytest.mark.unit
def test_public_float_is_registered_as_first_match_balance_sheet_concept():
    """doc 23 Stage B's explicit design call: public_float must never be
    conflated with market_cap -- it lives as its own canonical concept,
    single-tag (first_match), not summed with anything else."""
    by_name = {name: (statement, mode) for name, statement, mode, _desc in NEW_CANONICAL_CONCEPTS}

    assert "public_float" in by_name
    statement, combination_mode = by_name["public_float"]
    assert statement == "balance_sheet"
    assert combination_mode == "first_match"


@pytest.mark.unit
def test_public_float_maps_from_dei_entitypublicfloat_tag():
    mapping = next(m for m in NEW_CONCEPT_MAPPINGS if m[0] == "public_float")
    canonical_name, taxonomy, tag, priority, confidence, _notes = mapping

    assert taxonomy == "dei"
    assert tag == "EntityPublicFloat"
    assert priority == 1
    assert confidence == "approved"


@pytest.mark.unit
def test_seed_functions_wire_public_float_concept_mapping_end_to_end():
    """Simulates core.concept already containing dei:EntityPublicFloat
    (real, confirmed live for AAPL per doc 23) and confirms the two seed
    steps resolve it into a real analytics.concept_mapping row, the same
    additive pattern Mapper's own resolve() already reuses unchanged."""
    conn = FakeConnection(core_concepts={("dei", "EntityPublicFloat"): 9001})

    canonical_id_by_name = seed_new_canonical_concepts(conn)
    assert "public_float" in canonical_id_by_name

    stats = seed_new_concept_mappings(conn, canonical_id_by_name)

    public_float_rows = [
        m for m in conn.concept_mappings
        if m["canonical_concept_id"] == canonical_id_by_name["public_float"]
    ]
    assert len(public_float_rows) == 1
    assert public_float_rows[0]["concept_id"] == 9001
    assert public_float_rows[0]["confidence"] == "approved"
    assert stats["mapped"] >= 1


@pytest.mark.unit
def test_unresolved_tag_is_logged_not_crashed_when_concept_missing():
    """A concept mapping whose tag isn't in core.concept yet (e.g. a
    foreign-filer taxonomy gap, same known ENB/TSM pattern doc 24 already
    documents for public_float) must increment unresolved_tag and move on,
    never raise."""
    conn = FakeConnection(core_concepts={})  # nothing resolvable

    canonical_id_by_name = seed_new_canonical_concepts(conn)
    stats = seed_new_concept_mappings(conn, canonical_id_by_name)

    assert stats["unresolved_tag"] == len(NEW_CONCEPT_MAPPINGS)
    assert stats["mapped"] == 0
    assert conn.concept_mappings == []
