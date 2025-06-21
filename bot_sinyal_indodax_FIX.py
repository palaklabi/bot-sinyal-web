
import requests, time
import pandas as pd
from ta.trend import EMAIndicator

# ============ KONFIGURASI TELEGRAM ============
BOT_TOKEN = '123456789:ABCdEfGhIjKlMnOpQrStUvWxYz'
CHAT_ID = '987654321'

def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": message}
        response = requests.post(url, data=data)
        if response.status_code != 200:
            print("❗ Gagal kirim Telegram. Status:", response.status_code)
            print("Respon:", response.text)
    except Exception as e:
        print("❗ ERROR kirim telegram:", str(e))

# ============ FUNGSI UTAMA ============
def get_tickers():
    r = requests.get('https://indodax.com/api/pairs')
    return [x['ticker_id'] for x in r.json()]

def get_ohlc(ticker):
    url = f'https://indodax.com/api/chart/{ticker}/1h'
    data = requests.get(url).json()
    df = pd.DataFrame(data['tick'])
    df.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    df['close'] = df['close'].astype(float)
    return df

def check_strong_buy(ticker):
    df = get_ohlc(ticker)
    if len(df) < 20: return False

    ema5 = EMAIndicator(df['close'], 5).ema_indicator()
    ema20 = EMAIndicator(df['close'], 20).ema_indicator()

    price_now = df['close'].iloc[-1]
    price_before = df['close'].iloc[-4]
    gain = (price_now - price_before) / price_before * 100

    if ema5.iloc[-1] > ema20.iloc[-1] and gain > 3:
        return True
    return False

def scan_and_alert():
    strongs = []
    tickers = get_tickers()
    for t in tickers:
        try:
            if check_strong_buy(t):
                strongs.append(t.upper())
        except Exception as e:
            print("Error memproses {}: {}".format(t, e))
    if strongs:
        send_telegram("📈 Sinyal Strong Buy:\n" + "\n".join(strongs))
    else:
        send_telegram("❌ Tidak ada sinyal strong buy saat ini.")

# ============ LOOP SCAN SETIAP JAM ============
while True:
    try:
        scan_and_alert()
    except Exception as e:
        print("❗ ERROR saat scan_and_alert:", str(e))
    time.sleep(3600)  # Scan ulang setiap jam
