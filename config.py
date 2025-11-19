# trading-signals-website/config.py

import os
from datetime import timedelta

# =============================================================================
# CẤU HÌNH TRADING
# =============================================================================

COINS = [
    # Major coins
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT",
    "ADAUSDT", "DOGEUSDT", "AVAXUSDT", "DOTUSDT", "LINKUSDT",
    # Mid caps
    "MATICUSDT", "LTCUSDT", "ATOMUSDT", "UNIUSDT", "FILUSDT",
    # Small caps
    "NEARUSDT", "ALGOUSDT", "ETCUSDT", "XLMUSDT", "EGLDUSDT"
]

INTERVAL = os.getenv("INTERVAL", "15m")
LIMIT = int(os.getenv("LIMIT", "500"))
SQUEEZE_THRESHOLD = float(os.getenv("SQUEEZE_THRESHOLD", "0.015"))
COOLDOWN_MINUTES = int(os.getenv("COOLDOWN_MINUTES", "30"))

# =============================================================================
# CẤU HÌNH WEBSITE & BẢO MẬT
# =============================================================================

# Admin credentials
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

# Session settings
SESSION_TIMEOUT = timedelta(hours=24)
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")

# Key types and durations (in hours)
KEY_TYPES = {
    "24h": 24,
    "1w": 168,
    "1m": 720,
    "3m": 2160,
    "forever": 876000  # ~100 years
}

# =============================================================================
# CẤU HÌNH GIAO DIỆN
# =============================================================================

THEME_COLORS = {
    "primary": "#6366f1",
    "secondary": "#8b5cf6", 
    "success": "#10b981",
    "danger": "#ef4444",
    "warning": "#f59e0b",
    "info": "#3b82f6",
    "dark": "#1f2937",
    "light": "#f8fafc"
}

# =============================================================================
# MÔ TẢ COMBO CHI TIẾT
# =============================================================================

COMBO_DETAILS = {
    "FVG Squeeze Pro": {
        "description": "Kết hợp Squeeze Momentum và FVG (Fair Value Gap)",
        "conditions": "BB Width < 0.015, Volume spike > 130%, Giá trên EMA200",
        "rr_ratio": "1:3",
        "timeframe": "15m-1h",
        "success_rate": "72%"
    },
    "MACD Order Block Retest": {
        "description": "MACD Cross kết hợp retest Order Block",
        "conditions": "MACD histogram chuyển dương, Retest OB trong 0.5 ATR",
        "rr_ratio": "1:2.5", 
        "timeframe": "1h-4h",
        "success_rate": "68%"
    },
    # ... thêm các combo khác với cùng cấu trúc
}

# Ngôn ngữ
LANGUAGES = {
    'en': 'English',
    'vi': 'Tiếng Việt'
}
