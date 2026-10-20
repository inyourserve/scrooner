"""Runner and loader of the certification suite, with a fake cursor (no database):
chunking cap, shard file, loader row assembly, dry-run writes nothing, --apply
refuses without the migration and otherwise writes delete-then-insert in one
transaction per chunk, only into the two certification tables."""

from datetime import date, datetime, timezone
from decimal import Decimal

import pytest
from certification_fixtures import add, clean_company, src

from scrooner_pipeline.certification import loader
from scrooner_pipeline.certification.model import Finding
from scrooner_pipeline.certification.runner import (
    MAX_CHUNK,
    MigrationNotAppliedError,
    apply_chunk,
    certify,
    chunks,
    load_shard_company_ids,
    render_text,
)

D = Decimal


class FakeCursor:
    """Routes a statement to canned rows by the first matching substring."""

    def __init__(self, routes, log):
        self.routes, self.log, self.rows, self.many = routes, log, [], []

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def execute(self, sql, params=None):
        self.log.append(("execute", " ".join(sql.split()), params))
        self.rows = []
        for needle, rows in self.routes:
            if needle in sql:
                self.rows = rows
                break

    def executemany(self, sql, seq):
        self.log.append(("executemany", " ".join(sql.split()), list(seq)))

    def fetchall(self):
        return list(self.rows)

    def fetchone(self):
        return self.rows[0] if self.rows else None


class FakeConn:
    def __init__(self, routes):
        self.log, self.routes, self.commits, self.rollbacks = [], routes, 0, 0

    def cursor(self):
        return FakeCursor(self.routes, self.log)

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1

    def writes(self):
        return [e for e in self.log if e[0] == "executemany" or e[1].startswith(("delete", "insert", "update", "alter", "create"))]


def finding(cid=1, sev="wrong_value"):
    return Finding(cid, "I4", sev, "net_income", date(2023, 12, 31), D(4801), D(4_801_000_000),
                   {"rule": "neighbour_magnitude"}, [64871764])


@pytest.mark.unit
class TestChunking:
    def test_chunks_never_exceed_25(self):
        parts = chunks(list(range(60)), 1000)
        assert max(len(p) for p in parts) == MAX_CHUNK == 25
        assert [len(p) for p in parts] == [25, 25, 10]

    def test_small_chunk_size_respected(self):
        assert [len(p) for p in chunks(list(range(7)), 3)] == [3, 3, 1]


@pytest.mark.unit
class TestShardFile:
    def test_reads_ids_and_skips_excluded(self, tmp_path):
        p = tmp_path / "shards.csv"
        p.write_text(
            "shard,rank,company_id,cik,ticker,name,sic,mcap_bn,cells,filled,unexplained_blank,excluded\n"
            "S002,1,10,x,TBLA,T,1,1,1,1,1,dropped\n"
            "S002,2,11,x,MU,M,1,1,1,1,1,\n"
            "S001,3,12,x,AAPL,A,1,1,1,1,1,\n"
        )
        assert load_shard_company_ids("s002", p) == [11]
        with pytest.raises(ValueError):
            load_shard_company_ids("S999", p)

    def test_repo_shards_file_has_s001(self):
        ids = load_shard_company_ids("S001")
        assert 3 in ids and len(ids) == 9  # AAPL is in; AKTX is marked excluded in the file


