import json

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import ArbitrageType, Exchange
from app.core.models import UserSettings
from app.storage.repositories.settings import UserSettingsRepository
from app.storage.repositories.users import UsersRepository


class UserSettingsService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.users_repo = UsersRepository(session)
        self.settings_repo = UserSettingsRepository(session)

    async def _get_or_create_orm(self, telegram_user_id: int):
        user = await self.users_repo.get_or_create(telegram_user_id)
        settings = await self.settings_repo.get_by_user_id(user.id)
        if settings is None:
            settings = await self.settings_repo.create_default(user.id)
            await self.session.commit()
        return user, settings

    async def get_or_create_for_telegram_user(self, telegram_user_id: int) -> UserSettings:
        _, settings = await self._get_or_create_orm(telegram_user_id)
        return self.settings_repo.to_domain(settings, telegram_user_id)

    async def list_all(self) -> list[UserSettings]:
        users = await self.users_repo.list_all()
        items: list[UserSettings] = []
        for user in users:
            settings = await self.settings_repo.get_by_user_id(user.id)
            if settings is None:
                settings = await self.settings_repo.create_default(user.id)
            items.append(self.settings_repo.to_domain(settings, user.telegram_user_id))
        await self.session.commit()
        return items

    async def set_notifications_enabled(self, telegram_user_id: int, enabled: bool) -> UserSettings:
        _, settings = await self._get_or_create_orm(telegram_user_id)
        settings.notifications_enabled = enabled
        await self.session.commit()
        await self.session.refresh(settings)
        return self.settings_repo.to_domain(settings, telegram_user_id)

    async def toggle_exchange(self, telegram_user_id: int, exchange: Exchange) -> UserSettings:
        _, settings = await self._get_or_create_orm(telegram_user_id)
        current = set(json.loads(settings.enabled_exchanges_json))
        if exchange.value in current:
            if len(current) > 1:
                current.remove(exchange.value)
        else:
            current.add(exchange.value)
        settings.enabled_exchanges_json = json.dumps(sorted(current))
        await self.session.commit()
        await self.session.refresh(settings)
        return self.settings_repo.to_domain(settings, telegram_user_id)

    async def toggle_arbitrage_type(self, telegram_user_id: int, arb_type: ArbitrageType) -> UserSettings:
        _, settings = await self._get_or_create_orm(telegram_user_id)
        current = set(json.loads(settings.enabled_arbitrage_types_json))
        if arb_type.value in current:
            if len(current) > 1:
                current.remove(arb_type.value)
        else:
            current.add(arb_type.value)
        settings.enabled_arbitrage_types_json = json.dumps(sorted(current))
        await self.session.commit()
        await self.session.refresh(settings)
        return self.settings_repo.to_domain(settings, telegram_user_id)

    async def set_numeric_setting(self, telegram_user_id: int, key: str, value: float | int) -> UserSettings:
        _, settings = await self._get_or_create_orm(telegram_user_id)
        allowed = {
            "min_profit_pct",
            "min_volume_24h",
            "capital_usdt",
            "min_executable_ratio_pct",
            "max_signal_age_ms",
        }
        if key not in allowed:
            raise ValueError(f"Unsupported setting key: {key}")
        setattr(settings, key, value)
        await self.session.commit()
        await self.session.refresh(settings)
        return self.settings_repo.to_domain(settings, telegram_user_id)
