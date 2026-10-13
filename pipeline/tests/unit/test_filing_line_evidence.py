"""parsers/filing_line_evidence.py and coverage_matrix.apply_filing_line_evidence.

No database or network: rendered-statement HTML is built inline, the SEC client is a
stand-in, and cursors are fakes that record the SQL they were given.
"""

import httpx
import pytest

from scrooner_pipeline.mapper import coverage_matrix
from scrooner_pipeline.parsers import filing_line_evidence as fle


def _row(label: str, value: str = "1", css: str = "re") -> str:
    return f'<tr class="{css}"><td class="pl"><a>{label}</a></td><td class="nump">{value}</td></tr>'


def _statement(*labels: str) -> str:
    return "<table>" + "".join(_row(label) for label in labels) + "</table>"


def _spec(concept: str) -> fle.LineSpec:
    return fle.SPEC_BY_CONCEPT[concept]


@pytest.mark.unit
class TestExtractLabels:
    def test_hidden_definition_popup_rows_are_not_statement_lines(self):
        """Apple's phantom 'goodwill': a '- Definition ...' popup row sits under line items."""
        html = _statement(
            "Inventories",
            "- Definition Non-current portion of goodwill",
            "Total assets",
        )
        assert fle.extract_labels(html) == ["Inventories", "Total assets"]

    def test_blank_rows_are_skipped(self):
        assert fle.extract_labels(_statement("Revenue", "", "   ")) == ["Revenue"]


@pytest.mark.unit
@pytest.mark.parametrize(
    ("concept", "labels", "expected"),
    [
        # plain lines are found
        (
            "inventory",
            ["Cash", "Inventories", "Total assets"],
            (True, "Inventories", False),
        ),
        ("inventory", ["Inventory, net"], (True, "Inventory, net", False)),
        ("goodwill", ["Goodwill"], (True, "Goodwill", False)),
        ("gross_profit", ["Net sales", "Gross margin"], (True, "Gross margin", False)),
        ("cost_of_revenue", ["Cost of sales"], (True, "Cost of sales", False)),
        (
            "research_and_development",
            ["Product development"],
            (True, "Product development", False),
        ),
        (
            "operating_expenses",
            ["Total operating expenses"],
            (True, "Total operating expenses", False),
        ),
        # absent lines are reported as absent, not guessed
        (
            "inventory",
            ["Cash and due from banks", "Loans", "Total assets"],
            (False, None, False),
        ),
        ("goodwill", ["Total liabilities", "Retained earnings"], (False, None, False)),
        # a section HEADING is not the line ("Operating expenses:" precedes the real rows)
        (
            "operating_expenses",
            ["Operating expenses:", "Research and development"],
            (False, None, False),
        ),
        ("cost_of_revenue", ["Costs and expenses:"], (False, None, False)),
        # accounts payable: a plain line wins over a combined one
        (
            "accounts_payable",
            ["Accounts payable", "Accounts payable and accrued liabilities"],
            (True, "Accounts payable", False),
        ),
        (
            "accounts_payable",
            ["Trade accounts payable"],
            (True, "Trade accounts payable", False),
        ),
        # ...and only a combined line is reported as combined, not as the plain concept
        (
            "accounts_payable",
            ["Accounts payable and accrued expenses"],
            (True, "Accounts payable and accrued expenses", True),
        ),
        (
            "accounts_receivable",
            ["Accrued interest and accounts receivable"],
            (True, "Accrued interest and accounts receivable", True),
        ),
        (
            "accounts_receivable",
            ["Accounts receivable, net of allowance"],
            (True, "Accounts receivable, net of allowance", False),
        ),
        ("interest_income", ["Interest income"], (True, "Interest income", False)),
        (
            "interest_income",
            ["Interest and other income, net"],
            (True, "Interest and other income, net", True),
        ),
        (
            "interest_income",
            ["Interest income (expense), net"],
            (True, "Interest income (expense), net", False),
        ),
    ],
)
def test_classify_labels(concept, labels, expected):
    assert fle.classify_labels(_spec(concept), labels) == expected


