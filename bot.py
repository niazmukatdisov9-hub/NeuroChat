import asyncio
import requests

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command

# 🔑 КЛЮЧИ
BOT_TOKEN = "8792752911:AAGEO-USE4lg-2BaqfoxDdE7skgXzCr7QHs"
CLOUDFLARE_API_KEY = "xwM3EhdP-fSx8hQONxjcrmQWn4lbgEUwTQqBzzhl"
ACCOUNT_ID = "76931ff53ab99e356450b9a6245d4378"
VIDEO_API_KEY = "sk_live_dHA0ROK7Fn_9r6z1L2tSR-QTEYPAiG42nUykUHdEe-w"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Хранилище
users = {}
languages = {}

# Меню
menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💬 Чат")],
        [KeyboardButton(text="🖼 Фото"), KeyboardButton(text="🎬 Видео")],
        [KeyboardButton(text="🌐 Язык"), KeyboardButton(text="🧹 Очистить")],
        [KeyboardButton(text="🆕 Новый чат"), KeyboardButton(text="👥 Онлайн")]
    ],
    resize_keyboard=True
)

# AI запрос (Cloudflare)
def ask_ai(messages):

    url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/run/@cf/meta/llama-3-8b-instruct"

    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "messages": messages
    }

    r = requests.post(url, headers=headers, json=data)

    result = r.json()

    try:
        return result["result"]["response"]
    except:
        return str(result)


# Генерация фото
def generate_image(prompt):

    url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/run/@cf/stabilityai/stable-diffusion-xl-base-1.0"

    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_KEY}",
    }

    r = requests.post(url, headers=headers, json={"prompt": prompt})

    return "Фото сгенерировано (Cloudflare)"


# Генерация видео (пример API)
def generate_video(prompt):

    url = "https://api.someservice.com/video"
    headers = {"Authorization": f"Bearer {VIDEO_API_KEY}"}

    r = requests.post(url, headers=headers, json={"prompt": prompt})

    return "Видео создается..."


# СТАРТ
@dp.message(Command("start"))
async def start(message: Message):

    uid = message.from_user.id

    users.setdefault(uid, [])
    languages.setdefault(uid, "ru")

    await message.answer("Бот готов 🚀", reply_markup=menu)


# ЯЗЫК
@dp.message(F.text == "🌐 Язык")
async def lang_menu(message: Message):

    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Русский")],
            [KeyboardButton(text="English")],
            [KeyboardButton(text="中文")]
        ],
        resize_keyboard=True
    )

    await message.answer("Выбери язык:", reply_markup=kb)


@dp.message(F.text.in_(["Русский", "English", "中文"]))
async def set_lang(message: Message):

    uid = message.from_user.id

    if message.text == "Русский":
        languages[uid] = "ru"
    elif message.text == "English":
        languages[uid] = "en"
    else:
        languages[uid] = "cn"

    await message.answer("Язык изменен", reply_markup=menu)


# ОЧИСТКА
@dp.message(F.text == "🧹 Очистить")
async def clear(message: Message):

    users[message.from_user.id] = []

    await message.answer("История очищена")


# НОВЫЙ ЧАТ
@dp.message(F.text == "🆕 Новый чат")
async def new_chat(message: Message):

    users[message.from_user.id] = []

    await message.answer("Новый чат создан")


# ПОЛЬЗОВАТЕЛИ
@dp.message(F.text == "👥 Онлайн")
async def count_users(message: Message):

    await message.answer(f"Пользователей: {len(users)}")


# ФОТО
@dp.message(F.text == "🖼 Фото")
async def photo(message: Message):

    await message.answer("Напиши описание фото")


    @dp.message()
    async def gen(msg: Message):

        img = generate_image(msg.text)

        await msg.answer(img)


# ВИДЕО
@dp.message(F.text == "🎬 Видео")
async def video(message: Message):

    await message.answer("Напиши описание видео")


    @dp.message()
    async def genv(msg: Message):

        vid = generate_video(msg.text)

        await msg.answer(vid)


# AI ЧАТ
@dp.message()
async def chat(message: Message):

    uid = message.from_user.id

    users.setdefault(uid, [])

    users[uid].append({
        "role": "user",
        "content": message.text
    })

    users[uid] = users[uid][-1000:]

    answer = ask_ai(users[uid])

    users[uid].append({
        "role": "assistant",
        "content": answer
    })

    await message.answer(answer)


# ЗАПУСК
async def main():

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())