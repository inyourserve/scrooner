"""Structural hide audit (mapper/hide_audit.py, Dhairya brief 2026-11-21): a pre-filing year that a 10-K or 10-Q
presents is open; a never-reported row whose line a filing prints is open; a period only a registration statement
presents stays hidden as no_10k_presents_period. Each test fails without its rule."""

from datetime import date

from scrooner_pipeline.mapper import comparative_guard as cg
from scrooner_pipeline.mapper import hide_audit as ha
from scrooner_pipeline.mapper import top100_coverage as t100

BA = 1
MO = 1413


def _cell(cid, tk, dp, fy, **kw):
    r = {
        "company_id": cid,
        "rank": 1,
        "ticker": tk,
        "data_point": dp,
        "fiscal_year": fy,
        "period_end": f"{fy}-12-31",
        "class": "REASON",
        "reason_code": "no_10k_presents_period",
        "accession": "",
        "r_page": "",
        "evidence": "",
        "_parts_blank": 0,
        "_presented": False,
    }
    r.update(kw)
    return r


def _col(acc, form, stmt, d, qtrs, report=2):
    return cg.Column(acc, form, stmt, d, qtrs, report, 10, 10)


# --- rule 1: a year some 10-K or 10-Q presents is never hidden as pre-filing --------------------------------------


def test_a_10q_balance_sheet_column_presents_the_prior_year_end():
    q = _col("0000012927-17-000010", "10-Q", "BS", date(2016, 12, 31), 0)
    assert ha.presenting_column([q], date(2016, 12, 31), instant=True) == q
    # a quarter's duration column never presents a fiscal year; an equity roll-forward instant is not a BS column
    dur = _col("0000012927-17-000010", "10-Q", "IS", date(2016, 12, 31), 1)
    eq = _col("0000012927-17-000010", "10-Q", "EQ", date(2016, 12, 31), 0)
    assert ha.presenting_column([dur], date(2016, 12, 31), instant=False) is None
    assert ha.presenting_column([eq], date(2016, 12, 31), instant=True) is None


def test_a_pre_filing_year_a_periodic_filing_presents_is_reopened_with_its_accession():
    col = _col("0000012927-17-000010", "10-Q", "BS", date(2016, 12, 31), 0)
    r = _cell(BA, "BA", "total_assets", 2016, _before_first_filing=True)
    ha.attach_period_presence([r], {BA: [col]}, {"total_assets"})
    t100.apply_display([r])
    assert r["display"] == t100.OPEN and r["hide_class"] == ""
    assert (
        r["_reopen_rule"] == ha.RULE_YEAR and r["_reopen_prior"] == t100.HC_PRE_FILING
    )
    assert r["_reopen_accession"] == "0000012927-17-000010"
    assert "0000012927-17-000010" in r["evidence"]
    (a,) = ha.audit_rows([r])
    assert a["rule"] == ha.RULE_YEAR and a["evidence_accession"] == col.accession


def test_a_pre_filing_year_no_periodic_filing_presents_stays_hidden_as_no_10k_presents_period():
    # GEV FY2022 balance sheet: only the Form 10 shows it (out of V1 scope); the legacy code is renamed
    r = _cell(
        BA,
        "GEV",
        "total_assets",
        2022,
        reason_code="no_public_filing_for_period",
        _before_first_filing=True,
        _earliest_filing="2024-04-02",
    )
    keep = _cell(BA, "GEV", "total_assets", 2024, **{"class": "PROVEN"})
    ha.attach_period_presence([r, keep], {BA: []}, {"total_assets"})
    t100.apply_display([r, keep])
    assert r["display"] == t100.HIDDEN_YEAR and r["hide_class"] == t100.HC_PRE_FILING
    assert r["reason_code"] == "no_10k_presents_period"
    assert r["evidence"].startswith("no_10k_presents_period: no 10-K or 10-Q")
    assert not r.get("_reopen_rule")


def test_the_year_rule_leaves_other_hide_classes_alone():
    # a combined year is hidden on its own evidence even though a 10-K presents the period
    col = _col("0000764180-17-000028", "10-K", "IS", date(2016, 12, 31), 4)
    r = _cell(
        MO,
        "MO",
        "other_income_expense_net",
        2016,
        reason_code="line_presented_combined",
        _presented=True,
        _only_combined="years",
    )
    keep = _cell(MO, "MO", "other_income_expense_net", 2015, **{"class": "PROVEN"})
    ha.attach_period_presence([r, keep], {MO: [col]}, set())
    t100.apply_display([r, keep])
    assert r["display"] == t100.HIDDEN_YEAR and r["hide_class"] == t100.HC_COMBINED


