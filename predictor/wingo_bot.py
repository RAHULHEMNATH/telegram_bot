from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from collections import Counter

# --- Enhanced Pattern Definitions ---
patterns = {
    "Single Trend": ["B", "S", "B", "S", "B"],
    "Double Trend": ["S", "S", "B", "S", "S"],
    "Triple Trend": ["B", "B", "B", "S", "S"],
    "Quadra Trend": ["S", "S", "S", "B", "B", "B"],
    "Three in One Trend": ["B", "B", "B", "S", "B", "B"],
    "Two in One Trend": ["S", "S", "B", "S", "S", "B", "S", "S"],
    "Three in Two Trend": ["B", "B", "B", "S", "S", "B", "B"],
    "Four in One Trend": ["S", "S", "S", "S", "B", "S", "S", "S"],
    "Four in Two Trend": ["B", "B", "B", "B", "S", "S", "B", "B", "B"],
    "Long Trend": ["S", "S", "S", "S", "S", "S", "S", "S", "S"]
}

# Pattern priorities (higher means more significant)
pattern_priority = {
    "Long Trend": 10,
    "Quadra Trend": 8,
    "Four in One Trend": 7,
    "Four in Two Trend": 7,
    "Three in One Trend": 6,
    "Three in Two Trend": 6,
    "Two in One Trend": 5,
    "Triple Trend": 4,
    "Double Trend": 3,
    "Single Trend": 2
}

# --- Enhanced Prediction Logic ---
def predict_next(outcomes):
    # First check for pattern matches
    matched_patterns = []
    
    for name, pattern in patterns.items():
        pattern_length = len(pattern)
        if len(outcomes) >= pattern_length:
            # Check if the end of outcomes matches the pattern
            if outcomes[-pattern_length:] == pattern:
                matched_patterns.append((name, pattern))
    
    # If we found matching patterns, use the highest priority one
    if matched_patterns:
        # Sort by priority (highest first)
        matched_patterns.sort(key=lambda x: pattern_priority.get(x[0], 0), reverse=True)
        best_pattern_name, best_pattern = matched_patterns[0]
        
        # Apply the pattern's reversal logic
        last_element = best_pattern[-1]
        prediction = "S" if last_element == "B" else "B"
        
        # Special case for Long Trend (all S) - predict B
        if best_pattern_name == "Long Trend":
            prediction = "B"
            
        return prediction, best_pattern_name
    
    # Fallback to counting if no patterns match
    counts = Counter(outcomes[-5:])  # Look at last 5 results
    return ("B" if counts["B"] > counts["S"] else "S", "Count-based Prediction")

# --- Telegram Bot Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Welcome to Enhanced Wingo Predictor Bot!\nSend the last results using 'B' and 'S' (e.g., BSSBBSSBBS).")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.upper().replace(" ", "")
    if all(c in "BS" for c in text):
        prediction, pattern_used = predict_next(list(text))
        response = (
            f"🧠 Predicted Next: {'BIG' if prediction == 'B' else 'SMALL'}\n"
            f"📊 Pattern Used: {pattern_used}\n\n"
            "🔹 REMEMBER DUE:\n"
            "- BIG GREEN → SMALL RED\n"
            "- BIG RED → SMALL GREEN"
        )
        await update.message.reply_text(response)
    else:
        await update.message.reply_text("⚠️ Invalid input. Please use only 'B' and 'S' characters.")

# --- Main Bot Runner ---
if __name__ == '__main__':
    import os
    TOKEN = "7649917363:AAGgqHvB8A4HZ83sW9BQjOvSjOgpwYO3oqc"  # <-- Replace with your actual token
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Enhanced Bot is running...")
    app.run_polling()
