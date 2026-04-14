from aiogram import Router
from aiogram.types import CallbackQuery

from app.bot.keyboards.settings import settings_keyboard

router = Router()


@router.callback_query(lambda c: c.data == "open_settings")
async def open_settings(callback: CallbackQuery) -> None:
    if callback.message:
        await callback.message.delete()
        await callback.message.answer("Меню настроек", reply_markup=settings_keyboard())
    await callback.answer()
