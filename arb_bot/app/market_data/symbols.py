from collections import defaultdict

from app.core.enums import Exchange


class SymbolsStore:
    def __init__(self) -> None:
        self.by_exchange: dict[Exchange, set[str]] = defaultdict(set)

    def set_symbols(self, exchange: Exchange, symbols: set[str]) -> None:
        self.by_exchange[exchange] = symbols

    def common(self, ex_a: Exchange, ex_b: Exchange) -> set[str]:
        return self.by_exchange.get(ex_a, set()) & self.by_exchange.get(ex_b, set())