@pytest.mark.unit
class TestLoader:
    def test_assembles_company_data_from_rows(self):
        end, start = date(2023, 12, 31), date(2023, 1, 1)
        routes = [
            ("from core.company where id", [(7, "0000000007", "TST", "6022")]),
            ("group by cf.company_id", [(7, date(2011, 6, 30))]),
            ("from analytics.canonical_fact cf",
             [(7, "net_income", D(4801), [11], 100, start, end, "duration", 2023, "FY")]),
            ("where f.id = any", [(11, "NetIncomeLoss", D(4801), False, False, "DEF 14A", "usd",
                                   "0001-23-1", date(2024, 1, 5), start, end)]),
            ("not f2.is_authoritative", [(11, 13, "NetIncomeLoss", D(4800), False, False, "DEF 14A", "usd",
                                          "0003-24-1", date(2024, 2, 6), start, end)]),
            ("f1.id = any", [(11, 12, "NetIncomeLoss", D(4_801_000_000), True, False, "10-K", "usd",
                              "0002-24-1", date(2024, 2, 5), start, end)]),
            ("c.tag = any(%s) and u.unit_name", [(7, 21, "LongTermDebt", D(5), 101, date(2023, 12, 31))]),
            ("distinct on (mv.company_id", [(7, "market_cap", True, "TTM", date(2026, 10, 20), D(9), [11])]),
            ("select distinct f.company_id, f.concept_id", [(7, 21, date(2023, 1, 1), date(2023, 12, 31))]),
            ("min(period_of_report)", [(7, date(2012, 3, 31))]),
            ("select distinct company_id, period_of_report, form", [(7, date(2024, 12, 31), "10-K")]),
            ("from analytics.period_gap pg", [(7, "revenue_sanity_resolved", "Q", date(2024, 6, 30), "no_mapped_tag")]),
            ("mv.period_label in ('FY', 'Q1'", [(7, "net_margin", "FY", date(2024, 12, 31), None, "missing:revenue")]),
            ("from core.filing", [(7, date(2026, 6, 30))]),
            ("company_stock_split", [(7, date(2025, 1, 1), D(2))]),
            ("market_price_alpaca", [(7, date(2026, 10, 20), D(50))]),
            ("shares_outstanding_fallback", [(7, date(2026, 8, 1))]),
            ("length(c.sic_code)", [(7,)]),
            ("company_sec_tag", [(7, "NoninterestExpense"), (7, "Deposits")]),
        ]
        cur = FakeCursor(routes, [])
        reg = loader.Registry(modes={"net_income": "first_match"}, debt_tags=["LongTermDebt"],
                              adjustment_tags=["MinorityInterest"], mapped_ids={21: {"net_income"}},
                              mapped_tag_count={"net_income": 1})
        data = loader.load_chunk(cur, [7], reg, timeout_s=5, as_of=date(2026, 10, 21))[7]
        assert data.ticker == "TST" and data.cells[0].value == D(4801) and data.cells[0].days == 364
        assert data.sources[11].form == "DEF 14A" and not data.sources[11].authoritative
        assert data.authoritative_copies[11][0].value == D(4_801_000_000)
        assert [f.tag for f in data.debt_facts] == ["LongTermDebt"]
        assert data.metrics[0].requires_price and data.metrics[0].source_ids == (11,)
        assert data.latest_filed == date(2026, 6, 30) and data.price == (date(2026, 10, 20), D(50))
        assert data.is_bank and not data.bank_sic_without_evidence and data.shares_fallback_filed == date(2026, 8, 1)
        assert data.conflict_copies[11][0].id == 13 and data.mapped_facts == {"net_income": [(date(2023, 1, 1), date(2023, 12, 31))]}
        assert data.mapped_tag_count == {"net_income": 1}
        assert data.first_data_period == date(2011, 6, 30)
        assert data.first_filing_period == date(2012, 3, 31) and data.filings == [(date(2024, 12, 31), "10-K")]
        assert data.period_gaps[0].base == "revenue" and data.period_gaps[0].cause == "no_mapped_tag"
        assert data.metric_history[0].reason == "missing:revenue" and data.metric_history[0].value is None

    def test_every_statement_sets_a_timeout_first_and_is_a_select(self):
        log = []
        cur = FakeCursor([], log)
        loader.load_chunk(cur, [1], loader.Registry(), timeout_s=7)
        sql = [e for e in log if e[0] == "execute"]
        assert any("set_config('statement_timeout'" in e[1] and e[2] == ("7000",) for e in sql)
        timeouts = sum("set_config" in e[1] for e in sql)
        selects = sum(e[1].lstrip().lower().startswith(("select", "with")) for e in sql) - timeouts
        assert timeouts >= selects - 1  # one timeout before each query (bank predicate shares one)
        assert not any(e[1].lstrip().lower().startswith(("insert", "update", "delete")) for e in sql)