class _Response:
    def __init__(self, text):
        self.text = text


class _Client:
    """Stands in for SECClient: serves report HTML by file name."""

    def __init__(self, pages):
        self.pages = pages
        self.fetched = []

    def get(self, url):
        name = url.rsplit("/", 1)[1]
        self.fetched.append(name)
        return _Response(self.pages[name])


def _reports(*pairs):
    return [{"title": title, "html_file": html_file} for title, html_file in pairs]


@pytest.mark.unit
class TestReadFiling:
    def test_reads_the_balance_sheet_and_income_statement_and_reports_each_concept(
        self, monkeypatch
    ):
        monkeypatch.setattr(
            fle,
            "_filing_summary_reports",
            lambda *_: _reports(
                ("CONSOLIDATED BALANCE SHEETS", "R2.htm"),
                ("CONSOLIDATED BALANCE SHEETS (Parenthetical)", "R3.htm"),
                ("CONSOLIDATED STATEMENTS OF OPERATIONS", "R4.htm"),
            ),
        )
        client = _Client(
            {
                "R2.htm": _statement(
                    "Inventories",
                    "Accounts payable and accrued expenses",
                    "Total assets",
                ),
                "R4.htm": _statement(
                    "Net sales", "Cost of sales", "Research and development"
                ),
            }
        )
        rows = {
            r["data_point"]: r
            for r in fle.read_filing(client, "0000000001", "0000000001-26-000001")
        }
        assert rows["inventory"]["line_present"] is True
        assert (
            rows["accounts_payable"]["combined"] is True
        )  # combined, not a plain line
        assert rows["goodwill"]["line_present"] is False  # statement read, no such line
        assert rows["cost_of_revenue"]["matched_label"] == "Cost of sales"
        assert rows["gross_profit"]["line_present"] is False
        assert (
            "R3.htm" not in client.fetched
        )  # the parenthetical companion table is never read

    def test_a_statement_that_cannot_be_located_is_no_evidence_not_absence(
        self, monkeypatch
    ):
        """Microsoft's 'Income Statements' title was once not found; that must read as
        'unknown', never as 'the company has no R&D line'."""
        monkeypatch.setattr(
            fle,
            "_filing_summary_reports",
            lambda *_: _reports(("BALANCE SHEETS", "R2.htm")),
        )
        client = _Client({"R2.htm": _statement("Inventories")})
        rows = {
            r["data_point"]: r
            for r in fle.read_filing(client, "0000000001", "0000000001-26-000001")
        }
        assert rows["inventory"]["line_present"] is True
        assert rows["research_and_development"]["line_present"] is None
        assert rows["cost_of_revenue"]["line_present"] is None

    def test_a_filing_with_no_rendered_reports_returns_none(self, monkeypatch):
        monkeypatch.setattr(fle, "_filing_summary_reports", lambda *_: [])
        assert (
            fle.read_filing(_Client({}), "0000000001", "0000000001-26-000001") is None
        )


class _Cursor:
    def __init__(self, conn):
        self.conn = conn
        self.rowcount = 4

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def execute(self, sql, params=None):
        self.conn.calls.append((" ".join(sql.split()), params))

    def fetchone(self):
        return (self.conn.table_exists,)

    def fetchall(self):
        return []

    def executemany(self, sql, rows):
        self.conn.calls.append((" ".join(sql.split()), list(rows)))


class _Conn:
    def __init__(self, table_exists="analytics.company_filing_line_evidence"):
        self.calls = []
        self.commits = 0
        self.table_exists = table_exists

    def cursor(self):
        return _Cursor(self)

    def commit(self):
        self.commits += 1

    def rollback(self):
        pass


