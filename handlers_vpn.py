import logging
from aiogram import Router, F, types

import database as db
import xui_client
from texts import TEXTS

router = Router()

@router.callback_query(F.data.startswith("buy_vpn_"))
async def buy_vpn_handler(callback: types.CallbackQuery):
    _, lang = await db.get_user(callback.from_user.id)
    if not lang: lang = "en"
    t = TEXTS[lang]

    plan = callback.data.split("_")[2] # 1m, 3m, 6m, 12m
    user_id = callback.from_user.id
    
    balance, _ = await db.get_user(user_id)
    prices = await db.get_prices()
    price = prices.get(f"vpn_price_{plan}", 0)
    
    await callback.answer()
    
    if balance < price:
        await callback.message.edit_text(
            t["vpn_no_balance"].format(total=price, balance=balance),
            parse_mode="HTML"
        )
        return
        
    msg = await callback.message.edit_text(t["loading"], parse_mode="HTML")
    
    try:
        # Convert 1m to 1_month for the xui_client (which expects 1_month, 3_months, etc)
        xui_plan_map = {
            "1m": "1_month",
            "3m": "3_months",
            "6m": "6_months",
            "12m": "12_months"
        }
        xui_plan = xui_plan_map.get(plan, "1_month")
        
        result = await xui_client.add_client(user_id=user_id, plan=xui_plan)
        
        await db.deduct_balance(user_id, price)
        
        await msg.edit_text(
            t["vpn_success"].format(
                plan=plan, 
                days=result['expire_days'],
                total=price,
                link=result['link']
            ),
            parse_mode="HTML"
        )
        
    except Exception as e:
        logging.error(f"VPN Error: {e}")
        await msg.edit_text(t["vpn_error"], parse_mode="HTML")
