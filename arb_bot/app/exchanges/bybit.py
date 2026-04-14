from app.core.enums import Exchange
from app.exchanges._stub import StubExchangeAdapter


class BybitAdapter(StubExchangeAdapter):
    exchange = Exchange.BYBIT
