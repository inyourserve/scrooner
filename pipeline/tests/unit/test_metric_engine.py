"""Engine, provenance, applicability and golden checks for the metric registry."""

from __future__ import annotations

import json
import random
from datetime import date
from decimal import ROUND_HALF_EVEN, Decimal
from pathlib import Path

import pytest

from scrooner_pipeline.mapper.calculate_shapes import compute as legacy_compute
from scrooner_pipeline.mapper.ttm import _growth_value as legacy_growth
from scrooner_pipeline.metrics import expr
from scrooner_pipeline.metrics.applicability import (
    NOT_APPLICABLE_INSURER, alias_inputs, applicability,
)
from scrooner_pipeline.metrics.engine import DictEnv, evaluate, growth_value
from scrooner_pipeline.metrics.provenance import (
    InputCell, PeriodBasis, build_cell_record, detector_version, formula_fingerprint, gate_inputs,
    proof_is_stale, to_cell_proof_row, value_stamp,
)
from scrooner_pipeline.metrics.registry import get_registry

REG = get_registry()
GENERIC = [m for m in REG.values() if m.expression_status == "engine_wired"]
GROWTH = [m for m in REG.values() if m.expression_status == "growth_wired"]
D = Decimal


def _roles(m, vals):
    out: dict[str, list[Decimal]] = {}
    for concept, role in m.input_roles():
        out.setdefault(role, []).append(vals[concept])
    return out


def _random_values(m, rng):
    pool = [D(0), D(1), D(-5), D("0.5"), D(999999), D(1000000), D(12345678), D(-20000000), D("43135"), D(7)]
    return {c: rng.choice(pool) if rng.random() < 0.6 else D(rng.randint(1, 10**9)) for c, _ in m.input_roles()}


# ---- parser safety -----------------------------------------------------------------------------

@pytest.mark.unit
@pytest.mark.parametrize("bad", [
    "__import__('os')", "a ** 2", "a // b", "open(a)", "a.b", "max(a, b)", "lag(a, b)", "a +", "(a", "ttm(a + b)",
    "a; b", "1e3", "a if b else c", "[a]",
])
def test_parser_rejects_everything_outside_the_language(bad):
    with pytest.raises(expr.ExprError):
        expr.parse(bad)


@pytest.mark.unit
def test_parser_accepts_the_allowed_language_and_keeps_decimals():
    n = expr.parse("abs(avg(a)) + ttm(b) * 0.25 - lag(c, 1) / annual(d) + quarterly(e)")
    assert expr.names(n) == ["a", "b", "c", "d", "e"]
    assert expr.parse("0.1").value == D("0.1")


# ---- engine agrees with the live generic engine (calculate_shapes) --------------------------------

@pytest.mark.unit
@pytest.mark.parametrize("m", GENERIC, ids=lambda m: m.metric_id)
def test_engine_matches_live_shape_engine_on_random_inputs(m):
    rng = random.Random(m.metric_id)
    shape = m.shape
    denom_names = frozenset(c for c, r in m.input_roles() if r == "denominator")
    for _ in range(300):
        vals = _random_values(m, rng)
        live_v, live_r = legacy_compute(shape, _roles(m, vals), denom_names)
        res = evaluate(m, DictEnv(values=dict(vals)))
        assert res.value == live_v, (m.metric_id, vals)
        assert res.reason == live_r, (m.metric_id, vals, res.reason, live_r)
        if res.value is not None:
            assert isinstance(res.value, Decimal)


@pytest.mark.unit
def test_missing_input_is_an_incomplete_reason_and_zero_when_absent_counts_zero():
    qr = REG["quick_ratio"]
    env = DictEnv(values={"current_assets": D(50000000), "current_liabilities": D(25000000)})
    res = evaluate(qr, env)
    assert (res.value, res.reason) == (D(2), None)  # inventory absent -> zero (registry null rule)
    gm = REG["gross_margin"]
    res = evaluate(gm, DictEnv(values={"revenue": D(100)}))
    assert (res.value, res.reason) == (None, "incomplete:subtract")


