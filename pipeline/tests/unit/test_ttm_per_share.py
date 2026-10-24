"""RU-1 (WO-2, 2026-10-22): per-share values in ttm.py.

- No YTD route (YTD + prior FY - prior YTD) for a per-share concept: it is a
  subtraction of per-share values, never valid.
- EPS/DPS growth rows whose current or prior side is a derived value, or an
  unfiled Q4 whose FY is filed, are null with the input's own cause
  (PER_SHARE_NOT_DERIVED_REASON), not missing:prior_period and not absent.
Real values: MSFT FY26 diluted EPS (Q4 derived 4.80, filed 4.81, 8-K
0001193125-26-323632 Ex. 99.1); Symbotic net income (YTD route fixture).
"""

from datetime import date
from decimal import Decimal

import pytest
from scrooner_pipeline.common.derivation_policy import PER_SHARE_NOT_DERIVED_REASON
from scrooner_pipeline.mapper import ttm
from scrooner_pipeline.mapper.ttm import FactsByPeriod, _ttm_sum


@pytest.fixture(autouse=True)
def _release_pair_on(monkeypatch):
    """RU-1 behaviour is flag-gated (default OFF = legacy, proven by the
    *_legacy_off.py copy of this module); these tests exercise it ON."""
    monkeypatch.setenv(
        "SCROONER_RULES_ENABLED",
        "split.event_basis@1,pershare.never_derive@1,derive.periodic_inputs_only@1",
    )
    monkeypatch.delenv("SCROONER_RULES_DRYRUN", raising=False)


FY25 = (date(2024, 9, 29), date(2025, 9, 27), Decimal("-16937"), [1], 100)
NINE_M_25 = (date(2024, 9, 29), date(2025, 6, 28), Decimal("-8902"), [2], 100)
NINE_M_26 = (date(2025, 9, 28), date(2026, 6, 27), Decimal("16244"), [3], 100)
Q3_26 = (Decimal("11673"), [4], date(2026, 3, 29), date(2026, 6, 27))


@pytest.mark.unit
def test_per_share_series_never_takes_the_ytd_route():
    # The same inputs give a YTD TTM for an additive series (test_ttm_ytd_fallback).
    facts = FactsByPeriod({(2026, "Q3"): Q3_26})
    facts.durations = [FY25, NINE_M_25, NINE_M_26]
    assert _ttm_sum(facts, 2026, "Q3")[0] is not None
    facts.per_share = True
    assert _ttm_sum(facts, 2026, "Q3") == (None, [])


class _Cursor:
    def __init__(self, rows):
        self.rows = rows

    def __enter__(self):
        return self

    def __exit__(self, *_a):
        return False

    def execute(self, sql, params=None):
        self.sql = sql

    def fetchall(self):
        return self.rows


class _Conn:
    def __init__(self, rows):
        self.rows = rows

    def cursor(self):
        return _Cursor(self.rows)


LOADER_ROWS = [
    # fy, fp, value, fids, start, end, source_concept_id, any_derived
    (
        2026,
        "Q4",
        Decimal("4.80"),
        [341935],
        date(2026, 4, 1),
        date(2026, 6, 30),
        5,
        True,
    ),
    (
        2026,
        "FY",
        Decimal("17.95"),
        [341900],
        date(2025, 7, 1),
        date(2026, 6, 30),
        5,
        False,
    ),
    (
        None,
        None,
        Decimal("13.15"),
        [341901],
        date(2025, 7, 1),
        date(2026, 3, 31),
        5,
        False,
    ),
]


@pytest.mark.unit
def test_loader_marks_per_share_series_and_drops_its_ytd_durations():
    per_share = ttm._load_company_facts(_Conn(LOADER_ROWS), 1, 9, per_share=True)
    assert per_share.per_share is True
    assert per_share.durations == []
    assert per_share.derived_keys == frozenset({(2026, "Q4")})

    additive = ttm._load_company_facts(_Conn(LOADER_ROWS), 1, 9)
    assert additive.per_share is False
    assert len(additive.durations) == 3  # the 9M YTD stays available to additive TTMs


def _facts(entries, *, per_share, derived=()):
    out = FactsByPeriod(entries)
    out.durations = []
    out.per_share = per_share
    out.derived_keys = frozenset(derived)
    return out


