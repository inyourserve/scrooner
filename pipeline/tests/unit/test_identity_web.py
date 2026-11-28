"""Identity web over the shown export (proof/identity_web.py, 2026-11-22): every accounting identity per company x
fiscal year, the suspect cell of a break (the member no filing fact or proof supports), the self-check opening it,
and the draw checker counting an identity-consistent cell as corroborated. One pass and one break per identity, so
each test fails without its identity (mutation-checked)."""

from __future__ import annotations

from decimal import Decimal as D

from scrooner_pipeline.certification import display_cert as dc
from scrooner_pipeline.certification import draw_check as dck
from scrooner_pipeline.proof import identity_web as idw

ACC = "0000000001-24-000001"
Q1, Q2, Q3 = "0000000001-24-000101", "0000000001-24-000102", "0000000001-24-000103"
PE = "2023-12-31"
PRIOR = "2022-12-31"


def cell(
    dp: str, v, tag: str = "", fy: str = "2023", pe: str = PE, proof: str = "PROVEN"
) -> dc.Cell:
    return dc.Cell(dp, fy, pe, dc.SHOWN, D(str(v)), ACC, "R4", tag, proof=proof)


def fact(tag: str, v, q: int = 0, dd: str = PE, acc: str = ACC, form: str = "10-K"):
    return (acc, form, tag, dd, q, str(v), -6, "USD")


def web(cells, facts=(), cf_lines=(), auto=None):
    wf = idw.WebFacts(list(facts), list(cf_lines))
    proof = {c.key: c.proof for c in cells}
    return idw.identity_web(cells, wf, auto or {}, proof)


def one(results, identity: str) -> idw.WebResult:
    got = [r for r in results if r.identity == identity]
    assert len(got) == 1, [(r.identity, r.status) for r in results]
    return got[0]


# ---------------------------------------------------------------- 1. balance sheet
BS = [
    cell("total_assets", 1003),
    cell("total_liabilities", 601),
    cell("stockholders_equity", 301),
]


def test_balance_sheet_closes_with_nci_and_temporary_equity_from_the_filing():
    facts = [fact("MinorityInterest", 61), fact(idw.TEMP_EQUITY_TOTAL_TAG, 40)]
    assert one(web(BS, facts), idw.ID_BS).status == idw.WEB_PASS


def test_balance_sheet_breaks_without_the_operands_and_names_the_unsupported_side():
    facts = [
        fact("MinorityInterest", 61),
        fact("LiabilitiesAndStockholdersEquity", 1003),
    ]
    auto = {
        ("total_assets", "2023"): "AUTO_MATCH",
        ("stockholders_equity", "2023"): "AUTO_MATCH",
    }
    r = one(web(BS, facts, auto=auto), idw.ID_BS)
    assert r.status == idw.WEB_BREAK
    assert r.suspects == (
        "total_liabilities",
    )  # assets ties L&SE; equity matches its filing fact


# ---------------------------------------------------------------- 2. current <= total
def test_current_assets_above_total_assets_breaks():
    ok = web([cell("current_assets", 401), cell("total_assets", 1003)])
    assert one(ok, idw.ID_CURRENT).status == idw.WEB_PASS
    bad = web(
        [cell("current_assets", 4001, proof=""), cell("total_assets", 1003)],
        auto={("total_assets", "2023"): "AUTO_MATCH"},
    )
    r = one(bad, idw.ID_CURRENT)
    assert r.status == idw.WEB_BREAK and r.suspects == ("current_assets",)


# ---------------------------------------------------------------- 3. cash flow
CF = [
    cell("cfo", 503),
    cell("cash_flow_investing", -301),
    cell("cash_flow_financing", -151),
]


def test_cash_flow_ties_to_the_change_in_cash_including_fx():
    facts = [
        fact(idw.CASH_CHANGE_INCL_FX[0], 41, q=4),
        fact(idw.FX_TAGS[0], -10, q=4),
    ]
    assert one(web(CF, facts), idw.ID_CF).status == idw.WEB_PASS


