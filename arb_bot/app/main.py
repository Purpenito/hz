import asyncio
import logging

from aiogram import Bot, Dispatcher
from fastapi import FastAPI

from app.bot.handlers import callbacks, settings, start
from app.config.logging import setup_logging
from app.config.settings import get_settings
from app.exchanges.bingx import BingxAdapter
from app.exchanges.bybit import BybitAdapter
from app.exchanges.gate import GateAdapter
from app.exchanges.kucoin import KucoinAdapter
from app.exchanges.okx import OkxAdapter
from app.exchanges.registry import ExchangeRegistry
from app.market_data.funding import FundingStore
from app.market_data.orderbooks import OrderBookStore
from app.market_data.symbols import SymbolsStore
from app.market_data.volumes import VolumeStore
from app.services.dedup_service import DedupService
from app.services.notifier_service import NotifierService
from app.services.scanner_service import ScannerService
from app.services.user_settings_service import UserSettingsService
from app.storage.db import SessionLocal
from app.storage.init_db import ensure_schema

settings_cfg = get_settings()
setup_logging(settings_cfg.log_level)
logger = logging.getLogger(__name__)

fastapi_app = FastAPI(title=settings_cfg.app_name)


@fastapi_app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


async def scanner_loop(scanner: ScannerService, bot: Bot) -> None:
    notifier = NotifierService(bot)
    while True:
        try:
            await scanner.refresh_market_data(depth=10)

            async with SessionLocal() as session:
                settings_service = UserSettingsService(session)
                dedup_service = DedupService(session)
                users = await settings_service.list_all()
                total_sent = 0

                for user_settings in users:
                    if not user_settings.notifications_enabled:
                        continue
                    signals = await scanner.scan(user_settings)
                    for signal in signals:
                        if await dedup_service.should_send(user_settings.telegram_user_id, signal):
                            await notifier.send_signal(user_settings.telegram_user_id, signal)
                            await dedup_service.mark_sent(user_settings.telegram_user_id, signal)
                            total_sent += 1

                await session.commit()
                logger.info(
                    "scanner refresh completed; users=%s sent=%s",
                    len(users),
                    total_sent,
                )
        except Exception:
            logger.exception("scanner loop failed")
        await asyncio.sleep(settings_cfg.scanner_interval_sec)


async def run_bot() -> None:
    if not settings_cfg.telegram_bot_token:
        logger.warning("TELEGRAM_BOT_TOKEN is empty; bot polling skipped")
        return

    await ensure_schema()

    bot = Bot(token=settings_cfg.telegram_bot_token)
    dp = Dispatcher()
    dp.include_router(start.router)
    dp.include_router(settings.router)
    dp.include_router(callbacks.router)

    registry = ExchangeRegistry(
        adapters=[BybitAdapter(), KucoinAdapter(), OkxAdapter(), GateAdapter(), BingxAdapter()]
    )
    scanner = ScannerService(
        registry=registry,
        symbols_store=SymbolsStore(),
        orderbook_store=OrderBookStore(),
        funding_store=FundingStore(),
        volume_store=VolumeStore(),
    )

    asyncio.create_task(scanner_loop(scanner, bot))
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(run_bot())
