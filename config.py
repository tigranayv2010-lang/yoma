import os
from dotenv import load_dotenv

load_dotenv()

# --- Bot Settings ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

# --- Discord Boost / Gorgona API ---
GORGONA_API_KEY = os.getenv("GORGONA_API_KEY")
GORGONA_BASE_URL = os.getenv("GORGONA_BASE_URL", "https://api.gorgonaboost.xyz")

# --- CryptoBot ---
CRYPTO_BOT_TOKEN = os.getenv("CRYPTO_BOT_TOKEN")

# --- 3x-ui (VPN) Settings ---
XUI_URL = os.getenv("XUI_URL", "")
XUI_USERNAME = os.getenv("XUI_USERNAME", "")
XUI_PASSWORD = os.getenv("XUI_PASSWORD", "")
XUI_API_TOKEN = os.getenv("XUI_API_TOKEN", "")
XUI_HOST = os.getenv("XUI_HOST", "")
XUI_PORT = int(os.getenv("XUI_PORT", "47506"))

# Default VPN Prices (USDT)
DEFAULT_PRICE_VPN_1M = float(os.getenv("DEFAULT_PRICE_VPN_1M", "1.5"))
DEFAULT_PRICE_VPN_3M = float(os.getenv("DEFAULT_PRICE_VPN_3M", "4.0"))
DEFAULT_PRICE_VPN_6M = float(os.getenv("DEFAULT_PRICE_VPN_6M", "7.5"))
DEFAULT_PRICE_VPN_12M = float(os.getenv("DEFAULT_PRICE_VPN_12M", "14.0"))

# --- Reseller API ---
RESELLER_API_KEY = os.getenv("RESELLER_API_KEY", "sb_a8ef337cf2ac4991bd83bfe2c21c8acee2263811f809ca73")
RESELLER_BASE_URL = os.getenv("RESELLER_BASE_URL", "https://worker-production-53ca.up.railway.app")

# Reseller products mapping (id: sell_price)
RESELLER_PRICES = {
    1: 0.60,  # Gemini
    13: 2.10, # Chat GPT
    20: 1.20, # Quillbot
    23: 1.40, # Youtube
    24: 2.40, # Capcut
    27: 2.10  # Canva
}
RESELLER_EXCLUDE_IDS = [6, 30]
