"""
Mental Models Daily — Telegram Bot
Sends mental models and forex education tips on request or daily subscription.

Run locally:
    export BOT_TOKEN="your-token-from-botfather"
    python bot.py

Deployed on Railway, BOT_TOKEN is read from an environment variable you set
in the Railway dashboard (Variables tab) — never hard-code it in this file.
"""

import json
import logging
import os
import random
from datetime import time as dtime

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

SUBSCRIBERS_FILE = "subscribers.json"

# ---------------------------------------------------------------------------
# CONTENT LIBRARY — add new entries any time, no other code needs to change
# ---------------------------------------------------------------------------

MENTAL_MODELS = [
    {
        "title": "🧠 First Principles Thinking",
        "body": (
            "Break a complex problem down to its most basic, foundational truths — "
            "the things you know for certain — then build a solution upward from there.\n\n"
            "Instead of copying what others do with minor tweaks, dismantle the situation "
            "until you hit bedrock facts, and reason up from there."
        ),
    },
    {
        "title": "🧠 The Pareto Principle (80/20 Rule)",
        "body": (
            "80% of your results typically come from 20% of your efforts.\n\n"
            "Identify the specific 20% of your work, clients, or habits that actually "
            "move the needle — and double down on them."
        ),
    },
    {
        "title": "🧠 Occam's Razor",
        "body": (
            "The simplest explanation is usually the correct one.\n\n"
            "Before building a complex theory to explain a problem, check and eliminate "
            "the most obvious possibilities first."
        ),
    },
    {
        "title": "🧠 Inversion",
        "body": (
            "Instead of asking how to succeed, ask how to guarantee failure — then avoid "
            "those things.\n\n"
            "To win, first learn how not to lose."
        ),
    },
    {
        "title": "🧠 Second-Order Thinking",
        "body": (
            "First-order thinking looks at the immediate result of a decision. "
            "Second-order thinking asks 'and then what?' — tracing the chain reaction "
            "over time.\n\n"
            "Never judge a decision solely by its immediate outcome."
        ),
    },
    {
        "title": "🧠 Compounding",
        "body": (
            "Small, consistent gains multiply into large results over time.\n\n"
            "Focus on steady 1% improvements rather than looking for overnight wins."
        ),
    },
    {
        "title": "🧠 Circle of Competence",
        "body": (
            "True expertise isn't knowing everything — it's being clear on what you "
            "understand deeply, and knowing exactly where your gaps begin.\n\n"
            "Stay inside your circle for high-leverage decisions; when you must step "
            "outside it, learn the fundamentals first."
        ),
    },
    {
        "title": "🧠 The Map Is Not the Territory",
        "body": (
            "Any model, plan, or description of reality is a simplification — useful, "
            "but never complete.\n\n"
            "Hold your models loosely. When reality contradicts your map, trust reality "
            "and update the map."
        ),
    },
    {
        "title": "🧠 Opportunity Cost",
        "body": (
            "Every choice has a hidden price: the value of the next-best option you "
            "gave up.\n\n"
            "Before committing to anything, ask: what am I giving up to do this?"
        ),
    },
]

FOREX_TIPS = [
    {
        "title": "📊 Patience Over Emotion",
        "body": (
            "Waiting for price to reach a key support or resistance level — rather than "
            "chasing it — is a core part of a disciplined process, not a delay tactic.\n\n"
            "⚠️ Educational content only. Trading involves risk. Not financial advice."
        ),
    },
    {
        "title": "📊 Risk-to-Reward Basics",
        "body": (
            "Defining your invalidation level (stop loss) before opening a position — not "
            "after — is one of the most important habits in risk management.\n\n"
            "⚠️ Educational content only. Trading involves risk. Not financial advice."
        ),
    },
    {
        "title": "📊 Process Over Outcome",
        "body": (
            "Long-term consistency comes from following a defined process — entry rules, "
            "invalidation levels, and position sizing — rather than reacting to any single "
            "trade's result.\n\n"
            "⚠️ Educational content only. Trading involves risk. Not financial advice."
        ),
    },
    {
        "title": "📊 Higher Timeframe Alignment",
        "body": (
            "Assessing the overall trend on daily or 4H charts before looking at lower "
            "timeframe entries helps filter out setups that fight the dominant momentum.\n\n"
            "⚠️ Educational content only. Trading involves risk. Not financial advice."
        ),
    },
    {
        "title": "📊 Setup Selectivity",
        "body": (
            "Not every price fluctuation is a viable opportunity. Filtering for "
            "high-probability setups that match your criteria reduces overtrading.\n\n"
            "⚠️ Educational content only. Trading involves risk. Not financial advice."
        ),
    },
    {
        "title": "📊 Position Sizing",
        "body": (
            "Risking a small, fixed percentage of your account per trade helps absorb "
            "losing streaks without large drawdowns.\n\n"
            "⚠️ Educational content only. Trading involves risk. Not financial advice."
        ),
    },
]

