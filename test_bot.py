import asyncio
import os
from flask import Flask
import threading
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("✅ Привет! Бот работает!")

@dp.message()
async def echo(message: types.Message):
    await message.answer(f"✅ Ты написал: {message.text}")

def run_bot():
    asyncio.run(dp.start_polling(bot))

app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Бот работает!"

if __name__ == "__main__":
    # Запускаем бота в фоновом потоке
    thread = threading.Thread(target=run_bot, daemon=True)
    thread.start()
    
    # Запускаем Flask-сервер для Render
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)
