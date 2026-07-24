import logging
import aiohttp
from aiogram import Router, F, types

import config
import database as db
from texts import TEXTS
from keyboards import reseller_products_menu, reseller_buy_menu

router = Router()

async def reseller_request(method, endpoint, payload=None):
    headers = {"X-API-Key": config.RESELLER_API_KEY, "Content-Type": "application/json"}
    url = f"{config.RESELLER_BASE_URL}{endpoint}"
    async with aiohttp.ClientSession() as session:
        if method == "GET":
            async with session.get(url, headers=headers) as resp:
                return await resp.json()
        elif method == "POST":
            async with session.post(url, headers=headers, json=payload) as resp:
                return await resp.json()

from utils import send_menu_photo

@router.callback_query(F.data == "menu_digital")
async def menu_digital_handler(callback: types.CallbackQuery):
    _, lang = await db.get_user(callback.from_user.id)
    if not lang: lang = "en"
    t = TEXTS[lang]
    
    await callback.answer()
    
    try:
        data = await reseller_request("GET", "/api/products")
        if data.get("ok"):
            products = data["products"]
            markup = reseller_products_menu(products, config.RESELLER_PRICES, lang)
            await send_menu_photo(callback, "images/ai_subsribtion.png", t["reseller_list"], markup)
        else:
            await send_menu_photo(callback, "images/ai_subsribtion.png", t["error"], None)
    except Exception as e:
        logging.error(f"Reseller fetch error: {e}")
        await send_menu_photo(callback, "images/ai_subsribtion.png", t["error"], None)

@router.callback_query(F.data.startswith("view_prod_"))
async def view_product_handler(callback: types.CallbackQuery):
    _, lang = await db.get_user(callback.from_user.id)
    if not lang: lang = "en"
    t = TEXTS[lang]
    
    product_id = int(callback.data.split("_")[2])
    
    await callback.answer()
    
    try:
        data = await reseller_request("GET", "/api/products")
        if not data.get("ok"):
            await send_menu_photo(callback, "images/ai_subsribtion.png", t["error"], None)
            return
            
        product = next((p for p in data["products"] if p["id"] == product_id), None)
        if not product:
            await send_menu_photo(callback, "images/ai_subsribtion.png", t["error"], None)
            return
            
        sell_price = config.RESELLER_PRICES.get(product_id)
        name = product.get(f"name_{lang}", product.get("name_en", ""))
        desc = product.get(f"description_{lang}", product.get("description_en", ""))
        stock = product.get("stock_count", 0)
        
        text = t["reseller_product_info"].format(name=name, desc=desc, stock=stock, price=sell_price)
        markup = reseller_buy_menu(product_id, sell_price, lang)
        
        await send_menu_photo(callback, "images/ai_subsribtion.png", text, markup)
    except Exception as e:
        logging.error(f"Reseller view error: {e}")
        await send_menu_photo(callback, "images/ai_subsribtion.png", t["error"], None)

@router.callback_query(F.data.startswith("buy_prod_"))
async def buy_product_handler(callback: types.CallbackQuery):
    _, lang = await db.get_user(callback.from_user.id)
    if not lang: lang = "en"
    t = TEXTS[lang]
    
    product_id = int(callback.data.split("_")[2])
    user_id = callback.from_user.id
    
    sell_price = config.RESELLER_PRICES.get(product_id)
    if not sell_price:
        await callback.answer(t["error"], show_alert=True)
        return
        
    balance, _ = await db.get_user(user_id)
    if balance < sell_price:
        await send_menu_photo(
            callback, "images/ai_subsribtion.png",
            t["reseller_no_balance"].format(total=sell_price, balance=balance),
            None
        )
        return
        
    await callback.answer()
    
    try:
        # Check stock first, we can also just try to buy directly. We will buy directly.
        payload = {"product_id": product_id, "quantity": 1}
        buy_data = await reseller_request("POST", "/api/buy", payload)
        
        if buy_data.get("ok"):
            # Success, deduct balance
            await db.deduct_balance(user_id, sell_price)
            
            # Get item
            items = buy_data.get("items", [])
            item_text = items[0] if items else "No item data returned"
            
            # Fetch name
            products_data = await reseller_request("GET", "/api/products")
            name = "Product"
            if products_data.get("ok"):
                p = next((p for p in products_data["products"] if p["id"] == product_id), None)
                if p:
                    name = p.get(f"name_{lang}", p.get("name_en", ""))
            
            await send_menu_photo(
                callback, "images/ai_subsribtion.png",
                t["reseller_buy_success"].format(name=name, price=sell_price, item=item_text),
                None
            )
        else:
            # Maybe out of stock or error
            err_msg = buy_data.get("error", "")
            if "stock" in err_msg.lower():
                await send_menu_photo(callback, "images/ai_subsribtion.png", t["reseller_out_of_stock"], None)
            else:
                logging.error(f"API Buy error: {err_msg}")
                await send_menu_photo(callback, "images/ai_subsribtion.png", t["error"], None)
                
    except Exception as e:
        logging.error(f"Reseller buy error: {e}")
        await send_menu_photo(callback, "images/ai_subsribtion.png", t["error"], None)
