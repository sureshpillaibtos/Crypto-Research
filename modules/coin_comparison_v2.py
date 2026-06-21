import streamlit as st
import pandas as pd

from modules.coin_prediction import (
    analyze_coin
)

COINS = {
    "Bitcoin": "BTC-USD",
    "Ethereum": "ETH-USD",
    "Solana": "SOL-USD",
    "AAVE": "AAVE-USD",
    "Chainlink": "LINK-USD",
    "Avalanche": "AVAX-USD",
    "XRP": "XRP-USD",
    "BNB": "BNB-USD",
    "Sui": "SUI-USD",
    "Dogecoin": "DOGE-USD"
}
# Create Rankings
risk_rank = {
    "Low 🟢": 3,
    "Medium 🟡": 2,
    "High 🔴": 1
}

trend_rank = {
    "Very Strong Bullish 🟢": 6,
    "Strong Bullish 🟢": 5,
    "Bullish 🟢": 4,
    "Neutral 🟡": 3,
    "Bearish 🔴": 2,
    "Strong Bearish 🔴": 1,
    "Very Strong Bearish 🔴": 0
}



def show_coin_comparison_v2():

    st.title(
        "⚔️ Coin Comparison"
    )

    coin1_name = st.selectbox(
        "Select Coin 1",
        list(COINS.keys()),
        index=0
    )
    coin1 = COINS[coin1_name]

    coin2_name = st.selectbox(
        "Select Coin 2",
        list(COINS.keys()),
        index=1
    )
    coin2 = COINS[coin2_name]

    if st.button(
        "Compare Coins"
    ):

        #st.write(
        #    f"Comparing {coin1} vs {coin2}"
        #)
        if coin1 == coin2:

            st.warning(
                "Please select two different coins."
            )

            return

        coin1_result = analyze_coin(
            coin1
        )

        coin2_result = analyze_coin(
            coin2
        )
        if (
            coin1_result is None
            or coin2_result is None
        ):
            return       

        comparison_df = pd.DataFrame({

            "Metric": [

                "Current Price",

                "RSI",

                "Risk Level",

                "Trend",

                "Confidence Score",

                "Recommendation"
            ],

            coin1: [

                f"${coin1_result['current_price']:,.2f}",

                f"{coin1_result['rsi']:.2f}",

                coin1_result["risk_level"],

                coin1_result["trend_strength"],

                coin1_result["score"],

                coin1_result["recommendation_range"]
            ],

            coin2: [

                f"${coin2_result['current_price']:,.2f}",

                f"{coin2_result['rsi']:.2f}",

                coin2_result["risk_level"],

                coin2_result["trend_strength"],

                coin2_result["score"],

                coin2_result["recommendation_range"]
            ]
        })
        
        st.subheader(
            f"⚔️ {coin1_name} vs {coin2_name}"
        )
        comparison_df = comparison_df.astype(str)
        st.dataframe(
            comparison_df,
            width='stretch'
        )
        st.caption(
            "Comparison based on RSI, Trend Strength, Risk Level and Confidence Score."
        )

        coin1_points = 0
        coin2_points = 0
        # Compare confidence score
        #st.write(f"{coin1_result['score']} , {coin2_result['score']}")
        if coin1_result["score"] > coin2_result["score"]:
            coin1_points += 1

        elif coin2_result["score"] > coin1_result["score"]:
            coin2_points += 1
        # Compare RSI
        coin1_rsi_distance = abs(
            coin1_result["rsi"] - 50
        )

        coin2_rsi_distance = abs(
            coin2_result["rsi"] - 50
        )

        if coin1_rsi_distance < coin2_rsi_distance:
            coin1_points += 1

        elif coin2_rsi_distance < coin1_rsi_distance:
            coin2_points += 1
        # Compare Risk Level
        if (
            risk_rank[
                coin1_result["risk_level"]
            ]
            >
            risk_rank[
                coin2_result["risk_level"]
            ]
        ):

            coin1_points += 1

        elif (
            risk_rank[
                coin2_result["risk_level"]
            ]
            >
            risk_rank[
                coin1_result["risk_level"]
            ]
        ):

            coin2_points += 1
        # Compare Trend Strength
        if (
            trend_rank.get(
                coin1_result["trend_strength"],
                3
            )
            >
            trend_rank.get(
                coin2_result["trend_strength"],
                3
            )
        ):

            coin1_points += 1

        elif (
            trend_rank.get(
                coin2_result["trend_strength"],
                3
            )            
            >
            trend_rank.get(
                coin1_result["trend_strength"],
                3
            )
        ):

            coin2_points += 1
        # Display score board
        st.subheader(
            "🏆 Winner Analysis"
        )

        # create metrics
        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                coin1_name,
                coin1_points
            )

        with col2:
            st.metric(
                coin2_name,
                coin2_points
            )
        # Declare Winner
        if coin1_points > coin2_points:

            st.success(
                f"🏆 {coin1_name} currently has the stronger technical setup."
            )

        elif coin2_points > coin1_points:

            st.success(
                f"🏆 {coin2_name} currently has the stronger technical setup."
            )

        else:

            st.info(
                "⚖️ Both coins currently have similar technical strength."
            )
        st.caption(
            "Scoring based on Confidence Score, RSI Position, Risk Level and Trend Strength."
        )