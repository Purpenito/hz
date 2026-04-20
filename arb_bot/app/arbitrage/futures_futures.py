from app.arbitrage.depth_calc import buy_vwap, executable_notional, executable_ratio, sell_vwap
from app.core.constants import DEFAULT_FEE_PCT
from app.core.enums import ArbitrageType
from app.core.models import ArbitrageSignal, OrderBook
from app.utils.math import pct_diff


def calc_futures_futures_signal(
    symbol: str,
    long_ob: OrderBook,
    short_ob: OrderBook,
    capital_usdt: float,
    min_volume_24h: float,
    signal_age_ms: int,
    long_link: str,
    short_link: str,
) -> ArbitrageSignal | None:
    top_long = long_ob.asks[0].price
    top_short = short_ob.bids[0].price
    top_level_size = min(long_ob.asks[0].price * long_ob.asks[0].size, short_ob.bids[0].price * short_ob.bids[0].size)

    max_exec = executable_notional(long_ob.asks, short_ob.bids, capital_usdt)
    avg_long, spent = buy_vwap(long_ob.asks, max_exec)
    avg_short, received = sell_vwap(short_ob.bids, max_exec)
    if spent <= 0 or received <= 0:
        return None

    gross = pct_diff(avg_long, avg_short)
    fees = DEFAULT_FEE_PCT * 2
    net = gross - fees
    ratio = executable_ratio(max_exec, capital_usdt)

    return ArbitrageSignal(
        signal_key=f"{symbol}:{ArbitrageType.FUTURES_FUTURES}:{long_ob.exchange}:{short_ob.exchange}",
        arbitrage_type=ArbitrageType.FUTURES_FUTURES,
        symbol=symbol,
        long_exchange=long_ob.exchange,
        short_exchange=short_ob.exchange,
        top_long_price=top_long,
        top_short_price=top_short,
        avg_long_price=avg_long,
        avg_short_price=avg_short,
        top_level_size_usdt=top_level_size,
        max_executable_usdt=max_exec,
        capital_usdt=capital_usdt,
        trade_size_usdt=max_exec,
        executable_ratio_pct=ratio,
        gross_spread_pct=gross,
        fees_pct=fees,
        net_spread_pct=net,
        min_volume_24h=min_volume_24h,
        signal_age_ms=signal_age_ms,
        long_link=long_link,
        short_link=short_link,
    )
