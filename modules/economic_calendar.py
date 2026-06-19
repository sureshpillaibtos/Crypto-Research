# modules/economic_calendar.py

import pandas as pd
from datetime import datetime
import streamlit as st
from pathlib import Path


def get_economic_events():

    csv_path = (
        Path(__file__).resolve().parent.parent
        / "data"
        / "economic_events.csv"
    )

    df = pd.read_csv(csv_path)

    df["date"] = pd.to_datetime(df["date"])

    return df.sort_values("date") 


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
    display_df = events_df.copy()
    display_df["date"] = (
        display_df["date"]
        .dt.strftime("%d-%m-%Y")
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

    #st.dataframe(
    #    events_df,
    #    width='stretch'
    #)
    st.dataframe(
        display_df,
        width="stretch"
    )
    