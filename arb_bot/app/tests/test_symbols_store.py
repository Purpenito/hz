from app.core.enums import Exchange
from app.market_data.symbols import SymbolsStore


def test_symbols_store_get_and_common() -> None:
    store = SymbolsStore()
    store.set_symbols(Exchange.BYBIT, {"BTCUSDT", "ETHUSDT"})
    store.set_symbols(Exchange.KUCOIN, {"ETHUSDT", "SOLUSDT"})

    assert store.get_symbols(Exchange.BYBIT) == {"BTCUSDT", "ETHUSDT"}
    assert store.get_symbols(Exchange.OKX) == set()
    assert store.common(Exchange.BYBIT, Exchange.KUCOIN) == {"ETHUSDT"}
