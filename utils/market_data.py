# utils/market_data.py

import yfinance as yf
import logging
import streamlit as st


@st.cache_data(ttl=300)
def get_ticker_value(ticker):

    try:

        data = yf.Ticker(ticker)

        hist = data.history(period="2d")

        if hist.empty:
            return None

        return round(
            hist["Close"].iloc[-1],
            2
        )

    except Exception as e:

        logging.warning(
            f"Unable to fetch {ticker}: {e}"
        )

        return None


def get_value_with_fallback(
    primary_ticker,
    fallback_ticker=None
):

    value = get_ticker_value(
        primary_ticker
    )

    if value is None and fallback_ticker:

        logging.warning(
            f"{primary_ticker} failed. "
            f"Trying {fallback_ticker}"
        )

        value = get_ticker_value(
            fallback_ticker
        )

    return value

@st.cache_data(ttl=300)
def get_history(
    ticker,
    period="1mo"
):

    try:

        data = yf.Ticker(ticker)

        return data.history(
            period=period
        )

    except Exception as e:

        logging.warning(
            f"History fetch failed "
            f"for {ticker}: {e}"
        )

        return None