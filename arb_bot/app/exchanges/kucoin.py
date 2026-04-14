import httpx

from app.core.enums import Exchange
from app.core.models import FundingInfo, OrderBook, OrderBookLevel
from app.exchanges.base import BaseExchangeAdapter
from app.utils.links import ticker_link
from app.utils.time import now_ms


class KucoinAdapter(BaseExchangeAdapter):
    exchange = Exchange.KUCOIN
    _base_url = "https://api-futures.kucoin.com"

    def _contract_symbol(self, symbol: str) -> str:
        return f"{symbol}M"

    async def fetch_symbols(self) -> set[str]:
        return {"BTCUSDT", "ETHUSDT", "SOLUSDT"}

    def normalize_symbol(self, exchange_symbol: str) -> str:
        normalized = exchange_symbol.upper().replace("-", "")
        if normalized.endswith("M"):
            normalized = normalized[:-1]
        if normalized.startswith("XBT"):
            normalized = "BTC" + normalized[3:]
        return normalized

    async def fetch_orderbook(self, symbol: str, depth: int = 10) -> OrderBook:
        contract = self._contract_symbol(symbol)
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                f"{self._base_url}/api/v1/level2/snapshot",
                params={"symbol": contract},
            )
            data = resp.json()["data"]

        limit = min(max(depth, 1), 50)
        bids = [OrderBookLevel(price=float(x[0]), size=float(x[1])) for x in data.get("bids", [])[:limit]]
        asks = [OrderBookLevel(price=float(x[0]), size=float(x[1])) for x in data.get("asks", [])[:limit]]
        ts = int(data.get("ts") or now_ms())
        return OrderBook(symbol=symbol, exchange=self.exchange, bids=bids, asks=asks, timestamp_ms=ts)

    async def fetch_funding(self, symbol: str) -> FundingInfo | None:
        contract = self._contract_symbol(symbol)
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(f"{self._base_url}/api/v1/contracts/{contract}")
            data = resp.json()["data"]

        current = now_ms()
        return FundingInfo(
            symbol=symbol,
            exchange=self.exchange,
            rate_pct=float(data.get("fundingFeeRate", 0.0)) * 100,
            next_funding_ts_ms=current + 3600000,
            timestamp_ms=current,
        )

    async def fetch_volume_24h(self, symbol: str) -> float:
        contract = self._contract_symbol(symbol)
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(f"{self._base_url}/api/v1/contracts/{contract}")
            data = resp.json()["data"]
        return float(data.get("turnoverOf24h", 0.0))

    def build_ticker_link(self, symbol: str) -> str:
        return ticker_link(self.exchange, symbol)
