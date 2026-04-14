import httpx

from app.core.enums import Exchange
from app.core.models import FundingInfo, OrderBook, OrderBookLevel
from app.exchanges.base import BaseExchangeAdapter
from app.utils.links import ticker_link
from app.utils.time import now_ms


class BybitAdapter(BaseExchangeAdapter):
    exchange = Exchange.BYBIT
    _base_url = "https://api.bybit.com"

    async def fetch_symbols(self) -> set[str]:
        # keep controlled universe for stable scanning speed
        return {"BTCUSDT", "ETHUSDT", "SOLUSDT"}

    def normalize_symbol(self, exchange_symbol: str) -> str:
        return exchange_symbol.replace("-", "").upper()

    async def fetch_orderbook(self, symbol: str, depth: int = 10) -> OrderBook:
        limit = min(max(depth, 1), 50)
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                f"{self._base_url}/v5/market/orderbook",
                params={"category": "linear", "symbol": symbol, "limit": limit},
            )
            data = resp.json()["result"]

        bids = [OrderBookLevel(price=float(x[0]), size=float(x[1])) for x in data.get("b", [])[:limit]]
        asks = [OrderBookLevel(price=float(x[0]), size=float(x[1])) for x in data.get("a", [])[:limit]]
        ts = int(data.get("ts") or now_ms())
        return OrderBook(symbol=symbol, exchange=self.exchange, bids=bids, asks=asks, timestamp_ms=ts)

    async def fetch_funding(self, symbol: str) -> FundingInfo | None:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                f"{self._base_url}/v5/market/tickers",
                params={"category": "linear", "symbol": symbol},
            )
            item = resp.json()["result"]["list"][0]

        current = now_ms()
        return FundingInfo(
            symbol=symbol,
            exchange=self.exchange,
            rate_pct=float(item.get("fundingRate", 0.0)) * 100,
            next_funding_ts_ms=int(item.get("nextFundingTime", current)),
            timestamp_ms=current,
        )

    async def fetch_volume_24h(self, symbol: str) -> float:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                f"{self._base_url}/v5/market/tickers",
                params={"category": "linear", "symbol": symbol},
            )
            item = resp.json()["result"]["list"][0]
        return float(item.get("turnover24h", 0.0))

    def build_ticker_link(self, symbol: str) -> str:
        return ticker_link(self.exchange, symbol)
