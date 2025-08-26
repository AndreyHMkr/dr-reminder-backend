import logging, os, requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv, find_dotenv

logging.basicConfig(level=logging.INFO)
load_dotenv(find_dotenv())
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_URL = "http://127.0.0.1:8002/api/telegram/link/"  # <-- порт 8002

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    logging.info("start text=%r args=%r", update.message.text if update.message else None, context.args)

    token = None
    if context.args:
        token = context.args[0]
    elif update.message and update.message.text:
        parts = update.message.text.split(maxsplit=1)
        if len(parts) == 2:
            token = parts[1]

    if not token:
        await update.message.reply_text("Запусти меня через сайт (кнопка 'Подключить Telegram') "
                                        "или пришли сюда команду:\n/start <ТОКЕН>")
        return

    r = requests.post(API_URL, json={"token": token, "chat_id": chat_id}, timeout=10)
    if r.status_code == 200:
        await update.message.reply_text("✅ Telegram успешно привязан!")
    else:
        await update.message.reply_text(f"❌ Ошибка привязки ({r.status_code}). Попробуй сгенерировать токен заново.")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

if __name__ == "__main__":
    main()

