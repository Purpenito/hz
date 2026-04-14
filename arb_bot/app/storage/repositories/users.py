from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.storage.models import UserORM


class UsersRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_or_create(self, telegram_user_id: int) -> UserORM:
        result = await self.session.execute(
            select(UserORM).where(UserORM.telegram_user_id == telegram_user_id)
        )
        user = result.scalar_one_or_none()
        if user:
            return user
        user = UserORM(telegram_user_id=telegram_user_id)
        self.session.add(user)
        await self.session.flush()
        return user
