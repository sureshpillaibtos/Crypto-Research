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
            f"{coin1_name} vs {coin2_name}"
        )
        comparison_df = comparison_df.astype(str)
        st.dataframe(
            comparison_df,
            width='stretch'
        )