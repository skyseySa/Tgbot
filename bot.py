import asyncio
import os
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiohttp import web

TOKEN = os.getenv("TOKEN")
ADMIN_ID = 6254922733

bot = Bot(TOKEN)
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


# Добавляем веб-сервер для Render, чтобы он не усыплял бота
async def handle(request):
    return web.Response(text="Бот успешно работает!")


async def main():
    print("Бот запускается...")

    # Создаем мини веб-сервер на порту 10000 (стандартный для Render)
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 10000)
    await site.start()

    print("Веб-сервер активен. Запускаем polling...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
