# data_collector.py
import ccxt
import pandas as pd
from dotenv import load_dotenv
import os
import requests

def get_coingecko_data(symbols):
    """
    دریافت مارکت کپ و Circulating Supply از CoinGecko برای لیست توکن‌ها.
    :param symbols: لیستی از نمادهای توکن (مثل ['btc', 'eth', ...])
    :return: دیکشنری شامل داده‌های مورد نیاز.
    """
    
    # 1. آماده‌سازی لیست آیدی‌های CoinGecko (نیاز به تطبیق نام‌ها)
    # توجه: CCXT از جفت ارز (BTC/USDT) استفاده می‌کند، اما CG از آیدی توکن (bitcoin) استفاده می‌کند.
    # برای ساده‌سازی، فرض می‌کنیم CCXT Symbols را به آیدی‌های CG تبدیل می‌کنیم.
    
    # برای شروع، فقط 250 ارز برتر را دریافت می‌کنیم:
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        'vs_currency': 'usd',
        'per_page': 250,
        'page': 1,
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status() # بررسی خطاهای HTTP
        data = response.json()
        
        # 2. فیلتر داده‌ها برای استخراج مارکت کپ و نماد
        market_data = {}
        for coin in data:
            # CoinGecko نماد را lowercase می‌دهد
            symbol = coin.get('symbol', '').upper()
            market_data[symbol] = {
                'market_cap': coin.get('market_cap'),
                'total_volume': coin.get('total_volume')
            }
        
        return market_data
        
    except requests.RequestException as e:
        print(f"❌ خطا در اتصال به CoinGecko: {e}")
        return {}

# data_collector.py (تابع fetch_and_filter_markets را به صورت زیر جایگزین کنید)

# ... (بقیه توابع، شامل get_coingecko_data و initialize_exchange، بدون تغییر باقی می‌مانند) ...


def fetch_and_filter_markets(exchange):
    """
    1. دریافت مارکت‌کپ از CoinGecko.
    2. اعمال فیلتر ساختاری TraxCry.
    3. بررسی وجود جفت ارز در CoinEx با استفاده از fetch_markets().
    """
    
    # 1. دریافت داده‌های CoinGecko
    coingecko_data = get_coingecko_data(None)
    if not coingecko_data:
        return []

    # 2. دریافت لیست مارکت‌های صرافی (تست اصلی ارتباط CoinEx)
    try:
        # این فراخوانی از یک Public Endpoint استفاده می‌کند که نباید نیاز به API Key داشته باشد.
        markets = exchange.fetch_markets()
        available_symbols = set([m['symbol'] for m in markets]) # لیست جفت‌های موجود در صرافی (مثل 'BTC/USDT')
    except Exception as e:
        # اگر در اینجا خطا بدهد، مشکل همان اتصال پروکسی/احراز هویت عمومی است.
        print(f"❌ خطا در دریافت لیست مارکت‌های CoinEx. لطفاً پروکسی یا API KEY را بررسی کنید. خطا: {e}")
        return []


    # 3. اعمال فیلترهای ساختاری TraxCry
    # تنظیمات از متغیرهای global در بالای فایل data_collector.py گرفته می‌شود.
    # فرض می‌کنیم MAX_MARKET_CAP و MIN_DAILY_VOLUME هنوز تعریف شده‌اند.
    
    # 4. فیلتر کردن نهایی
    filtered_symbols = []
    
    for symbol_base, data in coingecko_data.items():
        mc = data.get('market_cap', 0)
        vol = data.get('total_volume', 0)
        
        # تبدیل نماد به فرمت CCXT
        ccxt_symbol = f"{symbol_base}/USDT" 
        
        # اعمال فیلتر: مارکت کپ < $500M و حجم > $1M
        if (mc is not None and mc <= MAX_MARKET_CAP) and \
           (vol is not None and vol >= MIN_DAILY_VOLUME):
            
            # بررسی نهایی: آیا این جفت ارز در CoinEx موجود است؟
            if ccxt_symbol in available_symbols:
                filtered_symbols.append(ccxt_symbol)
            
    return filtered_symbols

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