@pytest.mark.unit
class TestDryRunAndApply:
    def routes(self, tables=True):
        return [
            ("to_regclass", [(tables,)]),
            ("from core.company where id", [(1, "0000000001", "CLN", "3571")]),
        ]

    def test_dry_run_issues_no_write_and_never_checks_for_tables(self):
        conn = FakeConn(self.routes())
        res = certify(conn, [1], apply=False)
        assert conn.writes() == [] and conn.commits == 0
        assert not any("to_regclass" in e[1] for e in conn.log)
        assert res.companies[1]["ticker"] == "CLN" and res.findings == []

    def test_apply_refuses_without_the_migration(self):
        conn = FakeConn(self.routes(tables=False))
        with pytest.raises(MigrationNotAppliedError, match="0097"):
            certify(conn, [1], apply=True)
        assert conn.writes() == [] and conn.commits == 0

    def test_apply_with_tables_writes_one_transaction_per_chunk(self):
        conn = FakeConn(self.routes(tables=True))
        res = certify(conn, [1, 2, 3], chunk_size=2, apply=True)
        assert conn.commits == 2  # two chunks of <= 2, one transaction each
        stmts = [e[1] for e in conn.writes()]
        assert all("analytics.certification_finding" in s or "analytics.company_certification" in s for s in stmts)
        assert res.written == 0

    def test_apply_chunk_is_delete_then_insert_then_upsert_and_commits_once(self):
        conn = FakeConn([])
        n = apply_chunk(conn, [1, 2], [finding(1)], datetime(2026, 10, 21, tzinfo=timezone.utc))
        kinds = [(e[0], e[1].split()[0]) for e in conn.log]
        assert kinds == [("execute", "delete"), ("executemany", "insert"), ("executemany", "insert")]
        assert "resolved_at is null" in conn.log[0][1] and conn.log[0][2] == ([1, 2],)
        assert conn.commits == 1 and n == 1
        certs = conn.log[2][2]
        assert certs[0][:2] == (1, "uncertified") and certs[0][3] == 1  # finding() is wrong_value
        assert certs[1][:2] == (2, "checks_clean") and certs[1][3] == 0

    def test_rerun_with_no_findings_deletes_old_open_findings(self):
        conn = FakeConn([])
        apply_chunk(conn, [5], [], datetime(2026, 10, 21, tzinfo=timezone.utc))
        assert conn.log[0][1].startswith("delete from analytics.certification_finding")
        assert conn.log[2][2] == [(5, "checks_clean", datetime(2026, 10, 21, tzinfo=timezone.utc), 0)]

    def test_upsert_state_comes_from_the_python_rule_and_never_promotes_past_checks_clean(self):
        from scrooner_pipeline.certification.runner import UPSERT_CERTIFICATION as sql
        flat = " ".join(sql.split())
        assert "when excluded.state = 'uncertified' then 'uncertified'" in flat
        assert "when analytics.company_certification.state = 'uncertified' then 'checks_clean'" in flat
        assert "else analytics.company_certification.state" in flat

    def test_state_rule_review_does_not_block_but_wrong_value_and_unclassified_i11_do(self):
        from scrooner_pipeline.certification.runner import company_state
        review = finding(1, "review")
        wrong = finding(1, "wrong_value")
        gap_ok = Finding(1, "I11", "review", "revenue", None, None, None, {"rule": "missing_cell:q4_not_derived", "classified": True}, [])
        gap_bad = Finding(1, "I11", "review", "revenue", None, None, None, {"rule": "missing_cell:unclassified", "classified": False}, [])
        info = Finding(1, "I6", "info", "revenue", None, None, None, {"rule": "non_authoritative_source"}, [])
        assert company_state([]) == "checks_clean"
        assert company_state([review, gap_ok, info]) == "checks_clean"
        assert company_state([wrong]) == "uncertified"
        assert company_state([gap_bad]) == "uncertified"

    def test_apply_writes_state_by_rule_and_never_stores_info(self):
        conn = FakeConn([])
        info = Finding(2, "I6", "info", "revenue", date(2022, 9, 30), D(1), D(1), {"rule": "non_authoritative_source"}, [1])
        apply_chunk(conn, [1, 2, 3], [finding(1, "review"), finding(2, "wrong_value"), info],
                    datetime(2026, 10, 21, tzinfo=timezone.utc))
        inserted = conn.log[1][2]
        assert [(r[0], r[2]) for r in inserted] == [(1, "review"), (2, "wrong_value")]  # info never written
        certs = {r[0]: r for r in conn.log[2][2]}
        assert certs[1][1] == "checks_clean" and certs[1][3] == 1  # review stored, does not block
        assert certs[2][1] == "uncertified"
        assert certs[3][1] == "checks_clean" and certs[3][3] == 0

    def test_morning_summary_counts_states_wrong_values_and_i11_cells(self):
        from scrooner_pipeline.certification.runner import morning_summary, render_summary, RunResult
        r = RunResult()
        r.companies = {1: {"ticker": "A"}, 2: {"ticker": "B"}}
        r.findings = [finding(1, "wrong_value"), finding(2, "review")]
        r.history = {1: {"missing": {("revenue", "FY", "unclassified"): [date(2015, 12, 31), date(2016, 12, 31)],
                                     ("cfo", "Q", "q4_not_derived"): [date(2016, 6, 30)]},
                         "missing_metrics": {("roe", "FY", "no_row_inputs_present"): [date(2015, 12, 31)]}}}
        m = morning_summary(r)
        assert m["states"]["uncertified"] == 1 and m["states"]["checks_clean"] == 1
        assert m["wrong_by_invariant"]["I4"] == 1
        assert m["i11_cells"]["concepts"]["unclassified"] == 2 and m["i11_cells"]["concepts"]["q4_not_derived"] == 1
        assert m["unclassified_by_kind"][("concept", "FY")] == 2 and m["unclassified_by_kind"][("metric", "FY")] == 1
        text = render_summary(r)
        assert "checks_clean=1" in text and "uncertified=1" in text and "I4=1" in text

    def test_render_text_reports_counts_per_invariant_and_company(self):
        res = certify(FakeConn(self.routes()), [1])
        res.findings.append(finding(1))
        text = render_text(res, show=1)
        assert "I4" in text and "neighbour_magnitude" in text and "CLN" in text
