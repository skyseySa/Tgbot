import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message

import os

TOKEN = os.getenv("TOKEN")
ADMIN_ID = 6254922733

dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "👋 Привет!\n"
        "Напиши мне сообщение, и я передам его владельцу."
    )


@dp.message()
async def messages(message: Message):
    if message.chat.id == ADMIN_ID:
        return

    username = (
        f"@{message.from_user.username}"
        if message.from_user.username
        else "Нет username"
    )

    await bot.send_message(
        ADMIN_ID,
        f"""📩 Новое сообщение

👤 Имя: {message.from_user.full_name}
🔗 Username: {username}
🆔 ID: {message.from_user.id}
"""
    )

    await bot.forward_message(
        chat_id=ADMIN_ID,
        from_chat_id=message.chat.id,
        message_id=message.message_id,
    )
