# src/analysis/temporal.py
"""
Pure temporal analysis functions.
All functions: DataFrame in → DataFrame/dict out. No I/O, no plotting.
"""

import pandas as pd

DAYS_ORDERED = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


# ---------------------------------------------------------------------------
# Filtering
# ---------------------------------------------------------------------------
def filter_plays(
    df: pd.DataFrame,
    min_ms: int = 30_000,
    year_range: tuple[int, int] | None = None,
) -> pd.DataFrame:
    """
    Filter out podcasts (null track name) and short plays (< min_ms).
    Optionally restrict to a year range (inclusive).
    """
    track_col = "master_metadata_track_name"
    out = df[df[track_col].notna()].copy()
    out = out[out["ms_played"] >= min_ms]
    if year_range is not None:
        lo, hi = year_range
        out = out[(out["year"] >= lo) & (out["year"] <= hi)]
    return out


# ---------------------------------------------------------------------------
# KPIs
# ---------------------------------------------------------------------------
def compute_kpis(df: pd.DataFrame) -> dict:
    """
    Return a dict with summary KPIs.
    Expects df already filtered via filter_plays().
    """
    total_streams = len(df)
    total_hours = df["ms_played"].sum() / 3_600_000
    unique_artists = df["master_metadata_album_artist_name"].nunique()
    unique_tracks = df["master_metadata_track_name"].nunique()

    ts = pd.to_datetime(df["ts"], utc=True)
    date_range = f"{ts.min().date()} - {ts.max().date()}"

    top_artist = (
        df["master_metadata_album_artist_name"]
        .value_counts()
        .idxmax()
        if total_streams > 0
        else "N/A"
    )

    return {
        "total_streams": total_streams,
        "total_hours": round(total_hours, 1),
        "unique_artists": unique_artists,
        "unique_tracks": unique_tracks,
        "date_range": date_range,
        "top_artist": top_artist,
    }


# ---------------------------------------------------------------------------
# Heatmap: hour × day_of_week
# ---------------------------------------------------------------------------
def hourly_heatmap_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns a pivot table: rows = day_of_week (Mon–Sun), cols = hour (0–23).
    Values = play count.
    """
    tmp = df.copy()
    tmp["day_of_week"] = pd.Categorical(tmp["day_of_week"], categories=DAYS_ORDERED, ordered=True)
    pivot = (
        tmp.groupby(["day_of_week", "hour"], observed=True)
        .size()
        .unstack(fill_value=0)
    )
    # Ensure all 24 hours are present
    pivot = pivot.reindex(columns=range(24), fill_value=0)
    return pivot


# ---------------------------------------------------------------------------
# Volume over time
# ---------------------------------------------------------------------------
def daily_volume(df: pd.DataFrame) -> pd.Series:
    """
    Returns a Series: date → play_count, sorted by date.
    """
    return (
        df.groupby("date")
        .size()
        .rename("play_count")
        .sort_index()
    )


def monthly_volume(df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns a DataFrame with columns [year, month, play_count, hours_played].
    """
    tmp = df.copy()
    tmp["hours_played"] = tmp["ms_played"] / 3_600_000
    result = (
        tmp.groupby(["year", "month"])
        .agg(play_count=("ms_played", "count"), hours_played=("hours_played", "sum"))
        .reset_index()
        .sort_values(["year", "month"])
    )
    return result


# ---------------------------------------------------------------------------
# Day-of-week distribution
# ---------------------------------------------------------------------------
def day_of_week_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns a DataFrame with columns [day_of_week, play_count], ordered Mon–Sun.
    """
    tmp = df.copy()
    tmp["day_of_week"] = pd.Categorical(tmp["day_of_week"], categories=DAYS_ORDERED, ordered=True)
    result = (
        tmp.groupby("day_of_week", observed=True)
        .size()
        .rename("play_count")
        .reset_index()
    )
    return result
