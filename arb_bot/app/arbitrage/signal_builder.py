from app.core.models import ArbitrageSignal


def dedup_key(signal: ArbitrageSignal, user_id: int) -> str:
    return (
        f"{user_id}:{signal.symbol}:{signal.arbitrage_type}:"
        f"{signal.long_exchange}:{signal.short_exchange}"
    )