@pytest.mark.unit
def test_period_rule_blocks_quarterly_for_fy_only_metrics():
    env = DictEnv(values={"net_income": D(1), "stockholders_equity": D(2)})
    assert evaluate(REG["roe"], env, check_period="Q2").reason == "period_not_applicable:fy_only"
    assert evaluate(REG["roe"], env, check_period="FY").value == D("0.5")


@pytest.mark.unit
@pytest.mark.parametrize("m", GROWTH, ids=lambda m: m.metric_id)
def test_growth_matches_live_growth_engine(m):
    rng = random.Random(m.metric_id)
    concept, lag = m.ast.args[0].name, int(m.ast.args[1].value)
    for _ in range(300):
        cur = D(rng.choice([-50, -1, 0, 3, 100, 12345]))
        prior = D(rng.choice([-50, 0, 1, 7, 100, 999999, 2000000]))
        env = DictEnv(values={concept: cur}, lags={(concept, lag): prior})
        from scrooner_pipeline.mapper.calculate_shapes import CONCEPT_MATERIALITY_FLOORS
        floor = CONCEPT_MATERIALITY_FLOORS.get(concept, D("0"))
        assert (evaluate(m, env).value, evaluate(m, env).reason) == legacy_growth(cur, prior, lag, floor)
        assert growth_value(cur, prior, lag, floor) == legacy_growth(cur, prior, lag, floor)


@pytest.mark.unit
def test_operators_ttm_avg_lag_abs_and_price_formulas_evaluate_in_decimal():
    env = DictEnv(values={"shares_outstanding": D(10), "price": D("2.5"), "stockholders_equity": D(5), "x": D(-3)},
                  ttm={"diluted_eps": D("0.5"), "revenue": D(100)}, opening={"x": D(-1)})
    assert evaluate(REG["market_cap"], env).value == D("25.0")
    assert evaluate(REG["trailing_pe"], env).value == D("5")
    assert evaluate(REG["price_to_book"], env).value == D("5.0")
    assert evaluate(REG["price_to_sales"], env).value == D("0.25")
    assert evaluate(REG["trailing_pe"], DictEnv(values={"price": D(1)}, ttm={"diluted_eps": D(0)})).reason == "zero_denominator"
    assert evaluate(REG["trailing_pe"], DictEnv(values={"price": D(1)})).reason == "missing:ttm(diluted_eps)"
    assert evaluate(REG["piotroski_f_score"], env).reason.startswith("procedural:")
    e = expr.parse("abs(avg(x)) + abs(x)")
    assert e is not None


# ---- provenance: rule (c), recompute, version invalidation -------------------------------------

FY = PeriodBasis("FY", date(2025, 1, 1), date(2025, 12, 31), "any_period")


def _cells(**status):
    vals = {"net_income": D(20), "stockholders_equity": D(80)}
    return {c: InputCell(c, status.get(c, "PROVEN"), vals[c], rule_id="tagmap.x@1", rules_commit="abc123") for c in vals}


@pytest.mark.unit
@pytest.mark.parametrize("bad", ["DISAGREE", "UNCHECKED", "HELD", "MISSING"])
def test_metric_never_computes_from_an_unserved_input(bad):
    rec = build_cell_record(REG["roe"], _cells(stockholders_equity=bad), FY)
    assert rec.value is None
    assert rec.reason == f"input_not_served:stockholders_equity:{bad}"
    row = to_cell_proof_row(rec, 1, REG["roe"])
    assert row["verdict"] == "UNCHECKED"  # a blocked metric is never a REASON
    assert row["reason_code"] == "input_not_served"