WELCOME_MESSAGE = (
    "👋 Welcome to Mental Models Daily!\n\n"
    "This bot sends bite-sized mental models and forex market education — "
    "educational content only, no signals and no financial advice.\n\n"
    "Commands:\n"
    "/mentalmodel — get a random mental model\n"
    "/forextip — get a random forex education tip\n"
    "/subscribe — get a daily tip automatically\n"
    "/unsubscribe — stop daily tips\n"
    "/help — show this message again"
)

# ---------------------------------------------------------------------------
# SUBSCRIBER STORAGE
# ---------------------------------------------------------------------------


def load_subscribers() -> set:
    if os.path.exists(SUBSCRIBERS_FILE):
        with open(SUBSCRIBERS_FILE, "r") as f:
            return set(json.load(f))
    return set()


def save_subscribers(subscribers: set) -> None:
    with open(SUBSCRIBERS_FILE, "w") as f:
        json.dump(list(subscribers), f)


subscribers = load_subscribers()

# ---------------------------------------------------------------------------
# COMMAND HANDLERS
# ---------------------------------------------------------------------------


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(WELCOME_MESSAGE)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(WELCOME_MESSAGE)


async def mental_model(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pick = random.choice(MENTAL_MODELS)
    await update.message.reply_text(f"{pick['title']}\n\n{pick['body']}")


async def forex_tip(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pick = random.choice(FOREX_TIPS)
    await update.message.reply_text(f"{pick['title']}\n\n{pick['body']}")


async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    if chat_id in subscribers:
        await update.message.reply_text("You're already subscribed to daily tips.")
        return
    subscribers.add(chat_id)
    save_subscribers(subscribers)
    await update.message.reply_text(
        "✅ Subscribed! You'll get one tip a day. Use /unsubscribe to stop anytime."
    )


async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    if chat_id not in subscribers:
        await update.message.reply_text("You're not currently subscribed.")
        return
    subscribers.discard(chat_id)
    save_subscribers(subscribers)
    await update.message.reply_text("You've been unsubscribed from daily tips.")


async def send_daily_tip(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Runs once a day, sends one random tip to every subscriber."""
    if not subscribers:
        return
    pick = random.choice(MENTAL_MODELS + FOREX_TIPS)
    text = f"{pick['title']}\n\n{pick['body']}"
    for chat_id in list(subscribers):
        try:
            await context.bot.send_message(chat_id=chat_id, text=text)
        except Exception as exc:
            logger.warning("Failed to send to %s: %s", chat_id, exc)


# ---------------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------------


def main() -> None:
    token = os.environ.get("BOT_TOKEN")
    if not token:
        raise RuntimeError(
            "BOT_TOKEN environment variable is not set. "
            "Set it locally with `export BOT_TOKEN=...` or in Railway's Variables tab."
        )

    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("mentalmodel", mental_model))
    application.add_handler(CommandHandler("forextip", forex_tip))
    application.add_handler(CommandHandler("subscribe", subscribe))
    application.add_handler(CommandHandler("unsubscribe", unsubscribe))

    # Daily tip at 09:00 UTC — adjust the hour to suit your audience's timezone.
    application.job_queue.run_daily(send_daily_tip, time=dtime(hour=9, minute=0))

    logger.info("Bot starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
