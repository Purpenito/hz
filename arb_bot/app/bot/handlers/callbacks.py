from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery

from app.bot.keyboards.start import start_keyboard
from app.bot.utils import next_notifications_state
from app.services.user_settings_service import UserSettingsService
from app.storage.db import SessionLocal

router = Router()


@router.callback_query(lambda c: c.data == "toggle_notifications")
async def toggle_notifications(callback: CallbackQuery) -> None:
    if callback.message:
        current_text = None
        if callback.message.reply_markup and callback.message.reply_markup.inline_keyboard:
            current_text = callback.message.reply_markup.inline_keyboard[0][0].text

        enabled = next_notifications_state(current_text)

        async with SessionLocal() as session:
            settings = await UserSettingsService(session).set_notifications_enabled(
                callback.from_user.id, enabled
            )

        try:
            await callback.message.edit_reply_markup(
                reply_markup=start_keyboard(notifications_enabled=settings.notifications_enabled)
            )
        except TelegramBadRequest as exc:
            if "message is not modified" not in str(exc):
                raise
    await callback.answer("Статус уведомлений обновлён")
