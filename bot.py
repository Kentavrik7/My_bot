from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
import json, os

user_data = {}
with open("scenario.json", "r", encoding="utf-8") as f:
    scenario = json.load(f)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    user_data[uid] = {"username": None, "score": {"trust": 0, "hotwife": 0, "paranoia": 0, "submissive": 0, "flirt": 0, "neutral": 0}, "chapter": "chapter_1"}
    await update.message.reply_text("Привет! Введи имя:")

async def set_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid not in user_data or user_data[uid]['username']: return
    user_data[uid]['username'] = update.message.text.strip()
    await send_chapter(update, context, uid)

async def send_chapter(update_or_query, context, uid):
    ch = scenario.get(user_data[uid]['chapter'])
    if not ch: return
    btns = [[InlineKeyboardButton(c["text"], callback_data=str(i))] for i, c in enumerate(ch["choices"])]
    reply_markup = InlineKeyboardMarkup(btns)
    if ch.get("photo"):
        await context.bot.send_photo(chat_id=update_or_query.effective_chat.id, photo=ch["photo"], caption=ch["text"], reply_markup=reply_markup)
    else:
        await context.bot.send_message(chat_id=update_or_query.effective_chat.id, text=ch["text"], reply_markup=reply_markup)

async def handle_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    ch = scenario.get(user_data[uid]['chapter'])
    i = int(q.data)
    effects = ch["choices"][i].get("effects", {})
    for key, val in effects.items():
        user_data[uid]["score"][key] += val
    user_data[uid]["chapter"] = ch["choices"][i]["next"]
    await send_chapter(q, context, uid)

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    s = user_data.get(uid, {}).get("score", {})
    msg = "🧠 Характеристики:\n" + "\n".join(f"- {k}: {v}" for k, v in s.items())
    await update.message.reply_text(msg)

def main():
    app = ApplicationBuilder().token(os.environ["BOT_TOKEN"]).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("статы", stats))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, set_name))
    app.add_handler(CallbackQueryHandler(handle_choice))
    app.run_polling()

if __name__ == "__main__":
    main()