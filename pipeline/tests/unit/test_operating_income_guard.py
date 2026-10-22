"""T2 operating-income guard (WO-14, RF-14). Real facts: AFG/ELS/MOG-A named holds (filing evidence
in NAMED_HOLDS), values from the stored canonical rows 2026-10-22. Identity fixtures are SYNTHETIC
and labelled so."""

from __future__ import annotations

from datetime import date
from decimal import Decimal as D

from scrooner_pipeline.common.cell_blank_reason import InMemoryBlankReasonStore
from scrooner_pipeline.mapper import operating_income_guard as g

ON = {"SCROONER_RULES_ENABLED": g.RULE_ID}


def cell(pid, oi, *, fb=False, pre=None, rev=None, opex=None, cor=None):
    f = lambda x: None if x is None else D(x)  # noqa: E731
    return g.OiCell(pid, D(oi), fb, f(pre), f(rev), f(opex), f(cor))


# ---------------------------------------------------------------- named holds
def test_named_cases_afg_els_mog_met_hona_are_all_hidden_with_evidence():
    for cik in ("0001042046", "0000895417", "0000067887", "0001099219", "0002089271"):
        r = g.decide_company(cik, [cell(1, "1073000000")])
        assert r.hidden == [(1, g.REASON_NAMED)], cik
        assert g.NAMED_HOLDS[cik].evidence


# ---------------------------------------------------------------- fallback identity (SYNTHETIC)
def overlaps(*triples):
    return [g.Overlap(D(oi), D(rev), D(opex), None) for oi, rev, opex in triples]


def test_fallback_needs_two_matching_overlap_periods():
    assert g.fallback_identity_ok(overlaps((400, 1000, 600), (410, 1100, 690)))
    assert not g.fallback_identity_ok(
        overlaps((400, 1000, 600))
    )  # one overlap: no evidence
    assert not g.fallback_identity_ok(
        []
    )  # no overlap: no evidence (CVX/AJG/HTZ-type, reasoned blank)


def test_one_overlap_period_missing_the_identity_by_more_than_2pct_fails_the_company():
    assert not g.fallback_identity_ok(
        overlaps((400, 1000, 600), (410, 1100, 690), (300, 1000, 600))
    )


def test_fallback_cell_hidden_without_identity_and_kept_with_it():
    fb = cell(9, "400", fb=True, rev="1000", opex="600")
    good = [
        cell(1, "400", rev="1000", opex="600"),
        cell(2, "410", rev="1100", opex="690"),
    ]
    bad = [
        cell(1, "300", rev="1000", opex="600"),
        cell(2, "410", rev="1100", opex="690"),
    ]
    assert g.decide_company("0000000001", good + [fb]).hidden == []
    assert g.decide_company("0000000001", bad + [fb]).hidden == [(9, g.REASON_FALLBACK)]
    assert g.decide_company("0000000001", [fb]).hidden == [(9, g.REASON_FALLBACK)]


def test_real_base_oi_is_never_hidden_by_the_fallback_rule():
    assert (
        g.decide_company("0000000001", [cell(1, "300", rev="1000", opex="600")]).hidden
        == []
    )


# ---------------------------------------------------------------- pretax equal (SYNTHETIC)
def test_oi_equal_to_pretax_is_hidden_unless_the_arithmetic_vouches_for_it():
    assert g.decide_company("0000000001", [cell(1, "400", pre="400")]).hidden == [
        (1, g.REASON_PRETAX)
    ]
    # arithmetic identity holds (rev - opex = 400): OI genuinely equals pretax, keep
    assert (
        g.decide_company(
            "0000000001", [cell(1, "400", pre="400", rev="1000", opex="600")]
        ).hidden
        == []
    )
    # identity fails: hide
    assert g.decide_company(
        "0000000001", [cell(1, "400", pre="400", rev="1000", opex="300")]
    ).hidden == [(1, g.REASON_PRETAX)]
    # pretax differs by more than 0.1%: untouched
    assert g.decide_company("0000000001", [cell(1, "400", pre="420")]).hidden == []


# ---------------------------------------------------------------- DB layer with a fake connection
class _Cur:
    def __init__(self, c):
        self.c, self.res = c, []

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def execute(self, sql, params=None):
        sql = " ".join(sql.split())
        self.c.sql.append((sql, params))
        if sql.startswith("select id, cik from core.company"):
            self.res = [(1, "0001042046"), (2, "0000000002")]
        elif sql.startswith("select id, name from analytics.canonical_concept"):
            self.res = [(10, "operating_income"), (11, "operating_income_resolved")]
        elif "from analytics.canonical_fact cf" in sql:
            s, e = date(2025, 1, 1), date(2025, 12, 31)
            self.res = [
                (
                    1,
                    100,
                    "operating_income_resolved",
                    D("1073000000"),
                    [1],
                    s,
                    e,
                ),  # AFG named hold
                (
                    2,
                    200,
                    "operating_income_resolved",
                    D("500"),
                    [2],
                    s,
                    e,
                ),  # ordinary company: kept
            ]
        else:
            self.res = []

    def fetchall(self):
        return self.res


class _Conn:
    def __init__(self):
        self.sql = []

    def cursor(self):
        return _Cur(self)

    def commit(self):
        pass

    def writes(self):
        return [s for s, _ in self.sql if s.startswith(("delete", "insert"))]


def test_flag_off_is_noop():
    c = _Conn()
    assert g.apply_operating_income_guard(c, environ={})["skipped"] == "rule_off"
    assert c.sql == []


def test_dry_run_writes_nothing():
    c = _Conn()
    out = g.apply_operating_income_guard(c, dry_run=True, environ={})
    assert c.writes() == [] and out["cells_hidden"] == 1 and out[g.REASON_NAMED] == 1
    assert (
        out["planned"][0].before == D("1073000000") and out["planned"][0].after is None
    )


def test_live_deletes_exact_scope_and_stores_reason():
    c, store = _Conn(), InMemoryBlankReasonStore()
    g.apply_operating_income_guard(c, environ=ON, reason_store=store, run_id="r1")
    ((sql, params),) = [(s, p) for s, p in c.sql if s.startswith("delete")]
    assert params == (1, [10, 11], [100])
    (r,) = store.all()
    assert (r.company_id, r.rule_id, r.reason_code, r.data_point) == (
        1,
        g.RULE_ID,
        "guard_hidden",
        "operating_income_resolved",
    )
    assert r.detail["evidence"].startswith("FILING-CHECKED AFG")


def test_live_without_store_refuses():
    import pytest

    with pytest.raises(RuntimeError):
        g.apply_operating_income_guard(_Conn(), environ=ON)
