from app.core.models import OrderBookLevel


def buy_vwap(asks: list[OrderBookLevel], notional_usdt: float) -> tuple[float, float]:
    remaining = notional_usdt
    spent = 0.0
    qty = 0.0
    for level in asks:
        level_notional = level.price * level.size
        take_notional = min(level_notional, remaining)
        take_qty = take_notional / level.price
        spent += take_notional
        qty += take_qty
        remaining -= take_notional
        if remaining <= 1e-9:
            break
    if qty == 0:
        return 0.0, 0.0
    return spent / qty, spent


def sell_vwap(bids: list[OrderBookLevel], notional_usdt: float) -> tuple[float, float]:
    remaining = notional_usdt
    received = 0.0
    qty = 0.0
    for level in bids:
        level_notional = level.price * level.size
        take_notional = min(level_notional, remaining)
        take_qty = take_notional / level.price
        received += take_notional
        qty += take_qty
        remaining -= take_notional
        if remaining <= 1e-9:
            break
    if qty == 0:
        return 0.0, 0.0
    return received / qty, received


def executable_notional(asks: list[OrderBookLevel], bids: list[OrderBookLevel], capital_usdt: float) -> float:
    asks_available = sum(level.price * level.size for level in asks)
    bids_available = sum(level.price * level.size for level in bids)
    return min(capital_usdt, asks_available, bids_available)


def executable_ratio(executable_usdt: float, capital_usdt: float) -> float:
    if capital_usdt <= 0:
        return 0.0
    return (executable_usdt / capital_usdt) * 100.0
