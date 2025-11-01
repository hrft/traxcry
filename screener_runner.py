# screener_runner.py

import pandas as pd
from data_collector import initialize_exchange, fetch_and_filter_markets
from volume_screener import calculate_volume_spike

def run_traxcry_screener():
    """اجرای کامل فرآیند فیلترینگ TraxCry MVP."""
    print("🚀 در حال اجرای TraxCry Screener...")
    
    # 1. اتصال به صرافی
    exchange = initialize_exchange()
    if not exchange:
        return
    print(f"✅ اتصال به صرافی {exchange.id.upper()} برقرار شد.")

    # 2. دریافت و فیلتر اولیه (فیلتر ساختاری)
    initial_watchlist = fetch_and_filter_markets(exchange)
    print(f"🔍 تعداد ارزهای واجد شرایط اولیه: {len(initial_watchlist)}")
    
    if not initial_watchlist:
        print("❌ هیچ ارزی با حجم معاملات کافی یافت نشد. پایان اجرا.")
        return

    # 3. اعمال فیلتر حجم غیرمعمول (TraxCry Volume Filter)
    final_candidates = []
    
    print("\n⏳ در حال بررسی Volume Spike (حجم غیرمعمول)...")
    
    for symbol in initial_watchlist:
        # برای جلوگیری از محدودیت‌های Rate Limit، به صورت کند اجرا می‌کنیم.
        # در نسخه‌های پیشرفته‌تر، از حالت asynchronous استفاده می‌کنیم.
        
        volume_ratio, price_change, is_candidate = calculate_volume_spike(exchange, symbol)
        
        if is_candidate:
            final_candidates.append({
                'Symbol': symbol,
                'Volume_Ratio': f"{volume_ratio:.2f}x",
                'Price_Change_24h': f"{price_change:.2f}%"
            })
            
    # 4. نمایش نتایج نهایی
    if final_candidates:
        results_df = pd.DataFrame(final_candidates)
        results_df = results_df.sort_values(by='Volume_Ratio', ascending=False)
        
        print("\n=======================================================")
        print("🔥 واچ‌لیست فوری TraxCry: کاندیداهای پامپ حجمی")
        print("=======================================================")
        print(results_df.to_string(index=False))
        print("=======================================================")
        print(f"🎉 تعداد کل کاندیداها: {len(final_candidates)}")
        print("این ارزها واجد شرایط تحلیل تکنیکال ۱ دقیقه‌ای هستند.")
    else:
        print("\n😴 هیچ کاندیدای Volume Spike (حجم 3X) در فیلتر امروز یافت نشد.")

if __name__ == "__main__":
    run_traxcry_screener()