@pytest.mark.unit
def test_null_verdict_not_presented_only_for_registry_null_rules_or_a_not_presented_input():
    from scrooner_pipeline.metrics.provenance import null_verdict
    from scrooner_pipeline.mapper.top100_coverage import classify
    # registry null rules
    zero = build_cell_record(REG["roe"], {c: InputCell(c, "PROVEN", D(0) if c == "stockholders_equity" else D(5))
                                          for c in ("net_income", "stockholders_equity")}, FY)
    assert zero.reason == "zero_denominator" and zero.verdict == "NOT_PRESENTED"
    q = build_cell_record(REG["roe"], _cells(), PeriodBasis("Q1", None, None, "any_period"))
    assert q.reason == "period_not_applicable:fy_only" and q.verdict == "NOT_PRESENTED"
    assert null_verdict("input_not_served:revenue:NOT_PRESENTED") == "NOT_PRESENTED"
    # anything else that is null is UNCHECKED
    for r in ("input_not_served:revenue:UNCHECKED", "input_not_served:revenue:DISAGREE",
              "input_not_served:revenue:HELD", "input_not_served:revenue:MISSING", "missing:revenue", None):
        assert null_verdict(r) == "UNCHECKED", r
    blocked = build_cell_record(REG["roe"], _cells(net_income="HELD"), FY)
    row = to_cell_proof_row(blocked, 1, REG["roe"])
    cls, _ = classify(row["verdict"], row["reason_text"], None, None, None, None, None, None)
    assert cls == "UNCHECKED"  # never counted as REASON
    ok = build_cell_record(REG["roe"], _cells(stockholders_equity="NOT_PRESENTED"), FY)
    assert classify(to_cell_proof_row(ok, 1, REG["roe"])["verdict"], "x", None, None, None, None, None, None)[0] == "REASON"


@pytest.mark.unit
def test_recompute_is_self_when_nothing_is_stored_and_real_check_once_stored():
    rec = build_cell_record(REG["roe"], _cells(), FY)
    assert rec.recompute["status"] == "self" and rec.recompute["stored"] is None
    assert rec.recompute["recomputed"] == "0.25"
    assert build_cell_record(REG["roe"], _cells(), FY, stored_value=D("0.25")).recompute["status"] == "match"
    assert build_cell_record(REG["roe"], _cells(), FY, stored_value=D("0.26")).recompute["status"] == "mismatch"
    blocked = build_cell_record(REG["roe"], _cells(net_income="HELD"), FY, stored_value=D("0.25"))
    assert blocked.recompute["status"] == "n/a"


@pytest.mark.unit
def test_all_proven_inputs_compute_and_record_lineage_and_recompute():
    rec = build_cell_record(REG["roe"], _cells(), FY, stored_value=D("0.25"))
    assert rec.value == D("0.25") and rec.recompute["status"] == "match" and rec.verdict == "PROVEN"
    row = to_cell_proof_row(rec, 7, REG["roe"])
    assert row["verdict"] == "PROVEN" and row["position_is_expected_line"] is True
    assert row["checks"]["metric_inputs"][0]["rule_id"] == "tagmap.x@1"
    assert row["checks"]["metric_inputs"][0]["rules_commit"] == "abc123"
    assert row["checks"]["formula"]["ref"] == "roe@1"
    assert row["checks"]["period_basis"] == {"label": "FY", "rule": "any_period"}
    assert row["detector_version"].startswith("roe@1#")
    mismatch = build_cell_record(REG["roe"], _cells(), FY, stored_value=D("0.3"))
    assert mismatch.recompute["status"] == "mismatch" and mismatch.verdict == "DISAGREE"
    assert to_cell_proof_row(mismatch, 7, REG["roe"])["reason_code"] == "metric_recompute_mismatch"


@pytest.mark.unit
def test_not_presented_input_is_zero_only_where_the_registry_allows_it():
    qr = REG["quick_ratio"]
    cells = {
        "current_assets": InputCell("current_assets", "PROVEN", D(50000000)),
        "inventory": InputCell("inventory", "NOT_PRESENTED", None, "line not presented"),
        "current_liabilities": InputCell("current_liabilities", "PROVEN", D(25000000)),
    }
    rec = build_cell_record(qr, cells, FY)
    assert rec.value == D(2) and rec.verdict == "PROVEN"
    cells["current_assets"] = InputCell("current_assets", "NOT_PRESENTED", None)
    assert build_cell_record(qr, cells, FY).reason == "input_not_served:current_assets:NOT_PRESENTED"
    values, _ = gate_inputs(REG["gross_margin"], {"cost_of_revenue": InputCell("cost_of_revenue", "NOT_PRESENTED")})
    assert values["cost_of_revenue"] is None  # no zero-absent permission for gross_margin


