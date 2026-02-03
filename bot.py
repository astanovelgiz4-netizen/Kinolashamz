from aiogram import Bot, Dispatcher, executor, types
import sqlite3, random

TOKEN = "8561825405:AAHajSoNKlop2WXFwV_2NEw4-75x4W5fFfc"
ADMIN_ID = 6884014716
CHANNEL = "@kinolashamz"   # majburiy obuna kanali

bot = Bot(TOKEN)
dp = Dispatcher(bot)

# ===== DATABASE =====
db = sqlite3.connect("films.db")
sql = db.cursor()

sql.execute("""CREATE TABLE IF NOT EXISTS films(
code TEXT PRIMARY KEY,
title TEXT,
file_id TEXT,
views INTEGER DEFAULT 0
)""")

sql.execute("""CREATE TABLE IF NOT EXISTS saved(
user_id INTEGER,
code TEXT
)""")

sql.execute("""CREATE TABLE IF NOT EXISTS orders(
user_id INTEGER,
text TEXT
)""")

db.commit()

# ===== KEYBOARDS =====
menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
menu.add("🔎 Film qidirish")
menu.add("🔥 Top filmlar", "⭐ Saqlangan")
menu.add("📩 Murojaat")

search_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
search_menu.add("📂 Barcha filmlar")
search_menu.add("🎲 Tasodifiy film")
search_menu.add("📝 Film buyurtma")
search_menu.add("🔙 Bosh menu")

# ===== OBUNA TEKSHIRISH =====
async def check_sub(user_id):
    try:
        m = await bot.get_chat_member(CHANNEL, user_id)
        return m.status != "left"
    except:
        return False

# ===== START =====
@dp.message_handler(commands=["start"])
async def start(msg: types.Message):
    if not await check_sub(msg.from_user.id):
        btn = types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton(
                "➕ Obuna bo‘lish",
                url=f"https://t.me/{kinolashamz[1:]}"
            )
        )
        await msg.answer("❗ Avval kanalga obuna bo‘ling", reply_markup=btn)
        return
    await msg.answer("🎬 FILMDAMIZ BOT\n\nKino kodini yuboring", reply_markup=menu)

# ===== KOD ORQALI FILM =====
@dp.message_handler(lambda m: m.text.isdigit())
async def film_by_code(msg: types.Message):
    f = sql.execute("SELECT * FROM films WHERE code=?", (msg.text,)).fetchone()
    if not f:
        await msg.answer("❌ Film topilmadi")
        return

    await msg.answer_video(f[2], caption=f"🎬 {f[1]}")
    sql.execute("UPDATE films SET views=views+1 WHERE code=?", (msg.text,))
    db.commit()

# ===== TOP =====
@dp.message_handler(text="🔥 Top filmlar")
async def top(msg: types.Message):
    films = sql.execute("SELECT title,views FROM films ORDER BY views DESC LIMIT 10").fetchall()
    if not films:
        await msg.answer("Film yo‘q")
        return
    text = "🔥 TOP FILMLAR\n\n"
    for f in films:
        text += f"🎬 {f[0]} — 👁 {f[1]}\n"
    await msg.answer(text)

# ===== SAQLANGAN =====
@dp.message_handler(text="⭐ Saqlangan")
async def saved(msg: types.Message):
    films = sql.execute("""
    SELECT films.title FROM films
    JOIN saved ON films.code=saved.code
    WHERE saved.user_id=?
    """, (msg.from_user.id,)).fetchall()

    if not films:
        await msg.answer("⭐ Saqlangan yo‘q")
        return

    text = "⭐ Saqlangan filmlar:\n\n"
    for f in films:
        text += f"🎬 {f[0]}\n"
    await msg.answer(text)

# ===== QIDIRISH =====
@dp.message_handler(text="🔎 Film qidirish")
async def search(msg: types.Message):
    await msg.answer("Qidiruv menyusi:", reply_markup=search_menu)

@dp.message_handler(text="📂 Barcha filmlar")
async def all_films(msg: types.Message):
    films = sql.execute("SELECT code,title FROM films").fetchall()
    if not films:
        await msg.answer("Film yo‘q")
        return
    text = "🎬 Barcha filmlar:\n\n"
    for f in films:
        text += f"{f[0]} — {f[1]}\n"
    await msg.answer(text)

@dp.message_handler(text="🎲 Tasodifiy film")
async def random_film(msg: types.Message):
    films = sql.execute("SELECT * FROM films").fetchall()
    if not films:
        await msg.answer("Film yo‘q")
        return
    f = random.choice(films)
    await msg.answer_video(f[2], caption=f"🎬 {f[1]}")

@dp.message_handler(text="📝 Film buyurtma")
async def order(msg: types.Message):
    await msg.answer("✍️ Qaysi film kerak? Nomini yozing")
    dp.register_message_handler(save_order, state=None)

async def save_order(msg: types.Message):
    sql.execute("INSERT INTO orders VALUES(?,?)", (msg.from_user.id, msg.text))
    db.commit()
    await msg.answer("✅ Buyurtma qabul qilindi")

# ===== MUROJAAT =====
@dp.message_handler(text="📩 Murojaat")
async def contact(msg: types.Message):
    await msg.answer("📩 Admin: @erk1n0vee")

# ===== ADMIN PANEL =====
@dp.message_handler(commands=["panel"])
async def panel(msg: types.Message):
    if msg.from_user.id != ADMIN_ID: 6884014716
        return
    await msg.answer(
        "👑 ADMIN PANEL\n\n"
        "➕ Film qo‘shish:\n"
        "/add KOD | NOM | FILE_ID\n\n"
        "📋 Buyurtmalar:\n"
        "/orders"
    )

@dp.message_handler(commands=["add"])
async def add(msg: types.Message):
    if msg.from_user.id != ADMIN_ID: 6884014716
        return
    try:
        d = msg.text.replace("/add","").split("|")
        sql.execute("INSERT INTO films VALUES(?,?,?,0)",
        (d[0].strip(), d[1].strip(), d[2].strip()))
        db.commit()
        await msg.answer("✅ Film qo‘shildi")
    except:
        await msg.answer("❌ Xato format")

@dp.message_handler(commands=["orders"])
async def orders(msg: types.Message):
    if msg.from_user.id != ADMIN_ID: 6884014716
        return
    data = sql.execute("SELECT text FROM orders").fetchall()
    if not data:
        await msg.answer("Buyurtma yo‘q")
        return
    text = "📝 Buyurtmalar:\n\n"
    for o in data:
        text += f"• {o[0]}\n"
    await msg.answer(text)

# ===== RUN =====
executor.start_polling(dp)
