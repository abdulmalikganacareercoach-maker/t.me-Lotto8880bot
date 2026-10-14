import asyncio
import datetime
import logging
import os
import random
import sqlite3
from zoneinfo import ZoneInfo

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.error import Forbidden
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

logging.basicConfig(
    format="%(asctime)s %(name)s %(levelname)s %(message)s", level=logging.INFO
)
log = logging.getLogger("quotes-bot")

# ---------- Config (set these as Railway Variables) ----------
BOT_TOKEN = os.environ["BOT_TOKEN"]
DAILY_HOUR = int(os.getenv("DAILY_HOUR", "8"))
TIMEZONE = os.getenv("TIMEZONE", "Africa/Lagos")
DATA_DIR = os.getenv("DATA_DIR", ".")
DB_PATH = os.path.join(DATA_DIR, "subscribers.db")

# ---------- Quotes (text, author) ----------
# Short, widely cited quotes. Attributions are the commonly accepted ones.
QUOTES = [
    ("It is not that we have a short time to live, but that we waste a lot of it.", "Seneca"),
    ("We suffer more often in imagination than in reality.", "Seneca"),
    ("Waste no more time arguing what a good man should be. Be one.", "Marcus Aurelius"),
    ("The journey of a thousand miles begins with a single step.", "Lao Tzu"),
    ("It does not matter how slowly you go as long as you do not stop.", "Confucius"),
    ("He who has a why to live can bear almost any how.", "Friedrich Nietzsche"),
    ("The only thing we have to fear is fear itself.", "Franklin D. Roosevelt"),
    ("Courage is resistance to fear, mastery of fear, not absence of fear.", "Mark Twain"),
    ("An investment in knowledge pays the best interest.", "Benjamin Franklin"),
    ("Do what you can, with what you have, where you are.", "Theodore Roosevelt"),
    ("I know that I know nothing.", "Socrates"),
    ("Well begun is half done.", "Aristotle"),
    ("Fall seven times, stand up eight.", "Japanese proverb"),
    ("The best time to plant a tree was twenty years ago. The second best time is now.", "Proverb"),
    ("The man who moves a mountain begins by carrying away small stones.", "Confucius"),
    ("No one can make you feel inferior without your consent.", "Eleanor Roosevelt"),
    ("A smooth sea never made a skilled sailor.", "Proverb"),
    ("What we dwell on is who we become.", "Oprah Winfrey"),
]

# ---------- Storage ----------
def db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS subscribers (chat_id INTEGER PRIMARY KEY)"
    )
    return conn


def add_sub(chat_id: int):
    with db() as conn:
        conn.execute("INSERT OR IGNORE INTO subscribers VALUES (?)", (chat_id,))


def remove_sub(chat_id: int):
    with db() as conn:
        conn.execute("DELETE FROM subscribers WHERE chat_id = ?", (chat_id,))


def is_sub(chat_id: int) -> bool:
    with db() as conn:
        row = conn.execute(
            "SELECT 1 FROM subscribers WHERE chat_id = ?", (chat_id,)
        ).fetchone()
    return row is not None


def all_subs():
    with db() as conn:
        return [r[0] for r in conn.execute("SELECT chat_id FROM subscribers")]


# ---------- Helpers ----------
def quote_text() -> str:
    text, author = random.choice(QUOTES)
    return f"💬 \"{text}\"\n\n— {author}"


def keyboard(chat_id: int) -> InlineKeyboardMarkup:
    sub_btn = (
        InlineKeyboardButton("🔕 Stop daily", callback_data="unsub")
        if is_sub(chat_id)
        else InlineKeyboardButton("🔔 Get daily quote", callback_data="sub")
    )
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("✨ Another quote", callback_data="quote")],
            [sub_btn],
        ]
    )


# ---------- Handlers ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await update.message.reply_text(
        "👋 Welcome! I share short quotes to inspire your day.\n\n"
        "Tap a button below, or use /help to see all commands.",
        reply_markup=keyboard(chat_id),
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Commands:\n"
        "/quote - a random quote\n"
        "/daily - get a fresh quote every day\n"
        "/stop - stop the daily quotes\n"
        "/about - about this bot"
    )


async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "A simple bot that delivers short inspirational quotes. "
        "It does not run lotteries, take payments or offer prizes. "
        "Quotes are attributed to their commonly cited authors."
    )


async def quote_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        quote_text(), reply_markup=keyboard(update.effective_chat.id)
    )


async def daily_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    add_sub(update.effective_chat.id)
    await update.message.reply_text(
        f"✅ Subscribed. You'll get a daily quote around {DAILY_HOUR}:00 ({TIMEZONE}). Use /stop to cancel."
    )


async def stop_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    remove_sub(update.effective_chat.id)
    await update.message.reply_text("🔕 Unsubscribed. Use /daily any time to rejoin.")


async def on_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    chat_id = q.message.chat_id

    if q.data == "quote":
        await q.message.reply_text(quote_text(), reply_markup=keyboard(chat_id))
    elif q.data == "sub":
        add_sub(chat_id)
        await q.message.reply_text(
            f"✅ Subscribed. Daily quote around {DAILY_HOUR}:00 ({TIMEZONE}).",
            reply_markup=keyboard(chat_id),
        )
    elif q.data == "unsub":
        remove_sub(chat_id)
        await q.message.reply_text("🔕 Unsubscribed.", reply_markup=keyboard(chat_id))


# ---------- Daily broadcast ----------
async def send_daily(context: ContextTypes.DEFAULT_TYPE):
    subs = all_subs()
    log.info("Sending daily quote to %d subscribers", len(subs))
    text = "☀️ Quote of the day\n\n" + quote_text()
    for chat_id in subs:
        try:
            await context.bot.send_message(chat_id, text)
        except Forbidden:
            remove_sub(chat_id)
        except Exception as e:
            log.warning("Failed to send to %s: %s", chat_id, e)
        await asyncio.sleep(0.05)


# ---------- Main ----------
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("about", about))
    app.add_handler(CommandHandler("quote", quote_cmd))
    app.add_handler(CommandHandler("daily", daily_cmd))
    app.add_handler(CommandHandler("stop", stop_cmd))
    app.add_handler(CallbackQueryHandler(on_button))

    app.job_queue.run_daily(
        send_daily,
        time=datetime.time(hour=DAILY_HOUR, minute=0, tzinfo=ZoneInfo(TIMEZONE)),
    )

    log.info("Quotes bot starting...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
