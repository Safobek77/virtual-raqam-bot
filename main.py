import asyncio
import json
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

# ================= CONFIG =================
BOT_TOKEN = os.getenv("BOT_TOKEN")              # Bu yerga bot tokeningni yoz
ADMIN_ID = int(os.getenv("ADMIN_ID"))           # Bu yerga o'zingning Telegram ID
BALANCE_FILE = "balances.json"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ================= BALANS FUNKSIYALARI =================
def load_balances():
    try:
        with open(BALANCE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_balances(balances):
    with open(BALANCE_FILE, "w", encoding="utf-8") as f:
        json.dump(balances, f, ensure_ascii=False, indent=2)

# ================= /start VA ASOSIY TUGMALAR =================
@dp.message(F.text == "/start")
async def send_welcome(message: types.Message):
    kb = ReplyKeyboardBuilder()
    kb.add(KeyboardButton(text="📂 Raqamlar katalogi"))
    kb.add(KeyboardButton(text="💰 Balansim"))
    kb.add(KeyboardButton(text="➕ Balans to‘ldirish"))
    keyboard = kb.as_markup(resize_keyboard=True)
    await message.answer(
        "Assalomu alaykum!\n\n"
	"🇺🇿🇺🇸🇮🇳🇷🇺🇨🇦🇹🇷\n"
        "USA va boshqa davlatlar uchun virtual Telegram raqamlarini xarid qiling.\n\n"
        "Pastdagi tugmalardan foydalaning:",
        reply_markup=keyboard
    )

# ================= TUGMALAR FUNKSIYALARI =================
@dp.message(F.text == "📂 Raqamlar katalogi")
async def show_catalog(message: types.Message):
    kb = InlineKeyboardBuilder()
    kb.row(
        InlineKeyboardButton(text="🇺🇸 USA", callback_data="country_USA"),
        InlineKeyboardButton(text="🇨🇦 Kanada", callback_data="country_Canada")
    )
    kb.row(
        InlineKeyboardButton(text="🇺🇿 O‘zbekiston", callback_data="country_Uzbekistan"),
        InlineKeyboardButton(text="🇮🇳 India", callback_data="country_India")
    )
    kb.row(
        InlineKeyboardButton(text="🇬🇧 UK", callback_data="country_UK"),
        InlineKeyboardButton(text="🇹🇷 Turkiya", callback_data="country_Turkey")
    )
    kb.row(
        InlineKeyboardButton(text="📩 Boshqa davlat", callback_data="country_Other")
    )
    inline_keyboard = kb.as_markup()
    await message.answer(
    "📂 Davlatni tanlang:\n"
    "Barcha raqamlar spamsiz!\n\n"
    "🇮🇳 India - 18000 so'm\n"
    "🇺🇸 USA - 20000 so'm\n"
    "🇨🇦 Kanada - 20000 so'm\n"
    "🇺🇿 O‘zbekiston - 25000 so'm\n"
    "🇬🇧 UK - 25000 so'm\n"
    "🇹🇷 Turkiya - 28000 so'm",
    reply_markup=inline_keyboard
)

@dp.message(F.text == "💰 Balansim")
async def show_balance(message: types.Message):
    balances = load_balances()
    user_balance = balances.get(str(message.from_user.id), 0)
    await message.answer(f"💰 Sizning balansingiz: {user_balance} so‘m")

@dp.message(F.text == "➕ Balans to‘ldirish")
async def balance_topup(message: types.Message):
    await message.answer(
        "💳 Balans to‘ldirish uchun karta:\n\n"
        "9860170105552518\n"
        "Ism: S.M\n\n"
        "📸 To‘lovdan keyin screenshot yuboring"
    )

# ================= INLINE CALLBACK FUNKSIYALARI =================
@dp.callback_query()
async def handle_country(call: types.CallbackQuery):
    country = call.data.replace("country_", "")
    if country == "Other":
        await call.message.answer(
            f"📩 Kerakli davlat yo‘qmi? Admin bilan bog‘laning: @Usa_raqamlar_virtual"
        )
    else:
        balances = load_balances()
        user_balance = balances.get(str(call.from_user.id), 0)
        await call.message.answer(
            f"✅ Buyurtma qabul qilindi\n"
            f"🌍 Davlat: {country}\n"
            f"💰 Balansingiz: {user_balance} so‘m\n"
            "⏳ Admin siz bilan bog‘lanadi"
        )
        await bot.send_message(
            ADMIN_ID,
            f"📥 Yangi buyurtma\n"
            f"👤 User ID: {call.from_user.id}\n"
            f"👤 Username: @{call.from_user.username}\n"
            f"🌍 Davlat: {country}\n"
            f"💰 Balans: {user_balance} so‘m"
        )

# ================= SCREENSHOT QABUL QILISH =================
@dp.message(F.photo)
async def handle_screenshot(message: types.Message):
    await message.answer(
        "✅ Screenshot qabul qilindi.\n"
        "⏳ Tekshiruvdan so‘ng balansingiz to‘ldiriladi."
    )
    await bot.send_photo(
        chat_id=ADMIN_ID,
        photo=message.photo[-1].file_id,
        caption=(
            f"🧾 Yangi to‘lov screenshot\n"
            f"👤 User ID: {message.from_user.id}\n"
            f"👤 Username: @{message.from_user.username}"
        )
    )

# ================= ADMIN /add_balance =================
@dp.message(F.text.startswith("/add_balance"))
async def add_balance(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        _, user_id_str, amount_str = message.text.split()
        user_id = int(user_id_str)
        amount = int(amount_str)
    except Exception:
        await message.reply("❌ Format xato! Misol: /add_balance 123456789 50000")
        return
    balances = load_balances()
    balances[str(user_id)] = balances.get(str(user_id), 0) + amount
    save_balances(balances)
    await message.reply(f"✅ {user_id} foydalanuvchining balansi +{amount} qo‘shildi")
    try:
        await bot.send_message(user_id, f"💰 Sizning balansingiz +{amount} so‘mga to‘ldirildi!")
    except:
        pass

# ================= ADMIN /take_balance =================
@dp.message(F.text.startswith("/take_balance"))
async def take_balance(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        _, user_id_str, amount_str = message.text.split()
        user_id = int(user_id_str)
        amount = int(amount_str)
    except Exception:
        await message.reply("❌ Format xato! Misol: /take_balance 123456789 50000")
        return
    balances = load_balances()
    if balances.get(str(user_id), 0) < amount:
        await message.reply(f"❌ Foydalanuvchi balansida yetarli mablag‘ yo‘q")
        return
    balances[str(user_id)] -= amount
    save_balances(balances)
    await message.reply(f"✅ {amount} so‘m foydalanuvchi balansidan yechildi")
    try:
        await bot.send_message(user_id, f"💸 {amount} so‘m balansingizdan yechildi")
    except:
        pass

# ================= ADMIN /send_number =================
@dp.message(F.text.startswith("/send_number"))
async def send_number(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        parts = message.text.split(maxsplit=2)
        user_id = int(parts[1])
        number_info = parts[2]
    except Exception:
        await message.reply("❌ Format xato! Misol: /send_number 123456789 Raqam: +1 234567890 Kod: 1234")
        return
    await bot.send_message(user_id, f"📞 Sizga raqam va kod yuborildi:\n{number_info}")
    await message.reply("✅ Raqam foydalanuvchiga yuborildi")

# ================= MAIN =================
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
