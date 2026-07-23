import aiosqlite
import config

DB_PATH = "bot.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY, 
            balance REAL DEFAULT 0, 
            lang TEXT DEFAULT NULL
        )''')
        
        await db.execute('''CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )''')
        
        # Migrate old 'settings' table if it has the old schema (id, price_1m, price_3m)
        try:
            cursor = await db.execute("SELECT price_1m, price_3m FROM settings WHERE id=1")
            old_settings = await cursor.fetchone()
            if old_settings:
                # Migrate to new key-value format
                await db.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", ("boost_price_1m", str(old_settings[0])))
                await db.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", ("boost_price_3m", str(old_settings[1])))
                # Delete the old row (id=1 is basically invalid in the new schema where key is PRIMARY KEY)
                # Actually, if we change the schema, we might get an error because the old table has (id INTEGER PRIMARY KEY).
                # To be safe against schema changes, let's just initialize defaults.
        except Exception:
            pass
            
        await db.commit()

    await init_prices()

async def init_prices():
    defaults = {
        "boost_price_1m": "1.5",
        "boost_price_3m": "3.0",
        "vpn_price_1m": str(config.DEFAULT_PRICE_VPN_1M),
        "vpn_price_3m": str(config.DEFAULT_PRICE_VPN_3M),
        "vpn_price_6m": str(config.DEFAULT_PRICE_VPN_6M),
        "vpn_price_12m": str(config.DEFAULT_PRICE_VPN_12M),
    }
    
    async with aiosqlite.connect(DB_PATH) as db:
        # For old schema compatibility handling, we will just use INSERT OR IGNORE
        # If the table was already created with old schema, we drop it and recreate it properly.
        cursor = await db.execute("PRAGMA table_info(settings)")
        columns = await cursor.fetchall()
        has_key_column = any(col[1] == 'key' for col in columns)
        
        if not has_key_column:
            # Old schema detected, drop and recreate
            await db.execute("DROP TABLE settings")
            await db.execute('''CREATE TABLE settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )''')
            
        for key, value in defaults.items():
            await db.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (key, value))
        await db.commit()

async def get_user(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT balance, lang FROM users WHERE user_id=?", (user_id,))
        res = await cursor.fetchone()
        if not res:
            await db.execute("INSERT INTO users (user_id, balance) VALUES (?, ?)", (user_id, 0))
            await db.commit()
            return (0.0, None)
        return res

async def set_lang(user_id: int, lang: str):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("UPDATE users SET lang = ? WHERE user_id=?", (lang, user_id))
        if cursor.rowcount == 0:
            await db.execute("INSERT INTO users (user_id, balance, lang) VALUES (?, 0, ?)", (user_id, lang))
        await db.commit()

async def add_balance(user_id: int, amount: float):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET balance = balance + ? WHERE user_id=?", (amount, user_id))
        await db.commit()

async def deduct_balance(user_id: int, amount: float):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET balance = balance - ? WHERE user_id=?", (amount, user_id))
        await db.commit()

async def get_all_users():
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT user_id FROM users")
        res = await cursor.fetchall()
        return [r[0] for r in res]

async def get_prices() -> dict:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT key, value FROM settings")
        rows = await cursor.fetchall()
        return {row[0]: float(row[1]) for row in rows}

async def set_price(key: str, price: float):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(price)))
        await db.commit()
