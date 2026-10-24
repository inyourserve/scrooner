"""SB-6 / SB-7 / SB-8 and the release pair: split.event_basis@1 and
pershare.never_derive@1 ship together, default OFF = legacy.

- pair guard: exactly one of the two ON is refused;
- SB-6: with the pair ON each owned resolved concept has exactly one
  writer (share_basis); OFF keeps the legacy writers;
- SB-7: consumers read the current-basis twins only with the pair ON;
- SB-8: the nightly stage sits after resolve-facts and is a no-op when OFF;
- RU-1 gates: OFF never loads the per-share guard or the form-gated SQL.
"""

from pathlib import Path

import pytest
from scrooner_pipeline.common import rule_flags
from scrooner_pipeline.corporate_actions import share_basis as sb
from scrooner_pipeline.corporate_actions import stock_splits
from scrooner_pipeline.mapper import dividend_streak, price_metrics, ttm
from scrooner_pipeline.normalizer import derived

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


def test_price_metrics_points_per_share_inputs_at_their_twins():
    conn = _ConceptConn(
        {"diluted_eps_resolved": 254, "dividends_per_share_resolved": 292,
         "shares_outstanding_resolved": 350}
    )  # fmt: skip
    ids = {
        "diluted_eps": 15,
        "dividends_per_share": 17,
        "shares_outstanding": 16,
        "revenue": 1,
    }
    out = price_metrics._current_basis_ids(conn, ids)
    assert out == {
        "diluted_eps": 254,
        "dividends_per_share": 292,
        "shares_outstanding": 350,
        "revenue": 1,
    }


def test_missing_twin_drops_the_input_instead_of_reading_as_filed():
    conn = _ConceptConn({"diluted_eps_resolved": 254})
    out = price_metrics._current_basis_ids(
        conn, {"diluted_eps": 15, "dividends_per_share": 17}
    )
    assert out == {"diluted_eps": 254}


def test_ttm_growth_reads_the_current_basis_twin_only_with_the_pair_on(monkeypatch):
    asked = []

    def _cid(_c, name):
        if "eps" in name:
            asked.append(name)
            raise StopIteration  # stop at the first EPS growth input
        return 1

    monkeypatch.setattr(ttm, "_load_concept_id", _cid)
    monkeypatch.setattr(ttm, "_load_company_facts", lambda *a, **k: ttm.FactsByPeriod())
    for env, expected in ((PAIR, "diluted_eps_resolved"), ("", "diluted_eps")):
        asked.clear()
        monkeypatch.setenv(rule_flags.ENV_ENABLED, env)
        with pytest.raises(StopIteration):
            ttm._compute_growth_for_company(None, 1, {})
        assert asked[0] == expected


@pytest.mark.parametrize(
    "env,name", [(PAIR, "dividends_per_share_resolved"), ("", "dividends_per_share")]
)
def test_dividend_streak_series_follows_the_pair(monkeypatch, env, name):
    monkeypatch.setenv(rule_flags.ENV_ENABLED, env)
    conn = _ConceptConn({name: 7})
    assert dividend_streak._load_concept_id(conn) == 7
    assert conn.asked == [name]


# ---- RU-1 gates OFF = legacy -------------------------------------------
class _Cur:
    def __init__(self):
        self.sql = []

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def execute(self, sql, params=()):
        self.sql.append(" ".join(sql.split()))

    def fetchall(self):
        return []


class _Conn:
    def __init__(self):
        self.cur = _Cur()

    def cursor(self):
        return self.cur


def test_form_gate_off_uses_the_legacy_sql(rules_off):
    conn = _Conn()
    derived._load_quarterly_candidates(conn, 1)
    derived._load_all_duration_facts(conn, 1)
    assert all("core.filing" not in s and "fl.form" not in s for s in conn.cur.sql)


def test_form_gate_on_filters_by_form(monkeypatch):
    monkeypatch.setenv(rule_flags.ENV_ENABLED, derived.FORM_GATE_RULE)
    conn = _Conn()
    derived._load_quarterly_candidates(conn, 1)
    assert "fl.form = any(" in conn.cur.sql[0]


