# trading-signals-website/config.py

import os
from datetime import timedelta

# =============================================================================
# CẤU HÌNH TRADING
# =============================================================================

COINS = [
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT",
    "ADAUSDT", "DOGEUSDT", "AVAXUSDT", "DOTUSDT", "LINKUSDT"
]

INTERVAL = os.getenv("INTERVAL", "15m")
LIMIT = int(os.getenv("LIMIT", "500"))
SQUEEZE_THRESHOLD = float(os.getenv("SQUEEZE_THRESHOLD", "0.015"))
COOLDOWN_MINUTES = int(os.getenv("COOLDOWN_MINUTES", "30"))

# =============================================================================
# CẤU HÌNH WEBSITE & BẢO MẬT
# =============================================================================

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")

# Key types và durations (giờ)
KEY_TYPES = {
    "24h": 24,
    "1w": 168,
    "1m": 720,
    "3m": 2160,
    "forever": 876000
}

# =============================================================================
# MÔ TẢ COMBO
# =============================================================================

COMBO_DETAILS = {
    "FVG Squeeze Pro": {
        "description": "Kết hợp Squeeze Momentum và FVG (Fair Value Gap)",
        "conditions": "BB Width < 0.015, Volume spike > 130%, Giá trên EMA200",
        "rr_ratio": "1:3",
        "timeframe": "15m-1h",
        "success_rate": "72%"
    }
}
