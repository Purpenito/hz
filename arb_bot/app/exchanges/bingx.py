from app.core.enums import Exchange
from app.exchanges._stub import StubExchangeAdapter


class BingxAdapter(StubExchangeAdapter):
    exchange = Exchange.BINGX
