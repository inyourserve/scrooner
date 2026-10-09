"""Tests for mapper/revenue_resolvers/ (2026-10-02) -- the sub-mapper
registry for revenue resolution strategies, replacing the ad hoc
functions this project's tag-coverage investigations had been adding
directly to mapper/concept_fallback.py. Moved from test_concept_fallback.py
when the functions themselves moved, same test bodies/evidence."""

from unittest.mock import MagicMock

import pytest

from scrooner_pipeline.mapper.revenue_resolvers import RESOLVER_REGISTRY, registry_summary
from scrooner_pipeline.mapper.revenue_resolvers.net_lease_income import (
    _REVENUE_FINANCIAL_INCOME_TAGS,
)
from scrooner_pipeline.mapper.revenue_resolvers.net_lease_income import run as run_net_lease
from scrooner_pipeline.mapper.revenue_resolvers.shared import (
    companies_owned_by_other_revenue_writer,
)


@pytest.mark.unit
class TestRegistry:
    """The registry itself -- every entry must be a real, importable
    module exposing run(), and the ordering (tag-preference first,
    rendered-report parser last) must hold since later resolvers
    depend on earlier ones' exclusion sets being final."""

    def test_every_entry_has_a_run_function(self):
        for name, (module, _description) in RESOLVER_REGISTRY.items():
            assert callable(getattr(module, "run", None)), f"{name} has no run()"

    def test_spurious_zero_tag_preference_runs_first(self):
        assert next(iter(RESOLVER_REGISTRY)) == "spurious_zero_tag_preference"

    def test_rendered_report_parser_runs_last(self):
        assert list(RESOLVER_REGISTRY)[-1] == "rendered_report_parser"

    def test_registry_summary_lists_every_resolver(self):
        summary = registry_summary()
        assert {row["name"] for row in summary} == set(RESOLVER_REGISTRY)


@pytest.mark.unit
class TestCompaniesOwnedByOtherRevenueWriter:
    """Every resolver must never touch a company already owned, for
    every period, by sanity/tag_investigator.py's company_tag_preference
    or parsers/revenue_parser.py's concept_parser_result -- same
    single-writer-per-company discipline concept_fallback.py's
    resolve_arithmetic_fallback() already established for the
    gross_profit/cost_of_revenue family."""

    def test_queries_both_ownership_sources(self):
        conn = MagicMock()
        cur = conn.cursor.return_value.__enter__.return_value
        cur.fetchall.return_value = [(1,), (2,)]
        owned = companies_owned_by_other_revenue_writer(conn, revenue_id=99)
        assert owned == {1, 2}
        sql = cur.execute.call_args[0][0]
        assert "company_tag_preference" in sql
        assert "concept_parser_result" in sql
        assert cur.execute.call_args[0][1] == {"revenue_id": 99}


@pytest.mark.unit
class TestNetLeaseIncomeResolver:
    """Root cause 3 (2026-10-02, American Strategic Investment Co.):
    the candidate-selection query must gate on the REIT SIC bucket AND
    exclude any company that has ever reported a financial-institution
    interest-income tag (the mortgage-REIT/bank discriminator) -- checked
    live before shipping: of 75 companies where OperatingLeaseLeaseIncome
    is real/material and primary revenue is missing/zero, 23 also report
    a financial-income tag and 49 aren't REIT-SIC at all; only the
    remaining 12 are real equity/net-lease REITs."""

    def test_candidate_query_gates_on_reit_sic_and_excludes_financial_income_tags(self):
        conn = MagicMock()
        cur = conn.cursor.return_value.__enter__.return_value
        # _concept_id x3 (revenue, revenue_sanity_resolved, net_lease_revenue),
        # then companies_owned_by_other_revenue_writer, then the gating
        # query itself (returns zero candidates -- the per-company loop
        # never runs, keeping this test focused on the gating SQL shape).
        cur.fetchone.side_effect = [(1,), (2,), (3,)]
        cur.fetchall.side_effect = [[], []]  # owned=set(), candidates=[]
        stats = run_net_lease(conn)
        assert stats["considered"] == 0

        executed_sql = [call.args[0] for call in cur.execute.call_args_list]
        gating_sql = next(sql for sql in executed_sql if "sic_description" in sql)
        assert "Real Estate Investment Trusts" in gating_sql
        assert "not exists" in gating_sql
        gating_call = next(
            call for call in cur.execute.call_args_list if "sic_description" in call.args[0]
        )
        bound_params = gating_call.args[1]
        assert set(bound_params["fin_tags"]) == set(_REVENUE_FINANCIAL_INCOME_TAGS)

    def test_skips_companies_with_no_qualifying_candidates(self):
        conn = MagicMock()
        cur = conn.cursor.return_value.__enter__.return_value
        cur.fetchone.side_effect = [(1,), (2,), (3,)]
        cur.fetchall.side_effect = [[], []]
        stats = run_net_lease(conn)
        assert stats == {
            "considered": 0,
            "ok": 0,
            "errored": 0,
            "rows_written": 0,
            "skipped_other_writer": 0,
        }
