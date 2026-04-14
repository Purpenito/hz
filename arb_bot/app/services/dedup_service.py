from sqlalchemy.ext.asyncio import AsyncSession

from app.arbitrage.signal_builder import dedup_key
from app.core.models import ArbitrageSignal
from app.storage.repositories.sent_signals import SentSignalsRepository


class DedupService:
    def __init__(self, session: AsyncSession, ttl_sec: int = 180) -> None:
        self.repo = SentSignalsRepository(session)
        self.ttl_sec = ttl_sec

    async def should_send(self, user_id: int, signal: ArbitrageSignal) -> bool:
        key = dedup_key(signal, user_id)
        exists = await self.repo.exists_recent(user_id=user_id, signal_key=key, ttl_sec=self.ttl_sec)
        return not exists

    async def mark_sent(self, user_id: int, signal: ArbitrageSignal) -> None:
        key = dedup_key(signal, user_id)
        await self.repo.add(
            user_id=user_id,
            signal_key=key,
            symbol=signal.symbol,
            arbitrage_type=signal.arbitrage_type.value,
            long_exchange=signal.long_exchange.value,
            short_exchange=signal.short_exchange.value,
        )
