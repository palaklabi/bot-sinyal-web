import streamlit as st
import requests
import pandas as pd
import time

# ==== KONFIGURASI ====
BOT_TOKEN = "7844418185:AAGNywzrPEK2Z6vVEmy11d_8T2G0HDndQJ4"
CHAT_ID = "5991757052"
SCAN_INTERVAL = 60 * 60  # setiap 1 jam
INDODAX_API = "https://indodax.com/api/summaries"

# Fungsi kirim pesan ke Telegram
def kirim_telegram(pesan):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": pesan}
    requests.post(url, data=data)

# Fungsi analisa sederhana (misal deteksi penurunan besar = sinyal buy)
def analisa_sinyal(data):
    sinyal = []
    for koin, isi in data.items():
        try:
            low = float(isi['low'])
            high = float(isi['high'])
            last = float(isi['last'])
            persentase_turun = (high - last) / high * 100
            if persentase_turun >= 10:
                sinyal.append((koin.upper(), f"⬇ TURUN {persentase_turun:.1f}%"))
        except:
            continue
    return sinyal

# UI Streamlit
st.title("📊 Bot Sinyal Koin Indodax")
st.write("Versi Web - Otomatis kirim sinyal ke Telegram")

if st.button("🔍 Scan Sekarang"):
    try:
        response = requests.get(INDODAX_API)
        data = response.json()['tickers']
        sinyal = analisa_sinyal(data)

        if sinyal:
            for koin, pesan in sinyal:
                kirim_telegram(f"Sinyal Buy: {koin} | {pesan}")
            st.success(f"Ditemukan {len(sinyal)} sinyal. Dikirim ke Telegram!")
        else:
            st.info("Tidak ada sinyal kuat saat ini.")

    except Exception as e:
        st.error(f"Gagal memuat data: {e}")

st.caption("Bot Sinyal Pribadi by @zoza")