from app.core.enums import Exchange
from app.exchanges._stub import StubExchangeAdapter


class KucoinAdapter(StubExchangeAdapter):
    exchange = Exchange.KUCOIN