def test_cash_flow_from_restricted_cash_balances_when_no_change_line():
    facts = [
        fact("CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents", 253),
        fact(
            "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents",
            202,
            dd=PRIOR,
        ),
    ]
    assert one(web(CF, facts), idw.ID_CF).status == idw.WEB_PASS


def test_cash_flow_break_names_the_unmatched_member():
    facts = [fact(idw.CASH_CHANGE_INCL_FX[0], 91, q=4)]
    auto = {
        ("cfo", "2023"): "AUTO_MATCH",
        ("cash_flow_investing", "2023"): "AUTO_MATCH",
    }
    r = one(web(CF, facts, auto=auto), idw.ID_CF)
    assert r.status == idw.WEB_BREAK and r.suspects == ("cash_flow_financing",)


# ---------------------------------------------------------------- 4. net income to the CF start
CF_LINES = [
    (ACC, "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents", 7, 1),
    (ACC, "ProfitLoss", 7, 3),
]


def test_net_income_ties_to_profit_loss_less_nci_income():
    facts = [
        fact("ProfitLoss", 122, q=4),
        fact("NetIncomeLossAttributableToNoncontrollingInterest", 21, q=4),
    ]
    assert (
        one(web([cell("net_income", 101)], facts, CF_LINES), idw.ID_NI_CF).status
        == idw.WEB_PASS
    )


def test_net_income_off_the_cf_start_breaks():
    facts = [
        fact("ProfitLoss", 122, q=4),
        fact("NetIncomeLossAttributableToNoncontrollingInterest", 21, q=4),
    ]
    r = one(web([cell("net_income", 122, proof="")], facts, CF_LINES), idw.ID_NI_CF)
    assert r.status == idw.WEB_BREAK and r.suspects == ("net_income",)


# ---------------------------------------------------------------- 5. gross profit
def test_gross_profit_is_revenue_less_cost_of_revenue():
    ok = [
        cell("revenue", 1003),
        cell("cost_of_revenue", 607),
        cell("gross_profit", 396),
    ]
    assert one(web(ok), idw.ID_GP).status == idw.WEB_PASS
    bad = [
        cell("revenue", 1003),
        cell("cost_of_revenue", 607, proof="UNCHECKED"),
        cell("gross_profit", 296),
    ]
    r = one(
        web(
            bad,
            auto={
                ("revenue", "2023"): "AUTO_MATCH",
                ("gross_profit", "2023"): "AUTO_MATCH",
            },
        ),
        idw.ID_GP,
    )
    assert r.status == idw.WEB_BREAK and r.suspects == ("cost_of_revenue",)


# ---------------------------------------------------------------- 6. operating income to pretax band
def test_pretax_band_is_other_income_less_interest():
    ok = [
        cell("operating_income", 503),
        cell("income_before_tax", 471),
        cell("other_income_expense_net", 9),
        cell("interest_expense", 51),
        cell("interest_income", 11),
    ]
    assert one(web(ok), idw.ID_BAND).status == idw.WEB_PASS
    bad = [
        cell("operating_income", 503),
        cell("income_before_tax", 471),
        cell("other_income_expense_net", 201, proof=""),
    ]
    r = one(web(bad), idw.ID_BAND)
    assert r.status == idw.WEB_BREAK and r.suspects == ("other_income_expense_net",)


# ---------------------------------------------------------------- 7. quarters sum to the year
QTABLE = [
    fact("Revenues", 241, q=1, dd="2023-03-31"),
    fact("Revenues", 251, q=1, dd="2023-06-30"),
    fact("Revenues", 259, q=1, dd="2023-09-30"),
    fact("Revenues", 251, q=1, dd="2023-12-31"),
]


def test_quarters_of_the_10k_table_sum_to_the_year():
    assert (
        one(web([cell("revenue", 1002, "Revenues")], QTABLE), idw.ID_QUARTERS).status
        == idw.WEB_PASS
    )


