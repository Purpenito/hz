from app.core.enums import Exchange
from app.core.models import FundingInfo


class FundingStore:
    def __init__(self) -> None:
        self._data: dict[tuple[Exchange, str], FundingInfo] = {}

    def put(self, funding: FundingInfo) -> None:
        self._data[(funding.exchange, funding.symbol)] = funding

    def get(self, exchange: Exchange, symbol: str) -> FundingInfo | None:
        return self._data.get((exchange, symbol))
