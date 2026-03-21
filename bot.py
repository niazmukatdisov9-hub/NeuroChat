import asyncio
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from collections import deque

TELEGRAM_TOKEN = "8792752911:AAGEO-USE4lg-2BaqfoxDdE7skgXzCr7QHs"
CLOUDFLARE_API_KEY = "xwM3EhdP-fSx8hQONxjcrmQWn4lbgEUwTQqBzzhl"
ACCOUNT_ID = "76931ff53ab99e356450b9a6245d4378"

MODEL = "@cf/meta/llama-3-8b-instruct"

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# память пользователей (до 1000 сообщений)
user_memory = {}

# язык (просто хранится)
user_lang = {}

# статистика
user_stats = {}


# 🔹 запрос к AI
def ask_ai(messages):
    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/run/{MODEL}",
        headers=headers,
        json={"messages": messages}
    )

    result = response.json()
    return result["result"]["response"]


# 🚀 старт
@dp.message(Command("start"))
async def start(message: types.Message):
    user_id = message.from_user.id

    user_memory[user_id] = deque(maxlen=1000)
    user_lang[user_id] = "ru"
    user_stats[user_id] = 0

    await message.answer(
        "👋 Бот готов!\n\n"
        "/lang — смена языка\n"
        "/clear — очистить память\n"
        "/stats — статистика\n"
        "/help — помощь"
    )


# 📖 помощь
@dp.message(Command("help"))
async def help_cmd(message: types.Message):
    await message.answer(
        "📖 Команды:\n"
        "/lang — смена языка\n"
        "/clear — очистить память\n"
        "/stats — сколько сообщений отправил\n\n"
        "Просто пиши сообщение — я отвечу 🤖"
    )


# 🌍 смена языка
@dp.message(Command("lang"))
async def change_lang(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="Русский")],
            [types.KeyboardButton(text="English")]
        ],
        resize_keyboard=True
    )
    await message.answer("Выбери язык:", reply_markup=keyboard)


@dp.message(lambda msg: msg.text in ["Русский", "English"])
async def set_lang(message: types.Message):
    if message.text == "Русский":
        user_lang[message.from_user.id] = "ru"
        await message.answer("Язык установлен: Русский")
    else:
        user_lang[message.from_user.id] = "en"
        await message.answer("Language set: English")


# 🧹 очистка памяти
@dp.message(Command("clear"))
async def clear_memory(message: types.Message):
    user_memory[message.from_user.id] = deque(maxlen=1000)
    await message.answer("🧹 История очищена")


# 📊 статистика
@dp.message(Command("stats"))
async def stats(message: types.Message):
    count = user_stats.get(message.from_user.id, 0)
    await message.answer(f"📊 Сообщений отправлено: {count}")


# 💬 основной чат с эффектом печатания
@dp.message()
async def chat(message: types.Message):
    user_id = message.from_user.id

    if user_id not in user_memory:
        user_memory[user_id] = deque(maxlen=1000)
        user_stats[user_id] = 0

    user_memory[user_id].append({
        "role": "user",
        "content": message.text
    })

    messages = list(user_memory[user_id])

    msg = await message.answer("💬 Печатаю")

    try:
        # эффект "..."
        for i in range(3):
            await asyncio.sleep(0.4)
            dots = "." * (i + 1)
            await msg.edit_text(f"💬 Печатаю{dots}")

        # получаем ответ
        answer = ask_ai(messages)

        # эффект печати
        output = ""
        for char in answer:
            output += char

            try:
                await msg.edit_text(output[:4000])
            except:
                pass

            await asyncio.sleep(0.02)

        user_memory[user_id].append({
            "role": "assistant",
            "content": answer
        })

        user_stats[user_id] += 1

    except Exception:
        await msg.edit_text("⚠️ Ошибка API")


# 🚀 запуск
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())