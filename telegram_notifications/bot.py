from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import requests
import os
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    message = update.message.text

    parts = message.split()
    if len(parts) < 2:
        await update.message.reply_text("Please use the format: /start your@email.com")
        return

    email = parts[1]

    response = requests.post("http://localhost:8000/api/telegram/link/", json={
        "email": email,
        "chat_id": chat_id
    })

    if response.status_code == 200:
        await update.message.reply_text("✅ Telegram linked successfully!")
    else:
        await update.message.reply_text("❌ Failed to link. Please check your email or contact support.")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

if __name__ == '__main__':
    main()
