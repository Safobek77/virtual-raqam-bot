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

# ================= USERS =================
def load_users():
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def save_user(user: types.User, phone=None, referrer_id=None):
    users = load_users()
    existing_user = next((u for u in users if u["id"] == user.id), None)

    if not existing_user:
        users.append({
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "phone": phone,
            "joined_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "referrer_id": referrer_id
        })
        save_users(users)
        return True
    return False

# ================= BALANCE =================
def load_balances():
    try:
        with open(BALANCE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_balances(balances):
    with open(BALANCE_FILE, "w", encoding="utf-8") as f:
        json.dump(balances, f, ensure_ascii=False, indent=2)

def add_balance(user_id, amount):
    balances = load_balances()
    balances[str(user_id)] = balances.get(str(user_id), 0) + amount
    save_balances(balances)

# ================= /START =================
@dp.message(F.text == "/start")
async def start(message: types.Message):
    users = load_users()
    referrer_id = None
    if message.get_args():  # /start 12345
        try:
            referrer_id = int(message.get_args())
        except:
            referrer_id = None

    user_already_saved = any(u["id"] == message.from_user.id for u in users)

    if not user_already_saved:
        kb = ReplyKeyboardBuilder()
        kb.row(KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True))
        await message.answer(
            "Assalomu alaykum 👋\n\n"
            "Avvalo, sizning telefon raqamingizni olishimiz kerak, "
            "bu soxta akkauntlardan foydalanishni oldini oladi.\n\n"
            "📱 Quyidagi tugma orqali raqamingizni yuboring:",
            reply_markup=kb.as_markup(resize_keyboard=True)
        )
        # Referal id saqlashni keyin telefon kelganda qilamiz
        return

    await send_main_menu(message)

# ================= MAIN MENU =================
async def send_main_menu(message: types.Message):
    kb = ReplyKeyboardBuilder()
    # Balansim va Balans to'ldirish 1 qatorda
    kb.row(
        KeyboardButton(text="💰 Balansim"),
        KeyboardButton(text="➕ Balans to‘ldirish")
    )
    kb.row(KeyboardButton(text="📂 Raqamlar katalogi"))
    kb.row(KeyboardButton(text="📞 Admin bilan bog‘lanish"))

    await message.answer(
        "Assalomu alaykum 👋\n\n"
        "🇺🇿🇺🇸🇮🇳🇷🇺🇨🇦🇹🇷\n"
        "Telegram uchun virtual raqamlar savdosi.\n\n"
        "Kerakli bo‘limni tanlang:",
        reply_markup=kb.as_markup(resize_keyboard=True)
    )

# ================= TELEFON QABUL QILISH =================
@dp.message(F.content_type == "contact")
async def handle_contact(message: types.Message):
    phone = message.contact.phone_number
    users = load_users()
    user_data = next((u for u in users if u["id"] == message.from_user.id), None)
    referrer_id = user_data["referrer_id"] if user_data else None

    save_user(message.from_user, phone=phone, referrer_id=referrer_id)

    if referrer_id and referrer_id != message.from_user.id:
        add_balance(referrer_id, 4000)
        add_balance(message.from_user.id, 4000)
        await message.answer("✅ Sizning va sizni taklif qilgan odamning balansiga 4000 so‘m qo‘shildi!")

    await message.answer("✅ Telefon raqamingiz qabul qilindi.")
    await send_main_menu(message)

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
PRICES = {
    "India": 18000,
    "USA": 20000,
    "Canada": 20000,
    "Uzbekistan": 25000,
    "UK": 25000,
    "Turkey": 28000
}

@dp.callback_query(F.data.startswith("country_"))
async def handle_country(call: types.CallbackQuery):
    country = call.data.replace("country_", "")
    balances = load_balances()
    user_balance = balances.get(str(call.from_user.id), 0)
    price = PRICES.get(country, 0)

    if country == "Other" or not price:
        await call.message.answer("📩 Kerakli davlat bo‘yicha admin bilan bog‘laning.")
        return

    if user_balance < price:
        await send_topup_menu(call.message, price)
        return

    await call.message.answer(
        f"✅ Buyurtma qabul qilindi\n🌍 {country}\n💰 Balansingiz: {user_balance} so‘m\n\n"
        "‼️ Raqamni telegramga hoziroq kiriting va biz sizga kodni jo'natamiz ‼️"
    )

    await bot.send_message(
        ADMIN_ID,
        f"🆕 BUYURTMA\n👤 {call.from_user.id}\n🌍 {country}\n💰 Balans: {user_balance}"
    )

