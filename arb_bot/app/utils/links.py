from app.core.enums import Exchange


def ticker_link(exchange: Exchange, symbol: str) -> str:
    normalized = symbol.replace("/", "").replace(":", "")
    base = {
        Exchange.BYBIT: "https://www.bybit.com/trade/usdt/",
        Exchange.KUCOIN: "https://www.kucoin.com/futures/trade/",
        Exchange.OKX: "https://www.okx.com/trade-swap/",
        Exchange.GATE: "https://www.gate.io/futures_trade/USDT/",
        Exchange.BINGX: "https://bingx.com/en-us/futures/forward/",
    }[exchange]
    return f"{base}{normalized}"
