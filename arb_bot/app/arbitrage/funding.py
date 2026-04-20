from app.arbitrage.futures_futures import calc_futures_futures_signal
from app.core.enums import ArbitrageType
from app.core.models import ArbitrageSignal, FundingInfo, OrderBook


def calc_funding_signal(
    symbol: str,
    long_ob: OrderBook,
    short_ob: OrderBook,
    long_funding: FundingInfo,
    short_funding: FundingInfo,
    capital_usdt: float,
    min_volume_24h: float,
    signal_age_ms: int,
    long_link: str,
    short_link: str,
) -> ArbitrageSignal | None:
    base = calc_futures_futures_signal(
        symbol=symbol,
        long_ob=long_ob,
        short_ob=short_ob,
        capital_usdt=capital_usdt,
        min_volume_24h=min_volume_24h,
        signal_age_ms=signal_age_ms,
        long_link=long_link,
        short_link=short_link,
    )
    if not base:
        return None
    base.arbitrage_type = ArbitrageType.FUNDING
    base.signal_key = f"{symbol}:{ArbitrageType.FUNDING}:{long_ob.exchange}:{short_ob.exchange}"

    long_receive = -long_funding.rate_pct if long_funding.rate_pct < 0 else 0.0
    short_receive = short_funding.rate_pct if short_funding.rate_pct > 0 else 0.0
    funding_edge = long_receive + short_receive

    base.funding_long_pct = long_funding.rate_pct
    base.funding_short_pct = short_funding.rate_pct
    base.funding_edge_pct = funding_edge
    base.total_edge_pct = base.net_spread_pct + funding_edge
    base.funding_explain = f"LONG receives {long_receive:.4f}% | SHORT receives {short_receive:.4f}%"
    return base
