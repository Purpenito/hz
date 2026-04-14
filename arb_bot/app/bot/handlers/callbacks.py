from aiogram import Router
from aiogram.types import CallbackQuery

from app.bot.keyboards.start import start_keyboard

router = Router()


@router.callback_query(lambda c: c.data == "toggle_notifications")
async def toggle_notifications(callback: CallbackQuery) -> None:
    if callback.message:
        text = callback.message.text or ""
        enabled = "❌" in text
        await callback.message.edit_reply_markup(reply_markup=start_keyboard(notifications_enabled=enabled))
    await callback.answer("Статус уведомлений обновлён")
