# Spotify Mood Analysis

🌐 **[View the Live Dashboard](https://spotify-mood-analysis.streamlit.app/)**

## 📌 Project Overview
This project analyzes personal Spotify streaming data across 2012–2024 to explore listening patterns and their relationship with mood and emotional state. By enriching Spotify data with Last.fm genre and mood classifications, the analysis reveals temporal trends in music preferences, seasonal patterns in listening behavior, and how musical tastes evolve over time.

## ✨ Features
- **Temporal Analysis**: Daily, hourly, and day-of-week listening patterns; identify peak listening times
- **Mood & Genre Seasonality**: Classify tracks by mood and genre using Last.fm API enrichment
- **Artist & Genre Evolution**: Track how musical preferences change year-over-year
- **Interactive Dashboard**: Explore all analyses via Streamlit web application
- **Last.fm Enrichment**: Async data fetching for mood/genre metadata with intelligent caching

## 🗂 Project Structure
```
spotify-mood-analysis/
│
├── data/
│   ├── raw/                         # Raw Spotify streaming history (JSON files, 2012–2024)
│   ├── processed/                   # Cleaned CSVs and enriched data
│       ├── processed_streaming_data.csv       # Temporal analysis ready
│       ├── enriched_streaming_data.csv        # With Last.fm mood/genre tags
│       └── lastfm_tags_cache.json             # Persistent API cache
│
├── src/
│   ├── data/                        # Data loading & Last.fm enrichment
│   │   ├── data_loader.py           # Load and process raw streaming JSON
│   │   └── lastfm_enricher.py       # Async Last.fm metadata fetching
│   │
│   ├── analysis/                    # Core analysis functions
│   │   ├── temporal.py              # Listening patterns, KPIs, heatmaps
│   │   ├── genre_analysis.py        # Mood & genre seasonality analysis
│   │   ├── artist_timeline.py       # Artist evolution over time
│   │   └── tag_normalizer.py        # Genre/mood tag utilities
│   │
│   └── visualization/
│       └── dashboard.py              # Interactive Streamlit dashboard
│
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt
```

## ⚙️ Setup

1. Clone the repository
```bash
git clone https://github.com/mrazzini/spotify-mood-analysis.git
cd spotify-mood-analysis
```

2. Create and activate virtual environment
```bash
python -m venv venv
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Configure Last.fm API credentials (for enrichment)
   - Create a [Last.fm API account](https://www.last.fm/api/account/create)
   - Get your **API Key** and **Shared Secret**
   - Save them in a `.env` file:
   ```
   LASTFM_API_KEY=your_api_key
   LASTFM_API_SECRET=your_api_secret
   ```

## 🚀 Usage

1. **Process streaming data**
```bash
python src/data/data_loader.py
```
This loads and processes raw Spotify JSON streaming history into a clean CSV.

2. **Enrich with Last.fm metadata** (optional)
```bash
python src/data/lastfm_enricher.py
```
Fetches mood and genre classifications for all tracks, with intelligent caching to avoid redundant API calls.

3. **Launch the interactive dashboard**
```bash
streamlit run src/visualization/dashboard.py
```
Or view the public dashboard: **[spotify-mood-analysis.streamlit.app](https://spotify-mood-analysis.streamlit.app/)**

The dashboard includes:
- **Overview**: KPIs (total streams, hours, artists) and daily activity timeline
- **Listening Patterns**: Hourly heatmaps, day-of-week distribution, monthly trends
- **Artist Timeline**: Top artists, monthly evolution, artist deep dives
- **Mood & Genre**: Seasonality analysis, genre distribution, mood-based tracks

## 📊 Analysis Methodology

### Data Pipeline
1. **Loading**: Raw Spotify streaming history (JSON) → temporal features extraction
2. **Enrichment**: Last.fm API queries for mood/genre tags (with caching)
3. **Normalization**: Tag standardization to primary mood/genre categories
4. **Analysis**: Segmentation by temporal, seasonal, and artist dimensions

### Core Insights
- **Temporal Patterns**: Identifies peak listening hours (typically evenings) and weekly cycles
- **Seasonal Mood Shifts**: Reveals how mood preferences vary by season and month
- **Genre Evolution**: Tracks major shifts in musical taste across the 12-year period
- **Artist Timeline**: Visualizes which artists dominated each year and era

## 🎯 Key Findings

### Mood Seasonality
Analysis of 2012–2024 listening data reveals significant seasonal mood patterns:
- **Winter** leans toward introspective, melancholic moods
- **Spring/Summer** show increased energy and upbeat preferences
- **Autumn** exhibits a transitional blend with slight return to introspection

### Listening Behavior
- **Peak Activity**: Late evening hours (8 PM–midnight) dominate across all days
- **Weekly Patterns**: Slight variation between weekdays and weekends, with Friday evening showing highest engagement
- **Trend**: Listening frequency peaked during 2017–2019, with gradual decline in 2023–2024

### Artist & Genre Insights
- **Artist Loyalty**: Strong concentration in indie rock and alternative genres across the period
- **Genre Diversity**: Gradual expansion of genre palette; initial heavy rock focus evolved to include electronic and indie pop influences
- **Top Artist**: Consistent favorite across multiple years demonstrates strong genre/style preference

## 🔮 Future Improvements
- Enhanced mood inference using Spotify audio features (energy, valence, danceability, tempo)
- Machine learning classification of mood from audio and temporal features
- Clustering analysis to identify listening "personas" or distinct behavioral modes
- Integration of external data (weather, events, calendar) to correlate with listening patterns
- Comparison mode to benchmark against similar users (anonymized)

## ⚠️ Data Privacy Notice
**This repository contains personal Spotify streaming data (2012–2024).** While this data is publicly available in the repository, it has been included for analytical purposes and represents the complete listening history. Users should be aware that:
- Streaming history includes timestamps and exact play counts
- Artist and track names are personally identifying when combined with metadata
- The data reflects individual listening patterns and preferences

If you fork or use this project, be mindful of privacy implications when sharing results.  

## 🤝 Contributing
Pull requests are welcome! For major changes, please open an issue to discuss your idea first.

## 📜 License
[MIT](https://choosealicense.com/licenses/mit/)
