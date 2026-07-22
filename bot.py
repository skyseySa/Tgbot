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


# Функция для безопасной очистки текста от ломающих HTML-тегов
def clean_html(text: str) -> str:
    if not text:
        return ""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


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
        if message.reply_to_message and message.reply_to_message.from_user.id == bot.id:
            match = re.search(r"🆔 ID:\s*(\d+)", message.reply_to_message.text or message.reply_to_message.caption or "")
            if match:
                user_id = int(match.group(1))
                try:
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
    
    # 1. ПЕРВЫМ ДЕЛОМ отвечаем пользователю, чтобы он точно видел, что бот работает
    await message.answer("⏱ Сообщение отправлено! Владелец ответит вам в ближайшее время.")

    # 2. Безопасно подготавливаем данные (экранируем HTML-символы)
    user_name = clean_html(message.from_user.full_name)
    username = f"@{message.from_user.username}" if message.from_user.username else "Нет username"
    username = clean_html(username)

    if message.text:
        user_text = clean_html(message.text)
    elif message.caption:
        user_text = f"Медиафайл с подписью: {clean_html(message.caption)}"
    else:
        user_text = "Отправлен медиафайл, стикер или голосовое"

    # 3. Отправляем карточку админу внутри try-except, чтобы бот не падал при любых ошибках
    try:
        await bot.send_message(
            ADMIN_ID,
            f"📩 <b>Новое сообщение</b>\n\n"
            f"👤 <b>Имя:</b> {user_name}\n"
            f"🔗 <b>Username:</b> {username}\n"
            f"🆔 ID: {message.from_user.id}\n\n"
            f"📝 <b>Текст:</b> {user_text}",
            parse_mode="HTML"
        )

        # Если это медиафайл, дублируем его админу отдельно
        if not message.text:
            await message.copy_to(chat_id=ADMIN_ID)
            
    except Exception as admin_err:
        # Если карточка не отправилась админу, отправляем хотя бы чистое уведомление без разметки
        print(f"Ошибка отправки админу: {admin_err}")
        await bot.send_message(
            ADMIN_ID,
            f"📩 Новое сообщение (сбой разметки)\n"
            f"ID: {message.from_user.id}\n"
            f"Пользователь прислал текст или медиа, используйте Reply для ответа."
        )
        await message.copy_to(chat_id=ADMIN_ID)


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
