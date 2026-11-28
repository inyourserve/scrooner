"""Golden values for the expr_wired metrics: one hand-computed value per metric from filing-printed inputs.

Fixture tests/fixtures/metrics/golden_expr_metrics.json (inputs carry accession and R page; price is the one stated
assumption). The helper evaluates a metric the way the calculator will: a metric used as an input (fcf, ebitda,
market_cap, trailing_pe, debtor_days ...) is evaluated by the engine from its own registry formula first.
"""

from __future__ import annotations

import json
import re
from dataclasses import replace
from decimal import ROUND_HALF_EVEN, Decimal
from pathlib import Path

import pytest

from scrooner_pipeline.metrics import expr
from scrooner_pipeline.metrics.engine import DictEnv, evaluate
from scrooner_pipeline.metrics.provenance import formula_fingerprint
from scrooner_pipeline.metrics.registry import get_registry

REG = get_registry()
D = Decimal
GOLDEN = json.loads(
    (Path(__file__).resolve().parents[1] / "fixtures/metrics/golden_expr_metrics.json").read_text()
)
CASES = GOLDEN["cases"]
EXPR_WIRED = sorted(m.metric_id for m in REG.values() if m.expression_status == "expr_wired")


def _vals(inputs):
    return {k: D(v["value"]) for k, v in inputs.items()}


def _metric_or_input(name, base, ctx):
    """Value of `name`: an input as given, else the registry metric evaluated on `base`."""
    if name in base:
        return base[name]
    assert name in REG, f"{ctx}: no input and no metric for {name}"
    res = evaluate(REG[name], DictEnv(values=dict(base)))
    assert res.reason is None, (ctx, name, res.reason)
    return res.value


def _env(case):
    base = _vals(case["inputs"])
    if "price" in case:
        base["price"] = D(case["price"]["value"])
    m = REG[case["metric"]]
    values, ttm, lags = dict(base), {}, {}
    ctx = f"{case['company']} {case['metric']}"
    for node in _walk(m.ast):
        if isinstance(node, expr.Name) and node.name not in values and node.name in REG:
            values[node.name] = _metric_or_input(node.name, base, ctx)
        if isinstance(node, expr.Call) and node.func == "ttm":
            ttm[node.args[0].name] = _metric_or_input(node.args[0].name, base, ctx)
    for key, lag in case.get("lags", {}).items():
        name, n = key.split("|")
        lags[(name, int(n))] = _metric_or_input(name, _vals(lag["inputs"]), ctx)
        if name not in values:
            values[name] = _metric_or_input(name, base, ctx)
    # a metric that other metrics feed (trailing_pe, eps_growth_yoy) is evaluated before this one
    for name in {n for n in expr.names(m.ast) if n in REG and n not in values}:
        values[name] = _metric_or_input(name, values, ctx)
    return DictEnv(values=values, ttm=ttm, lags=lags)


def _walk(node):
    yield node
    for child in (getattr(node, "left", None), getattr(node, "right", None), getattr(node, "arg", None)):
        if child is not None:
            yield from _walk(child)
    for a in getattr(node, "args", ()):
        yield from _walk(a)


def _chained_env(case):
    """peg_ratio reads trailing_pe and eps_growth_yoy, each with its own windows; build them explicitly."""
    base = _vals(case["inputs"])
    base["price"] = D(case["price"]["value"])
    pe = evaluate(REG["trailing_pe"], DictEnv(ttm={"diluted_eps": base["diluted_eps"]}, values=base))
    prior = _vals(case["lags"]["diluted_eps|1"]["inputs"])["diluted_eps"]
    g = evaluate(REG["eps_growth_yoy"], DictEnv(values=base, lags={("diluted_eps", 1): prior}))
    assert pe.reason is None and g.reason is None
    return DictEnv(values={"trailing_pe": pe.value, "eps_growth_yoy": g.value})


@pytest.mark.unit
@pytest.mark.parametrize("case", CASES, ids=lambda c: f"{c['company']}-{c['metric']}")
def test_expr_wired_golden_value_from_filing_inputs(case):
    m = REG[case["metric"]]
    assert m.expression_status == "expr_wired"
    env = _chained_env(case) if case["metric"] == "peg_ratio" else _env(case)
    res = evaluate(m, env, check_period="FY")
    assert res.reason is None, (case["metric"], res.reason)
    assert res.value.quantize(D("0.000001"), ROUND_HALF_EVEN) == D(case["expected_6dp"])


@pytest.mark.unit
def test_every_expr_wired_metric_has_one_golden_case_and_no_other_does():
    cased = sorted(c["metric"] for c in CASES)
    assert cased == EXPR_WIRED, set(cased) ^ set(EXPR_WIRED)
    assert len(EXPR_WIRED) == 21


@pytest.mark.unit
def test_no_metric_is_left_described_and_only_the_two_bank_insurer_metrics_are_planned():
    left = {m.metric_id: m.expression_status for m in REG.values() if m.expression_status in ("described", "planned")}
    assert left == {"efficiency_ratio": "planned", "combined_ratio": "planned"}


@pytest.mark.unit
def test_golden_inputs_cite_accession_and_r_page_and_price_is_the_only_assumption():
    for c in CASES:
        for k, v in c["inputs"].items():
            assert re.fullmatch(r"\d{10}-\d{2}-\d{6}", v["accession"]), (c["metric"], k)
            assert re.fullmatch(r"R\d+\.htm", v["r_page"]), (c["metric"], k)
        for lag in c.get("lags", {}).values():
            for k, v in lag["inputs"].items():
                assert re.fullmatch(r"\d{10}-\d{2}-\d{6}", v["accession"]), (c["metric"], k)
        if REG[c["metric"]].requires_price:
            assert c["price"]["evidence"].startswith("ASSUMED"), c["metric"]


@pytest.mark.unit
def test_expr_wired_shares_the_described_fingerprint_so_proofs_stay_current():
    m = REG["ev_sales"]
    assert formula_fingerprint(m) == formula_fingerprint(replace(m, expression_status="described"))
    assert formula_fingerprint(m) != formula_fingerprint(replace(m, expression="market_cap / revenue"))


@pytest.mark.unit
@pytest.mark.parametrize("metric", EXPR_WIRED)
def test_a_missing_input_is_a_reasoned_null_never_a_value(metric):
    case = next(c for c in CASES if c["metric"] == metric)
    env = _chained_env(case) if metric == "peg_ratio" else _env(case)
    ttm_used = {n.args[0].name for n in _walk(REG[metric].ast) if isinstance(n, expr.Call) and n.func == "ttm"}
    in_call = {a.name for n in _walk(REG[metric].ast) if isinstance(n, expr.Call) and n.func != "growth" for a in n.args if isinstance(a, expr.Name)}
    point_used = set(expr.names(REG[metric].ast)) - in_call
    growth_used = {n.args[0].name for n in _walk(REG[metric].ast) if isinstance(n, expr.Call) and n.func == "growth"}
    tried = 0
    for store, used in ((env.values, point_used | growth_used), (env.ttm, ttm_used), (env.lags, growth_used)):
        for name in list(store):
            if (name[0] if isinstance(name, tuple) else name) not in used:
                continue
            saved = store.pop(name)
            res = evaluate(REG[metric], env, check_period="FY")
            store[name] = saved
            tried += 1
            assert res.value is None and res.reason, (metric, name)
    assert tried >= 1
