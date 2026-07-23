from aiocryptopay import AioCryptoPay, Networks
import config

crypto_client = None

def init_crypto():
    global crypto_client
    crypto_client = AioCryptoPay(token=config.CRYPTO_BOT_TOKEN, network=Networks.MAIN_NET)

def get_crypto():
    global crypto_client
    return crypto_client
