"""SB-6 / SB-7 / SB-8 and the release pair: split.event_basis@1 and
pershare.never_derive@1 ship together, default OFF = legacy.

- pair guard: exactly one of the two ON is refused;
- SB-6: with the pair ON each owned resolved concept has exactly one
  writer (share_basis); OFF keeps the legacy writers;
- SB-7 (metric consumers reading the current-basis twins) and the RU-1
  consumer gates are NOT on main yet: their tests stay with that work.
"""

import pytest

from scrooner_pipeline.common import rule_flags
from scrooner_pipeline.corporate_actions import share_basis as sb
from scrooner_pipeline.corporate_actions import stock_splits

PAIR = "split.event_basis@1,pershare.never_derive@1"
OWNED = sorted(sb.TARGETS)


@pytest.fixture
def pair_on(monkeypatch):
    monkeypatch.setenv(rule_flags.ENV_ENABLED, PAIR)
    monkeypatch.delenv(rule_flags.ENV_DRYRUN, raising=False)


@pytest.fixture
def rules_off(monkeypatch):
    monkeypatch.delenv(rule_flags.ENV_ENABLED, raising=False)
    monkeypatch.delenv(rule_flags.ENV_DRYRUN, raising=False)


# ---- pair guard ---------------------------------------------------------
@pytest.mark.parametrize("enabled", ["split.event_basis@1", "pershare.never_derive@1"])
def test_half_enabled_pair_is_refused(enabled):
    with pytest.raises(ValueError, match="ship together"):
        rule_flags.per_share_pair_enabled({rule_flags.ENV_ENABLED: enabled})


def test_pair_both_or_neither():
    assert rule_flags.per_share_pair_enabled({rule_flags.ENV_ENABLED: PAIR}) is True
    assert rule_flags.per_share_pair_enabled({}) is False
    # dry_run of the split rule is not "on": classification runs stay legal
    env = {rule_flags.ENV_DRYRUN: "split.event_basis@1"}
    assert rule_flags.per_share_pair_enabled(env) is False


def test_split_mode_on_without_ru1_is_refused_before_any_query():
    class Boom:
        def execute(self, *a, **k):  # pragma: no cover - must not be reached
            raise AssertionError("queried")

    with pytest.raises(ValueError, match="ship together"):
        sb.run_split_rebase(
            Boom(),
            [1],
            environ={rule_flags.ENV_ENABLED: "split.event_basis@1"},
            run_id="r",
        )


# ---- SB-6 single writer -------------------------------------------------
@pytest.mark.parametrize("concept", OWNED)
def test_exactly_one_writer_per_owned_concept_with_the_pair_on(concept):
    assert sb.registered_writers(concept, {rule_flags.ENV_ENABLED: PAIR}) == [
        "share_basis"
    ]


@pytest.mark.parametrize("concept", OWNED)
def test_legacy_writers_unchanged_with_the_pair_off(concept):
    writers = sb.registered_writers(concept, {})
    assert "share_basis" not in writers
    assert writers  # every owned concept had at least one legacy writer
    if concept != "shares_outstanding_resolved":
        assert "conflict_resolution.conflict_fill" in writers


def test_retroactive_adjuster_issues_no_query_with_the_pair_on(pair_on):
    class Boom:
        def cursor(self):  # pragma: no cover - must not be reached
            raise AssertionError("queried")

    out = stock_splits.resolve_retroactive_split_adjustments(Boom())
    assert out["adjusted"] == 0 and out["skipped"] is True


# ---- SB-7 consumers -----------------------------------------------------
class _ConceptConn:
    """Answers canonical_concept name lookups; records the names asked."""

    def __init__(self, catalog):
        self.catalog = catalog
        self.asked = []

    def cursor(self):
        return self

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def execute(self, sql, params=()):
        names = params[0]
        names = [names] if isinstance(names, str) else list(names)
        self.asked.extend(names)
        self._rows = [(n, self.catalog[n]) for n in names if n in self.catalog]

    def fetchall(self):
        return self._rows

    def fetchone(self):
        return (self._rows[0][1],) if self._rows else None
