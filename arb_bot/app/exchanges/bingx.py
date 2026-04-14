import httpx

from app.core.enums import Exchange
from app.core.models import FundingInfo, OrderBook, OrderBookLevel
from app.exchanges.base import BaseExchangeAdapter
from app.utils.links import ticker_link
from app.utils.time import now_ms


class BingxAdapter(BaseExchangeAdapter):
    exchange = Exchange.BINGX
    _base_url = "https://open-api.bingx.com"

    async def fetch_symbols(self) -> set[str]:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(f"{self._base_url}/openApi/swap/v2/quote/contracts")
            payload = resp.json()

        symbols: set[str] = set()
        if str(payload.get("code")) != "0":
            return symbols

        for item in payload.get("data", []):
            sym = item.get("symbol", "")
            if sym.endswith("-USDT") and item.get("status") == 1:
                symbols.add(sym.replace("-USDT", ""))

        return {f"{s}USDT" for s in symbols}

    def normalize_symbol(self, exchange_symbol: str) -> str:
        return exchange_symbol.replace("-", "").upper()

    def _contract_symbol(self, symbol: str) -> str:
        return symbol.replace("USDT", "") + "-USDT"

    async def fetch_orderbook(self, symbol: str, depth: int = 10) -> OrderBook:
        contract = self._contract_symbol(symbol)
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                f"{self._base_url}/openApi/swap/v2/quote/bookTicker",
                params={"symbol": contract},
            )
            payload = resp.json()
            top = (payload.get("data") or {}).get("book_ticker")
            if str(payload.get("code")) != "0" or not top:
                raise ValueError(f"BingX orderbook error: {payload}")

        bid = float(top["bid_price"])
        ask = float(top["ask_price"])
        bid_qty = float(top.get("bid_qty", 0))
        ask_qty = float(top.get("ask_qty", 0))
        ts = now_ms()

        # bookTicker gives top level only, extrapolate small depth levels from top for unified pipeline
        bids = [OrderBookLevel(price=bid * (1 - i * 0.00005), size=bid_qty) for i in range(depth)]
        asks = [OrderBookLevel(price=ask * (1 + i * 0.00005), size=ask_qty) for i in range(depth)]
        return OrderBook(symbol=symbol, exchange=self.exchange, bids=bids, asks=asks, timestamp_ms=ts)

    async def fetch_funding(self, symbol: str) -> FundingInfo | None:
        contract = self._contract_symbol(symbol)
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                f"{self._base_url}/openApi/swap/v2/quote/premiumIndex",
                params={"symbol": contract},
            )
            payload = resp.json()
            data = payload.get("data")
            if str(payload.get("code")) != "0" or not data:
                return None

        current = now_ms()
        return FundingInfo(
            symbol=symbol,
            exchange=self.exchange,
            rate_pct=float(data.get("lastFundingRate", 0.0)) * 100,
            next_funding_ts_ms=current + 3600000,
            timestamp_ms=current,
        )

    async def fetch_volume_24h(self, symbol: str) -> float:
        contract = self._contract_symbol(symbol)
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                f"{self._base_url}/openApi/swap/v2/quote/ticker",
                params={"symbol": contract},
            )
            payload = resp.json()
            data = payload.get("data")
            if str(payload.get("code")) != "0" or not data:
                return 0.0
        return float(data.get("quoteVolume", 0.0) or data.get("amount", 0.0) or 0.0)

    def build_ticker_link(self, symbol: str) -> str:
        return ticker_link(self.exchange, symbol)
