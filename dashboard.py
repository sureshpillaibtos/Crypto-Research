import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import yfinance as yf
import numpy as np
from coin_analysis_engine_app import CoinAnalysisEngineApp
# Solution 1 (Recommended). Use Streamlit Cache.
# Phase 7.3: Rebalancing Advisor
# Phase 7.4 is where your project starts moving from a research dashboard to a portfolio planning platform.
# The idea is simple. If I invest $10,000 today, what could this portfolio be worth in 1, 3, 5, or 10 years under different market scenarios?
# Phase 7.5: Monte Carlo Portfolio Simulation
# Instead of one Bear/Base/Bull estimate, run hundreds or thousands of random simulations and see the range of possible outcomes.
# Phase 7.6: Portfolio Backtesting Engine
# What would have happened if I had invested in the past? Backtest period (1Y, 2Y, 5Y)
# current backtest assumes a lump-sum investment at the beginning
# Phase 7.7, DCA (Dollar Cost Averaging) Simulator : feature answer What would my portfolio be worth today if I had invested a fixed amount every month?


def highlight_scores(row):

    if row["Investment Score"] >= 8:
        return ["background-color: lightgreen"] * len(row)

    return [""] * len(row)

st.set_page_config(
    page_title="Crypto Research Dashboard",
    layout="wide"
)

st.sidebar.title("🇮🇳 Crypto Research")

page = st.sidebar.radio(
    "Navigation",
    [
        "Home",
        "Coin Rankings",
        "Coin Comparison",
        "Coin Details",
        "Portfolio Simulator",
        "Macro Command Center",
        "Coin Prediction"
    ]
)

# Refactoring steps... Step 1: Create all_coin_data once

#coins = [
#    "bitcoin",
#    "ethereum",
#    "solana",
#    "ripple",
#    "polkadot",
#   "binancecoin",
#   "cardano",
#   "stellar",
#    "cosmos"
#]

coins = [
    "bitcoin",
    "ethereum",    
    "jasmycoin",  
    "zilliqa",
    "solana" 
]

#symbol_map = {
#
#    "bitcoin": "BTC-USD",

#    "ethereum": "ETH-USD",

#    "solana": "SOL-USD",

#    "ripple": "XRP-USD",

#    "polkadot": "DOT-USD",
#    "binancecoin": "BNB-USD",  
#    "cardano": "ADA-USD",
#    "stellar": "XLM-USD",

#    "cosmos": "ATOM-USD"
#}
symbol_map = {

    "bitcoin": "BTC-USD",
    "ethereum": "ETH-USD",
    "jasmycoin": "JASMY-USD",
    "zilliqa" : "ZIL-USD",       
    "solana": "SOL-USD"
}

# Refact : 1

@st.cache_data(ttl=300)
def get_coin_analysis(coin):

    engine = CoinAnalysisEngineApp(coin)

    rank = engine.metrics.market_cap_rank
    quality_score = engine.quality_score()
    investment_score = engine.final_score()
    drawdown = engine.drawdown

    # Risk Model

    rank_risk = min(rank / 10, 10)

    quality_risk = 10 - quality_score

    investment_risk = 10 - investment_score

    drawdown_risk = min(
        abs(drawdown) / 20,
        10
    )

    risk_score = round(
        (
            rank_risk +
            quality_risk +
            investment_risk +
            drawdown_risk
        ) / 4,
        1
    )

    # Opportunity Model

    opportunity_score = round(
        (
            investment_score +
            quality_score +
            min(
                abs(drawdown) / 10,
                10
            )
        ) / 3,
        1
    )

    return {

        "name": engine.metrics.name,

        "price": engine.metrics.current_price,

        "rank": rank,

        "drawdown": drawdown,

        "quality_score": quality_score,

        "valuation_score":
            engine.valuation_score(),

        "investment_score":
            investment_score,

        "conviction":
            engine.conviction_level(),

        "verdict":
            engine.verdict(),

        "risk_score":
            risk_score,

        "opportunity_score":
            opportunity_score,

        # useful for breakdown section

        "rank_risk":
            rank_risk,

        "quality_risk":
            quality_risk,

        "investment_risk":
            investment_risk,

        "drawdown_risk":
            drawdown_risk
    }



@st.cache_data(ttl=3600)
def get_historical_price(symbol, period):

    return yf.download(
        symbol,
        period=period,
        progress=False
    )


@st.cache_data(ttl=300)
def load_all_coins():

    result = {}

    for coin in coins:

        try:

            result[coin] = get_coin_analysis(
                coin
            )

        except Exception as e:

            print(
                f"Failed loading {coin}: {e}"
            )

    return result

all_coin_data = load_all_coins()


# Refact : 2 , Remove old Data Collection Loop and Build DataFrame from Cached Results; V7 will have old way of coding
data = [
    {
        "Coin": result["name"],
        "Price": round(result["price"], 2),
        "Rank": result["rank"],
        "Drawdown %": round(result["drawdown"], 2),
        "Quality Score": result["quality_score"],
        "Valuation Score": result["valuation_score"],
        "Investment Score": result["investment_score"],
        "Conviction": result["conviction"],
        "Risk Score": result["risk_score"],
        "Opportunity Score": result["opportunity_score"],
        "Verdict": result["verdict"]
    }
    for result in all_coin_data.values()
]
if not data:
    st.error("No coin data loaded.")
    st.stop()

df = pd.DataFrame(data)
df = df.sort_values(
    by="Investment Score",
    ascending=False
)

if page == "Home":

    st.title("🚀 Crypto Research Dashboard")

    st.markdown("""
    Welcome to the Crypto Research Dashboard.

    Features:

    • Coin Rankings
    • Coin Comparison
    • Investment Scores
    • Quality Scores
    • Valuation Scores
    • Conviction Levels
    """)

elif page == "Coin Rankings":

    st.subheader("🏆 Coin Rankings", divider="blue")

    min_score = st.slider(
        "Minimum Investment Score",
        min_value=0.0,
        max_value=10.0,
        value=7.0,
        step=0.1
    )

    filtered_df = df[
        df["Investment Score"] >= min_score
    ]

    
    if not filtered_df.empty:

        st.dataframe(
            filtered_df.style.apply(
                highlight_scores,
                axis=1
            ),
            width="stretch"
        )

        top_coin = filtered_df.iloc[0]

        st.metric(
            "🥇 Top Ranked Coin",
            top_coin["Coin"],
            f"{top_coin['Investment Score']}/10"
        )

    else:
        st.warning(
            "No coins match the selected score."
        )
    

elif page == "Coin Comparison":

    comparison_coins = st.multiselect(
        "Select Coins to Compare",
        coins,
        default=["bitcoin", "ethereum"]
    )

    comparison_data = []
# Refact : 3, Coin Comparison Optimization
    for coin in comparison_coins:

        # Commented and replaced        
        result = all_coin_data[coin]

        comparison_data.append({

            "Coin": result["name"],
            "Price": round(result["price"], 2),
            "Market Rank": result["rank"],
            "Drawdown %": round(result["drawdown"], 2),

            "Quality": result["quality_score"],
            "Valuation": result["valuation_score"],
            "Investment": result["investment_score"],

            "Risk": result["risk_score"],
            "Opportunity": result["opportunity_score"],

            "Conviction": result["conviction"],
            "Verdict": result["verdict"]
        })

    st.subheader(
        "⚖️ Coin Comparison", divider="blue"
    )
    comparison_df = pd.DataFrame(
        comparison_data
    )

    st.dataframe(
        comparison_df,
        width="stretch"
    )

    cols = st.columns(
        len(comparison_coins)
    )
    # Refact 4: Comparison Metrics Optimization
    for idx, coin in enumerate(comparison_coins):
        
        result = all_coin_data[coin]

        with cols[idx]:

            st.metric(
                "Coin",
                result["name"]
            )

            st.metric(
                "Price",
                f"${result['price']:,.2f}"
            )

            st.metric(
                "Investment Score",
                result["investment_score"]
            )

            st.metric(
                "Quality Score",
                result["quality_score"]
            )

            st.metric(
                "Valuation Score",
                result["valuation_score"]
            )

    best_coin = comparison_df.loc[
        comparison_df["Investment"]
        .idxmax()
    ]

    st.success(
        f"🏆 Best Score: "
        f"{best_coin['Coin']} "
        f"({best_coin['Investment']}/10)"
    )


elif page == "Coin Details":

    selected_coin = st.selectbox(
        "Select Coin",
        coins
    )
    period = st.selectbox(
        "Select Period",
        ["1mo", "3mo", "6mo", "1y", "2y", "5y"]
    )
    
    result = all_coin_data[
        selected_coin
    ]

    risk_score = result["risk_score"]
    opportunity_score = result["opportunity_score"]
    rank_risk = result["rank_risk"]
    quality_risk = result["quality_risk"]
    investment_risk = result["investment_risk"]
    drawdown_risk = result["drawdown_risk"]

    symbol = symbol_map[selected_coin]
    price_df = get_historical_price(
        symbol,
        period
    )
    if isinstance(price_df.columns, pd.MultiIndex):
        price_df.columns = (
            price_df.columns.get_level_values(0)
    )
    
    ath_price = float(price_df["High"].max())
    current_price = result["price"]
    recovery_needed = (
        (ath_price / current_price) - 1
    ) * 100


    price_df["MA50"] = (
        price_df["Close"]
        .rolling(window=50)
        .mean()
    )

    price_df["MA200"] = (
        price_df["Close"]
        .rolling(window=200)
        .mean()
    )
    
    #ath = price_df["High"].max()
    col1, col2, col3 = st.columns(3)
    col4, col5 = st.columns(2)

    ma50 = price_df["MA50"].iloc[-1]
    ma200 = price_df["MA200"].iloc[-1]

    col4.metric(
        "50-Day MA",
        (
            f"${ma50:,.2f}"
            if pd.notna(ma50)
            else "N/A"
        )
    )

    col5.metric(
        "200-Day MA",
        (
            f"${ma200:,.2f}"
            if pd.notna(ma200)
            else "N/A"
        )
    )
    col6, col7 = st.columns(2)
    col6.metric(
        "Risk Score",
        f"{risk_score:.1f}/10"
    )

    col7.metric(
        "Opportunity Score",
        f"{opportunity_score:.1f}/10"
    )
    with st.expander(
        "Risk Score Breakdown"
    ):
        st.write(
            f"Market Rank Risk: {rank_risk:.1f}"
        )
        st.write(
            f"Quality Risk: {quality_risk:.1f}"
        )
        st.write(
            f"Investment Risk: {investment_risk:.1f}"
        )
        st.write(
            f"Drawdown Risk: {drawdown_risk:.1f}"
        )

    risk_reward_ratio = (
        opportunity_score / risk_score
        if risk_score > 0
        else 0
    )
    if risk_reward_ratio >= 2:
        st.success(
            "🟢 Excellent Risk/Reward Setup"
        )
    elif risk_reward_ratio >= 1:
        st.info(
            "🟡 Balanced Risk/Reward"
        )
    else:
        st.warning(
            "🔴 Risk outweighs reward"
        )
    st.subheader(
        "Risk / Reward Analysis", divider="blue"
    )
    st.metric(
        "Risk/Reward Ratio",
        f"{risk_reward_ratio:.2f}"
    )
    

    if result["drawdown"] < 20:
        st.success(
            "🟢 Near ATH"
        )
    elif result["drawdown"] < 50:

        st.warning(
            "🟡 Moderate Drawdown"
        )
    else:
        st.error(
            "🔴 Deep Drawdown"
        )
    ath_progress = float(
        current_price / ath_price
    )
    
    st.subheader(
        "ATH Recovery Progress", divider="blue"
    )
    st.progress(
        min(
            ath_progress,
            1.0
        )
    )
    st.caption(
        f"{ath_progress*100:.1f}% of ATH"
    )

    if pd.isna(ma50):
        st.info(
            "50-Day MA requires at least 50 days of data."
        )

    if pd.isna(ma200):
        st.info(
            "200-Day MA requires at least 200 days of data."
        )
    # Add Golden Cross / Death Cross Signal
    latest_ma50 = price_df["MA50"].iloc[-1]
    latest_ma200 = price_df["MA200"].iloc[-1]

    if pd.notna(latest_ma50) and pd.notna(latest_ma200):

        if latest_ma50 > latest_ma200:
            st.success(
                "🟢 Golden Cross Trend (Bullish)"
            )
        else:
            st.warning(
                "🔴 Death Cross Trend (Bearish)"
            )

    col1.metric(
        "Price",
        f"${result['price']:,.2f}"
    )

    col2.metric(
        "ATH Drawdown",
        f"{result['drawdown']:.2f}%"
    )

    col3.metric(
        "Investment Score",
        result["investment_score"]
    )
    
    col4, col5 = st.columns(2)
    col4.metric(
        "ATH Price",
        f"${ath_price:,.2f}"
    )
    col5.metric(
        "Recovery Needed",
        f"{recovery_needed:.2f}%"
    )
    if recovery_needed < 25:
        st.info(
            "Small move required to reach ATH."
        )
    elif recovery_needed < 100:
        st.info(
            "Significant recovery required."
        )
    else:
        st.info(
            "More than 2x needed to reclaim ATH."
        )

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=result["investment_score"],
            title={
                "text": "Investment Score"
            },
            gauge={
                "axis": {
                    "range": [0, 10]
                }
            }
        )
    )
    st.plotly_chart(
        fig,
        width="stretch"
    )
    fig_opportunity = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=opportunity_score,
            title={
                "text": "Opportunity Score"
            },
            gauge={
                "axis": {
                    "range": [0, 10]
                }
            }
        )
    )
    st.plotly_chart(
        fig_opportunity,
        width="stretch"
    )
   
    st.subheader(
        "📈 1-Year Price History", divider="blue"
    )
    st.line_chart(
        price_df["Close"]
    )

    fig_price = go.Figure()

    fig_price.add_trace(
        go.Scatter(
            x=price_df.index,
            y=price_df["Close"],
            mode="lines",
            name="Price"
        )
    )
    
    if price_df["MA50"].notna().any():

        fig_price.add_trace(
            go.Scatter(
                x=price_df.index,
                y=price_df["MA50"],
                mode="lines",
                name="50-Day MA"
            )
        )

    if price_df["MA200"].notna().any():

        fig_price.add_trace(
            go.Scatter(
                x=price_df.index,
                y=price_df["MA200"],
                mode="lines",
                name="200-Day MA"
            )
        )

    fig_price.update_layout(
        title=f"{selected_coin.upper()} Price History",
        xaxis_title="Date",
        yaxis_title="Price (USD)"
    )

    fig_price.add_hline(
        y=ath_price,
        line_dash="dash",
        annotation_text=
        f"ATH ${ath_price:,.0f}",
        annotation_position=
        "top left"
    )

    st.plotly_chart(
        fig_price,
        width="stretch"
    )

