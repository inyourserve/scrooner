from datetime import date, datetime, timezone

import pytest

from scrooner_pipeline.company_master.market_price_alpaca import _alpaca_symbol, _trading_date


@pytest.mark.unit
def test_after_hours_utc_bar_keeps_its_new_york_trading_day():
    # Real AAPL bar from a Sunday run: 23:59Z is still Friday in New York.
    assert _trading_date(datetime(2026, 9, 25, 23, 59, tzinfo=timezone.utc)) == date(2026, 9, 25)


@pytest.mark.unit
def test_old_bar_keeps_its_own_date_not_the_run_date():
    assert _trading_date(datetime(2021, 10, 22, 20, 0, tzinfo=timezone.utc)) == date(2021, 10, 22)


@pytest.mark.unit
@pytest.mark.parametrize(
    ("ticker", "symbol"),
    [("BRK-A", "BRK.A"), ("BF-B", "BF.B"), ("MOG-A", "MOG.A"), ("AAPL", "AAPL"), ("PHXE-P", "PHXE-P"), ("ANG-PD", "ANG-PD")],
)
def test_share_class_tickers_use_alpaca_dot_form(ticker, symbol):
    assert _alpaca_symbol(ticker) == symbol
