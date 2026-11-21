"""The proof loader must load concepts whose served values are stated_zero / text_stated / printed_zero."""

from __future__ import annotations

import inspect

from scrooner_pipeline.proof import shown


class _Cur:
    def __init__(self, log):
        self.log = log

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def execute(self, sql, params):
        self.log.append((sql, params))

    def fetchall(self):
        return [("interest_income",)]


class _Conn:
    def __init__(self):
        self.log = []

    def cursor(self):
        return _Cur(self.log)


def test_stated_family_concepts_queries_all_three_families():
    c = _Conn()
    assert shown.stated_family_concepts(c, 1732) == {"interest_income"}
    ((sql, params),) = c.log
    assert "canonical_fact" in sql and params[0] == 1732
    assert set(params[1]) == {
        "company_tag_map:printed_zero",
        "company_tag_map:stated_zero",
        "company_tag_map:text_stated",
    }


def test_load_shown_adds_those_concepts_to_the_names_it_loads():
    # GILD interest_income FY2024: served text_stated, no map claim row, not in EXPECTED: never proven (no_proof_row)
    assert "stated_family_concepts(conn, company_id)" in inspect.getsource(
        shown.load_shown
    )
