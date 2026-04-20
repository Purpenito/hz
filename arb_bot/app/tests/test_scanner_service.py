import asyncio

from app.core.enums import Exchange
from app.core.models import FundingInfo, OrderBook, OrderBookLevel
from app.exchanges.base import BaseExchangeAdapter
from app.exchanges.registry import ExchangeRegistry
from app.market_data.funding import FundingStore
from app.market_data.orderbooks import OrderBookStore
from app.market_data.symbols import SymbolsStore
from app.market_data.volumes import VolumeStore
from app.services.scanner_service import ScannerService


class _FakeAdapter(BaseExchangeAdapter):
    def __init__(self, exchange: Exchange, symbols: set[str]) -> None:
        self.exchange = exchange
        self._symbols = symbols

    async def fetch_symbols(self) -> set[str]:
        return set(self._symbols)

    def normalize_symbol(self, exchange_symbol: str) -> str:
        return exchange_symbol

    async def fetch_orderbook(self, symbol: str, depth: int = 10) -> OrderBook:
        level = OrderBookLevel(price=100.0, size=10.0)
        return OrderBook(
            symbol=symbol,
            exchange=self.exchange,
            bids=[level] * depth,
            asks=[level] * depth,
            timestamp_ms=1,
        )

    async def fetch_funding(self, symbol: str) -> FundingInfo | None:
        return FundingInfo(
            symbol=symbol,
            exchange=self.exchange,
            rate_pct=0.01,
            next_funding_ts_ms=1,
            timestamp_ms=1,
        )

    async def fetch_volume_24h(self, symbol: str) -> float:
        return 1_000_000.0

    def build_ticker_link(self, symbol: str) -> str:
        return f"https://example.com/{self.exchange.value}/{symbol}"


def test_refresh_market_data_scans_common_symbols_for_all_exchanges() -> None:
    bybit = _FakeAdapter(Exchange.BYBIT, {"BTCUSDT", "ETHUSDT"})
    kucoin = _FakeAdapter(Exchange.KUCOIN, {"ETHUSDT", "SOLUSDT"})
    bingx = _FakeAdapter(Exchange.BINGX, {"ETHUSDT", "XRPUSDT"})

    scanner = ScannerService(
        registry=ExchangeRegistry([bybit, kucoin, bingx]),
        symbols_store=SymbolsStore(),
        orderbook_store=OrderBookStore(),
        funding_store=FundingStore(),
        volume_store=VolumeStore(),
        symbols_per_exchange_cycle=1,
    )

    asyncio.run(scanner.refresh_market_data(depth=2))

    # ETHUSDT is present on 3 exchanges and must be selected as common cycle symbol.
    assert scanner.orderbook_store.get(Exchange.BYBIT, "ETHUSDT") is not None
    assert scanner.orderbook_store.get(Exchange.KUCOIN, "ETHUSDT") is not None
    assert scanner.orderbook_store.get(Exchange.BINGX, "ETHUSDT") is not None

    metrics = scanner.get_last_refresh_metrics()
    assert metrics["symbols_common_2plus"] == 1
    assert metrics["symbols_scanned_this_cycle"] == 1
