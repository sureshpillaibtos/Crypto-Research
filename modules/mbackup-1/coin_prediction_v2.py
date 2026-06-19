# modules/coin_prediction.py
import streamlit as st
import requests
import pandas as pd
import yfinance as yf


def get_historical_prices(
    ticker,
    period="3mo"
):

    hist = yf.Ticker(
        ticker
    ).history(
        period=period
    )

    if hist.empty:
        raise Exception(
            f"No data found for {ticker}"
        )

    df = hist.reset_index()

    return df


def show_coin_prediction():

    st.title("🔮 Coin Prediction")
    COIN_MAPPING = {
        "bitcoin": "BTC-USD",
        "ethereum": "ETH-USD",
        "solana": "SOL-USD",
        "aave": "AAVE-USD",
        "chainlink": "LINK-USD"
    }

    #coin = st.text_input(
    #    "Coin",
    #    value="bitcoin"
    #).lower()
    coin = st.selectbox(
        "Select Coin",
        [
            "bitcoin",
            "ethereum",
            "solana",
            "aave",
            "chainlink"
        ]
    )

    ticker = COIN_MAPPING.get(
        coin,
        "BTC-USD"
    )
    

    if st.button("Analyze Coin", icon="🔥"):
        try:
            df = get_historical_prices(
                ticker
            )
            # Testing , enabble below code
            #st.success(
            #    f"Retrieved {len(df)} days of data"
            #)
            #st.dataframe(
            #    df.tail()
            #)

        except Exception as e:

            st.error(
                f"Error: {e}"
            )

        current_price = df["Close"].iloc[-1]
        #st.metric(
        #    "Current Price",
        #    f"${current_price:,.2f}"
        #)
        # Show 90-Day High and Low
        high_90 = df["High"].max()
        low_90 = df["Low"].min()

        #col1, col2 = st.columns(2)

        #with col1:
        #    st.metric(
        #        "90-Day High",
        #        f"${high_90:,.2f}"
        #    )

        #with col2:
        #    st.metric(
        #        "90-Day Low",
        #       f"${low_90:,.2f}"
         #   )
        
        # First Support & Resistance
        support = low_90
        resistance = high_90
        #col1, col2 = st.columns(2)

        #with col1:
        #    st.metric(
        #        "Support",
        #        f"${support:,.2f}"
        #    )

        #with col2:
        #    st.metric(
        #        "Resistance",
        #        f"${resistance:,.2f}"
        #    )
        
        # Trend Detection
        sma20 = (
            df["Close"]
            .rolling(20)
            .mean()
            .iloc[-1]
        )

        if current_price > sma20:
            trend = "Bullish"
        else:
            trend = "Bearish"
        st.subheader(
            f"Trend: {trend}"
        )
        
        if trend == "Bullish":
            recommendation = (
                "Buy on dips near support."
            )
        else:
            recommendation = (
                "Wait for confirmation."
            )

        st.info(recommendation)
        # Create a Dashboard Layout
        # simple layout
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Current Price",
                f"${current_price:,.2f}"
            )

        with col2:
            st.metric(
                "90-Day High",
                f"${high_90:,.2f}"
            )

        with col3:
            st.metric(
                "90-Day Low",
                f"${low_90:,.2f}"
            )
        # then another row
        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Support",
                f"${support:,.2f}"
            )

        with col2:
            st.metric(
                "Resistance",
                f"${resistance:,.2f}"
            )
        # Add a Price Chart: make the page more useful.
        chart_df = df[["Date", "Close"]]

        st.line_chart(
            chart_df.set_index("Date")
        )

        # Add RSI
        def calculate_rsi(
            prices,
            period=14
        ):
            delta = prices.diff()
            gain = (
                delta.where(delta > 0, 0)
                .rolling(period)
                .mean()
            )            

            loss = (
                -delta.where(delta < 0, 0)
                .rolling(period)
                .mean()
            )

            rs = gain / loss

            rsi = 100 - (
                100 / (1 + rs)
            )

            return rsi.iloc[-1]
        #rsi = calculate_rsi(
        #    df["Close"]
        #)

        #st.metric(
        #    "RSI",
        #    f"{rsi:.2f}"
        #)
        # interpretation
        #if rsi > 70:
        #    status = "Overbought"
        #elif rsi < 30:
        #    status = "Oversold"
        #else:
        #    status = "Neutral"

        #st.write(
        #    f"RSI Status: {status}"
        #)

        # Add RSI Interpretation
        rsi = calculate_rsi(df["Close"])

        if rsi >= 70:
            rsi_status = "Overbought 🔴"

        elif rsi <= 30:
            rsi_status = "Oversold 🟢"

        else:
            rsi_status = "Neutral 🟡"
        
        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "RSI",
                f"{rsi:.2f}"
            )

        with col2:
            st.metric(
                "RSI Status",
                rsi_status
            )
        # Add EMA20 and EMA50
        df["EMA20"] = (
            df["Close"]
            .ewm(span=20, adjust=False)
            .mean()
        )

        df["EMA50"] = (
            df["Close"]
            .ewm(span=50, adjust=False)
            .mean()
        )
        # latest values
        ema20 = df["EMA20"].iloc[-1]
        ema50 = df["EMA50"].iloc[-1]
        # Determine Trend Strength
        if current_price > ema20 > ema50:
            trend_strength = "Strong Bullish 🟢"
        elif current_price > ema20:
            trend_strength = "Bullish 🟢"
        elif current_price < ema20 < ema50:
            trend_strength = "Strong Bearish 🔴"
        else:
            trend_strength = "Neutral 🟡"
        #st.metric(
        #    "Trend Strength",
        #    trend_strength
        #)
        # Add Buy/Sell Recommendation Engine : users start finding the page useful.
        recommendation = "Hold"

        if rsi < 30:
            recommendation = "Potential Buy Zone"

        elif rsi > 70:
            recommendation = "Potential Profit Booking Zone"

        elif trend_strength.startswith("Strong Bullish"):
            recommendation = "Buy on Dips"

        elif trend_strength.startswith("Strong Bearish"):
            recommendation = "Wait for Reversal"
        st.info(
            f"Recommendation: {recommendation}"
        )

        # Confidence Score
        score = 50

        # Trend strength
        if trend_strength == "Strong Bullish 🟢":
            score += 20

        elif trend_strength == "Bullish 🟢":
            score += 10

        elif trend_strength == "Strong Bearish 🔴":
            score -= 20

        # RSI
        if 40 <= rsi <= 65:
            score += 10

        elif rsi > 80:
            score -= 10

        # EMA alignment
        if current_price > ema20:
            score += 5

        if ema20 > ema50:
            score += 5

        score = max(0, min(score, 100)) 
        #st.metric(
        #    "Confidence Score",
        #    f"{score}/100"
        #)
        # Risk Level
        if rsi > 75:
            risk_level = "High 🔴"

        elif rsi > 60:
            risk_level = "Medium 🟡"

        else:
            risk_level = "Low 🟢"        
        #st.metric(
        #    "Risk Level",
        #    risk_level
        #)
        # 90-Day Range Position
        range_position = (
            (current_price - low_90)
            /
            (high_90 - low_90)
        ) * 100
        # Protect against division by zero:
        price_range = high_90 - low_90

        if price_range > 0:
            range_position = (
                (current_price - low_90)
                / price_range
            ) * 100
        else:
            range_position = 50
        #st.metric(
        #    "90-Day Range Position",
        #    f"{range_position:.1f}%"
        #)
        # Suggested Layout
        # Row 1
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Current Price",
                f"${current_price:,.2f}"
            )

        with col2:
            st.metric(
                "Confidence Score",
                f"{score}/100"
            )

        with col3:
            st.metric(
                "Risk Level",
                risk_level
            )
        # Row 2
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "RSI",
                f"{rsi:.2f}"
            )

        with col2:
            st.metric(
                "Trend",
                trend_strength
            )

        with col3:
            st.metric(
                "90-Day Position",
                f"{range_position:.1f}%"
            )
        
        # Better Recommendation Logic
        #if score >= 80:
        #    recommendation = "Strong Buy Zone 🟢"

        #elif score >= 65:
        #    recommendation = "Buy on Dips 🟢"

        #elif score >= 50:
        #    recommendation = "Hold 🟡"

        #elif score >= 35:
        #    recommendation = "Weak Trend 🟠"

        #else:
        #    recommendation = "Avoid / Wait 🔴"
        
        if score >= 80 and range_position < 60:
            recommendation = "Strong Buy Zone 🟢"
        elif score >= 65 and range_position < 80:
            recommendation = "Buy on Dips 🟢"
        elif range_position > 90:
            recommendation = "Near Resistance ⚠️"
        elif score < 40:
            recommendation = "Avoid / Wait 🔴"
        else:
            recommendation = "Hold 🟡"

        st.success(
            f"Recommendation: {recommendation}"
        )
        
        # Add Buy Zone & Sell Zone
        buy_zone_low = support
        buy_zone_high = support * 1.05

        sell_zone_low = resistance * 0.95
        sell_zone_high = resistance
        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Buy Zone",
                f"${buy_zone_low:,.2f} - ${buy_zone_high:,.2f}"
            )

        with col2:
            st.metric(
                 " Sell Zone",
                f"${sell_zone_low:,.2f} - ${sell_zone_high:,.2f}"
            )
        
        #  Add Distance from Support/Resistance
        distance_support = (
            (current_price - support)
            / support
        ) * 100

        distance_resistance = (
            (resistance - current_price)
            / resistance
        ) * 100
        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Distance from Support",
                f"{distance_support:.2f}%"
            )

        with col2:
            st.metric(
                "Distance to Resistance",
                f"{distance_resistance:.2f}%"
            )
        # Upgrade Recommendation Logic
        # Replace the existing recommendation block with:
        #if score >= 80 and range_position < 60:
        #    recommendation = "Strong Buy Zone 🟢"
        #elif score >= 65 and range_position < 80:
        #    recommendation = "Buy on Dips 🟢"
        #elif range_position > 90:
        #    recommendation = "Near Resistance ⚠️"
        #elif score < 40:
        #    recommendation = "Avoid / Wait 🔴"
        #else:
        #   recommendation = "Hold 🟡"

    




    #if st.button("Analyze Coin"):

        # Get CoinGecko data

        # Calculate:
        # Support Levels
        # Resistance Levels
        # RSI
        # Trend

        #pass