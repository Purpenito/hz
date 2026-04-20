from datetime import datetime, timedelta

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.storage.models import SentSignalORM


class SentSignalsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def exists_recent(self, user_id: int, signal_key: str, ttl_sec: int) -> bool:
        threshold = datetime.utcnow() - timedelta(seconds=ttl_sec)
        q = select(SentSignalORM).where(
            SentSignalORM.user_id == user_id,
            SentSignalORM.signal_key == signal_key,
            SentSignalORM.sent_at >= threshold,
        )
        return (await self.session.execute(q)).scalar_one_or_none() is not None

    async def add(self, user_id: int, signal_key: str, symbol: str, arbitrage_type: str, long_exchange: str, short_exchange: str) -> None:
        self.session.add(
            SentSignalORM(
                user_id=user_id,
                signal_key=signal_key,
                symbol=symbol,
                arbitrage_type=arbitrage_type,
                long_exchange=long_exchange,
                short_exchange=short_exchange,
            )
        )

    async def cleanup(self, older_than_days: int = 2) -> None:
        threshold = datetime.utcnow() - timedelta(days=older_than_days)
        await self.session.execute(delete(SentSignalORM).where(SentSignalORM.sent_at < threshold))
