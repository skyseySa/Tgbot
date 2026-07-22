import asyncio
import os
import re
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
        # Проверяем, что админ отвечает на сообщение от бота
        if message.reply_to_message and message.reply_to_message.from_user.id == bot.id:
            # Ищем ID пользователя в тексте сообщения с помощью регулярного выражения
            match = re.search(r"🆔 ID:\s*(\d+)", message.reply_to_message.text or message.reply_to_message.caption or "")
            if match:
                user_id = int(match.group(1))
                try:
                    # Проверяем тип контента и пересылаем его пользователю
                    if message.text:
                        await bot.send_message(chat_id=user_id, text=message.text)
                    else:
                        await message.copy_to(chat_id=user_id)
                    await message.reply("✅ Ответ успешно отправлен пользователю!")
                except Exception as e:
                    await message.reply(f"❌ Не удалось отправить ответ. Ошибка: {e}")
                return

        await message.reply(
            "Чтобы ответить пользователю, сделайте 'Ответ' (Reply) "
            "именно на текстовую КАРТОЧКУ с данными пользователя."
        )
        return

    # ЛОГИКА ДЛЯ ПОЛЬЗОВАТЕЛЕЙ (ОТПРАВКА АДМИНУ)
    username = (
        f"@{message.from_user.username}"
        if message.from_user.username
        else "Нет username"
    )

    # Отправляем админу карточку с текстом пользователя (или уведомлением о медиа)
    user_text = message.text if message.text else f"[Отправлен медиафайл/стикер]"
    
    # Отправляем ОДНО сообщение админу, в котором есть и данные, и текст человека
    await bot.send_message(
        ADMIN_ID,
        f"📩 *Новое сообщение*\n\n"
        f"👤 *Имя:* {message.from_user.full_name}\n"
        f"🔗 *Username:* {username}\n"
        f"🆔 ID: {message.from_user.id}\n\n"  # Тэг ID важен, код ищет его
        f"📝 *Текст:* {user_text}",
        parse_mode="Markdown"
    )

    # Если пользователь прислал фото/документ, просто дублируем его админу отдельно
    if not message.text:
        await message.copy_to(chat_id=ADMIN_ID)

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
