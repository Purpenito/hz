class ArbitrageBotError(Exception):
    """Base domain exception."""


class ExchangeAdapterError(ArbitrageBotError):
    """Raised when exchange adapter cannot serve data."""
