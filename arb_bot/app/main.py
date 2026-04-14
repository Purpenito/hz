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
from app.services.scanner_service import ScannerService

settings_cfg = get_settings()
setup_logging(settings_cfg.log_level)
logger = logging.getLogger(__name__)

fastapi_app = FastAPI(title=settings_cfg.app_name)


@fastapi_app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


async def scanner_loop(scanner: ScannerService) -> None:
    while True:
        try:
            await scanner.refresh_market_data(depth=10)
            logger.info("scanner refresh completed")
        except Exception:
            logger.exception("scanner refresh failed")
        await asyncio.sleep(settings_cfg.scanner_interval_sec)


async def run_bot() -> None:
    if not settings_cfg.telegram_bot_token:
        logger.warning("TELEGRAM_BOT_TOKEN is empty; bot polling skipped")
        return

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

    asyncio.create_task(scanner_loop(scanner))
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(run_bot())
