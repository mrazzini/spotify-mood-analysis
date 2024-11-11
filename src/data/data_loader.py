# src/data/data_loader.py

import pandas as pd
import json
from pathlib import Path

def load_streaming_history(data_path):
    """Load Spotify streaming history from json files"""
    data_path = Path(data_path)
    streaming_files = list(data_path.glob('Streaming_History*.json'))
    
    all_streams = []
    for file in streaming_files:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            all_streams.extend(data)
    
    return pd.DataFrame(all_streams)

def process_data(raw_data):
    """Process the raw streaming data"""
    processed_data = raw_data.copy()
    
    # Convert endTime to datetime
    processed_data['ts'] = pd.to_datetime(processed_data['ts'])
    
    # Extract time components
    processed_data['date'] = processed_data['ts'].dt.date
    processed_data['hour'] = processed_data['ts'].dt.hour
    processed_data['day_of_week'] = processed_data['ts'].dt.day_name()
    processed_data['month'] = processed_data['ts'].dt.month
    processed_data['year'] = processed_data['ts'].dt.year
    
    return processed_data

def save_processed_data(processed_data, output_path):
    """Save processed data to CSV"""
    output_path = Path(output_path)
    processed_data.to_csv(output_path, index=False)
    print(f"Data saved to {output_path}")

if __name__ == "__main__":
    # Example usage
    raw_data = load_streaming_history('data/raw')
    processed_data = process_data(raw_data)
    save_processed_data(processed_data, 'data/processed/processed_streaming_data.csv')
    
    # Print basic statistics
    print("\nData Overview:")
    print(f"Total streams: {len(processed_data)}")
    print(f"Date range: {processed_data['date'].min()} to {processed_data['date'].max()}")
    print("\nTop 5 most played tracks:")
    print(processed_data['master_metadata_track_name'].value_counts().head())