@pytest.mark.unit
def test_version_bump_or_formula_edit_marks_proofs_stale_but_label_edit_does_not():
    from dataclasses import replace
    m = REG["roe"]
    dv = detector_version(m)
    assert not proof_is_stale(dv, m)
    assert proof_is_stale(dv, replace(m, version=2))
    assert proof_is_stale(dv, replace(m, expression="net_income / total_assets"))
    assert proof_is_stale(dv, replace(m, perimeter_spec={"x": "y"}))
    assert not proof_is_stale(dv, replace(m, label="Return on equity, renamed"))
    assert proof_is_stale(None, m) and proof_is_stale("garbage", m)
    assert formula_fingerprint(m) != formula_fingerprint(REG["roa"])
    stamp = value_stamp(m)
    assert stamp["formula_version"] == 1 and len(stamp["registry_version"]) == 16


# ---- applicability: families, OUT with a reason ----------------------------------------------------

@pytest.mark.unit
def test_corporate_metrics_are_out_for_banks_and_insurers_with_a_reason():
    a = applicability(REG["gross_margin"], "bank")
    assert a.status == "OUT" and a.reason and a.source == "family"
    assert applicability(REG["gross_margin"], "insurer").status == "OUT"
    assert applicability(REG["net_margin"], "insurer").reason == NOT_APPLICABLE_INSURER == "not_applicable_insurer"
    assert applicability(REG["pretax_margin"], "insurer").status == "OUT"
    for keep in ("roe", "roa", "book_value_per_share", "price_to_book", "trailing_pe"):
        assert applicability(REG[keep], "insurer").status == "IN"
    assert applicability(REG["gross_margin"], "general").status == "IN"
    assert applicability(REG["roe"], "bank").status == "IN"  # ROE, ROA, EPS, BVPS stay for banks (2026-10-19 decision)
    assert applicability(REG["net_interest_income"], "bank").status == "IN"
    assert applicability(REG["net_interest_income"], "general").status == "OUT"
    assert applicability(REG["efficiency_ratio"], "insurer").status == "OUT"
    assert applicability(REG["combined_ratio"], "insurer").status == "IN"
    assert applicability(REG["combined_ratio"], "bank").status == "OUT"
    t = applicability(REG["debtor_days"], "utility")  # no template-OUT input for a utility
    assert t.status == "IN"
    r = applicability(REG["rnd_intensity"], "utility")
    assert r.status == "OUT" and r.source == "template"


# ---- golden: five companies, filing-printed inputs, hand-computed values ----------------------------------

GOLDEN = json.loads((Path(__file__).resolve().parents[1] / "fixtures/metrics/golden_metrics.json").read_text())
ALIAS = {"total_debt_resolved": "total_debt", "operating_income_resolved": "operating_income",
         "depreciation_and_amortization_resolved": "depreciation_and_amortization"}
CASES = [(t, m) for t, c in GOLDEN["companies"].items() for m in c["expected_6dp"]]


@pytest.mark.unit
@pytest.mark.parametrize("ticker,metric", CASES)
def test_golden_values_from_filing_printed_inputs(ticker, metric):
    c = GOLDEN["companies"][ticker]
    values = {}
    inputs = alias_inputs(c["group"].split()[0], c["inputs"])  # MLP family renames, by family not company
    for concept in {n for n, _ in REG[metric].input_roles()}:
        src = inputs.get(ALIAS.get(concept, concept))
        if src is not None:
            values[concept] = D(src["value"])
    res = evaluate(REG[metric], DictEnv(values=values), check_period="FY")
    assert res.reason is None, (ticker, metric, res.reason)
    assert res.value.quantize(D("0.000001"), ROUND_HALF_EVEN) == D(c["expected_6dp"][metric])


@pytest.mark.unit
def test_golden_covers_diverse_companies_and_the_out_of_template_rows_are_reasoned():
    assert {c["group"].split()[0] for c in GOLDEN["companies"].values()} == {
        "general", "bank", "equity_reit", "insurer", "mlp"}
    assert set(GOLDEN["companies"]) == {"CB", "JPM", "MSFT", "PLD", "XOM", "EPD", "GD", "INTU"}
    assert sum(len(c["expected_6dp"]) for c in GOLDEN["companies"].values()) >= 100
    for ticker, group in (("JPM", "bank"), ("CB", "insurer"), ("PLD", "equity_reit")):
        out = [m for m in REG.values() if m.tier != "planned" and applicability(m, group).status == "OUT"]
        assert out and all(applicability(m, group).reason for m in out)
        assert not set(GOLDEN["companies"][ticker]["expected_6dp"]) & {
            "gross_margin", "current_ratio", "quick_ratio", "working_capital"}


