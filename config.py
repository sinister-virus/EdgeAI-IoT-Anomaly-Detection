"""
Configuration file for IoT Security System
"""
import os

# Database Configuration
DB_PATH = os.path.join(os.path.dirname(__file__), 'iot_security.db')

# Flask Configuration
FLASK_HOST = '0.0.0.0'
FLASK_PORT = 5000
FLASK_DEBUG = False  # Debug mode disabled for security

# Anomaly Detection Configuration
CONTAMINATION = 0.1  # Expected proportion of outliers
N_ESTIMATORS = 100  # Number of trees in Isolation Forest
RANDOM_STATE = 42

# Feature Engineering Configuration
TIME_WINDOW_SECONDS = 60  # Time window for feature aggregation