# --- rule 2: a never-reported row whose line a filing prints is open ------------------------------------------------


def _vocab():
    return ha.LineVocab(
        tags={"other_income_expense_net": {"OtherNonoperatingIncomeExpense"}},
        company_tags={("BA", "interest_income"): {"ba_InterestIncomeOther"}},
        labels={
            "other_income_expense_net": {"other income net"},
            "cf_ap_change": {"accounts payable"},
        },
        known={"NoninterestIncomeOther": {"noninterest_income"}},
    )


def _hit(tag, plabel, acc="0000764180-16-000128", custom=False):
    return ha.LineHit(acc, "10-K", "IS", 4, 12, tag, plabel, "", custom)


def test_lines_match_by_tag_company_tag_or_learned_label():
    v = _vocab()
    lines = [
        (MO, _hit("OtherNonoperatingIncomeExpense", "Other income, net")),
        (
            MO,
            _hit(
                "mo_OtherIncomeNet",
                "Other income, net",
                acc="0000764180-17-000028",
                custom=True,
            ),
        ),
        (MO, _hit("GainsLossesOnExtinguishmentOfDebt", "Loss on early extinguishment")),
        (BA, _hit("ba_InterestIncomeOther", "Interest income")),
    ]
    want = {(MO, "other_income_expense_net"), (BA, "interest_income")}
    got = ha.hits_by_row(lines, v, {MO: "MO", BA: "BA"}, want)
    mo = got[(MO, "other_income_expense_net")]
    assert [(h.tag, h.basis) for h in mo] == [
        ("OtherNonoperatingIncomeExpense", "tag"),
        ("mo_OtherIncomeNet", "label"),
    ]
    assert [h.basis for h in got[(BA, "interest_income")]] == ["tag"]


def test_a_label_on_another_data_points_tag_or_on_the_wrong_statement_is_no_hit():
    v = _vocab()
    bank = (
        BA,
        _hit("NoninterestIncomeOther", "Other income", custom=True),
    )  # a tag the library gives to another data point (noninterest income)
    std = (
        BA,
        _hit("NoninterestIncomeOtherOperatingIncome", "Other income"),
    )  # JPM/WFC: a standard tag outside the vocabulary; its label alone is not the line
    bs_ap = (
        BA,
        ha.LineHit(
            "a", "10-Q", "BS", 2, 23, "ba_AccountsPayable", "Accounts payable", "", True
        ),
    )
    cf_ap = (
        BA,
        ha.LineHit(
            "a", "10-Q", "CF", 5, 9, "ba_ChangeInPayables", "Accounts payable", "", True
        ),
    )
    want = {(BA, "other_income_expense_net"), (BA, "cf_ap_change")}
    v.labels["other_income_expense_net"].add("other income")
    got = ha.hits_by_row(
        [bank, std, bs_ap, cf_ap], v, {BA: "BA"}, want, {"accounts_payable"}
    )
    assert (BA, "other_income_expense_net") not in got
    assert [(h.stmt, h.tag) for h in got[(BA, "cf_ap_change")]] == [
        ("CF", "ba_ChangeInPayables")
    ]
    # an instant data point counts only a balance-sheet line
    inst = ha.LineVocab({"inventory": {"InventoryNet"}}, {}, {})
    cf = (BA, ha.LineHit("a", "10-Q", "CF", 5, 9, "InventoryNet", "Inventories", ""))
    assert (
        ha.hits_by_row([cf], inst, {BA: "BA"}, {(BA, "inventory")}, {"inventory"}) == {}
    )


def _row_cells(hits):
    cells = [
        _cell(
            MO,
            "MO",
            "other_income_expense_net",
            fy,
            reason_code="structural_not_presented",
            _presented=True,
        )
        for fy in (2015, 2016)
    ]
    ha.attach_line_hits(cells, {(MO, "other_income_expense_net"): hits} if hits else {})
    t100.apply_display(cells)
    return cells


def test_a_never_reported_row_with_a_printed_line_is_reopened_citing_the_line():
    h = ha.LineHit(
        "0000764180-16-000128",
        "10-K",
        "IS",
        4,
        12,
        "OtherNonoperatingIncomeExpense",
        "Other income, net",
        "label",
    )
    cells = _row_cells([h])
    assert all(c["display"] == t100.OPEN for c in cells)
    assert {c["_reopen_rule"] for c in cells} == {ha.RULE_ROW}
    assert "0000764180-16-000128 R4.htm line 12" in cells[0]["evidence"]
    s = ha.audit_summary(ha.audit_rows(cells))
    assert s["total"] == 2
    assert s["per_rule"] == {f"{ha.RULE_ROW}:{t100.HC_STRUCTURAL}": 2}
    assert s["per_company"] == {f"MO:{ha.RULE_ROW}": 2}


