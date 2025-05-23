from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from collections import Counter

# --- Prediction Logic ---
patterns = {
    "Single Trend": ["B", "S", "B", "S", "B"],
    "Double Trend": ["S", "S", "B", "B", "S", "S"],
    "Triple Trend": ["B", "B", "B", "S", "S", "S"],
    "Quadra Trend": ["S", "S", "S", "S", "B", "B", "B", "B"],
    "Three in One Trend": ["B", "B", "S", "B", "B", "B"],
    "Two in One Trend": ["S", "S", "B", "S", "S", "B", "S", "S"],
    "Three in Two Trend": ["B", "B", "B", "S", "S", "B", "B", "B"],
    "Four in One Trend": ["S", "S", "S", "S", "B", "S", "S", "S", "S"],
    "Four in Two Trend": ["B", "B", "B", "B", "S", "S", "B", "B", "B", "B"],
    "Long Trend": ["S"] * 10
}

def predict_next(outcomes):
    for pattern in patterns.values():
        if outcomes[-len(pattern):] == pattern:
            return "B" if pattern[-1] == "S" else "S"
    counts = Counter(outcomes[-5:])
    return "B" if counts["B"] > counts["S"] else "S"

# --- Telegram Bot Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Welcome to Wingo Predictor Bot!\nSend the last 10 results using 'B' and 'S' (e.g., BSSBBSSBBS).")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.upper().replace(" ", "")
    if len(text) == 10 and all(c in "BS" for c in text):
        prediction = predict_next(list(text))
        await update.message.reply_text(f"🧠 Predicted Next: {'BIG' if prediction == 'B' else 'SMALL'}")
    else:
        await update.message.reply_text("⚠️ Invalid input. Please send exactly 10 letters using only 'B' and 'S'.")

# --- Main Bot Runner ---
if __name__ == '__main__':
    import os
    TOKEN = "7649917363:AAGgqHvB8A4HZ83sW9BQjOvSjOgpwYO3oqc"  # <-- Replace this with your actual token
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot is running...")
    app.run_polling()
