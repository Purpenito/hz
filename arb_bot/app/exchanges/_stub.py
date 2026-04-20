from __future__ import annotations

from app.core.enums import Exchange
from app.core.models import FundingInfo, OrderBook, OrderBookLevel
from app.exchanges.base import BaseExchangeAdapter
from app.utils.links import ticker_link
from app.utils.time import now_ms


PRICE_BIAS = {
    Exchange.BYBIT: -0.35,
    Exchange.KUCOIN: 0.20,
    Exchange.OKX: 0.30,
    Exchange.GATE: -0.15,
    Exchange.BINGX: -0.05,
}

FUNDING_RATE = {
    Exchange.BYBIT: -0.008,
    Exchange.KUCOIN: 0.015,
    Exchange.OKX: 0.010,
    Exchange.GATE: -0.012,
    Exchange.BINGX: 0.006,
}

SYMBOL_BASE = {"BTCUSDT": 85000.0, "ETHUSDT": 1600.0, "SOLUSDT": 86.2}


class StubExchangeAdapter(BaseExchangeAdapter):
    exchange: Exchange

    async def fetch_symbols(self) -> set[str]:
        return {"BTCUSDT", "ETHUSDT", "SOLUSDT"}

    def normalize_symbol(self, exchange_symbol: str) -> str:
        return exchange_symbol.replace("-", "").upper()

    async def fetch_orderbook(self, symbol: str, depth: int = 10) -> OrderBook:
        mid = SYMBOL_BASE.get(symbol, 100.0) + PRICE_BIAS[self.exchange]
        step = max(mid * 0.0001, 0.01)
        bids = [OrderBookLevel(price=mid - i * step, size=0.05 * (10 + i)) for i in range(depth)]
        asks = [OrderBookLevel(price=mid + i * step, size=0.05 * (10 + i)) for i in range(depth)]
        return OrderBook(symbol=symbol, exchange=self.exchange, bids=bids, asks=asks, timestamp_ms=now_ms())

    async def fetch_funding(self, symbol: str) -> FundingInfo | None:
        current = now_ms()
        return FundingInfo(
            symbol=symbol,
            exchange=self.exchange,
            rate_pct=FUNDING_RATE[self.exchange],
            next_funding_ts_ms=current + 3600000,
            timestamp_ms=current,
        )

    async def fetch_volume_24h(self, symbol: str) -> float:
        return 250_000_000.0 if symbol == "BTCUSDT" else 90_000_000.0

    def build_ticker_link(self, symbol: str) -> str:
        return ticker_link(self.exchange, symbol)
