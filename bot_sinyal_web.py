import streamlit as st
import requests
import pandas as pd
from ta.trend import EMAIndicator
from ta.momentum import RSIIndicator
import time

# === Konfigurasi Bot Telegram ===
BOT_TOKEN = "7844418185:AAGNywzrPEK2Z6vVEmy11d_8T2G0HDndQJ4"
CHAT_ID = "5991757052"

def kirim_telegram(pesan):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": pesan}
    requests.post(url, data=data)

def fetch_price(symbol):
    try:
        url = f"https://indodax.com/api/{symbol}_idr/trades"
        res = requests.get(url).json()
        df = pd.DataFrame(res)
        df['price'] = df['price'].astype(float)
        df['date'] = pd.to_datetime(df['date'], unit='s')
        df = df.sort_values('date').reset_index(drop=True)
        return df
    except:
        return None

def analisa_strong_buy(symbol):
    df = fetch_price(symbol)
    if df is None or len(df) < 20:
        return None

    df['ema5'] = EMAIndicator(close=df['price'], window=5).ema_indicator()
    df['ema20'] = EMAIndicator(close=df['price'], window=20).ema_indicator()
    df['rsi'] = RSIIndicator(close=df['price'], window=14).rsi()
    df = df.dropna()

    if df.empty:
        return None

    latest = df.iloc[-1]
    score = 0
    if latest['ema5'] > latest['ema20']:
        score += 1
    if latest['price'] > latest['ema5']:
        score += 1
    if 45 <= latest['rsi'] <= 65:
        score += 1

    return {
        "symbol": symbol.upper(),
        "price": latest['price'],
        "ema5": latest['ema5'],
        "ema20": latest['ema20'],
        "rsi": latest['rsi'],
        "score": score
    }

def scan_koin():
    try:
        summary = requests.get("https://indodax.com/api/summaries").json()
        all_symbols = [k.replace("idr", "") for k in summary['tickers'] if k.endswith("idr")]
    except:
        return []

    hasil = []
    for sym in all_symbols:
        h = analisa_strong_buy(sym)
        if h and h['score'] >= 2:
            hasil.append(h)
        time.sleep(0.3)

    return sorted(hasil, key=lambda x: x['score'], reverse=True)[:10]

# === STREAMLIT UI ===
st.title("🔥 Bot Sinyal 10 Strong Buy - Indodax")
st.write("Analisa gabungan EMA, RSI, dan Harga Terkini")

if st.button("🔍 Scan Sekarang"):
    hasil = scan_koin()
    if hasil:
        for h in hasil:
            info = f"{h['symbol']} | Harga: {h['price']} | EMA5: {h['ema5']:.2f} | EMA20: {h['ema20']:.2f} | RSI: {h['rsi']:.2f}"
            st.success(info)
            kirim_telegram(f"Strong Buy 🔔 {h['symbol']} | Harga: {h['price']} | RSI: {h['rsi']:.1f}")
    else:
        st.warning("Tidak ditemukan sinyal strong buy saat ini.")

st.caption("Versi oleh @zoza | Top 10 Koin Potensi Naik")