elif page == "Portfolio Simulator":

    st.title(
        "💼 Portfolio Simulator"
    )
    total_investment = st.number_input(
        "Total Investment Amount ($)",
        min_value=100,
        value=10000,
        step=100
    )

    portfolio_coins = st.multiselect(
        "Select Coins",
        coins,
        default=[
            "bitcoin",
            "ethereum",
            "solana"
        ]
    )
    allocations = {}
    
    for coin in portfolio_coins:

        allocations[coin] = st.slider(
            f"{coin.upper()} Allocation %",
            min_value=0,
            max_value=100,
            value=int(
                100 / len(portfolio_coins)
            )
        )
    total_allocation = sum(
        allocations.values()
    )

    st.write(
        f"Total Allocation: {total_allocation}%"
    )

    if total_allocation != 100:

        st.error(
            "Portfolio allocation must equal 100%"
        )

        st.stop()

    portfolio_data = []

    for coin in portfolio_coins:

        allocation = allocations[coin]

        invested_amount = (
            total_investment *
            allocation / 100
        )

        result = all_coin_data[coin]

        portfolio_data.append({

            "Coin":
                result["name"],

            "Allocation %":
                allocation,

            "Investment $":
                round(
                    invested_amount,
                    2
                ),

            "Investment Score":
                result["investment_score"],

            "Risk Score":
                result["risk_score"],

            "Opportunity Score":
                result["opportunity_score"],
            "Drawdown %":
                result["drawdown"]
        })

    portfolio_df = pd.DataFrame(
        portfolio_data
    )

    st.subheader(
        "Portfolio Allocation", divider="blue"
    )

    st.dataframe(
        portfolio_df,
        width="stretch"
    )


    weighted_investment_score = sum(
        row["Investment Score"] *
        row["Allocation %"] / 100

        for _, row
        in portfolio_df.iterrows()

    )

    weighted_risk_score = sum(
        row["Risk Score"] *
        row["Allocation %"] / 100

        for _, row
        in portfolio_df.iterrows()

    )

    weighted_opportunity_score = sum(
        row["Opportunity Score"] *
        row["Allocation %"] / 100

        for _, row
        in portfolio_df.iterrows()

    )

    col1, col2, col3 = st.columns(3)
    col1.metric(
        "Portfolio Investment Score",
        f"{weighted_investment_score:.1f}/10"
    )
    col2.metric(
        "Portfolio Risk Score",
        f"{weighted_risk_score:.1f}/10"
    )
    col3.metric(
        "Portfolio Opportunity Score",
        f"{weighted_opportunity_score:.1f}/10"
    )

    st.subheader(
        "Portfolio Allocation Chart", divider="blue"
    )

    fig_pie = go.Figure(
        data=[
            go.Pie(
                labels=portfolio_df["Coin"],
                values=portfolio_df["Allocation %"],
                hole=0.4
            )
        ]
    )

    st.plotly_chart(
        fig_pie,
        width="stretch"
    )


    diversification_score = min(
        len(portfolio_coins) * 2,
        10
    )

    st.metric(
        "Diversification Score",
        f"{diversification_score}/10"
    )


    overall_score = (
        weighted_investment_score +
        weighted_opportunity_score +
        (10 - weighted_risk_score)
    ) / 3


    if overall_score >= 8:
        grade = "A"
    elif overall_score >= 7:
        grade = "B"
    elif overall_score >= 6:
        grade = "C"
    else:
        grade = "D"

    st.metric(
        "Portfolio Grade",
        grade
    )



    if grade == "A":
        st.success(
            "🟢 Strong Portfolio"
        )
    elif grade == "B":
        st.info(
            "🟡 Healthy Portfolio"
        )
    elif grade == "C":
        st.warning(
            "🟠 Average Portfolio"
        )
    else:
        st.error(
            "🔴 High Risk Portfolio"
        )

    # ==========================
    # Phase 8.1 Starts Here
    # ==========================
    # Calculate Health Score
    health_score = round(
        (
            weighted_investment_score * 0.40
            +
            weighted_opportunity_score * 0.30
            +
            diversification_score * 0.20
            +
            (10 - weighted_risk_score) * 0.10
        ),
        1
    )
    # Display Health Score
    st.subheader(
        "🏥 Portfolio Health Analyzer", divider="blue"
    )

    st.metric(
        "Portfolio Health Score",
        f"{health_score}/10"
    )

    # Generate Strengths
    strengths = []
    if weighted_investment_score >= 8:
        strengths.append(
            "✅ Strong investment quality"
        )

    if diversification_score >= 6:
        strengths.append(
            "✅ Well diversified portfolio"
        )

    if weighted_risk_score <= 4:
        strengths.append(
            "✅ Controlled risk exposure"
        )

    if weighted_opportunity_score >= 7:
        strengths.append(
            "✅ Strong growth potential"
        )
    
    # Generate Weaknesses
    weaknesses = []
    if weighted_risk_score > 6:
        weaknesses.append(
            "⚠️ Portfolio risk is elevated"
        )

    if diversification_score < 4:
        weaknesses.append(
            "⚠️ Low diversification"
        )

    if weighted_investment_score < 6:
        weaknesses.append(
            "⚠️ Weak investment quality"
        )

    if weighted_opportunity_score < 5:
        weaknesses.append(
            "⚠️ Limited upside potential"
        )
    # Display Analysis
    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            "### Strengths"
        )

        if strengths:

            for item in strengths:
                st.write(item)

        else:
            st.write(
                "No major strengths identified."
            )

    with col2:

        st.markdown(
            "### Weaknesses"
        )

        if weaknesses:

            for item in weaknesses:
                st.write(item)

        else:
            st.write(
                "No major weaknesses identified."
            )


    # Recommendation Engine
    if health_score >= 8:

        recommendation = (
            "🟢 Portfolio is in excellent condition."
        )

    elif health_score >= 6:

        recommendation = (
            "🟡 Portfolio is healthy but can be improved."
        )

    else:

        recommendation = (
            "🔴 Portfolio requires attention."
        )

    st.info(
        recommendation
    )

    # Health Gauge
    fig_health = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=health_score,
            title={
                "text":
                "Portfolio Health"
            },
            gauge={
                "axis": {
                    "range": [0, 10]
                }
            }
        )
    )

    st.plotly_chart(
        fig_health,
        width="stretch"
    )

    ##### Phase 8.2 – Volatility Analyzer ###
    ### ---- New section---- ######
    st.subheader(
        "📊 Volatility Analyzer", divider="blue"
    )
    # Create Volatility Data
    volatility_data = []
    # Loop Through Selected Coins
    for coin in portfolio_coins:

        symbol = symbol_map[coin]

        hist = get_historical_price(
            symbol,
            "1y"
        )
    # Handle MultiIndex
        if isinstance(
            hist.columns,
            pd.MultiIndex
        ):
            hist.columns = (
                hist.columns
                .get_level_values(0)
            )
    # Calculate Daily Return
        daily_returns = (
            hist["Close"]
            .pct_change()
            .dropna()
        )
    # Annualized Volatility
    volatility = (
        daily_returns.std()
        * (365 ** 0.5)
        * 100
    )
    volatility_data.append(
        {
            "Coin":
                all_coin_data[coin]["name"],
            "Volatility %":
                round(
                    volatility,
                    2
                )
            }
        )
    # Create DataFrame
    vol_df = pd.DataFrame(
        volatility_data
    )
    vol_df = vol_df.sort_values(
        by="Volatility %",
        ascending=False
    )

    # Display Table
    st.dataframe(
        vol_df,
        width="stretch"
    )
    # Portfolio Average Volatility
    portfolio_volatility = round(
        vol_df[
            "Volatility %"
        ].mean(),
        2
    )

    st.metric(
        "Average Portfolio Volatility",
        f"{portfolio_volatility}%"
    )

    # Volatility Rating
    if portfolio_volatility < 40:

        st.success(
            "🟢 Low Volatility Portfolio"
        )

    elif portfolio_volatility < 70:

        st.warning(
            "🟡 Moderate Volatility Portfolio"
        )

    else:

        st.error(
            "🔴 High Volatility Portfolio"
        )
    
    # Bar Chart
    fig_vol = go.Figure()

    fig_vol.add_bar(
        x=vol_df["Coin"],
        y=vol_df["Volatility %"]
    )

    fig_vol.update_layout(
        title=
        "Coin Volatility Comparison",
        xaxis_title="Coin",
        yaxis_title=
        "Volatility (%)"
    )

    st.plotly_chart(
        fig_vol,
        width="stretch"
    )
    # Most / Least Volatile Coin
    # Most volatile:
    most_volatile = vol_df.iloc[0]
    least_volatile = vol_df.iloc[-1]

    st.warning(
        f"⚠️ Most Volatile: "
        f"{most_volatile['Coin']} "
        f"({most_volatile['Volatility %']}%)"
    )

    st.success(
        f"🛡️ Least Volatile: "
        f"{least_volatile['Coin']} "
        f"({least_volatile['Volatility %']}%)"
    )


    ### Phase 8.3 – Sharpe Ratio Engine ###
    st.subheader(
        "⚖️ Sharpe Ratio Engine", divider="blue"
    )
    # Risk-Free Rate
    risk_free_rate = 0.04
    # Create Sharpe Data
    sharpe_data = []
    # Loop Through Coins
    for coin in portfolio_coins:

        symbol = symbol_map[coin]

        hist = get_historical_price(
            symbol,
            "1y"
        )
    # Handle MultiIndex
        if isinstance(
            hist.columns,
            pd.MultiIndex
        ):
            hist.columns = (
                hist.columns
                .get_level_values(0)
            )
        # Daily Returns
        daily_returns = (
            hist["Close"]
            .pct_change()
            .dropna()
        )
        # Annual Return
        start_price = float(
            hist["Close"].iloc[0]
        )

        end_price = float(
            hist["Close"].iloc[-1]
        )

        annual_return = (
            end_price /
            start_price
            - 1
        )
        # Annualized Volatility
        annual_volatility = (
            daily_returns.std()
            *
            (365 ** 0.5)
        )
        # Calculate Sharpe
        if annual_volatility > 0:

            sharpe_ratio = (
                annual_return -
                risk_free_rate
            ) / annual_volatility

        else:

            sharpe_ratio = 0
        
        # Store Results
        allocation = allocations[coin]

        sharpe_data.append(
            {
                "Coin": result["name"],
                "Allocation %": allocation,
                "Return %": round(
                    annual_return * 100,
                    2
                ),
                "Sharpe Ratio": round(
                    sharpe_ratio,
                    2
                )
            }
        )
        result = all_coin_data[coin]
        # Build DataFrame
        sharpe_df = pd.DataFrame(
            sharpe_data
        )

        sharpe_df = sharpe_df.sort_values(
            by="Sharpe Ratio",
            ascending=False
        )
        # Display
        st.dataframe(
            sharpe_df,
            width="stretch"
        )
        # Best & Worst
        best_sharpe = sharpe_df.iloc[0]
        worst_sharpe = sharpe_df.iloc[-1]
        st.success(
            f"🏆 Best Risk-Adjusted Return: "
            f"{best_sharpe['Coin']} "
            f"(Sharpe {best_sharpe['Sharpe Ratio']})"
        )

        st.warning(
            f"⚠️ Weakest Risk-Adjusted Return: "
            f"{worst_sharpe['Coin']} "
            f"(Sharpe {worst_sharpe['Sharpe Ratio']})"
        )
        # Average Portfolio Sharpe
        portfolio_sharpe = round(
            (
                sharpe_df["Sharpe Ratio"]
                *
                sharpe_df["Allocation %"]
                / 100
            ).sum(),
            2
        )
        st.metric(
            "Portfolio Sharpe Ratio",
            portfolio_sharpe
        )

        # Sharpe Rating
        if portfolio_sharpe >= 2:

            st.success(
                "🟢 Excellent Risk-Adjusted Return"
            )

        elif portfolio_sharpe >= 1:

            st.info(
                "🟡 Good Risk-Adjusted Return"
            )

        else:

            st.warning(
                "🔴 Weak Risk-Adjusted Return"
            )    
               
        # Bar Chart
        fig_sharpe = go.Figure()

        fig_sharpe.add_bar(
                x=sharpe_df["Coin"],
                y=sharpe_df["Sharpe Ratio"]
            )

        fig_sharpe.update_layout(
            title=
            "Sharpe Ratio Comparison",
            xaxis_title="Coin",
            yaxis_title=
            "Sharpe Ratio"
        )

        st.plotly_chart(
            fig_sharpe,
            width="stretch"
        )

    # Phase 8.4 – Correlation Matrix
    # Are my portfolio coins moving together or independently
    # Add Section Header
    st.subheader(
        "🔗 Correlation Matrix", divider="blue"
    )
    # Download Historical Prices
    correlation_prices = pd.DataFrame()
    for coin in portfolio_coins:

        symbol = symbol_map[coin]

        hist = get_historical_price(
            symbol,
            "1y"
        )

        if isinstance(
            hist.columns,
            pd.MultiIndex
        ):
            hist.columns = (
                hist.columns.get_level_values(0)
            )

    correlation_prices[
        coin.upper()
    ] = hist["Close"]

    # Calculate Daily Returns
    returns_df = (
        correlation_prices
        .pct_change()
        .dropna()
    )
    # Build Correlation Matrix
    correlation_matrix = (
        returns_df
        .corr()
    )
    # Display Table
    st.dataframe(
        correlation_matrix.round(2),
        width="stretch"
    )
    # Plot Heatmap
    fig_corr = go.Figure(
        data=go.Heatmap(
            z=correlation_matrix.values,
            x=correlation_matrix.columns,
            y=correlation_matrix.index,
            text=correlation_matrix.round(2),
            texttemplate="%{text}",
            hoverongaps=False
        )
    )

    fig_corr.update_layout(
        title="Portfolio Correlation Matrix"
    )

    st.plotly_chart(
        fig_corr,
        width="stretch"
    )
    
    # Portfolio Diversification Insight
    avg_corr = None
    if len(correlation_matrix) > 1:

        avg_corr = (
            correlation_matrix
            .where(
                ~np.eye(
                    len(correlation_matrix),
                    dtype=bool
                )
            )
            .stack()
            .dropna()
            .mean()
        )

        if pd.notna(avg_corr):

            st.metric(
                "Average Correlation",
                f"{avg_corr:.2f}"
            )
            # AI Interpretation
            if avg_corr < 0.3:
                st.success(
                    "🟢 Excellent diversification. Holdings are relatively independent."
                )
            elif avg_corr < 0.6:

                st.info(
                    "🟡 Moderate diversification."
                )
            else:
                st.warning(
                    "🔴 Highly correlated portfolio. Most holdings move together."
                )


        else:

            st.metric(
                "Average Correlation",
                "N/A"
            )

    else:

        st.metric(
            "Average Correlation",
            "N/A"
        )


    #### Phase 8.5 – Portfolio Stress Test Engine ####
    # How much money would my portfolio lose if crypto enters another major bear market?
    st.subheader(
        "💥 Portfolio Stress Test", divider="blue"
    )
    # Define Stress Scenarios
    stress_scenarios = {
        "Bear Market (-20%)": 0.20,
        "Crypto Winter (-40%)": 0.40,
        "Black Swan (-60%)": 0.60
    }
    # Calculate Portfolio Impact
    stress_results = []

    for scenario, decline in stress_scenarios.items():

        risk_multiplier = (
            weighted_risk_score / 10
        )

        adjusted_decline = (
            decline *
            (0.5 + risk_multiplier)
        )

        stressed_value = (
            total_investment *
            (1 - adjusted_decline)
        )

        dollar_loss = (
            total_investment -
            stressed_value
        )

        stress_results.append({

            "Scenario":
                scenario,

            "Portfolio Value ($)":
                round(
                    stressed_value,
                    2
                ),

            "Loss ($)":
                round(
                    dollar_loss,
                    2
                ),

            "Loss (%)":
                decline * 100
        })
        # Create DataFrame
        stress_df = pd.DataFrame(
            stress_results
        )
        # Display Table
        st.dataframe(
            stress_df,
            width="stretch"
        )
        # Survival Score
        black_swan_value = (
            stress_df.iloc[-1]
            ["Portfolio Value ($)"]
        )

        survival_score = round(
            (
                black_swan_value /
                total_investment
            ) * 10,
            1
        )
        # Show Survival Score
        st.metric(
            "Portfolio Survival Score",
            f"{survival_score}/10"
        )
        if survival_score >= 6:
            st.success(
                "🟢 Portfolio is resilient"
            )
        elif survival_score >= 4:

            st.warning(
                "🟡 Moderate resilience"
            )
        else:
            st.error(
                "🔴 Vulnerable portfolio"
            )
    # Add a bar chart
    fig_stress = go.Figure()

    fig_stress.add_bar(
        x=stress_df["Scenario"],
        y=stress_df["Portfolio Value ($)"]
    )

    fig_stress.update_layout(
        title="Portfolio Value Under Stress Scenarios"
    )

    st.plotly_chart(
        fig_stress,
        width="stretch"
    )

    #### Phase 8.6 – Portfolio AI Advisor ####
    st.subheader(
        "🤖 Portfolio AI Advisor", divider="blue"
    )
    advice = []
    # Analyze Portfolio Grade
    if grade == "A":
        advice.append(
            "Strong portfolio structure."
        )
    elif grade == "B":
        advice.append(
            "Good portfolio but has room for optimization."
        )
    elif grade == "C":
        advice.append(
            "Portfolio quality is average."
        )
    else:
        advice.append(
            "Portfolio risk appears elevated."
        )
    # Diversification Analysis
    if diversification_score < 4:
        advice.append(
            "Portfolio is under-diversified."
        )
    elif diversification_score < 8:
        advice.append(
            "Diversification is reasonable."
        )
    else:
        advice.append(
            "Diversification is excellent."
        )
    # Risk Analysis
    if weighted_risk_score > 6:
        advice.append(
            "Portfolio risk is relatively high."
        )
    elif weighted_risk_score > 3:

        advice.append(
            "Portfolio risk is moderate."
        )
    else:

        advice.append(
            "Portfolio risk is low."
        )
    # Sharpe Ratio Analysis : Using the portfolio Sharpe ratio from Phase 8.3:
    if portfolio_sharpe > 1:
        advice.append(
            "Risk-adjusted returns look strong."
        )
    elif portfolio_sharpe > 0:
        advice.append(
            "Risk-adjusted returns are acceptable."
        )
    else:
        advice.append(
            "Risk-adjusted returns are weak."
        )
    # Correlation Analysis : Using avg_corr from Phase 8.4:
    if avg_corr is not None:
        if avg_corr > 0.75:
            advice.append(
                "Holdings are highly correlated."
            )
        elif avg_corr > 0.50:

            advice.append(
                "Moderate correlation exists between assets."
            )
        else:

            advice.append(
                "Correlation is low and diversification is effective."
            )
    # Stress Test Analysis : Using survival_score from Phase 8.5:
    if survival_score >= 6:

        advice.append(
            "Portfolio demonstrates strong resilience."
        )

    elif survival_score >= 4:

        advice.append(
            "Portfolio resilience is moderate."
        )

    else:

        advice.append(
            "Portfolio could suffer heavily during severe market stress."
        )
    # Display Advice
    for item in advice:
        st.write(
            f"• {item}"
        )

    # Overall AI Verdict
    advisor_score = round(
        (
            overall_score +
            diversification_score +
            portfolio_sharpe +
            survival_score
        ) / 4,
        1
    )
    st.metric(
        "AI Portfolio Score",
        f"{advisor_score}/10"
    )
    if advisor_score >= 8:
        st.success(
            "🟢 AI Verdict: Excellent Portfolio"
        )
    elif advisor_score >= 6:
        st.info(
            "🟡 AI Verdict: Healthy Portfolio"
        )
    elif advisor_score >= 4:
        st.warning(
            "🟠 AI Verdict: Needs Improvement"
        )
    else:
        st.error(
            "🔴 AI Verdict: High Risk Portfolio"
        )


