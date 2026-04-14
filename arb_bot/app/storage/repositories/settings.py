import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import ArbitrageType, Exchange
from app.core.models import UserSettings
from app.storage.models import UserSettingsORM


class UserSettingsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_user_id(self, user_id: int) -> UserSettingsORM | None:
        result = await self.session.execute(select(UserSettingsORM).where(UserSettingsORM.user_id == user_id))
        return result.scalar_one_or_none()

    async def create_default(self, user_id: int) -> UserSettingsORM:
        item = UserSettingsORM(
            user_id=user_id,
            enabled_exchanges_json=json.dumps([Exchange.BYBIT.value, Exchange.KUCOIN.value]),
            enabled_arbitrage_types_json=json.dumps([
                ArbitrageType.FUTURES_FUTURES.value,
                ArbitrageType.FUNDING.value,
            ]),
        )
        self.session.add(item)
        await self.session.flush()
        return item

    @staticmethod
    def to_domain(orm: UserSettingsORM, telegram_user_id: int) -> UserSettings:
        return UserSettings(
            telegram_user_id=telegram_user_id,
            notifications_enabled=orm.notifications_enabled,
            enabled_exchanges=[Exchange(x) for x in json.loads(orm.enabled_exchanges_json)],
            enabled_arbitrage_types=[ArbitrageType(x) for x in json.loads(orm.enabled_arbitrage_types_json)],
            min_profit_pct=orm.min_profit_pct,
            min_volume_24h=orm.min_volume_24h,
            capital_usdt=orm.capital_usdt,
            min_executable_ratio_pct=orm.min_executable_ratio_pct,
            max_signal_age_ms=orm.max_signal_age_ms,
        )
