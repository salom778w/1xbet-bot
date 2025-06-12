from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from datetime import datetime

TOKEN = "TOKENINGIZNI_BU_YERGA_YOZING"
ADMIN_CHAT_ID = 5258395757  # Admin Telegram ID (raqam ko‘rinishida)

user_data = {}
pending_users = {}

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💰 Hisob to‘ldirish", callback_data="deposit")],
        [InlineKeyboardButton("🛄 Pul chiqarish", callback_data="withdraw")],
        [InlineKeyboardButton("👨‍💼 Aloqa", callback_data="contact")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Assalomu alaykum, hush kelibsiz! Kerakli menyuni tanlang 👇",
        reply_markup=reply_markup
    )

# Callback tugmalar
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "deposit":
        await query.message.reply_text("💵 Iltimos, to‘ldirmoqchi bo‘lgan summani kiriting:")
        pending_users[query.from_user.id] = {"step": "amount"}
    elif query.data == "withdraw":
        await query.message.reply_text("❌ Pul yechish hozircha mavjud emas.")
    elif query.data == "contact":
        await query.message.reply_text("👨‍💼 Admin: @Xbetkassauz1")

# Xabarlarni qayta ishlash
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id not in pending_users:
        await update.message.reply_text("Iltimos, menyudan amal tanlang: /start")
        return

    step = pending_users[user_id]["step"]

    if step == "amount":
        try:
            amount = int(update.message.text)
            pending_users[user_id]["amount"] = amount
            pending_users[user_id]["step"] = "id"
            await update.message.reply_text("🆔 Iltimos, 1xBet ID raqamingizni kiriting:")
        except ValueError:
            await update.message.reply_text("❗ Noto‘g‘ri format. Faqat raqam kiriting.")
    elif step == "id":
        pending_users[user_id]["id"] = update.message.text
        pending_users[user_id]["step"] = "screenshot"
        await update.message.reply_text(
            "📷 Endi to‘lov skrinshotini yuboring.\n✅ Karta: 8600 XXXX XXXX XXXX\n💰 {0} so‘m yuboring va tasdiqlovchi rasmni jo‘nating.".format(
                pending_users[user_id]["amount"]
            )
        )
    elif step == "screenshot" and update.message.photo:
        photo = update.message.photo[-1]
        file_id = photo.file_id
        user_info = pending_users[user_id]
        text = (
            f"💳 Karta raqami: 8600 XXXX XXXX XXXX\n"
            f"🆔 1xBet ID: {user_info['id']}\n"
            f"💶 Summa: {user_info['amount']} so‘m\n"
            f"🕘 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"⏳ Tekshirilmoqda..."
        )

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"approve:{user_id}")],
            [InlineKeyboardButton("❌ Rad etish", callback_data=f"reject:{user_id}")]
        ])

        await context.bot.send_photo(
            chat_id=ADMIN_CHAT_ID,
            photo=file_id,
            caption=text,
            reply_markup=keyboard
        )
        await update.message.reply_text("✅ So‘rovingiz adminga yuborildi. Tez orada javob olasiz.")
        user_data[user_id] = {
            "id": user_info["id"],
            "amount": user_info["amount"],
        }
        del pending_users[user_id]
    else:
        await update.message.reply_text("❗ Iltimos, to‘g‘ri rasm yuboring.")

# Admin tugmalarni qayta ishlaydi
async def admin_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    action, user_id = query.data.split(":")
    user_id = int(user_id)

    if action == "approve":
        await context.bot.send_message(
            chat_id=user_id,
            text=(
                f"💳 Karta raqami: 8600 XXXX XXXX XXXX\n"
                f"🆔 1xBet ID: {user_data[user_id]['id']}\n"
                f"💶 Summa: {user_data[user_id]['amount']} so‘m\n"
                f"✅ Muvaffaqiyatli o‘tkazildi"
            )
        )
        await query.edit_message_caption(caption="✅ To‘lov tasdiqlandi.")
    elif action == "reject":
        await context.bot.send_message(
            chat_id=user_id,
            text="❌ So‘rov rad etildi. Iltimos admin bilan bog‘laning: @Xbetkassauz1"
        )
        await query.edit_message_caption(caption="❌ To‘lov rad etildi.")

# Botni ishga tushurish
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler, pattern="^(deposit|withdraw|contact)$"))
    app.add_handler(CallbackQueryHandler(admin_response, pattern="^(approve|reject):"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.PHOTO, handle_message))
    app.run_polling()
