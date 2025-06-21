import streamlit as st
import requests
import pandas as pd
import time

# ==== KONFIGURASI ====
BOT_TOKEN = "7844418185:AAGNywzrPEK2Z6vVEmy11d_8T2G0HDndQJ4"
CHAT_ID = "5991757052"
INDODAX_API = "https://indodax.com/api/summaries"

# Fungsi kirim pesan ke Telegram
def kirim_telegram(pesan):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": pesan}
    requests.post(url, data=data)

# Fungsi analisa sinyal sederhana
def analisa_sinyal(data):
    sinyal = []
    for koin, isi in data.items():
        try:
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
st.write("Versi FIX - Kirim sinyal ke Telegram berdasarkan penurunan harga")

if st.button("🔍 Scan Sekarang"):
    try:
        response = requests.get(INDODAX_API)
        json_data = response.json()

        if 'tickers' not in json_data:
            st.error("Gagal memuat data: 'tickers' tidak ditemukan")
        else:
            data = json_data['tickers']
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