@pytest.mark.unit
class TestRun:
    def _patch(self, monkeypatch, targets, behaviour):
        monkeypatch.setattr(fle, "find_targets", lambda *_: targets)
        monkeypatch.setattr(
            fle, "read_filing", lambda client, cik, accession: behaviour(cik)
        )

        class _SEC:
            def __enter__(self):
                return self

            def __exit__(self, *_):
                return False

        monkeypatch.setattr(fle, "SECClient", _SEC)
        stored, errors = [], []
        monkeypatch.setattr(
            fle,
            "store_evidence",
            lambda conn, cid, acc, form, rows: stored.append((cid, acc, len(rows))),
        )
        monkeypatch.setattr(
            fle, "log_error", lambda conn, table, cik, stage, exc: errors.append(cik)
        )
        monkeypatch.setattr(fle, "safe_rollback", lambda conn, **_: conn)
        return stored, errors

    def test_one_companys_failure_does_not_stop_the_batch(self, monkeypatch):
        def behaviour(cik):
            if cik == "0000000002":
                raise RuntimeError("SEC 503")
            return [fle.no_evidence_row(s) for s in fle.SPECS]

        targets = [
            (1, "0000000001", "a-1", "10-K"),
            (2, "0000000002", "a-2", "10-Q"),
            (3, "0000000003", "a-3", "10-K"),
        ]
        stored, errors = self._patch(monkeypatch, targets, behaviour)
        stats = fle.run(_Conn())
        assert stats["probed"] == 2 and stats["errored"] == 1
        assert [s[0] for s in stored] == [1, 3]
        assert errors == ["0000000002"]

    def test_a_filing_without_reports_stores_no_evidence_so_it_is_not_refetched_every_run(
        self, monkeypatch
    ):
        stored, _ = self._patch(
            monkeypatch, [(7, "0000000007", "a-7", "10-K")], lambda cik: None
        )
        stats = fle.run(_Conn())
        assert stats["no_reports"] == 1
        assert stored == [
            (7, "a-7", len(fle.SPECS))
        ]  # one 'no evidence' row per concept

    def test_the_time_limit_stops_new_work_and_says_so(self, monkeypatch):
        stored, _ = self._patch(
            monkeypatch,
            [(1, "0000000001", "a-1", "10-K"), (2, "0000000002", "a-2", "10-K")],
            lambda cik: [fle.no_evidence_row(s) for s in fle.SPECS],
        )
        stats = fle.run(_Conn(), max_seconds=-1)
        assert stats["stopped_by_time_limit"] == 1
        assert stored == []


@pytest.mark.unit
class TestStoreAndTargets:
    def test_store_replaces_only_that_companys_rows_in_one_commit(self):
        conn = _Conn()
        rows = [fle.no_evidence_row(s) for s in fle.SPECS]
        fle.store_evidence(conn, 42, "0000000001-26-000009", "10-K", rows)
        sql = [c[0] for c in conn.calls]
        assert (
            sql[0]
            == "delete from analytics.company_filing_line_evidence where company_id = %s"
        )
        assert conn.calls[0][1] == (42,)
        inserted = conn.calls[1][1]
        assert len(inserted) == len(fle.SPECS)
        assert {r["accession"] for r in inserted} == {"0000000001-26-000009"}
        assert conn.commits == 1

    def test_targets_are_only_active_companies_whose_stored_accession_is_stale(self):
        conn = _Conn()
        fle.find_targets(conn, None, force=False)
        sql = conn.calls[-1][0]
        assert "c.status = 'active'" in sql
        assert "f.form in ('10-K', '10-Q')" in sql
        assert "s.accession_number is distinct from l.accession_number" in sql


