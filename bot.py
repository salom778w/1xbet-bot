from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (ApplicationBuilder, CommandHandler, MessageHandler,
                          CallbackQueryHandler, ContextTypes, filters)
from datetime import datetime
import random

TOKEN = "7250586844:AAGv-qh10O_SUZjE4eGodSwdPc63_Be0QhE"
ADMIN_CHAT_ID = 5258395757
user_data = {}
pending_payments = {}
pending_withdrawals = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💰 Hisob to‘ldirish: +0%", callback_data="hisob_tol")],
        [InlineKeyboardButton("➖ Pul chiqarish: 0%", callback_data="pul_chiqar")],
        [InlineKeyboardButton("👨‍💼 Operator", callback_data="operator")],
        [InlineKeyboardButton("📥 Ilovalar", url="https://t.me/YOUR_LINK")]
    ]
    await update.message.reply_text("💎 Hush kelibsiz 💎", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "operator":
        await query.message.reply_text("Admin: @xbetkassauz1")

    elif query.data == "hisob_tol":
        context.user_data.clear()
        await query.message.reply_text("Hisob raqamingizni kiriting:")
        context.user_data["state"] = "hisob_id"

    elif query.data == "pul_chiqar":
        await query.message.reply_text(
            "⚠️Oldin Shu manzilga ariza yarating va Ariza yartgan joyizda maqsus 4 talik kod olasiz✅\n"
            "⚠️MANZIL (SHAXAR: Oltiariq) (KOCHA: Remax24/7)\n\n"
            "Pul chiqarish uchun 1xBET UZS ID raqamingizni kiriting..."
        )
        context.user_data["state"] = "withdraw_id"

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text
    state = context.user_data.get("state")

    if state == "hisob_id":
        context.user_data["hisob_id"] = text
        await update.message.reply_text("Karta raqamini kiriting:")
        context.user_data["state"] = "hisob_card"

    elif state == "hisob_card":
        context.user_data["hisob_card"] = text
        await update.message.reply_text("Minimal: 15000 UZS\nMaksimal: 3000000 UZS\n\nMiqdorni kiriting:")
        context.user_data["state"] = "hisob_sum"

    elif state == "hisob_sum":
        try:
            amount = int(text)
            rand_extra = random.randint(1, 100)
            pay_amount = amount + rand_extra
            context.user_data["hisob_sum"] = amount
            context.user_data["pay_amount"] = pay_amount
            tg_id = random.randint(100000, 999999)
            context.user_data["tg_id"] = tg_id

            await update.message.reply_text(
                f"Diqqat! Bot sizga bergan aniq miqdorni o'tkazing, bu sizning summangizdan farq qiladi!\n"
                f"\nKarta: 8600530490663815\n"
                f"BUNI O'TKAZMANG: {amount} UZS ❌\n"
                f"BUNI O'TKAZING: {pay_amount} UZS ✅\n"
                f"\n✅ To'lovni amalga oshirgach, 5 daqiqa ichida skrinshot yuboring!\n"
                f"⛔️ Xato miqdor yuborilsa, 15 ish kuni ichida pul qaytariladi yoki kuyadi!\n"
                f"TG_ID: {tg_id}"
            )
            context.user_data["state"] = "hisob_screenshot"
        except:
            await update.message.reply_text("Miqdorni to‘g‘ri kiriting:")

    elif state == "hisob_screenshot" and update.message.photo:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        pending_payments[user_id] = dict(context.user_data)
        info = context.user_data

        caption = (
            f"✅HISOB TOLDIRIW\n\nID: {info['tg_id']}\n💳Karta: {info['hisob_card']}\n"
            f"🆔ID: {info['hisob_id']}\n💸Miqdor: {info['pay_amount']}\n📆Vaqt: {now}"
        )
        keyboard = [[
            InlineKeyboardButton("✅ TASDIQLASH", callback_data=f"tasdiq_{user_id}"),
            InlineKeyboardButton("❌ RAD ETISH", callback_data=f"rad_{user_id}")
        ]]
        await context.bot.send_photo(
            ADMIN_CHAT_ID,
            photo=update.message.photo[-1].file_id,
            caption=caption,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        await update.message.reply_text("✅Arizangiz muvoffaqiyatli qabul qilindi, pul 10 daqiqada tushadi!")
        context.user_data.clear()

    elif state == "withdraw_id":
        context.user_data["withdraw_id"] = text
        await update.message.reply_text("💳Pul qabul qilinishi kerak bo‘lgan karta raqamingizni kiriting...")
        context.user_data["state"] = "withdraw_card"

    elif state == "withdraw_card":
        if text.isdigit():
            context.user_data["withdraw_card"] = text
            await update.message.reply_text("#️⃣ Pul chiqarish uchun berilgan maxsus 4 ta belgidan iborat kodni kiriting...")
            context.user_data["state"] = "withdraw_code"
        else:
            await update.message.reply_text("❗️Diqqat, noto‘g‘ri ma’lumot. Faqat raqam kiriting.")

    elif state == "withdraw_code":
        if len(text) <= 4:
            context.user_data["withdraw_code"] = text
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            info = context.user_data
            pending_withdrawals[user_id] = dict(info)

            caption = (
                f"➖Pul chiqarish:\n\n💳Karta: {info['withdraw_card']}\n🆔ID: {info['withdraw_id']}\n"
                f"#️⃣4 talik kod: {info['withdraw_code']}\n📆Vaqt: {now}"
            )
            keyboard = [[
                InlineKeyboardButton("✅ TASDIQLASH", callback_data=f"tasdiq_w_{user_id}"),
                InlineKeyboardButton("❌ RAD ETISH", callback_data=f"rad_w_{user_id}")
            ]]
            await context.bot.send_message(
                ADMIN_CHAT_ID,
                caption,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            await update.message.reply_text("✅Arizangiz qabul qilindi, 10 daqiqadan 10 soatgacha pul tushadi.")
            context.user_data.clear()
        else:
            await update.message.reply_text("❗️Kod faqat 4 belgidan iborat bo‘lishi kerak.")

async def admin_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("tasdiq_"):
        user_id = int(data.split("_")[1])
        if user_id in pending_payments:
            info = pending_payments.pop(user_id)
            await context.bot.send_message(
                user_id,
                f"✅Arizangiz muvoffaqiyatli bajarildi!\n💳 {info['hisob_card']}\n💰 {info['pay_amount']} so‘m"
            )

    elif data.startswith("rad_"):
        user_id = int(data.split("_")[1])
        await context.bot.send_message(
            user_id,
            "❌ Arizangiz rad etildi. Iltimos, @xbetkassauz1 bilan bog‘laning."
        )

    elif data.startswith("tasdiq_w_"):
        user_id = int(data.split("_")[2])
        if user_id in pending_withdrawals:
            await context.bot.send_message(
                user_id,
                "✅Arizangiz muvoffaqiyatli bajarildi. Pul kartangizga tushdi."
            )

    elif data.startswith("rad_w_"):
        user_id = int(data.split("_")[2])
        await context.bot.send_message(
            user_id,
            "❌ Arizangiz rad etildi. Iltimos, @xbetkassauz1 bilan bog‘laning."
        )

    await query.message.edit_reply_markup(reply_markup=None)

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler, pattern="^(hisob_tol|pul_chiqar|operator|back_to_menu|tolov_1xbetuzs)$"))
    app.add_handler(CallbackQueryHandler(admin_response, pattern="^(tasdiq_|rad_|tasdiq_w_|rad_w_).+"))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, message_handler))
    app.run_polling()

if __name__ == "__main__":
    main()
