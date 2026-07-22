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
    # ЛОГИКА ДЛЯ АДМИНИСТРАТОРА (ОТВЕТ ПОЛЬЗОВАТЕЛЮ)
    if message.chat.id == ADMIN_ID:
        # Проверяем, что админ ответил на пересланное сообщение
        if message.reply_to_message and message.reply_to_message.forward_from:
            user_id = message.reply_to_message.forward_from.id
            try:
                # Отправляем текст админа пользователю
                await bot.send_message(chat_id=user_id, text=message.text)
                await message.reply("✅ Ответ успешно отправлен пользователю!")
            except Exception as e:
                await message.reply(f"❌ Не удалось отправить ответ. Ошибка: {e}")
        else:
            await message.reply(
                "Чтобы ответить пользователю, сделайте 'Ответ' (Reply) "
                "на пересланное ботом сообщение."
            )
        return

    # ЛОГИКА ДЛЯ ПОЛЬЗОВАТЕЛЕЙ (ОТПРАВКА АДМИНУ)
    username = (
        f"@{message.from_user.username}"
        if message.from_user.username
        else "Нет username"
    )

    # Карточка для админа (ссылку на чат убрали, оставили только данные)
    await bot.send_message(
        ADMIN_ID,
        f"📩 *Новое сообщение*\n\n"
        f"👤 *Имя:* {message.from_user.full_name}\n"
        f"🔗 *Username:* {username}\n"
        f"🆔 *ID:* {message.from_user.id}",
        parse_mode="Markdown"
    )

    # Пересылаем сообщение админу (ВАЖНО: используется forward, чтобы работал reply_to_message.forward_from)
    await bot.forward_message(
        chat_id=ADMIN_ID,
        from_chat_id=message.chat.id,
        message_id=message.message_id,
    )

    # Отвечаем пользователю
    await message.answer("⏱ Сообщение отправлено! Владелец ответит вам в ближайшее время.")


# Веб-сервер для Render
async def handle(request):
    return web.Response(text="Бот успешно работает!")


async def main():
    print("Бот запускается...")

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
