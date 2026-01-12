import asyncio
import json
import os
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

# ================= CONFIG =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID_STR = os.getenv("ADMIN_ID")
ADMIN_ID = int(ADMIN_ID_STR) if ADMIN_ID_STR else None

BALANCE_FILE = "balances.json"
USERS_FILE = "users.json"

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is required")
if not ADMIN_ID:
    raise ValueError("ADMIN_ID environment variable is required")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ================= USER SAQLASH =================
def save_user(user: types.User):
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            users = json.load(f)
    except:
        users = []

    if not any(u["id"] == user.id for u in users):
        users.append({
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "joined_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, ensure_ascii=False, indent=2)

# ================= BALANS =================
def load_balances():
    try:
        with open(BALANCE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_balances(balances):
    with open(BALANCE_FILE, "w", encoding="utf-8") as f:
        json.dump(balances, f, ensure_ascii=False, indent=2)

# ================= /START =================
@dp.message(F.text == "/start")
async def start(message: types.Message):
    save_user(message.from_user)

    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text="📂 Raqamlar katalogi"))
    kb.row(KeyboardButton(text="💰 Balansim"))
    kb.row(KeyboardButton(text="➕ Balans to‘ldirish"))
    kb.row(KeyboardButton(text="📞 Admin bilan bog‘lanish"))

    await message.answer(
        "Assalomu alaykum 👋\n\n"
        "🇺🇿🇺🇸🇮🇳🇷🇺🇨🇦🇹🇷\n"
        "Telegram uchun virtual raqamlar savdosi.\n\n"
        "Kerakli bo‘limni tanlang:",
        reply_markup=kb.as_markup(resize_keyboard=True)
    )

# ================= ADMIN BILAN BOG‘LANISH =================
@dp.message(F.text == "📞 Admin bilan bog‘lanish")
async def contact_admin(message: types.Message):
    await bot.send_message(
        ADMIN_ID,
        f"📩 Yangi murojaat\n\n"
        f"👤 @{message.from_user.username}\n"
        f"🆔 ID: {message.from_user.id}"
    )
    await message.answer("✅ Admin xabardor qilindi, tez orada javob beramiz.")

# ================= KATALOG =================
@dp.message(F.text == "📂 Raqamlar katalogi")
async def show_catalog(message: types.Message):
    kb = InlineKeyboardBuilder()
    # 2 ta qatorda 2 ta tugma
    kb.row(
        InlineKeyboardButton(text="🇮🇳 India", callback_data="country_India"),
        InlineKeyboardButton(text="🇺🇸 USA", callback_data="country_USA")
    )
    kb.row(
        InlineKeyboardButton(text="🇨🇦 Kanada", callback_data="country_Canada"),
        InlineKeyboardButton(text="🇺🇿 O‘zbekiston", callback_data="country_Uzbekistan")
    )
    kb.row(
        InlineKeyboardButton(text="🇬🇧 UK", callback_data="country_UK"),
        InlineKeyboardButton(text="🇹🇷 Turkiya", callback_data="country_Turkey")
    )
    kb.row(
        InlineKeyboardButton(text="📩 Boshqa davlat", callback_data="country_Other")
    )

    await message.answer(
        "📂 Davlatni tanlang:\n\n"
        "🇮🇳 India — 18 000 so‘m\n"
        "🇺🇸 USA — 20 000 so‘m\n"
        "🇨🇦 Kanada — 20 000 so‘m\n"
        "🇺🇿 O‘zbekiston — 25 000 so‘m\n"
        "🇬🇧 UK — 25 000 so‘m\n"
        "🇹🇷 Turkiya — 28 000 so‘m\n\n"
        "✅ Barcha raqamlar spamsiz",
        reply_markup=kb.as_markup()
    )

# ================= BUYURTMA =================
@dp.callback_query(F.data.startswith("country_"))
async def handle_country(call: types.CallbackQuery):
    country = call.data.replace("country_", "")
    balances = load_balances()
    user_balance = balances.get(str(call.from_user.id), 0)

    if country == "Other":
        await call.message.answer("📩 Kerakli davlat bo‘yicha admin bilan bog‘laning.")
        return

    await call.message.answer(
        f"✅ Buyurtma qabul qilindi\n"
        f"🌍 Davlat: {country}\n"
        f"💰 Balansingiz: {user_balance} so‘m\n\n"
        "‼️ Raqamni telegramga hoziroq kiriting va biz sizga kodni jo'natamiz ‼️"
    )

    await bot.send_message(
        ADMIN_ID,
        f"🆕 Yangi buyurtma\n\n"
        f"👤 ID: {call.from_user.id}\n"
        f"👤 @{call.from_user.username}\n"
        f"🌍 Davlat: {country}\n"
        f"💰 Balans: {user_balance} so‘m"
    )

# ================= BALANS =================
@dp.message(F.text == "💰 Balansim")
async def show_balance(message: types.Message):
    balances = load_balances()
    balance = balances.get(str(message.from_user.id), 0)
    await message.answer(f"💰 Sizning balansingiz: {balance} so‘m")

# ================= BALANS TO‘LDIRISH =================
@dp.message(F.text == "➕ Balans to‘ldirish")
async def topup(message: types.Message):
    await message.answer(
        "💳 Balans to‘ldirish uchun karta:\n\n"
        "9860 1701 0555 2518\n"
        "Ism: S.M\n\n"
        "📸 To‘lovdan so‘ng screenshot yuboring"
    )

# ================= SCREENSHOT =================
@dp.message(F.photo)
async def screenshot(message: types.Message):
    await message.answer("✅ Screenshot qabul qilindi, tekshirilmoqda.")

    await bot.send_photo(
        ADMIN_ID,
        message.photo[-1].file_id,
        caption=(
            f"🧾 To‘lov screenshot\n"
            f"👤 ID: {message.from_user.id}\n"
            f"👤 @{message.from_user.username}"
        )
    )

# ================= ADMIN: ADD BALANCE =================
@dp.message(F.text.startswith("/add_balance"))
async def add_balance(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    try:
        _, user_id, amount = message.text.split()
        user_id = int(user_id)
        amount = int(amount)
    except:
        await message.reply("❌ Format: /add_balance USER_ID SUMMA")
        return

    balances = load_balances()
    balances[str(user_id)] = balances.get(str(user_id), 0) + amount
    save_balances(balances)

    await message.reply("✅ Balans qo‘shildi")
    await bot.send_message(user_id, f"💰 Balansingiz +{amount} so‘m")

# ================= ADMIN: SEND NUMBER =================
@dp.message(F.text.startswith("/send_number"))
async def send_number(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    try:
        _, user_id, number = message.text.split(maxsplit=2)
        user_id = int(user_id)
    except:
        await message.reply("❌ Format: /send_number USER_ID +998901234567")
        return

    text = (
        f"📞 Sizning raqamingiz:\n"
        f"{number}\n\n"
        f"‼️ Raqamni telegramga hoziroq kiriting va biz sizga kodni jo'natamiz ‼️"
    )

    await bot.send_message(user_id, text)
    await message.reply("✅ Raqam yuborildi")

# ================= ADMIN: SEND CODE =================
@dp.message(F.text.startswith("/send_code"))
async def send_code(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    try:
        _, user_id, code = message.text.split(maxsplit=2)
        user_id = int(user_id)
    except:
        await message.reply("❌ Format: /send_code USER_ID KOD")
        return

    await bot.send_message(user_id, f"🔐 Tasdiqlash kodi:\n{code}")
    await message.reply("✅ Kod yuborildi")

# ================= ADMIN: MESSAGE =================
@dp.message(F.text.startswith("/msg"))
async def admin_msg(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    try:
        _, user_id, text = message.text.split(maxsplit=2)
        user_id = int(user_id)
    except:
        await message.reply("❌ Format: /msg USER_ID XABAR")
        return

    await bot.send_message(user_id, f"✉️ Admin:\n{text}")
    await message.reply("✅ Xabar yuborildi")

# ================= MAIN =================
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
