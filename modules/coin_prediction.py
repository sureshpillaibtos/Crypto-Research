# modules/coin_prediction.py
import streamlit as st
import requests
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

# Version 1.2 :RSI Chart # Create RSI Series Function
def calculate_rsi_series(
    prices,
    period=14
):

    delta = prices.diff()

    gain = delta.where(
        delta > 0,
        0
    )

    loss = -delta.where(
        delta < 0,
        0
    )

    avg_gain = gain.rolling(
        window=period
    ).mean()

    avg_loss = loss.rolling(
        window=period
    ).mean()

    rs = avg_gain / avg_loss

    rsi = 100 - (
        100 / (1 + rs)
    )

    return rsi

def get_historical_prices(
    ticker,
    period="1y"
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


# Create RSI Chart Function
def create_rsi_chart(df_90):
    st.subheader(
        "RSI Analysis",divider="blue"
    )

    rsi_fig = go.Figure()
    # Add RSI Trace
    rsi_fig.add_trace(
        go.Scatter(
            x=df_90.index,
            y=df_90["RSI"],
            name="RSI"
        )
    )
    # Add Overbought Line
    rsi_fig.add_hline(
        y=70,
        annotation_text="Overbought (70)"
    )
    # Add Oversold Line
    rsi_fig.add_hline(
        y=30,
        annotation_text="Oversold (30)"
    )
    # Add Midline (Optional but Useful)
    rsi_fig.add_hline(
        y=50,
        annotation_text="Neutral (50)"
    )
    rsi_fig.update_layout(
        title="RSI Analysis",
        xaxis_title="Date",
        yaxis_title="RSI",
        hovermode="x unified",
        height=400
    )
    #st.plotly_chart(
    #    rsi_fig,
    #    config={
    #        "displayModeBar": False,
    #        "responsive": True
    #    }
    #)
    display_chart(rsi_fig)
# Create MACD Chart Function: Visualization Enhancement: add Buy Zone & Sell Zone shading.
def create_macd_chart(df_90):
    st.subheader("MACD Analysis",divider="blue")

    macd_fig = go.Figure()
    macd_fig.add_trace(
        go.Scatter(
            x=df_90.index,
            y=df_90["MACD"],
            name="MACD"
        )
    )
    macd_fig.add_trace(
        go.Scatter(
            x=df_90.index,
            y=df_90["Signal"],
            name="Signal"
        )
    )
    #st.plotly_chart(
    #    macd_fig,
    #    config={
    #        "displayModeBar": False,
    #        "responsive": True
    #    }
    #)
    display_chart(macd_fig)

# Create Volume Chart Function
def create_volume_chart(df_90):
    st.subheader("📊 Trading Volume")
    volume_fig = go.Figure()
    # Add Volume
    volume_fig.add_trace(
        go.Bar(
            x=df_90["Date"],
            y=df_90["Volume"],
            name="Volume"
        )
    )
    volume_fig.update_layout(
        title="Trading Volume",
        xaxis_title="Date",
        yaxis_title="Volume",
        height=300
    )
    #st.plotly_chart(
    #    volume_fig,
    #    config={
    #        "displayModeBar": False,
    #        "responsive": True
    #    }
    #)
    display_chart(volume_fig)

# Version 1.1 : Analysis Summary Card - Professional Dashboard Style - Professional Dashboard Style
def show_analysis_summary(
    score,
    risk_level,
    trend_strength,
    macd_status,
    recommendation
):

    st.subheader("📋 Analysis Summary",divider="blue")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Confidence",
            f"{score}/100"
        )

    with col2:
        st.metric(
            "Risk",
            risk_level
        )

    with col3:
        st.metric(
            "Trend",
            trend_strength
        )

    with col4:
        st.metric(
            "MACD",
            macd_status
        ) 
    if "Strong Buy" in recommendation:
        st.success(
            f"Recommendation: {recommendation}"
    )

    elif "Buy" in recommendation:
        st.success(
            f"Recommendation: {recommendation}"
    )

    elif "Hold" in recommendation:
        st.warning(
            f"Recommendation: {recommendation}"
    )

    else:
        st.error(
            f"Recommendation: {recommendation}"
    )

#  SHOW  ZONE ALERT
def show_zone_alert(
    current_price,
    buy_zone_low,
    buy_zone_high,
    sell_zone_low,
    sell_zone_high
):
    if buy_zone_low <= current_price <= buy_zone_high:

        st.success(
            "🟢 Current price is inside the Buy Zone"
        )

    elif sell_zone_low <= current_price <= sell_zone_high:

        st.warning(
            "🔴 Current price is inside the Sell Zone"
        )

    # Very useful when BTC is running away from support
    elif current_price > buy_zone_high:

        distance = (
            (current_price - buy_zone_high)
            / current_price
        ) * 100

        st.info(
            f"ℹ️ Price is {distance:.2f}% above the Buy Zone"
        )

    else:

        distance = (
            (buy_zone_low - current_price)
            / buy_zone_low
        ) * 100

        st.warning(
            f"⚠️ Price is {distance:.2f}% below the Buy Zone"
        )

