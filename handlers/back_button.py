from utils import get_user_data, reset_stack
from messages import MESSAGES
from keyboards import main_menu_keyboard, wallet_menu_keyboard, topup_currency_keyboard, back_button
import handlers.create_deal as create_deal_module


def _show_main_menu(bot, call, lang):
    bot.edit_message_text(
        text=MESSAGES[lang]['welcome'],
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=main_menu_keyboard(lang)
    )


def _show_details(bot, call, cid, lang):
    from handlers.details import build_details_text
    bot.edit_message_text(
        text=build_details_text(cid),
        chat_id=cid,
        message_id=call.message.message_id,
        reply_markup=wallet_menu_keyboard()
    )


def _show_topup(bot, call, cid):
    bot.edit_message_text(
        text="💰 Пополнение баланса\n\nВыберите валюту:",
        chat_id=cid,
        message_id=call.message.message_id,
        reply_markup=topup_currency_keyboard()
    )


def register_back_button_handler(bot):

    @bot.callback_query_handler(func=lambda call: call.data.startswith("back_to_"))
    def handle_back(call):
        cid = call.message.chat.id
        target = call.data.replace("back_to_", "")

        # Отменяем активную сделку и очищаем next_step_handler
        create_deal_module.creating_deal_stage.pop(cid, None)
        bot.clear_step_handler_by_chat_id(cid)

        user_data = get_user_data(cid)
        lang = user_data.get("lang", "ru")

        if target == "main":
            reset_stack(cid)
            _show_main_menu(bot, call, lang)
        elif target == "details":
            _show_details(bot, call, cid, lang)
        elif target == "topup":
            _show_topup(bot, call, cid)
        elif target == "withdraw":
            from keyboards import withdraw_currency_keyboard
            bot.edit_message_text(
                text="📤 Вывод средств\n\nВыберите валюту для вывода:",
                chat_id=cid,
                message_id=call.message.message_id,
                reply_markup=withdraw_currency_keyboard()
            )
        else:
            reset_stack(cid)
            _show_main_menu(bot, call, lang)
