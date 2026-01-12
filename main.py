import asyncio
import json
import os
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

# ================= CONFIG =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

BALANCE_FILE = "balances.json"
USERS_FILE = "users.json"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ================= FILE HELPERS =================
def load_json(file, default):
    try:
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return default

def save_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_users():
    return load_json(USERS_FILE, [])

def load_balances():
    return load_json(BALANCE_FILE, {})

def add_balance(user_id, amount):
    balances = load_balances()
    balances[str(user_id)] = balances.get(str(user_id), 0) + amount
    save_json(BALANCE_FILE, balances)

# ================= MAIN MENU =================
async def send_main_menu(message):
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text="📂 Raqamlar katalogi"))
    kb.row(KeyboardButton(text="💰 Balansim"))
    kb.row(KeyboardButton(text="➕ Balans to‘ldirish"))
    kb.row(KeyboardButton(text="👫 Referal orqali taklif qilish"))
    kb.row(KeyboardButton(text="📞 Admin bilan bog‘lanish"))

    await message.answer(
        "👋 Assalomu alaykum!\n\n"
        "Virtual raqamlar savdosi botiga xush kelibsiz.\n\n"
        "Kerakli bo‘limni tanlang:",
        reply_markup=kb.as_markup(resize_keyboard=True)
    )

# ================= START =================
@dp.message(F.text.startswith("/start"))
async def start(message: types.Message):
    users = load_users()
    referrer_id = None

    args = message.text.split()
    if len(args) > 1:
        try:
            referrer_id = int(args[1])
        except:
            pass

    if any(u["id"] == message.from_user.id for u in users):
        await send_main_menu(message)
        return

    users.append({
        "id": message.from_user.id,
        "username": message.from_user.username,
        "phone": None,
        "referrer_id": referrer_id,
        "joined_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    save_json(USERS_FILE, users)

    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True))

    await message.answer(
        "📱 Telefon raqamingizni yuboring:",
        reply_markup=kb.as_markup(resize_keyboard=True)
    )

# ================= CONTACT =================
@dp.message(F.contact)
async def contact_handler(message: types.Message):
    users = load_users()
    user = next(u for u in users if u["id"] == message.from_user.id)
    user["phone"] = message.contact.phone_number
    save_json(USERS_FILE, users)

    if user["referrer_id"]:
        add_balance(user["referrer_id"], 4000)
        add_balance(user["id"], 4000)

    await send_main_menu(message)

# ================= BALANS =================
@dp.message(F.text == "💰 Balansim")
async def balance(message):
    bal = load_balances().get(str(message.from_user.id), 0)
    await message.answer(f"💰 Balansingiz: {bal} so‘m")

# ================= TOPUP =================
@dp.message(F.text == "➕ Balans to‘ldirish")
async def topup(message):
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text="⬅️ Ortga"))
    await message.answer(
        "💳 Karta: 9860 1701 0555 2518\n"
        "Ism: S.M\n\n"
        "📸 To‘lovdan so‘ng screenshot yuboring",
        reply_markup=kb.as_markup(resize_keyboard=True)
    )

# ================= REFERAL =================
@dp.message(F.text == "👫 Referal orqali taklif qilish")
async def referral(message):
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text="⬅️ Ortga"))
    await message.answer(
        f"🔗 Referal link:\nhttps://t.me/YOUR_BOT?start={message.from_user.id}",
        reply_markup=kb.as_markup(resize_keyboard=True)
    )

# ================= CATALOG =================
PRICES = {
    "India": 18000,
    "USA": 20000,
    "Canada": 20000,
    "Uzbekistan": 25000,
    "UK": 25000,
    "Turkey": 28000
}

@dp.message(F.text == "📂 Raqamlar katalogi")
async def catalog(message):
    kb = InlineKeyboardBuilder()
    for c, p in PRICES.items():
        kb.button(text=f"{c} – {p}", callback_data=f"order_{c}")
    kb.adjust(2)
    await message.answer("🌍 Davlatni tanlang:", reply_markup=kb.as_markup())

# ================= ORDER =================
@dp.callback_query(F.data.startswith("order_"))
async def order(call: types.CallbackQuery):
    country = call.data.replace("order_", "")
    await call.message.answer(
        f"🆕 Buyurtma qabul qilindi\n🌍 {country}\n\n"
        "Raqam tayyor bo‘lgach yuboriladi."
    )
    await bot.send_message(
        ADMIN_ID,
        f"🆕 BUYURTMA\n👤 {call.from_user.id}\n🌍 {country}"
    )

# ================= SEND NUMBER CONFIRM =================
@dp.message(F.text.startswith("/send_number"))
async def send_number(message):
    if message.from_user.id != ADMIN_ID:
        return

    _, user_id, number = message.text.split(maxsplit=2)
    user_id = int(user_id)

    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Raqamni oldim", callback_data="number_ok")
    kb.button(text="❌ Raqam kelmadi", callback_data="number_fail")

    await bot.send_message(
        user_id,
        f"📞 Sizning raqamingiz:\n{number}",
        reply_markup=kb.as_markup()
    )

# ================= CONFIRM CALLBACK =================
@dp.callback_query(F.data == "number_ok")
async def number_ok(call):
    await call.message.answer("✅ Tasdiqlandi")
    await bot.send_message(ADMIN_ID, f"✅ Mijoz {call.from_user.id} raqamni oldi")

@dp.callback_query(F.data == "number_fail")
async def number_fail(call):
    await call.message.answer("❌ Admin bilan bog‘lanilmoqda")
    await bot.send_message(
        ADMIN_ID,
        f"❌ Mijoz {call.from_user.id} raqam olmadim dedi"
    )

# ================= SCREENSHOT =================
@dp.message(F.photo)
async def screenshot(message):
    await bot.send_photo(
        ADMIN_ID,
        message.photo[-1].file_id,
        caption=f"🧾 To‘lov screenshot\n👤 {message.from_user.id}"
    )
    await message.answer("✅ Screenshot qabul qilindi")

# ================= BACK =================
@dp.message(F.text == "⬅️ Ortga")
async def back(message):
    await send_main_menu(message)

# ================= MAIN =================
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