def test_quarters_not_summing_to_the_year_break():
    r = one(web([cell("revenue", 1103, "Revenues", proof="")], QTABLE), idw.ID_QUARTERS)
    assert r.status == idw.WEB_BREAK and r.suspects == ("revenue",)


def test_quarters_from_the_10qs_plus_the_10k_q4():
    facts = [
        fact("Revenues", 241, q=1, dd="2023-03-31", acc=Q1, form="10-Q"),
        fact("Revenues", 251, q=1, dd="2023-06-30", acc=Q2, form="10-Q"),
        fact("Revenues", 259, q=1, dd="2023-09-30", acc=Q3, form="10-Q"),
        fact("Revenues", 251, q=1, dd="2023-12-31"),
    ]
    assert (
        one(web([cell("revenue", 1002, "Revenues")], facts), idw.ID_QUARTERS).status
        == idw.WEB_PASS
    )
    assert (
        one(web([cell("revenue", 1203, "Revenues")], facts), idw.ID_QUARTERS).status
        == idw.WEB_BREAK
    )


# ---------------------------------------------------------------- 8. shares x EPS
def test_shares_times_eps_is_income_available_to_common():
    facts = [fact("NetIncomeLossAvailableToCommonStockholdersBasic", 1007, q=4)]
    ok = [cell("basic_eps", "2.51"), cell("weighted_basic_shares", 401)]
    assert one(web(ok, facts), idw.ID_EPS).status == idw.WEB_PASS
    bad = [cell("basic_eps", "25.1", proof=""), cell("weighted_basic_shares", 401)]
    r = one(
        web(bad, facts, auto={("weighted_basic_shares", "2023"): "AUTO_MATCH"}),
        idw.ID_EPS,
    )
    assert r.status == idw.WEB_BREAK and r.suspects == ("basic_eps",)


# ---------------------------------------------------------------- attribution, corroboration, wiring
def test_a_break_every_member_of_which_matches_its_filing_is_a_filing_break_never_opened():
    auto = {
        (dp, "2023"): "AUTO_MATCH"
        for dp in ("revenue", "cost_of_revenue", "gross_profit")
    }
    bad = [
        cell("revenue", 1003),
        cell("cost_of_revenue", 607),
        cell("gross_profit", 296),
    ]
    r = one(web(bad, auto=auto), idw.ID_GP)
    assert r.status == idw.WEB_FILING_BREAK and r.suspects == ()


def test_exact_identity_corroborates_its_one_unsettled_member():
    auto = {
        ("revenue", "2023"): "AUTO_MATCH",
        ("cost_of_revenue", "2023"): "AUTO_MATCH",
    }
    res = web(
        [
            cell("revenue", 1003),
            cell("cost_of_revenue", 607),
            cell("gross_profit", 396),
        ],
        auto=auto,
    )
    corr = idw.web_corroborated(res)
    assert ("gross_profit", "2023") in corr
    checks = [
        dck.AutoCheck(
            "gross_profit", "2023", dck.NEEDS_READ, "family", None, "custom line"
        ),
        dck.AutoCheck("revenue", "2023", dck.AUTO_MATCH, "family", D(1003), ""),
    ]
    out = dck.corroborate(checks, corr)
    assert out[0].outcome == dck.AUTO_MATCH and out[0].method == "identity"
    # never overturns a mismatch; a slack identity (shares x EPS) never corroborates
    mm = [dck.AutoCheck("gross_profit", "2023", dck.AUTO_MISMATCH, "family", D(1), "")]
    assert dck.corroborate(mm, corr)[0].outcome == dck.AUTO_MISMATCH
    eps = web(
        [cell("basic_eps", "2.51"), cell("weighted_basic_shares", 401)],
        [fact("NetIncomeLossAvailableToCommonStockholdersBasic", 1007, q=4)],
        auto={("weighted_basic_shares", "2023"): "AUTO_MATCH"},
    )
    assert idw.web_corroborated(eps) == {}


