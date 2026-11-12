"""CI is the income statement when the filing has no IS with net income (CB 2014-2018 10-Qs)."""

import psycopg
import pytest

from scrooner_pipeline.fsn_store.stmt_effective import effective_stmt_sql


@pytest.fixture
def conn(isolated_database_url):
    c = psycopg.connect(isolated_database_url)
    ok = c.execute(
        "select count(*) from information_schema.tables where table_schema = 'fsn' "
        "and table_name in ('filing', 'line', 'tag')"
    ).fetchone()[0]
    if ok != 3:
        c.close()
        pytest.skip("needs migration 0118")
    yield c
    c.close()


def _filing(conn, acc, lines):
    """lines: (report, stmt, tag). Returns {(report, tag): effective stmt}."""
    fid = conn.execute(
        "insert into fsn.filing (accession, cik, form, fsn_set) values (%s, '1', '10-Q', 's') returning id",
        (acc,),
    ).fetchone()[0]
    for i, (rep, stmt, tag) in enumerate(lines):
        tid = conn.execute(
            "insert into fsn.tag (tag, version) values (%s, 'v') on conflict (tag, version) "
            "do update set tag = excluded.tag returning id",
            (tag,),
        ).fetchone()[0]
        conn.execute(
            "insert into fsn.line (filing_id, report, line, stmt, tag_id) values (%s, %s, %s, %s, %s)",
            (fid, rep, i, stmt, tid),
        )
    rows = conn.execute(
        f"select l.report, t.tag::text, {effective_stmt_sql('l')}::text from fsn.line l "
        "join fsn.tag t on t.id = l.tag_id where l.filing_id = %s",
        (fid,),
    ).fetchall()
    dec = lambda x: x.decode() if isinstance(x, bytes) else x  # noqa: E731
    return {(r, dec(t)): dec(s) for r, t, s in rows}


def test_combined_ci_report_is_the_income_statement_when_is_has_no_net_income(conn):
    # CB: report 4 = combined IS+CI (stmt CI), report 5 = its parenthetical (stmt IS, no net income)
    r = _filing(
        conn,
        "a1",
        [
            (4, "CI", "Revenues"),
            (4, "CI", "NetIncomeLoss"),
            (4, "CI", "OtherComprehensiveIncomeLossNetOfTax"),
            (5, "IS", "CommonStockParOrStatedValuePerShare"),
            (3, "BS", "Assets"),
        ],
    )
    assert r[(4, "Revenues")] == r[(4, "NetIncomeLoss")] == "IS"
    assert r[(5, "CommonStockParOrStatedValuePerShare")] == "IS"
    assert r[(3, "Assets")] == "BS"


def test_separate_is_and_ci_keep_ci(conn):
    r = _filing(
        conn,
        "a2",
        [
            (4, "IS", "NetIncomeLoss"),
            (6, "CI", "NetIncomeLoss"),
            (6, "CI", "ComprehensiveIncomeNetOfTax"),
        ],
    )
    assert r[(6, "ComprehensiveIncomeNetOfTax")] == "CI"
    assert r[(4, "NetIncomeLoss")] == "IS"


def test_ci_without_net_income_and_true_un_stay(conn):
    r = _filing(
        conn,
        "a3",
        [
            (6, "CI", "OtherComprehensiveIncomeLossNetOfTax"),
            (7, "UN", "NetIncomeLoss"),
            (8, "UN", "Assets"),
        ],
    )
    assert r[(6, "OtherComprehensiveIncomeLossNetOfTax")] == "CI"
    assert r[(7, "NetIncomeLoss")] == "UN"
    assert r[(8, "Assets")] == "UN"


def _filing_row(conn, cid, acc, form, amendment, stmts):
    fid = conn.execute(
        "insert into fsn.filing (accession, cik, form, fsn_set, amendment, company_id) "
        "values (%s, '1', %s, 's', %s, %s) returning id",
        (acc, form, amendment, cid),
    ).fetchone()[0]
    tid = conn.execute(
        "insert into fsn.tag (tag, version) values ('Assets', 'v') on conflict (tag, version) "
        "do update set tag = excluded.tag returning id"
    ).fetchone()[0]
    for i, s in enumerate(stmts):
        conn.execute(
            "insert into fsn.line (filing_id, report, line, stmt, tag_id) values (%s, 1, %s, %s, %s)",
            (fid, i, s, tid),
        )


def test_amendments_without_statements_are_not_expected_filings(conn):
    from scrooner_pipeline.fsn_store.select import load_filings

    # core.company.id is GENERATED ALWAYS: let the database assign it
    cid = conn.execute(
        "insert into core.company (cik, company_name) values ('0000000077', 'AMENDMENT TEST') returning id"
    ).fetchone()[0]
    _filing_row(conn, cid, "k1", "10-K", False, ["BS"])
    _filing_row(conn, cid, "k1a", "10-K/A", True, [])  # Part III only
    _filing_row(conn, cid, "k2a", "10-K/A", True, ["UN", "CP"])  # still no statement
    _filing_row(conn, cid, "q1a", "10-Q/A", True, ["CI"])  # a restated income statement
    _filing_row(conn, cid, "q2a", "10-Q/A", True, ["BS"])
    _filing_row(conn, cid, "q3", "10-Q", False, [])  # an original is never dropped here
    with conn.cursor() as cur:
        got = {
            f.accession.decode() if isinstance(f.accession, bytes) else f.accession
            for f in load_filings(cur, cid).values()
        }
    assert got == {"k1", "q1a", "q2a", "q3"}


def test_wmb_ci_report_with_net_income_beside_an_is_report_without_it(conn):
    # WMB 2026 10-Qs (0000107263-26-000017/-000026): report 2 = combined IS+CI (stmt CI, net income, tax);
    # report 9 = a Transco legal-entity statement (stmt IS: revenues, operating income, pre-tax income, NO
    # NetIncomeLoss/ProfitLoss). The face is report 2; the store's line_map made on 2026-11-09 mapped report 9 only
    r = _filing(
        conn,
        "a4",
        [
            (2, "CI", "Revenues"),
            (2, "CI", "IncomeTaxExpenseBenefit"),
            (2, "CI", "ProfitLoss"),
            (2, "CI", "NetIncomeLoss"),
            (2, "CI", "ComprehensiveIncomeNetOfTax"),
            (9, "IS", "Revenues"),
            (9, "IS", "OperatingIncomeLoss"),
            (
                9,
                "IS",
                "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",
            ),
        ],
    )
    assert (
        r[(2, "Revenues")]
        == r[(2, "IncomeTaxExpenseBenefit")]
        == r[(2, "NetIncomeLoss")]
        == "IS"
    )
    assert r[(2, "ComprehensiveIncomeNetOfTax")] == "IS"
    assert r[(9, "Revenues")] == "IS"
