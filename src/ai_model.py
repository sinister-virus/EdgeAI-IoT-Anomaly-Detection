import os
import sys

# --- UNIVERSAL IMPORT FIX ---
# This block ensures the script runs correctly whether using "python -m src.main"
# OR pressing the PyCharm "Play" button.
current_dir = os.path.dirname(os.path.abspath(__file__))  # Path to src/
project_root = os.path.dirname(current_dir)  # Path to Major_Project_I/
if project_root not in sys.path:
    sys.path.insert(0,project_root)
# -----------------------------

import joblib
import pandas as pd
import random
from datetime import datetime

# --- Configuration ---
MODEL_PATH = 'models/anomaly_model.pkl'

# Global Model Instance: Stores the loaded model (or mock) for reuse
ANOMALY_MODEL = None


# --- Mock Model for Simulation (Used if models/anomaly_model.pkl is missing) ---
class MockAnomalyModel:
    """Simulates Isolation Forest prediction and decision function for 5 features."""

    def predict(self,features_df):
        predictions = []
        for index,row in features_df.iterrows():
            # Flag anomaly if: very short Delta T OR very large packet length
            if (row['reconnect_delta'] < 5) or (row['packet_length'] > 1000):
                predictions.append(-1)  # -1 is the standard Isolation Forest code for anomaly
            else:
                predictions.append(1)  # 1 is the standard Isolation Forest code for normal
        return predictions

    def decision_function(self,features_df):
        """
        Simulates raw anomaly score.
        In Isolation Forest, a higher raw score means the data point is closer to normal (safer).
        """
        scores = []
        for index,row in features_df.iterrows():
            # Risk calculation based on two key features
            risk = (row['packet_length'] / 2000) + (10 / (row['reconnect_delta'] + 1))

            # We invert the risk to get the raw score (higher score = safer)
            raw_score = 0.5 - risk + random.uniform(-0.1,0.1)
            scores.append(raw_score)
        return scores


def load_model():
    """
    Loads the Isolation Forest model from disk (models/anomaly_model.pkl)
    or initializes a mock if the file is not found.
    """
    global ANOMALY_MODEL

    if ANOMALY_MODEL is not None:
        return ANOMALY_MODEL

    try:
        if os.path.exists(MODEL_PATH):
            ANOMALY_MODEL = joblib.load(MODEL_PATH)
            print(f"✅ AI Model loaded successfully from {MODEL_PATH}")
        else:
            print(f"⚠️ Warning: Model not found at {MODEL_PATH}. Initializing Mock Model for simulation.")
            ANOMALY_MODEL = MockAnomalyModel()

    except Exception as e:
        print(f"🛑 Error loading model: {e}. Falling back to Mock Model.")
        ANOMALY_MODEL = MockAnomalyModel()

    return ANOMALY_MODEL


def preprocess_features(features: dict) -> pd.DataFrame:
    """
    Converts the dictionary of incoming real-time features into a Pandas DataFrame
    compatible with the trained ML model.
    """

    input_data = {
        'usage': [features['usage']],
        'reconnect_delta': [features['reconnect_delta']],
        'hour': [features['hour']],
        'packet_length': [features['packet_length']],
        # Note: Protocol Type is handled implicitly in simulation for now.
    }
    df = pd.DataFrame(input_data)

    # CRITICAL FIX: Reorder columns to match exactly what was used in train_model.py
    # Order must be: ['usage', 'hour', 'reconnect_delta', 'packet_length']
    df = df[['usage','hour','reconnect_delta','packet_length']]

    return df


def predict_anomaly(features: dict) -> tuple[str,float]:
    """
    Predicts anomaly status based on incoming features from src/monitor.py.
    Returns: (anomaly_flag: "YES"/"NO", risk_score: float)
    """
    model = load_model()

    # 1. Preprocess features
    features_df = preprocess_features(features)

    # 2. Get the raw anomaly score (higher = safer)
    raw_scores = model.decision_function(features_df)
    raw_score = raw_scores[0]

    # 3. Convert raw score to a 0-1 Risk Score (0 = Safe, 1 = High Risk)
    # This scaling is common for Isolation Forest output
    risk_score = 1.0 - (raw_score + 1.0) / 2.0

    # 4. Apply a threshold for the binary flag (based on model's prediction)
    prediction = model.predict(features_df)[0]
    anomaly_flag = "YES" if prediction == -1 else "NO"

    # Clamp score to stay within 0.01 and 0.99 for display clarity
    final_risk_score = max(0.01,min(0.99,risk_score))

    return anomaly_flag,final_risk_score