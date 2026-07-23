import asyncio
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

import config
import database as db
from keyboards import admin_panel_menu

router = Router()

class AdminState(StatesGroup):
    setting_price = State()
    broadcast = State()

@router.message(Command("admin"))
async def cmd_admin(message: types.Message, state: FSMContext):
    if message.from_user.id != config.ADMIN_ID:
        return
    await state.clear()
    
    prices = await db.get_prices()
    
    await message.answer(
        f"🛠 <b>Админ-панель</b>\n\n"
        f"<b>Текущие цены (USDT):</b>\n"
        f"🚀 <i>Discord Бусты</i>\n"
        f"1 Месяц: {prices.get('boost_price_1m', '?')}\n"
        f"3 Месяца: {prices.get('boost_price_3m', '?')}\n\n"
        f"🛡 <i>VPN</i>\n"
        f"1 Месяц: {prices.get('vpn_price_1m', '?')}\n"
        f"3 Месяца: {prices.get('vpn_price_3m', '?')}\n"
        f"6 Месяцев: {prices.get('vpn_price_6m', '?')}\n"
        f"1 Год: {prices.get('vpn_price_12m', '?')}\n",
        reply_markup=admin_panel_menu(),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("admin_price_"))
async def admin_set_price_start(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != config.ADMIN_ID:
        return
    await callback.answer()
    
    # admin_price_boost_1m or admin_price_vpn_1m
    target_key = callback.data.replace("admin_price_", "") # boost_1m or vpn_1m
    
    await state.update_data(target_price_key=target_key)
    await state.set_state(AdminState.setting_price)
    
    await callback.message.answer(f"Введите новую цену для <b>{target_key}</b> в USDT:", parse_mode="HTML")

@router.message(AdminState.setting_price)
async def admin_set_price_process(message: types.Message, state: FSMContext):
    if message.from_user.id != config.ADMIN_ID: 
        return
        
    try:
        price = float(message.text.replace(",", "."))
        data = await state.get_data()
        key = data["target_price_key"]
        
        await db.set_price(key, price)
        await message.answer(f"✅ Цена для {key} успешно изменена на {price} USDT!")
        await state.clear()
    except ValueError:
        await message.answer("❌ Введите корректное число.")

@router.callback_query(F.data == "admin_broadcast")
async def admin_broadcast_start(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != config.ADMIN_ID:
        return
    await callback.answer()
    await callback.message.answer("Отправьте сообщение для рассылки всем пользователям бота (можно использовать форматирование, фото, видео):")
    await state.set_state(AdminState.broadcast)

@router.message(AdminState.broadcast)
async def admin_broadcast_process(message: types.Message, state: FSMContext):
    if message.from_user.id != config.ADMIN_ID: 
        return
    
    users = await db.get_all_users()
    sent_count = 0
    await message.answer(f"⏳ Начинаю рассылку для {len(users)} пользователей...")
    
    for uid in users:
        try:
            await message.send_copy(chat_id=uid)
            sent_count += 1
            await asyncio.sleep(0.05)
        except Exception:
            pass
            
    await message.answer(f"✅ Рассылка завершена!\nУспешно доставлено: {sent_count}/{len(users)}")
    await state.clear()
