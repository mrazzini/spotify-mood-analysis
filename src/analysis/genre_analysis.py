# src/analysis/genre_analysis.py
"""
Genre and mood analysis functions.
Core seasonality analysis: mood/genre distributions by month, season, year.
All functions: DataFrame in → DataFrame out. No I/O, no plotting.
"""

import pandas as pd

SEASON_MAP = {
    12: "Winter", 1: "Winter", 2: "Winter",
    3: "Spring", 4: "Spring", 5: "Spring",
    6: "Summer", 7: "Summer", 8: "Summer",
    9: "Autumn", 10: "Autumn", 11: "Autumn",
}

SEASON_ORDER = ["Winter", "Spring", "Summer", "Autumn"]

MONTH_NAMES = {
    1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr",
    5: "May", 6: "Jun", 7: "Jul", 8: "Aug",
    9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec",
}


def _require_enriched(df: pd.DataFrame) -> pd.DataFrame:
    """Filter to rows that have Last.fm data and a classified mood/genre."""
    if "has_lastfm_data" not in df.columns:
        raise ValueError(
            "DataFrame does not have 'has_lastfm_data' column. "
            "Run lastfm_enricher.py first."
        )
    return df[df["has_lastfm_data"] == True].copy()  # noqa: E712


# ---------------------------------------------------------------------------
# Mood seasonality — the core analysis
# ---------------------------------------------------------------------------
def mood_by_month(df: pd.DataFrame) -> pd.DataFrame:
    """
    For each month 1–12, compute the percentage of plays per mood.
    Uses only rows with a classified mood.
    Returns a DataFrame with columns [month, mood, pct] where pct is normalised
    within each month (so months with fewer plays aren't penalised).
    """
    enriched = _require_enriched(df)
    mood_df = enriched[enriched["primary_mood"].notna()].copy()

    counts = (
        mood_df.groupby(["month", "primary_mood"])
        .size()
        .reset_index(name="count")
    )
    totals = counts.groupby("month")["count"].transform("sum")
    counts["pct"] = counts["count"] / totals * 100

    # Add month name
    counts["month_name"] = counts["month"].map(MONTH_NAMES)
    return counts.sort_values(["month", "primary_mood"])


def mood_by_season(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate mood percentages into Winter/Spring/Summer/Autumn.
    Returns [season, mood, pct].
    """
    enriched = _require_enriched(df)
    mood_df = enriched[enriched["primary_mood"].notna()].copy()
    mood_df["season"] = mood_df["month"].map(SEASON_MAP)

    counts = (
        mood_df.groupby(["season", "primary_mood"])
        .size()
        .reset_index(name="count")
    )
    totals = counts.groupby("season")["count"].transform("sum")
    counts["pct"] = counts["count"] / totals * 100

    counts["season"] = pd.Categorical(counts["season"], categories=SEASON_ORDER, ordered=True)
    return counts.sort_values(["season", "primary_mood"])


def mood_by_year(df: pd.DataFrame) -> pd.DataFrame:
    """
    Mood percentages per year (shows macro emotional arc 2012–2024).
    Returns [year, mood, pct].
    """
    enriched = _require_enriched(df)
    mood_df = enriched[enriched["primary_mood"].notna()].copy()

    counts = (
        mood_df.groupby(["year", "primary_mood"])
        .size()
        .reset_index(name="count")
    )
    totals = counts.groupby("year")["count"].transform("sum")
    counts["pct"] = counts["count"] / totals * 100
    return counts.sort_values(["year", "primary_mood"])


# ---------------------------------------------------------------------------
# Genre distributions
# ---------------------------------------------------------------------------
def genre_by_year(df: pd.DataFrame) -> pd.DataFrame:
    """
    Genre percentages per year.
    Returns [year, genre, pct].
    """
    enriched = _require_enriched(df)
    genre_df = enriched[enriched["primary_genre"].notna()].copy()

    counts = (
        genre_df.groupby(["year", "primary_genre"])
        .size()
        .reset_index(name="count")
    )
    totals = counts.groupby("year")["count"].transform("sum")
    counts["pct"] = counts["count"] / totals * 100
    return counts.sort_values(["year", "primary_genre"])


def genre_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """
    Overall genre distribution (for pie chart).
    Returns [genre, count, pct].
    """
    enriched = _require_enriched(df)
    genre_df = enriched[enriched["primary_genre"].notna()]

    counts = (
        genre_df.groupby("primary_genre")
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )
    counts["pct"] = counts["count"] / counts["count"].sum() * 100
    return counts


def mood_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """
    Overall mood distribution (for donut chart).
    Returns [mood, count, pct].
    """
    enriched = _require_enriched(df)
    mood_df = enriched[enriched["primary_mood"].notna()]

    counts = (
        mood_df.groupby("primary_mood")
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )
    counts["pct"] = counts["count"] / counts["count"].sum() * 100
    return counts


# ---------------------------------------------------------------------------
# Top tracks per mood
# ---------------------------------------------------------------------------
def top_tracks_per_mood(df: pd.DataFrame, mood: str, n: int = 10) -> pd.DataFrame:
    """
    Return the top n tracks for a given mood bucket.
    Returns [track, artist, play_count].
    """
    enriched = _require_enriched(df)
    mood_df = enriched[enriched["primary_mood"] == mood]

    result = (
        mood_df.groupby(
            ["master_metadata_track_name", "master_metadata_album_artist_name"]
        )
        .size()
        .reset_index(name="play_count")
        .rename(columns={
            "master_metadata_track_name": "track",
            "master_metadata_album_artist_name": "artist",
        })
        .sort_values("play_count", ascending=False)
        .head(n)
        .reset_index(drop=True)
    )
    return result