def test_a_never_reported_row_with_no_printed_line_stays_hidden():
    cells = _row_cells([])
    assert all(c["display"] == t100.HIDDEN_ROW for c in cells)
    assert all(c["hide_class"] == t100.HC_STRUCTURAL for c in cells)


# --- vocabulary sources ---------------------------------------------------------------------------------------------


def test_library_primary_tags_skip_parts_and_components():
    rows = [
        {
            "element": "OtherNonoperatingIncomeExpense",
            "role_kind": "other_income_expense_net:primary#2",
        },
        {"element": "SellingExpense", "role_kind": "sga_expense:primary-part#2"},
        {"element": "DerivativeGainLossOnDerivativeNet", "role_kind": ""},
    ]
    assert ha.library_primary_tags(rows) == {
        "other_income_expense_net": {"OtherNonoperatingIncomeExpense"}
    }


def test_learned_labels_need_two_companies_and_a_primary_top_element():
    primary = {"other_income_expense_net": {"OtherNonoperatingIncomeExpense"}}
    rows = [
        {
            "data_point": "other_income_expense_net",
            "label": "other income , net",
            "companies": "32",
            "elements": "OtherNonoperatingIncomeExpense 158;NonoperatingIncomeExpense 53",
        },
        {
            "data_point": "other_income_expense_net",
            "label": "loss on extinguishment of debt",
            "companies": "6",
            "elements": "GainsLossesOnExtinguishmentOfDebt 27",
        },
        {
            "data_point": "other_income_expense_net",
            "label": "other, net (one filer)",
            "companies": "1",
            "elements": "OtherNonoperatingIncomeExpense 3",
        },
    ]
    rows.append(
        {
            "data_point": "other_income_expense_net",
            "label": "Other",
            "companies": "9",
            "elements": "OtherNonoperatingIncomeExpense 40",
        }
    )
    assert ha.learned_dp_labels(rows, primary) == {
        "other_income_expense_net": {"other income net"}
    }
    assert ha.norm_label("Other income, net") == "other income net"


def test_resolver_tags_are_single_line_mapped_rows_of_the_same_company_only():
    n = "OtherNonoperatingIncomeExpense=12 [R4.htm:12] | why: IS face"
    rows = [
        {
            "ticker": "MO",
            "data_point": "other_income_expense_net",
            "decision": "mapped",
            "nodes": n,
        },
        {
            "ticker": "KO",
            "data_point": "other_income_expense_net",
            "decision": "mapped",
            "nodes": n,
        },
        {
            "ticker": "BA",
            "data_point": "interest_income",
            "decision": "mapped",
            "nodes": "ba_InterestIncomeOther=5 [R4.htm:9] | why: IS face",
        },
        {
            "ticker": "BA",
            "data_point": "sga_expense",
            "decision": "component_sum",
            "nodes": "SellingExpense=1 + GeneralAndAdministrativeExpense=2 | why: parts",
        },
        {
            "ticker": "BA",
            "data_point": "capex",
            "decision": "not_presented",
            "nodes": "PaymentsToAcquirePropertyPlantAndEquipment=1",
        },
    ]
    rows.append(
        {
            "ticker": "BA",
            "data_point": "gross_profit",
            "decision": "derived_not_printed",
            "nodes": "SalesRevenueNet=9 [R4.htm:1] | why: revenue minus cost",
        }
    )
    per_co = ha.resolver_direct_tags(rows)
    assert per_co[("MO", "other_income_expense_net")] == {
        "OtherNonoperatingIncomeExpense"
    }
    assert ("BA", "gross_profit") not in per_co
    assert per_co[("BA", "interest_income")] == {"ba_InterestIncomeOther"}
    assert ("BA", "sga_expense") not in per_co and ("BA", "capex") not in per_co


class _Conn:
    def __init__(self):
        self.params = None

    def execute(self, sql, params):
        self.params = params
        return self

    def fetchall(self):
        return []


def test_the_period_read_covers_10q_forms_and_the_annual_guard_does_not():
    c = _Conn()
    ha.read_presenting_columns(c, [BA])
    assert "10-Q" in c.params[2] and "10-K" in c.params[2]
    cg.read_columns(c, [BA])
    assert "10-Q" not in c.params[2]
