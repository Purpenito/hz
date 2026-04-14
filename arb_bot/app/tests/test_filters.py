from app.arbitrage.filters import passes_user_filters
from app.core.enums import ArbitrageType, Exchange
from app.core.models import ArbitrageSignal, UserSettings


def test_filters_positive_case():
    settings = UserSettings(telegram_user_id=1)
    signal = ArbitrageSignal(
        signal_key="k",
        arbitrage_type=ArbitrageType.FUTURES_FUTURES,
        symbol="BTCUSDT",
        long_exchange=Exchange.BYBIT,
        short_exchange=Exchange.KUCOIN,
        top_long_price=100,
        top_short_price=101,
        avg_long_price=100,
        avg_short_price=101,
        top_level_size_usdt=100,
        max_executable_usdt=100,
        capital_usdt=100,
        trade_size_usdt=100,
        executable_ratio_pct=100,
        gross_spread_pct=1,
        fees_pct=0.11,
        net_spread_pct=0.89,
        min_volume_24h=1_000_000,
        signal_age_ms=100,
        long_link="a",
        short_link="b",
    )
    assert passes_user_filters(signal, settings)
