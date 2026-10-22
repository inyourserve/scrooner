"""Total-debt guards, lane 3: flag OFF identity, persisted blank reasons, the R5 floor
discount/issuance-cost exemption, the guard-reached-fallback hold (R6) and the partial-component
hold (R7).

Fixtures are real company-instants (tags and values from the stored core.fact, top-1000 dry run
2026-10-21, DATA-INFERRED) and, where stated, FILING-CHECKED against the filing's balance sheet R-file:
  CVX FY2016  0000093410-17-000013 R5: short-term debt 10,840 + long-term debt 35,193 = 46,033
  DPZ FY2024  0000950170-25-025223 R2: current portion 1,149,679 + long-term 3,825,659 = 4,975,338 ($K)
  PFE FY2020  0000078003-21-000038 R4: short-term borrowings incl. current LTD 2,703 + LTD 37,133 = 39,836
  AAPL FY2015 0001193125-15-356351 R5: CP 8,499 + current LTD 2,500 + LTD 53,463 = 64,462
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from scrooner_pipeline.common.cell_blank_reason import (
    InMemoryBlankReasonStore,
    PgBlankReasonStore,
)
from scrooner_pipeline.mapper import concept_fallback as cf

M = Decimal(1_000_000)
ON = {"SCROONER_RULES_ENABLED": cf.RULE_DEBT}


def D(**tags):
    """tags in $M -> {tag: (value, fact_id)}"""
    return {t: (Decimal(str(v)) * M, i) for i, (t, v) in enumerate(tags.items(), 1)}


HIG = D(
    LongTermDebt=4366,
    LineOfCredit=0,
    LongTermDebtNoncurrent=4366,
    DebtLongtermAndShorttermCombinedAmount=4366,
    NotesPayable=4482,
    DebtInstrumentUnamortizedDiscountPremiumAndDebtIssuanceCostsNet=116,
)
WMT = D(
    LongTermDebt=39579,
    ShortTermBorrowings=878,
    LongTermDebtCurrent=3447,
    LongTermDebtNoncurrent=36132,
    DebtLongtermAndShorttermCombinedAmount=39579,
    UnsecuredDebt=40405,
)
CVX = D(
    CommercialPaper=10410,
    LongTermDebt=32490,
    OtherShortTermBorrowings=0,
    ShortTermBorrowings=10840,
    LongTermDebtCurrent=6253,
    LongTermDebtNoncurrent=35193,
    DebtCurrent=19840,
    ShortTermBankLoansAndNotesPayable=50,
)
DPZ = D(
    LongTermDebt="14.7",
    OtherBorrowings="14.788",
    LongTermDebtCurrent="0.1",
    LongTermDebtAndCapitalLeaseObligations="3825.659",
    LongTermDebtAndCapitalLeaseObligationsCurrent="1149.679",
    DebtAndCapitalLeaseObligations="4975.338",
)
PFE = D(
    CommercialPaper=556,
    LongTermDebt=4000,
    OtherShortTermBorrowings=145,
    LongTermDebtCurrent=2002,
    LongTermDebtNoncurrent=37133,
    DebtCurrent=2703,
)
LAD = D(
    LongTermDebt="439.558",
    LongTermDebtNoncurrent="485.2",
    DebtInstrumentCarryingAmount="793.065",
    LongTermDebtAndCapitalLeaseObligations="769.916",
    LongTermDebtAndCapitalLeaseObligationsCurrent="20.965",
    SecuredDebt="428.367",
    OtherLongTermDebt="11.191",
    DebtAndCapitalLeaseObligations="2392.378",
)
AAPL_2015 = D(
    CommercialPaper=8499, LongTermDebtCurrent=2500, DebtInstrumentCarryingAmount=55701
)
DD_2020 = D(LongTermDebtAndCapitalLeaseObligationsCurrent=1)
MMM = D(LongTermDebt=13092, LongTermDebtNoncurrent=20593, DebtCurrent=820)
COR = D(
    LongTermDebt="177.453",
    LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities="4310.189",
    LongTermDebtCurrent="13.976",
    LongTermDebtNoncurrent="4158.532",
    DebtCurrent="151.657",
    LongTermDebtAndCapitalLeaseObligations="4310.189",
)
ALL = cf.ALL_DEBT_GUARDS


# ------------------------------------------------------------------ flag OFF identity
CASES = [HIG, WMT, CVX, DPZ, PFE, LAD, AAPL_2015, DD_2020, MMM, COR]


@pytest.mark.parametrize(
    "facts",
    CASES,
    ids=["HIG", "WMT", "CVX", "DPZ", "PFE", "LAD", "AAPL", "DD", "MMM", "COR"],
)
def test_flag_off_is_byte_identical_to_the_compose_only_path(facts, monkeypatch):
    monkeypatch.delenv("SCROONER_RULES_ENABLED", raising=False)
    assert cf.debt_guards_active() == frozenset()
    assert cf.compute_total_debt(facts) == cf._compose_total_debt(facts)
    assert cf.debt_preference_is_applicable("us-gaap", "ShortTermBorrowings") is True


def test_family_flag_enables_all_and_sub_rule_flag_enables_one(monkeypatch):
    assert cf.debt_guards_active(ON) == ALL
    one = {"SCROONER_RULES_ENABLED": f"{cf.RULE_DEBT}/{cf.GUARD_FLOOR}"}
    assert cf.debt_guards_active(one) == frozenset({cf.GUARD_FLOOR})
    assert cf.debt_preference_guard_active(one) is False
    assert cf.debt_preference_guard_active(
        {"SCROONER_RULES_ENABLED": f"{cf.RULE_DEBT}/{cf.GUARD_PREFERENCE}"}
    )


# ------------------------------------------------------------------ R5 floor exemption
def test_hig_gap_equals_filed_discount_and_issuance_cost_so_own_total_is_published():
    without_exemption = D(
        **{t: v[0] / M for t, v in HIG.items() if "Unamortized" not in t}
    )
    assert (
        cf.evaluate_total_debt(without_exemption, ALL).value is None
    )  # floor blanks it
    kept = cf.evaluate_total_debt(HIG, ALL)
    assert kept.value == Decimal(4366) * M and kept.guards_fired == ()


def test_floor_exemption_is_not_a_tolerance_widening_wmt_stays_blank():
    # WMT 2024-01-31: UnsecuredDebt 40,405 vs total 39,579, no discount tag filed.
    d = cf.evaluate_total_debt(WMT, ALL)
    assert d.value is None and d.reason == cf.REASON_UNDECIDABLE_FLOOR


def test_floor_exemption_needs_the_gap_to_match_within_half_a_percent():
    near = dict(HIG)
    near["DebtInstrumentUnamortizedDiscountPremiumAndDebtIssuanceCostsNet"] = (
        Decimal(116) * M * Decimal("1.10"),
        99,
    )
    assert (
        cf.evaluate_total_debt(near, ALL).value is None
    )  # coincidence control: gap shifted 10%


def test_floor_exemption_accepts_discount_plus_issuance_cost_pair():
    # AR 2020-12-31: gap 127,605K = DiscountPremiumNet 111,886K + DeferredFinanceCostsNoncurrentNet 16,000K (+/- 0.005)
    ar = {
        "LongTermDebtNoncurrent": (Decimal("3001593000"), 1),
        "LongTermLineOfCredit": (Decimal("3129198000"), 2),
        "DebtInstrumentUnamortizedDiscountPremiumNet": (Decimal("111886000"), 3),
        "DeferredFinanceCostsNoncurrentNet": (Decimal("16000000"), 4),
    }
    assert cf.evaluate_total_debt(ar, ALL).value == Decimal("3001593000")
    ar.pop("DeferredFinanceCostsNoncurrentNet")
    assert cf.evaluate_total_debt(ar, ALL).value is None


# ------------------------------------------------------------------ R6 guard-reached fallback
def test_cvx_2016_overcount_is_held_not_published():
    # stored 43,330M and guard-new 55,033M are both wrong; the filing's debt is 46,033M.
    d = cf.evaluate_total_debt(CVX, ALL)
    assert d.value is None and d.reason == cf.REASON_UNDECIDABLE_FALLBACK
    assert cf.GUARD_FALLBACK in d.guards_fired
    # without r6 the guards would have published the overcount
    assert (
        cf.evaluate_total_debt(CVX, ALL - {cf.GUARD_FALLBACK}).value
        == Decimal(55033) * M
    )


def test_dpz_2024_resolves_to_the_filed_lease_inclusive_total():
    d = cf.evaluate_total_debt(DPZ, ALL)
    assert d.value == Decimal("4975338000") and d.path == "lease_family_sum"
    assert cf.evaluate_total_debt(DPZ, ALL - {cf.GUARD_FALLBACK}).value == Decimal(
        "3825759000"
    )  # understated


def test_pfe_2020_current_debt_is_explained_so_the_new_value_stands():
    d = cf.evaluate_total_debt(PFE, ALL)
    assert d.value == Decimal(39836) * M and d.path == "noncurrent+debt_current"


def test_lad_2016_total_far_below_lease_inclusive_total_is_held():
    d = cf.evaluate_total_debt(LAD, ALL)
    assert d.value is None and d.reason == cf.REASON_UNDECIDABLE_LEASE


def test_mmm_and_cor_cases_with_nothing_contradicting_them_are_accepted():
    assert cf.evaluate_total_debt(MMM, ALL).value == Decimal(21413) * M
    assert cf.evaluate_total_debt(COR, ALL).value == Decimal("4310189000")


def test_r6_only_applies_where_a_guard_reached_the_fallback():
    # same CVX tags without the LongTermDebt that failed containment: no guard fired, r6 silent
    facts = {t: v for t, v in CVX.items() if t != "LongTermDebt"}
    assert cf.evaluate_total_debt(facts, ALL).guards_fired == ()


# ------------------------------------------------------------------ R7 partial component
def test_aapl_2015_current_only_total_is_blanked():
    assert (
        cf._compose_total_debt(AAPL_2015)[0] == Decimal(10999) * M
    )  # the stored wrong value
    d = cf.evaluate_total_debt(AAPL_2015, ALL)
    assert d.value is None and d.reason == cf.REASON_PARTIAL_COMPONENT


def test_dd_2020_single_current_lease_tag_is_blanked():
    assert cf.evaluate_total_debt(DD_2020, ALL).value is None


def test_r7_does_not_fire_when_a_long_term_block_is_filed():
    facts = D(LongTermDebtNoncurrent=100, LongTermDebtCurrent=10)
    assert cf.evaluate_total_debt(facts, ALL).value == Decimal(110) * M


# ------------------------------------------------------------------ writer: persisted reasons
class _Cur:
    def __init__(self, c):
        self.c = c
        self.res = []

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def execute(self, sql, params=None):
        sql = " ".join(sql.split())
        self.c.sql.append((sql, params))
        if sql.startswith("select id from analytics.canonical_concept"):
            self.res = [(7,)]
        elif sql.startswith("select c.id from core.company"):
            self.res = [(1,), (2,)]
        elif sql.startswith("select count(*) from core.company"):
            self.res = [(2,)]
        elif "from core.fact f" in sql:
            e = date(2016, 12, 31)
            rows = []
            for company, facts in ((1, CVX), (2, PFE)):
                for tag, (v, fid) in facts.items():
                    rows.append((company, 100 + company, tag, v, fid, e))
            self.res = rows
        elif sql.startswith(
            "select company_id, period_id, value from analytics.canonical_fact"
        ):
            self.res = [(1, 101, Decimal(43330) * M), (2, 102, Decimal(4556) * M)]
        elif sql.startswith("select id, cik from core.company"):
            self.res = [(1, "0000093410"), (2, "0000078003")]
        else:
            self.res = []

    def executemany(self, sql, rows):
        self.c.inserted.extend(rows)

    def fetchall(self):
        return self.res

    def fetchone(self):
        return self.res[0] if self.res else None


class _Conn:
    def __init__(self):
        self.sql, self.inserted = [], []

    def cursor(self):
        return _Cur(self)

    def commit(self):
        pass

    def rollback(self):
        pass

    def writes(self):
        return [
            s for s, _ in self.sql if s.startswith(("delete", "insert"))
        ] + self.inserted


def test_blocked_instant_reason_is_persisted_with_its_dates_and_rule_id():
    conn, store = _Conn(), InMemoryBlankReasonStore()
    stats = cf.resolve_total_debt_components(
        conn, {"x"}, reason_store=store, run_id="r1", environ=ON
    )
    rows = store.all()
    assert [r.company_id for r in rows] == [1]  # CVX held; PFE published
    r = rows[0]
    assert (r.data_point, r.period_grain, r.period_end, r.rule_id, r.reason_code) == (
        "total_debt_resolved",
        "instant",
        date(2016, 12, 31),
        cf.RULE_DEBT,
        "guard_hidden",
    )
    assert r.detail["reason"] == cf.REASON_UNDECIDABLE_FALLBACK
    assert stats["reasons_written"] == 1 and stats["rows_written"] == 1
    assert (1, "r1") != (2, "r1") and (
        2,
        cf.RULE_DEBT,
        "r1",
    ) in store.rows  # PFE's empty replace cleared its own scope


def test_reason_replace_scope_is_own_rule_and_company():
    store = InMemoryBlankReasonStore()
    foreign = cf.BlankReason(
        2, "x", "instant", None, None, "resolved", "other.rule@1", "guard_hidden"
    )
    with pytest.raises(ValueError):
        store.replace(1, cf.RULE_DEBT, "r1", [foreign])


def test_live_run_with_guards_refuses_without_the_reason_table():
    conn = _Conn()
    pg = MagicMock(spec=PgBlankReasonStore)
    pg.__class__ = PgBlankReasonStore
    pg.require_table.side_effect = RuntimeError(
        "analytics.cell_blank_reason does not exist"
    )
    with pytest.raises(RuntimeError):
        cf.resolve_total_debt_components(conn, {"x"}, reason_store=pg, environ=ON)
    assert conn.writes() == []


def test_flag_off_writes_old_values_and_no_reasons():
    conn = _Conn()
    store = InMemoryBlankReasonStore()
    stats = cf.resolve_total_debt_components(
        conn, {"x"}, reason_store=store, environ={}
    )
    assert (
        store.all() == [] and stats["reasons_written"] == 0 and stats["blocked"] == {}
    )
    vals = {r[0]: r[3] for r in conn.inserted}
    assert (
        vals[1] == Decimal(43330) * M
    )  # CVX composed the pre-guard way (ltd_incl_current+short_term)


def test_dry_run_writes_nothing_and_reports_before_after():
    conn = _Conn()
    stats = cf.resolve_total_debt_components(conn, {"x"}, dry_run=True, environ={})
    assert conn.writes() == []
    planned = {p.cik: p for p in stats["planned"]}
    assert (
        planned["0000093410"].before == Decimal(43330) * M
        and planned["0000093410"].after is None
    )
    assert (
        planned["0000078003"].before == Decimal(4556) * M
        and planned["0000078003"].after == Decimal(39836) * M
    )
