from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery

from app.bot.keyboards.settings import (
    arbitrage_types_keyboard,
    exchanges_keyboard,
    settings_keyboard,
)
from app.bot.keyboards.start import start_keyboard
from app.core.enums import ArbitrageType, Exchange
from app.services.user_settings_service import UserSettingsService
from app.storage.db import SessionLocal

router = Router()

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


@router.callback_query(lambda c: c.data in {
    "settings_min_profit",
    "settings_min_volume",
    "settings_capital",
    "settings_min_exec",
    "settings_max_age",
})
async def settings_values_placeholder(callback: CallbackQuery) -> None:
    labels = {
        "settings_min_profit": "Минимальный профит",
        "settings_min_volume": "Объём 24ч",
        "settings_capital": "Капитал",
        "settings_min_exec": "Минимальная исполнимость",
        "settings_max_age": "Макс. возраст сигнала",
    }
    label = labels[callback.data]
    await callback.answer(
        f"{label}: экран ввода будет добавлен следующим шагом.",
        show_alert=True,
    )


@router.callback_query(lambda c: c.data == "settings_back")
async def settings_back(callback: CallbackQuery) -> None:
    settings = await _load_settings(callback.from_user.id)
    await _safe_edit_text(
        callback,
        "Главное меню",
        start_keyboard(notifications_enabled=settings.notifications_enabled),
    )
    await callback.answer()
