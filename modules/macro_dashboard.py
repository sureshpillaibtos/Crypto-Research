import yfinance as yf
import pandas as pd
import streamlit as st
import logging

# Main Data Function
# moved Helper function, now in utils.py
from utils.market_data import (
    get_ticker_value,
    get_value_with_fallback
)

def fetch_macro_data():

    metrics = {
        "BTC": get_value_with_fallback(
            "BTC-USD"
        ),

        "US10Y": get_value_with_fallback(
            "^TNX"
        ),

        "DXY": get_value_with_fallback(
            "DX-Y.NYB",
            "UUP"
        ),

        "Gold": get_value_with_fallback(
            "GC=F"
        ),

        "Oil": get_value_with_fallback(
            "BZ=F"
        )
    }

    results = []

    for metric, value in metrics.items():

        results.append({
            "Metric": metric,
            "Value": value
        })

    #return pd.DataFrame(results)
    df = pd.DataFrame(results)
    df["Value"] = df["Value"].fillna(
        "Unavailable"
    )
    return df


# Macro Score Engine
def calculate_macro_score(df):

    score = 0

    try:

        us10y = float(
            df[df["Metric"] == "US10Y"]["Value"].iloc[0]
        )

        if us10y < 4.4:
            score += 1

    except Exception as e:

        logging.warning(
            f"Macro score calculation error: {e}"
        )

    try:

        dxy = float(
            df[df["Metric"] == "DXY"]["Value"].iloc[0]
        )

        if dxy < 98:
            score += 1

    except Exception as e:

        logging.warning(
            f"Macro score calculation error: {e}"
        )

    try:

        oil = float(
            df[df["Metric"] == "Oil"]["Value"].iloc[0]
        )

        if oil < 75:
            score += 1

    except Exception as e:

        logging.warning(
            f"Macro score calculation error: {e}"
        )

    return score

# Market Condition
def get_market_condition(score):

    if score == 3:
        return "🟢 Strong Bullish"

    if score == 2:
        return "🟢 Bullish"

    if score == 1:
        return "🟡 Neutral"

    return "🔴 Bearish"

# Streamlit Renderer
#This lets users know why values don't change on every page refresh.
st.caption(
    "Macro data refreshes every 5 minutes."
)
def render_macro_dashboard():

    st.subheader("🌍 Macro Dashboard")

    df = fetch_macro_data()

    if df.empty:
        st.error("Unable to fetch macro data.")
        return

    score = calculate_macro_score(df)

    condition = get_market_condition(score)

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Macro Score",
            f"{score}/3"
        )

    with col2:
        st.metric(
            "Market Condition",
            condition
        )

    st.dataframe(
        df,
        width="stretch"
    )