# ================= TOPUP/REFERRAL MENU =================
def build_topup_keyboard():
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text="💳 Balans to‘ldirish"),
           KeyboardButton(text="👫 Referal orqali taklif qilish"))
    kb.row(KeyboardButton(text="⬅️ Ortga"))
    return kb.as_markup(resize_keyboard=True)

async def send_topup_menu(message, price_needed):
    await message.answer(
        f"❌ Sizda yetarli balans yo‘q. Raqam narxi: {price_needed} so‘m.\n\n"
        "Siz balansni to‘ldirishingiz yoki referal orqali odamlarni taklif qilishingiz mumkin:",
        reply_markup=build_topup_keyboard()
    )

# ================= BALANS =================
@dp.message(F.text == "💰 Balansim")
async def show_balance(message: types.Message):
    balances = load_balances()
    balance = balances.get(str(message.from_user.id), 0)
    await message.answer(f"💰 Sizning balansingiz: {balance} so‘m")

# ================= BALANS TO'LDIRISH =================
@dp.message(F.text.in_(["➕ Balans to‘ldirish", "💳 Balans to‘ldirish"]))
async def topup(message: types.Message):
    await message.answer(
        "💳 Balans to‘ldirish uchun karta:\n\n"
        "9860 1701 0555 2518\nIsm: S.M\n\n"
        "📸 To‘lovdan so‘ng screenshot yuboring",
        reply_markup=ReplyKeyboardBuilder()
            .row(KeyboardButton(text="⬅️ Ortga"))
            .as_markup(resize_keyboard=True)
    )

# ================= REFERAL =================
@dp.message(F.text == "👫 Referal orqali taklif qilish")
async def send_referral(message: types.Message):
    ref_link = f"https://t.me/YOUR_BOT_USERNAME?start={message.from_user.id}"
    await message.answer(
        f"📢 Sizning referal ssilkingiz:\n{ref_link}\n\n"
        "Do‘stlaringiz ushbu ssilk orqali start bersa, siz va do‘stingiz 4000 so‘m balansga ega bo‘lasiz!",
        reply_markup=ReplyKeyboardBuilder()
            .row(KeyboardButton(text="⬅️ Ortga"))
            .as_markup(resize_keyboard=True)
    )

# ================= ORTGA =================
@dp.message(F.text == "⬅️ Ortga")
async def go_back(message: types.Message):
    await send_main_menu(message)

# ================= SCREENSHOT =================
@dp.message(F.photo)
async def screenshot(message: types.Message):
    await message.answer("✅ Screenshot qabul qilindi, tekshirilmoqda.")
    await bot.send_photo(
        ADMIN_ID,
        message.photo[-1].file_id,
        caption=(
            f"🧾 To‘lov screenshot\n👤 ID: {message.from_user.id}\n👤 @{message.from_user.username}"
        )
    )

# ================= ADMIN: ADD BALANCE =================
@dp.message(F.text.startswith("/add_balance"))
async def admin_add_balance(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        _, user_id, amount = message.text.split()
        user_id = int(user_id)
        amount = int(amount)
    except:
        await message.reply("❌ Format: /add_balance USER_ID SUMMA")
        return
    add_balance(user_id, amount)
    await message.reply("✅ Balans qo‘shildi")
    await bot.send_message(user_id, f"💰 Balansingiz +{amount} so‘m")

# ================= ADMIN: SEND NUMBER =================
@dp.message(F.text.startswith("/send_number"))
async def admin_send_number(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        _, user_id, number = message.text.split(maxsplit=2)
        user_id = int(user_id)
    except:
        await message.reply("❌ Format: /send_number USER_ID +998901234567")
        return
    text = f"📞 Sizning raqamingiz:\n{number}\n\n‼️ Raqamni telegramga hoziroq kiriting va biz sizga kodni jo'natamiz ‼️"
    await bot.send_message(user_id, text)
    await message.reply("✅ Raqam yuborildi")

# ================= ADMIN: SEND CODE =================
@dp.message(F.text.startswith("/send_code"))
async def admin_send_code(message: types.Message):
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

# ================= ADMIN: BROADCAST =================
@dp.message(F.text.startswith("/broadcast"))
async def admin_broadcast(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        _, *text_parts = message.text.split()
        broadcast_text = " ".join(text_parts)
        if not broadcast_text:
            await message.reply("❌ Format: /broadcast XABAR")
            return
    except:
        await message.reply("❌ Format: /broadcast XABAR")
        return
    users = load_users()
    sent_count = 0
    for user in users:
        try:
            await bot.send_message(user["id"], broadcast_text)
            sent_count += 1
        except:
            pass
    await message.reply(f"✅ Xabar {sent_count} foydalanuvchiga yuborildi")

# ================= MAIN =================
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
