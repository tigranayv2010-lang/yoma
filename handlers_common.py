from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

import database as db
from keyboards import lang_menu, main_menu, boosts_menu, vpn_menu
from texts import TEXTS

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    balance, lang = await db.get_user(message.from_user.id)
    
    if not lang:
        await message.answer("🇷🇺 Выберите язык / 🇬🇧 Choose language:", reply_markup=lang_menu())
        return

    t = TEXTS[lang]
    await message.answer(
        t["welcome"].format(balance=balance),
        reply_markup=main_menu(lang),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("lang_"))
async def set_lang_handler(callback: types.CallbackQuery):
    lang = callback.data.split("_")[1]
    await db.set_lang(callback.from_user.id, lang)
    await callback.answer(TEXTS[lang]["lang_changed"])
    
    balance, _ = await db.get_user(callback.from_user.id)
    await callback.message.edit_text(
        TEXTS[lang]["welcome"].format(balance=balance),
        reply_markup=main_menu(lang),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "change_lang")
async def change_lang_handler(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.edit_text("🇷🇺 Выберите язык / 🇬🇧 Choose language:", reply_markup=lang_menu())

@router.callback_query(F.data == "back_main")
async def back_main_handler(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    balance, lang = await db.get_user(callback.from_user.id)
    if not lang: lang = "en"
    
    await callback.answer()
    await callback.message.edit_text(
        TEXTS[lang]["welcome"].format(balance=balance),
        reply_markup=main_menu(lang),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "menu_boosts")
async def menu_boosts_handler(callback: types.CallbackQuery):
    _, lang = await db.get_user(callback.from_user.id)
    if not lang: lang = "en"
    
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=boosts_menu(lang))

@router.callback_query(F.data == "menu_vpn")
async def menu_vpn_handler(callback: types.CallbackQuery):
    _, lang = await db.get_user(callback.from_user.id)
    if not lang: lang = "en"
    
    prices = await db.get_prices()
    
    await callback.answer()
    await callback.message.edit_text(
        TEXTS[lang]["vpn_info"],
        reply_markup=vpn_menu(lang, prices),
        parse_mode="HTML"
    )
