from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import os

BOT_TOKEN = os.getenv("BOT_TOKEN") or "YOUR_BOT_TOKEN"

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

class OrderForm(StatesGroup):
    city = State()
    vin = State()
    dlink = State()
    lang = State()
    comment = State()
    confirm = State()

DLINK_VERSIONS = ["Dlink 3", "Dlink 4", "Dlink 5"]
LANG_OPTIONS = ["UA", "RU"]

@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    await message.answer("Введіть місто:")
    await OrderForm.city.set()

@dp.message_handler(state=OrderForm.city)
async def set_city(message: types.Message, state: FSMContext):
    await state.update_data(city=message.text)
    await message.answer("Введіть VIN код:")
    await OrderForm.vin.set()

@dp.message_handler(state=OrderForm.vin)
async def set_vin(message: types.Message, state: FSMContext):
    await state.update_data(vin=message.text)
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(*DLINK_VERSIONS)
    await message.answer("Оберіть версію Dlink:", reply_markup=kb)
    await OrderForm.dlink.set()

@dp.message_handler(state=OrderForm.dlink)
async def set_dlink(message: types.Message, state: FSMContext):
    if message.text not in DLINK_VERSIONS:
        return await message.answer("Будь ласка, оберіть версію Dlink з клавіатури.")
    await state.update_data(dlink=message.text)
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True).add("UA", "RU")
    await message.answer("Оберіть мову мультимедіа:", reply_markup=kb)
    await OrderForm.lang.set()

@dp.message_handler(state=OrderForm.lang)
async def set_lang(message: types.Message, state: FSMContext):
    if message.text not in LANG_OPTIONS:
        return await message.answer("Будь ласка, оберіть UA або RU.")
    await state.update_data(lang=message.text)
    await message.answer("Додайте коментар (або напишіть 'немає'):", reply_markup=types.ReplyKeyboardRemove())
    await OrderForm.comment.set()

@dp.message_handler(state=OrderForm.comment)
async def set_comment(message: types.Message, state: FSMContext):
    await state.update_data(comment=message.text)
    data = await state.get_data()
    summary = (
        f"📝 Заявка:\n"
        f"📍 Місто: {data['city']}\n"
        f"🚗 VIN: {data['vin']}\n"
        f"💾 Dlink: {data['dlink']}\n"
        f"🗣️ Мова: {data['lang']}\n"
        f"💬 Коментар: {data['comment']}"
    )
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True).add("Підтвердити", "Скасувати")
    await message.answer(summary + "\n\nПідтвердити заявку?", reply_markup=kb)
    await OrderForm.confirm.set()

@dp.message_handler(state=OrderForm.confirm)
async def confirm(message: types.Message, state: FSMContext):
    if message.text == "Підтвердити":
        await message.answer("✅ Заявка прийнята!", reply_markup=types.ReplyKeyboardRemove())
    else:
        await message.answer("❌ Заявка скасована.", reply_markup=types.ReplyKeyboardRemove())
    await state.finish()

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)