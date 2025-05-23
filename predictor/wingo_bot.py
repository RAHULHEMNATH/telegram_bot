from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from collections import Counter, defaultdict
import numpy as np
from typing import List, Tuple, Optional

# --- Enhanced Pattern Definitions with More Complex Patterns ---
patterns = {
    # Basic patterns
    "Single Trend": ["B", "S", "B", "S", "B"],
    "Double Trend": ["S", "S", "B", "S", "S"],
    "Triple Trend": ["B", "B", "B", "S", "S"],
    "Quadra Trend": ["S", "S", "S", "B", "B", "B"],
    
    # Advanced patterns
    "Three in One Trend": ["B", "B", "B", "S", "B", "B"],
    "Two in One Trend": ["S", "S", "B", "S", "S", "B", "S", "S"],
    "Three in Two Trend": ["B", "B", "B", "S", "S", "B", "B"],
    "Four in One Trend": ["S", "S", "S", "S", "B", "S", "S", "S"],
    "Four in Two Trend": ["B", "B", "B", "B", "S", "S", "B", "B", "B"],
    "Long Trend": ["S", "S", "S", "S", "S", "S", "S", "S", "S"],
    
    # New complex patterns
    "Alternating Pattern": ["B", "S", "B", "S", "B", "S"],
    "Double Reversal": ["B", "B", "S", "S", "B", "B"],
    "Triple Reversal": ["S", "S", "S", "B", "B", "B", "S", "S", "S"],
    "Staircase Up": ["B", "B", "S", "B", "B", "S", "B", "B"],
    "Staircase Down": ["S", "S", "B", "S", "S", "B", "S", "S"],
    "Pyramid": ["B", "S", "S", "B", "B", "B", "S", "S", "B"],
    "Diamond": ["S", "B", "B", "S", "S", "S", "B", "B", "S"]
}

# Pattern priorities (higher means more significant) with weights
pattern_priority = {
    "Long Trend": 15,
    "Triple Reversal": 12,
    "Quadra Trend": 11,
    "Diamond": 10,
    "Pyramid": 10,
    "Four in One Trend": 9,
    "Four in Two Trend": 9,
    "Double Reversal": 8,
    "Three in One Trend": 8,
    "Three in Two Trend": 8,
    "Staircase Up": 7,
    "Staircase Down": 7,
    "Two in One Trend": 6,
    "Triple Trend": 5,
    "Double Trend": 4,
    "Alternating Pattern": 4,
    "Single Trend": 3
}

# Pattern success rates (can be updated dynamically)
pattern_success_rates = defaultdict(lambda: 0.7)  # Default 70% success rate
pattern_success_rates.update({
    "Long Trend": 0.85,
    "Triple Reversal": 0.82,
    "Quadra Trend": 0.8,
    "Diamond": 0.78,
    "Pyramid": 0.78
})

# --- Markov Chain Implementation ---
class MarkovChain:
    def __init__(self):
        self.transitions = {"B": {"B": 0, "S": 0}, "S": {"B": 0, "S": 0}}
        self.total = {"B": 0, "S": 0}
    
    def update(self, sequence: List[str]):
        for i in range(len(sequence) - 1):
            current = sequence[i]
            next_state = sequence[i+1]
            self.transitions[current][next_state] += 1
            self.total[current] += 1
    
    def predict(self, current_state: str) -> Optional[str]:
        if self.total[current_state] == 0:
            return None
        
        bb = self.transitions[current_state]["B"] / self.total[current_state]
        bs = self.transitions[current_state]["S"] / self.total[current_state]
        
        if bb > bs:
            return "B"
        elif bs > bb:
            return "S"
        return None

markov_chain = MarkovChain()

