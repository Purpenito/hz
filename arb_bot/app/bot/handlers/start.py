from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.bot.keyboards.start import start_keyboard
from app.services.user_settings_service import UserSettingsService
from app.storage.db import SessionLocal

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message) -> None:
    async with SessionLocal() as session:
        settings = await UserSettingsService(session).get_or_create_for_telegram_user(message.from_user.id)

    await message.answer(
        "Добро пожаловать в арбитраж-бота. Управляйте уведомлениями и настройками ниже.",
        reply_markup=start_keyboard(notifications_enabled=settings.notifications_enabled),
    )
