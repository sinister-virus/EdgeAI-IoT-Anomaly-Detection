import sys
import os

# --- UNIVERSAL IMPORT FIX ---
# This block ensures the script runs correctly whether using "python -m src.train_model"
# OR pressing the PyCharm "Play" button.
current_dir = os.path.dirname(os.path.abspath(__file__))  # Path to src/
project_root = os.path.dirname(current_dir)  # Path to Major_Project_I/
if project_root not in sys.path:
    sys.path.insert(0,project_root)
# -----------------------------

import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib
import re
from datetime import datetime
import numpy as np

# --- Configuration with Dynamic Paths ---
# Uses the project_root calculated above to find files reliably
RAW_LOG_PATH = os.path.join(project_root,'data','logs.csv')
MODEL_SAVE_PATH = os.path.join(project_root,'models','anomaly_model.pkl')


def extract_mac_address(event_string):
    """Extracts MAC address from log events."""
    match = re.search(r'([0-9A-F]{2}(?::[0-9A-F]{2}){5})',event_string,re.IGNORECASE)
    if match:
        return match.group(0).replace(':','').replace('-','').upper()
    return None


def calculate_time_features(df_raw: pd.DataFrame) -> pd.DataFrame:
    """Processes raw logs using vectorized operations."""
    print("-> Calculating time-series features (Reconnect Delta T) using vectorization...")
    df = df_raw.copy()

    # Handle single Date column containing time
    try:
        df['timestamp'] = pd.to_datetime(df['Date'],errors='coerce')
    except KeyError:
        print("Warning: 'Date' column not found, trying Date+Time merge...")
        df['timestamp'] = pd.to_datetime(df['Date'] + ' ' + df['Time'],errors='coerce')

    df = df.sort_values('timestamp').reset_index(drop=True).dropna(subset=['timestamp'])

    df['MAC'] = df['Event'].apply(extract_mac_address)
    df_connect = df[df['Event'].str.contains('connected',case=False,na=False)].dropna(subset=['MAC']).copy()

    # Vectorized Delta T
    df_connect.loc[:,'reconnect_delta'] = df_connect.groupby('MAC')['timestamp'].diff().dt.total_seconds().fillna(0)
    df_connect.loc[:,'hour'] = df_connect['timestamp'].dt.hour

    # Simulation features
    df_connect.loc[:,'packet_length'] = df_connect['reconnect_delta'].apply(
        lambda x: np.random.randint(900,1500) if x < 15 else np.random.randint(50,400)
    )
    df_connect.loc[:,'usage'] = df_connect['packet_length'] * 10

    feature_df = df_connect[['usage','hour','reconnect_delta','packet_length']].copy()
    feature_df = feature_df[feature_df['reconnect_delta'] > 0].reset_index(drop=True)

    return feature_df


def train_and_save_model():
    """Drives the training process."""
    print(f"--- Starting Isolation Forest Model Training ---")
    print(f"Logs Path: {RAW_LOG_PATH}")

    if not os.path.exists(RAW_LOG_PATH):
        print(f"ERROR: Raw log file not found at {RAW_LOG_PATH}.")
        return

    try:
        df_raw = pd.read_csv(RAW_LOG_PATH,sep=";")
        print(f"-> Loaded {len(df_raw)} raw log entries.")
    except Exception as e:
        print(f"Error reading raw log file: {e}.")
        return

    feature_df = calculate_time_features(df_raw)

    if feature_df.empty:
        print("ERROR: No valid connection events found.")
        return

    features = feature_df[['usage','hour','reconnect_delta','packet_length']]

    print(f"Training on {len(features)} records...")
    model = IsolationForest(contamination=0.005,random_state=42)
    model.fit(features)

    os.makedirs(os.path.dirname(MODEL_SAVE_PATH),exist_ok=True)
    joblib.dump(model,MODEL_SAVE_PATH)

    print(f"✅ Model trained successfully and saved to: {MODEL_SAVE_PATH}")
    print("-----------------------------------")


if __name__ == '__main__':
    train_and_save_model()