class _WriteConn:
    def __init__(self):
        self.inserted = []

    def cursor(self):
        conn = self

        class C:
            def __enter__(self):
                return self

            def __exit__(self, *_a):
                return False

            def execute(self, *_a):
                pass

            def executemany(self, _sql, rows):
                conn.inserted.extend(rows)

        return C()

    def commit(self):
        pass


def _run_growth(monkeypatch, by_concept, q4_periods):
    concept_ids = {
        name: i
        for i, name in enumerate(sorted({c for c, _ in ttm.GROWTH_METRICS.values()}), 1)
    }
    requested: list[str] = []

    def _concept_id(_c, name):
        requested.append(name)
        return concept_ids[name.removesuffix("_resolved")]

    monkeypatch.setattr(ttm, "_load_concept_id", _concept_id)
    names = {v: k for k, v in concept_ids.items()}
    monkeypatch.setattr(
        ttm,
        "_load_company_facts",
        lambda _c, _co, cid, per_share=False: by_concept.get(
            names[cid], _facts({}, per_share=per_share)
        ),
    )
    monkeypatch.setattr(ttm, "_load_q4_periods", lambda _c, _co: q4_periods)
    metric_ids = {m: i for i, m in enumerate(ttm.GROWTH_METRICS, 1)}
    conn = _WriteConn()
    ttm._compute_growth_for_company(conn, 1, metric_ids)
    yoy = metric_ids["eps_growth_yoy"]
    return {
        (r["period_label"], r["period_end"]): r
        for r in conn.inserted
        if r["metric_definition_id"] == yoy
    }, conn


Q4_25 = (date(2025, 4, 1), date(2025, 6, 30))
Q4_26 = (date(2026, 4, 1), date(2026, 6, 30))
FY_25 = (date(2024, 7, 1), date(2025, 6, 30))
FY_26 = (date(2025, 7, 1), date(2026, 6, 30))


@pytest.mark.unit
def test_eps_growth_on_a_derived_q4_carries_the_per_share_reason(monkeypatch):
    # MSFT: Q4 FY26 derived 4.80 (filed 4.81) vs a filed Q4 FY25.
    # Kills: dropping the derived check (would compute (4.80-3.84)/3.84).
    eps = _facts(
        {
            (2026, "Q4"): (Decimal("4.80"), [341935], *Q4_26),
            (2025, "Q4"): (Decimal("3.84"), [300001], *Q4_25),
            (2026, "FY"): (Decimal("17.95"), [341900], *FY_26),
            (2025, "FY"): (Decimal("13.64"), [300000], *FY_25),
        },
        per_share=True,
        derived={(2026, "Q4")},
    )
    rows, _ = _run_growth(monkeypatch, {"diluted_eps": eps}, {})
    q4 = rows[("Q4", Q4_26[1])]
    assert q4["value"] is None and q4["is_null_reason"] == PER_SHARE_NOT_DERIVED_REASON
    fy = rows[("FY", FY_26[1])]
    assert fy["is_null_reason"] is None
    assert fy["value"] == (Decimal("17.95") - Decimal("13.64")) / Decimal("13.64")


@pytest.mark.unit
def test_unfiled_q4_gets_a_reasoned_row_instead_of_no_row(monkeypatch):
    # After the reviewed retirement: FY filed, Q4 per-share absent. The Q4
    # growth row must exist, dated from the company's own Q4 period, with the
    # per-share reason. Kills: removing the injection (no row = no reason).
    eps = _facts(
        {
            (2026, "FY"): (Decimal("17.95"), [341900], *FY_26),
            (2025, "FY"): (Decimal("13.64"), [300000], *FY_25),
        },
        per_share=True,
    )
    rows, _ = _run_growth(monkeypatch, {"diluted_eps": eps}, {2026: Q4_26, 2025: Q4_25})
    q4 = rows[("Q4", Q4_26[1])]
    assert q4["period_start"] == Q4_26[0]
    assert q4["value"] is None and q4["is_null_reason"] == PER_SHARE_NOT_DERIVED_REASON


