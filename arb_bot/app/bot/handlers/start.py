from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.bot.keyboards.start import start_keyboard

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message) -> None:
    await message.answer(
        "Добро пожаловать в арбитраж-бота. Управляйте уведомлениями и настройками ниже.",
        reply_markup=start_keyboard(notifications_enabled=True),
    )
