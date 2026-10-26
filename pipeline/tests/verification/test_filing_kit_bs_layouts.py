"""Balance-sheet layouts the Verifier found the kit misreading (total-liabilities dry run, 2026-10-26):
OMC/LYB/MCK mezzanine, EMR scale, duplicate date columns, PEP 'Liabilities', LEA bare 'Equity', WEC subtotals."""

from datetime import date
from decimal import Decimal

from scrooner_pipeline.verification import filing_kit as fk

D = date(2020, 12, 31)


def _bs(rows, head="BALANCE SHEETS - USD ($) $ in Millions", dates=("Dec. 31, 2020",)):
    h = "<tr><th class='tl'>" + head + "</th>" + "".join(f"<th>{d}</th>" for d in dates) + "</tr>"
    body = ""
    for lab, *vals in rows:
        tds = "".join("<td class='text'>&#160;</td>" if v is None else f"<td class='nump'>{v}</td>" for v in vals)
        body += f"<tr><td class='pl'>{lab}</td>{tds}</tr>"
    return fk.parse_rpage(h + body)


def test_omc_mezzanine_after_asset_side_equity_method_row():
    # 'Equity method investments' sits among ASSETS; it must not be taken as the start of equity
    p = _bs([("Equity method investments", 90), ("Total assets", 1000), ("Total Current Liabilities", 300),
             ("Temporary Equity - Redeemable Noncontrolling Interests", 20), ("Shareholders' Equity:", None),
             ("Common stock", 5), ("Total Equity", 200), ("TOTAL LIABILITIES AND EQUITY", 1000)])
    r = fk.face_liabilities(p, D)
    assert r.value == Decimal(780) and "Temporary Equity - Redeemable Noncontrolling Interests" in r.parts


def test_lyb_mck_label_names_the_mezzanine():
    for le in ("Total liabilities, redeemable non-controlling interests and equity",
               "Total Liabilities, Redeemable Noncontrolling Interests, and Deficit"):
        p = _bs([("Investments in equity affiliates", 50), ("Total assets", 500), ("Total current liabilities", 100),
                 ("Redeemable non-controlling interests", 14), ("Total equity", 100), (le, 500)])
        assert fk.face_liabilities(p, D).value == Decimal(386)


def test_emr_shares_in_thousands_does_not_set_the_scale():
    p = _bs([("Total liabilities", 19356)], head="Consolidated Balance Sheets - USD ($) shares in Thousands, $ in Millions")
    assert p.multiplier == 1_000_000


def test_duplicate_date_columns():
    same = _bs([("Total liabilities", 50, 60, 60)], dates=("Dec. 31, 2020", "Dec. 31, 2019", "Dec. 31, 2019"))
    assert fk.face_liabilities(same, date(2019, 12, 31)).value == Decimal(60)
    diff = _bs([("Total liabilities", 50, 60, 61)], dates=("Dec. 31, 2020", "Dec. 31, 2019", "Dec. 31, 2019"))
    r = fk.face_liabilities(diff, date(2019, 12, 31))
    assert r.value is None and r.method == "unavailable" and "differ" in r.note


def test_pep_plain_liabilities_total():
    p = _bs([("Total current liabilities", 20000), ("Liabilities", 62930), ("Total Equity", 20000), ("Total liabilities and equity", 82930)])
    r = fk.face_liabilities(p, D)
    assert (r.method, r.value) == ("printed_total", Decimal(62930))


def test_lea_bare_equity_total_includes_nci():
    p = _bs([("Total current liabilities", 5667), ("Total long-term liabilities", 3975), ("Equity:", None),
             ("Lear Corporation shareholders' equity", 5035), ("Noncontrolling interests", 166), ("Equity", 5201),
             ("Total liabilities and equity", 14843)])
    r = fk.face_liabilities(p, D)
    assert (r.method, r.value) == ("derived", Decimal(9642)) and "Equity" in r.parts
    # the NCI-inclusive bare 'Equity' wins over a parent-only total, wherever it is printed
    q = _bs([("Total current liabilities", 5667), ("Total long-term liabilities", 3975), ("Equity", 5201),
             ("Total Lear shareholders' equity", 5035), ("Total liabilities and equity", 14843)])
    assert fk.face_liabilities(q, D).value == Decimal(9642)


def test_equity_method_row_each_guard_on_its_own():
    # no 'Total assets' row: the label guard alone must keep the asset-side row out of equity
    a = _bs([("Equity method investments", 90), ("Total current liabilities", 300), ("Redeemable NCI", 20),
             ("Common stock", 5), ("Total Equity", 200), ("Total liabilities and equity", 1000)])
    assert fk.face_liabilities(a, D).value == Decimal(780)
    # a 'capital' asset row before Total assets: the position guard alone
    b = _bs([("Deferred capital costs", 90), ("Total assets", 1000), ("Total current liabilities", 300), ("Redeemable NCI", 20),
             ("Common stock", 5), ("Total Equity", 200), ("Total liabilities and equity", 1000)])
    assert fk.face_liabilities(b, D).value == Decimal(780)


def test_wec_subtotals_flagged_and_guarded():
    rows = [("Total assets", 35422), ("Current liabilities", None), ("Accounts payable", 751), ("Current liabilities", 2840),
            ("Long-term liabilities", None), ("Long-term debt", 11652), ("Long-term liabilities", 22023),
            ("Common shareholders' equity", None), ("Common stock", 3), ("Additional paid in capital", 4164),
            ("Common shareholders' equity", 10451), ("Preferred stock of subsidiary", 30), ("Noncontrolling interests", 78),
            ("Total liabilities and equity", 35422)]
    r = fk.face_liabilities(_bs(rows), D)
    assert r.method == "derived_from_subtotals" and r.value == Decimal(24863) and "subtotals" in r.note
    # a liability-like line after the long-term subtotal means a section is unsummed: refuse
    rows2 = rows[:7] + [("Contributions in aid of construction", 1276)] + rows[7:]
    assert fk.face_liabilities(_bs(rows2), D).method == "unavailable"
    # only one subtotal: refuse
    assert fk.face_liabilities(_bs([r_ for r_ in rows if r_[0] != "Long-term liabilities"]), D).method == "unavailable"
    # subtotals that exceed total L&E cannot be liabilities
    bad = [("Total assets", 100), ("Current liabilities", 60), ("Long-term liabilities", 70), ("Common stock", 3), ("Total liabilities and equity", 100)]
    assert fk.face_liabilities(_bs(bad), D).method == "unavailable"
