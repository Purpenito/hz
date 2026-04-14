from app.core.enums import Exchange


class ExchangeStateService:
    def __init__(self) -> None:
        self._status: dict[Exchange, bool] = {exchange: True for exchange in Exchange}

    def set_status(self, exchange: Exchange, is_ok: bool) -> None:
        self._status[exchange] = is_ok

    def is_available(self, exchange: Exchange) -> bool:
        return self._status.get(exchange, False)
