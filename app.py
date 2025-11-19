#!/usr/bin/env python3
print("🚀 Starting Trading Signals Website...")
print(f"Python version: {__import__('sys').version}")
print(f"Working directory: {__import__('os').getcwd()}")
print("=" * 50)

import os
import sys
import json
import threading
import logging
import time
import uuid
import secrets
from datetime import datetime, timedelta, timezone
from functools import wraps

import requests
import pandas as pd
from flask import Flask, jsonify, render_template, request, session, redirect, url_for
from apscheduler.schedulers.background import BackgroundScheduler
from ta.trend import MACD, EMAIndicator
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands, AverageTrueRange

from config import (
    COINS, INTERVAL, LIMIT, SQUEEZE_THRESHOLD, COOLDOWN_MINUTES,
    ADMIN_USERNAME, ADMIN_PASSWORD, SECRET_KEY, KEY_TYPES, COMBO_DETAILS,
    THEME_COLORS, LANGUAGES
)

# =============================================================================
# CONFIGURATION & LOGGING
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = SECRET_KEY

# Thread safety
data_lock = threading.Lock()

# File paths
DATA_FILE = 'trading_signals.json'
KEYS_FILE = 'access_keys.json'
USERS_FILE = 'users.json'

# =============================================================================
# AUTHENTICATION & AUTHORIZATION
# =============================================================================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session or not session['user'].get('is_admin', False):
            return jsonify({"error": "Admin access required"}), 403
        return f(*args, **kwargs)
    return decorated_function

# =============================================================================
# DATA MANAGEMENT
# =============================================================================

def load_json_file(filename, default=None):
    """Load JSON file with error handling"""
    if default is None:
        default = {}
    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Error loading {filename}: {e}")
    return default

