import streamlit as st
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import requests

st.set_page_config(page_title="📊 Forex Dashboard", layout="wide")
st.title("📊 Forex Signal Dashboard (15 นาที)")

symbols = {
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X",
    "USD/JPY": "JPY=X",
    "XAU/USD": "XAUUSD=X",
    "USD/CHF": "CHF=X"
}

def send_line_notify(message, token):
    url = 'https://notify-api.line.me/api/notify'
    headers = {"Authorization": f"Bearer {token}"}
    data = {'message': message}
    return requests.post(url, headers=headers, data=data).status_code

def fetch_data(symbol, interval='15m', period='2d'):
    df = yf.download(tickers=symbol, interval=interval, period=period)
    df.dropna(inplace=True)
    return df

def analyze(df):
    df['MA20'] = df['Close'].rolling(20).mean()
    df['MA50'] = df['Close'].rolling(50).mean()
    df['RSI'] = ta.rsi(df['Close'], length=14)
    macd = ta.macd(df['Close'])
    df = pd.concat([df, macd], axis=1)
    return df

def generate_signals(df):
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    signals = []

    if prev['MA20'] < prev['MA50'] and latest['MA20'] > latest['MA50']:
        signals.append('🔼 MA Bullish')
    elif prev['MA20'] > prev['MA50'] and latest['MA20'] < latest['MA50']:
        signals.append('🔽 MA Bearish')

    if latest['RSI'] > 70:
        signals.append('📈 RSI Overbought')
    elif latest['RSI'] < 30:
        signals.append('📉 RSI Oversold')

    if prev['MACD_12_26_9'] < prev['MACDs_12_26_9'] and latest['MACD_12_26_9'] > latest['MACDs_12_26_9']:
        signals.append('📊 MACD Bullish')
    elif prev['MACD_12_26_9'] > prev['MACDs_12_26_9'] and latest['MACD_12_26_9'] < latest['MACDs_12_26_9']:
        signals.append('📉 MACD Bearish')

    return signals

for name, ticker in symbols.items():
    st.subheader(f"📌 {name}")
    df = fetch_data(ticker)
    df = analyze(df)
    signals = generate_signals(df)

    col1, col2 = st.columns([2, 1])

    with col1:
        st.line_chart(df[['Close', 'MA20', 'MA50']].dropna())

    with col2:
        st.metric("ราคาล่าสุด", f"{df['Close'].iloc[-1]:.4f}")
        for sig in signals:
            st.success(sig)

    st.divider()
