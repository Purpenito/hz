from app.core.enums import Exchange


class VolumeStore:
    def __init__(self) -> None:
        self._data: dict[tuple[Exchange, str], float] = {}

    def put(self, exchange: Exchange, symbol: str, volume: float) -> None:
        self._data[(exchange, symbol)] = volume

    def get(self, exchange: Exchange, symbol: str) -> float:
        return self._data.get((exchange, symbol), 0.0)
