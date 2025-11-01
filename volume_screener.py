# volume_screener.py
import pandas as pd
import ccxt

def calculate_volume_spike(exchange, symbol, days=7):
    """
    محاسبه Volume Spike Ratio و تغییر قیمت 24 ساعته.
    
    :param exchange: نمونه CCXT صرافی
    :param symbol: جفت ارز (مثلاً BTC/USDT)
    :param days: تعداد روزهای Historical برای محاسبه EMA
    :return: (Volume Ratio, Price Change %, is_traxcry_candidate)
    """
    try:
        # 1. دریافت داده‌های کندل روزانه (1d) برای 8 روز اخیر (7 روز برای EMA + 1 روز برای Current)
        # تایم‌فریم '1d' و limit = days + 1 
        ohlcv = exchange.fetch_ohlcv(symbol, '1d', limit=days + 1)
        if not ohlcv or len(ohlcv) < days + 1:
            return 0, 0, False

        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        # 2. محاسبه EMA 7 روزه (میانگین حجم تاریخی)
        historical_volumes = df['volume'].iloc[:-1] # 7 روز گذشته
        current_volume = df['volume'].iloc[-1]      # حجم امروز
        
        # اطمینان از حداقل داده و محاسبه EMA (میانگین متحرک نمایی)
        if len(historical_volumes) == 0:
            return 0, 0, False

        # محاسبه EMA 7 روزه بر اساس داده‌های حجم تاریخی
        ema_7 = historical_volumes.ewm(span=days, adjust=False).mean().iloc[-1]
        
        # 3. محاسبه Volume Ratio
        volume_ratio = current_volume / ema_7 if ema_7 > 0 else 0
        
        # 4. محاسبه Price Change 24h
        open_price_24h_ago = df['open'].iloc[-1] # قیمت باز شدن کندل امروز
        current_price = df['close'].iloc[-1]     # قیمت بسته شدن کندل امروز (لحظه حال)
        
        price_change_percent = ((current_price - open_price_24h_ago) / open_price_24h_ago) * 100
        
        # 5. اعمال فیلتر نهایی TraxCry
        IS_ABNORMAL_SPIKE = (volume_ratio >= 3.0) and (price_change_percent <= 10.0)
        
        return volume_ratio, price_change_percent, IS_ABNORMAL_SPIKE
        
    except Exception as e:
        # print(f"خطا در پردازش حجم برای {symbol}: {e}")
        return 0, 0, False

# # نحوه استفاده:
# # (این بخش در فایل اصلی اجرا می‌شود)
