from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.core.enums import ArbitrageType, Exchange
from app.core.models import UserSettings


def settings_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Опросимые биржи", callback_data="settings_exchanges")],
            [InlineKeyboardButton(text="Минимальный профит", callback_data="settings_min_profit")],
            [InlineKeyboardButton(text="Объём 24ч", callback_data="settings_min_volume")],
            [InlineKeyboardButton(text="Тип арбитража", callback_data="settings_arb_types")],
            [InlineKeyboardButton(text="Капитал", callback_data="settings_capital")],
            [InlineKeyboardButton(text="Минимальная исполнимость", callback_data="settings_min_exec")],
            [InlineKeyboardButton(text="Макс. возраст сигнала", callback_data="settings_max_age")],
            [InlineKeyboardButton(text="Назад", callback_data="settings_back")],
        ]
    )


def exchanges_keyboard(settings: UserSettings) -> InlineKeyboardMarkup:
    rows = []
    for exchange in Exchange:
        status = "✅" if exchange in settings.enabled_exchanges else "❌"
        rows.append([
            InlineKeyboardButton(
                text=f"{exchange.value.upper()} {status}",
                callback_data=f"toggle_exchange:{exchange.value}",
            )
        ])
    rows.append([InlineKeyboardButton(text="Назад", callback_data="open_settings")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def arbitrage_types_keyboard(settings: UserSettings) -> InlineKeyboardMarkup:
    rows = []
    for arb_type in ArbitrageType:
        status = "✅" if arb_type in settings.enabled_arbitrage_types else "❌"
        rows.append([
            InlineKeyboardButton(
                text=f"{arb_type.value} {status}",
                callback_data=f"toggle_arb_type:{arb_type.value}",
            )
        ])
    rows.append([InlineKeyboardButton(text="Назад", callback_data="open_settings")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def numeric_options_keyboard(key: str, options: list[str]) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=option, callback_data=f"set_value:{key}:{option}")]
        for option in options
    ]
    rows.append([InlineKeyboardButton(text="Назад", callback_data="open_settings")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
