from utils import load_json, save_json, get_user_data, push_screen
from messages import MESSAGES
from keyboards import back_button, currency_keyboard

_bot = None
creating_deal_stage: dict = {}

# Соответствие валюты → ключ баланса в users.json
CURRENCY_BALANCE_KEY = {
    "usdt": "usd",
    "rub":  "rub",
    "ton":  "ton",
    "stars":"stars",
    # для "other" — custom_currency, не трогаем стандартные балансы
}

CURRENCY_LABEL = {
    "usdt":  "USDT",
    "rub":   "RUB",
    "ton":   "TON",
    "stars": "Stars",
}


def register_create_deal_handler(bot):
    global _bot
    _bot = bot

    # ── Шаг 1: нажали «Создать сделку» → показываем выбор валюты ──────────────
    @bot.callback_query_handler(func=lambda call: call.data == "create_deal")
    def handle_create_deal(call):
        cid = call.message.chat.id
        push_screen(cid, "create_deal")
        creating_deal_stage[cid] = {'step': 'waiting_for_currency'}

        _bot.edit_message_text(
            text="💱 Выберите валюту сделки:",
            chat_id=cid,
            message_id=call.message.message_id,
            reply_markup=currency_keyboard()
        )

    # ── Шаг 2а: выбрали валюту (кроме «другой») ───────────────────────────────
    @bot.callback_query_handler(func=lambda call: call.data.startswith("currency_") and call.data != "currency_other")
    def handle_currency_choice(call):
        cid = call.message.chat.id
        if cid not in creating_deal_stage:
            return

        currency_code = call.data.replace("currency_", "")   # usdt / rub / ton / stars
        label = CURRENCY_LABEL.get(currency_code, currency_code.upper())
        creating_deal_stage[cid]['currency'] = currency_code
        creating_deal_stage[cid]['currency_label'] = label
        creating_deal_stage[cid]['step'] = 'waiting_for_product'

        user_data = get_user_data(cid)
        lang = user_data.get("lang", "ru")

        _bot.edit_message_text(
            text=MESSAGES[lang]['create_deal_request'],
            chat_id=cid,
            message_id=call.message.message_id,
            reply_markup=back_button("main")
        )
        _bot.register_next_step_handler(call.message, process_product_input, call.message)

    # ── Шаг 2б: выбрали «Другая валюта» → просим ввести инициалы ──────────────
    @bot.callback_query_handler(func=lambda call: call.data == "currency_other")
    def handle_currency_other(call):
        cid = call.message.chat.id
        if cid not in creating_deal_stage:
            return

        creating_deal_stage[cid]['currency'] = 'other'
        creating_deal_stage[cid]['step'] = 'waiting_for_currency_name'

        _bot.edit_message_text(
            text="✏️ Введите инициалы валюты (например: AMD, EUR, GBP):",
            chat_id=cid,
            message_id=call.message.message_id,
            reply_markup=back_button("main")
        )
        _bot.register_next_step_handler(call.message, process_currency_name_input, call.message)

    def process_currency_name_input(message, original_msg):
        cid = message.chat.id
        if cid not in creating_deal_stage:
            return
        if message.text and message.text.startswith('/'):
            creating_deal_stage.pop(cid, None)
            _bot.process_new_messages([message])
            return

        currency_name = message.text.strip().upper()[:10]  # максимум 10 символов
        creating_deal_stage[cid]['currency_label'] = currency_name
        creating_deal_stage[cid]['step'] = 'waiting_for_product'

        user_data = get_user_data(cid)
        lang = user_data.get("lang", "ru")

        _bot.edit_message_text(
            text=MESSAGES[lang]['create_deal_request'],
            chat_id=cid,
            message_id=original_msg.message_id,
            reply_markup=back_button("main")
        )
        _bot.register_next_step_handler(original_msg, process_product_input, original_msg)

    # ── Шаг 3: название товара ─────────────────────────────────────────────────
    def process_product_input(message, original_msg):
        cid = message.chat.id
        if cid not in creating_deal_stage:
            return
        if message.text and message.text.startswith('/'):
            creating_deal_stage.pop(cid, None)
            _bot.process_new_messages([message])
            return

        user_data = get_user_data(cid)
        lang = user_data.get("lang", "ru")

        creating_deal_stage[cid]['product'] = message.text
        creating_deal_stage[cid]['step'] = 'waiting_for_price'

        currency_label = creating_deal_stage[cid].get('currency_label', '')

        _bot.edit_message_text(
            text=f"{MESSAGES[lang]['enter_price']} ({currency_label})",
            chat_id=cid,
            message_id=original_msg.message_id,
            reply_markup=back_button("main")
        )
        _bot.register_next_step_handler(original_msg, process_price_input, original_msg)

    # ── Шаг 4: цена ───────────────────────────────────────────────────────────
    def process_price_input(message, original_msg):
        cid = message.chat.id
        if cid not in creating_deal_stage:
            return
        if message.text and message.text.startswith('/'):
            creating_deal_stage.pop(cid, None)
            _bot.process_new_messages([message])
            return

        user_data = get_user_data(cid)
        lang = user_data.get("lang", "ru")

        try:
            price = float(message.text.replace(",", "."))
        except ValueError:
            _bot.reply_to(message, "❌ Цена должна быть числом. Попробуйте ещё раз:")
            _bot.register_next_step_handler(message, process_price_input, original_msg)
            return

        creating_deal_stage[cid]['price'] = price
        create_and_save_deal(cid, original_msg, lang)

    # ── Сохранение сделки ─────────────────────────────────────────────────────
    def create_and_save_deal(cid, original_msg, lang):
        product        = creating_deal_stage[cid]['product']
        price          = creating_deal_stage[cid]['price']
        currency       = creating_deal_stage[cid].get('currency', 'rub')
        currency_label = creating_deal_stage[cid].get('currency_label', 'RUB')

        deals = load_json("data/deals.json")
        deal_id = str(len(deals) + 1)
        deals[deal_id] = {
            "seller_id":       cid,
            "product":         product,
            "price":           price,
            "currency":        currency,
            "currency_label":  currency_label,
            "paid":            False,
            "payment_details": _get_seller_wallet(cid, currency),
        }
        save_json("data/deals.json", deals)
        creating_deal_stage.pop(cid, None)

        success_msg = (
            f"✅ Сделка создана!\n"
            f"Товар: {product}\n"
            f"Цена: {price} {currency_label}\n"
            f"Отправьте эту ссылку покупателю:\n"
            f"https://t.me/yomamarketdeal_bot?start=deal_{deal_id}"
        )

        _bot.edit_message_text(
            text=success_msg,
            chat_id=cid,
            message_id=original_msg.message_id,
            reply_markup=back_button("main")
        )


def _get_seller_wallet(seller_id, currency: str) -> str:
    """Возвращает реквизиты продавца для выбранной валюты."""
    user_data = get_user_data(seller_id)
    wallets = user_data.get("wallets", {})
    mapping = {
        "ton":   wallets.get("ton", ""),
        "rub":   wallets.get("rub_card", ""),
        "usdt":  wallets.get("usd_card", ""),
        "stars": wallets.get("ton", ""),   # Stars отправляются через TON-кошелёк
        "other": wallets.get("any_currency", ""),
    }
    wallet = mapping.get(currency, wallets.get("any_currency", ""))
    return wallet or "не указан — укажите реквизиты в разделе 💳 Реквизиты"