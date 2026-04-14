from app.core.enums import Exchange

DEFAULT_DEPTH_LEVELS = 10
DEFAULT_FEE_PCT = 0.02  # per side, conservative default for maker-like execution

EXCHANGE_PAIRS = [
    (Exchange.BYBIT, Exchange.KUCOIN),
    (Exchange.BYBIT, Exchange.OKX),
    (Exchange.BYBIT, Exchange.GATE),
    (Exchange.BYBIT, Exchange.BINGX),
    (Exchange.KUCOIN, Exchange.OKX),
    (Exchange.KUCOIN, Exchange.GATE),
    (Exchange.KUCOIN, Exchange.BINGX),
    (Exchange.OKX, Exchange.GATE),
    (Exchange.OKX, Exchange.BINGX),
    (Exchange.GATE, Exchange.BINGX),
]
