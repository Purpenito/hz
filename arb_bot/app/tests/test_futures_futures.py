from app.arbitrage.futures_futures import calc_futures_futures_signal
from app.core.enums import Exchange
from app.core.models import OrderBook, OrderBookLevel


def test_calc_futures_futures_signal():
    long_ob = OrderBook(
        symbol="BTCUSDT",
        exchange=Exchange.BYBIT,
        asks=[OrderBookLevel(100, 2)],
        bids=[OrderBookLevel(99, 2)],
        timestamp_ms=1,
    )
    short_ob = OrderBook(
        symbol="BTCUSDT",
        exchange=Exchange.OKX,
        asks=[OrderBookLevel(102, 2)],
        bids=[OrderBookLevel(101, 2)],
        timestamp_ms=1,
    )
    signal = calc_futures_futures_signal("BTCUSDT", long_ob, short_ob, 100, 1_000_000, 10, "a", "b")
    assert signal is not None
    assert signal.net_spread_pct > 0
