from app.arbitrage.depth_calc import buy_vwap, executable_notional, executable_ratio, sell_vwap
from app.core.models import OrderBookLevel


def test_buy_sell_vwap_and_executable():
    asks = [OrderBookLevel(price=100, size=1), OrderBookLevel(price=101, size=2)]
    bids = [OrderBookLevel(price=99, size=1), OrderBookLevel(price=98, size=2)]

    executable = executable_notional(asks, bids, capital_usdt=250)
    assert executable == 250

    buy_price, spent = buy_vwap(asks, executable)
    sell_price, received = sell_vwap(bids, executable)

    assert spent == 250
    assert received == 250
    assert buy_price > sell_price
    assert executable_ratio(executable, 500) == 50.0
