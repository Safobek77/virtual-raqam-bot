import asyncio
import json
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

# ================= CONFIG =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
BALANCE_FILE = "balances.json"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ================= USER SAQLASH =================
def save_user(user):
    try:
        with open("users.json", "r") as f:
            users = json.load(f)
    except:
        users = []

    if not any(u["id"] == user.id for u in users):
        users.append({
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name
        })
        with open("users.json", "w") as f:
            json.dump(users, f, indent=2)

# ================= BALANS =================
def load_balances():
    try:
        with open(BALANCE_FILE) as f:
            return json.load(f)
    except:
        return {}

def save_balances(data):
    with open(BALANCE_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ================= /start =================
@dp.message(F.text == "/start")
async def start(message: types.Message):
    save_user(message.from_user)
    kb = ReplyKeyboardBuilder()
    kb.add(KeyboardButton(text="📂 Raqamlar katalogi"))
    kb.add(KeyboardButton(text="💰 Balansim"))
    kb.add(KeyboardButton(text="➕ Balans to‘ldirish"))
    kb.add(KeyboardButton(text="📞 Admin bilan bog‘lanish"))
    await message.answer(
        "Xush kelibsiz 👋",
        reply_markup=kb.as_markup(resize_keyboard=True)
    )

# ================= ADMIN BILAN BOG‘LANISH =================
@dp.message(F.text == "📞 Admin bilan bog‘lanish")
async def contact_admin(message: types.Message):
    await bot.send_message(
        ADMIN_ID,
        f"📩 Murojaat\n"
        f"👤 @{message.from_user.username}\n"
        f"🆔 {message.from_user.id}"
    )
    await message.answer("✅ Xabaringiz admin’ga yuborildi")

# ================= KATALOG =================
@dp.message(F.text == "📂 Raqamlar katalogi")
async def catalog(message: types.Message):
    kb = InlineKeyboardBuilder()
    kb.row(
        InlineKeyboardButton(text="🇺🇸 USA", callback_data="country_USA"),
        InlineKeyboardButton(text="🇮🇳 India", callback_data="country_India")
    )
    await message.answer("🌍 Davlatni tanlang:", reply_markup=kb.as_markup())

@dp.callback_query(F.data.startswith("country_"))
async def order(call: types.CallbackQuery):
    country = call.data.replace("country_", "")
    await call.message.answer("✅ Buyurtma qabul qilindi. Admin bog‘lanadi.")
    await bot.send_message(
        ADMIN_ID,
        f"🆕 Buyurtma\n"
        f"👤 {call.from_user.id}\n"
        f"🌍 {country}"
    )

# ================= BALANS =================
@dp.message(F.text == "💰 Balansim")
async def balance(message: types.Message):
    balances = load_balances()
    await message.answer(f"💰 Balans: {balances.get(str(message.from_user.id), 0)} so‘m")

# ================= SCREENSHOT =================
@dp.message(F.photo)
async def screenshot(message: types.Message):
    await bot.send_photo(
        ADMIN_ID,
        message.photo[-1].file_id,
        caption=f"🧾 Screenshot\n👤 {message.from_user.id}"
    )
    await message.answer("✅ Screenshot qabul qilindi")

# ================= ADMIN: RAQAM =================
@dp.message(F.text.startswith("/send_number"))
async def send_number(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    _, user_id, number = message.text.split(maxsplit=2)

    text = (
        f"📞 Sizning raqamingiz:\n"
        f"{number}\n\n"
        f"‼️ Raqamni telegramga hoziroq kiriting va biz sizga kodni jo'natamiz ‼️"
    )

    await bot.send_message(int(user_id), text)
    await message.answer("✅ Raqam yuborildi")

# ================= ADMIN: KOD =================
@dp.message(F.text.startswith("/send_code"))
async def send_code(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    _, user_id, code = message.text.split(maxsplit=2)

    await bot.send_message(
        int(user_id),
        f"🔐 Tasdiqlash kodi:\n{code}"
    )
    await message.answer("✅ Kod yuborildi")

# ================= ADMIN: ODDIY XABAR =================
@dp.message(F.text.startswith("/msg"))
async def admin_msg(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    _, user_id, text = message.text.split(maxsplit=2)
    await bot.send_message(int(user_id), f"✉️ Admin:\n{text}")
    await message.answer("✅ Xabar yuborildi")

# ================= MAIN =================
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

