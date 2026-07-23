import asyncio
import logging
from aiogram import Bot, Dispatcher

import config
import database as db

# Import routers
from handlers_common import router as common_router
from handlers_boost import router as boost_router
from handlers_vpn import router as vpn_router
from handlers_reseller import router as reseller_router
from handlers_payment import router as payment_router
from handlers_admin import router as admin_router
from crypto import init_crypto

logging.basicConfig(level=logging.INFO)

async def main():
    init_crypto()
    
    await db.init_db()
    logging.info("Database initialized.")

    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher()

    # Include routers
    dp.include_router(common_router)
    dp.include_router(boost_router)
    dp.include_router(vpn_router)
    dp.include_router(reseller_router)
    dp.include_router(payment_router)
    dp.include_router(admin_router)

    logging.info("Bot is starting...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
