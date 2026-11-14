"""resolve_bs.py (data-team/tags/line_map/tools): position-based BS family roles, instant note facts, class-sum shares, unclassified balance sheets.
Synthetic filings in FSN extract format (st|rep|ln|tag|custom|neg|prole|label|value)."""
import sys
from decimal import Decimal as D
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[2] / "data-team" / "tags" / "line_map" / "tools"
sys.path.insert(0, str(TOOLS))
import resolve_bs  # noqa: E402


def filing(lines, cpv=""):
    return {"cik": "1", "a": "0-0-1", "p": "2020-12-31", "fd": "2021-02-01", "calc": "",
            "lines": "~".join("|".join(map(str, (("BS", 2, i + 1) + (t, 0, 0, "", lb, "" if v is None else v)))) for i, (t, lb, v) in enumerate(lines)), "cpv": cpv}


CLASSIFIED = [("AssetsCurrentAbstract", "Current assets", None), ("CashAndCashEquivalentsAtCarryingValue", "Cash and cash equivalents", 100),
              ("InventoryFinishedGoodsNetOfReserves", "Finished goods", 40), ("InventoryNet", "Inventories", 70), ("AssetsCurrent", "Total current assets", 170),
              ("Assets", "Total assets", 500), ("AccountsPayableCurrent", "Accounts payable", 30), ("LiabilitiesCurrent", "Total current liabilities", 60)]


def test_position_picks_total_not_component_and_no_calc_needed():
    r = resolve_bs.resolve_family(filing(CLASSIFIED), {})
    assert r["inventory"]["value"] == 70 and r["inventory"]["status"] == "mapped"
    assert r["cash_and_equivalents"]["value"] == 100 and r["accounts_payable"]["value"] == 30


def test_instant_note_fact_when_no_face_line():
    r = resolve_bs.resolve_family(filing(CLASSIFIED), {"Goodwill": D(257)})
    assert r["goodwill"]["status"] == "mapped" and r["goodwill"]["value"] == 257 and r["goodwill"]["rule"] == "note"
    assert resolve_bs.resolve_family(filing(CLASSIFIED), {})["goodwill"]["status"] == "not_presented"


def test_bank_cash_total_beats_cash_and_due_from_banks():
    lines = [("CashAndDueFromBanks", "Cash and due from banks", 31), ("CashAndCashEquivalentsAtCarryingValue", "Cash and cash equivalents", 159), ("Assets", "Total assets", 900)]
    assert resolve_bs.resolve_family(filing(lines), {})["cash_and_equivalents"]["value"] == 159


def test_unclassified_balance_sheet_current_totals_not_presented():
    lines = [("CashAndDueFromBanks", "Cash", 5), ("Assets", "Total assets", 900)]
    r = resolve_bs.resolve_family(filing(lines), {})
    assert r["current_assets"]["status"] == "not_presented" and r["current_liabilities"]["status"] == "not_presented"
    assert "current_assets" not in resolve_bs.resolve_family(filing(CLASSIFIED), {})


def test_shares_class_sum_and_undimensioned_wins():
    cpv = "R3|5|CommonStockSharesOutstanding|Common A|ClassOfStock=CommonClassAMember;|100~R3|6|CommonStockSharesOutstanding|Common B|ClassOfStock=CommonClassBMember;|20~R3|7|CommonStockSharesOutstanding|Preferred|ClassOfStock=PreferredStockMember;|9"
    r = resolve_bs.resolve_family(filing(CLASSIFIED, cpv), {})["shares_outstanding"]
    assert r["status"] == "component_sum" and r["value"] == 120
    r = resolve_bs.resolve_family(filing(CLASSIFIED, cpv), {"CommonStockSharesOutstanding": D(121)})["shares_outstanding"]
    assert r["status"] == "mapped" and r["value"] == 121
    assert resolve_bs.resolve_family(filing(CLASSIFIED), {})["shares_outstanding"]["status"] == "not_presented"


def test_note_beats_combined_caption_and_duplicate_fact_precision():
    lines = [x for x in CLASSIFIED if x[0] != "AccountsPayableCurrent"]
    lines.insert(-1, ("AccountsPayableAndAccruedLiabilitiesCurrent", "Accounts payable and accrued", 90))
    assert resolve_bs.resolve_family(filing(lines), {})["accounts_payable"]["status"] == "combined"
    assert resolve_bs.resolve_family(filing(lines), {"AccountsPayableCurrent": D(30)})["accounts_payable"]["value"] == 30
    assert resolve_bs.notes_for("CommonStockSharesOutstanding|0|1900000000~CommonStockSharesOutstanding|0|1949316000")["CommonStockSharesOutstanding"] == 1949316000
