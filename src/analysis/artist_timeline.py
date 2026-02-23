# src/analysis/artist_timeline.py
"""
Artist timeline analysis.
Works from processed_streaming_data.csv — no enrichment needed.
All functions: DataFrame in → DataFrame out. No I/O, no plotting.
"""

import pandas as pd


ARTIST_COL = "master_metadata_album_artist_name"
TRACK_COL = "master_metadata_track_name"


# ---------------------------------------------------------------------------
# Top artists per year
# ---------------------------------------------------------------------------
def top_artists_per_year(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """
    Return top n artists by play count for each year.
    Columns: [year, artist, play_count, rank]
    """
    counts = (
        df.groupby(["year", ARTIST_COL])
        .size()
        .reset_index(name="play_count")
        .rename(columns={ARTIST_COL: "artist"})
    )
    counts["rank"] = (
        counts.groupby("year")["play_count"]
        .rank(method="first", ascending=False)
        .astype(int)
    )
    result = (
        counts[counts["rank"] <= n]
        .sort_values(["year", "rank"])
        .reset_index(drop=True)
    )
    return result


# ---------------------------------------------------------------------------
# Monthly streams for a set of artists (stacked area chart data)
# ---------------------------------------------------------------------------
def monthly_artist_streams(df: pd.DataFrame, artists: list[str]) -> pd.DataFrame:
    """
    For the given list of artists, return monthly play counts.
    Columns: [year_month, artist, play_count]
    year_month is a Period string like '2020-03'.
    """
    ts = pd.to_datetime(df["ts"], utc=True)
    tmp = df.copy()
    tmp["year_month"] = ts.dt.to_period("M").astype(str)

    filtered = tmp[tmp[ARTIST_COL].isin(artists)]
    result = (
        filtered.groupby(["year_month", ARTIST_COL])
        .size()
        .reset_index(name="play_count")
        .rename(columns={ARTIST_COL: "artist"})
        .sort_values(["year_month", "artist"])
        .reset_index(drop=True)
    )
    return result


# ---------------------------------------------------------------------------
# Discovery and fade (lifecycle per artist)
# ---------------------------------------------------------------------------
def discovery_and_fade(df: pd.DataFrame) -> pd.DataFrame:
    """
    For each artist, compute:
      - first_play_year
      - peak_year (year with most plays)
      - last_play_year
      - total_plays
    Returns rows for artists with >= 5 total plays.
    """
    counts_per_year = (
        df.groupby(["year", ARTIST_COL])
        .size()
        .reset_index(name="plays")
    )

    first_year = (
        counts_per_year.groupby(ARTIST_COL)["year"].min().rename("first_play_year")
    )
    last_year = (
        counts_per_year.groupby(ARTIST_COL)["year"].max().rename("last_play_year")
    )
    total_plays = (
        counts_per_year.groupby(ARTIST_COL)["plays"].sum().rename("total_plays")
    )
    peak_year = (
        counts_per_year.loc[
            counts_per_year.groupby(ARTIST_COL)["plays"].idxmax()
        ]
        .set_index(ARTIST_COL)["year"]
        .rename("peak_year")
    )

    result = (
        pd.concat([first_year, peak_year, last_year, total_plays], axis=1)
        .reset_index()
        .rename(columns={ARTIST_COL: "artist"})
    )
    result = result[result["total_plays"] >= 5].sort_values("total_plays", ascending=False)
    return result.reset_index(drop=True)


# ---------------------------------------------------------------------------
# Single-artist monthly play history
# ---------------------------------------------------------------------------
def artist_play_history(df: pd.DataFrame, artist: str) -> pd.DataFrame:
    """
    Monthly play count for a single artist.
    Columns: [year_month, play_count]
    """
    ts = pd.to_datetime(df["ts"], utc=True)
    tmp = df.copy()
    tmp["year_month"] = ts.dt.to_period("M").astype(str)

    filtered = tmp[tmp[ARTIST_COL].str.lower() == artist.lower()]
    result = (
        filtered.groupby("year_month")
        .size()
        .reset_index(name="play_count")
        .sort_values("year_month")
        .reset_index(drop=True)
    )
    return result
