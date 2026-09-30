import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from dotenv import load_dotenv

from keyboards import admin_keyboard
from channels import router as channels_router
from messages import router as messages_router
from services.ChannelService import ChannelService
from services.MessageService import MessageService
from services.TelegramService import TelegramService

load_dotenv()
logging.basicConfig(level=logging.INFO)

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

tg_service = TelegramService(API_ID, API_HASH)
channel_service = ChannelService()
message_service = MessageService()

# Подключаем роутеры
dp.include_router(channels_router)
dp.include_router(messages_router)


# ----------------------------------------------------------------------
# /start
# ----------------------------------------------------------------------

@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Панель управления рассылками:", reply_markup=admin_keyboard())


# ----------------------------------------------------------------------
# Запуск
# ----------------------------------------------------------------------

async def main():
    await tg_service.start()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(
        bot,
        tg_service=tg_service,
        channel_service=channel_service,
        message_service=message_service,
    )


if __name__ == "__main__":
    asyncio.run(main())

