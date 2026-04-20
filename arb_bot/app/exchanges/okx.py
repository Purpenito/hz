from app.core.enums import Exchange
from app.exchanges._stub import StubExchangeAdapter


class OkxAdapter(StubExchangeAdapter):
    exchange = Exchange.OKX
