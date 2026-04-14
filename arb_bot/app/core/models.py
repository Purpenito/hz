from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from app.core.enums import ArbitrageType, Exchange


@dataclass(slots=True)
class OrderBookLevel:
    price: float
    size: float


@dataclass(slots=True)
class OrderBook:
    symbol: str
    exchange: Exchange
    bids: list[OrderBookLevel]
    asks: list[OrderBookLevel]
    timestamp_ms: int


@dataclass(slots=True)
class FundingInfo:
    symbol: str
    exchange: Exchange
    rate_pct: float
    next_funding_ts_ms: int
    timestamp_ms: int


@dataclass(slots=True)
class UserSettings:
    telegram_user_id: int
    notifications_enabled: bool = True
    enabled_exchanges: list[Exchange] = field(default_factory=lambda: [Exchange.BYBIT, Exchange.KUCOIN])
    enabled_arbitrage_types: list[ArbitrageType] = field(
        default_factory=lambda: [ArbitrageType.FUTURES_FUTURES, ArbitrageType.FUNDING]
    )
    min_profit_pct: float = 0.01
    min_volume_24h: float = 100_000.0
    capital_usdt: float = 100.0
    min_executable_ratio_pct: float = 50.0
    max_signal_age_ms: int = 10_000


@dataclass(slots=True)
class ArbitrageSignal:
    signal_key: str
    arbitrage_type: ArbitrageType
    symbol: str
    long_exchange: Exchange
    short_exchange: Exchange
    top_long_price: float
    top_short_price: float
    avg_long_price: float
    avg_short_price: float
    top_level_size_usdt: float
    max_executable_usdt: float
    capital_usdt: float
    trade_size_usdt: float
    executable_ratio_pct: float
    gross_spread_pct: float
    fees_pct: float
    net_spread_pct: float
    min_volume_24h: float
    signal_age_ms: int
    long_link: str
    short_link: str
    funding_long_pct: float | None = None
    funding_short_pct: float | None = None
    funding_edge_pct: float | None = None
    total_edge_pct: float | None = None
    funding_explain: str | None = None


def min_volume(values: Iterable[float]) -> float:
    values_list = list(values)
    return min(values_list) if values_list else 0.0
