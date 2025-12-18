"""
Feature Engineering Module for IoT Security System
Performs vectorized feature engineering using Pandas for network log timestamps
"""
import pandas as pd
import numpy as np
from typing import Dict, List
import config


class FeatureEngineer:
    """Handles feature engineering for anomaly detection"""
    
    def __init__(self, time_window: int = config.TIME_WINDOW_SECONDS):
        """
        Initialize the feature engineer
        
        Args:
            time_window: Time window in seconds for feature aggregation
        """
        self.time_window = time_window
    
    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Engineer features from network logs using vectorized operations
        
        Args:
            df: DataFrame containing network logs
            
        Returns:
            DataFrame with engineered features
        """
        if df.empty:
            return df
        
        # Create a copy to avoid modifying original
        features_df = df.copy()
        
        # Convert timestamp to datetime for easier manipulation
        features_df['datetime'] = pd.to_datetime(features_df['timestamp'], unit='s')
        
        # Sort by timestamp for delta calculations (keep original index for ID mapping)
        features_df = features_df.sort_values('timestamp')
        
        # Vectorized timestamp-based features
        features_df = self._compute_time_deltas(features_df)
        features_df = self._compute_time_based_aggregations(features_df)
        features_df = self._compute_traffic_features(features_df)
        features_df = self._compute_device_features(features_df)
        
        return features_df
    
    def _compute_time_deltas(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Compute time deltas between consecutive events
        Uses vectorized Pandas operations for performance
        
        Args:
            df: DataFrame with timestamp column
            
        Returns:
            DataFrame with delta_t features
        """
        # Delta T: Time difference between consecutive events (vectorized)
        df['delta_t'] = df['timestamp'].diff().fillna(0)
        
        # Delta T for same device (vectorized groupby operation)
        df['delta_t_device'] = df.groupby('device_id')['timestamp'].diff().fillna(0)
        
        # Delta T for same source IP (vectorized groupby operation)
        df['delta_t_source'] = df.groupby('source_ip')['timestamp'].diff().fillna(0)
        
        # Rolling statistics on delta_t (vectorized window operations)
        df['delta_t_mean'] = df['delta_t'].rolling(window=10, min_periods=1).mean()
        df['delta_t_std'] = df['delta_t'].rolling(window=10, min_periods=1).std().fillna(0)
        
        return df
    
    def _compute_time_based_aggregations(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Compute time-based aggregation features
        
        Args:
            df: DataFrame with timestamp column
            
        Returns:
            DataFrame with time-based features
        """
        # Extract time components (vectorized)
        df['hour'] = df['datetime'].dt.hour
        df['day_of_week'] = df['datetime'].dt.dayofweek
        df['minute'] = df['datetime'].dt.minute
        
        # Events per time window (rolling count - vectorized)
        df['events_per_window'] = df.rolling(
            window=f'{self.time_window}s', 
            on='datetime'
        ).count()['timestamp']
        
        return df
    
    def _compute_traffic_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Compute traffic-based features
        
        Args:
            df: DataFrame with traffic columns
            
        Returns:
            DataFrame with traffic features
        """
        # Total bytes (vectorized)
        df['total_bytes'] = df['bytes_sent'] + df['bytes_received']
        
        # Bytes ratio (vectorized with safe division)
        df['bytes_ratio'] = np.where(
            df['bytes_received'] > 0,
            df['bytes_sent'] / df['bytes_received'],
            0
        )
        
        # Rolling traffic statistics (vectorized window operations)
        df['bytes_mean'] = df['total_bytes'].rolling(window=10, min_periods=1).mean()
        df['bytes_std'] = df['total_bytes'].rolling(window=10, min_periods=1).std().fillna(0)
        
        # Z-score for bytes (vectorized)
        df['bytes_zscore'] = np.where(
            df['bytes_std'] > 0,
            (df['total_bytes'] - df['bytes_mean']) / df['bytes_std'],
            0
        )
        
        return df
    
    def _compute_device_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Compute device-based features
        
        Args:
            df: DataFrame with device information
            
        Returns:
            DataFrame with device features
        """
        # Count of events per device (vectorized transform)
        df['device_event_count'] = df.groupby('device_id')['device_id'].transform('count')
        
        # Unique destinations per device (vectorized transform)
        df['unique_destinations'] = df.groupby('device_id')['destination_ip'].transform('nunique')
        
        # Port diversity (vectorized transform)
        df['unique_ports'] = df.groupby('device_id')['port'].transform('nunique')
        
        return df
    
    def get_feature_vector(self, df: pd.DataFrame) -> np.ndarray:
        """
        Extract feature vector for anomaly detection
        
        Args:
            df: DataFrame with engineered features
            
        Returns:
            NumPy array of features
        """
        if df.empty:
            return np.array([])
        
        # Select numerical features for model
        feature_columns = [
            'delta_t', 'delta_t_device', 'delta_t_source',
            'delta_t_mean', 'delta_t_std',
            'hour', 'day_of_week', 'minute',
            'events_per_window',
            'total_bytes', 'bytes_ratio', 'bytes_mean', 'bytes_std', 'bytes_zscore',
            'device_event_count', 'unique_destinations', 'unique_ports',
            'port', 'bytes_sent', 'bytes_received'
        ]
        
        # Filter to only existing columns
        available_columns = [col for col in feature_columns if col in df.columns]
        
        # Extract feature matrix (vectorized)
        X = df[available_columns].values
        
        # Replace any inf values with 0 (vectorized)
        X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)
        
        return X
    
    def get_feature_names(self, df: pd.DataFrame) -> List[str]:
        """
        Get list of feature names used in the model
        
        Args:
            df: DataFrame with engineered features
            
        Returns:
            List of feature names
        """
        feature_columns = [
            'delta_t', 'delta_t_device', 'delta_t_source',
            'delta_t_mean', 'delta_t_std',
            'hour', 'day_of_week', 'minute',
            'events_per_window',
            'total_bytes', 'bytes_ratio', 'bytes_mean', 'bytes_std', 'bytes_zscore',
            'device_event_count', 'unique_destinations', 'unique_ports',
            'port', 'bytes_sent', 'bytes_received'
        ]
        
        return [col for col in feature_columns if col in df.columns]