@pytest.mark.unit
def test_every_golden_input_has_an_accession_and_an_r_page():
    import re
    for t, c in GOLDEN["companies"].items():
        for k, v in c["inputs"].items():
            assert re.fullmatch(r"\d{10}-\d{2}-\d{6}", v["accession"]), (t, k)
            assert re.fullmatch(r"R\d+\.htm(\+R\d+\.htm)*", v["r_page"]), (t, k)


@pytest.mark.unit
def test_golden_inputs_follow_docmap_status_and_insurer_carries_only_in_metrics():
    import csv
    root = Path(__file__).resolve().parents[3]
    for t, c in GOLDEN["companies"].items():
        if c["docmap"]:
            status = {}
            for r in csv.DictReader((root / c["docmap"]).open()):
                status.setdefault(r["data_point"], r["status"])
            assert not {k for k in c["inputs"] if status.get(k) == "combined"}, t  # combined line: not a golden input
    assert "accounts_payable" not in GOLDEN["companies"]["CB"]["inputs"]
    for m in GOLDEN["companies"]["CB"]["expected_6dp"]:
        assert applicability(REG[m], "insurer").status == "IN", m


@pytest.mark.unit
def test_mlp_inputs_map_by_family_not_company():
    epd = GOLDEN["companies"]["EPD"]
    assert set(alias_inputs("mlp", epd["inputs"])) >= {"stockholders_equity", "shares_outstanding", "dividends_paid"}
    assert "stockholders_equity" not in alias_inputs("general", epd["inputs"])  # not applied outside the family
    assert alias_inputs("general", {"x": 1}) == {"x": 1}
    assert {"book_value_per_share", "roe", "cash_returned_to_shareholders"} <= set(epd["expected_6dp"])
    assert applicability(REG["book_value_per_share"], "mlp").status == "IN"


@pytest.mark.unit
def test_golden_special_cases_gd_finance_lease_debt_and_intu_member_rows():
    gd = GOLDEN["companies"]["GD"]["inputs"]
    assert D(gd["total_debt"]["value"]) == D(1006 + 7007 + 39 + 353) * 10**6
    intu = GOLDEN["companies"]["INTU"]["inputs"]
    assert D(intu["cost_of_revenue"]["value"]) == D(4016 + 63) * 10**6


# ---- "which company uses which calculation": generated views -------------------------------------------

class _FakeCur:
    def __init__(self, rows):
        self.rows = rows

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def execute(self, sql, params):
        self.sql, self.params = sql, params

    def fetchall(self):
        return self.rows


class _FakeConn:
    def __init__(self, rows):
        self.rows = rows

    def cursor(self):
        return _FakeCur(self.rows)


@pytest.mark.unit
def test_company_metric_status_flags_a_value_the_registry_says_is_out():
    from scrooner_pipeline.metrics.uses import company_metric_status
    rows = [("gross_margin", 1, "COMPUTED", None, "bank", "FY", date(2025, 12, 31), D("0.4")),
            ("roe", 1, "COMPUTED", None, "bank", "FY", date(2025, 12, 31), D("0.1"))]
    out = {r["metric"]: r for r in company_metric_status(_FakeConn(rows), 1, group="bank")}
    assert out["gross_margin"]["status"] == "conflict" and out["gross_margin"]["applicability"] == "OUT"
    assert out["roe"]["status"] == "COMPUTED" and out["roe"]["registry_ref"] == "roe@1"


@pytest.mark.unit
def test_pending_migration_defines_the_views_and_columns_the_code_reads():
    sql = (Path(__file__).resolve().parents[2] / "db/pending/0126_metric_lineage_view.sql").read_text()
    for name in ("v_company_metric_status", "v_company_metric_inputs", "formula_fingerprint", "registry_version"):
        assert name in sql
    assert sql.rstrip().endswith(";")
