import os
import logging
import httpx
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

chat_histories = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hi! I'm NovaMind AI. Ask me anything!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    user_text = update.message.text
    if user_id not in chat_histories:
        chat_histories[user_id] = []
    chat_histories[user_id].append({"role": "user", "parts": [{"text": user_text}]})
    try:
        async with httpx.AsyncClient() as client:
            r = await client.post(GEMINI_URL, json={"contents": chat_histories[user_id]}, timeout=30)
            reply = r.json()["candidates"][0]["content"]["parts"][0]["text"]
            chat_histories[user_id].append({"role": "model", "parts": [{"text": reply}]})
            await update.message.reply_text(reply)
    except Exception as e:
        await update.message.reply_text("⚠️ Something went wrong. Please try again.")
        logging.error(e)

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_histories.pop(update.message.chat_id, None)
    await update.message.reply_text("🔄 Reset! Start fresh.")

def main():
    app = Application.builder().token(os.environ["TELEGRAM_TOKEN"]).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
