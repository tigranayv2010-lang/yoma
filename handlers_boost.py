import logging
import aiohttp
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import config
import database as db
from texts import TEXTS

router = Router()

class BuyBoostState(StatesGroup):
    invite = State()
    plan = State()
    amount = State()

async def gorgona_request(method, endpoint, payload=None):
    headers = {"Authorization": f"Bearer {config.GORGONA_API_KEY}", "Content-Type": "application/json"}
    url = f"{config.GORGONA_BASE_URL}{endpoint}"
    async with aiohttp.ClientSession() as session:
        if method == "GET":
            async with session.get(url, headers=headers) as resp:
                return await resp.json()
        elif method == "POST":
            async with session.post(url, headers=headers, json=payload) as resp:
                return await resp.json()

@router.callback_query(F.data == "stock_prices")
async def stock_prices_handler(callback: types.CallbackQuery):
    _, lang = await db.get_user(callback.from_user.id)
    if not lang: lang = "en"
    t = TEXTS[lang]
    
    await callback.answer()
    msg = await callback.message.answer(t["loading"])
    
    try:
        stock_data = await gorgona_request("GET", "/stock")
        stock_1m = stock_data.get("stock", {}).get("1m", 0)
        stock_3m = stock_data.get("stock", {}).get("3m", 0)
        
        prices = await db.get_prices()
        price_1m = prices.get("boost_price_1m", 1.5)
        price_3m = prices.get("boost_price_3m", 3.0)
        
        text = t["stock_info"].format(
            stock_1m=stock_1m,
            stock_3m=stock_3m,
            price_1m=price_1m,
            price_3m=price_3m
        )
        from keyboards import back_to_main_menu
        await msg.edit_text(text, parse_mode="HTML", reply_markup=back_to_main_menu(lang))
    except Exception as e:
        logging.error(f"Stock Error: {e}")
        await msg.edit_text(t["error"], parse_mode="HTML")

@router.callback_query(F.data == "buy_boost")
async def buy_boost_start(callback: types.CallbackQuery, state: FSMContext):
    _, lang = await db.get_user(callback.from_user.id)
    if not lang: lang = "en"
    t = TEXTS[lang]

    await callback.answer()
    await callback.message.answer(t["buy_invite"])
    await state.set_state(BuyBoostState.invite)

@router.message(BuyBoostState.invite)
async def buy_boost_invite(message: types.Message, state: FSMContext):
    _, lang = await db.get_user(message.from_user.id)
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

@router.callback_query(BuyBoostState.plan, F.data.startswith("plan_"))
async def buy_boost_plan(callback: types.CallbackQuery, state: FSMContext):
    _, lang = await db.get_user(callback.from_user.id)
    if not lang: lang = "en"
    t = TEXTS[lang]

    await callback.answer()
    plan = callback.data.split("_")[1] # 1m or 3m
    await state.update_data(plan=plan)
    
    await callback.message.answer(t["buy_amount"])
    await state.set_state(BuyBoostState.amount)

@router.message(BuyBoostState.amount)
async def buy_boost_amount(message: types.Message, state: FSMContext):
    _, lang = await db.get_user(message.from_user.id)
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
    balance, _ = await db.get_user(user_id)
    
    msg = await message.answer(t["loading"])
    
    prices = await db.get_prices()
    price_per_boost = prices.get(f"boost_price_{plan}", 1.5)
    total_price = price_per_boost * boosts_amount
        
    if balance < total_price:
        await msg.edit_text(t["buy_no_balance"].format(total=total_price, balance=balance), parse_mode="HTML")
        await state.clear()
        return
        
    try:
        order_payload = {
            "invite": invite,
            "boosts": boosts_amount,
            "plan": plan
        }
        order_resp = await gorgona_request("POST", "/boost", order_payload)
        
        if isinstance(order_resp, dict) and order_resp.get("error"):
            await msg.edit_text(t["error"])
        else:
            await db.deduct_balance(user_id, total_price)
            await msg.edit_text(
                t["buy_success"].format(invite=invite, amount=boosts_amount, plan=plan, total=total_price),
                parse_mode="HTML"
            )
            
    except Exception as e:
        logging.error(f"Order Error: {e}")
        await msg.edit_text(t["error"])
    
    await state.clear()
