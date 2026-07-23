from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from texts import TEXTS

def lang_menu():
    kb = [
        [
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
            InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def main_menu(lang: str):
    t = TEXTS[lang]
    kb = [
        [InlineKeyboardButton(text=t["btn_boosts"], callback_data="menu_boosts"),
         InlineKeyboardButton(text=t["btn_vpn"], callback_data="menu_vpn")],
        [InlineKeyboardButton(text=t["btn_digital"], callback_data="menu_digital")],
        [InlineKeyboardButton(text=t["btn_topup"], callback_data="top_up")],
        [InlineKeyboardButton(text="🌐 RU/EN", callback_data="change_lang")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def back_to_main_menu(lang: str):
    t = TEXTS[lang]
    kb = [[InlineKeyboardButton(text=t["btn_back_main"], callback_data="back_main")]]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def boosts_menu(lang: str):
    t = TEXTS[lang]
    kb = [
        [InlineKeyboardButton(text=t["btn_boosts"], callback_data="buy_boost")],
        [InlineKeyboardButton(text=t["btn_stock"], callback_data="stock_prices")],
        [InlineKeyboardButton(text=t["btn_back_main"], callback_data="back_main")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def vpn_menu(lang: str, prices: dict):
    t = TEXTS[lang]
    kb = [
        [InlineKeyboardButton(text=f"{t['btn_vpn_1m']} - {prices.get('vpn_price_1m', '?')} USDT", callback_data="buy_vpn_1m")],
        [InlineKeyboardButton(text=f"{t['btn_vpn_3m']} - {prices.get('vpn_price_3m', '?')} USDT", callback_data="buy_vpn_3m")],
        [InlineKeyboardButton(text=f"{t['btn_vpn_6m']} - {prices.get('vpn_price_6m', '?')} USDT", callback_data="buy_vpn_6m")],
        [InlineKeyboardButton(text=f"{t['btn_vpn_12m']} - {prices.get('vpn_price_12m', '?')} USDT", callback_data="buy_vpn_12m")],
        [InlineKeyboardButton(text=t["btn_back_main"], callback_data="back_main")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def admin_panel_menu():
    kb = [
        [InlineKeyboardButton(text="Цены Boost (1m)", callback_data="admin_price_boost_1m"),
         InlineKeyboardButton(text="Цены Boost (3m)", callback_data="admin_price_boost_3m")],
        [InlineKeyboardButton(text="Цены VPN (1m)", callback_data="admin_price_vpn_1m"),
         InlineKeyboardButton(text="Цены VPN (3m)", callback_data="admin_price_vpn_3m")],
        [InlineKeyboardButton(text="Цены VPN (6m)", callback_data="admin_price_vpn_6m"),
         InlineKeyboardButton(text="Цены VPN (12m)", callback_data="admin_price_vpn_12m")],
        [InlineKeyboardButton(text="Отправить рассылку", callback_data="admin_broadcast")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def reseller_products_menu(products: list, prices_map: dict, lang: str):
    kb = []
    for p in products:
        p_id = p["id"]
        # Filter excluded products
        from config import RESELLER_EXCLUDE_IDS
        if p_id in RESELLER_EXCLUDE_IDS:
            continue
            
        sell_price = prices_map.get(p_id)
        if sell_price is None:
            continue # skip unpriced products
            
        name = p.get(f"name_{lang}", p.get("name_en", ""))
        kb.append([InlineKeyboardButton(text=f"{name} - {sell_price:.2f} USDT", callback_data=f"view_prod_{p_id}")])
    
    t = TEXTS[lang]
    kb.append([InlineKeyboardButton(text=t["btn_back_main"], callback_data="back_main")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

def reseller_buy_menu(product_id: int, price: float, lang: str):
    t = TEXTS[lang]
    kb = [
        [InlineKeyboardButton(text=t["btn_buy_product"].format(price=price), callback_data=f"buy_prod_{product_id}")],
        [InlineKeyboardButton(text=t["btn_back_main"], callback_data="menu_digital")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)
