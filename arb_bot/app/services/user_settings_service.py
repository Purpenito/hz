from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models import UserSettings
from app.storage.repositories.settings import UserSettingsRepository
from app.storage.repositories.users import UsersRepository


class UserSettingsService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.users_repo = UsersRepository(session)
        self.settings_repo = UserSettingsRepository(session)

    async def get_or_create_for_telegram_user(self, telegram_user_id: int) -> UserSettings:
        user = await self.users_repo.get_or_create(telegram_user_id)
        settings = await self.settings_repo.get_by_user_id(user.id)
        if settings is None:
            settings = await self.settings_repo.create_default(user.id)
            await self.session.commit()
        return self.settings_repo.to_domain(settings, telegram_user_id)
