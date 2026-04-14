from aiogram import Bot

from app.bot.formatters.signals import format_signal_text
from app.core.models import ArbitrageSignal


class NotifierService:
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    async def send_signal(self, telegram_user_id: int, signal: ArbitrageSignal) -> None:
        await self.bot.send_message(chat_id=telegram_user_id, text=format_signal_text(signal), disable_web_page_preview=True)
