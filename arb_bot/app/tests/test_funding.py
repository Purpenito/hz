from app.arbitrage.funding import calc_funding_signal
from app.core.enums import Exchange
from app.core.models import FundingInfo, OrderBook, OrderBookLevel


def test_calc_funding_signal():
    long_ob = OrderBook("ETHUSDT", Exchange.GATE, [OrderBookLevel(100, 2)], [OrderBookLevel(99, 2)], 1)
    short_ob = OrderBook("ETHUSDT", Exchange.KUCOIN, [OrderBookLevel(102, 2)], [OrderBookLevel(101, 2)], 1)
    long_f = FundingInfo("ETHUSDT", Exchange.GATE, -0.012, 1000, 1)
    short_f = FundingInfo("ETHUSDT", Exchange.KUCOIN, 0.018, 1000, 1)

    signal = calc_funding_signal("ETHUSDT", long_ob, short_ob, long_f, short_f, 100, 10_000_000, 1, "a", "b")
    assert signal is not None
    assert signal.funding_edge_pct == 0.03
