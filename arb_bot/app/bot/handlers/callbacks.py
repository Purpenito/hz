from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery

from app.bot.keyboards.start import start_keyboard
from app.bot.utils import next_notifications_state

router = Router()


@router.callback_query(lambda c: c.data == "toggle_notifications")
async def toggle_notifications(callback: CallbackQuery) -> None:
    if callback.message:
        current_text = None
        if callback.message.reply_markup and callback.message.reply_markup.inline_keyboard:
            current_text = callback.message.reply_markup.inline_keyboard[0][0].text

        enabled = next_notifications_state(current_text)
        try:
            await callback.message.edit_reply_markup(
                reply_markup=start_keyboard(notifications_enabled=enabled)
            )
        except TelegramBadRequest as exc:
            if "message is not modified" not in str(exc):
                raise
    await callback.answer("Статус уведомлений обновлён")
