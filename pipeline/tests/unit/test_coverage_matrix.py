from scrooner_pipeline.mapper.coverage_matrix import (
    BDC_FAMILY_DATA_POINTS,
    BUYBACK_FAMILY_DATA_POINTS,
    CAPITAL_RETURN_FAMILY_DATA_POINTS,
    DIVIDEND_CONCEPT_DATA_POINTS,
    DIVIDEND_FAMILY_DATA_POINTS,
    POPULATION_QUERIES,
    RECONCILIATION_GAP_POPULATION_OVERRIDES,
    REVENUE_FAMILY_CONCEPTS,
    SIC_GAP_REASONS,
)


def test_revenue_family_concepts_includes_resolved_and_raw_pairs() -> None:
    # Every raw revenue-statement concept should have its resolved
    # companion covered too -- classify_concept_gaps() is applied to
    # both, and a company missing the raw tag is missing the resolved
    # one for the same structural reason. `revenue` is the one
    # exception to the `<name>_resolved` naming convention -- its
    # resolved concept is `revenue_sanity_resolved` (built by
    # sanity/tag_investigator.py, named for what it fixes, not a
    # simple suffix rule).
    resolved_names = {
        "revenue": "revenue_sanity_resolved",
        "cost_of_revenue": "cost_of_revenue_resolved",
        "gross_profit": "gross_profit_resolved",
        "operating_income": "operating_income_resolved",
        "operating_expenses": "operating_expenses_resolved",
    }
    for raw, resolved in resolved_names.items():
        assert raw in REVENUE_FAMILY_CONCEPTS
        assert resolved in REVENUE_FAMILY_CONCEPTS


def test_sic_gap_reasons_cover_every_verified_bucket() -> None:
    # Found live 2026-09-11 investigating the real revenue coverage gap --
    # each of these was spot-checked against real companies, not assumed
    # from the SIC label alone (see coverage_matrix.py's own comment).
    expected_sics = {
        "Blank Checks",
        "Pharmaceutical Preparations",
        "Biological Products, (No Diagnostic Substances)",
        "Commodity Contracts Brokers & Dealers",
        "Asset-Backed Securities",
        "Real Estate Investment Trusts",
        "State Commercial Banks",
        "National Commercial Banks",
        "Savings Institution, Federally Chartered",
        "Metal Mining",
        "Gold and Silver Ores",
    }
    assert set(SIC_GAP_REASONS.keys()) == expected_sics
    # Every reason is a non-empty, snake_case-ish string -- not blank,
    # not accidentally duplicated across unrelated SICs in a way that
    # would hide a real distinction (banks and REITs deliberately get
    # different reasons even though both are "not GAAP revenue").
    assert len(set(SIC_GAP_REASONS.values())) >= 5
    for reason in SIC_GAP_REASONS.values():
        assert reason and reason == reason.lower()


def test_population_queries_cover_every_named_population_a_data_point_can_reference() -> None:
    # capital_return_company is deliberately NOT in POPULATION_QUERIES --
    # classify_company_populations() builds it as a union of
    # dividend_payer/buyback_company instead of its own query (see that
    # function's own comment) -- so every OTHER family's target
    # population must have a real query to build it from.
    referenced_populations = {
        "real_operating_company", "dividend_payer", "dividend_family_ever_reported",
        "buyback_company", "bdc_company",
    }
    assert referenced_populations <= set(POPULATION_QUERIES.keys())


def test_family_data_point_lists_are_disjoint() -> None:
    # Each data point gets exactly one applicable_population override in
    # build_registry() -- a name appearing in two families would mean
    # whichever dict-population wins last silently shadows the other,
    # not a deliberate choice.
    all_families = [
        DIVIDEND_FAMILY_DATA_POINTS,
        DIVIDEND_CONCEPT_DATA_POINTS,
        BUYBACK_FAMILY_DATA_POINTS,
        CAPITAL_RETURN_FAMILY_DATA_POINTS,
        BDC_FAMILY_DATA_POINTS,
        tuple(RECONCILIATION_GAP_POPULATION_OVERRIDES.keys()),
    ]
    seen: set[str] = set()
    for family in all_families:
        overlap = seen & set(family)
        assert not overlap, f"data point(s) {overlap} appear in more than one population family"
        seen |= set(family)


class _FakeCursor:
    def __init__(self, conn: "_FakeConn") -> None:
        self._conn = conn
        self.rowcount = 0

    def __enter__(self) -> "_FakeCursor":
        return self

    def __exit__(self, *exc: object) -> None:
        return None

    def execute(self, sql: str, params: object = None) -> None:
        self._conn.statements.append(" ".join(sql.split()))
        if self._conn.fail_on and self._conn.fail_on in sql:
            raise RuntimeError("QueryCanceled: canceling statement due to statement timeout")

    def fetchone(self) -> tuple[int, int]:
        return (10, 7)


class _FakeConn:
    def __init__(self, fail_on: str | None = None) -> None:
        self.fail_on = fail_on
        self.statements: list[str] = []
        self.commits: list[int] = []

    def cursor(self) -> _FakeCursor:
        return _FakeCursor(self)

    def commit(self) -> None:
        # Record how many statements had run when each commit happened.
        self.commits.append(len(self.statements))