# CANDLESTICK CHART
def create_candlestick_chart(
    df_90,
    support,
    resistance,
    current_price,
    buy_zone_low,
    buy_zone_high,
    sell_zone_low,
    sell_zone_high
):
    st.subheader("🕯️ Detailed Candlestick Analysis", divider="blue")        
    candle_fig = go.Figure()
    candle_fig.add_trace(
        go.Candlestick(
            x=df_90["Date"],
            open=df_90["Open"],
            high=df_90["High"],
            low=df_90["Low"],
            close=df_90["Close"],
            name="Price"
        )
    )
    # Add EMA 20
    candle_fig.add_trace(
        go.Scatter(
            x=df_90["Date"],
            y=df_90["EMA20"],
            name="EMA20"
        )
    )
    # Add ENA 50
    candle_fig.add_trace(
        go.Scatter(
            x=df_90["Date"],
            y=df_90["EMA50"],
            name="EMA50"
        )
    )
    # Add EMA 200
    candle_fig.add_trace(
        go.Scatter(
            x=df_90["Date"],
            y=df_90["EMA200"],
            name="EMA200"
        )
    )
    candle_fig.add_hrect(
        y0=buy_zone_low,
        y1=buy_zone_high,
        annotation_text="Buy Zone",
        opacity=0.25
    )

    candle_fig.add_hrect(
        y0=sell_zone_low,
        y1=sell_zone_high,
        annotation_text="Sell Zone",
        opacity=0.25
    )
    # This removes Plotly's default mini-chart slider under candlestick charts, making the dashboard cleaner.
    candle_fig.update_xaxes(
        rangeslider_visible=False
    )
    # Add Support & Resistance
    candle_fig.add_hline(
        y=support,
        annotation_text="Support"
    )

    candle_fig.add_hline(
        y=resistance,
        annotation_text="Resistance"
    )

    candle_fig.add_hline(
        y=current_price,
        annotation_text="Current Price"
    )
    candle_fig.update_layout(
        title="Candlestick Chart",
        xaxis_title="Date",
        yaxis_title="Price",
        hovermode="x unified",
        height=700
    )
    #st.plotly_chart(
    #    candle_fig,
    #    config={
    #        "displayModeBar": False,
    #        "responsive": True
    #    }
    #)
    display_chart(candle_fig)

# Price Analysis
#def create_price_chart(
#    df_90,
#    support,
#    resistance,
#    current_price,
#    buy_zone_low,
#    buy_zone_high,
#    sell_zone_low,
#    sell_zone_high
#):
def display_chart(fig):

    st.plotly_chart(
        fig,
        config={
            "displayModeBar": False,
            "responsive": True
        }
    )


