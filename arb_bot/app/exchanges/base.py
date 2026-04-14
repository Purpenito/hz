from __future__ import annotations

from abc import ABC, abstractmethod

from app.core.enums import Exchange
from app.core.models import FundingInfo, OrderBook


class BaseExchangeAdapter(ABC):
    exchange: Exchange

    @abstractmethod
    async def fetch_symbols(self) -> set[str]:
        raise NotImplementedError

    @abstractmethod
    def normalize_symbol(self, exchange_symbol: str) -> str:
        raise NotImplementedError

    @abstractmethod
    async def fetch_orderbook(self, symbol: str, depth: int = 10) -> OrderBook:
        raise NotImplementedError

    @abstractmethod
    async def fetch_funding(self, symbol: str) -> FundingInfo | None:
        raise NotImplementedError

    @abstractmethod
    async def fetch_volume_24h(self, symbol: str) -> float:
        raise NotImplementedError

    @abstractmethod
    def build_ticker_link(self, symbol: str) -> str:
        raise NotImplementedError
