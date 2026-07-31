import asyncio
from flask import Flask
import threading
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 8853421640

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def start_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 НАЧАТЬ ОБУЧЕНИЕ", callback_data="start_click")]
    ])
    return keyboard

@dp.callback_query(lambda c: c.data == "start_click")
async def process_start_button(callback_query: types.CallbackQuery):
    user = callback_query.from_user
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(
        callback_query.from_user.id,
        "Отлично! Начинаем погружение в мир анализа и заработка!\n\n"
        "Теперь вы можете задать мне любой вопрос, и я отвечу вам как можно скорее."
    )
    await bot.send_message(
        ADMIN_ID,
        f"👤 Новый пользователь нажал кнопку 'НАЧАТЬ'!\n"
        f"🆔 ID: {user.id}\n"
        f"👤 Имя: {user.full_name}\n"
        f"📛 Username: @{user.username if user.username else 'не указан'}"
    )

@dp.message(Command("start"))
async def start(message: types.Message):
    user = message.from_user
    await bot.send_message(
        chat_id=message.chat.id,
        text="<b>Добро пожаловать!</b>\n\nЧтобы начать общение, нажмите кнопку ниже 👇",
        parse_mode="HTML",
        reply_markup=start_keyboard()
    )
    await bot.send_message(
        ADMIN_ID,
        f"👤 Пользователь ввел команду /start\n"
        f"🆔 ID: {user.id}\n"
        f"👤 Имя: {user.full_name}\n"
        f"📛 Username: @{user.username if user.username else 'не указан'}"
    )

last_user_id = None

@dp.message()
async def handle_message(message: types.Message):
    global last_user_id
    user_id = message.from_user.id

    if user_id == ADMIN_ID:
        if message.reply_to_message:
            original = message.reply_to_message
            target_user_id = None

            if original.forward_from:
                target_user_id = original.forward_from.id
            elif original.forward_from_chat:
                target_user_id = original.forward_from_chat.id
            else:
                import re
                match = re.search(r"🆔 ID: (\d+)", original.text or "")
                if match:
                    target_user_id = int(match.group(1))
                elif last_user_id:
                    target_user_id = last_user_id

            if target_user_id:
                try:
                    await bot.send_message(
                        target_user_id,
                        f"📩 Ответ от администратора:\n\n{message.text}"
                    )
                    await message.answer(f"✅ Ответ отправлен пользователю (ID: {target_user_id})")
                except Exception as e:
                    await message.answer(f"❌ Ошибка: {e}")
            else:
                await message.answer("❌ Не могу найти пользователя для ответа.")
            return

        if last_user_id:
            try:
                await bot.send_message(
                    last_user_id,
                    f"📩 Ответ от администратора:\n\n{message.text}"
                )
                await message.answer(f"✅ Ответ отправлен последнему пользователю (ID: {last_user_id})")
            except Exception as e:
                await message.answer(f"❌ Ошибка: {e}")
        else:
            await message.answer("ℹ️ Нет активных пользователей.")
        return

    last_user_id = user_id

    try:
        await bot.forward_message(ADMIN_ID, user_id, message.message_id)
        await bot.send_message(
            ADMIN_ID,
            f"👤 Пользователь: {message.from_user.full_name}\n"
            f"🆔 ID: {user_id}\n"
            f"📝 Текст: {message.text or 'не текстовое сообщение'}"
        )
        await message.answer("✅ Ваше сообщение отправлено администратору!")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

def run_bot():
    asyncio.run(dp.start_polling(bot))

app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Бот работает!"

@app.route('/health')
def health():
    return "OK"

if __name__ == "__main__":
    # ЗАПУСКАЕМ БОТА В ОТДЕЛЬНОМ ПОТОКЕ
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # ЗАПУСКАЕМ Flask
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
