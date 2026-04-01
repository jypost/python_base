import os
from dotenv import load_dotenv

load_dotenv()

# OKX
OKX_API_KEY    = os.getenv("OKX_API_KEY")
OKX_SECRET_KEY = os.getenv("OKX_SECRET_KEY")
OKX_PASSPHRASE = os.getenv("OKX_PASSPHRASE")

# Binance
BINANCE_API_KEY    = os.getenv("BINANCE_API_KEY")
BINANCE_SECRET_KEY = os.getenv("BINANCE_SECRET_KEY")

# Telegram
TELEGRAM_TOKEN   = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# 구독 심볼 목록
SYMBOLS = [
    "BTC-USDT-SWAP",
    # "ETH-USDT-SWAP",
    # "SOL-USDT-SWAP",
    # "XRP-USDT-SWAP",
]

# OKX WebSocket 엔드포인트
OKX_WS_PUBLIC   = "wss://ws.okx.com:8443/ws/v5/public"
OKX_WS_BUSINESS = "wss://ws.okx.com:8443/ws/v5/business"
OKX_WS_PRIVATE  = "wss://ws.okx.com:8443/ws/v5/private"
OKX_REST_URL    = "https://www.okx.com"

# Binance WebSocket 엔드포인트
BINANCE_WS_PUBLIC  = "wss://fstream.binance.com/ws"
BINANCE_REST_URL   = "https://fapi.binance.com"