def save_json_file(filename, data):
    """Save JSON file with error handling"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Error saving {filename}: {e}")
        return False

def load_data():
    return load_json_file(DATA_FILE, {"signals": [], "stats": {}})

def save_data(data):
    return save_json_file(DATA_FILE, data)

def load_keys():
    return load_json_file(KEYS_FILE, {"keys": {}})

def save_keys(keys_data):
    return save_json_file(KEYS_FILE, keys_data)

def load_users():
    return load_json_file(USERS_FILE, {"users": {}})

def save_users(users_data):
    return save_json_file(USERS_FILE, users_data)

# =============================================================================
# KEY MANAGEMENT
# =============================================================================

def generate_key(key_type):
    """Generate a new access key"""
    key_data = {
        "key": secrets.token_urlsafe(16),
        "type": key_type,
        "duration_hours": KEY_TYPES[key_type],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": (datetime.now(timezone.utc) + timedelta(hours=KEY_TYPES[key_type])).isoformat(),
        "is_active": True,
        "used_by": None,
        "used_at": None
    }
    return key_data

def validate_key(access_key, nickname):
    """Validate access key and nickname"""
    keys_data = load_keys()
    users_data = load_users()
    
    # Find the key
    for key_id, key_data in keys_data.get("keys", {}).items():
        if (key_data["key"] == access_key and 
            key_data["is_active"] and 
            datetime.fromisoformat(key_data["expires_at"]) > datetime.now(timezone.utc)):
            
            # Check if key is already used
            if key_data["used_by"] is None:
                # First time use - assign to nickname
                key_data["used_by"] = nickname
                key_data["used_at"] = datetime.now(timezone.utc).isoformat()
                keys_data["keys"][key_id] = key_data
                save_keys(keys_data)
                
                # Create user record
                users_data["users"][nickname] = {
                    "key_id": key_id,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "last_login": datetime.now(timezone.utc).isoformat(),
                    "is_admin": False
                }
                save_users(users_data)
                return True
                
            elif key_data["used_by"] == nickname:
                # Existing user - update last login
                users_data["users"][nickname]["last_login"] = datetime.now(timezone.utc).isoformat()
                save_users(users_data)
                return True
    
    return False

# =============================================================================
# TRADING ENGINE (giữ nguyên từ code trước)
# =============================================================================

def get_klines(symbol, max_retries=3):
    """Fetch klines from Binance with enhanced error handling"""
    # Implementation từ code trước
    pass

def add_indicators(df):
    """Add technical indicators to dataframe"""
    # Implementation từ code trước
    pass

def scan():
    """Main scanning function with enhanced logging"""
    # Implementation từ code trước
    pass

# Trading combos (giữ nguyên 18 combos từ code trước)
def combo1_fvg_squeeze_pro(df):
    """FVG Squeeze Pro"""
    try:
        last = df.iloc[-1]
        prev = df.iloc[-2]
        
        squeeze = (last.bb_width < SQUEEZE_THRESHOLD and 
                  last.bb_upper < last.kc_upper and 
                  last.bb_lower > last.kc_lower)
        breakout_up = last.close > last.bb_upper and prev.close <= prev.bb_upper
        vol_spike = last.volume > last.volume_ma20 * 1.3
        trend_up = last.close > last.ema200
        rsi_ok = last.rsi14 < 68
        
        if squeeze and breakout_up and vol_spike and trend_up and rsi_ok:
            entry = last.close
            sl = entry - 1.5 * last.atr
            tp = entry + 3.0 * last.atr
            return "LONG", entry, sl, tp, "FVG Squeeze Pro"
        
        breakout_down = last.close < last.bb_lower and prev.close >= prev.bb_lower
        if squeeze and breakout_down and vol_spike and last.close < last.ema200:
            entry = last.close
            sl = entry + 1.5 * last.atr
            tp = entry - 3.0 * last.atr
            return "SHORT", entry, sl, tp, "FVG Squeeze Pro"
            
    except Exception as e:
        logger.error(f"Combo1 error: {e}")
    
    return None

def combo2_macd_ob_retest(df):
    """MACD Order Block Retest"""
    try:
        last = df.iloc[-1]
        prev = df.iloc[-2]
        
        macd_cross_up = last.macd > last.macd_signal and prev.macd <= prev.macd_signal
        price_above_ema200 = last.close > last.ema200
        
        ob_zone = None
        if all(df["close"].iloc[-3:] > df["open"].iloc[-3:]):
            ob_zone = df["low"].iloc[-5:-2].min()
        
        retest = ob_zone is not None and last.low <= ob_zone + last.atr * 0.5
        vol_confirm = last.volume > df["volume"].mean() * 1.1
        
        if macd_cross_up and price_above_ema200 and retest and vol_confirm:
            entry = last.close
            sl = ob_zone - last.atr
            tp = entry + 2.5 * last.atr
            return "LONG", entry, sl, tp, "MACD Order Block Retest"
            
    except Exception as e:
        logger.error(f"Combo2 error: {e}")
    
    return None

def combo3_stop_hunt_squeeze(df):
    """Stop Hunt Squeeze"""
    try:
        last = df.iloc[-1]
        
        squeeze = last.bb_width < SQUEEZE_THRESHOLD
        stop_hunt = False
        
        if last.body > 0:
            if last.close > last.open:
                stop_hunt = (last.lower_wick / last.body > 2)
            else:
                stop_hunt = (last.upper_wick / last.body > 2)
        
        breakout_up = last.close > last.bb_upper
        
        if squeeze and stop_hunt and breakout_up:
            entry = last.close
            sl = last.low - last.atr
            tp = entry + 2.8 * last.atr
            return "LONG", entry, sl, tp, "Stop Hunt Squeeze"
            
    except Exception as e:
        logger.error(f"Combo3 error: {e}")
    
    return None

def combo4_fvg_ema_pullback(df):
    """FVG EMA Pullback"""
    try:
        last = df.iloc[-1]
        
        fvg_bull_zones = df[df["fvg_bull"]]
        fvg_pullback = False
        
        if not fvg_bull_zones.empty and df["fvg_bull"].iloc[-5:].any():
            fvg_pullback = last.low <= fvg_bull_zones["high"].max()
        
        cross_up = last.ema8 > last.ema21 and df["ema8"].iloc[-2] <= df["ema21"].iloc[-2]
        
        if fvg_pullback and cross_up:
            entry = last.close
            sl = last.low - last.atr * 0.8
            tp = entry + 2.0 * last.atr
            return "LONG", entry, sl, tp, "FVG EMA Pullback"
            
    except Exception as e:
        logger.error(f"Combo4 error: {e}")
    
    return None

def combo5_fvg_macd_divergence(df):
    """FVG + MACD Divergence"""
    try:
        last = df.iloc[-1]
        
        hist = df["macd_hist"]
        low = df["low"]
        
        divergence = hist.iloc[-1] > hist.iloc[-3] and low.iloc[-1] < low.iloc[-3]
        fvg = df["fvg_bull"].iloc[-8:].any()
        rsi_ok = last.rsi14 < 30
        
        if divergence and fvg and rsi_ok:
            entry = last.close
            sl = low.iloc[-5:].min() - last.atr
            tp = entry + 2.5 * last.atr
            return "LONG", entry, sl, tp, "FVG + MACD Divergence"
            
    except Exception as e:
        logger.error(f"Combo5 error: {e}")
    
    return None

def combo6_ob_liquidity_grab(df):
    """Order Block + Liquidity Grab"""
    try:
        last = df.iloc[-1]
        
        ob = df["low"].iloc[-6:-3].min()
        liquidity_grab = (last.lower_wick / last.body > 2.5) if last.body > 0 else False
        retest_ob = last.close > ob
        macd_pos = last.macd_hist > 0
        
        if liquidity_grab and retest_ob and macd_pos:
            entry = last.close
            sl = last.low - last.atr
            tp = entry + 1.8 * last.atr
            return "LONG", entry, sl, tp, "Order Block + Liquidity Grab"
            
    except Exception as e:
        logger.error(f"Combo6 error: {e}")
    
    return None

def combo7_stop_hunt_fvg_retest(df):
    """Stop Hunt + FVG Retest"""
    try:
        last = df.iloc[-1]
        
        stop_hunt = (last.lower_wick / last.body > 2) if last.body > 0 else False
        fvg_after = df["fvg_bull"].iloc[-3:]
        retest = (last.low <= df["high"].shift(1).max()) if fvg_after.any() else False
        
        if stop_hunt and fvg_after.any() and retest:
            entry = last.close
            sl = last.low - 0.5 * last.atr
            tp = entry + 1.5 * last.atr
            return "LONG", entry, sl, tp, "Stop Hunt + FVG Retest"
            
    except Exception as e:
        logger.error(f"Combo7 error: {e}")
    
    return None

def combo8_fvg_macd_hist_spike(df):
    """FVG + MACD Hist Spike"""
    try:
        last = df.iloc[-1]
        
        if len(df) >= 5:
            current_hist = df["macd_hist"].iloc[-3:].values
            prev_hist = df["macd_hist"].iloc[-4:-1].values
            if len(current_hist) == 3 and len(prev_hist) == 3:
                hist_spike = (current_hist > prev_hist).all()
            else:
                hist_spike = False
        else:
            hist_spike = False
            
        fvg = df["fvg_bull"].iloc[-5:].any()
        price_above_vwap = last.close > last.vwap
        
        if hist_spike and fvg and price_above_vwap:
            entry = last.close
            sl = last.low - last.atr
            tp = entry + 2.5 * last.atr
            return "LONG", entry, sl, tp, "FVG + MACD Hist Spike"
            
    except Exception as e:
        logger.error(f"Combo8 error: {e}")
    
    return None

def combo9_ob_fvg_confluence(df):
    """OB + FVG Confluence"""
    try:
        last = df.iloc[-1]
        
        ob = df["low"].iloc[-10:-5].min()
        fvg_bull_zones = df[df["fvg_bull"]]
        fvg_zone = 0
        
        if not fvg_bull_zones.empty and df["fvg_bull"].iloc[-10:].any():
            fvg_zone = fvg_bull_zones["high"].max()
        
        confluence = (abs(ob - fvg_zone) < last.atr * 0.5) if fvg_zone > 0 else False
        engulfing = last.close > last.open and last.open < df["close"].iloc[-2]
        volume_delta = last.volume > df["volume"].mean() * 1.5
        
        if confluence and engulfing and volume_delta:
            entry = last.close
            sl = min(ob, fvg_zone) - last.atr if fvg_zone > 0 else ob - last.atr
            tp = entry + 2.0 * last.atr
            return "LONG", entry, sl, tp, "OB + FVG Confluence"
            
    except Exception as e:
        logger.error(f"Combo9 error: {e}")
    
    return None

def combo10_smc_ultimate(df):
    """SMC Ultimate"""
    try:
        last = df.iloc[-1]
        
        squeeze = last.bb_width < SQUEEZE_THRESHOLD
        fvg = df["fvg_bull"].iloc[-5:].any()
        macd_up = last.macd_hist > 0 and last.macd_hist > df["macd_hist"].iloc[-2]
        liquidity = (last.lower_wick / last.body > 2) if last.body > 0 else False
        ob_retest = last.low <= df["low"].iloc[-5:-2].min()
        
        if squeeze and fvg and macd_up and liquidity and ob_retest:
            entry = last.close
            sl = last.low - last.atr
            tp = entry + 3.5 * last.atr
            return "LONG", entry, sl, tp, "SMC Ultimate"
            
    except Exception as e:
        logger.error(f"Combo10 error: {e}")
    
    return None

def combo11_fvg_ob_liquidity_break(df):
    """FVG + Order Block + Liquidity Break"""
    try:
        last = df.iloc[-1]
        
        # FVG bullish
        fvg = last.fvg_bull or df["fvg_bull"].iloc[-3:].any()
        
        # Order Block
        ob = df["low"].iloc[-5:].min()
        
        # Liquidity Break
        liquidity_break = last.close > df["high"].iloc[-5:].max()
        
        # Volume
        vol_spike = last.volume > last.volume_ma20 * 1.5
        
        if fvg and liquidity_break and vol_spike:
            entry = last.close
            sl = ob - 0.5 * last.atr
            tp = entry + 2.0 * last.atr
            return "LONG", entry, sl, tp, "FVG OB Liquidity Break"
            
    except Exception as e:
        logger.error(f"Combo11 error: {e}")
    
    return None

def combo12_liquidity_grab_fvg_retest(df):
    """Liquidity Grab + FVG Retest"""
    try:
        last = df.iloc[-1]
        
        # Liquidity Grab
        liquidity_grab = (last.lower_wick / last.body > 2.5) if last.body > 0 else False
        
        # FVG Retest
        fvg_zones = df[df["fvg_bull"]]
        fvg_retest = False
        if not fvg_zones.empty and df["fvg_bull"].iloc[-5:].any():
            fvg_retest = last.low <= fvg_zones["high"].max()
        
        # MACD
        macd_ok = last.macd_hist > 0 and last.macd_hist > df["macd_hist"].iloc[-2]
        
        if liquidity_grab and fvg_retest and macd_ok:
            entry = last.close
            sl = last.low - 0.8 * last.atr
            tp = entry + 1.8 * last.atr
            return "LONG", entry, sl, tp, "Liquidity Grab FVG Retest"
            
    except Exception as e:
        logger.error(f"Combo12 error: {e}")
    
    return None

def combo13_fvg_macd_momentum_scalp(df):
    """COMBO 13: FVG + MACD Momentum Scalp"""
    try:
        last = df.iloc[-1]
        
        # FVG recent
        fvg = df["fvg_bull"].iloc[-2:].any() and last.close > last.open
        
        # MACD momentum
        macd_mom = last.macd > last.macd_signal and abs(last.macd_hist) > abs(df["macd_hist"].iloc[-2])
        
        # VWAP
        above_vwap = last.close > last.vwap
        
        # Low volatility
        low_vol = (last.atr / last.close) < 0.02
        
        if fvg and macd_mom and above_vwap and low_vol:
            entry = last.close
            sl = last.low - 0.5 * last.atr
            tp = entry + 1.2 * last.atr
            return "LONG", entry, sl, tp, "FVG MACD Momentum Scalp"
            
    except Exception as e:
        logger.error(f"Combo13 error: {e}")
    
    return None

def combo14_ob_liquidity_macd_div(df):
    """COMBO 14: Order Block + Liquidity + MACD Divergence"""
    try:
        last = df.iloc[-1]
        
        # Order Block
        ob = df["low"].iloc[-7:-2].min()
        
        # Liquidity sweep
        liquidity = (last.lower_wick / last.body > 2.0) if last.body > 0 else False
        
        # MACD Divergence
        divergence = (df["macd_hist"].iloc[-1] > df["macd_hist"].iloc[-3] and 
                     df["low"].iloc[-1] < df["low"].iloc[-3])
        
        # Entry confirmation
        entry_ok = last.close > ob
        
        if liquidity and divergence and entry_ok:
            entry = last.close
            sl = ob - 0.3 * last.atr
            tp = entry + 2.5 * last.atr
            return "LONG", entry, sl, tp, "OB Liquidity MACD Div"
            
    except Exception as e:
        logger.error(f"Combo14 error: {e}")
    
    return None

def combo15_vwap_ema_volume_scalp(df):
    """COMBO 15: VWAP + EMA Cross + Volume Spike Scalp"""
    try:
        last = df.iloc[-1]
        prev = df.iloc[-2]
        
        # EMA Cross (8 & 21)
        ema_cross = last.ema8 > last.ema21 and prev.ema8 <= prev.ema21
        
        # Price above VWAP
        above_vwap = last.close > last.vwap
        
        # Volume spike (180% of 20-period average)
        vol_spike = last.volume > last.volume_ma20 * 1.8
        
        # RSI not overbought (below 60)
        rsi_ok = last.rsi14 < 60
        
        if ema_cross and above_vwap and vol_spike and rsi_ok:
            entry = last.close
            sl = last.low - 0.5 * last.atr
            tp = entry + 1.0 * last.atr
            return "LONG", entry, sl, tp, "VWAP EMA Volume Scalp"
            
    except Exception as e:
        logger.error(f"Combo15 error: {e}")
    
    return None

def combo16_rsi_extreme_bounce(df):
    """COMBO 16: RSI Extreme + Price Action Bounce"""
    try:
        last = df.iloc[-1]
        prev = df.iloc[-2]
        
        # RSI Extreme (oversold for long, overbought for short)
        rsi_oversold = last.rsi14 < 25
        rsi_overbought = last.rsi14 > 75
        
        # Price Action Bounce patterns
        bullish_engulfing = (last.close > last.open and 
                           prev.close < prev.open and 
                           last.close > prev.open and 
                           last.open < prev.close)
        
        bearish_engulfing = (last.close < last.open and 
                           prev.close > prev.open and 
                           last.close < prev.open and 
                           last.open > prev.close)
        
        hammer = (last.lower_wick > 2 * last.body and 
                last.upper_wick < 0.2 * last.body and 
                last.close > last.open) if last.body > 0 else False
                
        shooting_star = (last.upper_wick > 2 * last.body and 
                       last.lower_wick < 0.2 * last.body and 
                       last.close < last.open) if last.body > 0 else False
        
        # Volume confirmation
        vol_ok = last.volume > last.volume_ma20 * 1.2
        
        # LONG: RSI oversold + bullish pattern
        if rsi_oversold and (bullish_engulfing or hammer) and vol_ok:
            entry = last.close
            sl = last.low - 0.8 * last.atr
            tp = entry + 1.5 * last.atr
            return "LONG", entry, sl, tp, "RSI Extreme Bounce LONG"
            
        # SHORT: RSI overbought + bearish pattern  
        if rsi_overbought and (bearish_engulfing or shooting_star) and vol_ok:
            entry = last.close
            sl = last.high + 0.8 * last.atr
            tp = entry - 1.5 * last.atr
            return "SHORT", entry, sl, tp, "RSI Extreme Bounce SHORT"
            
    except Exception as e:
        logger.error(f"Combo16 error: {e}")
    
    return None

def combo17_ema_stack_volume_confirmation(df):
    """COMBO 17: EMA Stack + Volume Confirmation"""
    try:
        last = df.iloc[-1]
        
        # EMA Stack đẹp (xếp chồng tăng)
        ema_stack = (last.ema8 > last.ema21 > last.ema50 > last.ema200)
        
        # Giá trên tất cả EMA
        price_above_all = (last.close > last.ema8 and
                           last.close > last.ema21 and
                           last.close > last.ema50 and
                           last.close > last.ema200)
        
        # Volume tăng ít nhất 50% so với trung bình
        volume_confirm = last.volume > last.volume_ma20 * 1.5
        
        # RSI không quá mua (dưới 65)
        rsi_ok = last.rsi14 < 65
        
        # Pullback về EMA8 hoặc EMA21 rồi bật lên
        pullback_bounce = (
            (last.low <= last.ema8 and last.close > last.ema8) or
            (last.low <= last.ema21 and last.close > last.ema21)
        )
        
        if (ema_stack and price_above_all and volume_confirm and
            rsi_ok and pullback_bounce):
            
            entry = last.close
            # SL dưới EMA21 hoặc low của nến
            sl = min(last.ema21, last.low) - 0.3 * last.atr
            tp = entry + 1.8 * last.atr
            
            return "LONG", entry, sl, tp, "EMA Stack Volume Confirmation"
            
    except Exception as e:
        logger.error(f"Combo17 error: {e}")
    
    return None

def combo18_support_resistance_break_retest(df):
    """COMBO 18: Support/Resistance Break + Retest"""
    try:
        last = df.iloc[-1]
        prev = df.iloc[-2]

        # Xác định Support/Resistance gần nhất
        resistance_level = df["high"].iloc[-20:-1].max()
        support_level = df["low"].iloc[-20:-1].min()
        
        # Breakout trên Resistance
        resistance_break = (last.close > resistance_level and
                            prev.close <= resistance_level)
        
        # Breakout dưới Support
        support_break = (last.close < support_level and
                         prev.close >= support_level)
        
        # Volume xác nhận breakout (tăng ít nhất 80%)
        volume_spike = last.volume > last.volume_ma20 * 1.8
        
        # Retest sau breakout
        retest_confirmation = False
        if resistance_break:
            # Retest resistance trở thành support
            retest_confirmation = (last.low <= (resistance_level + last.atr * 0.2) and
                                   last.close > resistance_level)
        elif support_break:
            # Retest support trở thành resistance
            retest_confirmation = (last.high >= (support_level - last.atr * 0.2) and
                                   last.close < support_level)
        
        # MACD xác nhận momentum
        macd_confirm_long = (resistance_break and last.macd > last.macd_signal and last.macd_hist > 0)
        macd_confirm_short = (support_break and last.macd < last.macd_signal and last.macd_hist < 0)
            
        if (volume_spike and retest_confirmation):
            
            if resistance_break and macd_confirm_long:
                entry = last.close
                sl = resistance_level - 0.5 * last.atr
                tp = entry + 2.0 * last.atr
                return "LONG", entry, sl, tp, "Resistance Break Retest"
                
            elif support_break and macd_confirm_short:
                entry = last.close
                sl = support_level + 0.5 * last.atr
                tp = entry - 2.0 * last.atr
                return "SHORT", entry, sl, tp, "Support Break Retest"
                
    except Exception as e:
        logger.error(f"Combo18 error: {e}")
    
    return None

# =============================================================================
# FLASK ROUTES
# =============================================================================

@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nickname = request.form.get('nickname', '').strip()
        access_key = request.form.get('access_key', '').strip()
        
        # Admin login
        if nickname == ADMIN_USERNAME and access_key == ADMIN_PASSWORD:
            session['user'] = {
                'nickname': nickname,
                'is_admin': True,
                'login_time': datetime.now(timezone.utc).isoformat()
            }
            return redirect(url_for('dashboard'))
        
        # User login with key
        if validate_key(access_key, nickname):
            session['user'] = {
                'nickname': nickname,
                'is_admin': False,
                'login_time': datetime.now(timezone.utc).isoformat()
            }
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Key không hợp lệ hoặc đã được sử dụng bởi nickname khác")
    
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=session['user'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# =============================================================================
# API ROUTES
# =============================================================================

@app.route('/api/signals')
@login_required
def get_signals_api():
    """API: Get all active signals"""
    with data_lock:
        data = load_data()
        signals = data.get("signals", [])
    
    # Filter active signals and sort by timestamp
    active_signals = [s for s in signals if s.get('status', 'active') == 'active']
    active_signals.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return jsonify(active_signals)

@app.route('/api/stats')
@login_required  
def get_stats_api():
    """API: Get statistics"""
    with data_lock:
        data = load_data()
        signals = data.get("signals", [])
    
    # Calculate statistics
    closed_signals = [s for s in signals if s.get('status') == 'closed']
    
    stats = {
        "total_signals": len(signals),
        "active_signals": len([s for s in signals if s.get('status') == 'active']),
        "closed_signals": len(closed_signals),
        "win_rate": calculate_win_rate(closed_signals),
        "today_stats": get_period_stats(closed_signals, 'today'),
        "week_stats": get_period_stats(closed_signals, 'week'),
        "month_stats": get_period_stats(closed_signals, 'month')
    }
    
    return jsonify(stats)

@app.route('/api/vote/<signal_id>/<vote_type>', methods=['POST'])
@login_required
def vote_signal_api(signal_id, vote_type):
    """API: Vote for signal"""
    if vote_type not in ['win', 'lose']:
        return jsonify({"error": "Invalid vote type"}), 400
    
    user_ip = request.remote_addr
    
    with data_lock:
        data = load_data()
        signals = data.get("signals", [])
        
        # Find signal
        signal = next((s for s in signals if s['id'] == signal_id), None)
        if not signal:
            return jsonify({"error": "Signal not found"}), 404
        
        # Check if user already voted
        if user_ip in signal.get('voted_ips', []):
            return jsonify({"error": "You have already voted for this signal"}), 403
        
        # Record vote
        if vote_type == 'win':
            signal['votes_win'] = signal.get('votes_win', 0) + 1
        else:
            signal['votes_lose'] = signal.get('votes_lose', 0) + 1
        
        signal.setdefault('voted_ips', []).append(user_ip)
        
        # Close signal if enough votes
        total_votes = signal['votes_win'] + signal['votes_lose']
        if total_votes >= 5:
            signal['status'] = 'closed'
            signal['closed_at'] = datetime.now(timezone.utc).isoformat()
        
        save_data(data)
    
    return jsonify({
        "message": "Vote recorded successfully",
        "votes_win": signal['votes_win'],
        "votes_lose": signal['votes_lose'],
        "status": signal['status']
    })

# =============================================================================
# ADMIN ROUTES
# =============================================================================

@app.route('/admin/generate-key/<key_type>')
@admin_required
def generate_key_api(key_type):
    """API: Generate new key"""
    if key_type not in KEY_TYPES:
        return jsonify({"error": "Invalid key type"}), 400
    
    keys_data = load_keys()
    key_id = str(uuid.uuid4())
    keys_data["keys"][key_id] = generate_key(key_type)
    
    if save_keys(keys_data):
        return jsonify({
            "message": f"Key generated successfully",
            "key": keys_data["keys"][key_id]["key"],
            "expires": keys_data["keys"][key_id]["expires_at"]
        })
    else:
        return jsonify({"error": "Failed to save key"}), 500

@app.route('/admin/keys')
@admin_required
def get_keys_api():
    """API: Get all keys"""
    keys_data = load_keys()
    return jsonify(keys_data.get("keys", {}))

# =============================================================================
# SCHEDULER & BACKGROUND TASKS
# =============================================================================

def run_scheduler():
    """Run background scheduler"""
    logger.info("🚀 Starting Trading Signals Scheduler...")
    
    scheduler = BackgroundScheduler(timezone="UTC")
    
    # Scan every 15 minutes at specific times
    scheduler.add_job(scan, 'cron', minute='1,16,31,46')
    
    # Cleanup expired keys daily
    scheduler.add_job(cleanup_expired_keys, 'cron', hour=0, minute=0)
    
    # Run initial scan
    try:
        logger.info("🔍 Running initial scan...")
        scan()
    except Exception as e:
        logger.error(f"❌ Initial scan error: {e}")
    
    scheduler.start()
    logger.info("✅ Scheduler started successfully")
    
    # Keep the thread alive
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        scheduler.shutdown()

def cleanup_expired_keys():
    """Clean up expired keys"""
    keys_data = load_keys()
    current_time = datetime.now(timezone.utc)
    
    expired_count = 0
    for key_id, key_data in list(keys_data.get("keys", {}).items()):
        if datetime.fromisoformat(key_data["expires_at"]) < current_time:
            del keys_data["keys"][key_id]
            expired_count += 1
    
    if expired_count > 0:
        save_keys(keys_data)
        logger.info(f"🧹 Cleaned up {expired_count} expired keys")

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def calculate_win_rate(signals):
    """Calculate win rate from closed signals"""
    if not signals:
        return 0
    
    wins = sum(1 for s in signals if s.get('votes_win', 0) > s.get('votes_lose', 0))
    return round((wins / len(signals)) * 100, 1)

def get_period_stats(signals, period):
    """Get statistics for specific period"""
    now = datetime.now(timezone.utc)
    
    if period == 'today':
        start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == 'week':
        start_time = now - timedelta(days=now.weekday())
    elif period == 'month':
        start_time = now.replace(day=1)
    else:
        return {}
    
    period_signals = [s for s in signals if datetime.fromisoformat(s.get('closed_at', s['timestamp'])) >= start_time]
    
    wins = sum(1 for s in period_signals if s.get('votes_win', 0) > s.get('votes_lose', 0))
    losses = len(period_signals) - wins
    
    return {
        "total": len(period_signals),
        "wins": wins,
        "losses": losses,
        "win_rate": calculate_win_rate(period_signals) if period_signals else 0
    }

# =============================================================================
# APPLICATION STARTUP
# =============================================================================

# Start scheduler in background thread
scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
scheduler_thread.start()

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"🌐 Starting Flask server on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
