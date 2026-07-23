TEXTS = {
    "ru": {
        "welcome": "👋 <b>Привет! Это универсальный магазин.</b>\n\n💳 Твой баланс: <b>{balance:.2f} USDT</b>\n\nВыбери нужный раздел:",
        "btn_boosts": "🚀 Discord Бусты",
        "btn_vpn": "🛡 VPN",
        "btn_topup": "💰 Пополнить баланс",
        "btn_stock": "📊 Наличие и цены",
        "btn_back_main": "🔙 На главную",
        "choose_lang": "🇷🇺 Выберите язык / 🇬🇧 Choose language:",
        "lang_changed": "✅ Язык изменен на Русский!",
        "loading": "⏳ Загрузка...",
        "error": "❌ Произошла ошибка. Попробуйте позже.",
        
        # Payment
        "topup_ask": "Введите сумму пополнения в <b>USDT</b> (например, 1.5):",
        "topup_invalid": "❌ Введите корректное число больше нуля.",
        "topup_invoice": "🧾 Создан счет на <b>{amount} USDT</b>.\nОплатите по кнопке ниже и проверьте оплату.",
        "btn_pay": "🔗 Оплатить",
        "btn_check": "✅ Проверить оплату",
        "topup_success": "✅ <b>Успешное пополнение!</b>\nНа ваш баланс зачислено: <b>{amount} USDT</b>.",
        "topup_wait": "❌ Оплата еще не поступила. Попробуйте чуть позже.",
        "topup_not_found": "❌ Счет не найден.",
        
        # Boosts
        "buy_invite": "🔗 Отправьте ссылку-приглашение на сервер (invite link):",
        "buy_plan": "📅 Выберите срок подписки:",
        "btn_1m": "1 Месяц",
        "btn_3m": "3 Месяца",
        "buy_amount": "🔢 Введите количество бустов, которое хотите купить:",
        "buy_invalid": "❌ Введите корректное целое число больше нуля.",
        "buy_no_balance": "❌ <b>Недостаточно средств!</b>\n\nСтоимость: <b>{total:.2f} USDT</b>\nВаш баланс: <b>{balance:.2f} USDT</b>",
        "buy_success": "✅ <b>Заказ успешно оформлен!</b>\n\n🔗 Сервер: {invite}\n🚀 Бусты: {amount} шт.\n📅 Срок: {plan}\n💵 Списано: {total:.2f} USDT",
        "stock_info": "📊 <b>Наличие и Цены:</b>\n\n📦 <b>Наличие:</b>\n1 Месяц: <b>{stock_1m} шт.</b>\n3 Месяца: <b>{stock_3m} шт.</b>\n\n💵 <b>Цены на бусты:</b>\n1 Месяц: <b>{price_1m} USDT</b>\n3 Месяца: <b>{price_3m} USDT</b>",

        # VPN
        "vpn_info": (
            "🛡 <b>Высокоскоростной VPN (VLESS)</b>\n\n"
            "✅ Реально работает в РФ (обход DPI)\n"
            "✅ Скорость до 1 Гбит/с — ютуб в 4K\n"
            "✅ Без логов\n\n"
            "Выберите тариф:"
        ),
        "btn_vpn_1m": "1 месяц",
        "btn_vpn_3m": "3 месяца",
        "btn_vpn_6m": "6 месяцев",
        "btn_vpn_12m": "1 год",
        "vpn_no_balance": "❌ <b>Недостаточно средств для покупки VPN!</b>\n\nСтоимость: <b>{total:.2f} USDT</b>\nВаш баланс: <b>{balance:.2f} USDT</b>",
        "vpn_success": (
            "🎉 <b>VPN успешно куплен!</b>\n\n"
            "📦 Тариф: {plan}\n"
            "⏳ Срок: {days} дней\n"
            "💵 Списано: {total:.2f} USDT\n\n"
            "🔗 <b>Ваша ссылка подключения:</b>\n"
            "<code>{link}</code>\n\n"
            "📲 Скопируйте ссылку и вставьте в приложение (v2rayNG, Hiddify, V2Ray Tun и др.)"
        ),
        "vpn_error": "❌ Ошибка при создании VPN. Деньги возвращены на баланс.",
    },
    "en": {
        "welcome": "👋 <b>Hello! This is a universal shop.</b>\n\n💳 Your balance: <b>{balance:.2f} USDT</b>\n\nChoose a category:",
        "btn_boosts": "🚀 Discord Boosts",
        "btn_vpn": "🛡 VPN",
        "btn_topup": "💰 Top Up Balance",
        "btn_stock": "📊 Stock & Prices",
        "btn_back_main": "🔙 Main Menu",
        "choose_lang": "Choose language / Выберите язык:",
        "lang_changed": "✅ Language changed to English!",
        "loading": "⏳ Loading...",
        "error": "❌ An error occurred. Please try again later.",
        
        # Payment
        "topup_ask": "Enter the top-up amount in <b>USDT</b> (e.g., 1.5):",
        "topup_invalid": "❌ Enter a valid number greater than zero.",
        "topup_invoice": "🧾 Invoice created for <b>{amount} USDT</b>.\nPay via the button below and check payment.",
        "btn_pay": "🔗 Pay",
        "btn_check": "✅ Check Payment",
        "topup_success": "✅ <b>Top-up successful!</b>\nAdded to your balance: <b>{amount} USDT</b>.",
        "topup_wait": "❌ Payment not received yet. Try again later.",
        "topup_not_found": "❌ Invoice not found.",
        
        # Boosts
        "buy_invite": "🔗 Send the server invite link:",
        "buy_plan": "📅 Choose subscription plan:",
        "btn_1m": "1 Month",
        "btn_3m": "3 Months",
        "buy_amount": "🔢 Enter the number of boosts you want to buy:",
        "buy_invalid": "❌ Enter a valid integer greater than zero.",
        "buy_no_balance": "❌ <b>Insufficient funds!</b>\n\nCost: <b>{total:.2f} USDT</b>\nYour balance: <b>{balance:.2f} USDT</b>",
        "buy_success": "✅ <b>Order successfully placed!</b>\n\n🔗 Server: {invite}\n🚀 Boosts: {amount} pcs\n📅 Plan: {plan}\n💵 Deducted: {total:.2f} USDT",
        "stock_info": "📊 <b>Stock & Prices:</b>\n\n📦 <b>Stock:</b>\n1 Month: <b>{stock_1m} pcs</b>\n3 Months: <b>{stock_3m} pcs</b>\n\n💵 <b>Boost Prices:</b>\n1 Month: <b>{price_1m} USDT</b>\n3 Months: <b>{price_3m} USDT</b>",

        # VPN
        "vpn_info": (
            "🛡 <b>High-Speed VPN (VLESS)</b>\n\n"
            "✅ Bypasses censorship\n"
            "✅ Up to 1 Gbps speed\n"
            "✅ No logs\n\n"
            "Choose a plan:"
        ),
        "btn_vpn_1m": "1 Month",
        "btn_vpn_3m": "3 Months",
        "btn_vpn_6m": "6 Months",
        "btn_vpn_12m": "1 Year",
        "vpn_no_balance": "❌ <b>Insufficient funds for VPN!</b>\n\nCost: <b>{total:.2f} USDT</b>\nYour balance: <b>{balance:.2f} USDT</b>",
        "vpn_success": (
            "🎉 <b>VPN successfully purchased!</b>\n\n"
            "📦 Plan: {plan}\n"
            "⏳ Duration: {days} days\n"
            "💵 Deducted: {total:.2f} USDT\n\n"
            "🔗 <b>Your connection link:</b>\n"
            "<code>{link}</code>\n\n"
            "📲 Copy the link and paste it into your app (v2rayNG, Hiddify, V2Ray Tun, etc.)"
        ),
        "vpn_error": "❌ Error creating VPN. Funds returned to your balance.",
    }
}
