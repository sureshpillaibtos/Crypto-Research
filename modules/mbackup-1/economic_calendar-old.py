# modules/economic_calendar.py

import pandas as pd
from datetime import datetime
import streamlit as st


def get_economic_events():

    events = [
        {
            "date": "2026-06-17",
            "event": "FOMC Meeting",
            "impact": "High"
        },
        {
            "date": "2026-06-25",
            "event": "PCE Inflation",
            "impact": "High"
        },
        {
            "date": "2026-07-03",
            "event": "US Jobs Report",
            "impact": "High"
        },
        {
            "date": "2026-07-14",
            "event": "CPI Inflation",
            "impact": "High"
        },
        {
            "date": "2026-07-15",
            "event": "PPI Inflation",
            "impact": "High"
        },
        {
            "date": "2026-07-28",
            "event": "FOMC Meeting",
            "impact": "High"
        }
    ]

    return pd.DataFrame(events)


def calculate_days_remaining(df):

    today = datetime.today().date()

    df["date"] = pd.to_datetime(df["date"])

    df["days_left"] = (
        df["date"].dt.date - today
    ).apply(lambda x: x.days)

    return df


def get_next_high_impact_event(df):

    upcoming = df[df["days_left"] >= 0]

    if upcoming.empty:
        return None

    return upcoming.sort_values(
        "days_left"
    ).iloc[0]


def render_economic_calendar():

    st.subheader("📅 Economic Calendar")

    events_df = get_economic_events()

    events_df = calculate_days_remaining(
        events_df
    )

    next_event = get_next_high_impact_event(
        events_df
    )

    if next_event is not None:

        st.warning(
            f"Next Event: "
            f"{next_event['event']} "
            f"in {next_event['days_left']} days"
        )

    st.dataframe(
        events_df,
        use_container_width=True
    )