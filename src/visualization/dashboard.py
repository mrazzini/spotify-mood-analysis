# src/visualization/dashboard.py
"""
Streamlit dashboard for Spotify Mood Analysis.

Run:
    streamlit run src/visualization/dashboard.py
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).parent.parent.parent
PROCESSED_CSV = ROOT / "data" / "processed" / "processed_streaming_data.csv"
ENRICHED_CSV = ROOT / "data" / "processed" / "enriched_streaming_data.csv"

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Spotify Mood Analysis",
    page_icon="🎵",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Data loading (cached)
# ---------------------------------------------------------------------------
@st.cache_data
def load_processed(min_ms: int, year_lo: int, year_hi: int) -> pd.DataFrame:
    df = pd.read_csv(PROCESSED_CSV, low_memory=False)
    df["ts"] = pd.to_datetime(df["ts"], utc=True)
    # Re-derive columns in case they're missing / wrong type after csv round-trip
    df["date"] = df["ts"].dt.date
    df["hour"] = df["ts"].dt.hour
    df["day_of_week"] = df["ts"].dt.day_name()
    df["month"] = df["ts"].dt.month
    df["year"] = df["ts"].dt.year
    # Filter
    from src.analysis.temporal import filter_plays
    return filter_plays(df, min_ms=min_ms, year_range=(year_lo, year_hi))


@st.cache_data
def load_enriched(min_ms: int, year_lo: int, year_hi: int) -> pd.DataFrame | None:
    if not ENRICHED_CSV.exists():
        return None
    df = pd.read_csv(ENRICHED_CSV, low_memory=False)
    df["ts"] = pd.to_datetime(df["ts"], utc=True)
    df["date"] = df["ts"].dt.date
    df["hour"] = df["ts"].dt.hour
    df["day_of_week"] = df["ts"].dt.day_name()
    df["month"] = df["ts"].dt.month
    df["year"] = df["ts"].dt.year
    from src.analysis.temporal import filter_plays
    return filter_plays(df, min_ms=min_ms, year_range=(year_lo, year_hi))


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
st.sidebar.title("Filters")

year_range = st.sidebar.slider(
    "Year range",
    min_value=2012,
    max_value=2024,
    value=(2012, 2024),
    step=1,
)

min_ms_option = st.sidebar.selectbox(
    "Minimum play duration",
    options=[0, 15_000, 30_000, 60_000],
    index=2,
    format_func=lambda x: {0: "All plays", 15_000: "≥ 15s", 30_000: "≥ 30s", 60_000: "≥ 60s"}[x],
)

year_lo, year_hi = year_range
df = load_processed(min_ms=min_ms_option, year_lo=year_lo, year_hi=year_hi)
df_enriched = load_enriched(min_ms=min_ms_option, year_lo=year_lo, year_hi=year_hi)

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "Overview",
    "Listening Patterns",
    "Artist Timeline",
    "Mood & Genre",
])


# ============================================================
# TAB 1 — Overview
# ============================================================
with tab1:
    st.header("Overview")

    from src.analysis.temporal import compute_kpis, daily_volume

    kpis = compute_kpis(df)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Streams", f"{kpis['total_streams']:,}")
    col2.metric("Hours Listened", f"{kpis['total_hours']:,.0f} h")
    col3.metric("Unique Artists", f"{kpis['unique_artists']:,}")
    col4.metric("Unique Tracks", f"{kpis['unique_tracks']:,}")

    st.caption(f"Date range: {kpis['date_range']} · Top artist: **{kpis['top_artist']}**")

    # Daily activity timeline
    st.subheader("Daily Activity")
    daily = daily_volume(df).reset_index()
    daily.columns = ["date", "play_count"]
    daily["date"] = pd.to_datetime(daily["date"])
    daily = daily.sort_values("date")
    daily["rolling_7d"] = daily["play_count"].rolling(7, min_periods=1).mean()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=daily["date"], y=daily["play_count"],
        mode="lines", name="Daily plays",
        line=dict(color="#1DB954", width=1), opacity=0.5,
    ))
    fig.add_trace(go.Scatter(
        x=daily["date"], y=daily["rolling_7d"],
        mode="lines", name="7-day avg",
        line=dict(color="#ffffff", width=2),
    ))
    fig.update_layout(
        template="plotly_dark",
        xaxis_title="Date",
        yaxis_title="Plays",
        legend=dict(orientation="h"),
        height=350,
        margin=dict(l=0, r=0, t=10, b=0),
    )
    st.plotly_chart(fig, use_container_width=True)


# ============================================================
# TAB 2 — Listening Patterns
# ============================================================
with tab2:
    st.header("Listening Patterns")

    from src.analysis.temporal import (
        hourly_heatmap_data,
        day_of_week_distribution,
        monthly_volume,
    )

    # Hour × Day heatmap
    st.subheader("Play Count by Hour and Day")
    heatmap_df = hourly_heatmap_data(df)
    fig_heat = px.imshow(
        heatmap_df,
        labels=dict(x="Hour of day", y="Day of week", color="Plays"),
        color_continuous_scale="Greens",
        aspect="auto",
    )
    fig_heat.update_layout(template="plotly_dark", height=320, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig_heat, use_container_width=True)

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Plays by Day of Week")
        dow = day_of_week_distribution(df)
        fig_dow = px.bar(
            dow, x="day_of_week", y="play_count",
            color_discrete_sequence=["#1DB954"],
        )
        fig_dow.update_layout(
            template="plotly_dark",
            xaxis_title="", yaxis_title="Plays",
            height=300, margin=dict(l=0, r=0, t=10, b=0),
        )
        st.plotly_chart(fig_dow, use_container_width=True)

    with col_b:
        st.subheader("Monthly Volume")
        monthly = monthly_volume(df)
        monthly["label"] = (
            monthly["year"].astype(str) + "-"
            + monthly["month"].astype(str).str.zfill(2)
        )
        # Season colour annotations
        season_colors = {
            12: "#4a90d9", 1: "#4a90d9", 2: "#4a90d9",  # Winter
            3: "#7bc67e", 4: "#7bc67e", 5: "#7bc67e",    # Spring
            6: "#f5a623", 7: "#f5a623", 8: "#f5a623",    # Summer
            9: "#d0694a", 10: "#d0694a", 11: "#d0694a",  # Autumn
        }
        monthly["bar_color"] = monthly["month"].map(season_colors)
        fig_monthly = go.Figure(go.Bar(
            x=monthly["label"],
            y=monthly["play_count"],
            marker_color=monthly["bar_color"],
        ))
        fig_monthly.update_layout(
            template="plotly_dark",
            xaxis_title="", yaxis_title="Plays",
            height=300, margin=dict(l=0, r=0, t=10, b=0),
        )
        # Season legend via shapes
        for label, color in [
            ("Winter", "#4a90d9"), ("Spring", "#7bc67e"),
            ("Summer", "#f5a623"), ("Autumn", "#d0694a"),
        ]:
            fig_monthly.add_trace(go.Scatter(
                x=[None], y=[None], mode="markers",
                marker=dict(color=color, size=10, symbol="square"),
                name=label,
            ))
        st.plotly_chart(fig_monthly, use_container_width=True)


# ============================================================
# TAB 3 — Artist Timeline
# ============================================================
with tab3:
    st.header("Artist Timeline")

    from src.analysis.artist_timeline import (
        top_artists_per_year,
        monthly_artist_streams,
        artist_play_history,
    )

    # Stacked area: top 10 artists overall
    st.subheader("Top 10 Artists — Monthly Streams")
    top10_overall = (
        df.groupby("master_metadata_album_artist_name")
        .size()
        .nlargest(10)
        .index.tolist()
    )
    monthly_streams = monthly_artist_streams(df, top10_overall)
    fig_area = px.area(
        monthly_streams,
        x="year_month", y="play_count", color="artist",
        color_discrete_sequence=px.colors.qualitative.Plotly,
    )
    fig_area.update_layout(
        template="plotly_dark",
        xaxis_title="Month", yaxis_title="Plays",
        height=400, margin=dict(l=0, r=0, t=10, b=0),
        legend=dict(orientation="h", y=-0.2),
    )
    st.plotly_chart(fig_area, use_container_width=True)

    col_l, col_r = st.columns([1, 1])

    with col_l:
        st.subheader("Top Artists by Year")
        selected_year = st.selectbox(
            "Select year", options=sorted(df["year"].unique()), index=len(df["year"].unique()) - 1
        )
        topy = top_artists_per_year(df, n=10)
        topy_year = topy[topy["year"] == selected_year]
        fig_topy = px.bar(
            topy_year.sort_values("play_count"),
            x="play_count", y="artist",
            orientation="h",
            color_discrete_sequence=["#1DB954"],
        )
        fig_topy.update_layout(
            template="plotly_dark",
            xaxis_title="Plays", yaxis_title="",
            height=380, margin=dict(l=0, r=0, t=10, b=0),
        )
        st.plotly_chart(fig_topy, use_container_width=True)

    with col_r:
        st.subheader("Artist Deep Dive")
        artist_search = st.text_input("Search artist", placeholder="e.g. Pierce The Veil")
        if artist_search:
            history = artist_play_history(df, artist_search)
            if history.empty:
                st.warning(f"No plays found for '{artist_search}'.")
            else:
                fig_hist = px.bar(
                    history, x="year_month", y="play_count",
                    color_discrete_sequence=["#1DB954"],
                )
                fig_hist.update_layout(
                    template="plotly_dark",
                    xaxis_title="Month", yaxis_title="Plays",
                    height=350, margin=dict(l=0, r=0, t=10, b=0),
                )
                st.plotly_chart(fig_hist, use_container_width=True)
                total = history["play_count"].sum()
                st.caption(f"Total plays for {artist_search}: {total:,}")


# ============================================================
# TAB 4 — Mood & Genre
# ============================================================
with tab4:
    st.header("Mood & Genre Analysis")

    if df_enriched is None:
        st.warning(
            "Enriched data not found. "
            "Run the enricher first:\n\n"
            "```\npython src/data/lastfm_enricher.py\n```"
        )
        st.stop()

    from src.analysis.genre_analysis import (
        genre_distribution,
        mood_distribution,
        mood_by_month,
        mood_by_season,
        mood_by_year,
        genre_by_year,
        top_tracks_per_mood,
    )

    # --- Pie + Donut row ---
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Genre Distribution")
        genre_dist = genre_distribution(df_enriched)
        fig_pie = px.pie(
            genre_dist, values="count", names="primary_genre",
            color_discrete_sequence=px.colors.qualitative.Pastel,
        )
        fig_pie.update_layout(template="plotly_dark", height=340, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        st.subheader("Mood Distribution")
        mood_dist = mood_distribution(df_enriched)
        fig_donut = px.pie(
            mood_dist, values="count", names="primary_mood",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Vivid,
        )
        fig_donut.update_layout(template="plotly_dark", height=340, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig_donut, use_container_width=True)

    # --- Seasonality heatmap (month × mood) ---
    st.subheader("Mood Seasonality — Monthly Heatmap")
    st.caption("Percentage of plays per mood within each month (normalised)")
    mbm = mood_by_month(df_enriched)
    if not mbm.empty:
        pivot_mood_month = mbm.pivot_table(
            index="primary_mood", columns="month_name", values="pct", fill_value=0
        )
        month_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                       "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        pivot_mood_month = pivot_mood_month.reindex(columns=month_order, fill_value=0)
        fig_hm = px.imshow(
            pivot_mood_month,
            labels=dict(x="Month", y="Mood", color="% of plays"),
            color_continuous_scale="Viridis",
            aspect="auto",
            text_auto=".1f",
        )
        fig_hm.update_layout(template="plotly_dark", height=320, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig_hm, use_container_width=True)

    # --- Mood by year stacked bar ---
    st.subheader("Mood Evolution by Year")
    mby = mood_by_year(df_enriched)
    if not mby.empty:
        fig_mby = px.bar(
            mby, x="year", y="pct", color="primary_mood",
            barmode="stack",
            labels={"pct": "% of plays", "primary_mood": "Mood"},
            color_discrete_sequence=px.colors.qualitative.Vivid,
        )
        fig_mby.update_layout(
            template="plotly_dark",
            xaxis_title="Year", yaxis_title="% of plays",
            height=370, margin=dict(l=0, r=0, t=10, b=0),
            legend=dict(orientation="h"),
        )
        st.plotly_chart(fig_mby, use_container_width=True)

    # --- Genre by year stacked area ---
    st.subheader("Genre Evolution by Year")
    gby = genre_by_year(df_enriched)
    if not gby.empty:
        fig_gby = px.area(
            gby, x="year", y="pct", color="primary_genre",
            labels={"pct": "% of plays", "primary_genre": "Genre"},
            color_discrete_sequence=px.colors.qualitative.Pastel,
        )
        fig_gby.update_layout(
            template="plotly_dark",
            xaxis_title="Year", yaxis_title="% of plays",
            height=370, margin=dict(l=0, r=0, t=10, b=0),
            legend=dict(orientation="h"),
        )
        st.plotly_chart(fig_gby, use_container_width=True)

    # --- Top tracks per mood ---
    st.subheader("Top Tracks per Mood")
    available_moods = sorted(df_enriched["primary_mood"].dropna().unique().tolist())
    if available_moods:
        selected_mood = st.selectbox("Select mood", options=available_moods)
        top_tracks = top_tracks_per_mood(df_enriched, selected_mood, n=10)
        if top_tracks.empty:
            st.info(f"No tracks found for mood '{selected_mood}'.")
        else:
            st.dataframe(
                top_tracks.reset_index(drop=True),
                use_container_width=True,
                hide_index=True,
            )
    else:
        st.info("No mood data available in the current selection.")
