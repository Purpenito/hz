from app.exchanges.base import BaseExchangeAdapter


class ExchangeRegistry:
    def __init__(self, adapters: list[BaseExchangeAdapter]) -> None:
        self._adapters = {adapter.exchange: adapter for adapter in adapters}

    def get(self, exchange):
        return self._adapters[exchange]

    def all(self):
        return self._adapters.values()
