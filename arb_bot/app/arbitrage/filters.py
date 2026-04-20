from app.core.enums import ArbitrageType
from app.core.models import ArbitrageSignal, UserSettings


def passes_user_filters(signal: ArbitrageSignal, settings: UserSettings) -> bool:
    if not settings.notifications_enabled:
        return False
    if signal.long_exchange not in settings.enabled_exchanges:
        return False
    if signal.short_exchange not in settings.enabled_exchanges:
        return False
    if signal.arbitrage_type not in settings.enabled_arbitrage_types:
        return False
    if signal.min_volume_24h < settings.min_volume_24h:
        return False
    edge = signal.net_spread_pct
    if signal.arbitrage_type == ArbitrageType.FUNDING and signal.total_edge_pct is not None:
        edge = signal.total_edge_pct
    if edge < settings.min_profit_pct:
        return False
    if signal.executable_ratio_pct < settings.min_executable_ratio_pct:
        return False
    if signal.signal_age_ms > settings.max_signal_age_ms:
        return False
    return True
