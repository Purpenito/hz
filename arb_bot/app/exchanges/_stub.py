from __future__ import annotations

from app.core.enums import Exchange
from app.core.models import FundingInfo, OrderBook, OrderBookLevel
from app.exchanges.base import BaseExchangeAdapter
from app.utils.links import ticker_link
from app.utils.time import now_ms


class StubExchangeAdapter(BaseExchangeAdapter):
    exchange: Exchange

    async def fetch_symbols(self) -> set[str]:
        return {"BTCUSDT", "ETHUSDT", "SOLUSDT"}

    def normalize_symbol(self, exchange_symbol: str) -> str:
        return exchange_symbol.replace("-", "").upper()

    async def fetch_orderbook(self, symbol: str, depth: int = 10) -> OrderBook:
        mid = 100.0
        bids = [OrderBookLevel(price=mid - i * 0.1, size=10 + i) for i in range(depth)]
        asks = [OrderBookLevel(price=mid + i * 0.1, size=10 + i) for i in range(depth)]
        return OrderBook(symbol=symbol, exchange=self.exchange, bids=bids, asks=asks, timestamp_ms=now_ms())

    async def fetch_funding(self, symbol: str) -> FundingInfo | None:
        current = now_ms()
        return FundingInfo(symbol=symbol, exchange=self.exchange, rate_pct=0.01, next_funding_ts_ms=current + 3600000, timestamp_ms=current)

    async def fetch_volume_24h(self, symbol: str) -> float:
        return 1_000_000.0

    def build_ticker_link(self, symbol: str) -> str:
        return ticker_link(self.exchange, symbol)
