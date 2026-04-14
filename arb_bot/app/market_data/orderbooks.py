from app.core.enums import Exchange
from app.core.models import OrderBook


class OrderBookStore:
    def __init__(self) -> None:
        self._data: dict[tuple[Exchange, str], OrderBook] = {}

    def put(self, orderbook: OrderBook) -> None:
        self._data[(orderbook.exchange, orderbook.symbol)] = orderbook

    def get(self, exchange: Exchange, symbol: str) -> OrderBook | None:
        return self._data.get((exchange, symbol))
