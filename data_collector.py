# data_collector.py
import ccxt
import pandas as pd
from dotenv import load_dotenv
import os

# بارگذاری متغیرهای محیطی از فایل .env
load_dotenv()
EXCHANGE_ID = os.getenv("EXCHANGE_ID")
API_KEY = os.getenv("API_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")

# --- تنظیمات فیلتر ساختاری TraxCry ---
MAX_MARKET_CAP = 500_000_000  # 500 میلیون دلار
MIN_DAILY_VOLUME = 1_000_000  # 1 میلیون دلار

def initialize_exchange():
    """برقراری اتصال امن و خصوصی با صرافی."""
    if not EXCHANGE_ID or not API_KEY or not SECRET_KEY:
        print("خطا: تنظیمات API در فایل .env کامل نیست.")
        return None
    
    # اطمینان از اینکه ccxt کلاس صرافی مورد نظر را دارد
    if EXCHANGE_ID not in ccxt.exchanges:
        print(f"خطا: صرافی '{EXCHANGE_ID}' توسط CCXT پشتیبانی نمی‌شود.")
        return None
        
    exchange_class = getattr(ccxt, EXCHANGE_ID)
    exchange = exchange_class({
        'apiKey': API_KEY,
        'secret': SECRET_KEY,
        'enableRateLimit': True,
    })
    return exchange

def fetch_and_filter_markets(exchange):
    """
    دریافت لیست بازارها و اعمال فیلترهای مارکت‌کپ و حجم.
    (توجه: API های CCXT مارکت‌کپ را مستقیم نمی‌دهند؛ باید تخمین بزنیم.)
    """
    try:
        # 1. دریافت همه تیکرها (برای حجم 24h و قیمت)
        tickers = exchange.fetch_tickers()
        
        # 2. فیلتر کردن جفت‌های USDT و اعمال فیلتر ساختاری
        filtered_symbols = []
        
        for symbol, ticker in tickers.items():
            # فیلتر کردن جفت‌های USDT و توکن‌های ETF/اهرمی
            if symbol.endswith('/USDT') and '3L' not in symbol and '3S' not in symbol:
                
                base_currency = symbol.split('/')[0]
                
                # بررسی حجم
                volume_24h = ticker.get('quoteVolume', 0) 
                if volume_24h >= MIN_DAILY_VOLUME:
                    
                    # در CCXT، Market Cap را باید از منبع دیگری (مثل CoinGecko) دریافت کرد، 
                    # اما برای MVP اولیه، ما روی حجم و قیمت تمرکز می‌کنیم.
                    # فرض می‌کنیم ارزهایی که volume پایینی دارند احتمالاً MC پایینی هم دارند.
                    
                    # در این مرحله، ما فقط فیلتر حجم را اعمال می‌کنیم
                    filtered_symbols.append(symbol)
                    
        return filtered_symbols
        
    except Exception as e:
        print(f"خطا در دریافت و فیلتر بازارها: {e}")
        return []

# # نحوه استفاده (برای تست):
# exchange = initialize_exchange()
# if exchange:
#     initial_watchlist = fetch_and_filter_markets(exchange)
#     print(f"واچ‌لیست اولیه (بر اساس حجم): {initial_watchlist[:10]}")
