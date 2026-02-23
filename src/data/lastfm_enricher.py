# src/data/lastfm_enricher.py
"""
Async Last.fm enricher.

Usage:
    python src/data/lastfm_enricher.py

Reads:  data/processed/processed_streaming_data.csv
Writes: data/processed/lastfm_tags_cache.json   (persistent cache)
        data/processed/enriched_streaming_data.csv
"""

import asyncio
import json
import os
import sys
from pathlib import Path

import aiohttp
import pandas as pd
from dotenv import load_dotenv
from tqdm import tqdm

# Windows requires SelectorEventLoop for aiohttp
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).parent.parent.parent
DATA_PROCESSED = ROOT / "data" / "processed"
CACHE_FILE = DATA_PROCESSED / "lastfm_tags_cache.json"
INPUT_CSV = DATA_PROCESSED / "processed_streaming_data.csv"
OUTPUT_CSV = DATA_PROCESSED / "enriched_streaming_data.csv"

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
LASTFM_BASE = "https://ws.audioscrobbler.com/2.0/"
MAX_CONCURRENT = 5       # semaphore size — ~5 req/s
REQUEST_DELAY = 0.2      # seconds inside semaphore
FLUSH_EVERY = 100        # flush cache to disk every N completed requests

# ---------------------------------------------------------------------------
# Env / API key
# ---------------------------------------------------------------------------
load_dotenv(ROOT / "data" / ".env")
load_dotenv(ROOT / ".env")      # fallback to project root .env


def _get_api_key() -> str:
    key = os.getenv("LASTFM_API_KEY", "")
    if not key:
        raise RuntimeError(
            "LASTFM_API_KEY not set. "
            "Create data/.env with LASTFM_API_KEY=your_key_here"
        )
    return key


# ---------------------------------------------------------------------------
# Cache helpers
# ---------------------------------------------------------------------------
def _cache_key(artist: str, track: str) -> str:
    return f"{artist.lower()}|||{track.lower()}"


def load_cache() -> dict:
    if CACHE_FILE.exists():
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_cache(cache: dict) -> None:
    """Atomic write: write to .tmp then rename to avoid corruption."""
    tmp = CACHE_FILE.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False)
    os.replace(tmp, CACHE_FILE)


# ---------------------------------------------------------------------------
# Async fetch
# ---------------------------------------------------------------------------
async def fetch_tags(
    session: aiohttp.ClientSession,
    api_key: str,
    artist: str,
    track: str,
    semaphore: asyncio.Semaphore,
) -> list[dict] | None:
    """
    Fetch top tags for artist/track from Last.fm.
    Returns list of {"name": ..., "count": ...} dicts, or None on failure.
    """
    async with semaphore:
        await asyncio.sleep(REQUEST_DELAY)
        params = {
            "method": "track.gettoptags",
            "artist": artist,
            "track": track,
            "api_key": api_key,
            "format": "json",
        }
        try:
            async with session.get(
                LASTFM_BASE, params=params, timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json(content_type=None)
                tags = data.get("toptags", {}).get("tag", [])
                # Last.fm returns a dict (not list) when there is exactly 1 tag
                if isinstance(tags, dict):
                    tags = [tags]
                return tags if isinstance(tags, list) else None
        except Exception:
            return None


# ---------------------------------------------------------------------------
# Main enrichment coroutine
# ---------------------------------------------------------------------------
async def enrich(df: pd.DataFrame, cache: dict, api_key: str) -> dict:
    """
    Fetch missing tags for unique (artist, track) pairs not yet in cache.
    Updates `cache` in-place; returns the updated cache.
    """
    # Collect pairs that need fetching
    track_col = "master_metadata_track_name"
    artist_col = "master_metadata_album_artist_name"

    pairs = (
        df[[artist_col, track_col]]
        .dropna()
        .drop_duplicates()
        .values.tolist()
    )

    to_fetch = [
        (artist, track)
        for artist, track in pairs
        if _cache_key(artist, track) not in cache
    ]

    print(f"Unique tracks to fetch: {len(to_fetch)} (cache has {len(cache)} entries)")

    if not to_fetch:
        print("All tracks already in cache — nothing to fetch.")
        return cache

    semaphore = asyncio.Semaphore(MAX_CONCURRENT)
    completed = 0

    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch_tags(session, api_key, artist, track, semaphore)
            for artist, track in to_fetch
        ]

        with tqdm(total=len(tasks), desc="Fetching Last.fm tags") as pbar:
            for coro, (artist, track) in zip(
                asyncio.as_completed(tasks), to_fetch
            ):
                result = await coro
                key = _cache_key(artist, track)
                # None means "tried and failed" — store as JSON null to avoid re-fetch
                cache[key] = result
                completed += 1
                pbar.update(1)

                if completed % FLUSH_EVERY == 0:
                    save_cache(cache)

    save_cache(cache)
    return cache


# ---------------------------------------------------------------------------
# Apply cache to DataFrame
# ---------------------------------------------------------------------------
def apply_cache_to_df(df: pd.DataFrame, cache: dict) -> pd.DataFrame:
    """
    Add columns: lastfm_tags, primary_genre, primary_mood, has_lastfm_data.
    """
    from src.utils.tag_normalizer import normalize_tags, classify_genre, classify_mood

    track_col = "master_metadata_track_name"
    artist_col = "master_metadata_album_artist_name"

    def _get_tags(row):
        artist = row.get(artist_col)
        track = row.get(track_col)
        if pd.isna(artist) or pd.isna(track):
            return None
        raw = cache.get(_cache_key(str(artist), str(track)))
        return raw  # None or list

    def _process_row(row):
        raw_tags = _get_tags(row)
        if raw_tags is None:
            return pd.Series({
                "lastfm_tags": "[]",
                "primary_genre": None,
                "primary_mood": None,
                "has_lastfm_data": False,
            })
        norm = normalize_tags(raw_tags)
        cleaned = [t for t, _ in norm]
        return pd.Series({
            "lastfm_tags": json.dumps([{"name": t, "count": c} for t, c in norm]),
            "primary_genre": classify_genre(cleaned),
            "primary_mood": classify_mood(cleaned),
            "has_lastfm_data": True,
        })

    enriched_cols = df.apply(_process_row, axis=1)
    return pd.concat([df, enriched_cols], axis=1)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main():
    api_key = _get_api_key()
    print(f"Loading data from {INPUT_CSV} ...")
    df = pd.read_csv(INPUT_CSV, low_memory=False)
    print(f"Loaded {len(df):,} rows.")

    cache = load_cache()
    cache = asyncio.run(enrich(df, cache, api_key))

    print("Applying cache to DataFrame ...")
    enriched = apply_cache_to_df(df, cache)

    enriched.to_csv(OUTPUT_CSV, index=False)
    print(f"Enriched data saved to {OUTPUT_CSV}")
    print(f"Rows with Last.fm data: {enriched['has_lastfm_data'].sum():,} / {len(enriched):,}")


if __name__ == "__main__":
    main()