# --- Enhanced Prediction Logic ---
def predict_next(outcomes: List[str]) -> Tuple[str, str, float]:
    # Update Markov chain
    markov_chain.update(outcomes)
    
    # First check for pattern matches
    matched_patterns = []
    
    for name, pattern in patterns.items():
        pattern_length = len(pattern)
        if len(outcomes) >= pattern_length:
            # Check if the end of outcomes matches the pattern
            if outcomes[-pattern_length:] == pattern:
                matched_patterns.append((name, pattern, pattern_success_rates[name]))
    
    # If we found matching patterns, use the highest priority one
    if matched_patterns:
        # Sort by priority and success rate
        matched_patterns.sort(
            key=lambda x: (pattern_priority.get(x[0], 0), x[2]),
            reverse=True
        )
        
        best_pattern_name, best_pattern, success_rate = matched_patterns[0]
        
        # Apply the pattern's reversal logic
        last_element = best_pattern[-1]
        prediction = "S" if last_element == "B" else "B"
        
        # Special cases
        if best_pattern_name == "Long Trend":
            prediction = "B"
        elif best_pattern_name == "Alternating Pattern":
            prediction = "S" if outcomes[-1] == "B" else "B"
        elif best_pattern_name in ["Double Reversal", "Triple Reversal"]:
            prediction = outcomes[-1]  # Continue the current trend
        
        return prediction, best_pattern_name, success_rate
    
    # Check Markov chain prediction
    markov_prediction = markov_chain.predict(outcomes[-1])
    if markov_prediction:
        return markov_prediction, "Markov Chain Prediction", 0.75
    
    # Fallback to counting with weighted history
    lookback = min(10, len(outcomes))
    recent = outcomes[-lookback:]
    counts = Counter(recent)
    
    # Apply exponential weighting (more recent results have more weight)
    weights = np.exp(np.linspace(0, 1, lookback))
    b_weight = sum(w for w, x in zip(weights, recent) if x == "B")
    s_weight = sum(w for w, x in zip(weights, recent) if x == "S")
    
    if b_weight > s_weight:
        return "B", "Weighted Count-based Prediction", 0.65
    elif s_weight > b_weight:
        return "S", "Weighted Count-based Prediction", 0.65
    else:
        # If completely equal, use overall probability
        overall_b = sum(1 for x in outcomes if x == "B") / len(outcomes)
        return ("B" if overall_b > 0.5 else "S", "Overall Probability", 0.6)

# --- Telegram Bot Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to Advanced Wingo Predictor Bot!\n\n"
        "📊 Send the last results using 'B' and 'S' (e.g., BSSBBSSBBS).\n"
        "🔍 I'll analyze patterns and trends to predict the next outcome."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.upper().replace(" ", "")
    if all(c in "BS" for c in text):
        outcomes = list(text)
        if len(outcomes) < 3:
            await update.message.reply_text("⚠️ Please provide at least 3 results for meaningful prediction.")
            return
            
        prediction, pattern_used, confidence = predict_next(outcomes)
        confidence_percent = int(confidence * 100)
        
        response = (
            f"🧠 Predicted Next: {'BIG' if prediction == 'B' else 'SMALL'} (Confidence: {confidence_percent}%)\n"
            f"📊 Method Used: {pattern_used}\n\n"
            "🔹 REMEMBER DUE PATTERNS:\n"
            "- BIG GREEN → SMALL RED\n"
            "- BIG RED → SMALL GREEN\n\n"
            "💡 TIP: Combine with your own analysis for best results."
        )
        await update.message.reply_text(response)
    else:
        await update.message.reply_text(
            "⚠️ Invalid input. Please use only 'B' (for BIG) and 'S' (for SMALL) characters.\n"
            "Example: BSBSSBSBB"
        )

# --- Main Bot Runner ---
if __name__ == '__main__':
    import os
    TOKEN = "7649917363:AAGgqHvB8A4HZ83sW9BQjOvSjOgpwYO3oqc"  # <-- Replace with your actual token
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Advanced Prediction Bot is running...")
    app.run_polling()
