import os
from utils import load_json, save_json, get_user_data, push_screen
from messages import MESSAGES
from keyboards import language_keyboard, main_menu_keyboard


def register_language_handler(bot):

    @bot.callback_query_handler(func=lambda call: call.data == "language")
    def handle_language(call):
        cid = call.message.chat.id
        push_screen(cid, "language")

        user_data = get_user_data(cid)
        lang = user_data.get("lang", "ru")

        bot.edit_message_text(
            text=MESSAGES[lang]['select_language'],
            chat_id=cid,
            message_id=call.message.message_id,
            reply_markup=language_keyboard()
        )

    @bot.callback_query_handler(func=lambda call: call.data.startswith("lang_"))
    def handle_language_change(call):
        cid = call.message.chat.id
        new_lang = call.data.split('_')[1]   # "ru" или "en"

        # Сохраняем новый язык
        users = load_json("data/users.json")
        uid = str(cid)
        if uid not in users:
            get_user_data(cid)
            users = load_json("data/users.json")
        users[uid]["lang"] = new_lang
        save_json("data/users.json", users)

        # Уведомление
        notice = MESSAGES[new_lang]['switched_to_russian'] if new_lang == 'ru' \
                 else MESSAGES[new_lang]['switched_to_english']
        bot.answer_callback_query(call.id, notice)

        # После смены языка — всегда возвращаемся в главное меню
        bot.edit_message_text(
            text=MESSAGES[new_lang]['welcome'],
            chat_id=cid,
            message_id=call.message.message_id,
            reply_markup=main_menu_keyboard(new_lang)
        )