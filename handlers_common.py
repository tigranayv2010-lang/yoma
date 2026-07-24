from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

import database as db
from keyboards import lang_menu, main_menu, boosts_menu, vpn_menu
from texts import TEXTS
from utils import send_menu_photo

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    balance, lang = await db.get_user(message.from_user.id)
    
    if not lang:
        await send_menu_photo(message, "images/change languagee.png", "🇷🇺 Выберите язык / 🇬🇧 Choose language:", lang_menu())
        return

    t = TEXTS[lang]
    await send_menu_photo(message, "images/main menu.png", t["welcome"].format(balance=balance), main_menu(lang))

@router.callback_query(F.data.startswith("lang_"))
async def set_lang_handler(callback: types.CallbackQuery):
    lang = callback.data.split("_")[1]
    await db.set_lang(callback.from_user.id, lang)
    await callback.answer(TEXTS[lang]["lang_changed"])
    
    balance, _ = await db.get_user(callback.from_user.id)
    t = TEXTS[lang]
    await send_menu_photo(callback, "images/main menu.png", t["welcome"].format(balance=balance), main_menu(lang))

@router.callback_query(F.data == "change_lang")
async def change_lang_handler(callback: types.CallbackQuery):
    await callback.answer()
    await send_menu_photo(callback, "images/change languagee.png", "🇷🇺 Выберите язык / 🇬🇧 Choose language:", lang_menu())

@router.callback_query(F.data == "back_main")
async def back_main_handler(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    balance, lang = await db.get_user(callback.from_user.id)
    if not lang: lang = "en"
    
    await callback.answer()
    t = TEXTS[lang]
    await send_menu_photo(callback, "images/main menu.png", t["welcome"].format(balance=balance), main_menu(lang))

@router.callback_query(F.data == "menu_boosts")
async def menu_boosts_handler(callback: types.CallbackQuery):
    _, lang = await db.get_user(callback.from_user.id)
    if not lang: lang = "en"
    t = TEXTS[lang]
    
    await callback.answer()
    # Boosts menu doesn't have a specific info text in TEXTS, but we can just use the caption "Discord Boosts"
    # Or keep the old caption if it existed, but menu_boosts_handler used to do edit_reply_markup.
    # Now that we send a photo, we need a caption.
    await send_menu_photo(callback, "images/boosts.png", t["btn_boosts"], boosts_menu(lang))

@router.callback_query(F.data == "menu_vpn")
async def menu_vpn_handler(callback: types.CallbackQuery):
    _, lang = await db.get_user(callback.from_user.id)
    if not lang: lang = "en"
    
    prices = await db.get_prices()
    
    await callback.answer()
    await send_menu_photo(callback, "images/vpn.png", TEXTS[lang]["vpn_info"], vpn_menu(lang, prices))
