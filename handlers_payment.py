import logging
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import database as db
from texts import TEXTS

router = Router()

class TopUpState(StatesGroup):
    amount = State()

@router.callback_query(F.data == "top_up")
async def top_up_handler(callback: types.CallbackQuery, state: FSMContext):
    _, lang = await db.get_user(callback.from_user.id)
    if not lang: lang = "en"
    t = TEXTS[lang]
    
    await callback.answer()
    from utils import send_menu_photo
    await send_menu_photo(callback, "images/balance.png", t["topup_ask"], None)
    await state.set_state(TopUpState.amount)

@router.message(TopUpState.amount)
async def process_top_up_amount(message: types.Message, state: FSMContext):
    _, lang = await db.get_user(message.from_user.id)
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
        from crypto import get_crypto
        crypto_client = get_crypto()
        invoice = await crypto_client.create_invoice(fiat='USD', amount=amount)
        
        kb = [
            [InlineKeyboardButton(text=t["btn_pay"], url=invoice.bot_invoice_url)],
            [InlineKeyboardButton(text=t["btn_check"], callback_data=f"check_pay_{invoice.invoice_id}_{amount}")]
        ]
        markup = InlineKeyboardMarkup(inline_keyboard=kb)
        
        await message.answer(t["topup_invoice"].format(amount=amount), reply_markup=markup, parse_mode="HTML")
    except Exception as e:
        logging.error(f"Crypto Error: {e}")
        await message.answer(t["error"])

@router.callback_query(F.data.startswith("check_pay_"))
async def check_payment(callback: types.CallbackQuery):
    _, lang = await db.get_user(callback.from_user.id)
    if not lang: lang = "en"
    t = TEXTS[lang]

    parts = callback.data.split("_")
    invoice_id = int(parts[2])
    amount = float(parts[3])
    
    try:
        from crypto import get_crypto
        crypto_client = get_crypto()
        result = await crypto_client.get_invoices(invoice_ids=invoice_id)
        
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
            await db.add_balance(callback.from_user.id, amount)
            await callback.message.edit_text(t["topup_success"].format(amount=amount), parse_mode="HTML")
        elif status_str in ['active', 'created']:
            await callback.answer(t["topup_wait"], show_alert=True)
        else:
            await callback.answer(t["topup_wait"], show_alert=True)
    except Exception as e:
        logging.error(f"Crypto Check Error: {e}")
        await callback.answer(t["error"], show_alert=True)