def test_self_check_opens_the_suspect_cell_with_the_identity_reason():
    res = web(
        [
            cell("revenue", 1003),
            cell("cost_of_revenue", 607, proof=""),
            cell("gross_profit", 296),
        ],
        auto={
            ("revenue", "2023"): "AUTO_MATCH",
            ("gross_profit", "2023"): "AUTO_MATCH",
        },
    )
    run = dc.Run("T", "x.csv", "sha", "seed", {})
    run.web = res
    fs = [f for f in dc.self_check_findings(run) if f.check == "identity"]
    assert [(f.data_point, f.fiscal_year, f.severity) for f in fs] == [
        ("cost_of_revenue", "2023", "FAIL")
    ]
    rows = [
        {
            "data_point": "cost_of_revenue",
            "fiscal_year": "2023",
            "display": dc.SHOWN,
            "reason": "",
        }
    ]
    opened, _ = dc.apply_self_check(rows, fs)
    assert (
        opened
        and rows[0]["display"] == dc.OPEN
        and "identity gross_profit breaks" in rows[0]["reason"]
    )


class WebSrc:
    """identity_facts + filing_facts only: what identity_web_check reads."""

    def identity_facts(self, cik, tags):
        return idw.WebFacts([])

    def filing_facts(self, accessions, period_ends):
        facts = [
            dck.FilingFact(ACC, "Revenues", PE, 4, "", D(1003), 0, "USD"),
            dck.FilingFact(ACC, "CostOfRevenue", PE, 4, "", D(607), 0, "USD"),
        ]
        lines = [
            dck.FilingLine(ACC, "Revenues", 4, "IS", "Revenues", 1),
            dck.FilingLine(ACC, "CostOfRevenue", 4, "IS", "Cost of revenue", 2),
        ]
        return facts, lines


def test_identity_web_check_uses_the_draw_checker_census_as_support():
    cells = [
        cell("revenue", 1003, "Revenues", proof=""),
        cell("cost_of_revenue", 607, "CostOfRevenue", proof=""),
        cell(
            "gross_profit", 296, "", proof=""
        ),  # no proof anywhere: only the census tells the members apart
    ]
    got = dc.identity_web_check(cells, "1", WebSrc())
    assert got is not None
    res, census = got
    assert census[("revenue", "2023")].outcome == dck.AUTO_MATCH
    r = one(res, idw.ID_GP)
    assert r.status == idw.WEB_BREAK and r.suspects == ("gross_profit",)
    assert (
        dc.identity_web_check(cells, "1", object()) is None
    )  # a source without the reads: not run


def test_a_banded_break_never_opens_a_proven_cell():
    facts = [fact("NetIncomeLossAvailableToCommonStockholdersBasic", 1007, q=4)]
    proven = [cell("basic_eps", "25.1"), cell("weighted_basic_shares", 401)]
    r = one(
        web(proven, facts, auto={("weighted_basic_shares", "2023"): "AUTO_MATCH"}),
        idw.ID_EPS,
    )
    assert (
        r.status == idw.WEB_BREAK
        and r.suspects == ("basic_eps",)
        and not r.opens("basic_eps")
    )
    unproven = [cell("basic_eps", "25.1", proof=""), cell("weighted_basic_shares", 401)]
    r = one(
        web(unproven, facts, auto={("weighted_basic_shares", "2023"): "AUTO_MATCH"}),
        idw.ID_EPS,
    )
    assert r.opens("basic_eps")
    gp = [
        cell("revenue", 1003),
        cell("cost_of_revenue", 607),
        cell("gross_profit", 296),
    ]
    r = one(
        web(
            gp,
            auto={
                ("revenue", "2023"): "AUTO_MATCH",
                ("cost_of_revenue", "2023"): "AUTO_MATCH",
            },
        ),
        idw.ID_GP,
    )
    assert r.opens("gross_profit")  # an exact identity opens even a proven cell
