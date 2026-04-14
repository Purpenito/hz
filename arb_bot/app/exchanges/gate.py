from app.core.enums import Exchange
from app.exchanges._stub import StubExchangeAdapter


class GateAdapter(StubExchangeAdapter):
    exchange = Exchange.GATE
