 from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
from datetime import datetime
TOKEN = "7250586844:AAGv-qh10O_SUZjE4eGodSwdPc63_Be0QhE" ADMIN_CHAT_ID = 5258395757 user_data = {} pending_users = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): keyboard = [ [InlineKeyboardButton("💰 Hisob to‘ldirish", callback_data="deposit")], [InlineKeyboardButton("🛄 Pul chiqarish", callback_data="withdraw")], [InlineKeyboardButton("👨‍💼 Aloqa", callback_data="contact")] ] reply_markup = InlineKeyboardMarkup(keyboard) await update.message.reply_text( "Assalomu alaykum, hush kelibsiz! Kerakli menyuni tanlang 👇", reply_markup=reply_markup )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE): query = update.callback_query await query.answer() if query.data == "deposit": await query.message.reply_text("1xbet ID raqamingizni kiriting:") context.user_data["state"] = "awaiting_id" elif query.data == "withdraw": await query.message.reply_text( "⚠️Oldin shu manzilga ariza yarating va 4 talik kodni oling. (shaxar; Oltiariq) (Kocha; remax24/7)✅\n\n🔖ID raqamingizni kiriting..." ) context.user_data["state"] = "awaiting_withdraw_id" elif query.data == "contact": await query.message.reply_text( "Operatorlarimiz sizga 24/7 xizmat ko‘rsatadi!\n\n👉 @xbetkassauz1", disable_web_page_preview=True )

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE): text = update.message.text state = context.user_data.get("state") user_id = update.message.from_user.id

if state == "awaiting_id":
    context.user_data["1xbet_id"] = text
    await update.message.reply_text("Karta raqamingizni kiriting:")
    context.user_data["state"] = "awaiting_card"
elif state == "awaiting_card":
    context.user_data["card"] = text
    await update.message.reply_text("Minimal: 15000 UZS\nMaksimal: 3000000 UZS\n\nTo‘lov summasini kiriting:")
    context.user_data["state"] = "awaiting_amount"
elif state == "awaiting_amount":
    amount = text
    context.user_data["amount"] = amount
    pending_users[user_id] = dict(context.user_data)

    await update.message.reply_text(
        f"✅ Karta: 8600 5304 9066 3815\n"
        f"💰 {amount} so‘m yuboring va skrinshotni tashlang"
    )

    await update.message.reply_text(
        "TUGMANI BOSIB BIZGA PUL YUBORGANINGIZ HAQIDAGI SKRINSHOTNI YUKLANG\n\n"
        "⛔️ Agar xato qilib, boshqa summani o‘tkazsangiz, pul 15 ish kuni ichida qaytariladi yoki kuyadi!"
    )

    context.user_data["state"] = "awaiting_screenshot"

elif state == "awaiting_screenshot" and update.message.photo:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = pending_users.get(user_id, {})
    caption = (
        f"💳 Karta raqami: {data.get('card')}\n"
        f"🆔1xbet ID: {data.get('1xbet_id')}\n"
        f"💶 Summa: {data.get('amount')} so‘m\n"
        f"🕘 {now}\n"
        "Tasdiqlaysizmi?"
    )
    keyboard = [
        [
            InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"approve_{user_id}"),
            InlineKeyboardButton("❌ Rad etish", callback_data=f"reject_{user_id}")
        ]
    ]
    await context.bot.send_photo(
        ADMIN_CHAT_ID,
        photo=update.message.photo[-1].file_id,
        caption=caption,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    await update.message.reply_text("Rahmat! Iltimos, admin tekshiradi va javob beradi.")
    context.user_data.clear()

elif state == "awaiting_withdraw_id":
    context.user_data["withdraw_id"] = text
    await update.message.reply_text("Karta raqamingizni kiriting:")
    context.user_data["state"] = "awaiting_withdraw_card"
elif state == "awaiting_withdraw_card":
    context.user_data["withdraw_card"] = text
    await update.message.reply_text("1xbet tomonidan berilgan 4 talik kodni kiriting:")
    context.user_data["state"] = "awaiting_withdraw_code"
elif state == "awaiting_withdraw_code":
    code = text
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    await update.message.reply_text(
        f"✅ Arizangiz qabul qilindi!\n\n"
        f"📅 Vaqt: {now}\n"
        f"📅 1xbet ID: {context.user_data['withdraw_id']}\n"
        f"💳 Karta: {context.user_data['withdraw_card']}\n"
        f"#⃣ 4 talik kod: {code}\n\n"
        "Pul kartangizga 10 daqiqadan 10 soatgacha o'tkaziladi."
    )
    await context.bot.send_message(
        ADMIN_CHAT_ID,
        f"💳 Karta: {context.user_data['withdraw_card']}\n"
        f"🆔1xbet ID: {context.user_data['withdraw_id']}\n"
        f"#⃣ 4 talik kod: {code}\n"
        f"🗓 Vaqt: {now}"
    )
    context.user_data.clear()

async def confirm_admin(update: Update, context: ContextTypes.DEFAULT_TYPE): query = update.callback_query await query.answer() data = query.data

if data.startswith("approve_"):
    user_id = int(data.split("_")[1])
    info = pending_users.get(user_id)
    if info:
        await context.bot.send_message(
            chat_id=user_id,
            text=(
                f"💳 Karta: {info['card']}\n"
                f"🆔1xbet ID: {info['1xbet_id']}\n"
                f"💶 Summa: {info['amount']} so‘m\n"
                f"✅ Muvaffaqiyatli o‘tkazildi!"
            )
        )
elif data.startswith("reject_"):
    user_id = int(data.split("_")[1])
    await context.bot.send_message(
        chat_id=user_id,
        text="❌ To'lov rad etildi. Iltimos, @xbetkassauz1 bilan bog'laning."
    )

await query.message.edit_reply_markup(reply_markup=None)

def main(): app = ApplicationBuilder().token(TOKEN).build() app.add_handler(CommandHandler("start", start)) app.add_handler(CallbackQueryHandler(button_handler, pattern="^(deposit|withdraw|contact)$")) app.add_handler(CallbackQueryHandler(confirm_admin, pattern="^(approve_|reject_).+")) app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, message_handler)) app.run_polling()

if name == "main": main()

