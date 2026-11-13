"""Metric calculation library: one registry as data, one safe engine, generators.

The registry (registry/*.csv, one file per family) is the only place a metric's id,
version, formula, period rule, null rules, applicability and display metadata live.
`generate` derives the legacy shapes (pipeline definitions, backend catalog,
FORMULA_SHAPES, formula descriptions) from it; `engine` evaluates it in Decimal;
`provenance` records what each metric cell was computed from.
Adding a metric is adding a row, never code.
"""
