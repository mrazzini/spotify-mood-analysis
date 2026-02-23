# Spotify Mood Analysis

## 📌 Project Overview
This project analyzes personal Spotify streaming data to explore listening patterns and their potential relationship with mood.  
It includes temporal trends, genre distributions, and mood-related insights based on music choices across different years.

## ✨ Features
- Analysis of temporal listening patterns (daily, weekly, yearly)
- Genre-based mood correlation
- Interactive visualizations
- Spotify API integration for enriched metadata
- Streamlit dashboard for easy exploration
- Tableau visualizations (optional)

## 🗂 Project Structure
```
spotify-mood-analysis/
│
├── data/
│   ├── raw/                         # Raw Spotify data (JSONs, PDFs)
│   ├── processed/                   # Cleaned CSVs and analysis-ready data
│
├── src/
│   ├── data/                        # Data loading & preprocessing scripts
│   ├── analysis/                    # Scripts for temporal/genre/mood analysis
│   ├── visualization/               # Streamlit dashboards, Tableau exports
│
├── .gitignore
├── LICENSE
├── README.md
```

## ⚙️ Setup

1. Clone the repository
```bash
git clone https://github.com/your-username/spotify-mood-analysis.git
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

4. Configure Spotify API credentials  
   - Create a [Spotify Developer Account](https://developer.spotify.com/)  
   - Register a new app and obtain **Client ID** and **Client Secret**  
   - Save them in a `.env` file like this:
   ```
   SPOTIFY_CLIENT_ID=your_client_id
   SPOTIFY_CLIENT_SECRET=your_client_secret
   ```

## 🚀 Usage

1. **Load Data**
```bash
python src/data/data_loader.py
```

2. **Run Analysis**
```bash
python src/analysis/temporal.py
python src/analysis/genre_analysis.py
```

3. **Launch Dashboard**
```bash
streamlit run src/visualization/dashboard.py
```

## 📊 Analysis Methodology
- **Temporal analysis**: Identify trends in listening frequency and time-of-day patterns.  
- **Genre analysis**: Map genres to potential moods.  
- **Mood correlation**: Explore how playlists and artists align with mood categories.  

## 📈 Visualizations
- Heatmaps of listening by hour/day  
- Genre distribution charts  
- Year-over-year mood shifts  
- Streamlit dashboard with filters  

_(Screenshots or GIFs of visualizations can be added here)_

## 🔮 Future Improvements
- Use Spotify audio features (energy, valence, tempo) for deeper mood inference  
- Apply ML models to predict mood based on tracks  
- Add clustering of listening habits  
- Improve dashboard with personalization options  

## 🤝 Contributing
Pull requests are welcome! For major changes, please open an issue to discuss your idea first.

## 📜 License
[MIT](https://choosealicense.com/licenses/mit/)
