from aiogram import Bot, Dispatcher, executor, types
import os

API_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Привіт! Я працюю!")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
