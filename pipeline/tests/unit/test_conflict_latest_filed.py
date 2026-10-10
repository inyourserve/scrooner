import pytest

from scrooner_pipeline.normalizer import conflict_latest_filed as m


@pytest.mark.unit
def test_rule_is_scoped_to_validated_tags_and_annual_flow_facts():
    assert m.RULE == "latest_filed_fy_v1"
    assert {t for _, t in m.VALIDATED_TAGS} == {
        "NetIncomeLoss",
        "NetCashProvidedByUsedInOperatingActivities",
        "Revenues",
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "OperatingIncomeLoss",
        "GrossProfit",
    }
    assert (m.FULL_YEAR_MIN_DAYS, m.FULL_YEAR_MAX_DAYS) == (340, 380)
    assert (m.QUARTER_MIN_DAYS, m.QUARTER_MAX_DAYS) == (80, 100)


@pytest.mark.unit
def test_quarterly_rule_is_limited_to_the_four_tags_validated_for_quarters():
    """Cash flow's raw quarterly facts are year-to-date and RevenueFromContract
    was not measured quarterly, so neither may ride along on the annual list."""
    assert m.RULE_QUARTER == "latest_filed_quarter_v1"
    assert {t for _, t in m.VALIDATED_QUARTER_TAGS} == {
        "NetIncomeLoss",
        "Revenues",
        "OperatingIncomeLoss",
        "GrossProfit",
    }
    assert set(m.VALIDATED_QUARTER_TAGS) <= set(m.VALIDATED_TAGS)


@pytest.mark.unit
def test_promote_sql_only_touches_unresolved_groups_and_audits_each_promotion():
    sql = " ".join(m.PROMOTE_SQL.split())
    # Latest filing first, ties to the highest fact id.
    assert "order by fl.filing_date desc, f.id desc" in sql
    # Never overrides a Stage 2e decision, and never promotes a lone or agreeing row.
    assert "rn = 1 and n > 1 and not any_auth and vmin <> vmax" in sql
    assert "not f.is_authoritative" in sql
    # Annual and discrete Q1-Q3 durations only, each with its own tag list;
    # derived facts never compete.
    assert "p.fiscal_period = 'FY' and f.concept_id = any(%(concept_ids)s)" in sql
    assert (
        "p.fiscal_period in ('Q1', 'Q2', 'Q3') and f.concept_id = any(%(quarter_concept_ids)s)"
        in sql
    )
    assert "not f.is_derived" in sql
    # The audit row carries whichever rule (annual vs quarterly) promoted it.
    assert "select id, rule, n, vmin, vmax from promoted" in sql
    # Promotion and audit row are one statement, so neither can exist without the other.
    assert "insert into core.fact_conflict_resolution" in sql
    assert "update core.fact f set is_authoritative = true" in sql


class _Cursor:
    def __init__(self, conn):
        self.conn = conn
        self.rowcount = 7

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def execute(self, sql, params=None):
        self.conn.calls.append((sql, params))

    def fetchone(self):
        return (1,)

    def fetchall(self):
        return [("0000000001", 1), ("0000000002", 2)]


class _Conn:
    def __init__(self):
        self.calls = []
        self.commits = 0

    def cursor(self):
        return _Cursor(self)

    def commit(self):
        self.commits += 1

    def rollback(self):
        pass


@pytest.mark.unit
def test_resolve_latest_filed_batches_by_company_and_commits_each_batch():
    conn = _Conn()
    totals = m.resolve_latest_filed(conn, {"0000000001", "0000000002"})
    assert totals["considered"] == 2
    assert totals["batches"] == 1
    assert totals["errored"] == 0
    assert totals["promoted"] == 7
    assert conn.commits == 1
    promote_calls = [
        p for sql, p in conn.calls if "core.fact_conflict_resolution" in sql
    ]
    assert promote_calls and promote_calls[0]["rule"] == m.RULE
    assert promote_calls[0]["rule_quarter"] == m.RULE_QUARTER
    assert promote_calls[0]["company_ids"] == [1, 2]


@pytest.mark.unit
def test_a_timed_out_batch_is_split_and_retried_down_to_single_companies(monkeypatch):
    """25 companies hit the pooler's 2-minute statement_timeout on a busy DB
    once quarters were added; every failed batch silently skipped its
    companies. A timed-out batch must split, and only a lone company that
    still times out may be recorded as an error."""
    import psycopg

    calls = []

    def fake_promote(conn, company_ids, concept_ids, quarter_concept_ids):
        calls.append(list(company_ids))
        if len(company_ids) > 2 or 3 in company_ids:  # id 3 can never succeed
            raise psycopg.errors.QueryCanceled(
                "canceling statement due to statement timeout"
            )
        return len(company_ids)

    logged = []
    monkeypatch.setattr(m, "promote_for_companies", fake_promote)
    monkeypatch.setattr(m, "safe_rollback", lambda conn, **_: conn)
    monkeypatch.setattr(
        m, "log_error", lambda conn, table, cik, stage, exc: logged.append(cik)
    )

    totals = {"batches": 0, "splits": 0, "errored": 0, "promoted": 0}
    m._promote_with_split(
        _Conn(), ["c1", "c2", "c3", "c4"], [1, 2, 3, 4], [9], [9], totals
    )

    assert totals["splits"] >= 1
    assert totals["promoted"] == 3  # companies 1, 2 and 4 succeed; 3 does not
    assert totals["errored"] == 1 and logged == ["c3"]
    assert [3] in calls  # retried alone before being given up on
