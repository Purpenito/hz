from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def start_keyboard(notifications_enabled: bool) -> InlineKeyboardMarkup:
    status = "✅" if notifications_enabled else "❌"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"Уведомления {status}", callback_data="toggle_notifications")],
            [InlineKeyboardButton(text="Настройки", callback_data="open_settings")],
        ]
    )