@pytest.mark.unit
class TestApplyEvidenceToCoverage:
    def test_does_nothing_if_the_evidence_table_does_not_exist_yet(self):
        conn = _Conn(table_exists=None)  # migration 0093 not applied
        assert coverage_matrix.apply_filing_line_evidence(conn)["rows"] == 0
        assert len(conn.calls) == 1  # only the to_regclass probe: no update attempted

    def test_only_explains_absent_cells_and_never_overwrites_a_reason_or_touches_has_value(
        self,
    ):
        conn = _Conn()
        coverage_matrix.apply_filing_line_evidence(conn)
        sql, params = conn.calls[-1]
        assert "cov.has_value = false" in sql
        assert (
            "cov.gap_reason is null" in sql
        )  # the revenue-family SIC rules ran first and win
        assert (
            "e.line_present is not null" in sql
        )  # an unlocated statement explains nothing
        set_clause = sql.split(" set ")[1].split(" from ")[0]
        assert "has_value" not in set_clause  # the commitment made to the other lanes
        assert len(params["concepts"]) == len(params["points"])  # aligned unnest arrays

    def test_each_evidenced_concept_speaks_for_its_resolved_sibling(self):
        points = coverage_matrix.FILING_LINE_DATA_POINTS
        assert points["cost_of_revenue"] == (
            "cost_of_revenue",
            "cost_of_revenue_resolved",
        )
        assert points["gross_profit"] == ("gross_profit", "gross_profit_resolved")
        assert set(points) == set(
            fle.SPEC_BY_CONCEPT
        )  # every probed concept is classified

    def test_only_the_two_standalone_line_reasons_are_structural(self):
        assert set(coverage_matrix.FILING_LINE_STRUCTURAL_REASONS) == {
            "line_not_presented_in_filing",
            "line_presented_combined_with_others",
        }
        # a line that IS in the filing and not extracted is a real gap, never structural
        assert (
            coverage_matrix.REASON_LINE_NOT_EXTRACTED
            not in coverage_matrix.FILING_LINE_STRUCTURAL_REASONS
        )


def _http_error(status: int) -> httpx.HTTPStatusError:
    request = httpx.Request(
        "GET", "https://www.sec.gov/Archives/edgar/data/1/2/FilingSummary.xml"
    )
    return httpx.HTTPStatusError(
        "boom", request=request, response=httpx.Response(status, request=request)
    )


@pytest.mark.unit
class TestMissingRenderedStatements:
    """A dormant company's last 10-K from 2006 has no FilingSummary.xml. That is 'no
    evidence', not a failure: errors were being logged and the filing retried nightly."""

    def test_a_404_on_the_filing_summary_is_no_evidence_not_an_error(self, monkeypatch):
        def missing(*_):
            raise _http_error(404)

        monkeypatch.setattr(fle, "_filing_summary_reports", missing)
        assert (
            fle.read_filing(_Client({}), "0000000001", "0000000001-06-000001") is None
        )

    def test_any_other_http_error_is_still_a_real_failure(self, monkeypatch):
        def server_error(*_):
            raise _http_error(503)

        monkeypatch.setattr(fle, "_filing_summary_reports", server_error)
        with pytest.raises(httpx.HTTPStatusError):
            fle.read_filing(_Client({}), "0000000001", "0000000001-26-000001")

    def test_a_404_on_a_statement_page_means_that_statement_was_not_located(
        self, monkeypatch
    ):
        monkeypatch.setattr(
            fle,
            "_filing_summary_reports",
            lambda *_: _reports(
                ("BALANCE SHEETS", "R2.htm"), ("STATEMENTS OF OPERATIONS", "R4.htm")
            ),
        )

        class _Half(_Client):
            def get(self, url):
                if url.endswith("R4.htm"):
                    raise _http_error(404)
                return super().get(url)

        client = _Half({"R2.htm": _statement("Inventories")})
        rows = {
            r["data_point"]: r
            for r in fle.read_filing(client, "0000000001", "0000000001-26-000001")
        }
        assert rows["inventory"]["line_present"] is True
        assert (
            rows["research_and_development"]["line_present"] is None
        )  # IS not located: unknown
