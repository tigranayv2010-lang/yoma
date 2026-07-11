import asyncio
import logging
import sqlite3
import os
import aiohttp
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiocryptopay import AioCryptoPay, Networks
import json

load_dotenv()
logging.basicConfig(level=logging.INFO)

# --- НАСТРОЙКИ (из .env) ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
CRYPTO_BOT_TOKEN = os.getenv("CRYPTO_BOT_TOKEN")
GORGONA_API_KEY = os.getenv("GORGONA_API_KEY")
GORGONA_BASE_URL = os.getenv("GORGONA_BASE_URL", "https://api.gorgonaboost.xyz")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
crypto_client = AioCryptoPay(token=CRYPTO_BOT_TOKEN, network=Networks.MAIN_NET)

# --- БАЗА ДАННЫХ ---
def init_db():
    conn = sqlite3.connect('bot.db')
    c = conn.cursor()
    # Таблица пользователей
    c.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, balance REAL DEFAULT 0, lang TEXT DEFAULT NULL)''')
    # Таблица настроек (для админ-панели)
    c.execute('''CREATE TABLE IF NOT EXISTS settings (id INTEGER PRIMARY KEY, price_1m REAL DEFAULT 1.5, price_3m REAL DEFAULT 3.0)''')
    c.execute("INSERT OR IGNORE INTO settings (id, price_1m, price_3m) VALUES (1, 1.5, 3.0)")
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect('bot.db')
    c = conn.cursor()
    c.execute("SELECT balance, lang FROM users WHERE user_id=?", (user_id,))
    res = c.fetchone()
    if not res:
        c.execute("INSERT INTO users (user_id, balance) VALUES (?, ?)", (user_id, 0))
        conn.commit()
        res = (0.0, None)
    conn.close()
    return res

def set_lang(user_id, lang):
    conn = sqlite3.connect('bot.db')
    c = conn.cursor()
    c.execute("UPDATE users SET lang = ? WHERE user_id=?", (lang, user_id))
    if c.rowcount == 0:
        c.execute("INSERT INTO users (user_id, balance, lang) VALUES (?, 0, ?)", (user_id, lang))
    conn.commit()
    conn.close()

def add_balance(user_id, amount):
    conn = sqlite3.connect('bot.db')
    c = conn.cursor()
    c.execute("UPDATE users SET balance = balance + ? WHERE user_id=?", (amount, user_id))
    conn.commit()
    conn.close()

def deduct_balance(user_id, amount):
    conn = sqlite3.connect('bot.db')
    c = conn.cursor()
    c.execute("UPDATE users SET balance = balance - ? WHERE user_id=?", (amount, user_id))
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect('bot.db')
    c = conn.cursor()
    c.execute("SELECT user_id FROM users")
    res = c.fetchall()
    conn.close()
    return [r[0] for r in res]

def get_settings():
    conn = sqlite3.connect('bot.db')
    c = conn.cursor()
    c.execute("SELECT price_1m, price_3m FROM settings WHERE id=1")
    res = c.fetchone()
    conn.close()
    return res

def set_price(plan, price):
    conn = sqlite3.connect('bot.db')
    c = conn.cursor()
    if plan == "1m":
        c.execute("UPDATE settings SET price_1m = ? WHERE id=1", (price,))
    else:
        c.execute("UPDATE settings SET price_3m = ? WHERE id=1", (price,))
    conn.commit()
    conn.close()

# --- ЛОКАЛИЗАЦИЯ ---
TEXTS = {
    "ru": {
        "welcome": "👋 <b>Привет! Это бот для покупки Discord бустов.</b>\n\n💳 Твой баланс: <b>{balance:.2f} USDT</b>\n\nВыбери нужное действие:",
        "btn_buy": "🛒 Купить бусты",
        "btn_topup": "💰 Пополнить баланс",
        "btn_stock": "📊 Наличие и цены",
        "stock_info": "📊 <b>Наличие и Цены:</b>\n\n📦 <b>Наличие:</b>\n1 Месяц: <b>{stock_1m} шт.</b>\n3 Месяца: <b>{stock_3m} шт.</b>\n\n💵 <b>Наши цены:</b>\n1 Месяц: <b>{price_1m} USDT</b>\n3 Месяца: <b>{price_3m} USDT</b>",
        "loading": "⏳ Загрузка...",
        "error": "❌ Произошла ошибка. Попробуйте позже.",
        "topup_ask": "Введите сумму пополнения в <b>USDT</b> (например, 1.5):",
        "topup_invalid": "❌ Введите корректное число больше нуля.",
        "topup_invoice": "🧾 Создан счет на <b>{amount} USDT</b>.\nОплатите по кнопке ниже и проверьте оплату.",
        "btn_pay": "🔗 Оплатить",
        "btn_check": "✅ Проверить оплату",
        "topup_success": "✅ <b>Успешное пополнение!</b>\nНа ваш баланс зачислено: <b>{amount} USDT</b>.",
        "topup_wait": "❌ Оплата еще не поступила. Попробуйте чуть позже.",
        "topup_not_found": "❌ Счет не найден.",
        "buy_invite": "🔗 Отправьте ссылку-приглашение на сервер (invite link):",
        "buy_plan": "📅 Выберите срок подписки:",
        "btn_1m": "1 Месяц",
        "btn_3m": "3 Месяца",
        "buy_amount": "🔢 Введите количество бустов, которое хотите купить:",
        "buy_invalid": "❌ Введите корректное целое число больше нуля.",
        "buy_no_balance": "❌ <b>Недостаточно средств!</b>\n\nСтоимость заказа: <b>{total:.2f} USDT</b>\nВаш баланс: <b>{balance:.2f} USDT</b>",
        "buy_success": "✅ <b>Заказ успешно оформлен!</b>\n\n🔗 Сервер: {invite}\n🚀 Бусты: {amount} шт.\n📅 Срок: {plan}\n💵 Списано: {total:.2f} USDT",
        "lang_changed": "✅ Язык изменен на Русский!"
    },
    "en": {
        "welcome": "👋 <b>Hello! This is a bot for buying Discord boosts.</b>\n\n💳 Your balance: <b>{balance:.2f} USDT</b>\n\nChoose an action:",
        "btn_buy": "🛒 Buy Boosts",
        "btn_topup": "💰 Top Up Balance",
        "btn_stock": "📊 Stock & Prices",
        "stock_info": "📊 <b>Stock & Prices:</b>\n\n📦 <b>Stock:</b>\n1 Month: <b>{stock_1m} pcs</b>\n3 Months: <b>{stock_3m} pcs</b>\n\n💵 <b>Our Prices:</b>\n1 Month: <b>{price_1m} USDT</b>\n3 Months: <b>{price_3m} USDT</b>",
        "loading": "⏳ Loading...",
        "error": "❌ An error occurred. Please try again later.",
        "topup_ask": "Enter the top-up amount in <b>USDT</b> (e.g., 1.5):",
        "topup_invalid": "❌ Enter a valid number greater than zero.",
        "topup_invoice": "🧾 Invoice created for <b>{amount} USDT</b>.\nPay via the button below and check payment.",
        "btn_pay": "🔗 Pay",
        "btn_check": "✅ Check Payment",
        "topup_success": "✅ <b>Top-up successful!</b>\nAdded to your balance: <b>{amount} USDT</b>.",
        "topup_wait": "❌ Payment not received yet. Try again later.",
        "topup_not_found": "❌ Invoice not found.",
        "buy_invite": "🔗 Send the server invite link:",
        "buy_plan": "📅 Choose subscription plan:",
        "btn_1m": "1 Month",
        "btn_3m": "3 Months",
        "buy_amount": "🔢 Enter the number of boosts you want to buy:",
        "buy_invalid": "❌ Enter a valid integer greater than zero.",
        "buy_no_balance": "❌ <b>Insufficient funds!</b>\n\nOrder cost: <b>{total:.2f} USDT</b>\nYour balance: <b>{balance:.2f} USDT</b>",
        "buy_success": "✅ <b>Order successfully placed!</b>\n\n🔗 Server: {invite}\n🚀 Boosts: {amount} pcs\n📅 Plan: {plan}\n💵 Deducted: {total:.2f} USDT",
        "lang_changed": "✅ Language changed to English!"
    }
}

# --- GORGONA API ---
async def gorgona_request(method, endpoint, payload=None):
    headers = {"Authorization": f"Bearer {GORGONA_API_KEY}", "Content-Type": "application/json"}
    url = f"{GORGONA_BASE_URL}{endpoint}"
    async with aiohttp.ClientSession() as session:
        if method == "GET":
            async with session.get(url, headers=headers) as resp:
                return await resp.json()
        elif method == "POST":
            async with session.post(url, headers=headers, json=payload) as resp:
                return await resp.json()

# --- СТЕЙТЫ (FSM) ---
class TopUpState(StatesGroup):
    amount = State()

class BuyBoostState(StatesGroup):
    invite = State()
    plan = State()
    amount = State()

class AdminState(StatesGroup):
    price_1m = State()
    price_3m = State()
    broadcast = State()

# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---
def main_menu(lang):
    t = TEXTS[lang]
    kb = [
        [InlineKeyboardButton(text=t["btn_buy"], callback_data="buy_boost")],
        [InlineKeyboardButton(text=t["btn_topup"], callback_data="top_up")],
        [InlineKeyboardButton(text=t["btn_stock"], callback_data="stock_prices")],
        [InlineKeyboardButton(text="🌐 RU/EN", callback_data="change_lang")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def lang_menu():
    kb = [
        [
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
            InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

# --- ОБРАБОТЧИКИ БОТА ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    balance, lang = get_user(message.from_user.id)
    
    if not lang:
        await message.answer("🇷🇺 Выберите язык / 🇬🇧 Choose language:", reply_markup=lang_menu())
        return

    t = TEXTS[lang]
    await message.answer(
        t["welcome"].format(balance=balance),
        reply_markup=main_menu(lang),
        parse_mode="HTML"
    )

@dp.callback_query(F.data.startswith("lang_"))
async def set_lang_handler(callback: types.CallbackQuery):
    lang = callback.data.split("_")[1]
    set_lang(callback.from_user.id, lang)
    await callback.answer(TEXTS[lang]["lang_changed"])
    
    balance, _ = get_user(callback.from_user.id)
    await callback.message.edit_text(
        TEXTS[lang]["welcome"].format(balance=balance),
        reply_markup=main_menu(lang),
        parse_mode="HTML"
    )

@dp.callback_query(F.data == "change_lang")
async def change_lang_handler(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.edit_text("🇷🇺 Выберите язык / 🇬🇧 Choose language:", reply_markup=lang_menu())

@dp.callback_query(F.data == "stock_prices")
async def stock_prices_handler(callback: types.CallbackQuery):
    _, lang = get_user(callback.from_user.id)
    if not lang: lang = "en"
    t = TEXTS[lang]
    
    await callback.answer()
    msg = await callback.message.answer(t["loading"])
    
    try:
        # Получаем только наличие из API
        stock_data = await gorgona_request("GET", "/stock")
        stock_1m = stock_data.get("stock", {}).get("1m", 0)
        stock_3m = stock_data.get("stock", {}).get("3m", 0)
        
        # Получаем ЦЕНЫ из нашей базы (админские цены)
        price_1m, price_3m = get_settings()
        
        text = t["stock_info"].format(
            stock_1m=stock_1m,
            stock_3m=stock_3m,
            price_1m=price_1m,
            price_3m=price_3m
        )
        await msg.edit_text(text, parse_mode="HTML")
    except Exception as e:
        logging.error(f"Stock Error: {e}")
        await msg.edit_text(t["error"], parse_mode="HTML")

# --- ПОПОЛНЕНИЕ БАЛАНСА ---
@dp.callback_query(F.data == "top_up")
async def top_up_handler(callback: types.CallbackQuery, state: FSMContext):
    _, lang = get_user(callback.from_user.id)
    if not lang: lang = "en"
    t = TEXTS[lang]
    
    await callback.answer()
    await callback.message.answer(t["topup_ask"], parse_mode="HTML")
    await state.set_state(TopUpState.amount)

@dp.message(TopUpState.amount)
async def process_top_up_amount(message: types.Message, state: FSMContext):
    _, lang = get_user(message.from_user.id)
    if not lang: lang = "en"
    t = TEXTS[lang]

    try:
        amount = float(message.text.replace(",", "."))
        if amount <= 0:
            raise ValueError
    except ValueError:
        await message.answer(t["topup_invalid"])
        return

    await state.clear()
    
    try:
        invoice = await crypto_client.create_invoice(asset='USDT', amount=amount)
        
        kb = [
            [InlineKeyboardButton(text=t["btn_pay"], url=invoice.bot_invoice_url)],
            [InlineKeyboardButton(text=t["btn_check"], callback_data=f"check_pay_{invoice.invoice_id}_{amount}")]
        ]
        markup = InlineKeyboardMarkup(inline_keyboard=kb)
        
        await message.answer(t["topup_invoice"].format(amount=amount), reply_markup=markup, parse_mode="HTML")
    except Exception as e:
        logging.error(f"Crypto Error: {e}")
        await message.answer(t["error"])

@dp.callback_query(F.data.startswith("check_pay_"))
async def check_payment(callback: types.CallbackQuery):
    _, lang = get_user(callback.from_user.id)
    if not lang: lang = "en"
    t = TEXTS[lang]

    # Формат: check_pay_INVOICEID_AMOUNT
    parts = callback.data.split("_")
    invoice_id = int(parts[2])
    amount = float(parts[3])
    
    try:
        result = await crypto_client.get_invoices(invoice_ids=invoice_id)
        
        # get_invoices может вернуть один объект или список
        if isinstance(result, list):
            if not result:
                await callback.answer(t["topup_not_found"], show_alert=True)
                return
            invoice = result[0]
        else:
            invoice = result
        
        if not invoice:
            await callback.answer(t["topup_not_found"], show_alert=True)
            return
        
        status_str = str(invoice.status).lower()
            
        if status_str == 'paid':
            add_balance(callback.from_user.id, amount)
            await callback.message.edit_text(t["topup_success"].format(amount=amount), parse_mode="HTML")
        elif status_str in ['active', 'created']:
            await callback.answer(t["topup_wait"], show_alert=True)
        else:
            await callback.answer(t["topup_wait"], show_alert=True)
    except Exception as e:
        logging.error(f"Crypto Check Error: {e}")
        await callback.answer(t["error"], show_alert=True)

# --- ПОКУПКА БУСТОВ ---
@dp.callback_query(F.data == "buy_boost")
async def buy_boost_start(callback: types.CallbackQuery, state: FSMContext):
    _, lang = get_user(callback.from_user.id)
    if not lang: lang = "en"
    t = TEXTS[lang]

    await callback.answer()
    await callback.message.answer(t["buy_invite"])
    await state.set_state(BuyBoostState.invite)

@dp.message(BuyBoostState.invite)
async def buy_boost_invite(message: types.Message, state: FSMContext):
    _, lang = get_user(message.from_user.id)
    if not lang: lang = "en"
    t = TEXTS[lang]

    await state.update_data(invite=message.text)
    
    kb = [
        [InlineKeyboardButton(text=t["btn_1m"], callback_data="plan_1m")],
        [InlineKeyboardButton(text=t["btn_3m"], callback_data="plan_3m")]
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=kb)
    await message.answer(t["buy_plan"], reply_markup=markup)
    await state.set_state(BuyBoostState.plan)

@dp.callback_query(BuyBoostState.plan, F.data.startswith("plan_"))
async def buy_boost_plan(callback: types.CallbackQuery, state: FSMContext):
    _, lang = get_user(callback.from_user.id)
    if not lang: lang = "en"
    t = TEXTS[lang]

    await callback.answer()
    plan = callback.data.split("_")[1] # 1m or 3m
    await state.update_data(plan=plan)
    
    await callback.message.answer(t["buy_amount"])
    await state.set_state(BuyBoostState.amount)

@dp.message(BuyBoostState.amount)
async def buy_boost_amount(message: types.Message, state: FSMContext):
    _, lang = get_user(message.from_user.id)
    if not lang: lang = "en"
    t = TEXTS[lang]

    try:
        boosts_amount = int(message.text)
        if boosts_amount <= 0:
            raise ValueError
    except ValueError:
        await message.answer(t["buy_invalid"])
        return

    user_data = await state.get_data()
    invite = user_data['invite']
    plan = user_data['plan']
    
    user_id = message.from_user.id
    balance, _ = get_user(user_id)
    
    msg = await message.answer(t["loading"])
    
    price_1m, price_3m = get_settings()
    price_per_boost = price_1m if plan == "1m" else price_3m
    total_price = price_per_boost * boosts_amount
        
    if balance < total_price:
        await msg.edit_text(t["buy_no_balance"].format(total=total_price, balance=balance), parse_mode="HTML")
        await state.clear()
        return
        
    try:
        # Отправляем запрос на покупку. Не выводим ответ API юзеру.
        order_payload = {
            "invite": invite,
            "boosts": boosts_amount,
            "plan": plan
        }
        order_resp = await gorgona_request("POST", "/boost", order_payload)
        
        # Проверяем успешность заказа по ответу API (опционально). 
        # Если API вернуло ошибку, нужно перехватить её, но по ТЗ юзер не должен видеть упоминаний API.
        if isinstance(order_resp, dict) and order_resp.get("error"):
            await msg.edit_text(t["error"])
        else:
            # Списываем баланс только при успехе API
            deduct_balance(user_id, total_price)
            await msg.edit_text(
                t["buy_success"].format(invite=invite, amount=boosts_amount, plan=plan, total=total_price),
                parse_mode="HTML"
            )
            
    except Exception as e:
        logging.error(f"Order Error: {e}")
        await msg.edit_text(t["error"])
    
    await state.clear()

# --- АДМИН ПАНЕЛЬ ---
@dp.message(Command("admin"))
async def cmd_admin(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    await state.clear()
    
    price_1m, price_3m = get_settings()
    
    kb = [
        [InlineKeyboardButton(text="Изменить цену 1m", callback_data="set_price_1m")],
        [InlineKeyboardButton(text="Изменить цену 3m", callback_data="set_price_3m")],
        [InlineKeyboardButton(text="Отправить рассылку", callback_data="admin_broadcast")]
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=kb)
    
    await message.answer(
        f"🛠 <b>Админ-панель</b>\n\n"
        f"Текущие цены:\n"
        f"1 Месяц: {price_1m} USDT\n"
        f"3 Месяца: {price_3m} USDT",
        reply_markup=markup,
        parse_mode="HTML"
    )

@dp.callback_query(F.data.startswith("set_price_"))
async def admin_set_price_start(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    await callback.answer()
    plan = callback.data.split("_")[2] # 1m or 3m
    await state.update_data(admin_plan=plan)
    
    await callback.message.answer(f"Введите новую цену для плана <b>{plan}</b> в USDT:", parse_mode="HTML")
    if plan == "1m":
        await state.set_state(AdminState.price_1m)
    else:
        await state.set_state(AdminState.price_3m)

@dp.message(AdminState.price_1m)
async def admin_set_price_1m_process(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID: return
    try:
        price = float(message.text.replace(",", "."))
        set_price("1m", price)
        await message.answer(f"✅ Цена для 1m успешно изменена на {price} USDT!")
        await state.clear()
    except ValueError:
        await message.answer("❌ Введите корректное число.")

@dp.message(AdminState.price_3m)
async def admin_set_price_3m_process(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID: return
    try:
        price = float(message.text.replace(",", "."))
        set_price("3m", price)
        await message.answer(f"✅ Цена для 3m успешно изменена на {price} USDT!")
        await state.clear()
    except ValueError:
        await message.answer("❌ Введите корректное число.")

@dp.callback_query(F.data == "admin_broadcast")
async def admin_broadcast_start(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    await callback.answer()
    await callback.message.answer("Отправьте сообщение для рассылки всем пользователям бота (можно использовать форматирование, фото, видео):")
    await state.set_state(AdminState.broadcast)

@dp.message(AdminState.broadcast)
async def admin_broadcast_process(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID: return
    
    users = get_all_users()
    sent_count = 0
    await message.answer(f"⏳ Начинаю рассылку для {len(users)} пользователей...")
    
    for uid in users:
        try:
            await message.send_copy(chat_id=uid)
            sent_count += 1
            await asyncio.sleep(0.05) # Лимит Telegram
        except Exception:
            pass # Пользователь заблокировал бота
            
    await message.answer(f"✅ Рассылка завершена!\nУспешно доставлено: {sent_count}/{len(users)}")
    await state.clear()

async def main():
    init_db()
    print("Бот запускается... Нажмите Ctrl+C для остановки.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
