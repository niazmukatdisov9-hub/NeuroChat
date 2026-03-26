import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ===== НАСТРОЙКИ =====
TELEGRAM_TOKEN = "8792752911:AAGEO-USE4lg-2BaqfoxDdE7skgXzCr7QHs"      # от BotFather
ACCOUNT_ID = "5aca98f5b0f6b087c11b28eddf0b316b"   # ID аккаунта Cloudflare
API_TOKEN = "cfut_bOCx4Nrj0jVRj65sKGI6i3IPuh9YlYkwihkbAWOx40b6ca7d"     # API токен с правами Workers AI
MODEL = "@cf/meta/llama-3.2-3b-instruct"   # можно заменить на другую модель

# URL для Cloudflare Workers AI
AI_URL = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/run/{MODEL}"

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===== ФУНКЦИЯ ЗАПРОСА К CLOUDFLARE AI =====
async def ask_cloudflare_ai(prompt: str) -> str:
    """Отправляет запрос к Cloudflare Workers AI и возвращает ответ."""
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    # Для инструктивных моделей лучше передавать системный промпт, но API принимает просто messages
    # Для llama-3.2-3b-instruct используем массив сообщений
    payload = {
        "messages": [
            {"role": "system", "content": "Ты полезный и дружелюбный помощник."},
            {"role": "user", "content": prompt}
        ]
    }
    try:
        response = requests.post(AI_URL, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        # Успешный ответ содержит поле result.response
        if data.get("success"):
            answer = data["result"]["response"]
            return answer.strip()
        else:
            logger.error(f"Cloudflare API error: {data.get('errors')}")
            return "Извините, произошла ошибка при обращении к ИИ."
    except Exception as e:
        logger.error(f"Ошибка запроса: {e}")
        return "Не удалось связаться с сервером ИИ."

# ===== ОБРАБОТЧИКИ TELEGRAM =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я бот на базе Cloudflare AI. Просто отправь сообщение, и я отвечу.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    logger.info(f"Получено: {user_text}")
    await update.message.chat.send_action(action="typing")
    answer = await ask_cloudflare_ai(user_text)
    await update.message.reply_text(answer)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.warning(f"Ошибка: {context.error}")

# ===== ЗАПУСК =====
def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)
    logger.info("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()