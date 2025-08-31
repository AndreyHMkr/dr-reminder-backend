import os
import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_URL   = os.getenv("API_URL")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text if update.message else ""
    args = context.args or []
    logging.info("START: text=%r args=%r chat_id=%s", text, args, chat_id)

    # достаём токен из аргументов или из текста
    token = args[0] if args else (text.split(maxsplit=1)[1] if text and " " in text else None)
    if not token:
        await update.message.reply_text(
            "Запусти меня по ссылке с сайта (кнопка «Подключить Telegram»)\n"
            "или пришли команду одной строкой:\n/start <КОД>"
        )
        return

    try:
        r = requests.post(API_URL, json={"token": token, "chat_id": chat_id}, timeout=10)
        logging.info("API response: %s %s", r.status_code, r.text[:300])
    except requests.RequestException as e:
        logging.exception("API request failed")
        await update.message.reply_text("⚠️ Failed to connect to the server. Please try again later.")
        return

    if r.status_code == 200:
        await update.message.reply_text("✅ Telegram has been successfully linked!")
    elif r.status_code == 400:
        try:
            msg = r.json().get("detail") or r.json().get("message")
        except Exception:
            msg = None
        await update.message.reply_text(
            "❌ Binding error (400). " + (f"{msg}\n" if msg else "") +
            "Generate a new code on the site and open the link again."
        )
    else:
        await update.message.reply_text(f"❌ Binding error ({r.status_code}). {r.text[:200]}")

def main():
    logging.info("BOT starting, token_set=%s api_url=%s", bool(BOT_TOKEN), API_URL)
    if not BOT_TOKEN:
        logging.error("TELEGRAM_BOT_TOKEN is missing!")
        raise SystemExit(1)
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    logging.info("run_polling()...")
    app.run_polling()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.exception("BOT crashed: %s", e)
        raise