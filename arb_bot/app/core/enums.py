from enum import StrEnum


class Exchange(StrEnum):
    BYBIT = "bybit"
    KUCOIN = "kucoin"
    OKX = "okx"
    GATE = "gate"
    BINGX = "bingx"


class ArbitrageType(StrEnum):
    FUTURES_FUTURES = "futures_futures"
    FUNDING = "funding"
