# modules/etf_tracker.py

import pandas as pd
import streamlit as st
import yfinance as yf
from utils.market_data import get_history

ETF_LIST = {
    "IBIT": "BlackRock",
    "FBTC": "Fidelity",
    "ARKB": "Ark",
    "BITB": "Bitwise",
    "HODL": "VanEck"
}
# Fetch ETF Data
def fetch_etf_data():

    results = []

    for ticker, issuer in ETF_LIST.items():

        try:

            hist = get_history(
                ticker,
                period="5d"
            )
            #print(f"{ticker} rows: {len(hist)}")
            #print(hist.tail())

            if hist is None or hist.empty:
                continue

            close_prices = hist["Close"].dropna()

            hist = hist.dropna(
                subset=["Close"]
            )

            if len(hist) < 2:
                continue

            

            #if len(close_prices) < 2:
            #    continue

            latest = hist["Close"].iloc[-1]

            previous = hist["Close"].iloc[-2]

            pct_change = round(
                ((latest - previous)
                / previous) * 100,
                2
            )

            volume = int(
                hist["Volume"].iloc[-1]
            )

            results.append(
                {
                    "ETF": ticker,
                    "Issuer": issuer,
                    "Price": round(latest, 2),
                    "Change %": pct_change,
                    "Volume": volume
                }
            )

        except Exception:
            pass

    return pd.DataFrame(results)

# Liquidity Signal
def calculate_etf_signal(df):

    if df.empty:
        return "Unknown"

    avg_change = df[
        "Change %"
    ].mean()

    if avg_change > 1:
        return "🟢 Bullish"

    elif avg_change < -1:
        return "🔴 Bearish"

    else:
        return "🟡 Neutral"

# Render Function
def render_etf_tracker():

    st.subheader(
        "📈 ETF Tracker"
    )

    df = fetch_etf_data()

    if df.empty:

        st.warning(
            "ETF data unavailable."
        )

        return

    signal = calculate_etf_signal(df)

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Tracked ETFs",
            len(df)
        )

    with col2:

        st.metric(
            "Liquidity Signal",
            signal
        )

    st.dataframe(
        df,
        width="stretch"
    )
    