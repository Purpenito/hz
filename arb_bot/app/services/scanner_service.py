from itertools import product

from app.arbitrage.filters import passes_user_filters
from app.arbitrage.funding import calc_funding_signal
from app.arbitrage.futures_futures import calc_futures_futures_signal
from app.core.constants import EXCHANGE_PAIRS
from app.core.enums import ArbitrageType
from app.core.models import UserSettings, min_volume
from app.exchanges.registry import ExchangeRegistry
from app.market_data.funding import FundingStore
from app.market_data.orderbooks import OrderBookStore
from app.market_data.symbols import SymbolsStore
from app.market_data.volumes import VolumeStore
from app.utils.time import now_ms


class ScannerService:
    def __init__(
        self,
        registry: ExchangeRegistry,
        symbols_store: SymbolsStore,
        orderbook_store: OrderBookStore,
        funding_store: FundingStore,
        volume_store: VolumeStore,
    ) -> None:
        self.registry = registry
        self.symbols_store = symbols_store
        self.orderbook_store = orderbook_store
        self.funding_store = funding_store
        self.volume_store = volume_store

    async def refresh_market_data(self, depth: int = 10) -> None:
        for adapter in self.registry.all():
            symbols = await adapter.fetch_symbols()
            self.symbols_store.set_symbols(adapter.exchange, symbols)
            for symbol in symbols:
                self.orderbook_store.put(await adapter.fetch_orderbook(symbol, depth=depth))
                funding = await adapter.fetch_funding(symbol)
                if funding:
                    self.funding_store.put(funding)
                self.volume_store.put(adapter.exchange, symbol, await adapter.fetch_volume_24h(symbol))

    async def scan(self, settings: UserSettings):
        signals = []
        for ex_a, ex_b in EXCHANGE_PAIRS:
            if ex_a not in settings.enabled_exchanges or ex_b not in settings.enabled_exchanges:
                continue
            common = self.symbols_store.common(ex_a, ex_b)
            for symbol in common:
                for long_ex, short_ex in ((ex_a, ex_b), (ex_b, ex_a)):
                    long_ob = self.orderbook_store.get(long_ex, symbol)
                    short_ob = self.orderbook_store.get(short_ex, symbol)
                    if not long_ob or not short_ob:
                        continue
                    age = now_ms() - min(long_ob.timestamp_ms, short_ob.timestamp_ms)
                    min_vol = min_volume([
                        self.volume_store.get(long_ex, symbol),
                        self.volume_store.get(short_ex, symbol),
                    ])
                    long_adapter = self.registry.get(long_ex)
                    short_adapter = self.registry.get(short_ex)

                    if ArbitrageType.FUTURES_FUTURES in settings.enabled_arbitrage_types:
                        ff = calc_futures_futures_signal(
                            symbol=symbol,
                            long_ob=long_ob,
                            short_ob=short_ob,
                            capital_usdt=settings.capital_usdt,
                            min_volume_24h=min_vol,
                            signal_age_ms=age,
                            long_link=long_adapter.build_ticker_link(symbol),
                            short_link=short_adapter.build_ticker_link(symbol),
                        )
                        if ff and passes_user_filters(ff, settings):
                            signals.append(ff)

                    if ArbitrageType.FUNDING in settings.enabled_arbitrage_types:
                        long_f = self.funding_store.get(long_ex, symbol)
                        short_f = self.funding_store.get(short_ex, symbol)
                        if not long_f or not short_f:
                            continue
                        f_sig = calc_funding_signal(
                            symbol=symbol,
                            long_ob=long_ob,
                            short_ob=short_ob,
                            long_funding=long_f,
                            short_funding=short_f,
                            capital_usdt=settings.capital_usdt,
                            min_volume_24h=min_vol,
                            signal_age_ms=age,
                            long_link=long_adapter.build_ticker_link(symbol),
                            short_link=short_adapter.build_ticker_link(symbol),
                        )
                        if f_sig and passes_user_filters(f_sig, settings):
                            signals.append(f_sig)
        return signals