def show_coin_prediction():

    st.title("🔮 Coin Prediction")
    COIN_MAPPING = {
        "bitcoin": "BTC-USD",
        "ethereum": "ETH-USD",
        "solana": "SOL-USD",
        "aave": "AAVE-USD",
        "bnb": "BNB-USD",
        "xrp": "XRP-USD",
        "Bitcoin Cash": "BCH-USD",
        "avalanche": "AVAX-USD",
        "polkadot": "DOT-USD",
        "chainlink": "LINK-USD"
    }

    coin = st.selectbox(
        "Select Coin",
        [
            "bitcoin",
            "ethereum",
            "solana",
            "aave",
            "bnb",
            "xrp",
            "Bitcoin Cash",
            "avalanche",
            "polkadot",
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

        except Exception as e:

            st.error(
                f"Error: {e}"
            )

        current_price = df["Close"].iloc[-1]

        df["Daily_Return"] = (
            df["Close"]
            .pct_change()
        )

        volatility = (
            df["Daily_Return"]
            .tail(30)
            .std()
        ) * 100

        if volatility < 2:
            volatility_level = "Low 🟢"
        elif volatility < 4:
            volatility_level = "Medium 🟡"
        else:
            volatility_level = "High 🔴"

        # Last 90 days for support/resistance
        df_90 = df.tail(90)

        # Show 90-Day High and Low, replace this with code, after 1y period chsnge
        high_90 = df_90["High"].max()
        low_90 = df_90["Low"].min()
        
        # First Support & Resistance
        support = low_90
        resistance = high_90
        
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

        # Add RSI Interpretation
        rsi = calculate_rsi(df["Close"])

        if rsi >= 70:
            rsi_status = "Overbought 🔴"

        elif rsi <= 30:
            rsi_status = "Oversold 🟢"

        else:
            rsi_status = "Neutral 🟡"
        

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

        df["EMA200"] = (
            df["Close"]
            .ewm(span=200, adjust=False)
            .mean()
        )

        # latest values
        ema20 = df["EMA20"].iloc[-1]
        ema50 = df["EMA50"].iloc[-1]
        ema200 = df["EMA200"].iloc[-1]

        # Determine Trend Strength
        if current_price > ema20 > ema50:
            trend_strength = "Strong Bullish 🟢"
        elif current_price > ema20:
            trend_strength = "Bullish 🟢"
        elif current_price < ema20 < ema50:
            trend_strength = "Strong Bearish 🔴"
        else:
            trend_strength = "Neutral 🟡"
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
        st.divider()
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

        # Risk Level
        if (
            rsi > 75
            or volatility > 5
        ):

            risk_level = "High 🔴"

        elif (
            rsi > 60
            or volatility > 3
        ):
            risk_level = "Medium 🟡"

        else:
            risk_level = "Low 🟢"        

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

        # Suggested Layout
        # Row 1
        col1, col2, col3, col4 = st.columns(4)

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
        with col4:
            st.metric(
                "RSI Status",
                rsi_status
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
        st.divider()
        # Add EMA200
        df["EMA200"] = (
            df["Close"]
            .ewm(
                span=200,
                adjust=False
            )
            .mean()
        )

        ema200 = df["EMA200"].iloc[-1]

        st.subheader(
            "Moving Averages",divider="blue"
        )
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "EMA20",
                f"${ema20:,.2f}"
            )

        with col2:
            st.metric(
                "EMA50",
                f"${ema50:,.2f}"
        )

        with col3:
            st.metric(
                "EMA200",
                f"${ema200:,.2f}"
        )
        # Upgrade Trend Strength
        # Replace with:
        if current_price > ema20 > ema50 > ema200:
            trend_strength = (
                "Very Strong Bullish 🚀"
        )
        elif current_price > ema50 > ema200:
            trend_strength = (
                "Bullish 🟢"
        )
        elif current_price < ema20 < ema50 < ema200:
            trend_strength = (
                "Very Strong Bearish 🔴"
            )
        elif current_price < ema50 < ema200:
            trend_strength = (
                "Bearish 🔴"
            )
        else:
            trend_strength = (
                "Neutral 🟡"
            )

        # Upgrade Confidence Score : Add EMA200 contribution:
        if current_price > ema200:
            score += 10
        if current_price > ema20 > ema50 > ema200:
            score += 10
        
        score = max(
            0,
            min(score, 100)
        )
        # Display Market Structure
        if current_price > ema200:
            market_structure = (
                "Above EMA200 🟢"
            )
        else:
            market_structure = (
                "Below EMA200 🔴"
            )


        # RSI tells you:    Overbought / Oversold, EMA tells you:    Trend Direction, MACD tells you:    Trend Momentum
        # Calculate MACD : Add after EMA calculations        

        ema12 = (
            df["Close"]
            .ewm(span=12, adjust=False)
            .mean()
        )
        ema26 = (
            df["Close"]
            .ewm(span=26, adjust=False)
            .mean()
        )
        df["MACD"] = ema12 - ema26
        df["Signal"] = (
            df["MACD"]
            .ewm(span=9, adjust=False)
            .mean()
        )
        df["Histogram"] = (
            df["MACD"]
            - df["Signal"]
        )
        # Get Latest Values
        macd = df["MACD"].iloc[-1]
        signal = df["Signal"].iloc[-1]
        histogram = df["Histogram"].iloc[-1]

        # # MACD Crossover Detection, not Bollinger Bands
        current_macd = df["MACD"].iloc[-1]
        previous_macd = df["MACD"].iloc[-2]

        current_signal = df["Signal"].iloc[-1]
        previous_signal = df["Signal"].iloc[-2]

        # Detect Crossovers
        if (
            previous_macd <= previous_signal
            and
            current_macd > current_signal
        ):

            crossover = (
                "Fresh Bullish Crossover 🚀"
            )

        elif (
            previous_macd >= previous_signal
            and
            current_macd < current_signal
        ):

            crossover = (
                "Fresh Bearish Crossover 🔻"
            )

        else:

            crossover = (
                "No Recent Crossover"
            )

        #st.metric(
        #    "MACD Crossover",
        #    crossover
        #)

        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                "Market Structure",
                f"{market_structure}"
            )

        with col2:
            st.metric(
                "MACD Crossover",
                f"{crossover}"
            )



        # Determine MACD Status
        if macd > signal:
            macd_status = (
                "Bullish 🟢"
            )
        else:
            macd_status = (
                "Bearish 🔴"
            )
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "MACD",
                f"{macd:.4f}"
            )

        with col2:
            st.metric(
                "Signal",
                f"{signal:.4f}"
            )

        with col3:
            st.metric(
                "MACD Status",
                macd_status
            )
        # Upgrade Confidence Score
        if macd > signal:
            score += 10
        else:
            score -= 10
        score = max(
            0,
            min(score, 100)
        )

        
        st.metric(
            "30-Day Volatility",
            f"{volatility:.2f}% ({volatility_level})"
        )

        # Price + EMA Overlay Chart
        # Create Chart Data
        chart_df = df[
            [
                "Close",
                "EMA20",
                "EMA50",
                "EMA200"
            ]
        ]
        st.subheader(
            "Price & Moving Averages", divider="blue"
        )
        
        # Show Last 90 Days Only
        chart_df = df[
            [
                "Close",
                "EMA20",
                "EMA50",
                "EMA200"
            ]
        ].tail(90)
        st.line_chart(chart_df)

        df_90 = df.tail(90)
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=df_90.index,
                y=df_90["Close"],
                name="Price"
            )
        )
        fig.add_trace(
            go.Scatter(
                x=df_90.index,
                y=df_90["EMA20"],
                name="EMA20"
            )
        )
        fig.add_trace(
            go.Scatter(
                x=df_90.index,
                y=df_90["EMA50"],
                name="EMA50"
            )
        )
        fig.add_trace(
            go.Scatter(
                x=df_90.index,
                y=df_90["EMA200"],
                name="EMA200"
            )
        )

        # Add Support & Resistance
        fig.add_hline(
            y=support,
            annotation_text="Support"
        )
        fig.add_hline(
            y=resistance,
            annotation_text="Resistance"
        )
        # Add  buy zone
        fig.add_hrect(
            y0=buy_zone_low,
            y1=buy_zone_high,
            annotation_text="Buy Zone",
            opacity=0.15
        )
        # Add Sell zone
        fig.add_hrect(
            y0=sell_zone_low,
            y1=sell_zone_high,
            annotation_text="Sell Zone",
            opacity=0.15
        )


        fig.add_hline(
            y=current_price,
            annotation_text="Current Price"
        )
        st.plotly_chart(
            fig,
            width='stretch'
        )
        fig.update_layout(
            title="Price & Moving Averages",
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            hovermode="x unified",
            height=600
        )
        #st.plotly_chart(
        #    fig,
        #    config={
        #        "displayModeBar": False,
        #        "responsive": True
        #    }
        #)
        display_chart(fig)
        
        #  DELETEMACD
        create_macd_chart(df_90)

        st.divider()
        # Version 1.1 : Analysis Summary Card - Professional Dashboard Style
        # Professional Dashboard Style DELETEANALYSIS
        show_analysis_summary(
            score,
            risk_level,
            trend_strength,
            macd_status,
            recommendation
        )

        
        
        # Add RSI Column        
        df["RSI"] = calculate_rsi_series(
            df["Close"]
        )
        df_90 = df.tail(90)

        # Create RSI Figure  DELETEFROM
        create_rsi_chart(df_90)
         #DELETEEND            
        # Version 2.1 : Add Buy Zone Shading
        fig.add_hline(
            y=support,
            annotation_text="Support"
        )        

        fig.add_hrect(
            y0=buy_zone_low,
            y1=buy_zone_high,
            annotation_text="Buy Zone",
            opacity=0.25
        )
        # Add Sell Zone Shading
        fig.add_hline(
            y=resistance,
            annotation_text="Resistance"
        )
        fig.add_hrect(
            y0=sell_zone_low,
            y1=sell_zone_high,
            annotation_text="Sell Zone",
            opacity=0.25
        )
        fig.update_layout(
            #title="Price, EMA & Trading Zones",
            title="🎯 Trading Zones Overview",
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            hovermode="x unified",
            height=600
        )
        st.plotly_chart(
            fig,
            config={
                "displayModeBar": False,
                "responsive": True
            }
        )
        # DELETEALERT
        show_zone_alert(
            current_price,
            buy_zone_low,
            buy_zone_high,
            sell_zone_low,
            sell_zone_high
        )

        st.divider()
        # Create Candlestick Figure V 1.1 DELETECANDLESTICK
        create_candlestick_chart(
            df_90,
            support,
            resistance,
            current_price,
            buy_zone_low,
            buy_zone_high,
            sell_zone_low,
            sell_zone_high
        )
        # Add Volume Bars
        create_volume_chart(df_90)

