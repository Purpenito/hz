from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery

from app.bot.keyboards.settings import (
    arbitrage_types_keyboard,
    exchanges_keyboard,
    numeric_options_keyboard,
    settings_keyboard,
)
from app.bot.keyboards.start import start_keyboard
from app.core.enums import ArbitrageType, Exchange
from app.services.user_settings_service import UserSettingsService
from app.storage.db import SessionLocal

router = Router()

NUMERIC_CONFIGS = {
    "min_profit_pct": {
        "title": "Минимальный профит (%)",
        "options": ["0.1", "0.3", "0.5", "1.0", "2.0"],
        "cast": float,
    },
    "min_volume_24h": {
        "title": "Минимальный 24ч объём (USDT)",
        "options": ["100000", "500000", "1000000", "5000000"],
        "cast": float,
    },
    "capital_usdt": {
        "title": "Капитал (USDT)",
        "options": ["50", "100", "500", "1000", "5000"],
        "cast": float,
    },
    "min_executable_ratio_pct": {
        "title": "Минимальная исполнимость (%)",
        "options": ["30", "50", "70", "90"],
        "cast": float,
    },
    "max_signal_age_ms": {
        "title": "Максимальный возраст сигнала (мс)",
        "options": ["3000", "5000", "10000", "30000"],
        "cast": int,
    },
}

MENU_TO_KEY = {
    "settings_min_profit": "min_profit_pct",
    "settings_min_volume": "min_volume_24h",
    "settings_capital": "capital_usdt",
    "settings_min_exec": "min_executable_ratio_pct",
    "settings_max_age": "max_signal_age_ms",
}


async def _safe_edit_text(callback: CallbackQuery, text: str, reply_markup) -> None:
    if not callback.message:
        return
    try:
        await callback.message.edit_text(text, reply_markup=reply_markup)
    except TelegramBadRequest as exc:
        if "message is not modified" not in str(exc):
            raise


async def _safe_edit_markup(callback: CallbackQuery, reply_markup) -> None:
    if not callback.message:
        return
    try:
        await callback.message.edit_reply_markup(reply_markup=reply_markup)
    except TelegramBadRequest as exc:
        if "message is not modified" not in str(exc):
            raise


async def _load_settings(telegram_user_id: int):
    async with SessionLocal() as session:
        return await UserSettingsService(session).get_or_create_for_telegram_user(telegram_user_id)


@router.callback_query(lambda c: c.data == "open_settings")
async def open_settings(callback: CallbackQuery) -> None:
    await _safe_edit_text(callback, "Меню настроек", settings_keyboard())
    await callback.answer()


@router.callback_query(lambda c: c.data == "settings_exchanges")
async def settings_exchanges(callback: CallbackQuery) -> None:
    settings = await _load_settings(callback.from_user.id)
    await _safe_edit_text(
        callback,
        "Опросимые биржи (нажмите для переключения):",
        exchanges_keyboard(settings),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data == "settings_arb_types")
async def settings_arb_types(callback: CallbackQuery) -> None:
    settings = await _load_settings(callback.from_user.id)
    await _safe_edit_text(
        callback,
        "Типы арбитража (нажмите для переключения):",
        arbitrage_types_keyboard(settings),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data and c.data.startswith("toggle_exchange:"))
async def toggle_exchange(callback: CallbackQuery) -> None:
    exchange_value = callback.data.split(":", maxsplit=1)[1]
    exchange = Exchange(exchange_value)

    async with SessionLocal() as session:
        settings = await UserSettingsService(session).toggle_exchange(callback.from_user.id, exchange)

    await _safe_edit_markup(callback, exchanges_keyboard(settings))
    await callback.answer(f"{exchange.value.upper()} обновлено")


@router.callback_query(lambda c: c.data and c.data.startswith("toggle_arb_type:"))
async def toggle_arb_type(callback: CallbackQuery) -> None:
    arb_value = callback.data.split(":", maxsplit=1)[1]
    arb_type = ArbitrageType(arb_value)

    async with SessionLocal() as session:
        settings = await UserSettingsService(session).toggle_arbitrage_type(
            callback.from_user.id, arb_type
        )

    await _safe_edit_markup(callback, arbitrage_types_keyboard(settings))
    await callback.answer(f"{arb_type.value} обновлён")


@router.callback_query(lambda c: c.data in MENU_TO_KEY)
async def settings_numeric_menu(callback: CallbackQuery) -> None:
    key = MENU_TO_KEY[callback.data]
    config = NUMERIC_CONFIGS[key]
    await _safe_edit_text(
        callback,
        f"{config['title']}\nВыберите значение:",
        numeric_options_keyboard(key, config["options"]),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data and c.data.startswith("set_value:"))
async def settings_set_value(callback: CallbackQuery) -> None:
    _, key, value_raw = callback.data.split(":", maxsplit=2)
    config = NUMERIC_CONFIGS.get(key)
    if not config:
        await callback.answer("Неизвестный параметр", show_alert=True)
        return

    cast = config["cast"]
    value = cast(value_raw)

    async with SessionLocal() as session:
        await UserSettingsService(session).set_numeric_setting(callback.from_user.id, key, value)

    await callback.answer(f"Сохранено: {config['title']} = {value_raw}")


@router.callback_query(lambda c: c.data == "settings_back")
async def settings_back(callback: CallbackQuery) -> None:
    settings = await _load_settings(callback.from_user.id)
    await _safe_edit_text(
        callback,
        "Главное меню",
        start_keyboard(notifications_enabled=settings.notifications_enabled),
    )
    await callback.answer()