def test_per_share_guard_off_never_loads_the_non_additive_sets(monkeypatch, rules_off):
    def boom(_conn):  # pragma: no cover - must not be reached
        raise AssertionError("guard loaded with the pair off")

    monkeypatch.setattr(derived, "_load_non_additive", boom)
    monkeypatch.setattr(derived, "_load_quarterly_candidates", lambda c, i: [])
    monkeypatch.setattr(derived, "_load_average_concept_ids", lambda c: set())
    monkeypatch.setattr(derived, "_load_all_duration_facts", lambda c, i: [])
    derived.derive_q4_for_company(_Conn(), 1)
    derived.derive_interim_quarters_for_company(_Conn(), 1)


# ---- SB-8 wiring --------------------------------------------------------
def test_nightly_runs_split_rebase_right_after_resolve_facts():
    script = (
        Path(__file__).parents[2] / "scripts/reprocess_recent_filers.sh"
    ).read_text()
    order = script[script.index("STAGES=(") :]
    assert "map:resolve-facts map:split-rebase map:resolve-concept-fallbacks" in order


def test_split_rebase_cli_is_a_no_op_with_the_rule_off(monkeypatch, rules_off):
    from scrooner_pipeline.jobs import map as map_job
    from typer.testing import CliRunner

    def boom():  # pragma: no cover - must not be reached
        raise AssertionError("connected while off")

    monkeypatch.setattr(map_job, "get_connection", boom)
    res = CliRunner().invoke(map_job.app, ["split-rebase", "--ciks", "0000320193"])
    assert res.exit_code == 0, res.output
    assert "is off; nothing done" in res.output


@pytest.mark.parametrize("env", [PAIR, ""])
def test_conflict_fill_driver_visits_only_active_targets(monkeypatch, env):
    from scrooner_pipeline.mapper import concept_fallback
    from scrooner_pipeline.mapper import conflict_resolution as cr

    monkeypatch.setenv(rule_flags.ENV_ENABLED, env)
    seen: list[str] = []
    monkeypatch.setattr(
        cr, "resolve_baseline_passthrough", lambda c, p, r: seen.append(r) or 0
    )
    monkeypatch.setattr(cr, "resolve_conflict_fill", lambda c, p, r: {"filled": 0})
    monkeypatch.setattr(
        cr, "resolve_split_like_conflicts", lambda c, p, r: {"filled": 0}
    )
    monkeypatch.setattr(
        cr, "resolve_operating_income_arithmetic_fallback", lambda c: {}
    )
    monkeypatch.setattr(concept_fallback, "resolve_capex_with_software", lambda c: 0)
    monkeypatch.setattr(
        concept_fallback, "resolve_depreciation_and_amortization_max", lambda c: 0
    )
    monkeypatch.setattr(stock_splits, "detect_stock_splits", lambda c: {})
    monkeypatch.setattr(
        stock_splits, "resolve_retroactive_split_adjustments", lambda c: {}
    )
    cr.resolve_all_conflict_fills(None)
    owned_seen = set(seen) & cr.SHARE_BASIS_OWNED
    assert (owned_seen == set()) if env else (owned_seen == {
        "diluted_eps_resolved", "basic_eps_resolved", "dividends_per_share_resolved"
    })  # fmt: skip


@pytest.mark.parametrize("env", [PAIR, ""])
def test_dedup_driver_visits_only_active_concepts(monkeypatch, env):
    from scrooner_pipeline.mapper import dedup_majority_resolver as dm

    monkeypatch.setenv(rule_flags.ENV_ENABLED, env)
    seen: list[str] = []
    monkeypatch.setattr(
        dm, "resolve_majority_vote_for_concept", lambda c, n, r: seen.append(r) or {}
    )
    dm.resolve_all_safe_concepts(None)
    owned_seen = set(seen) & set(sb.TARGETS)
    assert (owned_seen == set()) if env else (owned_seen == set(sb.TARGETS))
