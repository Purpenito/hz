from app.core.enums import ArbitrageType
from app.core.models import ArbitrageSignal


def format_signal_text(signal: ArbitrageSignal) -> str:
    base = (
        f"💎 {signal.symbol} | {signal.arbitrage_type.value}\n\n"
        f"LONG: {signal.long_exchange.value.upper()}\n"
        f"SHORT: {signal.short_exchange.value.upper()}\n\n"
        f"Links:\n"
        f"{signal.long_exchange.value.title()}: {signal.long_link}\n"
        f"{signal.short_exchange.value.title()}: {signal.short_link}\n\n"
        f"Prices top long/short: {signal.top_long_price:.6f} / {signal.top_short_price:.6f}\n"
        f"Avg fill long/short: {signal.avg_long_price:.6f} / {signal.avg_short_price:.6f}\n\n"
        f"Top level size: {signal.top_level_size_usdt:.2f} USDT\n"
        f"Max executable: {signal.max_executable_usdt:.2f} USDT\n"
        f"Capital/Trade size: {signal.capital_usdt:.2f} / {signal.trade_size_usdt:.2f} USDT\n"
        f"Executable ratio: {signal.executable_ratio_pct:.1f}%\n\n"
        f"Gross spread: {signal.gross_spread_pct:+.4f}%\n"
        f"Fees: {signal.fees_pct:.4f}%\n"
        f"Net spread: {signal.net_spread_pct:+.4f}%\n\n"
        f"Signal age: {signal.signal_age_ms / 1000:.1f} sec\n"
        f"24h volume (min): {signal.min_volume_24h:,.2f} USDT"
    )
    if signal.arbitrage_type != ArbitrageType.FUNDING:
        return base
    return (
        base
        + "\n\n"
        + f"Funding long/short: {signal.funding_long_pct:+.4f}% / {signal.funding_short_pct:+.4f}%\n"
        + f"Funding explain: {signal.funding_explain}\n"
        + f"Funding edge: {signal.funding_edge_pct:+.4f}%\n"
        + f"Total edge: {signal.total_edge_pct:+.4f}%"
    )