def _patch_classifiers(monkeypatch, seen: list[bool]) -> None:
    import scrooner_pipeline.mapper.coverage_matrix as cm

    def fake(conn, *, commit: bool = True):
        seen.append(commit)
        return {"rows": 0}

    monkeypatch.setattr(cm, "classify_concept_gaps", fake)
    monkeypatch.setattr(cm, "apply_filing_line_evidence", fake)
    monkeypatch.setattr(cm, "classify_company_populations", fake)


def test_build_coverage_is_one_transaction_committed_once_at_the_end(monkeypatch) -> None:
    # 2026-10-16 nightly: the metric insert hit the statement timeout after
    # the delete and the concept insert had already been committed, leaving the
    # table with no metric rows and no gap_reason. The rebuild must be atomic.
    from scrooner_pipeline.mapper.coverage_matrix import build_coverage

    seen: list[bool] = []
    _patch_classifiers(monkeypatch, seen)
    conn = _FakeConn()
    build_coverage(conn)  # type: ignore[arg-type]

    assert seen == [False, False, False], "classifiers must not commit on their own"
    assert len(conn.commits) == 1, f"expected exactly one commit, got {conn.commits}"
    assert conn.commits[0] == len(conn.statements), "the commit must come after every statement"


def test_build_coverage_never_commits_when_a_middle_step_fails(monkeypatch) -> None:
    import pytest

    from scrooner_pipeline.mapper.coverage_matrix import build_coverage

    _patch_classifiers(monkeypatch, [])
    conn = _FakeConn(fail_on="analytics.metric_definition md")
    with pytest.raises(RuntimeError):
        build_coverage(conn)  # type: ignore[arg-type]

    assert conn.commits == [], "a failed rebuild must leave the previous table untouched"


def _run_build_statements(monkeypatch) -> list[str]:
    from scrooner_pipeline.mapper.coverage_matrix import build_coverage

    _patch_classifiers(monkeypatch, [])
    conn = _FakeConn()
    build_coverage(conn)  # type: ignore[arg-type]
    return conn.statements


def test_big_inserts_are_set_based_not_correlated(monkeypatch) -> None:
    # 2026-10-17: the correlated `exists (... canonical_fact ... cf.company_id =
    # c.id ...)` per (company x concept) cell exceeded the 30-minute timeout.
    stmts = _run_build_statements(monkeypatch)
    concept = next(s for s in stmts if "cross join analytics.canonical_concept" in s)
    metric = next(s for s in stmts if "cross join analytics.metric_definition md" in s)

    assert "exists" not in concept, "concept insert must not use a per-cell exists probe"
    assert "left join (" in concept
    assert "group by company_id, canonical_concept_id" in concept

    assert "exists" not in metric
    assert "limit 1" not in metric, "no per-cell correlated 'latest row' subquery"
    assert "mv2" not in metric
    assert "left join (" in metric
    assert "group by company_id, metric_definition_id" in metric
    # latest-period fill (B0(a)): first element of the same ordering as gap_reason
    assert (
        "array_agg(value is not null order by period_end desc, period_start desc, period_label))[1] as has_value"
        in metric
    )
    assert "bool_or(value is not null) as has_value," not in metric  # not the old ever-filled rule
    assert "bool_or(value is not null) as has_value_any_period" in metric  # history kept
    assert "order by period_end desc" in metric  # latest-period reason, deterministic tie-break
    assert "coalesce(agg.has_value, false)" in metric  # no metric_value rows -> false, row kept


def test_no_canonical_fact_probe_correlated_on_company(monkeypatch) -> None:
    for s in _run_build_statements(monkeypatch):
        if "from analytics.canonical_fact" in s:
            assert "cf.company_id = c.id" not in s


def test_metric_insert_omits_secondary_column_until_migration_0096_applied(monkeypatch) -> None:
    # The code must be safe to deploy before the migration: when the
    # has_value_any_period column does not exist, the insert must not name it.
    from scrooner_pipeline.mapper.coverage_matrix import build_coverage

    class _NoColCursor(_FakeCursor):
        def fetchone(self):  # type: ignore[override]
            last = self._conn.statements[-1]
            if "information_schema.columns" in last:
                return (False,)
            return (10, 7)

    class _NoColConn(_FakeConn):
        def cursor(self):  # type: ignore[override]
            return _NoColCursor(self)

    _patch_classifiers(monkeypatch, [])
    conn = _NoColConn()
    build_coverage(conn)  # type: ignore[arg-type]
    metric = next(s for s in conn.statements if "cross join analytics.metric_definition md" in s)
    assert "has_value_any_period" not in metric
    assert "array_agg(value is not null order by period_end desc" in metric  # still latest-period


def test_latest_period_fill_is_not_ever_filled(monkeypatch) -> None:
    # Fixture semantics (verified against a scratch Postgres 2026-10-19): company
    # with FY2019=5 and FY2020=NULL must be NOT filled (gap_reason of FY2020 row)
    # but has_value_any_period true. The has_value expression must therefore be
    # the first element of the latest-first ordering, never bool_or.
    metric = next(s for s in _run_build_statements(monkeypatch) if "cross join analytics.metric_definition md" in s)
    has_value_expr = metric.split("as has_value")[0].rsplit("(array_agg", 1)[1]
    assert "value is not null order by period_end desc, period_start desc, period_label" in has_value_expr
    assert "bool_or" not in has_value_expr