#### NEXT PHASE HERE
    # Phase 8.7 – Market Regime Detector
    st.subheader(
        "🌍 Market Regime Detector", divider="blue"
    )
    # Download BTC Data
    btc_hist = get_historical_price(
        "BTC-USD",
        "1y"
    )
    if isinstance(
        btc_hist.columns,
        pd.MultiIndex
    ):
        btc_hist.columns = (
            btc_hist.columns
            .get_level_values(0)
        )
        # Calculate Trend Indicators
        btc_hist["MA50"] = (
            btc_hist["Close"]
            .rolling(50)
            .mean()
        )

        btc_hist["MA200"] = (
            btc_hist["Close"]
            .rolling(200)
            .mean()
        )
        current_price = float(
            btc_hist["Close"].iloc[-1]
        )

        ma50 = float(
            btc_hist["MA50"].iloc[-1]
        )

        ma200 = float(
            btc_hist["MA200"].iloc[-1]
        )
        # Calculate Volatility
        btc_returns = (
            btc_hist["Close"]
            .pct_change()
        )

        btc_volatility = (
            btc_returns.std()
            * np.sqrt(365)
            * 100
        )
        # Detect Market Regime : bull/bear market
        if (
            current_price > ma50
            and
            ma50 > ma200
        ):
            regime = "Bull Market"
            emoji = "🟢"
        elif (
            current_price < ma50
            and
            ma50 < ma200
        ):
            regime = "Bear Market"
            emoji = "🔴"
        # correct, neutral
        elif btc_volatility > 60:
            regime = "Correction"
            emoji = "🟠"
        else:
            regime = "Neutral Market"
            emoji = "🟡"
        # Display Regime
        st.metric(
            "Current Market Regime",
            f"{emoji} {regime}"
        )
        # Market Commentary
        if regime == "Bull Market":
            st.success(
                "Momentum remains positive and trend indicators are bullish."
            )
        elif regime == "Bear Market":
            st.error(
                "Long-term trend remains negative. Risk management is important."
            )
        elif regime == "Correction":
            st.warning(
                "Market volatility is elevated and conditions remain unstable."
            )
        else:
            st.info(
                "Market lacks a clear directional trend."
            )
        # Regime Strength
        regime_strength = round(
            (
                (
                    current_price -
                    ma200
                )
                /
                ma200
            ) * 100,
            1
        )
        # display
        st.metric(
            "Trend Strength",
            f"{regime_strength}%"
        )
        # iterpretaion
        if regime_strength > 20:
            st.success(
                "Strong uptrend"
            )
        elif regime_strength > 0:
            st.info(
                "Moderate uptrend"
            )
        elif regime_strength > -20:
            st.warning(
                "Weak market structure"
            )
        else:
            st.error(
                "Strong downtrend"
            )
        # Dashboard Summary Card
        col1, col2, col3 = st.columns(3)
        col1.metric(
            "Market Regime",
            regime
        )
        col2.metric(
            "BTC Volatility",
            f"{btc_volatility:.1f}%"
        )
        col3.metric(
            "Trend Strength",
            f"{regime_strength}%"
        )

    # Phase 8.8 : Portfolio Risk Alert System
    st.subheader(
        "🚨 Portfolio Risk Alert System", divider="blue"
    )
    risk_alerts = []
    # Concentration Risk Check using current portfolio
    max_allocation = portfolio_df[
        "Allocation %"
    ].max()

    largest_holding = portfolio_df.loc[
        portfolio_df[
            "Allocation %"
        ].idxmax()
    ]
    if max_allocation > 50:

        risk_alerts.append(
            f"High concentration risk: "
            f"{largest_holding['Coin']} "
            f"represents {max_allocation}% "
            f"of the portfolio."
        )

    if weighted_risk_score > 6:

        risk_alerts.append(
            "Portfolio risk score is elevated."
        )
    # Diversification Alert
    if diversification_score < 4:

        risk_alerts.append(
            "Portfolio diversification is weak."
        )
    # Sharpe Ratio Alert
    if portfolio_sharpe < 0.5:

        risk_alerts.append(
            "Risk-adjusted returns are poor."
        )
    # Correlation Alert
    if (
        avg_corr is not None
        and
        avg_corr > 0.75
    ):

        risk_alerts.append(
            "Portfolio holdings are highly correlated."
        )
    # Stress-Test Alert
    if survival_score < 4:

        risk_alerts.append(
            "Portfolio may struggle during severe market stress."
        )
    # Market Regime Alert
    if regime == "Bear Market":

        risk_alerts.append(
            "Current market regime is bearish."
        )

    elif regime == "Correction":

        risk_alerts.append(
            "Market volatility remains elevated."
        )
    # 10: Display Alerts
    if risk_alerts:

        for alert in risk_alerts:

            st.warning(
                f"⚠️ {alert}"
            )

    else:

        st.success(
            "✅ No major portfolio risks detected."
        )
    # Risk Severity Score
    risk_alert_score = len(
        risk_alerts
    )
    st.metric(
        "Risk Alert Count",
        risk_alert_score
    )
    if risk_alert_score == 0:

        st.success(
            "Low Portfolio Risk"
        )

    elif risk_alert_score <= 2:

        st.info(
            "Manageable Risk Level"
        )

    elif risk_alert_score <= 4:

        st.warning(
            "Moderate Risk Level"
        )

    else:

        st.error(
            "High Risk Level"
        )
    # Risk Dashboard Summary
    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Portfolio Risk",
        f"{weighted_risk_score:.1f}/10"
    )

    col2.metric(
        "Risk Alerts",
        risk_alert_score
    )

    col3.metric(
        "Survival Score",
        f"{survival_score}/10"
    )
    # Critical Alert Detection
    critical_alert = (
        weighted_risk_score > 7
        and
        survival_score < 4
    )
    if critical_alert:

        st.error(
            "🚨 Critical Risk Warning: "
            "Portfolio is vulnerable to major drawdowns."
        )

    #st.markdown("End of :red[Portfolio Risk Alert System] and this is  :rainbow[Done]! :sunglasses:")
    #st.markdown(":rainbow[------------------------------------]")
    st.divider()

    # Phase 9 — Professional Quant Analytics., 9.1 Maximum Drawdown Analyzer
    st.subheader(
        "📉 Maximum Drawdown Analyzer", divider="blue"
    )
    # Build Portfolio Historical Curve
    portfolio_curve = pd.DataFrame()
    for coin in portfolio_coins:
        symbol = symbol_map[coin]
        try:
            hist = get_historical_price(
                symbol,
                "1y"
            )

            if isinstance(
                hist.columns,
                pd.MultiIndex
            ):
                hist.columns = (
                    hist.columns
                    .get_level_values(0)
                )

            portfolio_curve[
                coin
            ] = hist["Close"]
        except Exception:
            pass
    # Create Weighted Portfolio; Use current allocations.
    weights = []
    for coin in portfolio_coins:
        weights.append(
            allocations[coin] / 100
        )
    weights = np.array(weights)    
    # Normalize Prices : Convert all coins to same starting point
    normalized_prices = (
        portfolio_curve /
        portfolio_curve.iloc[0]
    )
    # Build Portfolio Value Series
    portfolio_values = (
        normalized_prices
        * weights
    ).sum(axis=1)
    # Calculate Running Peak
    running_peak = (
        portfolio_values
        .cummax()
    )
    # Calculate Drawdown
    drawdowns = (
        portfolio_values -
        running_peak
    ) / running_peak
    # Maximum Drawdown
    max_drawdown = (
        drawdowns.min()
        * 100
    )
    # Display Metric
    st.metric(
        "Maximum Drawdown",
        f"{max_drawdown:.2f}%"
    )
    # Add recovery statistics:
    current_drawdown = (
        drawdowns.iloc[-1]
        * 100
    )
    st.metric(
        "Current Drawdown",
        f"{current_drawdown:.2f}%"
    )
    # Risk Interpretation
    if max_drawdown > -10:
        st.success(
            "🟢 Very Stable Portfolio"
        )
    elif max_drawdown > -25:

        st.info(
            "🟡 Normal Market Risk"
        )
    elif max_drawdown > -40:
        st.warning(
            "🟠 High Drawdown Risk"
        )
    else:
        st.error(
            "🔴 Extreme Drawdown Risk"
        )
    # Drawdown Chart
    fig_dd = go.Figure()

    fig_dd.add_trace(
        go.Scatter(
            x=drawdowns.index,
            y=drawdowns * 100,
            mode="lines",
            name="Drawdown %"
        )
    )

    fig_dd.update_layout(
        title="Portfolio Drawdown History Suresh",
        yaxis_title="Drawdown %",
        xaxis_title="Date"
    )
    st.plotly_chart(
        fig_dd,
        width="stretch"
    )
    # Phase 9.2 – Sortino Ratio Analyzer
    st.subheader(
        "📊 Sortino Ratio Analyzer", divider='blue'
    )
    portfolio_returns = (
        portfolio_values
        .pct_change()
        .dropna()
    )
    # Risk-Free Rate
    risk_free_rate = 0.04
    daily_rf = (
        risk_free_rate / 252
    )
    # Excess Returns
    excess_returns = (
        portfolio_returns -
        daily_rf
    )
    # Downside Returns Only: This is the key difference.
    downside_returns = (
        excess_returns[
            excess_returns < 0
        ]
    )
    # Downside Deviation
    downside_deviation = (
        downside_returns.std()
        * np.sqrt(252)
    )
    # Annual Portfolio Return
    annual_return = (
        portfolio_returns.mean()
        * 252
    )
    # Sortino Ratio
    if downside_deviation > 0:
        portfolio_sortino = (
            (
                annual_return -
                risk_free_rate
            )
            /
            downside_deviation
        )
    else:
        portfolio_sortino = 0
    # Display Metric
    st.metric(
        "Portfolio Sortino Ratio",
        f"{portfolio_sortino:.2f}"
    )
    # Interpretation
    if portfolio_sortino >= 2:
        st.success(
            "🟢 Excellent downside-adjusted returns"
        )
    elif portfolio_sortino >= 1:
        st.info(
            "🟡 Good downside-adjusted returns"
        )
    elif portfolio_sortino > 0:
        st.warning(
            "🟠 Weak downside-adjusted returns"
        )
    else:
        st.error(
            "🔴 Poor downside protection"
        )
    # Compare Sharpe vs Sortino
    comparison_df = pd.DataFrame({

        "Metric": [
            "Sharpe Ratio",
            "Sortino Ratio"
        ],

        "Value": [
            round(
                portfolio_sharpe,
                2
            ),

            round(
                portfolio_sortino,
                2
            )
        ]
    })

    st.dataframe(
        comparison_df,
        width="stretch"
    )

    # AI Insight
    if portfolio_sortino > portfolio_sharpe:
        st.success(
            "Portfolio handles downside risk better than overall volatility suggests."
        )
    elif portfolio_sortino < portfolio_sharpe:
        st.warning(
            "Downside volatility remains a significant risk."
        )
    else:
        st.info(
            "Sharpe and Sortino indicate similar risk characteristics."
        )
    st.html(""" <hr style=" border: none; border-top: 3px solid orange; margin: 20px 0;"> """)

    # Phase 9.3 – Value at Risk (VaR)
    # answer What is the maximum expected loss over the next day with 95% confidence
    st.subheader(
        "⚠️ Value at Risk (VaR)", divider='blue'
    )
    # Reuse Portfolio Returns
    portfolio_returns = (
        portfolio_values
        .pct_change()
        .dropna()
    )
    # Calculate Historical VaR : 95%,99% confidence
    var_95 = np.percentile(
        portfolio_returns,
        5
    )
    var_99 = np.percentile(
        portfolio_returns,
        1
    )
    # Convert to Percent
    var_95_pct = (
        var_95 * 100
    )

    var_99_pct = (
        var_99 * 100
    )
    col1, col2 = st.columns(2)

    col1.metric(
        "95% VaR",
        f"{var_95_pct:.2f}%"
    )

    col2.metric(
        "99% VaR",
        f"{var_99_pct:.2f}%"
    )
    # Dollar VaR
    var_95_dollar = (
        total_investment *
        abs(var_95)
    )

    var_99_dollar = (
        total_investment *
        abs(var_99)
    )

    col3, col4 = st.columns(2)

    col3.metric(
        "95% Daily Loss ($)",
        f"${var_95_dollar:,.2f}"
    )

    col4.metric(
        "99% Daily Loss ($)",
        f"${var_99_dollar:,.2f}"
    )

    # Risk Interpretation
    if abs(var_95_pct) < 2:
        st.success(
            "🟢 Low daily risk profile"
        )
    elif abs(var_95_pct) < 5:
        st.info(
            "🟡 Moderate daily risk profile"
        )
    elif abs(var_95_pct) < 8:
        st.warning(
            "🟠 Elevated daily risk profile"
        )
    else:
        st.error(
            "🔴 High daily risk profile"
        )
    # AI Explanation
    st.info(
        f"""
        Historical analysis suggests that
        on 95% of trading days the portfolio
        should not lose more than
        {abs(var_95_pct):.2f}% in a day.

        Estimated loss:
        ${var_95_dollar:,.0f}
        """
    )
    # VaR Distribution Chart
    fig_var = go.Figure()
    fig_var.add_histogram(
        x=portfolio_returns * 100,
        nbinsx=50,
        name="Daily Returns"
    )
    fig_var.add_vline(
        x=var_95_pct,
        line_dash="dash",
        annotation_text="95% VaR"
    )
    fig_var.add_vline(
        x=var_99_pct,
        line_dash="dot",
        annotation_text="99% VaR"
    )
    fig_var.update_layout(
        title="Portfolio Return Distribution",
        xaxis_title="Daily Return %",
        yaxis_title="Frequency"
    )
    st.plotly_chart(
        fig_var,
        width="stretch"
    )
    
    # Risk Score
    var_risk_score = min(
        abs(var_95_pct),
        10
    )

    st.metric(
        "VaR Risk Score",
        f"{var_risk_score:.1f}/10"
    )
    st.html(""" <hr style=" border: none; border-top: 3px solid orange; margin: 20px 0;"> """)


    # Phase 9.4 – Conditional VaR (CVaR)
    # What's the loss threshold of the worst 5% days? If I actually fall into that worst 5%, what is my average loss?
    st.subheader(
        "🔥 Conditional VaR (CVaR)", divider='blue'
    )
    cvar_95 = (
        portfolio_returns[
            portfolio_returns <= var_95
        ]
        .mean()
    )
    cvar_99 = (
        portfolio_returns[
            portfolio_returns <= var_99
        ]
        .mean()
    )
    # Convert to Percentage
    cvar_95_pct = (
        cvar_95 * 100
    )

    cvar_99_pct = (
        cvar_99 * 100
    )
    col1, col2 = st.columns(2)

    col1.metric(
        "95% CVaR",
        f"{cvar_95_pct:.2f}%"
    )

    col2.metric(
        "99% CVaR",
        f"{cvar_99_pct:.2f}%"
    )

    # Dollar Impact
    cvar_95_dollar = (
        total_investment *
        abs(cvar_95)
    )

    cvar_99_dollar = (
        total_investment *
        abs(cvar_99)
    )
    col3, col4 = st.columns(2)

    col3.metric(
        "95% Tail Loss ($)",
        f"${cvar_95_dollar:,.2f}"
    )

    col4.metric(
        "99% Tail Loss ($)",
        f"${cvar_99_dollar:,.2f}"
    )
    # Compare VaR vs CVaR
    comparison_df = pd.DataFrame({

        "Metric": [
            "95% VaR",
            "95% CVaR",
            "99% VaR",
            "99% CVaR"
        ],

        "Value (%)": [

            round(
                var_95_pct,
                2
            ),

            round(
                cvar_95_pct,
                2
            ),

            round(
                var_99_pct,
                2
            ),

            round(
                cvar_99_pct,
                2
            )
        ]
    })

    st.dataframe(
        comparison_df,
        width="stretch"
    )
    # Tail Risk Interpretation
    tail_gap = abs(
        cvar_95_pct
    ) - abs(
        var_95_pct
    )
    if tail_gap < 2:
        st.success(
            "🟢 Limited tail-risk exposure"
        )
    elif tail_gap < 5:
        st.warning(
            "🟡 Moderate tail-risk exposure"
        )
    else:
        st.error(
            "🔴 Significant tail-risk exposure"
        )
    # AI Interpretation
    st.info(
        f"""
        VaR estimates losses up to
        {abs(var_95_pct):.2f}% on
        95% of trading days.

        During extreme events,
        losses historically averaged
        {abs(cvar_95_pct):.2f}%,
        indicating the portfolio's
        tail-risk profile.
        """
    )
    # Tail Risk Score
    tail_risk_score = min(
        abs(cvar_95_pct),
        10
    )
    st.metric(
        "Tail Risk Score",
        f"{tail_risk_score:.1f}/10"
    )
    # AI Portfolio Advisor Integration
    if tail_risk_score > 7:
        recommendations.append(
            "Portfolio exhibits elevated tail risk during extreme market selloffs."
        )
    st.html(""" <hr style=" border: none; border-top: 3px solid orange; margin: 20px 0;"> """)
    
    # Risk Pyramid
    st.subheader(
        "Risk Pyramid", divider='blue'
    )
    risk_pyramid = pd.DataFrame({

        "Risk Layer": [
            #"Volatility",
            "VaR",
            "CVaR"
        ],

        "Score": [

            #round(
            #    annualized_volatility / 10,
            #    2
            #),

            round(
                abs(var_95_pct),
                2
            ),

            round(
                abs(cvar_95_pct),
                2
            )
        ]
    })

    st.dataframe(
        risk_pyramid,
        width="stretch"
    )
    st.html(""" <hr style=" border: none; border-top: 3px solid orange; margin: 20px 0;"> """)

    # Phase 9.5 : project starts looking like a genuine quantitative portfolio analytics platform.
    st.subheader(
        "📈 Efficient Frontier Optimizer", divider='blue'
    )
    # Build Return Matrix
    returns_df = pd.DataFrame()
    for coin in portfolio_coins:
        symbol = symbol_map[coin]
        try:
            hist = get_historical_price(
                symbol,
                "1y"
            )
            if isinstance(
                hist.columns,
                pd.MultiIndex
            ):
                hist.columns = (
                    hist.columns
                    .get_level_values(0)
                )
            returns_df[coin] = (
                hist["Close"]
                .pct_change()
            )
        except Exception:
            pass

    returns_df = (
        returns_df
        .dropna()
    )
    # Annualized Statistics
    mean_returns = (
        returns_df.mean()
        * 252
    )

    cov_matrix = (
        returns_df.cov()
        * 252
    )
    # Generate Random Portfolios
    num_portfolios = 500
    portfolio_returns_list = []
    portfolio_risks_list = []
    portfolio_sharpes_list = []
    portfolio_weights = []
    # Simulation Loop
    for _ in range(num_portfolios):
        weights = np.random.random(
            len(portfolio_coins)
        )

        weights = (
            weights /
            np.sum(weights)
        )
    portfolio_return = np.sum(
        mean_returns * weights
    )
    portfolio_risk = np.sqrt(
        np.dot(
            weights.T,

            np.dot(
                cov_matrix,
                weights
            )
        )
    )

    sharpe = (
        portfolio_return - 0.04
    ) / portfolio_risk

    portfolio_returns_list.append(
        portfolio_return
    )

    portfolio_risks_list.append(
        portfolio_risk
    )

    portfolio_sharpes_list.append(
        sharpe
    )

    portfolio_weights.append(
        weights
    )
    # Build DataFrame
    frontier_df = pd.DataFrame({

        "Return":
            portfolio_returns_list,

        "Risk":
            portfolio_risks_list,

        "Sharpe":
            portfolio_sharpes_list
    })
    # Find Optimal Portfolio
    optimal_idx = (
        frontier_df["Sharpe"]
        .idxmax()
    )
    optimal_portfolio = (
        frontier_df.loc[
            optimal_idx
        ]
    )
    optimal_weights = (
        portfolio_weights[
            optimal_idx
        ]
    )
    # Display Optimal Portfolio
    st.metric(
        "Best Sharpe Ratio",
        f"{optimal_portfolio['Sharpe']:.2f}"
    )

    st.metric(
        "Expected Return",
        f"{optimal_portfolio['Return']*100:.2f}%"
    )
    st.metric(
        "Expected Risk",
        f"{optimal_portfolio['Risk']*100:.2f}%"
    )
    # Allocation Table
    optimal_df = pd.DataFrame({

        "Coin":
            portfolio_coins,

        "Optimal Allocation %":

            [
                round(
                    w * 100,
                    1
                )

                for w in optimal_weights
            ]
    })
    st.dataframe(
        optimal_df,
        width="stretch"
    )
    # Efficient Frontier Chart
    fig_frontier = go.Figure()
    # random
    fig_frontier.add_trace(
        go.Scatter(

            x=frontier_df["Risk"] * 100,

            y=frontier_df["Return"] * 100,

            mode="markers",

            marker=dict(

                size=6,

                color=
                frontier_df["Sharpe"],

                colorbar=dict(
                    title="Sharpe"
                )
            ),

            name="Portfolios"
        )
    )
    # optimal
    fig_frontier.add_trace(
        go.Scatter(
            x=[
                optimal_portfolio["Risk"]
                * 100
            ],
            y=[
                optimal_portfolio["Return"]
                * 100
            ],
            mode="markers",
            marker=dict(
                size=15,
                symbol="star"
            ),
            name="Optimal"
        )
    )
    # layout
    fig_frontier.update_layout(
        title=
        "Efficient Frontier",
        xaxis_title=
        "Risk (%)",
        yaxis_title=
        "Expected Return (%)"
    )
    st.plotly_chart(
        fig_frontier,
        width="stretch"
    )
    # Lowest Risk Portfolio
    min_risk_idx = (
        frontier_df["Risk"]
        .idxmin()
    )
    min_risk_portfolio = (
        frontier_df.loc[
            min_risk_idx
        ]
    )
    st.metric(
        "Lowest Risk Portfolio",
        f"{min_risk_portfolio['Risk']*100:.2f}%"
    )
    # AI Recommendation
    st.info(
        f"""
        The optimizer suggests
        allocating capital toward
        the highest risk-adjusted
        return portfolio.

        Expected annual return:
        {optimal_portfolio['Return']*100:.2f}%

        Expected annual volatility:
        {optimal_portfolio['Risk']*100:.2f}%

        Sharpe Ratio:
        {optimal_portfolio['Sharpe']:.2f}
        """
    )
    st.html(""" <hr style=" border: none; border-top: 3px solid orange; margin: 20px 0;"> """)

    # Phase 9.6 – Portfolio Beta Analyzer (vs Bitcoin)
    st.subheader(
        "₿ Portfolio Beta Analyzer", divider='blue'
    )
    btc_hist = get_historical_price(
        "BTC-USD",
        "1y"
    )
    if isinstance(
        btc_hist.columns,
        pd.MultiIndex
    ):
        btc_hist.columns = (
            btc_hist.columns
            .get_level_values(0)
        )
    # BTC daily returns
        btc_returns = (
        btc_hist["Close"]
        .pct_change()
        .dropna()
        )
        portfolio_returns = (
            portfolio_values
            .pct_change()
            .dropna()
        )
        # Align Dates
        beta_df = pd.concat(
            [
                portfolio_returns,
                btc_returns
            ],
            axis=1,
            join="inner"
        )
        beta_df.columns = [
            "Portfolio",
            "BTC"
        ]
        # Calculate Covariance
        #covariance = np.cov(
        #    beta_df["Portfolio"],
        #    beta_df["BTC"]
        #)[0][1]

        # Calculate BTC Variance
        #btc_variance = np.var(
        #    beta_df["BTC"]
        #)
        # Calculate Beta
        #portfolio_beta = (
        #    covariance /
        #    btc_variance
        #)

        from scipy.stats import linregress

        beta, alpha, r_value, p_value, std_err = (
            linregress(
                beta_df["BTC"],
                beta_df["Portfolio"]
            )
        )        

        portfolio_beta = beta
        portfolio_alpha = alpha
        portfolio_r2 = r_value ** 2


        #st.metric(
        #    "Portfolio Beta",
        #    f"{portfolio_beta:.2f}"
        #)
        col1, col2, col3 = st.columns(3)
        col1.metric(
            "Portfolio Beta",
            f"{portfolio_beta:.2f}"
        )
        col2.metric(
            "Portfolio Alpha",
            f"{portfolio_alpha:.4f}"
        )
        col3.metric(
            "R²",
            f"{portfolio_r2:.2f}"
        )
        # This becomes very useful once you add more altcoins such as SOL, XRP, DOT, and ATOM.
        if portfolio_r2 > 0.8:
            st.info(
            "Portfolio is highly driven by Bitcoin."
        )
        elif portfolio_r2 > 0.5:
            st.info(
                "Portfolio has moderate Bitcoin dependence."
            )
        else:
            st.success(
            "Portfolio shows diversification away from Bitcoin."
        )

        if portfolio_beta < 0.8:
            st.success(
                "🟢 Portfolio is less volatile than Bitcoin"
            )
        elif portfolio_beta < 1.2:
            st.info(
                "🟡 Portfolio behaves similarly to Bitcoin"
            )
        elif portfolio_beta < 1.8:
            st.warning(
                "🟠 Portfolio is more aggressive than Bitcoin"
            )
        else:
            st.error(
                "🔴 Extremely high market sensitivity"
            )
        # Expected Move vs BTC
        btc_move = 10
        expected_portfolio_move = (
            portfolio_beta *
            btc_move
        )
        st.metric(
            "Expected Portfolio Move if BTC Moves 10%",
            f"{expected_portfolio_move:.1f}%"
        )
        # AI Insight
        st.info(
            f"""
            Portfolio beta is
            {portfolio_beta:.2f}.

            Historically the portfolio
            moves approximately
            {portfolio_beta:.2f}x
            the magnitude of Bitcoin.
            """
        )
        # Portfolio Classification
        if portfolio_beta < 0.7:
            profile = "Defensive"
        elif portfolio_beta < 1.2:
            profile = "Market Neutral"
        elif portfolio_beta < 1.8:
            profile = "Growth"
        else:
            profile = "Speculative"

        st.metric(
            "Portfolio Style",
            profile
        )
        # Compare Portfolio vs BTC Returns
        comparison_returns = pd.DataFrame({
            "Portfolio":
                portfolio_returns,
             "Bitcoin":
                btc_returns
        })
        # This creates a very nice visual of how closely the portfolio tracks Bitcoin.
        st.line_chart(
            comparison_returns
        )
    st.html(""" <hr style=" border: none; border-top: 3px solid orange; margin: 20px 0;"> """)


    # Phase 9.7 – Portfolio Alpha Analyzer
    # Alpha measures whether your portfolio is outperforming or underperforming relative to the return expected from its Beta
    st.subheader(
        "📈 Portfolio Alpha Analyzer", divider='blue'
    )
    st.metric(
        "Portfolio Alpha",
        f"{portfolio_alpha:.4f}"
    )
    # Convert to yearly alpha:
    annual_alpha = (
        portfolio_alpha * 252 * 100
    )
    st.metric(
        "Annualized Alpha",
        f"{annual_alpha:.2f}%"
    )
    if annual_alpha > 10:
        st.success(
            "🟢 Exceptional Outperformance"
        )
    elif annual_alpha > 5:
        st.success(
            "🟢 Strong Outperformance"
        )
    elif annual_alpha > 0:
        st.info(
            "🟡 Mild Outperformance"
        )
    elif annual_alpha > -5:
        st.warning(
            "🟠 Slight Underperformance"
        )
    else:
        st.error(
            "🔴 Significant Underperformance"
        )
    st.info(
        f"""
        Annualized Alpha is
        {annual_alpha:.2f}%.

        Positive alpha means the portfolio
        historically delivered returns above
        what would be expected based on its
        Bitcoin market exposure.
        """
    )
    if annual_alpha >= 15:
        alpha_grade = "A"
    elif annual_alpha >= 8:
        alpha_grade = "B"
    elif annual_alpha >= 0:
        alpha_grade = "C"
    elif annual_alpha >= -5:
        alpha_grade = "D"
    else:
        alpha_grade = "F"
    st.metric(
        "Alpha Grade",
        alpha_grade
    )

    # Alpha Gauge
    fig_alpha = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=annual_alpha,
            title={
                "text": "Annual Alpha %"
            },
            gauge={
                "axis": {
                    "range": [-20, 20]
                }
            }
        )
    )

    st.plotly_chart(
        fig_alpha,
        width="stretch"
    )
    # Combine Alpha + Beta : This is how institutional investors classify portfolios.
    if annual_alpha > 0 and portfolio_beta < 1:
        profile = "Efficient"
    elif annual_alpha > 0 and portfolio_beta >= 1:
        profile = "Aggressive Winner"
    elif annual_alpha < 0 and portfolio_beta > 1:
        profile = "Risk Without Reward"
    else:
        profile = "Defensive"
    st.metric(
        "Manager Style",
        profile
    )
    # Alpha Score (0–10)
    alpha_score = min(
        max(
            (annual_alpha + 10) / 3,
            0
        ),
        10
    )
    st.metric(
        "Alpha Score",
        f"{alpha_score:.1f}/10"
    )
    st.html(""" <hr style=" border: none; border-top: 3px solid orange; margin: 20px 0;"> """)

    # Phase 9.8 – Sortino Ratio Analyzer
    st.subheader(
        "📉 Sortino Ratio Analyzer"
    )
    #portfolio_returns = portfolio_series.pct_change().dropna()
    risk_free_rate = 0.04
    daily_rf = risk_free_rate / 252
    excess_returns = (
        portfolio_returns -
        daily_rf
    )
    downside_returns = excess_returns[
        excess_returns < 0
    ]
    #downside_deviation = (
    #    downside_returns.std()
    #)
    downside_deviation = np.sqrt(
        (downside_returns ** 2).mean()
    )
    # Protect against division by zero:
    if downside_deviation == 0:
        sortino_ratio = 0
    else:
        sortino_ratio = (
            excess_returns.mean()
            /
            downside_deviation
        ) * np.sqrt(252)
    st.metric(
        "Portfolio Sortino Ratio",
        f"{sortino_ratio:.2f}"
    )
    if sortino_ratio >= 3:
        st.success(
            "🟢 Exceptional Risk-Adjusted Performance"
        )
    elif sortino_ratio >= 2:
        st.success(
            "🟢 Strong Risk-Adjusted Performance"
        )
    elif sortino_ratio >= 1:
        st.info(
            "🟡 Acceptable Risk-Adjusted Performance"
        )
    elif sortino_ratio >= 0:
        st.warning(
            "🟠 Weak Risk-Adjusted Performance"
        )
    else:
        st.error(
            "🔴 Negative Risk-Adjusted Performance"
        )

    # Compare Sharpe vs Sortino
    comparison_df = pd.DataFrame(
        {
            "Metric": [
                "Sharpe Ratio",
                "Sortino Ratio"
            ],
            "Value": [
                portfolio_sharpe,
                sortino_ratio
            ]
        }
    )

    st.dataframe(
        comparison_df,
        width="stretch"
    )
    # Sortino Grade
    if sortino_ratio >= 3:
        sortino_grade = "A"
    elif sortino_ratio >= 2:
        sortino_grade = "B"
    elif sortino_ratio >= 1:
        sortino_grade = "C"
    elif sortino_ratio >= 0:
        sortino_grade = "D"
    else:
        sortino_grade = "F"
    st.metric(
        "Sortino Grade",
        sortino_grade
    )

    # Sortino Gauge
    fig_sortino = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=sortino_ratio,
            title={
                "text": "Sortino Ratio"
            },
            gauge={
                "axis": {
                    "range": [0, 5]
                }
            }
        )
    )

    st.plotly_chart(
        fig_sortino,
        width="stretch"
    )
    # AI Interpretation
    if sortino_ratio > portfolio_sharpe:
        st.info(
            "Portfolio upside volatility is helping performance. "
            "Sortino exceeds Sharpe."
        )
    elif sortino_ratio == portfolio_sharpe:
        st.info(
            "Upside and downside volatility are balanced."
        )
    else:
        st.warning(
            "Downside volatility is dominating returns."
        )
    st.html(""" <hr style=" border: none; border-top: 3px solid orange; margin: 20px 0;"> """)


    # Phase 9.9 – Portfolio Performance Attribution Engine
    st.subheader(
        "📊 Portfolio Performance Attribution",divider='blue'
    )
    # Build Coin Return Table, We'll use 1-year returns
    attribution_data = []
    for coin in portfolio_coins:
        symbol = symbol_map[coin]
        hist = get_historical_price(
            symbol,
            "1y"
        )

        if isinstance(
            hist.columns,
            pd.MultiIndex
        ):
            hist.columns = (
                hist.columns
                .get_level_values(0)
            )
        start_price = float(
            hist["Close"].iloc[0]
        )
        end_price = float(
            hist["Close"].iloc[-1]
        )
        annual_return = (
            (
                end_price -
                start_price
            )
            /
            start_price
        ) * 100
        
        attribution_data.append({

            "Coin":
                coin.upper(),

            "Allocation %":
                allocations[coin],

            "Annual Return %":
                round(
                    annual_return,
                    2
                )
        })
    attribution_df = pd.DataFrame(
        attribution_data
    )
    # Calculate Contribution
    attribution_df[
        "Contribution"
    ] = (
        attribution_df[
            "Allocation %"
        ]
        *
        attribution_df[
            "Annual Return %"
        ]
        /
        100
    )
    # Sort Best to Worst
    attribution_df = (
        attribution_df
        .sort_values(
            by="Contribution",
            ascending=False
        )
    )
    st.dataframe(
        attribution_df,
        width="stretch"
    )
    # Biggest Winner
    best_contributor = (
        attribution_df
        .iloc[0]
    )
    st.success(
        f"""
        🏆 Top Contributor:
        {best_contributor['Coin']}
        ({best_contributor['Contribution']:.2f})
        """
    )
    # Worst Contributor
    worst_contributor = (
        attribution_df
        .iloc[-1]
    )
    st.warning(
        f"""
        ⚠️ Lowest Contributor:
        {worst_contributor['Coin']}
        ({worst_contributor['Contribution']:.2f})
        """
    )
    # Contribution Chart
    fig_contrib = go.Figure(
        data=[
            go.Bar(
                x=attribution_df["Coin"],
                y=attribution_df[
                    "Contribution"
                ]
            )
        ]
    )

    fig_contrib.update_layout(
        title=
        "Performance Contribution"
    )

    st.plotly_chart(
        fig_contrib,
        width="stretch"
    )
    # Percentage Contribution
    total_contribution = (
        attribution_df[
            "Contribution"
        ].sum()
    )
    attribution_df[
        "Contribution %"
    ] = (
        attribution_df[
            "Contribution"
        ]
        /
        total_contribution
        *
        100
    )
    # Attribution Pie Chart
    fig_attr_pie = go.Figure(
        data=[
            go.Pie(
                labels=
                attribution_df["Coin"],
                values=
                attribution_df[
                    "Contribution %"
                ]
            )
        ]
    )

    st.plotly_chart(
        fig_attr_pie,
        width="stretch"
    )
    # AI Interpretation
    dominance = (
        attribution_df[
            "Contribution %"
        ]
        .max()
    )
    if dominance > 50:
        st.warning(
            "Portfolio performance depends heavily on a single asset."
        )
    elif dominance > 35:
        st.info(
            "Portfolio performance is moderately concentrated."
        )
    else:
        st.success(
            "Portfolio performance is well diversified."
        )
    # Contribution Score
    contribution_score = min(
        (
            100 -
            dominance
        ) / 10,
        10
    )
    st.metric(
        "Attribution Diversification Score",
        f"{contribution_score:.1f}/10"
    )
    st.html(""" <hr style=" border: none; border-top: 3px solid orange; margin: 20px 0;"> """)


    # Phase 9.10 – Portfolio Risk Attribution Engine
    # Which coin contributes the most risk to my portfolio?
    st.subheader(
        "⚠️ Portfolio Risk Attribution",divider='blue'
    )
    # Calculate Annualized Volatility Per Coin
    risk_data = []
    for coin in portfolio_coins:
        symbol = symbol_map[coin]
        hist = get_historical_price(
            symbol,
            "1y"
        )
        if isinstance(
            hist.columns,
            pd.MultiIndex
        ):
            hist.columns = (
                hist.columns
                .get_level_values(0)
            )

        returns = (
            hist["Close"]
            .pct_change()
            .dropna()
        )

        volatility = (
            returns.std()
            * np.sqrt(252)
            * 100
        )

        risk_data.append({
            "Coin":
                coin.upper(),
            "Allocation %":
                allocations[coin],
            "Volatility %":
                round(
                    volatility,
                    2
                )
        })
        # Build DataFrame
        risk_df = pd.DataFrame(
            risk_data
        )
        risk_df[
            "Risk Contribution"
        ] = (
            risk_df[
                "Allocation %"
            ]
            *
            risk_df[
                "Volatility %"
            ]
            /
            100
        )
        # Sort Highest Risk First
        risk_df = (
            risk_df
            .sort_values(
                by="Risk Contribution",
                ascending=False
            )
        )
        st.dataframe(
            risk_df,
            width="stretch"
        )
        largest_risk = (
            risk_df
            .iloc[0]
        )
        st.warning(
            f"""
            ⚠️ Largest Risk Contributor:
            {largest_risk['Coin']}
            ({largest_risk['Risk Contribution']:.2f})
            """
        )
        lowest_risk = (
            risk_df
            .iloc[-1]
        )
        st.success(
            f"""
            🟢 Lowest Risk Contributor:
            {lowest_risk['Coin']}
            ({lowest_risk['Risk Contribution']:.2f})
            """
        )
        # Risk Contribution %
        total_risk = (
            risk_df[
                "Risk Contribution"
            ].sum()
        )
        risk_df[
            "Risk Contribution %"
        ] = (
            risk_df[
                "Risk Contribution"
            ]
            /
            total_risk
            *
             100
        )
        # Risk Pie Chart
        fig_risk_attr = go.Figure(
            data=[
                go.Pie(
                    labels=
                    risk_df["Coin"],
                    values=
                    risk_df[
                        "Risk Contribution %"
                    ]
                )
            ]
        )

        st.plotly_chart(
            fig_risk_attr,
            width="stretch"
        )
        # Risk Bar Chart
        fig_risk_bar = go.Figure(
            data=[
                go.Bar(
                    x=risk_df["Coin"],
                    y=risk_df[
                        "Risk Contribution"
                    ]
                )
            ]
        )

        fig_risk_bar.update_layout(
            title=
            "Risk Contribution by Asset"
        )

        st.plotly_chart(
            fig_risk_bar,
            width="stretch"
        )
        # AI Interpretation
        risk_dominance = (
            risk_df[
                "Risk Contribution %"
            ]
            .max()
        )
        if risk_dominance > 50:
            st.error(
                "Portfolio risk is heavily concentrated in one asset."
            )
        elif risk_dominance > 35:
            st.warning(
                "Portfolio risk is moderately concentrated."
            )
        else:
            st.success(
                "Portfolio risk is well diversified."
            )
        # Risk Diversification Score
        risk_div_score = min(
            (
                100 -
                risk_dominance
            ) / 10,
            10
        )
        st.metric(
            "Risk Diversification Score",
            f"{risk_div_score:.1f}/10"
        )
        # Return vs Risk Comparison
        comparison_df = pd.merge(
            attribution_df[
                [
                    "Coin",
                    "Contribution %"
                ]
            ],
            risk_df[
                [
                    "Coin",
                    "Risk Contribution %"
                ]
            ],
            on="Coin"
        )
        st.dataframe(
            comparison_df,
            width="stretch"
        )
        # Risk Efficiency Score
        comparison_df[
            "Risk Efficiency"
        ] = (
            comparison_df[
                "Contribution %"
            ]
            /
            comparison_df[
                "Risk Contribution %"
            ]
        )
        st.html(""" <hr style=" border: none; border-top: 3px solid orange; margin: 20px 0;"> """)
        

    # Phase 10.1 – AI Crypto Market Forecast Engine    
    st.subheader(
        "🔮 AI Crypto Market Forecast"
    )
    forecast_score = 0
    if regime == "Bull Market":
        forecast_score += 4
    elif regime == "Sideways Market":
        forecast_score += 2
    else:
        forecast_score += 0
    # Sharpe Component
    if portfolio_sharpe > 2:
        forecast_score += 2
    elif portfolio_sharpe > 1:
        forecast_score += 1
    # Risk Component
    if weighted_risk_score < 4:
        forecast_score += 2
    elif weighted_risk_score < 6:
        forecast_score += 1
    # Opportunity Component
    if weighted_opportunity_score > 7:
        forecast_score += 2
    elif weighted_opportunity_score > 5:
        forecast_score += 1
    # Convert to Probabilities
    bullish_prob = min(
        forecast_score * 10,
        90
    )
    bearish_prob = max(
        100 - bullish_prob - 10,
        5
    )
    neutral_prob = (
        100
        - bullish_prob
        - bearish_prob
    )
    col1, col2, col3 = st.columns(3)
    col1.metric(
        "🟢 Bullish %",
        f"{bullish_prob}%"
    )
    col2.metric(
        "🟡 Neutral %",
        f"{neutral_prob}%"
    )
    col3.metric(
        "🔴 Bearish %",
        f"{bearish_prob}%"
    )
    # AI Forecast Message
    if bullish_prob >= 70:
        st.success(
            "AI Forecast: Strong Bullish Outlook"
        )
    elif bullish_prob >= 50:
        st.info(
            "AI Forecast: Moderately Bullish"
        )
    elif bullish_prob >= 35:
        st.warning(
            "AI Forecast: Neutral Market"
        )
    else:
        st.error(
            "AI Forecast: Elevated Bearish Risk"
        )
    # Forecast Gauge
    fig_forecast = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=bullish_prob,
            title={
                "text":
                "Bullish Probability"
            },
            gauge={
                "axis": {
                    "range": [0, 100]
                }
            }
        )
    )

    st.plotly_chart(
        fig_forecast,
        width="stretch"
    )
    st.html(""" <hr style=" border: none; border-top: 3px solid orange; margin: 20px 0;"> """)

    # Phase 10.2 – Trend Strength Analyzer
    st.subheader(
        "📈 Trend Strength Analyzer",divider='blue'
    )
    trend_score = 0
    if regime == "Bull Market":
        trend_score += 4
    elif regime == "Sideways Market":
        trend_score += 2
    else:
        trend_score += 0
    
    if portfolio_sharpe > 2:
        trend_score += 2
    elif portfolio_sharpe > 1:
        trend_score += 1
    
    if weighted_opportunity_score > 7:
        trend_score += 2
    elif weighted_opportunity_score > 5:
        trend_score += 1
    # Risk :Lower risk = stronger trend.
    if weighted_risk_score < 4:
        trend_score += 2
    elif weighted_risk_score < 6:
        trend_score += 1
    # Cap at 10
    trend_score = min(
        trend_score,
        10
    )
    st.metric(
        "Trend Strength",
        f"{trend_score}/10"
    )
    if trend_score >= 8:
        st.success(
            "🚀 Strong Uptrend"
        )
    elif trend_score >= 6:
        st.info(
            "📈 Healthy Uptrend"
        )
    elif trend_score >= 4:
        st.warning(
            "⚖️ Sideways Trend"
        )
    else:
        st.error(
            "📉 Weak Trend"
        )
    fig_trend = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=trend_score,
            title={
                "text":
                "Trend Strength"
            },
            gauge={
                "axis": {
                    "range": [0, 10]
                }
            }
        )
    )

    st.plotly_chart(
        fig_trend,
        width="stretch"
    )
    # ATH Recovery Component
    weighted_drawdown = (
        portfolio_df["Drawdown %"]
        * portfolio_df["Allocation %"]
        / 100
    ).sum()

    portfolio_ath_progress = (
        100 - abs(weighted_drawdown)
    ) / 100

    if portfolio_ath_progress > 0.8:
        trend_score += 1
    elif portfolio_ath_progress > 0.6:
        trend_score += 0.5

    if trend_score >= 8:
        st.success(
            "Trend remains exceptionally strong with favorable momentum and risk conditions."
        )
    elif trend_score >= 6:
        st.info(
            "Trend is positive but requires monitoring for momentum continuation."
        )
    elif trend_score >= 4:
        st.warning(
            "Market is currently consolidating."
        )
    else:
        st.error(
            "Trend conditions remain weak and defensive positioning may be warranted."
        )

    trend_confidence = round(
        (
            bullish_prob
            *
            trend_score
        )
        / 10,
        1
    )
    st.metric(
        "Trend Confidence",
        f"{trend_confidence}%"
    )



    st.html(""" <hr style=" border: none; border-top: 3px solid orange; margin: 20px 0;"> """)


    #st.html(""" <hr style=" border: none; border-top: 3px solid crimson; margin: 20px 0;"> """)
    st.html(""" <hr style=" border: none; border-top: 3px solid orange; margin: 20px 0;"> """)
    # Phase 8.9 – Portfolio Opportunity Scanner
    st.subheader(
        "🎯 Portfolio Opportunity Scanner", divider="blue"
    )
    scanner_data = []
    for coin in portfolio_coins:
        result = all_coin_data[coin]

        scanner_data.append({

            "Coin":
                result["name"],

            "Investment Score":
                result["investment_score"],

            "Opportunity Score":
                result["opportunity_score"],

            "Risk Score":
                result["risk_score"],

            "Valuation Score":
                result["valuation_score"]
        })

    scanner_df = pd.DataFrame(
        scanner_data
    )
    # Find Leaders & Laggards
    best_coin = scanner_df.loc[
        scanner_df[
            "Investment Score"
        ].idxmax()
    ]

    worst_coin = scanner_df.loc[
        scanner_df[
            "Investment Score"
        ].idxmin()
    ]

    highest_opportunity = scanner_df.loc[
        scanner_df[
            "Opportunity Score"
        ].idxmax()
    ]

    lowest_risk = scanner_df.loc[
        scanner_df[
            "Risk Score"
        ].idxmin()
    ]

    highest_risk = scanner_df.loc[
        scanner_df[
            "Risk Score"
        ].idxmax()
    ]

    best_valuation = scanner_df.loc[
        scanner_df[
            "Valuation Score"
        ].idxmax()
    ]

    # Display Metrics
    c1, c2, c3 = st.columns(3)

    c1.metric(
        "🏆 Best Coin",
        best_coin["Coin"]
    )

    c2.metric(
        "🚀 Highest Opportunity",
        highest_opportunity["Coin"]
    )

    c3.metric(
        "💎 Best Valuation",
        best_valuation["Coin"]
    )

    c4, c5, c6 = st.columns(3)

    c4.metric(
        "🛡 Lowest Risk",
        lowest_risk["Coin"]
    )

    c5.metric(
        "⚠ Highest Risk",
        highest_risk["Coin"]
    )

    c6.metric(
        "📉 Weakest Coin",
        worst_coin["Coin"]
    )

    # AI Interpretation
    st.subheader(
        "🤖 Opportunity Insights", divider="blue"
    )

    st.info(
        f"""
        Strongest holding: {best_coin['Coin']}
        Highest upside candidate: {highest_opportunity['Coin']}
        Most attractively valued: {best_valuation['Coin']}
        Lowest-risk asset: {lowest_risk['Coin']}
        Highest-risk asset: {highest_risk['Coin']}
        """
    )
    scanner_df = scanner_df.sort_values(
        by="Opportunity Score",
        ascending=False
    )
    st.dataframe(
        scanner_df,
        width="stretch"
    )

    # Phase 8.10 – AI Portfolio Report Generator
    st.subheader(
        "📋 AI Portfolio Report Generator", divider="blue"
    )
    if weighted_risk_score < 3:
        portfolio_risk_profile = (
            "Low Risk"
        )
    elif weighted_risk_score < 6:
        portfolio_risk_profile = (
            "Moderate Risk"
        )
    else:
        portfolio_risk_profile = (
            "High Risk"
        )
    # Diversification Assessment
    if avg_corr is not None:
        if avg_corr < 0.40:

            diversification_assessment = (
                "Excellent"
            )
        elif avg_corr < 0.70:

            diversification_assessment = (
                "Good"
            )
        else:

            diversification_assessment = (
                "Weak"
            )
    else:

        diversification_assessment = (
            "N/A"
        )

    # Stress-Test Assessment
    if survival_score >= 8:
        resilience = (
            "Very Strong"
        )
    elif survival_score >= 6:

        resilience = (
            "Strong"
        )
    elif survival_score >= 4:

        resilience = (
            "Average"
        )
    else:

        resilience = (
            "Weak"
        )
    # Overall Verdict Logic
    if (
        grade == "A"
        and
        portfolio_sharpe > 1
        and
        risk_alert_score <= 2
    ):

        final_verdict = (
            "Excellent long-term portfolio with strong risk-adjusted performance."
        )
    elif grade in ["A", "B"]:
        final_verdict = (
            "Healthy portfolio with balanced growth and risk characteristics."
        )
    elif grade == "C":
        final_verdict = (
            "Portfolio is acceptable but has room for improvement."
        )
    else:
        final_verdict = (
            "Portfolio risk is elevated and requires attention."
        )
    # Build Report Text
    # annualized_volatility not defined
    #Volatility:
    #    {annualized_volatility:.2f}%
    report = f"""
        AI PORTFOLIO REPORT

        Portfolio Grade: {grade}

        Market Regime:
        {regime}

        Risk Profile:
        {portfolio_risk_profile}

        Portfolio Health:
        {health_score}/10

        Sharpe Ratio:
        {portfolio_sharpe:.2f}


        Diversification:
        {diversification_assessment}

        Stress Test Resilience:
        {resilience}

        Risk Alerts:
        {risk_alert_score}

        Best Holding:
        {best_coin['Coin']}

        Highest Opportunity:
        {highest_opportunity['Coin']}

        Highest Risk Asset:
        {highest_risk['Coin']}

        Final Verdict:
        {final_verdict}
    """
    # Color-Coded Verdict
    if grade == "A":
        st.success(
            final_verdict
        )
    elif grade == "B":
        st.info(
            final_verdict
        )
    elif grade == "C":
        st.warning(
            final_verdict
        )
    else:
        st.error(
            final_verdict
        )
    # Report Summary Metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(
        "Grade",
        grade
    )
    col2.metric(
        "Sharpe",
        f"{portfolio_sharpe:.2f}"
    )
    col3.metric(
        "Alerts",
        risk_alert_score
    )
    col4.metric(
        "Health",
        f"{health_score}/10"
    )
    # AI Recommendations
    recommendations = []
    if weighted_risk_score > 6:
        recommendations.append(
            "Reduce exposure to high-risk assets."
        )
    if avg_corr is not None and avg_corr > 0.75:
        recommendations.append(
            "Improve diversification."
        )
    if portfolio_sharpe < 1:
        recommendations.append(
            "Improve risk-adjusted returns."
        )
    if survival_score < 5:
        recommendations.append(
            "Strengthen downside protection."
        )

    if recommendations:
        st.subheader(
            "🎯 AI Recommendations", divider="blue"
        )

        for rec in recommendations:
            st.info(rec)
    else:
        st.success(
            "Portfolio currently shows no major weaknesses."
        )
    

    st.text_area(
        "Generated Report",
        report,
        height=400
    )



    best_coin = portfolio_df.loc[
        portfolio_df[
            "Investment Score"
        ].idxmax()
    ]
    advice.append(
        f"Highest conviction holding: {best_coin['Coin']}."
    )

    st.success(
        f"🏆 Strongest Holding: "
        f"{best_coin['Coin']}"
    )

    weakest_coin = portfolio_df.loc[
        portfolio_df[
            "Investment Score"
        ].idxmin()
    ]
    advice.append(
        f"Review position sizing of {weakest_coin['Coin']}."
    )

    st.warning(
        f"⚠️ Weakest Holding: "
        f"{weakest_coin['Coin']}"
    )

    

    fig_risk = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=weighted_risk_score,
            title={
                "text":
                "Portfolio Risk"
            },
            gauge={
                "axis": {
                    "range": [0, 10]
                }
            }
        )
    )

    st.plotly_chart(
        fig_risk,
        width="stretch"
    )    

    st.subheader(
        "🤖 Portfolio Optimizer", divider="blue"
    )

    risk_profile = st.selectbox(
        "Risk Profile",
        [
            "Conservative",
            "Balanced",
            "Aggressive"
        ]
    )
    

    if risk_profile == "Conservative":
        st.info(
            "Focuses on lower-risk coins and capital preservation."
        )
    elif risk_profile == "Balanced":
        st.info(
            "Balances risk and upside potential."
        )
    else:
        st.info(
            "Prioritizes growth and opportunity."
        )


    optimizer_data = []

    for coin in portfolio_coins:
        result = all_coin_data[coin]
        if risk_profile == "Conservative":

            optimization_score = round(
                (
                    result["investment_score"] * 0.40 +
                    result["opportunity_score"] * 0.20 +
                    (10 - result["risk_score"]) * 0.40
                ),
                2
            )

        elif risk_profile == "Balanced":

            optimization_score = round(
                (
                    result["investment_score"] * 0.50 +
                    result["opportunity_score"] * 0.30 +
                    (10 - result["risk_score"]) * 0.20
                ),
                2
            )

        else:  # Aggressive

            optimization_score = round(
                (
                    result["investment_score"] * 0.40 +
                    result["opportunity_score"] * 0.50 +
                    (10 - result["risk_score"]) * 0.10
                ),
                2
            )

        optimizer_data.append({
            "Coin": result["name"],
            "Optimization Score": optimization_score,
            "Risk Score": result["risk_score"]
        })

    

    optimizer_df = pd.DataFrame(
        optimizer_data
    )
    # Create allocations first
    total_score = optimizer_df[
        "Optimization Score"
    ].sum()

    optimizer_df[
        "Suggested Allocation %"
    ] = round(
        optimizer_df["Optimization Score"]
        / total_score
        * 100,
        1
    )

    # Then calculate portfolio risk
    portfolio_risk = round(
        (
            optimizer_df["Risk Score"]
            *
            optimizer_df["Suggested Allocation %"]
            / 100
        ).sum(),
        2
    )

    st.metric(
        "Portfolio Risk Score",
        f"{portfolio_risk}/10"
    )

    if portfolio_risk < 3:
        st.success(
            "🟢 Low Risk Portfolio"
        )
    elif portfolio_risk < 6:
        st.warning(
            "🟡 Moderate Risk Portfolio"
        )
    else:
        st.error(
            "🔴 High Risk Portfolio"
        )    


    total_score = optimizer_df[
        "Optimization Score"
    ].sum()
    optimizer_df[
        "Suggested Allocation %"
    ] = round(

        optimizer_df[
            "Optimization Score"
        ]
        /
        total_score
        * 100,

        1
    )

    st.dataframe(
        optimizer_df,
        width="stretch"
    )

    optimizer_df[
        "Suggested Investment $"
    ] = round(
        total_investment
        *
        optimizer_df[
            "Suggested Allocation %"
        ]
        / 100,
        2
    )

    # Calculate difference phase 7.3
    current_alloc_map = {
        result["name"]: allocations[coin]
        for coin, result in [
            (c, all_coin_data[c])
            for c in portfolio_coins
        ]
    }

    optimizer_df["Current Allocation %"] = (
        optimizer_df["Coin"]
        .map(current_alloc_map)
    )

    optimizer_df["Difference %"] = round(
        optimizer_df["Suggested Allocation %"]
        -
        optimizer_df["Current Allocation %"],
        1
    )
    # Generate Action
    def rebalance_action(diff):
        if diff > 5:
            return "Buy More"
        elif diff < -5:
            return "Reduce"
        else:
            return "Hold"

    # Create Recommendation Column
    optimizer_df["Action"] = (
        optimizer_df["Difference %"]
        .apply(rebalance_action)
    )

    # Show Table
    st.subheader(
        "🔄 Rebalancing Advisor", divider="blue"
    )

    st.dataframe(
        optimizer_df[
            [
                "Coin",
                "Current Allocation %",
                "Suggested Allocation %",
                "Difference %",
                "Action"
            ]
        ],
        width="stretch"
    )

    # Add Projection Section
    st.subheader(
        "📈 Future Portfolio Projection", divider="blue"
    )
    # Time Horizon
    years = st.slider(
        "Investment Horizon (Years)",
        min_value=1,
        max_value=10,
        value=5
    )
    # Scenario Growth Rates
    bull_cagr = st.slider(
        "Bull Market CAGR %",
        10,
        100,
        40
    )

    base_cagr = st.slider(
        "Base Market CAGR %",
        0,
        50,
        20
    )

    bear_cagr = st.slider(
        "Bear Market CAGR %",
        -20,
        20,
        5
    )
    
    # Projection Function
    def future_value(
        principal,
        annual_return,
        years
    ):

        return (
            principal *
            ((1 + annual_return / 100) ** years)
        )

    # Calculate Scenarios
    bear_value = future_value(
        total_investment,
        bear_cagr,
        years
    )

    base_value = future_value(
        total_investment,
        base_cagr,
        years
    )

    bull_value = future_value(
        total_investment,
        bull_cagr,
        years
    )

    # Display Metrics
    col1, col2, col3 = st.columns(3)

    col1.metric(
        "🐻 Bear Case",
        f"${bear_value:,.0f}"
    )

    col2.metric(
        "⚖️ Base Case",
        f"${base_value:,.0f}"
    )

    col3.metric(
        "🚀 Bull Case",
        f"${bull_value:,.0f}"
    )

    # Create Projection Table
    projection_df = pd.DataFrame({

        "Scenario": [
            "Bear",
            "Base",
            "Bull"
        ],

        "Annual Return %": [
            bear_cagr,
            base_cagr,
            bull_cagr
        ],

        "Projected Value $": [
            round(bear_value, 2),
            round(base_value, 2),
            round(bull_value, 2)
        ]
    })

    st.dataframe(
        projection_df,
        width="stretch"
    )

    # Add Bar Chart
    fig_projection = go.Figure()

    fig_projection.add_bar(
        x=projection_df["Scenario"],
        y=projection_df["Projected Value $"]
    )

    fig_projection.update_layout(
        title="Future Portfolio Value"
    )

    st.plotly_chart(
        fig_projection,
        width="stretch"
    )

    # New Section : Monte Carlo Portfolio Simulatio
    st.subheader(
        "🎲 Monte Carlo Portfolio Simulation", divider="blue"
    )
    # Simulation Inputs
    simulation_count = st.slider(
        "Number of Simulations",
        min_value=100,
        max_value=5000,
        value=1000,
        step=100
    )

    simulation_years = st.slider(
        "Simulation Horizon (Years)",
        min_value=1,
        max_value=10,
        value=5
    )

    # Assumptions, For Phase 1 of Monte Carlo: Crypto is extremely volatile, so 50% annual volatility is reasonable, 
    # Later we'll make this dynamic
    expected_return = 20
    volatility = 50

    # Simulation Engine
    simulation_results = []
    # To avoid unrealistic negative returns below -100%,
    # -95 prevents the simulation from producing mathematically impossible outcomes where a portfolio becomes negative

    for _ in range(simulation_count):
        value = total_investment

        for _ in range(simulation_years):
            annual_return = max(
                np.random.normal(
                    expected_return,
                    volatility
                ),
                -95
            )
            value *= (
                1 +
                annual_return / 100
            )
        simulation_results.append(value)

    # Convert to Array
    simulation_results = np.array(
        simulation_results
    )

    # Key Statistics
    best_case = simulation_results.max()
    worst_case = simulation_results.min()
    median_case = np.median(
        simulation_results
    )
    average_case = simulation_results.mean()

    # Profit Probability
    profit_probability = (
        (
            simulation_results >
            total_investment
        ).mean()
    ) * 100

    # Double Money Probability
    double_probability = (
        (
            simulation_results >
            total_investment * 2
        ).mean()
    ) * 100

    # Display Metrics
    col1, col2 = st.columns(2)

    col1.metric(
        "Best Case",
        f"${best_case:,.0f}"
    )

    col2.metric(
        "Worst Case",
        f"${worst_case:,.0f}"
    )

    col3, col4 = st.columns(2)

    col3.metric(
        "Median Outcome",
        f"${median_case:,.0f}"
    )

    col4.metric(
        "Average Outcome",
        f"${average_case:,.0f}"
    )

    # Probability Metrics
    col5, col6 = st.columns(2)

    col5.metric(
        "Chance of Profit",
        f"{profit_probability:.1f}%"
    )

    col6.metric(
        "Chance of 2x",
        f"{double_probability:.1f}%"
    )

    # Histogram Chart
    fig_mc = go.Figure()

    fig_mc.add_histogram(
        x=simulation_results,
        nbinsx=40
    )

    fig_mc.update_layout(
        title="Monte Carlo Distribution of Future Portfolio Value",
        xaxis_title="Portfolio Value ($)",
        yaxis_title="Frequency"
    )

    st.plotly_chart(
        fig_mc,
        width="stretch"
    )

    # Investment Verdict
    if profit_probability > 80:
        st.success(
            "🟢 Strong Probability of Growth"
        )
    elif profit_probability > 60:
        st.info(
            "🟡 Moderate Growth Potential"
        )
    else:
        st.warning(
            "🔴 Significant Downside Risk"
        )


    # New Section : Portfolio Backtesting Engine
    st.subheader(
        "📜 Portfolio Backtesting Engine", divider="blue"
    )
    # Select Backtest Period
    backtest_period = st.selectbox(
        "Backtest Period",
        ["1y", "2y", "5y"]
    )
    # Create Backtest Data
    backtest_data = []
    # Fetch Historical Prices
    for coin in portfolio_coins:

        symbol = symbol_map[coin]

        hist = get_historical_price(
            symbol,
            backtest_period
        )

        if isinstance(
            hist.columns,
            pd.MultiIndex
        ):
            hist.columns = (
                hist.columns.get_level_values(0)
            )

        start_price = float(
            hist["Close"].iloc[0]
        )

        end_price = float(
            hist["Close"].iloc[-1]
        )

        allocation = allocations[coin]

        invested_amount = (
            total_investment *
            allocation / 100
        )

        units = (
            invested_amount /
            start_price
        )

        current_value = (
            units *
            end_price
        )

        backtest_data.append({

            "Coin":
                all_coin_data[coin]["name"],

            "Start Price":
                round(start_price, 2),

            "End Price":
                round(end_price, 2),

            "Investment $":
                round(invested_amount, 2),

            "Current Value $":
                round(current_value, 2)
        })

    # DataFrame
    backtest_df = pd.DataFrame(
        backtest_data
    )
    st.dataframe(
        backtest_df,
        width="stretch"
    )

    # Portfolio Performance
    portfolio_initial = (
        backtest_df["Investment $"]
        .sum()
    )

    portfolio_current = (
        backtest_df["Current Value $"]
        .sum()
    )

    portfolio_profit = (
        portfolio_current
        -
        portfolio_initial
    )

    portfolio_return = (
        portfolio_profit
        /
        portfolio_initial
        * 100
    )

    # Display Metrics
    col1, col2 = st.columns(2)

    col1.metric(
        "Initial Portfolio",
        f"${portfolio_initial:,.0f}"
    )

    col2.metric(
        "Current Portfolio",
        f"${portfolio_current:,.0f}"
    )

    col3, col4 = st.columns(2)

    col3.metric(
        "Profit / Loss",
        f"${portfolio_profit:,.0f}"
    )

    col4.metric(
        "Return %",
        f"{portfolio_return:.1f}%"
    )

    # Performance Verdict
    if portfolio_return > 100:

        st.success(
            "🚀 Portfolio Doubled"
        )

    elif portfolio_return > 25:

        st.success(
            "🟢 Strong Historical Performance"
        )

    elif portfolio_return > 0:

        st.info(
            "🟡 Positive Performance"
        )

    else:

        st.error(
            "🔴 Negative Performance"
    )

    # Coin Winners and Losers
    backtest_df["Return %"] = round(

        (
            backtest_df["Current Value $"]
            -
            backtest_df["Investment $"]
        )

        /

        backtest_df["Investment $"]

        * 100,

        1
    )

    # Largest winner:
    best_coin = backtest_df.loc[
        backtest_df["Return %"]
        .idxmax()
    ]

    st.success(
        f"🏆 Best Performer: "
        f"{best_coin['Coin']} "
        f"({best_coin['Return %']}%)"
    )

    # Largest loser:
    worst_coin = backtest_df.loc[
        backtest_df["Return %"]
        .idxmin()
    ]

    st.warning(
        f"⚠️ Worst Performer: "
        f"{worst_coin['Coin']} "
        f"({worst_coin['Return %']}%)"
    )

    # Backtest Visualization
    fig_backtest = go.Figure()

    fig_backtest.add_bar(
        x=backtest_df["Coin"],
        y=backtest_df["Return %"]
    )

    fig_backtest.update_layout(
        title="Historical Portfolio Returns"
    )

    st.plotly_chart(
        fig_backtest,
        width="stretch"
    )


    # New Section : DCA Simulator
    st.subheader(
        "💰 DCA Simulator", divider="blue"
    )
    # input
    monthly_investment = st.number_input(
        "Monthly Investment ($)",
        min_value=50,
        value=500,
        step=50
    )

    dca_period = st.selectbox(
        "DCA Period",
        ["1y", "2y", "5y"]
    )

    # Create Results Container
    dca_data = []

    # Loop Through Portfolio Coins
    for coin in portfolio_coins:

        symbol = symbol_map[coin]

        hist = get_historical_price(
            symbol,
            dca_period
        )

        if isinstance(
            hist.columns,
            pd.MultiIndex
        ):
            hist.columns = (
                hist.columns.get_level_values(0)
            )
    # Monthly Allocation
    allocation_pct = allocations[coin]

    monthly_coin_investment = (
        monthly_investment *
        allocation_pct / 100
    )

    # Create Monthly Purchase Dates
    #purchase_dates = hist.index[::30] # below code is more accurate
    monthly_prices = (
        hist["Close"]
        .resample("M")
        .last()
    )
    purchase_dates = monthly_prices.index

    # Accumulate Coin Units
    total_units = 0
    total_invested = 0

    for date in purchase_dates:

        try:

            price = float(
                monthly_prices.loc[date]
            )

            units_bought = (
                monthly_coin_investment /
                price
            )

            total_units += units_bought

            total_invested += (
                monthly_coin_investment
            )

        except Exception:

            pass

    # Current Value
    current_price = float(
        hist["Close"].iloc[-1]
    )

    current_value = (
        total_units *
        current_price
    )

    # Store Results
    dca_data.append({

        "Coin":
            all_coin_data[coin]["name"],

        "Invested $":
            round(total_invested, 2),

        "Current Value $":
            round(current_value, 2)
    })


    # DataFrame
    dca_df = pd.DataFrame(
        dca_data
    )
    st.dataframe(
        dca_df,
        width="stretch"
    )

    # Portfolio Metrics
    total_dca_invested = (
        dca_df["Invested $"]
        .sum()
    )

    total_dca_value = (
        dca_df["Current Value $"]
        .sum()
    )

    dca_profit = (
        total_dca_value
        -
        total_dca_invested
    )

    dca_return = (
        dca_profit
        /
        total_dca_invested
        * 100
    )

    # Display Metrics
    col1, col2 = st.columns(2)

    col1.metric(
        "Total Invested",
        f"${total_dca_invested:,.0f}"
    )

    col2.metric(
        "Current Value",
        f"${total_dca_value:,.0f}"
    )

    col3, col4 = st.columns(2)

    col3.metric(
        "Profit",
        f"${dca_profit:,.0f}"
    )

    col4.metric(
        "Return %",
        f"{dca_return:.1f}%"
    )

    # DCA Verdict
    if dca_return > 100:
        st.success(
            "🚀 Exceptional DCA Performance"
        )
    elif dca_return > 25:

        st.success(
            "🟢 Strong DCA Returns"
        )
    elif dca_return > 0:
        st.info(
            "🟡 Positive DCA Returns"
        )
    else:
        st.warning(
            "🔴 DCA Currently Underwater"
        )

    # Best DCA Performer
    dca_df["Return %"] = round(
        (
            dca_df["Current Value $"]
            -
            dca_df["Invested $"]
        )
        /
        dca_df["Invested $"]
        * 100,
        1
    )

    # Best performer:
    best_dca = dca_df.loc[
        dca_df["Return %"]
        .idxmax()
    ]

    st.success(
        f"🏆 Best DCA Coin: "
        f"{best_dca['Coin']} "
        f"({best_dca['Return %']}%)"
    )

    # Visualization
    fig_dca = go.Figure()

    fig_dca.add_bar(
        x=dca_df["Coin"],
        y=dca_df["Return %"]
    )

    fig_dca.update_layout(
        title="DCA Returns by Coin"
    )

    st.plotly_chart(
        fig_dca,
        width="stretch"
    )

    # Phase 7.7.1 — DCA (Dollar-Cost Averaging) vs Lump Sum Comparison; New Section - DCA vs Lump Sum
    st.subheader(
        "⚔️ DCA vs Lump Sum", divider="blue"
    )
    # Calculate Lump Sum Result
    lump_sum_investment = (
        monthly_investment *
        len(purchase_dates)
    )
    # Buy On First Day
    start_price = float(
        hist["Close"].iloc[0]
    )

    lump_sum_units = (
        lump_sum_investment /
        start_price
    )
    # Current Value
    end_price = float(
        hist["Close"].iloc[-1]
    )

    lump_sum_value = (
        lump_sum_units *
        end_price
    )
    # Calculate Returns ; DCA return
    dca_return_pct = (
        (
            current_value -
            total_invested
        )
        /
        total_invested
    ) * 100
    # Lump sum return
    lump_sum_return_pct = (
        (
            lump_sum_value -
            lump_sum_investment
        )
        /
        lump_sum_investment
    ) * 100
    # Show Metrics
    col1, col2 = st.columns(2)

    col1.metric(
        "DCA Portfolio Value",
        f"${current_value:,.2f}",
        f"{dca_return_pct:.1f}%"
    )

    col2.metric(
        "Lump Sum Value",
        f"${lump_sum_value:,.2f}",
        f"{lump_sum_return_pct:.1f}%"
    )
    # Determine Winner
    if current_value > lump_sum_value:

        difference = (
            current_value -
            lump_sum_value
        )

        st.success(
            f"🏆 DCA Outperformed by "
            f"${difference:,.2f}"
        )

    else:

        difference = (
            lump_sum_value -
            current_value
        )

        st.info(
            f"🚀 Lump Sum Outperformed by "
            f"${difference:,.2f}"
        )

    # Comparison Chart
    comparison_df = pd.DataFrame(
        {
            "Strategy": [
                "DCA",
                "Lump Sum"
            ],
            "Portfolio Value": [
                current_value,
                lump_sum_value
            ]
        }
    )

    fig_compare = go.Figure(
        data=[
            go.Bar(
                x=comparison_df["Strategy"],
                y=comparison_df[
                    "Portfolio Value"
                ]
            )
        ]
    )

    fig_compare.update_layout(
        title=
        "DCA vs Lump Sum Result"
    )

    st.plotly_chart(
        fig_compare,
        width="stretch"
    )


    # Highlight Strongest Recommendation
    buy_coin = optimizer_df.loc[
        optimizer_df["Difference %"].idxmax()
    ]

    sell_coin = optimizer_df.loc[
        optimizer_df["Difference %"].idxmin()
    ]

    st.success(
        f"📈 Increase Allocation: "
        f"{buy_coin['Coin']} "
        f"({buy_coin['Difference %']}%)"
    )

    st.warning(
        f"📉 Reduce Allocation: "
        f"{sell_coin['Coin']} "
        f"({abs(sell_coin['Difference %'])}%)"
    )

    st.subheader(
        "Suggested Investment Plan", divider="blue"
    )

    st.dataframe(
        optimizer_df,
        width="stretch"
    )

    best_coin = optimizer_df.loc[
        optimizer_df[
            "Suggested Allocation %"
        ].idxmax()
    ]

    st.success(
        f"🏆 Largest Suggested Position: "
        f"{best_coin['Coin']} "
        f"({best_coin['Suggested Allocation %']}%)"
    )

    fig_opt = go.Figure(
        data=[
            go.Pie(
                labels=optimizer_df["Coin"],
                values=optimizer_df[
                    "Suggested Allocation %"
                ],
                hole=0.4
            )
        ]
    )

    st.plotly_chart(
        fig_opt,
        width="stretch"
    )

elif page == "Macro Command Center":
    from modules.macro_command_center import (
        render_macro_command_center
    )

    render_macro_command_center()
elif page == "Coin Prediction":
    from modules.coin_prediction import (
        show_coin_prediction
    )

    show_coin_prediction()

