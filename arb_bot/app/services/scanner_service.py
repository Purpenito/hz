from collections import Counter

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
        symbols_per_exchange_cycle: int = 80,
    ) -> None:
        self.registry = registry
        self.symbols_store = symbols_store
        self.orderbook_store = orderbook_store
        self.funding_store = funding_store
        self.volume_store = volume_store
        self.symbols_per_exchange_cycle = max(1, symbols_per_exchange_cycle)
        self._exchange_offsets = {adapter.exchange: 0 for adapter in self.registry.all()}
        self._last_refresh_metrics: dict[str, int] = {
            "symbols_total": 0,
            "symbols_common_2plus": 0,
            "symbols_scanned_this_cycle": 0,
        }
        self.last_scan_metrics: dict[str, int] = {
            "candidates_before_filters": 0,
            "signals_after_filters": 0,
        }

    def _symbols_for_cycle(self, exchange, symbols: set[str]) -> list[str]:
        ordered = sorted(symbols)
        if len(ordered) <= self.symbols_per_exchange_cycle:
            return ordered

        offset = self._exchange_offsets.get(exchange, 0) % len(ordered)
        selected: list[str] = []
        for i in range(self.symbols_per_exchange_cycle):
            selected.append(ordered[(offset + i) % len(ordered)])
        self._exchange_offsets[exchange] = (offset + self.symbols_per_exchange_cycle) % len(ordered)
        return selected

    def get_last_refresh_metrics(self) -> dict[str, int]:
        return dict(self._last_refresh_metrics)

    async def refresh_market_data(self, depth: int = 10) -> None:
        symbols_total = 0
        symbols_scanned_this_cycle = 0

        for adapter in self.registry.all():
            try:
                symbols = await adapter.fetch_symbols()
            except Exception:
                # keep scanner alive even if one exchange API is temporarily unavailable
                continue

            self.symbols_store.set_symbols(adapter.exchange, symbols)
            symbols_total += len(symbols)
            symbols_to_scan = self._symbols_for_cycle(adapter.exchange, symbols)
            symbols_scanned_this_cycle += len(symbols_to_scan)
            for symbol in symbols_to_scan:
                try:
                    self.orderbook_store.put(await adapter.fetch_orderbook(symbol, depth=depth))
                except Exception:
                    continue

                try:
                    funding = await adapter.fetch_funding(symbol)
                    if funding:
                        self.funding_store.put(funding)
                except Exception:
                    pass

                try:
                    self.volume_store.put(adapter.exchange, symbol, await adapter.fetch_volume_24h(symbol))
                except Exception:
                    # keep previous volume (if exists) when fetch fails
                    pass

        symbol_presence: Counter[str] = Counter()
        for adapter in self.registry.all():
            for symbol in self.symbols_store.get_symbols(adapter.exchange):
                symbol_presence[symbol] += 1
        self._last_refresh_metrics = {
            "symbols_total": symbols_total,
            "symbols_common_2plus": sum(1 for cnt in symbol_presence.values() if cnt >= 2),
            "symbols_scanned_this_cycle": symbols_scanned_this_cycle,
        }

    async def scan(self, settings: UserSettings):
        signals = []
        candidates_before_filters = 0
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
                        if ff:
                            candidates_before_filters += 1
                            if passes_user_filters(ff, settings):
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
                        if f_sig:
                            candidates_before_filters += 1
                            if passes_user_filters(f_sig, settings):
                                signals.append(f_sig)
        self.last_scan_metrics = {
            "candidates_before_filters": candidates_before_filters,
            "signals_after_filters": len(signals),
        }
        return signals
