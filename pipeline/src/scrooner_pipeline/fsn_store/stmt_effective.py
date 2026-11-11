"""Effective statement of an FSN line (Ritwik 2026-11-11, CB 2014-2018 10-Qs).

FSN marks a combined "Statement of Operations and Comprehensive Income" as stmt = CI, and the
filing's only IS report is then the parenthetical (no net income). Revenue, net income, EPS and
tax of that filing live under CI. Reading `fsn.line.stmt` literally leaves those filings with no
income statement. The store keeps stmt = 'CI' as provenance (no column change, no reload); every
reader that selects, maps or checks IS concepts asks for the effective statement instead:

    a CI report that prints a net-income anchor is the income statement (IS) when the filing has
    no IS line that prints one. Anything else keeps its FSN stmt (a true UN stays UN, a CI report
    with no net-income line, e.g. an OCI-only statement, stays CI).
"""

from __future__ import annotations

NET_INCOME_TAGS = ("NetIncomeLoss", "ProfitLoss")
_NI = ", ".join(f"'{t}'" for t in NET_INCOME_TAGS)


def effective_stmt_sql(a: str = "l") -> str:
    """SQL expression for the effective stmt of fsn.line aliased `a` (needs fsn.line, fsn.tag)."""
    return f"""(case when {a}.stmt = 'CI'
        and exists (select 1 from fsn.line _c join fsn.tag _ct on _ct.id = _c.tag_id
                    where _c.filing_id = {a}.filing_id and _c.report = {a}.report and _ct.tag in ({_NI}))
        and not exists (select 1 from fsn.line _i join fsn.tag _it on _it.id = _i.tag_id
                        where _i.filing_id = {a}.filing_id and _i.stmt = 'IS' and _it.tag in ({_NI}))
        then 'IS' else {a}.stmt end)"""


def no_statement_amendment_sql(a: str = "f") -> str:
    """SQL predicate on fsn.filing aliased `a`: a 10-K/A or 10-Q/A that prints no IS/BS/CF/CI line
    (Part III-only or exhibit-only amendment: MO 7, SCCO 4, DIS 2, NEM 1, TMUS 1 ...). Such a filing
    never carried a statement, so it is not an expected filing and gives no expected key."""
    return f"""({a}.amendment and not exists (select 1 from fsn.line _s
        where _s.filing_id = {a}.id and _s.stmt in ('IS', 'BS', 'CF', 'CI')))"""
