# modules/macro_command_center.py
import streamlit as st

from modules.economic_calendar import (
    render_economic_calendar
)

def render_macro_command_center():
    st.title("🌍 Crypto Macro Command Center")

    st.markdown(
        """
        Monitor macroeconomic events,
        liquidity conditions and market risks
        affecting crypto markets.
        """
    )
    render_economic_calendar()

from modules.macro_dashboard import (
    render_macro_dashboard
)
def render_macro_command_center():

    st.title("🌍 Crypto Macro Command Center")

    render_economic_calendar()

    st.divider()

    render_macro_dashboard()

from modules.etf_tracker import (
    render_etf_tracker
)
def render_macro_command_center():

    st.title(
        "🌍 Crypto Macro Command Center"
    )

    render_economic_calendar()

    st.divider()

    render_macro_dashboard()

    st.divider()

    render_etf_tracker()