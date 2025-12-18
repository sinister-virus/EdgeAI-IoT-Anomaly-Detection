import sys
import os

# --- UNIVERSAL IMPORT FIX ---
# This block ensures the script runs correctly whether using "python -m src.main"
# OR pressing the PyCharm "Play" button.
current_dir = os.path.dirname(os.path.abspath(__file__))  # Path to src/
project_root = os.path.dirname(current_dir)  # Path to Major_Project_I/
if project_root not in sys.path:
    sys.path.insert(0,project_root)
# -----------------------------

import sqlite3
import pandas as pd
from datetime import datetime

# --- Configuration ---
DB_PATH = 'data/smart_home_soc.db'
TABLE_NAME = 'processed_logs'


def initialize_database():
    """
    Initializes the SQLite database and creates the 'processed_logs' table.
    The schema is set to hold all the rich features (Delta T, usage, risk score).
    """
    # Ensure the 'data' directory exists before creating the DB file
    os.makedirs(os.path.dirname(DB_PATH),exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    schema = f"""
    CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
        timestamp TEXT PRIMARY KEY,
        device_mac TEXT,
        device_name TEXT,
        usage INTEGER,
        reconnect_delta REAL, -- The Delta T feature (seconds between connections)
        anomaly_flag TEXT,
        risk_score REAL,
        event_group TEXT -- Example: 'WiFi/TCP', 'Web UI'
    );
    """
    cursor.execute(schema)
    conn.commit()
    conn.close()
    print(f"✅ Database initialized at: {DB_PATH}")


def insert_log_entry(log_entry: dict):
    """
    Inserts a new processed log entry into the database.
    Called by src/monitor.py.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Automatically handle the column names and values from the dictionary keys
    columns = ', '.join(log_entry.keys())
    placeholders = ', '.join(['?'] * len(log_entry))
    values = tuple(log_entry.values())

    try:
        # Using INSERT OR IGNORE to prevent crashing on duplicate timestamps
        cursor.execute(f"INSERT OR IGNORE INTO {TABLE_NAME} ({columns}) VALUES ({placeholders})",values)
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # This will rarely trigger due to the 'OR IGNORE', but handles general DB errors.
        print(f"Skipping entry due to DB error or duplicate key: {log_entry.get('timestamp')}")
        return False
    except Exception as e:
        print(f"Error during database insertion: {e}")
        return False
    finally:
        conn.close()


def fetch_logs(limit=100) -> pd.DataFrame:
    """
    Fetches the latest processed logs for the dashboard display.
    Called by src/main.py API routes.
    """
    conn = sqlite3.connect(DB_PATH)
    # Fetch data ordered by timestamp descending for the most recent events
    query = f"SELECT * FROM {TABLE_NAME} ORDER BY timestamp DESC LIMIT {limit}"
    df = pd.read_sql_query(query,conn)
    conn.close()

    # Ensure all required columns are present, even if the DB is empty
    required_cols = ['timestamp','device_mac','device_name','usage','reconnect_delta','anomaly_flag','risk_score',
                     'event_group']
    for col in required_cols:
        if col not in df.columns:
            df[col] = None

    return df