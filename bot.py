from telebot import TeleBot
from config import BOT_TOKEN

from handlers.start_handler import register_start_handler
from handlers.main_menu import register_main_menu_handler
from handlers.create_deal import register_create_deal_handler
from handlers.my_deals import register_my_deals_handler
from handlers.details import register_details_handler
from handlers.language import register_language_handler
from handlers.back_button import register_back_button_handler
from handlers.manager import register_manager_handler

bot = TeleBot(BOT_TOKEN)

if __name__ == '__main__':
    register_back_button_handler(bot)
    register_start_handler(bot)
    register_main_menu_handler(bot)
    register_create_deal_handler(bot)
    register_my_deals_handler(bot)
    register_details_handler(bot)
    register_language_handler(bot)
    register_manager_handler(bot)

    print("Бот запущен...")
    bot.polling(none_stop=True)