@pytest.mark.unit
def test_filed_q4_compared_with_unfiled_prior_q4_passes_the_cause_through(monkeypatch):
    # A 10-K quarterly table filed Q4 FY26 EPS; FY25's Q4 was never filed.
    eps = _facts(
        {
            (2026, "Q4"): (Decimal("4.81"), [400001], *Q4_26),
            (2026, "FY"): (Decimal("17.95"), [341900], *FY_26),
            (2025, "FY"): (Decimal("13.64"), [300000], *FY_25),
        },
        per_share=True,
    )
    rows, _ = _run_growth(monkeypatch, {"diluted_eps": eps}, {2025: Q4_25})
    assert rows[("Q4", Q4_26[1])]["is_null_reason"] == PER_SHARE_NOT_DERIVED_REASON


@pytest.mark.unit
def test_both_q4s_filed_still_compute(monkeypatch):
    eps = _facts(
        {
            (2026, "Q4"): (Decimal("4.81"), [400001], *Q4_26),
            (2025, "Q4"): (Decimal("3.84"), [300001], *Q4_25),
        },
        per_share=True,
    )
    rows, _ = _run_growth(monkeypatch, {"diluted_eps": eps}, {})
    q4 = rows[("Q4", Q4_26[1])]
    assert q4["value"] == (Decimal("4.81") - Decimal("3.84")) / Decimal("3.84")


@pytest.mark.unit
def test_additive_derived_q4_growth_is_unchanged(monkeypatch):
    # Revenue Q4 = FY - 9M is additive: growth is still computed from it.
    revenue = _facts(
        {
            (2026, "Q4"): (Decimal("76400000000"), [1], *Q4_26),
            (2025, "Q4"): (Decimal("64700000000"), [2], *Q4_25),
        },
        per_share=False,
        derived={(2026, "Q4")},
    )
    metric_ids = {m: i for i, m in enumerate(ttm.GROWTH_METRICS, 1)}
    _rows, conn = _run_growth(monkeypatch, {"revenue": revenue}, {})
    rev = next(
        r
        for r in conn.inserted
        if r["metric_definition_id"] == metric_ids["revenue_growth_yoy"]
        and r["period_end"] == Q4_26[1]
    )
    assert rev["is_null_reason"] is None
    assert rev["value"] == (Decimal("76400000000") - Decimal("64700000000")) / Decimal(
        "64700000000"
    )


@pytest.mark.unit
def test_injected_q4_never_duplicates_a_span_already_keyed(monkeypatch):
    # A mislabelled twin (W5): the Q4 span is already present under another key.
    eps = _facts(
        {
            (2027, "Q4"): (Decimal("4.81"), [400001], *Q4_26),
            (2026, "FY"): (Decimal("17.95"), [341900], *FY_26),
        },
        per_share=True,
    )
    _rows, conn = _run_growth(monkeypatch, {"diluted_eps": eps}, {2026: Q4_26})
    keys = [
        (
            r["metric_definition_id"],
            r["period_start"],
            r["period_end"],
            r["period_label"],
        )
        for r in conn.inserted
    ]
    assert len(keys) == len(set(keys))


@pytest.mark.unit
def test_pre_cutoff_q4_reason_says_not_captured(monkeypatch):
    # FY2019 10-K had to file Q4 EPS (Item 302(a)); a blank there is ours.
    q4_19 = (date(2019, 4, 1), date(2019, 6, 30))
    fy_19, fy_18 = (
        (date(2018, 7, 1), date(2019, 6, 30)),
        (date(2017, 7, 1), date(2018, 6, 30)),
    )
    eps = _facts(
        {
            (2019, "Q4"): (Decimal("1.71"), [1], *q4_19),
            (2019, "FY"): (Decimal("4.75"), [2], *fy_19),
            (2018, "FY"): (Decimal("2.13"), [3], *fy_18),
        },
        per_share=True,
        derived={(2019, "Q4")},
    )
    rows, _ = _run_growth(monkeypatch, {"diluted_eps": eps}, {})
    from scrooner_pipeline.common.derivation_policy import PER_SHARE_NOT_CAPTURED_REASON

    assert rows[("Q4", q4_19[1])]["is_null_reason"] == PER_SHARE_NOT_CAPTURED_REASON
