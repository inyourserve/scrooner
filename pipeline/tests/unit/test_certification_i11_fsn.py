"""I11 in the FSN era (certification lead, 2026-11-09): a data point out of the company's
current sector template (0120) is not a cell, and a missing cell with a writer reason in
analytics.cell_blank_reason (0100) is classified by it. The loader part runs on REAL SQL
when SCROONER_TEST_DATABASE_URL is set."""

from __future__ import annotations

import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))

from certification_fixtures import CompanyData  # noqa: E402
from certification_fixtures import add as _add  # noqa: E402
from scrooner_pipeline.certification import history  # noqa: E402
from scrooner_pipeline.certification.loader import (  # noqa: E402
    load_template_and_reasons,
    template_out,
)
from scrooner_pipeline.certification.model import (  # noqa: E402
    BlankReasonRow,
    GapRow,
    MetricCell,
)
from scrooner_pipeline.certification.runner import company_state  # noqa: E402

Q4_ENDS = (date(2015, 12, 31), date(2016, 12, 31))


def company():
    """Window 2015-2016, two 10-Ks and one 10-Q; revenue's two Q4 cells are missing."""
    d = CompanyData(company_id=2, ticker="HST", as_of=date(2017, 3, 1))
    d.latest_filed = date(2016, 12, 31)
    d.window_start = date(2015, 1, 1)
    d.first_filing_period = date(2014, 3, 31)
    d.consumed = {"revenue_sanity_resolved": "income_statement", "total_assets_resolved": "balance_sheet"}
    d.filings = [(date(2015, 12, 31), "10-K"), (date(2016, 3, 31), "10-Q"), (date(2016, 12, 31), "10-K")]
    for fy in (2015, 2016):
        _add(d, "revenue_sanity_resolved", 1000, date(fy, 12, 31), date(fy, 1, 1), "FY", tag="Revenues")
        _add(d, "total_assets_resolved", 5000, date(fy, 12, 31), None, "FY", tag="Assets")
    _add(d, "revenue_sanity_resolved", 240, date(2016, 3, 31), date(2016, 1, 1), "Q1", tag="Revenues", form="10-Q")
    _add(d, "total_assets_resolved", 5000, date(2016, 3, 31), None, "Q1", tag="Assets", form="10-Q")
    return d


def rules(findings):
    return sorted(f.evidence["rule"] for f in findings)


@pytest.mark.unit
class TestTemplateAndWriterReasons:
    def test_baseline_missing_q4_is_unclassified_and_blocks(self):
        f = history.check(company())
        assert rules(f) == ["missing_cell:unclassified"]
        assert company_state(f) == "uncertified"

    def test_out_of_template_concept_is_not_a_cell(self):
        d = company()
        d.template_out = frozenset({"revenue"})
        assert history.check(d) == []
        m = history.history_matrix(d)
        assert m["concepts"][(2015, "FY", "expected")] == 0  # revenue no longer expected

    def test_writer_reason_classifies_the_missing_cell(self):
        d = company()
        for e in Q4_ENDS:
            d.blank_reasons[("revenue", "Q4", e)] = BlankReasonRow("no_basis_witness", "defect", "period")
        f = history.check(d)
        assert rules(f) == ["missing_cell:blank_reason:no_basis_witness"]
        assert f[0].evidence["classified"] is True and f[0].evidence["count"] == 2
        assert company_state(f) == "checks_clean"  # a classified gap is review, not blocking

    def test_unclassified_defect_reason_still_blocks(self):
        d = company()
        for e in Q4_ENDS:
            d.blank_reasons[("revenue", "Q4", e)] = BlankReasonRow("x", "defect", "unclassified")
        f = history.check(d)
        assert rules(f) == ["missing_cell:unclassified"] and company_state(f) == "uncertified"
        d.blank_reasons = {("revenue", "Q4", e): BlankReasonRow("x", "defect", None) for e in Q4_ENDS}
        assert company_state(history.check(d)) == "uncertified"

    def test_writer_reason_wins_over_period_gap_and_matches_within_tolerance(self):
        d = company()
        d.period_gaps = [GapRow("revenue_sanity_resolved", "Q4", e, "q4_not_derived") for e in Q4_ENDS]
        for e in Q4_ENDS:  # FSN period end three days off the filing's period of report
            d.blank_reasons[("revenue", "Q4", date(e.year, 12, 28))] = BlankReasonRow(
                "line_presented_combined_with_others", "not_presented", None
            )
        assert rules(history.check(d)) == ["missing_cell:blank_reason:line_presented_combined_with_others"]

    def test_metric_out_of_template_and_metric_writer_reason(self):
        d = company()
        d.blank_reasons = {("revenue", "Q4", e): BlankReasonRow("r", "not_presented", None) for e in Q4_ENDS}
        d.metric_history = [MetricCell("net_margin", "FY", date(2015, 12, 31), Decimal("0.1"), None)]
        d.blank_reasons[("net_margin", "FY", date(2016, 12, 31))] = BlankReasonRow(
            "bank_revenue_definition_pending", "defect", "definition_pending"
        )
        f = [x for x in history.check(d) if x.data_point_name == "net_margin"]
        assert rules(f) == ["missing_metric:blank_reason:bank_revenue_definition_pending"]
        assert f[0].evidence["classified"] is True
        d.template_out = frozenset({"net_margin"})
        assert [x for x in history.check(d) if x.data_point_name == "net_margin"] == []

    def test_metric_writer_defect_unclassified_blocks(self):
        d = company()
        d.blank_reasons = {("revenue", "Q4", e): BlankReasonRow("r", "not_presented", None) for e in Q4_ENDS}
        d.metric_history = [MetricCell("net_margin", "FY", date(2015, 12, 31), Decimal("0.1"), None)]
        d.blank_reasons[("net_margin", "FY", date(2016, 12, 31))] = BlankReasonRow("x", "defect", "unclassified")
        f = [x for x in history.check(d) if x.data_point_name == "net_margin"]
        assert f[0].evidence["classified"] is False

    def test_template_out_needs_every_variant_out(self):
        assert template_out([("cost_of_revenue", False), ("cost_of_revenue_resolved", False)]) == {"cost_of_revenue"}
        assert template_out([("revenue", True), ("revenue_sanity_resolved", False)]) == frozenset()
        assert template_out([("ebitda", False), ("inventory", True)]) == {"ebitda"}


