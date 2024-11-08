# Spotify Mood Analysis

## Project Overview
This project analyzes personal Spotify streaming data to understand music listening patterns and their correlation with moods across different time periods. The analysis includes temporal patterns, genre distributions, and potential mood indicators based on music choices.

## Features
- Temporal analysis of music listening patterns
- Genre-based mood correlation
- Interactive visualizations
- Spotify API integration
- Custom dashboard using Streamlit
- Tableau visualizations

## Setup
1. Clone the repository
```bash
git clone https://github.com/your-username/spotify-mood-analysis.git
cd spotify-mood-analysis
```

2. Create and activate virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Configure Spotify API
- Create a Spotify Developer account
- Create an application to get API credentials
- Add credentials to `.env` file (see `.env.example`)

## Project Structure
[Project structure description as shown in earlier artifact]

## Usage
1. Data Collection
```bash
python src/data/data_loader.py
```

2. Run Analysis
```bash
python src/analysis/temporal.py
python src/analysis/genre_analysis.py
```

3. Launch Dashboard
```bash
streamlit run src/visualization/dashboard.py
```

## Analysis Methodology
[Briefly describe your approach to analyzing the data and determining mood correlations]

## Visualizations
[Screenshots and descriptions of key visualizations]

## Future Improvements
- Add more sophisticated mood detection algorithms
- Incorporate audio features analysis
- Add machine learning models for pattern recognition
- Expand visualization capabilities

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)