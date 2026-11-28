"""interest_income_not_separately_stated (founder 2026-11-28, session scrooner-36): a year whose every presenting filing prints
only a residual 'Other income (expense), net' is a hidden year with an evidenced reason. Mutation checks: drop the class from
READER_HIDE_CLASSES (cells stay OPEN) or the problem check (an unevidenced or other-data-point hide is accepted)."""

from scrooner_pipeline.mapper import top100_coverage as t100

HEADER = "cik,ticker,data_point,period_end,grain,decision,nodes,value,accession,column,calc_check,flags,quote,locator,quote_period,resolver_version\n"
QUOTE = (
    "HIDE interest_income_not_separately_stated: FY2020 10-K 0001535527-20-000006 R4 prints 'Other income (expense), net'. "
    "Full-text search of all 7 CRWD 10-Ks (CIK 1535527) for 'interest income' finds only changes or a quarter."
)


def _cell(dp, fy, cls, code=""):
    return {
        "company_id": 1,
        "rank": 1,
        "ticker": "T",
        "data_point": dp,
        "fiscal_year": fy,
        "period_end": f"{fy}-12-31",
        "class": cls,
        "reason_code": code,
        "accession": "",
        "r_page": "",
        "evidence": "",
        "_parts_blank": 0,
    }


def _load(tmp_path, dp, quote):
    d = tmp_path / "resolver"
    d.mkdir()
    (d / "T.csv").write_text(
        HEADER
        + f'1,T,{dp},2019-12-31,FY,not_presented,,,0001535527-20-000006,own,,before_first_10k;filing_read_hide;interest_income_not_separately_stated,"{quote}",R4.htm,,r.94\n'
    )
    return t100.load_filing_read_hides(tmp_path)


def test_year_state_is_a_verified_absent_year_named_by_its_reader_class(tmp_path):
    h = _load(tmp_path, "interest_income", QUOTE)
    rows = [
        _cell("interest_income", 2019, "REASON", "structural_not_presented"),
        _cell("interest_income", 2024, "PROVEN"),
    ]
    t100.attach_filing_read_hides(rows, h)
    t100.apply_display(rows)
    c = rows[0]
    assert (c["display"], c["hide_class"]) == ("HIDDEN_YEAR", "verified_absent")
    assert c["evidence"].startswith(
        "filing read, interest_income_not_separately_stated"
    )
    _, hy = t100.hidden_evidence(rows)
    assert {r["basis"] for r in hy} == {
        "filing_read:interest_income_not_separately_stated"
    }


def test_year_state_is_refused_for_other_data_points_and_without_search_evidence(
    tmp_path,
):
    assert (
        _load(tmp_path, "other_income_expense_net", QUOTE) == {}
    )  # interest_income only
    assert t100.not_separately_stated_problem("interest_income", "no search")
    assert t100.not_separately_stated_problem(
        "interest_income", "Full-text search finds only deltas, cites no filing"
    )
    assert not t100.not_separately_stated_problem("interest_income", QUOTE)