# --------------------------------------------------------------------------- real SQL


@pytest.mark.integration
def test_loader_reads_current_template_and_newest_writer_reason(isolated_database_url):
    psycopg = pytest.importorskip("psycopg")
    with psycopg.connect(isolated_database_url) as conn, conn.cursor() as cur:
        cur.execute("select to_regclass('analytics.company_data_point_template') is not null")
        if not cur.fetchone()[0]:
            pytest.skip("needs the migrated schema with migration 0120")
        cur.execute("insert into core.company (cik, company_name) values ('0000000777', 'T') returning id")
        cid = cur.fetchone()[0]
        tmpl = ("insert into analytics.company_data_point_template (company_id, data_point, in_template, reason,"
                " effective_from, template, source, template_version) values (%s, %s, %s, %s, %s, 'bank', 'sector_default', 'tv')")  # fmt: skip
        # v1 (2026-11-01): ebitda out. v2 (2026-12-01): ebitda back in, inventory out.
        cur.execute(tmpl, (cid, "ebitda", False, "C", date(2026, 11, 1)))
        cur.execute(tmpl, (cid, "inventory", True, None, date(2026, 11, 1)))
        cur.execute(tmpl, (cid, "ebitda", True, None, date(2026, 12, 1)))
        cur.execute(tmpl, (cid, "inventory", False, "A", date(2026, 12, 1)))
        runs = []
        for _ in range(2):
            cur.execute("insert into analytics.rule_run (rule_id, rule_version, mode, flag_name, flag_state)"
                        " values ('fsn.cells@1', 1, 'apply', 'f', 'on') returning run_id")  # fmt: skip
            runs.append(cur.fetchone()[0])
        reason = ("insert into analytics.cell_blank_reason (run_id, company_id, data_point_name, period_grain,"
                  " period_start, period_end, state, defect_class, owner, rule_id, reason_code, created_at)"
                  " values (%s, %s, %s, %s, %s, %s, %s, %s,"
                  " case when %s = 'defect' then 'data_engineer_l1' end, 'fsn.cells@1', %s, %s)")  # fmt: skip
        q_start, q_end = date(2025, 1, 1), date(2025, 3, 31)

        def put(run, dp, grain, start, end, state, dclass, code, at):
            cur.execute(reason, (run, cid, dp, grain, start, end, state, dclass, state, code, at))

        put(runs[0], "revenue_sanity_resolved", "Q", q_start, q_end, "defect", "unclassified", "old", "2026-11-01")
        put(runs[1], "revenue_sanity_resolved", "Q", q_start, q_end, "not_presented", None, "new", "2026-11-09")
        put(runs[1], "total_assets", "I", q_end, q_end, "defect", "period", "inst", "2026-11-09")
        put(runs[1], "ebitda", "TTM", q_start, q_end, "defect", "period", "ttm_ignored", "2026-11-09")

        def load(as_of):
            d = CompanyData(company_id=cid, ticker="T", as_of=as_of)
            d.window_start = date(2015, 1, 1)
            data = {cid: d}
            load_template_and_reasons(cur, data, [cid], as_of, 15)
            return d

        before_v2, after_v2 = load(date(2026, 11, 15)), load(date(2026, 12, 15))
        assert before_v2.template_out == {"ebitda"}
        assert after_v2.template_out == {"inventory"}  # the whole current version decides
        assert load(date(2026, 10, 1)).template_out == frozenset()  # before any version
        br = after_v2.blank_reasons
        assert br[("revenue", "Q", q_end)].reason_code == "new"  # newest row wins
        assert br[("revenue", "Q4", q_end)].classified is True
        assert br[("total_assets", "I", q_end)].reason_code == "inst"
        assert not any(k[0] == "ebitda" for k in br)  # TTM grain is not an I11 cell
